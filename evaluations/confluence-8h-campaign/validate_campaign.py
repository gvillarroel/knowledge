#!/usr/bin/env python3
"""Validate deterministic evidence for an eight-hour Confluence campaign."""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
from hashlib import sha256
import importlib.util
import json
import math
from pathlib import Path
import re
import sys
from types import ModuleType
from typing import Any


SCHEMA_VERSION = "1.0"
MINIMUM_DURATION_HOURS = 8.0
ALLOWED_TEST_STATUSES = {"pending", "running", "passed", "failed", "blocked", "skipped"}
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
REQUIRED_WORKFLOW_OPERATIONS = (
    "scan",
    "inventory",
    "explore",
    "batch-download",
    "batch-validate",
    "batch-dry-run",
    "batch-upload",
    "batch-verify",
)
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")


def _load_contract() -> ModuleType:
    path = Path(__file__).resolve().with_name("materialize_live_campaign.py")
    module_name = "confluence_campaign_materializer_contract"
    existing = sys.modules.get(module_name)
    if existing is not None:
        return existing
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load campaign contract: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


contract = _load_contract()


def _load_object_bytes(path: Path) -> tuple[bytes, dict[str, Any]]:
    try:
        payload = path.read_bytes()
        value = json.loads(payload.decode("utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ValueError(f"cannot read JSON object {path}: {error}") from error
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload, value


def _parse_timestamp(value: Any, field: str, errors: list[str]) -> datetime | None:
    try:
        return contract._aware_datetime(value, field)
    except ValueError as error:
        errors.append(str(error))
        return None


def _resolve_evidence_path(
    root: Path,
    value: Any,
    field: str,
    errors: list[str],
    *,
    base: Path | None = None,
) -> Path | None:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{field} must be a non-empty relative path")
        return None
    relative = Path(value)
    if relative.is_absolute():
        errors.append(f"{field} must be relative to the campaign directory")
        return None
    resolved = ((base or root) / relative).resolve()
    if not resolved.is_relative_to(root):
        errors.append(f"{field} escapes the campaign directory")
        return None
    if not resolved.is_file():
        errors.append(f"{field} does not exist: {value}")
        return None
    return resolved


def _read_hashed_object(
    root: Path,
    record: Any,
    field: str,
    errors: list[str],
    *,
    base: Path | None = None,
) -> tuple[Path | None, bytes | None, dict[str, Any] | None]:
    if not isinstance(record, dict):
        errors.append(f"{field} must be a path and SHA-256 object")
        return None, None, None
    expected = record.get("sha256")
    if not isinstance(expected, str) or not SHA256_PATTERN.fullmatch(expected):
        errors.append(f"{field}.sha256 must be a lowercase SHA-256 digest")
        return None, None, None
    path = _resolve_evidence_path(root, record.get("path"), f"{field}.path", errors, base=base)
    if path is None:
        return None, None, None
    try:
        payload = path.read_bytes()
    except OSError as error:
        errors.append(f"cannot read JSON object {path}: {error}")
        return path, None, None
    actual = sha256(payload).hexdigest()
    if actual != expected:
        errors.append(f"{field} digest mismatch: expected {expected}, got {actual}")
    try:
        value = json.loads(payload.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as error:
        errors.append(f"cannot read JSON object {path}: {error}")
        return path, payload, None
    if not isinstance(value, dict):
        errors.append(f"{path} must contain a JSON object")
        return path, payload, None
    return path, payload, value


def _validate_screenshot(
    root: Path,
    browser_path: Path,
    record: Any,
    field: str,
    errors: list[str],
) -> tuple[Path, str] | None:
    if not isinstance(record, dict):
        errors.append(f"{field} must be an object")
        return None
    expected = record.get("sha256")
    if not isinstance(expected, str) or not SHA256_PATTERN.fullmatch(expected):
        errors.append(f"{field}.sha256 must be a lowercase SHA-256 digest")
        return None
    screenshot = _resolve_evidence_path(
        root, record.get("path"), f"{field}.path", errors, base=browser_path.parent
    )
    if screenshot is None:
        return None
    payload = screenshot.read_bytes()
    actual = sha256(payload).hexdigest()
    if actual != expected:
        errors.append(f"{field} digest mismatch: expected {expected}, got {actual}")
        return None
    if not contract._image_is_decodable(payload):
        errors.append(f"{field} is not a decodable PNG or JPEG")
        return None
    return screenshot, actual


def _validate_browser_screenshots(
    root: Path,
    browser_path: Path,
    browser: dict[str, Any],
    field: str,
    errors: list[str],
) -> tuple[Path, str] | None:
    baseline = _validate_screenshot(
        root, browser_path, browser.get("baseline"), f"{field}.baseline", errors
    )
    finals = browser.get("final_screenshots")
    if not isinstance(finals, list) or not finals:
        errors.append(f"{field}.final_screenshots must contain at least one screenshot")
        return baseline
    final_results = [
        _validate_screenshot(
            root, browser_path, record, f"{field}.final_screenshots[{index}]", errors
        )
        for index, record in enumerate(finals)
    ]
    all_results = [result for result in [baseline, *final_results] if result is not None]
    paths = [result[0] for result in all_results]
    if len(paths) != len(set(paths)):
        errors.append(f"{field} screenshot paths must be unique")
    final_digests = [result[1] for result in final_results if result is not None]
    if baseline and not any(digest != baseline[1] for digest in final_digests):
        errors.append(f"{field} must contain a final screenshot distinct from the baseline")
    return baseline


def _validate_case_evidence(
    root: Path,
    test_case: dict[str, Any],
    field: str,
    evidence_started: datetime | None,
    evidence_ended: datetime | None,
    base_url: str | None,
    space_id: str | None,
    errors: list[str],
) -> dict[str, Any]:
    page_id = str(test_case.get("page_id") or "")
    if not page_id:
        errors.append(f"{field}.page_id must be non-empty")
    evidence = test_case.get("evidence")
    if not isinstance(evidence, dict):
        errors.append(f"{field}.evidence must be an object")
        return {"page_id": page_id}
    api_path, api_bytes, api = _read_hashed_object(
        root, evidence.get("api_report"), f"{field}.evidence.api_report", errors
    )
    browser_path, _, browser = _read_hashed_object(
        root,
        evidence.get("browser_ground_truth"),
        f"{field}.evidence.browser_ground_truth",
        errors,
    )
    noop_path, _, noop = _read_hashed_object(
        root, evidence.get("noop_dry_run"), f"{field}.evidence.noop_dry_run", errors
    )
    workspace_path, _, workspace = _read_hashed_object(
        root,
        evidence.get("workspace_manifest"),
        f"{field}.evidence.workspace_manifest",
        errors,
    )
    evidence_paths = [
        path for path in (api_path, browser_path, noop_path, workspace_path) if path is not None
    ]
    if len(evidence_paths) != len(set(evidence_paths)):
        errors.append(f"{field} evidence reports must use distinct files")
    api_time: datetime | None = None
    browser_time: datetime | None = None
    if (
        api is not None
        and api_bytes is not None
        and browser is not None
        and noop is not None
        and workspace is not None
        and evidence_started is not None
        and evidence_ended is not None
        and base_url is not None
        and space_id is not None
    ):
        try:
            api_time, browser_time = contract._validate_case_binding(
                api,
                api_bytes,
                browser,
                noop,
                workspace,
                page_id,
                base_url,
                space_id,
                evidence_started,
                evidence_ended,
                field,
            )
        except ValueError as error:
            errors.append(str(error))
    baseline: tuple[Path, str] | None = None
    if browser_path is not None and browser is not None:
        baseline = _validate_browser_screenshots(
            root, browser_path, browser, f"{field}.browser_ground_truth", errors
        )
    if api_path is not None and browser_path is not None and api_path == browser_path:
        errors.append(f"{field} API and browser evidence must be separate reports")
    return {
        "page_id": page_id,
        "api_time": api_time,
        "browser_time": browser_time,
        "baseline_path": baseline[0] if baseline is not None else None,
        "baseline_sha256": baseline[1] if baseline is not None else None,
    }


def _validate_multi_page_workflow(
    root: Path,
    manifest: dict[str, Any],
    campaign_started: datetime | None,
    campaign_ended: datetime | None,
    base_url: str | None,
    space_id: str | None,
    errors: list[str],
) -> dict[str, Any]:
    fallback = {
        "pages": 0,
        "page_ids": [],
        "required": list(REQUIRED_WORKFLOW_OPERATIONS),
        "passed": [],
        "missing": list(REQUIRED_WORKFLOW_OPERATIONS),
    }
    workflow = manifest.get("multi_page_workflow")
    if not isinstance(workflow, dict):
        errors.append("multi_page_workflow must be an object")
        return fallback
    report_path, _, report = _read_hashed_object(
        root, workflow.get("report"), "multi_page_workflow.report", errors
    )
    if report_path is None or report is None:
        return fallback
    if report.get("status") != "verified":
        errors.append("multi_page_workflow.report status is not verified")
    if base_url is not None and space_id is not None:
        try:
            report_base, report_space = contract._confluence_identity(
                report.get("base_url"), report.get("space_id"), "multi_page_workflow.report"
            )
            if report_base != base_url or report_space != space_id:
                errors.append("multi_page_workflow.report belongs to a different tenant or space")
        except ValueError as error:
            errors.append(str(error))
    raw_page_ids = report.get("page_ids")
    if (
        not isinstance(raw_page_ids, list)
        or any(not isinstance(page_id, str) or not page_id for page_id in raw_page_ids)
        or len(raw_page_ids) != len(set(raw_page_ids))
    ):
        errors.append("multi_page_workflow.report.page_ids must contain unique non-empty strings")
        page_ids: list[str] = []
    else:
        page_ids = raw_page_ids
        if len(page_ids) < 2:
            errors.append("multi_page_workflow.report must cover at least two distinct pages")

    operations = report.get("operations")
    if not isinstance(operations, list) or not operations:
        errors.append("multi_page_workflow.report.operations must be a non-empty array")
        operations = []
    observed_order = [
        str(operation.get("name") or "") if isinstance(operation, dict) else ""
        for operation in operations
    ]
    if observed_order != list(REQUIRED_WORKFLOW_OPERATIONS):
        errors.append("multi-page workflow operations must appear once in the required milestone order")
    authoritative = set(REQUIRED_WORKFLOW_OPERATIONS)
    seen: set[str] = set()
    passed: set[str] = set()
    artifact_hashes: dict[str, str] = {}
    artifacts: dict[str, dict[str, Any]] = {}
    previous_digest: str | None = None
    for index, operation in enumerate(operations):
        operation_field = f"multi_page_workflow.report.operations[{index}]"
        if not isinstance(operation, dict):
            errors.append(f"{operation_field} must be an object")
            continue
        name = str(operation.get("name") or "")
        if name not in authoritative:
            errors.append(f"{operation_field}.name is not a required operation: {name!r}")
        elif name in seen:
            errors.append(f"duplicate multi-page workflow operation: {name}")
        seen.add(name)
        if operation.get("status") != "passed":
            errors.append(f"{operation_field}.status is not passed")
        captured_at = _parse_timestamp(
            operation.get("captured_at"), f"{operation_field}.captured_at", errors
        )
        if (
            captured_at is not None
            and campaign_started is not None
            and campaign_ended is not None
            and not campaign_started <= captured_at <= campaign_ended
        ):
            errors.append(f"{operation_field}.captured_at is outside the campaign interval")
        if operation.get("previous_artifact_sha256") != previous_digest:
            errors.append(f"{operation_field} breaks the ordered artifact hash chain")
        operation_page_ids = operation.get("page_ids")
        if (
            not isinstance(operation_page_ids, list)
            or any(not isinstance(item, str) or not item for item in operation_page_ids)
            or len(operation_page_ids) != len(set(operation_page_ids))
            or set(operation_page_ids) != set(page_ids)
        ):
            errors.append(f"{operation_field}.page_ids must uniquely match workflow page IDs")
        artifact_path, artifact_bytes, artifact = _read_hashed_object(
            root,
            operation.get("artifact"),
            f"{operation_field}.artifact",
            errors,
            base=report_path.parent,
        )
        if artifact_path is not None and artifact_bytes is not None:
            artifact_hashes[name] = sha256(artifact_bytes).hexdigest()
            previous_digest = artifact_hashes[name]
        if artifact is not None and name in authoritative and page_ids:
            artifacts[name] = artifact
            try:
                if campaign_started is not None and campaign_ended is not None:
                    contract._validate_embedded_timestamps(
                        artifact,
                        campaign_started,
                        campaign_ended,
                        f"workflow.{name}",
                    )
                semantic_page_ids = contract._validate_workflow_source(
                    name, artifact, page_ids, base_url, space_id
                )
                if set(semantic_page_ids) != set(page_ids):
                    raise ValueError(f"workflow.{name} semantic page set does not match its receipt")
            except ValueError as error:
                errors.append(str(error))
            else:
                if operation.get("status") == "passed":
                    passed.add(name)
    if report.get("artifact_chain_head_sha256") != previous_digest:
        errors.append("multi_page_workflow.report artifact chain head is stale or invalid")
    distinct_non_inventory = [
        digest
        for name, digest in artifact_hashes.items()
        if name not in {"scan", "inventory"}
    ]
    if len(distinct_non_inventory) != len(set(distinct_non_inventory)):
        errors.append("multi-page workflow operation artifacts must be distinct receipts")
    if authoritative.issubset(artifacts) and authoritative.issubset(artifact_hashes):
        try:
            contract._validate_workflow_bindings(artifacts, artifact_hashes, page_ids)
        except ValueError as error:
            errors.append(str(error))
    if artifact_hashes.get("explore") in {
        artifact_hashes.get("scan"),
        artifact_hashes.get("inventory"),
    }:
        errors.append("explore must use a distinct persisted filtered artifact")
    missing = sorted(authoritative - passed)
    if missing:
        errors.append(f"multi-page workflow operations have no passing evidence: {missing}")
    return {
        "pages": len(set(page_ids)),
        "page_ids": page_ids,
        "required": list(REQUIRED_WORKFLOW_OPERATIONS),
        "passed": sorted(passed),
        "missing": missing,
    }


def _validate_timeline(
    root: Path,
    manifest: dict[str, Any],
    campaign_id: str,
    started: datetime | None,
    ended: datetime | None,
    base_url: str | None,
    space_id: str | None,
    case_results: list[dict[str, Any]],
    errors: list[str],
) -> None:
    timeline_wrapper = manifest.get("timeline")
    if not isinstance(timeline_wrapper, dict):
        errors.append("timeline must be an object")
        return
    timeline_path, _, timeline = _read_hashed_object(
        root, timeline_wrapper.get("report"), "timeline.report", errors
    )
    if timeline_path is None or timeline is None:
        return
    if timeline.get("schema_version") != SCHEMA_VERSION or timeline.get("status") != "verified":
        errors.append("timeline.report must be a verified current-schema receipt")
    if timeline.get("campaign_id") != campaign_id:
        errors.append("timeline.report is bound to a different campaign_id")
    if base_url is not None and space_id is not None:
        try:
            receipt_base, receipt_space = contract._confluence_identity(
                timeline.get("base_url"), timeline.get("space_id"), "timeline.report"
            )
            if receipt_base != base_url or receipt_space != space_id:
                errors.append("timeline.report belongs to a different tenant or space")
        except ValueError as error:
            errors.append(str(error))
    page_ids = [str(result.get("page_id") or "") for result in case_results]
    receipt_page_ids = timeline.get("page_ids")
    if receipt_page_ids != page_ids:
        errors.append("timeline.report page IDs do not exactly match test-case order")
    timeline_started = _parse_timestamp(timeline.get("started_at"), "timeline.report.started_at", errors)
    timeline_ended = _parse_timestamp(timeline.get("ended_at"), "timeline.report.ended_at", errors)
    materialized = _parse_timestamp(
        timeline.get("materialized_at"), "timeline.report.materialized_at", errors
    )
    if started is not None and timeline_started != started:
        errors.append("timeline.report.started_at does not match the campaign")
    if ended is not None and timeline_ended != ended:
        errors.append("timeline.report.ended_at does not match the campaign")
    if materialized is not None:
        if ended is not None and not (
            ended <= materialized <= ended + timedelta(seconds=contract.FINALIZATION_GRACE_SECONDS)
        ):
            errors.append("timeline.report was not materialized within 30 minutes after campaign end")
        if materialized > datetime.now(timezone.utc):
            errors.append("timeline.report.materialized_at cannot be in the future")

    baseline_receipts = timeline.get("baseline_receipts")
    expected_baselines = {
        str(result.get("page_id") or ""): (
            result.get("baseline_path"),
            result.get("baseline_sha256"),
        )
        for result in case_results
    }
    baseline_times: list[datetime] = []
    seen_baselines: set[str] = set()
    if not isinstance(baseline_receipts, list) or not baseline_receipts:
        errors.append("timeline.report.baseline_receipts must be a non-empty array")
        baseline_receipts = []
    for index, receipt in enumerate(baseline_receipts):
        field = f"timeline.report.baseline_receipts[{index}]"
        if not isinstance(receipt, dict):
            errors.append(f"{field} must be an object")
            continue
        page_id = str(receipt.get("page_id") or "")
        if not page_id or page_id in seen_baselines:
            errors.append(f"{field}.page_id must be unique and non-empty")
        seen_baselines.add(page_id)
        timestamp = _parse_timestamp(receipt.get("captured_at"), f"{field}.captured_at", errors)
        if timestamp is not None:
            baseline_times.append(timestamp)
            if started is not None and ended is not None and not started <= timestamp <= ended:
                errors.append(f"{field}.captured_at is outside the campaign interval")
        expected_path, expected_digest = expected_baselines.get(page_id, (None, None))
        path = _resolve_evidence_path(root, receipt.get("path"), f"{field}.path", errors)
        digest = receipt.get("sha256")
        if not isinstance(digest, str) or not SHA256_PATTERN.fullmatch(digest):
            errors.append(f"{field}.sha256 must be a lowercase SHA-256 digest")
        elif path is not None:
            actual = sha256(path.read_bytes()).hexdigest()
            if actual != digest:
                errors.append(f"{field} digest mismatch: expected {digest}, got {actual}")
        if path != expected_path or digest != expected_digest:
            errors.append(f"{field} is not bound to the test case's exact baseline screenshot")
    if seen_baselines != set(page_ids):
        errors.append("timeline.report baseline receipts do not exactly cover campaign pages")
    earliest_baseline = min(baseline_times) if baseline_times else None
    if earliest_baseline is not None and started is not None:
        if not 0 <= (earliest_baseline - started).total_seconds() <= contract.START_ANCHOR_GRACE_SECONDS:
            errors.append("timeline.report has no baseline captured within 5 minutes of campaign start")
    if earliest_baseline is not None and materialized is not None:
        if (materialized - earliest_baseline).total_seconds() < contract.MINIMUM_DURATION_SECONDS:
            errors.append("fewer than 8 real hours elapsed between baseline capture and materialization")

    api_times = [result.get("api_time") for result in case_results]
    browser_times = [result.get("browser_time") for result in case_results]
    expected_times: list[datetime | None] = [
        started,
        earliest_baseline,
        max(api_times) if api_times and all(isinstance(value, datetime) for value in api_times) else None,
        max(browser_times)
        if browser_times and all(isinstance(value, datetime) for value in browser_times)
        else None,
        ended,
        materialized,
    ]
    milestones = timeline.get("milestones")
    if not isinstance(milestones, list):
        errors.append("timeline.report.milestones must be an array")
        milestones = []
    names = [
        str(milestone.get("name") or "") if isinstance(milestone, dict) else ""
        for milestone in milestones
    ]
    if names != list(contract.MILESTONE_NAMES):
        errors.append("timeline.report milestones are missing, duplicated, or reordered")
    previous: str | None = None
    observed_times: list[datetime] = []
    for index, milestone in enumerate(milestones):
        field = f"timeline.report.milestones[{index}]"
        if not isinstance(milestone, dict):
            errors.append(f"{field} must be an object")
            continue
        if milestone.get("previous_sha256") != previous:
            errors.append(f"{field} breaks the milestone hash chain")
        claimed_digest = milestone.get("sha256")
        unsigned = {key: value for key, value in milestone.items() if key != "sha256"}
        actual_digest = contract._canonical_json_digest(unsigned)
        if claimed_digest != actual_digest:
            errors.append(f"{field}.sha256 does not bind the exact milestone")
        previous = claimed_digest if isinstance(claimed_digest, str) else None
        occurred = _parse_timestamp(milestone.get("occurred_at"), f"{field}.occurred_at", errors)
        if occurred is not None:
            observed_times.append(occurred)
        if index < len(expected_times) and expected_times[index] is not None and occurred != expected_times[index]:
            errors.append(f"{field}.occurred_at is stale or bound to the wrong event")
    if observed_times != sorted(observed_times):
        errors.append("timeline.report milestones are not chronological")
    if timeline.get("milestone_chain_head_sha256") != previous:
        errors.append("timeline.report milestone chain head is stale or invalid")


def _phase_coverage(
    intervals: list[tuple[datetime, datetime, str]],
    started: datetime | None,
    ended: datetime | None,
    errors: list[str],
) -> None:
    if started is None or ended is None or not intervals:
        return
    if intervals[0][0] != started:
        errors.append("phases do not begin at the campaign start")
    covered_until = intervals[0][1]
    previous_started = intervals[0][0]
    for phase_started, phase_ended, field in intervals[1:]:
        if phase_started < previous_started:
            errors.append(f"phase milestones are reordered at {field}")
        if phase_started > covered_until:
            errors.append(f"phase coverage has a gap before {field}")
        elif phase_started < covered_until:
            errors.append(f"phase coverage overlaps before {field}")
        if phase_ended > covered_until:
            covered_until = phase_ended
        previous_started = phase_started
    if covered_until != ended:
        errors.append("phases do not cover through the campaign end")


def validate_campaign(manifest_path: Path) -> dict[str, Any]:
    """Validate a campaign manifest and every bound local evidence artifact."""

    manifest_path = manifest_path.resolve()
    errors: list[str] = []
    try:
        _, manifest = _load_object_bytes(manifest_path)
    except ValueError as error:
        return {
            "status": "failed",
            "campaign_id": "",
            "duration_hours": 0.0,
            "phases": 0,
            "test_cases": 0,
            "workflow": {
                "pages": 0,
                "page_ids": [],
                "required": list(REQUIRED_WORKFLOW_OPERATIONS),
                "passed": [],
                "missing": list(REQUIRED_WORKFLOW_OPERATIONS),
            },
            "coverage": {
                "required": list(REQUIRED_COVERAGE_CATEGORIES),
                "passed": [],
                "missing": list(REQUIRED_COVERAGE_CATEGORIES),
            },
            "errors": [str(error)],
        }
    root = manifest_path.parent.resolve()
    if manifest.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}")
    raw_campaign_id = manifest.get("campaign_id")
    campaign_id = raw_campaign_id.strip() if isinstance(raw_campaign_id, str) else ""
    if not campaign_id:
        errors.append("campaign_id must be non-empty")

    configured_minimum = manifest.get("minimum_duration_hours")
    required_duration = MINIMUM_DURATION_HOURS
    if (
        not isinstance(configured_minimum, (int, float))
        or isinstance(configured_minimum, bool)
        or not math.isfinite(float(configured_minimum))
    ):
        errors.append("minimum_duration_hours must be a finite number")
    elif float(configured_minimum) < MINIMUM_DURATION_HOURS:
        errors.append("minimum_duration_hours cannot be less than 8")
    else:
        required_duration = float(configured_minimum)

    started = _parse_timestamp(manifest.get("started_at"), "started_at", errors)
    ended = _parse_timestamp(manifest.get("ended_at"), "ended_at", errors)
    duration_hours = 0.0
    if started is not None and ended is not None:
        duration_hours = (ended - started).total_seconds() / 3600
        if ended < started:
            errors.append("ended_at cannot precede started_at")
        if duration_hours < required_duration:
            errors.append(
                f"campaign elapsed time is {duration_hours:.3f} hours; "
                f"at least {required_duration:g} hours are required"
            )
        if ended > datetime.now(timezone.utc):
            errors.append("ended_at cannot be in the future")
        if started > datetime.now(timezone.utc):
            errors.append("started_at cannot be in the future")

    confluence = manifest.get("confluence")
    base_url: str | None = None
    space_id: str | None = None
    if not isinstance(confluence, dict):
        errors.append("confluence must be a tenant and space identity object")
    else:
        try:
            base_url, space_id = contract._confluence_identity(
                confluence.get("base_url"), confluence.get("space_id"), "confluence"
            )
        except ValueError as error:
            errors.append(str(error))

    declared_categories = manifest.get("required_coverage_categories")
    if not isinstance(declared_categories, list) or any(
        not isinstance(value, str) for value in declared_categories
    ):
        errors.append("required_coverage_categories must be an array of strings")
        declared_set: set[str] = set()
    else:
        declared_set = set(declared_categories)
        if len(declared_categories) != len(declared_set):
            errors.append("required_coverage_categories contains duplicates")
    authoritative = set(REQUIRED_COVERAGE_CATEGORIES)
    if declared_set != authoritative:
        missing_declarations = sorted(authoritative - declared_set)
        unknown_declarations = sorted(declared_set - authoritative)
        if missing_declarations:
            errors.append(f"required coverage categories were removed: {missing_declarations}")
        if unknown_declarations:
            errors.append(f"unknown required coverage categories: {unknown_declarations}")

    workflow_result = _validate_multi_page_workflow(
        root, manifest, started, ended, base_url, space_id, errors
    )
    workflow_page_ids = set(workflow_result.get("page_ids") or [])
    phases = manifest.get("phases")
    if not isinstance(phases, list) or not phases:
        errors.append("phases must contain at least one phase")
        phases = []

    phase_ids: set[str] = set()
    test_ids: set[str] = set()
    test_page_ids: set[str] = set()
    passed_categories: set[str] = set()
    phase_intervals: list[tuple[datetime, datetime, str]] = []
    case_results: list[dict[str, Any]] = []
    test_count = 0
    for phase_index, phase in enumerate(phases):
        phase_field = f"phases[{phase_index}]"
        if not isinstance(phase, dict):
            errors.append(f"{phase_field} must be an object")
            continue
        phase_id = str(phase.get("id") or "")
        if not phase_id:
            errors.append(f"{phase_field}.id must be non-empty")
        elif phase_id in phase_ids:
            errors.append(f"duplicate phase id: {phase_id}")
        phase_ids.add(phase_id)
        phase_started = _parse_timestamp(phase.get("started_at"), f"{phase_field}.started_at", errors)
        phase_ended = _parse_timestamp(phase.get("ended_at"), f"{phase_field}.ended_at", errors)
        if phase_started is not None and phase_ended is not None:
            if phase_ended < phase_started:
                errors.append(f"{phase_field} ends before it starts")
            else:
                phase_intervals.append((phase_started, phase_ended, phase_field))
            if started is not None and phase_started < started:
                errors.append(f"{phase_field} starts before the campaign")
            if ended is not None and phase_ended > ended:
                errors.append(f"{phase_field} ends after the campaign")

        test_cases = phase.get("test_cases")
        if not isinstance(test_cases, list) or not test_cases:
            errors.append(f"{phase_field}.test_cases must contain at least one test case")
            continue
        for case_index, test_case in enumerate(test_cases):
            case_field = f"{phase_field}.test_cases[{case_index}]"
            test_count += 1
            if not isinstance(test_case, dict):
                errors.append(f"{case_field} must be an object")
                continue
            test_id = str(test_case.get("id") or "")
            if not test_id:
                errors.append(f"{case_field}.id must be non-empty")
            elif test_id in test_ids:
                errors.append(f"duplicate test case id: {test_id}")
            test_ids.add(test_id)
            status = test_case.get("status")
            if status not in ALLOWED_TEST_STATUSES:
                errors.append(f"{case_field}.status is invalid: {status!r}")
            elif status != "passed":
                errors.append(f"{case_field}.status is {status!r}; completed campaigns require passed")
            categories = test_case.get("coverage_categories")
            if not isinstance(categories, list) or not categories or any(
                not isinstance(value, str) for value in categories
            ):
                errors.append(f"{case_field}.coverage_categories must be a non-empty array of strings")
                categories = []
            unknown = sorted(set(categories) - authoritative)
            if unknown:
                errors.append(f"{case_field} has unknown coverage categories: {unknown}")
            if status == "passed":
                passed_categories.update(set(categories) & authoritative)
            case_result = _validate_case_evidence(
                root,
                test_case,
                case_field,
                phase_started,
                phase_ended,
                base_url,
                space_id,
                errors,
            )
            case_results.append(case_result)
            page_id = str(case_result.get("page_id") or "")
            if page_id in test_page_ids:
                errors.append(f"duplicate test case page_id: {page_id}")
            if page_id:
                test_page_ids.add(page_id)

    _phase_coverage(phase_intervals, started, ended, errors)
    _validate_timeline(
        root,
        manifest,
        campaign_id,
        started,
        ended,
        base_url,
        space_id,
        case_results,
        errors,
    )
    if test_page_ids != workflow_page_ids:
        errors.append(
            "test case page IDs must exactly match multi-page workflow page IDs: "
            f"cases={sorted(test_page_ids)}, workflow={sorted(workflow_page_ids)}"
        )
    missing_categories = sorted(authoritative - passed_categories)
    if missing_categories:
        errors.append(f"required coverage categories have no passing test: {missing_categories}")

    return {
        "status": "verified" if not errors else "failed",
        "campaign_id": campaign_id,
        "duration_hours": round(duration_hours, 6),
        "phases": len(phases),
        "test_cases": test_count,
        "workflow": workflow_result,
        "coverage": {
            "required": list(REQUIRED_COVERAGE_CATEGORIES),
            "passed": sorted(passed_categories),
            "missing": missing_categories,
        },
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path, help="Path to a completed campaign JSON manifest")
    args = parser.parse_args()
    result = validate_campaign(args.manifest)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["status"] == "verified" else 2


if __name__ == "__main__":
    raise SystemExit(main())
