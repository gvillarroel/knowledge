"""Tests for declarative Confluence live-fixture capability validation."""

from __future__ import annotations

import base64
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
from types import ModuleType
from typing import Any
from uuid import UUID


REPO_ROOT = Path(__file__).resolve().parents[1]
EVALUATION_ROOT = REPO_ROOT / "evaluations" / "confluence-8h-live"
VALIDATOR = EVALUATION_ROOT / "validate_capabilities.py"
DEFAULT_EXPECTATIONS = EVALUATION_ROOT / "capability-expectations.json"
PI_LUNA_EVIDENCE = EVALUATION_ROOT / "pi-luna-evidence.json"
PI_OPENROUTER_EVIDENCE = EVALUATION_ROOT / "pi-openrouter-evidence.json"


def _load_validator() -> ModuleType:
    spec = importlib.util.spec_from_file_location("confluence_8h_live_validator", VALIDATOR)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _build_fixture(tmp_path: Path) -> tuple[ModuleType, Path, Path]:
    module = _load_validator()
    roundtrip = module._roundtrip_module()
    campaign = tmp_path / "campaign"
    workspace = campaign / "workspaces" / "example"
    verification = workspace / "verification"
    attachment = workspace / "attachments" / "diagram.png"
    verification.mkdir(parents=True)
    attachment.parent.mkdir(parents=True)
    attachment.write_bytes(b"png fixture")
    storage_path = workspace / "page.storage.xml"
    storage_path.write_text(
        """<h2>Acceptance marker</h2>
<p><a href="https://example.test/reference">Reference</a></p>
<ac:structured-macro ac:name="info"><ac:rich-text-body><p>Panel marker</p></ac:rich-text-body></ac:structured-macro>
<p><ac:link><ri:page ri:content-title="Target Page" /><ac:link-body>Target</ac:link-body></ac:link></p>
<ac:image ac:alt="Fixture diagram accessible name"><ri:attachment ri:filename="diagram.png" /><ac:parameter ac:name="alt">Fixture diagram alternative text</ac:parameter></ac:image>
        """,
        encoding="utf-8",
    )
    storage = storage_path.read_text(encoding="utf-8")
    baseline_adf = {
        "type": "doc",
        "version": 1,
        "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Baseline"}]}],
    }
    _write_json(workspace / "page.adf.json", baseline_adf)
    (workspace / "page.view.html").write_text("<p>Baseline rendered view</p>", encoding="utf-8")
    _write_json(workspace / "page.restrictions.json", {"results": []})
    _write_json(
        workspace / "page.meta.json",
        {
            "page_id": "42",
            "title": "Fixture",
            "space_id": "100",
            "parent_id": "10",
            "status": "current",
            "subtype": None,
        },
    )
    _write_json(workspace / "page.labels.json", [])
    _write_json(workspace / "page.content-state.json", None)
    _write_json(
        workspace / "ground-truth.json",
        {
            "schema_version": "1.0",
            "captured_at": "2026-07-13T04:00:00Z",
            "page": {"page_id": "42", "title": "Fixture"},
            "storage": roundtrip.storage_summary(storage),
            "adf_observation": roundtrip.adf_summary(baseline_adf),
            "labels": [],
            "content_state": None,
            "attachments": [
                {
                    "filename": "diagram.png",
                    "sha256": sha256(attachment.read_bytes()).hexdigest(),
                    "file_size": attachment.stat().st_size,
                }
            ],
            "required_visible_text": ["Acceptance marker", "Panel marker"],
            "required_browser_check_ids": ["rendered-capability"],
            "visual_baseline": None,
        },
    )
    storage_summary = roundtrip.storage_summary(storage)
    _write_json(
        workspace / "manifest.json",
        {
            "schema_version": "1.0",
            "base_url": "https://tenant.atlassian.net",
            "downloaded_at": "2026-07-13T04:00:00Z",
            "last_verified_at": "2026-07-13T04:01:00Z",
            "page": {
                "page_id": "42",
                "title": "Fixture",
                "space_id": "100",
                "parent_id": "10",
                "status": "current",
                "subtype": None,
                "version": 2,
                "web_url": "https://tenant.atlassian.net/wiki/pages/42/Fixture",
            },
            "body": {
                "editable_representation": "storage",
                "storage": {
                    **storage_summary,
                    "path": "page.storage.xml",
                    "sha256": sha256(storage_path.read_bytes()).hexdigest(),
                },
                "atlas_doc_format": {
                    "path": "page.adf.json",
                    "sha256": roundtrip.sha256_json(baseline_adf),
                },
                "view": {
                    "path": "page.view.html",
                    "sha256": roundtrip.sha256_text("<p>Baseline rendered view</p>"),
                },
            },
            "attachments": [
                {
                    "id": "att42",
                    "filename": "diagram.png",
                    "path": "attachments/diagram.png",
                    "media_type": "image/png",
                    "file_size": attachment.stat().st_size,
                    "sha256": sha256(attachment.read_bytes()).hexdigest(),
                    "version": 1,
                }
            ],
            "editable_baselines": {"global_labels": [], "content_state": None},
            "preserved_read_only": [
                "page.adf.json",
                "page.view.html",
                "page.restrictions.json",
            ],
            "restrictions": {
                "path": "page.restrictions.json",
                "sha256": roundtrip.sha256_json({"results": []}),
            },
        },
    )
    desired_digest = roundtrip.desired_state_sha256(workspace)
    manifest = json.loads((workspace / "manifest.json").read_text(encoding="utf-8"))
    manifest["last_verified_operation_id"] = "operation-42"
    manifest["last_verified_desired_state_sha256"] = desired_digest
    _write_json(workspace / "manifest.json", manifest)

    report_path = verification / "report.json"
    rendered_view = verification / "remote.view.html"
    rendered_view.write_text(
        '<img alt="Fixture diagram accessible name" src="diagram.png">',
        encoding="utf-8",
    )
    remote_adf = {
        "type": "doc",
        "version": 1,
        "content": [
            {
                "type": "paragraph",
                "content": [
                    {
                        "type": "text",
                        "text": "Reference",
                        "marks": [
                            {
                                "type": "link",
                                "attrs": {"href": "https://example.test/reference"},
                            }
                        ],
                    }
                ],
            },
            {
                "type": "mediaSingle",
                "content": [
                    {
                        "type": "media",
                        "attrs": {
                            "id": "media-1",
                            "type": "file",
                            "collection": "contentId-42",
                            "alt": "Fixture diagram accessible name",
                        },
                    }
                ],
            },
        ],
    }
    (verification / "remote.storage.xml").write_text(storage, encoding="utf-8")
    _write_json(verification / "remote.adf.json", remote_adf)
    _write_json(verification / "remote.restrictions.json", {"results": []})
    evidence = {}
    for name, filename in {
        "storage": "remote.storage.xml",
        "atlas_doc_format": "remote.adf.json",
        "view": "remote.view.html",
        "restrictions": "remote.restrictions.json",
    }.items():
        evidence[name] = {
            "path": filename,
            "sha256": sha256((verification / filename).read_bytes()).hexdigest(),
        }
    storage_equivalence = roundtrip.sha256_text(roundtrip.remote_equivalence_storage(storage))
    attachment_digest = sha256(attachment.read_bytes()).hexdigest()
    _write_json(
        report_path,
        {
            "schema_version": "1.0",
            "status": "verified",
            "page_id": "42",
            "remote_version": 2,
            "operation_id": "operation-42",
            "verified_at": "2026-07-13T04:01:00Z",
            "desired_state_sha256": desired_digest,
            "evidence": evidence,
            "checks": [
                {
                    "name": "storage-equivalent",
                    "passed": True,
                    "detail": {"expected": storage_equivalence, "actual": storage_equivalence},
                },
                {"name": "title", "passed": True, "detail": "Fixture"},
                {
                    "name": "space-id",
                    "passed": True,
                    "detail": {"expected": "100", "actual": "100"},
                },
                {
                    "name": "parent-id",
                    "passed": True,
                    "detail": {"expected": "10", "actual": "10"},
                },
                {
                    "name": "labels",
                    "passed": True,
                    "detail": {"expected": [], "actual": []},
                },
                {
                    "name": "content-state",
                    "passed": True,
                    "detail": {"expected": None, "actual": None},
                },
                {
                    "name": "restrictions-unchanged",
                    "passed": True,
                    "detail": {
                        "expected": roundtrip.sha256_json({"results": []}),
                        "actual": roundtrip.sha256_json({"results": []}),
                    },
                },
                {"name": "visible-text:Acceptance marker", "passed": True},
                {"name": "visible-text:Panel marker", "passed": True},
                {
                    "name": "attachment:diagram.png",
                    "passed": True,
                    "detail": {"expected": attachment_digest, "actual": attachment_digest},
                },
            ],
            "adf_summary": roundtrip.adf_summary(remote_adf),
        },
    )
    _write_json(
        verification / "noop-dry-run.json",
        {
            "status": "dry-run",
            "plan": {
                "page_update": False,
                "body_changed": False,
                "metadata_changed": False,
                "attachments": [],
                "labels": {"added": [], "removed": []},
                "content_state_changed": False,
                "no_op": True,
                "page_id": "42",
                "current_version": 2,
                "expected_version": 2,
                "desired_state_sha256": desired_digest,
            },
        },
    )
    baseline = verification / "browser-baseline.png"
    screenshot = verification / "browser-final.png"
    baseline.write_bytes(
        base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAIAAAACCAIAAAD91JpzAAAAEElEQVR4nGP8zwACTGCSAQANHQEDgslx/wAAAABJRU5ErkJggg=="
        )
    )
    screenshot.write_bytes(
        base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAIAAAACCAIAAAD91JpzAAAAEklEQVR4nGNkYPjPwMDAxAAGAAsfAQMU4wsAAAAAAElFTkSuQmCC"
        )
    )
    _write_json(
        verification / "browser-ground-truth.json",
        {
            "schema_version": "1.0",
            "status": "verified",
            "page_id": "42",
            "operation_id": "operation-42",
            "api_report_sha256": sha256(report_path.read_bytes()).hexdigest(),
            "desired_state_sha256": desired_digest,
            "remote_version": 2,
            "verified_at": "2026-07-13T04:02:00Z",
            "page_url": "https://tenant.atlassian.net/wiki/spaces/T/pages/42/Fixture",
            "checks": [
                {"id": "rendered-capability", "name": "rendered-capability", "passed": True}
            ],
            "baseline": {
                "path": baseline.name,
                "sha256": sha256(baseline.read_bytes()).hexdigest(),
            },
            "final_screenshots": [
                {
                    "path": screenshot.name,
                    "sha256": sha256(screenshot.read_bytes()).hexdigest(),
                }
            ],
        },
    )
    _write_json(
        verification / "mutation-journal.json",
        {
            "schema_version": "1.0",
            "status": "api-verified",
            "operation_id": "operation-42",
            "page_id": "42",
            "desired_state_sha256": desired_digest,
            "started_at": "2026-07-13T04:00:30Z",
            "api_verified_at": "2026-07-13T04:01:00Z",
            "steps": [
                {
                    "id": "api-verification",
                    "kind": "verification",
                    "status": "verified",
                    "detail": {"remote_version": 2},
                }
            ],
        },
    )
    _write_json(
        verification / "upload.json",
        {
            "status": "uploaded",
            "operation_id": "mutation-operation-42",
            "page_id": "42",
            "page_updated": True,
            "attachments": [{"filename": "diagram.png", "action": "create"}],
            "verification": {
                "schema_version": "1.0",
                "status": "verified",
                "operation_id": "mutation-operation-42",
                "page_id": "42",
                "remote_version": 2,
                "verified_at": "2026-07-13T04:00:45Z",
            },
        },
    )
    expectations = campaign / "capability-expectations.json"
    _write_json(
        expectations,
        {
            "schema_version": module.SCHEMA_VERSION,
            "campaign_id": "synthetic-live-campaign",
            "workspaces": [
                {
                    "id": "example",
                    "path": "workspaces/example",
                    "artifacts": {
                        "storage": "page.storage.xml",
                        "api_report": "verification/report.json",
                        "noop_dry_run": "verification/noop-dry-run.json",
                        "browser_gt": "verification/browser-ground-truth.json",
                    },
                    "mutation_receipt": {
                        "path": "verification/upload.json",
                        "allowed_statuses": ["uploaded"],
                        "page_updated": True,
                        "attachment_actions": {"diagram.png": "create"},
                    },
                    "capabilities": [
                        {
                            "id": "complete-capability",
                            "description": "Complete synthetic acceptance capability.",
                            "local": {
                                "tags_min": {
                                    "a": 1,
                                    "ac:image": 1,
                                    "ac:structured-macro": 1,
                                    "h2": 1,
                                    "ri:attachment": 1,
                                    "ri:page": 1,
                                },
                                "macros_min": {"info": 1},
                                "parameters_min": {"alt": 1},
                                "parameter_values": {
                                    "alt": ["Fixture diagram alternative text"]
                                },
                                "image_alternative_texts": [
                                    "Fixture diagram accessible name"
                                ],
                                "hrefs": ["https://example.test/reference"],
                                "page_references": ["Target Page"],
                                "attachment_references": ["diagram.png"],
                                "attachment_files": ["diagram.png"],
                                "visible_markers": ["Acceptance marker", "Panel marker"],
                            },
                            "api": {
                                "report_status": "verified",
                                "nodes_min": {"doc": 1, "media": 1},
                                "marks_min": {"link": 1},
                                "urls": ["https://example.test/reference"],
                                "media_min": 1,
                                "view_contains": [
                                    'alt="Fixture diagram accessible name"'
                                ],
                                "required_checks": ["storage-equivalent"],
                            },
                            "browser": {
                                "required_check_ids": ["rendered-capability"],
                                "require_screenshots": True,
                            },
                        }
                    ],
                }
            ],
        },
    )
    return module, expectations, workspace


