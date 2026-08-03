#!/usr/bin/env python3
"""Validate the accepted knowledge-methodology offline ablation."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
ROOT = SCRIPT_PATH.parents[1]
REPO = SCRIPT_PATH.parents[3]
CONFIG_PATH = ROOT / "experiment.json"
REPORT_PATH = ROOT / "reports" / "offline-ablation-01.json"
MARKDOWN_PATH = ROOT / "reports" / "offline-ablation-01.md"
INVALID_ATTEMPT_PATH = ROOT / "reports" / "attempt-00-invalid.md"
DECISIONS_PATH = ROOT / "reports" / "offline-ablation-01-decisions.json"
DECISION_TABLE_PATH = (
    ROOT / "reports" / "offline-ablation-01-decision-table.md"
)


class ValidationError(ValueError):
    """Raised when an accepted experiment artifact is inconsistent."""


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValidationError(f"Expected a JSON object: {path}")
    return value


def _resolve_repo_path(value: str) -> Path:
    path = (REPO / value).resolve()
    try:
        path.relative_to(REPO.resolve())
    except ValueError as exc:
        raise ValidationError(f"Path escapes the repository: {value}") from exc
    return path


def _paper_tree_fingerprint(root: Path) -> dict[str, Any]:
    paths = sorted(root.glob("*.md"))
    rows = [
        {
            "path": path.resolve().relative_to(REPO.resolve()).as_posix(),
            "sha256": _sha256(path),
            "bytes": path.stat().st_size,
        }
        for path in paths
    ]
    payload = json.dumps(
        rows,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return {
        "file_count": len(rows),
        "sha256": hashlib.sha256(payload).hexdigest(),
    }


def _validate_dataset_inputs(
    config: dict[str, Any],
    datasets: dict[str, Any],
) -> None:
    configured = config.get("datasets")
    if not isinstance(configured, list):
        raise ValidationError("Configured datasets are invalid")
    by_id = {
        row.get("id"): row
        for row in configured
        if isinstance(row, dict) and isinstance(row.get("id"), str)
    }
    if len(by_id) != len(configured) or set(by_id) != set(datasets):
        raise ValidationError("Configured and reported datasets differ")

    for dataset_id, dataset in datasets.items():
        expected = by_id[dataset_id]
        inputs = dataset.get("inputs")
        if not isinstance(inputs, dict):
            raise ValidationError(f"Dataset inputs are missing: {dataset_id}")
        questions = inputs.get("questions")
        papers = inputs.get("papers")
        if not isinstance(questions, dict) or not isinstance(papers, dict):
            raise ValidationError(f"Dataset input bindings are invalid: {dataset_id}")

        question_path = _resolve_repo_path(str(expected["questions"]))
        paper_root = _resolve_repo_path(str(expected["papers"]))
        question_lines = [
            line
            for line in question_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        question_binding = {
            "path": question_path.relative_to(REPO).as_posix(),
            "sha256": _sha256(question_path),
            "count": len(question_lines),
        }
        paper_binding = {
            "path": paper_root.relative_to(REPO).as_posix(),
            **_paper_tree_fingerprint(paper_root),
            "count": len(list(paper_root.glob("*.md"))),
        }
        if (
            question_binding != questions
            or paper_binding != papers
            or question_binding["sha256"] != expected["questions_sha256"]
            or question_binding["count"] != expected["question_count"]
            or paper_binding["count"] != expected["paper_count"]
        ):
            raise ValidationError(f"Dataset input binding drift: {dataset_id}")


def validate() -> dict[str, Any]:
    """Validate result bindings, registered rules, and retrospective labels."""

    config = _load_object(CONFIG_PATH)
    report = _load_object(REPORT_PATH)
    if (
        config.get("schema_version")
        != "knowledge-methodology-proposal-experiment/1.0"
        or config.get("candidate_state")
        != "retrospective-all-qrels-exposed"
        or config.get("promotion_eligible") is not False
        or len(config.get("chunking_treatments", [])) != 7
        or len(config.get("retrieval_treatments", [])) != 3
    ):
        raise ValidationError("Experiment configuration is invalid")
    if (
        report.get("schema_version")
        != "knowledge-methodology-offline-ablation/1.0"
        or report.get("status") != "pass"
        or report.get("candidate_state") != config["candidate_state"]
        or report.get("promotion_eligible") is not False
        or report.get("experiment_id") != config["experiment_id"]
    ):
        raise ValidationError("Accepted report envelope is invalid")
    deterministic = report.get("deterministic")
    analysis = report.get("analysis")
    runtime = report.get("runtime", {}).get("datasets")
    if (
        not isinstance(deterministic, dict)
        or not isinstance(analysis, dict)
        or not isinstance(runtime, dict)
        or deterministic.get("config", {}).get("sha256")
        != _sha256(CONFIG_PATH)
    ):
        raise ValidationError("Accepted report bindings are invalid")

    datasets = deterministic.get("datasets")
    if not isinstance(datasets, dict) or set(datasets) != {
        "graphrag-papers-40",
        "quantum-error-correction-papers-40",
    }:
        raise ValidationError("Accepted dataset coverage is invalid")
    _validate_dataset_inputs(config, datasets)
    for dataset_id, dataset in datasets.items():
        treatments = dataset.get("treatments")
        if not isinstance(treatments, dict) or len(treatments) != 21:
            raise ValidationError(
                f"Treatment coverage is invalid: {dataset_id}"
            )
        if set(runtime.get(dataset_id, {})) != set(treatments):
            raise ValidationError(f"Runtime coverage is invalid: {dataset_id}")
        for treatment_id, treatment in treatments.items():
            query_metrics = treatment.get("query_metrics")
            aggregate = treatment.get("aggregate")
            if (
                not isinstance(query_metrics, list)
                or len(query_metrics) != 40
                or not isinstance(aggregate, dict)
                or set(aggregate)
                != {"recall_at_10", "mrr_at_10", "ndcg_at_10"}
                or len(treatment.get("rankings_sha256", "")) != 64
            ):
                raise ValidationError(
                    f"Treatment result is invalid: {dataset_id}/{treatment_id}"
                )
            timing = runtime[dataset_id][treatment_id]
            expected_accounting = (
                "bm25-plus-tfidf-plus-fusion"
                if treatment_id.endswith("::rrf-hybrid")
                else "retriever-score-and-document-aggregation"
            )
            if (
                timing.get("index_units", 0) < 15
                or timing.get("median_query_ms", 0.0) <= 0.0
                or timing.get("p95_query_ms", 0.0) <= 0.0
                or timing.get("accounting") != expected_accounting
            ):
                raise ValidationError(
                    f"Treatment runtime is invalid: {dataset_id}/{treatment_id}"
                )

    findings = analysis.get("proposal_findings")
    comparisons = analysis.get("chunking_comparisons")
    frontier = analysis.get("cross_domain_pareto_frontier")
    if (
        not isinstance(findings, dict)
        or not isinstance(comparisons, list)
        or len(comparisons) != 6
        or not isinstance(frontier, list)
        or not frontier
    ):
        raise ValidationError("Experiment analysis is incomplete")
    directional = any(row["material"] for row in comparisons)
    strong = any(
        row["material"] and row["interval_excludes_zero"]
        for row in comparisons
    )
    if (
        findings["KM-004"]["registered_rule_satisfied"] != directional
        or findings["KM-004"]["strong_rule_satisfied"] != strong
    ):
        raise ValidationError("KM-004 finding violates its registered rule")
    km005_expected = (
        findings["KM-005"]["domain_winners_differ"] or len(frontier) > 1
    )
    if (
        findings["KM-005"]["registered_rule_satisfied"] != km005_expected
        or findings["KM-005"]["pareto_frontier_size"] != len(frontier)
    ):
        raise ValidationError("KM-005 finding violates its registered rule")
    maximum_width = max(
        metric["aggregate"]["recall_at_10"]["interval"]["high"]
        - metric["aggregate"]["recall_at_10"]["interval"]["low"]
        for dataset in datasets.values()
        for metric in dataset["treatments"].values()
    )
    if (
        findings["KM-006"]["registered_rule_satisfied"]
        != (maximum_width >= 0.05)
        or abs(
            findings["KM-006"]["maximum_recall_interval_width"]
            - maximum_width
        )
        > 1e-12
    ):
        raise ValidationError("KM-006 finding violates its registered rule")

    markdown = MARKDOWN_PATH.read_text(encoding="utf-8")
    for proposal_id in ("KM-004", "KM-005", "KM-006"):
        if (
            proposal_id not in markdown
            or findings[proposal_id]["finding"] not in markdown
        ):
            raise ValidationError(
                f"Markdown omits accepted finding: {proposal_id}"
            )
    invalid_attempt = INVALID_ATTEMPT_PATH.read_text(encoding="utf-8")
    if (
        "Invalid and superseded" not in invalid_attempt
        or "omitted" not in invalid_attempt
    ):
        raise ValidationError("Invalid attempt receipt is incomplete")
    decisions = _load_object(DECISIONS_PATH)
    decision_rows = decisions.get("decisions")
    if (
        decisions.get("schema_version")
        != "knowledge-methodology-offline-decisions/1.0"
        or decisions.get("experiment_id") != config["experiment_id"]
        or decisions.get("candidate_state") != config["candidate_state"]
        or decisions.get("promotion_eligible") is not False
        or decisions.get("source_report", {}).get("sha256")
        != _sha256(REPORT_PATH)
        or not isinstance(decision_rows, list)
        or [row.get("id") for row in decision_rows]
        != [f"D{index:03d}" for index in range(1, 11)]
    ):
        raise ValidationError("Quantitative decision envelope is invalid")
    by_id = {row["id"]: row for row in decision_rows}

    def metric_delta(
        dataset_id: str,
        candidate: str,
        baseline: str,
        metric: str,
    ) -> float:
        treatments = datasets[dataset_id]["treatments"]
        return (
            treatments[candidate]["aggregate"][metric]["value"]
            - treatments[baseline]["aggregate"][metric]["value"]
        )

    checks = [
        (
            by_id["D001"]["graphrag"]["recall_delta"],
            metric_delta(
                "graphrag-papers-40",
                "fixed-128::tfidf-char3",
                "document::tfidf-char3",
                "recall_at_10",
            ),
        ),
        (
            by_id["D001"]["qec"]["recall_delta"],
            metric_delta(
                "quantum-error-correction-papers-40",
                "fixed-128::tfidf-char3",
                "document::tfidf-char3",
                "recall_at_10",
            ),
        ),
        (
            by_id["D002"]["qec"]["mrr_delta"],
            metric_delta(
                "quantum-error-correction-papers-40",
                "fixed-512::rrf-hybrid",
                "document::rrf-hybrid",
                "mrr_at_10",
            ),
        ),
        (
            by_id["D004"]["graphrag"]["recall_delta"],
            metric_delta(
                "graphrag-papers-40",
                "fixed-128::bm25-word",
                "document::bm25-word",
                "recall_at_10",
            ),
        ),
        (
            by_id["D006"]["qec_vs_fixed256_hybrid"]["ndcg_delta"],
            metric_delta(
                "quantum-error-correction-papers-40",
                "overlap-256-32::rrf-hybrid",
                "fixed-256::rrf-hybrid",
                "ndcg_at_10",
            ),
        ),
        (
            by_id["D009"]["qec_vs_fixed512_char3"]["mrr_delta"],
            metric_delta(
                "quantum-error-correction-papers-40",
                "fixed-128::tfidf-char3",
                "fixed-512::tfidf-char3",
                "mrr_at_10",
            ),
        ),
        (
            by_id["D010"]["qec_vs_fixed128_char3"]["recall_delta"],
            metric_delta(
                "quantum-error-correction-papers-40",
                "fixed-512::rrf-hybrid",
                "fixed-128::tfidf-char3",
                "recall_at_10",
            ),
        ),
    ]
    if any(abs(actual - expected) > 1e-12 for actual, expected in checks):
        raise ValidationError("Quantitative decision values have drifted")
    if (
        by_id["D007"]["graphrag_winner"]
        != analysis["best_by_dataset"]["graphrag-papers-40"]
        or by_id["D007"]["qec_winner"]
        != analysis["best_by_dataset"][
            "quantum-error-correction-papers-40"
        ]
        or by_id["D007"]["cross_domain_pareto_frontier_size"]
        != len(frontier)
        or abs(
            by_id["D008"]["maximum_recall_interval_width"]
            - maximum_width
        )
        > 1e-12
    ):
        raise ValidationError("Decision summary is inconsistent")
    decision_table = DECISION_TABLE_PATH.read_text(encoding="utf-8")
    for marker in (
        "Chunked char-TF-IDF",
        "Fixed-512 hybrid",
        "Fixed-512 BM25",
        "Fixed-128 BM25 as a global default",
        "Hierarchical page scoring",
        "256-token overlap",
        "QEC fixed-128 char-TF-IDF secondary-quality winner",
        "QEC fixed-512 hybrid cost-balanced option",
        "One global winner",
        "Uncertainty-free point ranking",
    ):
        if marker not in decision_table:
            raise ValidationError(
                f"Decision table omits quantitative row: {marker}"
            )
    return {
        "status": "pass",
        "experiment_id": config["experiment_id"],
        "dataset_count": len(datasets),
        "treatment_count": sum(
            len(dataset["treatments"]) for dataset in datasets.values()
        ),
        "question_result_count": sum(
            len(treatment["query_metrics"])
            for dataset in datasets.values()
            for treatment in dataset["treatments"].values()
        ),
        "findings": {
            key: value["finding"] for key, value in findings.items()
        },
        "decision_count": len(decision_rows),
    }


def main() -> int:
    """Validate the accepted experiment and emit a stable report."""

    try:
        result = validate()
    except (
        ValidationError,
        KeyError,
        OSError,
        UnicodeError,
        json.JSONDecodeError,
        TypeError,
    ) as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, sort_keys=True))
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
