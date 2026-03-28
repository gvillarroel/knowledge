from __future__ import annotations

from argparse import Namespace
import os
from pathlib import Path
import shutil

from .exporter import export_source
from .registry import create_source_adapter
from .sources.arxiv import search_arxiv
from .sources.brave import search_brave
from .sources.confluence import search_confluence
from .sources.jira import search_jira
from .sources.video import extract_video_id
from .store import KnowledgeStore
from .television import (
    format_arxiv_preview,
    format_arxiv_television,
    format_brave_preview,
    format_brave_television,
    format_confluence_preview,
    format_confluence_television,
    format_jira_preview,
    format_jira_television,
    format_keys_preview,
    format_keys_television,
    format_sources_preview,
    format_sources_television,
)


def _store_from_args(args: Namespace) -> KnowledgeStore:
    return KnowledgeStore(args.store)


def _config_value_or_env_ref(explicit_value: str | None, env_name: str) -> str | None:
    if explicit_value is not None:
        return explicit_value
    if os.getenv(env_name):
        return f"$env:{env_name}"
    return None


def cmd_init(args: Namespace) -> dict:
    store = _store_from_args(args)
    store.initialize()
    return {"store": str(store.root), "created": True}


def cmd_key_set(args: Namespace) -> dict:
    store = _store_from_args(args)
    store.initialize()
    store.set_key(args.name, args.value)
    return {"stored": args.name}


def cmd_key_list(args: Namespace) -> dict:
    store = _store_from_args(args)
    store.initialize()
    names = sorted(store.keys)
    return {"credentials": names}


def cmd_add_key(args: Namespace) -> dict:
    store = _store_from_args(args)
    store.initialize()
    payload = store.create_collection_key(args.name)
    return {"created": payload["name"]}


def cmd_list_keys(args: Namespace) -> dict:
    store = _store_from_args(args)
    store.initialize()
    keys = store.list_collection_keys()
    output_format = getattr(args, "format", "json")
    if output_format == "television":
        return format_keys_television(keys)
    if output_format == "television-preview":
        return format_keys_preview(keys, getattr(args, "entry", None))
    return {"keys": keys}


def cmd_list_collection_sources(args: Namespace) -> dict:
    store = _store_from_args(args)
    store.initialize()
    sources = store.list_collection_sources(
        key_name=getattr(args, "key", None),
        source_type=getattr(args, "type", None),
    )
    output_format = getattr(args, "format", "json")
    if output_format == "television":
        return format_sources_television(sources)
    if output_format == "television-preview":
        entry = getattr(args, "entry", None)
        source = _find_selected_source(sources, entry)
        body = _read_source_markdown_body(store, source) if source else None
        return format_sources_preview(sources, entry, markdown_body=body)
    return {"sources": sources}


def _find_selected_source(
    sources: list[dict], selected: str | None
) -> dict | None:
    """Resolve the source dict that matches the selected television row."""
    if not sources:
        return None
    if not selected:
        return sources[0]
    sel_id = selected.split(" | ", 1)[0].strip()
    for s in sources:
        if s.get("id") == sel_id:
            return s
    return sources[0]


def _read_source_markdown_body(store: KnowledgeStore, source: dict) -> str | None:
    """Read ``.md`` files from a source directory and return the body without YAML frontmatter."""
    try:
        source_dir = store.source_dir(source)
    except Exception:
        return None
    if not source_dir.exists():
        return None
    md_files = sorted(source_dir.glob("**/*.md"))
    if not md_files:
        return None
    parts: list[str] = []
    for md_file in md_files:
        try:
            text = md_file.read_text(encoding="utf-8")
        except Exception:
            continue
        body = _strip_yaml_frontmatter(text)
        if body.strip():
            parts.append(body.strip())
    return "\n\n---\n\n".join(parts) if parts else None


def _strip_yaml_frontmatter(text: str) -> str:
    """Remove leading YAML frontmatter delimited by ``---``."""
    if not text.startswith("---"):
        return text
    end = text.find("\n---", 3)
    if end == -1:
        return text
    return text[end + 4:].lstrip("\n")


