from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from pathlib import Path
from urllib.parse import urlparse

from .browse_commands import (
    cmd_browse_aha,
    cmd_browse_arxiv,
    cmd_browse_confluence,
    cmd_browse_confluence_pages,
    cmd_browse_confluence_spaces,
    cmd_browse_follow,
    cmd_browse_follow_launch,
    cmd_browse_follow_open,
    cmd_browse_github,
    cmd_browse_github_activity,
    cmd_browse_jira,
    cmd_browse_jira_projects,
    cmd_browse_local,
    cmd_browse_releases,
    cmd_browse_sites,
    cmd_browse_videos,
)
from .browse_extended import (
    cmd_browse_by_key,
    cmd_browse_by_type,
    cmd_browse_commands,
    cmd_browse_crossref,
    cmd_browse_files,
    cmd_browse_key_sources,
    cmd_browse_papers,
    cmd_browse_recent,
    cmd_browse_repo_files,
    cmd_browse_repos,
    cmd_browse_source_files,
    cmd_browse_stale,
    cmd_browse_stats,
    cmd_browse_timeline,
    cmd_browse_unsynced,
)
from .commands import (
    cmd_add_aha_workspace,
    cmd_add_arxiv,
    cmd_add_confluence,
    cmd_add_github_repo,
    cmd_add_google_releases,
    cmd_add_jira_project,
    cmd_add_key,
    cmd_add_site,
    cmd_add_television,
    cmd_add_video,
    cmd_delete_source,
    cmd_export,
    cmd_import,
    cmd_init,
    cmd_key_list,
    cmd_key_set,
    cmd_list_collection_sources,
    cmd_list_keys,
    cmd_search_arxiv,
    cmd_search_brave,
    cmd_search_confluence,
    cmd_search_jira,
    cmd_sync,
)
from .television import TV_FORMAT_CHOICES


def load_dotenv(dotenv_path: Path | None = None) -> None:
    """Load environment variables from a ``.env`` file if present."""
    path = (dotenv_path or Path.cwd() / ".env").resolve()
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        name = name.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]
        if name not in os.environ or os.environ[name] == "":
            os.environ[name] = value


