"""Focused tests for the frozen Astro q040 manual consultation check."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
EVALUATION = REPO / "evaluations" / "semantic-okf-astro"
SCRIPT = EVALUATION / "scripts" / "manual_query_verification.py"


def load_runtime():
    """Load the real script so tests exercise its actual report boundary."""

    name = "astro_manual_query_test_runtime"
    specification = importlib.util.spec_from_file_location(name, SCRIPT)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


RUNTIME = load_runtime()


def hit(*, document: str, retrieval: str, score: float = 1.0):
    """Build a normalized exact-evidence fixture."""

    text = f"Authoritative text for {document}."
    return RUNTIME.RETRIEVAL.Hit(
        source_id=f"source-{document}",
        record_id=f"record-{document}",
        document_id=document,
        record_sha256="a" * 64,
        concept_id=f"concept-{document}",
        concept_path=f"concepts/{document}.md",
        source_path=f"sources/{document}.mdx",
        locator={"kind": "character-range", "start": 0, "end": len(text)},
        text=text,
        text_sha256=RUNTIME.RETRIEVAL.sha256_bytes(text.encode("utf-8")),
        score=score,
        retrieval_id=retrieval,
        record_sha256_provenance="test",
    )


def question():
    """Return one small hard-question fixture."""

    return RUNTIME.RETRIEVAL.Question(
        "q040",
        "hard",
        "How should the route be configured?",
        ("doc-a", "doc-b"),
        ("source-doc-a", "source-doc-b"),
    )


class ValidLedger:
    """Accept exact evidence for control-flow tests."""

    @staticmethod
    def validate(_hit):
        return {"valid": True, "issues": []}


def test_signatures_separate_ordered_ranking_from_evidence() -> None:
    """Score changes affect ranking identity without changing evidence identity."""

    original = [hit(document="doc-a", retrieval="a", score=1.0)]
    rescored = [hit(document="doc-a", retrieval="a", score=0.5)]
    reordered = [
        hit(document="doc-b", retrieval="b"),
        hit(document="doc-a", retrieval="a"),
    ]
    assert RUNTIME.signature(original, evidence=False) != RUNTIME.signature(
        rescored, evidence=False
    )
    assert RUNTIME.signature(original, evidence=True) == RUNTIME.signature(
        rescored, evidence=True
    )
    assert RUNTIME.signature(reordered, evidence=True) != RUNTIME.signature(
        list(reversed(reordered)), evidence=True
    )


def test_verify_family_runs_twice_and_enforces_read_only_bundle(tmp_path: Path) -> None:
    """A stable result passes all independent determinism and mutation gates."""

    (tmp_path / "published.json").write_text("{}\n", encoding="utf-8")
    calls: list[str] = []
    values = [hit(document="doc-a", retrieval="a"), hit(document="doc-b", retrieval="b")]

    def search(query_text: str):
        calls.append(query_text)
        return values

    result = RUNTIME.verify_family(
        "legacy", "legacy_tfidf", question(), tmp_path, ValidLedger(), search
    )
    assert calls == [question().text, question().text]
    assert result["status"] == "pass"
    assert result["run_count"] == 2
    assert result["ranking_deterministic"] is True
    assert result["evidence_deterministic"] is True
    assert result["all_evidence_valid"] is True
    assert result["bundle_unchanged"] is True
    assert result["runs"][0]["required_document_recall_at_10"] == 1.0
    assert result["answer_pack"]["answer"]["document_ids"] == ["doc-a", "doc-b"]


def test_verify_family_fails_when_only_the_ranking_changes(tmp_path: Path) -> None:
    """Repeated evidence is insufficient if route scores are not deterministic."""

    (tmp_path / "published.json").write_text("{}\n", encoding="utf-8")
    calls = 0

    def search(_query_text: str):
        nonlocal calls
        calls += 1
        return [hit(document="doc-a", retrieval="a", score=1.0 / calls)]

    result = RUNTIME.verify_family(
        "legacy", "legacy_tfidf", question(), tmp_path, ValidLedger(), search
    )
    assert result["status"] == "fail"
    assert result["ranking_deterministic"] is False
    assert result["evidence_deterministic"] is True
    assert result["bundle_unchanged"] is True


def test_route_selection_is_bound_to_the_passing_retrieval_report() -> None:
    """Manual verification cannot silently choose a friendlier route."""

    selected = RUNTIME.strict_selected_routes(
        EVALUATION / "reports" / "retrieval-comparison.json"
    )
    assert selected == {
        "legacy": "legacy_tfidf",
        "embeddings": "lexical",
        "classical": "association",
        "adaptive": "association",
        "entity-graph": "entity",
        "ensemble": "quality",
    }


def test_checked_manual_report_passes_every_gate() -> None:
    """The compact checked artifact must retain all six double-run results."""

    report = json.loads(
        (EVALUATION / "reports" / "manual-query-verification.json").read_text(
            encoding="utf-8"
        )
    )
    assert report["schema_version"] == RUNTIME.SCHEMA
    assert report["status"] == "pass"
    assert report["question"]["id"] == "q040"
    assert report["execution_contract"]["mcp_dependency"] is False
    assert len(report["families"]) == 6
    assert {row["family"]: row["route"] for row in report["families"]} == RUNTIME.SELECTED_ROUTES
    for family in report["families"]:
        assert family["status"] == "pass"
        assert family["run_count"] == 2
        assert family["ranking_deterministic"] is True
        assert family["evidence_deterministic"] is True
        assert family["all_evidence_valid"] is True
        assert family["bundle_unchanged"] is True
        assert family["bundle_identity_before"] == family["bundle_identity_after"]
        assert len(family["runs"]) == 2
        assert all(run["invalid_evidence"] == 0 for run in family["runs"])
        assert family["answer_pack"]["answer"] is not None


def test_manual_script_contains_no_mcp_runtime_import() -> None:
    """The local verifier may record the boundary but cannot start an MCP runtime."""

    source = SCRIPT.read_text(encoding="utf-8").casefold()
    forbidden = ("import mcp", "from mcp", "fastmcp", "mcp_server", "mcp-server")
    assert not any(token in source for token in forbidden)
