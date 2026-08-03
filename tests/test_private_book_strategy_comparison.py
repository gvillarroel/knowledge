from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PREPARE_PATH = (
    ROOT
    / "evaluations"
    / "private-book-strategy-comparison"
    / "scripts"
    / "prepare_strategy_bundles.py"
)
EVALUATE_PATH = (
    ROOT
    / "evaluations"
    / "private-book-strategy-comparison"
    / "scripts"
    / "evaluate_all_routes.py"
)
QUESTIONS = (
    ROOT
    / "evaluations"
    / "data-science-ai-ml-books"
    / "benchmark"
    / "retrieval-questions.jsonl"
)
ARCHITECTURE_QUESTIONS = (
    ROOT
    / "evaluations"
    / "software-architecture-books"
    / "benchmark"
    / "retrieval-questions.jsonl"
)
CONTRACTS = (
    ROOT
    / "evaluations"
    / "software-architecture-books"
    / "benchmark"
    / "all-route-evaluation-contract.json",
    ROOT
    / "evaluations"
    / "data-science-ai-ml-books"
    / "benchmark"
    / "evaluation-contract.json",
)


def _load(name: str, path: Path):
    specification = importlib.util.spec_from_file_location(name, path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


PREPARE = _load("test_private_book_prepare", PREPARE_PATH)
EVALUATE = _load("test_private_book_evaluate", EVALUATE_PATH)


def test_data_science_book_questions_are_complete_and_cover_every_record() -> None:
    questions = EVALUATE.load_questions(QUESTIONS)
    assert len(questions) == 40
    assert [row["cohort"] for row in questions].count("development") == 30
    assert [row["cohort"] for row in questions].count("hard") == 10

    covered = {
        record_id
        for question in questions
        for record_id in question["relevant"]
    }
    assert len(covered) == 38
    assert all(record_id.startswith("processed/markdown/") for record_id in covered)
    assert sum("/ai-ml/" in record_id for record_id in covered) == 18
    assert sum("/ds/" in record_id for record_id in covered) == 20


def test_architecture_questions_prefer_authoritative_source_ids() -> None:
    questions = EVALUATE.load_questions(ARCHITECTURE_QUESTIONS)
    assert len(questions) == 40
    assert questions[0]["relevant"] == ["book-architecture-for-flow"]


def test_generated_plans_select_every_manifest_source_without_question_data() -> None:
    selection = ["ai-ml-books", "ds-books"]
    plans = {
        "embeddings": PREPARE.embedding_plan(selection),
        "classical": PREPARE.classical_plan(selection),
        "adaptive": PREPARE.adaptive_plan(selection),
        "entity": PREPARE.entity_graph_plan(selection),
        "ensemble": PREPARE.ensemble_plan(selection),
    }
    assert plans["embeddings"]["embedding"]["provider"] == "hashing"
    assert plans["embeddings"]["chunking"]["strategy"] == "record"
    assert plans["classical"]["topics"]["topic_count"] == 24
    assert plans["adaptive"]["topics"]["topic_count"] == 24
    assert plans["adaptive"]["passages"]["markdown_pdf_page_source_ids"] == []
    assert plans["ensemble"]["identity"] == {
        "default_grouping": "source-record-v1",
        "overrides": [],
    }
    assert plans["ensemble"]["quality_gates"]["require_core_parity"] is True
    for plan in plans.values():
        rendered = json.dumps(plan, sort_keys=True)
        assert "q001" not in rendered
        assert "question" not in rendered


def test_metrics_are_duplicate_safe_and_reward_complete_rankings() -> None:
    hits = [
        {"rank": 1, "record_id": "book-a"},
        {"rank": 2, "record_id": "book-b"},
    ]
    measured = EVALUATE.metrics(hits, ["book-a", "book-b"])
    assert measured == {
        "recall_at_10": 1.0,
        "mrr_at_10": 1.0,
        "ndcg_at_10": 1.0,
        "full_qrel_coverage_at_10": 1.0,
    }


def test_payload_results_accepts_every_registered_runtime_shape() -> None:
    row = {"record_id": "record-a"}
    for key in ("results", "records", "hits"):
        assert EVALUATE.payload_results({key: [row]}) == [row]


def test_qrels_resolve_record_ids_and_unambiguous_source_ids() -> None:
    authoritative = {
        "record-a": {"source_id": "source-a"},
        "record-b": {"source_id": "source-b"},
    }
    questions = [
        {
            "id": "q001-example",
            "question": "Example?",
            "cohort": "development",
            "relevant": ["record-a", "source-b"],
        }
    ]
    resolved = EVALUATE.resolve_qrels(questions, authoritative)
    assert resolved[0]["relevant"] == ["record-a", "record-b"]


def test_module_loader_replaces_conflicting_vendored_module(tmp_path: Path) -> None:
    first = tmp_path / "first.py"
    second = tmp_path / "second.py"
    first.write_text("VALUE = 'first'\n", encoding="utf-8")
    second.write_text("VALUE = 'second'\n", encoding="utf-8")
    assert EVALUATE.load_module("_test_vendored_runtime", first).VALUE == "first"
    assert EVALUATE.load_module("_test_vendored_runtime", second).VALUE == "second"
    assert sys.modules["_test_vendored_runtime"].VALUE == "second"


def test_route_inventory_covers_all_registered_families() -> None:
    assert len(EVALUATE.ROUTE_LABELS) == 18
    assert {family for family, _ in EVALUATE.ROUTE_LABELS.values()} == {
        "Legacy",
        "Embeddings",
        "Classical",
        "Adaptive",
        "Entity Graph",
        "Ensemble",
        "Graphify",
        "Turso",
    }
    for path in CONTRACTS:
        contract = json.loads(path.read_text(encoding="utf-8"))
        assert set(contract["candidate_policy"]["routes"]) == set(
            EVALUATE.ROUTE_LABELS
        )
