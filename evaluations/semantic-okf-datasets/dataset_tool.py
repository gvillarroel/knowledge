#!/usr/bin/env python3
"""Inspect, validate, and stage reproducible Semantic OKF evaluation datasets."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any, Mapping, Sequence

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
DATASETS = HERE / "datasets"
FAMILIES_PATH = HERE / "families.json"
QUESTION_ID = re.compile(r"^(q[0-9]{3})(?:-|$)")
GLOB_MAGIC = re.compile(r"[*?\[]")


class DatasetError(ValueError):
    """Raised when a checked dataset contract is invalid."""


def load_json(path: Path) -> Any:
    """Load one UTF-8 JSON document."""

    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    """Load non-empty objects from one UTF-8 JSON Lines document."""

    rows: list[dict[str, Any]] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise DatasetError(f"{path}: JSONL row {number} is not an object")
        rows.append(value)
    return rows


def write_json(path: Path, value: Any) -> None:
    """Write deterministic, LF-normalized JSON."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def sha256_file(path: Path) -> str:
    """Return the SHA-256 digest of one file."""

    return hashlib.sha256(path.read_bytes()).hexdigest()


def tree_digest(root: Path, *, exclude: set[str] | None = None) -> str:
    """Hash relative POSIX file paths and bytes in cross-platform order."""

    ignored = exclude or set()
    digest = hashlib.sha256()
    entries: list[tuple[bytes, str, Path]] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        if relative in ignored or "__pycache__" in path.parts:
            continue
        entries.append((relative.encode("utf-8"), relative, path))
    for _sort_key, relative, path in sorted(entries, key=lambda entry: entry[0]):
        digest.update(relative.encode("utf-8") + b"\0" + path.read_bytes() + b"\0")
    return digest.hexdigest()


def repo_path(value: str, label: str) -> Path:
    """Resolve one repository-relative path without allowing escape."""

    candidate = (REPO / value).resolve()
    if candidate != REPO and REPO not in candidate.parents:
        raise DatasetError(f"{label} escapes the repository: {value}")
    return candidate


def pinned_path(spec: Mapping[str, Any], label: str) -> Path:
    """Resolve and hash-check one pinned file descriptor."""

    path_value, expected = spec.get("path"), spec.get("sha256")
    if not isinstance(path_value, str) or not isinstance(expected, str):
        raise DatasetError(f"{label} must declare path and sha256")
    path = repo_path(path_value, label)
    if not path.is_file():
        raise DatasetError(f"{label} is absent: {path_value}")
    actual = sha256_file(path)
    if actual != expected:
        raise DatasetError(f"{label} hash drift: expected {expected}, found {actual}")
    return path


def available_datasets() -> list[str]:
    """Return checked dataset identifiers in stable order."""

    return sorted(path.stem for path in DATASETS.glob("*.json") if not path.name.endswith("-cohorts.json"))


def load_dataset(dataset_id: str) -> dict[str, Any]:
    """Load one checked dataset descriptor."""

    path = DATASETS / f"{dataset_id}.json"
    if not path.is_file():
        choices = ", ".join(available_datasets())
        raise DatasetError(f"unknown dataset {dataset_id!r}; choose from: {choices}")
    value = load_json(path)
    if not isinstance(value, dict) or value.get("dataset_id") != dataset_id:
        raise DatasetError(f"dataset descriptor identity mismatch: {path}")
    return value


def load_families() -> dict[str, dict[str, Any]]:
    """Load the shared build/consult family registry."""

    value = load_json(FAMILIES_PATH)
    families = value.get("families") if isinstance(value, Mapping) else None
    if not isinstance(families, dict):
        raise DatasetError("families.json has no families object")
    return families


def normalize_question_id(value: Any) -> str:
    """Return the stable qNNN prefix used by task directories and cohorts."""

    if not isinstance(value, str):
        raise DatasetError("question IDs must be strings")
    match = QUESTION_ID.match(value)
    if match is None:
        raise DatasetError(f"question ID has no qNNN prefix: {value!r}")
    return match.group(1)