def cmd_add_confluence(args: Namespace) -> dict:
    if not args.space and not args.cql:
        raise ValueError("confluence add requires --space or --cql")
    store = _store_from_args(args)
    store.initialize()
    config = {
        "space": args.space,
        "space_key": args.space,
        "base_url": args.base_url or os.getenv("CONFLUENCE_BASE_URL"),
        "username": _config_value_or_env_ref(args.username, "CONFLUENCE_USERNAME"),
        "token": _config_value_or_env_ref(args.token, "CONFLUENCE_TOKEN"),
        "cql": args.cql,
        "limit": args.limit,
    }
    title = args.space or args.cql
    update_command = (
        f"know sync confluence --space {args.space} --key {args.key}"
        if args.space
        else f"know sync --key {args.key}"
    )
    source = store.add_collection_source(
        key_name=args.key,
        source_type="confluence",
        title=title,
        config={key: value for key, value in config.items() if value is not None},
        update_command=update_command,
        delete_command=f"know del --key {args.key} {store._source_id('confluence', title)}",
    )
    return {"key": args.key, "source": source}


def cmd_add_arxiv(args: Namespace) -> dict:
    store = _store_from_args(args)
    store.initialize()
    source = store.add_collection_source(
        key_name=args.key,
        source_type="arxiv",
        title=args.url,
        config={"url": args.url},
        update_command=f"know sync arxiv {args.url} --key {args.key}",
        delete_command=f"know del --key {args.key} {store._source_id('arxiv', args.url)}",
    )
    return {"key": args.key, "source": source}


def cmd_add_site(args: Namespace) -> dict:
    store = _store_from_args(args)
    store.initialize()
    normalized_url = args.url.rstrip("/") or args.url
    source_id = store._source_id("site", normalized_url)
    config = {
        "url": args.url,
        "max_depth": args.max_depth,
        "max_pages": args.max_pages,
    }
    source = store.add_collection_source(
        key_name=args.key,
        source_type="site",
        source_id=source_id,
        title=args.url,
        config=config,
        update_command=f"know sync site {args.url} --key {args.key}",
        delete_command=f"know del --key {args.key} {source_id}",
    )
    return {"key": args.key, "source": source}


def cmd_add_video(args: Namespace) -> dict:
    store = _store_from_args(args)
    store.initialize()
    video_id = extract_video_id(args.url)
    config = {
        "url": args.url,
        "languages": args.language or ["en"],
    }
    source = store.add_collection_source(
        key_name=args.key,
        source_type="video",
        source_id=f"video-{video_id.lower()}",
        title=args.url,
        config=config,
        update_command=f"know sync video {args.url} --key {args.key}",
        delete_command=f"know del --key {args.key} video-{video_id.lower()}",
    )
    return {"key": args.key, "source": source}


def cmd_add_television(args: Namespace) -> dict:
    if not args.name:
        if any(
            value is not None
            for value in (
                args.key,
                args.description,
                args.source_command,
                args.source_display,
                args.preview_command,
                args.action_command,
            )
        ):
            raise ValueError(
                "know add tv without a channel name only installs the bundled cables; "
                "to register a channel provide NAME, --key, and --source-command"
            )
        return _install_bundled_television_cables()

    if not args.key or not args.source_command:
        raise ValueError("know add tv <NAME> requires --key and --source-command")

    store = _store_from_args(args)
    store.initialize()
    source_id = store._source_id("television", args.name)
    config = {
        "channel": args.name,
        "description": args.description or f"Television channel for knowledge key {args.key}",
        "source_command": args.source_command,
        "source_display": args.source_display,
        "preview_command": args.preview_command,
        "action_command": args.action_command,
    }
    normalized_config = {key: value for key, value in config.items() if value is not None}
    source = _upsert_television_source(
        store=store,
        key_name=args.key,
        source_id=source_id,
        title=args.name,
        config=normalized_config,
        update_command=f"know sync television {args.name} --key {args.key}",
        delete_command=f"know del --key {args.key} {source_id}",
    )
    return {"key": args.key, "source": source}


def _upsert_television_source(
    *,
    store: KnowledgeStore,
    key_name: str,
    source_id: str,
    title: str,
    config: dict[str, object],
    update_command: str,
    delete_command: str,
) -> dict[str, object]:
    """Create or replace a Television channel registration for a key."""
    existing = next(
        (
            source
            for source in store.list_collection_sources(key_name=key_name, source_type="television")
            if source.get("id") == source_id
        ),
        None,
    )
    if existing is None:
        return store.add_collection_source(
            key_name=key_name,
            source_type="television",
            source_id=source_id,
            title=title,
            config=config,
            update_command=update_command,
            delete_command=delete_command,
        )

    updated_source = {
        **existing,
        "title": title,
        "config": config,
        "update_command": update_command,
        "delete_command": delete_command,
    }
    store.update_collection_source(updated_source)
    return updated_source


