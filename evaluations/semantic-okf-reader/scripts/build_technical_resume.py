#!/usr/bin/env python3
"""Build a Luna resume manifest for technically incomplete comparison cells."""

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
DEFAULT_OUTPUT = EVALUATION_ROOT / "technical-resume-evaluation.yaml"
RESUME_MODEL = "openrouter/openai/gpt-5.6-luna"


class LiteralDumper(yaml.SafeDumper):
    """Render multiline prompts and assertions as literal blocks."""


def _represent_string(dumper: LiteralDumper, value: str) -> yaml.ScalarNode:
    return dumper.represent_scalar(
        "tag:yaml.org,2002:str", value, style="|" if "\n" in value else None
    )


LiteralDumper.add_representer(str, _represent_string)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected YAML object: {path}")
    return value


def load_rows(path: Path) -> list[dict[str, Any]]:
    value = json.loads(path.read_text(encoding="utf-8"))
    rows = value.get("results", {}).get("results", [])
    if not isinstance(rows, list) or not all(isinstance(row, dict) for row in rows):
        raise ValueError(f"invalid Promptfoo results: {path}")
    return rows


def completed_output(row: dict[str, Any] | None) -> bool:
    """Return whether one model cell produced a gradeable output."""

    if not isinstance(row, dict):
        return False
    response = row.get("response")
    if not isinstance(response, dict) or response.get("error"):
        return False
    output = response.get("output")
    return isinstance(output, str) and bool(output.strip())


def technical_error_prompt_ids(
    primary: dict[str, Any],
    rows: list[dict[str, Any]],
    *,
    selected_profile_ids: list[str] | None = None,
) -> tuple[list[str], list[str]]:
    """Return the shared technical-error prompt list and profile IDs."""

    benchmark_id = primary.get("benchmark", {}).get("id")
    prompts = primary.get("task", {}).get("prompts")
    profiles = primary.get("comparison", {}).get("profiles")
    variants = primary.get("comparison", {}).get("variants")
    if not isinstance(benchmark_id, str) or not isinstance(prompts, list):
        raise ValueError("primary config is missing its benchmark ID or prompts")
    if not isinstance(profiles, list) or not isinstance(variants, list):
        raise ValueError("primary config is missing profiles or variants")
    all_profile_ids = [item.get("id") for item in profiles]
    variant_ids = [item.get("id") for item in variants]
    if not all_profile_ids or not all(
        isinstance(item, str) for item in all_profile_ids
    ):
        raise ValueError("primary config contains invalid profile IDs")
    profile_ids = list(all_profile_ids)
    if selected_profile_ids is not None:
        unknown = sorted(set(selected_profile_ids) - set(all_profile_ids))
        if unknown:
            raise ValueError(f"unknown selected profiles: {', '.join(unknown)}")
        profile_ids = [item for item in profile_ids if item in selected_profile_ids]
        if not profile_ids:
            raise ValueError("at least one profile must be selected")
    if len(variant_ids) != 1 or not isinstance(variant_ids[0], str):
        raise ValueError("technical resume currently requires exactly one variant")

    prompt_by_id = {item.get("id"): item for item in prompts if isinstance(item, dict)}
    if len(prompt_by_id) != len(prompts) or not all(
        isinstance(item, str) for item in prompt_by_id
    ):
        raise ValueError("primary config contains duplicate or invalid prompt IDs")

    row_by_key: dict[tuple[str, str, str], dict[str, Any]] = {}
    for row in rows:
        metadata = row.get("metadata")
        provider = row.get("provider")
        variables = row.get("vars")
        if not isinstance(metadata, dict) or not isinstance(provider, dict):
            raise ValueError("result row is missing provider or metadata")
        if not isinstance(variables, dict):
            variables = row.get("testCase", {}).get("vars", {})
        prompt_id = metadata.get("promptId")
        profile_id = metadata.get("profileId")
        variant_id = metadata.get("variantId")
        if metadata.get("benchmarkId") != benchmark_id:
            raise ValueError("results were not produced by the configured benchmark")
        if prompt_id not in prompt_by_id:
            raise ValueError(f"unknown result prompt ID: {prompt_id!r}")
        if profile_id not in all_profile_ids or provider.get("id") != profile_id:
            raise ValueError(f"invalid result profile binding for {prompt_id!r}")
        if variant_id not in variant_ids:
            raise ValueError(f"invalid result variant binding for {prompt_id!r}")
        if variables.get("taskPrompt") != prompt_by_id[prompt_id].get("prompt"):
            raise ValueError(f"result prompt text mismatch for {prompt_id!r}")
        key = (str(prompt_id), str(profile_id), str(variant_id))
        if key in row_by_key:
            raise ValueError(f"duplicate result cell: {key}")
        row_by_key[key] = row

    variant_id = str(variant_ids[0])
    errors_by_profile: dict[str, list[str]] = {}
    for profile_id in profile_ids:
        errors_by_profile[str(profile_id)] = [
            str(prompt["id"])
            for prompt in prompts
            if not completed_output(
                row_by_key.get((str(prompt["id"]), str(profile_id), variant_id))
            )
        ]
    error_sets = {tuple(items) for items in errors_by_profile.values()}
    if len(error_sets) != 1:
        details = ", ".join(
            f"{profile}={len(items)}" for profile, items in errors_by_profile.items()
        )
        raise ValueError(
            "technical error masks differ by profile; partitioned manifests are required: "
            + details
        )
    return list(next(iter(error_sets))), [str(item) for item in profile_ids]


