"""ServiceNow Table API access and read-oriented knowledge synchronization."""

from __future__ import annotations

from datetime import datetime, timezone
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import tempfile
import time
from typing import Any
from urllib.parse import urlsplit

import requests

from ..errors import KnowledgeError
from ..okf import render_okf_markdown
from ..store import KnowledgeStore
from .base import SourceAdapter

TICKET_TABLES = ("incident", "problem", "change_request", "sc_task", "sc_req_item")
SYNC_TABLES = (*TICKET_TABLES, "kb_knowledge")
READ_TABLES = (*SYNC_TABLES, "kb_knowledge_base")
_SYS_ID = re.compile(r"[0-9a-fA-F]{32}")
_FIELD = re.compile(r"[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)*")
_COMMON_FIELDS = ("sys_id", "number", "short_description", "sys_created_on", "sys_updated_on")
_TICKET_FIELDS = ("description", "state", "priority", "impact", "urgency", "assignment_group", "assigned_to", "correlation_id")
_KNOWLEDGE_FIELDS = ("text", "kb_knowledge_base", "kb_category", "workflow_state", "article_type")
_MAX_PAGES = 1000


def instance_url(value: str | None) -> str:
    """Validate an HTTPS instance origin without echoing possibly embedded secrets."""
    try:
        parts = urlsplit(value or "")
        valid = (
            parts.scheme == "https" and parts.hostname and parts.port in (None, 443)
            and not parts.username and not parts.password
            and parts.path in ("", "/") and not parts.query and not parts.fragment
            and not re.search(r"[\s\\]", value or "")
        )
    except ValueError:
        valid = False
    if not valid:
        raise KnowledgeError("ServiceNow requires an HTTPS instance origin without credentials, a path, or a query.")
    return f"https://{parts.hostname.lower()}"


def validate_sys_id(value: str, label: str = "sys_id") -> str:
    """Validate a ServiceNow record identifier before using it in a URL or query."""
    if not isinstance(value, str) or not _SYS_ID.fullmatch(value):
        raise KnowledgeError(f"ServiceNow {label} must be a 32-character hexadecimal sys_id.")
    return value.lower()


def field_value(record: dict[str, Any], name: str, *, display: bool = False) -> str:
    """Read either a raw or display value from a Table API field."""
    value = record.get(name)
    if isinstance(value, dict):
        value = value.get("display_value" if display else "value", value.get("value"))
    return "" if value is None else str(value)


def encoded_query(value: str | None) -> str:
    """Validate query structure so appended scope filters cannot be bypassed."""
    query = (value or "").strip()
    if re.search(r"[\r\n]|javascript:|(?:^|\^)(?:NQ|EQ)(?:[^^]*)(?:\^|$)", query, re.IGNORECASE):
        raise KnowledgeError("ServiceNow queries cannot contain JavaScript, newlines, ^NQ, or ^EQ; register separate sources instead.")
    return query.strip("^")


def scope_query(
    table: str, query: str = "", *, knowledge_base: str | None = None,
    assignment_group: str | None = None, text: str | None = None,
) -> tuple[str, dict[str, str]]:
    """Compile a supported table query and exact reference-field scope checks."""
    if table not in READ_TABLES:
        raise KnowledgeError("Unsupported ServiceNow table.")
    clauses = [encoded_query(query)] if query else []
    scope: dict[str, str] = {}
    if knowledge_base:
        if table != "kb_knowledge":
            raise KnowledgeError("--knowledge-base applies only to kb_knowledge.")
        scope["kb_knowledge_base"] = validate_sys_id(knowledge_base, "knowledge base")
    if assignment_group:
        if table not in TICKET_TABLES:
            raise KnowledgeError("--assignment-group applies only to ticket tables.")
        scope["assignment_group"] = validate_sys_id(assignment_group, "assignment group")
    if text:
        if "^" in text or re.search(r"[\r\n]|javascript:", text, re.IGNORECASE):
            raise KnowledgeError("ServiceNow search text cannot contain query operators or JavaScript.")
        clauses.append(f"short_descriptionLIKE{text}")
    clauses.extend(f"{name}={value}" for name, value in scope.items())
    return "^".join(part for part in clauses if part), scope


