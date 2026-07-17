#!/usr/bin/env python3
"""Evaluate every compatible Semantic OKF consult route on the frozen PMCID battery."""

from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
import time
from pathlib import Path
from types import ModuleType
from typing import Any, Callable, Mapping, Sequence

from _retrieval_eval import (
    AuthoritativeLedger,
    EvaluationError,
    LegacyLexicalIndex,
    RetrievalHit,
    RetrievalQuestion,
    evaluate_hits,
    load_json,
    load_questions,
    parse_search_payload,
    pretty_json,
    route_summary,
    sha256_file,
)


SCRIPT = Path(__file__).resolve()
EVALUATION = SCRIPT.parents[1]
REPO = SCRIPT.parents[3]
CORPUS = EVALUATION / "corpus"
REPORTS = EVALUATION / "reports"
SCHEMA_VERSION = "semantic-okf-endocrine-hygiene-retrieval-report/1.0"
RAW_POOL = 100
FAMILY_ROUTES: dict[str, tuple[str, ...]] = {
    "legacy": ("legacy_lexical",),
    "embeddings": ("lexical", "vector", "hybrid"),
    "classical": ("bm25", "topic", "association", "fusion"),
    "entity-graph": ("lexical", "entity", "traversal", "fusion"),
    "adaptive": ("bm25", "topic", "association", "fusion", "adaptive"),
    "ensemble": ("quality", "fast", "robust"),
}


def _load_module(name: str, path: Path) -> ModuleType:
    specification = importlib.util.spec_from_file_location(name, path)
    if specification is None or specification.loader is None:
        raise EvaluationError(f"cannot import consultation runtime: {path}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    try:
        specification.loader.exec_module(module)
    except Exception as exc:
        raise EvaluationError(f"cannot initialize consultation runtime {path}: {exc}") from exc
    return module


def _run_json(command: Sequence[str], timeout: float) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            list(command),
            cwd=REPO,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="strict",
            check=False,
            timeout=timeout,
        )
    except (OSError, UnicodeError, subprocess.TimeoutExpired) as exc:
        raise EvaluationError(f"command could not run: {exc}") from exc
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip() or f"exit {completed.returncode}"
        raise EvaluationError(f"command failed: {detail}")
    try:
        value = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise EvaluationError(f"command emitted invalid JSON: {exc}") from exc
    if not isinstance(value, dict) or value.get("status") != "pass":
        raise EvaluationError(f"command did not return status=pass: {value}")
    return value


def _inspect_family(python: str, family: str, bundle: Path, timeout: float) -> dict[str, Any]:
    script = REPO / "skills" / f"consult-semantic-okf-{family}" / "scripts" / f"query_semantic_okf_{family.replace('-', '_')}.py"
    if family == "embeddings":
        command = [python, str(script), str(bundle), "inspect"]
    else:
        command = [python, str(script), str(bundle), "inspect", "--deep-validation"]
    return _run_json(command, timeout)


def _cached_embedding_provider(runtime: ModuleType, snapshot: Any) -> Callable[..., Any] | None:
    config = snapshot.index["embedding"]
    if config["provider"] != "sentence-transformers":
        return None
    try:
        model_module = __import__("sentence_transformers")
        model_class = getattr(model_module, "SentenceTransformer")
        model_path = runtime._resolve_sentence_transformer_snapshot(config)
        with runtime._offline_model_environment():
            model = model_class(str(model_path), device="cpu", local_files_only=True, trust_remote_code=False)
    except Exception as exc:
        raise EvaluationError(f"cannot initialize the pinned offline embedding model: {exc}") from exc

    def encode(text: str, active: Mapping[str, Any]) -> Any:
        kwargs = {
            "normalize_embeddings": bool(active["normalize"]),
            "show_progress_bar": False,
            "convert_to_numpy": True,
        }
        with runtime._offline_model_environment():
            if active["encoding"]["query"] == "query" and callable(getattr(model, "encode_query", None)):
                value = model.encode_query([text], **kwargs)
            else:
                value = model.encode([text], **kwargs)
        return runtime._sequence_from_model(value)

    return encode


