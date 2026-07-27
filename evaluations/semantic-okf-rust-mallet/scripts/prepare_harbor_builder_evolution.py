#!/usr/bin/env python3
"""Prepare isolated build-consult Harbor jobs for RustMallet builder evolution."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path
from typing import Any

import yaml

import prepare_harbor_evolution as consult_prep


HERE = Path(__file__).resolve().parents[1]
REPO = HERE.parents[1]
CANONICAL_TASKS = (
    REPO
    / "evaluations"
    / "semantic-okf-datasets"
    / "generated"
    / "tasks"
    / "graphrag-papers-40"
    / "build-consult"
    / "legacy"
)
CANONICAL_INPUT = (
    REPO
    / "evaluations"
    / "semantic-okf-datasets"
    / "generated"
    / "inputs"
    / "graphrag-papers-40"
    / "legacy"
)
PLAN = HERE / "rust-mallet-plan.json"
EXPECTED_REFERENCES = (
    REPO / "tmp" / "rust-mallet-graphrag-reference" / "classical" / "references.json"
)
DISCOVERY = (("discovery", "q007"), ("discovery", "q019"))
DEFAULT_HOLDOUT_QUERY_IDS = ("q010", "q029")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime-repo-root", required=True)
    parser.add_argument("--auth-directory", required=True)
    parser.add_argument("--evolution-output-root", required=True)
    parser.add_argument(
        "--build-skill", default="build-semantic-okf-rust-mallet-evolved"
    )
    parser.add_argument(
        "--consult-skill", default="consult-semantic-okf-rust-mallet-evolved"
    )
    parser.add_argument(
        "--model-name",
        default="openai-codex/gpt-5.3-codex-spark",
        help=(
            "One Harbor agent model identity used unchanged across discovery, "
            "development, and holdout."
        ),
    )
    parser.add_argument(
        "--variant", default="rust-mallet-reference-builder-evolution"
    )
    parser.add_argument("--run-id", default="20260723-builder-reference-a")
    parser.add_argument(
        "--holdout-query",
        action="append",
        dest="holdout_queries",
        help=(
            "Untouched canonical holdout query ID. Repeat at least twice. "
            "Defaults to q010 and q029 for backward compatibility."
        ),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=HERE / "generated" / "builder-evolution",
    )
    return parser.parse_args()


def holdout_entries(values: list[str] | None) -> tuple[tuple[str, str], ...]:
    """Normalize an explicit untouched build-consult holdout cohort."""

    query_ids = tuple(values or DEFAULT_HOLDOUT_QUERY_IDS)
    if len(query_ids) < 2:
        raise ValueError("at least two holdout queries are required")
    if len(set(query_ids)) != len(query_ids):
        raise ValueError("holdout queries must be unique")
    invalid = [
        query_id
        for query_id in query_ids
        if not query_id.startswith("q")
        or len(query_id) != 4
        or not query_id[1:].isdigit()
    ]
    if invalid:
        raise ValueError(f"invalid holdout query IDs: {invalid}")
    missing = [
        query_id
        for query_id in query_ids
        if not (CANONICAL_TASKS / "holdout" / query_id).is_dir()
    ]
    if missing:
        raise ValueError(f"canonical holdout queries are absent: {missing}")
    return tuple(("holdout", query_id) for query_id in query_ids)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def copy_input(destination: Path) -> dict[str, Any]:
    shutil.copytree(
        CANONICAL_INPUT,
        destination,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
    )
    shutil.copy2(PLAN, destination / "rust-mallet-plan.json")
    return {
        "canonical_input_tree_sha256": consult_prep.tree_digest(CANONICAL_INPUT),
        "generated_input_tree_sha256": consult_prep.tree_digest(destination),
        "plan_sha256": sha256_file(destination / "rust-mallet-plan.json"),
        "evaluator_material_included": False,
    }


def enable_build_reference_contract(destination: Path) -> None:
    """Add compact-reference support to one build-consult scorer v1 task."""

    tests = destination / "tests"
    shutil.copy2(
        HERE / "evolution-assets" / "reference_contract.py",
        tests / "reference_contract.py",
    )
    shutil.copy2(EXPECTED_REFERENCES, tests / "reference-dictionary.json")
    score_path = tests / "score.py"
    score = score_path.read_text(encoding="utf-8")
    replacements = (
        (
            "from typing import Any, Iterable, Mapping, Sequence\n",
            "from typing import Any, Iterable, Mapping, Sequence\n\n"
            "from reference_contract import materialize_reference_evidence\n",
        ),
        (
            "    parse_error: str | None = None\n",
            "    parse_error: str | None = None\n"
            "    resolved_reference_count = 0\n",
        ),
        (
            "        output = strict_json(output_text)\n",
            "        output = strict_json(output_text)\n"
            "        output, resolved_reference_count = materialize_reference_evidence(\n"
            "            output, args.reference_dictionary\n"
            "        )\n",
        ),
        (
            "    except (json.JSONDecodeError, ScoreError) as exc:\n",
            "    except (json.JSONDecodeError, ScoreError, ValueError, OSError) as exc:\n",
        ),
        (
            '    rewards["reward"] = float(gate) * utility\n',
            '    rewards["reference_dictionary_resolution"] = float(\n'
            "        resolved_reference_count == len(evidence) and bool(evidence)\n"
            "    )\n"
            '    rewards["reward"] = float(gate) * utility\n',
        ),
        (
            '        "evidence_count": len(evidence),\n',
            '        "evidence_count": len(evidence),\n'
            '        "resolved_reference_count": resolved_reference_count,\n',
        ),
        (
            '    parser.add_argument("--ground-truth", type=Path)\n',
            '    parser.add_argument("--ground-truth", type=Path)\n'
            "    parser.add_argument(\n"
            '        "--reference-dictionary",\n'
            "        type=Path,\n"
            '        default=Path("/tests/reference-dictionary.json"),\n'
            "    )\n",
        ),
    )
    for old, new in replacements:
        if score.count(old) != 1:
            raise ValueError(f"builder scorer patch target is not unique: {old!r}")
        score = score.replace(old, new)
    consult_prep.write_text(score_path, score)

    test_path = tests / "test.sh"
    test = test_path.read_text(encoding="utf-8")
    old_test = "  --authority-root /tests/authority \\\n"
    if test.count(old_test) != 1:
        raise ValueError("builder test patch target is not unique")
    consult_prep.write_text(
        test_path,
        test.replace(
            old_test,
            old_test
            + "  --reference-dictionary /tests/reference-dictionary.json \\\n",
        ),
    )

    schema_path = tests / "answer.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    legacy = schema["properties"]["evidence"]["items"]
    schema["properties"]["evidence"]["items"] = {
        "oneOf": [
            legacy,
            {
                "type": "object",
                "additionalProperties": False,
                "required": ["reference_id"],
                "properties": {
                    "reference_id": {
                        "type": "string",
                        "pattern": "^ref-[0-9a-f]{24}$",
                    }
                },
            },
        ]
    }
    consult_prep.write_json(schema_path, schema)

    instruction_path = destination / "instruction.md"
    instruction = instruction_path.read_text(encoding="utf-8")
    old_instruction = (
        "Every evidence row must contain exactly `source_id`, `record_id`, "
        "`concept_path`, `source_path`, `record_sha256`, `locator`, and "
        "`text_sha256`, copied from an exact validated consultation hit."
    )
    new_instruction = (
        "Every evidence row must contain exactly `reference_id` from the "
        "dictionary generated inside the new snapshot. The hidden verifier "
        "resolves each ID to the seven canonical evidence fields before scoring."
    )
    if instruction.count(old_instruction) != 1:
        raise ValueError("builder reference instruction patch target is not unique")
    consult_prep.write_text(
        instruction_path,
        instruction.replace(old_instruction, new_instruction),
    )


def copy_task(
    source: Path,
    destination: Path,
    *,
    build_skill: str,
    consult_skill: str,
    variant: str,
) -> dict[str, str]:
    shutil.copytree(
        source,
        destination,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
    )
    task_path = destination / "task.toml"
    task = task_path.read_text(encoding="utf-8")
    task = task.replace("__legacy__", f"__{variant}__")
    task = task.replace('family = "legacy"', 'family = "rust-mallet"')
    task = task.replace('"legacy",', '"rust-mallet",')
    task = task.replace(
        "build-consult question",
        "RustMallet reference-builder evolution question",
    )
    consult_prep.write_text(task_path, task)

    instruction_path = destination / "instruction.md"
    instruction = instruction_path.read_text(encoding="utf-8")
    old_opening = (
        "Use the installed `build-semantic-okf` skill to build a new `legacy` "
        "Semantic OKF snapshot at `/workspace/knowledge` from "
        "`/dataset/manifest.json`. The `/dataset` mount is read-only and contains "
        "no questions, qrels, or ground truth. Run `validate_semantic_okf.py` "
        "against the new snapshot and continue only after validation passes. "
        "Then hand that exact snapshot to the installed `consult-semantic-okf` "
        "skill and answer from it read-only. No prebuilt knowledge snapshot is "
        "mounted in this mode. Do not use the web, model memory, or guesses. If "
        "the available knowledge cannot support an answer, return `answer: null` "
        "and an empty `evidence` array."
    )
    new_opening = (
        f"Use the installed `{build_skill}` skill to build a new RustMallet "
        "Semantic OKF snapshot at `/workspace/knowledge` from "
        "`/dataset/manifest.json` and `/dataset/rust-mallet-plan.json`. The "
        "`/dataset` mount is read-only and contains no questions, qrels, ground "
        "truth, or prebuilt knowledge. Run "
        "`validate_semantic_okf_rust_mallet.py` against the new snapshot and "
        "continue only after validation passes. Require the published snapshot "
        "to contain a validated `classical/references.json` bound by both the "
        "classical index and build report. Then hand that exact snapshot to the "
        f"installed `{consult_skill}` skill and answer from it read-only. No "
        "prebuilt knowledge snapshot is mounted in this mode. Do not use the web, "
        "model memory, or guesses. If the available knowledge cannot support an "
        "answer, return `answer: null` and an empty `evidence` array."
    )
    if instruction.count(old_opening) != 1:
        raise ValueError(f"builder instruction opening drifted: {source}")
    consult_prep.write_text(
        instruction_path,
        instruction.replace(old_opening, new_opening),
    )
    enable_build_reference_contract(destination)
    return {
        "source": source.relative_to(REPO).as_posix(),
        "source_tree_sha256": consult_prep.tree_digest(source),
        "generated_tree_sha256": consult_prep.tree_digest(destination),
    }


def bind_mount(source: str, target: str, *, read_only: bool = False) -> dict[str, Any]:
    result: dict[str, Any] = {
        "type": "bind",
        "source": source,
        "target": target,
        "bind": {"create_host_path": False},
    }
    if read_only:
        result["read_only"] = True
    return result


def job_config(
    *,
    name: str,
    jobs_dir: str,
    task_root: str,
    task_ids: list[str],
    input_root: str,
    auth_directory: str,
    build_skill: str,
    consult_skill: str,
    model_name: str,
    attempts: int,
) -> dict[str, Any]:
    return {
        "job_name": name,
        "jobs_dir": jobs_dir,
        "n_attempts": attempts,
        "n_concurrent_trials": 1,
        "quiet": False,
        "retry": {
            "max_retries": 0,
            "include_exceptions": [],
            "exclude_exceptions": [
                "AgentTimeoutError",
                "ApiUsageLimitError",
                "RewardFileEmptyError",
                "RewardFileNotFoundError",
                "VerifierOutputParseError",
                "VerifierTimeoutError",
            ],
            "wait_multiplier": 1.0,
            "min_wait_sec": 1.0,
            "max_wait_sec": 60.0,
        },
        "environment": {
            "type": "docker",
            "delete": True,
            "mounts": [
                bind_mount(input_root, "/dataset", read_only=True),
                bind_mount(auth_directory, "/root/.pi/agent"),
            ],
        },
        "agents": [
            {
                "name": "pi",
                "model_name": model_name,
                "n_concurrent": 1,
                "skills": [build_skill, consult_skill],
                "kwargs": {"version": "0.73.1", "thinking": "high"},
                "env": {"PI_CODING_AGENT_DIR": "/root/.pi/agent"},
            }
        ],
        "datasets": [{"path": task_root, "task_names": task_ids}],
    }


def trace_config(
    *,
    run_id: str,
    campaign_root: str,
    baseline_skill: str,
    discovery_job: str,
) -> dict[str, Any]:
    return {
        "schemaVersion": 2,
        "run": {
            "id": f"{run_id}-trace-distillation",
            "baselineSkill": baseline_skill,
            "outputDir": f"{campaign_root}/distillation",
        },
        "harbor": {
            "rewardKey": "reward",
            "passThreshold": 0.01,
            "requiredRewards": {
                "quality_gate": 1.0,
                "reference_dictionary_resolution": 1.0,
            },
            "requiredEnv": [],
            "requireDiscoveryLocks": True,
        },
        "discovery": {
            "artifacts": [f"{campaign_root}/{discovery_job}"],
            "jobConfigs": [],
        },
        "proposals": {
            "path": "builder-proposals.json",
            "minimumUniqueTrials": 2,
            "minimumUniqueTasks": 2,
        },
        "development": {
            "candidateArtifacts": [],
            "candidateJobConfigs": ["jobs/builder-development.yaml"],
            "minimumPassRate": 1.0,
        },
        "holdout": {
            "baselineArtifacts": [],
            "candidateArtifacts": [],
            "baselineJobConfigs": ["jobs/builder-holdout.yaml"],
            "candidateJobConfigs": ["jobs/builder-holdout.yaml"],
            "allowWeakFairness": False,
            "minimumMeanGain": 0.01,
            "allowTaskRegressions": False,
            "requireNoErrors": True,
        },
    }


def main() -> int:
    args = parse_args()
    builder_holdout = holdout_entries(args.holdout_queries)
    output = consult_prep.require_safe_output(args.output)
    runtime_root = args.runtime_repo_root.rstrip("/")
    evolution_root = args.evolution_output_root.rstrip("/")
    if not runtime_root.startswith("/") or not evolution_root.startswith("/"):
        raise ValueError("runtime and evolution roots must be absolute Linux paths")
    if not args.auth_directory.startswith("/"):
        raise ValueError("--auth-directory must be an absolute Linux path")
    if not args.model_name or "/" not in args.model_name:
        raise ValueError("--model-name must include a provider and model")
    for skill_name in (args.build_skill, args.consult_skill):
        if not (REPO / "skills" / skill_name / "SKILL.md").is_file():
            raise ValueError(f"skill is absent: {skill_name}")
    for required in (CANONICAL_INPUT / "manifest.json", PLAN, EXPECTED_REFERENCES):
        if not required.is_file():
            raise ValueError(f"required builder input is absent: {required}")
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)

    manifest: dict[str, Any] = {
        "schema_version": "semantic-okf-rust-mallet-builder-evolution-inputs/1.0",
        "input": copy_input(output / "input"),
        "model_name": args.model_name,
        "expected_reference_dictionary_sha256": sha256_file(EXPECTED_REFERENCES),
        "splits": {"builder-discovery": {}, "builder-holdout": {}},
    }
    for split, entries in (
        ("builder-discovery", DISCOVERY),
        ("builder-holdout", builder_holdout),
    ):
        for cohort, task_id in entries:
            source = CANONICAL_TASKS / cohort / task_id
            destination = output / "tasks" / split / task_id
            manifest["splits"][split][task_id] = copy_task(
                source,
                destination,
                build_skill=args.build_skill,
                consult_skill=args.consult_skill,
                variant=args.variant,
            )

    output_relative = output.relative_to(REPO).as_posix()
    runtime_generated = f"{runtime_root}/{output_relative}"
    runtime_input = f"{runtime_generated}/input"
    runtime_build_skill = f"{runtime_root}/skills/{args.build_skill}"
    runtime_consult_skill = f"{runtime_root}/skills/{args.consult_skill}"
    campaign_root = f"{evolution_root}/{args.run_id}"
    discovery_job = f"{args.variant}-trace-discovery"
    jobs = output / "jobs"
    jobs.mkdir()
    for name, entries, attempts in (
        ("builder-discovery", DISCOVERY, 1),
        ("builder-development", DISCOVERY, 1),
        ("builder-holdout", builder_holdout, 2),
    ):
        task_split = "builder-discovery" if name == "builder-development" else name
        job_name = discovery_job if name == "builder-discovery" else f"{args.variant}-{name}"
        value = job_config(
            name=job_name,
            jobs_dir=campaign_root,
            task_root=f"{runtime_generated}/tasks/{task_split}",
            task_ids=[task_id for _, task_id in entries],
            input_root=runtime_input,
            auth_directory=args.auth_directory,
            build_skill=runtime_build_skill,
            consult_skill=runtime_consult_skill,
            model_name=args.model_name,
            attempts=attempts,
        )
        consult_prep.write_text(
            jobs / f"{name}.yaml", yaml.safe_dump(value, sort_keys=False)
        )
    consult_prep.write_text(
        output / "builder-trace-distillation.yaml",
        yaml.safe_dump(
            trace_config(
                run_id=args.run_id,
                campaign_root=campaign_root,
                baseline_skill=runtime_build_skill,
                discovery_job=discovery_job,
            ),
            sort_keys=False,
        ),
    )
    consult_prep.write_json(output / "builder-proposals.json", {"proposals": []})
    consult_prep.write_json(output / "input-manifest.json", manifest)
    print(
        json.dumps(
            {
                "status": "pass",
                "output": str(output),
                "build_skill": args.build_skill,
                "consult_skill": args.consult_skill,
                "holdout_query_ids": [
                    task_id for _, task_id in builder_holdout
                ],
                "model_name": args.model_name,
                "reference_dictionary_sha256": manifest[
                    "expected_reference_dictionary_sha256"
                ],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
