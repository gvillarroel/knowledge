from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
GENERATOR_PATH = (
    REPO_ROOT
    / "evaluations/semantic-okf-ensemble/scripts/generate_skill_arena_config.py"
)
CHECKED_OUTPUT = REPO_ROOT / "evaluations/semantic-okf-ensemble/skill-arena"


def _load_generator() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "semantic_okf_ensemble_skill_arena_generator", GENERATOR_PATH
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def generator() -> ModuleType:
    return _load_generator()


@pytest.fixture(scope="module")
def generated(generator: ModuleType) -> dict[str, bytes]:
    return generator.build_artifacts(REPO_ROOT)


def _config(generated: dict[str, bytes]) -> dict[str, Any]:
    value = yaml.safe_load(generated["ensemble-hard10.yaml"].decode("utf-8"))
    assert isinstance(value, dict)
    return value


def _json_assignment(script: str, name: str) -> Any:
    match = re.search(rf"^  const {re.escape(name)} = (.+);$", script, re.MULTILINE)
    assert match is not None, f"missing JavaScript assignment {name}"
    return json.loads(match.group(1))


def test_generated_bytes_are_deterministic_and_match_checked_outputs(
    generator: ModuleType, generated: dict[str, bytes]
) -> None:
    replay = generator.build_artifacts(REPO_ROOT)

    assert list(generated) == ["ensemble-hard10.yaml", "prompt-coverage.json"]
    assert replay == generated
    for name, payload in generated.items():
        assert (CHECKED_OUTPUT / name).read_bytes() == payload

    config = _config(generated)
    prompts = config["task"]["prompts"]
    assert len(prompts) == 10
    assert sum(len(prompt["evaluation"]["assertions"]) for prompt in prompts) == 40
    assert all(
        [item["metric"] for item in prompt["evaluation"]["assertions"]]
        == [
            "response-contract",
            "evidence-validity",
            "atomic-answer-completeness",
            "important-negative-coverage",
        ]
        for prompt in prompts
    )


def test_assertion_bindings_and_option_sets_exactly_match_reviewed_ground_truth(
    generator: ModuleType, generated: dict[str, bytes]
) -> None:
    questions = generator._load_reviewed_ground_truth(REPO_ROOT)
    bundle, records = generator._load_claim_records(REPO_ROOT)
    all_allowed = generator._all_claim_bindings(bundle, records)
    contracts = [
        generator._claim_contract(question, bundle, records, all_allowed)
        for question in questions
    ]
    prompts = _config(generated)["task"]["prompts"]
    expected_links: list[str] = []

    for prompt, question, contract in zip(prompts, questions, contracts, strict=True):
        assertions = {
            item["metric"]: item["value"]
            for item in prompt["evaluation"]["assertions"]
        }
        assert prompt["id"] == question["id"]
        assert f"Question: {question['question']}\n" in prompt["prompt"]
        assert _json_assignment(assertions["evidence-validity"], "allowed") == contract[
            "allowed"
        ]
        assert _json_assignment(
            assertions["atomic-answer-completeness"], "requiredPapers"
        ) == question["ground_truth"]["required_paper_ids"]
        assert _json_assignment(
            assertions["atomic-answer-completeness"], "expectedSets"
        ) == [
            sorted(set(item["evidence_claim_ids"]))
            for item in question["ground_truth"]["answer_claims"]
        ]
        assert _json_assignment(
            assertions["important-negative-coverage"], "expectedSets"
        ) == [
            sorted(set(item["evidence_claim_ids"]))
            for item in question["ground_truth"]["important_negatives"]
        ]
        assert contract["allowed"] == all_allowed
        expected_links.extend(
            claim_id
            for family in ("answer_claims", "important_negatives")
            for option in question["ground_truth"][family]
            for claim_id in option["evidence_claim_ids"]
        )
        for option in question["ground_truth"]["answer_claims"]:
            assert option["statement"] not in prompt["prompt"]

    assert sum(len(question["authoritative_evidence"]) for question in questions) == 71
    assert len(expected_links) == 113
    assert len(set(expected_links)) == 68
    assert len(all_allowed) == 831
    reviewed_ground_truth_ids = {
        item["claim_id"]
        for question in questions
        for item in question["authoritative_evidence"]
    }
    assert set(all_allowed) - reviewed_ground_truth_ids


def test_claim_replay_uses_checked_publication_evidence(
    generator: ModuleType,
) -> None:
    bundle, records = generator._load_claim_records(REPO_ROOT)

    assert bundle == (REPO_ROOT / generator.EVIDENCE_BUNDLE_RELATIVE)
    assert bundle != (REPO_ROOT / generator.PINNED_BUNDLE_RELATIVE)
    assert generator._sha256_file(bundle / "semantic/records.jsonl") == (
        generator.EXPECTED_RECORDS_SHA256
    )
    assert len(records) == 831