def _enable_campaign_progress(expectations: Path, workspace: Path) -> Path:
    """Add a valid hash-bound campaign ledger to the synthetic fixture."""

    campaign = expectations.parent
    report_relative = "workspaces/example/verification/report.json"
    report_path = campaign / report_relative
    browser_relative = "workspaces/example/verification/browser-ground-truth.json"
    browser_path = campaign / browser_relative
    progress_path = campaign / "campaign-progress.json"
    _write_json(
        progress_path,
        {
            "schema_version": "1.0",
            "campaign_id": "synthetic-live-campaign",
            "tenant": "https://tenant.atlassian.net",
            "space_id": "100",
            "started_at": "2026-07-12T20:00:00Z",
            "minimum_end_at": "2026-07-13T04:00:00Z",
            "status": "complete",
            "last_updated_at": "2026-07-13T04:03:00Z",
            "live_capability_result": {
                "status": "complete",
                "passed": 1,
                "failed": 0,
                "missing": 0,
                "prerequisite": 0,
            },
            "fixture_result": {
                "status": "verified",
                "page_id": "42",
                "remote_version": 2,
                "operation_id": "operation-42",
                "api_report": report_relative,
                "browser_evidence": browser_relative,
                "completion": {
                    "api_checks": 10,
                    "browser_checks": 1,
                    "screenshots": 2,
                    "noop": True,
                },
            },
            "evidence_bindings": {
                report_relative: sha256(report_path.read_bytes()).hexdigest(),
                browser_relative: sha256(browser_path.read_bytes()).hexdigest(),
            },
            "pages": [
                {
                    "page_id": "42",
                    "workspace": "workspaces/example",
                    "workspace_id": "example",
                    "title": "Fixture",
                    "phase": "verified",
                    "remote_version": 2,
                    "operation_id": "operation-42",
                }
            ],
        },
    )
    payload = json.loads(expectations.read_text(encoding="utf-8"))
    payload["campaign_progress"] = progress_path.name
    _write_json(expectations, payload)
    return progress_path


