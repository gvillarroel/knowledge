#!/usr/bin/env python3
"""Materialize live Confluence evidence into a self-contained campaign package."""

from __future__ import annotations

import argparse
from io import BytesIO
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
from typing import Any
from urllib.parse import urlsplit


SCHEMA_VERSION = "1.0"
SHA256_LENGTH = 64
MINIMUM_DURATION_SECONDS = 8 * 60 * 60
START_ANCHOR_GRACE_SECONDS = 5 * 60
FINALIZATION_GRACE_SECONDS = 30 * 60
MILESTONE_NAMES = (
    "campaign-start",
    "baseline-capture",
    "api-verification",
    "browser-verification",
    "campaign-end",
    "materialization",
)
REQUIRED_COVERAGE_CATEGORIES = (
    "text-and-marks",
    "structure",
    "inline-elements",
    "containers",
    "links",
    "smart-links",
    "media",
    "core-dynamic-macros",
    "marketplace-and-custom-extensions",
    "page-metadata",
    "attachments",
    "immutable-and-preserved-surfaces",
)
CASE_DEFINITIONS = (
    {
        "id": "text-and-structure",
        "name": "Text and structure round-trip",
        "page_id": "34340869",
        "coverage_categories": (
            "text-and-marks",
            "structure",
            "inline-elements",
            "containers",
        ),
    },
    {
        "id": "links-and-media",
        "name": "Links, media, and attachments round-trip",
        "page_id": "34504707",
        "coverage_categories": ("links", "smart-links", "media", "attachments"),
    },
    {
        "id": "macros-and-dynamic-content",
        "name": "Dynamic macro and extension round-trip",
        "page_id": "34570243",
        "coverage_categories": (
            "core-dynamic-macros",
            "marketplace-and-custom-extensions",
        ),
    },
    {
        "id": "metadata-and-safety",
        "name": "Metadata and preserved-surface round-trip",
        "page_id": "34406404",
        "coverage_categories": ("page-metadata", "immutable-and-preserved-surfaces"),
    },
)
WORKFLOW_SOURCES = (
    ("scan", "space-inventory.json"),
    ("inventory", "space-inventory.json"),
    ("explore", "campaign/space-explore-final.json"),
    ("batch-download", "campaign/batch-manifest.json"),
    ("batch-validate", "campaign/batch-local-validation-v2.json"),
    ("batch-dry-run", "campaign/batch-plan-final-noop.json"),
    ("batch-upload", "campaign/batch-upload-report.json"),
    ("batch-verify", "campaign/batch-verify-final.json"),
)