def test_workspace_runtime_profiles_and_evaluation_options_are_closed(
    generator: ModuleType, generated: dict[str, bytes]
) -> None:
    config = _config(generated)
    assert config["workspace"] == {
        "sources": [
            {
                "id": "semantic-okf-ensemble-final-bundle",
                "type": "local-path",
                "path": generator.PINNED_BUNDLE_RELATIVE.as_posix(),
                "target": "/knowledge",
            },
            {
                "id": "semantic-okf-profile-gated-mcp-runtime",
                "type": "local-path",
                "path": "skills/consult-semantic-okf-ensemble/mcp-runtime",
                "target": "/mcp-runtime",
            },
            {
                "id": "semantic-okf-confirmed-output-publication-runtime",
                "type": "local-path",
                "path": "skills/consult-semantic-okf-ensemble/publication-runtime",
                "target": "/publication-runtime",
            },
        ],
        "setup": {
            "initializeGit": True,
            "env": {
                "HF_HUB_OFFLINE": "1",
                "PYTHONDONTWRITEBYTECODE": "1",
                "SEMANTIC_OKF_BUNDLE": "$WORKSPACE/knowledge",
                "TRANSFORMERS_OFFLINE": "1",
            },
        },
    }
    assert config["evaluation"] == {
        "assertions": [{"type": "is-json", "metric": "response-format"}],
        "requests": 3,
        "timeoutMs": 600000,
        "tracing": False,
        "maxConcurrency": 2,
        "noCache": True,
    }

    profiles = config["comparison"]["profiles"]
    assert [profile["id"] for profile in profiles] == generator.PROFILE_IDS
    assert [profile["output"]["labels"]["causal_role"] for profile in profiles] == [
        "passive-control",
        "active-control",
        "treatment",
    ]
    installed = {
        profile["id"]: [
            skill["source"]["skillId"]
            for skill in profile.get("capabilities", {}).get("skills", [])
        ]
        for profile in profiles
    }
    assert installed == {
        "knowledge-only-control": [],
        "adaptive-consult-control": ["consult-semantic-okf-adaptive"],
        "ensemble-consult-treatment": ["consult-semantic-okf-ensemble"],
    }
    assert [
        profile_id
        for profile_id, skills in installed.items()
        if "consult-semantic-okf-ensemble" in skills
    ] == ["ensemble-consult-treatment"]

    variants = config["comparison"]["variants"]
    assert len(variants) == 1
    agent = variants[0]["agent"]
    assert agent["commandPath"] == r"publication-runtime\run_codex.cmd"
    assert agent["webSearchEnabled"] is False
    assert agent["networkAccessEnabled"] is False
    assert agent["approvalPolicy"] == "never"
    mcp = agent["config"]["mcp_servers"]["semantic_okf"]
    assert mcp == {
        "command": "cmd.exe",
        "args": ["/d", "/c", "mcp-runtime\\run_server.cmd"],
        "env_vars": generator.MCP_ENVIRONMENT,
        "enabled_tools": generator.MCP_TOOLS,
        "startup_timeout_sec": 60,
        "tool_timeout_sec": 600,
    }
    assert "SKILL_ARENA_ALLOWED_SKILLS" in mcp["env_vars"]
    assert "CODEX_HOME" in mcp["env_vars"]
    assert mcp["enabled_tools"][0] == "semantic_okf_bootstrap_skill"


def test_prompt_coverage_is_deterministic_and_exact(
    generator: ModuleType, generated: dict[str, bytes]
) -> None:
    coverage = json.loads(generated["prompt-coverage.json"])
    questions = generator._load_reviewed_ground_truth(REPO_ROOT)

    assert coverage == generator._coverage(questions)
    assert coverage["policy"] == {
        "minimumPrompts": 10,
        "minimumTaskFamilies": 6,
        "maximumPromptWords": 210,
        "maximumPairwiseJaccard": 0.65,
        "requiredCaseKinds": [
            "naturalistic-forward",
            "generalization",
            "boundary-recovery",
        ],
    }
    assert [case["promptId"] for case in coverage["cases"]] == generator.EXPECTED_QUESTION_IDS


def test_check_mode_detects_drift_without_rewriting(
    generator: ModuleType, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    output = tmp_path / "skill-arena"
    common = ["--repo-root", str(REPO_ROOT), "--output-dir", str(output)]

    assert generator.main(common) == 0
    assert generator.main([*common, "--check"]) == 0
    changed = output / "ensemble-hard10.yaml"
    changed.write_bytes(changed.read_bytes() + b"# drift\n")
    drifted = changed.read_bytes()

    assert generator.main([*common, "--check"]) == 2
    assert changed.read_bytes() == drifted
    assert "ensemble-hard10.yaml" in capsys.readouterr().err


def test_reviewed_ground_truth_hash_drift_fails_closed(
    generator: ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(generator, "EXPECTED_GROUND_TRUTH_SHA256", "0" * 64)

    with pytest.raises(generator.ConfigGenerationError, match="ground-truth"):
        generator.build_artifacts(REPO_ROOT)
