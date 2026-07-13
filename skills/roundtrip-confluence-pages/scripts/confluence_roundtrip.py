#!/usr/bin/env python3
"""Losslessly download, edit, upload, and verify Confluence Cloud pages."""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
from html import unescape
from html.parser import HTMLParser
import json
import mimetypes
import os
from pathlib import Path
import re
import shutil
import struct
import sys
import tempfile
import time
from typing import Any, Callable
from urllib.parse import quote, unquote, urljoin, urlparse
from uuid import uuid4
from xml.etree import ElementTree
import zlib

import requests


SCHEMA_VERSION = "1.0"
MANIFEST_NAME = "manifest.json"
META_NAME = "page.meta.json"
STORAGE_NAME = "page.storage.xml"
ADF_NAME = "page.adf.json"
VIEW_NAME = "page.view.html"
LABELS_NAME = "page.labels.json"
STATE_NAME = "page.content-state.json"
RESTRICTIONS_NAME = "page.restrictions.json"
PROPERTIES_NAME = "page.properties.json"
OPERATIONS_NAME = "page.operations.json"
GT_NAME = "ground-truth.json"
ATTACHMENTS_DIR = "attachments"
VERIFY_DIR = "verification"
REPORT_NAME = "report.json"
BROWSER_GT_NAME = "browser-ground-truth.json"
JOURNAL_NAME = "mutation-journal.json"
OPERATION_LOCK_NAME = "active-operation.lock"
REMOTE_STORAGE_NAME = "remote.storage.xml"
REMOTE_ADF_NAME = "remote.adf.json"
REMOTE_VIEW_NAME = "remote.view.html"
REMOTE_RESTRICTIONS_NAME = "remote.restrictions.json"
REMOTE_PROPERTIES_NAME = "remote.properties.json"
REMOTE_OPERATIONS_NAME = "remote.operations.json"
RENDER_SAFETY_RECONCILIATION_NAME = "render-safety-reconciliation.json"
ENV_KEYS = {
    "base_url": ("CONFLUENCE_BASE_URL", "ATLASSIAN_BASE_URL"),
    "username": ("CONFLUENCE_USERNAME", "ATLASSIAN_USERNAME"),
    "token": ("CONFLUENCE_TOKEN", "ATLASSIAN_API_TOKEN"),
}
AC_NS = "urn:confluence:ac"
RI_NS = "urn:confluence:ri"
TRANSIENT_GET_STATUSES = frozenset({429, 502, 503, 504})
MAX_RETRY_AFTER_SECONDS = 30.0
MAX_GET_RETRY_ATTEMPTS = 5
MAX_SCREENSHOT_PIXELS = 100_000_000
MAX_SCREENSHOT_DECODED_BYTES = 256 * 1024 * 1024
ASYNC_RENDER_MAX_POLLS = 40
ASYNC_RENDER_POLL_SECONDS = 0.5
ASYNC_RENDER_TIMEOUT_SECONDS = 30.0


class RoundTripError(RuntimeError):
    """Base class for safe, user-facing round-trip failures."""


class ConflictError(RoundTripError):
    """Raised when the remote page changed after it was downloaded."""


class ValidationError(RoundTripError):
    """Raised when a workspace would not produce a safe page update."""


class RemoteRenderPreflightError(RoundTripError):
    """Raised when server-rendered candidate storage is visibly unsafe."""

    def __init__(self, message: str, diagnostic: dict[str, Any]) -> None:
        super().__init__(message)
        self.diagnostic = diagnostic


def validate_page_id(page_id: Any) -> str:
    """Return a canonical positive numeric Confluence page ID."""

    value = str(page_id)
    if not re.fullmatch(r"[1-9][0-9]*", value):
        raise ValidationError("Confluence page ID must be a positive numeric ID")
    return value


def _resolve_workspace_root(workspace: Path) -> Path:
    """Resolve a workspace path without following a symlink at its root."""

    candidate = workspace if workspace.is_absolute() else Path.cwd() / workspace
    if _is_link_like(candidate):
        raise ValidationError(
            f"workspace root must not be a symbolic link or junction: {candidate}"
        )
    return candidate.resolve()


def _is_link_like(path: Path) -> bool:
    """Return whether a path redirects through a symlink or Windows junction."""

    if path.is_symlink():
        return True
    is_junction = getattr(path, "is_junction", None)
    return bool(is_junction and is_junction())


def _reject_symlink(path: Path, description: str) -> None:
    """Reject a filesystem entry that could redirect a workspace read."""

    if _is_link_like(path):
        raise ValidationError(
            f"{description} must not be a symbolic link or junction: {path}"
        )


def _verification_dir(workspace: Path, *, create: bool = False) -> Path:
    """Return the contained verification directory without following redirects."""

    workspace = _resolve_workspace_root(workspace)
    candidate = workspace / VERIFY_DIR
    _reject_symlink(candidate, "workspace verification directory")
    resolved = candidate.resolve()
    if resolved != candidate:
        raise ValidationError(
            f"workspace verification directory must stay inside the workspace: {candidate}"
        )
    if candidate.exists() and not candidate.is_dir():
        raise ValidationError(
            f"workspace verification path must be a directory: {candidate}"
        )
    if create:
        candidate.mkdir(exist_ok=True)
    return candidate


def _acquire_operation_lock(workspace: Path, operation_id: str) -> Path:
    """Atomically prevent two local processes from mutating one workspace."""

    path = _verification_dir(workspace, create=True) / OPERATION_LOCK_NAME
    try:
        descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise ConflictError(
            "another operation is already active for this workspace; inspect "
            f"{path} and the mutation journal before retrying"
        ) from exc
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(
                {"operation_id": operation_id, "pid": os.getpid(), "started_at": utc_now()},
                handle,
                sort_keys=True,
            )
            handle.write("\n")
    except BaseException:
        try:
            path.unlink()
        except FileNotFoundError:
            pass
        raise
    return path


def _release_operation_lock(workspace: Path, operation_id: str) -> None:
    """Release this operation's lock without deleting another process's lock."""

    path = _verification_dir(workspace) / OPERATION_LOCK_NAME
    if not path.exists():
        return
    _reject_symlink(path, "workspace operation lock")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValidationError(f"cannot validate workspace operation lock: {path}") from exc
    if not isinstance(payload, dict) or payload.get("operation_id") != operation_id:
        raise ConflictError("workspace operation lock belongs to a different operation")
    path.unlink()


def _attachment_files(workspace: Path) -> list[Path]:
    """Return regular attachment files after rejecting symlink redirection."""

    attachment_dir = workspace / ATTACHMENTS_DIR
    _reject_symlink(attachment_dir, "workspace attachments directory")
    if not attachment_dir.is_dir():
        raise ValidationError(f"workspace is missing required directory: {ATTACHMENTS_DIR}")
    entries = sorted(attachment_dir.iterdir())
    for path in entries:
        _reject_symlink(path, f"attachment entry {path.name!r}")
    return [path for path in entries if path.is_file()]


class _VisibleTextParser(HTMLParser):
    """Collect visible-ish text without external HTML dependencies."""

    HIDDEN_TAGS = frozenset({"script", "style", "template", "noscript"})
    ENCODED_HTML_CLASS = "html-viewer-unsafe-html-content"

    def __init__(self, *, decode_html_viewer_fragment: bool = True) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.hidden_depth = 0
        self.decode_html_viewer_fragment = decode_html_viewer_fragment
        self.encoded_fragment_depth = 0
        self.encoded_fragment_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        classes = {
            token
            for name, value in attrs
            if name == "class" and value
            for token in value.split()
        }
        if (
            self.decode_html_viewer_fragment
            and not self.encoded_fragment_depth
            and not self.hidden_depth
            and self.ENCODED_HTML_CLASS in classes
        ):
            self.encoded_fragment_depth = 1
            self.encoded_fragment_parts = []
            return
        if self.encoded_fragment_depth:
            self.encoded_fragment_depth += 1
            return
        if tag in self.HIDDEN_TAGS:
            self.hidden_depth += 1
        elif tag in {"p", "div", "li", "br", "h1", "h2", "h3", "h4", "h5", "h6"}:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if self.encoded_fragment_depth:
            self.encoded_fragment_depth -= 1
            if not self.encoded_fragment_depth:
                fragment = "".join(self.encoded_fragment_parts)
                parser = _VisibleTextParser(decode_html_viewer_fragment=False)
                parser.feed(fragment)
                parser.close()
                self.parts.append(parser.text())
                self.encoded_fragment_parts = []
            return
        if tag in self.HIDDEN_TAGS:
            self.hidden_depth = max(0, self.hidden_depth - 1)
        elif tag in {"p", "div", "li", "h1", "h2", "h3", "h4", "h5", "h6"}:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if self.encoded_fragment_depth:
            self.encoded_fragment_parts.append(data)
        elif not self.hidden_depth:
            self.parts.append(data)

    def text(self) -> str:
        return re.sub(r"\s+", " ", " ".join(self.parts)).strip()


