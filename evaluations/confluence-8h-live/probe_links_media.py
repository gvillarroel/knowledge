#!/usr/bin/env python3
"""Probe tenant acceptance of link and media storage sections through the skill."""

from __future__ import annotations

import argparse
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys
from types import ModuleType
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
CORE_PATH = (
    REPO_ROOT
    / "skills"
    / "roundtrip-confluence-pages"
    / "scripts"
    / "confluence_roundtrip.py"
)


def load_core() -> ModuleType:
    module_name = "confluence_links_media_probe_" + sha256(
        str(CORE_PATH).encode("utf-8")
    ).hexdigest()[:12]
    spec = importlib.util.spec_from_file_location(module_name, CORE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {CORE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


SECTIONS: list[tuple[str, str]] = [
    (
        "external-smart-links",
        """<h2>External, email, and Smart Links</h2>
<p><a href="https://support.atlassian.com/confluence-cloud/docs/insert-links-and-anchors/">External HTTPS documentation link</a></p>
<p><a href="mailto:villarroel.gj@gmail.com?subject=Confluence%20round-trip%20fixture">Email link fixture</a></p>
<p><a data-card-appearance="inline" href="https://support.atlassian.com/confluence-cloud/docs/work-with-images-videos-and-files/">Inline Smart Link fixture</a></p>
<p><a data-card-appearance="block" href="https://support.atlassian.com/confluence-cloud/docs/simplify-data-with-tables/">Block Smart Link fixture</a></p>""",
    ),
    (
        "internal-anchor-links",
        """<h2>Internal and anchor links</h2>
<p><ac:link><ri:page ri:content-title="Confluence 8h Lab — Text and Structure 2026-07-12" /><ac:link-body>Open the text and structure laboratory</ac:link-body></ac:link></p>
<p><ac:link><ri:page ri:content-title="Confluence 8h Undefined Page Fixture" /><ac:link-body>Undefined page creation link fixture</ac:link-body></ac:link></p>
<p><a href="#campaign-media-anchor">Jump to the media anchor</a></p>
<ac:structured-macro ac:name="anchor"><ac:parameter ac:name="">campaign-media-anchor</ac:parameter></ac:structured-macro>""",
    ),
    (
        "cross-page-excerpt",
        """<h2>Cross-page reusable content</h2>
<p>The following macro consumes the excerpt published by the macros laboratory:</p>
<ac:structured-macro ac:name="excerpt-include"><ac:parameter ac:name=""><ac:link><ri:page ri:content-title="Confluence 8h Lab — Macros and Dynamic Content 2026-07-12" /></ac:link></ac:parameter></ac:structured-macro>""",
    ),
    (
        "images",
        """<h2>Image attachments and controls</h2>
<p>PNG with center alignment, border, width, alt text, and caption:</p>
<ac:image ac:align="center" ac:border="true" ac:width="720">
  <ri:attachment ri:filename="campaign-diagram.png" />
  <ac:parameter ac:name="alt">Confluence round-trip architecture campaign diagram</ac:parameter>
  <ac:caption><p>PNG attachment with explicit storage controls.</p></ac:caption>
</ac:image>
<p>JPEG resized and right aligned:</p>
<ac:image ac:align="right" ac:width="360">
  <ri:attachment ri:filename="campaign-photo.jpg" />
  <ac:parameter ac:name="alt">JPEG conversion of the campaign architecture diagram</ac:parameter>
</ac:image>
<p>Animated GIF:</p>
<ac:image ac:align="center" ac:width="640">
  <ri:attachment ri:filename="campaign-animation.gif" />
  <ac:parameter ac:name="alt">Animated campaign diagram color transition</ac:parameter>
</ac:image>""",
    ),
    (
        "generic-files",
        """<h2>Generic files and previews</h2>
<ul>
  <li><ac:link><ri:attachment ri:filename="campaign-preview.pdf" /><ac:plain-text-link-body><![CDATA[Open PDF preview fixture]]></ac:plain-text-link-body></ac:link></li>
  <li><ac:link><ri:attachment ri:filename="campaign-video.mp4" /><ac:plain-text-link-body><![CDATA[Open MP4 video fixture]]></ac:plain-text-link-body></ac:link></li>
  <li><ac:link><ri:attachment ri:filename="campaign-audio.mp3" /><ac:plain-text-link-body><![CDATA[Open MP3 audio fixture]]></ac:plain-text-link-body></ac:link></li>
  <li><ac:link><ri:attachment ri:filename="campaign-data.csv" /><ac:plain-text-link-body><![CDATA[Open CSV data fixture]]></ac:plain-text-link-body></ac:link></li>
  <li><ac:link><ri:attachment ri:filename="campaign-notes.txt" /><ac:plain-text-link-body><![CDATA[Open plain-text fixture]]></ac:plain-text-link-body></ac:link></li>
</ul>""",
    ),
]


def run_probe(
    core: ModuleType,
    client: Any,
    page_id: str,
    workspace: Path,
    output: Path,
    selected_sections: set[str] | None = None,
) -> dict[str, Any]:
    core.download_page(client, page_id, workspace, overwrite=True)
    results: list[dict[str, Any]] = []
    fixtures = [item for item in SECTIONS if not selected_sections or item[0] in selected_sections]
    unknown = sorted((selected_sections or set()) - {name for name, _section in SECTIONS})
    if unknown:
        raise ValueError("unknown link/media probes: " + ", ".join(unknown))
    for name, section in fixtures:
        marker = f"Isolated link/media probe: {name}"
        storage = f"<h2>Confluence link and media acceptance probe</h2><p>{marker}</p>{section}"
        core.write_text(workspace / core.STORAGE_NAME, storage)
        core.capture_ground_truth(workspace, required_text=[marker])
        version_before = int(core.load_json(workspace / core.MANIFEST_NAME)["page"]["version"])
        try:
            upload = core.upload_workspace(
                client,
                workspace,
                message=f"Isolated Confluence link/media probe: {name}",
                verify=True,
            )
        except core.RoundTripError as error:
            upload = {
                "status": "failed",
                "page_updated": False,
                "error": {"type": type(error).__name__, "message": str(error)},
                "verification": {"status": "skipped"},
            }
        current = client.page(page_id, "storage")
        version_after = int((current.get("version") or {}).get("number") or 0)
        remote_storage = core.body_value(current, "storage")
        verification = upload.get("verification") or {}
        passed = upload.get("status") == "uploaded" and verification.get("status") == "verified"
        record: dict[str, Any] = {
            "section": name,
            "accepted": version_after > version_before,
            "passed": passed,
            "upload_status": upload.get("status"),
            "operation_id": upload.get("operation_id"),
            "version_before": version_before,
            "version_after": version_after,
            "verified_remote_version": verification.get("remote_version"),
            "remote_equivalent": core.remote_equivalence_storage(storage)
            == core.remote_equivalence_storage(remote_storage),
            "desired_storage": storage,
            "remote_storage": remote_storage,
        }
        if upload.get("error"):
            record["error"] = upload["error"]
        results.append(record)
        core.download_page(client, page_id, workspace, overwrite=True)
        interim = {
            "schema_version": "1.0",
            "page_id": page_id,
            "workspace": str(workspace),
            "tested": len(results),
            "accepted": sum(1 for item in results if item["accepted"]),
            "passed": sum(1 for item in results if item["passed"]),
            "failed": sum(1 for item in results if not item["passed"]),
            "results": results,
        }
        core.write_json(output, interim)
    return interim


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("page_id")
    parser.add_argument("workspace", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--env-file", type=Path, default=REPO_ROOT / ".env")
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument("--section", action="append", default=[])
    args = parser.parse_args(argv)
    core = load_core()
    credentials = argparse.Namespace(base_url=None, username=None, env_file=args.env_file)
    base_url, username, token = core.credentials_from_args(credentials)
    client = core.ConfluenceClient(base_url, username, token, timeout=args.timeout)
    result = run_probe(
        core,
        client,
        str(args.page_id),
        args.workspace.resolve(),
        args.output.resolve(),
        set(args.section) or None,
    )
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["failed"] == 0 else 3


if __name__ == "__main__":
    raise SystemExit(main())
