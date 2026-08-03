#!/usr/bin/env python3
"""Build and validate every registered retrieval-family snapshot for a private book corpus."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Sequence


REPO = Path(__file__).resolve().parents[3]
FAMILIES = (
    "embeddings",
    "classical",
    "adaptive",
    "entity-graph",
    "ensemble",
    "graphify",
    "turso",
)


class PreparationError(RuntimeError):
    """Describe an invalid plan, failed build, or failed validation."""


def canonical_json(value: Any) -> str:
    """Serialize one value deterministically."""

    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def sha256_file(path: Path) -> str:
    """Return the SHA-256 digest of one file."""

    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json(path: Path, value: Any) -> None:
    """Write deterministic, human-readable JSON."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            value,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
            allow_nan=False,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )


def source_ids(manifest: dict[str, Any]) -> list[str]:
    """Return the manifest's sorted closed source selection."""

    sources = manifest.get("sources")
    if not isinstance(sources, list) or not sources:
        raise PreparationError("manifest sources must be a non-empty array")
    identifiers = [
        row.get("id")
        for row in sources
        if isinstance(row, dict) and isinstance(row.get("id"), str)
    ]
    if len(identifiers) != len(sources) or len(set(identifiers)) != len(identifiers):
        raise PreparationError("manifest source identities are invalid")
    return sorted(identifiers)


def classical_plan(selection: list[str]) -> dict[str, Any]:
    """Create the shared deterministic classical plan."""

    return {
        "schema_version": "1.0",
        "selection": {"source_ids": selection},
        "tokenization": {
            "tokenizer": "ascii-alphanumeric-v1",
            "stopwords": "english-v1",
            "min_token_length": 2,
            "ngram_range": [1, 2],
        },
        "bm25": {
            "k1": 1.2,
            "b": 0.75,
            "title_weight": 2.0,
            "body_weight": 1.0,
        },
        "associations": {
            "window_size": 8,
            "min_document_frequency": 2,
            "min_cooccurrence": 2,
            "max_vocabulary": 6000,
            "max_neighbors": 8,
            "minimum_ppmi": 0.0,
        },
        "topics": {
            "topic_count": 24,
            "max_iterations": 20,
            "top_terms": 20,
        },
        "expansion": {
            "association_terms": 6,
            "topic_terms": 6,
            "association_weight": 0.35,
            "topic_weight": 0.2,
        },
        "reranking": {
            "candidate_pool": 100,
            "relevance_weight": 0.7,
            "topic_novelty_weight": 0.15,
            "source_novelty_weight": 0.15,
            "max_per_evidence_identity": 1,
            "rrf_k": 60,
        },
    }


def adaptive_plan(selection: list[str]) -> dict[str, Any]:
    """Create the source-generic adaptive plan."""

    plan = classical_plan(selection)
    plan["schema_version"] = "1.1"
    plan["evidence_identity"] = {
        "default_mode": "source-record",
        "paper_ids_by_source": {},
    }
    plan["passages"] = {
        "default_mode": "full-record",
        "markdown_pdf_page_source_ids": [],
    }
    plan["adaptive"] = {
        "aspect_weight": 0.25,
        "best_aspect_weight": 0.0,
        "full_query_weight": 2.0,
        "maximum_aspects": 10,
        "maximum_novel_aspect_rank": 1,
        "minimum_aspect_tokens": 4,
        "protected_full_results": 10,
        "rrf_k": 0,
    }
    return plan


def entity_graph_plan(selection: list[str]) -> dict[str, Any]:
    """Create the source-generic entity graph plan."""

    return {
        "schema_version": "2.0",
        "selection": {"source_ids": selection},
        "sectioning": {
            "strategy": "markdown-headings-or-bounded-record-v1",
            "maximum_characters": 12000,
        },
        "tokenization": {
            "tokenizer": "ascii-alphanumeric-v1",
            "stopwords": "english-v1",
            "min_token_length": 2,
        },
        "bm25": {"k1": 1.2, "b": 0.75},
        "extraction": {
            "ngram_range": [1, 3],
            "minimum_section_frequency": 2,
            "maximum_section_fraction": 0.35,
            "maximum_candidates": 1200,
            "top_candidates_per_section": 12,
        },
        "graph": {
            "minimum_co_mention_sections": 2,
            "max_co_mention_neighbors": 12,
            "max_co_mentions_per_section": 12,
            "max_edge_evidence_sections": 8,
        },
        "query": {
            "candidate_pool": 100,
            "resolved_entities": 32,
            "max_hops": 3,
            "hop_decay": 0.65,
            "mention_weight": 1.0,
            "reviewed_edge_weight": 1.0,
            "candidate_edge_weight": 0.3,
            "rrf_k": 60,
            "max_per_document": 1,
        },
    }