def _searchers(
    family: str,
    bundle: Path,
    identity_by_source: Mapping[str, str],
    ledger: AuthoritativeLedger,
) -> dict[str, Callable[[str], list[RetrievalHit]]]:
    if family == "embeddings":
        runtime = _load_module(
            "endocrine_hygiene_embedding_consult_runtime",
            REPO / "skills/consult-semantic-okf-embeddings/scripts/_embedding_snapshot.py",
        )
        snapshot = runtime.load_snapshot(bundle)
        embedder = _cached_embedding_provider(runtime, snapshot)

        def search(mode: str, query: str) -> list[RetrievalHit]:
            payload = runtime.search_snapshot(
                snapshot,
                query,
                requested_mode=mode,
                top_k=RAW_POOL,
                allow_fallback=False,
                embedder=embedder,
            )
            if payload.get("effective_mode") != mode or payload.get("fallback") is not None:
                raise EvaluationError(f"embedding {mode} route changed mode or fell back")
            return [
                ledger.bind_missing_record_sha256(hit)
                for hit in parse_search_payload(payload, identity_by_source)
            ]

        return {mode: (lambda query, active=mode: search(active, query)) for mode in FAMILY_ROUTES[family]}
    if family in {"classical", "adaptive"}:
        module_name = family.replace("-", "_")
        runtime = _load_module(
            f"endocrine_hygiene_{module_name}_consult_runtime",
            REPO / f"skills/consult-semantic-okf-{family}/scripts/_{module_name}_snapshot.py",
        )
        snapshot = runtime.load_snapshot(bundle, deep_validation=True)

        def search(mode: str, query: str) -> list[RetrievalHit]:
            payload = runtime.search_snapshot(snapshot, query, mode, RAW_POOL)
            if payload.get("effective_mode") != mode:
                raise EvaluationError(f"{family} {mode} route changed effective mode")
            return [
                ledger.bind_missing_record_sha256(hit)
                for hit in parse_search_payload(payload, identity_by_source)
            ]

        return {mode: (lambda query, active=mode: search(active, query)) for mode in FAMILY_ROUTES[family]}
    raise EvaluationError(f"no runtime adapter for {family}")


def _evaluate_route(
    family: str,
    route: str,
    questions: Sequence[RetrievalQuestion],
    ledger: AuthoritativeLedger,
    search: Callable[[str], list[RetrievalHit]],
) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for question in questions:
        started = time.perf_counter()
        error: str | None = None
        try:
            hits = search(question.question)
        except Exception as exc:
            if isinstance(exc, (KeyboardInterrupt, SystemExit)):
                raise
            hits = []
            error = f"{type(exc).__name__}: {exc}"
        elapsed_ms = (time.perf_counter() - started) * 1000.0
        rows.append(evaluate_hits(question, hits, ledger, elapsed_ms, error))
    query_errors = sum(row["error"] is not None for row in rows)
    invalid_evidence = sum(row["evidence_validity"]["invalid"] for row in rows)
    if query_errors == len(rows):
        status = "error"
    elif query_errors or invalid_evidence:
        status = "partial"
    else:
        status = "pass"
    return {
        "family": family,
        "route": route,
        "status": status,
        "execution": "read-only consultation runtime loaded once after CLI inspection",
        "candidate_pool": RAW_POOL,
        "overall": route_summary(rows),
        "hard": route_summary(rows, "hard"),
        "queries": rows,
    }


