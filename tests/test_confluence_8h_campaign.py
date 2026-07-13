"""Security and integrity tests for the Confluence eight-hour campaign package."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from hashlib import sha256
import importlib.util
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys
from types import ModuleType
from typing import Any
import zlib

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = REPO_ROOT / "evaluations" / "confluence-8h-campaign" / "validate_campaign.py"
MATERIALIZER = REPO_ROOT / "evaluations" / "confluence-8h-campaign" / "materialize_live_campaign.py"
START = "2025-01-01T09:00:00+00:00"
END = "2025-01-01T17:00:00+00:00"
API_TIME = "2025-01-01T12:00:00+00:00"
BROWSER_TIME = "2025-01-01T12:05:00+00:00"
BASE_URL = "https://example.atlassian.net"
SPACE_ID = "123"
LIVE_NOW = datetime.now(timezone.utc).replace(microsecond=0)
LIVE_END_DATETIME = LIVE_NOW - timedelta(minutes=1)
LIVE_START_DATETIME = LIVE_END_DATETIME - timedelta(hours=8)
LIVE_START = LIVE_START_DATETIME.isoformat()
LIVE_END = LIVE_END_DATETIME.isoformat()
LIVE_API_TIME = (LIVE_END_DATETIME - timedelta(minutes=10)).isoformat()
LIVE_BROWSER_TIME = (LIVE_END_DATETIME - timedelta(minutes=5)).isoformat()


def load_validator() -> ModuleType:
    spec = importlib.util.spec_from_file_location("test_confluence_8h_validator", VALIDATOR)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_materializer() -> ModuleType:
    spec = importlib.util.spec_from_file_location("test_confluence_8h_materializer", MATERIALIZER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def make_png(rgb: tuple[int, int, int]) -> bytes:
    def chunk(kind: bytes, payload: bytes) -> bytes:
        return (
            struct.pack(">I", len(payload))
            + kind
            + payload
            + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)
        )

    header = struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)
    pixels = b"\x00" + bytes(rgb)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header) + chunk(
        b"IDAT", zlib.compress(pixels)
    ) + chunk(b"IEND", b"")


def make_crc_valid_but_undecodable_png() -> bytes:
    def chunk(kind: bytes, payload: bytes) -> bytes:
        return (
            struct.pack(">I", len(payload))
            + kind
            + payload
            + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)
        )

    header = struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", header)
        + chunk(b"IDAT", zlib.compress(b"x"))
        + chunk(b"IEND", b"")
    )


def file_record(path: Path, root: Path) -> dict[str, str]:
    return {
        "path": path.relative_to(root).as_posix(),
        "sha256": sha256(path.read_bytes()).hexdigest(),
    }


def noop_plan(page_id: str, digest: str, version: int) -> dict[str, Any]:
    return {
        "page_id": page_id,
        "desired_state_sha256": digest,
        "current_version": version,
        "expected_version": version,
        "no_op": True,
        "page_update": False,
        "body_changed": False,
        "metadata_changed": False,
        "attachments": [],
        "labels": {"added": [], "removed": []},
        "content_state_changed": False,
        "suppressed_attachments": [],
        "suppressed_labels": {"added": [], "removed": []},
        "suppressed_content_state_changed": False,
        "sync": {"attachments": True, "labels": True, "content_state": True},
    }


def write_case_evidence(root: Path, case_id: str, page_id: str, color: int) -> dict[str, Any]:
    evidence = root / "evidence" / case_id
    evidence.mkdir(parents=True, exist_ok=True)
    baseline = evidence / "baseline.png"
    final = evidence / "final.png"
    baseline.write_bytes(make_png((color, 20, 30)))
    final.write_bytes(make_png((color, 80, 90)))
    operation_id = f"operation-{page_id}"
    digest = sha256(f"desired-{page_id}".encode()).hexdigest()
    version = int(page_id) if page_id.isdigit() else color + 1
    api_path = evidence / "report.json"
    write_json(
        api_path,
        {
            "status": "verified",
            "page_id": page_id,
            "operation_id": operation_id,
            "desired_state_sha256": digest,
            "remote_version": version,
            "verified_at": API_TIME,
            "checks": [{"name": "storage-equivalent", "passed": True}],
        },
    )
    browser_path = evidence / "browser-ground-truth.json"
    write_json(
        browser_path,
        {
            "status": "verified",
            "page_id": page_id,
            "operation_id": operation_id,
            "api_report_sha256": sha256(api_path.read_bytes()).hexdigest(),
            "desired_state_sha256": digest,
            "remote_version": version,
            "verified_at": BROWSER_TIME,
            "page_url": f"{BASE_URL}/wiki/spaces/lab/pages/{page_id}/fixture",
            "checks": [{"name": "rendered-page", "passed": True}],
            "baseline": {
                "path": baseline.name,
                "sha256": sha256(baseline.read_bytes()).hexdigest(),
            },
            "final_screenshots": [
                {"path": final.name, "sha256": sha256(final.read_bytes()).hexdigest()}
            ],
        },
    )
    noop_path = evidence / "noop-dry-run.json"
    write_json(noop_path, {"status": "dry-run", "plan": noop_plan(page_id, digest, version)})
    workspace_path = evidence / "workspace-manifest.json"
    write_json(
        workspace_path,
        {
            "schema_version": "1.0",
            "base_url": BASE_URL,
            "downloaded_at": "2025-01-01T10:00:00+00:00",
            "last_verified_at": "2025-01-01T12:01:00+00:00",
            "last_verified_operation_id": operation_id,
            "last_verified_desired_state_sha256": digest,
            "page": {
                "page_id": page_id,
                "space_id": SPACE_ID,
                "version": version,
                "web_url": f"{BASE_URL}/spaces/lab/pages/{page_id}/fixture",
            },
        },
    )
    return {
        "api_report": file_record(api_path, root),
        "browser_ground_truth": file_record(browser_path, root),
        "noop_dry_run": file_record(noop_path, root),
        "workspace_manifest": file_record(workspace_path, root),
    }


def workflow_payload(operation: str, page_ids: list[str]) -> dict[str, Any]:
    if operation in {"scan", "inventory"}:
        return {
            "base_url": BASE_URL,
            "space_id": SPACE_ID,
            "status": "verified",
            "pages": [{"page_id": page_id, "space_id": SPACE_ID} for page_id in page_ids]
            + [{"page_id": "inventory-extra", "space_id": SPACE_ID}],
        }
    if operation == "explore":
        return {
            "status": "queried",
            "inventory_status": "verified",
            "filters": {"text": ["campaign"]},
            "count": len(page_ids),
            "pages": [{"page_id": page_id, "space_id": SPACE_ID} for page_id in page_ids],
        }
    status = {
        "batch-download": "downloaded",
        "batch-validate": "valid",
        "batch-dry-run": "planned",
        "batch-upload": "verified",
        "batch-verify": "verified",
    }[operation]
    pages: list[dict[str, Any]] = []
    for page_id in page_ids:
        row: dict[str, Any] = {"page_id": page_id, "status": status}
        if operation == "batch-dry-run":
            row["plan"] = {
                "page_id": page_id,
                "no_op": True,
                "page_update": False,
                "attachments": [],
                "labels": {"added": [], "removed": []},
                "content_state_changed": False,
            }
        elif operation == "batch-upload":
            row["result"] = {"verification": {"status": "verified"}}
        elif operation == "batch-verify":
            row["verification"] = {"status": "verified"}
        pages.append(row)
    payload: dict[str, Any] = {"status": "verified", "pages": pages}
    if operation == "batch-download":
        payload.update(
            {
                "base_url": BASE_URL,
                "space_id": SPACE_ID,
                "batch_id": "batch-fixture",
            }
        )
    if operation in {"batch-validate", "batch-dry-run", "batch-upload", "batch-verify"}:
        payload["dependency_order"] = page_ids
    if operation in {"batch-dry-run", "batch-upload"}:
        payload["batch_id"] = "batch-fixture"
    return payload


def write_workflow(root: Path, module: ModuleType, page_ids: list[str]) -> dict[str, str]:
    workflow_dir = root / "evidence" / "multi-page-workflow"
    operations: list[dict[str, Any]] = []
    artifact_hashes: dict[str, str] = {}
    previous: str | None = None
    for operation in module.REQUIRED_WORKFLOW_OPERATIONS:
        artifact = workflow_dir / f"{operation}.json"
        payload = workflow_payload(operation, page_ids)
        if operation == "batch-download":
            payload["inventory_sha256"] = artifact_hashes["inventory"]
        if operation == "batch-upload":
            payload["batch_manifest_sha256"] = artifact_hashes["batch-download"]
        write_json(artifact, payload)
        digest = sha256(artifact.read_bytes()).hexdigest()
        artifact_hashes[operation] = digest
        operations.append(
            {
                "name": operation,
                "status": "passed",
                "page_ids": page_ids,
                "captured_at": API_TIME,
                "previous_artifact_sha256": previous,
                "artifact": {"path": artifact.name, "sha256": digest},
            }
        )
        previous = digest
    report = workflow_dir / "report.json"
    write_json(
        report,
        {
            "status": "verified",
            "base_url": BASE_URL,
            "space_id": SPACE_ID,
            "page_ids": page_ids,
            "operations": operations,
            "artifact_chain_head_sha256": previous,
        },
    )
    return file_record(report, root)


def write_timeline(
    root: Path,
    module: ModuleType,
    page_cases: list[tuple[str, str]],
    *,
    campaign_id: str = "complete-campaign",
    started_at: str = START,
    ended_at: str = END,
    materialized_at: str = END,
    api_time: str = API_TIME,
    browser_time: str = BROWSER_TIME,
) -> dict[str, str]:
    baseline_receipts: list[dict[str, str]] = []
    for page_id, case_id in page_cases:
        baseline = root / "evidence" / case_id / "baseline.png"
        baseline_receipts.append(
            {
                "page_id": page_id,
                "path": baseline.relative_to(root).as_posix(),
                "sha256": sha256(baseline.read_bytes()).hexdigest(),
                "captured_at": started_at,
            }
        )
    previous: str | None = None
    milestones: list[dict[str, Any]] = []
    times = (started_at, started_at, api_time, browser_time, ended_at, materialized_at)
    for name, occurred_at in zip(module.contract.MILESTONE_NAMES, times, strict=True):
        milestone: dict[str, Any] = {
            "name": name,
            "occurred_at": occurred_at,
            "previous_sha256": previous,
        }
        milestone["sha256"] = module.contract._canonical_json_digest(milestone)
        milestones.append(milestone)
        previous = milestone["sha256"]
    timeline = root / "evidence" / "campaign-timeline.json"
    write_json(
        timeline,
        {
            "schema_version": module.SCHEMA_VERSION,
            "status": "verified",
            "campaign_id": campaign_id,
            "base_url": BASE_URL,
            "space_id": SPACE_ID,
            "page_ids": [page_id for page_id, _ in page_cases],
            "started_at": started_at,
            "ended_at": ended_at,
            "materialized_at": materialized_at,
            "baseline_receipts": baseline_receipts,
            "milestones": milestones,
            "milestone_chain_head_sha256": previous,
        },
    )
    return file_record(timeline, root)


def build_complete_campaign(tmp_path: Path) -> tuple[ModuleType, Path, Path]:
    module = load_validator()
    root = tmp_path / "campaign"
    page_ids = ["42", "43"]
    first_evidence = write_case_evidence(root, "case-1", "42", 30)
    second_evidence = write_case_evidence(root, "case-2", "43", 60)
    categories = list(module.REQUIRED_COVERAGE_CATEGORIES)
    manifest = root / "campaign.json"
    write_json(
        manifest,
        {
            "schema_version": module.SCHEMA_VERSION,
            "campaign_id": "complete-campaign",
            "started_at": START,
            "ended_at": END,
            "minimum_duration_hours": 8,
            "confluence": {"base_url": BASE_URL, "space_id": SPACE_ID},
            "timeline": {
                "report": write_timeline(
                    root, module, [("42", "case-1"), ("43", "case-2")]
                )
            },
            "required_coverage_categories": categories,
            "multi_page_workflow": {"report": write_workflow(root, module, page_ids)},
            "phases": [
                {
                    "id": "roundtrip",
                    "name": "Complete round-trip",
                    "started_at": START,
                    "ended_at": END,
                    "test_cases": [
                        {
                            "id": "case-1",
                            "name": "First acceptance case",
                            "page_id": "42",
                            "status": "passed",
                            "coverage_categories": categories[:6],
                            "evidence": first_evidence,
                        },
                        {
                            "id": "case-2",
                            "name": "Second acceptance case",
                            "page_id": "43",
                            "status": "passed",
                            "coverage_categories": categories[6:],
                            "evidence": second_evidence,
                        },
                    ],
                }
            ],
        },
    )
    return module, manifest, root / "evidence" / "case-1" / "final.png"


def write_live_case(source: Path, case: dict[str, Any], color: int) -> None:
    page_id = str(case["page_id"])
    verification = source / "campaign" / "workspaces" / page_id / "verification"
    verification.mkdir(parents=True, exist_ok=True)
    baseline = verification / "baseline.png"
    final = verification / f"final-{page_id}.png"
    baseline.write_bytes(make_png((color, 10, 20)))
    final.write_bytes(make_png((color, 70, 80)))
    os.utime(baseline, (LIVE_START_DATETIME.timestamp(), LIVE_START_DATETIME.timestamp()))
    digest = sha256(f"live-{page_id}".encode()).hexdigest()
    operation_id = f"live-operation-{page_id}"
    version = color + 1
    api = verification / "report.json"
    write_json(
        api,
        {
            "status": "verified",
            "page_id": page_id,
            "operation_id": operation_id,
            "desired_state_sha256": digest,
            "remote_version": version,
            "verified_at": LIVE_API_TIME,
            "checks": [{"name": "api-equivalent", "passed": True}],
        },
    )
    write_json(
        verification / "browser-ground-truth.json",
        {
            "status": "verified",
            "page_id": page_id,
            "operation_id": operation_id,
            "api_report_sha256": sha256(api.read_bytes()).hexdigest(),
            "desired_state_sha256": digest,
            "remote_version": version,
            "verified_at": LIVE_BROWSER_TIME,
            "page_url": f"{BASE_URL}/wiki/spaces/lab/pages/{page_id}/fixture",
            "checks": [{"name": "rendered", "passed": True}],
            "baseline": {"path": baseline.name, "sha256": sha256(baseline.read_bytes()).hexdigest()},
            "final_screenshots": [
                {"path": final.name, "sha256": sha256(final.read_bytes()).hexdigest()}
            ],
        },
    )
    write_json(
        verification / "noop-dry-run.json",
        {"status": "dry-run", "plan": noop_plan(page_id, digest, version)},
    )
    write_json(
        verification.parent / "manifest.json",
        {
            "schema_version": "1.0",
            "base_url": BASE_URL,
            "downloaded_at": (LIVE_START_DATETIME + timedelta(minutes=10)).isoformat(),
            "last_verified_at": (LIVE_END_DATETIME - timedelta(minutes=9)).isoformat(),
            "last_verified_operation_id": operation_id,
            "last_verified_desired_state_sha256": digest,
            "page": {
                "page_id": page_id,
                "space_id": SPACE_ID,
                "version": version,
                "web_url": f"{BASE_URL}/spaces/lab/pages/{page_id}/fixture",
            },
        },
    )


def build_live_materializer_source(tmp_path: Path) -> tuple[ModuleType, Path]:
    module = load_materializer()
    source = tmp_path / "live-batch"
    page_ids = [str(case["page_id"]) for case in module.CASE_DEFINITIONS]
    for index, case in enumerate(module.CASE_DEFINITIONS, start=1):
        write_live_case(source, case, index * 30)
    inventory = source / "space-inventory.json"
    write_json(inventory, workflow_payload("inventory", page_ids))
    inventory_time = LIVE_START_DATETIME + timedelta(minutes=20)
    os.utime(inventory, (inventory_time.timestamp(), inventory_time.timestamp()))
    explore = source / "campaign" / "space-explore-final.json"
    write_json(
        explore,
        workflow_payload("explore", page_ids),
    )
    explore_time = LIVE_START_DATETIME + timedelta(minutes=25)
    os.utime(explore, (explore_time.timestamp(), explore_time.timestamp()))
    batch_payload = workflow_payload("batch-download", page_ids)
    batch_payload["inventory_sha256"] = sha256(inventory.read_bytes()).hexdigest()
    batch = source / "campaign" / "batch-manifest.json"
    write_json(batch, batch_payload)
    batch_time = LIVE_START_DATETIME + timedelta(minutes=30)
    os.utime(batch, (batch_time.timestamp(), batch_time.timestamp()))
    sources = {
        "batch-local-validation-v2.json": workflow_payload("batch-validate", page_ids),
        "batch-plan-final-noop.json": workflow_payload("batch-dry-run", page_ids),
        "batch-upload-report.json": workflow_payload("batch-upload", page_ids),
        "batch-verify-final.json": workflow_payload("batch-verify", page_ids),
    }
    sources["batch-upload-report.json"]["batch_manifest_sha256"] = sha256(
        batch.read_bytes()
    ).hexdigest()
    for index, (filename, payload) in enumerate(sources.items(), start=4):
        path = source / "campaign" / filename
        write_json(path, payload)
        captured = LIVE_START_DATETIME + timedelta(minutes=index * 10)
        os.utime(path, (captured.timestamp(), captured.timestamp()))
    return module, source


def read_manifest(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def rehash_timeline_milestones(timeline: dict[str, Any], module: ModuleType) -> None:
    previous: str | None = None
    for milestone in timeline["milestones"]:
        milestone["previous_sha256"] = previous
        unsigned = {key: value for key, value in milestone.items() if key != "sha256"}
        milestone["sha256"] = module.contract._canonical_json_digest(unsigned)
        previous = milestone["sha256"]
    timeline["milestone_chain_head_sha256"] = previous


def test_complete_campaign_with_exactly_eight_hours_is_verified(tmp_path: Path) -> None:
    module, manifest, _ = build_complete_campaign(tmp_path)
    result = module.validate_campaign(manifest)
    assert result["status"] == "verified", result
    assert result["duration_hours"] == 8.0
    assert result["test_cases"] == 2
    assert result["workflow"]["page_ids"] == ["42", "43"]
    assert result["errors"] == []


def test_campaign_rejects_less_than_eight_elapsed_hours(tmp_path: Path) -> None:
    module, manifest, _ = build_complete_campaign(tmp_path)
    payload = read_manifest(manifest)
    payload["ended_at"] = "2025-01-01T16:59:59+00:00"
    payload["phases"][0]["ended_at"] = payload["ended_at"]
    write_json(manifest, payload)
    result = module.validate_campaign(manifest)
    assert result["status"] == "failed"
    assert any("at least 8 hours" in error for error in result["errors"])


def test_campaign_rejects_future_end_and_phase_gap(tmp_path: Path) -> None:
    module, manifest, _ = build_complete_campaign(tmp_path)
    payload = read_manifest(manifest)
    payload["started_at"] = "2099-01-01T09:00:00+00:00"
    payload["ended_at"] = "2099-01-01T17:00:00+00:00"
    payload["phases"][0]["started_at"] = payload["started_at"]
    payload["phases"][0]["ended_at"] = "2099-01-01T10:00:00+00:00"
    write_json(manifest, payload)
    result = module.validate_campaign(manifest)
    assert any("ended_at cannot be in the future" in error for error in result["errors"])
    assert any("phases do not cover through" in error for error in result["errors"])


def test_campaign_rejects_backdated_start_even_when_timeline_is_rehashed(tmp_path: Path) -> None:
    module, manifest, _ = build_complete_campaign(tmp_path)
    payload = read_manifest(manifest)
    backdated_start = "2025-01-01T08:00:00+00:00"
    payload["started_at"] = backdated_start
    payload["phases"][0]["started_at"] = backdated_start
    timeline_record = payload["timeline"]["report"]
    timeline_path = manifest.parent / timeline_record["path"]
    timeline = read_manifest(timeline_path)
    timeline["started_at"] = backdated_start
    timeline["milestones"][0]["occurred_at"] = backdated_start
    rehash_timeline_milestones(timeline, module)
    write_json(timeline_path, timeline)
    timeline_record["sha256"] = sha256(timeline_path.read_bytes()).hexdigest()
    write_json(manifest, payload)

    result = module.validate_campaign(manifest)
    assert result["status"] == "failed"
    assert any("within 5 minutes of campaign start" in error for error in result["errors"])


def test_campaign_rejects_less_than_eight_observed_hours_despite_declared_duration(
    tmp_path: Path,
) -> None:
    module, manifest, _ = build_complete_campaign(tmp_path)
    payload = read_manifest(manifest)
    timeline_record = payload["timeline"]["report"]
    timeline_path = manifest.parent / timeline_record["path"]
    timeline = read_manifest(timeline_path)
    late_baseline = "2025-01-01T09:04:00+00:00"
    for receipt in timeline["baseline_receipts"]:
        receipt["captured_at"] = late_baseline
    timeline["milestones"][1]["occurred_at"] = late_baseline
    rehash_timeline_milestones(timeline, module)
    write_json(timeline_path, timeline)
    timeline_record["sha256"] = sha256(timeline_path.read_bytes()).hexdigest()
    write_json(manifest, payload)

    result = module.validate_campaign(manifest)
    assert result["duration_hours"] == 8.0
    assert result["status"] == "failed"
    assert any("fewer than 8 real hours elapsed" in error for error in result["errors"])


def test_campaign_rejects_reordered_phase_and_workflow_milestones(tmp_path: Path) -> None:
    module, manifest, _ = build_complete_campaign(tmp_path)
    payload = read_manifest(manifest)
    cases = payload["phases"][0]["test_cases"]
    payload["phases"] = [
        {
            "id": "late",
            "started_at": "2025-01-01T13:00:00+00:00",
            "ended_at": END,
            "test_cases": [cases[1]],
        },
        {
            "id": "early",
            "started_at": START,
            "ended_at": "2025-01-01T13:00:00+00:00",
            "test_cases": [cases[0]],
        },
    ]
    write_json(manifest, payload)
    result = module.validate_campaign(manifest)
    assert any("phase milestones are reordered" in error for error in result["errors"])

    module, manifest, _ = build_complete_campaign(tmp_path / "workflow")
    payload = read_manifest(manifest)
    workflow_record = payload["multi_page_workflow"]["report"]
    workflow_path = manifest.parent / workflow_record["path"]
    workflow = read_manifest(workflow_path)
    workflow["operations"][0], workflow["operations"][1] = (
        workflow["operations"][1],
        workflow["operations"][0],
    )
    previous: str | None = None
    for operation in workflow["operations"]:
        operation["previous_artifact_sha256"] = previous
        previous = operation["artifact"]["sha256"]
    workflow["artifact_chain_head_sha256"] = previous
    write_json(workflow_path, workflow)
    workflow_record["sha256"] = sha256(workflow_path.read_bytes()).hexdigest()
    write_json(manifest, payload)
    result = module.validate_campaign(manifest)
    assert any("required milestone order" in error for error in result["errors"])


def test_campaign_rejects_stale_browser_operation_and_api_hash(tmp_path: Path) -> None:
    module, manifest, _ = build_complete_campaign(tmp_path)
    payload = read_manifest(manifest)
    record = payload["phases"][0]["test_cases"][0]["evidence"]["browser_ground_truth"]
    browser_path = manifest.parent / record["path"]
    browser = read_manifest(browser_path)
    browser["operation_id"] = "stale-operation"
    browser["api_report_sha256"] = "0" * 64
    write_json(browser_path, browser)
    record["sha256"] = sha256(browser_path.read_bytes()).hexdigest()
    write_json(manifest, payload)
    result = module.validate_campaign(manifest)
    assert result["status"] == "failed"
    assert any("different API operation" in error for error in result["errors"])


def test_campaign_requires_a_distinct_hashed_workspace_receipt(tmp_path: Path) -> None:
    module, manifest, _ = build_complete_campaign(tmp_path)
    payload = read_manifest(manifest)
    evidence = payload["phases"][0]["test_cases"][0]["evidence"]
    evidence.pop("workspace_manifest")
    write_json(manifest, payload)
    result = module.validate_campaign(manifest)
    assert result["status"] == "failed"
    assert any("workspace_manifest must be a path and SHA-256 object" in error for error in result["errors"])

    module, manifest, _ = build_complete_campaign(tmp_path / "reused")
    payload = read_manifest(manifest)
    evidence = payload["phases"][0]["test_cases"][0]["evidence"]
    evidence["workspace_manifest"] = dict(evidence["api_report"])
    write_json(manifest, payload)
    result = module.validate_campaign(manifest)
    assert any("evidence reports must use distinct files" in error for error in result["errors"])


def test_campaign_rejects_tenant_space_and_page_url_mismatches(tmp_path: Path) -> None:
    module, manifest, _ = build_complete_campaign(tmp_path)
    payload = read_manifest(manifest)
    record = payload["phases"][0]["test_cases"][0]["evidence"]["workspace_manifest"]
    workspace_path = manifest.parent / record["path"]
    workspace = read_manifest(workspace_path)
    workspace["base_url"] = "https://other.atlassian.net"
    write_json(workspace_path, workspace)
    record["sha256"] = sha256(workspace_path.read_bytes()).hexdigest()
    write_json(manifest, payload)
    result = module.validate_campaign(manifest)
    assert any("workspace_manifest belongs to a different tenant" in error for error in result["errors"])

    module, manifest, _ = build_complete_campaign(tmp_path / "page")
    payload = read_manifest(manifest)
    record = payload["phases"][0]["test_cases"][0]["evidence"]["browser_ground_truth"]
    browser_path = manifest.parent / record["path"]
    browser = read_manifest(browser_path)
    browser["page_url"] = f"{BASE_URL}/wiki/spaces/lab/pages/999/wrong"
    write_json(browser_path, browser)
    record["sha256"] = sha256(browser_path.read_bytes()).hexdigest()
    write_json(manifest, payload)
    result = module.validate_campaign(manifest)
    assert any("does not identify page 42" in error for error in result["errors"])

    module, manifest, _ = build_complete_campaign(tmp_path / "space")
    payload = read_manifest(manifest)
    workflow_record = payload["multi_page_workflow"]["report"]
    workflow_path = manifest.parent / workflow_record["path"]
    workflow = read_manifest(workflow_path)
    scan = next(operation for operation in workflow["operations"] if operation["name"] == "scan")
    scan_path = workflow_path.parent / scan["artifact"]["path"]
    scan_payload = read_manifest(scan_path)
    scan_payload["pages"][0]["space_id"] = "different-space"
    write_json(scan_path, scan_payload)
    scan["artifact"]["sha256"] = sha256(scan_path.read_bytes()).hexdigest()
    previous: str | None = None
    for operation in workflow["operations"]:
        operation["previous_artifact_sha256"] = previous
        previous = operation["artifact"]["sha256"]
    workflow["artifact_chain_head_sha256"] = previous
    write_json(workflow_path, workflow)
    workflow_record["sha256"] = sha256(workflow_path.read_bytes()).hexdigest()
    write_json(manifest, payload)
    result = module.validate_campaign(manifest)
    assert any("page from a different space" in error for error in result["errors"])


def test_campaign_rejects_stale_cross_hashes_even_when_outer_receipts_are_rehashed(
    tmp_path: Path,
) -> None:
    module, manifest, _ = build_complete_campaign(tmp_path)
    payload = read_manifest(manifest)
    workflow_record = payload["multi_page_workflow"]["report"]
    workflow_path = manifest.parent / workflow_record["path"]
    workflow = read_manifest(workflow_path)
    upload = next(operation for operation in workflow["operations"] if operation["name"] == "batch-upload")
    upload_path = workflow_path.parent / upload["artifact"]["path"]
    upload_payload = read_manifest(upload_path)
    upload_payload["batch_manifest_sha256"] = "0" * 64
    write_json(upload_path, upload_payload)
    upload["artifact"]["sha256"] = sha256(upload_path.read_bytes()).hexdigest()
    previous: str | None = None
    for operation in workflow["operations"]:
        operation["previous_artifact_sha256"] = previous
        previous = operation["artifact"]["sha256"]
    workflow["artifact_chain_head_sha256"] = previous
    write_json(workflow_path, workflow)
    workflow_record["sha256"] = sha256(workflow_path.read_bytes()).hexdigest()
    write_json(manifest, payload)

    result = module.validate_campaign(manifest)
    assert result["status"] == "failed"
    assert any("not bound to the exact batch manifest" in error for error in result["errors"])


def test_campaign_rejects_future_timestamp_inside_rehashed_workflow_receipt(
    tmp_path: Path,
) -> None:
    module, manifest, _ = build_complete_campaign(tmp_path)
    payload = read_manifest(manifest)
    workflow_record = payload["multi_page_workflow"]["report"]
    workflow_path = manifest.parent / workflow_record["path"]
    workflow = read_manifest(workflow_path)
    upload = next(operation for operation in workflow["operations"] if operation["name"] == "batch-upload")
    upload_path = workflow_path.parent / upload["artifact"]["path"]
    upload_payload = read_manifest(upload_path)
    upload_payload["created_at"] = "2099-01-01T00:00:00+00:00"
    write_json(upload_path, upload_payload)
    upload["artifact"]["sha256"] = sha256(upload_path.read_bytes()).hexdigest()
    previous: str | None = None
    for operation in workflow["operations"]:
        operation["previous_artifact_sha256"] = previous
        previous = operation["artifact"]["sha256"]
    workflow["artifact_chain_head_sha256"] = previous
    write_json(workflow_path, workflow)
    workflow_record["sha256"] = sha256(workflow_path.read_bytes()).hexdigest()
    write_json(manifest, payload)
    result = module.validate_campaign(manifest)
    assert any("workflow.batch-upload.created_at is outside" in error for error in result["errors"])


def test_campaign_rejects_missing_required_category_and_operation(tmp_path: Path) -> None:
    module, manifest, _ = build_complete_campaign(tmp_path)
    payload = read_manifest(manifest)
    removed_category = module.REQUIRED_COVERAGE_CATEGORIES[-1]
    payload["required_coverage_categories"].remove(removed_category)
    for case in payload["phases"][0]["test_cases"]:
        if removed_category in case["coverage_categories"]:
            case["coverage_categories"].remove(removed_category)
    workflow_record = payload["multi_page_workflow"]["report"]
    workflow_path = manifest.parent / workflow_record["path"]
    workflow = read_manifest(workflow_path)
    workflow["operations"] = [
        operation for operation in workflow["operations"] if operation["name"] != "batch-verify"
    ]
    previous: str | None = None
    for operation in workflow["operations"]:
        operation["previous_artifact_sha256"] = previous
        previous = operation["artifact"]["sha256"]
    workflow["artifact_chain_head_sha256"] = previous
    write_json(workflow_path, workflow)
    workflow_record["sha256"] = sha256(workflow_path.read_bytes()).hexdigest()
    write_json(manifest, payload)
    result = module.validate_campaign(manifest)
    assert any("required coverage categories were removed" in error for error in result["errors"])
    assert any("operations have no passing evidence" in error for error in result["errors"])


def test_campaign_rejects_out_of_order_or_out_of_interval_evidence_times(tmp_path: Path) -> None:
    module, manifest, _ = build_complete_campaign(tmp_path)
    payload = read_manifest(manifest)
    case = payload["phases"][0]["test_cases"][0]
    browser_record = case["evidence"]["browser_ground_truth"]
    browser_path = manifest.parent / browser_record["path"]
    browser = read_manifest(browser_path)
    browser["verified_at"] = "2025-01-01T11:00:00+00:00"
    write_json(browser_path, browser)
    browser_record["sha256"] = sha256(browser_path.read_bytes()).hexdigest()
    write_json(manifest, payload)
    result = module.validate_campaign(manifest)
    assert any("must follow API verification" in error for error in result["errors"])

    module, manifest, _ = build_complete_campaign(tmp_path / "outside")
    payload = read_manifest(manifest)
    case = payload["phases"][0]["test_cases"][0]
    api_record = case["evidence"]["api_report"]
    api_path = manifest.parent / api_record["path"]
    api = read_manifest(api_path)
    api["verified_at"] = "2024-12-31T23:00:00+00:00"
    write_json(api_path, api)
    api_record["sha256"] = sha256(api_path.read_bytes()).hexdigest()
    browser_record = case["evidence"]["browser_ground_truth"]
    browser_path = manifest.parent / browser_record["path"]
    browser = read_manifest(browser_path)
    browser["api_report_sha256"] = sha256(api_path.read_bytes()).hexdigest()
    write_json(browser_path, browser)
    browser_record["sha256"] = sha256(browser_path.read_bytes()).hexdigest()
    write_json(manifest, payload)
    result = module.validate_campaign(manifest)
    assert any("API verification is outside" in error for error in result["errors"])


def test_campaign_rejects_label_state_or_suppressed_noop_changes(tmp_path: Path) -> None:
    module, manifest, _ = build_complete_campaign(tmp_path)
    payload = read_manifest(manifest)
    record = payload["phases"][0]["test_cases"][0]["evidence"]["noop_dry_run"]
    noop_path = manifest.parent / record["path"]
    noop = read_manifest(noop_path)
    noop["plan"]["no_op"] = False
    noop["plan"]["labels"]["added"] = ["changed"]
    noop["plan"]["content_state_changed"] = True
    noop["plan"]["suppressed_attachments"] = [{"filename": "hidden.png"}]
    write_json(noop_path, noop)
    record["sha256"] = sha256(noop_path.read_bytes()).hexdigest()
    write_json(manifest, payload)
    result = module.validate_campaign(manifest)
    assert result["status"] == "failed"
    assert any("content_state_changed must be false" in error for error in result["errors"])


def test_campaign_rejects_tampered_hashed_report(tmp_path: Path) -> None:
    module, manifest, _ = build_complete_campaign(tmp_path)
    payload = read_manifest(manifest)
    record = payload["phases"][0]["test_cases"][0]["evidence"]["api_report"]
    (manifest.parent / record["path"]).write_bytes(b"tampered")
    result = module.validate_campaign(manifest)
    assert result["status"] == "failed"
    assert any("api_report digest mismatch" in error for error in result["errors"])


def test_campaign_rejects_nonimage_or_unchanged_final_screenshot(tmp_path: Path) -> None:
    module, manifest, final = build_complete_campaign(tmp_path)
    payload = read_manifest(manifest)
    case = payload["phases"][0]["test_cases"][0]
    browser_record = case["evidence"]["browser_ground_truth"]
    browser_path = manifest.parent / browser_record["path"]
    browser = read_manifest(browser_path)
    final.write_bytes(b"not an image")
    browser["final_screenshots"][0]["sha256"] = sha256(final.read_bytes()).hexdigest()
    write_json(browser_path, browser)
    browser_record["sha256"] = sha256(browser_path.read_bytes()).hexdigest()
    write_json(manifest, payload)
    result = module.validate_campaign(manifest)
    assert any("not a decodable PNG or JPEG" in error for error in result["errors"])

    module, manifest, final = build_complete_campaign(tmp_path / "same")
    payload = read_manifest(manifest)
    case = payload["phases"][0]["test_cases"][0]
    browser_record = case["evidence"]["browser_ground_truth"]
    browser_path = manifest.parent / browser_record["path"]
    browser = read_manifest(browser_path)
    baseline = browser_path.parent / browser["baseline"]["path"]
    final.write_bytes(baseline.read_bytes())
    browser["final_screenshots"][0]["sha256"] = sha256(final.read_bytes()).hexdigest()
    write_json(browser_path, browser)
    browser_record["sha256"] = sha256(browser_path.read_bytes()).hexdigest()
    write_json(manifest, payload)
    result = module.validate_campaign(manifest)
    assert any("distinct from the baseline" in error for error in result["errors"])

    module, manifest, final = build_complete_campaign(tmp_path / "structurally-invalid")
    payload = read_manifest(manifest)
    browser_record = payload["phases"][0]["test_cases"][0]["evidence"]["browser_ground_truth"]
    browser_path = manifest.parent / browser_record["path"]
    browser = read_manifest(browser_path)
    final.write_bytes(make_crc_valid_but_undecodable_png())
    browser["final_screenshots"][0]["sha256"] = sha256(final.read_bytes()).hexdigest()
    write_json(browser_path, browser)
    browser_record["sha256"] = sha256(browser_path.read_bytes()).hexdigest()
    write_json(manifest, payload)
    result = module.validate_campaign(manifest)
    assert any("not a decodable PNG or JPEG" in error for error in result["errors"])


def test_campaign_rejects_escaping_hashed_evidence_path(tmp_path: Path) -> None:
    module, manifest, _ = build_complete_campaign(tmp_path)
    payload = read_manifest(manifest)
    outside = tmp_path / "outside.json"
    write_json(outside, {"status": "verified"})
    payload["phases"][0]["test_cases"][0]["evidence"]["api_report"] = {
        "path": "../outside.json",
        "sha256": sha256(outside.read_bytes()).hexdigest(),
    }
    write_json(manifest, payload)
    result = module.validate_campaign(manifest)
    assert any("escapes the campaign directory" in error for error in result["errors"])


def test_campaign_rejects_symlinked_evidence_escape(tmp_path: Path) -> None:
    module, manifest, _ = build_complete_campaign(tmp_path)
    payload = read_manifest(manifest)
    outside = tmp_path / "outside-api.json"
    write_json(outside, {"status": "verified"})
    link = manifest.parent / "evidence" / "outside-link.json"
    try:
        link.symlink_to(outside)
    except OSError as error:
        pytest.skip(f"symlink creation is unavailable: {error}")
    payload["phases"][0]["test_cases"][0]["evidence"]["api_report"] = {
        "path": "evidence/outside-link.json",
        "sha256": sha256(outside.read_bytes()).hexdigest(),
    }
    write_json(manifest, payload)
    result = module.validate_campaign(manifest)
    assert any("escapes the campaign directory" in error for error in result["errors"])


def test_campaign_rejects_semantically_false_workflow_artifact(tmp_path: Path) -> None:
    module, manifest, _ = build_complete_campaign(tmp_path)
    payload = read_manifest(manifest)
    workflow_record = payload["multi_page_workflow"]["report"]
    workflow_path = manifest.parent / workflow_record["path"]
    workflow = read_manifest(workflow_path)
    operation = next(item for item in workflow["operations"] if item["name"] == "batch-verify")
    artifact = workflow_path.parent / operation["artifact"]["path"]
    write_json(artifact, {"status": "verified", "pages": [{"page_id": "unrelated", "status": "failed"}]})
    operation["artifact"]["sha256"] = sha256(artifact.read_bytes()).hexdigest()
    write_json(workflow_path, workflow)
    workflow_record["sha256"] = sha256(workflow_path.read_bytes()).hexdigest()
    write_json(manifest, payload)
    result = module.validate_campaign(manifest)
    assert result["status"] == "failed"
    assert any("page IDs do not exactly match" in error for error in result["errors"])


def test_campaign_rejects_reused_inventory_as_explore_receipt(tmp_path: Path) -> None:
    module, manifest, _ = build_complete_campaign(tmp_path)
    payload = read_manifest(manifest)
    workflow_record = payload["multi_page_workflow"]["report"]
    workflow_path = manifest.parent / workflow_record["path"]
    workflow = read_manifest(workflow_path)
    inventory = next(item for item in workflow["operations"] if item["name"] == "inventory")
    explore = next(item for item in workflow["operations"] if item["name"] == "explore")
    inventory_path = workflow_path.parent / inventory["artifact"]["path"]
    explore_path = workflow_path.parent / explore["artifact"]["path"]
    explore_path.write_bytes(inventory_path.read_bytes())
    explore["artifact"]["sha256"] = sha256(explore_path.read_bytes()).hexdigest()
    write_json(workflow_path, workflow)
    workflow_record["sha256"] = sha256(workflow_path.read_bytes()).hexdigest()
    write_json(manifest, payload)
    result = module.validate_campaign(manifest)
    assert any("distinct persisted filtered artifact" in error for error in result["errors"])


def test_campaign_rejects_duplicate_case_page_or_case_workflow_mismatch(tmp_path: Path) -> None:
    module, manifest, _ = build_complete_campaign(tmp_path)
    payload = read_manifest(manifest)
    cases = payload["phases"][0]["test_cases"]
    cases[1]["page_id"] = "42"
    cases[1]["evidence"] = cases[0]["evidence"]
    write_json(manifest, payload)
    result = module.validate_campaign(manifest)
    assert any("duplicate test case page_id" in error for error in result["errors"])
    assert any("must exactly match multi-page workflow" in error for error in result["errors"])


def test_live_materializer_stages_self_contained_packages_with_stable_source_snapshots(
    tmp_path: Path,
) -> None:
    materializer, source = build_live_materializer_source(tmp_path)
    validator = load_validator()
    manifests = [tmp_path / name / "campaign.json" for name in ("materialized-a", "materialized-b")]
    for manifest in manifests:
        materializer.materialize_live_campaign(
            source,
            manifest,
            started_at=LIVE_START,
            ended_at=LIVE_END,
            campaign_id="deterministic-live-campaign",
        )
        assert validator.validate_campaign(manifest)["status"] == "verified"
    hashes = [
        {
            path.relative_to(manifest.parent).as_posix(): sha256(path.read_bytes()).hexdigest()
            for path in manifest.parent.rglob("*")
            if path.is_file()
        }
        for manifest in manifests
    ]
    dynamic = {"campaign.json", "evidence/campaign-timeline.json"}
    assert {key: value for key, value in hashes[0].items() if key not in dynamic} == {
        key: value for key, value in hashes[1].items() if key not in dynamic
    }
    assert not list(tmp_path.glob(".*.stage-*"))


def test_live_materializer_reads_once_then_rechecks_source_before_publish(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    materializer, source = build_live_materializer_source(tmp_path)
    batch_manifest = (source / "campaign" / "batch-manifest.json").resolve()
    original = Path.read_bytes
    reads: dict[Path, int] = {}

    def counting_read(path: Path) -> bytes:
        resolved = path.resolve()
        reads[resolved] = reads.get(resolved, 0) + 1
        return original(path)

    monkeypatch.setattr(Path, "read_bytes", counting_read)
    materializer.materialize_live_campaign(
        source,
        tmp_path / "materialized-once" / "campaign.json",
        started_at=LIVE_START,
        ended_at=LIVE_END,
    )
    assert reads[batch_manifest] == 2


def test_live_materializer_rejects_mutable_source_drift_before_publish(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    materializer, source = build_live_materializer_source(tmp_path)
    target = (source / "campaign" / "batch-manifest.json").resolve()
    original_read = Path.read_bytes
    original_mtime = target.stat().st_mtime
    reads = 0

    def drifting_read(path: Path) -> bytes:
        nonlocal reads
        payload = original_read(path)
        if path.resolve() == target:
            reads += 1
            if reads == 1:
                target.write_bytes(payload + b" ")
                os.utime(target, (original_mtime, original_mtime))
        return payload

    monkeypatch.setattr(Path, "read_bytes", drifting_read)
    output = tmp_path / "drifted-output" / "campaign.json"
    with pytest.raises(ValueError, match="source evidence changed during materialization"):
        materializer.materialize_live_campaign(
            source,
            output,
            started_at=LIVE_START,
            ended_at=LIVE_END,
        )
    assert not output.parent.exists()


def test_live_materializer_refuses_overwrite_and_failure_leaves_no_package(tmp_path: Path) -> None:
    materializer, source = build_live_materializer_source(tmp_path)
    manifest = tmp_path / "materialized" / "campaign.json"
    materializer.materialize_live_campaign(
        source, manifest, started_at=LIVE_START, ended_at=LIVE_END
    )
    before = {path.relative_to(manifest.parent): path.read_bytes() for path in manifest.parent.rglob("*") if path.is_file()}
    with pytest.raises(ValueError, match="already exists"):
        materializer.materialize_live_campaign(
            source, manifest, started_at=LIVE_START, ended_at=LIVE_END
        )
    after = {path.relative_to(manifest.parent): path.read_bytes() for path in manifest.parent.rglob("*") if path.is_file()}
    assert after == before

    failed_output = tmp_path / "failed-materialization" / "campaign.json"
    upload = source / "campaign" / "batch-upload-report.json"
    upload_payload = read_manifest(upload)
    upload_payload["status"] = "partial"
    write_json(upload, upload_payload)
    with pytest.raises(ValueError, match="workflow.batch-upload source status is not verified"):
        materializer.materialize_live_campaign(
            source, failed_output, started_at=LIVE_START, ended_at=LIVE_END
        )
    assert not failed_output.parent.exists()


def test_live_materializer_rejects_both_source_output_ancestor_directions(tmp_path: Path) -> None:
    materializer, source = build_live_materializer_source(tmp_path)
    with pytest.raises(ValueError, match="must not contain one another"):
        materializer.materialize_live_campaign(
            source,
            source / "nested" / "campaign.json",
            started_at=LIVE_START,
            ended_at=LIVE_END,
        )

    output_root = tmp_path / "ancestor-output"
    nested_source = output_root / "live-source"
    shutil.copytree(source, nested_source)
    with pytest.raises(ValueError, match="must not contain one another"):
        materializer.materialize_live_campaign(
            nested_source,
            output_root / "campaign.json",
            started_at=LIVE_START,
            ended_at=LIVE_END,
        )


def test_live_materializer_rejects_escaping_screenshot_and_duplicate_manifest_page(tmp_path: Path) -> None:
    materializer, source = build_live_materializer_source(tmp_path)
    verification = source / "campaign" / "workspaces" / "34340869" / "verification"
    browser_path = verification / "browser-ground-truth.json"
    browser = read_manifest(browser_path)
    outside = verification.parent / "outside.png"
    outside.write_bytes(make_png((1, 2, 3)))
    browser["final_screenshots"][0] = {
        "path": "../outside.png",
        "sha256": sha256(outside.read_bytes()).hexdigest(),
    }
    write_json(browser_path, browser)
    with pytest.raises(ValueError, match="escapes its source directory"):
        materializer.materialize_live_campaign(
            source,
            tmp_path / "escape-output" / "campaign.json",
            started_at=LIVE_START,
            ended_at=LIVE_END,
        )

    materializer, source = build_live_materializer_source(tmp_path / "duplicate")
    batch = source / "campaign" / "batch-manifest.json"
    batch_payload = read_manifest(batch)
    batch_payload["pages"].append(dict(batch_payload["pages"][0]))
    write_json(batch, batch_payload)
    with pytest.raises(ValueError, match="unique non-empty page IDs"):
        materializer.materialize_live_campaign(
            source,
            tmp_path / "duplicate-output" / "campaign.json",
            started_at=LIVE_START,
            ended_at=LIVE_END,
        )


def test_live_materializer_cli_rejects_short_or_backdated_duration(tmp_path: Path) -> None:
    _, source = build_live_materializer_source(tmp_path)
    manifest = tmp_path / "materialized" / "campaign.json"
    completed = subprocess.run(
        [
            sys.executable,
            str(MATERIALIZER),
            "--source-root",
            str(source),
            "--output",
            str(manifest),
            "--started-at",
            (LIVE_END_DATETIME - timedelta(hours=7)).isoformat(),
            "--ended-at",
            LIVE_END,
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=30,
        check=False,
    )
    assert completed.returncode == 2
    assert "at least 8 real hours" in completed.stderr
    assert not manifest.parent.exists()

    stale_end = LIVE_END_DATETIME - timedelta(hours=2)
    stale_start = stale_end - timedelta(hours=8)
    stale_output = tmp_path / "backdated" / "campaign.json"
    completed = subprocess.run(
        [
            sys.executable,
            str(MATERIALIZER),
            "--source-root",
            str(source),
            "--output",
            str(stale_output),
            "--started-at",
            stale_start.isoformat(),
            "--ended-at",
            stale_end.isoformat(),
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=30,
        check=False,
    )
    assert completed.returncode == 2
    assert "ended_at is backdated" in completed.stderr
    assert not stale_output.parent.exists()

    materializer = load_materializer()
    forged_output = tmp_path / "forged-start" / "campaign.json"
    with pytest.raises(ValueError, match="within 5 minutes of campaign start"):
        materializer.materialize_live_campaign(
            source,
            forged_output,
            started_at=(LIVE_START_DATETIME - timedelta(hours=1)).isoformat(),
            ended_at=LIVE_END,
        )
    assert not forged_output.parent.exists()


def test_validator_cli_returns_machine_readable_failure(tmp_path: Path) -> None:
    _, manifest, _ = build_complete_campaign(tmp_path)
    payload = read_manifest(manifest)
    payload["ended_at"] = "2025-01-01T16:00:00+00:00"
    payload["phases"][0]["ended_at"] = payload["ended_at"]
    write_json(manifest, payload)
    completed = subprocess.run(
        [sys.executable, str(VALIDATOR), str(manifest)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=30,
        check=False,
    )
    assert completed.returncode == 2
    assert json.loads(completed.stdout)["status"] == "failed"
