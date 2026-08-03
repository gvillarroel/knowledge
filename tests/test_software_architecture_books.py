from __future__ import annotations

import importlib.util
import hashlib
import json
from pathlib import Path
import sys
from types import ModuleType

import pytest


ROOT = Path(__file__).resolve().parents[1]
STUDY = ROOT / "evaluations" / "software-architecture-books"


def load_module(name: str, relative: str) -> ModuleType:
    path = STUDY / relative
    specification = importlib.util.spec_from_file_location(name, path)
    assert specification is not None
    assert specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


PREPARE = load_module(
    "test_software_books_prepare",
    "scripts/prepare_corpus.py",
)
FREEZE = load_module(
    "test_software_books_freeze",
    "scripts/freeze_benchmark.py",
)
EVALUATE = load_module(
    "test_software_books_evaluate",
    "scripts/evaluate_retrieval.py",
)
DRILLDOWN = load_module(
    "test_software_books_drilldown",
    "scripts/evaluate_evidence_drilldown.py",
)


def load_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def test_selection_contract_is_closed_and_totals_match() -> None:
    selection = PREPARE.load_selection()
    books = selection["books"]

    assert len(books) == 18
    assert sum(row["expected_pages"] for row in books) == 6170
    assert sum(row["expected_bytes"] for row in books) == 133_882_359
    assert [row["slug"] for row in books] == sorted(
        row["slug"] for row in books
    )
    assert all(len(row["pdf_sha256"]) == 64 for row in books)


def test_watermark_normalization_is_narrow_and_preserves_source_text() -> None:
    value = (
        "Useful architecture evidence\r\n"
        "Humble Bundle Pearson Software Development – © Pearson. "
        "Do Not Distribute.\r\n"
        "More evidence"
    )

    assert PREPARE.normalize_page_text(value) == (
        "Useful architecture evidence\n\nMore evidence"
    )
    assert PREPARE.normalize_page_text("Do Not Distribute is a topic") == (
        "Do Not Distribute is a topic"
    )


def test_page_span_returns_exact_trimmed_page() -> None:
    text = (
        "frontmatter\n\n"
        "## PDF page 1\n\nfirst page\n\n"
        "## PDF page 2\n\nsecond page\n\n"
    )

    start, end, passage = FREEZE.page_span(text, 2)

    assert text[start:end] == passage
    assert passage == "## PDF page 2\n\nsecond page"
    with pytest.raises(FREEZE.FreezeError):
        FREEZE.page_span(text, 3)


def test_question_qrels_and_source_combination_are_coherent() -> None:
    questions = EVALUATE.load_questions(
        STUDY / "benchmark" / "retrieval-questions.jsonl"
    )
    manifest = load_json(STUDY / "manifest.json")
    plan = load_json(STUDY / "plans" / "classical-plan.json")
    combination = load_json(STUDY / "source-combination.json")

    manifest_sources = sorted(row["id"] for row in manifest["sources"])
    assert len(questions) == 40
    assert sum(row["question_type"] == "hard" for row in questions) == 10
    assert manifest_sources == plan["selection"]["source_ids"]
    assert manifest_sources == sorted(
        row["source_id"] for row in combination["records"]
    )
    assert {
        document
        for question in questions
        for document in question["document_ids"]
    } == {row["document_id"] for row in combination["records"]}


def test_evaluation_contract_pins_every_ranking_input() -> None:
    contract = load_json(
        STUDY / "benchmark" / "evaluation-contract.json"
    )["frozen_inputs"]
    paths = {
        "source_manifest_sha256": STUDY / "manifest.json",
        "source_combination_sha256": STUDY / "source-combination.json",
        "classical_plan_file_sha256": STUDY
        / "plans"
        / "classical-plan.json",
        "questions_sha256": STUDY
        / "benchmark"
        / "retrieval-questions.jsonl",
        "hard_ground_truth_sha256": STUDY
        / "benchmark"
        / "hard-ground-truth.jsonl",
    }

    assert {
        name: hashlib.sha256(path.read_bytes()).hexdigest()
        for name, path in paths.items()
    } == contract


