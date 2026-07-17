"""Run a reproducible Zotero CLI proof of concept against a local library.

The POC deliberately uses only public Zotero HTTP interfaces to prepare its
fixture. All user-facing reads are then performed through ``zotero-cli`` so the
report distinguishes Zotero capabilities from capabilities supplied by the
community CLI.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Sequence
from urllib.error import HTTPError, URLError
from urllib.parse import quote, unquote, urlparse
from urllib.request import ProxyHandler, Request, build_opener, urlopen


DEFAULT_BASE_URL = "http://127.0.0.1:23119"
FIXTURE_TITLE = "Language agents achieve superhuman synthesis of scientific knowledge"
FIXTURE_WEB_TITLE = "Zotero CLI POC website record"
FIXTURE_URL = "https://arxiv.org/abs/2409.13740"
FIXTURE_PDF_URL = "https://arxiv.org/pdf/2409.13740"
FIXTURE_DOI = "10.48550/arXiv.2409.13740"
FIXTURE_FULLTEXT_TERM = "Gather Evidence"
FIXTURE_TAG = "know-zotero-cli-poc"


@dataclass(frozen=True)
class CommandResult:
    """Captured process result."""

    args: list[str]
    returncode: int
    stdout: str
    stderr: str


@dataclass(frozen=True)
class Probe:
    """One verified POC capability or gap."""

    name: str
    status: str
    evidence: str
    required: bool = False


class PocFailure(RuntimeError):
    """Raised when a required POC precondition or capability fails."""


def _local_opener():
    """Return an opener that never sends loopback requests through a proxy."""

    return build_opener(ProxyHandler({}))


def _request(
    base_url: str,
    path: str,
    *,
    method: str = "GET",
    body: bytes | None = None,
    headers: dict[str, str] | None = None,
    timeout: int = 60,
) -> tuple[int, dict[str, str], bytes]:
    """Make a request to the local Zotero server."""

    request = Request(
        f"{base_url.rstrip('/')}{path}",
        data=body,
        headers=headers or {},
        method=method,
    )
    try:
        with _local_opener().open(request, timeout=timeout) as response:
            return response.status, dict(response.headers.items()), response.read()
    except (HTTPError, URLError) as exc:
        raise PocFailure(f"Zotero request failed for {path}: {exc}") from exc


def _get_json(base_url: str, path: str) -> tuple[Any, dict[str, str]]:
    """Read JSON from the local Zotero API."""

    _, headers, body = _request(base_url, path)
    return json.loads(body.decode("utf-8")), headers


def _get_text(base_url: str, path: str) -> str:
    """Read text from the local Zotero API."""

    _, _, body = _request(base_url, path)
    return body.decode("utf-8")


def _post_json(base_url: str, path: str, payload: dict[str, Any]) -> int:
    """Post JSON to the Zotero Connector API."""

    status, _, _ = _request(
        base_url,
        path,
        method="POST",
        body=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "X-Zotero-Connector-API-Version": "3",
        },
    )
    return status


def _post_attachment(
    base_url: str,
    *,
    session_id: str,
    parent_connector_id: str,
    content: bytes,
) -> int:
    """Attach a PDF through the same local interface used by Zotero Connector."""

    metadata = json.dumps(
        {
            "sessionID": session_id,
            "title": "PaperQA2 full text",
            "parentItemID": parent_connector_id,
            "url": FIXTURE_PDF_URL,
        },
        separators=(",", ":"),
    )
    status, _, _ = _request(
        base_url,
        "/connector/saveAttachment",
        method="POST",
        body=content,
        headers={
            "Content-Type": "application/pdf",
            "X-Metadata": metadata,
            "X-Zotero-Connector-API-Version": "3",
        },
        timeout=120,
    )
    return status


def _download_fixture_pdf() -> bytes:
    """Download the public PaperQA2 fixture PDF."""

    request = Request(FIXTURE_PDF_URL, headers={"User-Agent": "knowledge-zotero-poc/1.0"})
    try:
        with urlopen(request, timeout=120) as response:  # noqa: S310 - fixed HTTPS fixture
            return response.read()
    except (HTTPError, URLError) as exc:
        raise PocFailure(f"Could not download the fixture PDF: {exc}") from exc


def _find_top_item(base_url: str, title: str) -> dict[str, Any] | None:
    """Find a top-level item by title."""

    items, _ = _get_json(
        base_url,
        f"/api/users/0/items/top?q={quote(title)}&qmode=titleCreatorYear",
    )
    for item in items:
        if item.get("data", {}).get("title") == title:
            return item
    return None


def _children(base_url: str, item_key: str) -> list[dict[str, Any]]:
    """Return child items for a Zotero parent item."""

    children, _ = _get_json(base_url, f"/api/users/0/items/{item_key}/children")
    return children


def _seed_fixture(base_url: str) -> tuple[str, str]:
    """Create or reuse a paper with an indexed PDF and a generic web record."""

    parent = _find_top_item(base_url, FIXTURE_TITLE)
    attachment = None
    if parent:
        attachment = next(
            (
                child
                for child in _children(base_url, parent["data"]["key"])
                if child.get("data", {}).get("contentType") == "application/pdf"
            ),
            None,
        )

    if not parent or not attachment:
        session_id = f"know-zotero-poc-{int(time.time())}"
        parent_connector_id = f"KNOWPOC{int(time.time())}"
        status = _post_json(
            base_url,
            "/connector/saveItems",
            {
                "sessionID": session_id,
                "uri": FIXTURE_URL,
                "items": [
                    {
                        "id": parent_connector_id,
                        "itemType": "journalArticle",
                        "title": FIXTURE_TITLE,
                        "creators": [
                            {
                                "firstName": "Michael D.",
                                "lastName": "Skarlinski",
                                "creatorType": "author",
                            },
                            {
                                "firstName": "Samuel G.",
                                "lastName": "Rodriques",
                                "creatorType": "author",
                            },
                        ],
                        "abstractNote": (
                            "A deterministic proof-of-concept record about agentic retrieval, "
                            "scientific synthesis, and citation-grounded question answering."
                        ),
                        "date": "2024",
                        "url": FIXTURE_URL,
                        "DOI": FIXTURE_DOI,
                        "tags": [FIXTURE_TAG, "arxiv", "agentic-rag"],
                    }
                ],
            },
        )
        if status != 201:
            raise PocFailure(f"Connector item seed returned HTTP {status}")

        parent = _wait_for_item(base_url, FIXTURE_TITLE)
        attachment_status = _post_attachment(
            base_url,
            session_id=session_id,
            parent_connector_id=parent_connector_id,
            content=_download_fixture_pdf(),
        )
        if attachment_status != 201:
            raise PocFailure(f"Connector attachment seed returned HTTP {attachment_status}")
        attachment = _wait_for_pdf_child(base_url, parent["data"]["key"])

    if not _find_top_item(base_url, FIXTURE_WEB_TITLE):
        web_status = _post_json(
            base_url,
            "/connector/saveItems",
            {
                "sessionID": f"know-zotero-web-{int(time.time())}",
                "uri": "https://example.com/knowledge-poc",
                "items": [
                    {
                        "id": f"KNOWWEB{int(time.time())}",
                        "itemType": "webpage",
                        "title": FIXTURE_WEB_TITLE,
                        "url": "https://example.com/knowledge-poc",
                        "abstractNote": "A generic webpage record; it is not a recursive site crawl.",
                        "tags": [FIXTURE_TAG, "website"],
                    }
                ],
            },
        )
        if web_status != 201:
            raise PocFailure(f"Connector webpage seed returned HTTP {web_status}")

    parent_key = parent["data"]["key"]
    attachment_key = attachment["data"]["key"]
    _wait_for_fulltext(base_url, attachment_key)
    return parent_key, attachment_key


def _wait_for_item(base_url: str, title: str, timeout: int = 30) -> dict[str, Any]:
    """Wait for a newly created top-level item."""

    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        item = _find_top_item(base_url, title)
        if item:
            return item
        time.sleep(1)
    raise PocFailure(f"Timed out waiting for Zotero item: {title}")


def _wait_for_pdf_child(base_url: str, parent_key: str, timeout: int = 30) -> dict[str, Any]:
    """Wait for a newly created PDF attachment."""

    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        for child in _children(base_url, parent_key):
            if child.get("data", {}).get("contentType") == "application/pdf":
                return child
        time.sleep(1)
    raise PocFailure("Timed out waiting for the Zotero PDF attachment")


def _wait_for_fulltext(base_url: str, attachment_key: str, timeout: int = 90) -> dict[str, Any]:
    """Wait until Zotero has indexed the fixture attachment."""

    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            fulltext, _ = _get_json(base_url, f"/api/users/0/items/{attachment_key}/fulltext")
        except PocFailure:
            time.sleep(2)
            continue
        if FIXTURE_FULLTEXT_TERM.lower() in fulltext.get("content", "").lower():
            return fulltext
        time.sleep(2)
    raise PocFailure("Timed out waiting for Zotero full-text indexing")


def run_cli(args: Sequence[str], *, force_utf8: bool = True, timeout: int = 60) -> CommandResult:
    """Run ``zotero-cli`` with a local-library-safe environment."""

    executable = shutil.which("zotero-cli")
    if not executable:
        raise PocFailure("zotero-cli is not installed")
    env = os.environ.copy()
    env.update({"ZOTERO_LOCAL": "true", "NO_PROXY": "localhost,127.0.0.1"})
    if force_utf8:
        env.update({"PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"})
    else:
        env.pop("PYTHONUTF8", None)
        env.pop("PYTHONIOENCODING", None)
    completed = subprocess.run(
        [executable, *args],
        capture_output=True,
        text=True,
        encoding="utf-8" if force_utf8 else None,
        errors="replace" if force_utf8 else None,
        env=env,
        timeout=timeout,
        check=False,
    )
    return CommandResult(
        args=["zotero-cli", *args],
        returncode=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
    )


def zotero_mcp_version() -> str:
    """Return the installed Zotero MCP package version."""

    executable = shutil.which("zotero-mcp")
    if not executable:
        raise PocFailure("zotero-mcp is not installed")
    completed = subprocess.run(
        [executable, "version"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=30,
        check=False,
    )
    output = completed.stdout or completed.stderr
    if completed.returncode or not output.strip():
        raise PocFailure("Could not determine the zotero-mcp version")
    return _compact(output)


def _compact(text: str, limit: int = 400) -> str:
    """Return compact evidence suitable for a JSON report."""

    compacted = " ".join(text.split())
    return compacted if len(compacted) <= limit else compacted[: limit - 1] + "…"


def _classify_fulltext_discovery(
    output: str,
    *,
    parent_key: str,
    attachment_key: str,
) -> str:
    """Classify exact full-text discovery separately from semantic fallback."""

    found = parent_key in output or attachment_key in output
    semantic_fallback = (
        "returned no results" in output.lower()
        and "semantically related" in output.lower()
    )
    if semantic_fallback:
        return "partial" if found else "gap"
    return "covered" if found else "gap"


def _cache_path(base_url: str, attachment_key: str) -> Path:
    """Resolve the managed Zotero full-text cache for a local attachment."""

    file_url = _get_text(base_url, f"/api/users/0/items/{attachment_key}/file/view/url")
    parsed = urlparse(file_url.strip())
    path_text = unquote(parsed.path)
    if os.name == "nt" and re.match(r"^/[A-Za-z]:", path_text):
        path_text = path_text[1:]
    return Path(path_text).parent / ".zotero-ft-cache"


def run_probes(base_url: str, parent_key: str, attachment_key: str) -> list[Probe]:
    """Execute the live capability probes."""

    probes: list[Probe] = []

    title_search = run_cli(["search", "superhuman synthesis"])
    probes.append(
        Probe(
            "title_metadata_search",
            "covered" if parent_key in title_search.stdout else "failed",
            _compact(title_search.stdout or title_search.stderr),
            required=True,
        )
    )

    metadata = run_cli(["get", "metadata", parent_key])
    probes.append(
        Probe(
            "structured_metadata",
            "covered" if FIXTURE_DOI in metadata.stdout else "failed",
            _compact(metadata.stdout),
            required=True,
        )
    )

    bibtex = run_cli(["get", "bibtex", parent_key])
    probes.append(
        Probe(
            "bibtex_export",
            "covered" if "@article" in bibtex.stdout else "failed",
            _compact(bibtex.stdout),
            required=True,
        )
    )

    children = run_cli(["get", "children", parent_key])
    probes.append(
        Probe(
            "attachment_discovery",
            "covered" if attachment_key in children.stdout else "failed",
            _compact(children.stdout),
            required=True,
        )
    )

    fulltext = run_cli(["get", "fulltext", parent_key], timeout=120)
    probes.append(
        Probe(
            "parent_pdf_fulltext",
            "covered" if FIXTURE_FULLTEXT_TERM.lower() in fulltext.stdout.lower() else "failed",
            f"characters={len(fulltext.stdout)}; term={FIXTURE_FULLTEXT_TERM!r}",
            required=True,
        )
    )

    rg_executable = shutil.which("rg")
    if rg_executable:
        grep = subprocess.run(
            [rg_executable, "-n", "-i", FIXTURE_FULLTEXT_TERM],
            input=fulltext.stdout,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        grep_status = "covered" if grep.returncode == 0 else "failed"
        grep_evidence = _compact(grep.stdout)
    else:
        grep_status = "failed"
        grep_evidence = "rg is not installed"
    probes.append(Probe("fulltext_pipe_to_rg", grep_status, grep_evidence, required=True))

    cache_path = _cache_path(base_url, attachment_key)
    if rg_executable and cache_path.exists():
        direct_grep = subprocess.run(
            [rg_executable, "-n", "-i", FIXTURE_FULLTEXT_TERM, str(cache_path)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        direct_status = "covered" if direct_grep.returncode == 0 else "failed"
        direct_evidence = f"storage/{attachment_key}/.zotero-ft-cache: {_compact(direct_grep.stdout)}"
    else:
        direct_status = "failed"
        direct_evidence = "Zotero full-text cache was not found"
    probes.append(Probe("direct_cache_rg", direct_status, direct_evidence, required=True))

    cli_fulltext_search = run_cli(
        ["search", "--qmode", "everything", FIXTURE_FULLTEXT_TERM]
    )
    api_matches, _ = _get_json(
        base_url,
        f"/api/users/0/items?q={quote(FIXTURE_FULLTEXT_TERM)}&qmode=everything",
    )
    api_keys = [item.get("data", {}).get("key") for item in api_matches]
    discovery_status = _classify_fulltext_discovery(
        cli_fulltext_search.stdout,
        parent_key=parent_key,
        attachment_key=attachment_key,
    )
    probes.append(
        Probe(
            "corpus_fulltext_discovery",
            discovery_status,
            (
                f"CLI: {_compact(cli_fulltext_search.stdout)}; "
                f"local API matching keys: {api_keys}"
            ),
        )
    )

    semantic = run_cli(["search", "--mode", "semantic", "agentic scientific synthesis"])
    semantic_output = f"{semantic.stdout}\n{semantic.stderr}"
    probes.append(
        Probe(
            "semantic_search",
            "covered" if parent_key in semantic.stdout else "optional_dependency",
            _compact(semantic_output),
        )
    )

    native_encoding = run_cli(["get", "fulltext", attachment_key], force_utf8=False, timeout=120)
    native_output = f"{native_encoding.stdout}\n{native_encoding.stderr}"
    encoding_failed = "charmap" in native_output.lower() or "codec can't encode" in native_output.lower()
    probes.append(
        Probe(
            "windows_default_encoding",
            "gap" if encoding_failed else "covered",
            (
                "Default Windows encoding fails; set PYTHONUTF8=1 and "
                "PYTHONIOENCODING=utf-8. " + _compact(native_output)
                if encoding_failed
                else f"Default encoding returned {len(native_encoding.stdout)} characters"
            ),
        )
    )

    tags = run_cli(["get", "tags"])
    probes.append(
        Probe(
            "tags",
            "covered" if FIXTURE_TAG in tags.stdout else "failed",
            _compact(tags.stdout),
            required=True,
        )
    )

    return probes


def capability_matrix(semantic_status: str) -> list[dict[str, str]]:
    """Return the comparison against the current ``know`` contract."""

    return [
        {"capability": "Bibliographic metadata and BibTeX", "status": "covered"},
        {"capability": "PDF storage and indexed full text", "status": "covered"},
        {"capability": "Tags and recent items", "status": "covered"},
        {
            "capability": "Notes and annotations",
            "status": "partial: CLI surface present; not live verified",
        },
        {"capability": "Agent access through CLI and MCP", "status": "covered"},
        {"capability": "Literal rg over one retrieved item", "status": "covered"},
        {"capability": "Collections", "status": "partial: local reads; writes need Web API credentials"},
        {"capability": "arXiv acquisition", "status": "partial: import, not declarative refresh"},
        {
            "capability": "Exact corpus-wide PDF keyword discovery",
            "status": "gap in CLI; semantic fallback, API, or cache workaround",
        },
        {"capability": "Semantic retrieval", "status": semantic_status},
        {"capability": "Recursive website crawling and CDP capture", "status": "gap"},
        {"capability": "Video transcription", "status": "gap"},
        {"capability": "Git repository and branch synchronization", "status": "gap"},
        {"capability": "Confluence, Jira, and Aha synchronization", "status": "gap"},
        {"capability": "Google release-feed normalization", "status": "gap"},
        {"capability": "Declarative source manifests and scheduled refresh", "status": "gap"},
        {"capability": "Markdown/OKF library export and zip import", "status": "gap"},
        {"capability": "Television terminal browsing formats", "status": "gap"},
        {"capability": "Semantic OKF RDF, SHACL, and SPARQL", "status": "gap"},
        {"capability": "Lossless Confluence Storage XML round trip", "status": "gap"},
    ]


def run(base_url: str, *, seed: bool) -> dict[str, Any]:
    """Run the complete POC and return its structured report."""

    _, headers, body = _request(base_url, "/api/")
    if b"Nothing to see here" not in body:
        raise PocFailure("Unexpected response from the Zotero local API")

    if seed:
        parent_key, attachment_key = _seed_fixture(base_url)
    else:
        parent = _find_top_item(base_url, FIXTURE_TITLE)
        if not parent:
            raise PocFailure("Fixture is absent; rerun with --seed")
        parent_key = parent["data"]["key"]
        attachment = next(
            (
                child
                for child in _children(base_url, parent_key)
                if child.get("data", {}).get("contentType") == "application/pdf"
            ),
            None,
        )
        if not attachment:
            raise PocFailure("Fixture PDF is absent; rerun with --seed")
        attachment_key = attachment["data"]["key"]
        _wait_for_fulltext(base_url, attachment_key)

    probes = run_probes(base_url, parent_key, attachment_key)
    required_failures = [probe.name for probe in probes if probe.required and probe.status != "covered"]
    semantic_status = next(probe.status for probe in probes if probe.name == "semantic_search")
    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "environment": {
            "platform": sys.platform,
            "zotero_version": headers.get("X-Zotero-Version"),
            "api_version": headers.get("Zotero-API-Version"),
            "schema_version": headers.get("Zotero-Schema-Version"),
            "zotero_mcp": zotero_mcp_version(),
        },
        "fixture": {
            "parent_key": parent_key,
            "attachment_key": attachment_key,
            "title": FIXTURE_TITLE,
            "url": FIXTURE_URL,
        },
        "probes": [asdict(probe) for probe in probes],
        "capability_matrix": capability_matrix(semantic_status),
        "required_failures": required_failures,
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument(
        "--seed",
        action="store_true",
        help="Create the isolated POC fixtures through Zotero Connector APIs",
    )
    parser.add_argument("--output", type=Path, help="Write the JSON report to this path")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entry point."""

    args = parse_args(argv)
    try:
        report = run(args.base_url, seed=args.seed)
    except PocFailure as exc:
        print(f"POC failed: {exc}", file=sys.stderr)
        return 2

    rendered = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 1 if report["required_failures"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
