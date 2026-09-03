#!/usr/bin/env python3
"""Build a classical expert with immutable knowledge and budgeted context."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
from typing import Any, Sequence

from _build_semantic_okf_core import build as build_core
from _classical_retrieval import ClassicalError, atomic_build
from _classical_snapshot import load_snapshot
from _context_projection import (
    ContextProjectionError,
    build_projection,
    load_plan as load_context_plan,
    validate_projection,
)
from _knowledge_skill import (
    SCHEMA_VERSION,
    KnowledgeSkillError,
    artifact_binding,
    concept_layout,
    normalize_text,
    render_expert_skill,
    render_openai_yaml,
    sha256_file,
    tree_binding,
    validate_generated_skill,
    validate_guidance,
    validate_knowledge,
    validate_skill_name,
)
from _semantic_okf import (
    BundleError,
    CONCEPT_LAYOUT_SOURCE_PACKED,
    CONCEPT_LAYOUTS,
    ManifestError,
    configure_utf8_output,
)


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _copy_regular_file(source: Path, target: Path, *, label: str) -> None:
    if source.is_symlink() or not source.is_file():
        raise KnowledgeSkillError(f"{label} is absent or unsafe: {source}")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)


def _inside(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def _validate_inputs(
    *,
    manifest: Path,
    plan: Path,
    context_plan: Path,
    guidance: Path,
    output: Path,
    name: str,
    description: str,
    check: bool,
) -> None:
    validate_skill_name(name)
    if output.name != name:
        raise KnowledgeSkillError(
            f"Output basename {output.name!r} must equal --name {name!r}"
        )
    if not description.strip() or "\n" in description or "\r" in description:
        raise KnowledgeSkillError("Description must be one non-empty line")
    for path, label in (
        (manifest, "Source manifest"),
        (plan, "Classical plan"),
        (context_plan, "Context plan"),
        (guidance, "Guidance"),
    ):
        if path.is_symlink() or not path.is_file():
            raise KnowledgeSkillError(f"{label} is absent or unsafe: {path}")
        if _inside(path, output):
            raise KnowledgeSkillError(f"{label} cannot be inside the generated skill")
    if check and not output.is_dir():
        raise KnowledgeSkillError("--check requires an existing output directory")
    if not check and (output.exists() or output.is_symlink()):
        raise KnowledgeSkillError(f"Output already exists: {output}")


def _build_candidate(
    *,
    manifest_path: Path,
    plan_path: Path,
    context_plan_path: Path,
    candidate: Path,
    name: str,
    description: str,
    guidance_path: Path,
    requested_layout: str,
    skill_root: Path,
) -> dict[str, Any]:
    guidance = normalize_text(guidance_path, label="guidance")
    validate_guidance(guidance)
    knowledge_root = candidate / "references" / "knowledge"
    atomic_build(
        manifest_path,
        plan_path,
        knowledge_root,
        lambda source_manifest, destination: build_core(
            source_manifest,
            destination,
            concept_layout=requested_layout,
        ),
    )
    knowledge = validate_knowledge(knowledge_root, deep_validation=True)
    actual_layout = concept_layout(knowledge_root)
    if actual_layout != requested_layout:
        raise KnowledgeSkillError(
            f"Built concept layout {actual_layout!r} differs from {requested_layout!r}"
        )

    context_plan = load_context_plan(context_plan_path)
    snapshot = load_snapshot(knowledge_root, deep_validation=False)
    context_root = candidate / "references" / "context"
    context_index = build_projection(
        knowledge_root,
        context_root,
        snapshot,
        context_plan,
    )
    context_projection = validate_projection(
        knowledge_root,
        context_root,
        snapshot,
        rederive=True,
    )
    context_tree = tree_binding(context_root)

    _write_text(candidate / "SKILL.md", render_expert_skill(name, description))
    _write_text(candidate / "references" / "guidance.md", guidance)
    _write_text(candidate / "agents" / "openai.yaml", render_openai_yaml(name, description))

    templates = skill_root / "assets" / "expert-template"
    _copy_regular_file(
        templates / "query_expert_knowledge.py",
        candidate / "scripts" / "query_expert_knowledge.py",
        label="Expert query template",
    )
    _copy_regular_file(
        skill_root / "scripts" / "_classical_snapshot.py",
        candidate / "scripts" / "_classical_snapshot.py",
        label="Classical snapshot runtime",
    )
    _copy_regular_file(
        skill_root / "scripts" / "_context_projection.py",
        candidate / "scripts" / "_context_projection.py",
        label="Budgeted context runtime",
    )
    _copy_regular_file(
        templates / "runtime_smoke.py",
        candidate / "scripts" / "runtime_smoke.py",
        label="Expert runtime smoke template",
    )
    _copy_regular_file(
        templates / "requirements.txt",
        candidate / "scripts" / "requirements.txt",
        label="Expert requirements template",
    )

    artifact_paths = {
        "skill_md": "SKILL.md",
        "guidance": "references/guidance.md",
        "query_script": "scripts/query_expert_knowledge.py",
        "snapshot_runtime": "scripts/_classical_snapshot.py",
        "context_runtime": "scripts/_context_projection.py",
        "runtime_smoke": "scripts/runtime_smoke.py",
        "requirements": "scripts/requirements.txt",
        "agents_metadata": "agents/openai.yaml",
    }
    artifacts = {
        key: artifact_binding(
            candidate.joinpath(*Path(relative).parts),
            relative,
        )
        for key, relative in artifact_paths.items()
    }
    expert_manifest = {
        "schema_version": SCHEMA_VERSION,
        "skill_name": name,
        "description": description,
        "generation": {
            "builder": "build-classical-chunked-knowledge-skill",
            "concept_layout": actual_layout,
            "default_query_mode": "fusion",
            "source_manifest_sha256": sha256_file(manifest_path),
            "classical_plan_input_sha256": sha256_file(plan_path),
            "context_plan_input_sha256": sha256_file(context_plan_path),
            "deep_validation": True,
        },
        "knowledge": {
            "format": "semantic-okf-classical",
            "path": "references/knowledge",
            "tree": {
                "sha256": knowledge.tree.sha256,
                "file_count": knowledge.tree.file_count,
            },
            "record_count": knowledge.record_count,
            "core_tree_sha256": knowledge.core_tree_sha256,
            "classical_index_sha256": knowledge.classical_index_sha256,
            "classical_plan_sha256": knowledge.classical_plan_sha256,
        },
        "context": {
            "format": context_index["schema_version"],
            "path": "references/context",
            "tree": {
                "sha256": context_tree.sha256,
                "file_count": context_tree.file_count,
            },
            "index_sha256": sha256_file(context_root / "index.json"),
            "plan_sha256": context_index["plan_sha256"],
            "chunk_count": len(context_projection.chunks),
            "default_budget_tokens": context_plan["selection"][
                "default_budget_tokens"
            ],
            "maximum_budget_tokens": context_plan["selection"][
                "maximum_budget_tokens"
            ],
        },
        "artifacts": artifacts,
    }
    _write_text(
        candidate / "expert-manifest.json",
        json.dumps(
            expert_manifest,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
            allow_nan=False,
        )
        + "\n",
    )
    validate_generated_skill(candidate, deep_validation=True)
    return expert_manifest


def build_parser() -> argparse.ArgumentParser:
    """Build the integrated classical knowledge-skill parser."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path, help="Closed Semantic OKF source manifest")
    parser.add_argument("classical_plan", type=Path, help="Closed classical retrieval plan")
    parser.add_argument("output", type=Path, help="New generated expert-skill directory")
    parser.add_argument(
        "--context-plan",
        type=Path,
        help="Closed context plan; defaults to the bundled reviewed plan",
    )
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
        "--concept-layout",
        choices=sorted(CONCEPT_LAYOUTS),
        default=CONCEPT_LAYOUT_SOURCE_PACKED,
        help="Physical concept layout embedded in the generated skill",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Rebuild privately and compare with an existing generated skill",
    )
    parser.add_argument(
        "--output-format",
        choices=("text", "json"),
        default="text",
    )
    return parser