def default_fields(table: str) -> list[str]:
    """Return a bounded field projection suitable for each supported table."""
    if table == "kb_knowledge_base":
        return ["sys_id", "title", "description", "active", "sys_updated_on"]
    return [*_COMMON_FIELDS, *(_KNOWLEDGE_FIELDS if table == "kb_knowledge" else _TICKET_FIELDS)]


def checked_fields(table: str, fields: list[str] | None, scope: dict[str, str]) -> list[str]:
    """Keep identity, title, timestamps, and scope fields in custom projections."""
    selected = fields if fields is not None else default_fields(table)
    if any(not isinstance(field, str) or not _FIELD.fullmatch(field) for field in selected):
        raise KnowledgeError("Invalid ServiceNow field name.")
    required = ("sys_id", "sys_updated_on") if table == "kb_knowledge_base" else _COMMON_FIELDS
    return list(dict.fromkeys([*required, *selected, *scope]))


def _check_record(record: Any, scope: dict[str, str] | None = None) -> dict[str, Any]:
    if not isinstance(record, dict):
        raise KnowledgeError("ServiceNow returned a malformed record.")
    validate_sys_id(field_value(record, "sys_id"))
    for name, expected in (scope or {}).items():
        if field_value(record, name).lower() != expected:
            raise KnowledgeError(f"ServiceNow returned a record outside the required {name} scope or hid that field.")
    return record


class _BearerAuth(requests.auth.AuthBase):
    """Set bearer authentication explicitly so netrc cannot replace it."""

    def __init__(self, token: str) -> None:
        self.token = token

    def __call__(self, request: requests.PreparedRequest) -> requests.PreparedRequest:
        request.headers["Authorization"] = f"Bearer {self.token}"
        return request


