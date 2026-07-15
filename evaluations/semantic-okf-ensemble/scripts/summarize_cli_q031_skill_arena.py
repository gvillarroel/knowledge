#!/usr/bin/env python3
"""Create the compact, reproducible diagnostic for the two CLI-only q031 runs."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[3]
REPORT_RELATIVE = Path(
    "evaluations/semantic-okf-ensemble/cli-q031-skill-arena-diagnostic.json"
)
MARKDOWN_RELATIVE = Path(
    "evaluations/semantic-okf-ensemble/cli-q031-skill-arena-diagnostic.md"
)
CONFIG_RELATIVE = Path("evaluations/semantic-okf-ensemble/skill-arena/cli-q031.yaml")
MANIFEST_RELATIVE = Path(
    "evaluations/semantic-okf-ensemble/skill-arena/cli-q031-manifest.json"
)
GENERATOR_RELATIVE = Path(
    "evaluations/semantic-okf-ensemble/scripts/generate_cli_q031_skill_arena_config.py"
)
COMPARISON_RELATIVE = Path(
    "evaluations/semantic-okf-ensemble/cli-q031-comparison.json"
)
RAW_ROOT_RELATIVE = Path("results/semantic-okf-ensemble-cli-q031-paired")
GATES = (
    "response-format",
    "response-contract",
    "evidence-validity",
    "atomic-answer-completeness",
    "important-negative-coverage",
)
RUN_SPECS = (
    {
        "id": "rejected-timeout",
        "directory": "2026-07-15T20-00-29-037Z-compare",
        "eval_id": "eval-vuT-2026-07-15T20:00:38",
        "disposition": "rejected",
        "reason": "Treatment timed out at the 240-second adapter limit and produced no evaluable output.",
    },
    {
        "id": "accepted-diagnostic",
        "directory": "2026-07-15T20-07-14-326Z-compare",
        "eval_id": "eval-3TJ-2026-07-15T20:07:20",
        "disposition": "accepted-diagnostic",
        "reason": "Both cells produced evaluable outputs; the treatment passed four of five mechanical gates.",
    },
)


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _canonical_sha256(value: Any) -> str:
    payload = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return _sha256_bytes(payload)


def _summary(response: dict[str, Any]) -> str | None:
    output = response.get("output")
    if not isinstance(output, str):
        return None
    parsed = json.loads(output)
    answer = parsed.get("answer")
    return answer.get("summary") if isinstance(answer, dict) else None


def _cell(result: dict[str, Any]) -> dict[str, Any]:
    response = copy.deepcopy(result["response"])
    output = response.get("output")
    summary = _summary(response)
    named_scores = {
        gate: result.get("namedScores", {}).get(gate)
        for gate in GATES
        if gate in result.get("namedScores", {})
    }
    failed_gates = [gate for gate, score in named_scores.items() if score != 1]
    cell = {
        "provider_id": result["provider"]["id"],
        "result_id": result["id"],
        "success": result["success"],
        "score": result["score"],
        "latency_ms": result["latencyMs"],
        "named_scores": named_scores,
        "failure_summary": (
            "failed mechanical gates: " + ", ".join(failed_gates)
            if failed_gates
            else ("adapter execution error" if not isinstance(output, str) else None)
        ),
        "response_sha256": _canonical_sha256(response),
        "output_sha256": _sha256_bytes(output.encode("utf-8")) if isinstance(output, str) else None,
        "summary": summary,
        "summary_sha256": _sha256_bytes(summary.encode("utf-8")) if summary else None,
        "response": response,
    }
    if not isinstance(output, str):
        cell["error"] = result.get("error") or response.get("error")
    return cell


def _mcp_occurrences(value: Any, path: str = "$") -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if "mcp" in str(key).casefold():
                found.append(child_path)
            found.extend(_mcp_occurrences(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(_mcp_occurrences(child, f"{path}[{index}]"))
    elif isinstance(value, str) and "mcp" in value.casefold():
        found.append(path)
    return found


def _load_raw_run(root: Path, spec: dict[str, str]) -> dict[str, Any] | None:
    directory = root / RAW_ROOT_RELATIVE / spec["directory"]
    results_path = directory / "promptfoo-results.json"
    if not results_path.is_file():
        return None
    raw = json.loads(results_path.read_text(encoding="utf-8"))
    if raw["evalId"] != spec["eval_id"]:
        raise ValueError(f"unexpected eval id for {spec['directory']}: {raw['evalId']}")
    results = raw["results"]["results"]
    cells = {_cell(item)["provider_id"]: _cell(item) for item in results}
    config_path = directory / "promptfooconfig.yaml"
    summary_path = directory / "summary.json"
    materialized_config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    return {
        "id": spec["id"],
        "disposition": spec["disposition"],
        "reason": spec["reason"],
        "compare_directory": spec["directory"],
        "eval_id": raw["evalId"],
        "artifacts": {
            "promptfoo_results": {"path": str((RAW_ROOT_RELATIVE / spec["directory"] / "promptfoo-results.json").as_posix()), "sha256": _sha256_file(results_path)},
            "summary": {"path": str((RAW_ROOT_RELATIVE / spec["directory"] / "summary.json").as_posix()), "sha256": _sha256_file(summary_path)},
            "materialized_config": {"path": str((RAW_ROOT_RELATIVE / spec["directory"] / "promptfooconfig.yaml").as_posix()), "sha256": _sha256_file(config_path), "mcp_token_occurrences": _mcp_occurrences(materialized_config)},
        },
        "cells": cells,
    }


def _checked_run(report: dict[str, Any], spec: dict[str, str]) -> dict[str, Any]:
    run = next((item for item in report.get("runs", []) if item.get("id") == spec["id"]), None)
    if not isinstance(run, dict):
        raise FileNotFoundError(f"raw run {spec['directory']} is absent and no checked fallback exists")
    if run.get("eval_id") != spec["eval_id"] or run.get("compare_directory") != spec["directory"]:
        raise ValueError(f"invalid checked fallback for {spec['id']}")
    for cell in run["cells"].values():
        if cell["response_sha256"] != _canonical_sha256(cell["response"]):
            raise ValueError(f"checked response hash mismatch for {cell['result_id']}")
        if cell["summary"] != _summary(cell["response"]):
            raise ValueError(f"checked summary mismatch for {cell['result_id']}")
    return copy.deepcopy(run)


def _allowed_bindings(config: dict[str, Any]) -> dict[str, Any]:
    assertions = config["task"]["prompts"][0]["evaluation"]["assertions"]
    assertion = next(item for item in assertions if item["metric"] == "evidence-validity")
    source = assertion["value"]
    marker = "const allowed = "
    start = source.index(marker) + len(marker)
    allowed, _ = json.JSONDecoder().raw_decode(source[start:])
    return allowed


def _binding_diagnostic(treatment: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
    parsed = json.loads(treatment["response"]["output"])
    allowed = _allowed_bindings(config)
    fields = ("claim_id", "concept_path", "paper_id", "source_path", "locators")
    mismatches: list[dict[str, Any]] = []
    checks = 0
    for item in parsed["evidence"]:
        expected_binding = allowed.get(item["claim_id"])
        for field in fields:
            checks += 1
            expected = item["claim_id"] if field == "claim_id" and expected_binding else (expected_binding or {}).get(field)
            if item.get(field) != expected:
                mismatches.append({"claim_id": item["claim_id"], "field": field, "expected": expected, "actual": item.get(field)})
    return {
        "evidence_item_count": len(parsed["evidence"]),
        "field_check_count": checks,
        "passed_field_check_count": checks - len(mismatches),
        "mismatch_count": len(mismatches),
        "mismatches": mismatches,
        "all_other_evidence_fields_match": len(mismatches) == 2 and checks - len(mismatches) == 53,
    }


def build_report(root: Path = ROOT) -> dict[str, Any]:
    existing_path = root / REPORT_RELATIVE
    existing = json.loads(existing_path.read_text(encoding="utf-8")) if existing_path.is_file() else {}
    config_path = root / CONFIG_RELATIVE
    manifest_path = root / MANIFEST_RELATIVE
    generator_path = root / GENERATOR_RELATIVE
    comparison_path = root / COMPARISON_RELATIVE
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    runs = []
    for spec in RUN_SPECS:
        runs.append(_load_raw_run(root, spec) or _checked_run(existing, spec))
    accepted = next(item for item in runs if item["id"] == "accepted-diagnostic")
    treatment = accepted["cells"]["ensemble-cli-consult-treatment"]
    comparison = json.loads(comparison_path.read_text(encoding="utf-8"))
    definitive = next(item for item in comparison["main_alternatives"] if item["id"] == "definitive_ensemble_cli")
    authored_mcp = _mcp_occurrences(config)
    materialized_mcp = {run["id"]: run["artifacts"]["materialized_config"]["mcp_token_occurrences"] for run in runs}
    return {
        "schema_version": "semantic-okf-ensemble-cli-q031-skill-arena-diagnostic/1.0",
        "question_id": "q031-graph-routing-boundary",
        "scope": "Two fresh isolated MCP-free Skill Arena runs of the current CLI-only consult treatment and its knowledge-only control.",
        "hash_contract": "SHA-256; response hashes use canonical UTF-8 JSON with sorted keys and compact separators; file and output hashes use exact bytes.",
        "configuration": {
            "config": {"path": CONFIG_RELATIVE.as_posix(), "sha256": _sha256_file(config_path)},
            "manifest": {"path": MANIFEST_RELATIVE.as_posix(), "sha256": _sha256_file(manifest_path)},
            "generator": {"path": GENERATOR_RELATIVE.as_posix(), "sha256": _sha256_file(generator_path)},
            "manifest_recorded_hashes": {"config_sha256": manifest["config"]["sha256"], "generator_sha256": manifest["generator"]["sha256"]},
        },
        "no_mcp_attestation": {
            "method": "Recursive, case-insensitive scan of every mapping key and string value in the authored and materialized YAML config structures.",
            "authored_config_mcp_token_occurrences": authored_mcp,
            "materialized_config_mcp_token_occurrences": materialized_mcp,
            "passed": not authored_mcp and not any(materialized_mcp.values()),
            "declared_treatment_capabilities": sorted(config["comparison"]["profiles"][1]["capabilities"]),
        },
        "runs": runs,
        "accepted_treatment_evidence_diagnostic": _binding_diagnostic(treatment, config),
        "direct_cli_finalizer_reference": {
            "artifact_path": COMPARISON_RELATIVE.as_posix(),
            "artifact_sha256": _sha256_file(comparison_path),
            "score": definitive["score"],
            "named_gates": definitive["named_gates"],
            "summary": definitive["response"]["answer"]["summary"],
            "output_sha256": definitive["provenance"]["finalizer_stdout_without_newline_sha256"],
            "mcp_used": definitive["provenance"]["mcp_used"],
        },
        "interpretation": {
            "accepted_pair": "In the accepted fresh pair, treatment scored 0.8 versus control 0.6. This is one isolated question, not a general superiority claim.",
            "publication_boundary": "The CLI retrieval/finalization core passes all five gates in the deterministic direct run, while the fresh agent treatment changed two authoritative source_path bytes after consultation and therefore failed evidence validity.",
            "cross_family": "The broader alternative comparison remains descriptive because its rows come from separate retained runs and bundles.",
        },
    }


def _markdown(report: dict[str, Any]) -> str:
    rejected, accepted = report["runs"]
    rc = rejected["cells"]["knowledge-only-control"]
    rt = rejected["cells"]["ensemble-cli-consult-treatment"]
    ac = accepted["cells"]["knowledge-only-control"]
    at = accepted["cells"]["ensemble-cli-consult-treatment"]
    d = report["accepted_treatment_evidence_diagnostic"]
    timeout_error = " / ".join(str(rt["error"]).splitlines())
    rows = []
    for label, cell in (("Control", ac), ("CLI treatment", at)):
        rows.append(f"| {label} | {cell['score']:.1f} | " + " | ".join(str(cell["named_scores"][gate]) for gate in GATES) + f" | {cell['latency_ms']:,} |")
    mismatch_rows = "\n".join(f"| `{item['claim_id']}` | `{item['field']}` | `{item['expected']}` | `{item['actual']}` |" for item in d["mismatches"])
    return f"""# CLI-only q031 Skill Arena diagnostic

