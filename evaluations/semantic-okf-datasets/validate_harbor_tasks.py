#!/usr/bin/env python3
"""Validate generated dual-mode Harbor tasks and execute every structural oracle."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path
from typing import Any, Mapping, Sequence

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))

import dataset_tool as data  # noqa: E402
import generate_harbor_tasks as tasks  # noqa: E402

HEX64 = re.compile(r"\b[0-9a-f]{64}\b")


class ValidationError(ValueError):
    """Raised when generated tasks violate the checked evaluation contract."""


def forbidden_fragments(
    question: Mapping[str, Any], truth: Mapping[str, Any] | None
) -> set[str]:
    """Return exact evaluator-only values that an agent instruction must not contain."""

    values: set[str] = set()
    qrels = question.get("qrels", {})
    if isinstance(qrels, Mapping):
        for key in ("document_ids", "source_ids"):
            values.update(str(value) for value in qrels.get(key, []))
    rubric = question.get("semantic_rubric")
    if isinstance(rubric, Mapping):
        values.update(str(value) for value in rubric.get("required_points", []))
    if truth is not None:
        for row in truth.get("authoritative_evidence", []):
            if isinstance(row, Mapping):
                for key in ("path", "locator", "file_sha256", "text_sha256", "upstream_path"):
                    if isinstance(row.get(key), str):
                        values.add(row[key])
        ground = truth.get("ground_truth", {})
        if isinstance(ground, Mapping):
            for collection in ("answer_claims", "important_negatives"):
                for row in ground.get(collection, []):
                    if isinstance(row, Mapping) and isinstance(row.get("statement"), str):
                        values.add(row["statement"])
    return {value for value in values if len(value) >= 8}


def mode_boundaries(
    instruction: str,
    mode: str,
    family: Mapping[str, Any],
    identifier: str,
) -> None:
    """Check that instructions expose exactly the resources intended for one mode."""

    if mode == "consult-only":
        required = ("/knowledge", family["consult_skill"], "Do not build")
        forbidden = ("/dataset", "/workspace/knowledge", family["build_skill"])
    else:
        required = (
            "/dataset/manifest.json",
            "/workspace/knowledge",
            family["build_skill"],
            family["consult_skill"],
            "No prebuilt knowledge snapshot is mounted",
        )
        forbidden = ("mounted read-only at `/knowledge`",)
    if any(value not in instruction for value in required):
        raise ValidationError(f"{identifier}: incomplete {mode} workflow instruction")
    if any(value in instruction for value in forbidden):
        raise ValidationError(f"{identifier}: {mode} instruction crosses its resource boundary")


def score_oracle(task_dir: Path, identifier: str) -> None:
    """Run the copied production grader against one generated oracle response."""

    tests = task_dir / "tests"
    with tempfile.TemporaryDirectory(prefix=f"semantic-okf-oracle-{identifier}-") as temporary:
        reward = Path(temporary) / "reward.json"
        diagnostics = Path(temporary) / "diagnostics.json"
        command = [
            sys.executable,
            str(tests / "score.py"),
            "--pi-log",
            str(task_dir / "solution/oracle-pi.jsonl"),
            "--question",
            str(tests / "question.json"),
            "--ledger",
            str(tests / "records.jsonl"),
            "--crosswalk",
            str(tests / "source-combination.json"),
            "--authority-root",
            str(tests / "authority"),
            "--reward",
            str(reward),
            "--diagnostics",
            str(diagnostics),
        ]
        ground_truth = tests / "hard-ground-truth.json"
        if ground_truth.is_file():
            command.extend(("--ground-truth", str(ground_truth)))
        completed = subprocess.run(command, cwd=REPO, capture_output=True, text=True)
        if completed.returncode != 0:
            raise ValidationError(f"{identifier}: oracle grader failed: {completed.stderr.strip()}")
        result = data.load_json(reward)
        if (
            result.get("evidence_contract_gate") != 1.0
            or result.get("mechanical_qualification_gate") != 1.0
            or result.get("reward") != 1.0
        ):
            detail = data.load_json(diagnostics) if diagnostics.is_file() else {}
            raise ValidationError(f"{identifier}: oracle did not pass: {detail}")


def validate_task(
    task_dir: Path,
    question: Mapping[str, Any],
    truth: Mapping[str, Any] | None,
    dataset_id: str,
    family_id: str,
    family: Mapping[str, Any],
    mode: str,
    cohort: str,
    records_sha256: str,
) -> None:
    """Validate one task's public prompt, hidden inputs, metadata, and oracle."""

    identifier = str(question["id"])
    required = (
        "instruction.md",
        "task.toml",
        "environment",
        "tests/Dockerfile",
        "tests/test.sh",
        "tests/score.py",
        "tests/trace_status.py",
        "tests/question.json",
        "tests/records.jsonl",
        "tests/source-combination.json",
        "solution/solve.sh",
        "solution/oracle-pi.jsonl",
    )
    missing = [value for value in required if not (task_dir / value).exists()]
    if missing:
        raise ValidationError(f"{identifier}: missing task files: {missing}")
    if any(path.is_file() for path in (task_dir / "environment").rglob("*")):
        raise ValidationError(f"{identifier}: public environment contains unexpected files")

    instruction = (task_dir / "instruction.md").read_text(encoding="utf-8")
    if instruction.count(str(question["question"])) != 1:
        raise ValidationError(f"{identifier}: question text is absent or duplicated")
    if HEX64.search(instruction):
        raise ValidationError(f"{identifier}: public instruction contains a hidden hash")
    if any(value in instruction for value in forbidden_fragments(question, truth)):
        raise ValidationError(f"{identifier}: evaluator-only value leaked into the instruction")
    mode_boundaries(instruction, mode, family, identifier)

    config = tomllib.loads((task_dir / "task.toml").read_text(encoding="utf-8"))
    metadata = config.get("metadata", {})
    expected_metadata = {
        "dataset_id": dataset_id,
        "family": family_id,
        "mode": mode,
        "cohort": cohort,
        "question_type": question["question_type"],
    }
    if config.get("schema_version") != "1.3" or any(
        metadata.get(key) != value for key, value in expected_metadata.items()
    ):
        raise ValidationError(f"{identifier}: Harbor metadata does not match the task identity")
    if config.get("verifier", {}).get("environment_mode") != "separate":
        raise ValidationError(f"{identifier}: verifier environment is not separate")
    artifacts = config.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts or artifacts[0].get("source") != "/logs/agent/pi.txt":
        raise ValidationError(f"{identifier}: Pi output log is not declared as an artifact")

    hidden_question = data.load_json(task_dir / "tests/question.json")
    if hidden_question != question:
        raise ValidationError(f"{identifier}: hidden question or qrel drift")
    if data.sha256_file(task_dir / "tests/records.jsonl") != records_sha256:
        raise ValidationError(f"{identifier}: hidden reference ledger drift")
    hard_path = task_dir / "tests/hard-ground-truth.json"
    if hard_path.is_file() != (truth is not None):
        raise ValidationError(f"{identifier}: hard-ground-truth presence mismatch")
    if truth is not None and data.load_json(hard_path) != truth:
        raise ValidationError(f"{identifier}: normalized hard-ground-truth drift")
    score_oracle(task_dir, identifier)