class _RenderedViewSafetyParser(HTMLParser):
    """Detect Confluence's structural unknown-macro placeholder signals."""

    URL_ATTRIBUTES = frozenset(
        {"src", "href", "action", "poster", "data-src", "data-url"}
    )

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.unknown_macro_placeholders = 0
        self.signals_found: set[str] = set()

    def handle_starttag(
        self,
        _tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        signals: set[str] = set()
        for raw_name, raw_value in attrs:
            name = str(raw_name or "").casefold()
            value = str(raw_value or "")
            if name == "class" and "wysiwyg-unknown-macro" in {
                token.casefold() for token in value.split()
            }:
                signals.add("class-token")
            if name in self.URL_ATTRIBUTES:
                path_segments = [
                    segment.casefold()
                    for segment in unquote(urlparse(value).path).split("/")
                    if segment
                ]
                if any(
                    path_segments[index : index + 2]
                    == ["placeholder", "unknown-macro"]
                    for index in range(max(0, len(path_segments) - 1))
                ):
                    signals.add("placeholder-path")
        if signals:
            self.unknown_macro_placeholders += 1
            self.signals_found.update(signals)

    def handle_startendtag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        self.handle_starttag(tag, attrs)


def utc_now() -> str:
    """Return a stable UTC timestamp."""

    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256_bytes(payload: bytes) -> str:
    """Return the lowercase SHA-256 digest of bytes."""

    return sha256(payload).hexdigest()


def sha256_text(payload: str) -> str:
    """Return the UTF-8 SHA-256 digest of text."""

    return sha256_bytes(payload.encode("utf-8"))


def canonical_json_bytes(payload: Any) -> bytes:
    """Serialize JSON deterministically for integrity bindings."""

    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def sha256_json(payload: Any) -> str:
    """Return a stable SHA-256 digest for a JSON-compatible value."""

    return sha256_bytes(canonical_json_bytes(payload))


def parse_utc_timestamp(value: Any, field: str) -> datetime:
    """Parse a timezone-aware ISO timestamp used by verification evidence."""

    if not isinstance(value, str) or not value:
        raise ValidationError(f"{field} must be a non-empty ISO timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValidationError(f"{field} must be a valid ISO timestamp") from exc
    if parsed.tzinfo is None:
        raise ValidationError(f"{field} must include a timezone")
    return parsed.astimezone(timezone.utc)


def load_json(path: Path) -> Any:
    """Read UTF-8 JSON from ``path``."""

    _reject_symlink(path, "JSON sidecar")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValidationError(f"cannot read valid JSON from {path}: {exc}") from exc


def write_json(path: Path, payload: Any) -> None:
    """Atomically write deterministic UTF-8 JSON."""

    text = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    write_text(path, text)


def write_cli_result(path: Path, payload: Any) -> None:
    """Atomically write a CLI result without following an output-file symlink."""

    candidate = path if path.is_absolute() else Path.cwd() / path
    _reject_symlink(candidate, "CLI output")
    resolved = candidate.parent.resolve() / candidate.name
    _reject_symlink(resolved, "CLI output")
    if resolved.exists() and not resolved.is_file():
        raise ValidationError(f"CLI output exists and is not a file: {resolved}")
    write_json(resolved, payload)


def validate_upload_output_path(workspace: Path, path: Path) -> Path:
    """Return a safe JSON receipt path that cannot replace workspace state."""

    workspace = _resolve_workspace_root(workspace)
    candidate = path if path.is_absolute() else Path.cwd() / path
    _reject_symlink(candidate, "upload CLI output")
    resolved = candidate.parent.resolve() / candidate.name
    if resolved.suffix.casefold() != ".json":
        raise ValidationError("upload --output must name a JSON file")
    try:
        relative = resolved.relative_to(workspace)
    except ValueError:
        return resolved
    if (
        not relative.parts
        or relative.parts[0].casefold() != VERIFY_DIR.casefold()
    ):
        raise ValidationError(
            "upload --output inside a page workspace must stay under verification/"
        )
    reserved = {
        REPORT_NAME,
        BROWSER_GT_NAME,
        JOURNAL_NAME,
        OPERATION_LOCK_NAME,
        REMOTE_STORAGE_NAME,
        REMOTE_ADF_NAME,
        REMOTE_VIEW_NAME,
        REMOTE_RESTRICTIONS_NAME,
        REMOTE_PROPERTIES_NAME,
        REMOTE_OPERATIONS_NAME,
        RENDER_SAFETY_RECONCILIATION_NAME,
    }
    if len(relative.parts) == 2 and relative.name.casefold() in {
        name.casefold() for name in reserved
    }:
        raise ValidationError(
            f"upload --output cannot replace reserved verification evidence: {relative.name}"
        )
    return resolved


def write_upload_cli_result(workspace: Path, path: Path, payload: Any) -> None:
    """Write one upload result after enforcing workspace output isolation."""

    write_cli_result(validate_upload_output_path(workspace, path), payload)


def _replace_with_retry(source: str, destination: Path) -> None:
    """Retry transient sharing violations during atomic replacement."""

    for attempt in range(5):
        try:
            os.replace(source, destination)
            return
        except PermissionError:
            if attempt == 4:
                raise
            time.sleep(0.02 * (attempt + 1))


def write_text(path: Path, payload: str) -> None:
    """Atomically write UTF-8 text."""

    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(payload)
        _replace_with_retry(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def write_bytes(path: Path, payload: bytes) -> None:
    """Atomically write bytes."""

    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(payload)
        _replace_with_retry(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def load_dotenv(path: Path, *, override: bool = False) -> None:
    """Load simple dotenv assignments, optionally overriding process values."""

    if not path.is_file():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", key):
            continue
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]
        if override or key not in os.environ:
            os.environ[key] = value


def first_env(names: tuple[str, ...]) -> str | None:
    """Return the first non-empty environment value from ``names``."""

    for name in names:
        value = os.environ.get(name)
        if value:
            return value
    return None


def normalize_base_url(value: str) -> str:
    """Normalize and validate an Atlassian Cloud base URL."""

    raw = value.strip()
    parsed = urlparse(raw)
    if parsed.scheme.lower() != "https" or not parsed.netloc or not parsed.hostname:
        raise ValidationError("Confluence base URL must be an absolute HTTPS URL")
    if parsed.username is not None or parsed.password is not None:
        raise ValidationError("Confluence base URL must not contain credentials")
    try:
        port = parsed.port
    except ValueError as exc:
        raise ValidationError("Confluence base URL has an invalid port") from exc
    if port not in {None, 443}:
        raise ValidationError("Confluence base URL must use the default HTTPS port")
    if parsed.params or parsed.query or parsed.fragment:
        raise ValidationError("Confluence base URL must not contain parameters, a query, or a fragment")
    path = parsed.path.rstrip("/")
    if path == "/wiki":
        path = ""
    if path:
        raise ValidationError("Confluence base URL must identify the site root, without /wiki")
    hostname = parsed.hostname.lower()
    return f"https://{hostname}"


def _https_origin(value: str) -> tuple[str, int]:
    """Return a normalized HTTPS origin or reject an unsafe absolute URL."""

    parsed = urlparse(value)
    if parsed.scheme.lower() != "https" or not parsed.netloc or not parsed.hostname:
        raise ValidationError("absolute Confluence URLs must use HTTPS")
    if parsed.username is not None or parsed.password is not None:
        raise ValidationError("absolute Confluence URLs must not contain credentials")
    try:
        port = parsed.port
    except ValueError as exc:
        raise ValidationError("absolute Confluence URL has an invalid port") from exc
    return parsed.hostname.lower(), port or 443


def credentials_from_args(args: argparse.Namespace) -> tuple[str, str, str]:
    """Resolve credentials without logging secret values."""

    implicit_env_file = args.env_file is None
    preexisting_base_url = args.base_url or first_env(ENV_KEYS["base_url"])
    preexisting_token = first_env(ENV_KEYS["token"])
    load_dotenv(
        args.env_file.resolve() if args.env_file else Path.cwd() / ".env",
        override=bool(args.env_file),
    )
    base_url = args.base_url or first_env(ENV_KEYS["base_url"])
    username = args.username or first_env(ENV_KEYS["username"])
    token = first_env(ENV_KEYS["token"])
    if (
        implicit_env_file
        and not preexisting_base_url
        and base_url
        and preexisting_token
    ):
        raise ValidationError(
            "refusing to combine a Confluence base URL from an implicit working-directory "
            ".env with a pre-existing API token; pass --base-url or --env-file explicitly"
        )
    missing = [
        name
        for name, value in (("base URL", base_url), ("username", username), ("API token", token))
        if not value
    ]
    if missing:
        raise ValidationError("missing Confluence " + ", ".join(missing))
    return normalize_base_url(str(base_url)), str(username), str(token)


def _get_retry_delay(response: requests.Response, attempt: int) -> float:
    """Return a short bounded delay, honoring a safe numeric Retry-After value."""

    retry_after = str(response.headers.get("Retry-After", "")).strip()
    if re.fullmatch(r"[0-9]+(?:\.[0-9]+)?", retry_after):
        seconds = float(retry_after)
        if seconds <= MAX_RETRY_AFTER_SECONDS:
            return seconds
    return min(MAX_RETRY_AFTER_SECONDS, 0.25 * (2**attempt))


class ConfluenceClient:
    """Small authenticated Confluence Cloud REST client."""

    def __init__(
        self,
        base_url: str,
        username: str,
        token: str,
        *,
        timeout: int = 60,
        get_retry_attempts: int = 3,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self.base_url = normalize_base_url(base_url)
        self.timeout = timeout
        if not 1 <= get_retry_attempts <= MAX_GET_RETRY_ATTEMPTS:
            raise ValidationError(
                f"GET retry attempts must be between one and {MAX_GET_RETRY_ATTEMPTS}"
            )
        self.get_retry_attempts = get_retry_attempts
        self._sleep = sleep
        self.session = requests.Session()
        self.session.auth = (username, token)
        self.session.headers.update({"Accept": "application/json"})

    def url(self, path: str) -> str:
        """Resolve an API or download path against the site root."""

        if not isinstance(path, str) or not path or path != path.strip():
            raise ValidationError("Confluence request path must be a non-empty URL without surrounding whitespace")
        if "\\" in path or any(ord(character) < 32 for character in path):
            raise ValidationError("Confluence request path contains unsafe characters")
        parsed = urlparse(path)
        if parsed.scheme or parsed.netloc:
            if parsed.scheme.lower() != "https" or not parsed.netloc:
                raise ValidationError("absolute Confluence URLs must use HTTPS")
            resolved = path
        else:
            resolved = urljoin(self.base_url.rstrip("/") + "/", path.lstrip("/"))
        if _https_origin(resolved) != _https_origin(self.base_url):
            raise ValidationError("refusing to send credentials to a different origin")
        return resolved

    def request(
        self,
        method: str,
        path: str,
        *,
        expected: tuple[int, ...] = (200,),
        redact_path: bool = False,
        **kwargs: Any,
    ) -> requests.Response:
        """Send a request, retrying only bounded transient read-only GET failures."""

        kwargs.setdefault("timeout", self.timeout)
        method = method.upper()
        url = self.url(path)
        attempts = self.get_retry_attempts if method == "GET" else 1
        for attempt in range(attempts):
            try:
                response = self.session.request(method, url, **kwargs)
            except requests.RequestException:
                if redact_path:
                    raise RoundTripError(
                        "Confluence async conversion request failed before a response"
                    ) from None
                raise
            if response.status_code in expected:
                return response
            if (
                method == "GET"
                and response.status_code in TRANSIENT_GET_STATUSES
                and attempt + 1 < attempts
            ):
                self._sleep(_get_retry_delay(response, attempt))
                continue
            if redact_path:
                raise RoundTripError(
                    "Confluence async conversion request returned "
                    f"HTTP {response.status_code}"
                )
            message = _response_message(response)
            raise RoundTripError(
                f"Confluence {method} {urlparse(response.url).path} returned "
                f"HTTP {response.status_code}: {message}"
            )
        raise AssertionError("request retry loop exhausted without returning or raising")

    def json(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        """Return an object JSON response."""

        response = self.request(method, path, **kwargs)
        try:
            payload = response.json()
        except ValueError as exc:
            raise RoundTripError("Confluence returned invalid JSON") from exc
        if not isinstance(payload, dict):
            raise RoundTripError("Confluence returned a non-object JSON response")
        return payload

    def doctor(self) -> dict[str, Any]:
        """Check authenticated access without mutating the site."""

        payload = self.json("GET", "/wiki/api/v2/spaces", params={"limit": 1})
        return {
            "authenticated": True,
            "site": urlparse(self.base_url).netloc,
            "visible_space_sample_count": len(payload.get("results", [])),
        }

    def page(self, page_id: str, representation: str = "storage") -> dict[str, Any]:
        """Fetch one page in a requested primary body representation."""

        page_id = validate_page_id(page_id)
        params: dict[str, Any] = {
            "body-format": representation,
            "include-labels": "true",
            "include-properties": "true",
            "include-operations": "true",
            "include-version": "true",
        }
        return self.json("GET", f"/wiki/api/v2/pages/{quote(page_id)}", params=params)

    def draft_page(self, page_id: str) -> dict[str, Any]:
        """Fetch the page's draft-aware storage snapshot."""

        page_id = validate_page_id(page_id)
        return self.json(
            "GET",
            f"/wiki/api/v2/pages/{quote(page_id)}",
            params={
                "body-format": "storage",
                "get-draft": "true",
                "include-version": "true",
            },
        )

    def attachments(self, page_id: str) -> list[dict[str, Any]]:
        """List all attachments for a page."""

        page_id = validate_page_id(page_id)
        path: str | None = f"/wiki/api/v2/pages/{quote(page_id)}/attachments"
        params: dict[str, Any] | None = {"limit": 250}
        results: list[dict[str, Any]] = []
        seen_urls: set[str] = set()
        while path:
            page_url = self.url(path)
            if page_url in seen_urls:
                raise RoundTripError("Confluence attachment pagination repeated a page URL")
            seen_urls.add(page_url)
            payload = self.json("GET", path, params=params)
            results.extend(item for item in payload.get("results", []) if isinstance(item, dict))
            next_path = (payload.get("_links") or {}).get("next")
            path = str(next_path) if next_path else None
            params = None
        return results

    def labels(self, page_id: str) -> list[str]:
        """List all global labels for a page."""

        page_id = validate_page_id(page_id)
        path: str | None = f"/wiki/api/v2/pages/{quote(page_id)}/labels"
        params: dict[str, Any] | None = {"limit": 250}
        labels: set[str] = set()
        seen_urls: set[str] = set()
        while path:
            page_url = self.url(path)
            if page_url in seen_urls:
                raise RoundTripError("Confluence label pagination repeated a page URL")
            seen_urls.add(page_url)
            payload = self.json("GET", path, params=params)
            for item in payload.get("results", []):
                if (
                    isinstance(item, dict)
                    and item.get("name")
                    and item.get("prefix", "global") == "global"
                ):
                    labels.add(str(item["name"]))
            next_path = (payload.get("_links") or {}).get("next")
            path = str(next_path) if next_path else None
            params = None
        return sorted(labels)

    def download_attachment(self, attachment: dict[str, Any]) -> bytes:
        """Download one attachment through its authenticated Confluence link."""

        link = attachment.get("downloadLink") or (attachment.get("_links") or {}).get("download")
        if not link:
            raise RoundTripError(f"attachment {attachment.get('title', '<unknown>')} has no download link")
        download_path = str(link)
        parsed = urlparse(download_path)
        if not parsed.scheme and not parsed.netloc and download_path.startswith(("/rest/", "/download/")):
            # Attachment v2 responses can omit Confluence Cloud's `/wiki` context path.
            download_path = "/wiki" + download_path
        response = self.request("GET", download_path, expected=(200,), headers={"Accept": "*/*"})
        return response.content

    def preflight_storage_render(
        self,
        page_id: str,
        storage: str,
        *,
        max_polls: int = ASYNC_RENDER_MAX_POLLS,
        poll_interval: float = ASYNC_RENDER_POLL_SECONDS,
        timeout_seconds: float = ASYNC_RENDER_TIMEOUT_SECONDS,
    ) -> dict[str, Any]:
        """Require Confluence to render candidate storage before a page-body PUT."""

        page_id = validate_page_id(page_id)
        if not isinstance(storage, str):
            raise ValidationError("remote render preflight requires storage XML text")
        if (
            not isinstance(max_polls, int)
            or isinstance(max_polls, bool)
            or not 1 <= max_polls <= 100
        ):
            raise ValidationError("remote render preflight max_polls must be between 1 and 100")
        if not 0 <= poll_interval <= 5:
            raise ValidationError("remote render preflight poll_interval must be between 0 and 5 seconds")
        if not 1 <= timeout_seconds <= 120:
            raise ValidationError("remote render preflight timeout must be between 1 and 120 seconds")

        deadline = time.monotonic() + timeout_seconds
        response = self.request(
            "POST",
            "/wiki/rest/api/contentbody/convert/async/view",
            expected=(200,),
            redact_path=True,
            timeout=max(0.1, min(float(self.timeout), timeout_seconds)),
            params={"contentIdContext": page_id, "allowCache": "false"},
            json={"value": storage, "representation": "storage"},
        )
        try:
            queued = response.json()
        except ValueError as exc:
            raise RoundTripError("Confluence remote render preflight returned invalid JSON") from exc
        if isinstance(queued, dict) and queued.get("error"):
            raise RoundTripError("Confluence remote render preflight failed to queue")
        async_id = queued.get("asyncId") if isinstance(queued, dict) else None
        if (
            not isinstance(async_id, str)
            or not async_id.strip()
            or len(async_id) > 4096
            or any(ord(character) < 32 or ord(character) == 127 for character in async_id)
        ):
            raise RoundTripError(
                "Confluence remote render preflight did not return a usable task identifier"
            )
        async_id = async_id.strip()

        for poll_number in range(1, max_polls + 1):
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                break
            response = self.request(
                "GET",
                f"/wiki/rest/api/contentbody/convert/async/{quote(async_id, safe='')}",
                expected=(200,),
                redact_path=True,
                timeout=max(0.1, min(float(self.timeout), remaining)),
            )
            try:
                converted = response.json()
            except ValueError as exc:
                raise RoundTripError(
                    "Confluence remote render preflight returned invalid result JSON"
                ) from exc
            if not isinstance(converted, dict):
                raise RoundTripError(
                    "Confluence remote render preflight returned an invalid result"
                )
            status = str(converted.get("status") or "").upper()
            if converted.get("error"):
                raise RoundTripError("Confluence remote render preflight failed")
            if status == "COMPLETED":
                value = converted.get("value")
                if converted.get("representation") != "view" or not isinstance(value, str):
                    raise RoundTripError(
                        "Confluence remote render preflight completed without a view result"
                    )
                render_safety = rendered_view_safety(value)
                if render_safety["status"] != "passed":
                    raise RemoteRenderPreflightError(
                        "Confluence remote render preflight produced an unknown-macro placeholder",
                        render_safety,
                    )
                return {
                    "status": "completed",
                    "representation": "view",
                    "rendered_sha256": sha256_text(value),
                    "rendered_bytes": len(value.encode("utf-8")),
                    "polls": poll_number,
                    "render_safety": render_safety,
                }
            if status in {"FAILED", "ERROR", "CANCELLED"}:
                raise RoundTripError("Confluence remote render preflight failed")
            if status not in {"WORKING", "PENDING", "QUEUED", "RUNNING"}:
                raise RoundTripError(
                    "Confluence remote render preflight returned an unknown task status"
                )
            if poll_number < max_polls:
                remaining = deadline - time.monotonic()
                if remaining > 0 and poll_interval:
                    self._sleep(min(poll_interval, remaining))
        raise RoundTripError(
            "Confluence remote render preflight did not complete within the bounded polling window"
        )

    def content_state(self, page_id: str) -> dict[str, Any] | None:
        """Return the current page content status, if available."""

        page_id = validate_page_id(page_id)
        response = self.request(
            "GET",
            f"/wiki/rest/api/content/{quote(page_id)}/state",
            expected=(200, 404),
            params={"status": "current"},
        )
        if response.status_code == 404:
            return None
        payload = response.json()
        state = payload.get("contentState") if isinstance(payload, dict) else None
        return state if isinstance(state, dict) else None

    def restrictions(self, page_id: str) -> dict[str, Any]:
        """Return restrictions as read-only evidence."""

        page_id = validate_page_id(page_id)
        response = self.request(
            "GET",
            f"/wiki/rest/api/content/{quote(page_id)}/restriction",
            expected=(200, 403, 404),
            params={"expand": "restrictions.user,restrictions.group"},
        )
        if response.status_code != 200:
            return {"available": False, "http_status": response.status_code}
        payload = response.json()
        return payload if isinstance(payload, dict) else {"available": True}

    def upload_attachment(
        self,
        page_id: str,
        path: Path,
        existing_id: str | None,
        *,
        comment: str,
        media_type: str | None = None,
    ) -> dict[str, Any]:
        """Create or update an attachment by filename."""

        page_id = validate_page_id(page_id)
        endpoint = f"/wiki/rest/api/content/{quote(page_id)}/child/attachment"
        if existing_id:
            endpoint += f"/{quote(str(existing_id))}/data"
        resolved_media_type = media_type or mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        with path.open("rb") as handle:
            response = self.request(
                "POST",
                endpoint,
                expected=(200,),
                headers={"Accept": "application/json", "X-Atlassian-Token": "no-check"},
                data={"comment": comment, "minorEdit": "true"},
                files={"file": (path.name, handle, resolved_media_type)},
            )
        payload = response.json()
        if not isinstance(payload, dict):
            raise RoundTripError("attachment upload returned invalid JSON")
        return payload

    def update_page(
        self,
        page_id: str,
        meta: dict[str, Any],
        storage: str,
        version: int,
        message: str,
    ) -> dict[str, Any]:
        """Update a page with optimistic versioning and storage XML."""

        page_id = validate_page_id(page_id)
        body: dict[str, Any] = {
            "id": page_id,
            "status": "current",
            "title": meta["title"],
            "body": {"representation": "storage", "value": storage},
            "version": {"number": version + 1, "message": message},
        }
        return self.json("PUT", f"/wiki/api/v2/pages/{quote(page_id)}", json=body)

    def sync_labels(self, page_id: str, desired: list[str], current: list[str]) -> dict[str, list[str]]:
        """Synchronize global labels while preserving other label prefixes."""

        page_id = validate_page_id(page_id)
        desired_set = set(desired)
        current_set = set(current)
        added = sorted(desired_set - current_set)
        removed = sorted(current_set - desired_set)
        if added:
            self.request(
                "POST",
                f"/wiki/rest/api/content/{quote(page_id)}/label",
                expected=(200,),
                json=[{"prefix": "global", "name": name} for name in added],
            )
        for name in removed:
            self.request(
                "DELETE",
                f"/wiki/rest/api/content/{quote(page_id)}/label",
                expected=(204,),
                params={"name": name},
            )
        return {"added": added, "removed": removed}

    def set_content_state(
        self,
        page_id: str,
        desired: dict[str, Any] | None,
        current: dict[str, Any] | None,
    ) -> str:
        """Set, clear, or preserve a page-level content status."""

        page_id = validate_page_id(page_id)
        if states_equivalent(desired, current):
            return "unchanged"
        endpoint = f"/wiki/rest/api/content/{quote(page_id)}/state"
        if desired is None:
            self.request("DELETE", endpoint, expected=(200,), params={"status": "current"})
            return "removed"
        if desired.get("id") is not None:
            body = {"id": desired["id"]}
        else:
            body = {key: desired[key] for key in ("name", "color") if desired.get(key) is not None}
        self.request("PUT", endpoint, expected=(200,), params={"status": "current"}, json=body)
        return "updated"


def _response_message(response: requests.Response) -> str:
    """Extract a short non-secret API error message."""

    try:
        payload = response.json()
    except ValueError:
        payload = None
    if isinstance(payload, dict):
        for key in ("message", "errorMessage", "error", "reason"):
            if payload.get(key):
                return re.sub(r"\s+", " ", str(payload[key]))[:300]
    return re.sub(r"\s+", " ", response.text or response.reason)[:300]


def body_value(page: dict[str, Any], representation: str) -> str:
    """Extract a body value from a v2 page response."""

    body = page.get("body") or {}
    value = (body.get(representation) or {}).get("value")
    if not isinstance(value, str):
        raise RoundTripError(f"page response did not include body.{representation}.value")
    return value


def safe_filename(value: str) -> str:
    """Reject unsafe attachment filenames."""

    windows_reserved = {"con", "prn", "aux", "nul"} | {
        f"{prefix}{number}" for prefix in ("com", "lpt") for number in range(1, 10)
    }
    stem = value.split(".", 1)[0].casefold()
    if (
        not value
        or Path(value).name != value
        or value in {".", ".."}
        or len(value) > 240
        or value.endswith((".", " "))
        or re.search(r'[<>:"/\\|?*\x00-\x1f]', value)
        or stem in windows_reserved
    ):
        raise ValidationError(f"unsafe attachment filename: {value!r}")
    return value


def normalize_adf(value: str) -> dict[str, Any]:
    """Parse a reasonable top-level ADF document while preserving unknown nodes."""

    try:
        payload = json.loads(value)
    except json.JSONDecodeError as exc:
        raise RoundTripError("Confluence returned malformed atlas_doc_format JSON") from exc
    if not isinstance(payload, dict):
        raise RoundTripError("Confluence atlas_doc_format must be a JSON object")
    version = payload.get("version")
    if (
        payload.get("type") != "doc"
        or not isinstance(version, int)
        or isinstance(version, bool)
        or version <= 0
        or not isinstance(payload.get("content"), list)
    ):
        raise RoundTripError(
            "Confluence atlas_doc_format must be a versioned doc with an array content field"
        )
    return payload


def global_labels(page: dict[str, Any]) -> list[str]:
    """Return sorted global label names from a page response."""

    labels = (page.get("labels") or {}).get("results") or []
    return sorted(
        {
            str(item.get("name"))
            for item in labels
            if isinstance(item, dict) and item.get("name") and item.get("prefix", "global") == "global"
        }
    )


def state_signature(state: dict[str, Any] | None) -> tuple[Any, ...] | None:
    """Return a stable content-state comparison signature."""

    if not state:
        return None
    if state.get("id") is not None:
        return ("id", str(state["id"]))
    return ("definition", state.get("name"), state.get("color"))


def states_equivalent(
    expected: dict[str, Any] | None,
    actual: dict[str, Any] | None,
) -> bool:
    """Compare state IDs when both are known, otherwise compare definitions."""

    if not expected or not actual:
        return not expected and not actual
    expected_id = expected.get("id")
    actual_id = actual.get("id")
    if expected_id is not None and actual_id is not None:
        return str(expected_id) == str(actual_id)
    expected_name = expected.get("name")
    actual_name = actual.get("name")
    expected_color = expected.get("color")
    actual_color = actual.get("color")
    if expected_name is None or actual_name is None or expected_color is None or actual_color is None:
        return False
    return (
        str(expected_name) == str(actual_name)
        and str(expected_color).casefold() == str(actual_color).casefold()
    )


def _validated_labels(value: Any, field: str) -> list[str]:
    """Validate and normalize a global-label lock or editable value."""

    if (
        not isinstance(value, list)
        or any(not isinstance(item, str) or not item for item in value)
        or len(value) != len(set(value))
    ):
        raise ValidationError(f"{field} must be an array of unique non-empty strings")
    return sorted(value)


def _validated_content_state(value: Any, field: str) -> dict[str, Any] | None:
    """Validate an editable content-state value or optimistic-lock baseline."""

    if value is not None and (
        not isinstance(value, dict)
        or (
            value.get("id") is None
            and (not value.get("name") or not value.get("color"))
        )
    ):
        raise ValidationError(
            f"{field} must be null, contain id, or contain name and color"
        )
    return value


def editable_baselines(manifest: dict[str, Any]) -> dict[str, Any] | None:
    """Return validated label/state locks, allowing legacy manifests without locks."""

    if "editable_baselines" not in manifest:
        return None
    value = manifest.get("editable_baselines")
    if not isinstance(value, dict):
        raise ValidationError("manifest.json editable_baselines must be an object")
    if "global_labels" not in value or "content_state" not in value:
        raise ValidationError(
            "manifest.json editable_baselines requires global_labels and content_state"
        )
    return {
        "global_labels": _validated_labels(
            value.get("global_labels"),
            "manifest.json editable_baselines.global_labels",
        ),
        "content_state": _validated_content_state(
            value.get("content_state"),
            "manifest.json editable_baselines.content_state",
        ),
    }


def canonical_storage(storage: str) -> str:
    """Canonicalize a Confluence storage fragment while preserving its content."""

    wrapped = _wrapped_storage_xml(storage)
    try:
        return ElementTree.canonicalize(xml_data=wrapped, strip_text=False, with_comments=True)
    except ElementTree.ParseError as exc:
        raise ValidationError(f"page.storage.xml is not well-formed Confluence storage XML: {exc}") from exc


def _wrapped_storage_xml(storage: str) -> str:
    """Wrap one storage fragment in a namespace-aware synthetic root."""

    normalized = storage.replace("\r\n", "\n").replace("\r", "\n").strip()
    normalized = _normalize_named_entities(normalized)
    return f'<roundtrip-root xmlns:ac="{AC_NS}" xmlns:ri="{RI_NS}">{normalized}</roundtrip-root>'


def _storage_root(storage: str) -> ElementTree.Element:
    """Parse storage XML while retaining comments as non-element nodes."""

    parser = ElementTree.XMLParser(target=ElementTree.TreeBuilder(insert_comments=True))
    try:
        return ElementTree.fromstring(_wrapped_storage_xml(storage), parser=parser)
    except ElementTree.ParseError as exc:
        raise ValidationError(f"page.storage.xml is not well-formed Confluence storage XML: {exc}") from exc


def _storage_name(name: Any) -> str | None:
    """Return the stable prefixed name of an XML element or attribute."""

    if not isinstance(name, str):
        return None
    if not name.startswith("{"):
        return name
    namespace, separator, local_name = name[1:].partition("}")
    if not separator:
        return name
    prefix = {AC_NS: "ac", RI_NS: "ri"}.get(namespace)
    return f"{prefix}:{local_name}" if prefix else local_name


def _normalized_css_style(value: str) -> str:
    """Normalize Confluence-owned CSS serialization without changing declarations."""

    declarations: list[tuple[str, str]] = []
    for raw in value.split(";"):
        if not raw.strip():
            continue
        if ":" not in raw:
            declarations.append((raw.strip(), ""))
            continue
        name, css_value = raw.split(":", 1)
        css_value = re.sub(r"\s*,\s*", ",", css_value.strip())
        css_value = re.sub(r"(?<![\w.])(-?\d+)\.0(?=(?:px|em|rem|%)(?:\b|$))", r"\1", css_value)
        css_value = re.sub(r"\s+", " ", css_value)
        declarations.append((name.strip().lower(), css_value))
    if len({name for name, _value in declarations}) == len(declarations):
        declarations.sort(key=lambda item: item[0])
    return ";".join(f"{name}:{css_value}" if css_value else name for name, css_value in declarations)


def remote_equivalence_storage(storage: str) -> str:
    """Canonicalize storage while ignoring Confluence-owned save normalization.

    Confluence adds opaque macro IDs, representation version hints, and default
    schema versions when it saves storage XML. It also reorders macro parameter
    elements. Those changes do not alter page behavior; all other nodes,
    attributes, comments, text, and child order remain part of the comparison.
    """

    normalized = storage.replace("\r\n", "\n").replace("\r", "\n").strip()
    normalized = _normalize_named_entities(normalized)
    wrapped = f'<roundtrip-root xmlns:ac="{AC_NS}" xmlns:ri="{RI_NS}">{normalized}</roundtrip-root>'
    parser = ElementTree.XMLParser(target=ElementTree.TreeBuilder(insert_comments=True))
    try:
        root = ElementTree.fromstring(wrapped, parser=parser)
    except ElementTree.ParseError as exc:
        raise ValidationError(f"page.storage.xml is not well-formed Confluence storage XML: {exc}") from exc

    generated_attributes = {
        f"{{{AC_NS}}}macro-id",
        f"{{{AC_NS}}}schema-version",
        f"{{{RI_NS}}}version-at-save",
    }
    macro_tag = f"{{{AC_NS}}}structured-macro"
    parameter_tag = f"{{{AC_NS}}}parameter"
    parameter_name = f"{{{AC_NS}}}name"
    whitespace_insensitive_containers = {
        f"{{{AC_NS}}}structured-macro",
        f"{{{AC_NS}}}rich-text-body",
        f"{{{AC_NS}}}layout",
        f"{{{AC_NS}}}layout-section",
        f"{{{AC_NS}}}layout-cell",
        f"{{{AC_NS}}}task-list",
        f"{{{AC_NS}}}task",
    }
    nested_xml_value_containers = {
        f"{{{AC_NS}}}parameter",
        f"{{{AC_NS}}}link",
    }
    for element in root.iter():
        for attribute in generated_attributes:
            element.attrib.pop(attribute, None)
        if "style" in element.attrib:
            element.attrib["style"] = _normalized_css_style(element.attrib["style"])
        if element.tag in whitespace_insensitive_containers or (
            element.tag in nested_xml_value_containers and len(element)
        ):
            if element.text is not None and not element.text.strip():
                element.text = None
            for child in element:
                if child.tail is not None and not child.tail.strip():
                    child.tail = None
        if element.tag != macro_tag:
            continue
        children = list(element)
        parameter_indexes = [index for index, child in enumerate(children) if child.tag == parameter_tag]
        if len(parameter_indexes) < 2:
            continue
        first_index = parameter_indexes[0]
        parameters = sorted(
            (children[index] for index in parameter_indexes),
            key=lambda child: (str(child.attrib.get(parameter_name) or ""), ElementTree.tostring(child, encoding="unicode")),
        )
        others = [child for child in children if child.tag != parameter_tag]
        for child in children:
            element.remove(child)
        before_count = sum(1 for index in range(first_index) if children[index].tag != parameter_tag)
        rebuilt = others[:before_count] + parameters + others[before_count:]
        element.extend(rebuilt)

    serialized = ElementTree.tostring(root, encoding="unicode")
    return ElementTree.canonicalize(xml_data=serialized, strip_text=False, with_comments=True)


def _entity_to_numeric(match: re.Match[str]) -> str:
    """Convert named HTML entities to XML-safe numeric entities."""

    decoded = unescape(match.group(0))
    if decoded == match.group(0):
        return match.group(0)
    return "".join(f"&#{ord(char)};" for char in decoded)


def _normalize_named_entities(storage: str) -> str:
    """Convert HTML entities only where XML parsing treats them as references."""

    protected = re.compile(r"(<!\[CDATA\[.*?\]\]>|<!--.*?-->|<\?.*?\?>)", re.DOTALL)
    parts = protected.split(storage)
    for index in range(0, len(parts), 2):
        parts[index] = re.sub(
            r"&([A-Za-z][A-Za-z0-9]+);",
            _entity_to_numeric,
            parts[index],
        )
    return "".join(parts)


def storage_summary(storage: str) -> dict[str, Any]:
    """Build a deterministic inventory of Confluence storage features."""

    canonical = canonical_storage(storage)
    root = _storage_root(storage)
    tags: Counter[str] = Counter()
    macros: Counter[str] = Counter()
    attachments: set[str] = set()
    page_links: set[str] = set()
    hrefs: set[str] = set()
    for element in root.iter():
        tag = _storage_name(element.tag)
        if tag is None or tag == "roundtrip-root":
            continue
        tags[tag] += 1
        if tag == "ac:structured-macro":
            macro_name = element.attrib.get(f"{{{AC_NS}}}name")
            if macro_name:
                macros[str(macro_name)] += 1
        elif tag == "ri:attachment":
            filename = element.attrib.get(f"{{{RI_NS}}}filename")
            if filename:
                attachments.add(str(filename))
        elif tag == "ri:page":
            content_title = element.attrib.get(f"{{{RI_NS}}}content-title")
            if content_title:
                page_links.add(str(content_title))
        for attribute_name, value in element.attrib.items():
            if _storage_name(attribute_name) == "href":
                hrefs.add(str(value))
    return {
        "canonical_sha256": sha256_text(canonical),
        "tags": dict(sorted(tags.items())),
        "macros": dict(sorted(macros.items())),
        "attachment_filenames": sorted(attachments),
        "page_references": sorted(page_links),
        "hrefs": sorted(hrefs),
    }


_ALLOWED_STORAGE_LINK_SCHEMES = frozenset({"http", "https", "mailto", "tel"})
_LOCAL_POSIX_PATH = re.compile(
    r"^/(?:Users|home|root|tmp|var|etc|opt|mnt|Volumes|private|srv|proc|sys|dev|run|"
    r"usr|bin|sbin|lib|workspace)(?:/|$)",
    re.IGNORECASE,
)


def _validate_storage_link_target(target: str, source: str) -> None:
    """Reject executable URL schemes and references to a local filesystem."""

    if target != target.strip() or any(ord(character) < 32 or ord(character) == 127 for character in target):
        raise ValidationError(f"unsafe storage link target in {source}: surrounding whitespace or controls")
    if (
        "\\" in target
        or re.match(r"^/?[A-Za-z]:/", target)
        or target.startswith(("~/", "$HOME/", "${HOME}/", "%USERPROFILE%/"))
        or _LOCAL_POSIX_PATH.match(target)
    ):
        raise ValidationError(f"unsafe storage link target in {source}: local filesystem reference")
    try:
        parsed = urlparse(target)
    except ValueError as exc:
        raise ValidationError(f"unsafe storage link target in {source}: malformed URL") from exc
    scheme = parsed.scheme.casefold()
    if scheme and scheme not in _ALLOWED_STORAGE_LINK_SCHEMES:
        raise ValidationError(f"unsafe storage link target in {source}: unsupported scheme {scheme!r}")
    if scheme in {"http", "https"} and not parsed.netloc:
        raise ValidationError(f"unsafe storage link target in {source}: absolute web URL has no host")
    if parsed.username is not None or parsed.password is not None:
        raise ValidationError(f"unsafe storage link target in {source}: embedded credentials")


def validate_storage_link_targets(storage: str) -> None:
    """Validate browser-navigation targets in editable Confluence storage XML."""

    root = _storage_root(storage)
    for element in root.iter():
        tag = _storage_name(element.tag)
        if tag is None:
            continue
        for attribute_name, value in element.attrib.items():
            attribute = _storage_name(attribute_name)
            if attribute in {"href", "src"}:
                _validate_storage_link_target(str(value), f"{tag}@{attribute}")
        if tag == "ri:url":
            value = element.attrib.get(f"{{{RI_NS}}}value")
            if value is not None:
                _validate_storage_link_target(str(value), "ri:url@ri:value")
        elif tag == "ac:parameter":
            parameter_name = str(element.attrib.get(f"{{{AC_NS}}}name") or "").casefold()
            parameter_value = str(element.text or "")
            if parameter_name == "url" and parameter_value.strip():
                _validate_storage_link_target(parameter_value, "ac:parameter[url]")


def adf_summary(payload: Any) -> dict[str, Any]:
    """Inventory ADF nodes, marks, extensions, links, and media IDs."""

    nodes: Counter[str] = Counter()
    marks: Counter[str] = Counter()
    extensions: set[str] = set()
    urls: set[str] = set()
    media_ids: set[str] = set()

    def visit(value: Any, *, is_mark: bool = False) -> None:
        if isinstance(value, dict):
            node_type = value.get("type")
            if isinstance(node_type, str):
                (marks if is_mark else nodes)[node_type] += 1
            attrs = value.get("attrs")
            if isinstance(attrs, dict):
                for key in ("extensionKey", "extensionType"):
                    if isinstance(attrs.get(key), str):
                        extensions.add(attrs[key])
                for key in ("href", "url"):
                    if isinstance(attrs.get(key), str):
                        urls.add(attrs[key])
                if node_type in {"media", "mediaInline"} and isinstance(attrs.get("id"), str):
                    media_ids.add(attrs["id"])
            for key, child in value.items():
                if key == "marks" and isinstance(child, list):
                    for item in child:
                        visit(item, is_mark=True)
                elif key != "attrs":
                    visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child, is_mark=is_mark)

    visit(payload)
    return {
        "nodes": dict(sorted(nodes.items())),
        "marks": dict(sorted(marks.items())),
        "extensions": sorted(extensions),
        "urls": sorted(urls),
        "media_ids": sorted(media_ids),
    }


def visible_text(html: str) -> str:
    """Return normalized visible-ish text from rendered HTML."""

    parser = _VisibleTextParser()
    parser.feed(html)
    parser.close()
    return parser.text()


def rendered_view_safety(html: str) -> dict[str, Any]:
    """Return sanitized structural diagnostics for server-rendered view HTML."""

    if not isinstance(html, str):
        raise RoundTripError("Confluence remote render preflight returned non-text view HTML")
    parser = _RenderedViewSafetyParser()
    parser.feed(html)
    parser.close()
    count = parser.unknown_macro_placeholders
    return {
        "status": "failed" if count else "passed",
        "unknown_macro_placeholders": count,
        "signals_found": sorted(parser.signals_found),
    }


def _render_safety_passed(value: Any) -> bool:
    """Return whether a sanitized render-safety record proves no placeholders."""

    if not isinstance(value, dict):
        return False
    count = value.get("unknown_macro_placeholders")
    return bool(
        set(value)
        == {"status", "unknown_macro_placeholders", "signals_found"}
        and value.get("status") == "passed"
        and isinstance(count, int)
        and not isinstance(count, bool)
        and count == 0
        and value.get("signals_found") == []
    )


def page_meta(page: dict[str, Any]) -> dict[str, Any]:
    """Return the editable page metadata contract."""

    page_id = validate_page_id(page.get("id"))
    return {
        "page_id": page_id,
        "title": str(page.get("title") or "Untitled"),
        "space_id": str(page["spaceId"]) if page.get("spaceId") is not None else None,
        "parent_id": str(page["parentId"]) if page.get("parentId") is not None else None,
        "status": str(page.get("status") or "current"),
        "subtype": page.get("subtype"),
    }


def validate_supported_page(page: dict[str, Any], expected_page_id: str | None = None) -> None:
    """Reject non-current pages and unsupported page subtypes such as live docs."""

    try:
        page_id = validate_page_id(page.get("id"))
        expected = validate_page_id(expected_page_id) if expected_page_id is not None else None
    except ValidationError as exc:
        raise ValidationError("Confluence returned an unexpected page identity") from exc
    if expected is not None and page_id != expected:
        raise ValidationError("Confluence returned an unexpected page identity")
    if str(page.get("status") or "") != "current":
        raise ValidationError("only current Confluence pages can be round-tripped")
    subtype = page.get("subtype")
    if subtype is not None and subtype != "page":
        raise ValidationError(f"unsupported Confluence page subtype: {subtype!r}")


def draft_observation(
    draft: dict[str, Any],
    current: dict[str, Any],
    expected_page_id: str,
) -> dict[str, Any]:
    """Describe whether a current editor draft diverges from the published page."""

    expected_page_id = validate_page_id(expected_page_id)
    try:
        draft_page_id = validate_page_id(draft.get("id"))
    except ValidationError as exc:
        raise ValidationError("Confluence returned an unexpected draft identity") from exc
    if draft_page_id != expected_page_id:
        raise ValidationError("Confluence returned an unexpected draft identity")
    status = str(draft.get("status") or "")
    if status == "current":
        return {
            "status": "current",
            "present": False,
            "diverged": False,
            "title_changed": False,
            "storage_changed": False,
        }
    if status != "draft":
        raise ValidationError(f"unexpected draft-aware page status: {status!r}")
    if draft.get("subtype") is not None and draft.get("subtype") != "page":
        raise ValidationError(f"unsupported Confluence draft subtype: {draft.get('subtype')!r}")
    for field in ("spaceId", "parentId"):
        if str(draft.get(field) or "") != str(current.get(field) or ""):
            raise ConflictError(f"draft {field} does not match the published page")
    version = (draft.get("version") or {}).get("number")
    if not isinstance(version, int) or isinstance(version, bool) or version <= 0:
        raise ValidationError("draft-aware page response has no positive version")
    draft_storage = body_value(draft, "storage")
    current_storage = body_value(current, "storage")
    title_changed = str(draft.get("title") or "") != str(current.get("title") or "")
    storage_changed = (
        remote_equivalence_storage(draft_storage)
        != remote_equivalence_storage(current_storage)
    )
    return {
        "status": "draft",
        "present": True,
        "diverged": title_changed or storage_changed,
        "title_changed": title_changed,
        "storage_changed": storage_changed,
        "version": version,
        "storage_equivalence_sha256": sha256_text(
            remote_equivalence_storage(draft_storage)
        ),
    }


def validate_representation_snapshot(
    pages: dict[str, dict[str, Any]],
    expected_page_id: str,
) -> int:
    """Require all fetched body representations to describe one page version."""

    signatures: dict[str, tuple[Any, ...]] = {}
    for representation, page in pages.items():
        validate_supported_page(page, expected_page_id)
        version = int((page.get("version") or {}).get("number") or 0)
        if version <= 0:
            raise ConflictError(f"{representation} response did not include a current page version")
        signatures[representation] = (
            str(page.get("id")),
            version,
            str(page.get("title") or ""),
            str(page.get("spaceId") or ""),
            str(page.get("parentId") or ""),
            str(page.get("status") or ""),
            str(page.get("subtype") or ""),
        )
    if len(set(signatures.values())) != 1:
        raise ConflictError(
            "Confluence page representations came from different versions; download or verify again"
        )
    return next(iter(signatures.values()))[1]


def attachment_record(item: dict[str, Any], filename: str, payload: bytes) -> dict[str, Any]:
    """Return a portable attachment manifest record."""

    return {
        "id": str(item.get("id") or ""),
        "filename": filename,
        "path": f"{ATTACHMENTS_DIR}/{filename}",
        "media_type": item.get("mediaType"),
        "file_size": len(payload),
        "sha256": sha256_bytes(payload),
        "version": (item.get("version") or {}).get("number"),
    }


def required_browser_check_ids(ground_truth: dict[str, Any]) -> list[str]:
    """Return the explicit browser checks required for completion."""

    raw = ground_truth.get("required_browser_check_ids", ["rendered-page"])
    if (
        not isinstance(raw, list)
        or not raw
        or any(not isinstance(item, str) or not item.strip() for item in raw)
    ):
        raise ValidationError(
            "ground-truth.json required_browser_check_ids must be a non-empty array of strings"
        )
    normalized = [item.strip() for item in raw]
    if len(set(normalized)) != len(normalized):
        raise ValidationError("ground-truth.json required_browser_check_ids contains duplicates")
    return normalized


def desired_state_contract(workspace: Path) -> dict[str, Any]:
    """Build the complete local state bound to API and browser verification."""

    workspace = _resolve_workspace_root(workspace)
    _reject_symlink(workspace / STORAGE_NAME, STORAGE_NAME)
    _reject_symlink(workspace / VIEW_NAME, VIEW_NAME)
    manifest = load_json(workspace / MANIFEST_NAME)
    meta = load_json(workspace / META_NAME)
    labels = load_json(workspace / LABELS_NAME)
    state = load_json(workspace / STATE_NAME)
    ground_truth = load_json(workspace / GT_NAME)
    prior = {
        str(item.get("filename")): item
        for item in manifest.get("attachments", [])
        if isinstance(item, dict) and item.get("filename")
    }
    attachments = []
    for path in _attachment_files(workspace):
        media_type = str((prior.get(path.name) or {}).get("media_type") or "") or (
            mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        )
        attachments.append(
            {
                "filename": path.name,
                "sha256": sha256_bytes(path.read_bytes()),
                "media_type": media_type,
            }
        )
    storage = (workspace / STORAGE_NAME).read_text(encoding="utf-8")
    adf = load_json(workspace / ADF_NAME)
    view = (workspace / VIEW_NAME).read_text(encoding="utf-8")
    restrictions = load_json(workspace / RESTRICTIONS_NAME)
    immutable_evidence = {
        ADF_NAME: sha256_json(adf),
        VIEW_NAME: sha256_text(view),
        RESTRICTIONS_NAME: sha256_json(restrictions),
    }
    extended_keys = ("properties", "operations")
    if any(key in manifest for key in extended_keys) and not all(
        key in manifest for key in extended_keys
    ):
        raise ValidationError(
            "manifest.json must declare both properties and operations evidence or neither"
        )
    if all(key in manifest for key in extended_keys):
        immutable_evidence[PROPERTIES_NAME] = sha256_json(
            load_json(workspace / PROPERTIES_NAME)
        )
        immutable_evidence[OPERATIONS_NAME] = sha256_json(
            load_json(workspace / OPERATIONS_NAME)
        )
    return {
        "page": {
            "page_id": str(meta.get("page_id") or ""),
            "title": meta.get("title"),
            "space_id": meta.get("space_id"),
            "parent_id": meta.get("parent_id"),
        },
        "storage_equivalence_sha256": sha256_text(remote_equivalence_storage(storage)),
        "labels": sorted(labels),
        "content_state": state,
        "attachments": attachments,
        "required_visible_text": list(ground_truth.get("required_visible_text", [])),
        "required_browser_check_ids": required_browser_check_ids(ground_truth),
        "immutable_evidence": immutable_evidence,
    }


def desired_state_sha256(workspace: Path) -> str:
    """Return the integrity digest for the current editable workspace state."""

    return sha256_json(desired_state_contract(workspace))


def _journal_path(workspace: Path) -> Path:
    return _verification_dir(workspace) / JOURNAL_NAME


def _load_resume_journal(workspace: Path, desired_digest: str) -> dict[str, Any] | None:
    """Return a compatible partial journal that can be reconciled safely."""

    path = _journal_path(workspace)
    if not path.is_file():
        return None
    journal = load_json(path)
    if (
        not isinstance(journal, dict)
        or journal.get("status") != "partial"
        or journal.get("desired_state_sha256") != desired_digest
    ):
        return None
    return journal


def _write_journal(workspace: Path, journal: dict[str, Any]) -> None:
    journal["updated_at"] = utc_now()
    write_json(_journal_path(workspace), journal)
    if journal.get("status") != "running":
        _release_operation_lock(workspace, str(journal.get("operation_id") or ""))


def _set_journal_step(
    workspace: Path,
    journal: dict[str, Any],
    step_id: str,
    status: str,
    detail: Any = None,
) -> None:
    """Atomically advance one mutation-journal step."""

    for step in journal.get("steps", []):
        if isinstance(step, dict) and step.get("id") == step_id:
            step["status"] = status
            step["updated_at"] = utc_now()
            if detail is not None:
                step["detail"] = detail
            _write_journal(workspace, journal)
            return
    raise ValidationError(f"mutation journal has no step {step_id!r}")


def _begin_operation(
    workspace: Path,
    plan: dict[str, Any],
    *,
    desired_digest: str,
    sync_attachments: bool,
    sync_labels: bool,
    sync_content_state: bool,
) -> dict[str, Any]:
    """Invalidate prior completion evidence and atomically start one operation."""

    verification = _verification_dir(workspace, create=True)
    steps: list[dict[str, Any]] = []
    reconciled = set(plan.get("reconciled_attachments", []))
    if plan.get("remote_render_preflight_required"):
        steps.append(
            {
                "id": "remote-render-preflight",
                "kind": "preflight",
                "status": "pending",
            }
        )
    if sync_attachments:
        for filename in sorted(reconciled):
            steps.append(
                {
                    "id": f"attachment:{filename}",
                    "kind": "attachment",
                    "status": "reconciled",
                    "filename": filename,
                }
            )
        for change in plan.get("attachments", []):
            steps.append(
                {
                    "id": f"attachment:{change['filename']}",
                    "kind": "attachment",
                    "status": "pending",
                    "filename": change["filename"],
                    "action": change["action"],
                    "sha256": change["sha256"],
                }
            )
    if plan.get("reconciled_page_update"):
        steps.append({"id": "page", "kind": "page", "status": "reconciled"})
    elif plan.get("page_update"):
        steps.append({"id": "page", "kind": "page", "status": "pending"})
    if sync_labels:
        steps.append({"id": "labels", "kind": "labels", "status": "pending"})
    if sync_content_state:
        steps.append({"id": "content-state", "kind": "content-state", "status": "pending"})
    steps.append({"id": "api-verification", "kind": "verification", "status": "pending"})
    started = utc_now()
    operation_id = str(uuid4())
    journal = {
        "schema_version": SCHEMA_VERSION,
        "operation_id": operation_id,
        "page_id": str(plan["page_id"]),
        "status": "running",
        "started_at": started,
        "updated_at": started,
        "desired_state_sha256": desired_digest,
        "plan_sha256": sha256_json(plan),
        "remote_render_preflight_required": bool(
            plan.get("remote_render_preflight_required")
        ),
        "remote_render_safety_contract_version": (
            1 if plan.get("remote_render_preflight_required") else None
        ),
        "resumed_from_operation_id": plan.get("resumed_from_operation_id"),
        "steps": steps,
    }
    _acquire_operation_lock(workspace, operation_id)
    try:
        for name in (
            REPORT_NAME,
            BROWSER_GT_NAME,
            RENDER_SAFETY_RECONCILIATION_NAME,
        ):
            try:
                (verification / name).unlink()
            except FileNotFoundError:
                pass
        write_json(_journal_path(workspace), journal)
    except BaseException:
        _release_operation_lock(workspace, operation_id)
        raise
    return journal


def _png_is_decodable(payload: bytes) -> bool:
    """Validate PNG structure, CRCs, dimensions, and compressed image data."""

    if not payload.startswith(b"\x89PNG\r\n\x1a\n"):
        return False
    offset = 8
    width = height = 0
    bit_depth = color_type = interlace = -1
    saw_ihdr = False
    saw_idat = False
    idat_ended = False
    compressed = bytearray()
    saw_iend = False
    while offset + 12 <= len(payload):
        length = struct.unpack(">I", payload[offset : offset + 4])[0]
        chunk_type = payload[offset + 4 : offset + 8]
        end = offset + 12 + length
        if end > len(payload):
            return False
        data = payload[offset + 8 : offset + 8 + length]
        expected_crc = struct.unpack(">I", payload[offset + 8 + length : end])[0]
        if zlib.crc32(chunk_type + data) & 0xFFFFFFFF != expected_crc:
            return False
        if chunk_type == b"IHDR":
            if saw_ihdr or offset != 8 or length != 13:
                return False
            width, height = struct.unpack(">II", data[:8])
            bit_depth, color_type, compression_method, filter_method, interlace = data[8:]
            allowed_depths = {
                0: {1, 2, 4, 8, 16},
                2: {8, 16},
                3: {1, 2, 4, 8},
                4: {8, 16},
                6: {8, 16},
            }
            if (
                width <= 0
                or height <= 0
                or width * height > MAX_SCREENSHOT_PIXELS
                or bit_depth not in allowed_depths.get(color_type, set())
                or compression_method != 0
                or filter_method != 0
                or interlace not in {0, 1}
            ):
                return False
            saw_ihdr = True
        elif chunk_type == b"IDAT":
            if not saw_ihdr or idat_ended:
                return False
            saw_idat = True
            compressed.extend(data)
        elif chunk_type == b"IEND":
            if length != 0 or not saw_ihdr or not saw_idat:
                return False
            saw_iend = True
            offset = end
            break
        elif saw_idat:
            idat_ended = True
        offset = end
    if not saw_iend or offset != len(payload) or not compressed:
        return False

    channels = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}[color_type]
    bits_per_pixel = channels * bit_depth
    passes = [(0, 0, 1, 1)]
    if interlace == 1:
        passes = [
            (0, 0, 8, 8),
            (4, 0, 8, 8),
            (0, 4, 4, 8),
            (2, 0, 4, 4),
            (0, 2, 2, 4),
            (1, 0, 2, 2),
            (0, 1, 1, 2),
        ]

    scanlines: list[tuple[int, int]] = []
    expected_size = 0
    for start_x, start_y, step_x, step_y in passes:
        pass_width = 0 if width <= start_x else (width - start_x + step_x - 1) // step_x
        pass_height = 0 if height <= start_y else (height - start_y + step_y - 1) // step_y
        if pass_width == 0 or pass_height == 0:
            continue
        row_size = (pass_width * bits_per_pixel + 7) // 8
        scanlines.extend((row_size, pass_height) for _ in range(1))
        expected_size += (row_size + 1) * pass_height
    if expected_size <= 0 or expected_size > MAX_SCREENSHOT_DECODED_BYTES:
        return False
    try:
        decoder = zlib.decompressobj()
        decoded = decoder.decompress(bytes(compressed), expected_size + 1)
    except zlib.error:
        return False
    if (
        not decoder.eof
        or decoder.unused_data
        or decoder.unconsumed_tail
        or len(decoded) != expected_size
    ):
        return False
    position = 0
    for row_size, pass_height in scanlines:
        for _ in range(pass_height):
            if decoded[position] > 4:
                return False
            position += row_size + 1
    return position == len(decoded)


def _jpeg_is_decodable(payload: bytes) -> bool:
    """Validate JPEG segments, frame components, and entropy-coded scans."""

    if len(payload) < 12 or not payload.startswith(b"\xff\xd8") or not payload.endswith(b"\xff\xd9"):
        return False
    offset = 2
    saw_frame = False
    saw_scan = False
    saw_quantization_table = False
    saw_entropy_table = False
    frame_components: set[int] = set()
    frame_markers = set(range(0xC0, 0xC4)) | set(range(0xC5, 0xC8)) | set(range(0xC9, 0xCC)) | set(range(0xCD, 0xD0))
    while offset + 1 < len(payload):
        if payload[offset] != 0xFF:
            return False
        while offset < len(payload) and payload[offset] == 0xFF:
            offset += 1
        if offset >= len(payload):
            return False
        marker = payload[offset]
        offset += 1
        if marker == 0xD9:
            return (
                offset == len(payload)
                and saw_frame
                and saw_scan
                and saw_quantization_table
                and saw_entropy_table
            )
        if marker == 0xD8:
            return False
        if marker in {0x01} or 0xD0 <= marker <= 0xD7:
            continue
        if offset + 2 > len(payload):
            return False
        length = struct.unpack(">H", payload[offset : offset + 2])[0]
        if length < 2 or offset + length > len(payload):
            return False
        data = payload[offset + 2 : offset + length]
        if marker in frame_markers:
            if len(data) < 9:
                return False
            height, width = struct.unpack(">HH", data[1:5])
            component_count = data[5]
            if (
                data[0] not in {8, 12}
                or width <= 0
                or height <= 0
                or width * height > MAX_SCREENSHOT_PIXELS
                or component_count not in {1, 3, 4}
                or len(data) != 6 + 3 * component_count
            ):
                return False
            components = {data[6 + 3 * index] for index in range(component_count)}
            if len(components) != component_count:
                return False
            frame_components = components
            saw_frame = True
        elif marker == 0xDB:
            if not data:
                return False
            saw_quantization_table = True
        elif marker in {0xC4, 0xCC}:
            if not data:
                return False
            saw_entropy_table = True
        elif marker == 0xDA:
            if not saw_frame or len(data) < 6:
                return False
            component_count = data[0]
            if component_count <= 0 or len(data) != 4 + 2 * component_count:
                return False
            scan_components = {data[1 + 2 * index] for index in range(component_count)}
            if len(scan_components) != component_count or not scan_components <= frame_components:
                return False
            saw_scan = True
            offset += length
            entropy_bytes = 0
            while offset < len(payload):
                if payload[offset] != 0xFF:
                    entropy_bytes += 1
                    offset += 1
                    continue
                marker_start = offset
                while offset < len(payload) and payload[offset] == 0xFF:
                    offset += 1
                if offset >= len(payload):
                    return False
                scan_marker = payload[offset]
                if scan_marker == 0x00:
                    entropy_bytes += 1
                    offset += 1
                    continue
                if 0xD0 <= scan_marker <= 0xD7:
                    offset += 1
                    continue
                offset = marker_start
                break
            if entropy_bytes == 0:
                return False
            continue
        offset += length
    return False


def screenshot_is_decodable(payload: bytes) -> bool:
    """Return whether screenshot bytes are a structurally valid PNG or JPEG."""

    if not (_png_is_decodable(payload) or _jpeg_is_decodable(payload)):
        return False
    try:
        from io import BytesIO

        from PIL import Image
    except ImportError:
        return True
    try:
        with Image.open(BytesIO(payload)) as image:
            if image.format not in {"PNG", "JPEG"}:
                return False
            image.verify()
        with Image.open(BytesIO(payload)) as image:
            image.load()
    except (OSError, SyntaxError, ValueError):
        return False
    return True


def capture_ground_truth(workspace: Path, required_text: list[str] | None = None) -> dict[str, Any]:
    """Capture editable local invariants before upload."""

    workspace = _resolve_workspace_root(workspace)
    for name in (
        MANIFEST_NAME,
        META_NAME,
        STORAGE_NAME,
        ADF_NAME,
        VIEW_NAME,
        LABELS_NAME,
        STATE_NAME,
        RESTRICTIONS_NAME,
        GT_NAME,
    ):
        _reject_symlink(workspace / name, name)
    storage = (workspace / STORAGE_NAME).read_text(encoding="utf-8")
    adf = load_json(workspace / ADF_NAME)
    meta = load_json(workspace / META_NAME)
    labels = load_json(workspace / LABELS_NAME)
    state = load_json(workspace / STATE_NAME)
    attachment_paths = _attachment_files(workspace)
    attachments = [
        {"filename": path.name, "sha256": sha256_bytes(path.read_bytes()), "file_size": path.stat().st_size}
        for path in attachment_paths
    ]
    prior = load_json(workspace / GT_NAME) if (workspace / GT_NAME).is_file() else {}
    gt = {
        "schema_version": SCHEMA_VERSION,
        "captured_at": utc_now(),
        "page": {"page_id": meta["page_id"], "title": meta["title"]},
        "storage": storage_summary(storage),
        "adf_observation": adf_summary(adf),
        "labels": labels,
        "content_state": state,
        "attachments": attachments,
        "required_visible_text": required_text if required_text is not None else prior.get("required_visible_text", []),
        "required_browser_check_ids": prior.get(
            "required_browser_check_ids", ["rendered-page"]
        ),
        "visual_baseline": prior.get("visual_baseline"),
    }
    write_json(workspace / GT_NAME, gt)
    return gt


def download_page(
    client: ConfluenceClient,
    page_id: str,
    output: Path,
    *,
    overwrite: bool = False,
    include_attachments: bool = True,
) -> dict[str, Any]:
    """Create an atomic, lossless page workspace."""

    page_id = validate_page_id(page_id)
    output_candidate = output if output.is_absolute() else Path.cwd() / output
    _reject_symlink(output_candidate, "workspace output")
    output = output_candidate.resolve()
    if output.exists() and not overwrite:
        raise ValidationError(f"output already exists: {output}; pass --overwrite to replace it")
    _validate_replace_target(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=f".{output.name}.download-", dir=output.parent))
    try:
        storage_page = client.page(page_id, "storage")
        adf_page = client.page(page_id, "atlas_doc_format")
        view_page = client.page(page_id, "view")
        snapshot_version = validate_representation_snapshot(
            {"storage": storage_page, "atlas_doc_format": adf_page, "view": view_page},
            str(page_id),
        )
        storage = body_value(storage_page, "storage")
        adf = normalize_adf(body_value(adf_page, "atlas_doc_format"))
        view = body_value(view_page, "view")
        draft_info = draft_observation(
            client.draft_page(page_id), storage_page, page_id
        )
        properties = storage_page.get("properties")
        operations = storage_page.get("operations")
        state = client.content_state(page_id)
        restrictions = client.restrictions(page_id)
        labels = client.labels(page_id)
        attachment_items = client.attachments(page_id)
        if not include_attachments and attachment_items:
            raise ValidationError(
                "cannot use --skip-attachments because the page has "
                f"{len(attachment_items)} remote attachment(s); run scan to inspect the page "
                "or perform a full download without --skip-attachments"
            )
        meta = page_meta(storage_page)

        write_json(stage / META_NAME, meta)
        write_text(stage / STORAGE_NAME, storage)
        write_json(stage / ADF_NAME, adf)
        write_text(stage / VIEW_NAME, view)
        write_json(stage / LABELS_NAME, labels)
        write_json(stage / STATE_NAME, state)
        write_json(stage / RESTRICTIONS_NAME, restrictions)
        write_json(stage / PROPERTIES_NAME, properties)
        write_json(stage / OPERATIONS_NAME, operations)
        (stage / ATTACHMENTS_DIR).mkdir(parents=True, exist_ok=True)

        records: list[dict[str, Any]] = []
        if include_attachments:
            seen_filenames: set[str] = set()
            for item in attachment_items:
                filename = safe_filename(str(item.get("title") or ""))
                folded = filename.casefold()
                if folded in seen_filenames:
                    raise ValidationError(
                        f"attachment filenames collide on case-insensitive filesystems: {filename!r}"
                    )
                seen_filenames.add(folded)
                payload = client.download_attachment(item)
                write_bytes(stage / ATTACHMENTS_DIR / filename, payload)
                records.append(attachment_record(item, filename, payload))

        manifest = {
            "schema_version": SCHEMA_VERSION,
            "downloaded_at": utc_now(),
            "base_url": client.base_url,
            "page": {
                **meta,
                "version": snapshot_version,
                "web_url": urljoin(client.base_url, str((storage_page.get("_links") or {}).get("webui") or "")),
            },
            "body": {
                "editable_representation": "storage",
                "storage": {
                    "path": STORAGE_NAME,
                    "sha256": sha256_text(storage),
                    **storage_summary(storage),
                },
                "atlas_doc_format": {"path": ADF_NAME, "sha256": sha256_json(adf)},
                "view": {"path": VIEW_NAME, "sha256": sha256_text(view)},
            },
            "restrictions": {
                "path": RESTRICTIONS_NAME,
                "sha256": sha256_json(restrictions),
            },
            "properties": {
                "path": PROPERTIES_NAME,
                "sha256": sha256_json(properties),
            },
            "operations": {
                "path": OPERATIONS_NAME,
                "sha256": sha256_json(operations),
            },
            "editable_baselines": {
                "global_labels": sorted(labels),
                "content_state": state,
            },
            "draft_observation": draft_info,
            "attachments": records,
            "preserved_read_only": [
                ADF_NAME,
                VIEW_NAME,
                RESTRICTIONS_NAME,
                PROPERTIES_NAME,
                OPERATIONS_NAME,
            ],
        }
        write_json(stage / MANIFEST_NAME, manifest)
        capture_ground_truth(stage)
        if output.exists():
            shutil.rmtree(output)
        stage.replace(output)
        return {
            "status": "downloaded",
            "workspace": str(output),
            "page_id": str(page_id),
            "version": manifest["page"]["version"],
            "attachments": len(records),
        }
    except BaseException:
        shutil.rmtree(stage, ignore_errors=True)
        raise


def validate_workspace(workspace: Path) -> dict[str, Any]:
    """Validate local files and referenced attachments before mutation."""

    workspace = _resolve_workspace_root(workspace)
    verification_path = workspace / VERIFY_DIR
    if verification_path.exists() or verification_path.is_symlink():
        _verification_dir(workspace)
    required = [
        MANIFEST_NAME,
        META_NAME,
        STORAGE_NAME,
        ADF_NAME,
        VIEW_NAME,
        LABELS_NAME,
        STATE_NAME,
        RESTRICTIONS_NAME,
        GT_NAME,
    ]
    for name in required:
        _reject_symlink(workspace / name, name)
    missing = [name for name in required if not (workspace / name).is_file()]
    if missing:
        raise ValidationError("workspace is missing required files: " + ", ".join(missing))
    manifest = load_json(workspace / MANIFEST_NAME)
    if manifest.get("schema_version") != SCHEMA_VERSION:
        raise ValidationError(f"unsupported manifest schema: {manifest.get('schema_version')!r}")
    extended_keys = ("properties", "operations")
    if any(key in manifest for key in extended_keys) and not all(
        key in manifest for key in extended_keys
    ):
        raise ValidationError(
            "manifest.json must declare both properties and operations evidence or neither"
        )
    has_extended_evidence = all(key in manifest for key in extended_keys)
    if has_extended_evidence:
        for name in (PROPERTIES_NAME, OPERATIONS_NAME):
            _reject_symlink(workspace / name, name)
            if not (workspace / name).is_file():
                raise ValidationError(f"workspace is missing required file: {name}")
    manifest_base_url = manifest.get("base_url")
    if not isinstance(manifest_base_url, str):
        raise ValidationError("manifest.json requires a valid base_url")
    normalize_base_url(manifest_base_url)
    meta = load_json(workspace / META_NAME)
    manifest_page = manifest.get("page")
    if not isinstance(manifest_page, dict):
        raise ValidationError("manifest.json page must be an object")
    meta_page_id = validate_page_id(meta.get("page_id"))
    manifest_page_id = validate_page_id(manifest_page.get("page_id"))
    if meta_page_id != manifest_page_id:
        raise ValidationError("page.meta.json page_id does not match manifest.json")
    try:
        manifest_version = int(manifest_page.get("version") or 0)
    except (TypeError, ValueError) as exc:
        raise ValidationError("manifest.json page version must be a positive integer") from exc
    if manifest_version <= 0:
        raise ValidationError("manifest.json page version must be a positive integer")
    if not isinstance(meta.get("title"), str) or not meta["title"].strip():
        raise ValidationError("page.meta.json requires a non-empty title")
    if str(meta.get("status") or "") != "current" or (
        meta.get("subtype") is not None and meta.get("subtype") != "page"
    ):
        raise ValidationError("page.meta.json must describe a current, standard Confluence page")
    for key in ("space_id", "parent_id", "status", "subtype"):
        if key in manifest_page and str(meta.get(key) or "") != str(manifest_page.get(key) or ""):
            raise ValidationError(
                f"changing {key} is unsupported; download the page again instead of moving it"
            )
    adf = load_json(workspace / ADF_NAME)
    view = (workspace / VIEW_NAME).read_text(encoding="utf-8")
    restrictions = load_json(workspace / RESTRICTIONS_NAME)
    if not isinstance(restrictions, dict):
        raise ValidationError("page.restrictions.json must contain a JSON object")
    body_manifest = manifest.get("body")
    if not isinstance(body_manifest, dict):
        raise ValidationError("manifest.json body must be an object")
    adf_manifest = body_manifest.get("atlas_doc_format")
    view_manifest = body_manifest.get("view")
    restrictions_manifest = manifest.get("restrictions")
    if not isinstance(adf_manifest, dict) or adf_manifest.get("sha256") != sha256_json(adf):
        raise ValidationError("page.adf.json differs from its immutable manifest evidence")
    if not isinstance(view_manifest, dict) or view_manifest.get("sha256") != sha256_text(view):
        raise ValidationError("page.view.html differs from its immutable manifest evidence")
    if (
        not isinstance(restrictions_manifest, dict)
        or restrictions_manifest.get("sha256") != sha256_json(restrictions)
    ):
        raise ValidationError(
            "page.restrictions.json differs from its immutable manifest evidence"
        )
    if has_extended_evidence:
        properties = load_json(workspace / PROPERTIES_NAME)
        operations = load_json(workspace / OPERATIONS_NAME)
        properties_manifest = manifest.get("properties")
        operations_manifest = manifest.get("operations")
        if (
            not isinstance(properties_manifest, dict)
            or properties_manifest.get("sha256") != sha256_json(properties)
        ):
            raise ValidationError(
                "page.properties.json differs from its immutable manifest evidence"
            )
        if (
            not isinstance(operations_manifest, dict)
            or operations_manifest.get("sha256") != sha256_json(operations)
        ):
            raise ValidationError(
                "page.operations.json differs from its immutable manifest evidence"
            )
    storage = (workspace / STORAGE_NAME).read_text(encoding="utf-8")
    summary = storage_summary(storage)
    validate_storage_link_targets(storage)
    labels = _validated_labels(
        load_json(workspace / LABELS_NAME), "page.labels.json"
    )
    state = _validated_content_state(
        load_json(workspace / STATE_NAME), "page.content-state.json"
    )
    editable_baselines(manifest)
    attachment_dir = workspace / ATTACHMENTS_DIR
    local_paths = _attachment_files(workspace)
    local_names: set[str] = set()
    local_folded: set[str] = set()
    for path in local_paths:
        filename = safe_filename(path.name)
        folded = filename.casefold()
        if folded in local_folded:
            raise ValidationError(
                f"attachment filenames collide on case-insensitive filesystems: {filename!r}"
            )
        local_names.add(filename)
        local_folded.add(folded)
    attachment_records = manifest.get("attachments", [])
    if not isinstance(attachment_records, list):
        raise ValidationError("manifest.json attachments must be an array")
    known_names: set[str] = set()
    known_folded: set[str] = set()
    for item in attachment_records:
        if not isinstance(item, dict):
            raise ValidationError("manifest.json contains an invalid attachment record")
        filename = safe_filename(str(item.get("filename") or ""))
        folded = filename.casefold()
        if folded in known_folded:
            raise ValidationError(f"manifest.json contains duplicate attachment: {filename}")
        expected_path = f"{ATTACHMENTS_DIR}/{filename}"
        if item.get("path") not in {None, expected_path}:
            raise ValidationError(
                f"manifest attachment {filename!r} must use path {expected_path!r}"
            )
        attachment_id = str(item.get("id") or "").strip()
        attachment_version = item.get("version")
        if bool(attachment_id) != (attachment_version is not None):
            raise ValidationError(
                f"manifest attachment {filename!r} has an incomplete remote version lock"
            )
        if attachment_version is not None:
            try:
                parsed_version = int(attachment_version)
            except (TypeError, ValueError) as exc:
                raise ValidationError(
                    f"manifest attachment {filename!r} version must be a positive integer"
                ) from exc
            if parsed_version <= 0:
                raise ValidationError(
                    f"manifest attachment {filename!r} version must be a positive integer"
                )
        known_names.add(filename)
        known_folded.add(folded)
    missing_known = sorted(known_names - local_names)
    if missing_known:
        raise ValidationError(
            "manifest attachments are missing local bytes: " + ", ".join(missing_known)
        )
    unavailable = sorted(set(summary["attachment_filenames"]) - local_names)
    if unavailable:
        raise ValidationError(
            "storage XML references unavailable attachments: " + ", ".join(unavailable)
        )
    gt = load_json(workspace / GT_NAME)
    if not isinstance(gt, dict) or gt.get("schema_version") != SCHEMA_VERSION:
        raise ValidationError("ground-truth.json has an unsupported schema")
    gt_storage = gt.get("storage") or {}
    if gt_storage.get("canonical_sha256") != summary["canonical_sha256"]:
        raise ValidationError("ground truth is stale for page.storage.xml; run capture-gt")
    if (gt.get("page") or {}).get("title") != meta["title"]:
        raise ValidationError("ground truth is stale for page.meta.json; run capture-gt")
    if sorted(gt.get("labels") or []) != sorted(labels):
        raise ValidationError("ground truth is stale for page.labels.json; run capture-gt")
    if not states_equivalent(gt.get("content_state"), state):
        raise ValidationError("ground truth is stale for page.content-state.json; run capture-gt")
    gt_attachments = {
        str(item.get("filename")): str(item.get("sha256"))
        for item in gt.get("attachments", [])
        if isinstance(item, dict) and item.get("filename")
    }
    local_attachments = {path.name: sha256_bytes(path.read_bytes()) for path in local_paths}
    if gt_attachments != local_attachments:
        raise ValidationError("ground truth is stale for attachments; run capture-gt")
    if not isinstance(gt.get("required_visible_text"), list):
        raise ValidationError("ground-truth.json required_visible_text must be an array")
    required_browser_check_ids(gt)
    return {
        "status": "valid",
        "workspace": str(workspace),
        "page_id": meta_page_id,
        "canonical_storage_sha256": summary["canonical_sha256"],
        "attachment_references": summary["attachment_filenames"],
        "local_attachments": sorted(local_names),
    }


def _validate_replace_target(output: Path) -> None:
    """Refuse dangerous download targets before an overwrite."""

    protected = {Path(output.anchor).resolve(), Path.home().resolve(), Path.cwd().resolve()}
    if output in protected or output.parent == output:
        raise ValidationError(f"refusing dangerous workspace output path: {output}")
    if output.exists() and not output.is_dir():
        raise ValidationError(f"workspace output exists and is not a directory: {output}")


def upload_plan(
    client: ConfluenceClient,
    workspace: Path,
    *,
    force: bool = False,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    """Build a mutation plan and enforce the optimistic lock."""

    validate_workspace(workspace)
    manifest = load_json(workspace / MANIFEST_NAME)
    meta = load_json(workspace / META_NAME)
    desired_labels = _validated_labels(
        load_json(workspace / LABELS_NAME), "page.labels.json"
    )
    desired_state = _validated_content_state(
        load_json(workspace / STATE_NAME), "page.content-state.json"
    )
    desired_digest = desired_state_sha256(workspace)
    resume_journal = _load_resume_journal(workspace, desired_digest)
    resume_steps = {
        str(step.get("id")): step
        for step in (resume_journal or {}).get("steps", [])
        if isinstance(step, dict) and step.get("id")
    }
    validate_workspace_tenant(client, manifest)
    baselines = editable_baselines(manifest)
    current_labels = client.labels(str(meta["page_id"]))
    current_state = client.content_state(str(meta["page_id"]))
    label_resume_step = resume_steps.get("labels") or {}
    state_resume_step = resume_steps.get("content-state") or {}
    labels_reconciled = bool(
        resume_journal
        and label_resume_step.get("kind") == "labels"
        and label_resume_step.get("status")
        in {"applied", "reconciled", "unknown-partial"}
        and sorted(current_labels) == desired_labels
    )
    state_reconciled = bool(
        resume_journal
        and state_resume_step.get("kind") == "content-state"
        and state_resume_step.get("status")
        in {"applied", "reconciled", "unknown-partial"}
        and states_equivalent(current_state, desired_state)
    )
    state_resume_detail = (
        state_resume_step.get("detail") if isinstance(state_resume_step, dict) else None
    )
    state_may_have_versioned = bool(
        state_reconciled
        and (
            state_resume_step.get("status") == "unknown-partial"
            or (
                isinstance(state_resume_detail, dict)
                and state_resume_detail.get("result") in {"updated", "removed"}
            )
        )
    )
    if baselines is not None:
        if (
            sorted(current_labels) != baselines["global_labels"]
            and not force
            and not labels_reconciled
        ):
            raise ConflictError(
                "remote global labels changed after download; download again or pass --force after review"
            )
        if (
            not states_equivalent(current_state, baselines["content_state"])
            and not force
            and not state_reconciled
        ):
            raise ConflictError(
                "remote content state changed after download; download again or pass --force after review"
            )
    current = client.page(str(meta["page_id"]), "storage")
    validate_supported_page(current, str(meta["page_id"]))
    manifest_page = manifest.get("page") or {}
    for local, remote in (("space_id", "spaceId"), ("parent_id", "parentId")):
        locked_value = manifest_page.get(local) if local in manifest_page else meta.get(local)
        if str(locked_value or "") != str(current.get(remote) or ""):
            raise ConflictError(
                f"remote {local} changed after download; download the page again before uploading"
            )
    storage = (workspace / STORAGE_NAME).read_text(encoding="utf-8")
    current_storage = body_value(current, "storage")
    body_changed = remote_equivalence_storage(storage) != remote_equivalence_storage(current_storage)
    meta_changed = str(meta.get("title") or "") != str(current.get("title") or "")
    draft_info = draft_observation(
        client.draft_page(str(meta["page_id"])), current, str(meta["page_id"])
    )
    if (body_changed or meta_changed) and draft_info["diverged"]:
        raise ConflictError(
            "a divergent Confluence editor draft would be overwritten by the planned page "
            "body/title update; publish or discard the draft and download again"
        )
    expected_version = int((manifest.get("page") or {}).get("version") or 0)
    current_version = int((current.get("version") or {}).get("number") or 0)
    page_resume_step = resume_steps.get("page") or {}
    page_resume_detail = (
        page_resume_step.get("detail") if isinstance(page_resume_step, dict) else None
    )
    recorded_page_version = (
        (page_resume_detail or {}).get("remote_version")
        if isinstance(page_resume_detail, dict)
        else None
    )
    try:
        recorded_page_version_int = (
            int(recorded_page_version) if recorded_page_version is not None else None
        )
    except (TypeError, ValueError):
        recorded_page_version_int = None
    reconciled_page_versions = {
        recorded_page_version_int or (expected_version + 1)
    }
    if state_may_have_versioned:
        reconciled_page_versions.update(
            version + 1 for version in tuple(reconciled_page_versions)
        )
    page_reconciled = bool(
        resume_journal
        and str(resume_journal.get("page_id") or "") == str(meta["page_id"])
        and page_resume_step.get("kind") == "page"
        and page_resume_step.get("status")
        in {"applied", "reconciled", "unknown-partial"}
        and current_version in reconciled_page_versions
        and not body_changed
        and not meta_changed
    )
    state_version_reconciled = bool(
        resume_journal
        and not page_resume_step
        and state_may_have_versioned
        and current_version == expected_version + 1
        and not body_changed
        and not meta_changed
    )
    if (
        expected_version != current_version
        and not force
        and not page_reconciled
        and not state_version_reconciled
    ):
        raise ConflictError(
            f"remote page is version {current_version}, but workspace was downloaded at "
            f"version {expected_version}; download again or pass --force after review"
        )
    remote_attachments = {str(item.get("title")): item for item in client.attachments(str(meta["page_id"]))}
    prior = {str(item.get("filename")): item for item in manifest.get("attachments", [])}
    attachment_changes = []
    reconciled_attachments: list[str] = []
    for path in sorted((workspace / ATTACHMENTS_DIR).iterdir()):
        if not path.is_file():
            continue
        digest = sha256_bytes(path.read_bytes())
        remote = remote_attachments.get(path.name)
        previous = prior.get(path.name)
        previous_id = str((previous or {}).get("id") or "").strip()
        previous_version = (previous or {}).get("version")
        has_remote_lock = bool(previous_id) and previous_version is not None
        divergence: str | None = None
        if has_remote_lock:
            if not remote:
                divergence = "was removed remotely"
            else:
                remote_id = str(remote.get("id") or "")
                remote_version = (remote.get("version") or {}).get("number")
                if previous_id != remote_id:
                    divergence = "remote attachment identity changed"
                elif str(previous_version) != str(remote_version):
                    divergence = (
                        f"remote attachment version changed from {previous_version} to {remote_version}"
                    )
        elif remote:
            divergence = "collides with an attachment created remotely after download"
        if divergence and remote:
            resume_step = resume_steps.get(f"attachment:{path.name}") or {}
            detail = resume_step.get("detail") if isinstance(resume_step, dict) else None
            recorded_id = str((detail or {}).get("remote_id") or "") if isinstance(detail, dict) else ""
            recorded_version = (
                (detail or {}).get("remote_version") if isinstance(detail, dict) else None
            )
            recorded_sha = str((detail or {}).get("sha256") or "") if isinstance(detail, dict) else ""
            remote_id = str(remote.get("id") or "")
            remote_version = (remote.get("version") or {}).get("number")
            reconciled_create = (
                resume_step.get("status") in {"applied", "reconciled"}
                and resume_step.get("action") == "create"
                and not has_remote_lock
                and resume_step.get("sha256") == digest
                and recorded_id
                and recorded_id == remote_id
            )
            reconciled_update = (
                resume_step.get("status") in {"applied", "reconciled"}
                and resume_step.get("action") == "update"
                and has_remote_lock
                and resume_step.get("sha256") == digest
                and recorded_sha == digest
                and recorded_id
                and recorded_id == previous_id == remote_id
                and recorded_version is not None
                and str(recorded_version) == str(remote_version)
            )
            if (reconciled_create or reconciled_update) and (
                sha256_bytes(client.download_attachment(remote)) == digest
            ):
                divergence = None
                reconciled_attachments.append(path.name)
        if divergence and not force:
            raise ConflictError(
                f"attachment {path.name!r} {divergence}; download the page again or pass --force after review"
            )
        media_type = str((previous or {}).get("media_type") or "") or (
            mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        )
        if path.name in reconciled_attachments:
            continue
        if not remote:
            attachment_changes.append(
                {"filename": path.name, "action": "create", "sha256": digest, "media_type": media_type}
            )
        elif divergence or not has_remote_lock or digest != (previous or {}).get("sha256"):
            attachment_changes.append(
                {"filename": path.name, "action": "update", "sha256": digest, "media_type": media_type}
            )
    plan = {
        "page_id": str(meta["page_id"]),
        "expected_version": expected_version,
        "current_version": current_version,
        "forced": bool(force),
        "page_update": body_changed or meta_changed,
        "reconciled_page_update": page_reconciled,
        "body_changed": body_changed,
        "metadata_changed": meta_changed,
        "draft": draft_info,
        "attachments": attachment_changes,
        "desired_state_sha256": desired_digest,
        "reconciled_attachments": sorted(reconciled_attachments),
        "resumed_from_operation_id": (
            resume_journal.get("operation_id") if resume_journal else None
        ),
    }
    context = {
        "manifest": manifest,
        "meta": meta,
        "current": current,
        "remote_attachments": remote_attachments,
        "current_labels": sorted(current_labels),
        "current_state": current_state,
    }
    return plan, context, {"storage": storage, "current_storage": current_storage}


def upload_workspace(
    client: ConfluenceClient,
    workspace: Path,
    *,
    message: str,
    force: bool = False,
    dry_run: bool = False,
    sync_attachments: bool = True,
    sync_labels: bool = True,
    sync_content_state: bool = True,
    verify: bool = True,
    expected_desired_state_sha256: str | None = None,
) -> dict[str, Any]:
    """Apply a reviewed local workspace to Confluence and verify it."""

    workspace = _resolve_workspace_root(workspace)
    plan, context, bodies = upload_plan(client, workspace, force=force)
    current_desired_digest = desired_state_sha256(workspace)
    if current_desired_digest != plan.get("desired_state_sha256"):
        raise ConflictError("workspace changed while its upload plan was being built")
    if (
        expected_desired_state_sha256 is not None
        and expected_desired_state_sha256 != current_desired_digest
    ):
        raise ConflictError("workspace desired state changed after batch preflight")
    desired_labels = list(load_json(workspace / LABELS_NAME))
    current_labels = list(context["current_labels"])
    label_changes = {
        "added": sorted(set(desired_labels) - set(current_labels)),
        "removed": sorted(set(current_labels) - set(desired_labels)),
    }
    desired_state = load_json(workspace / STATE_NAME)
    current_state = context["current_state"]
    state_would_change = not states_equivalent(desired_state, current_state)
    attachment_changes = list(plan["attachments"])
    plan["sync"] = {
        "attachments": sync_attachments,
        "labels": sync_labels,
        "content_state": sync_content_state,
    }
    plan["labels"] = label_changes if sync_labels else {"added": [], "removed": []}
    plan["content_state_changed"] = sync_content_state and state_would_change
    plan["suppressed_attachments"] = [] if sync_attachments else attachment_changes
    plan["suppressed_labels"] = (
        {"added": [], "removed": []} if sync_labels else label_changes
    )
    plan["suppressed_content_state_changed"] = (
        False if sync_content_state else state_would_change
    )
    if not sync_attachments:
        plan["attachments"] = []
    plan["remote_render_preflight_required"] = bool(
        plan["page_update"] and plan["body_changed"]
    )
    plan["no_op"] = not any(
        (
            plan["page_update"],
            plan["attachments"],
            plan["labels"]["added"],
            plan["labels"]["removed"],
            plan["content_state_changed"],
        )
    )
    if dry_run:
        return {"status": "dry-run", "plan": plan}
    suppressed = any(
        (
            plan["suppressed_attachments"],
            plan["suppressed_labels"]["added"],
            plan["suppressed_labels"]["removed"],
            plan["suppressed_content_state_changed"],
        )
    )
    if verify and suppressed:
        raise ValidationError(
            "skip flags suppress desired changes; use a complete upload or --no-verify after explicit review"
        )
    page_id = plan["page_id"]
    journal = _begin_operation(
        workspace,
        plan,
        desired_digest=str(plan["desired_state_sha256"]),
        sync_attachments=sync_attachments,
        sync_labels=sync_labels,
        sync_content_state=sync_content_state,
    )
    operation_id = str(journal["operation_id"])
    attachment_results: list[dict[str, str]] = []
    page_result: dict[str, Any] | None = None
    label_result = {"added": [], "removed": []}
    state_result = "skipped"
    remote_render_preflight: dict[str, Any] = {
        "status": (
            "pending" if plan["remote_render_preflight_required"] else "not-required"
        )
    }
    verification: dict[str, Any] = {"status": "skipped"}
    try:
        if plan["remote_render_preflight_required"]:
            _set_journal_step(
                workspace,
                journal,
                "remote-render-preflight",
                "started",
            )
            try:
                remote_render_preflight = client.preflight_storage_render(
                    page_id,
                    bodies["storage"],
                )
            except (RoundTripError, OSError, ValueError) as exc:
                remote_render_preflight = {"status": "failed"}
                if isinstance(exc, RemoteRenderPreflightError):
                    remote_render_preflight.update(
                        {
                            "reason": "unknown-macro-placeholder",
                            "render_safety": exc.diagnostic,
                        }
                    )
                _set_journal_step(
                    workspace,
                    journal,
                    "remote-render-preflight",
                    "failed",
                    remote_render_preflight,
                )
                raise
            _set_journal_step(
                workspace,
                journal,
                "remote-render-preflight",
                "applied",
                remote_render_preflight,
            )
        if plan["page_update"]:
            prewrite_draft = draft_observation(
                client.draft_page(page_id), context["current"], page_id
            )
            if prewrite_draft["diverged"]:
                raise ConflictError(
                    "a divergent Confluence editor draft appeared after planning; refusing "
                    "all mutations for the planned page body/title update"
                )
        if sync_attachments:
            changes_by_name = {item["filename"]: item for item in plan["attachments"]}
            for filename in sorted(changes_by_name):
                step_id = f"attachment:{filename}"
                change = changes_by_name[filename]
                planned_remote = context["remote_attachments"].get(filename)
                latest_remote = {
                    str(item.get("title")): item for item in client.attachments(page_id)
                }.get(filename)
                if planned_remote is None:
                    lock_matches = latest_remote is None
                else:
                    lock_matches = bool(latest_remote) and (
                        str(latest_remote.get("id") or "")
                        == str(planned_remote.get("id") or "")
                        and str((latest_remote.get("version") or {}).get("number"))
                        == str((planned_remote.get("version") or {}).get("number"))
                    )
                if not lock_matches:
                    raise ConflictError(
                        f"attachment {filename!r} changed between planning and its upload; "
                        "download the page again"
                    )
                _set_journal_step(workspace, journal, step_id, "started")
                client.upload_attachment(
                    page_id,
                    workspace / ATTACHMENTS_DIR / filename,
                    str(latest_remote.get("id")) if latest_remote else None,
                    comment=message,
                    media_type=change["media_type"],
                )
                remote_after = {
                    str(item.get("title")): item for item in client.attachments(page_id)
                }.get(filename)
                if not remote_after:
                    raise RoundTripError(
                        f"attachment {filename!r} was not visible after upload"
                    )
                actual_digest = sha256_bytes(client.download_attachment(remote_after))
                if actual_digest != change["sha256"]:
                    raise RoundTripError(
                        f"attachment {filename!r} bytes did not match immediately after upload"
                    )
                detail = {
                    "remote_id": str(remote_after.get("id") or ""),
                    "remote_version": (remote_after.get("version") or {}).get("number"),
                    "sha256": actual_digest,
                }
                _set_journal_step(workspace, journal, step_id, "applied", detail)
                attachment_results.append(
                    {"filename": filename, "action": change["action"]}
                )
        if plan["page_update"]:
            latest_draft = draft_observation(
                client.draft_page(page_id), context["current"], page_id
            )
            if latest_draft["diverged"]:
                raise ConflictError(
                    "a divergent Confluence editor draft appeared after planning; refusing "
                    "the page body/title update"
                )
            _set_journal_step(workspace, journal, "page", "started")
            page_result = client.update_page(
                page_id,
                context["meta"],
                bodies["storage"],
                int((context["current"].get("version") or {}).get("number") or 0),
                message,
            )
            _set_journal_step(
                workspace,
                journal,
                "page",
                "applied",
                {"remote_version": (page_result.get("version") or {}).get("number")},
            )
        if sync_labels:
            labels_before = client.labels(page_id)
            if (
                sorted(labels_before) != sorted(context["current_labels"])
                and not plan["forced"]
            ):
                raise ConflictError(
                    "remote global labels changed between planning and mutation; retry from a fresh plan"
                )
            _set_journal_step(
                workspace,
                journal,
                "labels",
                "started",
                {"before": sorted(labels_before)},
            )
            label_result = client.sync_labels(
                page_id,
                list(load_json(workspace / LABELS_NAME)),
                labels_before,
            )
            labels_after = client.labels(page_id)
            _set_journal_step(
                workspace,
                journal,
                "labels",
                "applied",
                {
                    "before": sorted(labels_before),
                    "after": sorted(labels_after),
                    "changes": label_result,
                },
            )
        if sync_content_state:
            state_before = client.content_state(page_id)
            if (
                not states_equivalent(state_before, context["current_state"])
                and not plan["forced"]
            ):
                raise ConflictError(
                    "remote content state changed between planning and mutation; retry from a fresh plan"
                )
            _set_journal_step(
                workspace,
                journal,
                "content-state",
                "started",
                {"before": state_before},
            )
            state_result = client.set_content_state(
                page_id,
                load_json(workspace / STATE_NAME),
                state_before,
            )
            state_after = client.content_state(page_id)
            _set_journal_step(
                workspace,
                journal,
                "content-state",
                "applied",
                {
                    "before": state_before,
                    "after": state_after,
                    "result": state_result,
                },
            )
        if verify:
            _set_journal_step(workspace, journal, "api-verification", "started")
            verification = verify_workspace(
                client,
                workspace,
                operation_id=operation_id,
                desired_digest=str(plan["desired_state_sha256"]),
            )
            if verification.get("status") != "verified":
                _set_journal_step(
                    workspace,
                    journal,
                    "api-verification",
                    "failed",
                    {"report_status": verification.get("status")},
                )
                journal["status"] = "verification-failed"
                _write_journal(workspace, journal)
            else:
                _set_journal_step(
                    workspace,
                    journal,
                    "api-verification",
                    "verified",
                    {"remote_version": verification.get("remote_version")},
                )
                refresh_manifest(
                    client,
                    workspace,
                    verified_report=verification,
                    operation_id=operation_id,
                )
                journal["status"] = "api-verified"
                journal["api_verified_at"] = verification.get("verified_at")
                _write_journal(workspace, journal)
        else:
            journal["status"] = "unverified"
            _write_journal(workspace, journal)
    except (RoundTripError, OSError, ValueError) as exc:
        unknown_partial = False
        for step in journal.get("steps", []):
            if (
                isinstance(step, dict)
                and step.get("kind") in {"attachment", "page", "labels", "content-state"}
                and step.get("status") == "started"
            ):
                step["status"] = "unknown-partial"
                step["updated_at"] = utc_now()
                step["uncertain"] = True
                unknown_partial = True
        applied = any(
            isinstance(step, dict)
            and step.get("status") in {"applied", "reconciled", "verified"}
            for step in journal.get("steps", [])
        )
        journal["status"] = "partial" if applied or unknown_partial else "failed"
        journal["error"] = {"type": type(exc).__name__, "message": str(exc)}
        _write_journal(workspace, journal)
        return {
            "status": journal["status"],
            "operation_id": operation_id,
            "page_id": page_id,
            "page_updated": page_result is not None,
            "attachments": attachment_results,
            "labels": label_result,
            "content_state": state_result,
            "remote_render_preflight": remote_render_preflight,
            "verification": verification,
            "error": journal["error"],
        }
    return {
        "status": (
            "uploaded"
            if verification.get("status") == "verified"
            else "unverified"
            if verification.get("status") == "skipped"
            else "verification-failed"
        ),
        "operation_id": operation_id,
        "page_id": page_id,
        "page_updated": page_result is not None,
        "attachments": attachment_results,
        "labels": label_result,
        "content_state": state_result,
        "remote_render_preflight": remote_render_preflight,
        "verification": verification,
    }


def reconcile_remote_render_safety(
    client: ConfluenceClient,
    workspace: Path,
) -> dict[str, Any]:
    """Backfill proven render-safety evidence for a legacy preflight journal."""

    workspace = _resolve_workspace_root(workspace)
    validate_workspace(workspace)
    manifest = load_json(workspace / MANIFEST_NAME)
    validate_workspace_tenant(client, manifest)
    reconciliation_id = f"render-safety-reconciliation-{uuid4()}"
    _acquire_operation_lock(workspace, reconciliation_id)
    try:
        verification = _verification_dir(workspace)
        journal_path = verification / JOURNAL_NAME
        report_path = verification / REPORT_NAME
        upload_path = verification / "upload.json"
        journal = load_json(journal_path)
        report = load_json(report_path)
        upload_receipt = load_json(upload_path)
        meta = load_json(workspace / META_NAME)
        if (
            not isinstance(journal, dict)
            or not isinstance(report, dict)
            or not isinstance(upload_receipt, dict)
        ):
            raise ValidationError(
                "render-safety reconciliation requires object journal, API, and upload evidence"
            )
        desired_digest = desired_state_sha256(workspace)
        page_id = str(meta.get("page_id") or "")
        operation_id = str(journal.get("operation_id") or "")
        if (
            journal.get("status") != "api-verified"
            or not journal.get("remote_render_preflight_required")
            or journal.get("remote_render_safety_contract_version") is not None
        ):
            raise ValidationError(
                "render-safety reconciliation requires an API-verified legacy preflight journal"
            )
        if (
            report.get("status") != "verified"
            or not operation_id
            or str(report.get("operation_id") or "") != operation_id
            or str(report.get("page_id") or "") != page_id
            or journal.get("desired_state_sha256") != desired_digest
            or report.get("desired_state_sha256") != desired_digest
            or manifest.get("last_verified_operation_id") != operation_id
            or manifest.get("last_verified_desired_state_sha256") != desired_digest
            or upload_receipt.get("status") != "uploaded"
            or str(upload_receipt.get("operation_id") or "") != operation_id
            or str(upload_receipt.get("page_id") or "") != page_id
        ):
            raise ValidationError(
                "legacy render-safety evidence is not bound to the current verified operation"
            )
        gate = validate_completion_gate(workspace)
        unrelated_errors = [
            error
            for error in gate.get("errors", [])
            if not str(error).startswith("mutation journal remote render preflight")
        ]
        if unrelated_errors:
            raise ValidationError(
                "cannot reconcile render safety while other completion evidence is invalid: "
                + "; ".join(str(error) for error in unrelated_errors)
            )
        render_steps = [
            step
            for step in journal.get("steps", [])
            if isinstance(step, dict) and step.get("id") == "remote-render-preflight"
        ]
        if len(render_steps) != 1:
            raise ValidationError(
                "legacy mutation journal has no unique remote render preflight step"
            )
        render_step = render_steps[0]
        detail = render_step.get("detail")
        if (
            render_step.get("status") != "applied"
            or not isinstance(detail, dict)
            or detail.get("status") != "completed"
            or detail.get("representation") != "view"
            or not re.fullmatch(
                r"[0-9a-f]{64}", str(detail.get("rendered_sha256") or "")
            )
            or not isinstance(detail.get("rendered_bytes"), int)
            or isinstance(detail.get("rendered_bytes"), bool)
            or detail.get("rendered_bytes") < 0
        ):
            raise ValidationError(
                "legacy mutation journal has invalid remote render evidence"
            )

        manifest_version = int((manifest.get("page") or {}).get("version") or 0)
        report_version = int(report.get("remote_version") or 0)
        local_storage = (workspace / STORAGE_NAME).read_text(encoding="utf-8")

        def require_current_remote_snapshot() -> None:
            current = client.page(page_id, "storage")
            validate_supported_page(current, page_id)
            current_version = int(
                (current.get("version") or {}).get("number") or 0
            )
            if (
                current_version != manifest_version
                or current_version != report_version
                or str(current.get("title") or "")
                != str(meta.get("title") or "")
                or remote_equivalence_storage(body_value(current, "storage"))
                != remote_equivalence_storage(local_storage)
            ):
                raise ConflictError(
                    "remote page changed after the verified legacy operation; download again"
                )

        require_current_remote_snapshot()

        rendered = client.preflight_storage_render(page_id, local_storage)
        if (
            rendered.get("status") != "completed"
            or rendered.get("representation") != "view"
            or not _render_safety_passed(rendered.get("render_safety"))
            or rendered.get("rendered_sha256") != detail.get("rendered_sha256")
            or rendered.get("rendered_bytes") != detail.get("rendered_bytes")
        ):
            raise ConflictError(
                "current safe render does not exactly match the legacy preflight evidence"
            )
        require_current_remote_snapshot()

        historical_upload_render = upload_receipt.get("remote_render_preflight")
        if (
            not isinstance(historical_upload_render, dict)
            or historical_upload_render.get("status") != "completed"
            or historical_upload_render.get("representation") != "view"
            or historical_upload_render.get("rendered_sha256")
            != detail.get("rendered_sha256")
            or historical_upload_render.get("rendered_bytes")
            != detail.get("rendered_bytes")
        ):
            raise ValidationError(
                "legacy upload receipt does not match its journaled remote render"
            )

        replayed_at = utc_now()
        artifact = {
            "schema_version": SCHEMA_VERSION,
            "status": "verified-reconciliation",
            "page_id": page_id,
            "operation_id": operation_id,
            "desired_state_sha256": desired_digest,
            "replayed_at": replayed_at,
            "page_mutated": False,
            "source_storage": {
                "path": f"../{STORAGE_NAME}",
                "sha256": sha256_bytes((workspace / STORAGE_NAME).read_bytes()),
            },
            "historical_journal": {
                "path": JOURNAL_NAME,
                "sha256": sha256_bytes(journal_path.read_bytes()),
                "rendered_sha256": detail["rendered_sha256"],
            },
            "historical_upload_receipt": {
                "path": "upload.json",
                "sha256": sha256_bytes(upload_path.read_bytes()),
                "rendered_sha256": detail["rendered_sha256"],
            },
            "fresh_remote_render": rendered,
            "digest_match": True,
        }
        artifact_path = verification / RENDER_SAFETY_RECONCILIATION_NAME
        write_json(artifact_path, artifact)
        artifact_record = {
            "path": RENDER_SAFETY_RECONCILIATION_NAME,
            "sha256": sha256_bytes(artifact_path.read_bytes()),
        }
        return {
            "status": "reconciled",
            "page_id": page_id,
            "operation_id": operation_id,
            "desired_state_sha256": desired_digest,
            "artifact": artifact_record,
            "render_safety": rendered["render_safety"],
        }
    finally:
        _release_operation_lock(workspace, reconciliation_id)


def verify_workspace(
    client: ConfluenceClient,
    workspace: Path,
    *,
    operation_id: str | None = None,
    desired_digest: str | None = None,
) -> dict[str, Any]:
    """Verify remote storage, render, labels, state, and attachment bytes."""

    workspace = _resolve_workspace_root(workspace)
    validate_workspace(workspace)
    validate_workspace_tenant(client, load_json(workspace / MANIFEST_NAME))
    current_desired_digest = desired_state_sha256(workspace)
    if desired_digest is not None and desired_digest != current_desired_digest:
        raise ConflictError("workspace changed after the upload operation began")
    desired_digest = current_desired_digest
    managed_journal: dict[str, Any] | None = None
    if operation_id is None:
        meta_for_plan = load_json(workspace / META_NAME)
        managed_journal = _begin_operation(
            workspace,
            {
                "page_id": str(meta_for_plan["page_id"]),
                "desired_state_sha256": desired_digest,
                "page_update": False,
                "attachments": [],
                "reconciled_attachments": [],
            },
            desired_digest=desired_digest,
            sync_attachments=False,
            sync_labels=False,
            sync_content_state=False,
        )
        operation_id = str(managed_journal["operation_id"])
        _set_journal_step(
            workspace, managed_journal, "api-verification", "started"
        )
    meta = load_json(workspace / META_NAME)
    page_id = str(meta["page_id"])
    local_storage = (workspace / STORAGE_NAME).read_text(encoding="utf-8")
    storage_page = client.page(page_id, "storage")
    adf_page = client.page(page_id, "atlas_doc_format")
    view_page = client.page(page_id, "view")
    validate_representation_snapshot(
        {"storage": storage_page, "atlas_doc_format": adf_page, "view": view_page},
        page_id,
    )
    remote_storage = body_value(storage_page, "storage")
    remote_adf = normalize_adf(body_value(adf_page, "atlas_doc_format"))
    remote_view = body_value(view_page, "view")
    remote_restrictions = client.restrictions(page_id)
    remote_properties = storage_page.get("properties")
    remote_operations = storage_page.get("operations")
    remote_text = visible_text(remote_view)
    remote_view_safety = rendered_view_safety(remote_view)
    desired_labels = list(load_json(workspace / LABELS_NAME))
    desired_state = load_json(workspace / STATE_NAME)
    gt = load_json(workspace / GT_NAME)
    manifest = load_json(workspace / MANIFEST_NAME)
    prior_attachments = {
        str(item.get("filename")): item
        for item in manifest.get("attachments", [])
        if isinstance(item, dict) and item.get("filename")
    }
    checks: list[dict[str, Any]] = []

    def check(name: str, passed: bool, detail: Any) -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    local_canonical = storage_summary(local_storage)["canonical_sha256"]
    remote_canonical = storage_summary(remote_storage)["canonical_sha256"]
    local_equivalent = sha256_text(remote_equivalence_storage(local_storage))
    remote_equivalent = sha256_text(remote_equivalence_storage(remote_storage))
    check(
        "storage-equivalent",
        local_equivalent == remote_equivalent,
        {
            "expected": local_equivalent,
            "actual": remote_equivalent,
            "exact_canonical_expected": local_canonical,
            "exact_canonical_actual": remote_canonical,
        },
    )
    check("title", str(meta["title"]) == str(storage_page.get("title")), str(storage_page.get("title")))
    check(
        "space-id",
        str(meta.get("space_id") or "") == str(storage_page.get("spaceId") or ""),
        {"expected": meta.get("space_id"), "actual": storage_page.get("spaceId")},
    )
    check(
        "parent-id",
        str(meta.get("parent_id") or "") == str(storage_page.get("parentId") or ""),
        {"expected": meta.get("parent_id"), "actual": storage_page.get("parentId")},
    )
    remote_labels = client.labels(page_id)
    check("labels", sorted(desired_labels) == remote_labels, {"expected": sorted(desired_labels), "actual": remote_labels})
    remote_state = client.content_state(page_id)
    check("content-state", states_equivalent(desired_state, remote_state), {"expected": desired_state, "actual": remote_state})
    local_restrictions = load_json(workspace / RESTRICTIONS_NAME)
    check(
        "restrictions-unchanged",
        sha256_json(local_restrictions) == sha256_json(remote_restrictions),
        {
            "expected": sha256_json(local_restrictions),
            "actual": sha256_json(remote_restrictions),
        },
    )
    check(
        "view-render-safety",
        _render_safety_passed(remote_view_safety),
        remote_view_safety,
    )
    for required in gt.get("required_visible_text", []):
        check(f"visible-text:{required}", str(required) in remote_text, str(required))

    remote_items = {str(item.get("title")): item for item in client.attachments(page_id)}
    verified_attachments: list[dict[str, Any]] = []
    for referenced in storage_summary(remote_storage)["attachment_filenames"]:
        check(f"attachment-reference:{referenced}", referenced in remote_items, "exists remotely")
    for local_path in sorted((workspace / ATTACHMENTS_DIR).iterdir()):
        if not local_path.is_file():
            continue
        item = remote_items.get(local_path.name)
        if not item:
            check(f"attachment:{local_path.name}", False, "missing remotely")
            continue
        expected_media_type = str((prior_attachments.get(local_path.name) or {}).get("media_type") or "") or (
            mimetypes.guess_type(local_path.name)[0] or "application/octet-stream"
        )
        actual_media_type = str(item.get("mediaType") or "")
        remote_id = str(item.get("id") or "")
        remote_attachment_version = (item.get("version") or {}).get("number")
        check(
            f"attachment-identity:{local_path.name}",
            bool(remote_id)
            and isinstance(remote_attachment_version, int)
            and not isinstance(remote_attachment_version, bool)
            and remote_attachment_version > 0,
            {"id": remote_id, "version": remote_attachment_version},
        )
        check(
            f"attachment-media-type:{local_path.name}",
            expected_media_type == actual_media_type,
            {"expected": expected_media_type, "actual": actual_media_type},
        )
        remote_payload = client.download_attachment(item)
        expected = sha256_bytes(local_path.read_bytes())
        actual = sha256_bytes(remote_payload)
        check(
            f"attachment:{local_path.name}",
            expected == actual,
            {
                "expected": expected,
                "actual": actual,
                "id": remote_id,
                "version": remote_attachment_version,
                "media_type": actual_media_type,
            },
        )
        verified_attachments.append(
            {
                "filename": local_path.name,
                "id": remote_id,
                "version": remote_attachment_version,
                "sha256": actual,
                "media_type": actual_media_type,
            }
        )

    verify_dir = _verification_dir(workspace, create=True)
    write_text(verify_dir / REMOTE_STORAGE_NAME, remote_storage)
    write_json(verify_dir / REMOTE_ADF_NAME, remote_adf)
    write_text(verify_dir / REMOTE_VIEW_NAME, remote_view)
    write_json(verify_dir / REMOTE_RESTRICTIONS_NAME, remote_restrictions)
    write_json(verify_dir / REMOTE_PROPERTIES_NAME, remote_properties)
    write_json(verify_dir / REMOTE_OPERATIONS_NAME, remote_operations)
    evidence = {
        "storage": {
            "path": REMOTE_STORAGE_NAME,
            "sha256": sha256_bytes((verify_dir / REMOTE_STORAGE_NAME).read_bytes()),
        },
        "atlas_doc_format": {
            "path": REMOTE_ADF_NAME,
            "sha256": sha256_bytes((verify_dir / REMOTE_ADF_NAME).read_bytes()),
        },
        "view": {
            "path": REMOTE_VIEW_NAME,
            "sha256": sha256_bytes((verify_dir / REMOTE_VIEW_NAME).read_bytes()),
        },
        "restrictions": {
            "path": REMOTE_RESTRICTIONS_NAME,
            "sha256": sha256_bytes((verify_dir / REMOTE_RESTRICTIONS_NAME).read_bytes()),
        },
        "properties": {
            "path": REMOTE_PROPERTIES_NAME,
            "sha256": sha256_bytes((verify_dir / REMOTE_PROPERTIES_NAME).read_bytes()),
        },
        "operations": {
            "path": REMOTE_OPERATIONS_NAME,
            "sha256": sha256_bytes((verify_dir / REMOTE_OPERATIONS_NAME).read_bytes()),
        },
    }
    report = {
        "schema_version": SCHEMA_VERSION,
        "verified_at": utc_now(),
        "operation_id": operation_id,
        "desired_state_sha256": desired_digest,
        "page_id": page_id,
        "remote_version": int((storage_page.get("version") or {}).get("number") or 0),
        "storage_summary": storage_summary(remote_storage),
        "adf_summary": adf_summary(remote_adf),
        "verified_attachments": verified_attachments,
        "evidence": evidence,
        "checks": checks,
        "status": "verified" if all(item["passed"] for item in checks) else "failed",
    }
    write_json(verify_dir / REPORT_NAME, report)
    if managed_journal is not None:
        if report["status"] == "verified":
            _set_journal_step(
                workspace,
                managed_journal,
                "api-verification",
                "verified",
                {"remote_version": report["remote_version"]},
            )
            refresh_manifest(
                client,
                workspace,
                verified_report=report,
                operation_id=str(operation_id),
            )
            managed_journal["status"] = "api-verified"
            managed_journal["api_verified_at"] = report["verified_at"]
        else:
            _set_journal_step(
                workspace,
                managed_journal,
                "api-verification",
                "failed",
                {"report_status": report["status"]},
            )
            managed_journal["status"] = "verification-failed"
        _write_journal(workspace, managed_journal)
    return report


def record_browser_ground_truth(
    workspace: Path,
    *,
    page_url: str,
    checks: list[str],
    baseline: Path,
    final_screenshots: list[Path],
) -> dict[str, Any]:
    """Bind authenticated browser observations to the current API operation."""

    workspace = _resolve_workspace_root(workspace)
    validate_workspace(workspace)
    verification = _verification_dir(workspace)
    api_path = verification / REPORT_NAME
    api = load_json(api_path)
    meta = load_json(workspace / META_NAME)
    ground_truth = load_json(workspace / GT_NAME)
    if not isinstance(api, dict) or api.get("status") != "verified":
        raise ValidationError("record-browser-gt requires a current verified API report")
    if not isinstance(page_url, str) or not page_url.strip():
        raise ValidationError("record-browser-gt requires the authenticated page URL")
    normalized_checks = [value.strip() for value in checks if isinstance(value, str)]
    if not normalized_checks or any(not value for value in normalized_checks):
        raise ValidationError("record-browser-gt requires non-empty --check values")
    if len(normalized_checks) != len(checks) or len(set(normalized_checks)) != len(normalized_checks):
        raise ValidationError("record-browser-gt check IDs must be unique non-empty strings")
    missing = sorted(set(required_browser_check_ids(ground_truth)) - set(normalized_checks))
    if missing:
        raise ValidationError("record-browser-gt is missing required checks: " + ", ".join(missing))
    if not final_screenshots:
        raise ValidationError("record-browser-gt requires at least one final screenshot")

    def screenshot_record(path: Path) -> dict[str, str]:
        resolved = path.resolve() if path.is_absolute() else (workspace / path).resolve()
        try:
            relative = resolved.relative_to(verification)
        except ValueError as exc:
            raise ValidationError("browser screenshots must be inside verification/") from exc
        if not resolved.is_file():
            raise ValidationError(f"browser screenshot is missing: {relative.as_posix()}")
        payload = resolved.read_bytes()
        if not screenshot_is_decodable(payload):
            raise ValidationError(f"browser screenshot is not a decodable PNG or JPEG: {relative.as_posix()}")
        return {"path": relative.as_posix(), "sha256": sha256_bytes(payload)}

    baseline_record = screenshot_record(baseline)
    final_records = [screenshot_record(path) for path in final_screenshots]
    if any(
        record["path"] == baseline_record["path"]
        or record["sha256"] == baseline_record["sha256"]
        for record in final_records
    ):
        raise ValidationError("baseline and final screenshots must be distinct")
    record = {
        "schema_version": SCHEMA_VERSION,
        "status": "verified",
        "page_id": str(meta.get("page_id") or ""),
        "page_url": page_url.strip(),
        "operation_id": str(api.get("operation_id") or ""),
        "api_report_sha256": sha256_bytes(api_path.read_bytes()),
        "remote_version": api.get("remote_version"),
        "desired_state_sha256": api.get("desired_state_sha256"),
        "verified_at": utc_now(),
        "baseline": baseline_record,
        "final_screenshots": final_records,
        "checks": [{"name": name, "passed": True} for name in normalized_checks],
    }
    write_json(verification / BROWSER_GT_NAME, record)
    validation = validate_browser_ground_truth(workspace)
    if validation.get("status") != "verified":
        raise ValidationError(
            "recorded browser ground truth did not validate: "
            + "; ".join(str(item) for item in validation.get("errors", []))
        )
    return validation


def validate_browser_ground_truth(workspace: Path) -> dict[str, Any]:
    """Validate the local authenticated-browser completion record and screenshots."""

    workspace = _resolve_workspace_root(workspace)
    try:
        verification = _verification_dir(workspace)
    except ValidationError as exc:
        return {
            "status": "failed",
            "page_id": "",
            "operation_id": "",
            "browser_checks": 0,
            "screenshots": 0,
            "errors": [str(exc)],
        }
    browser_path = verification / BROWSER_GT_NAME
    api_path = verification / REPORT_NAME
    errors: list[str] = []
    try:
        browser = load_json(browser_path)
        api = load_json(api_path)
        meta = load_json(workspace / META_NAME)
        manifest = load_json(workspace / MANIFEST_NAME)
        ground_truth = load_json(workspace / GT_NAME)
    except ValidationError as exc:
        return {
            "status": "failed",
            "page_id": "",
            "operation_id": "",
            "browser_checks": 0,
            "screenshots": 0,
            "errors": [str(exc)],
        }
    if not isinstance(browser, dict):
        return {
            "status": "failed",
            "page_id": "",
            "operation_id": "",
            "browser_checks": 0,
            "screenshots": 0,
            "errors": [f"{browser_path} must contain a JSON object"],
        }
    if not isinstance(api, dict):
        errors.append("verification/report.json must contain a JSON object")
        api = {}

    expected_page_id = str(meta.get("page_id") or "")
    browser_page_id = str(browser.get("page_id") or "")
    browser_operation_id = str(browser.get("operation_id") or "")
    api_operation_id = str(api.get("operation_id") or "")
    if browser.get("schema_version") != SCHEMA_VERSION:
        errors.append("browser verification has an unsupported schema version")
    if browser.get("status") != "verified":
        errors.append("browser verification status is not verified")
    if browser_page_id != expected_page_id:
        errors.append("browser verification refers to a different page ID")
    if not browser_operation_id or browser_operation_id != api_operation_id:
        errors.append("browser verification refers to a different API operation")
    api_report_digest = sha256_bytes(api_path.read_bytes()) if api_path.is_file() else ""
    if browser.get("api_report_sha256") != api_report_digest:
        errors.append("browser verification is not bound to the current API report")
    if browser.get("desired_state_sha256") != api.get("desired_state_sha256"):
        errors.append("browser verification is not bound to the verified desired state")
    try:
        browser_remote_version = int(browser.get("remote_version") or 0)
        api_remote_version = int(api.get("remote_version") or 0)
    except (TypeError, ValueError):
        browser_remote_version = api_remote_version = 0
    if browser_remote_version <= 0 or browser_remote_version != api_remote_version:
        errors.append("browser verification is not bound to the verified remote version")
    try:
        api_time = parse_utc_timestamp(api.get("verified_at"), "API verified_at")
        browser_time = parse_utc_timestamp(
            browser.get("verified_at"), "browser verified_at"
        )
        if browser_time < api_time:
            errors.append("browser verification predates API verification")
    except ValidationError as exc:
        errors.append(str(exc))

    page_url = browser.get("page_url")
    if not isinstance(page_url, str) or not page_url:
        errors.append("browser verification has no page URL")
    else:
        try:
            manifest_origin = _https_origin(normalize_base_url(str(manifest.get("base_url") or "")))
            if _https_origin(page_url) != manifest_origin:
                errors.append("browser page URL belongs to a different Confluence tenant")
            parsed_path = urlparse(page_url).path.rstrip("/")
            if not re.search(rf"(?:^|/)pages/{re.escape(expected_page_id)}(?:/|$)", parsed_path):
                errors.append("browser page URL does not identify the expected page ID")
        except ValidationError as exc:
            errors.append(str(exc))

    checks = browser.get("checks")
    if not isinstance(checks, list) or not checks:
        errors.append("browser verification has no checks")
        checks = []
    else:
        if any(not isinstance(check, dict) or check.get("passed") is not True for check in checks):
            errors.append("one or more browser checks failed")
        check_ids = [
            str(check.get("name"))
            for check in checks
            if isinstance(check, dict) and check.get("name")
        ]
        if len(check_ids) != len(set(check_ids)):
            errors.append("browser verification contains duplicate check IDs")
        try:
            required_ids = required_browser_check_ids(ground_truth)
        except ValidationError as exc:
            errors.append(str(exc))
            required_ids = []
        missing_ids = sorted(set(required_ids) - set(check_ids))
        if missing_ids:
            errors.append(
                "browser verification is missing required check IDs: "
                + ", ".join(missing_ids)
            )

    screenshot_records: list[dict[str, Any]] = []
    baseline = browser.get("baseline")
    if isinstance(baseline, dict):
        screenshot_records.append(baseline)
    else:
        errors.append("browser verification has no baseline screenshot")
    finals = browser.get("final_screenshots")
    if isinstance(finals, list) and finals:
        for record in finals:
            if isinstance(record, dict):
                screenshot_records.append(record)
            else:
                errors.append("final_screenshots contains a non-object record")
    else:
        errors.append("browser verification has no final screenshots")

    screenshot_identities: list[tuple[str, str]] = []
    verification_root = verification.resolve()
    for record in screenshot_records:
        relative = record.get("path")
        expected = str(record.get("sha256") or "").lower()
        if not isinstance(relative, str) or not relative:
            errors.append("a screenshot record has no path")
            continue
        if not re.fullmatch(r"[0-9a-f]{64}", expected):
            errors.append(f"screenshot record has an invalid SHA-256 digest: {relative}")
            continue
        relative_path = Path(relative)
        if relative_path.is_absolute():
            errors.append(f"screenshot path must be relative to verification/: {relative}")
            continue
        screenshot = (verification / relative_path).resolve()
        try:
            screenshot.relative_to(verification_root)
        except ValueError:
            errors.append(f"screenshot path escapes verification/: {relative}")
            continue
        if not screenshot.is_file():
            errors.append(f"screenshot is missing: {relative}")
            continue
        payload = screenshot.read_bytes()
        actual = sha256_bytes(payload)
        if actual != expected:
            errors.append(f"screenshot digest mismatch: {relative}")
            continue
        if not screenshot_is_decodable(payload):
            errors.append(f"screenshot is not a decodable PNG or JPEG: {relative}")
            continue
        screenshot_identities.append((str(screenshot), actual))
    if len(screenshot_identities) >= 2:
        baseline_identity = screenshot_identities[0]
        for final_identity in screenshot_identities[1:]:
            if final_identity[0] == baseline_identity[0] or final_identity[1] == baseline_identity[1]:
                errors.append("baseline and final screenshots must be distinct")
                break

    return {
        "status": "verified" if not errors else "failed",
        "page_id": browser_page_id,
        "operation_id": browser_operation_id,
        "remote_version": browser_remote_version,
        "desired_state_sha256": browser.get("desired_state_sha256"),
        "verified_at": browser.get("verified_at"),
        "browser_checks": len(checks),
        "screenshots": len(screenshot_records),
        "errors": errors,
    }


def validate_completion_gate(workspace: Path) -> dict[str, Any]:
    """Require current local state, API verification, and browser ground truth to agree."""

    workspace = _resolve_workspace_root(workspace)
    errors: list[str] = []
    try:
        validate_workspace(workspace)
        api = load_json(workspace / VERIFY_DIR / "report.json")
        meta = load_json(workspace / META_NAME)
        labels = load_json(workspace / LABELS_NAME)
        state = load_json(workspace / STATE_NAME)
        ground_truth = load_json(workspace / GT_NAME)
        manifest = load_json(workspace / MANIFEST_NAME)
        journal = load_json(workspace / VERIFY_DIR / JOURNAL_NAME)
    except ValidationError as exc:
        return {
            "status": "failed",
            "page_id": "",
            "api_checks": 0,
            "browser_checks": 0,
            "screenshots": 0,
            "errors": [str(exc)],
        }
    if not isinstance(api, dict):
        return {
            "status": "failed",
            "page_id": "",
            "api_checks": 0,
            "browser_checks": 0,
            "screenshots": 0,
            "errors": ["verification/report.json must contain a JSON object"],
        }

    page_id = str(meta.get("page_id") or "")
    current_desired_digest = desired_state_sha256(workspace)
    api_operation_id = str(api.get("operation_id") or "")
    if api.get("schema_version") != SCHEMA_VERSION:
        errors.append("API verification has an unsupported schema version")
    if api.get("status") != "verified":
        errors.append("API verification status is not verified")
    if str(api.get("page_id") or "") != page_id:
        errors.append("API verification refers to a different page ID")
    if not api_operation_id:
        errors.append("API verification has no operation ID")
    if api.get("desired_state_sha256") != current_desired_digest:
        errors.append("API verification is stale for the desired workspace state")
    try:
        remote_version = int(api.get("remote_version") or 0)
    except (TypeError, ValueError):
        remote_version = 0
    if remote_version <= 0:
        errors.append("API verification has no positive remote version")
    try:
        manifest_version = int((manifest.get("page") or {}).get("version") or 0)
    except (TypeError, ValueError):
        manifest_version = 0
    if manifest_version != remote_version:
        errors.append("API remote version does not match the manifest version lock")
    if manifest.get("last_verified_operation_id") != api_operation_id:
        errors.append("manifest is not bound to the current API operation")
    if manifest.get("last_verified_desired_state_sha256") != current_desired_digest:
        errors.append("manifest is not bound to the current desired workspace state")
    if not isinstance(journal, dict):
        errors.append("mutation journal must contain a JSON object")
        journal = {}
    if journal.get("status") != "api-verified":
        errors.append("mutation journal is not API-verified")
    if str(journal.get("operation_id") or "") != api_operation_id:
        errors.append("mutation journal refers to a different API operation")
    if journal.get("desired_state_sha256") != current_desired_digest:
        errors.append("mutation journal is stale for the desired workspace state")
    if journal.get("remote_render_preflight_required"):
        render_steps = [
            step
            for step in journal.get("steps", [])
            if isinstance(step, dict) and step.get("id") == "remote-render-preflight"
        ]
        if len(render_steps) != 1:
            errors.append("mutation journal has no unique remote render preflight step")
        else:
            render_step = render_steps[0]
            detail = render_step.get("detail")
            render_safety = (
                detail.get("render_safety") if isinstance(detail, dict) else None
            )
            basic_render_evidence_valid = not (
                render_step.get("status") != "applied"
                or not isinstance(detail, dict)
                or detail.get("status") != "completed"
                or detail.get("representation") != "view"
                or not re.fullmatch(
                    r"[0-9a-f]{64}",
                    str(detail.get("rendered_sha256") or ""),
                )
                or not isinstance(detail.get("rendered_bytes"), int)
                or isinstance(detail.get("rendered_bytes"), bool)
                or detail.get("rendered_bytes") < 0
                or not isinstance(detail.get("polls"), int)
                or isinstance(detail.get("polls"), bool)
                or detail.get("polls") <= 0
            )
            contract_version = journal.get("remote_render_safety_contract_version")
            if not basic_render_evidence_valid:
                errors.append("mutation journal remote render preflight is not completed")
            elif (
                isinstance(contract_version, int)
                and not isinstance(contract_version, bool)
                and contract_version == 1
            ):
                if not _render_safety_passed(render_safety):
                    errors.append(
                        "mutation journal remote render preflight is not completed"
                    )
                if (
                    _verification_dir(workspace)
                    / RENDER_SAFETY_RECONCILIATION_NAME
                ).exists():
                    errors.append(
                        "mutation journal remote render preflight has unexpected legacy reconciliation"
                    )
            elif contract_version is None:
                artifact_path = (
                    _verification_dir(workspace)
                    / RENDER_SAFETY_RECONCILIATION_NAME
                )
                upload_path = _verification_dir(workspace) / "upload.json"
                artifact: Any = None
                upload_receipt: Any = None
                reconciliation_valid = True
                try:
                    _reject_symlink(
                        artifact_path,
                        "remote render safety reconciliation",
                    )
                    _reject_symlink(upload_path, "legacy upload receipt")
                    if not artifact_path.is_file() or not upload_path.is_file():
                        reconciliation_valid = False
                    else:
                        artifact = load_json(artifact_path)
                        upload_receipt = load_json(upload_path)
                except (OSError, ValidationError):
                    reconciliation_valid = False
                if not isinstance(artifact, dict) or not isinstance(
                    upload_receipt, dict
                ):
                    reconciliation_valid = False
                    artifact = {}
                    upload_receipt = {}
                if reconciliation_valid:
                    try:
                        parse_utc_timestamp(
                            artifact.get("replayed_at"),
                            "render-safety replayed_at",
                        )
                    except ValidationError:
                        reconciliation_valid = False
                source_storage = artifact.get("source_storage")
                historical_journal = artifact.get("historical_journal")
                historical_upload = artifact.get("historical_upload_receipt")
                fresh_render = artifact.get("fresh_remote_render")
                upload_render = upload_receipt.get("remote_render_preflight")
                reconciliation_valid = bool(
                    reconciliation_valid
                    and set(artifact)
                    == {
                        "schema_version",
                        "status",
                        "page_id",
                        "operation_id",
                        "desired_state_sha256",
                        "replayed_at",
                        "page_mutated",
                        "source_storage",
                        "historical_journal",
                        "historical_upload_receipt",
                        "fresh_remote_render",
                        "digest_match",
                    }
                    and artifact.get("schema_version") == SCHEMA_VERSION
                    and artifact.get("status") == "verified-reconciliation"
                    and str(artifact.get("page_id") or "") == page_id
                    and str(artifact.get("operation_id") or "")
                    == api_operation_id
                    and artifact.get("desired_state_sha256")
                    == current_desired_digest
                    and artifact.get("page_mutated") is False
                    and artifact.get("digest_match") is True
                    and isinstance(source_storage, dict)
                    and set(source_storage) == {"path", "sha256"}
                    and source_storage.get("path") == f"../{STORAGE_NAME}"
                    and source_storage.get("sha256")
                    == sha256_bytes((workspace / STORAGE_NAME).read_bytes())
                    and isinstance(historical_journal, dict)
                    and set(historical_journal)
                    == {"path", "sha256", "rendered_sha256"}
                    and historical_journal.get("path") == JOURNAL_NAME
                    and historical_journal.get("sha256")
                    == sha256_bytes(
                        (_verification_dir(workspace) / JOURNAL_NAME).read_bytes()
                    )
                    and historical_journal.get("rendered_sha256")
                    == detail.get("rendered_sha256")
                    and isinstance(historical_upload, dict)
                    and set(historical_upload)
                    == {"path", "sha256", "rendered_sha256"}
                    and historical_upload.get("path") == "upload.json"
                    and historical_upload.get("sha256")
                    == sha256_bytes(upload_path.read_bytes())
                    and historical_upload.get("rendered_sha256")
                    == detail.get("rendered_sha256")
                    and upload_receipt.get("status") == "uploaded"
                    and str(upload_receipt.get("page_id") or "") == page_id
                    and str(upload_receipt.get("operation_id") or "")
                    == api_operation_id
                    and isinstance(upload_render, dict)
                    and upload_render.get("status") == "completed"
                    and upload_render.get("representation") == "view"
                    and upload_render.get("rendered_sha256")
                    == detail.get("rendered_sha256")
                    and upload_render.get("rendered_bytes")
                    == detail.get("rendered_bytes")
                    and isinstance(fresh_render, dict)
                    and set(fresh_render)
                    == {
                        "status",
                        "representation",
                        "rendered_sha256",
                        "rendered_bytes",
                        "polls",
                        "render_safety",
                    }
                    and fresh_render.get("status") == "completed"
                    and fresh_render.get("representation") == "view"
                    and fresh_render.get("rendered_sha256")
                    == detail.get("rendered_sha256")
                    and fresh_render.get("rendered_bytes")
                    == detail.get("rendered_bytes")
                    and isinstance(fresh_render.get("polls"), int)
                    and not isinstance(fresh_render.get("polls"), bool)
                    and fresh_render.get("polls") > 0
                    and _render_safety_passed(fresh_render.get("render_safety"))
                )
                if not reconciliation_valid:
                    errors.append(
                        "mutation journal remote render preflight has no valid legacy safety reconciliation"
                    )
            else:
                errors.append(
                    "mutation journal remote render preflight has an unsupported safety contract"
                )
    try:
        started_at = parse_utc_timestamp(journal.get("started_at"), "journal started_at")
        api_verified_at = parse_utc_timestamp(api.get("verified_at"), "API verified_at")
        if api_verified_at < started_at:
            errors.append("API verification predates the mutation operation")
    except ValidationError as exc:
        errors.append(str(exc))

    evidence = api.get("evidence")
    required_evidence = {
        "storage": REMOTE_STORAGE_NAME,
        "atlas_doc_format": REMOTE_ADF_NAME,
        "view": REMOTE_VIEW_NAME,
        "restrictions": REMOTE_RESTRICTIONS_NAME,
    }
    if all(key in manifest for key in ("properties", "operations")):
        required_evidence.update(
            {
                "properties": REMOTE_PROPERTIES_NAME,
                "operations": REMOTE_OPERATIONS_NAME,
            }
        )
    if not isinstance(evidence, dict):
        errors.append("API verification has no evidence inventory")
        evidence = {}
    verification_root = _verification_dir(workspace).resolve()
    for key, expected_name in required_evidence.items():
        record = evidence.get(key)
        if not isinstance(record, dict) or record.get("path") != expected_name:
            errors.append(f"API verification has invalid {key} evidence metadata")
            continue
        evidence_path = (verification_root / expected_name).resolve()
        try:
            evidence_path.relative_to(verification_root)
        except ValueError:
            errors.append(f"API verification evidence escapes verification/: {key}")
            continue
        if not evidence_path.is_file():
            errors.append(f"API verification evidence is missing: {expected_name}")
            continue
        if record.get("sha256") != sha256_bytes(evidence_path.read_bytes()):
            errors.append(f"API verification evidence digest mismatch: {expected_name}")

    remote_view_path = verification_root / REMOTE_VIEW_NAME
    try:
        _reject_symlink(remote_view_path, "API verified remote view")
        if remote_view_path.is_file():
            remote_view_safety = rendered_view_safety(
                remote_view_path.read_text(encoding="utf-8")
            )
            if not _render_safety_passed(remote_view_safety):
                errors.append(
                    "API verified remote view contains an unknown-macro placeholder"
                )
    except (OSError, UnicodeError, ValueError, ValidationError) as exc:
        errors.append(f"API verified remote view is unreadable: {exc}")

    api_checks = api.get("checks")
    if not isinstance(api_checks, list) or not api_checks:
        errors.append("API verification has no checks")
        api_checks = []
    elif any(not isinstance(check, dict) or check.get("passed") is not True for check in api_checks):
        errors.append("one or more API checks failed")
    checks_by_name = {
        str(check.get("name")): check
        for check in api_checks
        if isinstance(check, dict) and check.get("name")
    }
    restrictions_detail = (checks_by_name.get("restrictions-unchanged") or {}).get(
        "detail"
    )
    if "restrictions-unchanged" not in checks_by_name:
        errors.append("API verification is missing the restrictions integrity check")
    elif (
        not isinstance(restrictions_detail, dict)
        or restrictions_detail.get("expected")
        != sha256_json(load_json(workspace / RESTRICTIONS_NAME))
    ):
        errors.append("API verification is stale for page.restrictions.json")

    storage_check = checks_by_name.get("storage-equivalent") or {}
    storage_detail = storage_check.get("detail") if isinstance(storage_check, dict) else None
    expected_storage = sha256_text(
        remote_equivalence_storage((workspace / STORAGE_NAME).read_text(encoding="utf-8"))
    )
    if not isinstance(storage_detail, dict) or storage_detail.get("expected") != expected_storage:
        errors.append("API verification is stale for page.storage.xml")
    title_check = checks_by_name.get("title") or {}
    if title_check.get("detail") != meta.get("title"):
        errors.append("API verification is stale for page.meta.json")
    for key, check_name in (("space_id", "space-id"), ("parent_id", "parent-id")):
        detail = (checks_by_name.get(check_name) or {}).get("detail")
        if not isinstance(detail, dict) or str(detail.get("expected") or "") != str(meta.get(key) or ""):
            errors.append(f"API verification is stale for {key}")
    label_detail = (checks_by_name.get("labels") or {}).get("detail")
    expected_labels = label_detail.get("expected") if isinstance(label_detail, dict) else None
    if not isinstance(expected_labels, list) or sorted(expected_labels) != sorted(labels):
        errors.append("API verification is stale for page.labels.json")
    state_detail = (checks_by_name.get("content-state") or {}).get("detail")
    if not isinstance(state_detail, dict) or not states_equivalent(state_detail.get("expected"), state):
        errors.append("API verification is stale for page.content-state.json")

    for required in ground_truth.get("required_visible_text", []):
        if f"visible-text:{required}" not in checks_by_name:
            errors.append(f"API verification is missing visible-text assertion: {required}")
    for path in sorted((workspace / ATTACHMENTS_DIR).iterdir()):
        if not path.is_file():
            continue
        detail = (checks_by_name.get(f"attachment:{path.name}") or {}).get("detail")
        if not isinstance(detail, dict) or detail.get("expected") != sha256_bytes(path.read_bytes()):
            errors.append(f"API verification is stale for attachment: {path.name}")

    browser = validate_browser_ground_truth(workspace)
    errors.extend(str(error) for error in browser.get("errors", []))
    if browser.get("page_id") and browser.get("page_id") != page_id:
        errors.append("API and browser verification refer to different page IDs")
    if browser.get("operation_id") and browser.get("operation_id") != api_operation_id:
        errors.append("API and browser verification refer to different operations")
    if browser.get("remote_version") and int(browser["remote_version"]) != remote_version:
        errors.append("API and browser verification refer to different remote versions")
    if browser.get("desired_state_sha256") and browser.get("desired_state_sha256") != current_desired_digest:
        errors.append("browser verification is stale for the desired workspace state")
    return {
        "status": "verified" if not errors else "failed",
        "page_id": page_id,
        "api_checks": len(api_checks),
        "browser_checks": int(browser.get("browser_checks") or 0),
        "screenshots": int(browser.get("screenshots") or 0),
        "errors": errors,
    }


def validate_workspace_tenant(client: ConfluenceClient, manifest: dict[str, Any]) -> None:
    """Reject a workspace from another tenant before making any page request."""

    workspace_base_url = normalize_base_url(str(manifest.get("base_url") or ""))
    if workspace_base_url != normalize_base_url(client.base_url):
        raise ValidationError("workspace belongs to a different Confluence tenant")


def refresh_manifest(
    client: ConfluenceClient,
    workspace: Path,
    *,
    verified_report: dict[str, Any] | None = None,
    operation_id: str | None = None,
) -> None:
    """Advance optimistic-lock metadata after a successful verification."""

    workspace = _resolve_workspace_root(workspace)
    manifest = load_json(workspace / MANIFEST_NAME)
    meta = load_json(workspace / META_NAME)
    verified_report = verified_report or load_json(workspace / VERIFY_DIR / REPORT_NAME)
    operation_id = operation_id or str(verified_report.get("operation_id") or "")
    if not operation_id or verified_report.get("status") != "verified":
        raise ValidationError("manifest refresh requires a verified API operation")
    if verified_report.get("desired_state_sha256") != desired_state_sha256(workspace):
        raise ConflictError("workspace changed after API verification")
    page = client.page(str(meta["page_id"]), "storage")
    validate_supported_page(page, str(meta["page_id"]))
    verified_version = int(verified_report.get("remote_version") or 0)
    current_version = int((page.get("version") or {}).get("number") or 0)
    if verified_version <= 0 or current_version != verified_version:
        raise ConflictError(
            "remote page version changed between API verification and manifest refresh"
        )
    checks = {
        str(check.get("name")): check
        for check in verified_report.get("checks", [])
        if isinstance(check, dict) and check.get("name")
    }
    label_detail = (checks.get("labels") or {}).get("detail")
    state_detail = (checks.get("content-state") or {}).get("detail")
    if not isinstance(label_detail, dict) or not isinstance(
        label_detail.get("actual"), list
    ):
        raise ValidationError("verified report has no global-label baseline evidence")
    if not isinstance(state_detail, dict) or "actual" not in state_detail:
        raise ValidationError("verified report has no content-state baseline evidence")
    verified_labels = _validated_labels(
        label_detail["actual"], "verified report labels.actual"
    )
    verified_state = _validated_content_state(
        state_detail["actual"], "verified report content-state.actual"
    )
    current_labels = client.labels(str(meta["page_id"]))
    current_state = client.content_state(str(meta["page_id"]))
    if sorted(current_labels) != verified_labels:
        raise ConflictError(
            "remote global labels changed between API verification and manifest refresh"
        )
    if not states_equivalent(current_state, verified_state):
        raise ConflictError(
            "remote content state changed between API verification and manifest refresh"
        )

    raw_verified_attachments = verified_report.get("verified_attachments")
    if not isinstance(raw_verified_attachments, list):
        raise ValidationError("verified report has no attachment identity inventory")
    verified_attachments: dict[str, dict[str, Any]] = {}
    for record in raw_verified_attachments:
        if not isinstance(record, dict):
            raise ValidationError("verified report contains an invalid attachment record")
        filename = safe_filename(str(record.get("filename") or ""))
        if filename in verified_attachments:
            raise ValidationError(
                f"verified report contains duplicate attachment: {filename}"
            )
        remote_id = str(record.get("id") or "")
        remote_version = record.get("version")
        digest = str(record.get("sha256") or "")
        media_type = str(record.get("media_type") or "")
        if (
            not remote_id
            or not isinstance(remote_version, int)
            or isinstance(remote_version, bool)
            or remote_version <= 0
            or not re.fullmatch(r"[0-9a-f]{64}", digest)
            or not media_type
        ):
            raise ValidationError(
                f"verified report has an incomplete attachment identity: {filename}"
            )
        verified_attachments[filename] = record

    local_paths = _attachment_files(workspace)
    local_names = {path.name for path in local_paths}
    if local_names != set(verified_attachments):
        raise ConflictError(
            "local attachment inventory changed after API verification"
        )
    remote = {
        str(item.get("title")): item
        for item in client.attachments(str(meta["page_id"]))
    }
    records = []
    for path in local_paths:
        verified = verified_attachments[path.name]
        item = remote.get(path.name)
        if not item:
            raise ConflictError(
                f"attachment {path.name!r} disappeared after API verification"
            )
        payload = client.download_attachment(item)
        actual_version = (item.get("version") or {}).get("number")
        actual_media_type = str(item.get("mediaType") or "")
        if (
            str(item.get("id") or "") != str(verified["id"])
            or str(actual_version) != str(verified["version"])
            or actual_media_type != str(verified["media_type"])
            or sha256_bytes(payload) != str(verified["sha256"])
            or sha256_bytes(path.read_bytes()) != str(verified["sha256"])
        ):
            raise ConflictError(
                f"attachment {path.name!r} changed between API verification and manifest refresh"
            )
        records.append(attachment_record(item, path.name, payload))

    storage = (workspace / STORAGE_NAME).read_text(encoding="utf-8")
    manifest["page"] = {
        **page_meta(page),
        "version": current_version,
        "web_url": urljoin(client.base_url, str((page.get("_links") or {}).get("webui") or "")),
    }
    manifest["body"]["storage"] = {
        "path": STORAGE_NAME,
        "sha256": sha256_text(storage),
        **storage_summary(storage),
    }
    manifest["attachments"] = records
    manifest["editable_baselines"] = {
        "global_labels": verified_labels,
        "content_state": verified_state,
    }
    manifest["draft_observation"] = draft_observation(
        client.draft_page(str(meta["page_id"])), page, str(meta["page_id"])
    )
    manifest["last_verified_at"] = utc_now()
    manifest["last_verified_operation_id"] = operation_id
    manifest["last_verified_desired_state_sha256"] = verified_report.get(
        "desired_state_sha256"
    )
    write_json(workspace / MANIFEST_NAME, manifest)


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", help="Site root; prefer CONFLUENCE_BASE_URL")
    parser.add_argument("--username", help="Account email; prefer CONFLUENCE_USERNAME")
    parser.add_argument("--env-file", type=Path, help="Dotenv file containing Confluence credentials")
    parser.add_argument("--timeout", type=int, default=60)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("doctor", help="Check credentials and site availability")

    download = commands.add_parser("download", help="Download a page workspace")
    download.add_argument("page_id")
    download.add_argument("output", type=Path)
    download.add_argument("--overwrite", action="store_true")
    download.add_argument("--skip-attachments", action="store_true")

    validate = commands.add_parser("validate", help="Validate a local page workspace")
    validate.add_argument("workspace", type=Path)

    capture = commands.add_parser("capture-gt", help="Capture local ground-truth invariants")
    capture.add_argument("workspace", type=Path)
    capture.add_argument("--visible-text", action="append", default=None)

    browser = commands.add_parser(
        "record-browser-gt",
        help="Bind authenticated browser checks and screenshots to current API evidence",
    )
    browser.add_argument("workspace", type=Path)
    browser.add_argument("page_url")
    browser.add_argument("--check", action="append", required=True)
    browser.add_argument("--baseline", type=Path, required=True)
    browser.add_argument("--final-screenshot", type=Path, action="append", required=True)

    upload = commands.add_parser("upload", help="Upload and verify a page workspace")
    upload.add_argument("workspace", type=Path)
    upload.add_argument("--message", default="Updated through roundtrip-confluence-pages")
    upload.add_argument("--force", action="store_true")
    upload.add_argument("--dry-run", action="store_true")
    upload.add_argument("--skip-attachments", action="store_true")
    upload.add_argument("--skip-labels", action="store_true")
    upload.add_argument("--skip-content-state", action="store_true")
    upload.add_argument("--no-verify", action="store_true")
    upload.add_argument("--output", type=Path, help="Write the JSON result to this path")

    verify = commands.add_parser("verify", help="Verify a workspace against the remote page")
    verify.add_argument("workspace", type=Path)

    reconcile = commands.add_parser(
        "reconcile-render-safety",
        help="Backfill exact render-safety evidence for a legacy verified preflight",
    )
    reconcile.add_argument("workspace", type=Path)

    complete = commands.add_parser(
        "completion-gate",
        help="Validate the local API and authenticated-browser completion records",
    )
    complete.add_argument("workspace", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the standalone round-trip CLI."""

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "validate":
            result = validate_workspace(args.workspace)
        elif args.command == "capture-gt":
            result = capture_ground_truth(args.workspace, args.visible_text)
        elif args.command == "record-browser-gt":
            result = record_browser_ground_truth(
                args.workspace,
                page_url=args.page_url,
                checks=args.check,
                baseline=args.baseline,
                final_screenshots=args.final_screenshot,
            )
        elif args.command == "completion-gate":
            result = validate_completion_gate(args.workspace)
        else:
            if args.command == "upload" and args.output is not None:
                validate_upload_output_path(args.workspace, args.output)
            base_url, username, token = credentials_from_args(args)
            client = ConfluenceClient(base_url, username, token, timeout=args.timeout)
            if args.command == "doctor":
                result = client.doctor()
            elif args.command == "download":
                result = download_page(
                    client,
                    args.page_id,
                    args.output,
                    overwrite=args.overwrite,
                    include_attachments=not args.skip_attachments,
                )
            elif args.command == "upload":
                result = upload_workspace(
                    client,
                    args.workspace,
                    message=args.message,
                    force=args.force,
                    dry_run=args.dry_run,
                    sync_attachments=not args.skip_attachments,
                    sync_labels=not args.skip_labels,
                    sync_content_state=not args.skip_content_state,
                    verify=not args.no_verify,
                )
            elif args.command == "verify":
                result = verify_workspace(client, args.workspace)
            elif args.command == "reconcile-render-safety":
                result = reconcile_remote_render_safety(client, args.workspace)
            else:
                parser.error(f"unknown command: {args.command}")
                return 2
        if args.command == "upload" and args.output is not None:
            write_upload_cli_result(args.workspace, args.output, result)
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return (
            0
            if result.get("status")
            not in {"failed", "partial", "verification-failed", "unverified"}
            else 2
        )
    except (RoundTripError, OSError, ValueError) as exc:
        error_result = {
            "status": "failed",
            "error": str(exc),
            "type": type(exc).__name__,
        }
        if args.command == "upload" and args.output is not None:
            try:
                write_upload_cli_result(args.workspace, args.output, error_result)
            except (RoundTripError, OSError, ValueError) as output_exc:
                error_result["output_error"] = str(output_exc)
        print(json.dumps(error_result, ensure_ascii=False, sort_keys=True), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
