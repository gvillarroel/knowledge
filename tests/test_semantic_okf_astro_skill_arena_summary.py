"""Focused tests for the checked q040 Skill Arena result summarizer."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest


REPO = Path(__file__).resolve().parents[1]
EVALUATION = REPO / "evaluations" / "semantic-okf-astro"
SCRIPT = EVALUATION / "scripts" / "summarize_q040_skill_arena.py"
COMPARE = (
    REPO
    / "results"
    / "semantic-okf-astro-q040-ensemble-paired"
    / "2026-07-16T11-38-31-783Z-compare"
)
BUNDLES = (
    EVALUATION
    / "results"
    / "runs"
    / "20260716-astro-generic-01"
    / "bundles"
)
HAS_ACCEPTED_RAW_RUN = (
    (COMPARE / "promptfoo-results.json").is_file()
    and (BUNDLES / "ensemble-a" / "semantic" / "records.jsonl").is_file()
)
requires_accepted_raw_run = pytest.mark.skipif(
    not HAS_ACCEPTED_RAW_RUN,
    reason="the accepted append-only Skill Arena runs and bundles are intentionally ignored",
)


def load_runtime():
    """Load the real summarizer through its checked script boundary."""

    name = "astro_q040_skill_arena_summary_test_runtime"
    specification = importlib.util.spec_from_file_location(name, SCRIPT)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


RUNTIME = load_runtime()


def test_response_parser_preserves_object_and_reports_trailing_data() -> None:
    """A recoverable extra brace remains an explicit strict-JSON defect."""

    raw = '{"question_id":"q040","answer":null,"evidence":[]}}'
    parsed, metadata = RUNTIME.parse_response(raw)
    assert parsed == {"question_id": "q040", "answer": None, "evidence": []}
    assert list(parsed) == ["question_id", "answer", "evidence"]
    assert metadata["strict_json"] is False
    assert metadata["trailing_character_count"] == 1
    assert metadata["output_sha256"] == RUNTIME.sha256_bytes(raw.encode("utf-8"))
    RUNTIME.validate_parsed_response(parsed)


def test_family_paths_can_be_repeated_or_bound_explicitly(tmp_path: Path) -> None:
    """Future accepted runs can aggregate without inferring family from response content."""

    inferred = RUNTIME.parse_compare_dirs([str(COMPARE)])
    assert inferred == {"ensemble": COMPARE.resolve()}
    explicit = RUNTIME.parse_compare_dirs(
        [f"legacy={tmp_path / 'legacy'}", f"ensemble={COMPARE}"]
    )
    assert list(explicit) == ["legacy", "ensemble"]
    with pytest.raises(RUNTIME.SummaryError, match="duplicate"):
        RUNTIME.parse_compare_dirs([f"ensemble={COMPARE}", f"ensemble={COMPARE}"])


def test_aggregate_retains_supported_family_order(monkeypatch, tmp_path: Path) -> None:
    """Adding runs cannot merge or reorder their independent causal cells."""

    def fake(family: str, path: Path, **_kwargs):
        return {
            "family": family,
            "accepted_run": {"run_id": path.name},
            "outcome": {"control_pass_rate": 0.0, "treatment_pass_rate": 1.0},
            "profiles": [
                {"evidence_validation": {"all_valid": None}},
                {"evidence_validation": {"all_valid": True}},
            ],
        }

    monkeypatch.setattr(RUNTIME, "summarize_run", fake)
    report = RUNTIME.summarize(
        {"ensemble": tmp_path / "ensemble", "legacy": tmp_path / "legacy"}
    )
    assert [row["family"] for row in report["families"]] == ["legacy", "ensemble"]
    assert report["aggregate_interpretation"]["paired_result_count"] == 2
    assert report["aggregate_interpretation"]["all_treatments_passed"] is True
    assert report["aggregate_interpretation"]["all_controls_failed"] is True


@requires_accepted_raw_run
def test_accepted_ensemble_run_binds_artifacts_and_exact_responses() -> None:
    """The final eval ID, hashes, cells, assertions, and responses remain auditable."""

    family = RUNTIME.summarize_run("ensemble", COMPARE)
    accepted = family["accepted_run"]
    assert accepted == {
        "accepted": True,
        "run_id": "2026-07-16T11-38-31-783Z-compare",
        "compare_directory": (
            "results/semantic-okf-astro-q040-ensemble-paired/"
            "2026-07-16T11-38-31-783Z-compare"
        ),
        "eval_id": "eval-EG6-2026-07-16T11:38:39",
        "benchmark_id": "semantic-okf-astro-q040-ensemble-paired",
        "prompt_id": "q040",
        "variant_id": "pi-luna-only",
    }
    assert family["source_artifacts"]["promptfoo_results"]["sha256"] == (
        "5c4de2563c728916edcf0ee9224d5459fb9aafc26d01bc0c16388d23c1bbbc46"
    )
    assert [(row["profile_id"], row["pass"], row["score"], row["latency_ms"]) for row in family["profiles"]] == [
        ("knowledge-only-control", False, 0, 114571),
        ("ensemble-consult-treatment", True, 1, 271042),
    ]
    assert [[assertion["metric"] for assertion in row["assertions"]] for row in family["profiles"]] == [
        list(RUNTIME.EXPECTED_ASSERTIONS),
        list(RUNTIME.EXPECTED_ASSERTIONS),
    ]
    raw = RUNTIME.load_json(COMPARE / "promptfoo-results.json")["results"]["results"]
    for profile, source in zip(family["profiles"], raw):
        expected, _ = RUNTIME.parse_response(source["response"]["output"])
        assert profile["parsed_response"] == expected
    assert family["outcome"]["absolute_percentage_point_delta"] == 100.0
    assert family["outcome"]["treatment_evidence_status"] == "pass"
    assert [row["evidence_validation"]["status"] for row in family["profiles"]] == [
        "pass",
        "pass",
    ]
    assert [row["evidence_validation"]["invalid"] for row in family["profiles"]] == [0, 0]
    assert family["harness_interpretation"]["derived_overall_status"] == "FAILED"


@requires_accepted_raw_run
def test_authoritative_evidence_validator_surfaces_typos_and_extra_fields() -> None:
    """Contract-shaped output cannot hide a bad source ID or legacy field drift."""

    ledger = RUNTIME.AuthoritativeLedger(
        RUNTIME.DEFAULT_BUNDLES_ROOT / "ensemble-a" / "semantic" / "records.jsonl",
        RUNTIME.DEFAULT_SOURCE_COMBINATION,
    )
    report = RUNTIME.summarize_run("ensemble", COMPARE)
    valid = dict(report["profiles"][1]["parsed_response"]["evidence"][3])
    typo = dict(valid, source_id="astro-doc-67458ae49efafc50")
    typo_result = ledger.validate(typo, 0)
    assert typo_result["valid"] is False
    assert typo_result["issues"] == [
        "source_id + record_id is absent from the frozen identity crosswalk/ledger"
    ]
    legacy_shape = dict(valid)
    legacy_shape["locator"] = "character-range:0-10"
    legacy_shape["text"] = "untrusted model text"
    legacy_result = ledger.validate(legacy_shape, 1)
    assert legacy_result["valid"] is False
    assert "evidence keys/order differ from the closed response contract" in legacy_result["issues"]
    assert "locator is not an object" in legacy_result["issues"]


@requires_accepted_raw_run
def test_wrong_family_binding_is_rejected() -> None:
    """An ensemble run cannot silently populate another family's result row."""

    with pytest.raises(RUNTIME.SummaryError, match="frozen accepted classical run"):
        RUNTIME.summarize_run("classical", COMPARE)