def _capability(result: dict[str, Any]) -> dict[str, Any]:
    return result["workspaces"][0]["capabilities"][0]


def _rebind_browser_to_report(workspace: Path) -> None:
    report_path = workspace / "verification" / "report.json"
    browser_path = workspace / "verification" / "browser-ground-truth.json"
    browser = json.loads(browser_path.read_text(encoding="utf-8"))
    browser["api_report_sha256"] = sha256(report_path.read_bytes()).hexdigest()
    _write_json(browser_path, browser)


def _enable_fixture_interaction(
    expectations: Path,
    workspace: Path,
    *,
    actual: Any = "The expected marker was visible.",
    observed_at: str = "2026-07-13T04:01:30Z",
) -> Path:
    verification = workspace / "verification"
    browser_path = verification / "browser-ground-truth.json"
    screenshot = verification / "browser-final.png"
    interaction_path = verification / "browser-interactions.json"
    expected_actual = "The expected marker was visible."
    _write_json(
        interaction_path,
        {
            "schema_version": "1.0",
            "status": "verified",
            "page_id": "42",
            "operation_id": "operation-42",
            "browser_gt_sha256": sha256(browser_path.read_bytes()).hexdigest(),
            "observed_at": observed_at,
            "checks": [
                {
                    "id": "rendered-capability",
                    "passed": True,
                    "method": "authenticated-dom-and-screenshot",
                    "assertion": "The fixture renders.",
                    "actual": actual,
                    "screenshot": {
                        "path": screenshot.name,
                        "sha256": sha256(screenshot.read_bytes()).hexdigest(),
                    },
                }
            ],
        },
    )
    payload = json.loads(expectations.read_text(encoding="utf-8"))
    browser_config = payload["workspaces"][0]["capabilities"][0]["browser"]
    browser_config["interaction_evidence"] = "verification/browser-interactions.json"
    browser_config["required_interaction_ids"] = ["rendered-capability"]
    browser_config["interaction_expectations"] = {
        "rendered-capability": {
            "method": "authenticated-dom-and-screenshot",
            "actual_equals": expected_actual,
        }
    }
    _write_json(expectations, payload)
    return interaction_path


def test_default_expectations_are_english_and_cover_live_workspaces() -> None:
    payload = json.loads(DEFAULT_EXPECTATIONS.read_text(encoding="utf-8"))

    assert payload["schema_version"] == "1.0"
    assert payload["campaign_progress"] == "campaign-progress.json"
    assert [workspace["id"] for workspace in payload["workspaces"]] == [
        "text-structure",
        "links-media",
        "macros-dynamic",
        "metadata-safety",
        "pi-luna-complex-edit",
        "pi-openrouter-direct-tool-edit",
        "native-editor-coverage",
        "remote-render-preflight",
        "accessible-image-alt-text",
        "conditional-macro-discovery",
        "integration-macro-discovery",
    ]
    assert sum(len(workspace["capabilities"]) for workspace in payload["workspaces"]) == 32
    assert all(
        capability["description"]
        for workspace in payload["workspaces"]
        for capability in workspace["capabilities"]
    )


def test_accessible_image_expectation_requires_storage_view_and_browser_evidence() -> None:
    payload = json.loads(DEFAULT_EXPECTATIONS.read_text(encoding="utf-8"))
    workspace = next(
        item for item in payload["workspaces"] if item["id"] == "accessible-image-alt-text"
    )
    capability = workspace["capabilities"][0]

    assert capability["local"]["image_alternative_texts"] == [
        "Accessible Confluence storage round-trip architecture diagram"
    ]
    assert capability["api"]["adf_image_alternative_texts"] == [
        "Accessible Confluence storage round-trip architecture diagram"
    ]
    assert capability["api"]["view_image_alternative_texts"] == [
        "Accessible Confluence storage round-trip architecture diagram"
    ]
    assert capability["browser"]["required_check_ids"] == [
        "rendered-page",
        "accessible-alt-text",
        "caption",
    ]


def test_integration_macro_expectation_binds_office_rendering_and_tenant_boundaries() -> None:
    payload = json.loads(DEFAULT_EXPECTATIONS.read_text(encoding="utf-8"))
    workspace = next(
        item for item in payload["workspaces"] if item["id"] == "integration-macro-discovery"
    )

    assert workspace["path"] == "integration-macros-workspace-v5"
    assert [capability["id"] for capability in workspace["capabilities"]] == [
        "office-pdf-excel-functional-macros",
        "tenant-integration-gates-and-catalog-boundary",
    ]
    office, boundaries = workspace["capabilities"]
    assert office["local"]["macros_min"] == {"viewpdf": 1, "viewxls": 1}
    assert office["local"]["attachment_references"] == [
        "integration-preview.pdf",
        "office-excel-fixture.xlsx",
    ]
    assert office["api"]["extensions"] == ["viewpdf", "viewxls"]
    assert office["browser"]["required_check_ids"] == ["office-pdf-excel-render"]
    assert office["browser"]["required_interaction_ids"] == ["office-pdf-excel-render"]
    assert boundaries["local"]["tags_min"] == {"h2": 1, "li": 4, "ul": 1}
    assert boundaries["api"]["nodes_min"] == {
        "bulletList": 1,
        "heading": 4,
        "listItem": 4,
    }
    assert boundaries["browser"]["required_check_ids"] == [
        "tenant-integration-boundaries",
        "jira-activities-access-gate",
        "jira-chart-connection-gate",
        "assets-access-gate",
        "current-catalog-boundary",
    ]
    assert boundaries["browser"]["required_interaction_ids"] == [
        "tenant-integration-boundaries",
        "jira-activities-access-gate",
        "jira-chart-connection-gate",
        "assets-access-gate",
        "current-catalog-boundary",
    ]
    assert workspace["interaction_expectations"]["current-catalog-boundary"][
        "actual_equals"
    ]["locale"] == "es-ES"
    assert workspace["interaction_expectations"]["current-catalog-boundary"][
        "actual_equals"
    ]["exact_option_matches"] == {
        "Activity Stream": 0,
        "Team Calendars": 0,
        "Jira Timeline": 0,
        "Word": 0,
        "PowerPoint": 0,
    }