def validate(
    dataset_id: str,
    family_id: str,
    mode: str,
    task_root: Path,
) -> dict[str, Any]:
    """Validate one complete generated dataset/mode/family task tree."""

    data.validate_dataset(dataset_id, family_id)
    dataset = data.load_dataset(dataset_id)
    family = data.load_families()[family_id]
    manifest = data.load_json(task_root / "manifest.json")
    expected_identity = {"dataset_id": dataset_id, "family": family_id, "mode": mode}
    if any(manifest.get(key) != value for key, value in expected_identity.items()):
        raise ValidationError("generated task manifest identity mismatch")

    rubrics = data.dataset_semantic_rubrics(dataset)
    questions = {
        row["id"]: row
        for row in (
            tasks.normalized_question(
                item,
                dataset["question_format"],
                rubrics.get(data.normalize_question_id(item.get("id"))),
            )
            for item in data.dataset_questions(dataset)
        )
    }
    truths = tasks.normalized_truths(dataset)
    cohorts = data.dataset_cohorts(dataset)
    expected_counts = {name: len(cohorts[name]) for name in dataset["partition_cohorts"]}
    if manifest.get("question_count") != len(questions) or manifest.get("cohort_counts") != expected_counts:
        raise ValidationError("generated task manifest counts are invalid")
    records_hash = manifest.get("reference_records_sha256")
    if not isinstance(records_hash, str):
        raise ValidationError("generated task manifest has no reference ledger hash")

    count = 0
    for cohort in dataset["partition_cohorts"]:
        for identifier in cohorts[cohort]:
            validate_task(
                task_root / cohort / identifier,
                questions[identifier],
                truths.get(identifier),
                dataset_id,
                family_id,
                family,
                mode,
                cohort,
                records_hash,
            )
            count += 1
    actual_dirs = {
        path.relative_to(task_root).as_posix()
        for cohort in dataset["partition_cohorts"]
        for path in (task_root / cohort).iterdir()
        if path.is_dir()
    }
    expected_dirs = {
        f"{cohort}/{identifier}"
        for cohort in dataset["partition_cohorts"]
        for identifier in cohorts[cohort]
    }
    if actual_dirs != expected_dirs:
        raise ValidationError("generated task directories do not match the checked cohorts")
    return {
        "status": "pass",
        "dataset_id": dataset_id,
        "family": family_id,
        "mode": mode,
        "task_count": count,
        "leak_checks": "pass",
        "oracle_mechanical_qualification_gates": count,
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse complete task validation controls."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", choices=data.available_datasets(), required=True)
    parser.add_argument("--family", choices=sorted(data.load_families()), required=True)
    parser.add_argument("--mode", choices=tasks.MODES, required=True)
    parser.add_argument("--tasks", type=Path)
    parser.add_argument("--bundle", type=Path)
    parser.add_argument("--input", type=Path)
    parser.add_argument("--skip-generation-check", action="store_true")
    return parser.parse_args(argv)


