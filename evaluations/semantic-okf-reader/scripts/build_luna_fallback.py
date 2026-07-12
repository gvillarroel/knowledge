#!/usr/bin/env python3
"""Build a Luna-only retry manifest from failed treatment cells."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any

import yaml


EVALUATION_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = EVALUATION_ROOT / "evaluation.yaml"
DEFAULT_OUTPUT = EVALUATION_ROOT / "luna-fallback-evaluation.yaml"
FALLBACK_MODEL = "openrouter/openai/gpt-5.6-luna"


class LiteralDumper(yaml.SafeDumper):
    """Render multiline prompt and JavaScript strings as literal blocks."""


def _represent_string(dumper: LiteralDumper, value: str) -> yaml.ScalarNode:
    style = "|" if "\n" in value else None
    return dumper.represent_scalar("tag:yaml.org,2002:str", value, style=style)


LiteralDumper.add_representer(str, _represent_string)


def load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected YAML object: {path}")
    return value


def load_promptfoo_rows(path: Path) -> list[dict[str, Any]]:
    value = json.loads(path.read_text(encoding="utf-8"))
    rows = value.get("results", {}).get("results", [])
    if not isinstance(rows, list) or not all(isinstance(row, dict) for row in rows):
        raise ValueError(f"invalid Promptfoo results: {path}")
    return rows


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def completed_output(row: dict[str, Any] | None) -> bool:
    """Return whether one model cell produced a gradeable output."""

    if not isinstance(row, dict):
        return False
    response = row.get("response")
    if not isinstance(response, dict) or response.get("error"):
        return False
    output = response.get("output")
    return isinstance(output, str) and bool(output.strip())


def validate_results_binding(
    primary: dict[str, Any],
    rows: list[dict[str, Any]],
    *,
    profile_id: str = "skill",
) -> dict[str, dict[str, Any]]:
    """Require results to match the exact benchmark and prompts being retried."""

    benchmark_id = primary.get("benchmark", {}).get("id")
    prompts = primary.get("task", {}).get("prompts")
    if not isinstance(benchmark_id, str) or not isinstance(prompts, list):
        raise ValueError("primary config is missing its benchmark ID or prompts")

    prompt_by_id = {
        str(prompt.get("id")): prompt for prompt in prompts if isinstance(prompt, dict)
    }
    if len(prompt_by_id) != len(prompts) or "None" in prompt_by_id:
        raise ValueError("primary config contains duplicate or invalid prompt IDs")

    observed: dict[str, dict[str, Any]] = {}
    for row in rows:
        provider = row.get("provider")
        if not isinstance(provider, dict) or provider.get("id") != profile_id:
            continue
        metadata = row.get("metadata")
        if not isinstance(metadata, dict):
            metadata = row.get("testCase", {}).get("metadata", {})
        variables = row.get("vars")
        if not isinstance(variables, dict):
            variables = row.get("testCase", {}).get("vars", {})

        expected_id = metadata.get("promptId")
        if expected_id not in prompt_by_id:
            raise ValueError(f"results contain unknown prompt ID {expected_id!r}")
        if expected_id in observed:
            raise ValueError(f"duplicate `{profile_id}` result cell: {expected_id}")
        prompt = prompt_by_id[str(expected_id)]
        if metadata.get("benchmarkId") != benchmark_id:
            raise ValueError(
                "results/config benchmark mismatch: "
                f"expected {benchmark_id!r}, found {metadata.get('benchmarkId')!r}"
            )
        if metadata.get("profileId", profile_id) != profile_id:
            raise ValueError(f"results/config profile mismatch for {expected_id!r}")
        if variables.get("taskPrompt") != prompt.get("prompt"):
            raise ValueError(
                f"results/config prompt text mismatch for {expected_id!r}; use the exact source manifest"
            )
        observed[str(expected_id)] = row
    if not observed:
        raise ValueError(f"results contain no `{profile_id}` cells")
    missing = [prompt_id for prompt_id in prompt_by_id if prompt_id not in observed]
    if missing:
        raise ValueError(
            f"results are missing {len(missing)} `{profile_id}` cells from the exact source manifest"
        )
    incomplete = [
        prompt_id for prompt_id, row in observed.items() if not completed_output(row)
    ]
    if incomplete:
        sample = ", ".join(incomplete[:5])
        raise ValueError(
            "results contain technically incomplete treatment cells; run the technical "
            f"resume merge before semantic fallback: {sample}"
        )
    return observed


def failed_prompt_ids(
    primary: dict[str, Any],
    rows: list[dict[str, Any]],
    *,
    profile_id: str = "skill",
) -> list[str]:
    """Return unsuccessful but technically complete prompt IDs in manifest order."""

    observed = validate_results_binding(primary, rows, profile_id=profile_id)
    return [
        str(prompt["id"])
        for prompt in primary["task"]["prompts"]
        if observed[str(prompt["id"])].get("success") is not True
    ]


def build_fallback_config(
    primary: dict[str, Any], failed_ids: list[str]
) -> dict[str, Any]:
    """Create a one-profile Luna retry matrix for the selected prompts."""

    prompts = primary.get("task", {}).get("prompts")
    if not isinstance(prompts, list):
        raise ValueError("primary config does not contain task.prompts")
    if not failed_ids:
        raise ValueError("no failed treatment prompts require Luna fallback")
    prompt_by_id = {
        str(prompt.get("id")): prompt for prompt in prompts if isinstance(prompt, dict)
    }
    unknown = sorted(set(failed_ids) - set(prompt_by_id))
    if unknown:
        raise ValueError(f"unknown failed prompt IDs: {', '.join(unknown)}")

    fallback = copy.deepcopy(primary)
    benchmark = fallback["benchmark"]
    benchmark["id"] = "semantic-okf-reader-300-luna-semantic-fallback"
    benchmark["description"] = (
        "Retry failed Semantic OKF treatment cells with PI GPT-5.6 Luna."
    )
    benchmark["tags"] = list(
        dict.fromkeys([*benchmark.get("tags", []), "luna", "semantic-fallback"])
    )
    failed_set = set(failed_ids)
    fallback["task"]["prompts"] = [
        prompt for prompt in prompts if str(prompt.get("id")) in failed_set
    ]

    profiles = fallback.get("comparison", {}).get("profiles", [])
    skill_profiles = [item for item in profiles if item.get("id") == "skill"]
    if len(skill_profiles) != 1:
        raise ValueError("primary config must contain exactly one `skill` profile")
    fallback["comparison"]["profiles"] = skill_profiles
    fallback["comparison"]["variants"] = [
        {
            "id": "pi-openrouter-gpt56-luna-semantic-fallback",
            "description": (
                "PI GPT-5.6 Luna semantic fallback for treatment cells that failed the "
                "initial model route."
            ),
            "agent": {
                "adapter": "pi",
                "model": FALLBACK_MODEL,
                "executionMethod": "command",
                "commandPath": "bin/pi-spark-luna-fallback.ps1",
                "sandboxMode": "read-only",
                "approvalPolicy": "never",
                "webSearchEnabled": False,
                "networkAccessEnabled": True,
                "reasoningEffort": "low",
                "additionalDirectories": [],
                "cliEnv": {
                    "OPENROUTER_API_KEY": "$HOST_ENV:OPENROUTER_API_KEY",
                    "PI_FALLBACK_MODEL": FALLBACK_MODEL,
                    "PI_MODEL_TIMEOUT_SECONDS": "90",
                },
                "config": {},
            },
            "output": {
                "tags": ["pi", "gpt-5.6-luna", "semantic-fallback", "isolated"],
                "labels": {
                    "variantDisplayName": "PI GPT-5.6 Luna fallback",
                    "adapter_family": "pi",
                    "retry_model": FALLBACK_MODEL,
                    "fallback_reason": "failed-complete-treatment-cell",
                },
            },
        }
    ]
    fallback["evaluation"]["maxConcurrency"] = 2
    fallback["evaluation"]["noCache"] = True
    return fallback


def write_fallback_manifest(
    primary_path: Path, results_path: Path, output_path: Path
) -> list[str]:
    primary = load_yaml(primary_path)
    rows = load_promptfoo_rows(results_path)
    failed_ids = failed_prompt_ids(primary, rows)
    fallback = build_fallback_config(primary, failed_ids)
    prompt_ids = [str(item["id"]) for item in fallback["task"]["prompts"]]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        yaml.dump(
            fallback,
            Dumper=LiteralDumper,
            allow_unicode=True,
            sort_keys=False,
            width=120,
        ),
        encoding="utf-8",
    )
    selection = {
        "schema_version": "1.0",
        "origin_benchmark_id": primary["benchmark"]["id"],
        "primary_config": primary_path.resolve().as_posix(),
        "primary_config_sha256": sha256_file(primary_path),
        "primary_results": results_path.resolve().as_posix(),
        "primary_results_sha256": sha256_file(results_path),
        "fallback_config": output_path.resolve().as_posix(),
        "failed_prompt_ids": prompt_ids,
        "failed_prompt_count": len(prompt_ids),
        "failed_cell_state": "technically-complete-assertion-failure",
        "fallback_model": FALLBACK_MODEL,
    }
    output_path.with_suffix(".selection.json").write_text(
        json.dumps(selection, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return prompt_ids


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("results", type=Path, help="Primary Promptfoo results JSON.")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        prompt_ids = write_fallback_manifest(
            args.config.expanduser().resolve(),
            args.results.expanduser().resolve(),
            args.output.expanduser().resolve(),
        )
    except ValueError as exc:
        if str(exc) == "no failed treatment prompts require Luna fallback":
            print("No failed treatment prompts require Luna fallback.")
            return 2
        raise
    print(f"Generated Luna fallback for {len(prompt_ids)} prompts: {', '.join(prompt_ids)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
