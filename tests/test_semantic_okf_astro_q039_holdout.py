"""Focused tests for the frozen q039 ensemble Skill Arena holdout."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType

import pytest
import yaml


REPO = Path(__file__).resolve().parents[1]
GENERATOR = (
    REPO
    / "evaluations"
    / "semantic-okf-astro"
    / "scripts"
    / "generate_q039_ensemble_holdout.py"
)
OUTPUT = REPO / "evaluations" / "semantic-okf-astro" / "skill-arena"
SUMMARIZER = (
    REPO
    / "evaluations"
    / "semantic-okf-astro"
    / "scripts"
    / "summarize_q039_holdout.py"
)
REPORTS = REPO / "evaluations" / "semantic-okf-astro" / "reports"
GENERATION_BUNDLE = (
    REPO
    / "evaluations"
    / "semantic-okf-astro"
    / "results"
    / "runs"
    / "20260716-astro-generic-01"
    / "bundles"
    / "ensemble-a"
)
ACCEPTED_COMPARE = (
    REPO
    / "results"
    / "semantic-okf-astro-q039-ensemble-post-tuning-holdout"
    / "2026-07-16T11-59-44-962Z-compare"
)
HAS_GENERATION_BUNDLE = GENERATION_BUNDLE.is_dir()
HAS_ACCEPTED_RAW_RUN = (
    ACCEPTED_COMPARE.is_dir()
    and (ACCEPTED_COMPARE / "promptfoo-results.json").is_file()
    and HAS_GENERATION_BUNDLE
)
requires_generation_bundle = pytest.mark.skipif(
    not HAS_GENERATION_BUNDLE,
    reason="the accepted append-only generated bundle is intentionally ignored",
)
requires_accepted_raw_run = pytest.mark.skipif(
    not HAS_ACCEPTED_RAW_RUN,
    reason="the accepted append-only Skill Arena run and bundle are intentionally ignored",
)


def _load_generator() -> ModuleType:
    specification = importlib.util.spec_from_file_location(
        "semantic_okf_astro_q039_holdout_generator",
        GENERATOR,
    )
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


def _load_summarizer() -> ModuleType:
    specification = importlib.util.spec_from_file_location(
        "semantic_okf_astro_q039_holdout_summarizer",
        SUMMARIZER,
    )
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def generator() -> ModuleType:
    return _load_generator()


@pytest.fixture(scope="module")
def summarizer() -> ModuleType:
    return _load_summarizer()


@pytest.fixture(scope="module")
def artifacts(generator: ModuleType) -> dict[str, bytes]:
    if HAS_GENERATION_BUNDLE:
        return generator.build_artifacts(REPO)
    return {
        name: (OUTPUT / name).read_bytes()
        for name in (
            "q039-ensemble-holdout.yaml",
            "q039-ensemble-holdout-prompt-coverage.json",
            "q039-ensemble-holdout-manifest.json",
        )
    }


def _config(artifacts: dict[str, bytes]) -> dict[str, object]:
    payload = yaml.safe_load(artifacts["q039-ensemble-holdout.yaml"])
    assert isinstance(payload, dict)
    return payload


@requires_generation_bundle
def test_artifacts_are_deterministic_and_match_checked_outputs(
    generator: ModuleType,
    artifacts: dict[str, bytes],
) -> None:
    """The frozen holdout must be exactly reproducible before any live run."""

    assert list(artifacts) == [
        "q039-ensemble-holdout.yaml",
        "q039-ensemble-holdout-prompt-coverage.json",
        "q039-ensemble-holdout-manifest.json",
    ]
    assert generator.build_artifacts(REPO) == artifacts
    for name, payload in artifacts.items():
        assert (OUTPUT / name).read_bytes() == payload


def test_pair_is_same_bundle_same_model_and_has_only_one_skill_difference(
    artifacts: dict[str, bytes],
) -> None:
    """The treatment changes only the installed ensemble consultation skill."""

    config = _config(artifacts)
    assert config["workspace"]["sources"][0]["id"] == "ensemble-bundle"
    profiles = config["comparison"]["profiles"]
    assert [profile["id"] for profile in profiles] == [
        "knowledge-only-control",
        "ensemble-consult-treatment",
    ]
    assert profiles[0]["capabilities"] == {}
    assert profiles[1]["capabilities"] == {
        "skills": [
            {
                "source": {
                    "type": "local-path",
                    "path": "skills/consult-semantic-okf-ensemble",
                    "skillId": "consult-semantic-okf-ensemble",
                },
                "install": {"strategy": "workspace-overlay"},
            }
        ]
    }
    assert all(profile["isolation"] == {"inheritSystem": False} for profile in profiles)

    variants = config["comparison"]["variants"]
    assert len(variants) == 1
    agent = variants[0]["agent"]
    assert agent["model"] == "openai-codex/gpt-5.6-luna"
    assert agent["sandboxMode"] == "read-only"
    assert agent["approvalPolicy"] == "never"
    assert agent["webSearchEnabled"] is False
    assert agent["config"] == {}
    rendered = json.dumps(config).casefold().replace("no-mcp", "")
    assert "mcp" not in rendered


def test_prompt_covers_declared_facets_without_relevance_or_answer_leakage(
    artifacts: dict[str, bytes],
) -> None:
    """q039 supplies only its natural task facets and a neutral response contract."""

    config = _config(artifacts)
    prompt = config["task"]["prompts"][0]["prompt"]
    for facet in (
        "processed module deduplication",
        "inline scripts (including `is:inline`)",
        "`data-astro-rerun`",
        "lifecycle events",
        "persistent global listeners",
    ):
        assert facet in prompt
    for leaked in (
        "qrels",
        "document_ids",
        "source_ids",
        "astro-doc-",
        "/en/guides/client-side-scripts/",
        "/en/guides/view-transitions/",
        "/en/reference/directives-reference/",
    ):
        assert leaked not in prompt
    assertions = config["task"]["prompts"][0]["evaluation"]["assertions"]
    assert [row["metric"] for row in assertions] == [
        "response-contract",
        "grounded-answer",
    ]
    assert all("expected" not in row["value"].casefold() for row in assertions)


def test_manifest_binds_frozen_inputs_and_forbids_result_inspection(
    generator: ModuleType,
    artifacts: dict[str, bytes],
) -> None:
    """The compact manifest attests the post-tuning boundary and exact artifacts."""

    manifest = json.loads(artifacts["q039-ensemble-holdout-manifest.json"])
    protocol = manifest["holdout_protocol"]
    assert protocol == {
        "frozen_before_live_execution": True,
        "live_evaluation_executed_by_generator": False,
        "mcp_enabled": False,
        "profiles": [
            "knowledge-only-control",
            "ensemble-consult-treatment",
        ],
        "result_inspection_authorized": False,
        "same_bundle": True,
        "same_model": True,
        "skill_changes_authorized": False,
    }
    assert manifest["question"] == {
        "id": "q039",
        "question": generator.EXPECTED_QUESTION,
        "question_type": "hard",
    }
    assert manifest["question_source"]["qrels_in_prompt"] is False
    assert manifest["config"]["sha256"] == hashlib.sha256(
        artifacts["q039-ensemble-holdout.yaml"]
    ).hexdigest()
    assert manifest["prompt"]["coverage_sha256"] == hashlib.sha256(
        artifacts["q039-ensemble-holdout-prompt-coverage.json"]
    ).hexdigest()
    assert (
        manifest["bundle"]["tree_sha256"]
        == generator.EXPECTED_BUNDLE_TREE_SHA256
    )
    assert (
        manifest["treatment_skill"]["tree_sha256"]
        == generator.EXPECTED_SKILL_TREE_SHA256
    )
    assert manifest["runner"]["sha256"] == generator.EXPECTED_RUNNER_SHA256
    assert manifest["prompt"]["sha256"] == generator.EXPECTED_PROMPT_SHA256
    assert manifest["config"]["sha256"] == generator.EXPECTED_CONFIG_SHA256


def test_prompt_coverage_declares_single_post_tuning_boundary_case(
    artifacts: dict[str, bytes],
) -> None:
    """The one-question holdout cannot be mistaken for broad benchmark coverage."""

    coverage = json.loads(
        artifacts["q039-ensemble-holdout-prompt-coverage.json"]
    )
    assert coverage["policy"]["minimumPrompts"] == 1
    assert coverage["policy"]["minimumTaskFamilies"] == 1
    assert coverage["cases"] == [
        {
            "promptId": "q039",
            "caseKind": "boundary-recovery",
            "taskFamily": "client-router-script-lifecycle",
        }
    ]


@requires_generation_bundle
def test_check_mode_detects_drift_without_rewriting(
    generator: ModuleType,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Check mode must be read-only and fail closed on byte drift."""

    output = tmp_path / "skill-arena"
    common = ["--repo-root", str(REPO), "--output-dir", str(output)]
    assert generator.main(common) == 0
    assert generator.main([*common, "--check"]) == 0

    changed = output / "q039-ensemble-holdout.yaml"
    changed.write_bytes(changed.read_bytes() + b"# drift\n")
    drifted = changed.read_bytes()
    assert generator.main([*common, "--check"]) == 2
    assert changed.read_bytes() == drifted
    assert "q039-ensemble-holdout.yaml" in capsys.readouterr().err


