#!/usr/bin/env python3
"""Freeze the exhaustive historical GraphRAG strategy table before evaluation."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Sequence


REPO = Path(__file__).resolve().parents[3]
HISTORICAL_TABLE = REPO / "evaluations" / "LATEST-REPORT.comparison.json"
GENERAL_ROOT = (
    REPO
    / "evaluations"
    / "graphrag-unseen-generalization"
    / "study-v4-general"
    / "private"
)
RUNTIME_BUNDLES = GENERAL_ROOT / "runtime-bundles"
ENSEMBLE_EXPERT = (
    REPO
    / "evaluations"
    / "semantic-okf-tika-mallet-tantivy"
    / "generated"
    / "specialized-experts"
    / "20260728-ensemble-quality-02"
    / "experts"
    / "graphrag-ensemble-quality-expert-v46"
)
SPECIALIZED_ROOT = (
    REPO
    / "evaluations"
    / "semantic-okf-tika-mallet-tantivy"
    / "generated"
    / "specialized-experts"
)
V51 = (
    REPO
    / "evaluations"
    / "semantic-okf-specialized-experts"
    / "generated"
    / "20260728-definitive-profiles-03"
    / "experts"
    / "graphrag-papers-definitive-expert-v51"
)


class FreezeError(RuntimeError):
    """Describe an incomplete or drifting general-strategy freeze."""


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _display(path: Path) -> str:
    return path.resolve().relative_to(REPO.resolve()).as_posix()


def _artifact(path: Path) -> dict[str, Any]:
    resolved = path.resolve()
    if resolved.is_file():
        return {
            "path": _display(resolved),
            "kind": "file",
            "bytes": resolved.stat().st_size,
            "sha256": _sha256(resolved),
        }
    if not resolved.is_dir():
        raise FreezeError(f"strategy artifact is missing: {path}")
    rows = [
        {
            "path": item.relative_to(resolved).as_posix(),
            "bytes": item.stat().st_size,
            "sha256": _sha256(item),
        }
        for item in sorted(resolved.rglob("*"))
        if item.is_file()
    ]
    payload = json.dumps(
        rows,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return {
        "path": _display(resolved),
        "kind": "directory",
        "file_count": len(rows),
        "bytes": sum(row["bytes"] for row in rows),
        "tree_sha256": hashlib.sha256(payload).hexdigest(),
    }


def _strategy_artifacts() -> dict[str, list[Path]]:
    adaptive_evaluator = (
        REPO / "evaluations/semantic-okf-adaptive/scripts/compare_general_retrieval.py"
    )
    embedding = REPO / "evaluations/semantic-okf-embeddings/results/embedding-bundle"
    classical = (
        REPO
        / "evaluations/semantic-okf-datasets/generated/bundles/graphrag-papers-40/classical"
    )
    legacy = REPO / "evaluations/graphrag-cross-paper/bundle"
    entity = RUNTIME_BUNDLES / "entity-graph-frozen"
    adaptive = RUNTIME_BUNDLES / "adaptive-frozen"
    result: dict[str, list[Path]] = {}
    for strategy in ("legacy-lexical",):
        result[strategy] = [legacy, adaptive_evaluator]
    for strategy in ("embeddings-lexical", "embeddings-vector", "embeddings-hybrid"):
        result[strategy] = [
            embedding,
            REPO
            / "skills/consult-semantic-okf-embeddings/scripts/query_semantic_okf_embeddings.py",
            adaptive_evaluator,
        ]
    for strategy in (
        "classical-bm25",
        "classical-topic",
        "classical-association",
        "classical-fusion",
    ):
        result[strategy] = [
            classical,
            REPO
            / "skills/consult-semantic-okf-classical/scripts/query_semantic_okf_classical.py",
            adaptive_evaluator,
        ]
    for strategy in (
        "entity-graph-lexical",
        "entity-graph-entity",
        "entity-graph-traversal",
        "entity-graph-fusion",
    ):
        result[strategy] = [
            entity,
            REPO
            / "skills/consult-semantic-okf-entity-graph/scripts/query_semantic_okf_entity_graph.py",
            adaptive_evaluator,
        ]
    result["adaptive-fusion"] = [
        adaptive,
        REPO
        / "skills/consult-semantic-okf-adaptive/scripts/query_semantic_okf_adaptive.py",
        adaptive_evaluator,
    ]
    for strategy in ("ensemble-fast", "ensemble-robust"):
        result[strategy] = [
            ENSEMBLE_EXPERT / "references" / "knowledge",
            REPO
            / "skills/consult-semantic-okf-ensemble/scripts/query_semantic_okf_ensemble.py",
            REPO / "evaluations/semantic-okf-ensemble/scripts/run_frozen_retrieval.py",
        ]
    rust_inputs = [
        REPO / "evaluations/semantic-okf-rust-mallet/rust-mallet-plan.json",
        REPO
        / "skills/build-semantic-okf-rust-mallet/scripts/build_semantic_okf_rust_mallet.py",
        REPO
        / "skills/consult-semantic-okf-rust-mallet-evolved/scripts/query_semantic_okf_rust_mallet.py",
    ]
    for strategy in (
        "rust-mallet-bm25",
        "rust-mallet-topic",
        "rust-mallet-association",
        "rust-mallet-fusion",
    ):
        result[strategy] = rust_inputs
    result["tantivy-bm25"] = [
        REPO
        / "evaluations/semantic-okf-datasets/generated/campaigns"
        / "20260723-papers-consult-gpt53-spark-05/bundles/classical",
        REPO / "skills/consult-semantic-okf-tantivy/scripts/query_semantic_okf_tantivy.py",
    ]
    tika_bundle = (
        REPO
        / "evaluations/semantic-okf-tika-mallet/generated/graphrag-papers-40"
        / "bundle-attempt-10-ascii"
    )
    result["tika-mallet-fusion"] = [
        tika_bundle,
        REPO
        / "skills/consult-semantic-okf-tika-mallet/scripts/query_semantic_okf_tika_mallet.py",
    ]
    result["tika-mallet-tantivy-fusion"] = [
        tika_bundle,
        REPO
        / "skills/consult-semantic-okf-tika-mallet-tantivy/scripts"
        / "query_semantic_okf_tika_mallet_tantivy.py",
    ]
    result["specialized-expert-trace-early-confidence"] = [
        SPECIALIZED_ROOT
        / "20260728-trace-early-confidence-01/experts/graphrag-trace-expert-v45"
    ]
    result["specialized-expert-ensemble-quality-trace-v48"] = [
        SPECIALIZED_ROOT
        / "20260728-ensemble-quality-trace-02/experts"
        / "graphrag-ensemble-quality-trace-expert-v48"
    ]
    result["specialized-expert-supervised-profiles-v51"] = [V51]
    return result


def freeze(output: Path) -> dict[str, Any]:
    """Bind the exact exhaustive historical table and every selected runtime."""

    if output.exists() or output.is_symlink():
        raise FreezeError(f"refusing to overwrite selection: {output}")
    historical = json.loads(HISTORICAL_TABLE.read_text(encoding="utf-8"))
    alternatives = historical.get("alternatives")
    if not isinstance(alternatives, list) or len(alternatives) != 25:
        raise FreezeError("historical comparison must contain exactly 25 alternatives")
    definitions = _strategy_artifacts()
    ids = [row.get("id") for row in alternatives if isinstance(row, dict)]
    if len(ids) != 25 or len(set(ids)) != 25 or set(ids) != set(definitions):
        raise FreezeError("historical alternatives and strategy definitions differ")
    rows = []
    for historical_row in alternatives:
        strategy_id = historical_row["id"]
        rows.append(
            {
                "strategy_id": strategy_id,
                "label": historical_row["label"],
                "selection_basis": "exhaustive member of the pre-existing 25-row general table",
                "artifacts": [
                    _artifact(path) for path in definitions[strategy_id]
                ],
            }
        )
    result = {
        "schema_version": "graphrag-general-strategy-freeze/1.0",
        "dataset_id": "graphrag-papers-parallel-eval-60-v1",
        "selection_id": "exhaustive-historical-general-table-v1",
        "selection_rule": (
            "Include every row from the pre-existing 25-strategy general table; "
            "do not filter, tune, evolve, or replace a strategy after evaluation-only release."
        ),
        "historical_table": _artifact(HISTORICAL_TABLE),
        "strategy_count": len(rows),
        "strategies": rows,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return result


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        result = freeze(args.output)
    except (FreezeError, OSError, UnicodeError, ValueError, TypeError) as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, sort_keys=True))
        return 2
    print(
        json.dumps(
            {
                "status": "pass",
                "selection_id": result["selection_id"],
                "strategy_count": result["strategy_count"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
