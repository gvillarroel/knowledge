#!/usr/bin/env python3
"""Generate the isolated, MCP-free definitive-consult q031 comparison."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any, Mapping, Sequence

import yaml


REPO_ROOT = Path(__file__).resolve().parents[3]
HISTORICAL_CONFIG_RELATIVE = Path(
    "evaluations/semantic-okf-ensemble/skill-arena/ensemble-hard10.yaml"
)
OUTPUT_CONFIG_RELATIVE = Path(
    "evaluations/semantic-okf-ensemble/skill-arena/cli-q031.yaml"
)
OUTPUT_MANIFEST_RELATIVE = Path(
    "evaluations/semantic-okf-ensemble/skill-arena/cli-q031-manifest.json"
)
WORKSPACE_RELATIVE = Path(
    "evaluations/semantic-okf-ensemble/results/runs/"
    "20260715-ensemble-final-03/workspace-a"
)
RUNNER_RELATIVE = Path(
    "evaluations/semantic-okf-adaptive/results/runs/"
    "20260714-adaptive-final-05/workspaces/arena/bin"
)
SKILL_RELATIVE = Path("skills/consult-semantic-okf-ensemble")
GENERATOR_RELATIVE = Path(
    "evaluations/semantic-okf-ensemble/scripts/"
    "generate_cli_q031_skill_arena_config.py"
)
RUNTIME_BINDINGS_RELATIVE = Path(
    "evaluations/semantic-okf-ensemble/fixtures/historical-runtime-bindings.json"
)

EXPECTED_HISTORICAL_CONFIG_SHA256 = (
    "5042a9dae24bdac352ddf1c1f7482a5fe9cf76b0b771ae6d606a514eff5ad4ac"
)
EXPECTED_RUNTIME_BINDINGS_SHA256 = "6b16c239fcdf89cc40653321cc100ba6335812ad4ece498ce524e4c765506abc"
BENCHMARK_ID = "semantic-okf-ensemble-cli-q031-paired"
PROMPT_ID = "q031-graph-routing-boundary"
PROFILE_IDS = ["knowledge-only-control", "ensemble-cli-consult-treatment"]
TREE_HASH_ALGORITHM = (
    "SHA-256 over sorted source-relative-path NUL file-SHA-256 newline rows; "
    "__pycache__ directories and .pyc files excluded"
)


class ConfigGenerationError(RuntimeError):
    """Describe a fail-closed q031 config generation violation."""


class LiteralString(str):
    """A YAML scalar rendered as a literal block."""


class Dumper(yaml.SafeDumper):
    """Stable YAML emitter compatible with Skill Arena's V1 parser."""

    def increase_indent(self, flow: bool = False, indentless: bool = False) -> Any:
        return super().increase_indent(flow, False)


def _represent_literal(dumper: Dumper, value: LiteralString) -> yaml.ScalarNode:
    return dumper.represent_scalar("tag:yaml.org,2002:str", value, style="|")


Dumper.add_representer(LiteralString, _represent_literal)


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _regular_file(path: Path, label: str) -> Path:
    if path.is_symlink():
        raise ConfigGenerationError(f"{label} must be a regular non-link file")
    try:
        resolved = path.resolve(strict=True)
    except OSError as exc:
        raise ConfigGenerationError(f"cannot resolve {label}: {exc}") from exc
    if not resolved.is_file():
        raise ConfigGenerationError(f"{label} must be a regular non-link file")
    return resolved


def _regular_directory(path: Path, label: str) -> Path:
    if path.is_symlink():
        raise ConfigGenerationError(f"{label} must be a regular non-link directory")
    try:
        resolved = path.resolve(strict=True)
    except OSError as exc:
        raise ConfigGenerationError(f"cannot resolve {label}: {exc}") from exc
    if not resolved.is_dir():
        raise ConfigGenerationError(f"{label} must be a regular non-link directory")
    return resolved


