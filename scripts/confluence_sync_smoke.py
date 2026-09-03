"""Run an opt-in Confluence smoke test without touching existing remote content.

The default is a read-only access probe. --create-fixture creates a new isolated
space and synthetic pages, then exercises the public CLI twice. The space is
private unless --site-visible-fixture is explicitly supplied for plans such as
Confluence Free. Remote writes are never retried, and every attempted write is
journaled before transmission.
"""

from __future__ import annotations

import argparse
from contextlib import redirect_stdout
from datetime import UTC, datetime
import io
import json
import os
from pathlib import Path
import sys
import time
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]


def _write_report(path: Path, report: dict) -> None:
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(report, indent=2), encoding="utf-8")
    temporary.replace(path)


def _post_fixture(session, url: str, auth: tuple[str, str], payload: dict, report: dict, path: Path) -> dict:
    entry = {"title_or_key": payload.get("title") or payload.get("key"), "state": "started"}
    report["writes"].append(entry)
    _write_report(path, report)
    response = session.post(
        url, auth=auth, json=payload, timeout=(10, 30), allow_redirects=False,
        headers={"Accept": "application/json"},
    )
    try:
        entry["http_status"] = response.status_code
        if response.status_code not in (200, 201):
            entry["state"] = "unverified"
            raise RuntimeError(f"Fixture creation returned HTTP {response.status_code}; no write was retried")
        result = response.json()
        if not isinstance(result, dict) or not str(result.get("id", "")).isdigit():
            raise RuntimeError("Fixture creation returned an unverified identity; no write was retried")
        entry.update(state="created", id=str(result["id"]))
        return result
    finally:
        response.close()
        _write_report(path, report)


def main(argv: list[str] | None = None) -> int:
    """Probe access, or explicitly create and download an isolated fixture."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--create-fixture", action="store_true")
    parser.add_argument(
        "--site-visible-fixture",
        action="store_true",
        help="Create a fixture visible to signed-in site users (required by Confluence Free).",
    )
    parser.add_argument("--pages", type=int, default=40, help="Synthetic pages, from 1 to 80.")
    parser.add_argument("--body-kib", type=int, default=32, help="Approximate body size, from 1 to 128 KiB.")
    parser.add_argument("--output", type=Path, help="A new output directory below this repository.")
    args = parser.parse_args(argv)
    if args.site_visible_fixture and not args.create_fixture:
        parser.error("--site-visible-fixture requires --create-fixture")
    if not 1 <= args.pages <= 80 or not 1 <= args.body_kib <= 128:
        parser.error("Use 1-80 pages and 1-128 KiB bodies")
    run_id = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid4().hex[:8]
    directory = (args.output or ROOT / "tmp" / f"confluence-live-{run_id}").resolve()
    if not directory.is_relative_to(ROOT.resolve()):
        parser.error("Output must stay inside this repository")
    directory.mkdir(parents=True, exist_ok=False)
    temporary = directory / "temp"
    temporary.mkdir()
    os.environ["TMP"] = str(temporary)
    os.environ["TEMP"] = str(temporary)
    sys.path.insert(0, str(ROOT / "src"))

    import requests
    import yaml
    from knowledge.cli import load_dotenv, main as know_main
    from knowledge.sources.confluence_http import ConfluenceClient, ConfluenceOptions

    load_dotenv(ROOT / ".env")
    report = {"run_id": run_id, "complete": False, "phase": "preflight", "writes": []}
    report_path = directory / "live-report.json"
    _write_report(report_path, report)
    started = time.perf_counter()
    client = None
    try:
        base_url = os.environ["CONFLUENCE_BASE_URL"]
        auth = (os.environ["CONFLUENCE_USERNAME"], os.environ["CONFLUENCE_TOKEN"])
        with ConfluenceClient(base_url, auth, ConfluenceOptions(timeout=20, max_retries=2, max_retry_wait=20)) as client:
            client.get_json("rest/api/user/current")
            spaces = client.get_json("api/v2/spaces", {"limit": 1})
            if not isinstance(spaces.get("results"), list):
                raise RuntimeError("Space lookup returned malformed results")
            report.update(access="verified", preflight_requests=client.requests, preflight_retries=client.retries)
            if not args.create_fixture:
                report["complete"] = True
                return 0
            report["phase"] = "create-fixture"
            visibility = "site" if args.site_visible_fixture else "private"
            report["fixture_visibility"] = visibility
            _write_report(report_path, report)
            space_key = "KNOWTEST" + datetime.now(UTC).strftime("%m%d%H%M%S") + uuid4().hex[:4].upper()
            with requests.Session() as session:
                space = _post_fixture(
                    session, client.url("api/v2/spaces"), auth,
                    {
                        "key": space_key,
                        "name": f"Know synthetic sync test {run_id}",
                        "createPrivateSpace": not args.site_visible_fixture,
                    },
                    report, report_path,
                )
                report.update(space_key=space_key, space_id=str(space["id"]),
                              space_url=client.base_url + "wiki/spaces/" + space_key)
                expected_ids = []
                for number in range(1, args.pages + 1):
                    marker = f"Fixture page {number}: synthetic Confluence synchronization content. "
                    text = (marker * ((args.body_kib * 1024 // len(marker)) + 1))[:args.body_kib * 1024]
                    page = _post_fixture(
                        session, client.url("api/v2/pages"), auth,
                        {"spaceId": str(space["id"]), "status": "current", "title": f"Sync fixture {number:03d}",
                         "body": {"representation": "storage", "value": "<p>" + text + "</p>"}},
                        report, report_path,
                    )
                    expected_ids.append(str(page["id"]))
                    time.sleep(0.15)

        report["phase"] = "cli-sync"
        store = directory / "store"

        def run_cli(arguments):
            output = io.StringIO()
            with redirect_stdout(output):
                code = know_main(["--store", str(store), "--json", *arguments])
            if code != 0:
                raise RuntimeError("CLI operation failed; inspect the isolated store's sync report")
            return json.loads(output.getvalue())

        run_cli(["add", "key", "smoke"])
        run_cli(["add", "confluence", "--space", space_key, "--key", "smoke", "--base-url", base_url,
                 "--workers", "4", "--page-size", "5", "--timeout", "20", "--max-retries", "2"])
        first = run_cli(["sync", "confluence", "--key", "smoke"])["synced"][0]
        second = run_cli(["sync", "confluence", "--key", "smoke"])["synced"][0]
        ids = set()
        for document in Path(first["raw_dir"]).glob("*.md"):
            metadata = yaml.safe_load(document.read_text(encoding="utf-8").split("---", 2)[1])
            ids.add(str(metadata["document_id"]))
        if not set(expected_ids).issubset(ids) or second["downloaded"] != 0:
            raise RuntimeError("The downloaded fixture or unchanged-version reuse did not verify")
        report.update(
            complete=True, phase="verified", created_pages=len(expected_ids),
            first_sync={key: first[key] for key in ("pages", "downloaded", "reused", "requests", "retries")},
            second_sync={key: second[key] for key in ("pages", "downloaded", "reused", "requests", "retries")},
        )
        return 0
    except Exception as exc:
        from knowledge.errors import KnowledgeError
        report.update(error=str(exc) if isinstance(exc, (KnowledgeError, RuntimeError)) else type(exc).__name__)
        if client is not None:
            report.update(requests=client.requests, retries=client.retries)
        return 1
    finally:
        report["elapsed_seconds"] = round(time.perf_counter() - started, 3)
        _write_report(report_path, report)
        print(json.dumps({**report, "report": str(report_path)}, indent=2))


if __name__ == "__main__":
    raise SystemExit(main())
