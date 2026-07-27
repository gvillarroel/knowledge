from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path
from typing import Any

import yaml


HERE = Path(__file__).resolve().parents[1]
REPO = HERE.parents[1]
CANONICAL_TASKS = (
    REPO
    / "evaluations"
    / "semantic-okf-datasets"
    / "generated"
    / "tasks"
    / "graphrag-papers-40"
    / "consult-only"
    / "classical"
)
CONSULT_DISCOVERY = (
    ("discovery", "q007"),
    ("discovery", "q019"),
)
DEFAULT_CONSULT_HOLDOUT_QUERY_IDS = ("q010", "q029")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prepare isolated Harbor jobs for RustMallet trace distillation."
    )
    parser.add_argument(
        "--runtime-repo-root",
        required=True,
        help="Absolute repository path as seen by the Linux Harbor runtime.",
    )
    parser.add_argument(
        "--auth-directory",
        required=True,
        help="Private Pi authentication directory mounted into Harbor containers.",
    )
    parser.add_argument(
        "--evolution-output-root",
        required=True,
        help="Absolute Linux-native directory that will contain append-only live runs.",
    )
    parser.add_argument(
        "--snapshot",
        default="tmp/rust-mallet-graphrag-b",
        help="Repository-relative validated RustMallet snapshot used by consult-only tasks.",
    )
    parser.add_argument(
        "--consult-skill",
        default="consult-semantic-okf-rust-mallet",
        help="Repository skill directory and logical skill name under evaluation.",
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
        "--runtime-consult-skill",
        help=(
            "Optional absolute Linux path to an immutable iterative parent bundle; "
            "defaults to the repository consult skill"
        ),
    )
    parser.add_argument(
        "--variant",
        default="rust-mallet-consult-evolution",
        help="Filesystem-safe task and Harbor job identity segment.",
    )
    parser.add_argument(
        "--reference-contract",
        action="store_true",
        help=(
            "accept compact reference_id evidence and resolve it through the "
            "mounted snapshot dictionary while retaining the legacy evidence form"
        ),
    )
    parser.add_argument(
        "--run-id",
        default="20260722-consult-trace-a",
        help="Append-only trace-distillation campaign identifier.",
    )
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
        default=HERE / "generated" / "evolution",
        help="Generated task and configuration root.",
    )
    return parser.parse_args()


def holdout_entries(values: list[str] | None) -> tuple[tuple[str, str], ...]:
    """Normalize an explicit untouched holdout cohort."""

    query_ids = tuple(values or DEFAULT_CONSULT_HOLDOUT_QUERY_IDS)
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


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8", newline="\n")


def write_json(path: Path, value: Any) -> None:
    write_text(
        path,
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
    )


def tree_digest(root: Path) -> str:
    digest = hashlib.sha256()
    files = (
        item
        for item in root.rglob("*")
        if item.is_file()
        and "__pycache__" not in item.parts
        and item.suffix != ".pyc"
    )
    for path in sorted(files):
        relative = path.relative_to(root).as_posix().encode("utf-8")
        digest.update(len(relative).to_bytes(8, "big"))
        digest.update(relative)
        payload = path.read_bytes()
        digest.update(len(payload).to_bytes(8, "big"))
        digest.update(payload)
    return digest.hexdigest()


def require_safe_output(path: Path) -> Path:
    resolved = path.resolve()
    allowed = (HERE / "generated").resolve()
    if not resolved.is_relative_to(allowed) or resolved == allowed:
        raise ValueError(f"output must be a child of {allowed}")
    return resolved


