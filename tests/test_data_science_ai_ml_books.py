"""Tests for the private data-science, AI, and ML EPUB corpus workflow."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType
from zipfile import ZIP_DEFLATED, ZIP_STORED, ZipFile

import pytest


REPO = Path(__file__).resolve().parents[1]
SCRIPT = (
    REPO
    / "evaluations"
    / "data-science-ai-ml-books"
    / "scripts"
    / "prepare_dataset.py"
)


def load_module() -> ModuleType:
    """Load the hyphenated dataset script as a regular test module."""

    specification = importlib.util.spec_from_file_location(
        "data_science_ai_ml_books_prepare",
        SCRIPT,
    )
    assert specification is not None and specification.loader is not None
    result = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = result
    specification.loader.exec_module(result)
    return result


CORPUS = load_module()


def write_json(path: Path, value: object) -> None:
    """Write one stable JSON fixture."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def write_epub(
    path: Path,
    *,
    language: str = "en",
    xhtml: str | None = None,
    mimetype_first: bool = True,
    unsafe_member: bool = False,
) -> None:
    """Create a minimal synthetic EPUB without using private corpus content."""

    path.parent.mkdir(parents=True, exist_ok=True)
    container = """<?xml version="1.0" encoding="UTF-8"?>
<container xmlns="urn:oasis:names:tc:opendocument:xmlns:container" version="1.0">
  <rootfiles>
    <rootfile full-path="OPS/package.opf"
      media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>
"""
    package = f"""<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:title>Synthetic Data Systems</dc:title>
    <dc:creator>Example Author</dc:creator>
    <dc:publisher>Example Publisher</dc:publisher>
    <dc:language>{language}</dc:language>
    <dc:date>2026-07-30</dc:date>
    <dc:identifier>9780000000001</dc:identifier>
  </metadata>
  <manifest>
    <item id="chapter" href="chapter.xhtml" media-type="application/xhtml+xml"/>
  </manifest>
  <spine>
    <itemref idref="chapter"/>
  </spine>
</package>
"""
    chapter = xhtml or """<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml">
  <head><title>Chapter</title></head>
  <body>
    <h1>Reliable Pipelines</h1>
    <p>Use deterministic inputs.</p>
  </body>
</html>
"""
    with ZipFile(path, "w") as archive:
        if mimetype_first:
            archive.writestr("mimetype", CORPUS.EPUB_MIME_TYPE, compress_type=ZIP_STORED)
        archive.writestr(
            "META-INF/container.xml",
            container,
            compress_type=ZIP_DEFLATED,
        )
        if not mimetype_first:
            archive.writestr("mimetype", CORPUS.EPUB_MIME_TYPE, compress_type=ZIP_STORED)
        archive.writestr("OPS/package.opf", package, compress_type=ZIP_DEFLATED)
        archive.writestr("OPS/chapter.xhtml", chapter, compress_type=ZIP_DEFLATED)
        if unsafe_member:
            archive.writestr("../escape.txt", "unsafe", compress_type=ZIP_DEFLATED)


def source_catalog(epub: Path) -> dict[str, object]:
    """Return a closed one-book Drive catalog for a synthetic EPUB."""

    folder_id = "1SyntheticFolderABC"
    file_id = "1SyntheticFileABCDEF"
    timestamp = "2026-07-30T12:00:00Z"
    return {
        "schema_version": CORPUS.CATALOG_SCHEMA,
        "dataset_id": CORPUS.DATASET_ID,
        "folders": [
            {
                "partition": "ds",
                "folder_id": folder_id,
                "folder_name": "ds",
                "url": f"https://drive.google.com/drive/folders/{folder_id}",
                "created_time": timestamp,
                "modified_time": timestamp,
            }
        ],
        "files": [
            {
                "partition": "ds",
                "drive_file_id": file_id,
                "filename": epub.name,
                "mime_type": CORPUS.EPUB_MIME_TYPE,
                "size_bytes": epub.stat().st_size,
                "created_time": timestamp,
                "modified_time": timestamp,
                "url": f"https://drive.google.com/file/d/{file_id}/view?usp=drivesdk",
            }
        ],
    }