def _failure_reason(family: str, build_report: Mapping[str, Any] | None, bundle: Path) -> str:
    if build_report is not None:
        families = build_report.get("families")
        if isinstance(families, dict):
            row = families.get(family)
            if isinstance(row, dict):
                contract = row.get("failure_contract")
                if isinstance(contract, dict):
                    diagnostics = contract.get("diagnostics")
                    if isinstance(diagnostics, list) and diagnostics and isinstance(diagnostics[0], str):
                        try:
                            payload = json.loads(diagnostics[0])
                        except json.JSONDecodeError:
                            payload = None
                        if isinstance(payload, dict) and isinstance(payload.get("error"), str):
                            return payload["error"]
                        return diagnostics[0]
                if row.get("observed") != "success":
                    return f"builder observed {row.get('observed')!r}"
        if isinstance(families, list):
            for row in families:
                if isinstance(row, dict) and row.get("family") == family:
                    value = row.get("failure_reason") or row.get("error")
                    if isinstance(value, str) and value:
                        return value
                    if row.get("status") not in {"pass", "success"}:
                        return f"builder status is {row.get('status')!r}"
    return f"compatible bundle was not published at {bundle.relative_to(bundle.parents[1]).as_posix()}"


def _na_route(family: str, route: str, reason: str) -> dict[str, Any]:
    return {
        "family": family,
        "route": route,
        "status": "not-applicable",
        "reason": reason,
        "execution": None,
        "candidate_pool": None,
        "overall": None,
        "hard": None,
        "queries": [],
    }


def _error_route(family: str, route: str, reason: str) -> dict[str, Any]:
    """Represent an executable route that failed before per-query evaluation."""

    row = _na_route(family, route, reason)
    row["status"] = "error"
    row["execution"] = "consult initialization attempted"
    return row


def _evaluation_status(routes: Sequence[Mapping[str, Any]]) -> str:
    """Fail the evaluation if any executable route is not a complete pass."""

    for row in routes:
        status = row.get("status")
        if status == "not-applicable":
            continue
        overall = row.get("overall")
        if status != "pass":
            return "error"
        if not isinstance(overall, Mapping):
            return "error"
        evidence_validity = overall.get("evidence_validity")
        if not isinstance(evidence_validity, Mapping):
            return "error"
        if overall.get("error_count") or evidence_validity.get("invalid"):
            return "error"
    return "pass"


