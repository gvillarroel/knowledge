from __future__ import annotations

from argparse import Namespace
from pathlib import Path

from knowledge.browse_commands import _repo_name_from_selected_row, cmd_browse_github_activity


def test_repo_name_from_selected_row_strips_marker_and_ansi() -> None:
    row = "\033[32m●\033[0m owner/myrepo | Example repo | \033[2m★10 Python\033[0m"

    assert _repo_name_from_selected_row(row) == "owner/myrepo"


def test_browse_github_activity_accepts_selected_row(tmp_path: Path, monkeypatch) -> None:
    calls: list[tuple[str, str, int]] = []

    monkeypatch.setenv("GITHUB_TOKEN", "token")

    def fake_list_repo_activity(token: str, owner: str, repo: str, per_page: int = 30) -> list[dict[str, object]]:
        calls.append((owner, repo, per_page))
        assert token == "token"
        return [{"kind": "issue", "number": 10, "title": "Test", "user": "octocat", "comments_count": 1}]

    monkeypatch.setattr("knowledge.sources.github_api.list_repo_activity", fake_list_repo_activity)

    result = cmd_browse_github_activity(
        Namespace(
            store=tmp_path,
            format="json",
            entry=None,
            repo=None,
            selected_row="\033[36m○\033[0m owner/myrepo | Example repo | \033[2m★10 Python\033[0m",
        )
    )

    assert result["repo"] == "owner/myrepo"
    assert calls == [("owner", "myrepo", 30)]


def test_bundled_tv_cables_use_expected_commands() -> None:
    github_cable = Path("cables/know-github-view.toml").read_text(encoding="utf-8")
    arxiv_cable = Path("cables/know-arxiv.toml").read_text(encoding="utf-8")
    brave_cable = Path("cables/know-brave.toml").read_text(encoding="utf-8")
    follow_cable = Path("cables/know-follow.toml").read_text(encoding="utf-8")

    assert "sed " not in github_cable
    assert "$(" not in github_cable
    assert "--selected-row '{}'" in github_cable
    assert 'know search arxiv \\"all:$SEARCH\\" --format television-preview' in arxiv_cable
    assert 'know search brave \\"$SEARCH\\" --format television --count 20' in brave_cable
    assert 'know search brave \\"$SEARCH\\" --format television-preview --count 20 --entry \'{}\'' in brave_cable
    assert "preview_size = 70" in follow_cable
    assert "preview_word_wrap = true" in follow_cable
    assert "bat --language=markdown" in follow_cable
    assert 'know browse follow-url' in follow_cable
    assert 'powershell -NoProfile -Command' in follow_cable
    assert 'start `$url' in follow_cable
