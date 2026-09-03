"""Bounded, read-only HTTP transport for Confluence Cloud."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
import logging
import math
import random
import threading
import time
from typing import Any, Iterator
from urllib.parse import parse_qs, urljoin, urlsplit

import requests

from ..errors import KnowledgeError

_LOG = logging.getLogger(__name__)
_RETRY_STATUSES = {408, 429, 500, 502, 503, 504}
_PERMANENT_SITE_ERRORS = {
    "SUSPENDED_INACTIVITY": (
        "Confluence Cloud subscription is deactivated due to inactivity "
        "(SUSPENDED_INACTIVITY); reactivate it in Atlassian Administration"
    ),
}
_NO_PRODUCT_ACCESS_FRAGMENT = "caller cannot access Confluence"
_TRANSIENT_ERRORS = (
    requests.Timeout,
    requests.ConnectionError,
    requests.exceptions.ChunkedEncodingError,
)


class _IncompleteJSON(Exception):
    """A possibly truncated successful response that can be retried safely."""


class ConfluenceRequestError(KnowledgeError):
    """A sanitized remote failure, optionally fatal to the current request group."""

    def __init__(self, reason: str, *, status: int | None = None, fatal: bool = False) -> None:
        self.status = status
        self.fatal = fatal
        super().__init__(reason)


@dataclass(frozen=True)
class ConfluenceOptions:
    """Validated limits shared by Confluence discovery and downloads."""

    workers: int = 4
    page_size: int = 25
    timeout: float = 60.0
    connect_timeout: float = 10.0
    max_retries: int = 4
    max_retry_wait: float = 120.0
    max_pages: int = 0

    def __post_init__(self) -> None:
        for name, minimum, maximum in (
            ("workers", 1, 16),
            ("page_size", 1, 250),
            ("max_retries", 0, 10),
            ("max_pages", 0, None),
        ):
            value = getattr(self, name)
            if type(value) is not int or value < minimum or (maximum is not None and value > maximum):
                bound = f"{minimum}..{maximum}" if maximum is not None else f">= {minimum}"
                raise ValueError(f"Confluence {name} must be an integer in {bound}")
        for name in ("timeout", "connect_timeout", "max_retry_wait"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
                raise ValueError(f"Confluence {name} must be a finite positive number")

    @classmethod
    def from_config(cls, config: dict[str, Any]) -> ConfluenceOptions:
        """Read explicit controls while preserving the historical meaning of limit."""
        values = {name: config[name] for name in cls.__dataclass_fields__ if config.get(name) is not None}
        legacy_limit = config.get("limit")
        if legacy_limit is not None:
            if type(legacy_limit) is not int or legacy_limit < 1:
                raise ValueError("Confluence limit must be a positive integer")
            if config.get("cql"):
                values.setdefault("max_pages", legacy_limit)
            else:
                values.setdefault("page_size", min(legacy_limit, 250))
        return cls(**values)


def normalize_confluence_base_url(value: str) -> str:
    """Accept a site root or /wiki URL without duplicating the API prefix."""
    parsed = urlsplit(value)
    if (
        parsed.scheme not in {"https", "http"}
        or not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
        or parsed.query
        or parsed.fragment
    ):
        raise ValueError("Confluence base URL must be an HTTP(S) site URL without credentials, query, or fragment")
    # Accessing port also rejects malformed port values before any request.
    parsed.port
    path = parsed.path.rstrip("/")
    if path.endswith("/wiki"):
        path = path[:-5]
    return parsed._replace(path=path + "/", query="", fragment="").geturl()


def retry_after_seconds(value: str | None) -> float | None:
    """Parse Retry-After seconds or an HTTP date; ignore invalid server values."""
    if not isinstance(value, str):
        return None
    try:
        seconds = float(value)
    except ValueError:
        try:
            moment = parsedate_to_datetime(value)
            if moment.tzinfo is None:
                moment = moment.replace(tzinfo=UTC)
            seconds = max(0.0, (moment - datetime.now(UTC)).total_seconds())
        except (TypeError, ValueError, OverflowError):
            return None
    return seconds if math.isfinite(seconds) and seconds >= 0 else None


def permanent_site_error(response: requests.Response) -> str | None:
    """Return a sanitized explanation for a known permanent Atlassian response."""
    try:
        payload = response.json()
    except ValueError:
        return None
    if not isinstance(payload, dict):
        return None
    known = _PERMANENT_SITE_ERRORS.get(payload.get("errorCode"))
    if known:
        return known
    message = payload.get("message")
    if response.status_code == 403 and isinstance(message, str) and _NO_PRODUCT_ACCESS_FRAGMENT in message:
        return (
            "Configured account cannot access Confluence; grant Confluence app access to "
            "CONFLUENCE_USERNAME in Atlassian Administration or update the configured credentials"
        )
    return None


class ConfluenceClient:
    """Reuse one session per thread and coordinate a bounded shared cooldown.

    Only GET is exposed. Pagination cannot change origin, endpoint, or filters,
    and redirects are never followed with configured credentials.
    """

    def __init__(
        self, base_url: str, auth: tuple[str, str], options: ConfluenceOptions | None = None
    ) -> None:
        self.base_url = normalize_confluence_base_url(base_url)
        self.auth = auth
        self.options = options or ConfluenceOptions()
        self._local = threading.local()
        self._lock = threading.Lock()
        self._cancelled = threading.Event()
        self._sessions: list[requests.Session] = []
        self._cooldown_until = 0.0
        self.requests = 0
        self.retries = 0

    def __enter__(self) -> ConfluenceClient:
        return self

    def __exit__(self, *_exc: object) -> None:
        self.close()

    def close(self) -> None:
        """Close pooled connections after all download workers have stopped."""
        self.cancel()
        for session in self._sessions:
            session.close()
        self._sessions.clear()

    def cancel(self) -> None:
        """Interrupt cooldown waits and prevent further requests in this group."""
        self._cancelled.set()

    def url(self, path: str) -> str:
        """Build an API URL below the configured Confluence site."""
        return urljoin(self.base_url, "wiki/" + path.lstrip("/"))

    def _session(self) -> requests.Session:
        if not hasattr(self._local, "session"):
            session = requests.Session()
            adapter = requests.adapters.HTTPAdapter(pool_connections=1, pool_maxsize=1, max_retries=0)
            session.mount("https://", adapter)
            session.mount("http://", adapter)
            self._local.session = session
            with self._lock:
                self._sessions.append(session)
        return self._local.session

    def _wait(self, seconds: float) -> None:
        if self._cancelled.wait(seconds):
            raise ConfluenceRequestError("Confluence request group was stopped", fatal=True)

    def _wait_for_cooldown(self, budget: float) -> float:
        waited = 0.0
        while True:
            if self._cancelled.is_set():
                raise ConfluenceRequestError("Confluence request group was stopped", fatal=True)
            with self._lock:
                delay = max(0.0, self._cooldown_until - time.monotonic())
            if delay <= 0:
                return waited
            if delay > budget - waited:
                self.cancel()
                raise ConfluenceRequestError(
                    "Confluence cooldown exceeds max_retry_wait; retry this sync later", status=429, fatal=True
                )
            started = time.monotonic()
            self._wait(min(delay, 1.0))
            waited += time.monotonic() - started

    def get_json(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """GET one JSON object with bounded retries and sanitized diagnostics."""
        waited = 0.0
        for attempt in range(self.options.max_retries + 1):
            waited += self._wait_for_cooldown(self.options.max_retry_wait - waited)
            response = None
            status = None
            retry_after = None
            try:
                with self._lock:
                    self.requests += 1
                response = self._session().get(
                    self.url(path),
                    headers={"Accept": "application/json"},
                    params=params,
                    auth=self.auth,
                    timeout=(self.options.connect_timeout, self.options.timeout),
                    allow_redirects=False,
                )
                status = response.status_code
                retry_after = retry_after_seconds(response.headers.get("Retry-After"))
                site_error = permanent_site_error(response) if status in {403, 503} else None
                if site_error:
                    self.cancel()
                    raise ConfluenceRequestError(site_error, status=status, fatal=True)
                if 200 <= status < 300:
                    try:
                        payload = response.json()
                    except ValueError:
                        raise _IncompleteJSON from None
                    if not isinstance(payload, dict):
                        raise ConfluenceRequestError("Confluence returned a non-object JSON response")
                    # v2 also advertises pagination in the standard Link header.
                    links = payload.get("_links") or {}
                    if not isinstance(links, dict):
                        raise ConfluenceRequestError("Confluence returned malformed pagination links")
                    header_next = response.links.get("next", {}).get("url")
                    if header_next and not (payload.get("_links") or {}).get("next"):
                        payload["_links"] = {**(payload.get("_links") or {}), "next": header_next}
                    return payload
                reason = f"Confluence HTTP {status}"
                if status not in _RETRY_STATUSES:
                    if status == 401:
                        self.cancel()
                    raise ConfluenceRequestError(reason, status=status, fatal=status == 401)
            except _IncompleteJSON:
                reason = "Confluence returned invalid JSON"
                status = None
                retry_after = None
            except requests.exceptions.SSLError:
                raise ConfluenceRequestError("Confluence TLS certificate validation failed") from None
            except _TRANSIENT_ERRORS as exc:
                reason = f"Confluence {type(exc).__name__}"
            finally:
                if response is not None:
                    response.close()

            if attempt == self.options.max_retries:
                if status == 429:
                    self.cancel()
                raise ConfluenceRequestError(
                    f"{reason} after {attempt + 1} attempt(s)", status=status, fatal=status == 429
                ) from None
            delay = max(retry_after or 0.0, min(30.0, 2.0 ** attempt) * random.uniform(0.5, 1.0))
            if delay > self.options.max_retry_wait - waited:
                self.cancel()
                raise ConfluenceRequestError(
                    f"{reason}; required retry wait {delay:.1f}s exceeds max_retry_wait; retry this sync later",
                    status=status,
                    fatal=True,
                ) from None
            with self._lock:
                self.retries += 1
                if status == 429 or retry_after is not None:
                    self._cooldown_until = max(self._cooldown_until, time.monotonic() + delay)
            _LOG.warning("%s; retry %d/%d in %.1fs", reason, attempt + 1, self.options.max_retries, delay)
            if status != 429 and retry_after is None:
                self._wait(delay)
                waited += delay
        raise AssertionError("unreachable")

    def iter_batches(self, path: str, params: dict[str, Any]) -> Iterator[list[dict[str, Any]]]:
        """Follow validated cursor/offset links while retaining every scope filter."""
        current = dict(params)
        seen: set[tuple[tuple[str, str], ...]] = set()
        while True:
            marker = tuple(sorted((key, str(value)) for key, value in current.items()))
            if marker in seen:
                raise ConfluenceRequestError("Confluence pagination repeated a cursor or offset")
            seen.add(marker)
            payload = self.get_json(path, current)
            results = payload.get("results")
            if not isinstance(results, list) or any(not isinstance(row, dict) for row in results):
                raise ConfluenceRequestError("Confluence returned a malformed results list")
            links = payload.get("_links") or {}
            if not isinstance(links, dict):
                raise ConfluenceRequestError("Confluence returned malformed pagination links")
            next_link = links.get("next")
            if next_link is not None and not isinstance(next_link, str):
                raise ConfluenceRequestError("Confluence returned a malformed continuation")
            if next_link and not results:
                raise ConfluenceRequestError("Confluence returned an empty page with a continuation")
            # Validate before exposing rows, including when the caller has a result cap.
            next_params = self._next_params(path, params, next_link) if next_link else None
            yield results
            if next_params is None:
                return
            current = next_params

    def _next_params(self, path: str, initial: dict[str, Any], link: str) -> dict[str, Any]:
        endpoint = urlsplit(self.url(path))
        candidate = urlsplit(urljoin(endpoint.geturl(), link))
        if (
            (candidate.scheme, candidate.hostname, candidate.port, candidate.path)
            != (endpoint.scheme, endpoint.hostname, endpoint.port, endpoint.path)
            or candidate.username is not None
            or candidate.password is not None
            or candidate.fragment
        ):
            raise ConfluenceRequestError("Confluence continuation changed origin or endpoint")
        query = parse_qs(candidate.query, keep_blank_values=True)
        result = dict(initial)
        for key, values in query.items():
            if len(values) != 1 or key not in {*initial, "cursor", "start", "limit"}:
                raise ConfluenceRequestError("Confluence continuation has unexpected parameters")
            value = values[0]
            if key in {"cursor", "start", "limit"}:
                if key == "cursor":
                    if not value:
                        raise ConfluenceRequestError("Confluence continuation has an empty cursor")
                    result[key] = value
                else:
                    try:
                        number = int(value)
                    except ValueError:
                        raise ConfluenceRequestError("Confluence continuation has an invalid page bound") from None
                    if number < (1 if key == "limit" else 0) or (
                        key == "limit" and number > int(initial.get("limit", 250))
                    ):
                        raise ConfluenceRequestError("Confluence continuation exceeds its page bound")
                    result[key] = number
            elif str(initial[key]) != value:
                raise ConfluenceRequestError("Confluence continuation changed a scope filter")
        if not any(key in query for key in ("cursor", "start")):
            raise ConfluenceRequestError("Confluence continuation is missing a cursor or offset")
        return result