@requires_accepted_raw_run
def test_write_and_check_modes_detect_report_drift(tmp_path: Path) -> None:
    """The checked mode compares both outputs byte for byte with raw artifacts."""

    json_output, markdown_output = tmp_path / "result.json", tmp_path / "result.md"
    args = [
        "--compare-dir",
        f"ensemble={COMPARE}",
        "--json-output",
        str(json_output),
        "--markdown-output",
        str(markdown_output),
    ]
    assert RUNTIME.main(args) == 0
    assert RUNTIME.main([*args, "--check"]) == 0
    markdown_output.write_text(markdown_output.read_text(encoding="utf-8") + "drift\n", encoding="utf-8")
    assert RUNTIME.main([*args, "--check"]) == 1


def test_checked_report_contains_all_families_and_is_secret_free() -> None:
    """The compact artifact preserves all six independent pairs without runtime secrets."""

    path = EVALUATION / "reports" / "skill-arena-q040-comparison.json"
    text = path.read_text(encoding="utf-8")
    report = json.loads(text)
    assert report["schema_version"] == RUNTIME.SCHEMA
    assert report["status"] == "pass"
    assert report["family_count"] == 6
    assert [row["family"] for row in report["families"]] == list(
        RUNTIME.SUPPORTED_FAMILIES
    )
    assert {
        row["family"]: (
            row["outcome"]["control_pass_rate"],
            row["outcome"]["treatment_pass_rate"],
            row["outcome"]["treatment_evidence_status"],
        )
        for row in report["families"]
    } == {
        "legacy": (0.0, 0.0, "fail"),
        "embeddings": (1.0, 1.0, "fail"),
        "classical": (1.0, 1.0, "pass"),
        "adaptive": (0.0, 1.0, "pass"),
        "entity-graph": (0.0, 0.0, "pass"),
        "ensemble": (0.0, 1.0, "pass"),
    }
    assert report["aggregate_interpretation"] == {
        "accepted_runs_only": True,
        "paired_result_count": 6,
        "all_treatments_passed": False,
        "all_controls_failed": False,
        "all_treatment_evidence_valid": False,
        "scope": "each family remains a separate one-prompt paired q040 diagnostic",
    }
    forbidden = (
        "appdata\\local\\temp",
        "codex_home",
        "userprofile",
        "authorization",
        "api_key",
        "bearer ",
    )
    assert not any(token in text.casefold() for token in forbidden)


def test_summarizer_contains_no_mcp_runtime_import() -> None:
    """The checked result workflow remains a local artifact read."""

    source = SCRIPT.read_text(encoding="utf-8").casefold()
    forbidden = ("import mcp", "from mcp", "fastmcp", "mcp_server", "mcp-server")
    assert not any(token in source for token in forbidden)
