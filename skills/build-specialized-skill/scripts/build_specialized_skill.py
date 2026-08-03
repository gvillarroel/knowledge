#!/usr/bin/env python3
"""Build or reproducibly check a standalone expert skill."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import tempfile
from typing import Sequence

from _supervised_profile import (
    IDENTITY_MODES,
    PROFILE_MODE,
    SupervisedProfileError,
    build_supervised_profile,
    canonical_json,
    manifest_profile_binding,
)
from _specialized_skill import (
    PROFILE_SCHEMA_VERSION,
    SCHEMA_VERSION,
    SpecializedSkillError,
    normalize_text,
    sha256_file,
    tree_binding,
    validate_generated_skill,
    validate_guidance,
    validate_knowledge,
    validate_skill_name,
    render_expert_skill,
    render_openai_yaml,
)

EVALUATION_ONLY_REGISTRY_SCHEMA = "evaluation-only-registry/1.0"
EVALUATION_ONLY_POLICY_SCHEMA = "evaluation-only-dataset-policy/1.0"


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _load_json_object(path: Path, *, label: str) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise SpecializedSkillError(f"Cannot read {label} at {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise SpecializedSkillError(f"{label} must be a JSON object: {path}")
    return value


def _assert_profile_questions_not_evaluation_only(questions: Path) -> None:
    """Reject evaluation-only bytes and marked directories from profile forging."""

    for directory in (questions.parent, *questions.parents):
        marker = directory / "EVALUATION_ONLY.json"
        if not marker.is_file():
            continue
        policy = _load_json_object(marker, label="evaluation-only policy")
        if policy.get("schema_version") != EVALUATION_ONLY_POLICY_SCHEMA:
            raise SpecializedSkillError(
                f"Unsupported evaluation-only policy marker: {marker}"
            )
        dataset_id = policy.get("dataset_id", "registered dataset")
        raise SpecializedSkillError(
            f"{dataset_id} is evaluation-only and cannot be used to forge "
            "a retrieval profile"
        )

    repository_root = Path(__file__).resolve().parents[3]
    registry_candidates = (
        repository_root / "evaluations" / "evaluation-only-registry.json",
        Path.cwd() / "evaluations" / "evaluation-only-registry.json",
    )
    question_sha = sha256_file(questions)
    seen: set[Path] = set()
    for registry_path in registry_candidates:
        registry_path = registry_path.resolve()
        if registry_path in seen or not registry_path.is_file():
            continue
        seen.add(registry_path)
        registry = _load_json_object(
            registry_path,
            label="evaluation-only registry",
        )
        if registry.get("schema_version") != EVALUATION_ONLY_REGISTRY_SCHEMA:
            raise SpecializedSkillError(
                f"Unsupported evaluation-only registry: {registry_path}"
            )
        rows = registry.get("datasets")
        if not isinstance(rows, list):
            raise SpecializedSkillError(
                f"Evaluation-only registry lacks datasets: {registry_path}"
            )
        for row in rows:
            if not isinstance(row, dict):
                raise SpecializedSkillError(
                    f"Evaluation-only registry contains an invalid row: {registry_path}"
                )
            if row.get("questions_sha256") == question_sha:
                dataset_id = row.get("dataset_id", "registered dataset")
                raise SpecializedSkillError(
                    f"{dataset_id} is evaluation-only and cannot be used to "
                    "forge a retrieval profile"
                )


def _copy_regular_tree(source: Path, target: Path) -> None:
    target.mkdir(parents=True)
    for path in source.rglob("*"):
        if path.is_symlink():
            raise SpecializedSkillError(f"Symlinks are not allowed: {path}")
        relative = path.relative_to(source)
        destination = target / relative
        if path.is_dir():
            destination.mkdir(parents=True, exist_ok=True)
        elif path.is_file():
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, destination)


def _copy_query_support(
    sources: Sequence[Path],
    scripts_root: Path,
) -> list[dict[str, str]]:
    """Copy and bind optional files required by a custom query adapter."""

    bindings: list[dict[str, str]] = []
    seen_names: set[str] = {"query_expert_knowledge.py"}
    for source in sorted(sources, key=lambda item: item.name):
        if source.is_symlink() or not source.is_file():
            raise SpecializedSkillError(
                f"Query support must be a regular file: {source}"
            )
        name = source.name
        if name in seen_names:
            raise SpecializedSkillError(
                f"Duplicate or reserved query-support basename: {name}"
            )
        seen_names.add(name)
        destination = scripts_root / name
        shutil.copyfile(source, destination)
        bindings.append(
            {
                "path": f"scripts/{name}",
                "sha256": sha256_file(destination),
            }
        )
    return bindings


def _build_candidate(
    *,
    knowledge: Path,
    candidate: Path,
    name: str,
    description: str,
    guidance_path: Path,
    query_template: Path,
    query_support: Sequence[Path],
    profile_dataset_id: str | None,
    profile_questions: Path | None,
    profile_qrel_key: str | None,
    profile_identity_mode: str | None,
) -> dict[str, object]:
    knowledge_binding = validate_knowledge(knowledge)
    guidance = normalize_text(guidance_path, label="guidance")
    validate_guidance(guidance)

    profile_payload: dict[str, object] | None = None
    if profile_questions is not None:
        if (
            profile_dataset_id is None
            or profile_qrel_key is None
            or profile_identity_mode is None
        ):
            raise SpecializedSkillError(
                "Retrospective profile configuration is incomplete"
            )
        try:
            profile_payload = build_supervised_profile(
                dataset_id=profile_dataset_id,
                knowledge=knowledge,
                questions_path=profile_questions,
                qrel_key=profile_qrel_key,
                identity_mode=profile_identity_mode,
            )
        except SupervisedProfileError as exc:
            raise SpecializedSkillError(str(exc)) from exc

    skill_md = render_expert_skill(
        name,
        description,
        retrieval_profile=profile_payload,
    )
    agents_yaml = render_openai_yaml(name, description)
    _write_text(candidate / "SKILL.md", skill_md)
    _write_text(candidate / "references" / "guidance.md", guidance)
    _write_text(candidate / "agents" / "openai.yaml", agents_yaml)
    _copy_regular_tree(knowledge, candidate / "references" / "knowledge")

    if not query_template.is_file():
        raise SpecializedSkillError(
            f"Query helper template is absent: {query_template}"
        )
    query_script = candidate / "scripts" / "query_expert_knowledge.py"
    query_script.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(query_template, query_script)
    query_support_bindings = _copy_query_support(query_support, query_script.parent)
    profile_binding: dict[str, object] | None = None
    if profile_payload is not None:
        profile_path = query_script.parent / "expert_routing_index.json"
        _write_text(profile_path, canonical_json(profile_payload))
        profile_sha256 = sha256_file(profile_path)
        query_support_bindings.append(
            {
                "path": "scripts/expert_routing_index.json",
                "sha256": profile_sha256,
            }
        )
        profile_binding = manifest_profile_binding(profile_payload, profile_sha256)

    artifacts = {
        "skill_md": {
            "path": "SKILL.md",
            "sha256": sha256_file(candidate / "SKILL.md"),
        },
        "guidance": {
            "path": "references/guidance.md",
            "sha256": sha256_file(candidate / "references" / "guidance.md"),
        },
        "query_script": {
            "path": "scripts/query_expert_knowledge.py",
            "sha256": sha256_file(query_script),
        },
        "agents_metadata": {
            "path": "agents/openai.yaml",
            "sha256": sha256_file(candidate / "agents" / "openai.yaml"),
        },
    }
    if query_support_bindings:
        artifacts["query_support"] = query_support_bindings
    manifest: dict[str, object] = {
        "schema_version": (
            PROFILE_SCHEMA_VERSION if profile_payload is not None else SCHEMA_VERSION
        ),
        "skill_name": name,
        "description": description,
        "knowledge": {
            "format": "semantic-okf",
            "path": "references/knowledge",
            "tree": {
                "sha256": knowledge_binding.tree.sha256,
                "file_count": knowledge_binding.tree.file_count,
            },
            "record_count": knowledge_binding.record_count,
            "build_report_sha256": knowledge_binding.build_report_sha256,
        },
        "artifacts": artifacts,
    }
    if profile_binding is not None:
        manifest["retrieval_profile"] = profile_binding
    _write_text(
        candidate / "expert-manifest.json",
        json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
    )
    validate_generated_skill(candidate)
    return manifest


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("knowledge", type=Path, help="Validated Semantic OKF folder")
    parser.add_argument("output", type=Path, help="New expert skill directory")
    parser.add_argument("--name", required=True, help="Generated skill name")
    parser.add_argument(
        "--description",
        required=True,
        help="Generated skill trigger description",
    )
    parser.add_argument(
        "--guidance",
        required=True,
        type=Path,
        help="Reviewed domain-application guidance Markdown",
    )
    parser.add_argument(
        "--query-template",
        type=Path,
        help=(
            "Optional self-contained query helper template. The default preserves "
            "the stable lexical expert contract."
        ),
    )
    parser.add_argument(
        "--query-support",
        type=Path,
        action="append",
        default=[],
        help=(
            "Optional regular file copied beside a custom query template and "
            "bound in the expert manifest; repeat for multiple support files."
        ),
    )
    parser.add_argument(
        "--retrieval-profile",
        choices=[PROFILE_MODE],
        help=(
            "Build the explicitly retrospective supervised n-gram profile "
            "inside this skill instead of selecting a custom query adapter."
        ),
    )
    parser.add_argument(
        "--profile-dataset-id",
        help="Stable dataset ID recorded in the retrospective profile",
    )
    parser.add_argument(
        "--profile-questions",
        type=Path,
        help="JSONL questions containing the exposed qrels used for the profile",
    )
    parser.add_argument(
        "--profile-qrel-key",
        help="Array member below each question's qrels object",
    )
    parser.add_argument(
        "--profile-identity-mode",
        choices=IDENTITY_MODES,
        help="How qrel identities map to authoritative ledger records",
    )
    parser.add_argument(
        "--acknowledge-exposed-qrels",
        action="store_true",
        help=(
            "Acknowledge that every supplied qrel is development-visible and "
            "the generated expert is not promotion eligible"
        ),
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Compare a temporary rebuild with the existing output",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Build or check one expert skill."""

    args = build_parser().parse_args(argv)
    knowledge = args.knowledge.resolve()
    output = args.output.resolve()
    guidance = args.guidance.resolve()
    skill_root = Path(__file__).resolve().parents[1]
    if args.retrieval_profile == PROFILE_MODE:
        query_template = (
            skill_root
            / "assets"
            / "expert-template"
            / "query_expert_knowledge_supervised_profiles.py"
        )
    else:
        query_template = (
            args.query_template.resolve()
            if args.query_template is not None
            else (
                skill_root
                / "assets"
                / "expert-template"
                / "query_expert_knowledge.py"
            )
        )
    query_support = [path.resolve() for path in args.query_support]
    profile_questions = (
        args.profile_questions.resolve()
        if args.profile_questions is not None
        else None
    )
    try:
        validate_skill_name(args.name)
        profile_values = (
            args.profile_dataset_id,
            profile_questions,
            args.profile_qrel_key,
            args.profile_identity_mode,
        )
        if args.retrieval_profile == PROFILE_MODE:
            if args.query_template is not None or query_support:
                raise SpecializedSkillError(
                    "Integrated retrieval profiles cannot be combined with "
                    "--query-template or --query-support"
                )
            if not args.acknowledge_exposed_qrels:
                raise SpecializedSkillError(
                    "--acknowledge-exposed-qrels is required for a "
                    "retrospective supervised profile"
                )
            if any(value is None for value in profile_values):
                raise SpecializedSkillError(
                    "The profile dataset ID, questions, qrel key, and identity "
                    "mode are all required"
                )
            _assert_profile_questions_not_evaluation_only(profile_questions)
        elif any(value is not None for value in profile_values):
            raise SpecializedSkillError(
                "Profile options require --retrieval-profile "
                f"{PROFILE_MODE}"
            )
        elif args.acknowledge_exposed_qrels:
            raise SpecializedSkillError(
                "--acknowledge-exposed-qrels requires an integrated profile"
            )
        if query_support and args.query_template is None:
            raise SpecializedSkillError(
                "--query-support requires an explicit --query-template"
            )
        if output.name != args.name:
            raise SpecializedSkillError(
                f"Output basename {output.name!r} must equal --name {args.name!r}"
            )
        if not args.description.strip():
            raise SpecializedSkillError("Description must not be empty")
        for left, right, label in (
            (output, knowledge, "output cannot contain the knowledge input"),
            (knowledge, output, "output cannot be inside the knowledge input"),
        ):
            try:
                right.relative_to(left)
            except ValueError:
                continue
            raise SpecializedSkillError(label)
        if args.check and not output.is_dir():
            raise SpecializedSkillError("--check requires an existing output directory")
        if not args.check and output.exists():
            raise SpecializedSkillError(f"Output already exists: {output}")

        output.parent.mkdir(parents=True, exist_ok=True)
        temporary_root = Path(
            tempfile.mkdtemp(prefix=f".{args.name}-", dir=output.parent)
        )
        candidate = temporary_root / args.name
        candidate.mkdir()
        try:
            manifest = _build_candidate(
                knowledge=knowledge,
                candidate=candidate,
                name=args.name,
                description=args.description.strip(),
                guidance_path=guidance,
                query_template=query_template,
                query_support=query_support,
                profile_dataset_id=args.profile_dataset_id,
                profile_questions=profile_questions,
                profile_qrel_key=args.profile_qrel_key,
                profile_identity_mode=args.profile_identity_mode,
            )
            if args.check:
                expected = tree_binding(output)
                actual = tree_binding(candidate)
                if expected != actual:
                    raise SpecializedSkillError(
                        "Existing expert skill differs from a deterministic rebuild"
                    )
                result = {
                    "status": "pass",
                    "mode": "check",
                    "skill_name": args.name,
                    "tree_sha256": actual.sha256,
                    "file_count": actual.file_count,
                }
            else:
                os.replace(candidate, output)
                accepted = tree_binding(output)
                result = {
                    "status": "pass",
                    "mode": "build",
                    "skill_name": args.name,
                    "tree_sha256": accepted.sha256,
                    "file_count": accepted.file_count,
                    "record_count": manifest["knowledge"]["record_count"],
                }
                if "retrieval_profile" in manifest:
                    result["retrieval_profile"] = {
                        "mode": PROFILE_MODE,
                        "promotion_eligible": False,
                    }
        finally:
            shutil.rmtree(temporary_root, ignore_errors=True)
    except (OSError, SpecializedSkillError) as exc:
        raise SystemExit(f"Specialized skill build failed: {exc}") from exc

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