def _best_by_family(routes: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for family in FAMILY_ROUTES:
        candidates = [row for row in routes if row["family"] == family and row["overall"] is not None]
        if not candidates:
            failures = [row.get("reason") for row in routes if row["family"] == family and row.get("reason")]
            rows.append({"family": family, "status": "not-applicable", "best_route": None, "reason": failures[0] if failures else "no compatible route"})
            continue
        winner = max(
            candidates,
            key=lambda row: (
                row["hard"]["paper_metrics"]["recall_at_10"],
                row["overall"]["paper_metrics"]["ndcg_at_10"],
                row["overall"]["paper_metrics"]["mrr_at_10"],
                row["route"],
            ),
        )
        rows.append(
            {
                "family": family,
                "status": winner["status"],
                "best_route": winner["route"],
                "overall": winner["overall"],
                "hard": winner["hard"],
                "reason": None,
            }
        )
    return rows


def _percentage(value: Any) -> str:
    return "N/A" if value is None else f"{100.0 * float(value):.1f}%"


def _number(value: Any, digits: int = 3) -> str:
    return "N/A" if value is None else f"{float(value):.{digits}f}"


def _render_markdown(report: Mapping[str, Any]) -> str:
    lines = [
        "# Endocrine-Hygiene Retrieval Comparison",
        "",
        "All quality metrics use the same frozen question battery, a raw candidate pool of 100, first-occurrence paper deduplication, and exact evidence validation against the authoritative Semantic OKF ledger. `N/A` means the unchanged builder could not represent this corpus; it is not a zero score.",
        "",
        "## Best route by builder/consult family",
        "",
        "| Family | Status | Best route | Recall@10 overall | Recall@10 hard | MRR@10 | nDCG@10 | Evidence valid | Mean ms | p95 ms | Reason |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in report["families"]:
        if row["best_route"] is None:
            lines.append(f"| {row['family']} | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | {row['reason']} |")
            continue
        overall, hard = row["overall"], row["hard"]
        lines.append(
            "| {family} | {status} | {route} | {r10} | {hr10} | {mrr} | {ndcg} | {valid} | {mean} | {p95} |  |".format(
                family=row["family"],
                status=row["status"],
                route=row["best_route"],
                r10=_percentage(overall["paper_metrics"]["recall_at_10"]),
                hr10=_percentage(hard["paper_metrics"]["recall_at_10"]),
                mrr=_number(overall["paper_metrics"]["mrr_at_10"]),
                ndcg=_number(overall["paper_metrics"]["ndcg_at_10"]),
                valid=_percentage(overall["evidence_validity"]["ratio"]),
                mean=_number(overall["timing_ms"]["mean"], 1),
                p95=_number(overall["timing_ms"]["p95"], 1),
            )
        )
    lines.extend(
        [
            "",
            "## Route-level results",
            "",
            "| Family | Route | Status | Recall@1 | Recall@3 | Recall@5 | Recall@10 | Hard Recall@10 | MRR@10 | nDCG@10 | Evidence valid | Mean ms |",
            "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in report["routes"]:
        if row["overall"] is None:
            lines.append(f"| {row['family']} | {row['route']} | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |")
            continue
        metrics = row["overall"]["paper_metrics"]
        lines.append(
            "| {family} | {route} | {status} | {r1} | {r3} | {r5} | {r10} | {hard} | {mrr} | {ndcg} | {valid} | {mean} |".format(
                family=row["family"], route=row["route"], status=row["status"],
                r1=_percentage(metrics["recall_at_1"]), r3=_percentage(metrics["recall_at_3"]),
                r5=_percentage(metrics["recall_at_5"]), r10=_percentage(metrics["recall_at_10"]),
                hard=_percentage(row["hard"]["paper_metrics"]["recall_at_10"]),
                mrr=_number(metrics["mrr_at_10"]), ndcg=_number(metrics["ndcg_at_10"]),
                valid=_percentage(row["overall"]["evidence_validity"]["ratio"]),
                mean=_number(row["overall"]["timing_ms"]["mean"], 1),
            )
        )
    lines.extend(
        [
            "",
            "The legacy row is explicitly an evaluator-side deterministic TF-IDF-like ledger baseline. The legacy consult package exposes validated ledger and SPARQL reads but no ranked natural-language search command; this row does not invoke `grep` or `rg` and is not mislabeled as a consult CLI search.",
            "",
        ]
    )
    return "\n".join(lines)


def _atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(content, encoding="utf-8", newline="\n")
    temporary.replace(path)


def _append_only_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise EvaluationError(f"refusing to replace append-only raw result: {path}")
    path.write_text(content, encoding="utf-8", newline="\n")


def evaluate(args: argparse.Namespace) -> dict[str, Any]:
    combination = load_json(args.source_combination)
    identity_by_source = combination.get("identity_by_source")
    if not isinstance(identity_by_source, dict) or not identity_by_source:
        raise EvaluationError("source combination has no identity_by_source map")
    if any(not isinstance(key, str) or not isinstance(value, str) for key, value in identity_by_source.items()):
        raise EvaluationError("source identity map must contain string keys and values")
    questions = load_questions(args.questions, identity_by_source)
    build_report = load_json(args.build_report) if args.build_report.is_file() else None
    routes: list[dict[str, Any]] = []
    inspections: dict[str, Any] = {}
    for family, route_names in FAMILY_ROUTES.items():
        bundle = args.run_dir / "bundles" / f"{family}-a"
        if not bundle.is_dir():
            reason = _failure_reason(family, build_report, bundle)
            routes.extend(_na_route(family, route, reason) for route in route_names)
            continue
        ledger = AuthoritativeLedger(bundle)
        if family == "legacy":
            inspect = _run_json(
                [args.python, str(REPO / "skills/consult-semantic-okf/scripts/query_semantic_okf.py"), str(bundle), "ledger", "--all", "--validate", "--format", "json"],
                args.timeout,
            )
            inspections[family] = {"status": "pass", "ledger_command": "validated", "record_count": len(inspect.get("records", inspect.get("results", [])))}
            index = LegacyLexicalIndex(ledger, identity_by_source)
            routes.append(_evaluate_route(family, "legacy_lexical", questions, ledger, lambda query: index.search(query, RAW_POOL)))
            continue
        try:
            inspections[family] = _inspect_family(args.python, family, bundle, args.timeout)
            searchers = _searchers(family, bundle, identity_by_source, ledger)
        except EvaluationError as exc:
            routes.extend(_error_route(family, route, f"consult initialization failed: {exc}") for route in route_names)
            continue
        for route in route_names:
            routes.append(_evaluate_route(family, route, questions, ledger, searchers[route]))
    report: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "status": _evaluation_status(routes),
        "benchmark": {
            "questions_path": args.questions.relative_to(REPO).as_posix(),
            "questions_sha256": sha256_file(args.questions),
            "question_count": len(questions),
            "hard_question_count": sum(question.cohort == "hard" for question in questions),
            "candidate_pool": RAW_POOL,
            "paper_deduplication": "first occurrence before metric cutoffs",
        },
        "run_dir": args.run_dir.relative_to(REPO).as_posix(),
        "source_identity_path": args.source_combination.relative_to(REPO).as_posix(),
        "inspections": inspections,
        "routes": routes,
    }
    report["families"] = _best_by_family(routes)
    return report


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True, help="Append-only build run containing bundles/<family>-a.")
    parser.add_argument("--questions", type=Path, default=EVALUATION / "benchmark/retrieval-questions.jsonl")
    parser.add_argument("--source-combination", type=Path, default=CORPUS / "source-combination.json")
    parser.add_argument("--build-report", type=Path, default=REPORTS / "build-comparison.json")
    parser.add_argument("--compact-json", type=Path, default=REPORTS / "retrieval-comparison.json")
    parser.add_argument("--compact-markdown", type=Path, default=REPORTS / "retrieval-comparison.md")
    parser.add_argument(
        "--raw-output",
        type=Path,
        help="Append-only detailed report path; defaults to <run-dir>/retrieval/detailed-report.json.",
    )
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--timeout", type=float, default=180.0)
    args = parser.parse_args(argv)
    args.run_dir = args.run_dir.resolve()
    for name in ("questions", "source_combination", "build_report", "compact_json", "compact_markdown"):
        setattr(args, name, getattr(args, name).resolve())
    args.raw_output = (
        args.raw_output.resolve()
        if args.raw_output is not None
        else args.run_dir / "retrieval" / "detailed-report.json"
    )
    if not args.run_dir.is_dir():
        parser.error(f"run directory does not exist: {args.run_dir}")
    return args


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        report = evaluate(args)
        raw_path = args.raw_output
        _append_only_write(raw_path, pretty_json(report))
        compact = dict(report)
        compact["routes"] = [{key: value for key, value in row.items() if key != "queries"} for row in report["routes"]]
        _atomic_write(args.compact_json, pretty_json(compact))
        _atomic_write(args.compact_markdown, _render_markdown(compact))
    except EvaluationError as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1
    if report["status"] != "pass":
        failed = [
            f"{row['family']}/{row['route']}={row['status']}"
            for row in report["routes"]
            if row["status"] not in {"pass", "not-applicable"}
        ]
        print(
            json.dumps(
                {"status": "error", "error": "executable retrieval routes did not pass", "routes": failed},
                ensure_ascii=False,
            ),
            file=sys.stderr,
        )
        return 1
    print(json.dumps({"status": "pass", "routes": len(report["routes"]), "families": len(report["families"]), "raw_report": str(raw_path)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