def build_parser() -> argparse.ArgumentParser:
    """Build the top-level argument parser for the ``know`` CLI."""

    parser = argparse.ArgumentParser(
        prog="know",
        description="Manage a local knowledge base in ~/.knowledge.",
    )
    parser.add_argument("--store", type=Path, default=None, help="Override the knowledge store path.")
    parser.add_argument("--json", action="store_true", help="Emit command output as JSON.")
    parser.add_argument("--verbose", action="store_true", help="Print progress messages.")
    parser.add_argument("--quiet", action="store_true", help="Suppress non-error output.")

    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add", help="Create keys and attach source definitions.")
    add_subparsers = add_parser.add_subparsers(dest="add_command", required=True)

    add_key_parser = add_subparsers.add_parser("key", help="Create a knowledge key.")
    add_key_parser.add_argument("name", help="Knowledge key name.")
    add_key_parser.set_defaults(handler=cmd_add_key)

    add_confluence_parser = add_subparsers.add_parser("confluence", help="Attach a Confluence space.")
    add_confluence_parser.add_argument("--space", help="Confluence space key.")
    add_confluence_parser.add_argument("--key", required=True, help="Knowledge key name.")
    add_confluence_parser.add_argument("--base-url", help="Confluence base URL.")
    add_confluence_parser.add_argument("--username", help="Username or credential key reference.")
    add_confluence_parser.add_argument("--token", help="Token or credential key reference.")
    add_confluence_parser.add_argument("--cql", help="Persist a custom Confluence CQL filter for sync.")
    add_confluence_parser.add_argument("--limit", type=int, help="Page sync limit.")
    add_confluence_parser.set_defaults(handler=cmd_add_confluence)

    add_arxiv_parser = add_subparsers.add_parser("arxiv", help="Attach an arXiv paper URL.")
    add_arxiv_parser.add_argument("url", help="arXiv URL.")
    add_arxiv_parser.add_argument("--key", required=True, help="Knowledge key name.")
    add_arxiv_parser.set_defaults(handler=cmd_add_arxiv)

    add_site_parser = add_subparsers.add_parser("site", help="Attach a website URL.")
    add_site_parser.add_argument("url", help="Website URL.")
    add_site_parser.add_argument("--key", required=True, help="Knowledge key name.")
    add_site_parser.add_argument("--max-depth", type=int, default=1, help="Optional crawl depth.")
    add_site_parser.add_argument("--max-pages", type=int, default=1, help="Optional page limit.")
    add_site_parser.set_defaults(handler=cmd_add_site)

    add_video_parser = add_subparsers.add_parser("video", help="Attach a video URL or path.")
    add_video_parser.add_argument("url", help="Video URL or local path.")
    add_video_parser.add_argument("--key", required=True, help="Knowledge key name.")
    add_video_parser.add_argument("--language", action="append", help="Preferred transcript language. Repeatable.")
    add_video_parser.set_defaults(handler=cmd_add_video)

    add_television_parser = add_subparsers.add_parser(
        "tv",
        aliases=["television"],
        help="Attach a Television channel definition.",
    )
    add_television_parser.add_argument(
        "name",
        nargs="?",
        help="Television channel name. Omit it to install the bundled cable files.",
    )
    add_television_parser.add_argument("--key", help="Knowledge key name.")
    add_television_parser.add_argument("--description", help="Channel description.")
    add_television_parser.add_argument("--source-command", help="Television source command.")
    add_television_parser.add_argument("--source-display", help="Optional Television source display template.")
    add_television_parser.add_argument("--preview-command", help="Optional Television preview command.")
    add_television_parser.add_argument("--action-command", help="Optional command for the default open action.")
    add_television_parser.set_defaults(handler=cmd_add_television)

    add_github_parser = add_subparsers.add_parser("github-repo", help="Attach a GitHub repository.")
    add_github_parser.add_argument("repo_url", help="Git repository URL.")
    add_github_parser.add_argument("--key", required=True, help="Knowledge key name.")
    add_github_parser.add_argument("--branch", action="append", help="Branch to include. Repeatable.")
    add_github_parser.set_defaults(handler=cmd_add_github_repo)

    add_google_releases_parser = add_subparsers.add_parser(
        "google-releases",
        help="Attach a Google Cloud release notes Atom feed.",
    )
    add_google_releases_parser.add_argument("url", help="Google Cloud release notes feed URL.")
    add_google_releases_parser.add_argument("--key", required=True, help="Knowledge key name.")
    add_google_releases_parser.set_defaults(handler=cmd_add_google_releases)

    add_jira_parser = add_subparsers.add_parser("jira-project", help="Attach a Jira project.")
    add_jira_parser.add_argument("project", help="Jira project key.")
    add_jira_parser.add_argument("--key", required=True, help="Knowledge key name.")
    add_jira_parser.add_argument("--base-url", help="Jira base URL.")
    add_jira_parser.add_argument("--username", help="Username or credential key reference.")
    add_jira_parser.add_argument("--token", help="Token or credential key reference.")
    add_jira_parser.add_argument("--jql", help="Override default JQL.")
    add_jira_parser.add_argument("--field", action="append", help="Field to request. Repeatable.")
    add_jira_parser.add_argument("--limit", type=int, help="Issue sync limit.")
    add_jira_parser.set_defaults(handler=cmd_add_jira_project)

    add_aha_parser = add_subparsers.add_parser("aha", help="Attach an Aha workspace.")
    add_aha_parser.add_argument("workspace", help="Aha workspace or product identifier.")
    add_aha_parser.add_argument("--key", required=True, help="Knowledge key name.")
    add_aha_parser.add_argument("--base-url", help="Aha base URL.")
    add_aha_parser.add_argument("--token", help="Token or credential key reference.")
    add_aha_parser.add_argument("--limit", type=int, help="Feature sync limit.")
    add_aha_parser.set_defaults(handler=cmd_add_aha_workspace)

    list_parser = subparsers.add_parser("list", help="List keys, credentials, or attached sources.")
    list_subparsers = list_parser.add_subparsers(dest="list_command", required=True)

    list_keys_parser = list_subparsers.add_parser("keys", help="List knowledge keys.")
    list_keys_parser.add_argument("--format", choices=TV_FORMAT_CHOICES, default="json", help="Output format.")
    list_keys_parser.add_argument("--entry", help="Entry to preview when using --format television-preview.")
    list_keys_parser.set_defaults(handler=cmd_list_keys)

    list_credentials_parser = list_subparsers.add_parser("credentials", help="List stored credential names.")
    list_credentials_parser.set_defaults(handler=cmd_key_list)

    list_sources_parser = list_subparsers.add_parser("sources", help="List sources attached to keys.")
    list_sources_parser.add_argument("--key", help="Restrict to a single knowledge key.")
    list_sources_parser.add_argument("--type", help="Restrict to a single source type.")
    list_sources_parser.add_argument("--format", choices=TV_FORMAT_CHOICES, default="json", help="Output format.")
    list_sources_parser.add_argument("--entry", help="Entry to preview when using --format television-preview.")
    list_sources_parser.set_defaults(handler=cmd_list_collection_sources)

    search_parser = subparsers.add_parser("search", help="Search configured source definitions.")
    search_subparsers = search_parser.add_subparsers(dest="search_command", required=True)

    search_confluence_parser = search_subparsers.add_parser("confluence", help="Search Confluence content.")
    search_confluence_parser.add_argument("query", nargs="?", help="Free-text query string.")
    search_confluence_parser.add_argument("--knowledge-key", help="Restrict to one knowledge key.")
    search_confluence_parser.add_argument("--space", help="Restrict the search to one Confluence space.")
    search_confluence_parser.add_argument("--cql", help="Override the generated CQL query.")
    search_confluence_parser.add_argument("--type", help="Restrict by Confluence content type.")
    search_confluence_parser.add_argument("--label", action="append", help="Restrict by label. Repeatable.")
    search_confluence_parser.add_argument("--title-contains", help="Filter by title text.")
    search_confluence_parser.add_argument("--text-contains", help="Filter by body text.")
    search_confluence_parser.add_argument("--created-after", help="Restrict to content created after this ISO-8601 timestamp.")
    search_confluence_parser.add_argument("--created-before", help="Restrict to content created before this ISO-8601 timestamp.")
    search_confluence_parser.add_argument("--updated-after", help="Restrict to content updated after this ISO-8601 timestamp.")
    search_confluence_parser.add_argument("--updated-before", help="Restrict to content updated before this ISO-8601 timestamp.")
    search_confluence_parser.add_argument("--limit", type=int, default=25, help="Maximum number of results per source.")
    search_confluence_parser.add_argument("--cursor", help="Cursor token from a previous response.")
    search_confluence_parser.add_argument("--format", choices=TV_FORMAT_CHOICES, default="json", help="Output format.")
    search_confluence_parser.add_argument("--entry", help="Entry to preview when using --format television-preview.")
    search_confluence_parser.set_defaults(handler=cmd_search_confluence)

    search_jira_parser = search_subparsers.add_parser("jira", help="Search Jira issues through REST API v3.")
    search_jira_parser.add_argument("query", nargs="?", help="Free-text query used to build JQL.")
    search_jira_parser.add_argument("--knowledge-key", help="Restrict to one knowledge key.")
    search_jira_parser.add_argument("--project", help="Restrict to one Jira project.")
    search_jira_parser.add_argument("--jql", help="Explicit JQL to execute.")
    search_jira_parser.add_argument("--status", action="append", help="Restrict by Jira status. Repeatable.")
    search_jira_parser.add_argument("--issue-type", action="append", help="Restrict by issue type. Repeatable.")
    search_jira_parser.add_argument("--assignee", help="Restrict by assignee.")
    search_jira_parser.add_argument("--reporter", help="Restrict by reporter.")
    search_jira_parser.add_argument("--created-after", help="Restrict to issues created after this ISO-8601 timestamp.")
    search_jira_parser.add_argument("--created-before", help="Restrict to issues created before this ISO-8601 timestamp.")
    search_jira_parser.add_argument("--updated-after", help="Restrict to issues updated after this ISO-8601 timestamp.")
    search_jira_parser.add_argument("--updated-before", help="Restrict to issues updated before this ISO-8601 timestamp.")
    search_jira_parser.add_argument("--order-by", action="append", help="JQL ORDER BY expression fragment. Repeatable.")
    search_jira_parser.add_argument("--field", action="append", help="Field to request. Repeatable.")
    search_jira_parser.add_argument("--property", action="append", help="Entity property to request. Repeatable.")
    search_jira_parser.add_argument("--expand", action="append", help="Expand value to request. Repeatable.")
    search_jira_parser.add_argument("--fields-by-keys", action="store_true", help="Ask Jira to interpret fields by keys.")
    search_jira_parser.add_argument("--limit", type=int, default=25, help="Maximum number of results per source.")
    search_jira_parser.add_argument("--next-page-token", help="Enhanced-search pagination token.")
    search_jira_parser.add_argument("--format", choices=TV_FORMAT_CHOICES, default="json", help="Output format.")
    search_jira_parser.add_argument("--entry", help="Entry to preview when using --format television-preview.")
    search_jira_parser.set_defaults(handler=cmd_search_jira)

    search_arxiv_parser = search_subparsers.add_parser("arxiv", help="Search arXiv via the public API.")
    search_arxiv_parser.add_argument("query", help="arXiv search_query expression or plain text.")
    search_arxiv_parser.add_argument(
        "--format",
        choices=("json", "television", "television-preview"),
        default="json",
        help="Output format. Use television variants when wiring the command into tv.",
    )
    search_arxiv_parser.add_argument(
        "--entry",
        help="Entry title to preview when using --format television-preview.",
    )
    search_arxiv_parser.add_argument("--start", type=int, default=0, help="Starting result offset.")
    search_arxiv_parser.add_argument("--max-results", type=int, default=10, help="Maximum number of results.")
    search_arxiv_parser.add_argument(
        "--sort-by",
        choices=("relevance", "lastUpdatedDate", "submittedDate"),
        default="relevance",
        help="Sort field supported by the arXiv API.",
    )
    search_arxiv_parser.add_argument(
        "--sort-order",
        choices=("ascending", "descending"),
        default="descending",
        help="Sort direction supported by the arXiv API.",
    )
    search_arxiv_parser.set_defaults(handler=cmd_search_arxiv)

    search_brave_parser = search_subparsers.add_parser("brave", help="Search the web through the Brave Search API.")
    search_brave_parser.add_argument("query", help="Text to search on the web.")
    search_brave_parser.add_argument(
        "--format",
        choices=("json", "television", "television-preview"),
        default="json",
        help="Output format. Use television variants when wiring the command into tv.",
    )
    search_brave_parser.add_argument(
        "--entry",
        help="Entry title to preview when using --format television-preview.",
    )
    search_brave_parser.add_argument("--country", help="Country code for regional results, for example US.")
    search_brave_parser.add_argument("--search-lang", help="Language code for search results, for example en.")
    search_brave_parser.add_argument("--ui-lang", help="Preferred UI language in the response, for example en-US.")
    search_brave_parser.add_argument("--count", type=int, default=10, help="Maximum number of Brave results.")
    search_brave_parser.add_argument("--offset", type=int, default=0, help="Page offset to skip before returning results.")
    search_brave_parser.add_argument(
        "--safesearch",
        choices=("off", "moderate", "strict"),
        help="Adult-content filtering level.",
    )
    search_brave_parser.add_argument(
        "--spellcheck",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Enable Brave spell correction.",
    )
    search_brave_parser.add_argument(
        "--freshness",
        help="Freshness filter such as pd, pw, pm, py, or YYYY-MM-DDtoYYYY-MM-DD.",
    )
    search_brave_parser.add_argument(
        "--text-decorations",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Include Brave text decoration markers in snippets.",
    )
    search_brave_parser.add_argument(
        "--result-filter",
        action="append",
        choices=("discussions", "faq", "infobox", "news", "query", "summarizer", "videos", "web", "locations"),
        help="Result types to include. Repeatable.",
    )
    search_brave_parser.add_argument(
        "--units",
        choices=("imperial", "metric"),
        help="Measurement units for result formatting.",
    )
    search_brave_parser.add_argument(
        "--goggles",
        action="append",
        help="Goggle URL or inline definition. Repeatable.",
    )
    search_brave_parser.add_argument(
        "--extra-snippets",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Request additional alternate snippets.",
    )
    search_brave_parser.add_argument(
        "--summary",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Enable summary generation for summarizer results.",
    )
    search_brave_parser.add_argument(
        "--enable-rich-callback",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Enable Brave rich callback support.",
    )
    search_brave_parser.add_argument(
        "--include-fetch-metadata",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Include fetch metadata in the response.",
    )
    search_brave_parser.add_argument(
        "--operators",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Apply Brave search operators found in the query.",
    )
    search_brave_parser.add_argument("--loc-lat", type=float, help="Client latitude for local results.")
    search_brave_parser.add_argument("--loc-long", type=float, help="Client longitude for local results.")
    search_brave_parser.add_argument("--loc-timezone", help="Client IANA timezone for local results.")
    search_brave_parser.add_argument("--loc-city", help="Client city for local results.")
    search_brave_parser.add_argument("--loc-state", help="Client state or region code for local results.")
    search_brave_parser.add_argument("--loc-state-name", help="Client state or region name for local results.")
    search_brave_parser.add_argument("--loc-country", help="Client country code for local results.")
    search_brave_parser.add_argument("--loc-postal-code", help="Client postal code for local results.")
    search_brave_parser.add_argument("--api-version", help="Explicit Brave API version header.")
    search_brave_parser.add_argument(
        "--accept",
        choices=("application/json", "*/*"),
        help="Accept header to send to Brave.",
    )
    search_brave_parser.add_argument(
        "--cache-control",
        choices=("no-cache",),
        help="Cache-Control header for Brave requests.",
    )
    search_brave_parser.add_argument("--user-agent", help="User-Agent header for Brave requests.")
    search_brave_parser.set_defaults(handler=cmd_search_brave)

    sync_parser = subparsers.add_parser("sync", help="Synchronize one key or selected sources.")
    sync_parser.add_argument("--key", help="Restrict sync to a single knowledge key.")
    sync_subparsers = sync_parser.add_subparsers(dest="sync_command")
    sync_parser.set_defaults(handler=cmd_sync, source_type=None, match_value=None)

    sync_confluence_parser = sync_subparsers.add_parser("confluence", help="Sync a Confluence source.")
    sync_confluence_parser.add_argument("--space", required=True, help="Confluence space key.")
    sync_confluence_parser.add_argument("--key", required=True, help="Knowledge key name.")
    sync_confluence_parser.set_defaults(handler=cmd_sync, source_type="confluence", match_value=None)

    sync_arxiv_parser = sync_subparsers.add_parser("arxiv", help="Sync an arXiv source.")
    sync_arxiv_parser.add_argument("url", help="arXiv URL.")
    sync_arxiv_parser.add_argument("--key", required=True, help="Knowledge key name.")
    sync_arxiv_parser.set_defaults(handler=cmd_sync, source_type="arxiv", match_value=None)

    sync_site_parser = sync_subparsers.add_parser("site", help="Sync a website source.")
    sync_site_parser.add_argument("url", help="Website URL.")
    sync_site_parser.add_argument("--key", required=True, help="Knowledge key name.")
    sync_site_parser.set_defaults(handler=cmd_sync, source_type="site", match_value=None)

    sync_video_parser = sync_subparsers.add_parser("video", help="Sync a video source.")
    sync_video_parser.add_argument("url", help="Video URL or local path.")
    sync_video_parser.add_argument("--key", required=True, help="Knowledge key name.")
    sync_video_parser.set_defaults(handler=cmd_sync, source_type="video", match_value=None)

    sync_television_parser = sync_subparsers.add_parser("television", help="Sync a Television channel definition.")
    sync_television_parser.add_argument("name", help="Television channel name.")
    sync_television_parser.add_argument("--key", required=True, help="Knowledge key name.")
    sync_television_parser.set_defaults(handler=cmd_sync, source_type="television", match_value=None)

    sync_github_parser = sync_subparsers.add_parser("github-repo", help="Sync a GitHub repository source.")
    sync_github_parser.add_argument("repo_url", help="Git repository URL.")
    sync_github_parser.add_argument("--key", required=True, help="Knowledge key name.")
    sync_github_parser.add_argument("--branch", action="append", help="Optional branch filters.")
    sync_github_parser.set_defaults(handler=cmd_sync, source_type="github", match_value=None)

    sync_google_releases_parser = sync_subparsers.add_parser(
        "google-releases",
        help="Sync a Google Cloud release notes feed source.",
    )
    sync_google_releases_parser.add_argument("url", help="Google Cloud release notes feed URL.")
    sync_google_releases_parser.add_argument("--key", required=True, help="Knowledge key name.")
    sync_google_releases_parser.set_defaults(handler=cmd_sync, source_type="google_releases", match_value=None)

    sync_jira_parser = sync_subparsers.add_parser("jira-project", help="Sync a Jira project source.")
    sync_jira_parser.add_argument("project", help="Jira project key.")
    sync_jira_parser.add_argument("--key", required=True, help="Knowledge key name.")
    sync_jira_parser.set_defaults(handler=cmd_sync, source_type="jira", match_value=None)

    sync_aha_parser = sync_subparsers.add_parser("aha", help="Sync an Aha workspace source.")
    sync_aha_parser.add_argument("workspace", help="Aha workspace or product.")
    sync_aha_parser.add_argument("--key", required=True, help="Knowledge key name.")
    sync_aha_parser.set_defaults(handler=cmd_sync, source_type="aha", match_value=None)

    del_parser = subparsers.add_parser("del", help="Delete a registered source from a key.")
    del_parser.add_argument("--key", required=True, help="Knowledge key name.")
    del_parser.add_argument("source_id", help="Registered source id.")
    del_parser.set_defaults(handler=cmd_delete_source)

    init_parser = subparsers.add_parser("init", help="Initialize the knowledge store.")
    init_parser.set_defaults(handler=cmd_init)

    set_parser = subparsers.add_parser("set", help="Store mutable configuration values.")
    set_subparsers = set_parser.add_subparsers(dest="set_command", required=True)

    set_credential_parser = set_subparsers.add_parser("credential", help="Store a named credential.")
    set_credential_parser.add_argument("name", help="Credential name.")
    set_credential_parser.add_argument("value", help="Credential value.")
    set_credential_parser.set_defaults(handler=cmd_key_set)

    export_parser = subparsers.add_parser("export", help="Render markdown output and create a zip export.")
    export_parser.add_argument("--key", help="Restrict export to a single knowledge key.")
    export_parser.set_defaults(handler=cmd_export)

    import_parser = subparsers.add_parser("import", help="Import a previously exported zip archive.")
    import_parser.add_argument("archive", help="Zip archive path.")
    import_parser.set_defaults(handler=cmd_import)

    # ── Browse subcommands ───────────────────────────────────────────────
    browse_parser = subparsers.add_parser("browse", help="Browse knowledge with sync-status indicators.")
    browse_subparsers = browse_parser.add_subparsers(dest="browse_command", required=True)

    browse_jira_parser = browse_subparsers.add_parser("jira", help="Browse Jira issues with sync status.")
    browse_jira_parser.add_argument("--key", help="Restrict to a knowledge key.")
    browse_jira_parser.add_argument("--format", choices=TV_FORMAT_CHOICES, default="json", help="Output format.")
    browse_jira_parser.add_argument("--entry", help="Entry to preview.")
    browse_jira_parser.set_defaults(handler=cmd_browse_jira)

    browse_jprojects_parser = browse_subparsers.add_parser("jira-projects", help="List Jira projects.")
    browse_jprojects_parser.add_argument("--format", choices=TV_FORMAT_CHOICES, default="json", help="Output format.")
    browse_jprojects_parser.add_argument("--entry", help="Entry to preview.")
    browse_jprojects_parser.set_defaults(handler=cmd_browse_jira_projects)

    browse_confluence_parser = browse_subparsers.add_parser("confluence", help="Browse Confluence pages with sync status.")
    browse_confluence_parser.add_argument("--key", help="Restrict to a knowledge key.")
    browse_confluence_parser.add_argument("--format", choices=TV_FORMAT_CHOICES, default="json", help="Output format.")
    browse_confluence_parser.add_argument("--entry", help="Entry to preview.")
    browse_confluence_parser.set_defaults(handler=cmd_browse_confluence)

    browse_cspaces_parser = browse_subparsers.add_parser("confluence-spaces", help="List Confluence spaces.")
    browse_cspaces_parser.add_argument("--format", choices=TV_FORMAT_CHOICES, default="json", help="Output format.")
    browse_cspaces_parser.add_argument("--entry", help="Entry to preview.")
    browse_cspaces_parser.set_defaults(handler=cmd_browse_confluence_spaces)

    browse_cpages_parser = browse_subparsers.add_parser("confluence-pages", help="List Confluence pages as /path/title.")
    browse_cpages_parser.add_argument("--space", help="Confluence space key.")
    browse_cpages_parser.add_argument("--selected-row", help="Television row for drill-in from spaces channel.")
    browse_cpages_parser.add_argument("--format", choices=TV_FORMAT_CHOICES, default="json", help="Output format.")
    browse_cpages_parser.add_argument("--entry", help="Entry to preview.")
    browse_cpages_parser.set_defaults(handler=cmd_browse_confluence_pages)

    browse_github_parser = browse_subparsers.add_parser("github", help="Browse GitHub repos you've interacted with.")
    browse_github_parser.add_argument("--key", help="Restrict to a knowledge key.")
    browse_github_parser.add_argument("--format", choices=TV_FORMAT_CHOICES, default="json", help="Output format.")
    browse_github_parser.add_argument("--entry", help="Entry to preview.")
    browse_github_parser.set_defaults(handler=cmd_browse_github)

    browse_github_activity_parser = browse_subparsers.add_parser(
        "github-activity",
        help="Browse issues, PRs & discussions for a GitHub repo.",
    )
    browse_github_activity_parser.add_argument("repo", nargs="?", help="Repository in owner/repo format.")
    browse_github_activity_parser.add_argument(
        "--selected-row",
        help="Full Television row text to derive the repository from when drilling in from another channel.",
    )
    browse_github_activity_parser.add_argument("--format", choices=TV_FORMAT_CHOICES, default="json", help="Output format.")
    browse_github_activity_parser.add_argument("--entry", help="Entry to preview.")
    browse_github_activity_parser.set_defaults(handler=cmd_browse_github_activity)

    browse_follow_parser = browse_subparsers.add_parser(
        "follow",
        help="Open items from GitHub repos and Jira projects interacted with in the last 6 months.",
    )
    browse_follow_parser.add_argument("--format", choices=TV_FORMAT_CHOICES, default="json", help="Output format.")
    browse_follow_parser.add_argument("--entry", help="Entry to preview.")
    browse_follow_parser.set_defaults(handler=cmd_browse_follow)

    browse_follow_open_parser = browse_subparsers.add_parser(
        "follow-url",
        help="Print the web URL for a follow item.",
    )
    browse_follow_open_parser.add_argument("selected_row", help="Television row text.")
    browse_follow_open_parser.set_defaults(handler=cmd_browse_follow_open)

    browse_follow_launch_parser = browse_subparsers.add_parser(
        "follow-open",
        help="Open the web URL for a follow item in the default browser.",
    )
    browse_follow_launch_parser.add_argument("selected_row", help="Television row text.")
    browse_follow_launch_parser.set_defaults(handler=cmd_browse_follow_launch)

    browse_arxiv_parser = browse_subparsers.add_parser("arxiv", help="Browse arXiv papers with sync status.")
    browse_arxiv_parser.add_argument("--key", help="Restrict to a knowledge key.")
    browse_arxiv_parser.add_argument("--format", choices=TV_FORMAT_CHOICES, default="json", help="Output format.")
    browse_arxiv_parser.add_argument("--entry", help="Entry to preview.")
    browse_arxiv_parser.set_defaults(handler=cmd_browse_arxiv)

    browse_aha_parser = browse_subparsers.add_parser("aha", help="Browse Aha features with sync status.")
    browse_aha_parser.add_argument("--key", help="Restrict to a knowledge key.")
    browse_aha_parser.add_argument("--format", choices=TV_FORMAT_CHOICES, default="json", help="Output format.")
    browse_aha_parser.add_argument("--entry", help="Entry to preview.")
    browse_aha_parser.set_defaults(handler=cmd_browse_aha)

    browse_releases_parser = browse_subparsers.add_parser("releases", help="Browse Google release notes with sync status.")
    browse_releases_parser.add_argument("--key", help="Restrict to a knowledge key.")
    browse_releases_parser.add_argument("--format", choices=TV_FORMAT_CHOICES, default="json", help="Output format.")
    browse_releases_parser.add_argument("--entry", help="Entry to preview.")
    browse_releases_parser.set_defaults(handler=cmd_browse_releases)

    browse_videos_parser = browse_subparsers.add_parser("videos", help="Browse video sources with sync status.")
    browse_videos_parser.add_argument("--key", help="Restrict to a knowledge key.")
    browse_videos_parser.add_argument("--format", choices=TV_FORMAT_CHOICES, default="json", help="Output format.")
    browse_videos_parser.add_argument("--entry", help="Entry to preview.")
    browse_videos_parser.set_defaults(handler=cmd_browse_videos)

    browse_sites_parser = browse_subparsers.add_parser("sites", help="Browse crawled sites with sync status.")
    browse_sites_parser.add_argument("--key", help="Restrict to a knowledge key.")
    browse_sites_parser.add_argument("--format", choices=TV_FORMAT_CHOICES, default="json", help="Output format.")
    browse_sites_parser.add_argument("--entry", help="Entry to preview.")
    browse_sites_parser.set_defaults(handler=cmd_browse_sites)

    browse_local_parser = browse_subparsers.add_parser("local", help="Browse all locally downloaded knowledge.")
    browse_local_parser.add_argument("--key", help="Restrict to a knowledge key.")
    browse_local_parser.add_argument("--type", help="Restrict to a source type.")
    browse_local_parser.add_argument("--format", choices=TV_FORMAT_CHOICES, default="json", help="Output format.")
    browse_local_parser.add_argument("--entry", help="Entry to preview.")
    browse_local_parser.set_defaults(handler=cmd_browse_local)

    # ── Extended browse subcommands ──────────────────────────────────────
    browse_by_key_parser = browse_subparsers.add_parser("by-key", help="Keys overview with source counts. Enter drills in.")
    browse_by_key_parser.add_argument("--format", choices=TV_FORMAT_CHOICES, default="json", help="Output format.")
    browse_by_key_parser.add_argument("--entry", help="Entry to preview.")
    browse_by_key_parser.set_defaults(handler=cmd_browse_by_key)

    browse_by_type_parser = browse_subparsers.add_parser("by-type", help="Source types overview. Enter drills into type.")
    browse_by_type_parser.add_argument("--format", choices=TV_FORMAT_CHOICES, default="json", help="Output format.")
    browse_by_type_parser.add_argument("--entry", help="Entry to preview.")
    browse_by_type_parser.set_defaults(handler=cmd_browse_by_type)

    browse_papers_parser = browse_subparsers.add_parser("papers", help="Unified arXiv paper browser across all keys.")
    browse_papers_parser.add_argument("--format", choices=TV_FORMAT_CHOICES, default="json", help="Output format.")
    browse_papers_parser.add_argument("--entry", help="Entry to preview.")
    browse_papers_parser.set_defaults(handler=cmd_browse_papers)

    browse_repos_parser = browse_subparsers.add_parser("repos", help="All synced GitHub repos across all keys.")
    browse_repos_parser.add_argument("--format", choices=TV_FORMAT_CHOICES, default="json", help="Output format.")
    browse_repos_parser.add_argument("--entry", help="Entry to preview.")
    browse_repos_parser.set_defaults(handler=cmd_browse_repos)

    browse_repo_files_parser = browse_subparsers.add_parser("repo-files", help="Browse files inside a synced repo.")
    browse_repo_files_parser.add_argument("--repo", help="Filter by repo name.")
    browse_repo_files_parser.add_argument("--format", choices=TV_FORMAT_CHOICES, default="json", help="Output format.")
    browse_repo_files_parser.add_argument("--entry", help="Entry to preview.")
    browse_repo_files_parser.set_defaults(handler=cmd_browse_repo_files)

    browse_files_parser = browse_subparsers.add_parser("files", help="Full-text searchable file browser.")
    browse_files_parser.add_argument("--query", help="Full-text search query.")
    browse_files_parser.add_argument("--key", help="Restrict to a knowledge key.")
    browse_files_parser.add_argument("--format", choices=TV_FORMAT_CHOICES, default="json", help="Output format.")
    browse_files_parser.add_argument("--entry", help="Entry to preview.")
    browse_files_parser.set_defaults(handler=cmd_browse_files)

    browse_recent_parser = browse_subparsers.add_parser("recent", help="Recently synced sources.")
    browse_recent_parser.add_argument("--limit", type=int, default=50, help="Max items.")
    browse_recent_parser.add_argument("--format", choices=TV_FORMAT_CHOICES, default="json", help="Output format.")
    browse_recent_parser.add_argument("--entry", help="Entry to preview.")
    browse_recent_parser.set_defaults(handler=cmd_browse_recent)

    browse_stale_parser = browse_subparsers.add_parser("stale", help="Sources not synced recently.")
    browse_stale_parser.add_argument("--days", type=int, default=7, help="Consider stale after N days.")
    browse_stale_parser.add_argument("--format", choices=TV_FORMAT_CHOICES, default="json", help="Output format.")
    browse_stale_parser.add_argument("--entry", help="Entry to preview.")
    browse_stale_parser.set_defaults(handler=cmd_browse_stale)

    browse_unsynced_parser = browse_subparsers.add_parser("unsynced", help="Sources never synced.")
    browse_unsynced_parser.add_argument("--format", choices=TV_FORMAT_CHOICES, default="json", help="Output format.")
    browse_unsynced_parser.add_argument("--entry", help="Entry to preview.")
    browse_unsynced_parser.set_defaults(handler=cmd_browse_unsynced)

    browse_timeline_parser = browse_subparsers.add_parser("timeline", help="Chronological source timeline.")
    browse_timeline_parser.add_argument("--format", choices=TV_FORMAT_CHOICES, default="json", help="Output format.")
    browse_timeline_parser.add_argument("--entry", help="Entry to preview.")
    browse_timeline_parser.set_defaults(handler=cmd_browse_timeline)

    browse_commands_parser = browse_subparsers.add_parser("commands", help="All available sync/delete/export commands.")
    browse_commands_parser.add_argument("--format", choices=TV_FORMAT_CHOICES, default="json", help="Output format.")
    browse_commands_parser.add_argument("--entry", help="Entry to preview.")
    browse_commands_parser.set_defaults(handler=cmd_browse_commands)

    browse_stats_parser = browse_subparsers.add_parser("stats", help="Knowledge base statistics overview.")
    browse_stats_parser.add_argument("--format", choices=TV_FORMAT_CHOICES, default="json", help="Output format.")
    browse_stats_parser.add_argument("--entry", help="Entry to preview.")
    browse_stats_parser.set_defaults(handler=cmd_browse_stats)

    browse_crossref_parser = browse_subparsers.add_parser("crossref", help="Sources shared across multiple keys.")
    browse_crossref_parser.add_argument("--format", choices=TV_FORMAT_CHOICES, default="json", help="Output format.")
    browse_crossref_parser.add_argument("--entry", help="Entry to preview.")
    browse_crossref_parser.set_defaults(handler=cmd_browse_crossref)

    browse_key_sources_parser = browse_subparsers.add_parser("key-sources", help="Sources for a specific key (fork target).")
    browse_key_sources_parser.add_argument("--key", required=True, help="Knowledge key name.")
    browse_key_sources_parser.add_argument("--format", choices=TV_FORMAT_CHOICES, default="json", help="Output format.")
    browse_key_sources_parser.add_argument("--entry", help="Entry to preview.")
    browse_key_sources_parser.set_defaults(handler=cmd_browse_key_sources)

    browse_source_files_parser = browse_subparsers.add_parser("source-files", help="Files inside a specific source (fork target).")
    browse_source_files_parser.add_argument("--key", required=True, help="Knowledge key name.")
    browse_source_files_parser.add_argument("--source-id", required=True, help="Source ID.")
    browse_source_files_parser.add_argument("--format", choices=TV_FORMAT_CHOICES, default="json", help="Output format.")
    browse_source_files_parser.add_argument("--entry", help="Entry to preview.")
    browse_source_files_parser.set_defaults(handler=cmd_browse_source_files)

    return parser


