#!/usr/bin/env python3
"""Compare a baseline expert with one retrospective supervised QEC expert."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import statistics
import sys
from types import ModuleType
from typing import Any, Mapping, Sequence


sys.dont_write_bytecode = True
SCHEMA_VERSION = "qec-retrospective-expert-evaluation/1.0"
DATASET_ID = "quantum-error-correction-papers-40"
SCRIPT_PATH = Path(__file__).resolve()
EVALUATION_ROOT = SCRIPT_PATH.parents[1]
REPO_ROOT = SCRIPT_PATH.parents[3]
BASE_PATH = (
    REPO_ROOT
    / "evaluations"
    / "semantic-okf-embeddings"
    / "scripts"
    / "compare_retrieval.py"
)
ARXIV_ID_RE = re.compile(
    r"(?<!\d)(\d{4})[.-](\d{4,5})(v\d+)(?!\w)",
    re.IGNORECASE,
)


class EvaluationError(RuntimeError):
    """Describe an invalid input, expert, ranking, or evaluation result."""


def _load_module(name: str, path: Path) -> ModuleType:
    specification = importlib.util.spec_from_file_location(name, path)
    if specification is None or specification.loader is None:
        raise EvaluationError(f"Cannot load Python module from {path}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


BASE = _load_module("qec_retrospective_retrieval_base", BASE_PATH)


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _portable_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return str(resolved)


def _fingerprint(path: Path) -> dict[str, Any]:
    return {
        "path": _portable_path(path),
        "bytes": path.stat().st_size,
        "sha256": _sha256_file(path),
    }


def _tree_inventory(root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted(
        root.rglob("*"),
        key=lambda item: item.relative_to(root).as_posix(),
    ):
        if path.is_symlink():
            raise EvaluationError(f"Expert contains a symlink: {path}")
        if path.is_file():
            rows.append(
                {
                    "path": path.relative_to(root).as_posix(),
                    "bytes": path.stat().st_size,
                    "sha256": _sha256_file(path),
                }
            )
    if not rows:
        raise EvaluationError(f"Expert has no regular files: {root}")
    return rows


def _load_json_object(path: Path, *, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise EvaluationError(f"Cannot read {label} at {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise EvaluationError(f"{label} must be a JSON object: {path}")
    return value


def _load_questions(
    path: Path,
) -> tuple[list[Any], dict[str, str]]:
    questions: list[Any] = []
    cohorts: dict[str, str] = {}
    identifiers: set[str] = set()
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        raise EvaluationError(f"Cannot read questions at {path}: {exc}") from exc
    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise EvaluationError(
                f"Invalid question JSON on line {line_number}: {exc}"
            ) from exc
        qrels = row.get("qrels") if isinstance(row, dict) else None
        identifier = row.get("id") if isinstance(row, dict) else None
        question = row.get("question") if isinstance(row, dict) else None
        paper_ids = qrels.get("paper_ids") if isinstance(qrels, dict) else None
        source_ids = qrels.get("source_ids") if isinstance(qrels, dict) else None
        if (
            not isinstance(identifier, str)
            or not identifier
            or identifier in identifiers
            or not isinstance(question, str)
            or not question.strip()
            or not isinstance(paper_ids, list)
            or not paper_ids
            or paper_ids != sorted(set(paper_ids))
            or not all(isinstance(item, str) for item in paper_ids)
            or not isinstance(source_ids, list)
            or not source_ids
            or source_ids != sorted(set(source_ids))
            or not all(isinstance(item, str) for item in source_ids)
            or len(paper_ids) != len(source_ids)
            or len(paper_ids) > 10
        ):
            raise EvaluationError(f"Question line {line_number} is invalid")
        match = re.match(r"^q(\d{3})", identifier)
        if match is None:
            raise EvaluationError(f"Question has no canonical number: {identifier}")
        number = int(match.group(1))
        identifiers.add(identifier)
        cohorts[identifier] = "hard" if number >= 31 else "development"
        questions.append(
            BASE.RetrievalQuestion(
                identifier,
                question,
                tuple(paper_ids),
                tuple(source_ids),
            )
        )
    if len(questions) != 40:
        raise EvaluationError(
            f"The frozen evaluation requires 40 questions, found {len(questions)}"
        )
    return questions, cohorts


def _paper_id(value: str) -> str:
    matches = {
        f"{match.group(1)}.{match.group(2)}{match.group(3).lower()}"
        for match in ARXIV_ID_RE.finditer(value)
    }
    if len(matches) != 1:
        raise EvaluationError(
            f"Expected one versioned arXiv identity in {value!r}"
        )
    return next(iter(matches))


def _runtime(expert: Path, label: str) -> ModuleType:
    helper = expert / "scripts" / "query_expert_knowledge.py"
    if not helper.is_file():
        raise EvaluationError(f"{label} query helper is absent: {helper}")
    suffix = hashlib.sha256(str(expert).encode("utf-8")).hexdigest()[:12]
    return _load_module(f"qec_expert_runtime_{label}_{suffix}", helper)


def _verified(runtime: ModuleType, *, label: str) -> dict[str, Any]:
    try:
        value = runtime.verify()
    except Exception as exc:
        raise EvaluationError(f"{label} verification raised: {exc}") from exc
    if (
        not isinstance(value, dict)
        or value.get("status") != "pass"
        or value.get("record_count") != 15
    ):
        raise EvaluationError(f"{label} verification did not pass")
    return value


def _hit(row: Mapping[str, Any]) -> Any:
    source_id = row.get("source_id")
    record_id = row.get("record_id")
    if not isinstance(source_id, str) or not isinstance(record_id, str):
        raise EvaluationError("Expert result lacks a source-scoped identity")
    text = row.get("text")
    if not isinstance(text, str):
        text = row.get("body")
    locator = row.get("locator")
    score = row.get("score")
    return BASE.RetrievalHit(
        source_id=source_id,
        paper_id=_paper_id(source_id),
        chunk_id=record_id,
        ordinal=None,
        concept_path=row.get("concept_path"),
        concept_id=row.get("concept_id"),
        record_id=record_id,
        record_sha256=row.get("record_sha256"),
        source_path=row.get("source_path"),
        locator=locator if isinstance(locator, dict) else None,
        text=text if isinstance(text, str) else None,
        text_sha256=(
            row.get("text_sha256")
            if isinstance(row.get("text_sha256"), str)
            else None
        ),
        score=float(score) if isinstance(score, (int, float)) else None,
    )


def _search(
    runtime: ModuleType,
    query: str,
    top_k: int,
    *,
    label: str,
) -> list[Any]:
    _verified(runtime, label=label)
    try:
        rows = runtime.search(
            query,
            source_id=None,
            concept_type=None,
            limit=top_k,
            show_content=True,
        )
    except Exception as exc:
        raise BASE.ComparisonError(f"{label} search raised: {exc}") from exc
    if not isinstance(rows, list):
        raise BASE.ComparisonError(f"{label} search did not return a list")
    hits: list[Any] = []
    identities: set[str] = set()
    try:
        for row in rows:
            if not isinstance(row, dict):
                raise EvaluationError(f"{label} returned a non-object hit")
            hit = _hit(row)
            if hit.paper_id in identities:
                continue
            identities.add(hit.paper_id)
            hits.append(hit)
            if len(hits) == top_k:
                break
    except EvaluationError as exc:
        raise BASE.ComparisonError(str(exc)) from exc
    return hits


def _mean_metrics(routes: Sequence[Mapping[str, Any]]) -> dict[str, float]:
    names = [
        *(f"recall_at_{cutoff}" for cutoff in BASE.METRIC_CUTOFFS),
        "mrr_at_10",
        "ndcg_at_10",
    ]
    return {
        name: statistics.fmean(
            float(route["paper_metrics"][name]) for route in routes
        )
        for name in names
    }


def _aggregate(routes: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    returned = sum(
        int(route["evidence_validity"]["returned"]) for route in routes
    )
    valid = sum(int(route["evidence_validity"]["valid"]) for route in routes)
    p95_values = [float(route["timing_ms"]["p95"]) for route in routes]
    medians = [float(route["timing_ms"]["median"]) for route in routes]
    return {
        "metrics": _mean_metrics(routes),
        "evidence": {
            "returned": returned,
            "valid": valid,
            "invalid": returned - valid,
            "ratio": valid / returned if returned else None,
        },
        "timing_ms": {
            "replicate_p95": p95_values,
            "representative_p95": statistics.median(p95_values),
            "maximum_p95": max(p95_values),
            "representative_median": statistics.median(medians),
        },
    }


def _ranking_signature(route: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "question_id": row["question_id"],
            "paper_ids": list(row["paper_ids"]),
        }
        for row in route["queries"]
    ]


def _cohort_metrics(
    route: Mapping[str, Any],
    cohorts: Mapping[str, str],
) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for cohort in sorted(set(cohorts.values())):
        rows = [
            row
            for row in route["queries"]
            if cohorts[str(row["question_id"])] == cohort
        ]
        names = ("recall_at_10", "mrr_at_10", "ndcg_at_10")
        result[cohort] = {
            "query_count": len(rows),
            "metrics": {
                name: statistics.fmean(
                    float(row["paper_metrics"][name]) for row in rows
                )
                for name in names
            },
        }
    return result


def _validate_expert_manifest(
    expert: Path,
    *,
    expected_schema: str,
    label: str,
) -> dict[str, Any]:
    manifest_path = expert / "expert-manifest.json"
    manifest = _load_json_object(manifest_path, label=f"{label} manifest")
    if (
        manifest.get("schema_version") != expected_schema
        or manifest.get("skill_name") != expert.name
    ):
        raise EvaluationError(f"{label} expert manifest contract is invalid")
    return manifest


def evaluate(args: argparse.Namespace) -> dict[str, Any]:
    """Run the paired all-question comparison for the requested replicates."""

    if args.top_k != 10:
        raise EvaluationError("This contract requires --top-k 10")
    if args.replicates < 3:
        raise EvaluationError("At least three replicates are required")
    baseline = args.baseline.resolve()
    candidate = args.candidate.resolve()
    questions_path = args.questions.resolve()
    for path, label in (
        (baseline, "baseline expert"),
        (candidate, "candidate expert"),
        (questions_path, "questions"),
    ):
        if not path.exists():
            raise EvaluationError(f"{label} is absent: {path}")

    baseline_manifest = _validate_expert_manifest(
        baseline,
        expected_schema="semantic-okf-expert-skill/1.0",
        label="baseline",
    )
    candidate_manifest = _validate_expert_manifest(
        candidate,
        expected_schema="semantic-okf-expert-skill/1.1",
        label="candidate",
    )
    profile = candidate_manifest.get("retrieval_profile")
    if (
        not isinstance(profile, dict)
        or profile.get("mode") != "retrospective-supervised-ngram"
        or profile.get("promotion_eligible") is not False
        or profile.get("question_count") != 40
    ):
        raise EvaluationError("Candidate profile boundary is not explicit")

    baseline_before = _tree_inventory(baseline)
    candidate_before = _tree_inventory(candidate)
    questions, cohorts = _load_questions(questions_path)
    baseline_runtime = _runtime(baseline, "baseline")
    candidate_runtime = _runtime(candidate, "candidate")
    baseline_verification = _verified(baseline_runtime, label="baseline")
    candidate_verification = _verified(candidate_runtime, label="candidate")
    if (
        candidate_verification.get("dataset_id") != DATASET_ID
        or candidate_verification.get("promotion_eligible") is not False
        or candidate_verification.get("candidate_state")
        != "retrospective-all-exposed-supervised-profile"
    ):
        raise EvaluationError("Candidate runtime disclosure is invalid")

    baseline_knowledge = baseline / "references" / "knowledge"
    candidate_knowledge = candidate / "references" / "knowledge"
    if _sha256_file(
        baseline_knowledge / "semantic" / "records.jsonl"
    ) != _sha256_file(candidate_knowledge / "semantic" / "records.jsonl"):
        raise EvaluationError("Treatments do not embed the same ledger")
    baseline_ledger = BASE.AuthoritativeLedger.from_bundle(baseline_knowledge)
    candidate_ledger = BASE.AuthoritativeLedger.from_bundle(candidate_knowledge)

    baseline_routes: list[dict[str, Any]] = []
    candidate_routes: list[dict[str, Any]] = []
    for replicate in range(1, args.replicates + 1):
        treatments = (
            ("baseline", baseline_runtime, baseline_knowledge, baseline_ledger),
            ("candidate", candidate_runtime, candidate_knowledge, candidate_ledger),
        )
        if replicate % 2 == 0:
            treatments = tuple(reversed(treatments))
        produced: dict[str, dict[str, Any]] = {}
        for label, runtime, knowledge, ledger in treatments:
            produced[label] = BASE.evaluate_route(
                f"{label}-replicate-{replicate}",
                knowledge,
                ledger,
                questions,
                lambda query, active=runtime, name=label: _search(
                    active,
                    query,
                    args.top_k,
                    label=name,
                ),
                continue_on_error=False,
            )
        baseline_routes.append(produced["baseline"])
        candidate_routes.append(produced["candidate"])

    for label, routes in (
        ("baseline", baseline_routes),
        ("candidate", candidate_routes),
    ):
        if any(route["error_count"] for route in routes):
            raise EvaluationError(f"{label} produced retrieval errors")
        if any(route["evidence_validity"]["ratio"] != 1.0 for route in routes):
            raise EvaluationError(f"{label} produced invalid evidence")
        signature = _ranking_signature(routes[0])
        if any(_ranking_signature(route) != signature for route in routes[1:]):
            raise EvaluationError(f"{label} rankings changed across replicates")

    baseline_aggregate = _aggregate(baseline_routes)
    candidate_aggregate = _aggregate(candidate_routes)
    metric_names = ("recall_at_10", "mrr_at_10", "ndcg_at_10")
    comparison = {
        name: {
            "baseline": baseline_aggregate["metrics"][name],
            "candidate": candidate_aggregate["metrics"][name],
            "delta": (
                candidate_aggregate["metrics"][name]
                - baseline_aggregate["metrics"][name]
            ),
        }
        for name in metric_names
    }
    perfect_quality = all(
        row["candidate"] == 1.0 for row in comparison.values()
    )
    non_regression = all(
        row["candidate"] >= row["baseline"] for row in comparison.values()
    )
    strict_improvement = any(
        row["candidate"] > row["baseline"] for row in comparison.values()
    )
    evidence_gate = candidate_aggregate["evidence"]["ratio"] == 1.0
    latency_gate = (
        candidate_aggregate["timing_ms"]["maximum_p95"]
        <= args.p95_limit_ms
    )
    passed = (
        perfect_quality
        and non_regression
        and strict_improvement
        and evidence_gate
        and latency_gate
    )
    if not passed:
        raise EvaluationError(
            "Candidate did not satisfy perfect quality, exact evidence, strict "
            "baseline improvement, and the P95 ceiling"
        )

    treatments = [
        {
            "treatment": "retrospective-supervised-ngram",
            **candidate_aggregate,
        },
        {"treatment": "baseline-lexical", **baseline_aggregate},
    ]
    treatments.sort(
        key=lambda row: (
            -float(row["metrics"]["recall_at_10"]),
            -float(row["metrics"]["mrr_at_10"]),
            -float(row["metrics"]["ndcg_at_10"]),
            float(row["timing_ms"]["representative_p95"]),
        )
    )
    for rank, treatment in enumerate(treatments, start=1):
        treatment["rank"] = rank

    if baseline_before != _tree_inventory(baseline):
        raise EvaluationError("Evaluation modified the baseline expert")
    if candidate_before != _tree_inventory(candidate):
        raise EvaluationError("Evaluation modified the candidate expert")

    candidate_profile_path = (
        candidate / "scripts" / "expert_routing_index.json"
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "pass",
        "dataset_id": DATASET_ID,
        "candidate_id": candidate.name,
        "candidate_state": candidate_verification["candidate_state"],
        "promotion_eligible": False,
        "retrospective_warning": (
            "All 40 questions and their reviewed qrels were exposed to profile "
            "construction. The result measures fixed-workload specialization "
            "and cannot support promotion or unseen-query generalization."
        ),
        "evaluation_contract": {
            "question_count": 40,
            "top_k": args.top_k,
            "replicates": args.replicates,
            "primary_identity": "exact versioned arXiv paper ID",
            "relevance": "binary reviewed qrels",
            "duplicate_policy": "keep first rank per paper identity",
            "quality_targets": {
                "recall_at_10": 1.0,
                "mrr_at_10": 1.0,
                "ndcg_at_10": 1.0,
                "exact_evidence_ratio": 1.0,
                "maximum_replicate_p95_ms": args.p95_limit_ms,
            },
            "timing_scope": (
                "Each timed query performs full manifest and embedded-tree "
                "verification, then one in-process authoritative-ledger search."
            ),
        },
        "gate": {
            "status": "pass",
            "perfect_quality": perfect_quality,
            "baseline_non_regression": non_regression,
            "strict_quality_improvement": strict_improvement,
            "exact_evidence": evidence_gate,
            "latency_ceiling": latency_gate,
            "comparison": comparison,
        },
        "leaderboard": treatments,
        "baseline": {
            "aggregate": baseline_aggregate,
            "replicates": baseline_routes,
            "verification": baseline_verification,
            "cohorts": _cohort_metrics(baseline_routes[0], cohorts),
        },
        "candidate": {
            "aggregate": candidate_aggregate,
            "replicates": candidate_routes,
            "verification": candidate_verification,
            "cohorts": _cohort_metrics(candidate_routes[0], cohorts),
        },
        "inputs": {
            "questions": _fingerprint(questions_path),
            "baseline_manifest": _fingerprint(
                baseline / "expert-manifest.json"
            ),
            "candidate_manifest": _fingerprint(
                candidate / "expert-manifest.json"
            ),
            "candidate_profile": _fingerprint(candidate_profile_path),
            "evaluator": _fingerprint(SCRIPT_PATH),
        },
        "artifacts": {
            "baseline": {
                "path": _portable_path(baseline),
                "file_count": len(baseline_before),
                "unchanged_after_evaluation": True,
                "knowledge_binding": baseline_manifest["knowledge"],
            },
            "candidate": {
                "path": _portable_path(candidate),
                "file_count": len(candidate_before),
                "unchanged_after_evaluation": True,
                "knowledge_binding": candidate_manifest["knowledge"],
            },
        },
    }


def _percent(value: float) -> str:
    return f"{100.0 * value:.4f}%"


def render_markdown(report: Mapping[str, Any]) -> str:
    """Render the concise human audit beside the complete JSON evidence."""

    rows = []
    for treatment in sorted(
        report["leaderboard"],
        key=lambda item: int(item["rank"]),
    ):
        rows.append(
            "| {rank} | {name} | {recall} | {mrr} | {ndcg} | {evidence} | "
            "{p95:.3f} |".format(
                rank=treatment["rank"],
                name=treatment["treatment"],
                recall=_percent(treatment["metrics"]["recall_at_10"]),
                mrr=_percent(treatment["metrics"]["mrr_at_10"]),
                ndcg=_percent(treatment["metrics"]["ndcg_at_10"]),
                evidence=_percent(treatment["evidence"]["ratio"]),
                p95=treatment["timing_ms"]["representative_p95"],
            )
        )
    replicate_rows = []
    for number, route in enumerate(report["candidate"]["replicates"], start=1):
        replicate_rows.append(
            "| {number} | {recall} | {mrr} | {ndcg} | {evidence} | "
            "{p95:.3f} |".format(
                number=number,
                recall=_percent(route["paper_metrics"]["recall_at_10"]),
                mrr=_percent(route["paper_metrics"]["mrr_at_10"]),
                ndcg=_percent(route["paper_metrics"]["ndcg_at_10"]),
                evidence=_percent(route["evidence_validity"]["ratio"]),
                p95=route["timing_ms"]["p95"],
            )
        )
    return (
        "# Retrospective QEC expert evaluation\n\n"
        "Status: **PASS**. The integrated supervised-profile builder produced "
        "the top-ranked treatment on the frozen 40-question workload.\n\n"
        "## Primary results\n\n"
        "| Rank | Treatment | Recall@10 | MRR@10 | nDCG@10 | Exact evidence | "
        "Representative P95 (ms) |\n"
        "|---:|---|---:|---:|---:|---:|---:|\n"
        + "\n".join(rows)
        + "\n\n"
        "## Candidate replicates\n\n"
        "| Replicate | Recall@10 | MRR@10 | nDCG@10 | Exact evidence | "
        "P95 (ms) |\n"
        "|---:|---:|---:|---:|---:|---:|\n"
        + "\n".join(replicate_rows)
        + "\n\n"
        "## Interpretation\n\n"
        "Every retained result resolves to the exact immutable ledger record "
        "and concept path. Ranking was stable across all replicates, and every "
        "quality target reached 100% at Top-10.\n\n"
        "## Promotion boundary\n\n"
        + str(report["retrospective_warning"])
        + "\n"
    )


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line contract."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--questions", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-markdown", type=Path, required=True)
    parser.add_argument("--replicates", type=int, default=3)
    parser.add_argument("--top-k", type=int, default=10)
    parser.add_argument("--p95-limit-ms", type=float, default=250.0)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Evaluate, enforce the gate, and write both audit formats."""

    args = build_parser().parse_args(argv)
    try:
        report = evaluate(args)
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_markdown.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(
            json.dumps(
                report,
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
                allow_nan=False,
            )
            + "\n",
            encoding="utf-8",
            newline="\n",
        )
        args.output_markdown.write_text(
            render_markdown(report),
            encoding="utf-8",
            newline="\n",
        )
    except (EvaluationError, OSError, UnicodeError) as exc:
        raise SystemExit(f"QEC expert evaluation failed: {exc}") from exc
    print(
        json.dumps(
            {
                "status": report["status"],
                "candidate_id": report["candidate_id"],
                "rank": next(
                    row["rank"]
                    for row in report["leaderboard"]
                    if row["treatment"] == "retrospective-supervised-ngram"
                ),
                "recall_at_10": report["candidate"]["aggregate"]["metrics"][
                    "recall_at_10"
                ],
                "mrr_at_10": report["candidate"]["aggregate"]["metrics"][
                    "mrr_at_10"
                ],
                "ndcg_at_10": report["candidate"]["aggregate"]["metrics"][
                    "ndcg_at_10"
                ],
                "exact_evidence_ratio": report["candidate"]["aggregate"][
                    "evidence"
                ]["ratio"],
                "representative_p95_ms": report["candidate"]["aggregate"][
                    "timing_ms"
                ]["representative_p95"],
                "promotion_eligible": False,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
