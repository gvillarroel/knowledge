"""CLI commands for ServiceNow registration, discovery, and explicit ticket writes."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
from typing import Any

from .browse_commands import cmd_browse_local
from .errors import KnowledgeError, SourceNotFoundError
from .sources.servicenow import (
    SYNC_TABLES, TICKET_TABLES, ServiceNowSource, client_from_config,
    encoded_query, field_value, instance_url, record_markdown, scope_query,
    validate_sys_id, checked_fields,
)
from .store import KnowledgeStore
from .television import TV_FORMAT_CHOICES


def _add_auth(parser: argparse.ArgumentParser, *, selection: bool = True) -> None:
    if selection:
        parser.add_argument("--key", help="Use a registered ServiceNow source on this knowledge key.")
        parser.add_argument("--source-id", help="Select one exact registered source; requires --key.")
    parser.add_argument("--base-url", help="HTTPS instance origin; defaults to SERVICENOW_BASE_URL.")
    parser.add_argument("--username", help="Instance username or credential reference.")
    parser.add_argument("--password", help="Password reference ($name or $env:NAME), never a literal secret.")
    parser.add_argument("--token", help="Bearer token reference ($name or $env:NAME), instead of basic authentication.")


def _add_format(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--format", choices=TV_FORMAT_CHOICES, default="json", help="Output format.")
    parser.add_argument("--entry", help="Exact result row to preview.")


def _add_filters(parser: argparse.ArgumentParser, *, default_table: str | None = None) -> None:
    parser.add_argument("--table", choices=SYNC_TABLES, default=default_table, help="ServiceNow table (default: incident).")
    parser.add_argument("--query", help="Encoded filter; no ^NQ, ^EQ, or JavaScript.")
    parser.add_argument("--knowledge-base", help="Exact kb_knowledge_base sys_id; only for kb_knowledge.")
    parser.add_argument("--assignment-group", help="Exact assignment group sys_id; only for tickets.")
    parser.add_argument("--field", action="append", help="Field to retrieve; repeatable. Identity fields are always included.")


def register_servicenow_parsers(
    root: Any, add: Any, search: Any, sync: Any, browse: Any,
) -> None:
    """Attach ServiceNow to the established command families and explicit write group."""
    add_parser = add.add_parser("servicenow", help="Attach a scoped ServiceNow table or knowledge base.")
    add_parser.add_argument("--key", required=True, help="Knowledge key name.")
    _add_auth(add_parser, selection=False)
    _add_filters(add_parser, default_table="incident")
    add_parser.add_argument("--limit", type=int, default=1000, help="Maximum records per synchronization.")
    add_parser.add_argument("--page-size", type=int, default=100, help="Records requested per page (1-100).")
    add_parser.set_defaults(handler=cmd_add_servicenow)

    sync_parser = sync.add_parser("servicenow", help="Upsert registered ServiceNow records into local Markdown.")
    sync_parser.add_argument("--key", required=True, help="Knowledge key name.")
    sync_parser.add_argument("--source-id", help="Sync one exact registration instead of all ServiceNow sources on the key.")
    sync_parser.set_defaults(handler=cmd_sync_servicenow)

    search_parser = search.add_parser("servicenow", help="Search ServiceNow records through the Table API.")
    _add_auth(search_parser)
    _add_filters(search_parser)
    search_parser.add_argument("text", nargs="?", help="Literal text to find in short_description.")
    search_parser.add_argument("--limit", type=int, default=25, help="Maximum records to return.")
    search_parser.add_argument("--offset", type=int, default=0, help="Offset from a previous next_offset result.")
    _add_format(search_parser)
    search_parser.set_defaults(handler=cmd_search_servicenow)

    browse_parser = browse.add_parser("servicenow", help="Browse locally synchronized ServiceNow Markdown.")
    browse_parser.add_argument("--key", help="Knowledge key name.")
    _add_format(browse_parser)
    browse_parser.set_defaults(handler=cmd_browse_local, type="servicenow")

    service = root.add_parser("servicenow", help="Read tickets, create incidents, and discover knowledge bases.")
    actions = service.add_subparsers(dest="servicenow_command", required=True)
    read = actions.add_parser("read-ticket", help="Read one exact ticket by number or sys_id.")
    read.add_argument("identifier", help="Ticket number (for example INC0010001) or sys_id.")
    read.add_argument("--table", choices=TICKET_TABLES, help="Ticket table (default: incident or registered table).")
    _add_auth(read)
    read.set_defaults(handler=cmd_read_servicenow_ticket)

    create = actions.add_parser("create-ticket", help="Explicitly create one incident and verify it with GET.")
    _add_auth(create)
    create.add_argument("--short-description", required=True, help="Incident summary.")
    description = create.add_mutually_exclusive_group()
    description.add_argument("--description", help="Incident description.")
    description.add_argument("--description-file", type=Path, help="UTF-8 incident description file.")
    create.add_argument("--caller-id", help="Caller sys_id, when required by the instance.")
    create.add_argument("--assignment-group", help="Assignment group sys_id.")
    create.add_argument("--impact", choices=("1", "2", "3"), help="Impact: 1 high, 2 medium, 3 low.")
    create.add_argument("--urgency", choices=("1", "2", "3"), help="Urgency: 1 high, 2 medium, 3 low.")
    create.add_argument("--correlation-id", help="External reference to identify this request; not an idempotency guarantee.")
    create.add_argument("--dry-run", action="store_true", help="Preview the POST without resolving secrets or accessing the network.")
    create.set_defaults(handler=cmd_create_servicenow_ticket)

    bases = actions.add_parser("knowledge-bases", help="List accessible knowledge bases and their sys_ids.")
    _add_auth(bases)
    bases.add_argument("--limit", type=int, default=100, help="Maximum knowledge bases to return.")
    bases.add_argument("--offset", type=int, default=0, help="Offset from a previous result.")
    _add_format(bases)
    bases.set_defaults(handler=cmd_servicenow_knowledge_bases)


def _reference(value: str | None, name: str) -> str | None:
    if value is not None and not re.fullmatch(r"\$(?:env:[A-Za-z_][A-Za-z0-9_]*|[A-Za-z_][A-Za-z0-9_.-]*)", value):
        raise KnowledgeError(f"ServiceNow {name} must be a $name or $env:NAME reference; literal secrets are not stored.")
    return value


def _direct_config(args: argparse.Namespace) -> dict[str, Any]:
    config: dict[str, Any] = {"base_url": instance_url(args.base_url or os.getenv("SERVICENOW_BASE_URL"))}
    username, password, token = args.username, args.password, args.token
    if token and (username is not None or password is not None):
        raise KnowledgeError("Choose ServiceNow bearer authentication or username/password, not both.")
    if token is not None or (username is None and password is None and os.getenv("SERVICENOW_TOKEN")):
        config["token"] = _reference(token or "$env:SERVICENOW_TOKEN", "token")
    else:
        config["username"] = username or "$env:SERVICENOW_USERNAME"
        config["password"] = _reference(password or "$env:SERVICENOW_PASSWORD", "password")
    return config


def _safe_key(value: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", value):
        raise KnowledgeError("ServiceNow knowledge keys must be a single alphanumeric path segment.")
    return value


def _connection(args: argparse.Namespace) -> tuple[KnowledgeStore, dict[str, Any], dict[str, Any] | None]:
    store = KnowledgeStore(args.store)
    key = getattr(args, "key", None)
    source_id = getattr(args, "source_id", None)
    if source_id and not key:
        raise KnowledgeError("--source-id requires --key.")
    if not key:
        return store, _direct_config(args), None
    if any(getattr(args, name, None) is not None for name in ("base_url", "username", "password", "token")):
        raise KnowledgeError("Use the registered connection with --key, or explicit connection options without --key.")
    sources = store.list_collection_sources(key_name=_safe_key(key), source_type="servicenow")
    if source_id:
        sources = [source for source in sources if source["id"] == source_id]
    if not sources:
        raise SourceNotFoundError(key, source_id or "servicenow")
    if len(sources) != 1:
        raise KnowledgeError("Multiple ServiceNow sources match; choose --source-id explicitly.")
    source = sources[0]
    config = dict(source["config"])
    if getattr(args, "table", None) and args.table != config.get("table", "incident"):
        raise KnowledgeError("--table must match the registered ServiceNow source.")
    return store, config, source


def cmd_add_servicenow(args: argparse.Namespace) -> dict[str, Any]:
    """Register a reproducible table selection without resolving or persisting secrets."""
    _safe_key(args.key)
    config = _direct_config(args)
    if args.limit < 1 or not 1 <= args.page_size <= 100:
        raise KnowledgeError("ServiceNow limit must be positive and page size must be 1-100.")
    query, scope = scope_query(
        args.table, args.query or "", knowledge_base=args.knowledge_base,
        assignment_group=args.assignment_group,
    )
    config.update({
        "table": args.table, "query": encoded_query(args.query),
        "limit": args.limit, "page_size": args.page_size,
    })
    if args.knowledge_base:
        config["knowledge_base"] = scope["kb_knowledge_base"]
    if args.assignment_group:
        config["assignment_group"] = scope["assignment_group"]
    if args.field:
        config["fields"] = checked_fields(args.table, args.field, scope)
    identity = json.dumps([config["base_url"], args.table, query], ensure_ascii=True)
    source_id = f"servicenow-{args.table}-{hashlib.sha256(identity.encode()).hexdigest()[:12]}"
    store = KnowledgeStore(args.store)
    store.initialize()
    source = store.add_collection_source(
        key_name=args.key, source_type="servicenow", source_id=source_id,
        title=f"ServiceNow {args.table}", config=config,
        update_command=f"know sync servicenow --key {args.key} --source-id {source_id}",
        delete_command=f"know del --key {args.key} {source_id}",
    )
    return {"key": args.key, "source": source}


def cmd_sync_servicenow(args: argparse.Namespace) -> dict[str, Any]:
    """Sync all ServiceNow sources on a key or one exact source identity."""
    store = KnowledgeStore(args.store)
    sources = store.list_collection_sources(key_name=_safe_key(args.key), source_type="servicenow")
    if args.source_id:
        sources = [source for source in sources if source["id"] == args.source_id]
    if not sources:
        raise SourceNotFoundError(args.key, args.source_id or "servicenow")
    return {"synced": [ServiceNowSource(source, store).sync() for source in sources]}


def _output(args: argparse.Namespace, page: dict[str, Any], base_url: str) -> object:
    fmt = getattr(args, "format", "json")
    if fmt == "json":
        return page
    records = page["records"]
    if fmt == "television":
        rows = []
        for record in records:
            cells = [
                field_value(record, "number") or field_value(record, "sys_id"),
                field_value(record, "short_description") or field_value(record, "title"),
                field_value(record, "state", display=True) or field_value(record, "workflow_state", display=True),
            ]
            rows.append(" | ".join(re.sub(r"[\r\n\t|]", " ", cell) for cell in cells))
        return "\n".join(rows)
    selected = getattr(args, "entry", None)
    identity = selected.split(" | ", 1)[0].strip() if selected else None
    record = next((
        record for record in records
        if identity is None or identity in (field_value(record, "number"), field_value(record, "sys_id"))
    ), None)
    if record is None:
        return "No matching ServiceNow record."
    url = f"{base_url}/{page['table']}.do?sys_id={validate_sys_id(field_value(record, 'sys_id'))}"
    return record_markdown(record, page["table"], url)


def cmd_search_servicenow(args: argparse.Namespace) -> object:
    """Search a registered scope or an explicitly configured instance."""
    store, config, source = _connection(args)
    table = args.table or config.get("table", "incident")
    query = "^".join(filter(None, (encoded_query(config.get("query")), encoded_query(args.query))))
    knowledge_base = config.get("knowledge_base")
    assignment_group = config.get("assignment_group")
    for name, saved in (("knowledge_base", knowledge_base), ("assignment_group", assignment_group)):
        requested = getattr(args, name, None)
        if saved and requested and validate_sys_id(requested, name) != saved:
            raise KnowledgeError("Search cannot replace a registered ServiceNow scope.")
    query, scope = scope_query(
        table, query, knowledge_base=knowledge_base or args.knowledge_base,
        assignment_group=assignment_group or args.assignment_group, text=args.text,
    )
    client = client_from_config(config, store)
    page = client.list_records(
        table, query=query, scope=scope, fields=args.field or config.get("fields"),
        limit=args.limit, offset=args.offset, page_size=config.get("page_size", 100),
    )
    if source:
        page.update({"key": source["key"], "source_id": source["id"]})
    return _output(args, page, client.base_url)


def cmd_read_servicenow_ticket(args: argparse.Namespace) -> dict[str, Any]:
    """Read an exact ticket without creating or modifying a remote record."""
    store, config, _ = _connection(args)
    table = args.table or config.get("table", "incident")
    if table not in TICKET_TABLES:
        raise KnowledgeError("read-ticket requires a ticket source; use search for knowledge articles.")
    client = client_from_config(config, store)
    record = client.read_record(table, args.identifier)
    group = config.get("assignment_group")
    if group and field_value(record, "assignment_group").lower() != group:
        raise KnowledgeError("The requested ticket is outside the registered assignment group.")
    return {
        "table": table, "record": record,
        "url": client.record_url(table, field_value(record, "sys_id")),
    }


def cmd_create_servicenow_ticket(args: argparse.Namespace) -> dict[str, Any]:
    """Create an incident only through this explicit command, optionally previewing it."""
    store, config, _ = _connection(args)
    if config.get("table", "incident") != "incident":
        raise KnowledgeError("create-ticket supports incident sources only.")
    summary = args.short_description.strip()
    if not summary:
        raise KnowledgeError("A non-empty ticket short description is required.")
    fields = {"short_description": summary}
    if args.description_file:
        if args.description_file.stat().st_size > 1_048_576:
            raise KnowledgeError("Ticket description file exceeds 1 MiB.")
        fields["description"] = args.description_file.read_text(encoding="utf-8")
    elif args.description is not None:
        fields["description"] = args.description
    saved_group = config.get("assignment_group")
    if saved_group and args.assignment_group and validate_sys_id(args.assignment_group) != saved_group:
        raise KnowledgeError("Creation cannot replace the registered assignment group.")
    for name in ("caller_id", "assignment_group", "impact", "urgency", "correlation_id"):
        value = getattr(args, name)
        if name == "assignment_group":
            value = saved_group or value
        if value is not None:
            fields[name] = validate_sys_id(value, name) if name in {"caller_id", "assignment_group"} else value
    if args.dry_run:
        return {
            "dry_run": True, "method": "POST",
            "url": instance_url(config["base_url"]) + "/api/now/table/incident", "fields": fields,
        }
    return client_from_config(config, store).create_ticket(fields)


def cmd_servicenow_knowledge_bases(args: argparse.Namespace) -> object:
    """Discover accessible knowledge-base identities using the configured connection."""
    store, config, _ = _connection(args)
    client = client_from_config(config, store)
    page = client.list_records("kb_knowledge_base", limit=args.limit, offset=args.offset)
    return _output(args, page, client.base_url)
