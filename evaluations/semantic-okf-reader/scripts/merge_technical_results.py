#!/usr/bin/env python3
"""Merge ordered technical retries into one canonical Promptfoo result matrix."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


EVALUATION_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = EVALUATION_ROOT / "evaluation.yaml"


def sha256_file(path: Path) -> str:
    """Return the SHA-256 digest of one input artifact."""

    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected YAML object: {path}")
    return value


def load_results(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    rows = value.get("results", {}).get("results")
    if not isinstance(value, dict) or not isinstance(rows, list):
        raise ValueError(f"invalid Promptfoo results: {path}")
    if not all(isinstance(row, dict) for row in rows):
        raise ValueError(f"Promptfoo results contain a non-object row: {path}")
    return value


def completed_output(row: dict[str, Any] | None) -> bool:
    """Return whether a result cell has a gradeable model response."""

    if not isinstance(row, dict):
        return False
    response = row.get("response")
    if not isinstance(response, dict) or response.get("error"):
        return False
    output = response.get("output")
    return isinstance(output, str) and bool(output.strip())


def _row_metadata(row: dict[str, Any]) -> dict[str, Any]:
    metadata = row.get("metadata")
    if not isinstance(metadata, dict):
        metadata = row.get("testCase", {}).get("metadata")
    if not isinstance(metadata, dict):
        raise ValueError("result row is missing metadata")
    return metadata


def _row_vars(row: dict[str, Any]) -> dict[str, Any]:
    variables = row.get("vars")
    if not isinstance(variables, dict):
        variables = row.get("testCase", {}).get("vars")
    if not isinstance(variables, dict):
        raise ValueError("result row is missing vars")
    return variables


def expected_matrix(
    primary: dict[str, Any],
) -> tuple[
    list[dict[str, Any]],
    list[str],
    str,
    str,
    dict[str, dict[str, Any]],
]:
    """Validate the source manifest and return its canonical matrix definition."""

    benchmark_id = primary.get("benchmark", {}).get("id")
    prompts = primary.get("task", {}).get("prompts")
    profiles = primary.get("comparison", {}).get("profiles")
    variants = primary.get("comparison", {}).get("variants")
    if not isinstance(benchmark_id, str) or not benchmark_id:
        raise ValueError("primary config is missing benchmark.id")
    if not isinstance(prompts, list) or not prompts:
        raise ValueError("primary config is missing task.prompts")
    if not isinstance(profiles, list) or not profiles:
        raise ValueError("primary config is missing comparison.profiles")
    if not isinstance(variants, list) or len(variants) != 1:
        raise ValueError("technical merge requires exactly one primary variant")

    prompt_by_id: dict[str, dict[str, Any]] = {}
    for prompt in prompts:
        if not isinstance(prompt, dict) or not isinstance(prompt.get("id"), str):
            raise ValueError("primary config contains an invalid prompt")
        prompt_id = str(prompt["id"])
        if prompt_id in prompt_by_id:
            raise ValueError(f"duplicate primary prompt ID: {prompt_id}")
        prompt_by_id[prompt_id] = prompt

    profile_ids: list[str] = []
    for profile in profiles:
        if not isinstance(profile, dict) or not isinstance(profile.get("id"), str):
            raise ValueError("primary config contains an invalid profile")
        profile_id = str(profile["id"])
        if profile_id in profile_ids:
            raise ValueError(f"duplicate primary profile ID: {profile_id}")
        profile_ids.append(profile_id)

    variant_id = variants[0].get("id") if isinstance(variants[0], dict) else None
    if not isinstance(variant_id, str) or not variant_id:
        raise ValueError("primary config contains an invalid variant ID")
    return prompts, profile_ids, benchmark_id, variant_id, prompt_by_id


def index_result_rows(
    document: dict[str, Any],
    *,
    path: Path,
    prompt_by_id: dict[str, dict[str, Any]],
    profile_ids: list[str],
    expected_benchmark_id: str | None = None,
    expected_variant_id: str | None = None,
) -> dict[tuple[str, str], dict[str, Any]]:
    """Index and bind one result file to the exact source questions and profiles."""

    rows = document["results"]["results"]
    indexed: dict[tuple[str, str], dict[str, Any]] = {}
    for row in rows:
        metadata = _row_metadata(row)
        variables = _row_vars(row)
        provider = row.get("provider")
        if not isinstance(provider, dict):
            raise ValueError(f"result row is missing provider: {path}")
        prompt_id = metadata.get("promptId")
        profile_id = metadata.get("profileId") or provider.get("id")
        benchmark_id = metadata.get("benchmarkId")
        variant_id = metadata.get("variantId")
        if prompt_id not in prompt_by_id:
            raise ValueError(f"unknown prompt ID {prompt_id!r} in {path}")
        if profile_id not in profile_ids or provider.get("id") != profile_id:
            raise ValueError(
                f"invalid profile binding for {prompt_id!r} in {path}"
            )
        if provider.get("label", profile_id) != profile_id:
            raise ValueError(f"invalid provider label for {prompt_id!r} in {path}")
        if metadata.get("skillModeId", profile_id) != profile_id:
            raise ValueError(f"invalid skill-mode binding for {prompt_id!r} in {path}")
        if not isinstance(benchmark_id, str) or not benchmark_id:
            raise ValueError(f"missing benchmark binding for {prompt_id!r} in {path}")
        if not isinstance(variant_id, str) or not variant_id:
            raise ValueError(f"missing variant binding for {prompt_id!r} in {path}")
        if expected_benchmark_id is not None and benchmark_id != expected_benchmark_id:
            raise ValueError(
                f"primary benchmark mismatch in {path}: expected "
                f"{expected_benchmark_id!r}, found {benchmark_id!r}"
            )
        if expected_variant_id is not None and variant_id != expected_variant_id:
            raise ValueError(
                f"primary variant mismatch in {path}: expected "
                f"{expected_variant_id!r}, found {variant_id!r}"
            )
        if variables.get("taskPrompt") != prompt_by_id[str(prompt_id)].get("prompt"):
            raise ValueError(f"prompt text mismatch for {prompt_id!r} in {path}")
        prompt_value = row.get("prompt")
        if isinstance(prompt_value, dict) and prompt_value.get("raw") != variables.get(
            "taskPrompt"
        ):
            raise ValueError(f"rendered prompt mismatch for {prompt_id!r} in {path}")
        test_case = row.get("testCase")
        if not isinstance(test_case, dict):
            raise ValueError(f"result row is missing testCase for {prompt_id!r} in {path}")
        test_metadata = test_case.get("metadata")
        test_variables = test_case.get("vars")
        if not isinstance(test_metadata, dict) or not isinstance(test_variables, dict):
            raise ValueError(
                f"result testCase is missing metadata or vars for {prompt_id!r} in {path}"
            )
        for field in ("benchmarkId", "promptId", "variantId"):
            if test_metadata.get(field) != metadata.get(field):
                raise ValueError(
                    f"result/testCase {field} mismatch for {prompt_id!r} in {path}"
                )
        for field in ("taskPrompt", "variantId", "variantDisplayName"):
            if test_variables.get(field) != variables.get(field):
                raise ValueError(
                    f"result/testCase vars.{field} mismatch for {prompt_id!r} in {path}"
                )
        key = (str(prompt_id), str(profile_id))
        if key in indexed:
            raise ValueError(f"duplicate result cell {key!r} in {path}")
        indexed[key] = row
    return indexed


def _normalize_selected_row(
    selected: dict[str, Any],
    original: dict[str, Any],
    *,
    prompt_index: int,
    source_index: int,
    source_role: str,
    source_path: Path,
    provenance_field: str = "technicalMerge",
) -> dict[str, Any]:
    """Restore primary matrix identity while retaining the selected attempt output."""

    merged = copy.deepcopy(selected)
    original_metadata = _row_metadata(original)
    source_metadata = _row_metadata(selected)
    source_identity = {
        "sourceIndex": source_index,
        "sourceRole": source_role,
        "sourceFile": source_path.resolve().as_posix(),
        "sourceBenchmarkId": source_metadata.get("benchmarkId"),
        "sourceVariantId": source_metadata.get("variantId"),
        "sourceTestIdx": selected.get("testIdx"),
    }

    merged["testIdx"] = prompt_index
    for field in ("promptIdx", "promptId", "prompt", "provider"):
        if field in original:
            merged[field] = copy.deepcopy(original[field])

    merged["vars"] = copy.deepcopy(_row_vars(original))
    test_case = merged.get("testCase")
    if not isinstance(test_case, dict):
        test_case = {}
        merged["testCase"] = test_case
    original_test_case = original.get("testCase")
    if isinstance(original_test_case, dict):
        for field in ("description", "vars", "metadata"):
            if field in original_test_case:
                test_case[field] = copy.deepcopy(original_test_case[field])

    metadata = copy.deepcopy(source_metadata)
    identity_fields = (
        "benchmarkId",
        "promptId",
        "promptDescription",
        "variantId",
        "variantDisplayName",
        "rowId",
        "label_variantId",
        "label_variantDisplayName",
        "scenarioId",
        "scenarioDescription",
        "profileId",
        "skillModeId",
    )
    for field in identity_fields:
        if field in original_metadata:
            metadata[field] = copy.deepcopy(original_metadata[field])
        else:
            metadata.pop(field, None)
    metadata[provenance_field] = source_identity
    merged["metadata"] = metadata

    response = merged.get("response")
    if isinstance(response, dict) and isinstance(response.get("metadata"), dict):
        original_response = original.get("response")
        original_response_metadata = (
            original_response.get("metadata")
            if isinstance(original_response, dict)
            else None
        )
        if isinstance(original_response_metadata, dict):
            for field in ("variantId", "variantDisplayName", "scenarioId"):
                if field in original_response_metadata:
                    response["metadata"][field] = copy.deepcopy(
                        original_response_metadata[field]
                    )
                else:
                    response["metadata"].pop(field, None)
        response["metadata"][provenance_field] = copy.deepcopy(source_identity)
    return merged


def _prompt_metrics(
    rows: list[dict[str, Any]], template: dict[str, Any]
) -> dict[str, Any]:
    """Rebuild one Promptfoo provider aggregate from its canonical rows."""

    metrics = copy.deepcopy(template)
    errors = sum(not completed_output(row) for row in rows)
    successes = sum(completed_output(row) and row.get("success") is True for row in rows)
    metrics["testPassCount"] = successes
    metrics["testFailCount"] = len(rows) - successes - errors
    metrics["testErrorCount"] = errors
    metrics["score"] = sum(
        float(row.get("score", 0))
        for row in rows
        if isinstance(row.get("score"), (int, float))
    )
    component_results = [
        component
        for row in rows
        for component in (
            row.get("gradingResult", {}).get("componentResults", [])
            if isinstance(row.get("gradingResult"), dict)
            else []
        )
        if isinstance(component, dict)
    ]
    metrics["assertPassCount"] = sum(
        component.get("pass") is True for component in component_results
    )
    metrics["assertFailCount"] = sum(
        component.get("pass") is not True for component in component_results
    )
    metrics["totalLatencyMs"] = sum(
        int(row.get("latencyMs", 0))
        for row in rows
        if isinstance(row.get("latencyMs"), (int, float))
    )
    named_scores: Counter[str] = Counter()
    named_counts: Counter[str] = Counter()
    for row in rows:
        scores = row.get("namedScores")
        if not isinstance(scores, dict):
            continue
        for name, value in scores.items():
            if isinstance(name, str) and isinstance(value, (int, float)):
                named_scores[name] += value
                named_counts[name] += 1
    metrics["namedScores"] = dict(named_scores)
    metrics["namedScoresCount"] = dict(named_counts)
    metrics["cost"] = sum(
        float(row.get("cost", 0))
        for row in rows
        if isinstance(row.get("cost"), (int, float))
    )
    token_usage = metrics.get("tokenUsage")
    if not isinstance(token_usage, dict):
        token_usage = {}
        metrics["tokenUsage"] = token_usage
    token_usage["numRequests"] = len(rows)
    return metrics


def _rebuild_prompt_aggregates(
    prompt_aggregates: Any,
    rows: list[dict[str, Any]],
    profile_ids: list[str],
) -> list[dict[str, Any]]:
    """Recompute the per-provider metrics embedded in Promptfoo exports."""

    if not isinstance(prompt_aggregates, list):
        raise ValueError("primary Promptfoo results are missing provider aggregates")
    by_provider = {
        item.get("provider"): item
        for item in prompt_aggregates
        if isinstance(item, dict) and isinstance(item.get("provider"), str)
    }
    if set(by_provider) != set(profile_ids):
        raise ValueError("primary provider aggregates do not match configured profiles")
    rebuilt: list[dict[str, Any]] = []
    for profile_id in profile_ids:
        aggregate = copy.deepcopy(by_provider[profile_id])
        profile_rows = [
            row
            for row in rows
            if isinstance(row.get("provider"), dict)
            and row["provider"].get("id") == profile_id
        ]
        aggregate["metrics"] = _prompt_metrics(
            profile_rows,
            aggregate.get("metrics") if isinstance(aggregate.get("metrics"), dict) else {},
        )
        rebuilt.append(aggregate)
    return rebuilt


def _result_stats(
    rows: list[dict[str, Any]], source_documents: list[dict[str, Any]]
) -> dict[str, Any]:
    """Recompute outcome counters and aggregate source-run wall durations."""

    errors = sum(not completed_output(row) for row in rows)
    successes = sum(completed_output(row) and row.get("success") is True for row in rows)
    failures = len(rows) - successes - errors
    template = copy.deepcopy(
        source_documents[0].get("results", {}).get("stats", {})
    )
    if not isinstance(template, dict):
        template = {}
    template.update({"successes": successes, "failures": failures, "errors": errors})
    token_usage = template.get("tokenUsage")
    if not isinstance(token_usage, dict):
        token_usage = {}
        template["tokenUsage"] = token_usage
    token_usage["numRequests"] = len(rows)
    duration = 0
    for document in source_documents:
        stats = document.get("results", {}).get("stats", {})
        if isinstance(stats, dict) and isinstance(stats.get("durationMs"), (int, float)):
            duration += stats["durationMs"]
    template["durationMs"] = duration
    template["evaluationDurationMs"] = duration
    return template


def merge_results(
    primary: dict[str, Any],
    primary_document: dict[str, Any],
    resume_documents: list[dict[str, Any]],
    *,
    resume_configs: list[dict[str, Any]],
    source_paths: list[Path],
    source_config_paths: list[Path],
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Select the first complete attempt for every canonical matrix cell."""

    if len(source_paths) != 1 + len(resume_documents):
        raise ValueError("source path count does not match result document count")
    if len(resume_configs) != len(resume_documents):
        raise ValueError("resume config count does not match resume result count")
    if len(source_config_paths) != len(source_paths):
        raise ValueError("source config path count does not match result source count")
    prompts, profile_ids, benchmark_id, variant_id, prompt_by_id = expected_matrix(primary)
    documents = [primary_document, *resume_documents]
    source_configs = [primary, *resume_configs]
    indexed: list[dict[tuple[str, str], dict[str, Any]]] = []
    for source_config, document, path in zip(
        source_configs, documents, source_paths, strict=True
    ):
        (
            source_prompts,
            source_profile_ids,
            source_benchmark_id,
            source_variant_id,
            _,
        ) = expected_matrix(source_config)
        unknown_prompts = [
            str(prompt.get("id"))
            for prompt in source_prompts
            if str(prompt.get("id")) not in prompt_by_id
        ]
        changed_prompts = [
            str(prompt.get("id"))
            for prompt in source_prompts
            if str(prompt.get("id")) in prompt_by_id
            and prompt.get("prompt")
            != prompt_by_id[str(prompt.get("id"))].get("prompt")
        ]
        unknown_profiles = sorted(set(source_profile_ids) - set(profile_ids))
        if unknown_prompts:
            raise ValueError(
                f"source manifest contains unknown prompts: {', '.join(unknown_prompts[:5])}"
            )
        if changed_prompts:
            raise ValueError(
                f"source manifest changed prompt text: {', '.join(changed_prompts[:5])}"
            )
        if unknown_profiles:
            raise ValueError(
                f"source manifest contains unknown profiles: {', '.join(unknown_profiles)}"
            )
        row_index = index_result_rows(
            document,
            path=path,
            prompt_by_id=prompt_by_id,
            profile_ids=profile_ids,
            expected_benchmark_id=source_benchmark_id,
            expected_variant_id=source_variant_id,
        )
        source_expected = {
            (str(prompt["id"]), profile_id)
            for prompt in source_prompts
            for profile_id in source_profile_ids
        }
        if set(row_index) != source_expected:
            missing = source_expected - set(row_index)
            extra = set(row_index) - source_expected
            raise ValueError(
                f"results do not match source manifest {path}: "
                f"missing={len(missing)}, extra={len(extra)}"
            )
        indexed.append(row_index)

    expected_keys = [
        (str(prompt["id"]), profile_id)
        for prompt in prompts
        for profile_id in profile_ids
    ]
    primary_keys = set(indexed[0])
    missing_primary = [key for key in expected_keys if key not in primary_keys]
    extra_primary = sorted(primary_keys - set(expected_keys))
    if missing_primary or extra_primary:
        raise ValueError(
            "primary results do not contain the exact canonical matrix: "
            f"missing={len(missing_primary)}, extra={len(extra_primary)}"
        )

    merged_rows: list[dict[str, Any]] = []
    audit_cells: list[dict[str, Any]] = []
    selected_counts: Counter[str] = Counter()
    unresolved: list[dict[str, str]] = []
    prompt_index_by_id = {
        str(prompt["id"]): index for index, prompt in enumerate(prompts)
    }
    roles = ["primary", *[f"resume-{index}" for index in range(1, len(documents))]]
    for key in expected_keys:
        prompt_id, profile_id = key
        attempts: list[dict[str, Any]] = []
        selected_row: dict[str, Any] | None = None
        selected_index: int | None = None
        for source_index, (row_index, role, path) in enumerate(
            zip(indexed, roles, source_paths, strict=True)
        ):
            row = row_index.get(key)
            metadata = _row_metadata(row) if row is not None else {}
            response = row.get("response") if row is not None else None
            attempts.append(
                {
                    "source_index": source_index,
                    "source_role": role,
                    "source_file": path.resolve().as_posix(),
                    "present": row is not None,
                    "completed": completed_output(row),
                    "success": row.get("success") if row is not None else None,
                    "benchmark_id": metadata.get("benchmarkId"),
                    "variant_id": metadata.get("variantId"),
                    "response_error": bool(
                        isinstance(response, dict) and response.get("error")
                    ),
                }
            )
            if selected_row is None and completed_output(row):
                selected_row = row
                selected_index = source_index

        if selected_row is None or selected_index is None:
            unresolved.append({"prompt_id": prompt_id, "profile_id": profile_id})
            continue
        role = roles[selected_index]
        selected_counts[role] += 1
        merged_rows.append(
            _normalize_selected_row(
                selected_row,
                indexed[0][key],
                prompt_index=prompt_index_by_id[prompt_id],
                source_index=selected_index,
                source_role=role,
                source_path=source_paths[selected_index],
            )
        )
        audit_cells.append(
            {
                "prompt_index": prompt_index_by_id[prompt_id],
                "prompt_id": prompt_id,
                "profile_id": profile_id,
                "attempts": attempts,
                "selected_source_index": selected_index,
                "selected_source_role": role,
            }
        )

    if unresolved:
        sample = ", ".join(
            f"{item['prompt_id']}/{item['profile_id']}" for item in unresolved[:5]
        )
        raise ValueError(
            f"technical merge left {len(unresolved)} unresolved cells: {sample}"
        )
    if len(merged_rows) != len(expected_keys):
        raise ValueError("technical merge did not produce the exact expected row count")

    result = copy.deepcopy(primary_document)
    result["results"]["results"] = merged_rows
    result["results"]["stats"] = _result_stats(merged_rows, documents)
    result["results"]["prompts"] = _rebuild_prompt_aggregates(
        result["results"].get("prompts"), merged_rows, profile_ids
    )
    now = datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace(
        "+00:00", "Z"
    )
    result["results"]["timestamp"] = now
    result["shareableUrl"] = None
    if isinstance(result.get("evalId"), str):
        result["evalId"] += "-technical-composite"
    result_metadata = result.get("metadata")
    if not isinstance(result_metadata, dict):
        result_metadata = {}
        result["metadata"] = result_metadata
    result_metadata["exportedAt"] = now
    result_metadata["technicalMerge"] = {
        "schemaVersion": "1.0",
        "sourceCount": len(documents),
        "selectedSourceCounts": dict(selected_counts),
        "canonicalCellCount": len(merged_rows),
        "technicalErrorCount": 0,
    }

    audit = {
        "schema_version": "1.0",
        "origin_benchmark_id": benchmark_id,
        "origin_variant_id": variant_id,
        "prompt_count": len(prompts),
        "profile_ids": profile_ids,
        "canonical_cell_count": len(merged_rows),
        "technical_error_count": 0,
        "selected_source_counts": dict(selected_counts),
        "sources": [
            {
                "source_index": index,
                "source_role": roles[index],
                "config_path": config_path.resolve().as_posix(),
                "config_sha256": sha256_file(config_path),
                "results_path": path.resolve().as_posix(),
                "results_sha256": sha256_file(path),
                "row_count": len(document["results"]["results"]),
            }
            for index, (config_path, path, document) in enumerate(
                zip(source_config_paths, source_paths, documents, strict=True)
            )
        ],
        "cells": audit_cells,
    }
    return result, audit


