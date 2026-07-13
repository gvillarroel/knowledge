"""Validate the Luna modification task against a preserved baseline workspace."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import sys
from types import ModuleType
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
SKILL_SCRIPT = REPO_ROOT / "skills" / "roundtrip-confluence-pages" / "scripts" / "confluence_roundtrip.py"
EXPECTED_TITLE = "Confluence Round-Trip Acceptance — Revised"
NEW_LINK = "https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-attachment/"


def load_roundtrip() -> ModuleType:
    """Load the standalone skill script from its repository path."""

    spec = importlib.util.spec_from_file_location("confluence_roundtrip_evaluation", SKILL_SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_json(path: Path) -> Any:
    """Load JSON for deterministic evaluation."""

    return json.loads(path.read_text(encoding="utf-8"))


def evaluate(baseline: Path, candidate: Path) -> dict[str, Any]:
    """Return named assertions for the complex page-edit task."""

    roundtrip = load_roundtrip()
    checks: list[dict[str, Any]] = []

    def check(name: str, passed: bool, detail: Any = None) -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    try:
        validation = roundtrip.validate_workspace(candidate)
        check("workspace-valid", True, validation)
    except Exception as exc:  # evaluation must report every deterministic failure
        check("workspace-valid", False, str(exc))

    baseline_storage = (baseline / roundtrip.STORAGE_NAME).read_text(encoding="utf-8")
    candidate_storage = (candidate / roundtrip.STORAGE_NAME).read_text(encoding="utf-8")
    before = roundtrip.storage_summary(baseline_storage)
    after = roundtrip.storage_summary(candidate_storage)
    meta = load_json(candidate / roundtrip.META_NAME)
    labels = load_json(candidate / roundtrip.LABELS_NAME)
    state = load_json(candidate / roundtrip.STATE_NAME)
    gt = load_json(candidate / roundtrip.GT_NAME)

    check("title-metadata", meta.get("title") == EXPECTED_TITLE, meta.get("title"))
    check("title-heading", f"<h1>{EXPECTED_TITLE}</h1>" in candidate_storage)
    check("release-readiness-section", "<h2>Release readiness</h2>" in candidate_storage)
    check("ready-status", after["macros"].get("status", 0) >= before["macros"].get("status", 0) + 1)
    check("green-status-parameter", "Green" in candidate_storage and "READY" in candidate_storage)
    check(
        "release-table",
        all(value in candidate_storage for value in ("Owner", "Area", "Decision"))
        and candidate_storage.count("<tr>") >= baseline_storage.count("<tr>") + 3,
    )
    check("new-smart-link", NEW_LINK in after["hrefs"] and 'data-card-appearance="block"' in candidate_storage)
    check("new-image-reference", "release-architecture.svg" in after["attachment_filenames"])
    check("new-image-file", (candidate / "attachments" / "release-architecture.svg").is_file())
    if (candidate / "attachments" / "release-architecture.svg").is_file():
        svg = (candidate / "attachments" / "release-architecture.svg").read_text(encoding="utf-8")
        check("new-image-accessibility", "<title" in svg and "<desc" in svg)
    check("label-added", "roundtrip-validated" in labels)
    check("labels-preserved", set(load_json(baseline / roundtrip.LABELS_NAME)).issubset(labels))
    check("content-state", state == {"name": "Ready", "color": "GREEN"}, state)
    check("ground-truth-release", "Release readiness" in gt.get("required_visible_text", []))
    check("ground-truth-ready", "READY" in gt.get("required_visible_text", []))
    check("visual-baseline-preserved", gt.get("visual_baseline") == load_json(baseline / roundtrip.GT_NAME).get("visual_baseline"))

    for macro, count in before["macros"].items():
        check(f"macro-preserved:{macro}", after["macros"].get(macro, 0) >= count)
    check("internal-page-link-preserved", set(before["page_references"]).issubset(after["page_references"]))
    check("existing-hrefs-preserved", set(before["hrefs"]).issubset(after["hrefs"]))
    check("existing-image-reference-preserved", "system-context.svg" in after["attachment_filenames"])
    check(
        "existing-image-bytes-preserved",
        (baseline / "attachments" / "system-context.svg").read_bytes()
        == (candidate / "attachments" / "system-context.svg").read_bytes(),
    )
    check("task-preserved", "<ac:task-id>1</ac:task-id>" in candidate_storage)
    check("details-id-preserved", "roundtrip-details" in candidate_storage)

    return {
        "status": "passed" if all(item["passed"] for item in checks) else "failed",
        "checks": checks,
        "summary": {
            "passed": sum(1 for item in checks if item["passed"]),
            "failed": sum(1 for item in checks if not item["passed"]),
            "total": len(checks),
        },
    }


def main(argv: list[str] | None = None) -> int:
    """Run the deterministic evaluation and emit JSON."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("baseline", type=Path)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    report = evaluate(args.baseline.resolve(), args.candidate.resolve())
    text = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0 if report["status"] == "passed" else 2


if __name__ == "__main__":
    raise SystemExit(main())
