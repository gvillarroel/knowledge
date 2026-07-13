"""Unit and portability tests for the Confluence page round-trip skill."""

from __future__ import annotations

import importlib.util
from io import BytesIO
import json
from pathlib import Path
import shutil
import struct
import subprocess
import sys
from types import ModuleType
from typing import Any
import zlib

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPO_ROOT / "skills" / "roundtrip-confluence-pages"
SCRIPT = SKILL_ROOT / "scripts" / "confluence_roundtrip.py"


def load_script() -> ModuleType:
    """Load the standalone script for focused unit tests."""

    spec = importlib.util.spec_from_file_location("test_confluence_roundtrip", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class FakeClient:
    """Stateful in-memory Confluence API used by round-trip tests."""

    def __init__(self) -> None:
        self.base_url = "https://example.atlassian.net"
        self.version = 3
        self.meta = {
            "id": "42",
            "title": "Fixture",
            "spaceId": "7",
            "parentId": None,
            "status": "current",
            "subtype": "page",
        }
        self.storage = (
            '<h1>Fixture</h1><p>Old content</p>'
            '<ac:structured-macro ac:name="status"><ac:parameter ac:name="title">In progress</ac:parameter>'
            '</ac:structured-macro><ac:image><ri:attachment ri:filename="old.png" /></ac:image>'
        )
        self.adf = {
            "version": 1,
            "type": "doc",
            "content": [
                {"type": "paragraph", "content": [{"type": "text", "text": "Old content", "marks": [{"type": "strong"}]}]},
                {"type": "status", "attrs": {"text": "In progress", "color": "yellow"}},
            ],
        }
        self.view = "<h1>Fixture</h1><p>Old content</p>"
        self.label_names = ["alpha"]
        self.state: dict[str, Any] | None = {"id": 1, "name": "Draft", "color": "YELLOW"}
        self.attachment_bytes = {"old.png": b"old-image"}
        self.attachment_ids = {"old.png": "a1"}
        self.upload_calls: list[tuple[str, str | None]] = []
        self.page_updates = 0
        self.render_preflight_calls = 0

    def page(self, page_id: str, representation: str = "storage") -> dict[str, Any]:
        assert page_id == "42"
        value = {
            "storage": self.storage,
            "atlas_doc_format": json.dumps(self.adf),
            "view": self.view,
        }[representation]
        return {
            **self.meta,
            "version": {"number": self.version},
            "body": {representation: {"value": value}},
            "labels": {"results": [{"prefix": "global", "name": label} for label in self.label_names]},
            "properties": {"results": [{"key": "fixture", "value": {"ok": True}}]},
            "operations": {"results": [{"operation": "update", "targetType": "page"}]},
            "_links": {"webui": "/wiki/spaces/T/pages/42"},
        }

    def draft_page(self, page_id: str) -> dict[str, Any]:
        """Return the current page when the fixture has no editor draft."""

        return self.page(page_id, "storage")

    def attachments(self, page_id: str) -> list[dict[str, Any]]:
        assert page_id == "42"
        return [
            {
                "id": self.attachment_ids[name],
                "title": name,
                "mediaType": "image/png",
                "version": {"number": 1},
                "downloadLink": f"/download/{name}",
            }
            for name in sorted(self.attachment_bytes)
        ]

    def labels(self, page_id: str) -> list[str]:
        assert page_id == "42"
        return sorted(self.label_names)

    def download_attachment(self, attachment: dict[str, Any]) -> bytes:
        return self.attachment_bytes[str(attachment["title"])]

    def content_state(self, page_id: str) -> dict[str, Any] | None:
        assert page_id == "42"
        return self.state

    def preflight_storage_render(self, page_id: str, storage: str) -> dict[str, Any]:
        assert page_id == "42"
        assert isinstance(storage, str)
        self.render_preflight_calls += 1
        return {
            "status": "completed",
            "representation": "view",
            "rendered_sha256": "a" * 64,
            "rendered_bytes": 123,
            "polls": 1,
            "render_safety": {
                "status": "passed",
                "unknown_macro_placeholders": 0,
                "signals_found": [],
            },
        }

    def restrictions(self, page_id: str) -> dict[str, Any]:
        assert page_id == "42"
        return {"read": {"restrictions": {"user": {"results": []}}}}

    def upload_attachment(
        self,
        page_id: str,
        path: Path,
        existing_id: str | None,
        *,
        comment: str,
        media_type: str | None = None,
    ) -> dict[str, Any]:
        assert page_id == "42"
        assert comment
        assert media_type == "image/png"
        self.upload_calls.append((path.name, existing_id))
        self.attachment_bytes[path.name] = path.read_bytes()
        self.attachment_ids.setdefault(path.name, f"a{len(self.attachment_ids) + 1}")
        return {"results": [{"id": self.attachment_ids[path.name]}]}

    def update_page(
        self,
        page_id: str,
        meta: dict[str, Any],
        storage: str,
        version: int,
        message: str,
    ) -> dict[str, Any]:
        assert page_id == "42"
        assert version == self.version
        assert message
        self.storage = storage
        self.meta["title"] = meta["title"]
        self.version += 1
        self.page_updates += 1
        self.adf = {
            "version": 1,
            "type": "doc",
            "content": [{"type": "paragraph", "content": [{"type": "text", "text": "New content"}]}],
        }
        self.view = f"<h1>{meta['title']}</h1><p>New content</p>"
        return self.page(page_id, "storage")

    def sync_labels(self, page_id: str, desired: list[str], current: list[str]) -> dict[str, list[str]]:
        assert page_id == "42"
        added = sorted(set(desired) - set(current))
        removed = sorted(set(current) - set(desired))
        self.label_names = sorted(desired)
        return {"added": added, "removed": removed}

    def set_content_state(
        self,
        page_id: str,
        desired: dict[str, Any] | None,
        current: dict[str, Any] | None,
    ) -> str:
        assert page_id == "42"
        if desired == current:
            return "unchanged"
        self.state = desired
        self.version += 1
        return "removed" if desired is None else "updated"


def write_browser_record(
    module: ModuleType,
    workspace: Path,
    *,
    page_id: str = "42",
    status: str = "verified",
) -> None:
    """Write a local browser-ground-truth record with real screenshot hashes."""

    verification = workspace / module.VERIFY_DIR
    baseline = verification / "browser-baseline.png"
    final = verification / "browser-final.png"
    baseline.write_bytes(make_png((20, 40, 60)))
    final.write_bytes(make_png((60, 40, 20)))
    api_path = verification / module.REPORT_NAME
    api = module.load_json(api_path)
    module.write_json(
        verification / module.BROWSER_GT_NAME,
        {
            "schema_version": module.SCHEMA_VERSION,
            "status": status,
            "page_id": page_id,
            "page_url": f"https://example.atlassian.net/wiki/pages/{page_id}",
            "operation_id": api["operation_id"],
            "api_report_sha256": module.sha256_bytes(api_path.read_bytes()),
            "remote_version": api["remote_version"],
            "desired_state_sha256": api["desired_state_sha256"],
            "verified_at": module.utc_now(),
            "baseline": {
                "path": baseline.name,
                "sha256": module.sha256_bytes(baseline.read_bytes()),
            },
            "final_screenshots": [
                {
                    "path": final.name,
                    "sha256": module.sha256_bytes(final.read_bytes()),
                }
            ],
            "checks": [{"name": "rendered-page", "passed": status == "verified"}],
        },
    )


def make_png(rgb: tuple[int, int, int]) -> bytes:
    """Return a tiny valid RGB PNG without optional image libraries."""

    def chunk(kind: bytes, payload: bytes) -> bytes:
        return (
            struct.pack(">I", len(payload))
            + kind
            + payload
            + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)
        )

    header = struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)
    pixels = zlib.compress(b"\x00" + bytes(rgb))
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header) + chunk(b"IDAT", pixels) + chunk(b"IEND", b"")


def test_screenshot_decoder_rejects_framing_only_images() -> None:
    module = load_script()
    fake_jpeg = (
        b"\xff\xd8\xff\xc0\x00\x07\x08\x00\x01\x00\x01"
        b"\xff\xda\x00\x02\xff\xd9"
    )

    def chunk(kind: bytes, payload: bytes) -> bytes:
        return (
            struct.pack(">I", len(payload))
            + kind
            + payload
            + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)
        )

    header = struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)
    wrong_scanline_size_png = (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", header)
        + chunk(b"IDAT", zlib.compress(b"\x00"))
        + chunk(b"IEND", b"")
    )

    assert module.screenshot_is_decodable(make_png((1, 2, 3)))
    assert not module.screenshot_is_decodable(fake_jpeg)
    assert not module.screenshot_is_decodable(wrong_scanline_size_png)


def test_screenshot_decoder_accepts_a_real_jpeg_and_rejects_corruption() -> None:
    image_module = pytest.importorskip("PIL.Image")
    module = load_script()
    buffer = BytesIO()
    image_module.new("RGB", (2, 2), (12, 34, 56)).save(buffer, format="JPEG")
    jpeg = buffer.getvalue()

    assert module.screenshot_is_decodable(jpeg)
    assert not module.screenshot_is_decodable(jpeg[:-2])
    assert not module.screenshot_is_decodable(jpeg[:2] + b"\xff\xd8" + jpeg[2:])


def make_symlink_or_skip(link: Path, target: Path, *, target_is_directory: bool = False) -> None:
    """Create a symlink or skip on hosts that do not permit test symlinks."""

    try:
        link.symlink_to(target, target_is_directory=target_is_directory)
    except (NotImplementedError, OSError) as exc:
        pytest.skip(f"symlinks are unavailable for this test: {exc}")


def make_verified_workspace(tmp_path: Path) -> tuple[ModuleType, FakeClient, Path]:
    """Create one API- and browser-verified workspace for integrity tests."""

    module = load_script()
    client = FakeClient()
    workspace = tmp_path / "verified-page"
    module.download_page(client, "42", workspace)
    result = module.upload_workspace(client, workspace, message="Integrity fixture")
    assert result["status"] == "uploaded", result
    write_browser_record(module, workspace)
    assert module.validate_completion_gate(workspace)["status"] == "verified"
    return module, client, workspace