@requires_accepted_raw_run
def test_completed_holdout_is_exactly_one_live_pair_with_valid_evidence(
    summarizer: ModuleType,
) -> None:
    """The post-tuning result remains no-regression evidence, not a hidden rerun."""

    report = summarizer.summarize(summarizer.DEFAULT_COMPARE_DIR)
    assert report["accepted_run"] == {
        "run_id": "2026-07-16T11-59-44-962Z-compare",
        "eval_id": "eval-jIy-2026-07-16T11:59:52",
        "benchmark_id": "semantic-okf-astro-q039-ensemble-post-tuning-holdout",
        "question_id": "q039",
        "variant_id": "pi-luna-only",
        "compare_directory": (
            "results/semantic-okf-astro-q039-ensemble-post-tuning-holdout/"
            "2026-07-16T11-59-44-962Z-compare"
        ),
    }
    assert [
        (
            profile["profile_id"],
            profile["pass"],
            profile["latency_ms"],
            profile["evidence_validation"]["status"],
        )
        for profile in report["profiles"]
    ] == [
        ("knowledge-only-control", True, 75842, "pass"),
        ("ensemble-consult-treatment", True, 162166, "pass"),
    ]
    assert report["outcome"]["absolute_percentage_point_delta"] == 0.0
    assert [
        (
            profile["benchmark_evidence_audit"]["required_document_coverage"],
            profile["benchmark_evidence_audit"]["authoritative_evidence_completeness"],
            profile["benchmark_evidence_audit"]["atomic_claim_evidence_completeness"],
            profile["benchmark_evidence_audit"]["important_negative_evidence_completeness"],
        )
        for profile in report["profiles"]
    ] == [(1.0, 1.0, 1.0, 1.0), (2 / 3, 0.75, 0.8, 1.0)]
    assert report["holdout"]["completed_live_evaluations"] == 1
    assert sum(row["completed_live_evaluation"] for row in report["execution_traces"]) == 1
    assert sum("dry-run" in row["classification"] for row in report["execution_traces"]) == 2


