from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .commands import (
    cmd_add_aha_workspace,
    cmd_add_arxiv,
    cmd_add_confluence,
    cmd_add_github_repo,
    cmd_add_jira_project,
    cmd_add_key,
    cmd_add_site,
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
    cmd_search_confluence,
    cmd_sync,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="know",
        description="Manage a local knowledge base in ~/.knowledge.",
    )
    parser.add_argument("--store", type=Path, default=None, help="Override the knowledge store path.")
    parser.add_argument("--json", action="store_true", help="Emit command output as JSON.")

    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add", help="Create keys and attach source definitions.")
    add_subparsers = add_parser.add_subparsers(dest="add_command", required=True)

    add_key_parser = add_subparsers.add_parser("key", help="Create a knowledge key.")
    add_key_parser.add_argument("name", help="Knowledge key name.")
    add_key_parser.set_defaults(handler=cmd_add_key)

    add_confluence_parser = add_subparsers.add_parser("confluence", help="Attach a Confluence space.")
    add_confluence_parser.add_argument("--space", required=True, help="Confluence space key.")
    add_confluence_parser.add_argument("--key", required=True, help="Knowledge key name.")
    add_confluence_parser.add_argument("--base-url", help="Confluence base URL.")
    add_confluence_parser.add_argument("--username", help="Username or credential key reference.")
    add_confluence_parser.add_argument("--token", help="Token or credential key reference.")
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

    add_github_parser = add_subparsers.add_parser("github-repo", help="Attach a GitHub repository.")
    add_github_parser.add_argument("repo_url", help="Git repository URL.")
    add_github_parser.add_argument("--key", required=True, help="Knowledge key name.")
    add_github_parser.add_argument("--branch", action="append", help="Branch to include. Repeatable.")
    add_github_parser.set_defaults(handler=cmd_add_github_repo)

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

    add_aha_parser = add_subparsers.add_parser("aha-workspace", help="Attach an Aha workspace.")
    add_aha_parser.add_argument("workspace", help="Aha workspace or product identifier.")
    add_aha_parser.add_argument("--key", required=True, help="Knowledge key name.")
    add_aha_parser.add_argument("--base-url", help="Aha base URL.")
    add_aha_parser.add_argument("--token", help="Token or credential key reference.")
    add_aha_parser.add_argument("--limit", type=int, help="Feature sync limit.")
    add_aha_parser.set_defaults(handler=cmd_add_aha_workspace)

    list_parser = subparsers.add_parser("list", help="List keys, credentials, or attached sources.")
    list_subparsers = list_parser.add_subparsers(dest="list_command", required=True)

    list_keys_parser = list_subparsers.add_parser("keys", help="List knowledge keys.")
    list_keys_parser.set_defaults(handler=cmd_list_keys)

    list_credentials_parser = list_subparsers.add_parser("credentials", help="List stored credential names.")
    list_credentials_parser.set_defaults(handler=cmd_key_list)

    list_sources_parser = list_subparsers.add_parser("sources", help="List sources attached to keys.")
    list_sources_parser.add_argument("--key", help="Restrict to a single knowledge key.")
    list_sources_parser.add_argument("--type", help="Restrict to a single source type.")
    list_sources_parser.set_defaults(handler=cmd_list_collection_sources)

    search_parser = subparsers.add_parser("search", help="Search configured source definitions.")
    search_subparsers = search_parser.add_subparsers(dest="search_command", required=True)

    search_confluence_parser = search_subparsers.add_parser("confluence", help="List Confluence sources.")
    search_confluence_parser.add_argument("query", help="Free-text query string.")
    search_confluence_parser.add_argument("--start-time", help="Optional lower time bound.")
    search_confluence_parser.add_argument("--end-time", help="Optional upper time bound.")
    search_confluence_parser.set_defaults(handler=cmd_search_confluence)

    search_arxiv_parser = search_subparsers.add_parser("arxiv", help="Search arXiv via the public API.")
    search_arxiv_parser.add_argument("query", help="arXiv search_query expression or plain text.")
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

    sync_github_parser = sync_subparsers.add_parser("github-repo", help="Sync a GitHub repository source.")
    sync_github_parser.add_argument("repo_url", help="Git repository URL.")
    sync_github_parser.add_argument("--key", required=True, help="Knowledge key name.")
    sync_github_parser.add_argument("--branch", action="append", help="Optional branch filters.")
    sync_github_parser.set_defaults(handler=cmd_sync, source_type="github", match_value=None)

    sync_jira_parser = sync_subparsers.add_parser("jira-project", help="Sync a Jira project source.")
    sync_jira_parser.add_argument("project", help="Jira project key.")
    sync_jira_parser.add_argument("--key", required=True, help="Knowledge key name.")
    sync_jira_parser.set_defaults(handler=cmd_sync, source_type="jira", match_value=None)

    sync_aha_parser = sync_subparsers.add_parser("aha-workspace", help="Sync an Aha workspace source.")
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

    return parser


def emit(payload: object, as_json: bool) -> int:
    if as_json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    elif isinstance(payload, str):
        print(payload)
    else:
        print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if getattr(args, "sync_command", None) == "confluence":
        args.match_value = args.space
    elif getattr(args, "sync_command", None) == "arxiv":
        args.match_value = args.url
    elif getattr(args, "sync_command", None) == "site":
        args.match_value = args.url
    elif getattr(args, "sync_command", None) == "video":
        args.match_value = args.url
    elif getattr(args, "sync_command", None) == "github-repo":
        args.match_value = args.repo_url
    elif getattr(args, "sync_command", None) == "jira-project":
        args.match_value = args.project
    elif getattr(args, "sync_command", None) == "aha-workspace":
        args.match_value = args.workspace

    try:
        result = args.handler(args)
    except Exception as exc:  # pragma: no cover - CLI boundary
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return emit(result, args.json)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
