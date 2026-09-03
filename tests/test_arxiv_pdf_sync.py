from __future__ import annotations

from copy import deepcopy
from io import BytesIO
import hashlib
from pathlib import Path

from pypdf import PdfWriter
from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject
import pytest
import yaml

from knowledge.errors import SyncError
from knowledge.sources import arxiv
from knowledge.store import KnowledgeStore


def _pdf_bytes(*page_texts: str) -> bytes:
    """Build a compact, text-extractable PDF without external test tools."""
    writer = PdfWriter()
    font = DictionaryObject(
        {
            NameObject("/Type"): NameObject("/Font"),
            NameObject("/Subtype"): NameObject("/Type1"),
            NameObject("/BaseFont"): NameObject("/Helvetica"),
        }
    )
    font_reference = writer._add_object(font)
    for page_text in page_texts:
        page = writer.add_blank_page(width=612, height=792)
        page[NameObject("/Resources")] = DictionaryObject(
            {
                NameObject("/Font"): DictionaryObject(
                    {NameObject("/F1"): font_reference}
                )
            }
        )
        escaped = page_text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        stream = DecodedStreamObject()
        stream.set_data(f"BT /F1 12 Tf 72 720 Td ({escaped}) Tj ET".encode("latin-1"))
        page[NameObject("/Contents")] = writer._add_object(stream)
    output = BytesIO()
    writer.write(output)
    return output.getvalue()


def _entry(paper_id: str = "2409.04701v1") -> dict[str, object]:
    return {
        "id": f"https://arxiv.org/abs/{paper_id}",
        "title": "Complete Paper",
        "summary": "The official abstract.",
        "authors": ["Ada Researcher"],
        "categories": ["cs.IR"],
        "primary_category": "cs.IR",
        "published": "2024-09-07T03:54:46Z",
        "updated": "2024-09-07T03:54:46Z",
        "pdf_url": f"https://arxiv.org/pdf/{paper_id}",
        "links": {"alternate": f"https://arxiv.org/abs/{paper_id}"},
    }


def _source(tmp_path: Path, paper_id: str = "2409.04701v1") -> tuple[KnowledgeStore, dict]:
    store = KnowledgeStore(tmp_path)
    store.initialize()
    store.create_collection_key("papers")
    url = f"https://arxiv.org/abs/{paper_id}"
    source = store.add_collection_source(
        "papers",
        "arxiv",
        title=url,
        config={"url": url},
        update_command=f"know sync arxiv {url} --key papers",
        delete_command=f"know del --key papers arxiv-{paper_id}",
    )
    return store, source


def test_process_arxiv_pdf_extracts_every_page_and_records_digest() -> None:
    first = "Methods, evidence, and reproducible results. " * 10
    second = "Discussion, limitations, references, and conclusions. " * 10
    payload = _pdf_bytes(first, second)

    processed = arxiv._process_arxiv_pdf(
        payload,
        paper_id="2409.04701v1",
        url="https://arxiv.org/pdf/2409.04701v1",
        content_type="application/pdf",
    )

    assert processed.pages[0].startswith("## PDF page 1\n\nMethods")
    assert processed.pages[1].startswith("## PDF page 2\n\nDiscussion")
    assert processed.nonempty_pages == 2
    assert processed.extracted_characters > 800
    assert processed.sha256 == hashlib.sha256(payload).hexdigest()


