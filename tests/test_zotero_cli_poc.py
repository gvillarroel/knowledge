from __future__ import annotations

import json
from pathlib import Path

import pytest

from pocs.zotero_cli import run_poc


def test_capability_matrix_records_major_know_gaps() -> None:
    matrix = run_poc.capability_matrix("optional_dependency")
    by_capability = {entry["capability"]: entry["status"] for entry in matrix}

    assert by_capability["Bibliographic metadata and BibTeX"] == "covered"
    assert by_capability["PDF storage and indexed full text"] == "covered"
    assert by_capability["Notes and annotations"].startswith("partial:")
    assert by_capability["Exact corpus-wide PDF keyword discovery"].startswith("gap in CLI")
    assert by_capability["Semantic retrieval"] == "optional_dependency"
    assert by_capability["Recursive website crawling and CDP capture"] == "gap"
    assert by_capability["Video transcription"] == "gap"
    assert by_capability["Git repository and branch synchronization"] == "gap"
    assert by_capability["Confluence, Jira, and Aha synchronization"] == "gap"
    assert by_capability["Markdown/OKF library export and zip import"] == "gap"
    assert by_capability["Lossless Confluence Storage XML round trip"] == "gap"


def test_compact_normalizes_and_truncates_evidence() -> None:
    assert run_poc._compact("a\n  b\tc") == "a b c"
    assert run_poc._compact("abcdef", limit=5) == "abcd…"


@pytest.mark.parametrize(
    ("output", "expected"),
    [
        ("Item Key: PARENT", "covered"),
        (
            "Original search returned no results. Semantically related papers: PARENT",
            "partial",
        ),
        ("No items found", "gap"),
    ],
)
def test_classify_fulltext_discovery_distinguishes_semantic_fallback(
    output: str,
    expected: str,
) -> None:
    assert (
        run_poc._classify_fulltext_discovery(
            output,
            parent_key="PARENT",
            attachment_key="ATTACHMENT",
        )
        == expected
    )


def test_run_cli_requires_installed_executable(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(run_poc.shutil, "which", lambda _: None)

    with pytest.raises(run_poc.PocFailure, match="zotero-cli is not installed"):
        run_poc.run_cli(["search", "test"])


def test_zotero_mcp_version_requires_installed_executable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(run_poc.shutil, "which", lambda _: None)

    with pytest.raises(run_poc.PocFailure, match="zotero-mcp is not installed"):
        run_poc.zotero_mcp_version()


def test_find_top_item_matches_exact_title(monkeypatch: pytest.MonkeyPatch) -> None:
    expected = {"data": {"key": "ABC123", "title": run_poc.FIXTURE_TITLE}}
    monkeypatch.setattr(
        run_poc,
        "_get_json",
        lambda *_: ([{"data": {"key": "NOPE", "title": "Other"}}, expected], {}),
    )

    assert run_poc._find_top_item("http://localhost", run_poc.FIXTURE_TITLE) == expected


def test_find_top_item_returns_none_for_missing_exact_title(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        run_poc,
        "_get_json",
        lambda *_: ([{"data": {"key": "NOPE", "title": "Partial title"}}], {}),
    )

    assert run_poc._find_top_item("http://localhost", run_poc.FIXTURE_TITLE) is None


def test_main_writes_report_and_returns_success(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    report = {
        "generated_at": "2026-07-12T00:00:00+00:00",
        "required_failures": [],
    }
    monkeypatch.setattr(run_poc, "run", lambda *_args, **_kwargs: report)
    output = tmp_path / "report.json"

    assert run_poc.main(["--output", str(output)]) == 0
    assert json.loads(output.read_text(encoding="utf-8")) == report


def test_main_returns_failure_for_poc_error(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    def fail(*_args, **_kwargs):
        raise run_poc.PocFailure("not ready")

    monkeypatch.setattr(run_poc, "run", fail)

    assert run_poc.main([]) == 2
    assert "POC failed: not ready" in capsys.readouterr().err