class ServiceNowClient:
    """Access explicitly selected ServiceNow tables with bounded GET retries."""

    def __init__(
        self, base_url: str, *, username: str | None = None,
        password: str | None = None, token: str | None = None,
    ) -> None:
        self.base_url = instance_url(base_url)
        if token and (username or password):
            raise KnowledgeError("Choose ServiceNow bearer authentication or username/password, not both.")
        if token:
            if re.search(r"[\r\n]", token):
                raise KnowledgeError("Invalid ServiceNow bearer credential.")
            self.auth = _BearerAuth(token)
        elif username and password:
            self.auth = requests.auth.HTTPBasicAuth(username, password)
        else:
            raise KnowledgeError("ServiceNow needs a bearer token or an instance username and password.")

    def record_url(self, table: str, sys_id: str) -> str:
        """Return the native instance URL for one supported record."""
        if table not in READ_TABLES:
            raise KnowledgeError("Unsupported ServiceNow table.")
        return f"{self.base_url}/{table}.do?sys_id={validate_sys_id(sys_id)}"

    def _request(
        self, method: str, table: str, *, sys_id: str | None = None,
        params: dict[str, Any] | None = None, data: dict[str, str] | None = None,
    ) -> tuple[Any, dict[str, str]]:
        if table not in READ_TABLES:
            raise KnowledgeError("Unsupported ServiceNow table.")
        path = f"/api/now/table/{table}"
        if sys_id:
            path += f"/{validate_sys_id(sys_id)}"
        attempts = 3 if method == "GET" else 1
        for attempt in range(attempts):
            try:
                response = requests.request(
                    method, self.base_url + path, auth=self.auth,
                    headers={"Accept": "application/json"}, params=params,
                    json=data, timeout=60, allow_redirects=False,
                )
            except requests.RequestException:
                suffix = " The creation outcome is unknown; read the instance before retrying." if method == "POST" else ""
                raise KnowledgeError(f"ServiceNow {method} failed at the transport layer.{suffix}") from None
            try:
                status = response.status_code
                headers = {key.lower(): value for key, value in response.headers.items()}
                if method == "GET" and status in {429, 502, 503, 504} and attempt + 1 < attempts:
                    try:
                        delay = min(5.0, max(0.0, float(headers.get("retry-after", 2 ** attempt))))
                    except ValueError:
                        delay = float(2 ** attempt)
                    time.sleep(delay)
                    continue
                expected = 201 if method == "POST" else 200
                if status != expected:
                    if 300 <= status < 400:
                        reason = "Redirect refused; use the instance origin and API credentials, not an SSO page."
                    elif status in {401, 403}:
                        reason = "Check instance credentials, table/field ACLs, and API access policies."
                    elif status == 404:
                        reason = "The table or record is unavailable to this account."
                    else:
                        reason = "Check the instance and request; response bodies are not logged."
                    if method == "POST" and status >= 500:
                        reason += " Creation may have succeeded; inspect the instance before retrying."
                    raise KnowledgeError(f"ServiceNow {method} failed (HTTP {status}). {reason}")
                try:
                    payload = response.json()
                except ValueError:
                    if method == "POST":
                        raise KnowledgeError(
                            "ServiceNow accepted the creation but returned invalid JSON. "
                            "Inspect the instance before retrying; do not repeat creation."
                        ) from None
                    raise KnowledgeError(f"ServiceNow {method} returned invalid JSON; no request was replayed.") from None
                if not isinstance(payload, dict) or "result" not in payload:
                    if method == "POST":
                        raise KnowledgeError(
                            "ServiceNow accepted the creation but returned no result envelope. "
                            "Inspect the instance before retrying; do not repeat creation."
                        )
                    raise KnowledgeError(f"ServiceNow {method} response is missing result; no request was replayed.")
                return payload["result"], headers
            finally:
                response.close()
        raise KnowledgeError("ServiceNow request attempts exhausted.")

    def list_records(
        self, table: str, *, query: str = "", fields: list[str] | None = None,
        scope: dict[str, str] | None = None, limit: int = 1000, page_size: int = 100,
        offset: int = 0,
    ) -> dict[str, Any]:
        """Read bounded pages without following URLs supplied in pagination headers."""
        if table not in READ_TABLES:
            raise KnowledgeError("Unsupported ServiceNow table.")
        if limit < 1 or not 1 <= page_size <= 100 or offset < 0:
            raise KnowledgeError("ServiceNow limit must be positive, page size 1-100, and offset non-negative.")
        query = encoded_query(query)
        query = f"{query}^ORDERBYsys_id" if query else "ORDERBYsys_id"
        scope = scope or {}
        projection = checked_fields(table, fields, scope)
        records: list[dict[str, Any]] = []
        seen: set[str] = set()
        start = offset
        more = False
        for _ in range(_MAX_PAGES):
            size = min(page_size, limit - len(records))
            result, headers = self._request("GET", table, params={
                "sysparm_query": query, "sysparm_limit": size, "sysparm_offset": offset,
                "sysparm_fields": ",".join(projection), "sysparm_display_value": "all",
                "sysparm_exclude_reference_link": "true",
            })
            if not isinstance(result, list) or len(result) > size:
                raise KnowledgeError("ServiceNow returned a malformed or oversized result page.")
            for record in result:
                _check_record(record, scope)
                sys_id = field_value(record, "sys_id").lower()
                if sys_id in seen:
                    raise KnowledgeError("ServiceNow repeated a record across pages; synchronization was not published.")
                seen.add(sys_id)
                records.append(record)
            offset += size  # ServiceNow applies the limit before record ACL filtering.
            if "link" in headers:
                more = any(link.get("rel") == "next" for link in requests.utils.parse_header_links(headers["link"]))
            elif "x-total-count" in headers:
                try:
                    more = offset < int(headers["x-total-count"])
                except ValueError:
                    raise KnowledgeError("ServiceNow returned an invalid pagination count.") from None
            else:
                more = len(result) == size
            if not more or len(records) >= limit:
                break
        else:
            raise KnowledgeError("ServiceNow pagination exceeded the safety limit; narrow the query.")
        return {
            "table": table, "query": query, "records": records, "offset": start,
            "next_offset": offset if more else None, "truncated": more,
        }

    def read_record(self, table: str, identifier: str) -> dict[str, Any]:
        """Read a ticket/article by exact sys_id or record number."""
        if _SYS_ID.fullmatch(identifier):
            result, _ = self._request("GET", table, sys_id=identifier, params={
                "sysparm_display_value": "all", "sysparm_exclude_reference_link": "true",
                "sysparm_fields": ",".join(default_fields(table)),
            })
            record = _check_record(result)
            if field_value(record, "sys_id").lower() != identifier.lower():
                raise KnowledgeError("ServiceNow returned a different record than requested.")
            return record
        if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]*[0-9]", identifier):
            raise KnowledgeError("Use an exact ServiceNow record number or hexadecimal sys_id.")
        page = self.list_records(table, query=f"number={identifier}", limit=2, page_size=2)
        records = page["records"]
        if len(records) != 1 or field_value(records[0], "number") != identifier:
            raise KnowledgeError("ServiceNow record number was not found or was not unique.")
        return records[0]

    def create_ticket(self, fields: dict[str, str]) -> dict[str, Any]:
        """Create one incident once, then verify its identity with a separate GET."""
        if not fields.get("short_description", "").strip():
            raise KnowledgeError("A non-empty ticket short description is required.")
        allowed = {
            "short_description", "description", "caller_id", "assignment_group",
            "impact", "urgency", "correlation_id",
        }
        if set(fields) - allowed or any(not isinstance(value, str) for value in fields.values()):
            raise KnowledgeError("Unsupported ServiceNow ticket fields.")
        for name in ("caller_id", "assignment_group"):
            if fields.get(name):
                validate_sys_id(fields[name], name)
        for name in ("impact", "urgency"):
            if name in fields and fields[name] not in {"1", "2", "3"}:
                raise KnowledgeError(f"ServiceNow {name} must be 1, 2, or 3.")
        result, _ = self._request("POST", "incident", params={
            "sysparm_display_value": "all", "sysparm_exclude_reference_link": "true",
        }, data=fields)
        try:
            record = _check_record(result)
        except KnowledgeError:
            raise KnowledgeError("ServiceNow accepted the creation but returned no valid identity. Inspect the instance before retrying.") from None
        sys_id = field_value(record, "sys_id")
        try:
            verified = self.read_record("incident", sys_id)
        except KnowledgeError as exc:
            raise KnowledgeError(f"ServiceNow created incident {sys_id}, but read-back failed: {exc} Do not repeat creation.") from None
        return {
            "created": True, "verified": True, "sys_id": sys_id,
            "number": field_value(verified, "number"),
            "url": self.record_url("incident", sys_id), "record": verified,
        }