def test_download_uses_export_fallback_when_primary_returns_html(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    payload = _pdf_bytes("A complete extractable research paper body. " * 12)
    calls: list[str] = []
    responses: list[Response] = []

    class Response:
        status_code = 200

        def __init__(self, url: str, content: bytes, content_type: str) -> None:
            self.url = url
            self.content = content
            self.headers = {"Content-Type": content_type, "Content-Length": str(len(content))}
            self.closed = False

        def raise_for_status(self) -> None:
            return None

        def close(self) -> None:
            self.closed = True

    def fake_get(url: str, **kwargs: object) -> Response:
        calls.append(url)
        assert kwargs["stream"] is True
        assert kwargs["headers"] == {
            "Accept": "application/pdf",
            "User-Agent": arxiv.ARXIV_USER_AGENT,
        }
        if url.startswith("https://arxiv.org/"):
            response = Response(url, b"<html>rate limited</html>", "text/html")
        else:
            response = Response(url, payload, "application/pdf")
        responses.append(response)
        return response

    monkeypatch.setattr(arxiv.requests, "get", fake_get)
    processed = arxiv._download_and_process_arxiv_pdf("2409.04701v1")

    assert calls == [
        "https://arxiv.org/pdf/2409.04701v1",
        "https://export.arxiv.org/pdf/2409.04701v1",
    ]
    assert processed.url == "https://export.arxiv.org/pdf/2409.04701v1"
    assert processed.pages[0].startswith("## PDF page 1")
    assert all(response.closed for response in responses)


def test_streamed_pdf_reader_enforces_limit_without_buffering_rest(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    yielded: list[bytes] = []

    class Response:
        headers: dict[str, str] = {}

        def iter_content(self, *, chunk_size: int):
            assert chunk_size == 1024 * 1024
            for chunk in (b"12345678", b"abcdefgh", b"must-not-be-read"):
                yielded.append(chunk)
                yield chunk

    monkeypatch.setattr(arxiv, "ARXIV_MAX_PDF_BYTES", 10)

    with pytest.raises(ValueError, match="download limit"):
        arxiv._read_pdf_response(Response())

    assert yielded == [b"12345678", b"abcdefgh"]


def test_process_arxiv_pdf_rejects_suspiciously_empty_extraction() -> None:
    payload = _pdf_bytes("short")

    with pytest.raises(ValueError, match="non-whitespace characters"):
        arxiv._process_arxiv_pdf(
            payload,
            paper_id="2409.04701v1",
            url="https://arxiv.org/pdf/2409.04701v1",
            content_type="application/pdf",
        )


def test_sync_persists_full_page_addressable_markdown(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    store, source = _source(tmp_path)
    payload = _pdf_bytes(
        "Full introduction, methodology, experiments, and evidence. " * 10,
        "Full discussion, limitations, citations, and conclusions. " * 10,
    )
    processed = arxiv._process_arxiv_pdf(
        payload,
        paper_id="2409.04701v1",
        url="https://arxiv.org/pdf/2409.04701v1",
        content_type="application/pdf",
    )
    monkeypatch.setattr(arxiv, "_download_and_process_arxiv_pdf", lambda *_args, **_kwargs: processed)

    result = arxiv.ArxivSource(source, store).sync_from_entry(_entry())

    paper_path = store.source_raw_dir(source) / "paper.md"
    paper = paper_path.read_text(encoding="utf-8")
    metadata = yaml.safe_load((store.source_raw_dir(source) / "source-metadata.yaml").read_text(encoding="utf-8"))
    assert paper.count("## PDF page ") == 2
    assert "Full introduction" in paper
    assert "Full discussion" in paper
    assert f"pdf_sha256: {processed.sha256}" in paper
    assert "page_count: 2" in paper
    assert result["content_source"] == "arxiv-pdf"
    assert result["pdf_sha256"] == processed.sha256
    assert metadata["stats"]["nonempty_page_count"] == 2


def test_failed_pdf_validation_preserves_last_successful_document(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    store, source = _source(tmp_path)
    paper_path = store.source_raw_dir(source) / "paper.md"
    paper_path.write_text("last known good paper\n", encoding="utf-8")
    monkeypatch.setattr(
        arxiv,
        "_download_and_process_arxiv_pdf",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(ValueError("response is not a PDF")),
    )

    with pytest.raises(SyncError, match="response is not a PDF"):
        arxiv.ArxivSource(source, store).sync_from_entry(_entry())

    assert paper_path.read_text(encoding="utf-8") == "last known good paper\n"
    assert not (store.source_raw_dir(source) / "source-metadata.yaml").exists()


def test_staged_paper_write_failure_preserves_complete_previous_snapshot(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    store, source = _source(tmp_path)
    processed = iter(
        [
            arxiv._process_arxiv_pdf(
                _pdf_bytes("First complete paper body with stable evidence. " * 12),
                paper_id="2409.04701v1",
                url="https://arxiv.org/pdf/2409.04701v1",
                content_type="application/pdf",
            ),
            arxiv._process_arxiv_pdf(
                _pdf_bytes("Replacement paper body that must not be published. " * 12),
                paper_id="2409.04701v1",
                url="https://arxiv.org/pdf/2409.04701v1",
                content_type="application/pdf",
            ),
        ]
    )
    monkeypatch.setattr(
        arxiv,
        "_download_and_process_arxiv_pdf",
        lambda *_args, **_kwargs: next(processed),
    )
    adapter = arxiv.ArxivSource(source, store)
    adapter.sync_from_entry(_entry())
    raw_dir = store.source_raw_dir(source)
    previous_files = {
        path.relative_to(raw_dir): path.read_bytes()
        for path in raw_dir.rglob("*")
        if path.is_file()
    }
    collection_metadata = store.key_dir("papers") / "metadata.yaml"
    previous_collection_metadata = collection_metadata.read_bytes()
    previous_source = deepcopy(source)

    def fail_write(*_args: object, **_kwargs: object) -> None:
        raise OSError("injected staged write failure")

    monkeypatch.setattr(adapter, "write_markdown", fail_write)
    with pytest.raises(OSError, match="injected staged write failure"):
        adapter.sync_from_entry(_entry())

    assert previous_files == {
        path.relative_to(raw_dir): path.read_bytes()
        for path in raw_dir.rglob("*")
        if path.is_file()
    }
    assert collection_metadata.read_bytes() == previous_collection_metadata
    assert source == previous_source
    assert not any((store.root / ".arxiv-sync").iterdir())


def test_finalize_failure_rolls_back_paper_source_and_collection_metadata(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    store, source = _source(tmp_path)
    processed = iter(
        [
            arxiv._process_arxiv_pdf(
                _pdf_bytes("First complete paper body with stable evidence. " * 12),
                paper_id="2409.04701v1",
                url="https://arxiv.org/pdf/2409.04701v1",
                content_type="application/pdf",
            ),
            arxiv._process_arxiv_pdf(
                _pdf_bytes("Replacement paper body that must be rolled back. " * 12),
                paper_id="2409.04701v1",
                url="https://arxiv.org/pdf/2409.04701v1",
                content_type="application/pdf",
            ),
        ]
    )
    monkeypatch.setattr(
        arxiv,
        "_download_and_process_arxiv_pdf",
        lambda *_args, **_kwargs: next(processed),
    )
    adapter = arxiv.ArxivSource(source, store)
    adapter.sync_from_entry(_entry())
    raw_dir = store.source_raw_dir(source)
    previous_files = {
        path.relative_to(raw_dir): path.read_bytes()
        for path in raw_dir.rglob("*")
        if path.is_file()
    }
    collection_metadata = store.key_dir("papers") / "metadata.yaml"
    previous_collection_metadata = collection_metadata.read_bytes()
    previous_source = deepcopy(source)
    original_finalize = adapter.finalize_sync

    def fail_after_finalize(stats: dict[str, object]) -> dict[str, object]:
        original_finalize(stats)
        raise OSError("injected post-finalize failure")

    monkeypatch.setattr(adapter, "finalize_sync", fail_after_finalize)
    with pytest.raises(OSError, match="injected post-finalize failure"):
        adapter.sync_from_entry(_entry())

    assert previous_files == {
        path.relative_to(raw_dir): path.read_bytes()
        for path in raw_dir.rglob("*")
        if path.is_file()
    }
    assert collection_metadata.read_bytes() == previous_collection_metadata
    assert source == previous_source
    assert not any((store.root / ".arxiv-sync").iterdir())


def test_exact_version_sync_rejects_metadata_for_another_version(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    store, source = _source(tmp_path, "2409.04701v1")
    called = False

    def acquire(*_args: object, **_kwargs: object) -> arxiv._ProcessedPDF:
        nonlocal called
        called = True
        raise AssertionError("PDF acquisition must not run for mismatched metadata")

    monkeypatch.setattr(arxiv, "_download_and_process_arxiv_pdf", acquire)

    with pytest.raises(SyncError, match="instead of requested version"):
        arxiv.ArxivSource(source, store).sync_from_entry(_entry("2409.04701v2"))

    assert called is False


def test_direct_sync_falls_back_from_invalid_atom_and_paces_requests(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    store, source = _source(tmp_path)
    sleeps: list[float] = []
    fallbacks: list[str] = []

    class Response:
        text = "<invalid"

    processed = arxiv._process_arxiv_pdf(
        _pdf_bytes("A complete paper body for direct synchronization. " * 12),
        paper_id="2409.04701v1",
        url="https://arxiv.org/pdf/2409.04701v1",
        content_type="application/pdf",
    )
    monkeypatch.setattr(arxiv, "_request_arxiv", lambda *_args, **_kwargs: Response())
    monkeypatch.setattr(
        arxiv,
        "_fetch_arxiv_html_entry",
        lambda paper_id: fallbacks.append(paper_id) or _entry(paper_id),
    )
    monkeypatch.setattr(arxiv, "_download_and_process_arxiv_pdf", lambda *_args, **_kwargs: processed)
    monkeypatch.setattr(arxiv.time, "sleep", lambda delay: sleeps.append(delay))

    result = arxiv.ArxivSource(source, store).sync()

    assert result["page_count"] == 1
    assert fallbacks == ["2409.04701v1"]
    assert sleeps == [arxiv.ARXIV_DEFAULT_REQUEST_DELAY, arxiv.ARXIV_DEFAULT_REQUEST_DELAY]


def test_sync_from_entry_rejects_negative_download_delay(tmp_path: Path) -> None:
    store, source = _source(tmp_path)

    with pytest.raises(ValueError, match="non-negative"):
        arxiv.ArxivSource(source, store).sync_from_entry(_entry(), download_delay=-0.1)


def test_identity_helpers_fail_closed_on_malformed_or_unrelated_metadata() -> None:
    assert arxiv._entry_for_paper_id({}, "2409.04701v1") is None
    assert (
        arxiv._entry_for_paper_id(
            [None, {"id": "not-an-arxiv-id"}, {"id": "https://arxiv.org/abs/1111.22222v1"}],
            "2409.04701v1",
        )
        is None
    )
    assert arxiv._resolved_entry_paper_id({}, "2409.04701v1") == "2409.04701v1"
    with pytest.raises(ValueError, match="does not match requested paper"):
        arxiv._resolved_entry_paper_id(
            {"id": "https://arxiv.org/abs/1111.22222v1"},
            "2409.04701v1",
        )
    assert arxiv._clean_string_list("Ada Researcher") == []


def test_pdf_response_reader_checks_declared_and_streamed_sizes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class DeclaredTooLarge:
        headers = {"Content-Length": "11"}
        content = b""

    class Streamed:
        headers: dict[str, str] = {}

        def iter_content(self, *, chunk_size: int):
            assert chunk_size == 1024 * 1024
            yield b""
            yield b"%PDF-"

    class BufferedTooLarge:
        headers: dict[str, str] = {}
        content = b"12345678901"

    monkeypatch.setattr(arxiv, "ARXIV_MAX_PDF_BYTES", 10)
    with pytest.raises(ValueError, match="download limit"):
        arxiv._read_pdf_response(DeclaredTooLarge())
    assert arxiv._read_pdf_response(Streamed()) == b"%PDF-"
    with pytest.raises(ValueError, match="download limit"):
        arxiv._read_pdf_response(BufferedTooLarge())


def test_pdf_request_retries_connection_and_transient_status(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import requests

    calls = 0
    sleeps: list[float] = []
    responses: list[Response] = []

    class Response:
        headers: dict[str, str] = {}

        def __init__(self, status_code: int) -> None:
            self.status_code = status_code
            self.closed = False

        def raise_for_status(self) -> None:
            return None

        def close(self) -> None:
            self.closed = True

    def fake_get(*_args: object, **_kwargs: object) -> Response:
        nonlocal calls
        calls += 1
        if calls == 1:
            raise requests.ConnectionError("temporary connection failure")
        response = Response(503 if calls == 2 else 200)
        responses.append(response)
        return response

    monkeypatch.setattr(arxiv.requests, "get", fake_get)
    monkeypatch.setattr(arxiv.time, "sleep", lambda delay: sleeps.append(delay))

    response = arxiv._request_arxiv_pdf("https://arxiv.org/pdf/2409.04701v1")

    assert response.status_code == 200
    assert calls == 3
    assert sleeps == [3.0, 6.0]
    assert responses[0].closed is True
    assert responses[1].closed is False
    response.close()


def test_pdf_request_raises_after_connection_retries_are_exhausted(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import requests

    calls = 0
    sleeps: list[float] = []

    def fail(*_args: object, **_kwargs: object) -> None:
        nonlocal calls
        calls += 1
        raise requests.ConnectionError("offline")

    monkeypatch.setattr(arxiv, "ARXIV_MAX_ATTEMPTS", 2)
    monkeypatch.setattr(arxiv.requests, "get", fail)
    monkeypatch.setattr(arxiv.time, "sleep", lambda delay: sleeps.append(delay))

    with pytest.raises(requests.ConnectionError, match="offline"):
        arxiv._request_arxiv_pdf("https://arxiv.org/pdf/2409.04701v1")

    assert calls == 2
    assert sleeps == [3.0]


def test_official_pdf_urls_ignore_untrusted_or_mismatched_preferences() -> None:
    expected = [
        "https://arxiv.org/pdf/2409.04701v1",
        "https://export.arxiv.org/pdf/2409.04701v1",
    ]

    assert (
        arxiv._official_pdf_urls(
            "2409.04701v1",
            "http://arxiv.org/pdf/2409.04701v1.pdf",
        )
        == expected
    )
    assert arxiv._official_pdf_urls(
        "2409.04701v1",
        "https://export.arxiv.org/pdf/2409.04701v1",
    ) == list(reversed(expected))
    assert (
        arxiv._official_pdf_urls(
            "2409.04701v1",
            "https://arxiv.org/pdf/2409.04701v2",
        )
        == expected
    )
    assert arxiv._official_pdf_urls("2409.04701v1", "https://malicious.example/paper.pdf") == expected


def test_pdf_acquisition_reports_both_invalid_official_endpoints(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class Response:
        headers = {"Content-Type": "text/html"}
        content = b"<html>blocked</html>"

        def close(self) -> None:
            return None

    monkeypatch.setattr(arxiv, "_request_arxiv_pdf", lambda _url: Response())

    with pytest.raises(ValueError, match="could not acquire a valid, extractable PDF") as error:
        arxiv._download_and_process_arxiv_pdf(
            "2409.04701v1",
            preferred_url="https://malicious.example/paper.pdf",
        )

    assert str(error.value).count("response is not a PDF") == 2
    assert "malicious.example" not in str(error.value)


def test_pdf_parser_rejects_invalid_empty_and_encrypted_documents() -> None:
    with pytest.raises(ValueError, match="cannot parse PDF"):
        arxiv._process_arxiv_pdf(
            b"%PDF-not-really-a-pdf",
            paper_id="2409.04701v1",
            url="https://arxiv.org/pdf/2409.04701v1",
            content_type="application/pdf",
        )

    empty_writer = PdfWriter()
    empty_output = BytesIO()
    empty_writer.write(empty_output)
    with pytest.raises(ValueError, match="PDF has no pages"):
        arxiv._process_arxiv_pdf(
            empty_output.getvalue(),
            paper_id="2409.04701v1",
            url="https://arxiv.org/pdf/2409.04701v1",
            content_type="application/pdf",
        )

    with pytest.raises(ValueError, match="non-whitespace characters"):
        arxiv._process_arxiv_pdf(
            _pdf_bytes(""),
            paper_id="2409.04701v1",
            url="https://arxiv.org/pdf/2409.04701v1",
            content_type="application/pdf",
        )

    encrypted_writer = PdfWriter()
    encrypted_writer.add_blank_page(width=612, height=792)
    encrypted_writer.encrypt("secret")
    encrypted_output = BytesIO()
    encrypted_writer.write(encrypted_output)
    with pytest.raises(ValueError, match="encrypted"):
        arxiv._process_arxiv_pdf(
            encrypted_output.getvalue(),
            paper_id="2409.04701v1",
            url="https://arxiv.org/pdf/2409.04701v1",
            content_type="application/pdf",
        )


def test_pdf_parser_reports_stale_install_without_pypdf(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(arxiv, "pypdf", None)

    with pytest.raises(ValueError, match="reinstall or upgrade knowledge-cli"):
        arxiv._process_arxiv_pdf(
            b"%PDF-1.7",
            paper_id="2409.04701v1",
            url="https://arxiv.org/pdf/2409.04701v1",
            content_type="application/pdf",
        )