This report covers two fresh, isolated Skill Arena comparisons of the definitive consultation skill after MCP retirement. The recursive structural scan found no MCP key or string value in the authored config or either materialized run config.

## Run disposition

| Run | Eval | Control | Treatment | Decision |
|---|---|---:|---:|---|
| `{rejected['compare_directory']}` | `{rejected['eval_id']}` | {rc['score']:.1f} | timeout/error | Rejected: treatment produced no evaluable output at the 240-second adapter limit. |
| `{accepted['compare_directory']}` | `{accepted['eval_id']}` | {ac['score']:.1f} | {at['score']:.1f} | Accepted as a diagnostic: both cells returned evaluated JSON. |

The rejected run is execution evidence only; its {rc['score']:.1f} control result cannot be paired with a missing treatment output. The treatment error was `{timeout_error}`.

## Accepted isolated pair

| Cell | Score | Format | Contract | Evidence | Atomic | Negative | Latency (ms) |
|---|---:|---:|---:|---:|---:|---:|---:|
{chr(10).join(rows)}

The treatment passed format, response contract, atomic completeness, and important-negative coverage. It failed only evidence validity. The mechanically reproduced check found {d['mismatch_count']} mismatches among {d['field_check_count']} evidence-field checks; all {d['passed_field_check_count']} other checks passed.