def dataset_questions(dataset: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Load questions and attach a normalized identifier without changing source bytes."""

    path = pinned_path(dataset["questions"], f"{dataset['dataset_id']} questions")
    rows = load_jsonl(path)
    for row in rows:
        row["normalized_id"] = normalize_question_id(row.get("id"))
    return rows


def dataset_semantic_rubrics(dataset: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    """Load and validate optional hidden semantic rubrics keyed by normalized question ID."""

    spec = dataset.get("semantic_rubric")
    if spec is None:
        return {}
    if not isinstance(spec, Mapping) or spec.get("format") != "paper-blueprint":
        raise DatasetError(f"{dataset['dataset_id']}: unsupported semantic rubric")
    path = pinned_path(spec, f"{dataset['dataset_id']} semantic rubric")
    value = load_json(path)
    rows = value.get("questions") if isinstance(value, Mapping) else None
    if not isinstance(rows, list) or len(rows) != spec.get("count"):
        raise DatasetError(f"{dataset['dataset_id']}: semantic rubric count drift")
    result: dict[str, dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict):
            raise DatasetError(f"{dataset['dataset_id']}: invalid semantic rubric row")
        identifier = normalize_question_id(row.get("id"))
        points = row.get("required_points")
        focus = row.get("focus_papers")
        minimum = row.get("min_papers")
        if identifier in result:
            raise DatasetError(f"{dataset['dataset_id']}: duplicate semantic rubric {identifier}")
        if (
            not isinstance(points, list)
            or len(points) < 1
            or any(not isinstance(point, str) or not point.strip() for point in points)
            or len(points) != len(set(points))
        ):
            raise DatasetError(f"{dataset['dataset_id']}/{identifier}: invalid required points")
        if not isinstance(focus, list) or not focus or any(not isinstance(item, str) for item in focus):
            raise DatasetError(f"{dataset['dataset_id']}/{identifier}: invalid focus documents")
        if isinstance(minimum, bool) or not isinstance(minimum, int) or not 1 <= minimum <= len(focus):
            raise DatasetError(f"{dataset['dataset_id']}/{identifier}: invalid minimum document count")
        result[identifier] = row
    return result


def dataset_cohorts(dataset: Mapping[str, Any]) -> dict[str, list[str]]:
    """Load the named, checked question cohorts."""

    path = pinned_path(dataset["cohorts"], f"{dataset['dataset_id']} cohorts")
    value = load_json(path)
    cohorts = value.get("cohorts") if isinstance(value, Mapping) else None
    if not isinstance(cohorts, Mapping):
        raise DatasetError(f"{path}: no cohorts object")
    result: dict[str, list[str]] = {}
    for name, rows in cohorts.items():
        if not isinstance(name, str) or not isinstance(rows, list):
            raise DatasetError(f"{path}: invalid cohort entry")
        normalized = [normalize_question_id(item) for item in rows]
        if len(normalized) != len(set(normalized)):
            raise DatasetError(f"{path}: duplicate ID in cohort {name}")
        result[name] = normalized
    return result


def manifest_source_files(manifest_path: Path) -> dict[str, Path]:
    """Resolve every declared source file relative to its manifest directory."""

    manifest = load_json(manifest_path)
    sources = manifest.get("sources") if isinstance(manifest, Mapping) else None
    if not isinstance(sources, list):
        raise DatasetError(f"{manifest_path}: no sources array")
    root = manifest_path.parent.resolve()
    files: dict[str, Path] = {}
    for number, source in enumerate(sources, 1):
        value = source.get("path") if isinstance(source, Mapping) else None
        if not isinstance(value, str) or not value:
            raise DatasetError(f"{manifest_path}: source {number} has no path")
        pure = PurePosixPath(value)
        if pure.is_absolute() or ".." in pure.parts:
            raise DatasetError(f"{manifest_path}: unsafe source path {value!r}")
        matches = sorted(root.glob(value)) if GLOB_MAGIC.search(value) else [root / Path(*pure.parts)]
        if not matches:
            raise DatasetError(f"{manifest_path}: source pattern matched no files: {value}")
        expanded: list[Path] = []
        for match in matches:
            if match.is_dir():
                expanded.extend(sorted(item for item in match.rglob("*") if item.is_file()))
            elif match.is_file():
                expanded.append(match)
            else:
                raise DatasetError(f"{manifest_path}: source is absent: {value}")
        for match in expanded:
            resolved = match.resolve()
            if root not in resolved.parents:
                raise DatasetError(f"{manifest_path}: source escapes manifest root: {value}")
            relative = resolved.relative_to(root).as_posix()
            prior = files.get(relative)
            if prior is not None and prior != resolved:
                raise DatasetError(f"{manifest_path}: conflicting staged path: {relative}")
            files[relative] = resolved
    return files


def validate_dataset(dataset_id: str, family_id: str | None = None) -> dict[str, Any]:
    """Validate one descriptor, its corpus, cohorts, plans, and skill pairs."""

    dataset = load_dataset(dataset_id)
    if dataset.get("schema_version") != "semantic-okf-evaluation-dataset/1.0":
        raise DatasetError(f"{dataset_id}: unsupported schema_version")
    families = load_families()
    plan_specs = dataset.get("plans")
    if not isinstance(plan_specs, Mapping) or set(plan_specs) != set(families):
        raise DatasetError(f"{dataset_id}: plans must cover every registered family")
    selected = [family_id] if family_id else sorted(families)
    if any(item not in families for item in selected):
        raise DatasetError(f"{dataset_id}: unknown family {family_id!r}")

    manifest_path = pinned_path(dataset["source_manifest"], f"{dataset_id} source manifest")
    source_files = manifest_source_files(manifest_path)
    source_manifest = load_json(manifest_path)
    source_count = len(source_manifest["sources"])
    if source_count != dataset["source_manifest"].get("count"):
        raise DatasetError(f"{dataset_id}: source count drift")

    questions = dataset_questions(dataset)
    question_ids = [row["normalized_id"] for row in questions]
    if len(question_ids) != dataset["questions"].get("count") or len(question_ids) != len(set(question_ids)):
        raise DatasetError(f"{dataset_id}: question count or identity drift")

    rubrics = dataset_semantic_rubrics(dataset)
    questions_by_id = {row["normalized_id"]: row for row in questions}
    if not set(rubrics).issubset(questions_by_id):
        raise DatasetError(f"{dataset_id}: semantic rubric contains unknown questions")
    for identifier, rubric in rubrics.items():
        question = questions_by_id[identifier]
        qrels = question.get("qrels")
        papers = qrels.get("paper_ids") if isinstance(qrels, Mapping) else None
        if rubric.get("question") != question.get("question"):
            raise DatasetError(f"{dataset_id}/{identifier}: semantic rubric question text drift")
        if papers != rubric.get("focus_papers"):
            raise DatasetError(f"{dataset_id}/{identifier}: semantic rubric focus drift")

    truth_path = pinned_path(dataset["hard_ground_truth"], f"{dataset_id} hard ground truth")
    truths = load_jsonl(truth_path)
    truth_ids = [normalize_question_id(row.get("id")) for row in truths]
    if len(truth_ids) != dataset["hard_ground_truth"].get("count") or not set(truth_ids).issubset(question_ids):
        raise DatasetError(f"{dataset_id}: hard-ground-truth count or identity drift")

    combination = dataset.get("source_combination")
    if combination is not None:
        if not isinstance(combination, Mapping):
            raise DatasetError(f"{dataset_id}: source_combination must be null or a pinned file")
        pinned_path(combination, f"{dataset_id} source combination")

    cohorts = dataset_cohorts(dataset)
    partition = dataset.get("partition_cohorts")
    if not isinstance(partition, list) or any(name not in cohorts for name in partition):
        raise DatasetError(f"{dataset_id}: invalid partition_cohorts")
    partition_ids = [item for name in partition for item in cohorts[name]]
    if len(partition_ids) != len(set(partition_ids)) or set(partition_ids) != set(question_ids):
        raise DatasetError(f"{dataset_id}: partition cohorts must cover every question exactly once")

    for name in selected:
        family = families[name]
        plan = plan_specs[name]
        if bool(family.get("uses_plan")) != (plan is not None):
            raise DatasetError(f"{dataset_id}/{name}: plan presence disagrees with family contract")
        if plan is not None:
            if not isinstance(plan, Mapping):
                raise DatasetError(f"{dataset_id}/{name}: plan must be a pinned file")
            pinned_path(plan, f"{dataset_id}/{name} plan")
        build_skill = repo_path(f"skills/{family['build_skill']}", f"{name} build skill")
        consult_skill = repo_path(f"skills/{family['consult_skill']}", f"{name} consult skill")
        if not (build_skill / "SKILL.md").is_file() or not (consult_skill / "SKILL.md").is_file():
            raise DatasetError(f"{dataset_id}/{name}: skill pair is incomplete")
        if not (build_skill / "scripts" / family["build_script"]).is_file():
            raise DatasetError(f"{dataset_id}/{name}: build script is absent")
        if not (build_skill / "scripts" / family["validate_script"]).is_file():
            raise DatasetError(f"{dataset_id}/{name}: validator script is absent")

    reference = dataset.get("reference_bundle")
    reference_present = False
    if reference is not None:
        if not isinstance(reference, str):
            raise DatasetError(f"{dataset_id}: reference_bundle must be a path or null")
        reference_present = (repo_path(reference, f"{dataset_id} reference bundle") / "semantic/records.jsonl").is_file()
        if not reference_present:
            raise DatasetError(f"{dataset_id}: checked reference bundle is incomplete")

    return {
        "status": "pass",
        "dataset_id": dataset_id,
        "question_count": len(questions),
        "hard_question_count": len(truths),
        "semantic_rubric_count": len(rubrics),
        "source_count": source_count,
        "source_file_count": len(source_files),
        "cohort_counts": {name: len(cohorts[name]) for name in partition},
        "families": selected,
        "reference_bundle_present": reference_present,
    }


def build_arguments(family: Mapping[str, Any], *, agent: bool) -> list[str]:
    """Return the family-specific build arguments for staged input."""

    root = "/dataset" if agent else "<STAGED_INPUT>"
    arguments = [f"{root}/manifest.json"]
    if family["uses_plan"]:
        arguments.append(f"{root}/plan.json")
    arguments.append("/workspace/knowledge" if agent else "<OUTPUT_BUNDLE>")
    return arguments


def stage_dataset(dataset_id: str, family_id: str, output: Path) -> dict[str, Any]:
    """Create a leak-free raw-input tree for build-plus-consult evaluation."""

    validate_dataset(dataset_id, family_id)
    dataset = load_dataset(dataset_id)
    family = load_families()[family_id]
    manifest_path = pinned_path(dataset["source_manifest"], f"{dataset_id} source manifest")
    shutil.copyfile(manifest_path, output / "manifest.json")
    staged_files: list[dict[str, str]] = []
    for relative, source in manifest_source_files(manifest_path).items():
        target = output / Path(*PurePosixPath(relative).parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        staged_files.append({"path": relative, "sha256": sha256_file(target)})
    plan_spec = dataset["plans"][family_id]
    if plan_spec is not None:
        shutil.copyfile(pinned_path(plan_spec, f"{dataset_id}/{family_id} plan"), output / "plan.json")
    payload_hash = tree_digest(output)
    host_args = build_arguments(family, agent=False)
    agent_args = build_arguments(family, agent=True)
    receipt = {
        "schema_version": "semantic-okf-evaluation-staged-input/1.0",
        "dataset_id": dataset_id,
        "family": family_id,
        "source_manifest_sha256": sha256_file(output / "manifest.json"),
        "plan_sha256": sha256_file(output / "plan.json") if (output / "plan.json").is_file() else None,
        "payload_tree_sha256": payload_hash,
        "source_files": staged_files,
        "evaluator_material_included": False,
        "agent_mount": {"source": "<STAGED_INPUT>", "target": "/dataset", "read_only": True},
        "agent_build": {
            "skill": family["build_skill"],
            "script": family["build_script"],
            "arguments": agent_args,
        },
        "agent_validate": {
            "skill": family["build_skill"],
            "script": family["validate_script"],
            "arguments": ["/workspace/knowledge", "--output-format", "json"],
        },
        "host_commands": {
            "build": [
                "python",
                f"skills/{family['build_skill']}/scripts/{family['build_script']}",
                *host_args,
                "--output-format",
                "json",
            ],
            "validate": [
                "python",
                f"skills/{family['build_skill']}/scripts/{family['validate_script']}",
                "<OUTPUT_BUNDLE>",
                "--output-format",
                "json",
            ],
        },
    }
    write_json(output / "input-manifest.json", receipt)
    return receipt


def materialize_stage(
    dataset_id: str,
    family_id: str,
    output: Path,
    *,
    replace: bool,
    check: bool,
) -> dict[str, Any]:
    """Stage atomically or compare an existing stage with a fresh candidate."""

    output = output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    candidate = Path(tempfile.mkdtemp(prefix=f".{output.name}.candidate-", dir=output.parent))
    try:
        receipt = stage_dataset(dataset_id, family_id, candidate)
        digest = tree_digest(candidate)
        if check:
            if not output.is_dir():
                raise DatasetError(f"staged input is absent: {output}")
            if tree_digest(output) != digest:
                raise DatasetError(f"staged input drift: {output}")
            return {"status": "pass", "tree_sha256": digest, **receipt}
        if output.exists():
            if not replace:
                raise DatasetError(f"output exists; use --replace: {output}")
            backup = output.with_name(f".{output.name}.previous-{os.getpid()}")
            output.rename(backup)
            try:
                candidate.rename(output)
            except BaseException:
                backup.rename(output)
                raise
            shutil.rmtree(backup)
        else:
            candidate.rename(output)
        return {"status": "pass", "tree_sha256": digest, **receipt}
    finally:
        if candidate.exists():
            shutil.rmtree(candidate)


def describe(dataset_id: str, family_id: str) -> dict[str, Any]:
    """Describe the two execution modes and their authority boundaries."""

    report = validate_dataset(dataset_id, family_id)
    family = load_families()[family_id]
    return {
        **report,
        "family": family_id,
        "skill_pair": [family["build_skill"], family["consult_skill"]],
        "modes": {
            "build-consult": {
                "installed_skills": [family["build_skill"], family["consult_skill"]],
                "read_only_mount": "/dataset",
                "generated_knowledge": "/workspace/knowledge",
                "prebuilt_knowledge_mounted": False,
            },
            "consult-only": {
                "installed_skills": [family["consult_skill"]],
                "read_only_mount": "/knowledge",
                "raw_sources_mounted": False,
            },
        },
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse dataset management commands."""

    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    listing = subparsers.add_parser("list", help="List checked datasets and counts.")
    listing.add_argument("--json", action="store_true")
    validation = subparsers.add_parser("validate", help="Validate checked descriptors and inputs.")
    validation.add_argument("--dataset", choices=[*available_datasets(), "all"], default="all")
    validation.add_argument("--family", choices=sorted(load_families()))
    preparation = subparsers.add_parser("prepare", help="Stage raw, evaluator-free build input.")
    preparation.add_argument("--dataset", choices=available_datasets(), required=True)
    preparation.add_argument("--family", choices=sorted(load_families()), required=True)
    preparation.add_argument("--output", type=Path)
    preparation.add_argument("--replace", action="store_true")
    preparation.add_argument("--check", action="store_true")
    description = subparsers.add_parser("describe", help="Describe both evaluation modes.")
    description.add_argument("--dataset", choices=available_datasets(), required=True)
    description.add_argument("--family", choices=sorted(load_families()), required=True)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    """Run one dataset management command."""

    args = parse_args(argv)
    try:
        if args.command == "list":
            reports = [validate_dataset(identifier) for identifier in available_datasets()]
            if args.json:
                print(json.dumps(reports, ensure_ascii=False, sort_keys=True))
            else:
                for report in reports:
                    cohorts = ", ".join(f"{key}={value}" for key, value in report["cohort_counts"].items())
                    print(
                        f"{report['dataset_id']}: {report['source_count']} sources, "
                        f"{report['question_count']} questions ({cohorts})"
                    )
            return 0
        if args.command == "validate":
            identifiers = available_datasets() if args.dataset == "all" else [args.dataset]
            print(json.dumps([validate_dataset(item, args.family) for item in identifiers], sort_keys=True))
            return 0
        if args.command == "describe":
            print(json.dumps(describe(args.dataset, args.family), indent=2, sort_keys=True))
            return 0
        output = args.output or (HERE / "generated/inputs" / args.dataset / args.family)
        result = materialize_stage(
            args.dataset,
            args.family,
            output,
            replace=args.replace,
            check=args.check,
        )
        print(json.dumps(result, sort_keys=True))
        return 0
    except DatasetError as exc:
        raise SystemExit(str(exc)) from exc


if __name__ == "__main__":
    raise SystemExit(main())
