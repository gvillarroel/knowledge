from __future__ import annotations

from argparse import Namespace
from datetime import datetime
from pathlib import Path

from .exporter import export_source
from .registry import create_source_adapter
from .sources.arxiv import search_arxiv
from .sources.video import extract_video_id
from .store import KnowledgeStore


def _store_from_args(args: Namespace) -> KnowledgeStore:
    return KnowledgeStore(args.store)


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
    return {"keys": sorted(store.keys)}


def cmd_add_key(args: Namespace) -> dict:
    store = _store_from_args(args)
    store.initialize()
    payload = store.create_collection_key(args.name)
    return {"created": payload["name"]}


def cmd_list_keys(args: Namespace) -> dict:
    store = _store_from_args(args)
    store.initialize()
    return {"keys": store.list_collection_keys()}


def cmd_list_collection_sources(args: Namespace) -> dict:
    store = _store_from_args(args)
    store.initialize()
    return {
        "sources": store.list_collection_sources(
            key_name=getattr(args, "key", None),
            source_type=getattr(args, "type", None),
        )
    }


def cmd_add_confluence(args: Namespace) -> dict:
    store = _store_from_args(args)
    store.initialize()
    config = {
        "space": args.space,
        "space_key": args.space,
        "base_url": args.base_url,
        "username": args.username,
        "token": args.token,
        "limit": args.limit,
    }
    source = store.add_collection_source(
        key_name=args.key,
        source_type="confluence",
        title=args.space,
        config={key: value for key, value in config.items() if value is not None},
        update_command=f"know sync confluence --space {args.space} --key {args.key}",
        delete_command=f"know del --key {args.key} {store._source_id('confluence', args.space)}",
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


def cmd_add_jira_project(args: Namespace) -> dict:
    store = _store_from_args(args)
    store.initialize()
    config = {
        "project": args.project,
        "jql": args.jql or f"project = {args.project} ORDER BY updated DESC",
        "base_url": args.base_url,
        "username": args.username,
        "token": args.token,
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
        "base_url": args.base_url,
        "token": args.token,
        "limit": args.limit,
    }
    source = store.add_collection_source(
        key_name=args.key,
        source_type="aha",
        title=args.workspace,
        config={key: value for key, value in config.items() if value is not None},
        update_command=f"know sync aha-workspace {args.workspace} --key {args.key}",
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
    sources = _filter_confluence_sources_by_time_bounds(
        store.list_collection_sources(source_type="confluence"),
        start_time=getattr(args, "start_time", None),
        end_time=getattr(args, "end_time", None),
    )
    matches = []
    for source in sources:
        config = source.get("config", {})
        matches.append(
            {
                "source_id": source["id"],
                "key": source["key"],
                "space": config.get("space") or config.get("space_key") or source.get("title"),
            }
        )
    return {
        "query": args.query,
        "start_time": getattr(args, "start_time", None),
        "end_time": getattr(args, "end_time", None),
        "possible_sources": matches,
    }


def cmd_search_arxiv(args: Namespace) -> dict:
    results = search_arxiv(
        args.query,
        start=args.start,
        max_results=args.max_results,
        sort_by=args.sort_by,
        sort_order=args.sort_order,
    )
    return {
        "query": args.query,
        "search_query": results.pop("search_query", None) or None,
        "start": args.start,
        "max_results": args.max_results,
        "sort_by": args.sort_by,
        "sort_order": args.sort_order,
        **results,
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
        config.get("url"),
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


def _filter_confluence_sources_by_time_bounds(
    sources: list[dict],
    *,
    start_time: str | None,
    end_time: str | None,
) -> list[dict]:
    lower_bound = _parse_iso8601(start_time) if start_time else None
    upper_bound = _parse_iso8601(end_time) if end_time else None
    if lower_bound is None and upper_bound is None:
        return sources

    matches: list[dict] = []
    for source in sources:
        candidate = _parse_iso8601(
            source.get("last_synced_at")
            or source.get("updated_at")
            or source.get("created_at")
        )
        if candidate is None:
            continue
        if lower_bound and candidate < lower_bound:
            continue
        if upper_bound and candidate > upper_bound:
            continue
        matches.append(source)
    return matches


def _parse_iso8601(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))