def _install_bundled_television_cables() -> dict:
    """Copy the repository's bundled Television cable files into Television's config dir."""
    source_dir = Path(__file__).resolve().parents[2] / "cables"
    if not source_dir.exists():
        raise FileNotFoundError(f"bundled cable directory '{source_dir}' not found")

    installed: list[str] = []
    destination_dirs = _television_cable_destinations()
    for destination_dir in destination_dirs:
        destination_dir.mkdir(parents=True, exist_ok=True)
        for cable_path in sorted(source_dir.glob("*.toml")):
            shutil.copy2(cable_path, destination_dir / cable_path.name)
            if cable_path.name not in installed:
                installed.append(cable_path.name)

    return {
        "destination": str(destination_dirs[0]),
        "destinations": [str(path) for path in destination_dirs],
        "installed": installed,
    }


def _television_cable_destinations() -> list[Path]:
    """Return the Television cable directories active for this environment."""
    destinations: list[Path] = []

    television_config = os.getenv("TELEVISION_CONFIG")
    if television_config:
        destinations.append(Path(television_config).expanduser().resolve() / "cable")

    local_app_data = os.getenv("LOCALAPPDATA")
    if local_app_data:
        destinations.append(Path(local_app_data).expanduser().resolve() / "television" / "config" / "cable")

    destinations.append(Path.home() / ".config" / "television" / "cable")

    unique_destinations: list[Path] = []
    seen: set[Path] = set()
    for destination in destinations:
        resolved = destination.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        unique_destinations.append(resolved)
    return unique_destinations


def cmd_add_github_repo(args: Namespace) -> dict:
    store = _store_from_args(args)
    store.initialize()
    config = {
        "repo_url": args.repo_url,
        "branches": args.branch or ["HEAD"],
    }
    source = store.add_collection_source(
        key_name=args.key,
        source_type="github",
        title=args.repo_url,
        config=config,
        update_command=_build_github_sync_command(args.repo_url, args.key, config["branches"]),
        delete_command=f"know del --key {args.key} {store._source_id('github', args.repo_url)}",
    )
    return {"key": args.key, "source": source}


def cmd_add_google_releases(args: Namespace) -> dict:
    store = _store_from_args(args)
    store.initialize()
    source = store.add_collection_source(
        key_name=args.key,
        source_type="google_releases",
        title=args.url,
        config={"url": args.url},
        update_command=f"know sync google-releases {args.url} --key {args.key}",
        delete_command=f"know del --key {args.key} {store._source_id('google_releases', args.url)}",
    )
    return {"key": args.key, "source": source}


def cmd_add_jira_project(args: Namespace) -> dict:
    store = _store_from_args(args)
    store.initialize()
    config = {
        "project": args.project,
        "jql": args.jql or f"project = {args.project} ORDER BY updated DESC",
        "base_url": args.base_url or os.getenv("JIRA_BASE_URL"),
        "username": _config_value_or_env_ref(args.username, "JIRA_USERNAME"),
        "token": _config_value_or_env_ref(args.token, "JIRA_TOKEN"),
        "fields": args.field,
        "limit": args.limit,
    }
    source = store.add_collection_source(
        key_name=args.key,
        source_type="jira",
        title=args.project,
        config={key: value for key, value in config.items() if value is not None},
        update_command=f"know sync jira-project {args.project} --key {args.key}",
        delete_command=f"know del --key {args.key} {store._source_id('jira', args.project)}",
    )
    return {"key": args.key, "source": source}


def cmd_add_aha_workspace(args: Namespace) -> dict:
    store = _store_from_args(args)
    store.initialize()
    config = {
        "workspace": args.workspace,
        "product": args.workspace,
        "base_url": args.base_url or os.getenv("AHA_BASE_URL"),
        "token": _config_value_or_env_ref(args.token, "AHA_TOKEN"),
        "limit": args.limit,
    }
    source = store.add_collection_source(
        key_name=args.key,
        source_type="aha",
        title=args.workspace,
        config={key: value for key, value in config.items() if value is not None},
        update_command=f"know sync aha {args.workspace} --key {args.key}",
        delete_command=f"know del --key {args.key} {store._source_id('aha', args.workspace)}",
    )
    return {"key": args.key, "source": source}


def cmd_delete_source(args: Namespace) -> dict:
    store = _store_from_args(args)
    store.initialize()
    return store.delete_collection_source(args.key, args.source_id)