def _error_code(exc: Exception) -> str:
    if isinstance(exc, ManifestError):
        return "manifest-error"
    if isinstance(exc, ClassicalError):
        return "classical-error"
    if isinstance(exc, ContextProjectionError):
        return "context-projection-error"
    if isinstance(exc, BundleError):
        return "semantic-error"
    if isinstance(exc, KnowledgeSkillError):
        return "knowledge-skill-error"
    return "input-error"


def main(argv: Sequence[str] | None = None) -> int:
    """Build or deterministically check one complete expert skill."""

    configure_utf8_output()
    args = build_parser().parse_args(argv)
    skill_root = Path(__file__).resolve().parents[1]
    context_plan_argument = args.context_plan or (
        skill_root / "assets" / "default-context-plan.json"
    )
    raw_paths = (
        (args.manifest.expanduser(), "Source manifest"),
        (args.classical_plan.expanduser(), "Classical plan"),
        (context_plan_argument.expanduser(), "Context plan"),
        (args.guidance.expanduser(), "Guidance"),
        (args.output.expanduser(), "Output"),
    )
    linked = [label for path, label in raw_paths if path.is_symlink()]
    if linked:
        error = {
            "schema_version": SCHEMA_VERSION,
            "status": "error",
            "code": "knowledge-skill-error",
            "error": "Symlink paths are not accepted: " + ", ".join(linked),
        }
        if args.output_format == "json":
            print(json.dumps(error, ensure_ascii=False, sort_keys=True))
        else:
            print(f"{error['code']}: {error['error']}", file=sys.stderr)
        return 2
    manifest = args.manifest.expanduser().resolve()
    plan = args.classical_plan.expanduser().resolve()
    context_plan = context_plan_argument.expanduser().resolve()
    guidance = args.guidance.expanduser().resolve()
    output = args.output.expanduser().resolve()
    temporary_root: Path | None = None
    try:
        _validate_inputs(
            manifest=manifest,
            plan=plan,
            context_plan=context_plan,
            guidance=guidance,
            output=output,
            name=args.name,
            description=args.description,
            check=args.check,
        )
        output.parent.mkdir(parents=True, exist_ok=True)
        temporary_root = Path(
            tempfile.mkdtemp(prefix=f".{args.name}.candidate-", dir=output.parent)
        )
        candidate = temporary_root / args.name
        candidate.mkdir()
        expert_manifest = _build_candidate(
            manifest_path=manifest,
            plan_path=plan,
            context_plan_path=context_plan,
            candidate=candidate,
            name=args.name,
            description=args.description.strip(),
            guidance_path=guidance,
            requested_layout=args.concept_layout,
            skill_root=skill_root,
        )
        candidate_binding = tree_binding(candidate)
        if args.check:
            accepted_binding = tree_binding(output)
            if accepted_binding != candidate_binding:
                raise KnowledgeSkillError(
                    "Existing expert skill differs from a deterministic rebuild"
                )
            mode = "check"
        else:
            os.replace(candidate, output)
            accepted_binding = tree_binding(output)
            if accepted_binding != candidate_binding:
                raise KnowledgeSkillError("Published expert tree differs from its candidate")
            mode = "build"
        result = {
            "schema_version": SCHEMA_VERSION,
            "status": "pass",
            "mode": mode,
            "skill_name": args.name,
            "skill_tree_sha256": candidate_binding.sha256,
            "skill_file_count": candidate_binding.file_count,
            "knowledge_tree_sha256": expert_manifest["knowledge"]["tree"]["sha256"],
            "knowledge_file_count": expert_manifest["knowledge"]["tree"]["file_count"],
            "record_count": expert_manifest["knowledge"]["record_count"],
            "concept_layout": args.concept_layout,
            "default_query_mode": "fusion",
            "context_chunk_count": expert_manifest["context"]["chunk_count"],
            "default_context_budget_tokens": expert_manifest["context"][
                "default_budget_tokens"
            ],
            "deep_validation": True,
        }
    except (
        OSError,
        UnicodeError,
        ValueError,
        TypeError,
        KeyError,
        IndexError,
        OverflowError,
    ) as exc:
        error = {
            "schema_version": SCHEMA_VERSION,
            "status": "error",
            "code": _error_code(exc),
            "error": str(exc),
        }
        if args.output_format == "json":
            print(json.dumps(error, ensure_ascii=False, sort_keys=True))
        else:
            print(f"{error['code']}: {error['error']}", file=sys.stderr)
        return 2
    finally:
        if temporary_root is not None:
            shutil.rmtree(temporary_root, ignore_errors=True)

    if args.output_format == "json":
        print(json.dumps(result, ensure_ascii=False, sort_keys=True, allow_nan=False))
    else:
        print(
            f"Classical chunked knowledge skill {mode} passed: {output}\n"
            f"Records: {result['record_count']}; files: {result['skill_file_count']}; "
            f"chunks: {result['context_chunk_count']}; "
            f"context budget: {result['default_context_budget_tokens']}; "
            f"layout: {result['concept_layout']}; default query mode: fusion"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
