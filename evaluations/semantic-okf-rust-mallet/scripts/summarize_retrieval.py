#!/usr/bin/env python3
"""Summarize RustMallet retrieval runs against the frozen classical baseline."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Mapping, Sequence


SCHEMA_VERSION = "semantic-okf-rust-mallet-retrieval-summary/1.0"
MODES = ("bm25", "topic", "association", "fusion")
METRICS = ("recall_at_10", "mrr_at_10", "ndcg_at_10")
COHORTS = ("all_40", "original_30", "hard_10")


class SummaryError(RuntimeError):
    """Describe invalid or incomparable evaluation evidence."""


def _load(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise SummaryError(f"cannot load {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise SummaryError(f"{path} must contain a JSON object")
    return value


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _tree(root: Path) -> dict[str, Any]:
    if not root.is_dir():
        raise SummaryError(f"build directory is missing: {root}")
    files = [path for path in sorted(root.rglob("*")) if path.is_file()]
    inventory = [
        {"path": path.relative_to(root).as_posix(), "sha256": _sha256(path)}
        for path in files
    ]
    payload = b"".join(
        row["path"].encode("utf-8") + b"\0" + row["sha256"].encode("ascii") + b"\0"
        for row in inventory
    )
    return {
        "file_count": len(inventory),
        "tree_sha256": hashlib.sha256(payload).hexdigest(),
        "files": inventory,
    }


def _rust_routes(report: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    routes = report.get("routes")
    if not isinstance(routes, list):
        raise SummaryError("RustMallet run has no route array")
    result = {
        str(row.get("name")): row
        for row in routes
        if isinstance(row, dict) and str(row.get("name", "")).startswith("rust_mallet_")
    }
    expected = {f"rust_mallet_{mode}" for mode in MODES}
    if set(result) != expected:
        raise SummaryError("RustMallet run does not contain the four expected routes")
    return result


def _rust_cohort(route: Mapping[str, Any], cohort: str) -> Mapping[str, Any]:
    if cohort == "all_40":
        return route
    cohorts = route.get("cohorts")
    value = cohorts.get(cohort) if isinstance(cohorts, dict) else None
    if not isinstance(value, dict):
        raise SummaryError(f"RustMallet route is missing cohort {cohort}")
    return value


def _compact_rust(route: Mapping[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {
        "query_count": route["query_count"],
        "error_count": route["error_count"],
        "evidence_validity": route["evidence_validity"],
        "timing_ms": route["timing_ms"],
    }
    for cohort in COHORTS:
        source = _rust_cohort(route, cohort)
        result[cohort] = {
            "paper": source["paper_metrics"],
            "source": source["source_metrics"],
            "evidence_validity": source["evidence_validity"],
            "error_count": source["error_count"],
        }
    return result


def _delta(left: Any, right: Any) -> float:
    value = round(float(left) - float(right), 8)
    return 0.0 if value == 0.0 else value


def _assert_run(report: Mapping[str, Any], top_k: int) -> None:
    if report.get("schema_version") != "1.4" or report.get("query_count") != 40:
        raise SummaryError("RustMallet run identity or question count is invalid")
    if report.get("top_k") != top_k:
        raise SummaryError(f"expected top-k {top_k}, found {report.get('top_k')!r}")
    parity = report.get("core_semantic_parity")
    if not isinstance(parity, dict) or parity.get("status") != "pass":
        raise SummaryError("RustMallet run failed authoritative core parity")
    raw = report.get("inputs", {}).get("raw_input_verification")
    if not isinstance(raw, dict) or raw.get("status") != "pass":
        raise SummaryError("RustMallet run failed raw input verification")
    for route in _rust_routes(report).values():
        if route.get("error_count") != 0:
            raise SummaryError(f"route {route.get('name')} contains errors")
        evidence = route.get("evidence_validity")
        if not isinstance(evidence, dict) or evidence.get("ratio") != 1.0:
            raise SummaryError(f"route {route.get('name')} contains invalid evidence")


def _assert_shared_baselines(
    report: Mapping[str, Any], classical_run: Mapping[str, Any]
) -> None:
    observed = {
        str(row.get("name")): row
        for row in report["routes"]
        if isinstance(row, dict)
        and not str(row.get("name", "")).startswith("rust_mallet_")
    }
    for name in ("legacy_lexical", "new_lexical", "vector", "hybrid"):
        current = observed.get(name)
        frozen = classical_run["routes"].get(name)
        if not isinstance(current, dict) or not isinstance(frozen, dict):
            raise SummaryError(f"shared baseline {name} is missing")
        for cohort in COHORTS:
            current_metrics = _rust_cohort(current, cohort)["paper_metrics"]
            frozen_metrics = frozen[cohort]["paper"]
            if any(
                not math.isclose(
                    float(current_metrics[metric]),
                    float(frozen_metrics[metric]),
                    rel_tol=0.0,
                    abs_tol=1e-8,
                )
                for metric in METRICS
            ):
                raise SummaryError(
                    f"shared baseline {name}/{cohort} drifted from the frozen comparison"
                )


def summarize(
    top10_path: Path,
    pool100_path: Path,
    classical_path: Path,
    build_a: Path,
    build_b: Path,
) -> dict[str, Any]:
    """Validate two runs and return a compact, evidence-bound comparison."""

    top10 = _load(top10_path)
    pool100 = _load(pool100_path)
    classical = _load(classical_path)
    _assert_run(top10, 10)
    _assert_run(pool100, 100)
    classical_runs = classical.get("runs")
    if not isinstance(classical_runs, dict) or set(classical_runs) < {
        "top10",
        "pool100",
    }:
        raise SummaryError("frozen classical summary is missing top10 or pool100")
    _assert_shared_baselines(top10, classical_runs["top10"])
    _assert_shared_baselines(pool100, classical_runs["pool100"])

    first_tree = _tree(build_a)
    second_tree = _tree(build_b)
    deterministic = (
        first_tree["file_count"] == second_tree["file_count"]
        and first_tree["tree_sha256"] == second_tree["tree_sha256"]
        and first_tree["files"] == second_tree["files"]
    )
    if not deterministic:
        raise SummaryError("the two clean RustMallet builds are not byte-identical")

    runs: dict[str, Any] = {}
    for label, report, frozen in (
        ("top10", top10, classical_runs["top10"]),
        ("pool100", pool100, classical_runs["pool100"]),
    ):
        rust = _rust_routes(report)
        comparisons: dict[str, Any] = {}
        for mode in MODES:
            classical_route = frozen["routes"][f"classical_{mode}"]
            rust_route = _compact_rust(rust[f"rust_mallet_{mode}"])
            deltas = {
                cohort: {
                    metric: _delta(
                        rust_route[cohort]["paper"][metric],
                        classical_route[cohort]["paper"][metric],
                    )
                    for metric in METRICS
                }
                for cohort in COHORTS
            }
            comparisons[mode] = {
                "classical": classical_route,
                "rust_mallet": rust_route,
                "rust_mallet_minus_classical": deltas,
            }
        runs[label] = {
            "top_k": report["top_k"],
            "query_count": report["query_count"],
            "input_sha256": _sha256(top10_path if label == "top10" else pool100_path),
            "core_semantic_parity": "pass",
            "evidence_validity": "pass",
            "comparisons": comparisons,
        }

    return {
        "schema_version": SCHEMA_VERSION,
        "comparison": "classical-topic-communities-vs-rust-mallet-lda",
        "question_count": 40,
        "cohorts": {"all_40": 40, "original_30": 30, "hard_10": 10},
        "rust_mallet": {
            "repository": "https://github.com/mimno/RustMallet",
            "package": "pyrmallet",
            "version": "0.1.1",
            "algorithm": "pyrmallet-0.1.1-sparse-gibbs-lda-v1",
        },
        "determinism": {
            "status": "pass",
            "byte_identical": True,
            "file_count": first_tree["file_count"],
            "tree_sha256": first_tree["tree_sha256"],
        },
        "runs": runs,
        "conclusion": (
            "Retain RustMallet as an experimental skill pair. It preserves BM25 and exact evidence "
            "validity but does not replace the classical topic-community default on this benchmark."
        ),
    }


def _percent(value: Any) -> str:
    return f"{100.0 * float(value):.2f}%"


def render_markdown(summary: Mapping[str, Any]) -> str:
    """Render the compact comparison without raw evidence text."""

    lines = [
        "# RustMallet Semantic OKF Retrieval Evaluation",
        "",
        "The fixed-seed RustMallet candidate passed two-build byte determinism, authoritative-core parity, and exact evidence validation on all 40 GraphRAG questions.",
        "",
        "## Top-10 comparison",
        "",
        "| Mode | Classical recall@10 | RustMallet recall@10 | Delta | Classical nDCG@10 | RustMallet nDCG@10 | Delta |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for mode in MODES:
        row = summary["runs"]["top10"]["comparisons"][mode]
        classical = row["classical"]["all_40"]["paper"]
        rust = row["rust_mallet"]["all_40"]["paper"]
        delta = row["rust_mallet_minus_classical"]["all_40"]
        lines.append(
            f"| {mode} | {_percent(classical['recall_at_10'])} | {_percent(rust['recall_at_10'])} | "
            f"{_percent(delta['recall_at_10'])} | {_percent(classical['ndcg_at_10'])} | "
            f"{_percent(rust['ndcg_at_10'])} | {_percent(delta['ndcg_at_10'])} |"
        )
    lines.extend(
        [
            "",
            "## Hard-10 comparison",
            "",
            "| Mode | Classical recall@10 | RustMallet recall@10 | Delta | Classical nDCG@10 | RustMallet nDCG@10 | Delta |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for mode in MODES:
        row = summary["runs"]["top10"]["comparisons"][mode]
        classical = row["classical"]["hard_10"]["paper"]
        rust = row["rust_mallet"]["hard_10"]["paper"]
        delta = row["rust_mallet_minus_classical"]["hard_10"]
        lines.append(
            f"| {mode} | {_percent(classical['recall_at_10'])} | {_percent(rust['recall_at_10'])} | "
            f"{_percent(delta['recall_at_10'])} | {_percent(classical['ndcg_at_10'])} | "
            f"{_percent(rust['ndcg_at_10'])} | {_percent(delta['ndcg_at_10'])} |"
        )
    determinism = summary["determinism"]
    lines.extend(
        [
            "",
            "## Validation",
            "",
            f"- Two clean builds were byte-identical across {determinism['file_count']} files with tree SHA-256 `{determinism['tree_sha256']}`.",
            "- Both retrieval runs had passing authoritative-core parity, zero route errors, and 100% exact evidence validity.",
            "- The pool-100 run is retained in the JSON summary to distinguish candidate-budget effects from top-10 ranking quality.",
            "",
            "## Decision",
            "",
            summary["conclusion"],
            "",
        ]
    )
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--top10", type=Path, required=True)
    parser.add_argument("--pool100", type=Path, required=True)
    parser.add_argument("--classical-summary", type=Path, required=True)
    parser.add_argument("--build-a", type=Path, required=True)
    parser.add_argument("--build-b", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-markdown", type=Path, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        summary = summarize(
            args.top10.resolve(),
            args.pool100.resolve(),
            args.classical_summary.resolve(),
            args.build_a.resolve(),
            args.build_b.resolve(),
        )
    except SummaryError as exc:
        print(f"summary error: {exc}")
        return 2
    args.output_json.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.output_markdown.write_text(render_markdown(summary), encoding="utf-8")
    print(
        json.dumps({"status": "pass", "schema_version": SCHEMA_VERSION}, sort_keys=True)
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
