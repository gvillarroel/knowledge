from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
PREPARE_CORPUS = (
    REPO_ROOT
    / "evaluations"
    / "semantic-okf-endocrine-hygiene"
    / "scripts"
    / "prepare_corpus.py"
)


def _load_prepare(name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, PREPARE_CORPUS)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _tree_bytes(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*"), key=lambda item: item.as_posix())
        if path.is_file()
    }


def _publication_fixture(
    prepare: ModuleType,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> tuple[Path, Path, dict[Path, bytes]]:
    evaluation = tmp_path / "evaluation"
    corpus = evaluation / "corpus"
    prior_files = {
        "acquisition-selection.json": b"pinned selection\n",
        "claims-seed.json": b"reviewed claims\n",
        "notes/reviewer.txt": b"unmanaged note\n",
        "sources/other/keep.txt": b"unmanaged source\n",
        "sources/markdown/stale.md": b"stale paper\n",
        "sources/claims/stale.jsonl": b'{"stale":true}\n',
        "sources/semantic/stale.jsonl": b'{"stale":true}\n',
        "manifest.json": b'{"generation":"old"}\n',
    }
    for relative, payload in prior_files.items():
        path = corpus / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)

    monkeypatch.setattr(prepare, "EVALUATION", evaluation)
    monkeypatch.setattr(prepare, "CORPUS", corpus)
    outputs = {
        corpus / "sources" / "markdown" / "PMC1001.md": b"new paper\n",
        corpus / "sources" / "claims" / "PMC1001.jsonl": b'{"id":"new"}\n',
        corpus / "sources" / "semantic" / "analysis-vocabulary.jsonl": b'{"id":"term"}\n',
        corpus / "manifest.json": b'{"generation":"new"}\n',
    }
    return evaluation, corpus, outputs