def test_retrieval_metrics_ignore_duplicate_pages_from_one_book() -> None:
    results = [
        {"rank": 1, "source_id": "book-a"},
        {"rank": 2, "source_id": "book-a"},
        {"rank": 3, "source_id": "book-b"},
        {"rank": 4, "source_id": "book-c"},
    ]

    metrics = EVALUATE.retrieval_metrics(
        results,
        ["book-a", "book-b"],
        4,
    )

    assert metrics["recall@4"] == 1.0
    assert metrics["mrr@4"] == 1.0
    assert metrics["full_qrel_coverage@4"] == 1.0
    assert metrics["source_precision@4"] == pytest.approx(2 / 3)
    assert 0.0 < metrics["ndcg@4"] < 1.0


def test_exact_evidence_metrics_use_source_and_text_identity() -> None:
    results = [
        {
            "rank": 1,
            "source_id": "book-a",
            "text_sha256": "a" * 64,
        },
        {
            "rank": 2,
            "source_id": "book-b",
            "text_sha256": "b" * 64,
        },
    ]
    reviewed = [
        {"source_id": "book-a", "text_sha256": "a" * 64},
        {"source_id": "book-b", "text_sha256": "c" * 64},
    ]

    metrics = EVALUATE.exact_evidence_metrics(results, reviewed, 2)

    assert metrics["reviewed_locator_recall@2"] == 0.5
    assert metrics["full_reviewed_locator_coverage@2"] == 0.0


def test_frozen_hard_truth_contains_hash_only_private_evidence() -> None:
    questions = EVALUATE.load_questions(
        STUDY / "benchmark" / "retrieval-questions.jsonl"
    )
    hard_ids = {
        row["id"] for row in questions if row["question_type"] == "hard"
    }
    truth = EVALUATE.load_hard_truth(
        STUDY / "benchmark" / "hard-ground-truth.jsonl",
        hard_ids,
    )
    raw_rows = FREEZE.load_jsonl(
        STUDY / "benchmark" / "hard-ground-truth.jsonl"
    )

    assert len(truth) == 10
    assert sum(len(rows) for rows in truth.values()) == 28
    for row in raw_rows:
        for evidence in row["authoritative_evidence"]:
            assert "text" not in evidence
            assert "excerpt" not in evidence
            assert evidence["path"].startswith(
                "evaluations/software-architecture-books/processed/"
            )
            assert len(evidence["file_sha256"]) == 64
            assert len(evidence["text_sha256"]) == 64


def test_metric_report_header_uses_requested_cutoff() -> None:
    report = {
        "top_k": 4,
        "ranking": [
            {
                "mode": "bm25",
                "recall@4": 1.0,
                "ndcg@4": 0.8,
                "full_qrel_coverage@4": 0.75,
                "reviewed_locator_recall@4": 0.5,
                "p95_latency_ms": 12.3,
            }
        ],
    }

    rendered = EVALUATE.render_markdown(report)

    assert "Recall@4" in rendered
    assert "nDCG@4" in rendered
    assert "Recall@10" not in rendered


def test_drilldown_evidence_score_requires_exact_source_and_page_hash() -> None:
    pages = [
        {"source_id": "book-a", "text_sha256": "a" * 64},
        {"source_id": "book-b", "text_sha256": "b" * 64},
    ]
    reviewed = [
        {"source_id": "book-a", "text_sha256": "a" * 64},
        {"source_id": "book-b", "text_sha256": "c" * 64},
    ]

    recall, complete, matches = DRILLDOWN.evidence_score(pages, reviewed)

    assert recall == 0.5
    assert complete == 0.0
    assert matches == 1


def test_harbor_summary_records_both_isolated_modes() -> None:
    summary = load_json(
        STUDY / "reports" / "harbor-rehearsal-summary.json"
    )

    assert summary["status"] == "pass"
    assert sum(
        row["oracle_mechanical_qualification_gates"]
        for row in summary["modes"]
    ) == 80
    by_mode = {row["mode"]: row for row in summary["modes"]}
    assert by_mode["build-consult"]["raw_sources_mounted"] is True
    assert by_mode["build-consult"]["prebuilt_knowledge_mounted"] is False
    assert by_mode["consult-only"]["raw_sources_mounted"] is False
    assert by_mode["consult-only"]["prebuilt_knowledge_mounted"] is True