| Claim | Field | Expected | Actual |
|---|---|---|---|
{mismatch_rows}

Both failures replace the authoritative dotted arXiv source filename with a dashed filename. The answer content and every other checked evidence binding match the config contract.

## Interpretation

The direct deterministic CLI finalizer in `cli-q031-comparison.json` scored **1.0** with all five gates and used no MCP. The accepted fresh agent treatment scored **0.8** because the agent publication step mutated two `source_path` bytes. The isolated result therefore shows that the CLI retrieval/finalization core succeeds without MCP, but an agent can still corrupt exact evidence bytes when no host-enforced publication gate copies validated stdout verbatim.

The treatment's 0.8 versus the control's 0.6 is limited evidence from one question. Cross-family comparisons remain descriptive because the legacy, embedding, classical, entity-graph, adaptive, and definitive rows were produced by separate retained runs and bundles. Exact response objects, summaries, result IDs, latency, named scores, and artifact hashes are retained in `cli-q031-skill-arena-diagnostic.json`.
"""


def _bytes(report: dict[str, Any]) -> tuple[bytes, bytes]:
    json_bytes = (json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8")
    markdown_bytes = _markdown(report).encode("utf-8")
    return json_bytes, markdown_bytes


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    args = parser.parse_args(argv)
    report = build_report(args.repo_root.resolve())
    expected = dict(zip((REPORT_RELATIVE, MARKDOWN_RELATIVE), _bytes(report)))
    if args.check:
        drift = [path.as_posix() for path, payload in expected.items() if not (args.repo_root / path).is_file() or (args.repo_root / path).read_bytes() != payload]
        if drift:
            print("stale CLI q031 diagnostic: " + ", ".join(drift), file=sys.stderr)
            return 2
        print("CLI q031 Skill Arena diagnostic artifacts are current")
        return 0
    for path, payload in expected.items():
        target = args.repo_root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(payload)
    print("wrote CLI q031 Skill Arena diagnostic artifacts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