def embedding_plan(selection: list[str]) -> dict[str, Any]:
    """Create the dependency-free record-level hashing plan."""

    return {
        "schema_version": "1.0",
        "selection": {"source_ids": selection},
        "chunking": {
            "implementation": "native",
            "strategy": "record",
            "buffer_size": 1,
            "breakpoint_percentile_threshold": 95,
        },
        "embedding": {
            "provider": "hashing",
            "model_id": "knowledge-hashing-embedding",
            "revision": "1",
            "dimension": 384,
            "normalize": True,
        },
    }


def ensemble_plan(selection: list[str]) -> dict[str, Any]:
    """Create the closed source-generic ensemble plan."""

    return {
        "schema_version": "2.0",
        "adaptive": adaptive_plan(selection),
        "entity_graph": entity_graph_plan(selection),
        "embedding": embedding_plan(selection),
        "identity": {
            "default_grouping": "source-record-v1",
            "overrides": [],
        },
        "policies": {
            "default": "quality",
            "fast": {
                "routes": ["adaptive", "graph_lexical"],
                "weights": [4, 1],
                "rrf_k": 5,
                "protected_route": "adaptive",
                "promotion": {
                    "route": "graph_lexical",
                    "confirmation_routes": ["adaptive", "graph_lexical"],
                    "confirmation_depth": 3,
                    "minimum_confirmations": 2,
                    "maximum_protected_rank": 3,
                },
            },
            "quality": {
                "routes": [
                    "adaptive",
                    "graph_fusion",
                    "bm25",
                    "embedding_hybrid",
                ],
                "weights": [4, 1, 5, 1],
                "rrf_k": 7,
                "protected_route": "adaptive",
                "promotion": {
                    "route": "graph_lexical",
                    "confirmation_routes": [
                        "adaptive",
                        "graph_lexical",
                        "graph_fusion",
                        "bm25",
                        "embedding_hybrid",
                    ],
                    "confirmation_depth": 3,
                    "minimum_confirmations": 3,
                    "maximum_protected_rank": 10,
                },
            },
            "robust": {
                "routes": ["adaptive"],
                "weights": [1],
                "rrf_k": 0,
                "protected_route": "adaptive",
                "promotion": {
                    "route": "adaptive",
                    "confirmation_routes": ["adaptive"],
                    "confirmation_depth": 1,
                    "minimum_confirmations": 1,
                    "maximum_protected_rank": 1,
                },
            },
        },
        "quality_gates": {
            "required_components": ["adaptive", "entity_graph", "embedding"],
            "protect_candidate_set": True,
            "require_core_parity": True,
            "reviewed_graph_claims_only": True,
            "reviewed_embedding_claims_only": True,
            "require_facet_status": True,
            "require_exact_answer_bindings": True,
            "candidate_edge_weight": 0.0,
            "maximum_graph_claims_per_facet": 8,
            "maximum_graph_claims_total": 80,
            "maximum_embedding_claims_per_facet": 20,
            "maximum_embedding_claims_total": 240,
            "require_child_plan_parity": True,
            "require_total_identity_crosswalk": True,
            "require_component_group_parity": True,
            "require_exact_passage_evidence": True,
            "claim_only_coverage_requires_bindings": True,
        },
    }


