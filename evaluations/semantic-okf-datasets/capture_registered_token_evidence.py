#!/usr/bin/env python3
"""Capture compact token evidence for all eight registered strategy pairs."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any, Mapping, Sequence


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
DEFAULT_EVIDENCE = HERE / "token-usage-evidence.json"
DEFAULT_BUILD_JOBS = (
    REPO
    / "evaluations/semantic-okf-token-efficiency-study-v7"
    / "private/native-jobs"
)
DEFAULT_CONSULT_RUNS = (
    HERE
    / "generated/campaigns/20260717-papers-consult-gpt53-spark-01/runs"
)
DEFAULT_DIRECT_COMPARISON = REPO / "evaluations/LATEST-REPORT.comparison.json"
FAMILIES = (
    "adaptive",
    "classical",
    "embeddings",
    "ensemble",
    "entity-graph",
    "graphify",
    "legacy",
    "turso",
)
LABELS = {
    "adaptive": "Adaptive",
    "classical": "Classical",
    "embeddings": "Embeddings",
    "ensemble": "Ensemble",
    "entity-graph": "Entity Graph",
    "graphify": "Graphify",
    "legacy": "Legacy",
    "turso": "Turso",
}
REPLICATES = ("replicate-a", "replicate-b")
CONSULT_QUESTION_IDS = ("q005", "q010", "q015", "q020", "q025", "q029")
MODEL = "openai-codex/gpt-5.3-codex-spark"
PI_VERSION = "0.73.1"
THINKING = "high"
EXPECTED_BUILD_GATES = {
    "artifact_integrity_gate": 1.0,
    "invocation_coverage_gate": 1.0,
    "records_identity_gate": 1.0,
    "reward": 1.0,
    "workflow_safety_gate": 1.0,
}


class CaptureError(ValueError):
    """Raised when raw Harbor evidence cannot be compacted safely."""


def load_object(path: Path) -> dict[str, Any]:
    """Load one JSON object."""

    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise CaptureError(f"cannot read JSON object: {path}") from exc
    if not isinstance(value, dict):
        raise CaptureError(f"expected a JSON object: {path}")
    return value


def sha256_file(path: Path) -> str:
    """Return one file digest."""

    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(path: Path) -> str:
    """Return a repository-relative POSIX path."""

    try:
        return path.resolve().relative_to(REPO.resolve()).as_posix()
    except ValueError as exc:
        raise CaptureError(f"path escapes repository: {path}") from exc


def usage(result: Mapping[str, Any]) -> dict[str, int]:
    """Read Harbor usage with input-includes-cache semantics."""

    agent = result.get("agent_result")
    if not isinstance(agent, Mapping):
        raise CaptureError("trial has no agent_result")
    values: dict[str, int] = {}
    for source, target in (
        ("n_input_tokens", "input_tokens_including_cache"),
        ("n_cache_tokens", "cache_tokens_reported_separately"),
        ("n_output_tokens", "output_tokens"),
    ):
        value = agent.get(source)
        if (
            not isinstance(value, int)
            or isinstance(value, bool)
            or value < 0
        ):
            raise CaptureError(f"invalid {source}")
        values[target] = value
    if (
        values["cache_tokens_reported_separately"]
        > values["input_tokens_including_cache"]
    ):
        raise CaptureError("cache tokens exceed input tokens")
    values["total_tokens"] = (
        values["input_tokens_including_cache"] + values["output_tokens"]
    )
    return values


def model(result: Mapping[str, Any]) -> str:
    """Read the fully qualified model identity."""

    config = result.get("config")
    agent = config.get("agent") if isinstance(config, Mapping) else None
    value = agent.get("model_name") if isinstance(agent, Mapping) else None
    if not isinstance(value, str) or not value:
        raise CaptureError("trial has no bound model")
    return value


def pi_version(result: Mapping[str, Any]) -> str:
    """Read the Pi version from native agent metadata."""

    agent = result.get("agent_info")
    value = agent.get("version") if isinstance(agent, Mapping) else None
    if not isinstance(value, str) or not value:
        raise CaptureError("trial has no Pi version")
    return value


def one_trial_result(job: Path) -> Path:
    """Resolve the sole native trial result inside one job."""

    paths = sorted(job.glob("*__*/result.json"))
    if len(paths) != 1:
        raise CaptureError(
            f"expected one trial result in {job}, found {len(paths)}"
        )
    return paths[0]


def builder_diagnostics(
    result_path: Path,
    family: str,
) -> tuple[Path, str]:
    """Read the qualified output-tree identity from one native verifier."""

    path = result_path.parent / "verifier/diagnostics.json"
    value = load_object(path)
    bundles = value.get("bundles")
    commands = value.get("commands")
    if (
        value.get("schema_version")
        != "semantic-okf-builder-token-diagnostics/2.0"
        or value.get("status") != "qualified-single-folder"
        or value.get("family") != family
        or not isinstance(bundles, list)
        or len(bundles) != 1
        or not isinstance(bundles[0], Mapping)
        or bundles[0].get("artifact_integrity") is not True
        or bundles[0].get("records_identity") is not True
        or not isinstance(commands, Mapping)
        or commands.get("build_command_count") != 1
        or commands.get("validation_command_count") != 1
    ):
        raise CaptureError(f"builder diagnostics are unqualified: {path}")
    tree_sha256 = bundles[0].get("tree_sha256")
    if (
        not isinstance(tree_sha256, str)
        or not re.fullmatch(r"[0-9a-f]{64}", tree_sha256)
    ):
        raise CaptureError(f"builder tree identity is invalid: {path}")
    return path, tree_sha256


def capture_builders(jobs: Path) -> dict[str, Any]:
    """Capture the two-replicate builder matrix."""

    family_rows: list[dict[str, Any]] = []
    for family in FAMILIES:
        trials: list[dict[str, Any]] = []
        for replicate in REPLICATES:
            job = (
                jobs
                / (
                    "20260730-graphrag-papers-builder-token-single-spark-v2-"
                    f"{replicate}-{family}"
                )
            )
            result_path = one_trial_result(job)
            result = load_object(result_path)
            diagnostics_path, tree_sha256 = builder_diagnostics(
                result_path,
                family,
            )
            expected_task = (
                "knowledge/graphrag-papers-40__builder-token__"
                f"{family}__{replicate}"
            )
            if result.get("task_name") != expected_task:
                raise CaptureError(f"builder task identity drift: {result_path}")
            if model(result) != MODEL or pi_version(result) != PI_VERSION:
                raise CaptureError(f"builder execution contract drift: {result_path}")
            if result.get("exception_info") is not None:
                raise CaptureError(f"builder trial errored: {result_path}")
            verifier = result.get("verifier_result")
            rewards = (
                verifier.get("rewards")
                if isinstance(verifier, Mapping)
                else None
            )
            if rewards != EXPECTED_BUILD_GATES:
                raise CaptureError(
                    f"builder qualification gates failed: {result_path}"
                )
            trials.append(
                {
                    "replicate": replicate,
                    "task_name": expected_task,
                    "result_path": relative(result_path),
                    "result_sha256": sha256_file(result_path),
                    "diagnostics_path": relative(diagnostics_path),
                    "diagnostics_sha256": sha256_file(diagnostics_path),
                    "output_tree_sha256": tree_sha256,
                    "generated_folders": 1,
                    "usage": usage(result),
                    "qualified": True,
                    "expected_gates": EXPECTED_BUILD_GATES,
                }
            )
        tree_sha256s = {
            trial["output_tree_sha256"] for trial in trials
        }
        if len(tree_sha256s) != 1:
            raise CaptureError(
                f"{family} replicate folder inventories are not identical"
            )
        family_rows.append(
            {
                "methodology": family,
                "label": LABELS[family],
                "cross_replicate_tree_sha256": next(iter(tree_sha256s)),
                "trials": trials,
            }
        )
    return {
        "dataset_id": "graphrag-papers-40",
        "mode": "builder-token",
        "model": MODEL,
        "pi_version": PI_VERSION,
        "thinking": THINKING,
        "runtime_image_id": (
            "sha256:"
            "bcd2b2b57b968ff8b4976bedf8c5ddf7b7e2ff41c341f7a13a05ae4df2ffc9d8"
        ),
        "family_count": len(family_rows),
        "replicates_per_family": len(REPLICATES),
        "generated_folders_per_replicate": 1,
        "new_model_calls": len(family_rows) * len(REPLICATES),
        "families": family_rows,
    }


def question_id(result: Mapping[str, Any]) -> str:
    """Extract the canonical question ID from one native task identity."""

    task_name = result.get("task_name")
    if not isinstance(task_name, str):
        raise CaptureError("consultation trial has no task name")
    value = task_name.rsplit("__", 1)[-1]
    if value not in CONSULT_QUESTION_IDS:
        raise CaptureError(f"unexpected consultation question: {value}")
    return value


def capture_consultations(runs: Path) -> dict[str, Any]:
    """Capture the common six-question consultation matrix."""

    family_rows: list[dict[str, Any]] = []
    for family in FAMILIES:
        job = runs / f"{family}-holdout"
        candidates = sorted(job.glob("q*__*/result.json"))
        by_question: dict[str, tuple[Path, dict[str, Any]]] = {}
        for path in candidates:
            result = load_object(path)
            identifier = question_id(result)
            if identifier in by_question:
                raise CaptureError(
                    f"duplicate consultation trial: {family}/{identifier}"
                )
            by_question[identifier] = (path, result)
        if set(by_question) != set(CONSULT_QUESTION_IDS):
            raise CaptureError(
                f"{family} does not have the common holdout question set"
            )
        trials: list[dict[str, Any]] = []
        for identifier in CONSULT_QUESTION_IDS:
            path, result = by_question[identifier]
            expected_task = (
                "knowledge/graphrag-papers-40__consult-only__"
                f"{family}__{identifier}"
            )
            if result.get("task_name") != expected_task:
                raise CaptureError(
                    f"consultation task identity drift: {path}"
                )
            if model(result) != MODEL or pi_version(result) != PI_VERSION:
                raise CaptureError(
                    f"consultation execution contract drift: {path}"
                )
            exception = result.get("exception_info")
            exception_type = (
                exception.get("exception_type")
                if isinstance(exception, Mapping)
                else None
            )
            trials.append(
                {
                    "question_id": identifier,
                    "task_name": expected_task,
                    "result_path": relative(path),
                    "result_sha256": sha256_file(path),
                    "runtime_error": exception is not None,
                    "exception_type": exception_type,
                    "usage": usage(result),
                }
            )
        family_rows.append(
            {
                "methodology": family,
                "label": LABELS[family],
                "trials": trials,
            }
        )
    return {
        "dataset_id": "graphrag-papers-40",
        "mode": "consult-only",
        "cohort": "holdout",
        "question_ids": list(CONSULT_QUESTION_IDS),
        "model": MODEL,
        "pi_version": PI_VERSION,
        "thinking": THINKING,
        "family_count": len(family_rows),
        "queries_per_family": len(CONSULT_QUESTION_IDS),
        "source_campaign": (
            "20260717-papers-consult-gpt53-spark-01"
        ),
        "fairness_basis": (
            "The same six question IDs, model, Pi version, thinking level, "
            "corpus, and consult-only task contract are present for all eight "
            "families. The legacy campaign predates the immutable runtime "
            "input-binding v2 contract."
        ),
        "families": family_rows,
    }


def capture_direct_retrieval_routes(path: Path) -> dict[str, Any]:
    """Capture the exhaustive deterministic direct-retrieval inventory."""

    comparison = load_object(path)
    alternatives = comparison.get("alternatives")
    if (
        comparison.get("schema_version") != "final-report-comparison/1.0"
        or not isinstance(alternatives, list)
        or len(alternatives) != 25
    ):
        raise CaptureError("direct-retrieval comparison inventory drift")
    routes: list[dict[str, str]] = []
    observed: set[str] = set()
    for alternative in alternatives:
        if not isinstance(alternative, Mapping):
            raise CaptureError("direct-retrieval alternative is invalid")
        identifier = alternative.get("id")
        label = alternative.get("label")
        if (
            not isinstance(identifier, str)
            or not identifier
            or identifier in observed
            or not isinstance(label, str)
            or not label
        ):
            raise CaptureError("direct-retrieval route identity is invalid")
        observed.add(identifier)
        routes.append({"strategy": identifier, "label": label})
    return {
        "comparison_path": relative(path),
        "comparison_sha256": sha256_file(path),
        "route_count": len(routes),
        "llm_calls_per_retrieval": 0,
        "llm_tokens_per_retrieval": 0,
        "scope": (
            "Deterministic retrieval helper execution only. Any later "
            "grounded answer-generation agent is outside this zero-token unit."
        ),
        "routes": routes,
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", type=Path, default=DEFAULT_EVIDENCE)
    parser.add_argument("--build-jobs", type=Path, default=DEFAULT_BUILD_JOBS)
    parser.add_argument(
        "--consult-runs", type=Path, default=DEFAULT_CONSULT_RUNS
    )
    parser.add_argument(
        "--direct-comparison",
        type=Path,
        default=DEFAULT_DIRECT_COMPARISON,
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    """Capture and write compact checked evidence."""

    args = parse_args(argv)
    evidence_path = args.evidence.resolve()
    evidence = load_object(evidence_path)
    evidence["schema_version"] = "semantic-okf-token-usage-evidence/2.0"
    evidence["registered_build_matrix"] = capture_builders(
        args.build_jobs.resolve()
    )
    evidence["registered_consultation_matrix"] = capture_consultations(
        args.consult_runs.resolve()
    )
    evidence["direct_retrieval_routes"] = capture_direct_retrieval_routes(
        args.direct_comparison.resolve()
    )
    evidence_path.write_text(
        json.dumps(evidence, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        json.dumps(
            {
                "status": "captured",
                "evidence": str(evidence_path),
                "build_families": len(
                    evidence["registered_build_matrix"]["families"]
                ),
                "consult_families": len(
                    evidence["registered_consultation_matrix"]["families"]
                ),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except CaptureError as exc:
        raise SystemExit(str(exc)) from exc