def _tree_binding(root: Path, label: str) -> dict[str, Any]:
    resolved = _regular_directory(root, label)
    rows: list[bytes] = []
    file_count = 0
    byte_count = 0
    for path in sorted(resolved.rglob("*"), key=lambda item: item.relative_to(resolved).as_posix()):
        relative = path.relative_to(resolved)
        if "__pycache__" in relative.parts or path.suffix == ".pyc":
            continue
        if path.is_symlink():
            raise ConfigGenerationError(f"{label} contains a symbolic link: {relative.as_posix()}")
        if path.is_dir():
            continue
        if not path.is_file():
            raise ConfigGenerationError(f"{label} contains a non-regular entry: {relative.as_posix()}")
        payload = path.read_bytes()
        rows.append(
            relative.as_posix().encode("utf-8")
            + b"\0"
            + _sha256_bytes(payload).encode("ascii")
            + b"\n"
        )
        file_count += 1
        byte_count += len(payload)
    if file_count == 0:
        raise ConfigGenerationError(f"{label} must contain at least one file")
    return {
        "tree_sha256": _sha256_bytes(b"".join(rows)),
        "file_count": file_count,
        "byte_count": byte_count,
    }


def _historical_runtime_bindings(repo_root: Path) -> dict[str, dict[str, Any]]:
    """Load immutable metadata for historical sources that are intentionally ignored."""

    path = _regular_file(
        repo_root / RUNTIME_BINDINGS_RELATIVE,
        "historical runtime binding fixture",
    )
    if _sha256_file(path) != EXPECTED_RUNTIME_BINDINGS_SHA256:
        raise ConfigGenerationError("historical runtime binding fixture drifted")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ConfigGenerationError(
            f"cannot read historical runtime binding fixture: {exc}"
        ) from exc
    if not isinstance(payload, dict) or set(payload) != {
        "schema_version",
        "run_id",
        "workspace",
        "runner",
    }:
        raise ConfigGenerationError("historical runtime binding fixture schema differs")
    if (
        payload["schema_version"]
        != "semantic-okf-ensemble-historical-runtime-bindings/1.0"
        or payload["run_id"] != "20260715-ensemble-final-03"
    ):
        raise ConfigGenerationError("historical runtime binding fixture identity differs")
    expected = {
        "workspace": (WORKSPACE_RELATIVE, {"path", "file_count", "byte_count", "tree_sha256"}),
        "runner": (
            RUNNER_RELATIVE,
            {"path", "file_count", "byte_count", "tree_sha256", "runner_sha256"},
        ),
    }
    result: dict[str, dict[str, Any]] = {}
    for name, (expected_path, keys) in expected.items():
        binding = payload[name]
        if not isinstance(binding, dict) or set(binding) != keys:
            raise ConfigGenerationError(f"historical {name} binding schema differs")
        if binding["path"] != expected_path.as_posix():
            raise ConfigGenerationError(f"historical {name} binding path differs")
        if any(
            isinstance(binding[key], bool)
            or not isinstance(binding[key], int)
            or binding[key] < 1
            for key in ("file_count", "byte_count")
        ):
            raise ConfigGenerationError(f"historical {name} binding counts differ")
        digest_keys = {"tree_sha256"} | ({"runner_sha256"} if name == "runner" else set())
        if any(
            not isinstance(binding[key], str)
            or len(binding[key]) != 64
            or any(character not in "0123456789abcdef" for character in binding[key])
            for key in digest_keys
        ):
            raise ConfigGenerationError(f"historical {name} binding digest differs")
        result[name] = dict(binding)
    return result