def write_merged_results(
    config_path: Path,
    primary_path: Path,
    attempts: list[tuple[Path, Path]],
    output_path: Path,
) -> dict[str, Any]:
    """Merge result files and write both the composite and audit sidecar."""

    primary = load_yaml(config_path)
    resume_config_paths = [config for config, _ in attempts]
    resume_paths = [results for _, results in attempts]
    source_paths = [primary_path, *resume_paths]
    source_config_paths = [config_path, *resume_config_paths]
    documents = [load_results(path) for path in source_paths]
    resume_configs = [load_yaml(path) for path in resume_config_paths]
    merged, audit = merge_results(
        primary,
        documents[0],
        documents[1:],
        resume_configs=resume_configs,
        source_paths=source_paths,
        source_config_paths=source_config_paths,
    )
    audit["primary_config"] = config_path.resolve().as_posix()
    audit["primary_config_sha256"] = sha256_file(config_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(merged, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    audit_path = output_path.with_suffix(".audit.json")
    audit["composite_results"] = output_path.resolve().as_posix()
    audit["composite_results_sha256"] = sha256_file(output_path)
    audit_path.write_text(
        json.dumps(audit, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return audit


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("primary", type=Path, help="Primary Promptfoo results JSON.")
    parser.add_argument(
        "--attempt",
        action="append",
        dest="attempts",
        required=True,
        nargs=2,
        metavar=("CONFIG", "RESULTS"),
        type=Path,
        help="Ordered resume config/results pair; repeat for later attempts.",
    )
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    audit = write_merged_results(
        args.config.expanduser().resolve(),
        args.primary.expanduser().resolve(),
        [
            (config.expanduser().resolve(), results.expanduser().resolve())
            for config, results in args.attempts
        ],
        args.output.expanduser().resolve(),
    )
    counts = ", ".join(
        f"{role}={count}"
        for role, count in audit["selected_source_counts"].items()
    )
    print(
        f"Merged {audit['canonical_cell_count']} canonical cells with zero technical "
        f"errors ({counts})."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