def cmd_search_confluence(args: Namespace) -> dict:
    store = _store_from_args(args)
    store.initialize()
    sources = store.list_collection_sources(
        key_name=getattr(args, "knowledge_key", None),
        source_type="confluence",
    )
    if getattr(args, "space", None):
        sources = [
            source
            for source in sources
            if (source.get("config", {}).get("space") or source.get("config", {}).get("space_key")) == args.space
        ]
    matches = []
    for source in sources:
        config = source.get("config", {})
        if not config.get("base_url") or not config.get("username") or not config.get("token"):
            matches.append(
                {
                    "source_id": source["id"],
                    "key": source["key"],
                    "space": config.get("space") or config.get("space_key") or source.get("title"),
                    "error": "missing credentials or base_url",
                }
            )
            continue
        results = search_confluence(
            base_url=config["base_url"],
            username=store.resolve_key(config["username"]),
            token=store.resolve_key(config["token"]),
            query=getattr(args, "query", None),
            cql=getattr(args, "cql", None),
            space=getattr(args, "space", None) or config.get("space") or config.get("space_key"),
            content_type=getattr(args, "type", None),
            labels=getattr(args, "label", None),
            title_contains=getattr(args, "title_contains", None),
            text_contains=getattr(args, "text_contains", None),
            created_after=getattr(args, "created_after", None),
            created_before=getattr(args, "created_before", None),
            updated_after=getattr(args, "updated_after", None),
            updated_before=getattr(args, "updated_before", None),
            limit=getattr(args, "limit", 25),
            cursor=getattr(args, "cursor", None),
        )
        matches.append(
            {
                "source_id": source["id"],
                "key": source["key"],
                "space": config.get("space") or config.get("space_key") or source.get("title"),
                "base_url": config.get("base_url"),
                "cql": results["cql"],
                "results": results["results"],
                "next_cursor": results["next_cursor"],
            }
        )
    return _format_confluence_output(args, matches)


def cmd_search_jira(args: Namespace) -> dict:
    store = _store_from_args(args)
    store.initialize()
    sources = store.list_collection_sources(
        key_name=getattr(args, "knowledge_key", None),
        source_type="jira",
    )
    if getattr(args, "project", None):
        sources = [source for source in sources if source.get("config", {}).get("project") == args.project]

    matches = []
    for source in sources:
        config = source.get("config", {})
        if not config.get("base_url") or not config.get("username") or not config.get("token"):
            matches.append(
                {
                    "source_id": source["id"],
                    "key": source["key"],
                    "project": config.get("project") or source.get("title"),
                    "error": "missing credentials or base_url",
                }
            )
            continue
        results = search_jira(
            base_url=config["base_url"],
            username=store.resolve_key(config["username"]),
            token=store.resolve_key(config["token"]),
            query=getattr(args, "query", None),
            project=getattr(args, "project", None) or config.get("project"),
            jql=getattr(args, "jql", None),
            statuses=getattr(args, "status", None),
            issue_types=getattr(args, "issue_type", None),
            assignee=getattr(args, "assignee", None),
            reporter=getattr(args, "reporter", None),
            created_after=getattr(args, "created_after", None),
            created_before=getattr(args, "created_before", None),
            updated_after=getattr(args, "updated_after", None),
            updated_before=getattr(args, "updated_before", None),
            order_by=getattr(args, "order_by", None),
            fields=getattr(args, "field", None),
            properties=getattr(args, "property", None),
            limit=getattr(args, "limit", 25),
            next_page_token=getattr(args, "next_page_token", None),
            expand=getattr(args, "expand", None),
            fields_by_keys=getattr(args, "fields_by_keys", False),
        )
        matches.append(
            {
                "source_id": source["id"],
                "key": source["key"],
                "project": config.get("project") or source.get("title"),
                "base_url": config.get("base_url"),
                "jql": results["jql"],
                "issues": results["issues"],
                "next_page_token": results["next_page_token"],
            }
        )
    return _format_jira_output(args, matches)


def cmd_search_arxiv(args: Namespace) -> dict:
    results = search_arxiv(
        args.query,
        start=args.start,
        max_results=args.max_results,
        sort_by=args.sort_by,
        sort_order=args.sort_order,
    )
    output_format = getattr(args, "format", "json")
    if output_format == "television":
        entries = results.get("entries", [])
        return format_arxiv_television(entries)
    if output_format == "television-preview":
        entries = results.get("entries", [])
        return format_arxiv_preview(entries, getattr(args, "entry", None))
    return {
        "query": args.query,
        "search_query": results.pop("search_query", None) or None,
        "start": args.start,
        "max_results": args.max_results,
        "sort_by": args.sort_by,
        "sort_order": args.sort_order,
        **results,
    }