def require_explicit_bundle_for_nondefault_tasks(
    dataset_id: str,
    family_id: str,
    mode: str,
    task_root: Path,
    dataset: Mapping[str, Any],
    supplied_bundle: Path | None,
) -> None:
    """Reject an implicit default bundle that cannot reproduce existing tasks."""

    if supplied_bundle is not None:
        return
    manifest_path = task_root / "manifest.json"
    default_value = dataset.get("reference_bundle")
    if not manifest_path.is_file() or not isinstance(default_value, str):
        return
    manifest = data.load_json(manifest_path)
    pinned_hash = manifest.get("reference_bundle_tree_sha256")
    if not isinstance(pinned_hash, str):
        return
    default_bundle = data.repo_path(default_value, f"{dataset_id} reference bundle")
    if not (default_bundle / "semantic/records.jsonl").is_file():
        return
    default_hash = data.tree_digest(default_bundle)
    if pinned_hash == default_hash:
        return
    raise ValidationError(
        f"{dataset_id}/{mode}/{family_id}: existing tasks pin reference bundle "
        f"SHA-256 {pinned_hash}, but the dataset default bundle {default_bundle} "
        f"has SHA-256 {default_hash}. Pass --bundle <path-to-exact-{family_id}-bundle> "
        f"using the exact {family_id} bundle that generated these tasks."
    )


def main(argv: Sequence[str] | None = None) -> int:
    """Validate task isolation, oracle behavior, and deterministic regeneration."""

    args = parse_args(argv)
    task_root = (
        args.tasks or HERE / "generated/tasks" / args.dataset / args.mode / args.family
    ).resolve()
    try:
        dataset = data.load_dataset(args.dataset)
        require_explicit_bundle_for_nondefault_tasks(
            args.dataset,
            args.family,
            args.mode,
            task_root,
            dataset,
            args.bundle,
        )
        report = validate(args.dataset, args.family, args.mode, task_root)
        if not args.skip_generation_check:
            generated_manifest = data.load_json(task_root / "manifest.json")
            command = [
                sys.executable,
                str(HERE / "generate_harbor_tasks.py"),
                "--dataset",
                args.dataset,
                "--family",
                args.family,
                "--mode",
                args.mode,
                "--output",
                str(task_root),
                "--check",
                "--agent-network-mode",
                str(generated_manifest["agent_network_mode"]),
                "--verifier-network-mode",
                str(generated_manifest["verifier_network_mode"]),
            ]
            if args.bundle is not None:
                command.extend(("--bundle", str(args.bundle.resolve())))
            if args.input is not None:
                command.extend(("--input", str(args.input.resolve())))
            subprocess.run(command, cwd=REPO, check=True)
        report["deterministic"] = not args.skip_generation_check
        print(json.dumps(report, sort_keys=True))
        return 0
    except (data.DatasetError, tasks.GenerationError, ValidationError, OSError) as exc:
        raise SystemExit(str(exc)) from exc


if __name__ == "__main__":
    raise SystemExit(main())