def run(command: list[str]) -> dict[str, Any]:
    """Run one child command and retain its machine-readable audit."""

    completed = subprocess.run(
        command,
        cwd=REPO,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    result = {
        "command": command,
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }
    if completed.returncode != 0:
        raise PreparationError(
            f"command failed ({completed.returncode}): {' '.join(command)}\n"
            f"{completed.stdout}\n{completed.stderr}"
        )
    return result


def family_commands(
    family: str,
    manifest: Path,
    plan_path: Path | None,
    output: Path,
) -> tuple[list[str], list[list[str]]]:
    """Return one build command and its independent validators."""

    root = REPO / "skills" / f"build-semantic-okf-{family}" / "scripts"
    python = sys.executable
    if family in {"embeddings", "classical", "adaptive", "entity-graph", "ensemble"}:
        slug = family.replace("-", "_")
        build = [
            python,
            str(root / f"build_semantic_okf_{slug}.py"),
            str(manifest),
            str(plan_path),
            str(output),
            "--output-format",
            "json",
        ]
        validators = [
            [
                python,
                str(root / f"validate_semantic_okf_{slug}.py"),
                str(output),
                "--output-format",
                "json",
            ]
        ]
        return build, validators
    if family == "graphify":
        return (
            [
                python,
                str(root / "build_semantic_okf_graphify.py"),
                str(manifest),
                str(output),
                "--output-format",
                "json",
            ],
            [
                [
                    python,
                    str(root / "validate_semantic_okf_graphify.py"),
                    str(output),
                    "--output-format",
                    "json",
                ]
            ],
        )
    if family == "turso":
        return (
            [
                python,
                str(root / "build_semantic_okf.py"),
                str(manifest),
                str(output),
                "--output-format",
                "json",
            ],
            [
                [
                    python,
                    str(root / "validate_semantic_okf.py"),
                    str(output),
                    "--output-format",
                    "json",
                ],
                [
                    python,
                    str(root / "validate_turso_store.py"),
                    str(output / "semantic" / "knowledge.db"),
                    "--bundle",
                    str(output),
                    "--output-format",
                    "json",
                ],
            ],
        )
    raise PreparationError(f"unsupported family: {family}")


def prepare(
    manifest_path: Path,
    output_root: Path,
    families: Sequence[str],
    verify_existing: bool,
) -> dict[str, Any]:
    """Build or verify the selected family snapshots."""

    manifest_path = manifest_path.resolve()
    output_root = output_root.resolve()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    selection = source_ids(manifest)
    plans = {
        "embeddings": embedding_plan(selection),
        "classical": classical_plan(selection),
        "adaptive": adaptive_plan(selection),
        "entity-graph": entity_graph_plan(selection),
        "ensemble": ensemble_plan(selection),
    }
    plan_paths: dict[str, Path] = {}
    for family, plan in plans.items():
        path = output_root / "plans" / f"{family}-plan.json"
        if path.exists():
            existing = json.loads(path.read_text(encoding="utf-8"))
            if canonical_json(existing) != canonical_json(plan):
                raise PreparationError(f"existing plan drifted: {path}")
        else:
            write_json(path, plan)
        plan_paths[family] = path

    rows: list[dict[str, Any]] = []
    for family in families:
        output = output_root / "bundles" / family
        build, validators = family_commands(
            family,
            manifest_path,
            plan_paths.get(family),
            output,
        )
        commands: list[dict[str, Any]] = []
        if output.exists():
            if not verify_existing:
                raise PreparationError(
                    f"output already exists; use --verify-existing: {output}"
                )
        else:
            commands.append(run(build))
        for command in validators:
            commands.append(run(command))
        records = output / "semantic" / "records.jsonl"
        rows.append(
            {
                "family": family,
                "output": str(output),
                "records_sha256": sha256_file(records),
                "commands": commands,
            }
        )

    record_hashes = {row["records_sha256"] for row in rows}
    if len(record_hashes) != 1:
        raise PreparationError("authoritative record ledgers differ across families")
    receipt = {
        "schema_version": "private-book-strategy-build/1.0",
        "status": "pass",
        "manifest": {
            "path": str(manifest_path),
            "sha256": sha256_file(manifest_path),
        },
        "selection": selection,
        "families": rows,
        "core_records_sha256": next(iter(record_hashes)),
    }
    write_json(output_root / "build-receipt.json", receipt)
    return receipt


def build_parser() -> argparse.ArgumentParser:
    """Create the command-line parser."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument(
        "--family",
        action="append",
        choices=FAMILIES,
        dest="families",
        help="Build one family; repeat as needed. Defaults to every family.",
    )
    parser.add_argument("--verify-existing", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the build and validation workflow."""

    args = build_parser().parse_args(argv)
    try:
        receipt = prepare(
            args.manifest,
            args.output_root,
            args.families or FAMILIES,
            args.verify_existing,
        )
    except (
        PreparationError,
        OSError,
        UnicodeError,
        json.JSONDecodeError,
        ValueError,
        TypeError,
    ) as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, sort_keys=True))
        return 2
    print(
        json.dumps(
            {
                "status": "pass",
                "families": [row["family"] for row in receipt["families"]],
                "records_sha256": receipt["core_records_sha256"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
