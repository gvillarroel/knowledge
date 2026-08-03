#!/usr/bin/env python3
"""Evaluate one definitive expert against its strongest recorded baseline."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import statistics
import sys
from types import ModuleType
from typing import Any, Mapping, Sequence


sys.dont_write_bytecode = True
SCHEMA_VERSION = "semantic-okf-definitive-expert-evaluation/1.0"
SUPPORTED_DATASETS = ("astro-40", "graphrag-papers-40")
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
DEFAULT_BASELINES = EVALUATION_ROOT / "definitive-baselines.json"


class EvaluationError(RuntimeError):
    """Describe an invalid expert, baseline, or incomplete evaluation."""


def _load_module(name: str, path: Path) -> ModuleType:
    specification = importlib.util.spec_from_file_location(name, path)
    if specification is None or specification.loader is None:
        raise EvaluationError(f"Cannot load Python module from {path}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


BASE = _load_module("semantic_okf_definitive_evidence", BASE_PATH)


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


def _file_fingerprint(path: Path) -> dict[str, Any]:
    return {
        "path": _portable_path(path),
        "bytes": path.stat().st_size,
        "sha256": _sha256_file(path),
    }


def _canonical_digest(value: Any) -> str:
    rendered = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(rendered).hexdigest()


def _load_json_object(path: Path, *, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise EvaluationError(f"Cannot read {label} at {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise EvaluationError(f"{label} must be a JSON object: {path}")
    return value


def _tree_inventory(root: Path) -> list[dict[str, Any]]:
    rows = []
    for path in sorted(
        root.rglob("*"),
        key=lambda item: item.relative_to(root).as_posix(),
    ):
        if path.is_symlink():
            raise EvaluationError(f"Artifact contains a symlink: {path}")
        if path.is_file():
            rows.append(
                {
                    "path": path.relative_to(root).as_posix(),
                    "bytes": path.stat().st_size,
                    "sha256": _sha256_file(path),
                }
            )
    return rows


def _load_runtime(expert: Path) -> ModuleType:
    helper = expert / "scripts" / "query_expert_knowledge.py"
    if not helper.is_file():
        raise EvaluationError(f"Expert query helper is absent: {helper}")
    name = (
        "semantic_okf_definitive_runtime_"
        + hashlib.sha256(str(expert).encode("utf-8")).hexdigest()[:12]
    )
    return _load_module(name, helper)


def _load_questions(
    path: Path,
    dataset_id: str,
) -> tuple[list[Any], dict[str, str]]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        raise EvaluationError(f"Cannot read retrieval questions: {exc}") from exc
    questions = []
    question_types: dict[str, str] = {}
    seen: set[str] = set()
    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise EvaluationError(
                f"Invalid questions JSON on line {line_number}: {exc}"
            ) from exc
        if not isinstance(value, dict) or not isinstance(value.get("qrels"), dict):
            raise EvaluationError(f"Question line {line_number} is incomplete")
        identifier = value.get("id")
        text = value.get("question")
        source_ids = value["qrels"].get("source_ids")
        if (
            not isinstance(identifier, str)
            or not identifier
            or identifier in seen
            or not isinstance(text, str)
            or not text
            or not isinstance(source_ids, list)
            or not source_ids
            or not all(isinstance(item, str) for item in source_ids)
        ):
            raise EvaluationError(f"Question line {line_number} is invalid")
        seen.add(identifier)
        if source_ids != sorted(set(source_ids)):
            raise EvaluationError(f"Question {identifier} source qrels drift")
        if dataset_id == "graphrag-papers-40":
            primary_ids = value["qrels"].get("paper_ids")
            question_type = (
                "hard"
                if int(identifier[1:4]) >= 31
                else "original"
            )
        else:
            primary_ids = source_ids
            question_type = value.get("question_type")
        if (
            not isinstance(primary_ids, list)
            or not primary_ids
            or not all(isinstance(item, str) for item in primary_ids)
            or primary_ids != sorted(set(primary_ids))
        ):
            raise EvaluationError(f"Question {identifier} primary qrels drift")
        if not isinstance(question_type, str) or not question_type:
            raise EvaluationError(f"Question {identifier} lacks a cohort type")
        question_types[identifier] = question_type
        questions.append(
            BASE.RetrievalQuestion(
                identifier,
                text,
                tuple(primary_ids),
                tuple(source_ids),
            )
        )
    if len(questions) != 40:
        raise EvaluationError(
            f"The canonical dataset requires 40 questions, found {len(questions)}"
        )
    return questions, question_types


def _as_primary_source_hit(hit: Any) -> Any:
    if hit.source_id is None:
        raise EvaluationError("Astro expert hit lacks source_id")
    return BASE.RetrievalHit(
        source_id=hit.source_id,
        paper_id=hit.source_id,
        chunk_id=hit.chunk_id,
        ordinal=hit.ordinal,
        concept_path=hit.concept_path,
        concept_id=hit.concept_id,
        record_id=hit.record_id,
        record_sha256=hit.record_sha256,
        source_path=hit.source_path,
        locator=hit.locator,
        text=hit.text,
        text_sha256=hit.text_sha256,
        score=hit.score,
    )


def _search(
    runtime: ModuleType,
    query: str,
    top_k: int,
    dataset_id: str,
) -> list[Any]:
    verification = runtime.verify()
    if verification.get("status") != "pass":
        raise EvaluationError("Expert verification did not pass before search")
    record_count = verification.get("record_count")
    if (
        isinstance(record_count, bool)
        or not isinstance(record_count, int)
        or record_count < 1
    ):
        raise EvaluationError("Expert verification lacks a positive record count")
    rows = runtime.search(
        query,
        source_id=None,
        concept_type=None,
        limit=top_k,
        show_content=True,
    )
    normalized = [
        {**row, "chunk_id": row.get("record_id")}
        for row in rows
    ]
    parsed = BASE.parse_search_output({"results": normalized}, len(normalized))
    if dataset_id == "astro-40":
        parsed = [_as_primary_source_hit(hit) for hit in parsed]

    distinct = []
    seen: set[str] = set()
    for hit in parsed:
        identity = hit.paper_id
        if not isinstance(identity, str) or not identity:
            raise EvaluationError("Expert hit lacks its primary identity")
        if identity in seen:
            continue
        seen.add(identity)
        distinct.append(hit)
        if len(distinct) == top_k:
            break
    return distinct


def _mean_metrics(rows: Sequence[dict[str, Any]]) -> dict[str, float]:
    names = [
        *(f"recall_at_{cutoff}" for cutoff in BASE.METRIC_CUTOFFS),
        "mrr_at_10",
        "ndcg_at_10",
    ]
    return {
        name: statistics.fmean(
            float(row["paper_metrics"][name])
            for row in rows
        )
        for name in names
    }


def _cohorts(
    route: Mapping[str, Any],
    question_types: Mapping[str, str],
) -> dict[str, Any]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in route["queries"]:
        cohort = question_types[str(row["question_id"])]
        grouped.setdefault(cohort, []).append(row)
    result = {}
    for name, rows in sorted(grouped.items()):
        returned = sum(int(row["evidence_validity"]["returned"]) for row in rows)
        valid = sum(int(row["evidence_validity"]["valid"]) for row in rows)
        result[name] = {
            "query_count": len(rows),
            "metrics": _mean_metrics(rows),
            "evidence_validity": {
                "returned": returned,
                "valid": valid,
                "invalid": returned - valid,
                "ratio": valid / returned if returned else None,
            },
        }
    return result


def _load_baseline(
    baselines_path: Path,
    dataset_id: str,
) -> dict[str, Any]:
    collection = _load_json_object(baselines_path, label="baseline registry")
    baseline = collection.get(dataset_id)
    if not isinstance(baseline, dict):
        raise EvaluationError(f"Baseline registry lacks {dataset_id}")
    evidence = baseline.get("evidence_report")
    metrics = baseline.get("metrics")
    if not isinstance(evidence, dict) or not isinstance(metrics, dict):
        raise EvaluationError("Baseline lacks evidence or metrics")
    raw_path = evidence.get("path")
    expected_sha256 = evidence.get("sha256")
    if not isinstance(raw_path, str) or not isinstance(expected_sha256, str):
        raise EvaluationError("Baseline evidence binding is invalid")
    evidence_path = REPO_ROOT / raw_path
    if not evidence_path.is_file():
        raise EvaluationError(f"Baseline evidence report is absent: {raw_path}")
    if _sha256_file(evidence_path) != expected_sha256:
        raise EvaluationError(f"Baseline evidence report digest drift: {raw_path}")
    required_metrics = ("recall_at_10", "mrr_at_10", "ndcg_at_10")
    if any(not isinstance(metrics.get(key), (int, float)) for key in required_metrics):
        raise EvaluationError("Baseline quality metrics are incomplete")
    if not isinstance(baseline.get("p95_ms"), (int, float)):
        raise EvaluationError("Baseline P95 is incomplete")
    return {**baseline, "evidence_report": _file_fingerprint(evidence_path)}


def _improvement_gate(
    metrics: Mapping[str, Any],
    p95_ms: float,
    evidence_ratio: float,
    baseline: Mapping[str, Any],
) -> dict[str, Any]:
    quality_rows = {}
    for name in ("recall_at_10", "mrr_at_10", "ndcg_at_10"):
        candidate = float(metrics[name])
        incumbent = float(baseline["metrics"][name])
        quality_rows[name] = {
            "candidate": candidate,
            "baseline": incumbent,
            "delta": candidate - incumbent,
            "non_regression": candidate >= incumbent,
            "strict_improvement": candidate > incumbent,
        }
    baseline_p95 = float(baseline["p95_ms"])
    latency = {
        "candidate": p95_ms,
        "baseline": baseline_p95,
        "delta": p95_ms - baseline_p95,
        "ratio": p95_ms / baseline_p95,
        "strict_improvement": p95_ms < baseline_p95,
    }
    quality_non_regression = all(
        row["non_regression"]
        for row in quality_rows.values()
    )
    quality_strict = any(
        row["strict_improvement"]
        for row in quality_rows.values()
    )
    passed = (
        quality_non_regression
        and quality_strict
        and latency["strict_improvement"]
        and evidence_ratio == 1.0
    )
    return {
        "status": "pass" if passed else "fail",
        "contract": (
            "No Recall@10, MRR@10, or nDCG@10 regression; at least one strict "
            "quality improvement; strict P95 reduction; and 100% exact evidence"
        ),
        "quality": quality_rows,
        "latency_ms": latency,
        "evidence_ratio": evidence_ratio,
    }


def evaluate(args: argparse.Namespace) -> dict[str, Any]:
    """Run the canonical all-40 gate and prove expert immutability."""

    if args.top_k != 10:
        raise EvaluationError("The definitive comparison requires --top-k 10")
    dataset_id = args.dataset_id
    expert = args.expert.resolve()
    questions_path = args.questions.resolve()
    baselines_path = args.baselines.resolve()
    for path, label in (
        (expert, "expert"),
        (questions_path, "questions"),
        (baselines_path, "baseline registry"),
    ):
        if not path.exists():
            raise EvaluationError(f"{label} is absent: {path}")

    manifest_path = expert / "expert-manifest.json"
    manifest = _load_json_object(manifest_path, label="expert manifest")
    if manifest.get("schema_version") != "semantic-okf-expert-skill/1.0":
        raise EvaluationError("Unsupported expert manifest schema")
    if manifest.get("skill_name") != expert.name:
        raise EvaluationError("Expert manifest name does not match its directory")
    expert_before = _tree_inventory(expert)
    knowledge = expert / "references" / "knowledge"
    knowledge_before = _tree_inventory(knowledge)

    runtime = _load_runtime(expert)
    verification = runtime.verify()
    if verification.get("status") != "pass":
        raise EvaluationError("Expert verification failed")
    if verification.get("dataset_id") != dataset_id:
        raise EvaluationError("Expert and requested dataset differ")
    if verification.get("promotion_eligible") is not False:
        raise EvaluationError("Retrospective expert cannot be promotion eligible")
    contract = runtime.retrieval_contract()
    if not isinstance(contract, dict):
        raise EvaluationError("Expert retrieval contract is invalid")

    questions, question_types = _load_questions(questions_path, dataset_id)
    ledger = BASE.AuthoritativeLedger.from_bundle(knowledge)
    route = BASE.evaluate_route(
        str(contract["route_name"]),
        knowledge,
        ledger,
        questions,
        lambda query: _search(runtime, query, args.top_k, dataset_id),
        continue_on_error=False,
    )
    if route["error_count"] != 0:
        raise EvaluationError("Expert retrieval produced query errors")
    if route["evidence_validity"]["ratio"] != 1.0:
        raise EvaluationError("Expert retrieval produced invalid evidence")
    cohorts = _cohorts(route, question_types)

    expert_after = _tree_inventory(expert)
    knowledge_after = _tree_inventory(knowledge)
    if expert_before != expert_after or knowledge_before != knowledge_after:
        raise EvaluationError("Evaluation modified the immutable expert")

    baseline = _load_baseline(baselines_path, dataset_id)
    metrics = route["paper_metrics"]
    gate = _improvement_gate(
        metrics,
        float(route["timing_ms"]["p95"]),
        float(route["evidence_validity"]["ratio"]),
        baseline,
    )
    if gate["status"] != "pass":
        raise EvaluationError("Candidate did not beat the strongest baseline")
    knowledge_binding = manifest.get("knowledge")
    if not isinstance(knowledge_binding, dict):
        raise EvaluationError("Expert manifest lacks its knowledge binding")
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "pass",
        "dataset_id": dataset_id,
        "candidate_id": expert.name,
        "candidate_state": verification.get("candidate_state"),
        "promotion_eligible": False,
        "retrospective_warning": (
            "All canonical questions and qrels were exposed during profile "
            "construction. This result ranks the frozen benchmark but cannot "
            "support holdout promotion or unseen-query generalization."
        ),
        "query_count": len(questions),
        "top_k": args.top_k,
        "metric_contract": {
            "primary_identity": (
                "paper_id"
                if dataset_id == "graphrag-papers-40"
                else "source_id (one-to-one with canonical document_id)"
            ),
            "duplicate_policy": "keep first rank per primary identity",
            "recall_cutoffs": list(BASE.METRIC_CUTOFFS),
            "mrr_cutoff": 10,
            "ndcg_cutoff": 10,
            "relevance": "binary reviewed qrels",
            "retrieval_contract_id": contract.get("id"),
            "query_adapter": contract.get("query_adapter"),
            "query_parameters": contract.get("parameters"),
        },
        "timing_contract": {
            "unit": "milliseconds",
            "query_scope": (
                "one in-process full manifest and knowledge-tree verification "
                "followed by one profile-guided authoritative-ledger search"
            ),
            "setup_excluded_from_query_latency": True,
            "candidate_pool": (
                10
            ),
            "cross_family_warning": (
                "P95 is operational because historical setup boundaries differ; "
                "the candidate uses the stricter per-query full-verification scope."
            ),
        },
        "baseline": baseline,
        "selected_metrics": {
            "all_40": metrics,
            "cohorts": cohorts,
            "evidence_validity": route["evidence_validity"],
            "timing_ms": route["timing_ms"],
        },
        "improvement_gate": gate,
        "inputs": {
            "questions": _file_fingerprint(questions_path),
            "baseline_registry": _file_fingerprint(baselines_path),
            "expert_manifest": _file_fingerprint(manifest_path),
            "query_helper": _file_fingerprint(
                expert / "scripts" / "query_expert_knowledge.py"
            ),
            "routing_index": _file_fingerprint(
                expert / "scripts" / "expert_routing_index.json"
            ),
            "evaluator_script": _file_fingerprint(SCRIPT_PATH),
        },
        "expert": {
            "path": _portable_path(expert),
            "tree_sha256": _canonical_digest(expert_before),
            "file_count": len(expert_before),
            "knowledge_tree_sha256": knowledge_binding.get("tree", {}).get("sha256"),
            "knowledge_file_count": knowledge_binding.get("tree", {}).get("file_count"),
            "record_count": knowledge_binding.get("record_count"),
            "knowledge_inventory_sha256": _canonical_digest(knowledge_before),
            "knowledge_unchanged_after_evaluation": True,
            "expert_unchanged_after_evaluation": True,
            "verification": verification,
        },
        "route": route,
    }


def _percent(value: Any) -> str:
    return f"{100.0 * float(value):.2f}%"


def render_markdown(report: Mapping[str, Any]) -> str:
    """Render one compact definitive-expert evaluation."""

    metrics = report["selected_metrics"]["all_40"]
    timing = report["selected_metrics"]["timing_ms"]
    baseline = report["baseline"]
    baseline_metrics = baseline["metrics"]
    gate = report["improvement_gate"]
    return "\n".join(
        [
            "# Definitive Expert Evaluation",
            "",
            f"Dataset: `{report['dataset_id']}`. Candidate: "
            f"`{report['candidate_id']}`. State: `{report['candidate_state']}`.",
            "",
            "| Candidate | Recall@10 | MRR@10 | nDCG@10 | P95 | Exact evidence |",
            "|---|---:|---:|---:|---:|---:|",
            f"| `{report['candidate_id']}` | "
            f"{_percent(metrics['recall_at_10'])} | "
            f"{_percent(metrics['mrr_at_10'])} | "
            f"{_percent(metrics['ndcg_at_10'])} | "
            f"{timing['p95']:.2f} ms | "
            f"{_percent(report['selected_metrics']['evidence_validity']['ratio'])} |",
            f"| `{baseline['candidate_id']}` | "
            f"{_percent(baseline_metrics['recall_at_10'])} | "
            f"{_percent(baseline_metrics['mrr_at_10'])} | "
            f"{_percent(baseline_metrics['ndcg_at_10'])} | "
            f"{float(baseline['p95_ms']):.2f} ms | 100.00% |",
            "",
            f"Improvement gate: **{str(gate['status']).upper()}**. "
            f"P95 ratio: {float(gate['latency_ms']['ratio']):.4f}.",
            "",
            report["retrospective_warning"],
            "",
        ]
    )


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line interface."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-id", choices=SUPPORTED_DATASETS, required=True)
    parser.add_argument("--expert", type=Path, required=True)
    parser.add_argument("--questions", type=Path, required=True)
    parser.add_argument("--baselines", type=Path, default=DEFAULT_BASELINES)
    parser.add_argument("--top-k", type=int, default=10)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-markdown", type=Path, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run one append-only definitive-expert evaluation."""

    args = build_parser().parse_args(argv)
    if any(
        path.exists() or path.is_symlink()
        for path in (args.output_json, args.output_markdown)
    ):
        print(json.dumps({"status": "error", "error": "output already exists"}))
        return 2
    try:
        report = evaluate(args)
    except (
        EvaluationError,
        BASE.ComparisonError,
        OSError,
        UnicodeError,
        ValueError,
        TypeError,
        KeyError,
    ) as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, sort_keys=True))
        return 2
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
    print(
        json.dumps(
            {
                "status": report["status"],
                "dataset_id": report["dataset_id"],
                "candidate_id": report["candidate_id"],
                "improvement_gate": report["improvement_gate"]["status"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
