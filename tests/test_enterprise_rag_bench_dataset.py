"""Small public fixtures exercise the EnterpriseRAG adapter without downloaded data."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import stat
import sys
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("enterprise_dataset_test", ROOT / "evaluations/enterprise-rag-bench/dataset_tool.py")
DATA = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = DATA
SPEC.loader.exec_module(DATA)


def identity(index: int) -> str:
    return "dsid_" + f"{index:032x}"


@pytest.fixture
def corpus(tmp_path: Path) -> tuple[Path, dict]:
    raw = tmp_path / "raw"
    raw.mkdir()
    license_bytes = b"Synthetic public test fixture license.\n"
    (raw / "LICENSE").write_bytes(license_bytes)
    questions = [{"question_id": f"question-{i}", "question_type": category,
                  "question": f"Evaluator prompt {i}", "expected_doc_ids": [identity(i * 3)],
                  "gold_answer": f"PRIVATE GOLD {i}", "answer_facts": [f"PRIVATE FACT {i}"]}
                 for i, category in enumerate(("basic", "semantic"))]
    (raw / "questions.jsonl").write_text("\n".join(json.dumps(row) for row in questions), encoding="utf-8")
    with zipfile.ZipFile(raw / "all_documents.zip", "w") as archive:
        for i in range(6):
            source = "slack" if i < 3 else "gmail"
            archive.writestr(f"{source}/{identity(i)}__document.txt", f"Document {i}\nOriginal evidence {i}.\n")
        archive.writestr("questions.jsonl", "THIS MUST NEVER ENTER THE BUILDER INPUT")
    descriptor = copy.deepcopy(DATA.read_descriptor())
    descriptor["upstream"].update({"question_count": 2, "document_count": 6, "unique_document_ids": 6,
                                   "ambiguous_document_ids": 0, "questions_sha256": DATA.sha256(raw / "questions.jsonl"),
                                   "license_sha256": hashlib.sha256(license_bytes).hexdigest()})
    descriptor["upstream"]["archive"]["sha256"] = DATA.sha256(raw / "all_documents.zip")
    descriptor["selection"].update({"categories": ["basic", "semantic"], "sources": ["gmail", "slack"],
                                    "questions_per_category": 1, "distractors_per_source": 1})
    return tmp_path, descriptor


def test_prepare_is_reproducible_and_evaluator_free(corpus):
    root, descriptor = corpus
    first = DATA.prepare(root, descriptor)
    assert first == DATA.prepare(root, descriptor, check=True)
    assert first["question_count"] == 2
    assert first["document_count"] == 4
    assert first["distractor_count"] == 2
    folder = root / "processed" / descriptor["dataset_id"]
    public = "\n".join(path.read_text(encoding="utf-8") for path in (folder / "input").rglob("*") if path.is_file())
    assert "PRIVATE GOLD" not in public
    assert "Evaluator prompt" not in public
    assert "MUST NEVER ENTER" not in public
    assert "expected_doc_ids" not in public
    assert "Original evidence" in public
    assert set(DATA.manifest(["gmail", "slack"], "unit")["sources"][0]["schema"]) == {
        "id", "title", "body", "upstream_path", "upstream_sha256"}


def test_preparation_is_append_only_and_detects_extra_or_changed_files(corpus):
    root, descriptor = corpus
    DATA.prepare(root, descriptor)
    with pytest.raises(ValueError, match="exists"):
        DATA.prepare(root, descriptor)
    folder = root / "processed" / descriptor["dataset_id"]
    (folder / "injected.json").write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError, match="drift"):
        DATA.prepare(root, descriptor, check=True)


def test_selection_does_not_depend_on_input_enumeration(corpus):
    root, descriptor = corpus
    rows = DATA.load_questions(root / "raw/questions.jsonl", descriptor)
    assert DATA.select_questions(rows, descriptor["selection"]) == DATA.select_questions(list(reversed(rows)), descriptor["selection"])
    assert DATA.selection_key("seed", "question", "x") != DATA.selection_key("seed", "distractor", "x")


@pytest.mark.parametrize("filename", ["../escape.txt", "/escape.txt", "C:/escape.txt", "slack\\escape.txt"])
def test_archive_rejects_path_escape(tmp_path, filename):
    from types import SimpleNamespace
    # ZipInfo normalizes separators on Windows. Present the original decoded
    # filename directly so this tests the adapter's own guard on every host.
    info = zipfile.ZipInfo("placeholder")
    info.filename = filename
    archive = SimpleNamespace(infolist=lambda: [info])
    with pytest.raises(ValueError, match="unsafe"):
        DATA.inventory(archive, ["slack"])


def test_archive_rejects_symlinks(tmp_path):
    path = tmp_path / "bad.zip"
    info = zipfile.ZipInfo(f"slack/{identity(1)}__document.txt")
    info.create_system = 3
    info.external_attr = (stat.S_IFLNK | 0o777) << 16
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr(info, "../../secret")
    with zipfile.ZipFile(path) as archive, pytest.raises(ValueError, match="unsafe"):
        DATA.inventory(archive, ["slack"])


def test_archive_quarantines_all_colliding_identities(tmp_path):
    path = tmp_path / "duplicates.zip"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr(f"slack/{identity(1)}__one.txt", "first")
        archive.writestr(f"gmail/{identity(1)}__two.txt", "different")
        archive.writestr(f"slack/{identity(2)}__three.txt", "unique")
    with zipfile.ZipFile(path) as archive:
        documents, summary = DATA.inventory(archive, ["slack", "gmail"])
    assert set(documents) == {identity(2)}
    assert summary == {"document_count": 3, "unique_document_ids": 2, "ambiguous_document_ids": 1}


def test_missing_reference_fails_before_publication(corpus):
    root, descriptor = corpus
    path = root / "raw/questions.jsonl"
    text = path.read_text(encoding="utf-8").replace(identity(0), identity(99))
    path.write_text(text, encoding="utf-8")
    descriptor["upstream"]["questions_sha256"] = DATA.sha256(path)
    with pytest.raises(ValueError, match="missing or ambiguous"):
        DATA.prepare(root, descriptor)
    assert not (root / "processed" / descriptor["dataset_id"]).exists()
    assert not list((root / "processed").glob(".prepare-*"))


def test_duplicate_qrels_have_set_semantics_and_are_counted(corpus):
    root, descriptor = corpus
    path = root / "raw/questions.jsonl"
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    rows[0]["expected_doc_ids"] *= 2
    path.write_text("\n".join(json.dumps(row) for row in rows), encoding="utf-8")
    descriptor["upstream"]["questions_sha256"] = DATA.sha256(path)
    result = DATA.prepare(root, descriptor)
    evaluator = json.loads((root / "processed" / descriptor["dataset_id"] / "evaluator/questions.json").read_text(encoding="utf-8"))
    assert result["upstream_duplicate_qrel_entries"] == 1
    assert evaluator[0]["relevant"] == [identity(0)]


@pytest.mark.parametrize("change", ["duplicate-question", "empty-query", "empty-qrels", "unknown-category", "invalid-id"])
def test_invalid_question_contracts_fail(corpus, change):
    root, descriptor = corpus
    path = root / "raw/questions.jsonl"
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    if change == "duplicate-question":
        rows[1]["question_id"] = rows[0]["question_id"]
    elif change == "empty-query":
        rows[0]["question"] = " "
    elif change == "empty-qrels":
        rows[0]["expected_doc_ids"] = []
    elif change == "unknown-category":
        rows[0]["question_type"] = "invented"
    else:
        rows[0]["expected_doc_ids"] = ["../secret"]
    path.write_text("\n".join(json.dumps(row) for row in rows), encoding="utf-8")
    descriptor["upstream"]["questions_sha256"] = DATA.sha256(path)
    with pytest.raises(ValueError):
        DATA.load_questions(path, descriptor)


def test_cached_download_drift_does_not_overwrite(tmp_path):
    path = tmp_path / "download"
    path.write_bytes(b"bad")
    with pytest.raises(ValueError, match="cached input"):
        DATA.download("https://example.invalid", path, "0" * 64)
    assert path.read_bytes() == b"bad"


def test_download_is_verified_and_reused_without_network(tmp_path, monkeypatch):
    import io
    payload = b"pinned source"
    target = tmp_path / "source"
    calls = []
    def open_url(*args, **kwargs):
        calls.append(1)
        return io.BytesIO(payload)
    monkeypatch.setattr(DATA.urllib.request, "urlopen", open_url)
    digest = hashlib.sha256(payload).hexdigest()
    DATA.download("https://example.invalid", target, digest, len(payload))
    DATA.download("https://example.invalid", target, digest, len(payload))
    assert calls == [1]
    assert target.read_bytes() == payload


def test_wrong_download_never_publishes(tmp_path, monkeypatch):
    import io
    monkeypatch.setattr(DATA.urllib.request, "urlopen", lambda *a, **kw: io.BytesIO(b"wrong"))
    with pytest.raises(ValueError, match="download digest"):
        DATA.download("https://example.invalid", tmp_path / "source", "0" * 64)
    assert list(tmp_path.iterdir()) == []
