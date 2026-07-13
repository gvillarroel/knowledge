"""Unit and portability tests for the Confluence multi-page batch companion."""

from __future__ import annotations

import importlib.util
import json
import os
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
BATCH_SCRIPT = SKILL_ROOT / "scripts" / "confluence_batch.py"


def load_batch() -> ModuleType:
    """Load the standalone batch script for focused tests."""

    spec = importlib.util.spec_from_file_location("test_confluence_batch", BATCH_SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class FakeBatchClient:
    """Stateful multi-page Confluence fake with optional HTTP 429 failures."""

    def __init__(self, page_count: int = 3) -> None:
        self.base_url = "https://example.atlassian.net"
        self.pages: dict[str, dict[str, Any]] = {}
        for number in range(1, page_count + 1):
            page_id = str(number)
            storage = f"<h1>Release page {number}</h1><p>Batch candidate {number}</p>"
            if number == 1:
                storage += (
                    '<p><a href="https://developer.atlassian.com/cloud/confluence/">Docs</a></p>'
                    '<ac:structured-macro ac:name="status">'
                    '<ac:parameter ac:name="title">READY</ac:parameter>'
                    "</ac:structured-macro>"
                    '<ac:image><ri:attachment ri:filename="diagram.png" /></ac:image>'
                )
            self.pages[page_id] = {
                "title": f"Release page {number}",
                "storage": storage,
                "version": 1,
                "labels": ["batch"] + (["release"] if number == 1 else []),
                "state": None,
                "attachments": {"diagram.png": b"diagram-bytes"} if number == 1 else {},
                "attachment_versions": {"diagram.png": 1} if number == 1 else {},
            }
        self.page_calls = 0
        self.update_attempts = {page_id: 0 for page_id in self.pages}
        self.update_successes = {page_id: 0 for page_id in self.pages}
        self.update_order: list[str] = []
        self.fail_update_once: set[str] = set()
        self.paginated_rate_limit = False
        self.render_preflight_calls: list[str] = []

    def json(self, _method: str, path: str, **_kwargs: Any) -> dict[str, Any]:
        if path == "/wiki/api/v2/pages":
            page_ids = sorted(self.pages, key=int)
            if self.paginated_rate_limit:
                return {
                    "results": [{"id": page_ids[0]}],
                    "_links": {
                        "next": (
                            "/wiki/api/v2/pages?cursor=next&limit=250&space-id=7"
                            "&status=current&subtype=page"
                        )
                    },
                }
            return {"results": [{"id": page_id} for page_id in page_ids], "_links": {}}
        if "cursor=next" in path and self.paginated_rate_limit:
            raise load_batch().core.RoundTripError("Confluence GET returned HTTP 429: retry later")
        raise AssertionError(f"unexpected JSON endpoint: {path}")

    def page(self, page_id: str, representation: str = "storage") -> dict[str, Any]:
        self.page_calls += 1
        state = self.pages[str(page_id)]
        adf = {
            "version": 1,
            "type": "doc",
            "content": [
                {"type": "table"},
                {"type": "paragraph", "content": [{"type": "text", "text": state["title"]}]},
                {
                    "type": "inlineCard",
                    "attrs": {"url": "https://developer.atlassian.com/cloud/confluence/"},
                },
            ],
        }
        values = {
            "storage": state["storage"],
            "atlas_doc_format": json.dumps(adf),
            "view": f"<article>{state['storage']}</article>",
        }
        return {
            "id": str(page_id),
            "title": state["title"],
            "spaceId": "7",
            "parentId": None,
            "status": "current",
            "subtype": "page",
            "version": {"number": state["version"]},
            "body": {representation: {"value": values[representation]}},
            "_links": {"webui": f"/wiki/spaces/T/pages/{page_id}"},
        }

    def attachments(self, page_id: str) -> list[dict[str, Any]]:
        state = self.pages[str(page_id)]
        return [
            {
                "id": f"{page_id}-{filename}",
                "title": filename,
                "mediaType": "image/png",
                "version": {"number": state["attachment_versions"][filename]},
                "downloadLink": f"/download/{page_id}/{filename}",
            }
            for filename in sorted(state["attachments"])
        ]

    def draft_page(self, page_id: str) -> dict[str, Any]:
        """Return the published page when the fake has no divergent draft."""

        return self.page(page_id, "storage")

    def labels(self, page_id: str) -> list[str]:
        return sorted(self.pages[str(page_id)]["labels"])

    def download_attachment(self, attachment: dict[str, Any]) -> bytes:
        page_id = str(attachment["id"]).split("-", 1)[0]
        return self.pages[page_id]["attachments"][str(attachment["title"])]

    def content_state(self, page_id: str) -> dict[str, Any] | None:
        return self.pages[str(page_id)]["state"]

    def preflight_storage_render(self, page_id: str, storage: str) -> dict[str, Any]:
        assert isinstance(storage, str)
        self.render_preflight_calls.append(str(page_id))
        return {
            "status": "completed",
            "representation": "view",
            "rendered_sha256": "b" * 64,
            "rendered_bytes": len(storage.encode("utf-8")),
            "polls": 1,
            "render_safety": {
                "status": "passed",
                "unknown_macro_placeholders": 0,
                "signals_found": [],
            },
        }

    def restrictions(self, _page_id: str) -> dict[str, Any]:
        return {"read": {"restrictions": {"user": {"results": []}}}}

    def upload_attachment(
        self,
        page_id: str,
        path: Path,
        _existing_id: str | None,
        *,
        comment: str,
        media_type: str | None = None,
    ) -> dict[str, Any]:
        assert comment
        assert media_type
        state = self.pages[str(page_id)]
        state["attachments"][path.name] = path.read_bytes()
        state["attachment_versions"][path.name] = state["attachment_versions"].get(path.name, 0) + 1
        return {"results": [{"id": f"{page_id}-{path.name}"}]}

    def update_page(
        self,
        page_id: str,
        meta: dict[str, Any],
        storage: str,
        version: int,
        message: str,
    ) -> dict[str, Any]:
        page_id = str(page_id)
        self.update_attempts[page_id] += 1
        if page_id in self.fail_update_once:
            self.fail_update_once.remove(page_id)
            raise load_batch().core.RoundTripError("Confluence PUT returned HTTP 429: retry later")
        assert message
        state = self.pages[page_id]
        assert version == state["version"]
        state["title"] = meta["title"]
        state["storage"] = storage
        state["version"] += 1
        self.update_successes[page_id] += 1
        self.update_order.append(page_id)
        return self.page(page_id, "storage")

    def sync_labels(self, page_id: str, desired: list[str], current: list[str]) -> dict[str, list[str]]:
        added = sorted(set(desired) - set(current))
        removed = sorted(set(current) - set(desired))
        self.pages[str(page_id)]["labels"] = sorted(desired)
        return {"added": added, "removed": removed}

    def set_content_state(
        self,
        page_id: str,
        desired: dict[str, Any] | None,
        current: dict[str, Any] | None,
    ) -> str:
        if desired == current:
            return "unchanged"
        self.pages[str(page_id)]["state"] = desired
        return "updated" if desired is not None else "removed"


def prepare_batch(
    tmp_path: Path,
    *,
    page_count: int = 3,
) -> tuple[ModuleType, FakeBatchClient, Path, Path]:
    """Scan and download a complete fake batch."""

    module = load_batch()
    client = FakeBatchClient(page_count)
    inventory = tmp_path / "inventory.json"
    scanned = module.scan_space(client, "7", inventory)
    assert scanned["status"] == "verified"
    batch_root = tmp_path / "batch"
    downloaded = module.batch_download(client, inventory, batch_root)
    assert downloaded["status"] == "verified"
    return module, client, inventory, batch_root / module.BATCH_MANIFEST_NAME


def write_browser_evidence(module: ModuleType, workspace: Path, page_id: str) -> None:
    """Create valid local browser evidence with recomputable screenshot hashes."""

    verification = workspace / module.core.VERIFY_DIR
    baseline = verification / "browser-baseline.png"
    final = verification / "browser-final.png"
    baseline.write_bytes(make_png((20, 40, int(page_id))))
    final.write_bytes(make_png((60, 40, int(page_id))))
    api_path = verification / module.core.REPORT_NAME
    api = module.core.load_json(api_path)
    module.core.write_json(
        verification / module.core.BROWSER_GT_NAME,
        {
            "schema_version": module.core.SCHEMA_VERSION,
            "status": "verified",
            "page_id": page_id,
            "page_url": f"https://example.atlassian.net/wiki/pages/{page_id}",
            "operation_id": api["operation_id"],
            "api_report_sha256": module.core.sha256_bytes(api_path.read_bytes()),
            "remote_version": api["remote_version"],
            "desired_state_sha256": api["desired_state_sha256"],
            "verified_at": module.core.utc_now(),
            "baseline": {
                "path": baseline.name,
                "sha256": module.core.sha256_bytes(baseline.read_bytes()),
            },
            "final_screenshots": [
                {"path": final.name, "sha256": module.core.sha256_bytes(final.read_bytes())}
            ],
            "checks": [{"name": "rendered-page", "passed": True}],
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


def test_scan_persists_inventory_and_all_filters_are_local(tmp_path: Path) -> None:
    module = load_batch()
    client = FakeBatchClient(2)
    inventory_path = tmp_path / "inventory.json"
    explored_path = tmp_path / "explored.json"

    scanned = module.scan_space(client, "7", inventory_path)
    calls_after_scan = client.page_calls
    explored = module.explore_inventory(
        inventory_path,
        text=["release page 1"],
        macro=["status"],
        adf_node=["table"],
        label=["release"],
        domain=["developer.atlassian.com"],
        attachment=["diagram"],
        output=explored_path,
    )

    assert scanned["status"] == "verified"
    assert inventory_path.is_file()
    assert explored["status"] == "queried"
    assert [page["page_id"] for page in explored["pages"]] == ["1"]
    assert module.core.load_json(explored_path) == explored
    assert client.page_calls == calls_after_scan


@pytest.mark.parametrize("detailed_subtype", ["live", [], {}])
def test_scan_requests_standard_pages_and_rejects_an_unsupported_detailed_subtype(
    tmp_path: Path,
    detailed_subtype: Any,
) -> None:
    module = load_batch()

    class RecordingClient(FakeBatchClient):
        def __init__(self) -> None:
            super().__init__(1)
            self.list_params: list[dict[str, Any]] = []

        def json(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
            if path == "/wiki/api/v2/pages":
                self.list_params.append(dict(kwargs.get("params") or {}))
            return super().json(method, path, **kwargs)

        def page(self, page_id: str, representation: str = "storage") -> dict[str, Any]:
            page = super().page(page_id, representation)
            page["subtype"] = detailed_subtype
            return page

    client = RecordingClient()
    result = module.scan_space(client, "7", tmp_path / "live-doc.json")

    assert client.list_params == [
        {"space-id": "7", "status": "current", "subtype": "page", "limit": 250}
    ]
    assert result["status"] == "partial"
    assert result["pages"] == []
    assert result["errors"][0]["stage"] == "inventory-page"
    assert "unsupported Confluence page subtype" in result["errors"][0]["error"]
    assert client.page_calls == 1


@pytest.mark.parametrize("listed_subtype", ["live", [], {}])
def test_scan_rejects_an_explicit_unsupported_subtype_before_page_fetch(
    tmp_path: Path,
    listed_subtype: Any,
) -> None:
    module = load_batch()
    client = FakeBatchClient(1)
    client.json = lambda *_args, **_kwargs: {  # type: ignore[method-assign]
        "results": [{"id": "1", "subtype": listed_subtype}],
        "_links": {},
    }

    result = module.scan_space(client, "7", tmp_path / "listed-live-doc.json")

    assert result["status"] == "partial"
    assert result["pages"] == []
    assert "unsupported Confluence page-list subtype" in result["errors"][0]["error"]
    assert client.page_calls == 0


@pytest.mark.parametrize("malformed_next", [[], {}])
def test_scan_persists_partial_for_a_malformed_next_link(
    tmp_path: Path,
    malformed_next: Any,
) -> None:
    module = load_batch()
    client = FakeBatchClient(1)
    client.json = lambda *_args, **_kwargs: {  # type: ignore[method-assign]
        "results": [{"id": "1"}],
        "_links": {"next": malformed_next},
    }

    result = module.scan_space(client, "7", tmp_path / "malformed-next.json")

    assert result["status"] == "partial"
    assert [page["page_id"] for page in result["pages"]] == ["1"]
    assert "next link must be a non-empty URL" in result["errors"][-1]["error"]


@pytest.mark.parametrize("malformed_entry", [None, [], {}, {"title": "missing"}, {"id": "abc"}])
def test_scan_persists_partial_for_a_malformed_listing_entry(
    tmp_path: Path,
    malformed_entry: Any,
) -> None:
    module = load_batch()
    client = FakeBatchClient(1)
    client.json = lambda *_args, **_kwargs: {  # type: ignore[method-assign]
        "results": [malformed_entry],
        "_links": {},
    }

    result = module.scan_space(client, "7", tmp_path / "malformed-entry.json")

    assert result["status"] == "partial"
    assert result["pages"] == []
    assert result["errors"][0]["stage"] == "inventory-page"


@pytest.mark.parametrize("malformed_links", [[], "", 0, False])
def test_scan_persists_partial_for_malformed_pagination_links(
    tmp_path: Path,
    malformed_links: Any,
) -> None:
    module = load_batch()
    client = FakeBatchClient(1)
    client.json = lambda *_args, **_kwargs: {  # type: ignore[method-assign]
        "results": [{"id": "1"}],
        "_links": malformed_links,
    }

    result = module.scan_space(client, "7", tmp_path / "malformed-links.json")

    assert result["status"] == "partial"
    assert [page["page_id"] for page in result["pages"]] == ["1"]
    assert "listing _links must be an object" in result["errors"][-1]["error"]


@pytest.mark.parametrize(
    "next_link, expected_error",
    [
        (
            "/wiki/api/v2/pages?cursor=x",
            "must preserve space-id=7",
        ),
        (
            "/wiki/api/v2/pages?cursor=x&space-id=7&status=current&subtype=live",
            "must preserve subtype=page",
        ),
        (
            "/wiki/api/v2/pages?cursor=x&space-id=999&status=current&subtype=page",
            "must preserve space-id=7",
        ),
        (
            "/wiki/api/v2/pages?cursor=x&space-id=7&status=draft&subtype=page",
            "must preserve status=current",
        ),
        (
            "/wiki/api/v2/pages?cursor=x&space-id=7&status=current&subtype=page&id=1",
            "unexpected query fields: id",
        ),
    ],
)
def test_scan_rejects_pagination_that_changes_or_drops_invariants(
    tmp_path: Path,
    next_link: str,
    expected_error: str,
) -> None:
    module = load_batch()
    client = FakeBatchClient(1)
    client.json = lambda *_args, **_kwargs: {  # type: ignore[method-assign]
        "results": [{"id": "1"}],
        "_links": {"next": next_link},
    }

    result = module.scan_space(client, "7", tmp_path / "changed-filter.json")

    assert result["status"] == "partial"
    assert [page["page_id"] for page in result["pages"]] == ["1"]
    assert expected_error in result["errors"][-1]["error"]


def test_scan_extracts_excel_cells_without_embedded_css_or_scripts(tmp_path: Path) -> None:
    module = load_batch()

    class ExcelViewClient(FakeBatchClient):
        def page(self, page_id: str, representation: str = "storage") -> dict[str, Any]:
            page = super().page(page_id, representation)
            if representation == "view":
                page["body"]["view"]["value"] = """
                    <article>
                      <h1>Office verification</h1>
                      <style>.outer-secret { color: red; }</style>
                      <script>window.outerSecret = true;</script>
                      <template>
                        template-only text
                        <div class="html-viewer-unsafe-html-content">
                          &lt;table&gt;&lt;tr&gt;&lt;td&gt;template worksheet leak&lt;/td&gt;&lt;/tr&gt;&lt;/table&gt;
                        </div>
                      </template>
                      <noscript>noscript-only text</noscript>
                      <div class="conf-macro html-viewer-unsafe-html-content">
                        &lt;style&gt;.cell-secret { font-weight: bold; }&lt;/style&gt;
                        &lt;script&gt;window.cellSecret = true;&lt;/script&gt;
                        &lt;template&gt;encoded-template-only text&lt;/template&gt;
                        &lt;noscript&gt;encoded-noscript-only text&lt;/noscript&gt;
                        &lt;div class=&quot;cells-worksheet&quot;&gt;
                          &lt;table&gt;&lt;tr&gt;
                            &lt;td&gt;Storage round-trip&lt;/td&gt;
                            &lt;td&gt;30&lt;/td&gt;
                          &lt;/tr&gt;&lt;/table&gt;
                        &lt;/div&gt;
                      </div>
                      <p>Other visible text</p>
                      <p>Literal example: &lt;style&gt; is documentation.</p>
                    </article>
                """
            return page

    inventory_path = tmp_path / "inventory.json"
    scanned = module.scan_space(ExcelViewClient(1), "7", inventory_path)

    visible_text = scanned["pages"][0]["visible_text"]
    assert "Office verification" in visible_text
    assert "Storage round-trip 30" in visible_text
    assert "Other visible text" in visible_text
    assert "Literal example: <style> is documentation." in visible_text
    assert "outer-secret" not in visible_text
    assert "cell-secret" not in visible_text
    assert "template-only text" not in visible_text
    assert "template worksheet leak" not in visible_text
    assert "noscript-only text" not in visible_text


def test_scan_persists_partial_inventory_and_surfaces_http_429(tmp_path: Path) -> None:
    module = load_batch()
    client = FakeBatchClient(2)
    client.paginated_rate_limit = True
    inventory_path = tmp_path / "inventory.json"

    result = module.scan_space(client, "7", inventory_path)

    assert result["status"] == "partial"
    assert result["rate_limited"] is True
    assert [page["page_id"] for page in result["pages"]] == ["1"]
    assert module.core.load_json(inventory_path)["errors"][0]["stage"] == "list-pages"


def test_page_id_filter_selects_an_explicit_union_without_network(tmp_path: Path) -> None:
    module = load_batch()
    client = FakeBatchClient(3)
    inventory_path = tmp_path / "inventory.json"
    module.scan_space(client, "7", inventory_path)
    calls_after_scan = client.page_calls

    explored = module.explore_inventory(inventory_path, page_id=["1", "3"])

    assert [page["page_id"] for page in explored["pages"]] == ["1", "3"]
    assert explored["filters"]["page_id"] == ["1", "3"]
    assert client.page_calls == calls_after_scan


def test_batch_edit_prevalidates_every_candidate_and_plan_covers_sidecars(tmp_path: Path) -> None:
    module, client, _, manifest = prepare_batch(tmp_path, page_count=2)
    workspace_one = manifest.parent / "workspaces" / "1"
    workspace_two = manifest.parent / "workspaces" / "2"
    originals = [
        (workspace_one / module.core.STORAGE_NAME).read_text(encoding="utf-8"),
        (workspace_two / module.core.STORAGE_NAME).read_text(encoding="utf-8"),
    ]

    with pytest.raises(module.core.ValidationError, match="well-formed"):
        module.batch_edit(manifest, append_storage="<p>")
    assert (workspace_one / module.core.STORAGE_NAME).read_text(encoding="utf-8") == originals[0]
    assert (workspace_two / module.core.STORAGE_NAME).read_text(encoding="utf-8") == originals[1]

    edited = module.batch_edit(
        manifest,
        append_storage="<p>Locally appended</p>",
        add_labels=["reviewed"],
        remove_labels=["batch"],
        title_prefix="[Reviewed] ",
        title_suffix=" — Final",
    )
    validation = module.batch_validate(manifest)
    updates_before = sum(client.update_attempts.values())
    plan = module.batch_plan(client, manifest)

    assert edited["status"] == "edited"
    assert validation["status"] == "verified"
    assert plan["status"] == "verified"
    assert plan["forced"] is False
    assert sum(client.update_attempts.values()) == updates_before
    for page in plan["pages"]:
        assert page["plan"]["page_update"] is True
        assert page["plan"]["labels"] == {"added": ["reviewed"], "removed": ["batch"]}
        assert page["plan"]["no_op"] is False


def test_batch_upload_does_not_mutate_when_any_workspace_fails_prevalidation(tmp_path: Path) -> None:
    module, client, _, manifest = prepare_batch(tmp_path, page_count=2)
    workspace_two = manifest.parent / "workspaces" / "2"
    (workspace_two / module.core.STORAGE_NAME).write_text("<p>stale local edit</p>", encoding="utf-8")
    calls_before = client.page_calls

    result = module.batch_upload(client, manifest, message="Must not run")

    assert result["status"] == "partial"
    assert result["preflight"]["status"] == "failed"
    assert sum(client.update_attempts.values()) == 0
    assert client.page_calls == calls_before


def test_partial_429_report_resumes_without_reuploading_verified_pages(tmp_path: Path) -> None:
    module, client, _, manifest = prepare_batch(tmp_path, page_count=3)
    module.batch_edit(manifest, append_storage="<p>Resume-safe change</p>")
    client.fail_update_once.add("2")

    partial = module.batch_upload(client, manifest, message="First attempt")

    assert partial["status"] == "partial"
    assert partial["rate_limited"] is True
    assert [page["status"] for page in partial["pages"]] == ["verified", "failed", "pending"]
    assert partial["atomic"] is False
    assert partial["rollback_attempted"] is False
    assert partial["pages"][1]["mutation_state"] == "unknown-partial"
    assert client.update_successes == {"1": 1, "2": 0, "3": 0}
    binding = partial["pages"][0]["verification_binding"]
    assert set(binding) == {
        "desired_state_sha256",
        "operation_id",
        "remote_version",
        "api_report_sha256",
        "page_id",
    }
    assert binding["remote_version"] == client.pages["1"]["version"]

    completed = module.batch_upload(client, manifest, message="Resume", resume=True)

    assert completed["status"] == "verified"
    assert [page["status"] for page in completed["pages"]] == ["verified", "verified", "verified"]
    assert completed["resumed"] is True
    assert completed["history"][0]["previous_status"] == "partial"
    assert completed["history"][0]["previous_errors"][0]["rate_limited"] is True
    assert client.update_successes == {"1": 1, "2": 1, "3": 1}
    assert client.update_attempts == {"1": 1, "2": 2, "3": 1}


def test_batch_resume_reprocesses_verified_page_when_desired_state_changes(tmp_path: Path) -> None:
    module, client, _, manifest = prepare_batch(tmp_path, page_count=2)
    module.batch_edit(manifest, append_storage="<p>Initial batch change</p>")
    first = module.batch_upload(client, manifest, message="Initial upload")
    first_binding = first["pages"][0]["verification_binding"]
    workspace = manifest.parent / "workspaces" / "1"
    storage = workspace / module.core.STORAGE_NAME
    storage.write_text(
        storage.read_text(encoding="utf-8") + "<p>Changed after verified row</p>",
        encoding="utf-8",
    )
    module.core.capture_ground_truth(workspace)

    resumed = module.batch_upload(client, manifest, message="Reprocess stale row", resume=True)

    assert resumed["status"] == "verified"
    assert client.update_successes == {"1": 2, "2": 1}
    current = resumed["pages"][0]["verification_binding"]
    assert current["operation_id"] != first_binding["operation_id"]
    assert current["desired_state_sha256"] == module.core.desired_state_sha256(workspace)
    report = workspace / module.core.VERIFY_DIR / module.core.REPORT_NAME
    assert current["api_report_sha256"] == module._file_sha256(report)


def test_batch_verify_refreshes_once_and_emits_one_row_per_page(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module, client, _, manifest = prepare_batch(tmp_path, page_count=2)
    real_refresh = module.core.refresh_manifest
    refreshes: list[str] = []

    def counting_refresh(client_arg: Any, workspace: Path, **kwargs: Any) -> None:
        refreshes.append(workspace.name)
        real_refresh(client_arg, workspace, **kwargs)

    monkeypatch.setattr(module.core, "refresh_manifest", counting_refresh)

    result = module.batch_verify(client, manifest)

    assert result["status"] == "verified"
    assert refreshes == ["1", "2"]
    assert [page["page_id"] for page in result["pages"]] == ["1", "2"]


def test_batch_verify_failure_emits_one_failed_row(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    module, client, _, manifest = prepare_batch(tmp_path, page_count=2)
    real_verify = module.core.verify_workspace

    def fail_first(client_arg: Any, workspace: Path, **kwargs: Any) -> dict[str, Any]:
        if workspace.name == "1":
            raise module.core.RoundTripError("simulated verification failure")
        return real_verify(client_arg, workspace, **kwargs)

    monkeypatch.setattr(module.core, "verify_workspace", fail_first)

    result = module.batch_verify(client, manifest)

    assert result["status"] == "partial"
    assert [page["page_id"] for page in result["pages"]] == ["1", "2"]
    assert len([page for page in result["pages"] if page["page_id"] == "1"]) == 1
    assert result["pages"][0]["status"] == "failed"


def test_batch_verify_and_completion_require_every_page(tmp_path: Path) -> None:
    module, client, _, manifest = prepare_batch(tmp_path, page_count=2)
    module.batch_edit(manifest, append_storage="<p>Verified change</p>")
    assert module.batch_upload(client, manifest, message="Verify all")["status"] == "verified"

    verified = module.batch_verify(client, manifest)
    for page_id in ("1", "2"):
        write_browser_evidence(module, manifest.parent / "workspaces" / page_id, page_id)
    completion = module.batch_completion_gate(manifest)

    assert verified["status"] == "verified"
    assert completion["status"] == "verified"
    assert all(page["status"] == "verified" for page in completion["pages"])

    final = manifest.parent / "workspaces" / "2" / module.core.VERIFY_DIR / "browser-final.png"
    final.write_bytes(b"tampered")
    failed = module.batch_completion_gate(manifest)
    assert failed["status"] == "failed"
    assert failed["pages"][1]["status"] == "failed"


def test_batch_edit_rejects_conflicting_label_operations_before_writes(tmp_path: Path) -> None:
    module, _, _, manifest = prepare_batch(tmp_path, page_count=1)
    workspace = manifest.parent / "workspaces" / "1"
    labels = (workspace / module.core.LABELS_NAME).read_bytes()

    with pytest.raises(module.core.ValidationError, match="same label"):
        module.batch_edit(manifest, add_labels=["Reviewed"], remove_labels=["reviewed"])

    assert (workspace / module.core.LABELS_NAME).read_bytes() == labels


def test_internal_page_references_drive_one_source_before_consumer_order(tmp_path: Path) -> None:
    module, client, _, manifest = prepare_batch(tmp_path, page_count=3)
    payload = module.core.load_json(manifest)
    payload["pages"].reverse()
    module.core.write_json(manifest, payload)
    consumer = manifest.parent / "workspaces" / "3"
    storage_path = consumer / module.core.STORAGE_NAME
    storage_path.write_text(
        storage_path.read_text(encoding="utf-8")
        + '<p><ri:page ri:content-id="1" /></p>'
        + '<p><ri:page ri:content-title="Release page 2" /></p>'
        + '<!-- <ri:page ri:content-id="outside-comment" /> -->'
        + '<ac:plain-text-body><![CDATA[<ri:page ri:content-id="outside-cdata" />]]></ac:plain-text-body>',
        encoding="utf-8",
    )
    module.core.capture_ground_truth(consumer)
    module.batch_edit(manifest, append_storage="<p>Dependency-ordered edit</p>")

    validation = module.batch_validate(manifest)
    plan = module.batch_plan(client, manifest)
    uploaded = module.batch_upload(client, manifest, message="Dependency order")
    verified = module.batch_verify(client, manifest)

    expected = ["2", "1", "3"]
    for report in (validation, plan, uploaded, verified):
        assert report["dependency_order"] == expected
        assert [page["page_id"] for page in report["pages"]] == expected
        assert report["dependencies"] == {"1": [], "2": [], "3": ["2", "1"]}
    assert client.update_order == expected


def test_explicit_dependencies_are_validated_and_topologically_ordered(tmp_path: Path) -> None:
    module, _, _, manifest = prepare_batch(tmp_path, page_count=3)
    payload = module.core.load_json(manifest)
    payload["pages"].reverse()
    by_id = {page["page_id"]: page for page in payload["pages"]}
    by_id["3"]["depends_on"] = ["1"]
    module.core.write_json(manifest, payload)

    ordered = module.batch_validate(manifest)

    assert ordered["status"] == "verified"
    assert ordered["dependency_order"] == ["2", "1", "3"]
    assert ordered["dependencies"]["3"] == ["1"]

    by_id["3"]["depends_on"] = ["missing"]
    module.core.write_json(manifest, payload)
    with pytest.raises(module.core.ValidationError, match="unknown batch page ID"):
        module.batch_validate(manifest)

    by_id["3"]["depends_on"] = ["3"]
    module.core.write_json(manifest, payload)
    with pytest.raises(module.core.ValidationError, match="cannot depend on itself"):
        module.batch_validate(manifest)

    by_id["3"]["depends_on"] = ["1"]
    by_id["1"]["depends_on"] = ["3"]
    module.core.write_json(manifest, payload)
    with pytest.raises(module.core.ValidationError, match="dependency cycle"):
        module.batch_validate(manifest)


def test_inferred_dependency_self_reference_and_cycle_fail_validation(tmp_path: Path) -> None:
    module, _, _, manifest = prepare_batch(tmp_path, page_count=2)
    workspace_one = manifest.parent / "workspaces" / "1"
    storage_one = workspace_one / module.core.STORAGE_NAME
    storage_one.write_text(
        storage_one.read_text(encoding="utf-8") + '<ri:page ri:content-id="1" />',
        encoding="utf-8",
    )
    module.core.capture_ground_truth(workspace_one)

    self_reference = module.batch_validate(manifest)

    assert self_reference["status"] == "failed"
    assert self_reference["errors"] == ["page 1 has an internal reference to itself"]

    storage_one.write_text(
        '<p>Page one</p><ri:page ri:content-id="2" />',
        encoding="utf-8",
    )
    module.core.capture_ground_truth(workspace_one)
    workspace_two = manifest.parent / "workspaces" / "2"
    storage_two = workspace_two / module.core.STORAGE_NAME
    storage_two.write_text(
        '<p>Page two</p><ri:page ri:content-title="Release page 1" />',
        encoding="utf-8",
    )
    module.core.capture_ground_truth(workspace_two)

    cycle = module.batch_validate(manifest)

    assert cycle["status"] == "failed"
    assert cycle["errors"] == ["batch dependency cycle detected among page IDs: 1, 2"]


def test_scan_rejects_repeated_pages_and_wrong_pagination_endpoints(tmp_path: Path) -> None:
    module = load_batch()
    duplicate_client = FakeBatchClient(1)
    duplicate_calls = 0

    def duplicate_json(_method: str, _path: str, **_kwargs: Any) -> dict[str, Any]:
        nonlocal duplicate_calls
        duplicate_calls += 1
        return {
            "results": [{"id": "1"}],
            "_links": {
                "next": (
                    "/wiki/api/v2/pages?cursor=repeat&limit=250&space-id=7"
                    "&status=current&subtype=page"
                    if duplicate_calls == 1
                    else None
                )
            },
        }

    duplicate_client.json = duplicate_json  # type: ignore[method-assign]
    duplicate = module.scan_space(duplicate_client, "7", tmp_path / "duplicate.json")

    assert duplicate["status"] == "partial"
    assert [page["page_id"] for page in duplicate["pages"]] == ["1"]
    assert "repeated page ID" in duplicate["errors"][0]["error"]

    endpoint_client = FakeBatchClient(1)
    endpoint_client.json = lambda *_args, **_kwargs: {  # type: ignore[method-assign]
        "results": [{"id": "1"}],
        "_links": {"next": "/wiki/api/v2/pages/1/labels"},
    }
    endpoint = module.scan_space(endpoint_client, "7", tmp_path / "endpoint.json")

    assert endpoint["status"] == "partial"
    assert endpoint["errors"][-1]["stage"] == "list-pages"
    assert "must remain on /wiki/api/v2/pages" in endpoint["errors"][-1]["error"]

    cursor_client = FakeBatchClient(1)
    cursor_calls = 0

    def repeated_cursor_with_changed_limit(
        *_args: Any, **_kwargs: Any
    ) -> dict[str, Any]:
        nonlocal cursor_calls
        cursor_calls += 1
        return {
            "results": [],
            "_links": {
                "next": (
                    f"/wiki/api/v2/pages?cursor=same&limit={cursor_calls}"
                    "&space-id=7&status=current&subtype=page"
                )
            },
        }

    cursor_client.json = repeated_cursor_with_changed_limit  # type: ignore[method-assign]
    cursor = module.scan_space(cursor_client, "7", tmp_path / "cursor.json")
    assert cursor["status"] == "partial"
    assert "cursor repeated" in cursor["errors"][-1]["error"]
    assert cursor_calls == 2

    origin_client = FakeBatchClient(1)
    origin_client.json = lambda *_args, **_kwargs: {  # type: ignore[method-assign]
        "results": [],
        "_links": {"next": "https://evil.example/wiki/api/v2/pages?cursor=x"},
    }
    origin = module.scan_space(origin_client, "7", tmp_path / "origin.json")
    assert origin["status"] == "partial"
    assert "configured Confluence origin" in origin["errors"][-1]["error"]


def test_scan_rejects_a_page_outside_the_requested_space(tmp_path: Path) -> None:
    module = load_batch()
    client = FakeBatchClient(1)
    real_page = client.page

    def wrong_space(page_id: str, representation: str = "storage") -> dict[str, Any]:
        page = real_page(page_id, representation)
        page["spaceId"] = "8"
        return page

    client.page = wrong_space  # type: ignore[method-assign]
    result = module.scan_space(client, "7", tmp_path / "wrong-space.json")

    assert result["status"] == "partial"
    assert result["pages"] == []
    assert "not requested space 7" in result["errors"][0]["error"]


def test_explicit_page_id_filter_rejects_any_absent_inventory_id(tmp_path: Path) -> None:
    module = load_batch()
    client = FakeBatchClient(2)
    inventory = tmp_path / "inventory.json"
    module.scan_space(client, "7", inventory)

    with pytest.raises(module.core.ValidationError, match="absent from the inventory: 999"):
        module.explore_inventory(inventory, page_id=["1", "999"])


def test_batch_manifest_identity_must_match_every_workspace(tmp_path: Path) -> None:
    module, _, _, manifest = prepare_batch(tmp_path, page_count=1)
    original = module.core.load_json(manifest)
    payload = json.loads(json.dumps(original))
    payload["pages"][0]["page_id"] = "999"
    payload["selection"]["page_ids"] = ["999"]
    module.core.write_json(manifest, payload)

    with pytest.raises(module.core.ValidationError, match="does not match workspace page identity"):
        module.batch_validate(manifest)

    payload = json.loads(json.dumps(original))
    payload["base_url"] = "https://other.atlassian.net"
    module.core.write_json(manifest, payload)
    with pytest.raises(module.core.ValidationError, match="different Confluence tenant"):
        module.batch_validate(manifest)

    payload = json.loads(json.dumps(original))
    payload["space_id"] = "8"
    module.core.write_json(manifest, payload)
    with pytest.raises(module.core.ValidationError, match="belongs to space 7, not 8"):
        module.batch_validate(manifest)

    payload = json.loads(json.dumps(original))
    payload["batch_id"] = "0" * 20
    module.core.write_json(manifest, payload)
    with pytest.raises(module.core.ValidationError, match="do not match its batch_id"):
        module.batch_validate(manifest)


def test_batch_report_output_cannot_overwrite_page_evidence(tmp_path: Path) -> None:
    module, client, _, manifest = prepare_batch(tmp_path, page_count=1)
    module.batch_edit(manifest, append_storage="<p>Output isolation</p>")
    workspace = manifest.parent / "workspaces" / "1"
    target = workspace / module.core.VERIFY_DIR / module.core.REPORT_NAME

    with pytest.raises(module.core.ValidationError, match="outside page workspaces"):
        module.batch_upload(client, manifest, message="Must not start", output=target)

    assert client.update_attempts == {"1": 0}
    assert not target.exists()


def test_batch_manifest_rejects_in_root_workspace_symlinks(tmp_path: Path) -> None:
    module, _, _, manifest = prepare_batch(tmp_path, page_count=1)
    target = manifest.parent / "workspaces" / "1"
    alias = manifest.parent / "workspaces" / "alias"
    try:
        alias.symlink_to(target, target_is_directory=True)
    except OSError as error:
        pytest.skip(f"directory symlinks are unavailable: {error}")
    payload = module.core.load_json(manifest)
    payload["pages"][0]["workspace"] = "workspaces/alias"
    module.core.write_json(manifest, payload)

    with pytest.raises(module.core.ValidationError, match="symbolic link or junction"):
        module.batch_validate(manifest)


def test_dependency_inference_respects_external_ids_and_space_keys(tmp_path: Path) -> None:
    module, _, _, manifest = prepare_batch(tmp_path, page_count=3)
    workspace = manifest.parent / "workspaces" / "1"
    storage = workspace / module.core.STORAGE_NAME
    storage.write_text(
        storage.read_text(encoding="utf-8")
        + '<ri:page ri:content-id="999" ri:content-title="Release page 2" />'
        + '<ri:page ri:space-key="OTHER" ri:content-title="Release page 3" />'
        + '<ri:page ri:space-key="@self" ri:content-title="Release page 2" />',
        encoding="utf-8",
    )
    module.core.capture_ground_truth(workspace)

    validation = module.batch_validate(manifest)

    assert validation["status"] == "verified"
    assert validation["dependencies"]["1"] == ["2"]


def test_resume_rechecks_remote_noop_immediately_before_skip(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module, client, _, manifest = prepare_batch(tmp_path, page_count=1)
    module.batch_edit(manifest, append_storage="<p>Resume race</p>")
    assert module.batch_upload(client, manifest, message="Initial")["status"] == "verified"
    real_plan = module.batch_plan

    def race_after_preflight(client_arg: Any, manifest_arg: Path, **kwargs: Any) -> dict[str, Any]:
        plan = real_plan(client_arg, manifest_arg, **kwargs)
        client.pages["1"]["storage"] += "<p>Concurrent remote edit</p>"
        client.pages["1"]["version"] += 1
        return plan

    monkeypatch.setattr(module, "batch_plan", race_after_preflight)
    resumed = module.batch_upload(client, manifest, message="Resume", resume=True)

    assert resumed["status"] == "partial"
    assert resumed["pages"][0]["status"] == "failed"
    assert client.update_successes == {"1": 1}


def test_batch_upload_rejects_local_dependency_change_after_preflight(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module, client, _, manifest = prepare_batch(tmp_path, page_count=2)
    module.batch_edit(manifest, append_storage="<p>Preflight snapshot</p>")
    real_upload = module.core.upload_workspace
    changed = False

    def race_before_page_upload(client_arg: Any, workspace: Path, **kwargs: Any) -> dict[str, Any]:
        nonlocal changed
        workspace = Path(workspace)
        if workspace.name == "1" and not changed:
            storage = workspace / module.core.STORAGE_NAME
            storage.write_text(
                storage.read_text(encoding="utf-8")
                + '<ri:page ri:content-id="2" />',
                encoding="utf-8",
            )
            module.core.capture_ground_truth(workspace)
            changed = True
        return real_upload(client_arg, workspace, **kwargs)

    monkeypatch.setattr(module.core, "upload_workspace", race_before_page_upload)
    result = module.batch_upload(client, manifest, message="Reject raced edit")

    assert result["status"] == "partial"
    assert result["pages"][0]["status"] == "failed"
    assert "changed after batch preflight" in result["pages"][0]["error"]
    assert client.update_order == []
    assert module.batch_validate(manifest)["dependency_order"] == ["2", "1"]


def test_batch_companion_remains_portable_with_its_sibling_script(tmp_path: Path) -> None:
    copied = tmp_path / "roundtrip-confluence-pages"
    shutil.copytree(SKILL_ROOT, copied)

    completed = subprocess.run(
        [sys.executable, str(copied / "scripts" / "confluence_batch.py"), "--help"],
        cwd=copied,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=30,
        check=False,
    )

    assert completed.returncode == 0
    assert "scan-space" in completed.stdout
    assert "batch-completion-gate" in completed.stdout


def test_batch_parser_exposes_every_standalone_command() -> None:
    module = load_batch()
    parser = module.build_parser()
    examples = {
        "scan-space": ["scan-space", "7", "inventory.json"],
        "explore": ["explore", "inventory.json"],
        "batch-download": ["batch-download", "inventory.json", "batch"],
        "batch-edit": ["batch-edit", "batch/batch-manifest.json"],
        "batch-validate": ["batch-validate", "batch/batch-manifest.json"],
        "batch-plan": ["batch-plan", "batch/batch-manifest.json"],
        "batch-upload": ["batch-upload", "batch/batch-manifest.json"],
        "batch-verify": ["batch-verify", "batch/batch-manifest.json"],
        "batch-completion-gate": [
            "batch-completion-gate",
            "batch/batch-manifest.json",
        ],
    }

    parsed = {name: parser.parse_args(arguments).command for name, arguments in examples.items()}

    assert parsed == {name: name for name in examples}


def test_batch_main_dispatches_every_cli_command(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    module = load_batch()
    calls: list[str] = []

    def stub(name: str) -> Any:
        def run(*_args: Any, **_kwargs: Any) -> dict[str, str]:
            calls.append(name)
            return {"status": "verified", "command": name}

        return run

    command_functions = {
        "explore": "explore_inventory",
        "batch-edit": "batch_edit",
        "batch-validate": "batch_validate",
        "batch-completion-gate": "batch_completion_gate",
        "scan-space": "scan_space",
        "batch-download": "batch_download",
        "batch-plan": "batch_plan",
        "batch-upload": "batch_upload",
        "batch-verify": "batch_verify",
    }
    for command, function_name in command_functions.items():
        monkeypatch.setattr(module, function_name, stub(command))
    monkeypatch.setattr(
        module.core,
        "credentials_from_args",
        lambda _args: ("https://example.atlassian.net", "user@example.com", "token"),
    )
    monkeypatch.setattr(module.core, "ConfluenceClient", lambda *_args, **_kwargs: object())
    examples = {
        "explore": ["explore", "inventory.json"],
        "batch-edit": ["batch-edit", "batch/batch-manifest.json"],
        "batch-validate": ["batch-validate", "batch/batch-manifest.json"],
        "batch-completion-gate": [
            "batch-completion-gate",
            "batch/batch-manifest.json",
        ],
        "scan-space": ["scan-space", "7", "inventory.json"],
        "batch-download": ["batch-download", "inventory.json", "batch"],
        "batch-plan": ["batch-plan", "batch/batch-manifest.json"],
        "batch-upload": ["batch-upload", "batch/batch-manifest.json"],
        "batch-verify": ["batch-verify", "batch/batch-manifest.json"],
    }

    for command, arguments in examples.items():
        assert module.main(arguments) == 0
        assert calls[-1] == command

    output = capsys.readouterr()
    records = [json.loads(line) for line in output.out.splitlines()]
    assert [record["command"] for record in records] == list(examples)
    assert output.err == ""


def test_batch_main_returns_nonzero_for_partial_results_and_validation_errors(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    module = load_batch()
    monkeypatch.setattr(
        module,
        "explore_inventory",
        lambda *_args, **_kwargs: {"status": "partial"},
    )

    assert module.main(["explore", "inventory.json"]) == 2
    assert json.loads(capsys.readouterr().out)["status"] == "partial"

    def fail(*_args: Any, **_kwargs: Any) -> dict[str, Any]:
        raise module.core.ValidationError("invalid inventory")

    monkeypatch.setattr(module, "explore_inventory", fail)
    assert module.main(["explore", "inventory.json"]) == 2
    error = json.loads(capsys.readouterr().err)
    assert error == {"error": "invalid inventory", "type": "ValidationError"}


def test_batch_cli_emits_unicode_json_on_windows_code_pages(tmp_path: Path) -> None:
    module = load_batch()
    inventory = tmp_path / "space-inventory.json"
    module.core.write_json(
        inventory,
        {
            "schema_version": module.BATCH_SCHEMA_VERSION,
            "kind": module.INVENTORY_KIND,
            "status": "verified",
            "pages": [
                {
                    "page_id": "1",
                    "title": "Flow ⤴ page",
                    "visible_text": "Flow ⤴ page",
                }
            ],
        },
    )

    completed = subprocess.run(
        [
            sys.executable,
            str(SKILL_ROOT / "scripts" / "confluence_batch.py"),
            "explore",
            str(inventory),
        ],
        cwd=SKILL_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=30,
        check=False,
        env={**os.environ, "PYTHONIOENCODING": "cp1252"},
    )

    assert completed.returncode == 0
    assert "Flow ⤴ page" in completed.stdout