def build_resume_config(
    primary: dict[str, Any],
    prompt_ids: list[str],
    *,
    profile_ids: list[str] | None = None,
) -> dict[str, Any]:
    """Create one two-profile Luna manifest for the shared missing prompt mask."""

    if not prompt_ids:
        raise ValueError("no technical errors require a resume run")
    resume = copy.deepcopy(primary)
    prompt_by_id = {item["id"]: item for item in primary["task"]["prompts"]}
    source_benchmark_id = str(primary["benchmark"]["id"])
    resume["benchmark"]["id"] = (
        source_benchmark_id + "-retry"
        if "technical-resume" in source_benchmark_id
        else "semantic-okf-reader-300-technical-resume"
    )
    resume["benchmark"]["description"] = (
        "Resume technically incomplete Semantic OKF cells with PI GPT-5.6 Luna "
        "through a separately authenticated OpenRouter provider route."
    )
    resume["benchmark"]["tags"] = list(
        dict.fromkeys(
            [
                *resume["benchmark"].get("tags", []),
                "technical-resume",
                "luna",
            ]
        )
    )
    resume["task"]["prompts"] = [prompt_by_id[item] for item in prompt_ids]
    if profile_ids is not None:
        resume["comparison"]["profiles"] = [
            item
            for item in resume["comparison"]["profiles"]
            if item.get("id") in profile_ids
        ]
    resume["comparison"]["variants"] = [
        {
            "id": "pi-openai-gpt56-luna-technical-resume",
            "description": (
                "PI GPT-5.6 Luna technical resume after the original Codex route "
                "exhausted its shared usage limit."
            ),
            "agent": {
                "adapter": "pi",
                "model": RESUME_MODEL,
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
                    "PI_FALLBACK_MODEL": RESUME_MODEL,
                    "PI_MODEL_TIMEOUT_SECONDS": "90",
                },
                "config": {},
            },
            "output": {
                "tags": ["pi", "gpt-5.6-luna", "technical-resume", "isolated"],
                "labels": {
                    "variantDisplayName": "PI GPT-5.6 Luna technical resume",
                    "adapter_family": "pi",
                    "resume_model": RESUME_MODEL,
                    "resume_reason": "shared-codex-usage-limit",
                },
            },
        }
    ]
    resume["evaluation"]["maxConcurrency"] = 2
    resume["evaluation"]["noCache"] = True
    return resume


def write_resume_manifest(
    primary_path: Path,
    results_path: Path,
    output_path: Path,
    *,
    limit: int | None = None,
    profile_ids: list[str] | None = None,
) -> list[str]:
    primary = load_yaml(primary_path)
    rows = load_rows(results_path)
    all_prompt_ids, selected_profiles = technical_error_prompt_ids(
        primary, rows, selected_profile_ids=profile_ids
    )
    prompt_ids = all_prompt_ids[:limit] if limit is not None else all_prompt_ids
    resume = build_resume_config(
        primary, prompt_ids, profile_ids=selected_profiles
    )
    if limit is not None:
        resume["benchmark"]["id"] += "-preflight"
        resume["benchmark"]["description"] = (
            "Limited preflight for the Semantic OKF technical resume route."
        )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        yaml.dump(
            resume,
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
        "resume_benchmark_id": resume["benchmark"]["id"],
        "primary_config": primary_path.resolve().as_posix(),
        "primary_config_sha256": sha256_file(primary_path),
        "primary_results": results_path.resolve().as_posix(),
        "primary_results_sha256": sha256_file(results_path),
        "resume_config": output_path.resolve().as_posix(),
        "profile_ids": selected_profiles,
        "technical_error_prompt_ids": prompt_ids,
        "technical_error_prompt_count": len(prompt_ids),
        "technical_error_cell_count": len(prompt_ids) * len(selected_profiles),
        "source_technical_error_prompt_count": len(all_prompt_ids),
        "selection_limit": limit,
        "resume_model": RESUME_MODEL,
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
    parser.add_argument("--limit", type=int, help="Select only the first N errors for a preflight run.")
    parser.add_argument(
        "--profile",
        action="append",
        dest="profile_ids",
        help="Select one profile with technical errors; repeat to select several.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.limit is not None and args.limit < 1:
        raise ValueError("--limit must be positive")
    try:
        prompt_ids = write_resume_manifest(
            args.config.expanduser().resolve(),
            args.results.expanduser().resolve(),
            args.output.expanduser().resolve(),
            limit=args.limit,
            profile_ids=args.profile_ids,
        )
    except ValueError as exc:
        if str(exc) == "no technical errors require a resume run":
            print("No technical errors require a resume run.")
            return 2
        raise
    print(
        f"Generated technical resume for {len(prompt_ids)} prompts: "
        f"{prompt_ids[0]} through {prompt_ids[-1]}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
