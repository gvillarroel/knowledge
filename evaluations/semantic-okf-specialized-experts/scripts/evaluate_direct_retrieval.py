#!/usr/bin/env python3
"""Evaluate one generated expert skill on the frozen GraphRAG retrieval contract."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import statistics
import sys
from pathlib import Path
from types import ModuleType
from typing import Any, Mapping, Sequence


sys.dont_write_bytecode = True

SCHEMA_VERSION = "semantic-okf-specialized-expert-retrieval/1.0"
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
DEFAULT_QUESTIONS = (
    REPO_ROOT
    / "evaluations"
    / "semantic-okf-adaptive"
    / "retrieval-questions.jsonl"
)


class EvaluationError(RuntimeError):
    """Describe an invalid expert artifact or incomplete retrieval run."""


def _load_module(name: str, path: Path) -> ModuleType:
    specification = importlib.util.spec_from_file_location(name, path)
    if specification is None or specification.loader is None:
        raise EvaluationError(f"Cannot load Python module from {path}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


BASE = _load_module("semantic_okf_specialized_expert_evidence", BASE_PATH)


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


def _tree_inventory(
    root: Path,
    *,
    ignore_transient_python_cache: bool = False,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted(
        root.rglob("*"),
        key=lambda item: item.relative_to(root).as_posix(),
    ):
        relative = path.relative_to(root)
        if path.is_symlink():
            raise EvaluationError(f"Artifact contains a symlink: {path}")
        if ignore_transient_python_cache and (
            "__pycache__" in relative.parts
            or path.suffix.casefold() in {".pyc", ".pyo"}
        ):
            continue
        if path.is_file():
            rows.append(
                {
                    "path": relative.as_posix(),
                    "bytes": path.stat().st_size,
                    "sha256": _sha256_file(path),
                }
            )
    return rows


def _canonical_digest(value: Any) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _load_json(path: Path, *, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise EvaluationError(f"Cannot read {label} at {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise EvaluationError(f"{label} must be a JSON object: {path}")
    return value


def _mean_metrics(rows: Sequence[dict[str, Any]], key: str) -> dict[str, float]:
    names = [
        *(f"recall_at_{cutoff}" for cutoff in BASE.METRIC_CUTOFFS),
        "mrr_at_10",
        "ndcg_at_10",
    ]
    return {
        name: statistics.fmean(float(row[key][name]) for row in rows)
        for name in names
    }


def _cohort_summary(rows: Sequence[dict[str, Any]]) -> dict[str, Any]:
    returned = sum(int(row["evidence_validity"]["returned"]) for row in rows)
    valid = sum(int(row["evidence_validity"]["valid"]) for row in rows)
    return {
        "query_count": len(rows),
        "error_count": sum(row["error"] is not None for row in rows),
        "paper_metrics": _mean_metrics(rows, "paper_metrics"),
        "source_metrics": _mean_metrics(rows, "source_metrics"),
        "evidence_validity": {
            "returned": returned,
            "valid": valid,
            "invalid": returned - valid,
            "ratio": valid / returned if returned else None,
        },
    }


def _attach_cohorts(route: dict[str, Any]) -> None:
    rows = route["queries"]
    original = [row for row in rows if int(row["question_id"][1:4]) <= 30]
    hard = [row for row in rows if int(row["question_id"][1:4]) >= 31]
    if len(original) != 30 or len(hard) != 10:
        raise EvaluationError("The route does not contain the frozen 30/10 cohorts")
    route["cohorts"] = {
        "original_30": _cohort_summary(original),
        "hard_10": _cohort_summary(hard),
    }


def _load_expert_runtime(expert: Path) -> ModuleType:
    script = expert / "scripts" / "query_expert_knowledge.py"
    if not script.is_file():
        raise EvaluationError(f"Expert query helper is absent: {script}")
    module_name = (
        "semantic_okf_generated_expert_"
        + hashlib.sha256(str(expert).encode("utf-8")).hexdigest()[:12]
    )
    return _load_module(module_name, script)


def _search(
    runtime: ModuleType,
    query: str,
    top_k: int,
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
        limit=max(top_k, record_count),
        show_content=True,
    )
    normalized = [
        {**row, "chunk_id": row.get("record_id")}
        for row in rows
    ]
    parsed = BASE.parse_search_output(
        {"results": normalized},
        len(normalized),
    )
    distinct: list[Any] = []
    seen: set[Any] = set()
    for hit in parsed:
        identity: Any = hit.paper_id
        if identity is None:
            identity = (
                hit.source_id,
                hit.record_id,
                hit.chunk_id,
            )
        if identity in seen:
            continue
        seen.add(identity)
        distinct.append(hit)
        if len(distinct) == top_k:
            break
    return distinct


def _retrieval_contract(runtime: ModuleType) -> dict[str, Any]:
    describe = getattr(runtime, "retrieval_contract", None)
    if not callable(describe):
        return {
            "id": "stable-raw-occurrence-v1",
            "route_name": "specialized_expert_lexical",
            "query_adapter": (
                "Unicode word-and-hyphen tokens with stable raw occurrence counts "
                "over authoritative title, body, source, record, and type fields, "
                "followed by first-hit authoritative-paper deduplication"
            ),
            "parameters": {},
        }
    contract = describe()
    if not isinstance(contract, dict):
        raise EvaluationError("Expert retrieval contract must be a JSON object")
    for key in ("id", "route_name", "query_adapter"):
        if not isinstance(contract.get(key), str) or not contract[key].strip():
            raise EvaluationError(f"Expert retrieval contract lacks {key}")
    parameters = contract.get("parameters", {})
    if not isinstance(parameters, dict):
        raise EvaluationError("Expert retrieval parameters must be a JSON object")
    return {**contract, "parameters": parameters}


def _select_questions(
    questions: Sequence[Any],
    requested_ids: Sequence[str],
) -> list[Any]:
    if not requested_ids:
        return list(questions)
    if len(set(requested_ids)) != len(requested_ids):
        raise EvaluationError("--question-id values must be unique")
    by_id: dict[str, Any] = {}
    for question in questions:
        identifier = str(question.identifier)
        short = identifier.split("-", 1)[0]
        for key in (identifier, short):
            if key in by_id and by_id[key] is not question:
                raise EvaluationError(f"Ambiguous question identifier: {key}")
            by_id[key] = question
    missing = [identifier for identifier in requested_ids if identifier not in by_id]
    if missing:
        raise EvaluationError(
            "Unknown --question-id values: " + ", ".join(sorted(missing))
        )
    return [by_id[identifier] for identifier in requested_ids]


def evaluate(args: argparse.Namespace) -> dict[str, Any]:
    """Verify one expert, run all questions, and prove immutability."""

    if not 10 <= args.top_k <= 100:
        raise EvaluationError("--top-k must be from 10 through 100")
    expert = args.expert.resolve()
    questions_path = args.questions.resolve()
    builder_skill = args.builder_skill.resolve()
    packager_skill = (
        args.packager_skill.resolve()
        if args.packager_skill is not None
        else None
    )
    required_paths = [
        (expert, "expert skill"),
        (questions_path, "questions"),
        (builder_skill, "builder skill"),
    ]
    if packager_skill is not None:
        required_paths.append((packager_skill, "packager skill"))
    for path, label in required_paths:
        if not path.exists():
            raise EvaluationError(f"{label} is missing: {path}")

    manifest_path = expert / "expert-manifest.json"
    manifest = _load_json(manifest_path, label="expert manifest")
    if manifest.get("schema_version") != "semantic-okf-expert-skill/1.0":
        raise EvaluationError("Unsupported expert manifest schema")
    if manifest.get("skill_name") != expert.name:
        raise EvaluationError("Expert manifest name does not match its directory")

    expert_before = _tree_inventory(expert)
    runtime = _load_expert_runtime(expert)
    verification = runtime.verify()
    if verification.get("status") != "pass":
        raise EvaluationError("Generated expert failed its binding verification")
    retrieval_contract = _retrieval_contract(runtime)

    if args.expected_question_count < 1:
        raise EvaluationError("--expected-question-count must be positive")
    all_questions = BASE.load_questions(questions_path)
    if len(all_questions) != args.expected_question_count:
        raise EvaluationError(
            "The frozen dataset requires "
            f"{args.expected_question_count} questions, found {len(all_questions)}"
        )
    questions = _select_questions(all_questions, args.question_id)
    canonical_scope = not args.question_id
    if not questions:
        raise EvaluationError("The selected evaluation scope is empty")
    scope_label = args.scope_label.strip()
    if not scope_label:
        raise EvaluationError("--scope-label must not be empty")

    knowledge = expert / "references" / "knowledge"
    ledger = BASE.AuthoritativeLedger.from_bundle(knowledge)
    knowledge_before = _tree_inventory(knowledge)
    builder_inventory = _tree_inventory(
        builder_skill,
        ignore_transient_python_cache=True,
    )
    packager_inventory = (
        _tree_inventory(
            packager_skill,
            ignore_transient_python_cache=True,
        )
        if packager_skill is not None
        else None
    )

    route = BASE.evaluate_route(
        retrieval_contract["route_name"],
        knowledge,
        ledger,
        questions,
        lambda query: _search(runtime, query, args.top_k),
        continue_on_error=False,
    )
    if canonical_scope:
        _attach_cohorts(route)
    if route["error_count"] != 0:
        raise EvaluationError("Expert lexical retrieval produced query errors")
    if route["evidence_validity"]["ratio"] != 1.0:
        raise EvaluationError("Expert lexical retrieval produced invalid evidence")

    expert_after = _tree_inventory(expert)
    knowledge_after = _tree_inventory(knowledge)
    if expert_before != expert_after or knowledge_before != knowledge_after:
        raise EvaluationError("Evaluation modified the immutable expert artifact")

    trace_inputs = [
        _file_fingerprint(path.resolve())
        for path in args.trace_evidence
    ]
    knowledge_binding = manifest.get("knowledge")
    if not isinstance(knowledge_binding, dict):
        raise EvaluationError("Expert manifest lacks its knowledge binding")
    selected_metrics: dict[str, Any] = {
        "scope": route["paper_metrics"],
        "evidence_validity": route["evidence_validity"],
        "timing_ms": route["timing_ms"],
    }
    if canonical_scope:
        selected_metrics.update(
            {
                "all_40": route["paper_metrics"],
                "hard_10": route["cohorts"]["hard_10"]["paper_metrics"],
            }
        )
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "pass",
        "dataset_id": "graphrag-papers-40",
        "candidate_id": expert.name,
        "candidate_state": "experimental-specialized-expert",
        "ranking_eligible": canonical_scope,
        "evaluation_scope": {
            "label": "canonical-all-40" if canonical_scope else scope_label,
            "canonical": canonical_scope,
            "question_ids": [
                str(question.identifier)
                for question in questions
            ],
        },
        "selected_route": route["name"],
        "query_count": len(questions),
        "top_k": args.top_k,
        "metric_contract": {
            "primary_identity": "paper_id",
            "duplicate_policy": "keep first rank per paper",
            "recall_cutoffs": list(BASE.METRIC_CUTOFFS),
            "mrr_cutoff": 10,
            "ndcg_cutoff": 10,
            "relevance": "binary reviewed qrels",
            "cohorts": (
                "all 40, original 30, and hard 10"
                if canonical_scope
                else scope_label
            ),
            "retrieval_contract_id": retrieval_contract["id"],
            "query_adapter": retrieval_contract["query_adapter"],
            "query_parameters": retrieval_contract["parameters"],
        },
        "timing_contract": {
            "unit": "milliseconds",
            "query_scope": (
                "one in-process expert manifest/tree verification followed by one "
                "authoritative-ledger lexical search"
            ),
            "setup_excluded_from_query_latency": True,
            "cross_family_warning": (
                "P95 is an operational diagnostic because setup and runtime "
                "boundaries differ across routes."
            ),
        },
        "inputs": {
            "questions": _file_fingerprint(questions_path),
            "question_filter": list(args.question_id),
            "expert_manifest": _file_fingerprint(manifest_path),
            "query_helper": _file_fingerprint(
                expert / "scripts" / "query_expert_knowledge.py"
            ),
            "guidance": _file_fingerprint(
                expert / "references" / "guidance.md"
            ),
            "builder_skill": {
                "path": _portable_path(builder_skill),
                "tree_sha256": _canonical_digest(builder_inventory),
                "file_count": len(builder_inventory),
            },
            "packager_skill": (
                {
                    "path": _portable_path(packager_skill),
                    "tree_sha256": _canonical_digest(packager_inventory),
                    "file_count": len(packager_inventory),
                }
                if (
                    packager_skill is not None
                    and packager_inventory is not None
                )
                else None
            ),
            "trace_evidence": trace_inputs,
            "evaluator_script": _file_fingerprint(SCRIPT_PATH),
        },
        "expert": {
            "path": _portable_path(expert),
            "skill_name": manifest["skill_name"],
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
        "selected_metrics": selected_metrics,
        "routes": [route],
    }


def _percent(value: Any) -> str:
    return f"{100.0 * float(value):.2f}%"


def render_markdown(report: Mapping[str, Any]) -> str:
    """Render one complete expert direct-retrieval result."""

    metrics = report["selected_metrics"]
    scope = metrics["scope"]
    timing = metrics["timing_ms"]
    evidence = metrics["evidence_validity"]
    if report["evaluation_scope"]["canonical"]:
        all_40 = metrics["all_40"]
        hard_10 = metrics["hard_10"]
        metric_header = (
            "| Route | Recall@10 | Hard Recall@10 | MRR@10 | nDCG@10 | "
            "Evidence valid | P95 |"
        )
        metric_row = (
            f"| `{report['selected_route']}` | "
            f"{_percent(all_40['recall_at_10'])} | "
            f"{_percent(hard_10['recall_at_10'])} | "
            f"{_percent(all_40['mrr_at_10'])} | "
            f"{_percent(all_40['ndcg_at_10'])} | "
            f"{_percent(evidence['ratio'])} | "
            f"{timing['p95']:.2f} ms |"
        )
        separator = "|---|---:|---:|---:|---:|---:|---:|"
    else:
        metric_header = (
            "| Route | Recall@10 | MRR@10 | nDCG@10 | Evidence valid | P95 |"
        )
        metric_row = (
            f"| `{report['selected_route']}` | "
            f"{_percent(scope['recall_at_10'])} | "
            f"{_percent(scope['mrr_at_10'])} | "
            f"{_percent(scope['ndcg_at_10'])} | "
            f"{_percent(evidence['ratio'])} | "
            f"{timing['p95']:.2f} ms |"
        )
        separator = "|---|---:|---:|---:|---:|---:|"
    return "\n".join(
        [
            "# Specialized Expert Direct-Retrieval Run",
            "",
            f"Expert: `{report['candidate_id']}`. Dataset: "
            f"`{report['dataset_id']}`. Questions: {report['query_count']}. "
            f"Scope: `{report['evaluation_scope']['label']}`. "
            f"Returned pool: {report['top_k']}.",
            "",
            metric_header,
            separator,
            metric_row,
            "",
            "Every query reverified the complete expert binding before searching. "
            "The expert and its embedded knowledge remained byte-identical.",
            "",
        ]
    )


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line interface."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--expert", type=Path, required=True)
    parser.add_argument("--builder-skill", type=Path, required=True)
    parser.add_argument(
        "--packager-skill",
        type=Path,
        help="Optional specialized-skill packager provenance bound to this run",
    )
    parser.add_argument(
        "--trace-evidence",
        type=Path,
        action="append",
        default=[],
        help="Trace-distillation artifact bound to the expert guidance",
    )
    parser.add_argument("--questions", type=Path, default=DEFAULT_QUESTIONS)
    parser.add_argument(
        "--question-id",
        action="append",
        default=[],
        help="Evaluate only this exact or qNNN-prefixed question (repeatable)",
    )
    parser.add_argument(
        "--scope-label",
        default="selected-development-scope",
        help="Non-canonical cohort label used with --question-id",
    )
    parser.add_argument("--top-k", type=int, default=10)
    parser.add_argument(
        "--expected-question-count",
        type=int,
        default=40,
        help=(
            "Exact number of rows required in --questions; defaults to the "
            "canonical 40-question benchmark"
        ),
    )
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-markdown", type=Path, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run one append-only evaluation."""

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
                "candidate_id": report["candidate_id"],
                "top_k": report["top_k"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