def test_conditional_premium_cards_and_carousel_gates_are_semantically_bound() -> None:
    payload = json.loads(DEFAULT_EXPECTATIONS.read_text(encoding="utf-8"))
    workspace = next(
        item for item in payload["workspaces"] if item["id"] == "conditional-macro-discovery"
    )
    capability = next(
        item
        for item in workspace["capabilities"]
        if item["id"] == "premium-cards-and-carousel-gates"
    )

    assert capability["browser"]["required_check_ids"] == [
        "cards-premium-gate",
        "carousel-premium-gate",
    ]
    assert capability["browser"]["required_interaction_ids"] == [
        "cards-premium-gate",
        "carousel-premium-gate",
    ]
    assert workspace["interaction_expectations"]["cards-premium-gate"][
        "actual_equals"
    ]["exact_option"] == "Tarjetas"
    assert workspace["interaction_expectations"]["carousel-premium-gate"][
        "actual_equals"
    ]["exact_option"] == "Carrusel"


def test_image_variants_require_separate_live_browser_checks() -> None:
    payload = json.loads(DEFAULT_EXPECTATIONS.read_text(encoding="utf-8"))
    workspace = next(item for item in payload["workspaces"] if item["id"] == "links-media")
    capability = next(
        item for item in workspace["capabilities"] if item["id"] == "image-attachments"
    )

    assert capability["browser"]["required_interaction_ids"] == [
        "image-attachments",
        "jpeg-image-render",
        "animated-gif-render",
    ]
    assert workspace["interaction_expectations"]["jpeg-image-render"]["actual_equals"][
        "mime_type"
    ] == "image/jpeg"
    assert workspace["interaction_expectations"]["animated-gif-render"]["actual_equals"][
        "changed_pixels"
    ] > 0


def test_native_editor_and_remote_preflight_expectations_are_structural() -> None:
    payload = json.loads(DEFAULT_EXPECTATIONS.read_text(encoding="utf-8"))
    native = next(
        item for item in payload["workspaces"] if item["id"] == "native-editor-coverage"
    )
    layout = next(item for item in native["capabilities"] if item["id"] == "native-layout-variants")
    assert layout["local"]["tags_min"]["ac:layout-cell"] == 22
    assert layout["api"]["nodes_min"] == {"layoutColumn": 22, "layoutSection": 8}
    assert native["interaction_expectations"]["nested-lists-tasks"]["actual_equals"][
        "toggle_evidence"
    ] == "browser-task-toggle.json"

    preflight = next(
        item for item in payload["workspaces"] if item["id"] == "remote-render-preflight"
    )
    assert preflight["mutation_receipt"]["remote_render_preflight"] == {
        "status": "completed",
        "polls_min": 1,
        "rendered_bytes_min": 1,
    }
    capability = preflight["capabilities"][0]
    assert capability["api"]["nodes_min"]["panel"] == 1
    assert capability["browser"]["required_interaction_ids"] == [
        "rendered-page",
        "remote-preflight-info-panel",
        "remote-preflight-four-columns",
        "remote-preflight-table",
    ]


def test_current_live_evidence_passes_hardened_contract() -> None:
    result = _load_validator().validate_capabilities(DEFAULT_EXPECTATIONS)

    assert result["status"] == "complete"
    assert result["campaign_complete"] is True
    assert result["counts"] == {
        "fail": 0,
        "missing": 0,
        "pass": 32,
        "prerequisite": 0,
    }
    assert result["campaign_progress"]["status"] == "pass"
    assert len(result["campaign_progress"]["page_ids"]) == 11


def test_campaign_progress_binds_counts_pages_lineage_and_evidence(tmp_path: Path) -> None:
    module, expectations, workspace = _build_fixture(tmp_path)
    _enable_campaign_progress(expectations, workspace)

    result = module.validate_capabilities(expectations)

    assert result["status"] == "complete"
    assert result["campaign_progress"]["status"] == "pass"
    assert result["campaign_progress"]["page_ids"] == ["42"]


def test_campaign_progress_rejects_stale_hash_escape_count_time_and_duplicate_page(
    tmp_path: Path,
) -> None:
    scenarios = {
        "stale-hash": (
            lambda payload: payload["evidence_bindings"].update(
                {"workspaces/example/verification/report.json": "0" * 64}
            ),
            "digest mismatch",
        ),
        "path-escape": (
            lambda payload: payload["fixture_result"].update(
                {"evidence": "../../outside.json"}
            ),
            "escapes its workspace",
        ),
        "wrong-count": (
            lambda payload: payload["live_capability_result"].update({"passed": 99}),
            "live_capability_result.passed expected 1",
        ),
        "wrong-derived-completion": (
            lambda payload: payload["fixture_result"]["completion"].update(
                {"api_checks": 99}
            ),
            "fixture_result.completion.api_checks expected 10",
        ),
        "stale-time": (
            lambda payload: payload.update(
                {"last_updated_at": "2026-07-13T03:59:00Z"}
            ),
            "cannot be complete before minimum_end_at",
        ),
        "duplicate-page": (
            lambda payload: payload["pages"].append(dict(payload["pages"][0])),
            "duplicate page_id '42'",
        ),
    }
    for name, (mutate, expected_issue) in scenarios.items():
        module, expectations, workspace = _build_fixture(tmp_path / name)
        progress_path = _enable_campaign_progress(expectations, workspace)
        progress = json.loads(progress_path.read_text(encoding="utf-8"))
        mutate(progress)
        _write_json(progress_path, progress)

        result = module.validate_capabilities(expectations)

        assert result["status"] == "failed", name
        assert result["campaign_progress"]["status"] == "fail", name
        assert any(
            expected_issue in issue for issue in result["campaign_progress"]["issues"]
        ), (name, result["campaign_progress"]["issues"])


def test_pi_luna_expectation_requires_complex_edit_evidence() -> None:
    payload = json.loads(DEFAULT_EXPECTATIONS.read_text(encoding="utf-8"))
    workspace = next(
        item for item in payload["workspaces"] if item["id"] == "pi-luna-complex-edit"
    )
    capability = workspace["capabilities"][0]

    assert workspace["path"] == "pi-luna-workspace"
    assert capability["id"] == "pi-luna-complex-edit"
    assert capability["local"]["macros_min"] == {
        "anchor": 1,
        "code": 1,
        "expand": 2,
        "info": 1,
        "status": 1,
        "tasks-report-macro": 1,
    }
    assert {
        "layoutColumn",
        "layoutSection",
        "nestedExpand",
        "status",
        "table",
        "taskItem",
        "taskList",
    } <= capability["api"]["nodes_min"].keys()
    assert capability["api"]["marks_min"]["link"] == 3
    assert capability["api"]["extensions"] == ["tasks-report-macro"]
    assert capability["browser"]["required_check_ids"] == [
        "rendered-page",
        "dynamic-task-report",
        "nested-expand",
        "internal-and-external-links",
        "table-and-layout",
    ]