def client_from_config(config: dict[str, Any], store: KnowledgeStore) -> ServiceNowClient:
    """Resolve credentials in memory, never embedding their values in source metadata."""
    credentials = {
        name: store.resolve_key(config[name]) if config.get(name) else None
        for name in ("username", "password", "token")
    }
    return ServiceNowClient(config.get("base_url"), **credentials)


class _ArticleText(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.hidden = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style"}:
            self.hidden += 1
        elif not self.hidden and tag in {"p", "div", "br", "li", "tr", "h1", "h2", "h3", "h4", "pre"}:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style"}:
            self.hidden = max(0, self.hidden - 1)
        elif not self.hidden and tag in {"p", "div", "li", "tr", "h1", "h2", "h3", "h4", "pre"}:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if not self.hidden:
            self.parts.append(data)


def record_markdown(record: dict[str, Any], table: str, url: str) -> str:
    """Render ticket fields or normalized article text with its source URL."""
    title = field_value(record, "short_description") or field_value(record, "title") or field_value(record, "sys_id")
    number = field_value(record, "number")
    lines = [f"# {number + ': ' if number else ''}{title}", "", f"- Source: {url}"]
    for name in ("state", "workflow_state", "priority", "assignment_group", "kb_knowledge_base"):
        value = field_value(record, name, display=True)
        if value:
            lines.append(f"- {name.replace('_', ' ').title()}: {value}")
    description = field_value(record, "description")
    if description:
        lines.extend(["", "## Description", "", description])
    if table == "kb_knowledge":
        parser = _ArticleText()
        parser.feed(field_value(record, "text"))
        body = "\n".join(line.strip() for line in "".join(parser.parts).splitlines() if line.strip())
        lines.extend(["", "## Article", "", body])
    fence = chr(96) * 3
    lines.extend(["", "## Source Data", "", fence + "json", json.dumps(record, indent=2, sort_keys=True), fence])
    return "\n".join(lines).rstrip()


def _record_timestamp(record: dict[str, Any]) -> str | None:
    value = field_value(record, "sys_updated_on")
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc).isoformat()
    except ValueError:
        raise KnowledgeError("ServiceNow returned an invalid raw sys_updated_on timestamp.") from None