@requires_accepted_raw_run
def test_checked_holdout_report_rebuilds_from_ignored_sources(
    summarizer: ModuleType,
) -> None:
    """When retained locally, ignored raw artifacts reproduce the report exactly."""

    assert summarizer.main(["--check"]) == 0


def test_checked_holdout_report_is_secret_free() -> None:
    """The checked compact artifact remains independently inspectable in a clean clone."""

    text = (REPORTS / "skill-arena-q039-holdout.json").read_text(encoding="utf-8")
    report = json.loads(text)
    assert report["schema_version"] == "semantic-okf-astro-q039-holdout-result/1.0"
    assert report["holdout"]["executed_skill_tree_sha256"] == (
        "ab66ade281810abc10ff626d3189d78314f8c939874c3aed86634e1023f8fe19"
    )
    assert [
        profile["benchmark_evidence_audit"]["atomic_claim_evidence_completeness"]
        for profile in report["profiles"]
    ] == [1.0, 0.8]
    assert report["privacy"] == {
        "raw_environment_copied": False,
        "raw_workspace_paths_copied": False,
        "parsed_model_responses_retained_exactly": True,
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


def test_holdout_summarizer_has_no_mcp_runtime_import() -> None:
    """The result audit reads frozen local artifacts only."""

    source = SUMMARIZER.read_text(encoding="utf-8").casefold()
    forbidden = ("import mcp", "from mcp", "fastmcp", "mcp_server", "mcp-server")
    assert not any(token in source for token in forbidden)