def test_pi_luna_evidence_binds_artifacts_inventory_and_exploration() -> None:
    evidence = json.loads(PI_LUNA_EVIDENCE.read_text(encoding="utf-8"))

    assert evidence["schema_version"] == "1.0"
    assert evidence["status"] == "verified"
    assert evidence["page_id"] == "34570271"
    assert evidence["operation_id"] == "8a78ce08-6113-4d22-9307-f083bf67cddf"

    evidence_root = PI_LUNA_EVIDENCE.parent.resolve()
    resolved_artifacts: dict[str, tuple[dict[str, Any], Path]] = {}
    for name, artifact in evidence["artifacts"].items():
        relative_path = Path(artifact["path"])
        assert not relative_path.is_absolute(), name
        artifact_path = (evidence_root / relative_path).resolve()
        assert artifact_path.is_relative_to(evidence_root), name
        assert artifact_path.is_file(), name
        assert sha256(artifact_path.read_bytes()).hexdigest() == artifact["sha256"], name
        resolved_artifacts[name] = (artifact, artifact_path)

    api_report = json.loads(
        resolved_artifacts["api_report"][1].read_text(encoding="utf-8")
    )
    assert api_report["schema_version"] == evidence["schema_version"]
    assert api_report["status"] == evidence["status"]
    assert api_report["page_id"] == evidence["page_id"]
    assert api_report["operation_id"] == evidence["operation_id"]

    inventory_declaration, inventory_path = resolved_artifacts["refreshed_space_inventory"]
    inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
    assert inventory["schema_version"] == "1.0"
    assert inventory["status"] == "verified"
    assert inventory["errors"] == []
    assert inventory_declaration["pages"] == 14
    assert len(inventory["pages"]) == 14

    exploration_declaration, exploration_path = resolved_artifacts[
        "persisted_local_exploration"
    ]
    exploration = json.loads(exploration_path.read_text(encoding="utf-8"))
    assert exploration["status"] == "queried"
    assert exploration["inventory_status"] == "verified"
    assert exploration["errors"] == []
    assert exploration["count"] == 1
    assert exploration_declaration["matched_page_ids"] == [evidence["page_id"]]
    assert [page["page_id"] for page in exploration["pages"]] == [evidence["page_id"]]


def test_pi_openrouter_expectation_requires_direct_tool_edit_evidence() -> None:
    payload = json.loads(DEFAULT_EXPECTATIONS.read_text(encoding="utf-8"))
    workspace = next(
        item
        for item in payload["workspaces"]
        if item["id"] == "pi-openrouter-direct-tool-edit"
    )
    capability = workspace["capabilities"][0]

    assert workspace["path"] == "pi-openrouter-workspace"
    assert capability["id"] == "pi-openrouter-direct-tool-edit"
    assert capability["local"]["macros_min"] == {
        "code": 1,
        "expand": 2,
        "info": 1,
        "status": 1,
    }
    assert {
        "decisionItem",
        "decisionList",
        "layoutColumn",
        "layoutSection",
        "nestedExpand",
        "status",
        "table",
        "taskItem",
        "taskList",
    } <= capability["api"]["nodes_min"].keys()
    assert capability["api"]["marks_min"]["link"] == 2
    assert capability["browser"]["required_check_ids"] == [
        "rendered-page",
        "direct-pi-edit",
        "decision-node",
        "nested-expand",
        "task-table-layout-links",
    ]


def test_pi_openrouter_evidence_binds_api_browser_and_noop_state() -> None:
    evidence = json.loads(PI_OPENROUTER_EVIDENCE.read_text(encoding="utf-8"))

    assert evidence["schema_version"] == "1.0"
    assert evidence["status"] == "verified"
    assert evidence["page_id"] == "34471938"
    assert str(UUID(evidence["operation_id"])) == evidence["operation_id"]
    assert isinstance(evidence["remote_version"], int) and evidence["remote_version"] > 0

    evidence_root = PI_OPENROUTER_EVIDENCE.parent.resolve()
    resolved_artifacts: dict[str, Path] = {}
    for name, artifact in evidence["artifacts"].items():
        relative_path = Path(artifact["path"])
        assert not relative_path.is_absolute(), name
        artifact_path = (evidence_root / relative_path).resolve()
        assert artifact_path.is_relative_to(evidence_root), name
        assert artifact_path.is_file(), name
        assert sha256(artifact_path.read_bytes()).hexdigest() == artifact["sha256"], name
        resolved_artifacts[name] = artifact_path

    report_path = resolved_artifacts["api_report"]
    report = json.loads(report_path.read_text(encoding="utf-8"))
    browser = json.loads(
        resolved_artifacts["browser_ground_truth"].read_text(encoding="utf-8")
    )
    noop = json.loads(resolved_artifacts["noop_dry_run"].read_text(encoding="utf-8"))

    assert report["schema_version"] == evidence["schema_version"]
    assert report["status"] == evidence["status"]
    assert report["page_id"] == evidence["page_id"]
    assert report["operation_id"] == evidence["operation_id"]
    assert report["remote_version"] == evidence["remote_version"]

    assert browser["schema_version"] == evidence["schema_version"]
    assert browser["status"] == evidence["status"]
    assert browser["page_id"] == evidence["page_id"]
    assert browser["operation_id"] == evidence["operation_id"]
    assert browser["remote_version"] == evidence["remote_version"]
    assert browser["desired_state_sha256"] == report["desired_state_sha256"]
    assert browser["api_report_sha256"] == sha256(report_path.read_bytes()).hexdigest()

    assert noop["status"] == "dry-run"
    assert noop["plan"]["page_id"] == evidence["page_id"]
    assert noop["plan"]["current_version"] == evidence["remote_version"]
    assert noop["plan"]["expected_version"] == evidence["remote_version"]
    assert noop["plan"]["desired_state_sha256"] == report["desired_state_sha256"]
    assert noop["plan"]["resumed_from_operation_id"] is None
    assert noop["plan"]["no_op"] is True
    assert noop["plan"]["page_update"] is False
    assert noop["plan"]["body_changed"] is False
    assert noop["plan"]["metadata_changed"] is False
    assert noop["plan"]["attachments"] == []


def test_complete_fixture_passes_every_evidence_layer(tmp_path: Path) -> None:
    module, expectations, _ = _build_fixture(tmp_path)

    result = module.validate_capabilities(expectations)

    assert result["status"] == "complete"
    assert result["campaign_complete"] is True
    assert result["counts"] == {"fail": 0, "missing": 0, "pass": 1, "prerequisite": 0}
    capability = _capability(result)
    assert capability["status"] == "pass"
    assert [check["status"] for check in capability["checks"]] == ["pass"] * 6


