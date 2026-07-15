from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
GENERATOR_PATH = (
    REPO_ROOT
    / "evaluations/semantic-okf-ensemble/scripts/"
    "generate_cli_q031_skill_arena_config.py"
)
OUTPUT_DIRECTORY = REPO_ROOT / "evaluations/semantic-okf-ensemble/skill-arena"


def _load_generator() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "semantic_okf_ensemble_cli_q031_skill_arena_generator",
        GENERATOR_PATH,
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
    value = yaml.safe_load(generated["cli-q031.yaml"].decode("utf-8"))
    assert isinstance(value, dict)
    return value


def _walk(value: Any) -> list[Any]:
    values = [value]
    if isinstance(value, dict):
        for key, child in value.items():
            values.extend(_walk(key))
            values.extend(_walk(child))
    elif isinstance(value, list):
        for child in value:
            values.extend(_walk(child))
    return values


def test_generated_artifacts_are_deterministic_and_checked_in(
    generator: ModuleType, generated: dict[str, bytes]
) -> None:
    assert list(generated) == ["cli-q031.yaml", "cli-q031-manifest.json"]
    assert generator.build_artifacts(REPO_ROOT) == generated
    for name, payload in generated.items():
        assert (OUTPUT_DIRECTORY / name).read_bytes() == payload


def test_q031_prompt_and_four_assertions_are_exactly_preserved(
    generated: dict[str, bytes]
) -> None:
    historical = yaml.safe_load(
        (OUTPUT_DIRECTORY / "ensemble-hard10.yaml").read_text(encoding="utf-8")
    )
    expected = next(
        prompt
        for prompt in historical["task"]["prompts"]
        if prompt["id"] == "q031-graph-routing-boundary"
    )
    config = _config(generated)

    assert config["task"]["prompts"] == [expected]
    assertions = config["task"]["prompts"][0]["evaluation"]["assertions"]
    assert len(assertions) == 4
    assert [item["metric"] for item in assertions] == [
        "response-contract",
        "evidence-validity",
        "atomic-answer-completeness",
        "important-negative-coverage",
    ]
    assert config["evaluation"]["assertions"] == [
        {"type": "is-json", "metric": "response-format"}
    ]


def test_compare_is_paired_isolated_and_has_no_mcp_surface(
    generated: dict[str, bytes], generator: ModuleType
) -> None:
    config = _config(generated)
    assert config["benchmark"]["id"] == "semantic-okf-ensemble-cli-q031-paired"
    assert config["evaluation"] == {
        "assertions": [{"type": "is-json", "metric": "response-format"}],
        "requests": 1,
        "timeoutMs": 600000,
        "tracing": False,
        "maxConcurrency": 1,
        "noCache": True,
    }
    profiles = config["comparison"]["profiles"]
    assert [profile["id"] for profile in profiles] == generator.PROFILE_IDS
    assert all(profile["isolation"] == {"inheritSystem": False} for profile in profiles)
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
    assert not any(
        isinstance(item, str) and "mcp" in item.casefold() for item in _walk(config)
    )


def test_workspace_runner_and_pi_contract_are_closed(
    generated: dict[str, bytes]
) -> None:
    config = _config(generated)
    assert config["workspace"] == {
        "sources": [
            {
                "id": "semantic-okf-ensemble-final-workspace",
                "type": "local-path",
                "path": (
                    "evaluations/semantic-okf-ensemble/results/runs/"
                    "20260715-ensemble-final-03/workspace-a"
                ),
                "target": "/",
            },
            {
                "id": "pi-luna-runner-only",
                "type": "local-path",
                "path": (
                    "evaluations/semantic-okf-adaptive/results/runs/"
                    "20260714-adaptive-final-05/workspaces/arena/bin"
                ),
                "target": "/bin",
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
    agent = config["comparison"]["variants"][0]["agent"]
    assert agent == {
        "adapter": "pi",
        "model": "openai-codex/gpt-5.6-luna",
        "executionMethod": "command",
        "commandPath": "bin/pi-luna.ps1",
        "sandboxMode": "read-only",
        "approvalPolicy": "never",
        "webSearchEnabled": False,
        "networkAccessEnabled": True,
        "reasoningEffort": "medium",
        "additionalDirectories": [],
        "cliEnv": {"PI_MODEL_TIMEOUT_SECONDS": "600"},
        "envPassthrough": [
            "SEMANTIC_OKF_PYTHON",
            "SEMANTIC_OKF_HF_HUB_CACHE",
        ],
        "config": {},
    }


def test_manifest_binds_config_sources_skill_and_mcp_free_status(
    generator: ModuleType, generated: dict[str, bytes]
) -> None:
    manifest = json.loads(generated["cli-q031-manifest.json"])
    config_sha256 = generator._sha256_bytes(generated["cli-q031.yaml"])

    assert manifest["benchmark_id"] == generator.BENCHMARK_ID
    assert manifest["config"]["sha256"] == config_sha256
    assert manifest["prompt"]["id"] == generator.PROMPT_ID
    assert manifest["prompt"]["source_config_sha256"] == (
        generator.EXPECTED_HISTORICAL_CONFIG_SHA256
    )
    assert manifest["runtime_contract"] == {
        "consult_transport": "bounded-cli",
        "mcp_agent_config": False,
        "mcp_capabilities": 0,
        "mcp_free": True,
        "mcp_sources": 0,
        "network_access_enabled": True,
        "offline_knowledge_environment": True,
        "read_only": True,
        "required_host_environment_variables": [
            "SEMANTIC_OKF_PYTHON",
            "SEMANTIC_OKF_HF_HUB_CACHE",
        ],
        "web_search_enabled": False,
    }
    sources = {item["id"]: item for item in manifest["workspace_sources"]}
    assert sources["pi-luna-runner-only"]["role"] == "runner-only-not-knowledge"
    assert sources["semantic-okf-ensemble-final-workspace"]["file_count"] > 800
    assert manifest["treatment_skill"]["skill_md_sha256"] == generator._sha256_file(
        REPO_ROOT / "skills/consult-semantic-okf-ensemble/SKILL.md"
    )
    assert manifest["generator"]["sha256"] == generator._sha256_file(GENERATOR_PATH)


def test_check_mode_detects_drift_without_rewriting(
    generator: ModuleType, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    output = tmp_path / "skill-arena"
    common = ["--repo-root", str(REPO_ROOT), "--output-dir", str(output)]

    assert generator.main(common) == 0
    assert generator.main([*common, "--check"]) == 0
    changed = output / "cli-q031.yaml"
    changed.write_bytes(changed.read_bytes() + b"# drift\n")
    drifted = changed.read_bytes()

    assert generator.main([*common, "--check"]) == 2
    assert changed.read_bytes() == drifted
    assert "cli-q031.yaml" in capsys.readouterr().err
