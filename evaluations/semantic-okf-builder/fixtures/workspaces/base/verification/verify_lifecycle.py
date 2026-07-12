#!/usr/bin/env python3
"""Verify deterministic outcomes for Semantic OKF lifecycle benchmark cases."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Callable

from rdflib import Graph
from rdflib.namespace import RDF


def load_json(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    failures: list[Exception] = []
    for encoding in ("utf-8-sig", "utf-16"):
        try:
            value = json.loads(raw.decode(encoding).strip())
            if not isinstance(value, dict):
                raise TypeError(f"expected JSON object in {path}")
            return value
        except (UnicodeError, json.JSONDecodeError, TypeError) as exc:
            failures.append(exc)
    raise ValueError(f"cannot parse JSON object at {path}: {failures[-1]}")


def records(bundle: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in (bundle / "semantic" / "records.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def check_bundle(bundle: Path, expected_sources: set[str], expected_records: int) -> tuple[list[str], list[dict[str, Any]]]:
    errors: list[str] = []
    if not bundle.is_dir():
        return [f"missing bundle: {bundle}"], []
    try:
        report = load_json(bundle / "semantic" / "build-report.json")
        source_manifest = load_json(bundle / "semantic" / "source-manifest.json")
        ledger = records(bundle)
        if report.get("valid") is not True or report.get("status") != "pass":
            errors.append("build report is not passing")
        actual_sources = {str(item.get("id")) for item in source_manifest.get("sources", [])}
        if actual_sources != expected_sources:
            errors.append(f"source IDs differ: {sorted(actual_sources)}")
        if len(ledger) != expected_records:
            errors.append(f"record count differs: {len(ledger)}")
        for record in ledger:
            concept_path = record.get("concept_path")
            if not isinstance(concept_path, str) or not (bundle / concept_path).is_file():
                errors.append(f"missing concept path: {concept_path!r}")
        graph = Graph().parse(bundle / "semantic" / "data.ttl", format="turtle")
        if len(set(graph.subjects(RDF.type, None))) != expected_records:
            errors.append("typed data subject count differs")
        return errors, ledger
    except Exception as exc:  # pragma: no cover - reported as benchmark evidence
        errors.append(f"bundle inspection failed: {exc}")
        return errors, []


def report_status(path: Path, expected: str, errors: list[str]) -> dict[str, Any]:
    try:
        payload = load_json(path)
        if payload.get("status") != expected:
            errors.append(f"unexpected status in {path.name}: {payload.get('status')!r}")
        return payload
    except Exception as exc:
        errors.append(f"cannot inspect {path.name}: {exc}")
        return {}


def verify_create(workspace: Path) -> list[str]:
    root = workspace / "deliverables" / "create"
    errors, ledger = check_bundle(root / "bundle", {"people", "policies", "projects", "vocabulary"}, 5)
    kinds = {record.get("source_kind") for record in ledger}
    if ledger and kinds != {"csv", "json", "markdown", "rdf"}:
        errors.append(f"heterogeneous source kinds differ: {sorted(str(item) for item in kinds)}")
    return errors


def verify_augment(workspace: Path) -> list[str]:
    root = workspace / "deliverables" / "augment"
    errors, ledger = check_bundle(root / "bundle", {"people", "projects"}, 3)
    report_status(root / "refresh-report.json", "updated", errors)
    try:
        plan = load_json(root / "bundle" / "semantic" / "semantic-plan.json")
        if plan["bundle"]["version_iri"] != "https://example.org/ontology/augment/1.1.0":
            errors.append("augmented bundle did not advance the ontology version")
    except Exception as exc:
        errors.append(f"cannot inspect augmented semantic plan: {exc}")
    if ledger and {record.get("source_id") for record in ledger} != {"people", "projects"}:
        errors.append("augmented ledger does not contain both sources")
    return errors


def verify_refresh(workspace: Path) -> list[str]:
    root = workspace / "deliverables" / "refresh"
    errors, ledger = check_bundle(root / "bundle", {"people"}, 2)
    report_status(root / "refresh-report.json", "updated", errors)
    by_id = {record.get("record_id"): record for record in ledger}
    if by_id.get("person-1", {}).get("attributes", {}).get("role") != "Architect":
        errors.append("changed person role was not refreshed")
    if "person-2" not in by_id:
        errors.append("added source record was not refreshed")
    return errors


def verify_remove(workspace: Path) -> list[str]:
    root = workspace / "deliverables" / "remove"
    errors, _ = check_bundle(root / "bundle", {"people"}, 1)
    safety = report_status(root / "safety-report.json", "changes-pending", errors)
    blockers = {item.get("code") for item in safety.get("blockers", []) if isinstance(item, dict)}
    required = {"ontology-version-reuse", "plan-change-not-allowed", "record-removal-not-allowed"}
    if not required.issubset(blockers):
        errors.append(f"safety blockers differ: {sorted(str(item) for item in blockers)}")
    report_status(root / "refresh-report.json", "updated", errors)
    try:
        plan = load_json(root / "bundle" / "semantic" / "semantic-plan.json")
        if plan["bundle"]["version_iri"] != "https://example.org/ontology/remove/2.0.0":
            errors.append("removal did not publish the approved ontology version")
    except Exception as exc:
        errors.append(f"cannot inspect removal semantic plan: {exc}")
    return errors


def verify_topology(workspace: Path) -> list[str]:
    path = workspace / "deliverables" / "topology" / "decision.json"
    expected = {
        "crm-support": "separate-in-bundle",
        "regional-partitions": "logical-union",
        "tenant-isolation": "separate-bundles",
        "vendor-entity-fusion": "upstream-canonicalization",
    }
    try:
        actual = load_json(path)
        return [] if actual == expected else [f"topology decision differs: {actual!r}"]
    except Exception as exc:
        return [f"cannot inspect topology decision: {exc}"]


def verify_atomic(workspace: Path) -> list[str]:
    root = workspace / "deliverables" / "atomic"
    errors: list[str] = []
    if (root / "rejected").exists():
        errors.append("failed build published a rejected output")
    rejection = report_status(root / "rejection-report.json", "error", errors)
    if rejection and rejection.get("code") != "semantic-error":
        errors.append(f"unexpected rejection code: {rejection.get('code')!r}")
    bundle_errors, _ = check_bundle(root / "bundle", {"people"}, 1)
    errors.extend(bundle_errors)
    recovery = report_status(root / "recovery-report.json", "recovered", errors)
    if recovery and recovery.get("resolution") != "rollback":
        errors.append(f"unexpected recovery resolution: {recovery.get('resolution')!r}")
    leftovers = [
        path.name
        for path in root.iterdir()
        if path.name.startswith(".sokf-") or path.name.endswith(".refresh.json") or path.name.endswith(".refresh.lock")
    ] if root.is_dir() else []
    if leftovers:
        errors.append(f"transaction artifacts remain: {sorted(leftovers)}")
    return errors


def verify_tamper(workspace: Path) -> list[str]:
    root = workspace / "deliverables" / "tamper"
    errors, _ = check_bundle(root / "bundle", {"people"}, 1)
    validation = report_status(root / "validation-report.json", "error", errors)
    if validation and validation.get("valid") is not False:
        errors.append("tampered bundle validation did not fail")
    tampered_data = root / "tampered" / "semantic" / "data.ttl"
    try:
        if "tamper-extra" not in tampered_data.read_text(encoding="utf-8"):
            errors.append("tampered data marker is absent")
    except OSError as exc:
        errors.append(f"cannot inspect tampered data: {exc}")
    return errors


VERIFIERS: dict[str, Callable[[Path], list[str]]] = {
    "create": verify_create,
    "augment": verify_augment,
    "refresh": verify_refresh,
    "remove": verify_remove,
    "topology": verify_topology,
    "atomic": verify_atomic,
    "tamper": verify_tamper,
}


def safe_report_path(workspace: Path, raw: Path) -> Path:
    path = (workspace / raw).resolve() if not raw.is_absolute() else raw.resolve()
    if workspace not in path.parents:
        raise ValueError("report must remain inside the workspace")
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case", choices=tuple(VERIFIERS))
    parser.add_argument("--workspace", type=Path, default=Path.cwd())
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    workspace = args.workspace.resolve()
    errors = VERIFIERS[args.case](workspace)
    payload = {"case": args.case, "errors": errors, "pass": not errors}
    if args.report is not None:
        report = safe_report_path(workspace, args.report)
        report.parent.mkdir(parents=True, exist_ok=True)
        report.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