def test_extensions_are_validated_only_when_declared(tmp_path: Path) -> None:
    module, expectations, _ = _build_fixture(tmp_path)

    result = module.validate_capabilities(expectations)
    assert _capability(result)["checks"][1]["status"] == "pass"

    payload = json.loads(expectations.read_text(encoding="utf-8"))
    payload["workspaces"][0]["capabilities"][0]["api"]["extensions"] = ["widget"]
    _write_json(expectations, payload)

    result = module.validate_capabilities(expectations)

    api = _capability(result)["checks"][1]
    assert api["status"] == "fail"
    assert api["issues"] == ["extensions is missing 'widget'"]


def test_storage_parameter_values_are_structurally_validated(tmp_path: Path) -> None:
    module, expectations, workspace = _build_fixture(tmp_path)
    storage = workspace / "page.storage.xml"
    storage.write_text(
        storage.read_text(encoding="utf-8").replace(
            '<ac:parameter ac:name="alt">Fixture diagram alternative text</ac:parameter>',
            "",
        ),
        encoding="utf-8",
    )

    result = module.validate_capabilities(expectations)

    local = _capability(result)["checks"][0]
    assert local["status"] == "fail"
    assert any("parameters.alt expected >= 1" in issue for issue in local["issues"])
    assert any("parameter_values.alt is missing" in issue for issue in local["issues"])


def test_accessible_image_name_is_bound_across_storage_and_rendered_view(
    tmp_path: Path,
) -> None:
    module, expectations, workspace = _build_fixture(tmp_path)
    storage = workspace / "page.storage.xml"
    storage.write_text(
        storage.read_text(encoding="utf-8").replace(
            ' ac:alt="Fixture diagram accessible name"',
            "",
        ),
        encoding="utf-8",
    )
    view = workspace / "verification" / "remote.view.html"
    view.write_text('<img src="diagram.png">', encoding="utf-8")
    report_path = workspace / "verification" / "report.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    report["evidence"]["view"]["sha256"] = sha256(view.read_bytes()).hexdigest()
    _write_json(report_path, report)

    result = module.validate_capabilities(expectations)

    capability = _capability(result)
    assert capability["checks"][0]["status"] == "fail"
    assert any(
        "image_alternative_texts is missing" in issue
        for issue in capability["checks"][0]["issues"]
    )
    assert capability["checks"][1]["status"] == "fail"
    assert any(
        "rendered-view image alt is missing" in issue
        for issue in capability["checks"][1]["issues"]
    )


def test_in_progress_fixture_reports_missing_and_prerequisites(tmp_path: Path) -> None:
    module, expectations, workspace = _build_fixture(tmp_path)
    (workspace / "verification" / "report.json").unlink()
    (workspace / "verification" / "noop-dry-run.json").unlink()
    (workspace / "verification" / "browser-ground-truth.json").unlink()

    result = module.validate_capabilities(expectations)

    assert result["status"] == "in-progress"
    assert result["campaign_complete"] is False
    capability = _capability(result)
    assert capability["status"] == "missing"
    assert [check["status"] for check in capability["checks"]] == [
        "pass",
        "missing",
        "prerequisite",
        "prerequisite",
        "pass",
        "prerequisite",
    ]


def test_present_but_contradictory_evidence_fails_instead_of_looking_missing(
    tmp_path: Path,
) -> None:
    module, expectations, workspace = _build_fixture(tmp_path)
    report_path = workspace / "verification" / "report.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    report["status"] = "failed"
    report["adf_summary"]["nodes"]["media"] = 0
    _write_json(report_path, report)

    result = module.validate_capabilities(expectations)

    assert result["status"] == "failed"
    assert result["campaign_complete"] is False
    api = _capability(result)["checks"][1]
    assert api["status"] == "fail"
    assert any("API report status" in issue for issue in api["issues"])
    assert any("adf_summary.nodes does not match" in issue for issue in api["issues"])


def test_noop_artifact_rejects_any_planned_mutation(tmp_path: Path) -> None:
    module, expectations, workspace = _build_fixture(tmp_path)
    noop_path = workspace / "verification" / "noop-dry-run.json"
    noop = json.loads(noop_path.read_text(encoding="utf-8"))
    noop["plan"]["page_update"] = True
    noop["plan"]["attachments"] = [{"filename": "diagram.png", "action": "update"}]
    noop["plan"]["labels"]["added"] = ["unexpected-label"]
    noop["plan"]["content_state_changed"] = True
    noop["plan"]["no_op"] = False
    _write_json(noop_path, noop)

    result = module.validate_capabilities(expectations)

    noop_check = _capability(result)["checks"][2]
    assert result["status"] == "failed"
    assert noop_check["status"] == "fail"
    assert any("plan.page_update must be false" in issue for issue in noop_check["issues"])
    assert any("plan.attachments must be empty" in issue for issue in noop_check["issues"])
    assert any("plan.labels.added must be empty" in issue for issue in noop_check["issues"])
    assert any("content_state_changed must be false" in issue for issue in noop_check["issues"])
    assert any("plan.no_op must be true" in issue for issue in noop_check["issues"])


def test_browser_gt_requires_named_passing_checks_and_untampered_screenshot(
    tmp_path: Path,
) -> None:
    module, expectations, workspace = _build_fixture(tmp_path)
    browser_path = workspace / "verification" / "browser-ground-truth.json"
    browser = json.loads(browser_path.read_text(encoding="utf-8"))
    browser["checks"][0]["id"] = "unrelated-check"
    _write_json(browser_path, browser)
    (workspace / "verification" / "browser-final.png").write_bytes(b"tampered screenshot")

    result = module.validate_capabilities(expectations)

    browser_check = _capability(result)["checks"][3]
    assert result["status"] == "failed"
    assert browser_check["status"] == "fail"
    assert any("rendered-capability" in issue for issue in browser_check["issues"])
    assert any("digest mismatch" in issue for issue in browser_check["issues"])


def test_detailed_browser_interactions_bind_operation_gt_and_screenshot(
    tmp_path: Path,
) -> None:
    module, expectations, workspace = _build_fixture(tmp_path)
    verification = workspace / "verification"
    browser_path = verification / "browser-ground-truth.json"
    screenshot = verification / "browser-final.png"
    interactions = verification / "browser-interactions.json"
    _write_json(
        interactions,
        {
            "schema_version": "1.0",
            "status": "verified",
            "page_id": "42",
            "operation_id": "operation-42",
            "browser_gt_sha256": sha256(browser_path.read_bytes()).hexdigest(),
            "observed_at": "2026-07-13T04:01:30Z",
            "checks": [
                {
                    "id": "rendered-capability",
                    "passed": True,
                    "method": "authenticated-dom-and-screenshot",
                    "assertion": "The fixture renders.",
                    "actual": "The expected marker was visible.",
                    "screenshot": {
                        "path": screenshot.name,
                        "sha256": sha256(screenshot.read_bytes()).hexdigest(),
                    },
                }
            ],
        },
    )
    payload = json.loads(expectations.read_text(encoding="utf-8"))
    browser_config = payload["workspaces"][0]["capabilities"][0]["browser"]
    browser_config["interaction_evidence"] = "verification/browser-interactions.json"
    browser_config["required_interaction_ids"] = ["rendered-capability"]
    browser_config["interaction_expectations"] = {
        "rendered-capability": {
            "method": "authenticated-dom-and-screenshot",
            "actual_equals": "The expected marker was visible.",
        }
    }
    _write_json(expectations, payload)

    passing = module.validate_capabilities(expectations)
    assert _capability(passing)["checks"][3]["status"] == "pass"

    evidence = json.loads(interactions.read_text(encoding="utf-8"))
    evidence["browser_gt_sha256"] = "0" * 64
    evidence["checks"][0]["screenshot"]["sha256"] = "f" * 64
    _write_json(interactions, evidence)
    failing = module.validate_capabilities(expectations)
    issues = _capability(failing)["checks"][3]["issues"]
    assert any("does not bind the current browser GT" in issue for issue in issues)
    assert any("screenshot digest mismatch" in issue for issue in issues)


