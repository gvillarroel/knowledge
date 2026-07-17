from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    REPO_ROOT
    / "evaluations"
    / "semantic-okf-ensemble"
    / "scripts"
    / "evaluate_hard10_coverage_pack.py"
)
HISTORICAL_REPORT = (
    REPO_ROOT
    / "evaluations"
    / "semantic-okf-ensemble"
    / "hard10-coverage-pack-final.json"
)


def _load() -> ModuleType:
    scripts = SCRIPT.parent
    if str(scripts) not in sys.path:
        sys.path.insert(0, str(scripts))
    spec = importlib.util.spec_from_file_location(
        "semantic_okf_ensemble_multisignal_coverage_evaluation",
        SCRIPT,
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def evaluator() -> ModuleType:
    return _load()


def _binding(claim_id: str = "claim-1") -> dict[str, object]:
    return {
        "record_id": claim_id,
        "paper_id": "paper-a",
        "concept_path": f"concepts/{claim_id}.md",
        "source_path": "sources/claims/paper-a.jsonl",
        "locator_tokens": ["PDF-page-3"],
        "citation_pages": [3],
        "authoritative_text": "An exact reviewed claim.",
        "authoritative_text_sha256": "a" * 64,
        "review_state": "reviewed",
    }


def _candidate(binding: dict[str, object]) -> dict[str, object]:
    return {
        "rank": 1,
        "claim_id": binding["record_id"],
        "paper_id": binding["paper_id"],
        "score": 0.75,
        "concept_path": binding["concept_path"],
        "source_path": binding["source_path"],
        "locators": binding["locator_tokens"],
        "citation_pages": binding["citation_pages"],
        "authoritative_text": binding["authoritative_text"],
        "authoritative_text_sha256": binding["authoritative_text_sha256"],
        "review_state": "reviewed",
    }


def test_historical_v1_report_is_preserved_and_not_accepted_as_v2(
    evaluator: ModuleType,
) -> None:
    historical = json.loads(HISTORICAL_REPORT.read_text(encoding="utf-8"))
    assert historical["schema_version"] == "semantic-okf-ensemble-hard10-coverage-pack/1.0"
    assert historical["status"] == "pass"
    assert evaluator.SCHEMA_VERSION == "semantic-okf-ensemble-hard10-coverage-pack/2.0"
    with pytest.raises(evaluator.EvaluationError, match="version or status"):
        evaluator.validate_report(historical)


def test_embedding_candidates_require_exact_reviewed_bindings_and_semantic_limit(
    evaluator: ModuleType,
) -> None:
    binding = _binding()
    pack = {
        "gates": {"maximum_embedding_claims_per_facet": 20},
        "embedding_queries": [
            {
                "query_kind": "full",
                "facet": "semantic query",
                "returned": 1,
                "candidates": [_candidate(binding)],
            }
        ],
    }
    assert evaluator._embedding_ids(
        pack,
        {"claim-1": binding},
        {"claim-1"},
    ) == {"claim-1"}

    tampered = json.loads(json.dumps(pack))
    tampered["embedding_queries"][0]["candidates"][0]["authoritative_text_sha256"] = "b" * 64
    with pytest.raises(evaluator.EvaluationError, match="exact unique binding"):
        evaluator._embedding_ids(tampered, {"claim-1": binding}, {"claim-1"})

    over_limit = json.loads(json.dumps(pack))
    over_limit["gates"]["maximum_embedding_claims_per_facet"] = 0
    with pytest.raises(evaluator.EvaluationError, match="exceeds or differs"):
        evaluator._embedding_ids(over_limit, {"claim-1": binding}, {"claim-1"})


def test_embedding_provider_plan_and_index_are_bound(
    evaluator: ModuleType,
) -> None:
    config = {
        "provider": "sentence-transformers",
        "model_id": "sentence-transformers/all-MiniLM-L6-v2",
        "revision": "1" * 40,
        "dimension": 384,
        "normalize": True,
    }
    component_plan = {
        "schema_version": "1.0",
        "embedding": config,
    }
    digest = evaluator._canonical_sha(component_plan)
    snapshot = SimpleNamespace(
        embedding=SimpleNamespace(
            index={
                "retrieval_plan_sha256": digest,
                "embedding": {**config, "metric": "cosine"},
            },
            hashes={
                "index_sha256": "a" * 64,
                "chunks_sha256": "b" * 64,
                "embeddings_sha256": "c" * 64,
            },
        )
    )
    ensemble_index = {
        "components": {
            "embedding": {
                "index": {
                    "path": "retrieval/index.json",
                    "sha256": "a" * 64,
                }
            }
        }
    }
    result = evaluator._embedding_route_binding(
        snapshot,
        ensemble_index,
        {"embedding": component_plan},
    )
    assert result["provider"] == "sentence-transformers"
    assert result["retrieval_plan_sha256"] == digest
    assert result["index_sha256"] == "a" * 64

    snapshot.embedding.index["embedding"]["revision"] = "2" * 40
    with pytest.raises(evaluator.EvaluationError, match="provider/model"):
        evaluator._embedding_route_binding(
            snapshot,
            ensemble_index,
            {"embedding": component_plan},
        )


def test_group_metrics_and_candidate_overlaps_include_embedding(
    evaluator: ModuleType,
) -> None:
    routes = {
        "adaptive": {"a", "shared"},
        "graph": {"g", "shared"},
        "embedding": {"e", "shared"},
        "union": {"a", "g", "e", "shared"},
    }
    rows = evaluator._group_rows(
        [
            {
                "id": "answer-1",
                "statement": "The semantic route contributes an exact option.",
                "evidence_claim_ids": ["e"],
            }
        ],
        routes,
    )
    assert rows[0]["adaptive_covered"] is False
    assert rows[0]["graph_covered"] is False
    assert rows[0]["embedding_matches"] == ["e"]
    assert rows[0]["embedding_covered"] is True
    assert rows[0]["union_covered"] is True
    assert evaluator._marginal_group_counts(rows) == {
        "graph_over_adaptive": 0,
        "embedding_over_adaptive": 1,
        "embedding_over_adaptive_graph": 1,
    }
    assert evaluator._route_overlaps(routes) == {
        "adaptive_graph": 1,
        "adaptive_embedding": 1,
        "graph_embedding": 1,
        "all_three": 1,
    }


def test_multisignal_contract_fixes_independent_route_limits(
    evaluator: ModuleType,
) -> None:
    assert evaluator.COVERAGE_ALGORITHM == "bounded-reviewed-claim-multisignal-expansion-v2"
    assert evaluator.GRAPH_LIMITS == (8, 80)
    assert evaluator.EMBEDDING_LIMITS == (20, 240)
    assert evaluator.ROUTES == ("adaptive", "graph", "embedding", "union")


def test_runtime_tree_hash_ignores_interpreter_bytecode(
    evaluator: ModuleType,
    tmp_path: Path,
) -> None:
    (tmp_path / "SKILL.md").write_text("stable package\n", encoding="utf-8")
    before = evaluator._tree_sha(tmp_path)

    cache = tmp_path / "scripts" / "__pycache__"
    cache.mkdir(parents=True)
    (cache / "query.cpython-313.pyc").write_bytes(b"local bytecode")
    (tmp_path / "scripts" / "query.pyo").write_bytes(b"optimized bytecode")

    assert evaluator._tree_sha(tmp_path) == before


def _review_truth_row(number: int) -> dict[str, object]:
    claim = f"claim-paper-{number:03d}-001"
    return {
        "schema_version": "semantic-okf-hard-ground-truth/1.0",
        "id": f"q{number:03d}-case",
        "question": f"Question {number}?",
        "corpus_inventory": {"path": "inventory.json", "sha256": "a" * 64},
        "authoritative_evidence": [{"claim_id": claim}],
        "ground_truth": {
            "answer_claims": [
                {
                    "id": f"q{number:03d}-a1",
                    "statement": "A stable atomic statement.",
                    "evidence_claim_ids": [claim],
                }
            ],
            "important_negatives": [
                {
                    "id": f"q{number:03d}-n1",
                    "statement": "A stable negative statement.",
                    "evidence_claim_ids": [claim],
                }
            ],
            "required_paper_ids": [f"paper-{number:03d}"],
            "required_source_ids": [f"source-{number:03d}"],
            "derivation": [{"operation": "join", "inputs": [f"q{number:03d}-a1"], "conclusion": "Stable."}],
            "acceptable_variants": ["Stable wording."],
        },
    }


def test_reviewed_truth_may_only_append_or_equivalent_options(
    evaluator: ModuleType,
) -> None:
    parent = [_review_truth_row(number) for number in range(31, 41)]
    reviewed = json.loads(json.dumps(parent))
    reviewed[0]["authoritative_evidence"].append({"claim_id": "claim-paper-031-002"})
    reviewed[0]["ground_truth"]["answer_claims"][0]["evidence_claim_ids"].append(
        "claim-paper-031-002"
    )
    evaluator._validate_reviewed_truth(parent, reviewed)

    removed = json.loads(json.dumps(reviewed))
    removed[0]["ground_truth"]["answer_claims"][0]["evidence_claim_ids"] = [
        "claim-paper-031-002"
    ]
    with pytest.raises(evaluator.EvaluationError, match="not an option superset"):
        evaluator._validate_reviewed_truth(parent, removed)

    rewritten = json.loads(json.dumps(reviewed))
    rewritten[0]["ground_truth"]["answer_claims"][0]["statement"] = "Changed."
    with pytest.raises(evaluator.EvaluationError, match="changed answer_claims semantics"):
        evaluator._validate_reviewed_truth(parent, rewritten)


def test_markdown_exposes_semantic_route_and_provider_binding(
    evaluator: ModuleType,
) -> None:
    route_scores = {
        route: {"evidence_claim_recall": 1.0, "option_group_coverage": 1.0}
        for route in evaluator.ROUTES
    }
    count_stats = {
        route: {"mean": 1.0, "minimum": 1, "maximum": 1}
        for route in evaluator.ROUTES
    }
    overlap_stats = {
        overlap: {"mean": 1.0, "minimum": 1, "maximum": 1}
        for overlap in evaluator.OVERLAPS
    }
    report = {
        "status": "pass",
        "inputs": {
            "embedding_route": {
                "provider": "sentence-transformers",
                "model_id": "sentence-transformers/all-MiniLM-L6-v2",
                "revision": "1" * 40,
            }
        },
        "metrics": {
            "answer_claims": route_scores,
            "important_negatives": route_scores,
            "required_paper_coverage": {route: 1.0 for route in evaluator.ROUTES},
            "candidate_claims": count_stats,
            "candidate_overlaps": overlap_stats,
            "group_counts": {
                "answer_claims": {
                    "total": 1,
                    **{f"{route}_covered": 1 for route in evaluator.ROUTES},
                },
                "important_negatives": {
                    "total": 1,
                    **{f"{route}_covered": 1 for route in evaluator.ROUTES},
                },
            },
            "marginal_groups": {
                section: {
                    "graph_over_adaptive": 0,
                    "embedding_over_adaptive": 0,
                    "embedding_over_adaptive_graph": 0,
                }
                for section in ("answer_claims", "important_negatives")
            },
            "evidence_validation": {"unique_returned_bindings": 1},
        },
        "questions": [],
    }
    markdown = evaluator.render_markdown(report)
    assert "Pinned semantic claims" in markdown
    assert "adaptive∩embedding" in markdown
    assert "sentence-transformers/all-MiniLM-L6-v2" in markdown
    assert "embedding artifacts are hash-bound" in markdown
