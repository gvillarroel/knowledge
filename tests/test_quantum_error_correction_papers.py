"""Tests for the frozen quantum-error-correction transfer benchmark."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unicodedata


REPO = Path(__file__).resolve().parents[1]
ROOT = REPO / "evaluations" / "quantum-error-correction-papers"
GENERATOR = ROOT / "scripts" / "generate_benchmark.py"
EVALUATOR = ROOT / "scripts" / "evaluate_expert_retrieval.py"
NATIVE_SMOKE = ROOT / "scripts" / "validate_native_harbor_retrieval.py"
NATIVE_SCORER = (
    REPO
    / "evaluations"
    / "semantic-okf-specialized-experts"
    / "harbor"
    / "grader"
    / "score.py"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _jsonl(path: Path) -> list[dict[str, object]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def test_qec_source_inventory_is_complete_hashed_and_nfc() -> None:
    """Every exact PDF and derived Markdown source matches the frozen inventory."""

    selection = json.loads(
        (ROOT / "paper-selection.json").read_text(encoding="utf-8")
    )
    inventory = json.loads(
        (ROOT / "sources" / "inventory.json").read_text(encoding="utf-8")
    )
    selected = [row["arxiv_id"] for row in selection["papers"]]

    assert selection["dataset_id"] == "quantum-error-correction-papers-40"
    assert inventory["dataset_id"] == selection["dataset_id"]
    assert selected == sorted(set(selected))
    assert len(selected) == inventory["paper_count"] == 15
    assert [row["arxiv_id"] for row in inventory["papers"]] == selected

    for row in inventory["papers"]:
        pdf = ROOT / "sources" / row["pdf_path"]
        markdown = ROOT / "sources" / row["markdown_path"]
        text = markdown.read_text(encoding="utf-8")
        assert pdf.read_bytes().startswith(b"%PDF")
        assert _sha256(pdf) == row["pdf_sha256"]
        assert _sha256(markdown) == row["markdown_sha256"]
        assert unicodedata.is_normalized("NFC", text)
        assert text.count("## PDF page ") == row["page_count"]


def test_qec_benchmark_regenerates_and_hard_spans_join_the_ledger() -> None:
    """Derived contracts are stable and every hard source span maps exactly."""

    checked = subprocess.run(
        [sys.executable, str(GENERATOR), "--check"],
        cwd=REPO,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    assert checked.returncode == 0, checked.stderr
    assert json.loads(checked.stdout)["status"] == "pass"

    questions = _jsonl(ROOT / "benchmark" / "retrieval-questions.jsonl")
    truths = _jsonl(ROOT / "benchmark" / "hard-ground-truth.jsonl")
    records = _jsonl(ROOT / "bundle" / "semantic" / "records.jsonl")
    by_source = {row["source_id"]: row for row in records}
    assert len(questions) == 40
    assert len(truths) == 10
    assert len(by_source) == 15

    for truth in truths:
        for authority in truth["authoritative_evidence"]:
            source_id = f"paper-{authority['paper_id'].replace('.', '-', 1)}"
            for evidence in authority["paper_evidence"]:
                source = REPO / evidence["path"]
                text = source.read_text(encoding="utf-8-sig")
                selected = text[evidence["char_start"] : evidence["char_end"]]
                assert hashlib.sha256(
                    selected.encode("utf-8")
                ).hexdigest() == evidence["text_sha256"]
                body = by_source[source_id]["body"]
                assert body.count(selected) == 1


def test_qec_retrospective_report_records_perfect_three_replicate_result() -> None:
    """The tracked result remains explicit, complete, and promotion-ineligible."""

    report = json.loads(
        (
            ROOT
            / "reports"
            / "retrospective-supervised-expert-evaluation.json"
        ).read_text(encoding="utf-8")
    )
    candidate = report["candidate"]
    assert report["status"] == "pass"
    assert report["dataset_id"] == "quantum-error-correction-papers-40"
    assert report["promotion_eligible"] is False
    assert len(candidate["replicates"]) == 3
    assert candidate["aggregate"]["metrics"]["recall_at_10"] == 1.0
    assert candidate["aggregate"]["metrics"]["mrr_at_10"] == 1.0
    assert candidate["aggregate"]["metrics"]["ndcg_at_10"] == 1.0
    assert candidate["aggregate"]["evidence"]["ratio"] == 1.0
    assert all(
        route["paper_metrics"]["recall_at_10"] == 1.0
        and route["paper_metrics"]["mrr_at_10"] == 1.0
        and route["paper_metrics"]["ndcg_at_10"] == 1.0
        and route["evidence_validity"]["ratio"] == 1.0
        for route in candidate["replicates"]
    )
    winner = min(report["leaderboard"], key=lambda row: row["rank"])
    assert winner["treatment"] == "retrospective-supervised-ngram"
    assert report["inputs"]["questions"]["sha256"] == _sha256(
        ROOT / "benchmark" / "retrieval-questions.jsonl"
    )
    assert report["inputs"]["evaluator"]["sha256"] == _sha256(EVALUATOR)


def test_qec_evaluator_accepts_four_and_five_digit_arxiv_numbers() -> None:
    """Old and new arXiv identifier widths share one exact identity contract."""

    specification = importlib.util.spec_from_file_location(
        "qec_evaluator_contract",
        EVALUATOR,
    )
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)

    assert module._paper_id("paper-1208-0928v2") == "1208.0928v2"
    assert module._paper_id("paper-2508-05095v3") == "2508.05095v3"


def test_qec_candidate_passes_representative_native_harbor_grading() -> None:
    """A development and hard case pass the exact native retrieval contract."""

    report = json.loads(
        (ROOT / "reports" / "native-harbor-retrieval-smoke.json").read_text(
            encoding="utf-8"
        )
    )
    assert report["status"] == "pass"
    assert report["dataset_id"] == "quantum-error-correction-papers-40"
    assert report["promotion_eligible"] is False
    assert report["all_qrels_exposed"] is True
    assert report["case_count"] == 2
    assert {row["question_type"] for row in report["cases"]} == {
        "cross-paper",
        "hard",
    }
    assert all(
        row["diagnostics_status"] == "scored-retrieval"
        and set(row["rewards"].values()) == {1.0}
        for row in report["cases"]
    )
    assert report["questions"]["sha256"] == _sha256(
        ROOT / "benchmark" / "retrieval-questions.jsonl"
    )
    assert report["native_harbor_scorer"]["sha256"] == _sha256(NATIVE_SCORER)
    assert NATIVE_SMOKE.is_file()
