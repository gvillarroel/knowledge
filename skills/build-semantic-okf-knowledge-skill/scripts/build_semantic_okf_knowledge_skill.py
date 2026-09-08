#!/usr/bin/env python3
"""Build a portable expert skill with one matched Semantic OKF family."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from typing import Any, Mapping, Sequence

from _direct_skill import (
    SCHEMA_VERSION,
    SOURCE_PACKED_LAYOUT,
    DirectSkillError,
    artifact_binding,
    canonical_json,
    copy_regular_tree,
    normalize_text,
    regular_files,
    render_expert_skill,
    render_openai_yaml,
    sha256_file,
    tree_binding,
    validate_generated_skill,
    validate_guidance,
    validate_knowledge,
    validate_skill_name,
)
from _family_registry import PROFILES, FamilyProfile, profile, vendor_root
from _source_coverage import source_coverage, source_declarations


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _copy_file(source: Path, target: Path, *, label: str) -> None:
    if not source.is_file() or source.is_symlink():
        raise DirectSkillError(f"{label} is absent or unsafe: {source}")
    if target.exists() or target.is_symlink():
        raise DirectSkillError(f"{label} target already exists: {target}")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)


def _inside(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def _uses_local_embedding_runtime(value: Any) -> bool:
    if isinstance(value, Mapping):
        if value.get("provider") == "sentence-transformers":
            return True
        return any(_uses_local_embedding_runtime(child) for child in value.values())
    if isinstance(value, list):
        return any(_uses_local_embedding_runtime(child) for child in value)
    return False


def _run_json(command: Sequence[str], *, cwd: Path, label: str) -> dict[str, Any]:
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    completed = subprocess.run(
        list(command),
        cwd=cwd,
        env=environment,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="strict",
        check=False,
    )
    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout).strip()
        raise DirectSkillError(f"{label} failed ({completed.returncode}): {detail[-4000:]}")
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise DirectSkillError(
            f"{label} emitted invalid JSON: {completed.stdout[-2000:]!r}"
        ) from exc
    if not isinstance(payload, dict) or payload.get("status") in {"error", "fail"}:
        raise DirectSkillError(f"{label} did not return a passing JSON object")
    return payload


def _validate_inputs(
    *, manifest: Path, plan_path: Path | None, guidance: Path, output: Path,
    name: str, description: str, family: FamilyProfile, check: bool,
) -> None:
    validate_skill_name(name)
    if output.name != name:
        raise DirectSkillError(f"Output basename {output.name!r} must equal --name {name!r}")
    if not description.strip() or "\n" in description or "\r" in description:
        raise DirectSkillError("Description must be one non-empty line")
    required = [(manifest, "Source manifest"), (guidance, "Guidance")]
    if family.uses_plan:
        if plan_path is None:
            raise DirectSkillError(f"Family {family.family_id!r} requires --plan")
        required.append((plan_path, "Family plan"))
    elif plan_path is not None:
        raise DirectSkillError(f"Family {family.family_id!r} does not accept --plan")
    for path, label in required:
        if not path.is_file() or path.is_symlink():
            raise DirectSkillError(f"{label} is absent or unsafe: {path}")
        if _inside(path, output):
            raise DirectSkillError(f"{label} cannot be inside the generated skill")
    if check and (not output.is_dir() or output.is_symlink()):
        raise DirectSkillError("--check requires an existing regular output directory")
    if not check and (output.exists() or output.is_symlink()):
        raise DirectSkillError(f"Output already exists: {output}")


def _build_knowledge(
    *, skill_root: Path, family: FamilyProfile, manifest: Path,
    plan_path: Path | None, knowledge: Path, concept_layout: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    builder_root = vendor_root(skill_root, family.family_id, "builder")
    scripts = builder_root / "scripts"
    builder = scripts / family.build_script
    validator = scripts / family.validate_script
    arguments = [sys.executable, "-B", str(builder), str(manifest)]
    if plan_path is not None:
        arguments.append(str(plan_path))
    arguments.extend(
        [str(knowledge), "--concept-layout", concept_layout, "--output-format", "json"]
    )
    build_report = _run_json(arguments, cwd=scripts, label=f"{family.family_id} builder")
    validation = _run_json(
        [sys.executable, "-B", str(validator), str(knowledge), "--output-format", "json"],
        cwd=scripts,
        label=f"{family.family_id} validator",
    )
    return build_report, validation


def _copy_consultant(
    *, skill_root: Path, family: FamilyProfile, candidate: Path,
    uses_embedding_runtime: bool,
) -> str:
    consultant = vendor_root(skill_root, family.family_id, "consultant")
    consultation = candidate / "references" / "consultation"
    consultation.mkdir(parents=True)
    _copy_file(consultant / "SKILL.md", consultation / "SKILL.md", label="Consultation SKILL.md")
    if (consultant / "references").is_dir():
        copy_regular_tree(consultant / "references", consultation / "references")
    copy_regular_tree(consultant / "scripts", candidate / "scripts" / "native")

    active = candidate / "scripts" / "requirements.txt"
    if uses_embedding_runtime:
        optional = candidate / "scripts" / "native" / "requirements-embeddings.txt"
        if not optional.is_file():
            raise DirectSkillError("Selected model plan lacks a consultant embedding lock")
        _write_text(
            active,
            "# Generated active read-only runtime.\n"
            "-r native/requirements.txt\n"
            "-r native/requirements-embeddings.txt\n",
        )
    else:
        _write_text(
            active,
            "# Generated active read-only runtime.\n-r native/requirements.txt\n",
        )
    return active.relative_to(candidate).as_posix()


def _build_candidate(
    *, skill_root: Path, family: FamilyProfile, manifest_path: Path,
    plan_path: Path | None, candidate: Path, name: str, description: str,
    guidance_path: Path, requested_layout: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    guidance = normalize_text(guidance_path, label="guidance")
    validate_guidance(guidance)
    declarations, source_manifest_sha256 = source_declarations(manifest_path)
    plan_data = (
        json.loads(plan_path.read_text(encoding="utf-8")) if plan_path is not None else None
    )
    uses_embedding_runtime = _uses_local_embedding_runtime(plan_data)
    knowledge_root = candidate / "references" / "knowledge"
    build_result, validation_result = _build_knowledge(
        skill_root=skill_root,
        family=family,
        manifest=manifest_path,
        plan_path=plan_path,
        knowledge=knowledge_root,
        concept_layout=requested_layout,
    )
    knowledge_binding, record_count, actual_layout = validate_knowledge(knowledge_root)
    if actual_layout != requested_layout:
        raise DirectSkillError(
            f"Built concept layout {actual_layout!r} differs from {requested_layout!r}"
        )

    _write_text(candidate / "SKILL.md", render_expert_skill(name, description, family))
    _write_text(candidate / "references" / "guidance.md", guidance)
    _write_text(candidate / "agents" / "openai.yaml", render_openai_yaml(name, description))
    templates = skill_root / "assets" / "expert-template"
    _copy_file(
        templates / "query_expert_knowledge.py",
        candidate / "scripts" / "query_expert_knowledge.py",
        label="Expert query template",
    )
    _copy_file(
        templates / "runtime_smoke.py",
        candidate / "scripts" / "runtime_smoke.py",
        label="Expert runtime smoke template",
    )
    active_requirements = _copy_consultant(
        skill_root=skill_root,
        family=family,
        candidate=candidate,
        uses_embedding_runtime=uses_embedding_runtime,
    )

    if sha256_file(manifest_path) != source_manifest_sha256:
        raise DirectSkillError("Source manifest changed during construction")
    _write_text(
        candidate / "references" / "source-coverage.json",
        json.dumps(source_coverage(declarations, source_manifest_sha256, knowledge_root),
                   ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + "\n",
    )

    artifacts = [
        artifact_binding(candidate, path)
        for path in regular_files(candidate)
        if not path.relative_to(candidate).as_posix().startswith("references/knowledge/")
        and path.name != "expert-manifest.json"
    ]
    expert_manifest = {
        "schema_version": SCHEMA_VERSION,
        "skill_name": name,
        "description": description,
        "family": family.as_manifest(),
        "generation": {
            "builder": "build-semantic-okf-knowledge-skill",
            "concept_layout": actual_layout,
            "source_manifest_sha256": sha256_file(manifest_path),
            "plan_input_sha256": sha256_file(plan_path) if plan_path is not None else None,
            "deep_validation": True,
            "active_requirements": active_requirements,
        },
        "knowledge": {
            "format": "semantic-okf",
            "path": "references/knowledge",
            "tree": {
                "sha256": knowledge_binding.sha256,
                "file_count": knowledge_binding.file_count,
            },
            "record_count": record_count,
            "build_report_sha256": sha256_file(
                knowledge_root / "semantic" / "build-report.json"
            ),
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
    validate_generated_skill(candidate)
    native_verification = _run_json(
        [
            sys.executable,
            "-B",
            str(candidate / "scripts" / "query_expert_knowledge.py"),
            "verify",
            "--deep-validation",
        ],
        cwd=candidate,
        label="generated expert verification",
    )
    if native_verification.get("family") != family.family_id:
        raise DirectSkillError("Generated expert verified a different family")
    return expert_manifest, {
        "builder": build_result,
        "validator": validation_result,
        "generated_expert": native_verification,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path, help="Closed Semantic OKF source manifest")
    parser.add_argument("output", type=Path, help="New generated expert-skill directory")
    parser.add_argument("--family", required=True, choices=sorted(PROFILES))
    parser.add_argument("--plan", type=Path, help="Required only by plan-based families")
    parser.add_argument("--name", required=True, help="Generated skill name")
    parser.add_argument("--description", required=True, help="Generated skill trigger description")
    parser.add_argument("--guidance", required=True, type=Path, help="Reviewed application guidance")
    parser.add_argument(
        "--concept-layout",
        choices=("record-per-file-v1", SOURCE_PACKED_LAYOUT),
        default=SOURCE_PACKED_LAYOUT,
    )
    parser.add_argument("--check", action="store_true", help="Rebuild and compare an existing skill")
    parser.add_argument("--output-format", choices=("text", "json"), default="text")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    raw_paths = [args.manifest.expanduser(), args.guidance.expanduser(), args.output.expanduser()]
    if args.plan is not None:
        raw_paths.append(args.plan.expanduser())
    if any(path.is_symlink() for path in raw_paths):
        error = {
            "schema_version": SCHEMA_VERSION, "status": "error",
            "code": "knowledge-skill-error", "error": "Symlink paths are not accepted",
        }
        if args.output_format == "json":
            print(canonical_json(error))
        else:
            print(f"{error['code']}: {error['error']}", file=sys.stderr)
        return 2
    manifest = args.manifest.expanduser().resolve()
    guidance = args.guidance.expanduser().resolve()
    output = args.output.expanduser().resolve()
    plan_path = args.plan.expanduser().resolve() if args.plan is not None else None
    selected = profile(args.family)
    skill_root = Path(__file__).resolve().parents[1]
    temporary_root: Path | None = None
    try:
        _validate_inputs(
            manifest=manifest,
            plan_path=plan_path,
            guidance=guidance,
            output=output,
            name=args.name,
            description=args.description,
            family=selected,
            check=args.check,
        )
        output.parent.mkdir(parents=True, exist_ok=True)
        temporary_root = Path(
            tempfile.mkdtemp(prefix=f".{args.name}.candidate-", dir=output.parent)
        )
        candidate = temporary_root / args.name
        candidate.mkdir()
        expert_manifest, stages = _build_candidate(
            skill_root=skill_root,
            family=selected,
            manifest_path=manifest,
            plan_path=plan_path,
            candidate=candidate,
            name=args.name,
            description=args.description.strip(),
            guidance_path=guidance,
            requested_layout=args.concept_layout,
        )
        candidate_binding = tree_binding(candidate)
        if args.check:
            if tree_binding(output) != candidate_binding:
                raise DirectSkillError("Existing expert differs from a deterministic rebuild")
            mode = "check"
        else:
            os.replace(candidate, output)
            if tree_binding(output) != candidate_binding:
                raise DirectSkillError("Published expert tree differs from its candidate")
            mode = "build"
        result = {
            "schema_version": SCHEMA_VERSION,
            "status": "pass",
            "mode": mode,
            "skill_name": args.name,
            "family": selected.family_id,
            "skill_tree_sha256": candidate_binding.sha256,
            "skill_file_count": candidate_binding.file_count,
            "knowledge_tree_sha256": expert_manifest["knowledge"]["tree"]["sha256"],
            "knowledge_file_count": expert_manifest["knowledge"]["tree"]["file_count"],
            "record_count": expert_manifest["knowledge"]["record_count"],
            "concept_layout": args.concept_layout,
            "default_query_mode": selected.default_mode,
            "deep_validation": True,
            "stages": stages,
        }
    except (
        DirectSkillError, OSError, UnicodeError, ValueError, TypeError,
        KeyError, IndexError, OverflowError, subprocess.SubprocessError,
    ) as exc:
        error = {
            "schema_version": SCHEMA_VERSION,
            "status": "error",
            "code": "knowledge-skill-error",
            "error": str(exc),
        }
        if args.output_format == "json":
            print(canonical_json(error))
        else:
            print(f"{error['code']}: {error['error']}", file=sys.stderr)
        return 2
    finally:
        if temporary_root is not None:
            shutil.rmtree(temporary_root, ignore_errors=True)
    if args.output_format == "json":
        print(canonical_json(result))
    else:
        print(
            f"Semantic OKF knowledge skill {mode} passed: {output}\n"
            f"Family: {selected.family_id}; records: {result['record_count']}; "
            f"files: {result['skill_file_count']}; default mode: {selected.default_mode}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
