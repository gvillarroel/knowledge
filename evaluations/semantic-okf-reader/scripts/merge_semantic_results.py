#!/usr/bin/env python3
"""Overlay a bound semantic fallback run onto a complete canonical result matrix."""

from __future__ import annotations

import argparse
import copy
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from merge_technical_results import (  # noqa: E402
    _normalize_selected_row,
    _rebuild_prompt_aggregates,
    _result_stats,
    completed_output,
    expected_matrix,
    index_result_rows,
    load_results,
    load_yaml,
    sha256_file,
)


EVALUATION_ROOT = SCRIPT_DIR.parent
DEFAULT_CONFIG = EVALUATION_ROOT / "evaluation.yaml"
DEFAULT_FALLBACK_CONFIG = EVALUATION_ROOT / "luna-fallback-evaluation.yaml"


def merge_semantic_results(
    primary: dict[str, Any],
    primary_document: dict[str, Any],
    fallback: dict[str, Any],
    fallback_document: dict[str, Any],
    *,
    primary_path: Path,
    fallback_path: Path,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Replace only failed, complete treatment cells with their fallback attempts."""

    prompts, profile_ids, benchmark_id, variant_id, prompt_by_id = expected_matrix(primary)
    primary_index = index_result_rows(
        primary_document,
        path=primary_path,
        prompt_by_id=prompt_by_id,
        profile_ids=profile_ids,
        expected_benchmark_id=benchmark_id,
        expected_variant_id=variant_id,
    )
    expected_keys = [
        (str(prompt["id"]), profile_id)
        for prompt in prompts
        for profile_id in profile_ids
    ]
    if set(primary_index) != set(expected_keys):
        raise ValueError("primary results do not contain the exact canonical matrix")
    incomplete_primary = [
        key for key in expected_keys if not completed_output(primary_index[key])
    ]
    if incomplete_primary:
        raise ValueError(
            "primary results still contain technical errors; merge technical resumes first"
        )

    (
        fallback_prompts,
        fallback_profiles,
        fallback_benchmark_id,
        fallback_variant_id,
        _,
    ) = expected_matrix(fallback)
    if fallback_profiles != ["skill"]:
        raise ValueError("semantic fallback must contain only the `skill` profile")
    unknown_prompts = [
        str(prompt.get("id"))
        for prompt in fallback_prompts
        if str(prompt.get("id")) not in prompt_by_id
    ]
    changed_prompts = [
        str(prompt.get("id"))
        for prompt in fallback_prompts
        if str(prompt.get("id")) in prompt_by_id
        and prompt.get("prompt") != prompt_by_id[str(prompt.get("id"))].get("prompt")
    ]
    if unknown_prompts:
        raise ValueError(
            f"fallback manifest contains unknown prompts: {', '.join(unknown_prompts[:5])}"
        )
    if changed_prompts:
        raise ValueError(
            f"fallback manifest changed prompt text: {', '.join(changed_prompts[:5])}"
        )
    fallback_index = index_result_rows(
        fallback_document,
        path=fallback_path,
        prompt_by_id=prompt_by_id,
        profile_ids=profile_ids,
        expected_benchmark_id=fallback_benchmark_id,
        expected_variant_id=fallback_variant_id,
    )
    fallback_expected = {
        (str(prompt["id"]), "skill") for prompt in fallback_prompts
    }
    if set(fallback_index) != fallback_expected:
        missing = fallback_expected - set(fallback_index)
        extra = set(fallback_index) - fallback_expected
        raise ValueError(
            "fallback results do not match the fallback manifest: "
            f"missing={len(missing)}, extra={len(extra)}"
        )

    prompt_index = {
        str(prompt["id"]): index for index, prompt in enumerate(prompts)
    }
    audit_cells: list[dict[str, Any]] = []
    merged_rows: list[dict[str, Any]] = []
    for key in expected_keys:
        original = primary_index[key]
        selected = fallback_index.get(key)
        if selected is None:
            merged_rows.append(copy.deepcopy(original))
            continue
        if original.get("success") is True:
            raise ValueError(f"fallback targeted a successful primary cell: {key}")
        if not completed_output(selected):
            raise ValueError(f"semantic fallback is technically incomplete: {key}")
        normalized = _normalize_selected_row(
            selected,
            original,
            prompt_index=prompt_index[key[0]],
            source_index=1,
            source_role="semantic-fallback",
            source_path=fallback_path,
            provenance_field="semanticFallback",
        )
        original_metadata = original.get("metadata")
        if isinstance(original_metadata, dict) and "technicalMerge" in original_metadata:
            normalized["metadata"]["technicalMerge"] = copy.deepcopy(
                original_metadata["technicalMerge"]
            )
        original_response = original.get("response")
        normalized_response = normalized.get("response")
        if (
            isinstance(original_response, dict)
            and isinstance(original_response.get("metadata"), dict)
            and "technicalMerge" in original_response["metadata"]
            and isinstance(normalized_response, dict)
            and isinstance(normalized_response.get("metadata"), dict)
        ):
            normalized_response["metadata"]["technicalMerge"] = copy.deepcopy(
                original_response["metadata"]["technicalMerge"]
            )
        merged_rows.append(normalized)
        audit_cells.append(
            {
                "prompt_index": prompt_index[key[0]],
                "prompt_id": key[0],
                "profile_id": key[1],
                "primary_success": original.get("success"),
                "primary_named_scores": original.get("namedScores"),
                "fallback_success": selected.get("success"),
                "fallback_named_scores": selected.get("namedScores"),
            }
        )

    result = copy.deepcopy(primary_document)
    result["results"]["results"] = merged_rows
    result["results"]["stats"] = _result_stats(
        merged_rows, [primary_document, fallback_document]
    )
    result["results"]["prompts"] = _rebuild_prompt_aggregates(
        result["results"].get("prompts"), merged_rows, profile_ids
    )
    now = datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace(
        "+00:00", "Z"
    )
    result["results"]["timestamp"] = now
    result["shareableUrl"] = None
    if isinstance(result.get("evalId"), str):
        result["evalId"] += "-semantic-composite"
    metadata = result.get("metadata")
    if not isinstance(metadata, dict):
        metadata = {}
        result["metadata"] = metadata
    metadata["exportedAt"] = now
    metadata["semanticFallback"] = {
        "schemaVersion": "1.0",
        "selectedCellCount": len(audit_cells),
        "passedCellCount": sum(
            cell["fallback_success"] is True for cell in audit_cells
        ),
        "failedCellCount": sum(
            cell["fallback_success"] is not True for cell in audit_cells
        ),
        "technicalErrorCount": 0,
    }

    audit = {
        "schema_version": "1.0",
        "origin_benchmark_id": benchmark_id,
        "origin_variant_id": variant_id,
        "fallback_benchmark_id": fallback_benchmark_id,
        "fallback_variant_id": fallback_variant_id,
        "canonical_cell_count": len(merged_rows),
        "fallback_cell_count": len(audit_cells),
        "fallback_pass_count": sum(
            cell["fallback_success"] is True for cell in audit_cells
        ),
        "fallback_fail_count": sum(
            cell["fallback_success"] is not True for cell in audit_cells
        ),
        "technical_error_count": 0,
        "cells": audit_cells,
    }
    return result, audit


def write_semantic_composite(
    config_path: Path,
    primary_path: Path,
    fallback_config_path: Path,
    fallback_path: Path,
    output_path: Path,
) -> dict[str, Any]:
    """Write the semantic composite and a source-bound audit sidecar."""

    primary = load_yaml(config_path)
    fallback = load_yaml(fallback_config_path)
    merged, audit = merge_semantic_results(
        primary,
        load_results(primary_path),
        fallback,
        load_results(fallback_path),
        primary_path=primary_path,
        fallback_path=fallback_path,
    )
    audit.update(
        {
            "primary_config": config_path.resolve().as_posix(),
            "primary_config_sha256": sha256_file(config_path),
            "primary_results": primary_path.resolve().as_posix(),
            "primary_results_sha256": sha256_file(primary_path),
            "fallback_config": fallback_config_path.resolve().as_posix(),
            "fallback_config_sha256": sha256_file(fallback_config_path),
            "fallback_results": fallback_path.resolve().as_posix(),
            "fallback_results_sha256": sha256_file(fallback_path),
        }
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(merged, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    audit["composite_results"] = output_path.resolve().as_posix()
    audit["composite_results_sha256"] = sha256_file(output_path)
    output_path.with_suffix(".audit.json").write_text(
        json.dumps(audit, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return audit


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("primary", type=Path, help="Complete canonical Promptfoo results.")
    parser.add_argument("fallback", type=Path, help="Semantic fallback Promptfoo results.")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument(
        "--fallback-config", type=Path, default=DEFAULT_FALLBACK_CONFIG
    )
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    audit = write_semantic_composite(
        args.config.expanduser().resolve(),
        args.primary.expanduser().resolve(),
        args.fallback_config.expanduser().resolve(),
        args.fallback.expanduser().resolve(),
        args.output.expanduser().resolve(),
    )
    print(
        f"Applied {audit['fallback_cell_count']} semantic fallback cells: "
        f"passed={audit['fallback_pass_count']}, failed={audit['fallback_fail_count']}, "
        "technical-errors=0."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
