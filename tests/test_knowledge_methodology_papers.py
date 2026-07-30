"""Tests for the paper-grounded knowledge-methodology review package."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import unicodedata


REPO = Path(__file__).resolve().parents[1]
ROOT = REPO / "evaluations" / "knowledge-methodology-papers"
SKILL = REPO / "skills" / "review-knowledge-methodology"
AGENT = REPO / "agents" / "knowledge-methodology-reviewer"


def _run(*arguments: object) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *map(str, arguments)],
        cwd=REPO,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_methodology_corpus_inventory_is_complete_pinned_and_nfc() -> None:
    """All 47 papers retain exact identities and immutable source bindings."""

    selection = json.loads(
        (ROOT / "paper-selection.json").read_text(encoding="utf-8")
    )
    inventory = json.loads(
        (ROOT / "sources" / "inventory.json").read_text(encoding="utf-8")
    )
    assert selection["dataset_id"] == "knowledge-methodology-papers-47"
    assert inventory["dataset_id"] == selection["dataset_id"]
    assert inventory["paper_count"] == 47
    assert inventory["new_paper_count"] == 32
    assert inventory["reused_paper_count"] == 15
    assert len(selection["selection_policy"]["coverage_lanes"]) == 8

    identities = [row["arxiv_id"] for row in inventory["papers"]]
    assert identities == sorted(set(identities))
    for row in inventory["papers"]:
        markdown = ROOT / "sources" / row["markdown_path"]
        text = markdown.read_text(encoding="utf-8")
        assert _sha256(markdown) == row["markdown_sha256"]
        assert unicodedata.is_normalized("NFC", text)
        assert f'paper_id: "{row["arxiv_id"]}"' in text
        if row["source_group"] == "new-methodology-papers":
            pdf = ROOT / "sources" / row["pdf_path"]
            assert pdf.read_bytes().startswith(b"%PDF")
            assert _sha256(pdf) == row["pdf_sha256"]
            assert text.count("## PDF page ") == row["page_count"]


def test_dataset_manifest_snapshot_and_audit_validate() -> None:
    """The complete source, Semantic OKF, and audit graph passes its validator."""

    manifest_check = _run(ROOT / "scripts" / "generate_manifest.py", "--check")
    assert manifest_check.returncode == 0, manifest_check.stderr
    assert json.loads(manifest_check.stdout)["source_count"] == 47

    validated = _run(ROOT / "scripts" / "validate_dataset.py")
    assert validated.returncode == 0, validated.stderr
    report = json.loads(validated.stdout)
    assert report == {
        "audit_recommendation_count": 11,
        "coverage_lane_count": 8,
        "dataset_id": "knowledge-methodology-papers-47",
        "manifest_source_count": 47,
        "paper_count": 47,
        "status": "pass",
    }

    build_report = json.loads(
        (ROOT / "bundle" / "semantic" / "build-report.json").read_text(
            encoding="utf-8"
        )
    )
    assert build_report["status"] == "pass"
    assert build_report["valid"] is True
    assert build_report["summary"]["records"] == 47
    assert build_report["summary"]["shacl"] == "conformant"


def test_standalone_methodology_expert_is_bound_and_retrieves_evidence() -> None:
    """The only agent skill verifies and returns exact paper identities."""

    query = SKILL / "scripts" / "query_expert_knowledge.py"
    verified = _run(query, "verify")
    assert verified.returncode == 0, verified.stderr
    assert json.loads(verified.stdout)["record_count"] == 47

    searched = _run(
        query,
        "search",
        "--contains",
        "holdout adaptive contamination",
    )
    assert searched.returncode == 0, searched.stderr
    results = json.loads(searched.stdout)["results"]
    returned = {row["source_id"] for row in results}
    assert "paper-1506-02629v2" in returned
    assert "paper-2406-04244v1" in returned


def test_reviewer_agent_has_one_skill_and_read_only_authority() -> None:
    """The local reviewer cannot load unrelated skills or mutate the repository."""

    manifest = json.loads(
        (AGENT / "agent.json").read_text(encoding="utf-8")
    )
    assert manifest["default_skills"] == ["review-knowledge-methodology"]
    assert manifest["allowed_skills"] == ["review-knowledge-methodology"]
    assert manifest["authority"] == {
        "mode": "read-only-review",
        "may_modify_repository": False,
        "may_acquire_external_sources": False,
    }

    validated = _run(ROOT / "scripts" / "validate_agent.py")
    assert validated.returncode == 0, validated.stderr
    assert json.loads(validated.stdout)["status"] == "pass"


def test_audit_citations_resolve_to_embedded_pdf_pages() -> None:
    """Every machine-readable paper citation names an existing embedded page."""

    audit = json.loads(
        (
            ROOT
            / "reports"
            / "repository-methodology-audit-20260729.json"
        ).read_text(encoding="utf-8")
    )
    assert audit["status"] == "complete"
    assert {row["priority"] for row in audit["recommendations"]} == {
        "P0",
        "P1",
        "P2",
    }
    assert len(audit["recommendations"]) == 11

    knowledge = SKILL / "references" / "knowledge"
    for recommendation in audit["recommendations"]:
        assert recommendation["validation"]
        assert recommendation["confidence"]
        for citation in recommendation["evidence"]:
            concept = knowledge / citation["concept_path"]
            text = concept.read_text(encoding="utf-8")
            assert citation["paper_id"] in text
            for page in citation["pdf_pages"]:
                assert f"## PDF page {page}\n" in text