def enable_reference_contract(
    destination: Path, reference_dictionary: Path
) -> None:
    """Add dual legacy/reference evidence support to one copied Harbor task."""

    tests = destination / "tests"
    shutil.copy2(
        HERE / "evolution-assets" / "reference_contract.py",
        tests / "reference_contract.py",
    )
    # Harbor runs the verifier in a separate container that cannot see the
    # agent's read-only /knowledge mount. Seal the exact processed dictionary
    # into verifier-only task inputs instead of granting the verifier a second
    # runtime mount.
    shutil.copy2(reference_dictionary, tests / "reference-dictionary.json")
    score_path = tests / "score.py"
    score = score_path.read_text(encoding="utf-8")
    replacements = (
        (
            "from trace_status import classify_pi_trace\n",
            "from reference_contract import materialize_reference_evidence\n"
            "from trace_status import classify_pi_trace\n",
        ),
        (
            "    parse_error: str | None = None\n",
            "    parse_error: str | None = None\n"
            "    resolved_reference_count = 0\n",
        ),
        (
            "            output = strict_json(output_text)\n",
            "            output = strict_json(output_text)\n"
            "            output, resolved_reference_count = materialize_reference_evidence(\n"
            "                output, args.reference_dictionary\n"
            "            )\n",
        ),
        (
            "        except (json.JSONDecodeError, ScoreError) as exc:\n",
            "        except (json.JSONDecodeError, ScoreError, ValueError) as exc:\n",
        ),
        (
            '    rewards["reward"] = rewards["mechanical_qualification_gate"] * utility\n',
            '    rewards["reference_dictionary_resolution"] = float(\n'
            "        resolved_reference_count == len(evidence) and bool(evidence)\n"
            "    )\n"
            '    rewards["reward"] = rewards["mechanical_qualification_gate"] * utility\n',
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
            raise ValueError(f"reference scorer patch target is not unique: {old!r}")
        score = score.replace(old, new)
    write_text(score_path, score)

    test_path = tests / "test.sh"
    test = test_path.read_text(encoding="utf-8")
    old_test = "  --authority-root /tests/authority \\\n"
    if test.count(old_test) != 1:
        raise ValueError("reference test patch target is not unique")
    write_text(
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
    write_json(schema_path, schema)

    instruction_path = destination / "instruction.md"
    instruction = instruction_path.read_text(encoding="utf-8")
    old_instruction = (
        "Every evidence row must contain exactly `source_id`, `record_id`, "
        "`concept_path`, `source_path`, `record_sha256`, `locator`, and "
        "`text_sha256`, copied from an exact validated consultation hit."
    )
    new_instruction = (
        "Every evidence row must use one closed form: preferably exactly "
        "`reference_id` from the snapshot dictionary, or the legacy exact fields "
        "`source_id`, `record_id`, `concept_path`, `source_path`, "
        "`record_sha256`, `locator`, and `text_sha256`. The verifier resolves "
        "compact IDs to those seven canonical fields before scoring."
    )
    if instruction.count(old_instruction) != 1:
        raise ValueError("reference instruction patch target is not unique")
    write_text(
        instruction_path,
        instruction.replace(old_instruction, new_instruction),
    )


def copy_consult_task(
    source: Path,
    destination: Path,
    *,
    consult_skill: str,
    variant: str,
    reference_contract: bool,
    reference_dictionary: Path | None,
) -> dict[str, str]:
    if (
        not (source / "task.toml").is_file()
        or not (source / "instruction.md").is_file()
    ):
        raise ValueError(f"canonical task is incomplete: {source}")
    shutil.copytree(
        source,
        destination,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
    )

    task_path = destination / "task.toml"
    task = task_path.read_text(encoding="utf-8")
    task = task.replace("__classical__", f"__{variant}__")
    task = task.replace('family = "classical"', 'family = "rust-mallet"')
    task = task.replace('"classical",', '"rust-mallet",')
    task = task.replace(
        "consult-only question", "RustMallet consult-only evolution question"
    )
    write_text(task_path, task)

    instruction_path = destination / "instruction.md"
    instruction = instruction_path.read_text(encoding="utf-8")
    old = "consult-semantic-okf-classical"
    if old not in instruction:
        raise ValueError(f"expected consultant identity is absent: {source}")
    write_text(
        instruction_path,
        instruction.replace(old, consult_skill),
    )
    if reference_contract:
        if reference_dictionary is None:
            raise ValueError("reference dictionary path is required")
        enable_reference_contract(destination, reference_dictionary)
    return {
        "source": str(source.relative_to(REPO)).replace("\\", "/"),
        "source_tree_sha256": tree_digest(source),
        "generated_tree_sha256": tree_digest(destination),
    }


def bind_mount(source: str, target: str, *, read_only: bool = False) -> dict[str, Any]:
    value: dict[str, Any] = {
        "type": "bind",
        "source": source,
        "target": target,
        "bind": {"create_host_path": False},
    }
    if read_only:
        value["read_only"] = True
    return value


def job_config(
    *,
    name: str,
    task_root: str,
    task_ids: list[str],
    snapshot: str,
    auth_directory: str,
    attempts: int,
    jobs_dir: str,
    baseline_skill: str,
    model_name: str,
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
                bind_mount(snapshot, "/knowledge", read_only=True),
                bind_mount(auth_directory, "/root/.pi/agent"),
            ],
        },
        "agents": [
            {
                "name": "pi",
                "model_name": model_name,
                "n_concurrent": 1,
                "skills": [baseline_skill],
                "kwargs": {"version": "0.73.1", "thinking": "high"},
                "env": {"PI_CODING_AGENT_DIR": "/root/.pi/agent"},
            }
        ],
        "datasets": [{"path": task_root, "task_names": task_ids}],
    }


def trace_distillation_config(
    run_id: str,
    evolution_output_root: str,
    *,
    runtime_baseline_skill: str,
    discovery_job_name: str,
    variant: str,
) -> dict[str, Any]:
    campaign_root = f"{evolution_output_root.rstrip('/')}/{run_id}"
    return {
        "schemaVersion": 2,
        "run": {
            "id": f"{variant}-trace-distillation",
            "baselineSkill": runtime_baseline_skill,
            "outputDir": f"{campaign_root}/distillation",
        },
        "harbor": {
            "rewardKey": "reward",
            "passThreshold": 0.01,
            "requiredRewards": {
                "evidence_contract_gate": 1.0,
                "mechanical_qualification_gate": 1.0,
            },
            "requiredEnv": [],
            "requireDiscoveryLocks": True,
        },
        "discovery": {
            "artifacts": [f"{campaign_root}/{discovery_job_name}"],
            "jobConfigs": [],
        },
        "proposals": {
            "path": "consult-proposals.json",
            "minimumUniqueTrials": 2,
            "minimumUniqueTasks": 2,
        },
        "development": {
            "candidateArtifacts": [],
            "candidateJobConfigs": ["jobs/consult-development.yaml"],
            "minimumPassRate": 1.0,
        },
        "holdout": {
            "baselineArtifacts": [],
            "candidateArtifacts": [],
            "baselineJobConfigs": ["jobs/consult-holdout.yaml"],
            "candidateJobConfigs": ["jobs/consult-holdout.yaml"],
            "allowWeakFairness": False,
            "minimumMeanGain": 0.01,
            "allowTaskRegressions": False,
            "requireNoErrors": True,
        },
    }


def main() -> int:
    args = parse_args()
    consult_holdout = holdout_entries(args.holdout_queries)
    output = require_safe_output(args.output)
    runtime_root = args.runtime_repo_root.rstrip("/")
    if not runtime_root.startswith("/"):
        raise ValueError("--runtime-repo-root must be an absolute Linux path")
    evolution_output_root = args.evolution_output_root.rstrip("/")
    if not evolution_output_root.startswith("/"):
        raise ValueError("--evolution-output-root must be an absolute Linux path")
    if not args.auth_directory.startswith("/"):
        raise ValueError("--auth-directory must be an absolute Linux path")
    if (
        not args.consult_skill
        or "/" in args.consult_skill
        or "\\" in args.consult_skill
    ):
        raise ValueError("--consult-skill must be one repository skill directory name")
    if not args.model_name or "/" not in args.model_name:
        raise ValueError("--model-name must include a provider and model")
    if not args.variant or any(
        character not in "abcdefghijklmnopqrstuvwxyz0123456789-_"
        for character in args.variant
    ):
        raise ValueError("--variant must contain only lowercase letters, digits, '-' or '_'")
    consult_skill = REPO / "skills" / args.consult_skill
    if not (consult_skill / "SKILL.md").is_file():
        raise ValueError(f"consult skill is absent: {consult_skill}")
    snapshot = (REPO / args.snapshot).resolve()
    if not (snapshot / "classical" / "index.json").is_file():
        raise ValueError(f"validated RustMallet snapshot is absent: {snapshot}")
    if args.reference_contract and not (
        snapshot / "classical" / "references.json"
    ).is_file():
        raise ValueError("--reference-contract requires classical/references.json")

    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)

    manifest: dict[str, Any] = {
        "schema_version": "semantic-okf-rust-mallet-harbor-evolution-inputs/1.0",
        "snapshot": args.snapshot.replace("\\", "/"),
        "snapshot_tree_sha256": tree_digest(snapshot),
        "reference_contract": args.reference_contract,
        "model_name": args.model_name,
        "splits": {"consult-discovery": {}, "consult-holdout": {}},
    }
    reference_dictionary = (
        snapshot / "classical" / "references.json"
        if args.reference_contract
        else None
    )
    if reference_dictionary is not None:
        manifest["reference_dictionary_sha256"] = hashlib.sha256(
            reference_dictionary.read_bytes()
        ).hexdigest()
    for split, entries in (
        ("consult-discovery", CONSULT_DISCOVERY),
        ("consult-holdout", consult_holdout),
    ):
        destination_root = output / "tasks" / split
        for cohort, task_id in entries:
            source = CANONICAL_TASKS / cohort / task_id
            destination = destination_root / task_id
            manifest["splits"][split][task_id] = copy_consult_task(
                source,
                destination,
                consult_skill=args.consult_skill,
                variant=args.variant,
                reference_contract=args.reference_contract,
                reference_dictionary=reference_dictionary,
            )

    output_relative = output.relative_to(REPO).as_posix()
    runtime_generated = f"{runtime_root}/{output_relative}"
    normalized_snapshot = args.snapshot.replace("\\", "/")
    runtime_snapshot = f"{runtime_root}/{normalized_snapshot}"
    runtime_baseline_skill = (
        args.runtime_consult_skill
        or f"{runtime_root}/skills/{args.consult_skill}"
    )
    if not runtime_baseline_skill.startswith("/"):
        raise ValueError("--runtime-consult-skill must be an absolute Linux path")
    manifest["runtime_consult_skill"] = runtime_baseline_skill
    campaign_root = f"{evolution_output_root}/{args.run_id}"
    discovery_job_name = f"{args.variant}-trace-discovery"
    jobs = output / "jobs"
    jobs.mkdir()
    for name, entries, attempts in (
        ("consult-discovery", CONSULT_DISCOVERY, 1),
        ("consult-development", CONSULT_DISCOVERY, 1),
        ("consult-holdout", consult_holdout, 2),
    ):
        task_split = "consult-discovery" if name == "consult-development" else name
        job_name = (
            discovery_job_name
            if name == "consult-discovery"
            else f"{args.variant}-{name.replace('development', 'trace-development')}"
        )
        value = job_config(
            name=job_name,
            task_root=f"{runtime_generated}/tasks/{task_split}",
            task_ids=[task_id for _, task_id in entries],
            snapshot=runtime_snapshot,
            auth_directory=args.auth_directory,
            attempts=attempts,
            jobs_dir=campaign_root,
            baseline_skill=runtime_baseline_skill,
            model_name=args.model_name,
        )
        write_text(jobs / f"{name}.yaml", yaml.safe_dump(value, sort_keys=False))

    write_text(
        output / "consult-trace-distillation.yaml",
        yaml.safe_dump(
            trace_distillation_config(
                args.run_id,
                evolution_output_root,
                runtime_baseline_skill=runtime_baseline_skill,
                discovery_job_name=discovery_job_name,
                variant=args.variant,
            ),
            sort_keys=False,
        ),
    )
    write_json(output / "consult-proposals.json", {"proposals": []})
    write_json(output / "input-manifest.json", manifest)
    print(
        json.dumps(
            {
                "status": "pass",
                "output": str(output),
                "consult_discovery_tasks": len(CONSULT_DISCOVERY),
                "consult_holdout_tasks": len(consult_holdout),
                "consult_holdout_query_ids": [
                    task_id for _, task_id in consult_holdout
                ],
                "snapshot_tree_sha256": manifest["snapshot_tree_sha256"],
                "consult_skill": args.consult_skill,
                "variant": args.variant,
                "reference_contract": args.reference_contract,
                "model_name": args.model_name,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