def test_publish_replaces_stale_generated_set_and_preserves_unmanaged_files(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    prepare = _load_prepare("endocrine_hygiene_atomic_stale")
    _, corpus, outputs = _publication_fixture(prepare, tmp_path, monkeypatch)

    prepare.publish(outputs, check=False)

    assert not (corpus / "sources" / "markdown" / "stale.md").exists()
    assert not (corpus / "sources" / "claims" / "stale.jsonl").exists()
    assert not (corpus / "sources" / "semantic" / "stale.jsonl").exists()
    assert all(path.read_bytes() == payload for path, payload in outputs.items())
    assert (corpus / "acquisition-selection.json").read_bytes() == b"pinned selection\n"
    assert (corpus / "claims-seed.json").read_bytes() == b"reviewed claims\n"
    assert (corpus / "notes" / "reviewer.txt").read_bytes() == b"unmanaged note\n"
    assert (corpus / "sources" / "other" / "keep.txt").read_bytes() == b"unmanaged source\n"
    prepare.publish(outputs, check=True)


def test_check_is_read_only_even_when_generated_files_are_stale(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    prepare = _load_prepare("endocrine_hygiene_atomic_check")
    _, corpus, outputs = _publication_fixture(prepare, tmp_path, monkeypatch)
    before = _tree_bytes(corpus)
    monkeypatch.setattr(
        prepare.tempfile,
        "mkdtemp",
        lambda *args, **kwargs: pytest.fail("--check attempted to create a staging directory"),
    )

    with pytest.raises(prepare.PreparationError, match="corpus check failed"):
        prepare.publish(outputs, check=True)

    assert _tree_bytes(corpus) == before


def test_staging_failure_leaves_previous_complete_corpus_unchanged(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    prepare = _load_prepare("endocrine_hygiene_atomic_stage_failure")
    evaluation, corpus, outputs = _publication_fixture(prepare, tmp_path, monkeypatch)
    before = _tree_bytes(corpus)

    def fail_after_one_write(candidate: Path, staged: dict[Path, bytes]) -> None:
        relative, payload = sorted(staged.items(), key=lambda item: item[0].as_posix())[0]
        destination = candidate / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(payload)
        raise OSError("injected staging failure")

    monkeypatch.setattr(prepare, "_write_staged_outputs", fail_after_one_write)

    with pytest.raises(prepare.PreparationError, match="staging failed before publication"):
        prepare.publish(outputs, check=False)

    assert _tree_bytes(corpus) == before
    assert not list(evaluation.glob(".corpus-publication-*"))


def test_promotion_failure_rolls_back_without_a_mixed_generation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    prepare = _load_prepare("endocrine_hygiene_atomic_promote_failure")
    evaluation, corpus, outputs = _publication_fixture(prepare, tmp_path, monkeypatch)
    before = _tree_bytes(corpus)
    real_rename = prepare._atomic_rename
    call_count = 0

    def fail_candidate_rename(source: Path, target: Path) -> None:
        nonlocal call_count
        call_count += 1
        if call_count == 2:
            raise OSError("injected candidate promotion failure")
        real_rename(source, target)

    monkeypatch.setattr(prepare, "_atomic_rename", fail_candidate_rename)

    with pytest.raises(prepare.PreparationError, match="previous corpus was restored"):
        prepare.publish(outputs, check=False)

    assert call_count == 3
    assert _tree_bytes(corpus) == before
    assert not list(evaluation.glob(".corpus-publication-*"))


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _write_bioc_page(prepare: ModuleType, root: Path, content_type: str) -> tuple[Path, str]:
    pmcid = "PMC1001"
    title = "A literal <tag> in BioC JSON"
    body = json.dumps(
        [
            {
                "documents": [
                    {
                        "id": pmcid,
                        "infons": {"license": "CC BY 4.0"},
                        "passages": [
                            {
                                "offset": 0,
                                "infons": {
                                    "article-id_doi": "10.9999/fixture",
                                    "article-id_pmid": "1001",
                                    "name_0": "given-names:Ada;surname:Lovelace",
                                    "section_type": "TITLE",
                                    "type": "title",
                                    "year": "2024",
                                },
                                "text": title,
                            }
                        ],
                    }
                ]
            }
        ],
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )
    body_bytes = body.encode("utf-8")
    page = root / "fixture-key" / "site" / "pmc1001" / "pages" / "source.md"
    page.parent.mkdir(parents=True)
    frontmatter = (
        "---\n"
        "knowledge_key: fixture-key\n"
        "source_id: pmc1001\n"
        f"url: {prepare.BIOC_URL.format(pmcid=pmcid)}\n"
        "source_metadata:\n"
        "  content_format: json\n"
        f"  content_type: {content_type}\n"
        f"  raw_content_bytes: {len(body_bytes)}\n"
        f"  raw_content_sha256: {_sha256(body_bytes)}\n"
        "---\n"
    )
    page.write_bytes(frontmatter.encode("utf-8") + body_bytes)
    return page, title


@pytest.mark.parametrize(
    "content_type",
    [
        "Application/JSON; Charset=UTF-8",
        "application/vnd.ncbi.bioc+JSON; charset=utf-8",
    ],
)
def test_paper_record_accepts_site_source_json_media_types_case_insensitively(
    tmp_path: Path,
    content_type: str,
) -> None:
    prepare = _load_prepare(f"endocrine_hygiene_media_{len(content_type)}")
    _, title = _write_bioc_page(prepare, tmp_path, content_type)
    selection: dict[str, Any] = {
        "pmcid": "PMC1001",
        "role": "fixture",
        "relevance": "Fixture relevance.",
        "caution": "Fixture caution.",
    }

    record = prepare.paper_record(selection, tmp_path, "fixture-key")

    assert record["pmcid"] == "PMC1001"
    assert record["passages"][0]["text"] == title
    assert prepare.is_json_content_type(content_type)
    assert not prepare.is_json_content_type("application/jsonp")