def _historical_prompt(repo_root: Path) -> tuple[dict[str, Any], str]:
    path = _regular_file(
        repo_root / HISTORICAL_CONFIG_RELATIVE,
        "historical ensemble Skill Arena config",
    )
    observed_sha256 = _sha256_file(path)
    if observed_sha256 != EXPECTED_HISTORICAL_CONFIG_SHA256:
        raise ConfigGenerationError(
            "historical ensemble Skill Arena config drifted; q031 must remain frozen"
        )
    try:
        config = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (UnicodeError, yaml.YAMLError) as exc:
        raise ConfigGenerationError(f"cannot parse historical Skill Arena config: {exc}") from exc
    prompts = config.get("task", {}).get("prompts") if isinstance(config, Mapping) else None
    if not isinstance(prompts, list):
        raise ConfigGenerationError("historical Skill Arena prompts are missing")
    matches = [item for item in prompts if isinstance(item, dict) and item.get("id") == PROMPT_ID]
    if len(matches) != 1:
        raise ConfigGenerationError("historical Skill Arena q031 prompt must be unique")
    prompt = matches[0]
    assertions = prompt.get("evaluation", {}).get("assertions")
    if (
        not isinstance(assertions, list)
        or len(assertions) != 4
        or any(item.get("type") != "javascript" for item in assertions)
        or [item.get("metric") for item in assertions]
        != [
            "response-contract",
            "evidence-validity",
            "atomic-answer-completeness",
            "important-negative-coverage",
        ]
    ):
        raise ConfigGenerationError("historical q031 must contain its four reviewed assertions")
    return prompt, observed_sha256


def _literal_prompt(prompt: Mapping[str, Any]) -> dict[str, Any]:
    assertions = prompt["evaluation"]["assertions"]
    return {
        "id": prompt["id"],
        "description": prompt["description"],
        "prompt": LiteralString(prompt["prompt"]),
        "evaluation": {
            "assertions": [
                {
                    "type": item["type"],
                    "metric": item["metric"],
                    "value": LiteralString(item["value"]),
                }
                for item in assertions
            ]
        },
    }