def test_browser_screenshot_cannot_escape_workspace(tmp_path: Path) -> None:
    module, expectations, workspace = _build_fixture(tmp_path)
    outside = workspace.parent / "outside.png"
    outside.write_bytes(b"outside")
    browser_path = workspace / "verification" / "browser-ground-truth.json"
    browser = json.loads(browser_path.read_text(encoding="utf-8"))
    browser["final_screenshots"][0] = {
        "path": "../../outside.png",
        "sha256": sha256(outside.read_bytes()).hexdigest(),
    }
    _write_json(browser_path, browser)

    result = module.validate_capabilities(expectations)

    browser_check = _capability(result)["checks"][3]
    assert browser_check["status"] == "fail"
    assert any("escapes its workspace" in issue for issue in browser_check["issues"])


def test_browser_gt_is_bound_to_api_operation_url_and_distinct_baseline(
    tmp_path: Path,
) -> None:
    module, expectations, workspace = _build_fixture(tmp_path)
    browser_path = workspace / "verification" / "browser-ground-truth.json"
    browser = json.loads(browser_path.read_text(encoding="utf-8"))
    browser["operation_id"] = "different-operation"
    browser["api_report_sha256"] = "f" * 64
    browser["page_url"] = "http://other.example/pages/99"
    baseline_path = workspace / "verification" / browser["baseline"]["path"]
    final_path = workspace / "verification" / browser["final_screenshots"][0]["path"]
    final_path.write_bytes(baseline_path.read_bytes())
    browser["final_screenshots"][0]["sha256"] = sha256(final_path.read_bytes()).hexdigest()
    _write_json(browser_path, browser)

    result = module.validate_capabilities(expectations)

    issues = _capability(result)["checks"][3]["issues"]
    assert any("operation_id does not match" in issue for issue in issues)
    assert any("api_report_sha256" in issue for issue in issues)
    assert any("absolute HTTPS" in issue for issue in issues)
    assert any("does not identify" in issue for issue in issues)
    assert any("different tenant" in issue for issue in issues)
    assert any("baseline and final screenshots must be distinct" in issue for issue in issues)


def test_unuploaded_local_storage_change_cannot_remain_complete(tmp_path: Path) -> None:
    module, expectations, workspace = _build_fixture(tmp_path)
    storage = workspace / "page.storage.xml"
    storage.write_text(
        storage.read_text(encoding="utf-8") + "<p>Never uploaded local change</p>\n",
        encoding="utf-8",
    )

    result = module.validate_capabilities(expectations)

    assert result["status"] == "failed"
    contract = _capability(result)["checks"][5]
    assert contract["status"] == "fail"
    assert any("stale for page.storage.xml" in issue for issue in contract["issues"])


def test_noop_must_bind_page_version_and_desired_digest(tmp_path: Path) -> None:
    module, expectations, workspace = _build_fixture(tmp_path)
    noop_path = workspace / "verification" / "noop-dry-run.json"
    noop = json.loads(noop_path.read_text(encoding="utf-8"))
    noop["plan"].update(
        {
            "page_id": "999999",
            "current_version": 999,
            "expected_version": 999,
            "desired_state_sha256": "0" * 64,
        }
    )
    _write_json(noop_path, noop)

    result = module.validate_capabilities(expectations)

    check = _capability(result)["checks"][2]
    assert check["status"] == "fail"
    assert any("page_id" in issue for issue in check["issues"])
    assert any("current_version" in issue for issue in check["issues"])
    assert any("expected_version" in issue for issue in check["issues"])
    assert any("desired_state_sha256" in issue for issue in check["issues"])


def test_every_api_evidence_hash_is_verified(tmp_path: Path) -> None:
    module, expectations, workspace = _build_fixture(tmp_path)
    adf_path = workspace / "verification" / "remote.adf.json"
    adf_path.write_text('{"type":"doc","version":1,"content":[]}', encoding="utf-8")

    result = module.validate_capabilities(expectations)

    api = _capability(result)["checks"][1]
    assert api["status"] == "fail"
    assert any("atlas_doc_format" in issue and "digest mismatch" in issue for issue in api["issues"])


def test_report_media_ids_are_derived_from_hashed_adf(tmp_path: Path) -> None:
    module, expectations, workspace = _build_fixture(tmp_path)
    report_path = workspace / "verification" / "report.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    report["adf_summary"]["media_ids"] = [None]
    _write_json(report_path, report)
    _rebind_browser_to_report(workspace)

    result = module.validate_capabilities(expectations)

    api = _capability(result)["checks"][1]
    assert api["status"] == "fail"
    assert any("adf_summary.media_ids does not match" in issue for issue in api["issues"])


def test_alt_text_in_html_comment_does_not_satisfy_img_semantics(tmp_path: Path) -> None:
    module, expectations, workspace = _build_fixture(tmp_path)
    view = workspace / "verification" / "remote.view.html"
    view.write_text(
        '<img src="diagram.png"><!-- alt="Fixture diagram accessible name" -->',
        encoding="utf-8",
    )
    report_path = workspace / "verification" / "report.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    report["evidence"]["view"]["sha256"] = sha256(view.read_bytes()).hexdigest()
    _write_json(report_path, report)
    _rebind_browser_to_report(workspace)

    result = module.validate_capabilities(expectations)

    api = _capability(result)["checks"][1]
    assert api["status"] == "fail"
    assert any("rendered-view image alt is missing" in issue for issue in api["issues"])


def test_manifest_is_mandatory_for_page_and_tenant_binding(tmp_path: Path) -> None:
    module, expectations, workspace = _build_fixture(tmp_path)
    (workspace / "manifest.json").unlink()
    report_path = workspace / "verification" / "report.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    report["page_id"] = "999"
    _write_json(report_path, report)
    browser_path = workspace / "verification" / "browser-ground-truth.json"
    browser = json.loads(browser_path.read_text(encoding="utf-8"))
    browser["page_id"] = "999"
    browser["page_url"] = "https://evil.example/wiki/pages/999/Fake"
    browser["api_report_sha256"] = sha256(report_path.read_bytes()).hexdigest()
    _write_json(browser_path, browser)

    result = module.validate_capabilities(expectations)

    assert result["status"] == "failed"
    identity = _capability(result)["checks"][4]
    assert identity["status"] == "fail"
    assert any("manifest.json" in issue for issue in identity["issues"])