def write_descriptor(root: Path, catalog: dict[str, object], inventory: dict[str, object]) -> None:
    """Create the compact hash-pinned files required by descriptor validation."""

    tracked = {
        "manifest.json": {"synthetic": "manifest"},
        "source-combination.json": {"synthetic": "combination"},
    }
    for relative, value in tracked.items():
        write_json(root / relative, value)
    (root / "scope.md").write_text("# Synthetic corpus scope\n", encoding="utf-8")

    artifacts = [
        ("source-catalog", "sources/drive-files.json"),
        ("source-inventory", "sources/inventory.json"),
        ("semantic-manifest", "manifest.json"),
        ("source-combination", "source-combination.json"),
        ("scope", "scope.md"),
    ]
    folders = catalog["folders"]
    assert isinstance(folders, list)
    descriptor = {
        "schema_version": CORPUS.DESCRIPTOR_SCHEMA,
        "dataset_id": CORPUS.DATASET_ID,
        "title": "Synthetic book corpus",
        "description": "A synthetic test-only corpus.",
        "language": "en",
        "source_format": "EPUB",
        "source_folders": [
            {
                "partition": folder["partition"],
                "folder_id": folder["folder_id"],
                "url": folder["url"],
            }
            for folder in folders
        ],
        "summary": inventory["summary"],
        "artifacts": [
            {
                "role": role,
                "path": relative,
                "sha256": CORPUS.sha256_file(root / relative),
            }
            for role, relative in artifacts
        ],
        "evaluation_status": "corpus-only-not-registered",
    }
    write_json(root / "dataset.json", descriptor)


def synthetic_dataset(root: Path, *, xhtml: str | None = None) -> Path:
    """Create one complete content-bound synthetic dataset."""

    epub = root / "raw" / "epub" / "ds" / "synthetic.epub"
    write_epub(epub, xhtml=xhtml)
    catalog = source_catalog(epub)
    write_json(root / "sources" / "drive-files.json", catalog)
    inventory = CORPUS.write_inventory(root)
    write_descriptor(root, catalog, inventory)
    return epub


def test_prepare_replace_and_check_are_deterministic(tmp_path: Path) -> None:
    xhtml = """<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml">
  <head><title>Ignored title</title><style>.hidden { color: red; }</style></head>
  <body>
    <h1>Reliable Pipelines</h1>
    <p>Use deterministic inputs.</p>
    <blockquote>Keep source identity.</blockquote>
    <script>do_not_publish()</script>
  </body>
</html>
"""
    root = tmp_path / "dataset"
    synthetic_dataset(root, xhtml=xhtml)
    destination = root / "processed"

    first_receipt = CORPUS.prepare_dataset(root, destination)
    first_hashes = CORPUS._tree_hashes(destination)
    markdown_files = list((destination / "markdown" / "ds").glob("*.md"))
    assert len(markdown_files) == 1
    rendered = markdown_files[0].read_text(encoding="utf-8")
    assert "# Synthetic Data Systems" in rendered
    assert "## Reliable Pipelines" in rendered
    assert "Keep source identity." in rendered
    assert "do_not_publish" not in rendered
    assert first_receipt["summary"]["books"] == 1

    with pytest.raises(CORPUS.DatasetError, match="use --replace explicitly"):
        CORPUS.prepare_dataset(root, destination)

    markdown_files[0].write_text("drift\n", encoding="utf-8")
    with pytest.raises(CORPUS.DatasetError, match="processed dataset drift"):
        CORPUS.check_processed(root, destination)

    second_receipt = CORPUS.prepare_dataset(root, destination, replace=True)
    assert second_receipt == first_receipt
    assert CORPUS._tree_hashes(destination) == first_hashes

    derived = destination / "semantic-okf"
    derived.mkdir()
    (derived / "bundle.json").write_text("{}\n", encoding="utf-8")
    assert CORPUS.check_processed(root, destination) == first_receipt


