#!/usr/bin/env python3
"""Validate the API and browser ground-truth records for a live Confluence run."""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def validate(workspace: Path) -> dict[str, Any]:
    verification = workspace.resolve() / "verification"
    api_path = verification / "report.json"
    browser_path = verification / "browser-ground-truth.json"
    api = load_json(api_path)
    browser = load_json(browser_path)
    errors: list[str] = []

    if api.get("status") != "verified":
        errors.append("API verification status is not verified")
    if browser.get("status") != "verified":
        errors.append("browser verification status is not verified")
    if str(api.get("page_id")) != str(browser.get("page_id")):
        errors.append("API and browser records refer to different page IDs")

    checks = browser.get("checks")
    if not isinstance(checks, list) or not checks:
        errors.append("browser verification has no checks")
    elif any(not isinstance(check, dict) or check.get("passed") is not True for check in checks):
        errors.append("one or more browser checks failed")

    screenshot_records: list[dict[str, Any]] = []
    baseline = browser.get("baseline")
    if isinstance(baseline, dict):
        screenshot_records.append(baseline)
    else:
        errors.append("browser verification has no baseline screenshot")
    finals = browser.get("final_screenshots")
    if isinstance(finals, list) and finals:
        screenshot_records.extend(record for record in finals if isinstance(record, dict))
        if len([record for record in finals if isinstance(record, dict)]) != len(finals):
            errors.append("final_screenshots contains a non-object record")
    else:
        errors.append("browser verification has no final screenshots")

    for record in screenshot_records:
        relative = record.get("path")
        expected = str(record.get("sha256") or "")
        if not isinstance(relative, str) or not relative:
            errors.append("a screenshot record has no path")
            continue
        screenshot = (verification / relative).resolve()
        if not screenshot.is_file():
            errors.append(f"screenshot is missing: {relative}")
            continue
        actual = sha256(screenshot.read_bytes()).hexdigest()
        if actual != expected:
            errors.append(f"screenshot digest mismatch: {relative}")

    return {
        "status": "verified" if not errors else "failed",
        "page_id": str(browser.get("page_id") or ""),
        "api_checks": len(api.get("checks") or []),
        "browser_checks": len(checks or []),
        "screenshots": len(screenshot_records),
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("workspace", type=Path)
    args = parser.parse_args()
    result = validate(args.workspace)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["status"] == "verified" else 2


if __name__ == "__main__":
    raise SystemExit(main())