def test_interaction_actual_and_timestamp_are_semantically_validated(tmp_path: Path) -> None:
    module, expectations, workspace = _build_fixture(tmp_path)
    _enable_fixture_interaction(
        expectations,
        workspace,
        actual={"count": 0, "name": "wrong"},
        observed_at="not-a-timestamp",
    )

    result = module.validate_capabilities(expectations)

    browser = _capability(result)["checks"][3]
    assert browser["status"] == "fail"
    assert any("observed_at must be a valid ISO timestamp" in issue for issue in browser["issues"])
    assert any("actual evidence is unexpected" in issue for issue in browser["issues"])


def test_failed_mutation_receipt_cannot_be_ignored(tmp_path: Path) -> None:
    module, expectations, workspace = _build_fixture(tmp_path)
    receipt_path = workspace / "verification" / "upload.json"
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    receipt["status"] = "verification-failed"
    receipt["page_updated"] = False
    _write_json(receipt_path, receipt)

    result = module.validate_capabilities(expectations)

    contract = _capability(result)["checks"][5]
    assert contract["status"] == "fail"
    assert any("status is not accepted" in issue for issue in contract["issues"])
    assert any("page_updated expected" in issue for issue in contract["issues"])


def test_capability_ids_are_globally_unique_and_nonempty(tmp_path: Path) -> None:
    module, expectations, workspace = _build_fixture(tmp_path)
    campaign = expectations.parent
    second = campaign / "workspaces" / "second"
    shutil.copytree(workspace, second)
    payload = json.loads(expectations.read_text(encoding="utf-8"))
    second_config = json.loads(json.dumps(payload["workspaces"][0]))
    second_config["id"] = "second"
    second_config["path"] = "workspaces/second"
    payload["workspaces"].append(second_config)
    _write_json(expectations, payload)

    duplicate = module.validate_capabilities(expectations)
    assert duplicate["status"] == "failed"
    assert duplicate["campaign_complete"] is False
    assert any("duplicate capability id across campaign" in error for error in duplicate["errors"])

    payload = json.loads(expectations.read_text(encoding="utf-8"))
    payload["workspaces"] = payload["workspaces"][:1]
    payload["workspaces"][0]["capabilities"][0]["id"] = ""
    _write_json(expectations, payload)
    empty = module.validate_capabilities(expectations)
    assert empty["status"] == "failed"
    assert any("non-empty string id" in error for error in empty["errors"])


def test_unhashable_interaction_screenshot_path_fails_without_crashing(tmp_path: Path) -> None:
    module, expectations, workspace = _build_fixture(tmp_path)
    interaction_path = _enable_fixture_interaction(expectations, workspace)
    browser_path = workspace / "verification" / "browser-ground-truth.json"
    browser = json.loads(browser_path.read_text(encoding="utf-8"))
    browser["final_screenshots"][0]["path"] = []
    _write_json(browser_path, browser)
    interactions = json.loads(interaction_path.read_text(encoding="utf-8"))
    interactions["browser_gt_sha256"] = sha256(browser_path.read_bytes()).hexdigest()
    _write_json(interaction_path, interactions)

    result = module.validate_capabilities(expectations)

    assert result["status"] == "failed"
    browser_check = _capability(result)["checks"][3]
    assert browser_check["status"] == "fail"
    assert any("artifact path must be" in issue for issue in browser_check["issues"])


def test_screenshot_must_be_a_decodable_image(tmp_path: Path) -> None:
    module, expectations, workspace = _build_fixture(tmp_path)
    screenshot = workspace / "verification" / "browser-final.png"
    screenshot.write_bytes(b"not a PNG despite the extension")
    browser_path = workspace / "verification" / "browser-ground-truth.json"
    browser = json.loads(browser_path.read_text(encoding="utf-8"))
    browser["final_screenshots"][0]["sha256"] = sha256(screenshot.read_bytes()).hexdigest()
    _write_json(browser_path, browser)

    result = module.validate_capabilities(expectations)

    browser_check = _capability(result)["checks"][3]
    assert browser_check["status"] == "fail"
    assert any("not a decodable PNG or JPEG" in issue for issue in browser_check["issues"])


def test_cli_distinguishes_valid_in_progress_from_required_completion(tmp_path: Path) -> None:
    _, expectations, workspace = _build_fixture(tmp_path)
    (workspace / "verification" / "report.json").unlink()
    (workspace / "verification" / "noop-dry-run.json").unlink()
    (workspace / "verification" / "browser-ground-truth.json").unlink()

    ordinary = subprocess.run(
        [sys.executable, str(VALIDATOR), "--expectations", str(expectations)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=30,
        check=False,
    )
    strict = subprocess.run(
        [
            sys.executable,
            str(VALIDATOR),
            "--expectations",
            str(expectations),
            "--require-complete",
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=30,
        check=False,
    )

    assert ordinary.returncode == 0
    assert strict.returncode == 3
    assert json.loads(strict.stdout)["status"] == "in-progress"


def test_cli_output_matches_stdout_and_preserves_require_complete_exit_code(
    tmp_path: Path,
) -> None:
    _, expectations, workspace = _build_fixture(tmp_path)
    (workspace / "verification" / "report.json").unlink()
    (workspace / "verification" / "noop-dry-run.json").unlink()
    (workspace / "verification" / "browser-ground-truth.json").unlink()
    output = tmp_path / "nested" / "capability-results.json"

    completed = subprocess.run(
        [
            sys.executable,
            str(VALIDATOR),
            "--expectations",
            str(expectations),
            "--output",
            str(output),
            "--require-complete",
        ],
        capture_output=True,
        text=False,
        timeout=30,
        check=False,
    )

    assert completed.returncode == 3
    assert output.read_bytes() == completed.stdout
    assert json.loads(output.read_text(encoding="utf-8"))["status"] == "in-progress"
    assert list(output.parent.glob(f".{output.name}.*.tmp")) == []


def test_official_documentation_audit_is_operationally_bound() -> None:
    progress = json.loads(
        (EVALUATION_ROOT / "campaign-progress.json").read_text(encoding="utf-8")
    )
    declaration = progress["official_documentation_audit"]
    relative = declaration["evidence"]
    path = EVALUATION_ROOT / relative
    audit = json.loads(path.read_text(encoding="utf-8"))

    assert declaration["status"] == "verified"
    assert declaration["reviewed_at"] == audit["reviewed_at"]
    assert progress["evidence_bindings"][relative] == sha256(path.read_bytes()).hexdigest()
    assert audit["status"] == "verified"
    assert all(
        source["url"].startswith(
            ("https://support.atlassian.com/", "https://developer.atlassian.com/")
        )
        for source in audit["sources"]
    )
    probe = audit["tenant_read_only_probe"]
    assert probe["page_subtype_results"] == probe["all_current_results"] == 20
    assert probe["live_subtype_results"] == 0
    assert probe["pagination_next_present"] is True
    assert probe["pagination_query_keys"] == [
        "cursor",
        "limit",
        "space-id",
        "status",
        "subtype",
    ]
    assert probe["pagination_invariants_validated"] is True
    assert probe["mutation_performed"] is False