class ServiceNowSource(SourceAdapter):
    """Upsert scoped records as OKF Markdown while retaining unreturned local records."""

    def sync(self) -> dict[str, Any]:
        """Fetch and render all selected pages before publishing any record files."""
        client = client_from_config(self.config, self.store)
        table = self.config.get("table", "incident")
        if table not in SYNC_TABLES:
            raise KnowledgeError("This ServiceNow table is not a synchronization source.")
        query, scope = scope_query(
            table, self.config.get("query", ""), knowledge_base=self.config.get("knowledge_base"),
            assignment_group=self.config.get("assignment_group"),
        )
        page = client.list_records(
            table, query=query, scope=scope, fields=self.config.get("fields"),
            limit=self.config.get("limit", 1000), page_size=self.config.get("page_size", 100),
        )
        documents: dict[str, str] = {}
        for record in page["records"]:
            sys_id = validate_sys_id(field_value(record, "sys_id"))
            url = client.record_url(table, sys_id)
            title = field_value(record, "short_description") or field_value(record, "number") or sys_id
            frontmatter = {
                "type": "ServiceNow Knowledge Article" if table == "kb_knowledge" else "ServiceNow Ticket",
                "title": title, "knowledge_key": self.source["key"], "source_id": self.source["id"],
                "source_type": "servicenow", "table": table, "sys_id": sys_id,
                "number": field_value(record, "number"), "source_url": url,
                "updated_at": _record_timestamp(record),
                "status": field_value(record, "workflow_state" if table == "kb_knowledge" else "state", display=True),
            }
            documents[f"{sys_id}.md"] = render_okf_markdown(
                frontmatter, record_markdown(record, table, url), source=self.source, fallback_title=title,
            )
        records_dir = self.raw_dir / "records"
        if records_dir.is_symlink():
            raise KnowledgeError("ServiceNow records directory must not be a symbolic link.")
        records_dir.mkdir(exist_ok=True)
        existing = {path.name for path in records_dir.glob("*.md")}
        changed = 0
        with tempfile.TemporaryDirectory(prefix=".servicenow-", dir=self.raw_dir) as staging:
            staged = Path(staging)
            for name, document in documents.items():
                target = records_dir / name
                if target.is_symlink():
                    raise KnowledgeError("ServiceNow record files must not be symbolic links.")
                if not target.exists() or target.read_text(encoding="utf-8") != document:
                    (staged / name).write_text(document, encoding="utf-8")
            for path in staged.iterdir():
                path.replace(records_dir / path.name)
                changed += 1
        return self.finalize_sync({
            "table": table, "query": query, "records": len(documents), "documents": len(documents),
            "changed": changed, "retained": len(existing - documents.keys()),
            "truncated": page["truncated"], "next_offset": page["next_offset"],
            "mode": "upsert", "library_dir": str(self.raw_dir),
        })