def cmd_search_brave(args: Namespace) -> dict:
    """Search the web through the Brave Search API."""
    store = _store_from_args(args)
    store.initialize()
    results = search_brave(
        args.query,
        api_key=_resolve_brave_api_key(store),
        count=args.count,
    )
    output_format = getattr(args, "format", "json")
    if output_format == "television":
        return format_brave_television(results["results"])
    if output_format == "television-preview":
        return format_brave_preview(results["results"], getattr(args, "entry", None))
    return results


def _resolve_brave_api_key(store: KnowledgeStore) -> str:
    """Resolve the Brave Search API key from env or stored credentials."""
    if os.getenv("BRAVE_SEARCH_API_KEY"):
        return os.environ["BRAVE_SEARCH_API_KEY"]
    for ref in ("$brave_search_api_key", "$brave_api_key"):
        try:
            return store.resolve_key(ref)
        except Exception:
            continue
    raise ValueError(
        "Brave Search API key not configured. Set BRAVE_SEARCH_API_KEY or store `brave_search_api_key`."
    )


def _format_confluence_output(args: Namespace, matches: list[dict]) -> object:
    output_format = getattr(args, "format", "json")
    if output_format == "television":
        return format_confluence_television(matches)
    if output_format == "television-preview":
        return format_confluence_preview(matches, getattr(args, "entry", None))
    return {
        "query": args.query,
        "cql": getattr(args, "cql", None),
        "content_type": getattr(args, "type", None),
        "labels": getattr(args, "label", None) or [],
        "limit": getattr(args, "limit", 25),
        "cursor": getattr(args, "cursor", None),
        "matches": matches,
    }


def _format_jira_output(args: Namespace, matches: list[dict]) -> object:
    output_format = getattr(args, "format", "json")
    if output_format == "television":
        return format_jira_television(matches)
    if output_format == "television-preview":
        return format_jira_preview(matches, getattr(args, "entry", None))
    return {
        "query": getattr(args, "query", None),
        "jql": getattr(args, "jql", None),
        "limit": getattr(args, "limit", 25),
        "statuses": getattr(args, "status", None) or [],
        "issue_types": getattr(args, "issue_type", None) or [],
        "assignee": getattr(args, "assignee", None),
        "reporter": getattr(args, "reporter", None),
        "order_by": getattr(args, "order_by", None) or [],
        "fields": getattr(args, "field", None) or [],
        "properties": getattr(args, "property", None) or [],
        "expand": getattr(args, "expand", None) or [],
        "fields_by_keys": getattr(args, "fields_by_keys", False),
        "matches": matches,
    }


def cmd_sync(args: Namespace) -> dict:
    store = _store_from_args(args)
    store.initialize()
    key_name = getattr(args, "key", None)
    source_type = getattr(args, "source_type", None)
    matched_value = getattr(args, "match_value", None)

    sources = store.list_collection_sources(key_name=key_name, source_type=source_type)
    if matched_value:
        sources = [source for source in sources if _matches_source(source, matched_value)]
    synced = [create_source_adapter(_prepare_source_for_sync(source, args), store).sync() for source in sources]
    return {"synced": synced}


def cmd_export(args: Namespace) -> dict:
    store = _store_from_args(args)
    store.initialize()
    key_names = [args.key] if args.key else store.list_collection_keys()
    exported: list[dict] = []
    for key_name in key_names:
        for source in store.list_collection_sources(key_name=key_name):
            exported.append(export_source(store, source))
    archive = store.archive_keys(key_names)
    return {"exported": exported, "archive": str(archive)}


def cmd_import(args: Namespace) -> dict:
    store = _store_from_args(args)
    store.initialize()
    return store.import_archive(Path(args.archive))


def _matches_source(source: dict, value: str) -> bool:
    config = source.get("config", {})
    return value in {
        source.get("id"),
        source.get("title"),
        config.get("space"),
        config.get("space_key"),
        config.get("channel"),
        config.get("url"),
        config.get("feed_url"),
        config.get("repo_url"),
        config.get("video_url"),
        config.get("project"),
        config.get("workspace"),
        config.get("product"),
    }


def _build_github_sync_command(repo_url: str, key_name: str, branches: list[str]) -> str:
    branch_flags = " ".join(f"--branch {branch}" for branch in branches)
    suffix = f" {branch_flags}" if branch_flags else ""
    return f"know sync github-repo {repo_url} --key {key_name}{suffix}"


def _prepare_source_for_sync(source: dict, args: Namespace) -> dict:
    prepared = {
        **source,
        "config": dict(source.get("config", {})),
    }
    branch_override = getattr(args, "branch", None)
    if prepared.get("type") == "github" and branch_override:
        prepared["_sync_branches"] = list(branch_override)
    return prepared