def emit(payload: object, as_json: bool) -> int:
    """Print *payload* to stdout and return exit code ``0``."""
    import sys
    if as_json:
        text = json.dumps(payload, indent=2, sort_keys=True)
    elif isinstance(payload, str):
        text = payload
    else:
        text = json.dumps(payload, indent=2, sort_keys=True)
    sys.stdout.buffer.write(text.encode("utf-8", errors="replace"))
    sys.stdout.buffer.write(b"\n")
    sys.stdout.buffer.flush()
    return 0


_SYNC_ATTR_MAP: dict[str, str] = {
    "confluence": "space",
    "arxiv": "url",
    "site": "url",
    "video": "url",
    "television": "name",
    "github-repo": "repo_url",
    "google-releases": "url",
    "jira-project": "project",
    "aha": "workspace",
}


def _validate_url(value: str) -> None:
    """Raise ``SystemExit`` if *value* is not a valid URL with scheme."""
    from .errors import InvalidURLError

    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise InvalidURLError(value, reason="URL must start with http:// or https://")


def main(argv: list[str] | None = None) -> int:
    """Entry-point for the ``know`` CLI."""

    load_dotenv()
    parser = build_parser()
    args = parser.parse_args(argv)

    # Logging -----------------------------------------------------------
    if getattr(args, "quiet", False):
        logging.basicConfig(level=logging.ERROR, format="%(message)s")
    elif getattr(args, "verbose", False):
        logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")
    else:
        logging.basicConfig(level=logging.WARNING, format="%(message)s")

    # Resolve sync match_value via attribute map -------------------------
    sync_cmd = getattr(args, "sync_command", None)
    if sync_cmd in _SYNC_ATTR_MAP:
        args.match_value = getattr(args, _SYNC_ATTR_MAP[sync_cmd])

    # URL validation for source registration commands --------------------
    add_cmd = getattr(args, "add_command", None)
    if add_cmd in {"arxiv", "site", "google-releases"} and hasattr(args, "url"):
        _validate_url(args.url)

    try:
        result = args.handler(args)
    except Exception as exc:  # pragma: no cover - CLI boundary
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return emit(result, args.json)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
