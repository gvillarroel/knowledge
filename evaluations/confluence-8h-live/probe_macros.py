#!/usr/bin/env python3
"""Probe tenant acceptance of individual Confluence storage macros through the skill."""

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
    """Load the standalone skill script without relying on repository imports."""

    module_name = "confluence_macro_probe_" + sha256(
        str(CORE_PATH).encode("utf-8")
    ).hexdigest()[:12]
    spec = importlib.util.spec_from_file_location(module_name, CORE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {CORE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


MACROS: list[tuple[str, str]] = [
    (
        "toc",
        '<ac:structured-macro ac:name="toc"><ac:parameter ac:name="maxLevel">3</ac:parameter>'
        '<ac:parameter ac:name="printable">true</ac:parameter></ac:structured-macro>',
    ),
    (
        "pagetree",
        '<ac:structured-macro ac:name="pagetree" />',
    ),
    (
        "children",
        '<ac:structured-macro ac:name="children"><ac:parameter ac:name="all">true</ac:parameter>'
        '<ac:parameter ac:name="sort">creation</ac:parameter></ac:structured-macro>',
    ),
    (
        "attachments",
        '<ac:structured-macro ac:name="attachments"><ac:parameter ac:name="old">false</ac:parameter>'
        '</ac:structured-macro>',
    ),
    (
        "contentbylabel",
        '<ac:structured-macro ac:name="contentbylabel"><ac:parameter ac:name="labels">roundtrip-campaign'
        '</ac:parameter><ac:parameter ac:name="max">20</ac:parameter><ac:parameter ac:name="cql">'
        'label = &quot;roundtrip-campaign&quot;</ac:parameter></ac:structured-macro>',
    ),
    (
        "recently-updated",
        '<ac:structured-macro ac:name="recently-updated"><ac:parameter ac:name="max">10</ac:parameter>'
        '<ac:parameter ac:name="types">page</ac:parameter></ac:structured-macro>',
    ),
    ("change-history", '<ac:structured-macro ac:name="change-history" />'),
    (
        "contributors",
        '<ac:structured-macro ac:name="contributors"><ac:parameter ac:name="limit">10</ac:parameter>'
        '<ac:parameter ac:name="showAnonymous">false</ac:parameter></ac:structured-macro>',
    ),
    (
        "excerpt",
        '<ac:structured-macro ac:name="excerpt"><ac:parameter ac:name="hidden">false</ac:parameter>'
        '<ac:rich-text-body><p>Macro probe reusable excerpt.</p></ac:rich-text-body>'
        '</ac:structured-macro>',
    ),
    (
        "details",
        '<ac:structured-macro ac:name="details"><ac:parameter ac:name="id">probe-properties</ac:parameter>'
        '<ac:rich-text-body><table><tbody><tr><th><p>Probe</p></th><td><p>PASS</p></td>'
        '</tr></tbody></table></ac:rich-text-body></ac:structured-macro>',
    ),
    (
        "detailssummary",
        '<ac:structured-macro ac:name="detailssummary"><ac:parameter ac:name="cql">'
        'label = &quot;roundtrip-campaign&quot;</ac:parameter></ac:structured-macro>',
    ),
    (
        "livesearch",
        '<ac:structured-macro ac:name="livesearch"><ac:parameter ac:name="placeholder">Search this space'
        '</ac:parameter><ac:parameter ac:name="spaceKey"><ri:space ri:space-key="@self" />'
        '</ac:parameter></ac:structured-macro>',
    ),
    (
        "tasks-report",
        '<ac:structured-macro ac:name="tasks-report-macro"><ac:parameter ac:name="spaces">'
        '~701216ec7fd06929c4771add0ec012097b466</ac:parameter><ac:parameter ac:name="pageSize">20'
        '</ac:parameter><ac:parameter ac:name="status">incomplete</ac:parameter></ac:structured-macro>',
    ),
    (
        "listlabels",
        '<ac:structured-macro ac:name="listlabels"><ac:parameter ac:name="spaceKey">'
        '<ri:space ri:space-key="@self" /></ac:parameter></ac:structured-macro>',
    ),
    (
        "popular-labels",
        '<ac:structured-macro ac:name="popular-labels"><ac:parameter ac:name="count">20</ac:parameter>'
        '</ac:structured-macro>',
    ),
    (
        "profile-picture",
        '<ac:structured-macro ac:name="profile-picture"><ac:parameter ac:name="User">'
        '<ri:user ri:account-id="70121:6ec7fd06-929c-4771-add0-ec012097b466" />'
        '</ac:parameter></ac:structured-macro>',
    ),
    (
        "profile",
        '<ac:structured-macro ac:name="profile"><ac:parameter ac:name="user">'
        '<ri:user ri:account-id="70121:6ec7fd06-929c-4771-add0-ec012097b466" />'
        '</ac:parameter></ac:structured-macro>',
    ),
    (
        "widget",
        '<ac:structured-macro ac:name="widget"><ac:parameter ac:name="overlay">youtube'
        '</ac:parameter><ac:parameter ac:name="_template">com/atlassian/confluence/extra/'
        'widgetconnector/templates/youtube.vm</ac:parameter><ac:parameter ac:name="width">480px'
        '</ac:parameter><ac:parameter ac:name="url"><ri:url ri:value="https://www.youtube.com/'
        'watch?v=CNeuec8ybc4" /></ac:parameter><ac:parameter ac:name="height">300px</ac:parameter>'
        '</ac:structured-macro>',
    ),
]


def run_probe(
    core: ModuleType,
    client: Any,
    page_id: str,
    workspace: Path,
    output: Path,
    selected_macros: set[str] | None = None,
) -> dict[str, Any]:
    """Download once, then replace the page with one isolated macro at a time."""

    core.download_page(client, page_id, workspace, overwrite=True)
    results: list[dict[str, Any]] = []
    fixtures = [item for item in MACROS if not selected_macros or item[0] in selected_macros]
    unknown = sorted((selected_macros or set()) - {name for name, _macro in MACROS})
    if unknown:
        raise ValueError("unknown macro probes: " + ", ".join(unknown))
    for name, macro in fixtures:
        marker = f"Isolated macro probe: {name}"
        storage = (
            "<h2>Confluence macro acceptance probe</h2>"
            f"<p>{marker}</p>"
            f"<h3>{name}</h3>{macro}"
        )
        core.write_text(workspace / core.STORAGE_NAME, storage)
        core.capture_ground_truth(workspace, required_text=[marker])
        version_before = int(core.load_json(workspace / core.MANIFEST_NAME)["page"]["version"])
        try:
            upload = core.upload_workspace(
                client,
                workspace,
                message=f"Isolated Confluence macro probe: {name}",
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
            "macro": name,
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
    parser.add_argument("--macro", action="append", default=[])
    args = parser.parse_args(argv)
    core = load_core()
    credentials = argparse.Namespace(
        base_url=None,
        username=None,
        env_file=args.env_file,
    )
    base_url, username, token = core.credentials_from_args(credentials)
    client = core.ConfluenceClient(base_url, username, token, timeout=args.timeout)
    result = run_probe(
        core,
        client,
        str(args.page_id),
        args.workspace.resolve(),
        args.output.resolve(),
        set(args.macro) or None,
    )
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["failed"] == 0 else 3


if __name__ == "__main__":
    raise SystemExit(main())