def test_atomic_replace_restores_previous_output_on_publish_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "dataset"
    synthetic_dataset(root)
    destination = root / "processed"
    CORPUS.prepare_dataset(root, destination)
    original_hashes = CORPUS._tree_hashes(destination)
    real_replace = CORPUS.os.replace

    def fail_candidate_publish(source: object, target: object) -> None:
        source_path = Path(source)
        target_path = Path(target)
        if source_path.name == "candidate" and target_path == destination.resolve():
            raise OSError("simulated publication failure")
        real_replace(source, target)

    monkeypatch.setattr(CORPUS.os, "replace", fail_candidate_publish)
    with pytest.raises(OSError, match="simulated publication failure"):
        CORPUS.prepare_dataset(root, destination, replace=True)

    assert CORPUS._tree_hashes(destination) == original_hashes
    assert not list(root.glob(".processed.transaction-*"))


def test_prepare_rejects_a_destination_outside_the_processed_boundary(
    tmp_path: Path,
) -> None:
    root = tmp_path / "dataset"
    synthetic_dataset(root)

    with pytest.raises(CORPUS.DatasetError, match="or one of its descendants"):
        CORPUS.prepare_dataset(root, root, replace=True)

    assert (root / "dataset.json").is_file()
    assert (root / "raw" / "epub" / "ds" / "synthetic.epub").is_file()


def test_xhtml_renderer_preserves_structure_and_ignores_active_content() -> None:
    xhtml = b"""<html xmlns="http://www.w3.org/1999/xhtml"><body>
<h1>Heading</h1><p>First <strong>paragraph</strong>.</p>
<ol><li>One</li><li>Two<ul><li>Nested</li></ul></li></ol>
<pre>alpha()
```</pre>
<table><tr><th>Name</th><th>Value</th></tr><tr><td>A</td><td>B</td></tr></table>
<img alt="Architecture diagram" src="diagram.png"/>
<blockquote>Quoted guidance</blockquote>
<script>hidden()</script><style>.secret { display: block; }</style>
</body></html>"""

    markdown = CORPUS._xhtml_to_markdown(xhtml, "OPS/chapter.xhtml")

    assert "## Heading" in markdown
    assert "1. One" in markdown
    assert "2. Two" in markdown
    assert "- Nested" in markdown
    assert "````text\nalpha()\n```\n````" in markdown
    assert "Name | Value" in markdown
    assert "[Image: Architecture diagram]" in markdown
    assert "Quoted guidance" in markdown
    assert "hidden" not in markdown
    assert "secret" not in markdown


@pytest.mark.parametrize(
    ("options", "message"),
    [
        ({"language": "es"}, "outside the English-only corpus"),
        ({"mimetype_first": False}, "mimetype must be the first"),
        ({"unsafe_member": True}, "not a safe EPUB member path"),
    ],
)
def test_epub_validation_rejects_out_of_contract_archives(
    tmp_path: Path,
    options: dict[str, object],
    message: str,
) -> None:
    epub = tmp_path / "invalid.epub"
    write_epub(epub, **options)

    with pytest.raises(CORPUS.DatasetError, match=message):
        CORPUS.inspect_epub(epub, extract_sections=True)


def test_inventory_and_descriptor_fail_closed_on_drift(tmp_path: Path) -> None:
    root = tmp_path / "dataset"
    epub = synthetic_dataset(root)

    epub.write_bytes(epub.read_bytes() + b"drift")
    with pytest.raises(CORPUS.DatasetError, match="size drift"):
        CORPUS.check_inventory(root)

    descriptor_root = tmp_path / "descriptor-dataset"
    synthetic_dataset(descriptor_root)
    (descriptor_root / "scope.md").write_text("# Changed scope\n", encoding="utf-8")
    with pytest.raises(CORPUS.DatasetError, match="artifact digest drift"):
        CORPUS.check_descriptor(descriptor_root)


def test_cli_describe_and_prepare_replace(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    root = tmp_path / "dataset"
    synthetic_dataset(root)

    assert CORPUS.main(["--root", str(root), "describe"]) == 0
    described = json.loads(capsys.readouterr().out)
    assert described["status"] == "passed"
    assert described["summary"]["files"] == 1

    assert CORPUS.main(["--root", str(root), "prepare"]) == 0
    capsys.readouterr()
    assert CORPUS.main(["--root", str(root), "prepare", "--replace"]) == 0
    replaced = json.loads(capsys.readouterr().out)
    assert replaced["operation"] == "prepare"