def _config(prompt: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": 1,
        "benchmark": {
            "id": BENCHMARK_ID,
            "description": (
                "Paired isolated comparison of knowledge-only and current definitive "
                "CLI consultation on the frozen q031 hard question."
            ),
            "tags": [
                "compare",
                "semantic-okf",
                "hard-question",
                "isolated",
                "paired",
                "ensemble",
                "cli",
            ],
        },
        "task": {"prompts": [_literal_prompt(prompt)]},
        "workspace": {
            "sources": [
                {
                    "id": "semantic-okf-ensemble-final-workspace",
                    "type": "local-path",
                    "path": WORKSPACE_RELATIVE.as_posix(),
                    "target": "/",
                },
                {
                    "id": "pi-luna-runner-only",
                    "type": "local-path",
                    "path": RUNNER_RELATIVE.as_posix(),
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
        },
        "evaluation": {
            "assertions": [{"type": "is-json", "metric": "response-format"}],
            "requests": 1,
            "timeoutMs": 600000,
            "tracing": False,
            "maxConcurrency": 1,
            "noCache": True,
        },
        "comparison": {
            "profiles": [
                {
                    "id": "knowledge-only-control",
                    "description": (
                        "Isolated control with the pinned definitive bundle and no "
                        "declared consult skill."
                    ),
                    "isolation": {"inheritSystem": False},
                    "capabilities": {},
                    "output": {
                        "tags": ["control", "knowledge-only", "knowledge-on"],
                        "labels": {
                            "capability": "none",
                            "bundle_kind": "ensemble-derived",
                            "causal_role": "passive-control",
                        },
                    },
                },
                {
                    "id": "ensemble-cli-consult-treatment",
                    "description": (
                        "Isolated treatment with only the current definitive CLI "
                        "consultation skill over the same pinned bundle."
                    ),
                    "isolation": {"inheritSystem": False},
                    "capabilities": {
                        "skills": [
                            {
                                "source": {
                                    "type": "local-path",
                                    "path": SKILL_RELATIVE.as_posix(),
                                    "skillId": "consult-semantic-okf-ensemble",
                                },
                                "install": {"strategy": "workspace-overlay"},
                            }
                        ]
                    },
                    "output": {
                        "tags": ["treatment", "ensemble", "knowledge-on", "cli"],
                        "labels": {
                            "capability": "consult-semantic-okf-ensemble",
                            "bundle_kind": "ensemble-derived",
                            "causal_role": "treatment",
                        },
                    },
                },
            ],
            "variants": [
                {
                    "id": "pi-luna-only",
                    "description": (
                        "PI with the same GPT-5.6 Luna route for both isolated answer "
                        "requests."
                    ),
                    "agent": {
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
                    },
                    "output": {
                        "tags": ["pi", "gpt-5.6-luna", "isolated", "cli"],
                        "labels": {"variantDisplayName": "PI GPT-5.6 Luna"},
                    },
                }
            ],
        },
    }


def _walk_values(value: Any) -> list[Any]:
    values = [value]
    if isinstance(value, Mapping):
        for key, child in value.items():
            values.extend(_walk_values(key))
            values.extend(_walk_values(child))
    elif isinstance(value, list):
        for child in value:
            values.extend(_walk_values(child))
    return values


def _validate_config(config: Mapping[str, Any], historical_prompt: Mapping[str, Any]) -> None:
    if set(config) != {
        "schemaVersion",
        "benchmark",
        "task",
        "workspace",
        "evaluation",
        "comparison",
    }:
        raise ConfigGenerationError("generated config top-level schema differs")
    if config["benchmark"]["id"] != BENCHMARK_ID:
        raise ConfigGenerationError("generated benchmark identity differs")
    prompts = config["task"]["prompts"]
    if len(prompts) != 1 or prompts[0] != historical_prompt:
        raise ConfigGenerationError("generated q031 prompt or assertions differ from history")
    if config["evaluation"] != {
        "assertions": [{"type": "is-json", "metric": "response-format"}],
        "requests": 1,
        "timeoutMs": 600000,
        "tracing": False,
        "maxConcurrency": 1,
        "noCache": True,
    }:
        raise ConfigGenerationError("generated evaluation options differ")
    profiles = config["comparison"]["profiles"]
    if [profile.get("id") for profile in profiles] != PROFILE_IDS:
        raise ConfigGenerationError("generated profile identities differ")
    if any(profile.get("isolation") != {"inheritSystem": False} for profile in profiles):
        raise ConfigGenerationError("generated profiles must not inherit system skills")
    agent = config["comparison"]["variants"][0]["agent"]
    if agent.get("adapter") != "pi" or agent.get("config") != {}:
        raise ConfigGenerationError("generated PI agent options differ")
    for item in _walk_values(config):
        if isinstance(item, str) and "mcp" in item.casefold():
            raise ConfigGenerationError("generated config must not declare or mention MCP")


def _manifest(
    repo_root: Path,
    config_bytes: bytes,
    historical_sha256: str,
    historical_prompt: Mapping[str, Any],
) -> dict[str, Any]:
    historical = _historical_runtime_bindings(repo_root)
    workspace = historical["workspace"]
    runner = historical["runner"]
    skill = _tree_binding(repo_root / SKILL_RELATIVE, "definitive consult skill")
    skill_file = _regular_file(repo_root / SKILL_RELATIVE / "SKILL.md", "definitive SKILL.md")
    generator_file = _regular_file(repo_root / GENERATOR_RELATIVE, "q031 config generator")
    prompt_bytes = str(historical_prompt["prompt"]).encode("utf-8")
    assertions_bytes = json.dumps(
        historical_prompt["evaluation"]["assertions"],
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return {
        "schema_version": "semantic-okf-ensemble-cli-q031-config-manifest/1.0",
        "status": "generated",
        "benchmark_id": BENCHMARK_ID,
        "config": {
            "path": OUTPUT_CONFIG_RELATIVE.as_posix(),
            "sha256": _sha256_bytes(config_bytes),
            "profile_ids": PROFILE_IDS,
            "variant_id": "pi-luna-only",
            "gate_count": 5,
        },
        "prompt": {
            "id": PROMPT_ID,
            "source_config_path": HISTORICAL_CONFIG_RELATIVE.as_posix(),
            "source_config_sha256": historical_sha256,
            "prompt_sha256": _sha256_bytes(prompt_bytes),
            "assertions_sha256": _sha256_bytes(assertions_bytes),
            "per_prompt_assertion_count": 4,
        },
        "workspace_sources": [
            {
                "id": "semantic-okf-ensemble-final-workspace",
                "path": WORKSPACE_RELATIVE.as_posix(),
                "target": "/",
                "role": "pinned-knowledge-workspace",
                "tree_sha256": workspace["tree_sha256"],
                "file_count": workspace["file_count"],
                "byte_count": workspace["byte_count"],
            },
            {
                "id": "pi-luna-runner-only",
                "path": RUNNER_RELATIVE.as_posix(),
                "target": "/bin",
                "role": "runner-only-not-knowledge",
                "tree_sha256": runner["tree_sha256"],
                "file_count": runner["file_count"],
                "byte_count": runner["byte_count"],
                "runner_sha256": runner["runner_sha256"],
            },
        ],
        "treatment_skill": {
            "skill_id": "consult-semantic-okf-ensemble",
            "path": SKILL_RELATIVE.as_posix(),
            **skill,
            "skill_md_sha256": _sha256_file(skill_file),
        },
        "runtime_contract": {
            "mcp_free": True,
            "mcp_sources": 0,
            "mcp_capabilities": 0,
            "mcp_agent_config": False,
            "consult_transport": "bounded-cli",
            "read_only": True,
            "web_search_enabled": False,
            "network_access_enabled": True,
            "offline_knowledge_environment": True,
            "required_host_environment_variables": [
                "SEMANTIC_OKF_PYTHON",
                "SEMANTIC_OKF_HF_HUB_CACHE",
            ],
        },
        "generator": {
            "path": GENERATOR_RELATIVE.as_posix(),
            "sha256": _sha256_file(generator_file),
            "deterministic": True,
            "check_mode": True,
        },
        "tree_hash_algorithm": TREE_HASH_ALGORITHM,
    }


def build_artifacts(repo_root: Path = REPO_ROOT) -> dict[str, bytes]:
    """Build and internally validate deterministic config and manifest bytes."""

    root = repo_root.resolve(strict=True)
    historical_prompt, historical_sha256 = _historical_prompt(root)
    config = _config(historical_prompt)
    _validate_config(config, historical_prompt)
    config_text = yaml.dump(
        config,
        Dumper=Dumper,
        allow_unicode=True,
        sort_keys=False,
        width=4096,
    )
    config_bytes = config_text.encode("utf-8")
    manifest = _manifest(root, config_bytes, historical_sha256, historical_prompt)
    manifest_bytes = (
        json.dumps(manifest, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    ).encode("utf-8")
    return {
        OUTPUT_CONFIG_RELATIVE.name: config_bytes,
        OUTPUT_MANIFEST_RELATIVE.name: manifest_bytes,
    }


def _write_atomic(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and (not path.is_file() or path.is_symlink()):
        raise ConfigGenerationError(f"output must be a regular non-link file: {path}")
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as stream:
            temporary = Path(stream.name)
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        temporary = None
    except OSError as exc:
        raise ConfigGenerationError(f"cannot publish {path}: {exc}") from exc
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=OUTPUT_CONFIG_RELATIVE.parent,
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fail if checked outputs differ; never modify files.",
    )
    return parser.parse_args(list(argv))


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    try:
        repo_root = args.repo_root.resolve(strict=True)
        output_dir = (
            args.output_dir.resolve()
            if args.output_dir.is_absolute()
            else (repo_root / args.output_dir).resolve()
        )
        outputs = build_artifacts(repo_root)
        changed: list[str] = []
        for name, payload in outputs.items():
            path = output_dir / name
            if args.check:
                try:
                    current = _regular_file(path, f"checked output {name}").read_bytes()
                except ConfigGenerationError:
                    changed.append(name)
                    continue
                if current != payload:
                    changed.append(name)
            else:
                _write_atomic(path, payload)
        if changed:
            print(
                "error: generated CLI q031 Skill Arena outputs drifted: "
                + ", ".join(changed),
                file=sys.stderr,
            )
            return 2
        print(
            json.dumps(
                {
                    "status": "pass",
                    "mode": "check" if args.check else "write",
                    "benchmark_id": BENCHMARK_ID,
                    "outputs": [
                        {
                            "path": (output_dir / name).as_posix(),
                            "sha256": _sha256_bytes(payload),
                        }
                        for name, payload in outputs.items()
                    ],
                },
                ensure_ascii=False,
                separators=(",", ":"),
            )
        )
        return 0
    except (ConfigGenerationError, OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
