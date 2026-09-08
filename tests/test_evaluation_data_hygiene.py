"""Exercise index-only data cleanup in a disposable public Git repository."""

from __future__ import annotations

import importlib.util
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("evaluation_hygiene_test", ROOT / "scripts/check_evaluation_data.py")
HYGIENE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(HYGIENE)


def test_index_migration_preserves_local_payload_and_reports(tmp_path):
    subprocess.run(["git", "init", "--quiet", str(tmp_path)], check=True)
    data = tmp_path / "evaluations/example/raw"
    data.mkdir(parents=True)
    payload = data / "source with spaces.jsonl"
    payload.write_bytes(b'{"text":"synthetic fixture"}\n')
    report = tmp_path / "evaluations/example/report.md"
    report.write_text("# Aggregate report\n", encoding="utf-8")
    subprocess.run(["git", "add", "evaluations"], cwd=tmp_path, check=True)
    (tmp_path / ".gitignore").write_text("evaluations/**/raw/\n", encoding="utf-8")
    paths = HYGIENE.tracked_ignored(tmp_path)
    assert paths == ["evaluations/example/raw/source with spaces.jsonl"]
    receipt = HYGIENE.untrack_payloads(paths, tmp_path)
    assert receipt["untracked_files"] == 1
    assert receipt["local_file_hashes_preserved"] is True
    assert payload.read_bytes() == b'{"text":"synthetic fixture"}\n'
    assert HYGIENE.tracked_ignored(tmp_path) == []
    tracked = subprocess.check_output(["git", "ls-files"], cwd=tmp_path, text=True)
    assert "report.md" in tracked
    assert "jsonl" not in tracked


def test_index_migration_rejects_scope_escape(tmp_path):
    with pytest.raises(ValueError, match="escapes"):
        HYGIENE.untrack_payloads(["outside.txt"], tmp_path)


def test_existing_receipt_rejects_before_any_index_operation(tmp_path, monkeypatch):
    import sys
    receipt = tmp_path / "receipt.json"
    receipt.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["check_evaluation_data.py", "--untrack", "--receipt", str(receipt)])
    monkeypatch.setattr(HYGIENE, "tracked_ignored", lambda: pytest.fail("index access occurred before receipt guard"))
    with pytest.raises(ValueError, match="receipt exists"):
        HYGIENE.main()


def test_repository_preserves_runtime_code_and_ignores_new_data():
    expected = ["evaluations/new-study/raw/doc.txt", "evaluations/new-study/bundle/concepts/a.md",
                "evaluations/new-study/questions.jsonl", "evaluations/new-study/corpus/sources/paper.md"]
    result = subprocess.run(["git", "check-ignore", "--no-index", "--stdin", "-z"], cwd=ROOT,
                            input=b"\0".join(path.encode() for path in expected) + b"\0", capture_output=True, check=False)
    assert result.stdout.decode().strip("\0").split("\0") == expected
    safe = ["evaluations/new-study/reports/comparison.md", "evaluations/new-study/reports/comparison.json",
            "evaluations/semantic-okf-harbor/runtime/pinned/Dockerfile",
            "evaluations/know/fixtures/command-planning/src/knowledge/cli.py",
            "evaluations/new-study/corpus/manifest.json"]
    result = subprocess.run(["git", "check-ignore", "--no-index", "--stdin", "-z"], cwd=ROOT,
                            input=b"\0".join(path.encode() for path in safe) + b"\0", capture_output=True, check=False)
    assert result.stdout == b""