def test_atomic_writes_retry_transient_permission_errors(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = load_script()
    destination = tmp_path / "journal.json"
    real_replace = module.os.replace
    attempts: list[int] = []

    def flaky_replace(source: str, target: Path) -> None:
        attempts.append(1)
        if len(attempts) < 3:
            raise PermissionError("transient Windows sharing violation")
        real_replace(source, target)

    monkeypatch.setattr(module.os, "replace", flaky_replace)
    monkeypatch.setattr(module.time, "sleep", lambda _seconds: None)

    module.write_text(destination, "durable evidence")

    assert destination.read_text(encoding="utf-8") == "durable evidence"
    assert len(attempts) == 3


def test_storage_and_adf_summaries_preserve_complex_features() -> None:
    module = load_script()
    storage = (
        '<h2>Plan</h2><p><a href="https://example.com">Smart</a></p>'
        '<ac:structured-macro ac:name="recently-updated" />'
        '<ac:structured-macro ac:name="status"><ac:parameter ac:name="title">Ready</ac:parameter></ac:structured-macro>'
        '<ac:image><ri:attachment ri:filename="diagram.png" /></ac:image>'
        '<ac:link><ri:page ri:content-title="Architecture" /></ac:link>'
    )

    summary = module.storage_summary(storage)
    assert summary["macros"] == {"recently-updated": 1, "status": 1}
    assert summary["attachment_filenames"] == ["diagram.png"]
    assert summary["page_references"] == ["Architecture"]
    assert summary["hrefs"] == ["https://example.com"]
    assert len(summary["canonical_sha256"]) == 64

    adf = {
        "version": 1,
        "type": "doc",
        "content": [
            {"type": "inlineCard", "attrs": {"url": "https://example.com"}},
            {"type": "media", "attrs": {"id": "media-1", "type": "file"}},
            {
                "type": "extension",
                "attrs": {"extensionType": "com.atlassian.confluence.macro.core", "extensionKey": "toc"},
            },
            {"type": "text", "text": "bold", "marks": [{"type": "strong"}]},
        ],
    }
    adf_inventory = module.adf_summary(adf)
    assert adf_inventory["nodes"]["inlineCard"] == 1
    assert adf_inventory["marks"] == {"strong": 1}
    assert adf_inventory["extensions"] == ["com.atlassian.confluence.macro.core", "toc"]
    assert adf_inventory["media_ids"] == ["media-1"]


def test_storage_summary_ignores_xml_like_text_in_comments_and_cdata() -> None:
    module = load_script()
    storage = (
        '<!-- <ac:structured-macro ac:name="comment-fake" />'
        '<ri:attachment ri:filename="comment-fake.png" />'
        '<a href="javascript:commentFake()">comment fake</a> -->'
        '<p><![CDATA[<ac:structured-macro ac:name="cdata-fake" />'
        '<ri:page ri:content-title="CDATA Fake" />'
        '<a href="file:///tmp/cdata-fake">CDATA fake</a>]]></p>'
        '<ac:structured-macro ac:name="status" />'
        '<ac:image><ri:attachment ri:filename="real.png" /></ac:image>'
        '<ac:link><ri:page ri:content-title="Real page" /></ac:link>'
        '<p><a href="https://example.com/real">Real link</a></p>'
    )

    summary = module.storage_summary(storage)
    module.validate_storage_link_targets(storage)

    assert summary["macros"] == {"status": 1}
    assert summary["attachment_filenames"] == ["real.png"]
    assert summary["page_references"] == ["Real page"]
    assert summary["hrefs"] == ["https://example.com/real"]
    assert summary["tags"] == {
        "a": 1,
        "ac:image": 1,
        "ac:link": 1,
        "ac:structured-macro": 1,
        "p": 2,
        "ri:attachment": 1,
        "ri:page": 1,
    }


def test_storage_entity_normalization_preserves_literal_cdata_content() -> None:
    module = load_script()
    named = (
        '<ac:structured-macro ac:name="code"><ac:plain-text-body>'
        '<![CDATA[&nbsp;]]></ac:plain-text-body></ac:structured-macro>'
    )
    numeric_literal = named.replace("&nbsp;", "&#160;")

    assert module.canonical_storage(named) != module.canonical_storage(numeric_literal)
    assert module.remote_equivalence_storage(named) != module.remote_equivalence_storage(
        numeric_literal
    )


@pytest.mark.parametrize(
    "target",
    [
        "https://example.com/path",
        "http://example.com/path",
        "mailto:editor@example.com?subject=Round%20trip",
        "tel:+12025550123",
        "#page-anchor",
        "/wiki/spaces/ENG/pages/42",
        "relative/page",
        "//cdn.example.com/image.png",
    ],
)
def test_storage_link_validation_accepts_supported_web_targets(target: str) -> None:
    module = load_script()
    escaped_target = target.replace("&", "&amp;")

    module.validate_storage_link_targets(f'<p><a href="{escaped_target}">Link</a></p>')
    module.validate_storage_link_targets(
        f'<ac:image><ri:url ri:value="{escaped_target}" /></ac:image>'
    )


@pytest.mark.parametrize(
    "target",
    [
        "javascript:alert(1)",
        "java&#x73;cript:alert(1)",
        "data:text/html,unsafe",
        "vbscript:msgbox(1)",
        "file:///C:/Users/editor/secret.txt",
        "C:/Users/editor/secret.txt",
        r"C:\Users\editor\secret.txt",
        r"\\server\share\secret.txt",
        "~/secret.txt",
        "$HOME/secret.txt",
        "/home/editor/secret.txt",
        "/root/secret.txt",
        "/Users/editor/secret.txt",
        " https://example.com/hidden-whitespace",
        "https://user:secret@example.com/private",
        "https://[invalid-host",
    ],
)
def test_storage_link_validation_rejects_unsafe_schemes_and_local_paths(target: str) -> None:
    module = load_script()

    with pytest.raises(module.ValidationError, match="unsafe storage link target"):
        module.validate_storage_link_targets(f'<p><a href="{target}">Unsafe</a></p>')


def test_storage_link_validation_checks_plain_text_macro_url_parameters() -> None:
    module = load_script()
    storage = (
        '<ac:structured-macro ac:name="widget">'
        '<ac:parameter ac:name="url">javascript:alert(1)</ac:parameter>'
        '</ac:structured-macro>'
    )

    with pytest.raises(module.ValidationError, match=r"ac:parameter\[url\]"):
        module.validate_storage_link_targets(storage)


def test_workspace_validation_rejects_unsafe_ri_url_before_upload(tmp_path: Path) -> None:
    module = load_script()
    workspace = tmp_path / "page"
    module.download_page(FakeClient(), "42", workspace)
    storage_path = workspace / module.STORAGE_NAME
    storage = storage_path.read_text(encoding="utf-8")
    storage_path.write_text(
        storage + '<ac:image><ri:url ri:value="file:///tmp/local.png" /></ac:image>',
        encoding="utf-8",
    )
    module.capture_ground_truth(workspace)

    with pytest.raises(module.ValidationError, match="unsafe storage link target"):
        module.validate_workspace(workspace)


def test_canonical_storage_hash_includes_xml_comments() -> None:
    module = load_script()

    without_comment = module.storage_summary("<p>Visible</p>")["canonical_sha256"]
    with_comment = module.storage_summary("<!-- preserve me --><p>Visible</p>")["canonical_sha256"]

    assert without_comment != with_comment


def test_remote_storage_equivalence_accepts_only_confluence_owned_normalization() -> None:
    module = load_script()
    local = (
        '<ac:structured-macro ac:name="status">'
        '<ac:parameter ac:name="title">READY</ac:parameter>'
        '<ac:parameter ac:name="colour">Green</ac:parameter>'
        '</ac:structured-macro>'
        '<ac:image><ri:attachment ri:filename="architecture.png" /></ac:image>'
    )
    remote = (
        '<ac:structured-macro ac:name="status" ac:schema-version="1" ac:macro-id="generated">'
        '<ac:parameter ac:name="colour">Green</ac:parameter>'
        '<ac:parameter ac:name="title">READY</ac:parameter>'
        '</ac:structured-macro>'
        '<ac:image><ri:attachment ri:filename="architecture.png" ri:version-at-save="1" /></ac:image>'
    )

    assert module.remote_equivalence_storage(local + "\n") == module.remote_equivalence_storage(remote)
    assert module.remote_equivalence_storage(local) != module.remote_equivalence_storage(
        remote.replace("READY", "BLOCKED")
    )


def test_remote_storage_equivalence_accepts_style_and_macro_whitespace_normalization() -> None:
    module = load_script()
    local = (
        '<p style="margin-left: 60px"><span style="color: rgb(0, 82, 204)">Blue</span></p>'
        '<ac:structured-macro ac:name="expand">\n'
        '  <ac:parameter ac:name="title">Details</ac:parameter>\n'
        '  <ac:rich-text-body>\n    <p>Body</p>\n  </ac:rich-text-body>\n'
        '</ac:structured-macro>'
    )
    remote = (
        '<p style="margin-left: 60.0px;"><span style="color:rgb(0,82,204);">Blue</span></p>'
        '<ac:structured-macro ac:name="expand" ac:macro-id="generated" ac:schema-version="1">'
        '<ac:parameter ac:name="title">Details</ac:parameter>'
        '<ac:rich-text-body><p>Body</p></ac:rich-text-body>'
        '</ac:structured-macro>'
    )

    assert module.remote_equivalence_storage(local) == module.remote_equivalence_storage(remote)
    assert module.remote_equivalence_storage("<p><strong>A</strong> <em>B</em></p>") != (
        module.remote_equivalence_storage("<p><strong>A</strong><em>B</em></p>")
    )


def test_remote_storage_equivalence_accepts_nested_macro_parameter_formatting() -> None:
    module = load_script()
    local = (
        '<ac:structured-macro ac:name="include">\n'
        '<ac:parameter ac:name="">\n'
        '<ac:link>\n<ri:page ri:content-title="Included page" />\n</ac:link>\n'
        '</ac:parameter>\n'
        '</ac:structured-macro>'
        '<ac:structured-macro ac:name="iframe">\n'
        '<ac:parameter ac:name="src">\n'
        '<ri:url ri:value="https://example.com/embed" />\n'
        '</ac:parameter>\n'
        '<ac:parameter ac:name="height">320</ac:parameter>\n'
        '</ac:structured-macro>'
    )
    remote = (
        '<ac:structured-macro ac:name="include">'
        '<ac:parameter ac:name=""><ac:link>'
        '<ri:page ri:content-title="Included page" />'
        '</ac:link></ac:parameter>'
        '</ac:structured-macro>'
        '<ac:structured-macro ac:name="iframe">'
        '<ac:parameter ac:name="height">320</ac:parameter>'
        '<ac:parameter ac:name="src">'
        '<ri:url ri:value="https://example.com/embed" />'
        '</ac:parameter>'
        '</ac:structured-macro>'
    )

    assert module.remote_equivalence_storage(local) == module.remote_equivalence_storage(remote)
    assert module.remote_equivalence_storage(local) != module.remote_equivalence_storage(
        remote.replace("Included page", "Different page")
    )
    whitespace_value = (
        '<ac:structured-macro ac:name="example">'
        '<ac:parameter ac:name="value"> </ac:parameter>'
        '</ac:structured-macro>'
    )
    empty_value = whitespace_value.replace(
        "> </ac:parameter>",
        "></ac:parameter>",
    )
    assert module.remote_equivalence_storage(whitespace_value) != (
        module.remote_equivalence_storage(empty_value)
    )


def test_upload_plan_is_noop_after_confluence_normalizes_saved_storage(tmp_path: Path) -> None:
    module = load_script()
    client = FakeClient()
    workspace = tmp_path / "page"
    module.download_page(client, "42", workspace)
    original = (workspace / module.STORAGE_NAME).read_text(encoding="utf-8")
    local_macro = (
        '<ac:structured-macro ac:name="status">'
        '<ac:parameter ac:name="title">READY</ac:parameter>'
        '<ac:parameter ac:name="colour">Green</ac:parameter>'
        '</ac:structured-macro>'
    )
    remote_macro = (
        '<ac:structured-macro ac:name="status" ac:schema-version="1" ac:macro-id="generated">'
        '<ac:parameter ac:name="colour">Green</ac:parameter>'
        '<ac:parameter ac:name="title">READY</ac:parameter>'
        '</ac:structured-macro>'
    )
    (workspace / module.STORAGE_NAME).write_text(original + local_macro, encoding="utf-8")
    client.storage = original + remote_macro
    module.capture_ground_truth(workspace)

    plan, _, _ = module.upload_plan(client, workspace)

    assert plan["body_changed"] is False
    assert plan["page_update"] is False


def test_download_validate_capture_upload_and_verify(tmp_path: Path) -> None:
    module = load_script()
    client = FakeClient()
    workspace = tmp_path / "page"

    downloaded = module.download_page(client, "42", workspace)
    assert downloaded["status"] == "downloaded"
    assert (workspace / "attachments" / "old.png").read_bytes() == b"old-image"
    assert module.validate_workspace(workspace)["status"] == "valid"

    storage = (workspace / module.STORAGE_NAME).read_text(encoding="utf-8")
    storage = storage.replace("Old content", "New content")
    storage += '<ac:image><ri:attachment ri:filename="new.png" /></ac:image>'
    (workspace / module.STORAGE_NAME).write_text(storage, encoding="utf-8")
    (workspace / "attachments" / "new.png").write_bytes(b"new-image")
    meta = module.load_json(workspace / module.META_NAME)
    meta["title"] = "Changed fixture"
    module.write_json(workspace / module.META_NAME, meta)
    module.write_json(workspace / module.LABELS_NAME, ["alpha", "beta"])
    module.write_json(workspace / module.STATE_NAME, {"name": "Ready", "color": "GREEN"})
    module.capture_ground_truth(workspace, ["New content"])

    dry_run = module.upload_workspace(client, workspace, message="Test", dry_run=True)
    assert dry_run["status"] == "dry-run"
    assert dry_run["plan"]["page_update"] is True
    assert dry_run["plan"]["attachments"] == [
        {
            "filename": "new.png",
            "action": "create",
            "sha256": module.sha256_bytes(b"new-image"),
            "media_type": "image/png",
        }
    ]
    assert dry_run["plan"]["labels"] == {"added": ["beta"], "removed": []}
    assert dry_run["plan"]["content_state_changed"] is True
    assert dry_run["plan"]["remote_render_preflight_required"] is True
    assert dry_run["plan"]["no_op"] is False
    assert dry_run["plan"]["sync"] == {
        "attachments": True,
        "labels": True,
        "content_state": True,
    }

    suppressed = module.upload_workspace(
        client,
        workspace,
        message="Suppressed plan",
        dry_run=True,
        sync_attachments=False,
        sync_labels=False,
        sync_content_state=False,
    )
    assert suppressed["plan"]["attachments"] == []
    assert suppressed["plan"]["labels"] == {"added": [], "removed": []}
    assert suppressed["plan"]["content_state_changed"] is False
    assert suppressed["plan"]["suppressed_attachments"][0]["filename"] == "new.png"
    assert suppressed["plan"]["suppressed_labels"] == {"added": ["beta"], "removed": []}
    assert suppressed["plan"]["suppressed_content_state_changed"] is True
    with pytest.raises(module.ValidationError, match="skip flags suppress desired changes"):
        module.upload_workspace(
            client,
            workspace,
            message="Unsafe suppressed upload",
            sync_attachments=False,
            sync_labels=False,
            sync_content_state=False,
        )
    assert client.page_updates == 0
    assert client.render_preflight_calls == 0

    result = module.upload_workspace(client, workspace, message="Test")

    assert result["status"] == "uploaded"
    assert result["verification"]["status"] == "verified"
    assert result["remote_render_preflight"]["status"] == "completed"
    assert client.render_preflight_calls == 1
    assert client.page_updates == 1
    assert client.upload_calls == [("new.png", None)]
    assert client.label_names == ["alpha", "beta"]
    assert client.state == {"name": "Ready", "color": "GREEN"}
    report = module.load_json(workspace / module.VERIFY_DIR / "report.json")
    assert all(item["passed"] for item in report["checks"])
    manifest = module.load_json(workspace / module.MANIFEST_NAME)
    assert manifest["page"]["version"] == client.version
    assert manifest["page"]["space_id"] == "7"
    write_browser_record(module, workspace)
    completion = module.validate_completion_gate(workspace)
    assert completion["status"] == "verified", completion
    assert completion["api_checks"] == len(report["checks"])
    assert completion["browser_checks"] == 1
    assert completion["screenshots"] == 2

    journal_path = workspace / module.VERIFY_DIR / module.JOURNAL_NAME
    journal = module.load_json(journal_path)
    render_step = next(
        item for item in journal["steps"] if item["id"] == "remote-render-preflight"
    )
    render_step["detail"]["render_safety"] = {
        "status": "failed",
        "unknown_macro_placeholders": 1,
        "signals_found": ["class-token"],
    }
    module.write_json(journal_path, journal)
    tampered_completion = module.validate_completion_gate(workspace)
    assert tampered_completion["status"] == "failed"
    assert (
        "mutation journal remote render preflight is not completed"
        in tampered_completion["errors"]
    )


def test_remote_render_preflight_failure_blocks_attachments_and_page_put(
    tmp_path: Path,
) -> None:
    module = load_script()

    class FailedRenderClient(FakeClient):
        def preflight_storage_render(
            self,
            page_id: str,
            storage: str,
        ) -> dict[str, Any]:
            assert page_id == "42"
            assert "New content" in storage
            self.render_preflight_calls += 1
            raise module.RemoteRenderPreflightError(
                "Confluence remote render preflight produced an unknown-macro placeholder",
                {
                    "status": "failed",
                    "unknown_macro_placeholders": 1,
                    "signals_found": ["class-token", "placeholder-path"],
                },
            )

    client = FailedRenderClient()
    workspace = tmp_path / "page"
    module.download_page(client, "42", workspace)
    storage = (workspace / module.STORAGE_NAME).read_text(encoding="utf-8")
    (workspace / module.STORAGE_NAME).write_text(
        storage.replace("Old content", "New content"),
        encoding="utf-8",
    )
    (workspace / module.ATTACHMENTS_DIR / "old.png").write_bytes(b"replacement")
    module.capture_ground_truth(workspace)

    result = module.upload_workspace(client, workspace, message="Blocked render")

    assert result["status"] == "failed"
    assert result["page_updated"] is False
    assert result["attachments"] == []
    assert result["remote_render_preflight"] == {
        "status": "failed",
        "reason": "unknown-macro-placeholder",
        "render_safety": {
            "status": "failed",
            "unknown_macro_placeholders": 1,
            "signals_found": ["class-token", "placeholder-path"],
        },
    }
    assert client.render_preflight_calls == 1
    assert client.upload_calls == []
    assert client.page_updates == 0
    journal = module.load_json(
        workspace / module.VERIFY_DIR / module.JOURNAL_NAME
    )
    step = next(
        item for item in journal["steps"] if item["id"] == "remote-render-preflight"
    )
    assert step["status"] == "failed"
    assert step["detail"] == result["remote_render_preflight"]
    serialized = json.dumps({"result": result, "journal": journal})
    assert "definitely-not-a-real-confluence-macro" not in serialized


def test_post_upload_verification_rejects_unknown_macro_remote_view(
    tmp_path: Path,
) -> None:
    module = load_script()

    class UnsafeFinalViewClient(FakeClient):
        def update_page(
            self,
            page_id: str,
            meta: dict[str, Any],
            storage: str,
            version: int,
            message: str,
        ) -> dict[str, Any]:
            result = super().update_page(page_id, meta, storage, version, message)
            self.view = (
                '<img class="wysiwyg-unknown-macro" '
                'src="/wiki/plugins/servlet/confluence/placeholder/unknown-macro" />'
            )
            return result

    client = UnsafeFinalViewClient()
    workspace = tmp_path / "unsafe-final-view"
    module.download_page(client, "42", workspace)
    storage_path = workspace / module.STORAGE_NAME
    storage_path.write_text(
        storage_path.read_text(encoding="utf-8").replace(
            "Old content", "New content"
        ),
        encoding="utf-8",
    )
    module.capture_ground_truth(workspace)

    result = module.upload_workspace(client, workspace, message="Unsafe final view")

    assert result["status"] == "verification-failed"
    assert result["verification"]["status"] == "failed"
    safety_check = next(
        check
        for check in result["verification"]["checks"]
        if check["name"] == "view-render-safety"
    )
    assert safety_check == {
        "name": "view-render-safety",
        "passed": False,
        "detail": {
            "status": "failed",
            "unknown_macro_placeholders": 1,
            "signals_found": ["class-token", "placeholder-path"],
        },
    }


def test_completion_gate_scans_legacy_remote_view_evidence_for_placeholders(
    tmp_path: Path,
) -> None:
    module, _client, workspace = make_verified_workspace(tmp_path)
    verification = workspace / module.VERIFY_DIR
    remote_view_path = verification / module.REMOTE_VIEW_NAME
    remote_view_path.write_text(
        '<img class="wysiwyg-unknown-macro" '
        'src="/wiki/plugins/servlet/confluence/placeholder/unknown-macro" />',
        encoding="utf-8",
    )
    report_path = verification / module.REPORT_NAME
    report = module.load_json(report_path)
    report["checks"] = [
        check
        for check in report["checks"]
        if check["name"] != "view-render-safety"
    ]
    report["evidence"]["view"]["sha256"] = module.sha256_bytes(
        remote_view_path.read_bytes()
    )
    module.write_json(report_path, report)
    browser_path = verification / module.BROWSER_GT_NAME
    browser = module.load_json(browser_path)
    browser["api_report_sha256"] = module.sha256_bytes(report_path.read_bytes())
    module.write_json(browser_path, browser)

    completion = module.validate_completion_gate(workspace)

    assert completion["status"] == "failed"
    assert (
        "API verified remote view contains an unknown-macro placeholder"
        in completion["errors"]
    )


def test_legacy_render_safety_reconciliation_is_exact_and_tamper_evident(
    tmp_path: Path,
) -> None:
    module = load_script()
    client = FakeClient()
    workspace = tmp_path / "legacy-render-safety"
    module.download_page(client, "42", workspace)
    storage_path = workspace / module.STORAGE_NAME
    storage_path.write_text(
        storage_path.read_text(encoding="utf-8").replace(
            "Old content", "New content"
        ),
        encoding="utf-8",
    )
    module.capture_ground_truth(workspace)

    result = module.upload_workspace(client, workspace, message="Legacy fixture")
    assert result["status"] == "uploaded", result
    write_browser_record(module, workspace)
    assert module.validate_completion_gate(workspace)["status"] == "verified"

    verification = workspace / module.VERIFY_DIR
    reconciliation_path = (
        verification / module.RENDER_SAFETY_RECONCILIATION_NAME
    )
    module.write_json(reconciliation_path, {})
    current_contract_gate = module.validate_completion_gate(workspace)
    assert current_contract_gate["status"] == "failed"
    assert (
        "mutation journal remote render preflight has unexpected legacy reconciliation"
        in current_contract_gate["errors"]
    )
    reconciliation_path.unlink()

    journal_path = verification / module.JOURNAL_NAME
    journal = module.load_json(journal_path)
    assert journal.pop("remote_render_safety_contract_version") == 1
    render_step = next(
        item for item in journal["steps"] if item["id"] == "remote-render-preflight"
    )
    assert render_step["detail"].pop("render_safety")["status"] == "passed"
    module.write_json(journal_path, journal)

    upload_receipt = json.loads(json.dumps(result))
    assert upload_receipt["remote_render_preflight"].pop("render_safety")[
        "status"
    ] == "passed"
    module.write_json(verification / "upload.json", upload_receipt)
    historical_journal_sha256 = module.sha256_bytes(journal_path.read_bytes())

    legacy_gate = module.validate_completion_gate(workspace)
    assert legacy_gate["status"] == "failed"
    assert (
        "mutation journal remote render preflight has no valid legacy safety reconciliation"
        in legacy_gate["errors"]
    )

    original_page = client.page
    original_version = client.version
    reconciliation_page_calls = 0

    def racing_page(page_id: str, representation: str = "storage") -> dict[str, Any]:
        nonlocal reconciliation_page_calls
        if representation == "storage":
            reconciliation_page_calls += 1
            if reconciliation_page_calls == 2:
                client.version += 1
        return original_page(page_id, representation)

    client.page = racing_page  # type: ignore[method-assign]
    with pytest.raises(module.ConflictError, match="remote page changed"):
        module.reconcile_remote_render_safety(client, workspace)
    assert not reconciliation_path.exists()
    client.page = original_page  # type: ignore[method-assign]
    client.version = original_version

    reconciled = module.reconcile_remote_render_safety(client, workspace)

    assert reconciled["status"] == "reconciled"
    assert module.sha256_bytes(journal_path.read_bytes()) == historical_journal_sha256
    artifact = module.load_json(reconciliation_path)
    assert artifact["page_mutated"] is False
    assert artifact["digest_match"] is True
    assert artifact["historical_journal"]["sha256"] == historical_journal_sha256
    assert artifact["fresh_remote_render"]["render_safety"] == {
        "status": "passed",
        "unknown_macro_placeholders": 0,
        "signals_found": [],
    }
    assert module.validate_completion_gate(workspace)["status"] == "verified"

    artifact["fresh_remote_render"]["render_safety"]["status"] = "failed"
    module.write_json(reconciliation_path, artifact)
    tampered_gate = module.validate_completion_gate(workspace)
    assert tampered_gate["status"] == "failed"
    assert (
        "mutation journal remote render preflight has no valid legacy safety reconciliation"
        in tampered_gate["errors"]
    )


def test_title_only_page_update_does_not_queue_storage_render(tmp_path: Path) -> None:
    module = load_script()
    client = FakeClient()
    workspace = tmp_path / "title-only"
    module.download_page(client, "42", workspace)
    meta = module.load_json(workspace / module.META_NAME)
    meta["title"] = "Changed title only"
    module.write_json(workspace / module.META_NAME, meta)
    module.capture_ground_truth(workspace)

    result = module.upload_workspace(client, workspace, message="Title only")

    assert result["status"] == "uploaded"
    assert result["page_updated"] is True
    assert result["remote_render_preflight"] == {"status": "not-required"}
    assert client.render_preflight_calls == 0


def test_conflict_and_missing_attachment_are_blocked(tmp_path: Path) -> None:
    module = load_script()
    client = FakeClient()
    workspace = tmp_path / "page"
    module.download_page(client, "42", workspace)

    storage = (workspace / module.STORAGE_NAME).read_text(encoding="utf-8")
    storage += '<ac:image><ri:attachment ri:filename="missing.png" /></ac:image>'
    (workspace / module.STORAGE_NAME).write_text(storage, encoding="utf-8")
    with pytest.raises(module.ValidationError, match="unavailable attachments"):
        module.validate_workspace(workspace)

    (workspace / "attachments" / "missing.png").write_bytes(b"present")
    with pytest.raises(module.ValidationError, match="ground truth is stale"):
        module.validate_workspace(workspace)
    module.capture_ground_truth(workspace)
    client.version += 1
    with pytest.raises(module.ConflictError, match="download again"):
        module.upload_plan(client, workspace)
    plan, _, _ = module.upload_plan(client, workspace, force=True)
    assert plan["forced"] is True


def test_attachment_version_conflict_requires_reviewed_force(tmp_path: Path) -> None:
    module = load_script()

    class AttachmentVersionClient(FakeClient):
        attachment_version = 1

        def attachments(self, page_id: str) -> list[dict[str, Any]]:
            items = super().attachments(page_id)
            for item in items:
                item["version"] = {"number": self.attachment_version}
            return items

    client = AttachmentVersionClient()
    workspace = tmp_path / "page"
    module.download_page(client, "42", workspace)
    client.attachment_version = 2
    (workspace / "attachments" / "old.png").write_bytes(b"local replacement")
    module.capture_ground_truth(workspace)

    with pytest.raises(module.ConflictError, match="remote attachment version changed"):
        module.upload_plan(client, workspace)

    plan, _, _ = module.upload_plan(client, workspace, force=True)
    assert plan["attachments"][0]["action"] == "update"


def test_attachment_lock_is_rechecked_immediately_before_upload(tmp_path: Path) -> None:
    module = load_script()

    class RacingAttachmentClient(FakeClient):
        def __init__(self) -> None:
            super().__init__()
            self.attachment_version = 1
            self.attachment_list_calls = 0

        def attachments(self, page_id: str) -> list[dict[str, Any]]:
            self.attachment_list_calls += 1
            if self.attachment_list_calls == 3:
                self.attachment_version = 2
                self.attachment_bytes["old.png"] = b"concurrent-writer"
            results = super().attachments(page_id)
            for item in results:
                item["version"] = {"number": self.attachment_version}
            return results

    client = RacingAttachmentClient()
    workspace = tmp_path / "attachment-race"
    module.download_page(client, "42", workspace)
    local = workspace / module.ATTACHMENTS_DIR / "old.png"
    local.write_bytes(b"reviewed-local-change")
    module.capture_ground_truth(workspace)

    result = module.upload_workspace(client, workspace, message="Race test")

    assert result["status"] == "failed"
    assert result["error"]["type"] == "ConflictError"
    assert client.upload_calls == []
    assert client.attachment_bytes["old.png"] == b"concurrent-writer"


def test_new_local_attachment_cannot_overwrite_untracked_remote_collision(tmp_path: Path) -> None:
    module = load_script()
    client = FakeClient()
    workspace = tmp_path / "page"
    module.download_page(client, "42", workspace)
    client.attachment_bytes["collision.png"] = b"remote bytes"
    client.attachment_ids["collision.png"] = "remote-id"
    (workspace / "attachments" / "collision.png").write_bytes(b"local bytes")
    module.capture_ground_truth(workspace)

    with pytest.raises(module.ConflictError, match="collides with an attachment created remotely"):
        module.upload_plan(client, workspace)


def test_manifest_known_attachment_requires_local_bytes(tmp_path: Path) -> None:
    module = load_script()
    client = FakeClient()
    workspace = tmp_path / "page"
    module.download_page(client, "42", workspace)

    (workspace / module.ATTACHMENTS_DIR / "old.png").unlink()

    with pytest.raises(module.ValidationError, match="manifest attachments are missing local bytes"):
        module.validate_workspace(workspace)


def test_legacy_manifest_location_fields_are_portable_but_cannot_authorize_a_move(
    tmp_path: Path,
) -> None:
    module = load_script()
    client = FakeClient()
    workspace = tmp_path / "page"
    module.download_page(client, "42", workspace)
    manifest = module.load_json(workspace / module.MANIFEST_NAME)
    for field in ("space_id", "parent_id", "status", "subtype"):
        manifest["page"].pop(field)
    module.write_json(workspace / module.MANIFEST_NAME, manifest)

    assert module.validate_workspace(workspace)["status"] == "valid"

    meta = module.load_json(workspace / module.META_NAME)
    meta["parent_id"] = "99"
    module.write_json(workspace / module.META_NAME, meta)
    module.capture_ground_truth(workspace)
    with pytest.raises(module.ConflictError, match="remote parent_id changed"):
        module.upload_plan(client, workspace, force=True)


def test_manifest_local_new_attachment_placeholder_is_planned_as_create(tmp_path: Path) -> None:
    module = load_script()
    client = FakeClient()
    workspace = tmp_path / "page"
    module.download_page(client, "42", workspace)
    new_attachment = workspace / module.ATTACHMENTS_DIR / "release-architecture.svg"
    new_attachment.write_bytes(b"<svg />")
    storage = (workspace / module.STORAGE_NAME).read_text(encoding="utf-8")
    (workspace / module.STORAGE_NAME).write_text(
        storage
        + '<ac:image><ri:attachment ri:filename="release-architecture.svg" /></ac:image>',
        encoding="utf-8",
    )
    manifest = module.load_json(workspace / module.MANIFEST_NAME)
    manifest["attachments"].append(
        {
            "id": "",
            "filename": new_attachment.name,
            "path": f"attachments/{new_attachment.name}",
            "media_type": "image/svg+xml",
            "file_size": new_attachment.stat().st_size,
            "version": None,
        }
    )
    module.write_json(workspace / module.MANIFEST_NAME, manifest)
    module.capture_ground_truth(workspace)

    plan, _, _ = module.upload_plan(client, workspace)

    assert plan["attachments"] == [
        {
            "filename": new_attachment.name,
            "action": "create",
            "sha256": module.sha256_bytes(new_attachment.read_bytes()),
            "media_type": "image/svg+xml",
        }
    ]


@pytest.mark.parametrize(
    "attachment_id, version",
    [("a1", None), ("", 1)],
)
def test_manifest_rejects_incomplete_attachment_version_locks(
    tmp_path: Path,
    attachment_id: str,
    version: int | None,
) -> None:
    module = load_script()
    workspace = tmp_path / "page"
    module.download_page(FakeClient(), "42", workspace)
    manifest = module.load_json(workspace / module.MANIFEST_NAME)
    manifest["attachments"][0]["id"] = attachment_id
    manifest["attachments"][0]["version"] = version
    module.write_json(workspace / module.MANIFEST_NAME, manifest)

    with pytest.raises(module.ValidationError, match="incomplete remote version lock"):
        module.validate_workspace(workspace)


@pytest.mark.parametrize("required_name", ["page.view.html", "page.restrictions.json"])
def test_validation_requires_read_only_evidence_files(tmp_path: Path, required_name: str) -> None:
    module = load_script()
    workspace = tmp_path / "page"
    module.download_page(FakeClient(), "42", workspace)
    (workspace / required_name).unlink()

    with pytest.raises(module.ValidationError, match="workspace is missing required files"):
        module.validate_workspace(workspace)


def test_validation_rejects_invalid_xml_and_unsafe_filenames(tmp_path: Path) -> None:
    module = load_script()
    with pytest.raises(module.ValidationError, match="unsafe attachment"):
        module.safe_filename("../secret.txt")
    with pytest.raises(module.ValidationError, match="well-formed"):
        module.canonical_storage("<p>broken")
    assert module.normalize_base_url("https://example.atlassian.net/wiki") == "https://example.atlassian.net"
    with pytest.raises(module.ValidationError, match="site root"):
        module.normalize_base_url("https://example.atlassian.net/wiki/spaces/X")


@pytest.mark.parametrize(
    "filename",
    ["CON", "aux.txt", "report?.png", "trailing.", "trailing ", "x" * 241],
)
def test_attachment_filenames_must_be_portable_on_windows(filename: str) -> None:
    module = load_script()

    with pytest.raises(module.ValidationError, match="unsafe attachment filename"):
        module.safe_filename(filename)

    assert module.safe_filename("release architecture.png") == "release architecture.png"


def test_download_rejects_case_insensitive_attachment_collisions(tmp_path: Path) -> None:
    module = load_script()
    client = FakeClient()
    client.attachment_bytes.update({"Diagram.png": b"one", "diagram.png": b"two"})
    client.attachment_ids.update({"Diagram.png": "a2", "diagram.png": "a3"})

    with pytest.raises(module.ValidationError, match="collide on case-insensitive filesystems"):
        module.download_page(client, "42", tmp_path / "page")


def test_skip_attachments_rejects_pages_with_remote_attachments(tmp_path: Path) -> None:
    module = load_script()
    output = tmp_path / "page"

    with pytest.raises(
        module.ValidationError,
        match=r"--skip-attachments.*run scan.*full download",
    ):
        module.download_page(FakeClient(), "42", output, include_attachments=False)

    assert not output.exists()


def test_skip_attachments_allows_attachment_free_pages(tmp_path: Path) -> None:
    module = load_script()
    client = FakeClient()
    client.storage = "<h1>Fixture</h1><p>No remote attachments</p>"
    client.attachment_bytes.clear()
    client.attachment_ids.clear()
    output = tmp_path / "page"

    result = module.download_page(client, "42", output, include_attachments=False)

    assert result["attachments"] == 0
    assert module.validate_workspace(output)["status"] == "valid"


def test_download_rejects_existing_symlink_target_before_overwrite(tmp_path: Path) -> None:
    module = load_script()
    real_target = tmp_path / "real-target"
    real_target.mkdir()
    output = tmp_path / "page-link"
    make_symlink_or_skip(output, real_target, target_is_directory=True)

    with pytest.raises(module.ValidationError, match="workspace output.*symbolic link"):
        module.download_page(FakeClient(), "42", output, overwrite=True)


def test_validate_rejects_symlink_workspace_root(tmp_path: Path) -> None:
    module = load_script()
    workspace = tmp_path / "page"
    module.download_page(FakeClient(), "42", workspace)
    linked_workspace = tmp_path / "linked-page"
    make_symlink_or_skip(linked_workspace, workspace, target_is_directory=True)

    with pytest.raises(module.ValidationError, match="workspace root.*symbolic link"):
        module.validate_workspace(linked_workspace)


def test_validate_rejects_symlink_required_sidecar(tmp_path: Path) -> None:
    module = load_script()
    workspace = tmp_path / "page"
    module.download_page(FakeClient(), "42", workspace)
    external = tmp_path / "external.storage.xml"
    external.write_text("<p>external</p>", encoding="utf-8")
    sidecar = workspace / module.STORAGE_NAME
    sidecar.unlink()
    make_symlink_or_skip(sidecar, external)

    with pytest.raises(module.ValidationError, match=r"page\.storage\.xml.*symbolic link"):
        module.validate_workspace(workspace)


def test_validate_rejects_symlink_attachment_entry(tmp_path: Path) -> None:
    module = load_script()
    workspace = tmp_path / "page"
    module.download_page(FakeClient(), "42", workspace)
    external = tmp_path / "external.png"
    external.write_bytes(b"external")
    attachment = workspace / module.ATTACHMENTS_DIR / "old.png"
    attachment.unlink()
    make_symlink_or_skip(attachment, external)

    with pytest.raises(module.ValidationError, match="attachment entry.*symbolic link"):
        module.validate_workspace(workspace)


def test_verify_rejects_symlinked_verification_directory_without_touching_target(
    tmp_path: Path,
) -> None:
    module = load_script()
    workspace = tmp_path / "page"
    module.download_page(FakeClient(), "42", workspace)
    victim = tmp_path / "victim"
    victim.mkdir()
    victim_report = victim / module.REPORT_NAME
    victim_report.write_text("do not overwrite", encoding="utf-8")
    make_symlink_or_skip(
        workspace / module.VERIFY_DIR,
        victim,
        target_is_directory=True,
    )

    with pytest.raises(module.ValidationError, match="verification directory"):
        module.verify_workspace(FakeClient(), workspace)

    assert victim_report.read_text(encoding="utf-8") == "do not overwrite"
    assert sorted(path.name for path in victim.iterdir()) == [module.REPORT_NAME]


@pytest.mark.parametrize(
    "page_id",
    ["", "0", "-1", "01", "42/attachments", "42?expand=body", " 42", "1.0", "٤٢"],
)
def test_page_ids_must_be_canonical_positive_ascii_numbers(page_id: str) -> None:
    module = load_script()

    with pytest.raises(module.ValidationError, match="positive numeric ID"):
        module.validate_page_id(page_id)


def test_all_client_page_endpoints_reject_path_injection_before_request(tmp_path: Path) -> None:
    module = load_script()
    client = module.ConfluenceClient(
        "https://example.atlassian.net", "user@example.com", "secret"
    )
    attachment = tmp_path / "file.txt"
    attachment.write_text("safe", encoding="utf-8")
    request_calls = 0

    def forbidden_request(*_args: Any, **_kwargs: Any) -> None:
        nonlocal request_calls
        request_calls += 1
        raise AssertionError("an invalid page ID must be rejected before a request")

    client.session.request = forbidden_request  # type: ignore[method-assign]
    page_id = "42/../../spaces"
    invocations = [
        lambda: client.page(page_id),
        lambda: client.draft_page(page_id),
        lambda: client.attachments(page_id),
        lambda: client.labels(page_id),
        lambda: client.content_state(page_id),
        lambda: client.restrictions(page_id),
        lambda: client.upload_attachment(page_id, attachment, None, comment="test"),
        lambda: client.update_page(
            page_id,
            {"title": "Safe"},
            "<p>Safe</p>",
            1,
            "test",
        ),
        lambda: client.sync_labels(page_id, [], []),
        lambda: client.set_content_state(page_id, None, None),
    ]

    for invoke in invocations:
        with pytest.raises(module.ValidationError, match="positive numeric ID"):
            invoke()
    assert request_calls == 0


@pytest.mark.parametrize(
    ("method_name", "resource"),
    [("attachments", "attachments"), ("labels", "labels")],
)
def test_page_collection_pagination_rejects_repeated_url(
    method_name: str,
    resource: str,
) -> None:
    module = load_script()
    client = module.ConfluenceClient(
        "https://example.atlassian.net", "user@example.com", "secret"
    )
    calls = 0
    repeated = f"https://example.atlassian.net/wiki/api/v2/pages/42/{resource}"

    def repeated_page(_method: str, _path: str, **_kwargs: Any) -> dict[str, Any]:
        nonlocal calls
        calls += 1
        return {"results": [], "_links": {"next": repeated}}

    client.json = repeated_page  # type: ignore[method-assign]

    with pytest.raises(module.RoundTripError, match="pagination repeated a page URL"):
        getattr(client, method_name)("42")

    assert calls == 1


def test_workspace_rejects_non_numeric_page_id_before_remote_use(tmp_path: Path) -> None:
    module = load_script()
    workspace = tmp_path / "page"
    module.download_page(FakeClient(), "42", workspace)
    meta = module.load_json(workspace / module.META_NAME)
    manifest = module.load_json(workspace / module.MANIFEST_NAME)
    meta["page_id"] = "42/labels"
    manifest["page"]["page_id"] = "42/labels"
    module.write_json(workspace / module.META_NAME, meta)
    module.write_json(workspace / module.MANIFEST_NAME, manifest)

    with pytest.raises(module.ValidationError, match="positive numeric ID"):
        module.validate_workspace(workspace)


def test_draft_page_requests_the_v2_draft_aware_storage_snapshot() -> None:
    module = load_script()
    client = module.ConfluenceClient(
        "https://example.atlassian.net", "user@example.com", "secret"
    )
    captured: dict[str, Any] = {}

    def record_json(method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        captured.update({"method": method, "path": path, **kwargs})
        return {}

    client.json = record_json  # type: ignore[method-assign]

    client.draft_page("42")

    assert captured["method"] == "GET"
    assert captured["path"] == "/wiki/api/v2/pages/42"
    assert captured["params"]["body-format"] == "storage"
    assert captured["params"]["get-draft"] == "true"


def test_async_storage_render_preflight_queues_and_polls_without_returning_task_id() -> None:
    module = load_script()
    sleeps: list[float] = []
    client = module.ConfluenceClient(
        "https://example.atlassian.net",
        "user@example.com",
        "secret",
        sleep=sleeps.append,
    )
    async_id = "ari:cloud:confluence:account/secret-account-id"
    responses = iter(
        [
            {"asyncId": async_id},
            {"status": "WORKING"},
            {
                "status": "COMPLETED",
                "representation": "view",
                "value": "<p>Rendered</p>",
                "renderTaskId": async_id,
            },
        ]
    )
    calls: list[tuple[str, str, dict[str, Any]]] = []

    class Response:
        def __init__(self, payload: dict[str, Any]) -> None:
            self.payload = payload

        def json(self) -> dict[str, Any]:
            return self.payload

    def respond(method: str, path: str, **kwargs: Any) -> Response:
        calls.append((method, path, kwargs))
        return Response(next(responses))

    client.request = respond  # type: ignore[method-assign]

    result = client.preflight_storage_render(
        "42",
        "<p>Candidate</p>",
        max_polls=3,
        poll_interval=0.01,
        timeout_seconds=5,
    )

    assert result == {
        "status": "completed",
        "representation": "view",
        "rendered_sha256": module.sha256_text("<p>Rendered</p>"),
        "rendered_bytes": len("<p>Rendered</p>".encode("utf-8")),
        "polls": 2,
        "render_safety": {
            "status": "passed",
            "unknown_macro_placeholders": 0,
            "signals_found": [],
        },
    }
    assert async_id not in json.dumps(result)
    assert calls[0][0:2] == (
        "POST",
        "/wiki/rest/api/contentbody/convert/async/view",
    )
    assert calls[0][2]["params"] == {
        "contentIdContext": "42",
        "allowCache": "false",
    }
    assert calls[0][2]["json"] == {
        "value": "<p>Candidate</p>",
        "representation": "storage",
    }
    assert calls[1][2]["redact_path"] is True
    assert calls[2][2]["redact_path"] is True
    assert sleeps == [0.01]


def test_rendered_view_safety_detects_only_structural_unknown_macro_markers() -> None:
    module = load_script()
    unknown = module.rendered_view_safety(
        '<img class="image wysiwyg-unknown-macro" '
        'src="https://example.atlassian.net/wiki/plugins/servlet/confluence/'
        'placeholder/unknown-macro?name=obsolete" />'
    )
    valid_warning = module.rendered_view_safety(
        '<div class="aui-message warning"><span class="aui-icon '
        'aui-iconfont-error"></span>Valid warning panel</div>'
        '<a href="/placeholder/unknown-macro-help">Documentation</a>'
    )
    encoded_path = module.rendered_view_safety(
        '<img src="/wiki/placeholder%2Funknown-macro?name=obsolete" />'
    )

    assert unknown == {
        "status": "failed",
        "unknown_macro_placeholders": 1,
        "signals_found": ["class-token", "placeholder-path"],
    }
    assert valid_warning == {
        "status": "passed",
        "unknown_macro_placeholders": 0,
        "signals_found": [],
    }
    assert encoded_path == {
        "status": "failed",
        "unknown_macro_placeholders": 1,
        "signals_found": ["placeholder-path"],
    }


def test_async_storage_render_rejects_completed_unknown_macro_placeholder() -> None:
    module = load_script()
    client = module.ConfluenceClient(
        "https://example.atlassian.net", "user@example.com", "secret"
    )
    async_id = "account-id-that-must-not-leak"
    macro_name = "definitely-not-a-real-confluence-macro"
    responses = iter(
        [
            {"asyncId": async_id},
            {
                "status": "COMPLETED",
                "representation": "view",
                "value": (
                    '<img class="wysiwyg-unknown-macro" '
                    'src="/wiki/plugins/servlet/confluence/placeholder/'
                    f'unknown-macro?name={macro_name}" />'
                ),
            },
        ]
    )

    class Response:
        def json(self) -> dict[str, Any]:
            return next(responses)

    client.request = lambda *_args, **_kwargs: Response()  # type: ignore[method-assign]

    with pytest.raises(module.RemoteRenderPreflightError) as raised:
        client.preflight_storage_render("42", "<p>Candidate</p>")

    assert raised.value.diagnostic == {
        "status": "failed",
        "unknown_macro_placeholders": 1,
        "signals_found": ["class-token", "placeholder-path"],
    }
    assert async_id not in str(raised.value)
    assert macro_name not in str(raised.value)


@pytest.mark.parametrize(
    ("responses", "expected"),
    [
        (
            [
                {"asyncId": "secret-task", "error": "queue failed secret-task"},
            ],
            "failed to queue",
        ),
        (
            [
                {"asyncId": "secret-task"},
                {
                    "status": "COMPLETED",
                    "representation": "view",
                    "value": "<p>Apparently valid</p>",
                    "error": "conversion failed secret-task",
                },
            ],
            "remote render preflight failed",
        ),
    ],
)
def test_async_storage_render_rejects_any_service_error_even_with_result(
    responses: list[dict[str, Any]],
    expected: str,
) -> None:
    module = load_script()
    client = module.ConfluenceClient(
        "https://example.atlassian.net", "user@example.com", "secret"
    )
    payloads = iter(responses)

    class Response:
        def json(self) -> dict[str, Any]:
            return next(payloads)

    client.request = lambda *_args, **_kwargs: Response()  # type: ignore[method-assign]

    with pytest.raises(module.RoundTripError, match=expected) as raised:
        client.preflight_storage_render("42", "<p>Candidate</p>")

    assert "secret-task" not in str(raised.value)


def test_async_storage_render_preflight_redacts_failure_and_is_bounded() -> None:
    module = load_script()
    async_id = "account-id-that-must-not-leak"

    class Response:
        def __init__(self, payload: dict[str, Any]) -> None:
            self.payload = payload

        def json(self) -> dict[str, Any]:
            return self.payload

    for poll_payload, expected in (
        (
            {"status": "FAILED", "error": f"bad task {async_id}"},
            "remote render preflight failed",
        ),
        ({"status": "WORKING"}, "bounded polling window"),
    ):
        client = module.ConfluenceClient(
            "https://example.atlassian.net",
            "user@example.com",
            "secret",
            sleep=lambda _seconds: None,
        )
        calls = 0

        def respond(_method: str, _path: str, **_kwargs: Any) -> Response:
            nonlocal calls
            calls += 1
            return Response({"asyncId": async_id} if calls == 1 else poll_payload)

        client.request = respond  # type: ignore[method-assign]

        with pytest.raises(module.RoundTripError, match=expected) as raised:
            client.preflight_storage_render(
                "42",
                "<p>Candidate</p>",
                max_polls=2,
                poll_interval=0,
                timeout_seconds=5,
            )

        assert async_id not in str(raised.value)
        assert calls == (2 if poll_payload["status"] == "FAILED" else 3)


def test_async_poll_http_error_redacts_path_and_response_body() -> None:
    module = load_script()
    client = module.ConfluenceClient(
        "https://example.atlassian.net", "user@example.com", "secret"
    )
    secret_id = "account-id-that-must-not-leak"

    class Response:
        status_code = 403
        url = f"https://example.atlassian.net/wiki/rest/api/contentbody/convert/async/{secret_id}"
        reason = "Forbidden"
        text = secret_id
        headers: dict[str, str] = {}

        def json(self) -> dict[str, str]:
            return {"message": secret_id}

    client.session.request = lambda *_args, **_kwargs: Response()  # type: ignore[method-assign]

    with pytest.raises(module.RoundTripError) as raised:
        client.request(
            "GET",
            f"/wiki/rest/api/contentbody/convert/async/{secret_id}",
            redact_path=True,
        )

    assert str(raised.value) == "Confluence async conversion request returned HTTP 403"
    assert secret_id not in str(raised.value)

    client.session.request = (  # type: ignore[method-assign]
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            module.requests.exceptions.ConnectionError(f"network error for {secret_id}")
        )
    )
    with pytest.raises(module.RoundTripError) as network_failure:
        client.request(
            "GET",
            f"/wiki/rest/api/contentbody/convert/async/{secret_id}",
            redact_path=True,
        )
    assert str(network_failure.value) == (
        "Confluence async conversion request failed before a response"
    )
    assert secret_id not in str(network_failure.value)


@pytest.mark.parametrize(
    "value, error",
    [
        ("http://example.atlassian.net", "absolute HTTPS"),
        ("https://user:secret@example.atlassian.net", "must not contain credentials"),
        ("https://example.atlassian.net:8443", "default HTTPS port"),
        ("https://example.atlassian.net?tenant=other", "query"),
        ("https://example.atlassian.net#fragment", "fragment"),
    ],
)
def test_base_url_rejects_ambiguous_or_credentialed_urls(value: str, error: str) -> None:
    module = load_script()
    with pytest.raises(module.ValidationError, match=error):
        module.normalize_base_url(value)


@pytest.mark.parametrize(
    "path",
    [
        "http://example.atlassian.net/wiki/api/v2/pages/42",
        "//evil.example/wiki/api/v2/pages/42",
        "https://evil.example/wiki/api/v2/pages/42",
        "https://user:secret@example.atlassian.net/wiki/api/v2/pages/42",
        " https://example.atlassian.net/wiki/api/v2/pages/42",
        "\\\\evil.example\\wiki\\api",
    ],
)
def test_client_rejects_unsafe_absolute_and_relative_urls(path: str) -> None:
    module = load_script()
    client = module.ConfluenceClient("https://example.atlassian.net", "user@example.com", "secret")

    with pytest.raises(module.ValidationError):
        client.url(path)


def test_client_accepts_only_same_https_origin_for_absolute_downloads() -> None:
    module = load_script()
    client = module.ConfluenceClient("https://Example.Atlassian.net/wiki", "user@example.com", "secret")

    assert client.url("https://example.atlassian.net:443/download/file.png") == (
        "https://example.atlassian.net:443/download/file.png"
    )
    assert client.url("/wiki/api/v2/pages/42") == "https://example.atlassian.net/wiki/api/v2/pages/42"


def test_get_retries_transient_statuses_with_bounded_retry_after() -> None:
    module = load_script()
    sleeps: list[float] = []
    client = module.ConfluenceClient(
        "https://example.atlassian.net",
        "user@example.com",
        "secret",
        get_retry_attempts=3,
        sleep=sleeps.append,
    )

    class Response:
        def __init__(self, status: int, retry_after: str = "") -> None:
            self.status_code = status
            self.headers = {"Retry-After": retry_after} if retry_after else {}
            self.url = "https://example.atlassian.net/wiki/api/v2/pages/42"
            self.text = "busy"
            self.reason = "busy"

        def json(self) -> dict[str, Any]:
            return {"ok": True} if self.status_code == 200 else {"message": "busy"}

    responses = iter([Response(429, "2"), Response(503, "999"), Response(200)])
    calls: list[str] = []

    def request(method: str, _url: str, **_kwargs: Any) -> Response:
        calls.append(method)
        return next(responses)

    client.session.request = request  # type: ignore[method-assign]
    response = client.request("GET", "/wiki/api/v2/pages/42")

    assert response.status_code == 200
    assert calls == ["GET", "GET", "GET"]
    assert sleeps == [2.0, 0.5]


@pytest.mark.parametrize("status", [429, 502, 503, 504])
def test_get_retries_each_supported_transient_status(status: int) -> None:
    module = load_script()
    client = module.ConfluenceClient(
        "https://example.atlassian.net",
        "user@example.com",
        "secret",
        get_retry_attempts=2,
        sleep=lambda _seconds: None,
    )

    class Response:
        def __init__(self, response_status: int) -> None:
            self.status_code = response_status
            self.headers: dict[str, str] = {}
            self.url = "https://example.atlassian.net/wiki/api/v2/pages/42"
            self.text = "busy"
            self.reason = "busy"

        def json(self) -> dict[str, Any]:
            return {"ok": True}

    responses = iter([Response(status), Response(200)])
    calls = 0

    def request(*_args: Any, **_kwargs: Any) -> Response:
        nonlocal calls
        calls += 1
        return next(responses)

    client.session.request = request  # type: ignore[method-assign]
    assert client.request("GET", "/wiki/api/v2/pages/42").status_code == 200
    assert calls == 2


def test_get_retry_attempts_have_a_hard_upper_bound() -> None:
    module = load_script()

    with pytest.raises(module.ValidationError, match="between one and 5"):
        module.ConfluenceClient(
            "https://example.atlassian.net",
            "user@example.com",
            "secret",
            get_retry_attempts=6,
        )


def test_mutation_requests_are_never_automatically_retried() -> None:
    module = load_script()
    sleeps: list[float] = []
    client = module.ConfluenceClient(
        "https://example.atlassian.net",
        "user@example.com",
        "secret",
        get_retry_attempts=5,
        sleep=sleeps.append,
    )

    class Response:
        status_code = 503
        headers = {"Retry-After": "0"}
        url = "https://example.atlassian.net/wiki/api/v2/pages/42"
        text = "busy"
        reason = "busy"

        def json(self) -> dict[str, str]:
            return {"message": "busy"}

    calls = 0

    def request(*_args: Any, **_kwargs: Any) -> Response:
        nonlocal calls
        calls += 1
        return Response()

    client.session.request = request  # type: ignore[method-assign]
    with pytest.raises(module.RoundTripError, match="HTTP 503"):
        client.request("PUT", "/wiki/api/v2/pages/42", json={"title": "Safe"})

    assert calls == 1
    assert sleeps == []


def test_cross_tenant_workspace_is_rejected_before_remote_page_request(tmp_path: Path) -> None:
    module = load_script()
    client = FakeClient()
    workspace = tmp_path / "page"
    module.download_page(client, "42", workspace)
    client.base_url = "https://other.atlassian.net"
    called = False

    def forbidden_page(*_args: Any, **_kwargs: Any) -> dict[str, Any]:
        nonlocal called
        called = True
        raise AssertionError("page request must not happen")

    client.page = forbidden_page  # type: ignore[method-assign]
    with pytest.raises(module.ValidationError, match="different Confluence tenant"):
        module.upload_plan(client, workspace)
    assert called is False


def test_cross_tenant_verification_is_rejected_before_remote_page_request(tmp_path: Path) -> None:
    module = load_script()
    client = FakeClient()
    workspace = tmp_path / "page"
    module.download_page(client, "42", workspace)
    client.base_url = "https://other.atlassian.net"
    called = False

    def forbidden_page(*_args: Any, **_kwargs: Any) -> dict[str, Any]:
        nonlocal called
        called = True
        raise AssertionError("page request must not happen")

    client.page = forbidden_page  # type: ignore[method-assign]
    with pytest.raises(module.ValidationError, match="different Confluence tenant"):
        module.verify_workspace(client, workspace)
    assert called is False


def test_download_pins_editable_label_and_state_baselines(tmp_path: Path) -> None:
    module = load_script()
    workspace = tmp_path / "page"
    module.download_page(FakeClient(), "42", workspace)

    manifest = module.load_json(workspace / module.MANIFEST_NAME)

    assert manifest["editable_baselines"] == {
        "global_labels": ["alpha"],
        "content_state": {"id": 1, "name": "Draft", "color": "YELLOW"},
    }


def test_workspace_validates_editable_baseline_lock_format(tmp_path: Path) -> None:
    module = load_script()
    workspace = tmp_path / "page"
    module.download_page(FakeClient(), "42", workspace)
    manifest = module.load_json(workspace / module.MANIFEST_NAME)
    manifest["editable_baselines"]["global_labels"] = "alpha"
    module.write_json(workspace / module.MANIFEST_NAME, manifest)

    with pytest.raises(
        module.ValidationError,
        match="editable_baselines.global_labels.*unique non-empty strings",
    ):
        module.validate_workspace(workspace)


def test_legacy_manifest_without_editable_baselines_is_upgraded_after_verification(
    tmp_path: Path,
) -> None:
    module = load_script()
    client = FakeClient()
    workspace = tmp_path / "legacy-page"
    module.download_page(client, "42", workspace)
    manifest = module.load_json(workspace / module.MANIFEST_NAME)
    manifest.pop("editable_baselines")
    module.write_json(workspace / module.MANIFEST_NAME, manifest)

    assert module.validate_workspace(workspace)["status"] == "valid"
    result = module.upload_workspace(client, workspace, message="Upgrade legacy lock")

    assert result["status"] == "uploaded", result
    refreshed = module.load_json(workspace / module.MANIFEST_NAME)
    assert refreshed["editable_baselines"] == {
        "global_labels": ["alpha"],
        "content_state": client.state,
    }


def test_remote_label_baseline_conflict_requires_force_and_journals_before_after(
    tmp_path: Path,
) -> None:
    module = load_script()
    client = FakeClient()
    workspace = tmp_path / "label-lock"
    module.download_page(client, "42", workspace)
    module.write_json(workspace / module.LABELS_NAME, ["alpha", "beta"])
    module.capture_ground_truth(workspace)
    client.label_names = ["concurrent"]

    with pytest.raises(module.ConflictError, match="global labels changed after download"):
        module.upload_plan(client, workspace)
    assert client.page_updates == 0
    assert client.upload_calls == []

    result = module.upload_workspace(
        client, workspace, message="Reviewed forced label update", force=True
    )

    assert result["status"] == "uploaded", result
    journal = module.load_json(workspace / module.VERIFY_DIR / module.JOURNAL_NAME)
    label_step = next(step for step in journal["steps"] if step["id"] == "labels")
    assert label_step["detail"] == {
        "before": ["concurrent"],
        "after": ["alpha", "beta"],
        "changes": {"added": ["alpha", "beta"], "removed": ["concurrent"]},
    }
    manifest = module.load_json(workspace / module.MANIFEST_NAME)
    assert manifest["editable_baselines"]["global_labels"] == ["alpha", "beta"]


def test_remote_content_state_baseline_conflicts_before_mutation(tmp_path: Path) -> None:
    module = load_script()
    client = FakeClient()
    workspace = tmp_path / "state-lock"
    module.download_page(client, "42", workspace)
    module.write_json(
        workspace / module.STATE_NAME, {"name": "Ready", "color": "GREEN"}
    )
    module.capture_ground_truth(workspace)
    client.state = {"id": 2, "name": "Other", "color": "RED"}

    with pytest.raises(module.ConflictError, match="content state changed after download"):
        module.upload_plan(client, workspace)

    assert client.page_updates == 0
    assert client.upload_calls == []


def test_label_change_between_plan_and_write_is_detected_before_label_mutation(
    tmp_path: Path,
) -> None:
    module = load_script()

    class ConcurrentLabelClient(FakeClient):
        label_sync_calls = 0

        def upload_attachment(
            self,
            page_id: str,
            path: Path,
            existing_id: str | None,
            *,
            comment: str,
            media_type: str | None = None,
        ) -> dict[str, Any]:
            result = super().upload_attachment(
                page_id,
                path,
                existing_id,
                comment=comment,
                media_type=media_type,
            )
            self.label_names = ["concurrent"]
            return result

        def sync_labels(
            self,
            page_id: str,
            desired: list[str],
            current: list[str],
        ) -> dict[str, list[str]]:
            self.label_sync_calls += 1
            return super().sync_labels(page_id, desired, current)

    client = ConcurrentLabelClient()
    workspace = tmp_path / "label-race"
    module.download_page(client, "42", workspace)
    new_attachment = workspace / module.ATTACHMENTS_DIR / "new.png"
    new_attachment.write_bytes(b"new-image")
    storage = (workspace / module.STORAGE_NAME).read_text(encoding="utf-8")
    (workspace / module.STORAGE_NAME).write_text(
        storage + '<ac:image><ri:attachment ri:filename="new.png" /></ac:image>',
        encoding="utf-8",
    )
    module.write_json(workspace / module.LABELS_NAME, ["alpha", "beta"])
    module.capture_ground_truth(workspace)

    result = module.upload_workspace(client, workspace, message="Race detection")

    assert result["status"] == "partial"
    assert result["error"]["type"] == "ConflictError"
    assert "between planning and mutation" in result["error"]["message"]
    assert client.label_sync_calls == 0
    journal = module.load_json(workspace / module.VERIFY_DIR / module.JOURNAL_NAME)
    assert next(step for step in journal["steps"] if step["id"] == "labels")[
        "status"
    ] == "pending"


@pytest.mark.parametrize(
    "field, changed",
    [("space_id", "other-space"), ("parent_id", "99")],
)
def test_workspace_rejects_unsupported_page_moves(
    tmp_path: Path,
    field: str,
    changed: str,
) -> None:
    module = load_script()
    workspace = tmp_path / "page"
    module.download_page(FakeClient(), "42", workspace)
    meta = module.load_json(workspace / module.META_NAME)
    meta[field] = changed
    module.write_json(workspace / module.META_NAME, meta)
    module.capture_ground_truth(workspace)

    with pytest.raises(module.ValidationError, match=f"changing {field} is unsupported"):
        module.validate_workspace(workspace)


def test_remote_page_move_is_a_non_forceable_conflict(tmp_path: Path) -> None:
    module = load_script()
    client = FakeClient()
    workspace = tmp_path / "page"
    module.download_page(client, "42", workspace)
    client.meta["parentId"] = "99"

    with pytest.raises(module.ConflictError, match="remote parent_id changed"):
        module.upload_plan(client, workspace, force=True)


def test_divergent_editor_draft_blocks_page_updates_but_not_attachment_only_work(
    tmp_path: Path,
) -> None:
    module = load_script()

    class DivergentDraftClient(FakeClient):
        def draft_page(self, page_id: str) -> dict[str, Any]:
            draft = super().page(page_id, "storage")
            draft["status"] = "draft"
            draft["version"] = {"number": self.version + 1}
            draft["body"]["storage"]["value"] = "<p>Unpublished editor work</p>"
            return draft

    client = DivergentDraftClient()
    workspace = tmp_path / "draft-page"
    module.download_page(client, "42", workspace)
    manifest = module.load_json(workspace / module.MANIFEST_NAME)
    assert manifest["draft_observation"]["diverged"] is True

    local_attachment = workspace / module.ATTACHMENTS_DIR / "old.png"
    local_attachment.write_bytes(b"attachment-only-change")
    module.capture_ground_truth(workspace)
    attachment_plan, _, _ = module.upload_plan(client, workspace)
    assert attachment_plan["page_update"] is False
    assert attachment_plan["draft"]["diverged"] is True

    storage = (workspace / module.STORAGE_NAME).read_text(encoding="utf-8")
    (workspace / module.STORAGE_NAME).write_text(
        storage.replace("Old content", "Reviewed page edit"), encoding="utf-8"
    )
    module.capture_ground_truth(workspace)

    with pytest.raises(module.ConflictError, match="divergent Confluence editor draft"):
        module.upload_plan(client, workspace, force=True)

    assert client.page_updates == 0


@pytest.mark.parametrize(
    "status, subtype, error",
    [
        ("draft", "page", "only current"),
        ("current", "live", "unsupported Confluence page subtype"),
        ("current", [], "unsupported Confluence page subtype"),
        ("current", {}, "unsupported Confluence page subtype"),
    ],
)
def test_download_rejects_non_current_and_live_pages(
    tmp_path: Path,
    status: str,
    subtype: Any,
    error: str,
) -> None:
    module = load_script()
    client = FakeClient()
    client.meta["status"] = status
    client.meta["subtype"] = subtype

    with pytest.raises(module.ValidationError, match=error):
        module.download_page(client, "42", tmp_path / "page")


@pytest.mark.parametrize("subtype", [[], {}])
def test_download_rejects_a_malformed_draft_subtype(
    tmp_path: Path,
    subtype: Any,
) -> None:
    module = load_script()

    class MalformedDraftClient(FakeClient):
        def draft_page(self, page_id: str) -> dict[str, Any]:
            draft = super().page(page_id, "storage")
            draft["status"] = "draft"
            draft["subtype"] = subtype
            draft["version"] = {"number": self.version + 1}
            return draft

    with pytest.raises(module.ValidationError, match="unsupported Confluence draft subtype"):
        module.download_page(MalformedDraftClient(), "42", tmp_path / "page")


@pytest.mark.parametrize("subtype", [[], {}])
def test_workspace_rejects_a_malformed_local_subtype(
    tmp_path: Path,
    subtype: Any,
) -> None:
    module = load_script()
    workspace = tmp_path / "page"
    module.download_page(FakeClient(), "42", workspace)
    meta_path = workspace / module.META_NAME
    meta = module.load_json(meta_path)
    meta["subtype"] = subtype
    module.write_json(meta_path, meta)

    with pytest.raises(module.ValidationError, match="current, standard Confluence page"):
        module.validate_workspace(workspace)


def test_download_rejects_mixed_representation_versions(tmp_path: Path) -> None:
    module = load_script()

    class MixedVersionClient(FakeClient):
        def page(self, page_id: str, representation: str = "storage") -> dict[str, Any]:
            page = super().page(page_id, representation)
            if representation == "view":
                page["version"] = {"number": self.version + 1}
            return page

    with pytest.raises(module.ConflictError, match="different versions"):
        module.download_page(MixedVersionClient(), "42", tmp_path / "page")


def test_download_rejects_malformed_adf_json(tmp_path: Path) -> None:
    module = load_script()

    class MalformedAdfClient(FakeClient):
        def page(self, page_id: str, representation: str = "storage") -> dict[str, Any]:
            page = super().page(page_id, representation)
            if representation == "atlas_doc_format":
                page["body"][representation]["value"] = "{not-json"
            return page

    output = tmp_path / "page"
    with pytest.raises(module.RoundTripError, match="malformed atlas_doc_format JSON"):
        module.download_page(MalformedAdfClient(), "42", output)

    assert not output.exists()


def test_verify_rejects_malformed_adf_json(tmp_path: Path) -> None:
    module = load_script()

    class ToggleMalformedAdfClient(FakeClient):
        malformed = False

        def page(self, page_id: str, representation: str = "storage") -> dict[str, Any]:
            page = super().page(page_id, representation)
            if self.malformed and representation == "atlas_doc_format":
                page["body"][representation]["value"] = "{not-json"
            return page

    client = ToggleMalformedAdfClient()
    workspace = tmp_path / "page"
    module.download_page(client, "42", workspace)
    client.malformed = True

    with pytest.raises(module.RoundTripError, match="malformed atlas_doc_format JSON"):
        module.verify_workspace(client, workspace)


@pytest.mark.parametrize(
    "value",
    ["[]", "{}", '{"version":1,"type":"doc","content":{}}'],
)
def test_adf_requires_reasonable_top_level_doc_shape(value: str) -> None:
    module = load_script()

    with pytest.raises(module.RoundTripError, match="atlas_doc_format must"):
        module.normalize_adf(value)


def test_adf_preserves_unknown_nodes_and_fields() -> None:
    module = load_script()
    payload = {
        "version": 1,
        "type": "doc",
        "content": [{"type": "future-node", "attrs": {"future": True}}],
        "futureTopLevel": {"preserved": True},
    }

    assert module.normalize_adf(json.dumps(payload)) == payload


def test_no_verify_result_is_explicitly_unverified(tmp_path: Path) -> None:
    module = load_script()
    client = FakeClient()
    workspace = tmp_path / "page"
    module.download_page(client, "42", workspace)

    result = module.upload_workspace(client, workspace, message="Test", verify=False)

    assert result["status"] == "unverified"
    assert result["verification"] == {"status": "skipped"}
    assert result["remote_render_preflight"] == {"status": "not-required"}
    assert client.render_preflight_calls == 0


def test_no_verify_cli_cannot_report_shell_success(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = load_script()
    client = FakeClient()
    workspace = tmp_path / "page"
    module.download_page(client, "42", workspace)
    monkeypatch.setattr(
        module,
        "credentials_from_args",
        lambda _args: ("https://example.atlassian.net", "user@example.com", "secret"),
    )
    monkeypatch.setattr(module, "ConfluenceClient", lambda *_args, **_kwargs: client)

    return_code = module.main(["upload", str(workspace), "--no-verify"])

    assert return_code == 2


def test_completion_gate_rejects_bad_browser_hash_and_stale_api_evidence(tmp_path: Path) -> None:
    module = load_script()
    client = FakeClient()
    workspace = tmp_path / "page"
    module.download_page(client, "42", workspace)
    result = module.upload_workspace(client, workspace, message="Test")
    assert result["verification"]["status"] == "verified"
    write_browser_record(module, workspace)

    browser_path = workspace / module.VERIFY_DIR / "browser-ground-truth.json"
    browser = module.load_json(browser_path)
    browser["final_screenshots"][0]["sha256"] = "0" * 64
    module.write_json(browser_path, browser)
    bad_browser = module.validate_completion_gate(workspace)
    assert bad_browser["status"] == "failed"
    assert "screenshot digest mismatch: browser-final.png" in bad_browser["errors"]

    write_browser_record(module, workspace)
    attachment = workspace / module.ATTACHMENTS_DIR / "old.png"
    attachment.write_bytes(b"changed-after-api-verification")
    module.capture_ground_truth(workspace)
    stale_api = module.validate_completion_gate(workspace)
    assert stale_api["status"] == "failed"
    assert "API verification is stale for attachment: old.png" in stale_api["errors"]


def test_completion_gate_cli_is_local_and_returns_failure_status(tmp_path: Path) -> None:
    module = load_script()
    workspace = tmp_path / "page"
    module.download_page(FakeClient(), "42", workspace)

    completed = subprocess.run(
        [sys.executable, str(SCRIPT), "completion-gate", str(workspace)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=60,
        check=False,
    )

    assert completed.returncode == 2
    payload = json.loads(completed.stdout)
    assert payload["status"] == "failed"
    assert "verification\\report.json" in payload["errors"][0] or "verification/report.json" in payload["errors"][0]


def test_upload_output_persists_structured_preflight_errors(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = load_script()
    monkeypatch.setattr(
        module,
        "credentials_from_args",
        lambda _args: ("https://example.atlassian.net", "user@example.com", "secret"),
    )
    monkeypatch.setattr(module, "ConfluenceClient", lambda *_args, **_kwargs: FakeClient())
    output = tmp_path / "preflight-error.json"

    return_code = module.main(
        ["upload", str(tmp_path / "missing-workspace"), "--output", str(output)]
    )

    assert return_code == 2
    result = module.load_json(output)
    assert result["status"] == "failed"
    assert result["type"] == "ValidationError"
    assert "workspace is missing required files" in result["error"]


def test_upload_output_cannot_replace_workspace_state_or_reserved_evidence(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    module = load_script()
    workspace = tmp_path / "page"
    workspace.mkdir()
    manifest_path = workspace / module.MANIFEST_NAME
    manifest_path.write_text("unchanged", encoding="utf-8")

    for target in (
        manifest_path,
        workspace / module.ATTACHMENTS_DIR / "result.json",
        workspace / module.VERIFY_DIR / module.REPORT_NAME,
        workspace / module.VERIFY_DIR / "REPORT.JSON",
        workspace / module.VERIFY_DIR / module.RENDER_SAFETY_RECONCILIATION_NAME,
    ):
        with pytest.raises(module.ValidationError, match="upload --output"):
            module.validate_upload_output_path(workspace, target)

    allowed = workspace / module.VERIFY_DIR / "noop-dry-run.json"
    assert module.validate_upload_output_path(workspace, allowed) == allowed
    assert (
        module.validate_upload_output_path(workspace, tmp_path / "external.json")
        == tmp_path / "external.json"
    )

    return_code = module.main(
        ["upload", str(workspace), "--output", str(manifest_path)]
    )
    captured = capsys.readouterr()

    assert return_code == 2
    assert "upload --output" in captured.err
    assert manifest_path.read_text(encoding="utf-8") == "unchanged"


def test_cli_output_refuses_to_follow_a_symlink(tmp_path: Path) -> None:
    module = load_script()
    victim = tmp_path / "victim.json"
    victim.write_text("unchanged", encoding="utf-8")
    output = tmp_path / "result.json"
    make_symlink_or_skip(output, victim)

    with pytest.raises(module.ValidationError, match="CLI output.*symbolic link"):
        module.write_cli_result(output, {"status": "failed"})

    assert victim.read_text(encoding="utf-8") == "unchanged"


def test_label_deletion_uses_query_parameter_for_slashes() -> None:
    module = load_script()
    client = module.ConfluenceClient("https://example.atlassian.net", "user@example.com", "secret")
    calls: list[tuple[str, str, dict[str, Any]]] = []

    def record_request(method: str, path: str, **kwargs: Any) -> None:
        calls.append((method, path, kwargs))

    client.request = record_request  # type: ignore[method-assign]
    result = client.sync_labels("42", [], ["team/release"])

    assert result == {"added": [], "removed": ["team/release"]}
    assert calls == [
        (
            "DELETE",
            "/wiki/rest/api/content/42/label",
            {"expected": (204,), "params": {"name": "team/release"}},
        )
    ]


def test_content_state_identity_prefers_id_and_puts_id_only() -> None:
    module = load_script()
    client = module.ConfluenceClient("https://example.atlassian.net", "user@example.com", "secret")
    calls: list[dict[str, Any]] = []

    def record_request(_method: str, _path: str, **kwargs: Any) -> None:
        calls.append(kwargs)

    client.request = record_request  # type: ignore[method-assign]
    desired = {"id": 2, "name": "Ready", "color": "GREEN"}
    current = {"id": 1, "name": "Ready", "color": "GREEN"}

    assert module.state_signature(desired) != module.state_signature(current)
    assert client.set_content_state("42", desired, current) == "updated"
    assert calls[0]["json"] == {"id": 2}


def test_content_state_same_id_is_unchanged_despite_display_drift() -> None:
    module = load_script()
    desired = {"id": "2", "name": "Ready", "color": "GREEN"}
    current = {"id": 2, "name": "Renamed", "color": "BLUE"}

    assert module.state_signature(desired) == module.state_signature(current)


def test_content_state_definition_matches_server_assigned_id_and_color_case() -> None:
    module = load_script()
    desired = {"name": "Campaign Ready", "color": "#00875A"}
    remote = {"id": 34734099, "name": "Campaign Ready", "color": "#00875a"}

    assert module.states_equivalent(desired, remote)
    assert not module.states_equivalent(desired, {**remote, "name": "Different"})


def test_attachment_upload_preserves_inferred_image_mime_type(tmp_path: Path) -> None:
    module = load_script()
    client = module.ConfluenceClient("https://example.atlassian.net", "user@example.com", "secret")
    image_path = tmp_path / "architecture.png"
    image_path.write_bytes(b"png-bytes")
    captured: dict[str, Any] = {}

    class Response:
        def json(self) -> dict[str, Any]:
            return {"results": []}

    def record_request(_method: str, _path: str, **kwargs: Any) -> Response:
        captured.update(kwargs)
        return Response()

    client.request = record_request  # type: ignore[method-assign]
    client.upload_attachment("42", image_path, None, comment="Live acceptance")

    filename, _handle, media_type = captured["files"]["file"]
    assert filename == "architecture.png"
    assert media_type == "image/png"


def test_attachment_download_rest_link_uses_wiki_context_path() -> None:
    module = load_script()
    client = module.ConfluenceClient("https://example.atlassian.net", "user@example.com", "secret")
    calls: list[str] = []

    class Response:
        content = b"image-bytes"

    def record_request(_method: str, path: str, **_kwargs: Any) -> Response:
        calls.append(path)
        return Response()

    client.request = record_request  # type: ignore[method-assign]
    result = client.download_attachment(
        {"title": "architecture.png", "downloadLink": "/rest/api/content/42/child/attachment/a1/download"}
    )

    assert result == b"image-bytes"
    assert calls == ["/wiki/rest/api/content/42/child/attachment/a1/download"]


def test_implicit_dotenv_cannot_redirect_a_preexisting_api_token(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = load_script()
    for name in (
        "CONFLUENCE_BASE_URL",
        "ATLASSIAN_BASE_URL",
        "CONFLUENCE_USERNAME",
        "ATLASSIAN_USERNAME",
        "CONFLUENCE_TOKEN",
        "ATLASSIAN_API_TOKEN",
    ):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("CONFLUENCE_USERNAME", "victim@example.com")
    monkeypatch.setenv("CONFLUENCE_TOKEN", "preexisting-secret-token")
    (tmp_path / ".env").write_text(
        "CONFLUENCE_BASE_URL=https://attacker.example\n",
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    args = module.build_parser().parse_args(["doctor"])

    with pytest.raises(module.ValidationError, match=r"implicit.*\.env.*pre-existing API token"):
        module.credentials_from_args(args)


def test_explicit_dotenv_overrides_stale_process_credentials(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    module = load_script()
    env_file = tmp_path / ".env"
    env_file.write_text(
        "CONFLUENCE_BASE_URL=https://active.atlassian.net\n"
        "CONFLUENCE_USERNAME=active@example.com\n"
        "CONFLUENCE_TOKEN=fresh-token\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("CONFLUENCE_BASE_URL", "https://stale.atlassian.net")
    monkeypatch.setenv("CONFLUENCE_USERNAME", "stale@example.com")
    monkeypatch.setenv("CONFLUENCE_TOKEN", "stale-token")
    args = module.build_parser().parse_args(["--env-file", str(env_file), "doctor"])

    assert module.credentials_from_args(args) == (
        "https://active.atlassian.net",
        "active@example.com",
        "fresh-token",
    )


def test_skill_documents_the_exact_credential_contract() -> None:
    instructions = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
    normalized_instructions = " ".join(instructions.casefold().split())

    for variable in (
        "CONFLUENCE_BASE_URL",
        "CONFLUENCE_USERNAME",
        "CONFLUENCE_TOKEN",
        "ATLASSIAN_BASE_URL",
        "ATLASSIAN_USERNAME",
        "ATLASSIAN_API_TOKEN",
    ):
        assert variable in instructions
    assert "CONFLUENCE_EMAIL` and `CONFLUENCE_API_TOKEN` are not accepted" in instructions
    assert "not **Create API token with scopes**" in instructions
    assert "--env-file /absolute/path/to/.env doctor" in instructions
    assert "HTTP 401" in instructions
    assert "HTTP 403" in instructions
    assert "revoke a token immediately" in normalized_instructions


def test_skill_is_portable_and_metadata_has_only_native_fields(tmp_path: Path) -> None:
    module = load_script()
    workspace = tmp_path / "portable-workspace"
    module.download_page(FakeClient(), "42", workspace)
    copied = tmp_path / "roundtrip-confluence-pages"
    shutil.copytree(SKILL_ROOT, copied)
    result = subprocess.run(
        [sys.executable, str(copied / "scripts" / "confluence_roundtrip.py"), "--help"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert all(
        command in result.stdout
        for command in ("download", "upload", "verify", "completion-gate")
    )

    validation = subprocess.run(
        [
            sys.executable,
            str(copied / "scripts" / "confluence_roundtrip.py"),
            "validate",
            str(workspace),
        ],
        cwd=copied,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=60,
        check=False,
    )
    assert validation.returncode == 0, validation.stderr
    assert json.loads(validation.stdout)["status"] == "valid"

    skill_text = (copied / "SKILL.md").read_text(encoding="utf-8")
    frontmatter = skill_text.split("---", 2)[1]
    keys = [line.split(":", 1)[0] for line in frontmatter.splitlines() if ":" in line]
    assert keys == ["name", "description"]
    assert "## Standalone boundary" in skill_text
    assert "repository-approved" not in skill_text
    assert "completion-gate" in skill_text
    assert "intended Confluence filename" in skill_text
    assert "attachments upload before storage XML" in skill_text
    assert "SHA-256 digest and media type" in skill_text
    assert "preserve old remote attachments" in skill_text


def test_active_operation_lock_prevents_journal_overwrite(tmp_path: Path) -> None:
    module = load_script()
    client = FakeClient()
    workspace = tmp_path / "locked-workspace"
    module.download_page(client, "42", workspace)
    plan, _, _ = module.upload_plan(client, workspace)
    digest = module.desired_state_sha256(workspace)
    first = module._begin_operation(
        workspace,
        plan,
        desired_digest=digest,
        sync_attachments=True,
        sync_labels=True,
        sync_content_state=True,
    )
    report_path = workspace / module.VERIFY_DIR / module.REPORT_NAME
    report_path.write_text("first operation evidence", encoding="utf-8")

    with pytest.raises(module.ConflictError, match="another operation is already active"):
        module._begin_operation(
            workspace,
            plan,
            desired_digest=digest,
            sync_attachments=True,
            sync_labels=True,
            sync_content_state=True,
        )

    journal = module.load_json(
        workspace / module.VERIFY_DIR / module.JOURNAL_NAME
    )
    assert journal["operation_id"] == first["operation_id"]
    assert report_path.read_text(encoding="utf-8") == "first operation evidence"
    assert (workspace / module.VERIFY_DIR / module.OPERATION_LOCK_NAME).is_file()
    first["status"] = "failed"
    module._write_journal(workspace, first)
    assert not (workspace / module.VERIFY_DIR / module.OPERATION_LOCK_NAME).exists()


def test_partial_attachment_create_is_journaled_and_safely_resumed(tmp_path: Path) -> None:
    module = load_script()

    class FailPageOnceClient(FakeClient):
        fail_page_once = True

        def update_page(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
            if self.fail_page_once:
                self.fail_page_once = False
                raise module.ConflictError("simulated concurrent page update")
            return super().update_page(*args, **kwargs)

    client = FailPageOnceClient()
    workspace = tmp_path / "resumable"
    module.download_page(client, "42", workspace)
    new_attachment = workspace / module.ATTACHMENTS_DIR / "new.png"
    new_attachment.write_bytes(b"new-image")
    storage = (workspace / module.STORAGE_NAME).read_text(encoding="utf-8")
    (workspace / module.STORAGE_NAME).write_text(
        storage + '<ac:image><ri:attachment ri:filename="new.png" /></ac:image>',
        encoding="utf-8",
    )
    module.capture_ground_truth(workspace)

    first = module.upload_workspace(client, workspace, message="First attempt")

    assert first["status"] == "partial"
    journal = module.load_json(workspace / module.VERIFY_DIR / module.JOURNAL_NAME)
    assert journal["status"] == "partial"
    attachment_step = next(
        step for step in journal["steps"] if step["id"] == "attachment:new.png"
    )
    assert attachment_step["status"] == "applied"
    assert attachment_step["detail"]["remote_id"] == client.attachment_ids["new.png"]
    first_operation = journal["operation_id"]

    second = module.upload_workspace(client, workspace, message="Resume")

    assert second["status"] == "uploaded", second
    assert client.upload_calls.count(("new.png", None)) == 1
    resumed = module.load_json(workspace / module.VERIFY_DIR / module.JOURNAL_NAME)
    assert resumed["status"] == "api-verified"
    assert resumed["resumed_from_operation_id"] == first_operation
    assert next(
        step for step in resumed["steps"] if step["id"] == "attachment:new.png"
    )["status"] == "reconciled"
    write_browser_record(module, workspace)
    assert module.validate_completion_gate(workspace)["status"] == "verified"


def test_existing_attachment_update_is_reconciled_after_later_failure(
    tmp_path: Path,
) -> None:
    module = load_script()

    class FailLabelsOnceClient(FakeClient):
        def __init__(self) -> None:
            super().__init__()
            self.attachment_versions = {"old.png": 1}
            self.fail_labels_once = True

        def attachments(self, page_id: str) -> list[dict[str, Any]]:
            results = super().attachments(page_id)
            for item in results:
                item["version"] = {
                    "number": self.attachment_versions[str(item["title"])]
                }
            return results

        def upload_attachment(
            self,
            page_id: str,
            path: Path,
            existing_id: str | None,
            *,
            comment: str,
            media_type: str | None = None,
        ) -> dict[str, Any]:
            result = super().upload_attachment(
                page_id,
                path,
                existing_id,
                comment=comment,
                media_type=media_type,
            )
            if existing_id:
                self.attachment_versions[path.name] += 1
            return result

        def sync_labels(
            self,
            page_id: str,
            desired: list[str],
            current: list[str],
        ) -> dict[str, list[str]]:
            if self.fail_labels_once:
                self.fail_labels_once = False
                raise module.RoundTripError("simulated later label failure")
            return super().sync_labels(page_id, desired, current)

    client = FailLabelsOnceClient()
    workspace = tmp_path / "attachment-update-resume"
    module.download_page(client, "42", workspace)
    (workspace / module.ATTACHMENTS_DIR / "old.png").write_bytes(b"updated-image")
    module.write_json(workspace / module.LABELS_NAME, ["alpha", "beta"])
    module.capture_ground_truth(workspace)

    first = module.upload_workspace(client, workspace, message="First attempt")

    assert first["status"] == "partial"
    first_operation = first["operation_id"]
    first_journal = module.load_json(
        workspace / module.VERIFY_DIR / module.JOURNAL_NAME
    )
    first_attachment = next(
        step
        for step in first_journal["steps"]
        if step["id"] == "attachment:old.png"
    )
    assert first_attachment["action"] == "update"
    assert first_attachment["status"] == "applied"
    assert first_attachment["detail"]["remote_id"] == "a1"
    assert first_attachment["detail"]["remote_version"] == 2

    second = module.upload_workspace(client, workspace, message="Resume")

    assert second["status"] == "uploaded", second
    assert client.upload_calls.count(("old.png", "a1")) == 1
    assert client.attachment_versions["old.png"] == 2
    resumed = module.load_json(workspace / module.VERIFY_DIR / module.JOURNAL_NAME)
    assert resumed["resumed_from_operation_id"] == first_operation
    assert next(
        step for step in resumed["steps"] if step["id"] == "attachment:old.png"
    )["status"] == "reconciled"


def test_applied_page_update_is_reconciled_after_later_label_failure(
    tmp_path: Path,
) -> None:
    module = load_script()

    class FailLabelsOnceClient(FakeClient):
        fail_labels_once = True

        def sync_labels(
            self,
            page_id: str,
            desired: list[str],
            current: list[str],
        ) -> dict[str, list[str]]:
            if self.fail_labels_once:
                self.fail_labels_once = False
                raise module.RoundTripError("simulated later label failure")
            return super().sync_labels(page_id, desired, current)

    client = FailLabelsOnceClient()
    workspace = tmp_path / "page-update-resume"
    module.download_page(client, "42", workspace)
    storage = (workspace / module.STORAGE_NAME).read_text(encoding="utf-8")
    (workspace / module.STORAGE_NAME).write_text(
        storage.replace("Old content", "New content"), encoding="utf-8"
    )
    meta = module.load_json(workspace / module.META_NAME)
    meta["title"] = "Updated fixture"
    module.write_json(workspace / module.META_NAME, meta)
    module.write_json(workspace / module.LABELS_NAME, ["alpha", "beta"])
    module.capture_ground_truth(workspace)

    first = module.upload_workspace(client, workspace, message="First attempt")

    assert first["status"] == "partial"
    assert first["page_updated"] is True
    assert client.page_updates == 1
    first_operation = first["operation_id"]
    first_journal = module.load_json(
        workspace / module.VERIFY_DIR / module.JOURNAL_NAME
    )
    page_step = next(
        step for step in first_journal["steps"] if step["id"] == "page"
    )
    assert page_step["kind"] == "page"
    assert page_step["status"] == "applied"
    assert page_step["detail"] == {"remote_version": 4}

    second = module.upload_workspace(client, workspace, message="Resume")

    assert second["status"] == "uploaded", second
    assert second["page_updated"] is False
    assert client.page_updates == 1
    resumed = module.load_json(workspace / module.VERIFY_DIR / module.JOURNAL_NAME)
    assert resumed["resumed_from_operation_id"] == first_operation
    assert next(step for step in resumed["steps"] if step["id"] == "page")[
        "status"
    ] == "reconciled"


def test_started_mutation_becomes_unknown_partial_and_preserves_resume_lineage(
    tmp_path: Path,
) -> None:
    module = load_script()

    class FailLabelsOnceClient(FakeClient):
        fail_labels_once = True

        def sync_labels(
            self,
            page_id: str,
            desired: list[str],
            current: list[str],
        ) -> dict[str, list[str]]:
            if self.fail_labels_once:
                self.fail_labels_once = False
                raise module.RoundTripError("label result is unknown")
            return super().sync_labels(page_id, desired, current)

    client = FailLabelsOnceClient()
    workspace = tmp_path / "unknown-partial-resume"
    module.download_page(client, "42", workspace)
    module.write_json(workspace / module.LABELS_NAME, ["alpha", "beta"])
    module.capture_ground_truth(workspace)

    first = module.upload_workspace(client, workspace, message="First attempt")

    assert first["status"] == "partial"
    first_operation = first["operation_id"]
    first_journal = module.load_json(
        workspace / module.VERIFY_DIR / module.JOURNAL_NAME
    )
    label_step = next(
        step for step in first_journal["steps"] if step["id"] == "labels"
    )
    assert label_step["status"] == "unknown-partial"
    assert label_step["uncertain"] is True

    second = module.upload_workspace(client, workspace, message="Resume")

    assert second["status"] == "uploaded", second
    resumed = module.load_json(workspace / module.VERIFY_DIR / module.JOURNAL_NAME)
    assert resumed["resumed_from_operation_id"] == first_operation
    assert next(step for step in resumed["steps"] if step["id"] == "labels")[
        "status"
    ] == "applied"


def test_resume_accepts_page_version_added_by_applied_content_state(
    tmp_path: Path,
) -> None:
    module = load_script()

    class FailVerificationAfterStateClient(FakeClient):
        def __init__(self) -> None:
            super().__init__()
            self.fail_next_page_read = False
            self.failed = False

        def set_content_state(
            self,
            page_id: str,
            desired: dict[str, Any] | None,
            current: dict[str, Any] | None,
        ) -> str:
            result = super().set_content_state(page_id, desired, current)
            self.fail_next_page_read = True
            return result

        def page(self, page_id: str, representation: str = "storage") -> dict[str, Any]:
            if self.fail_next_page_read and not self.failed:
                self.failed = True
                raise module.RoundTripError("verification GET was interrupted")
            return super().page(page_id, representation)

    client = FailVerificationAfterStateClient()
    workspace = tmp_path / "content-state-resume"
    module.download_page(client, "42", workspace)
    storage = (workspace / module.STORAGE_NAME).read_text(encoding="utf-8")
    (workspace / module.STORAGE_NAME).write_text(
        storage.replace("Old content", "New content"), encoding="utf-8"
    )
    module.write_json(
        workspace / module.STATE_NAME,
        {"id": 2, "name": "Ready", "color": "GREEN"},
    )
    module.capture_ground_truth(workspace)

    first = module.upload_workspace(client, workspace, message="First attempt")
    assert first["status"] == "partial"
    assert client.version == 5
    assert client.page_updates == 1

    second = module.upload_workspace(client, workspace, message="Resume")

    assert second["status"] == "uploaded", second
    assert client.page_updates == 1


def test_new_upload_invalidates_prior_browser_completion(tmp_path: Path) -> None:
    module, client, workspace = make_verified_workspace(tmp_path)
    old_report = module.load_json(workspace / module.VERIFY_DIR / module.REPORT_NAME)

    second = module.upload_workspace(client, workspace, message="Fresh verification operation")

    assert second["status"] == "uploaded"
    assert second["operation_id"] != old_report["operation_id"]
    assert not (workspace / module.VERIFY_DIR / module.BROWSER_GT_NAME).exists()
    gate = module.validate_completion_gate(workspace)
    assert gate["status"] == "failed"
    assert any("browser-ground-truth.json" in error for error in gate["errors"])


def test_api_report_is_bound_to_operation_state_evidence_and_manifest(tmp_path: Path) -> None:
    module, _client, workspace = make_verified_workspace(tmp_path)
    report = module.load_json(workspace / module.VERIFY_DIR / module.REPORT_NAME)
    manifest = module.load_json(workspace / module.MANIFEST_NAME)

    assert report["operation_id"] == manifest["last_verified_operation_id"]
    assert report["desired_state_sha256"] == module.desired_state_sha256(workspace)
    assert report["remote_version"] == manifest["page"]["version"]
    assert set(report["evidence"]) == {
        "storage",
        "atlas_doc_format",
        "view",
        "restrictions",
        "properties",
        "operations",
    }
    for record in report["evidence"].values():
        evidence_path = workspace / module.VERIFY_DIR / record["path"]
        assert record["sha256"] == module.sha256_bytes(evidence_path.read_bytes())


def test_completion_rejects_manifest_version_and_evidence_drift(tmp_path: Path) -> None:
    module, _client, workspace = make_verified_workspace(tmp_path)
    manifest = module.load_json(workspace / module.MANIFEST_NAME)
    manifest["page"]["version"] += 1
    module.write_json(workspace / module.MANIFEST_NAME, manifest)

    version_drift = module.validate_completion_gate(workspace)
    assert version_drift["status"] == "failed"
    assert "API remote version does not match the manifest version lock" in version_drift["errors"]

    manifest["page"]["version"] -= 1
    module.write_json(workspace / module.MANIFEST_NAME, manifest)
    remote_view = workspace / module.VERIFY_DIR / module.REMOTE_VIEW_NAME
    remote_view.write_text("tampered", encoding="utf-8")
    evidence_drift = module.validate_completion_gate(workspace)
    assert evidence_drift["status"] == "failed"
    assert any("remote.view.html" in error for error in evidence_drift["errors"])


@pytest.mark.parametrize(
    "name, replacement, error",
    [
        ("page.adf.json", {}, "page.adf.json differs"),
        ("page.view.html", "<p>tampered</p>", "page.view.html differs"),
        ("page.restrictions.json", {"tampered": True}, "page.restrictions.json differs"),
        ("page.properties.json", {"tampered": True}, "page.properties.json differs"),
        ("page.operations.json", {"tampered": True}, "page.operations.json differs"),
    ],
)
def test_validate_rejects_modified_immutable_evidence(
    tmp_path: Path,
    name: str,
    replacement: Any,
    error: str,
) -> None:
    module = load_script()
    workspace = tmp_path / name.replace(".", "-")
    module.download_page(FakeClient(), "42", workspace)
    path = workspace / name
    if isinstance(replacement, str):
        path.write_text(replacement, encoding="utf-8")
    else:
        module.write_json(path, replacement)

    with pytest.raises(module.ValidationError, match=error):
        module.validate_workspace(workspace)


def test_legacy_manifest_without_properties_and_operations_remains_compatible(
    tmp_path: Path,
) -> None:
    module = load_script()
    workspace = tmp_path / "legacy-evidence"
    module.download_page(FakeClient(), "42", workspace)
    manifest = module.load_json(workspace / module.MANIFEST_NAME)
    manifest.pop("properties")
    manifest.pop("operations")
    module.write_json(workspace / module.MANIFEST_NAME, manifest)
    (workspace / module.PROPERTIES_NAME).unlink()
    (workspace / module.OPERATIONS_NAME).unlink()

    assert module.validate_workspace(workspace)["status"] == "valid"
    contract = module.desired_state_contract(workspace)
    assert module.PROPERTIES_NAME not in contract["immutable_evidence"]
    assert module.OPERATIONS_NAME not in contract["immutable_evidence"]


def test_manifest_cannot_partially_declare_extended_page_evidence(
    tmp_path: Path,
) -> None:
    module = load_script()
    workspace = tmp_path / "partial-evidence"
    module.download_page(FakeClient(), "42", workspace)
    manifest = module.load_json(workspace / module.MANIFEST_NAME)
    manifest.pop("operations")
    module.write_json(workspace / module.MANIFEST_NAME, manifest)

    with pytest.raises(module.ValidationError, match="both properties and operations"):
        module.validate_workspace(workspace)


def test_verify_fails_when_restrictions_change(tmp_path: Path) -> None:
    module = load_script()

    class RestrictionDriftClient(FakeClient):
        drifted = False

        def restrictions(self, page_id: str) -> dict[str, Any]:
            if self.drifted:
                return {"read": {"restrictions": {"user": {"results": [{"id": "u1"}]}}}}
            return super().restrictions(page_id)

    client = RestrictionDriftClient()
    workspace = tmp_path / "restriction-drift"
    module.download_page(client, "42", workspace)
    client.drifted = True

    report = module.verify_workspace(client, workspace)

    assert report["status"] == "failed"
    check = next(item for item in report["checks"] if item["name"] == "restrictions-unchanged")
    assert check["passed"] is False


def test_refresh_rejects_attachment_drift_after_api_verification(tmp_path: Path) -> None:
    module = load_script()

    class VersionedAttachmentClient(FakeClient):
        attachment_version = 1

        def attachments(self, page_id: str) -> list[dict[str, Any]]:
            items = super().attachments(page_id)
            for item in items:
                item["version"] = {"number": self.attachment_version}
            return items

    client = VersionedAttachmentClient()
    workspace = tmp_path / "attachment-refresh-race"
    module.download_page(client, "42", workspace)
    report = module.verify_workspace(
        client,
        workspace,
        operation_id="manual-verification-operation",
    )
    assert report["status"] == "verified"
    assert report["verified_attachments"] == [
        {
            "filename": "old.png",
            "id": "a1",
            "version": 1,
            "sha256": module.sha256_bytes(b"old-image"),
            "media_type": "image/png",
        }
    ]

    client.attachment_bytes["old.png"] = b"changed-after-verification"
    client.attachment_version = 2

    with pytest.raises(
        module.ConflictError,
        match="changed between API verification and manifest refresh",
    ):
        module.refresh_manifest(
            client,
            workspace,
            verified_report=report,
            operation_id="manual-verification-operation",
        )

    manifest = module.load_json(workspace / module.MANIFEST_NAME)
    assert manifest["attachments"][0]["version"] == 1
    assert manifest["attachments"][0]["sha256"] == module.sha256_bytes(b"old-image")


def test_page_update_payload_omits_immutable_location_fields() -> None:
    module = load_script()
    client = module.ConfluenceClient(
        "https://example.atlassian.net", "user@example.com", "secret"
    )
    captured: dict[str, Any] = {}

    def record_json(_method: str, _path: str, **kwargs: Any) -> dict[str, Any]:
        captured.update(kwargs["json"])
        return {}

    client.json = record_json  # type: ignore[method-assign]
    client.update_page(
        "42",
        {"title": "Safe", "space_id": "7", "parent_id": "99"},
        "<p>Safe</p>",
        3,
        "Safe update",
    )

    assert "spaceId" not in captured
    assert "parentId" not in captured


def test_browser_gate_requires_exact_bound_page_and_timestamp(tmp_path: Path) -> None:
    module, _client, workspace = make_verified_workspace(tmp_path)
    browser_path = workspace / module.VERIFY_DIR / module.BROWSER_GT_NAME
    browser = module.load_json(browser_path)
    browser["page_url"] = "https://example.atlassian.net/wiki/pages/99"
    browser["verified_at"] = "2000-01-01T00:00:00Z"
    module.write_json(browser_path, browser)

    gate = module.validate_completion_gate(workspace)

    assert gate["status"] == "failed"
    assert "browser page URL does not identify the expected page ID" in gate["errors"]
    assert "browser verification predates API verification" in gate["errors"]


def test_browser_gate_binds_api_report_operation_version_and_desired_state(
    tmp_path: Path,
) -> None:
    module, _client, workspace = make_verified_workspace(tmp_path)
    browser_path = workspace / module.VERIFY_DIR / module.BROWSER_GT_NAME
    browser = module.load_json(browser_path)
    browser["operation_id"] = "different-operation"
    browser["remote_version"] += 1
    browser["desired_state_sha256"] = "0" * 64
    browser["api_report_sha256"] = "f" * 64
    module.write_json(browser_path, browser)

    gate = module.validate_completion_gate(workspace)

    assert gate["status"] == "failed"
    assert "browser verification refers to a different API operation" in gate["errors"]
    assert "browser verification is not bound to the current API report" in gate["errors"]
    assert "browser verification is not bound to the verified desired state" in gate["errors"]
    assert "browser verification is not bound to the verified remote version" in gate["errors"]


def test_browser_gate_rejects_escaping_and_non_image_screenshots(tmp_path: Path) -> None:
    module, _client, workspace = make_verified_workspace(tmp_path)
    verification = workspace / module.VERIFY_DIR
    browser_path = verification / module.BROWSER_GT_NAME
    browser = module.load_json(browser_path)
    escaped = workspace / "escaped.png"
    escaped.write_bytes(make_png((1, 2, 3)))
    browser["baseline"] = {
        "path": "../escaped.png",
        "sha256": module.sha256_bytes(escaped.read_bytes()),
    }
    invalid = verification / "invalid.png"
    invalid.write_bytes(b"not-an-image")
    browser["final_screenshots"] = [
        {"path": invalid.name, "sha256": module.sha256_bytes(invalid.read_bytes())}
    ]
    module.write_json(browser_path, browser)

    gate = module.validate_completion_gate(workspace)

    assert gate["status"] == "failed"
    assert "screenshot path escapes verification/: ../escaped.png" in gate["errors"]
    assert "screenshot is not a decodable PNG or JPEG: invalid.png" in gate["errors"]


def test_browser_gate_requires_distinct_images_and_feature_check_ids(tmp_path: Path) -> None:
    module, _client, workspace = make_verified_workspace(tmp_path)
    verification = workspace / module.VERIFY_DIR
    browser_path = verification / module.BROWSER_GT_NAME
    browser = module.load_json(browser_path)
    copied_final = verification / "copied-final.png"
    baseline_path = verification / browser["baseline"]["path"]
    copied_final.write_bytes(baseline_path.read_bytes())
    browser["final_screenshots"] = [
        {
            "path": copied_final.name,
            "sha256": module.sha256_bytes(copied_final.read_bytes()),
        }
    ]
    module.write_json(browser_path, browser)
    ground_truth = module.load_json(workspace / module.GT_NAME)
    ground_truth["required_browser_check_ids"] = ["rendered-page", "expand-open"]
    module.write_json(workspace / module.GT_NAME, ground_truth)

    gate = module.validate_completion_gate(workspace)

    assert gate["status"] == "failed"
    assert "baseline and final screenshots must be distinct" in gate["errors"]
    assert "browser verification is missing required check IDs: expand-open" in gate["errors"]


def test_record_browser_ground_truth_binds_current_api_evidence(tmp_path: Path) -> None:
    module, _client, workspace = make_verified_workspace(tmp_path)
    verification = workspace / module.VERIFY_DIR
    (verification / module.BROWSER_GT_NAME).unlink()

    recorded = module.record_browser_ground_truth(
        workspace,
        page_url="https://example.atlassian.net/wiki/spaces/T/pages/42/Fixture",
        checks=["rendered-page"],
        baseline=Path("verification/browser-baseline.png"),
        final_screenshots=[Path("verification/browser-final.png")],
    )

    assert recorded["status"] == "verified"
    browser = module.load_json(verification / module.BROWSER_GT_NAME)
    api_path = verification / module.REPORT_NAME
    api = module.load_json(api_path)
    assert browser["operation_id"] == api["operation_id"]
    assert browser["api_report_sha256"] == module.sha256_bytes(api_path.read_bytes())
    assert browser["checks"] == [{"name": "rendered-page", "passed": True}]