def _aware_datetime(value: Any, field: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty ISO 8601 timestamp")
    candidate = value.strip()
    parseable = f"{candidate[:-1]}+00:00" if candidate.endswith("Z") else candidate
    try:
        parsed = datetime.fromisoformat(parseable)
    except ValueError as exc:
        raise ValueError(f"{field} is not a valid ISO 8601 timestamp: {value!r}") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{field} must include a timezone offset")
    return parsed.astimezone(timezone.utc)


def _aware_timestamp(value: Any, field: str) -> str:
    _aware_datetime(value, field)
    return str(value).strip()


def _utc_timestamp(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def _canonical_json_digest(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return sha256(payload.encode("utf-8")).hexdigest()


def _confluence_identity(base_url: Any, space_id: Any, field: str) -> tuple[str, str]:
    if not isinstance(base_url, str) or not base_url.strip():
        raise ValueError(f"{field}.base_url must be a non-empty HTTPS tenant URL")
    candidate = base_url.strip()
    parsed = urlsplit(candidate)
    if (
        parsed.scheme.lower() != "https"
        or not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
        or parsed.query
        or parsed.fragment
        or parsed.path not in {"", "/"}
    ):
        raise ValueError(f"{field}.base_url must be an origin-only HTTPS tenant URL")
    host = parsed.hostname.lower()
    port = f":{parsed.port}" if parsed.port is not None else ""
    normalized_url = f"https://{host}{port}"
    normalized_space = str(space_id or "").strip()
    if not normalized_space:
        raise ValueError(f"{field}.space_id must be non-empty")
    return normalized_url, normalized_space


def _page_url_matches(value: Any, base_url: str, page_id: str, field: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty absolute page URL")
    parsed = urlsplit(value.strip())
    tenant = urlsplit(base_url)
    if (
        parsed.scheme.lower() != tenant.scheme.lower()
        or (parsed.hostname or "").lower() != (tenant.hostname or "").lower()
        or parsed.port != tenant.port
        or parsed.username is not None
        or parsed.password is not None
        or parsed.query
        or parsed.fragment
    ):
        raise ValueError(f"{field} belongs to a different tenant or is not a canonical page URL")
    segments = [segment for segment in parsed.path.split("/") if segment]
    if not any(
        segments[index] == "pages" and segments[index + 1] == page_id
        for index in range(len(segments) - 1)
    ):
        raise ValueError(f"{field} does not identify page {page_id}")


def _contained_file(base: Path, relative: Any, field: str) -> Path:
    if not isinstance(relative, str) or not relative.strip():
        raise ValueError(f"{field} must be a non-empty relative path")
    relative_path = Path(relative)
    if relative_path.is_absolute():
        raise ValueError(f"{field} must be relative")
    base = base.resolve()
    candidate = (base / relative_path).resolve()
    if not candidate.is_relative_to(base):
        raise ValueError(f"{field} escapes its source directory")
    if not candidate.is_file():
        raise ValueError(f"{field} does not exist: {candidate}")
    return candidate


def _contained_destination(root: Path, relative: Path) -> Path:
    if relative.is_absolute():
        raise ValueError("destination path must be relative")
    root = root.resolve()
    candidate = (root / relative).resolve()
    if not candidate.is_relative_to(root):
        raise ValueError(f"destination path escapes the campaign directory: {relative}")
    return candidate


def _atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            temporary_path = Path(handle.name)
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, path)
        temporary_path = None
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def _atomic_json(path: Path, payload: dict[str, Any]) -> None:
    serialized = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    _atomic_write(path, serialized.encode("utf-8"))


def _write_snapshot(destination: Path, payload: bytes) -> str:
    _atomic_write(destination, payload)
    return sha256(payload).hexdigest()


def _read_once(path: Path, cache: dict[Path, bytes]) -> bytes:
    resolved = path.resolve()
    if resolved not in cache:
        cache[resolved] = resolved.read_bytes()
    return cache[resolved]


def _json_snapshot(
    base: Path,
    relative: str,
    field: str,
    cache: dict[Path, bytes],
) -> tuple[Path, bytes, dict[str, Any]]:
    path = _contained_file(base, relative, field)
    payload = _read_once(path, cache)
    try:
        value = json.loads(payload.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read JSON object {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return path, payload, value


def _passing_checks(payload: dict[str, Any], field: str) -> None:
    checks = payload.get("checks")
    if not isinstance(checks, list) or not checks:
        raise ValueError(f"{field} must contain at least one check")
    if any(not isinstance(check, dict) or check.get("passed") is not True for check in checks):
        raise ValueError(f"{field} contains a failed or invalid check")


def _sha256_value(value: Any, field: str) -> str:
    if (
        not isinstance(value, str)
        or len(value) != SHA256_LENGTH
        or any(character not in "0123456789abcdef" for character in value)
    ):
        raise ValueError(f"{field} must be a lowercase SHA-256 digest")
    return value


def _positive_version(value: Any, field: str) -> int:
    if isinstance(value, bool):
        raise ValueError(f"{field} must be a positive integer")
    try:
        version = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field} must be a positive integer") from exc
    if version <= 0:
        raise ValueError(f"{field} must be a positive integer")
    return version


def _validate_embedded_timestamps(
    value: Any,
    campaign_started: datetime,
    campaign_ended: datetime,
    field: str,
) -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            nested_field = f"{field}.{key}"
            if key.endswith("_at") and nested is not None:
                timestamp = _aware_datetime(nested, nested_field)
                if not campaign_started <= timestamp <= campaign_ended:
                    raise ValueError(f"{nested_field} is outside the campaign interval")
            _validate_embedded_timestamps(nested, campaign_started, campaign_ended, nested_field)
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            _validate_embedded_timestamps(
                nested, campaign_started, campaign_ended, f"{field}[{index}]"
            )


def _require_noop_plan(plan: Any, field: str) -> dict[str, Any]:
    if not isinstance(plan, dict):
        raise ValueError(f"{field} must be an object")
    required_false = (
        "page_update",
        "body_changed",
        "metadata_changed",
        "content_state_changed",
        "suppressed_content_state_changed",
    )
    for key in required_false:
        if plan.get(key) is not False:
            raise ValueError(f"{field}.{key} must be false")
    if plan.get("no_op") is not True:
        raise ValueError(f"{field}.no_op must be true")
    for key in ("attachments", "suppressed_attachments"):
        if plan.get(key) != []:
            raise ValueError(f"{field}.{key} must be empty")
    empty_labels = {"added": [], "removed": []}
    for key in ("labels", "suppressed_labels"):
        if plan.get(key) != empty_labels:
            raise ValueError(f"{field}.{key} must contain no label changes")
    sync = plan.get("sync")
    if sync != {"attachments": True, "labels": True, "content_state": True}:
        raise ValueError(f"{field}.sync must enable attachments, labels, and content state")
    return plan


def _image_is_decodable(payload: bytes) -> bool:
    """Return whether Pillow can verify and fully decode a PNG or JPEG payload."""

    try:
        from PIL import Image, UnidentifiedImageError
    except ImportError:
        return False
    try:
        with Image.open(BytesIO(payload)) as image:
            if (
                image.format not in {"PNG", "JPEG"}
                or image.width <= 0
                or image.height <= 0
                or image.width * image.height > 100_000_000
            ):
                return False
            image.verify()
        with Image.open(BytesIO(payload)) as image:
            image.load()
            return image.format in {"PNG", "JPEG"} and image.width > 0 and image.height > 0
    except (
        OSError,
        SyntaxError,
        ValueError,
        UnidentifiedImageError,
        Image.DecompressionBombError,
    ):
        return False


def _validate_workspace_binding(
    workspace: dict[str, Any],
    page_id: str,
    operation_id: str,
    desired_digest: str,
    remote_version: int,
    base_url: str,
    space_id: str,
    field: str,
) -> datetime:
    workspace_base, _ = _confluence_identity(
        workspace.get("base_url"), space_id, f"{field}.workspace_manifest"
    )
    if workspace_base != base_url:
        raise ValueError(f"{field}.workspace_manifest belongs to a different tenant")
    page = workspace.get("page")
    if not isinstance(page, dict):
        raise ValueError(f"{field}.workspace_manifest.page must be an object")
    if str(page.get("page_id") or "") != page_id:
        raise ValueError(f"{field}.workspace_manifest identifies a different page")
    if str(page.get("space_id") or "") != space_id:
        raise ValueError(f"{field}.workspace_manifest identifies a different space")
    if _positive_version(page.get("version"), f"{field}.workspace_manifest.page.version") != remote_version:
        raise ValueError(f"{field}.workspace_manifest is bound to a different remote version")
    _page_url_matches(page.get("web_url"), base_url, page_id, f"{field}.workspace_manifest.page.web_url")
    if str(workspace.get("last_verified_operation_id") or "") != operation_id:
        raise ValueError(f"{field}.workspace_manifest is bound to a different API operation")
    if workspace.get("last_verified_desired_state_sha256") != desired_digest:
        raise ValueError(f"{field}.workspace_manifest is bound to a different desired state")
    workspace_time = _aware_datetime(
        workspace.get("last_verified_at"), f"{field}.workspace_manifest.last_verified_at"
    )
    if workspace_time < _aware_datetime(
        workspace.get("downloaded_at"), f"{field}.workspace_manifest.downloaded_at"
    ):
        raise ValueError(f"{field}.workspace_manifest verification precedes its download")
    return workspace_time


def _validate_case_binding(
    api: dict[str, Any],
    api_bytes: bytes,
    browser: dict[str, Any],
    noop: dict[str, Any],
    workspace: dict[str, Any],
    page_id: str,
    base_url: str,
    space_id: str,
    campaign_started: datetime,
    campaign_ended: datetime,
    field: str,
) -> tuple[datetime, datetime]:
    if api.get("status") != "verified" or browser.get("status") != "verified":
        raise ValueError(f"{field} API and browser reports must be verified")
    if noop.get("status") != "dry-run":
        raise ValueError(f"{field} no-op report must have status dry-run")
    _passing_checks(api, f"{field}.api_report")
    _passing_checks(browser, f"{field}.browser_ground_truth")
    operation_id = str(api.get("operation_id") or "")
    if not operation_id:
        raise ValueError(f"{field}.api_report has no operation_id")
    desired_digest = _sha256_value(
        api.get("desired_state_sha256"), f"{field}.api_report.desired_state_sha256"
    )
    remote_version = _positive_version(api.get("remote_version"), f"{field}.api_report.remote_version")
    plan = _require_noop_plan(noop.get("plan"), f"{field}.noop_dry_run.plan")
    identities = {
        str(api.get("page_id") or ""),
        str(browser.get("page_id") or ""),
        str(plan.get("page_id") or ""),
    }
    if identities != {page_id}:
        raise ValueError(f"{field} verification triad does not consistently identify page {page_id}")
    if str(browser.get("operation_id") or "") != operation_id:
        raise ValueError(f"{field} browser report is bound to a different API operation")
    if browser.get("desired_state_sha256") != desired_digest:
        raise ValueError(f"{field} browser report is bound to a different desired state")
    if _positive_version(browser.get("remote_version"), f"{field}.browser.remote_version") != remote_version:
        raise ValueError(f"{field} browser report is bound to a different remote version")
    if browser.get("api_report_sha256") != sha256(api_bytes).hexdigest():
        raise ValueError(f"{field} browser report is not bound to the exact API report")
    if plan.get("desired_state_sha256") != desired_digest:
        raise ValueError(f"{field} no-op report is bound to a different desired state")
    if _positive_version(plan.get("current_version"), f"{field}.noop.current_version") != remote_version:
        raise ValueError(f"{field} no-op report is bound to a different remote version")
    workspace_time = _validate_workspace_binding(
        workspace,
        page_id,
        operation_id,
        desired_digest,
        remote_version,
        base_url,
        space_id,
        field,
    )
    _page_url_matches(browser.get("page_url"), base_url, page_id, f"{field}.browser.page_url")
    api_time = _aware_datetime(api.get("verified_at"), f"{field}.api_report.verified_at")
    browser_time = _aware_datetime(
        browser.get("verified_at"), f"{field}.browser_ground_truth.verified_at"
    )
    if not campaign_started <= api_time <= campaign_ended:
        raise ValueError(f"{field} API verification is outside the campaign interval")
    if not api_time <= browser_time <= campaign_ended:
        raise ValueError(f"{field} browser verification must follow API verification inside the campaign")
    if not api_time <= workspace_time <= browser_time:
        raise ValueError(f"{field}.workspace_manifest timestamp is stale or out of verification order")
    return api_time, browser_time


def _page_records(payload: dict[str, Any], field: str) -> tuple[list[dict[str, Any]], list[str]]:
    pages = payload.get("pages")
    if not isinstance(pages, list) or not pages or any(not isinstance(page, dict) for page in pages):
        raise ValueError(f"{field}.pages must be a non-empty array of page objects")
    page_ids = [str(page.get("page_id") or "") for page in pages]
    if any(not page_id for page_id in page_ids) or len(page_ids) != len(set(page_ids)):
        raise ValueError(f"{field}.pages must contain unique non-empty page IDs")
    return pages, page_ids


def _validate_workflow_source(
    operation: str,
    payload: dict[str, Any],
    expected_page_ids: list[str],
    expected_base_url: str | None = None,
    expected_space_id: str | None = None,
) -> list[str]:
    field = f"workflow.{operation}"
    pages, observed = _page_records(payload, field)
    expected = set(expected_page_ids)
    observed_set = set(observed)
    if operation in {"scan", "inventory"}:
        if expected_base_url is not None and expected_space_id is not None:
            base_url, space_id = _confluence_identity(
                payload.get("base_url"), payload.get("space_id"), field
            )
            if base_url != expected_base_url or space_id != expected_space_id:
                raise ValueError(f"{field} belongs to a different Confluence tenant or space")
            if any(str(page.get("space_id") or "") != expected_space_id for page in pages):
                raise ValueError(f"{field}.pages contains a page from a different space")
        if payload.get("status") != "verified" or not expected.issubset(observed_set):
            raise ValueError(f"{field} must be a verified inventory containing every campaign page")
        return expected_page_ids.copy()
    if observed_set != expected or len(observed) != len(expected_page_ids):
        raise ValueError(f"{field} page IDs do not exactly match the campaign page set")
    if operation == "explore":
        filters = payload.get("filters")
        if expected_space_id is not None and any(
            str(page.get("space_id") or "") != expected_space_id for page in pages
        ):
            raise ValueError(f"{field}.pages contains a page from a different space")
        if (
            payload.get("status") != "queried"
            or payload.get("inventory_status") != "verified"
            or payload.get("count") != len(expected_page_ids)
            or not isinstance(filters, dict)
            or not any(isinstance(value, list) and value for value in filters.values())
        ):
            raise ValueError(f"{field} must be a distinct filtered query over a verified inventory")
        return observed
    if operation == "batch-download" and expected_base_url is not None and expected_space_id is not None:
        base_url, space_id = _confluence_identity(
            payload.get("base_url"), payload.get("space_id"), field
        )
        if base_url != expected_base_url or space_id != expected_space_id:
            raise ValueError(f"{field} belongs to a different Confluence tenant or space")
    if payload.get("status") != "verified":
        raise ValueError(f"{field} source status is not verified")
    expected_status = {
        "batch-download": "downloaded",
        "batch-validate": "valid",
        "batch-dry-run": "planned",
        "batch-upload": "verified",
        "batch-verify": "verified",
    }[operation]
    for index, page in enumerate(pages):
        if page.get("status") != expected_status:
            raise ValueError(f"{field}.pages[{index}].status must be {expected_status}")
        if operation == "batch-dry-run":
            plan = page.get("plan")
            if not isinstance(plan, dict) or plan.get("no_op") is not True:
                raise ValueError(f"{field}.pages[{index}] must contain a no-op plan")
            if (
                plan.get("page_update") is not False
                or plan.get("attachments") != []
                or plan.get("labels") != {"added": [], "removed": []}
                or plan.get("content_state_changed") is not False
            ):
                raise ValueError(f"{field}.pages[{index}] plan is not converged")
        if operation == "batch-upload":
            result = page.get("result")
            if not isinstance(result, dict) or (result.get("verification") or {}).get("status") != "verified":
                raise ValueError(f"{field}.pages[{index}] has no verified upload result")
        if operation == "batch-verify":
            verification = page.get("verification")
            if not isinstance(verification, dict) or verification.get("status") != "verified":
                raise ValueError(f"{field}.pages[{index}] has no verified API result")
    return observed


def _validate_workflow_bindings(
    payloads: dict[str, dict[str, Any]],
    digests: dict[str, str],
    expected_page_ids: list[str],
) -> None:
    inventory_digest = digests.get("inventory")
    batch_digest = digests.get("batch-download")
    batch = payloads.get("batch-download", {})
    if batch.get("inventory_sha256") != inventory_digest:
        raise ValueError("workflow.batch-download is not bound to the exact inventory receipt")
    upload = payloads.get("batch-upload", {})
    if upload.get("batch_manifest_sha256") != batch_digest:
        raise ValueError("workflow.batch-upload is not bound to the exact batch manifest")
    batch_id = str(batch.get("batch_id") or "")
    if not batch_id:
        raise ValueError("workflow.batch-download has no batch_id")
    for operation in ("batch-dry-run", "batch-upload"):
        if str(payloads.get(operation, {}).get("batch_id") or "") != batch_id:
            raise ValueError(f"workflow.{operation} is bound to a different batch_id")
    dependency_orders: list[tuple[str, list[Any]]] = []
    for operation in ("batch-validate", "batch-dry-run", "batch-upload", "batch-verify"):
        order = payloads.get(operation, {}).get("dependency_order")
        if not isinstance(order, list) or len(order) != len(expected_page_ids):
            raise ValueError(f"workflow.{operation}.dependency_order must cover every campaign page")
        if any(not isinstance(page_id, str) or not page_id for page_id in order):
            raise ValueError(f"workflow.{operation}.dependency_order must contain page ID strings")
        if len(order) != len(set(order)) or set(order) != set(expected_page_ids):
            raise ValueError(f"workflow.{operation}.dependency_order must uniquely match campaign pages")
        dependency_orders.append((operation, order))
    reference_order = dependency_orders[0][1]
    for operation, order in dependency_orders[1:]:
        if order != reference_order:
            raise ValueError(f"workflow.{operation}.dependency_order differs from the validated order")


def _copy_case(
    source_root: Path,
    campaign_root: Path,
    case: dict[str, Any],
    cache: dict[Path, bytes],
    base_url: str,
    space_id: str,
    campaign_started: datetime,
    campaign_ended: datetime,
) -> tuple[dict[str, Any], dict[str, str], datetime, datetime]:
    page_id = str(case["page_id"])
    verification_relative = f"campaign/workspaces/{page_id}/verification"
    destination_relative = Path("evidence") / str(case["id"])
    destination = _contained_destination(campaign_root, destination_relative)
    snapshots: dict[str, tuple[Path, bytes, dict[str, Any]]] = {}
    for field, filename in (
        ("api_report", "report.json"),
        ("browser_ground_truth", "browser-ground-truth.json"),
        ("noop_dry_run", "noop-dry-run.json"),
        ("workspace_manifest", "../manifest.json"),
    ):
        snapshots[field] = _json_snapshot(
            source_root,
            f"{verification_relative}/{filename}",
            f"{case['id']}.{field}",
            cache,
        )
    _, api_bytes, api = snapshots["api_report"]
    _, _, browser = snapshots["browser_ground_truth"]
    _, _, noop = snapshots["noop_dry_run"]
    _, _, workspace = snapshots["workspace_manifest"]
    api_time, browser_time = _validate_case_binding(
        api,
        api_bytes,
        browser,
        noop,
        workspace,
        page_id,
        base_url,
        space_id,
        campaign_started,
        campaign_ended,
        str(case["id"]),
    )

    evidence_records: dict[str, dict[str, str]] = {}
    destination_names = {
        "api_report": "report.json",
        "browser_ground_truth": "browser-ground-truth.json",
        "noop_dry_run": "noop-dry-run.json",
        "workspace_manifest": "workspace-manifest.json",
    }
    for field, (_, payload, _) in snapshots.items():
        destination_name = destination_names[field]
        digest = _write_snapshot(destination / destination_name, payload)
        evidence_records[field] = {
            "path": (destination_relative / destination_name).as_posix(),
            "sha256": digest,
        }

    screenshot_records = [browser.get("baseline")]
    finals = browser.get("final_screenshots")
    if not isinstance(finals, list) or not finals:
        raise ValueError(f"{case['id']} must have at least one final screenshot")
    screenshot_records.extend(finals)
    screenshot_digests: list[str] = []
    baseline_receipt: dict[str, str] | None = None
    verification_root = _contained_file(
        source_root,
        f"{verification_relative}/report.json",
        f"{case['id']}.verification",
    ).parent
    for index, record in enumerate(screenshot_records):
        if not isinstance(record, dict):
            raise ValueError(f"{case['id']} screenshot record {index} must be an object")
        screenshot = _contained_file(
            verification_root,
            record.get("path"),
            f"{case['id']}.screenshots[{index}]",
        )
        payload = _read_once(screenshot, cache)
        digest = sha256(payload).hexdigest()
        if record.get("sha256") != digest:
            raise ValueError(f"{case['id']} screenshot record {index} digest mismatch")
        if not _image_is_decodable(payload):
            raise ValueError(f"{case['id']} screenshot record {index} is not a decodable PNG or JPEG")
        relative = screenshot.relative_to(verification_root.resolve())
        _write_snapshot(destination / relative, payload)
        screenshot_digests.append(digest)
        if index == 0:
            captured = datetime.fromtimestamp(screenshot.stat().st_mtime, timezone.utc)
            if not campaign_started <= captured <= campaign_ended:
                raise ValueError(f"{case['id']} baseline capture time is outside the campaign")
            baseline_receipt = {
                "page_id": page_id,
                "path": (destination_relative / relative).as_posix(),
                "sha256": digest,
                "captured_at": _utc_timestamp(captured),
            }
    if not any(digest != screenshot_digests[0] for digest in screenshot_digests[1:]):
        raise ValueError(f"{case['id']} final screenshots must differ from the baseline")
    if baseline_receipt is None:
        raise ValueError(f"{case['id']} has no baseline receipt")

    return (
        {
            "id": case["id"],
            "name": case["name"],
            "page_id": page_id,
            "status": "passed",
            "coverage_categories": list(case["coverage_categories"]),
            "evidence": evidence_records,
        },
        baseline_receipt,
        api_time,
        browser_time,
    )


def _copy_workflow(
    source_root: Path,
    campaign_root: Path,
    page_ids: list[str],
    cache: dict[Path, bytes],
    base_url: str,
    space_id: str,
    campaign_started: datetime,
    campaign_ended: datetime,
) -> dict[str, str]:
    workflow_relative = Path("evidence") / "multi-page-workflow"
    workflow_directory = _contained_destination(campaign_root, workflow_relative)
    operations: list[dict[str, Any]] = []
    payloads: dict[str, dict[str, Any]] = {}
    digests: dict[str, str] = {}
    previous_digest: str | None = None
    for operation, source_relative in WORKFLOW_SOURCES:
        source, payload, source_object = _json_snapshot(
            source_root, source_relative, f"workflow.{operation}", cache
        )
        _validate_embedded_timestamps(
            source_object, campaign_started, campaign_ended, f"workflow.{operation}"
        )
        operation_page_ids = _validate_workflow_source(
            operation, source_object, page_ids, base_url, space_id
        )
        captured = datetime.fromtimestamp(source.stat().st_mtime, timezone.utc)
        if not campaign_started <= captured <= campaign_ended:
            raise ValueError(f"workflow.{operation} receipt time is outside the campaign")
        destination = workflow_directory / f"{operation}.json"
        digest = _write_snapshot(destination, payload)
        payloads[operation] = source_object
        digests[operation] = digest
        operations.append(
            {
                "name": operation,
                "status": "passed",
                "page_ids": operation_page_ids,
                "artifact": {"path": destination.name, "sha256": digest},
                "source_name": source.name,
                "captured_at": _utc_timestamp(captured),
                "previous_artifact_sha256": previous_digest,
            }
        )
        previous_digest = digest
    _validate_workflow_bindings(payloads, digests, page_ids)
    report = {
        "status": "verified",
        "base_url": base_url,
        "space_id": space_id,
        "page_ids": page_ids,
        "operations": operations,
        "artifact_chain_head_sha256": previous_digest,
    }
    report_path = workflow_directory / "report.json"
    _atomic_json(report_path, report)
    return {
        "path": (workflow_relative / "report.json").as_posix(),
        "sha256": sha256(report_path.read_bytes()).hexdigest(),
    }


def _write_timeline(
    campaign_root: Path,
    campaign_id: str,
    base_url: str,
    space_id: str,
    page_ids: list[str],
    started: datetime,
    ended: datetime,
    materialized: datetime,
    baseline_receipts: list[dict[str, str]],
    api_times: list[datetime],
    browser_times: list[datetime],
) -> dict[str, str]:
    if not baseline_receipts or not api_times or not browser_times:
        raise ValueError("campaign timeline requires baseline, API, and browser receipts")
    earliest_baseline = min(
        _aware_datetime(receipt["captured_at"], "timeline.baseline_receipts.captured_at")
        for receipt in baseline_receipts
    )
    if (earliest_baseline - started).total_seconds() > START_ANCHOR_GRACE_SECONDS:
        raise ValueError("earliest baseline was not captured within 5 minutes of campaign start")
    if (materialized - earliest_baseline).total_seconds() < MINIMUM_DURATION_SECONDS:
        raise ValueError("fewer than 8 real hours elapsed between baseline capture and materialization")
    occurred = (
        started,
        earliest_baseline,
        max(api_times),
        max(browser_times),
        ended,
        materialized,
    )
    if list(occurred) != sorted(occurred):
        raise ValueError("campaign milestones are not chronological")
    previous: str | None = None
    milestones: list[dict[str, Any]] = []
    for name, timestamp in zip(MILESTONE_NAMES, occurred, strict=True):
        record: dict[str, Any] = {
            "name": name,
            "occurred_at": _utc_timestamp(timestamp),
            "previous_sha256": previous,
        }
        record["sha256"] = _canonical_json_digest(record)
        milestones.append(record)
        previous = record["sha256"]
    timeline = {
        "schema_version": SCHEMA_VERSION,
        "status": "verified",
        "campaign_id": campaign_id,
        "base_url": base_url,
        "space_id": space_id,
        "page_ids": page_ids,
        "started_at": _utc_timestamp(started),
        "ended_at": _utc_timestamp(ended),
        "materialized_at": _utc_timestamp(materialized),
        "baseline_receipts": baseline_receipts,
        "milestones": milestones,
        "milestone_chain_head_sha256": previous,
    }
    relative = Path("evidence") / "campaign-timeline.json"
    destination = _contained_destination(campaign_root, relative)
    _atomic_json(destination, timeline)
    return {"path": relative.as_posix(), "sha256": sha256(destination.read_bytes()).hexdigest()}


def _assert_sources_unchanged(cache: dict[Path, bytes]) -> None:
    for path, expected in cache.items():
        try:
            actual = path.read_bytes()
        except OSError as exc:
            raise ValueError(f"source evidence changed or disappeared during materialization: {path}") from exc
        if actual != expected:
            raise ValueError(f"source evidence changed during materialization: {path}")


def materialize_live_campaign(
    source_root: Path,
    output: Path,
    *,
    started_at: str,
    ended_at: str,
    campaign_id: str = "confluence-8h-live",
) -> dict[str, Any]:
    """Snapshot live evidence into a newly staged, self-contained campaign package."""

    started_at = _aware_timestamp(started_at, "started_at")
    ended_at = _aware_timestamp(ended_at, "ended_at")
    campaign_started = _aware_datetime(started_at, "started_at")
    campaign_ended = _aware_datetime(ended_at, "ended_at")
    materialized_at = datetime.now(timezone.utc)
    if campaign_ended > materialized_at:
        raise ValueError("ended_at cannot be in the future")
    if campaign_ended < campaign_started:
        raise ValueError("ended_at cannot precede started_at")
    if (campaign_ended - campaign_started).total_seconds() < MINIMUM_DURATION_SECONDS:
        raise ValueError("campaign elapsed time must be at least 8 real hours")
    if (materialized_at - campaign_ended).total_seconds() > FINALIZATION_GRACE_SECONDS:
        raise ValueError("ended_at is backdated; materialize within 30 minutes of campaign end")
    if not isinstance(campaign_id, str) or not campaign_id.strip():
        raise ValueError("campaign_id must be a non-empty string")
    campaign_id = campaign_id.strip()

    source_root = source_root.resolve()
    output_candidate = output if output.is_absolute() else Path.cwd() / output
    output = output_candidate.resolve()
    campaign_root = output.parent
    if (
        campaign_root == source_root
        or campaign_root.is_relative_to(source_root)
        or source_root.is_relative_to(campaign_root)
    ):
        raise ValueError("campaign output and live source must not contain one another")
    if campaign_root.exists():
        raise ValueError(f"campaign output directory already exists: {campaign_root}")
    campaign_root.parent.mkdir(parents=True, exist_ok=True)

    staging = Path(
        tempfile.mkdtemp(prefix=f".{campaign_root.name}.stage-", dir=campaign_root.parent)
    )
    cache: dict[Path, bytes] = {}
    try:
        page_ids = [str(case["page_id"]) for case in CASE_DEFINITIONS]
        _, _, batch_manifest = _json_snapshot(
            source_root, "campaign/batch-manifest.json", "batch_manifest", cache
        )
        base_url, space_id = _confluence_identity(
            batch_manifest.get("base_url"), batch_manifest.get("space_id"), "batch_manifest"
        )
        batch_pages, observed_page_ids = _page_records(batch_manifest, "batch_manifest")
        if (
            batch_manifest.get("status") != "verified"
            or len(observed_page_ids) != len(page_ids)
            or set(observed_page_ids) != set(page_ids)
            or any(page.get("status") != "downloaded" for page in batch_pages)
        ):
            raise ValueError("live batch manifest must contain the exact four unique downloaded fixtures")

        copied_cases = [
            _copy_case(
                source_root,
                staging,
                case,
                cache,
                base_url,
                space_id,
                campaign_started,
                campaign_ended,
            )
            for case in CASE_DEFINITIONS
        ]
        test_cases = [item[0] for item in copied_cases]
        baseline_receipts = [item[1] for item in copied_cases]
        api_times = [item[2] for item in copied_cases]
        browser_times = [item[3] for item in copied_cases]
        workflow_report = _copy_workflow(
            source_root,
            staging,
            page_ids,
            cache,
            base_url,
            space_id,
            campaign_started,
            campaign_ended,
        )
        timeline_report = _write_timeline(
            staging,
            campaign_id,
            base_url,
            space_id,
            page_ids,
            campaign_started,
            campaign_ended,
            materialized_at,
            baseline_receipts,
            api_times,
            browser_times,
        )
        manifest = {
            "schema_version": SCHEMA_VERSION,
            "campaign_id": campaign_id,
            "started_at": started_at,
            "ended_at": ended_at,
            "minimum_duration_hours": 8,
            "confluence": {"base_url": base_url, "space_id": space_id},
            "timeline": {"report": timeline_report},
            "required_coverage_categories": list(REQUIRED_COVERAGE_CATEGORIES),
            "multi_page_workflow": {"report": workflow_report},
            "phases": [
                {
                    "id": "live-roundtrip-verification",
                    "name": "Live multi-page round-trip verification",
                    "started_at": started_at,
                    "ended_at": ended_at,
                    "test_cases": test_cases,
                }
            ],
        }
        _atomic_json(_contained_destination(staging, Path(output.name)), manifest)
        _assert_sources_unchanged(cache)
        os.replace(staging, campaign_root)
        staging = Path()
        return manifest
    finally:
        if staging != Path() and staging.exists():
            shutil.rmtree(staging, ignore_errors=True)


def main(argv: list[str] | None = None) -> int:
    """Run the deterministic live-evidence materializer."""

    default_source = Path(__file__).resolve().parents[1] / "confluence-8h-live" / "batch"
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=default_source)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--started-at", required=True)
    parser.add_argument("--ended-at", required=True)
    parser.add_argument("--campaign-id", default="confluence-8h-live")
    args = parser.parse_args(argv)
    try:
        manifest = materialize_live_campaign(
            args.source_root,
            args.output,
            started_at=args.started_at,
            ended_at=args.ended_at,
            campaign_id=args.campaign_id,
        )
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", newline="\n")
    print(
        json.dumps(
            {
                "status": "materialized",
                "manifest": str(args.output.resolve()),
                "campaign_id": manifest["campaign_id"],
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
