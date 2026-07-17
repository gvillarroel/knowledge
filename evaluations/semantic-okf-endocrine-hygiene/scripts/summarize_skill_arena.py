#!/usr/bin/env python3
"""Create a compact, fail-closed report from one explicitly bound Skill Arena run."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any, Mapping, Sequence

import yaml


REPOSITORY = Path(__file__).resolve().parents[3]
EVALUATION = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = EVALUATION / "skill-arena/classical-hard4.yaml"
DEFAULT_MANIFEST = EVALUATION / "skill-arena/classical-hard4-manifest.json"
DEFAULT_JSON = EVALUATION / "reports/skill-arena-hard5-diagnostic.json"
DEFAULT_MARKDOWN = EVALUATION / "reports/skill-arena-hard5-diagnostic.md"
SHOWCASE_ID = "q030-causal-evidence-map"
EVIDENCE_FIELDS = (
    "concept_path",
    "paper_id",
    "source_path",
    "evidence_locator",
    "evidence_text_sha256",
)


class SummaryError(RuntimeError):
    """Describe an invalid, incomplete, or incorrectly bound Skill Arena artifact."""


def canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SummaryError(f"expected a JSON object: {path}")
    return value


def load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SummaryError(f"expected a YAML object: {path}")
    return value


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]
    if not all(isinstance(row, dict) for row in rows):
        raise SummaryError(f"expected JSONL objects: {path}")
    return rows


def tree_binding(root: Path) -> dict[str, Any]:
    rows: list[bytes] = []
    total = 0
    count = 0
    for path in sorted(root.rglob("*"), key=lambda item: item.relative_to(root).as_posix()):
        relative = path.relative_to(root)
        if "__pycache__" in relative.parts or path.suffix == ".pyc":
            continue
        if path.is_symlink():
            raise SummaryError(f"bound bundle contains a symbolic link: {relative.as_posix()}")
        if not path.is_file():
            continue
        payload = path.read_bytes()
        rows.append(
            relative.as_posix().encode("utf-8")
            + b"\0"
            + sha256_bytes(payload).encode("ascii")
            + b"\n"
        )
        count += 1
        total += len(payload)
    if not rows:
        raise SummaryError(f"bound bundle is empty: {root}")
    return {"tree_sha256": sha256_bytes(b"".join(rows)), "file_count": count, "bytes": total}


def _string_ids(items: Any, label: str) -> list[str]:
    if not isinstance(items, list):
        raise SummaryError(f"{label} must be an array")
    result = [item.get("id") if isinstance(item, dict) else None for item in items]
    if not all(isinstance(identifier, str) and identifier for identifier in result):
        raise SummaryError(f"{label} contains an invalid ID")
    if len(set(result)) != len(result):
        raise SummaryError(f"{label} contains duplicate IDs")
    return result


def _assertions(value: Any, label: str) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not all(isinstance(item, dict) for item in value):
        raise SummaryError(f"{label} assertions must be an array of objects")
    metrics = [item.get("metric") for item in value]
    if not all(isinstance(metric, str) and metric for metric in metrics):
        raise SummaryError(f"{label} contains an assertion without a metric")
    if len(set(metrics)) != len(metrics):
        raise SummaryError(f"{label} contains duplicate metrics")
    return [dict(item) for item in value]


def source_contract(source: Mapping[str, Any]) -> dict[str, Any]:
    benchmark = source.get("benchmark")
    task = source.get("task")
    comparison = source.get("comparison")
    evaluation = source.get("evaluation")
    if not all(isinstance(value, dict) for value in (benchmark, task, comparison, evaluation)):
        raise SummaryError("source config lacks benchmark/task/comparison/evaluation objects")
    benchmark_id = benchmark.get("id")
    if not isinstance(benchmark_id, str) or not benchmark_id:
        raise SummaryError("source config has no benchmark ID")
    prompts = task.get("prompts")
    if not isinstance(prompts, list) or not all(isinstance(item, dict) for item in prompts):
        raise SummaryError("source config task.prompts must be an array of objects")
    prompt_ids = _string_ids(prompts, "source task.prompts")
    prompt_by_id = {item["id"]: item for item in prompts}
    prompt_text: dict[str, str] = {}
    global_assertions = _assertions(evaluation.get("assertions"), "source global evaluation")
    metrics_by_prompt: dict[str, list[str]] = {}
    assertions_by_prompt: dict[str, list[dict[str, Any]]] = {}
    for identifier in prompt_ids:
        prompt = prompt_by_id[identifier]
        text = prompt.get("prompt")
        local = prompt.get("evaluation")
        if not isinstance(text, str) or not text or not isinstance(local, dict):
            raise SummaryError(f"source prompt {identifier} has no prompt/evaluation contract")
        local_assertions = _assertions(local.get("assertions"), f"source prompt {identifier}")
        combined = [*global_assertions, *local_assertions]
        combined_metrics = [item["metric"] for item in combined]
        if len(set(combined_metrics)) != len(combined_metrics):
            raise SummaryError(f"source prompt {identifier} repeats a global/local metric")
        prompt_text[identifier] = text
        assertions_by_prompt[identifier] = combined
        metrics_by_prompt[identifier] = combined_metrics
    metric_orders = {tuple(metrics) for metrics in metrics_by_prompt.values()}
    if len(metric_orders) != 1:
        raise SummaryError("all accepted prompts must use the same ordered metric contract")
    profile_ids = _string_ids(comparison.get("profiles"), "source comparison.profiles")
    variants = comparison.get("variants")
    variant_ids = _string_ids(variants, "source comparison.variants")
    variant_models: dict[str, str] = {}
    variant_adapters: dict[str, str] = {}
    for variant in variants:
        agent = variant.get("agent")
        if not isinstance(agent, dict):
            raise SummaryError(f"source variant {variant['id']} has no agent object")
        model, adapter = agent.get("model"), agent.get("adapter")
        if not isinstance(model, str) or not model or not isinstance(adapter, str) or not adapter:
            raise SummaryError(f"source variant {variant['id']} has invalid model/adapter metadata")
        variant_models[variant["id"]] = model
        variant_adapters[variant["id"]] = adapter
    requests = evaluation.get("requests")
    if isinstance(requests, bool) or not isinstance(requests, int) or requests != 1:
        raise SummaryError("this paired summarizer requires exactly one request per cell")
    return {
        "benchmark_id": benchmark_id,
        "prompt_ids": prompt_ids,
        "prompt_text": prompt_text,
        "assertions_by_prompt": assertions_by_prompt,
        "metrics": list(next(iter(metric_orders))),
        "profile_ids": profile_ids,
        "variant_ids": variant_ids,
        "variant_models": variant_models,
        "variant_adapters": variant_adapters,
        "requests_per_cell": requests,
    }


def validate_manifest_binding(
    manifest: Mapping[str, Any],
    contract: Mapping[str, Any],
    source_config: Path,
    bundle: Path,
) -> None:
    if manifest.get("status") != "pass":
        raise SummaryError("generated config manifest is not pass")
    config = manifest.get("config")
    if not isinstance(config, dict) or config.get("sha256") != sha256_file(source_config):
        raise SummaryError("current source config digest does not match the generated manifest")
    expected_path = source_config.relative_to(REPOSITORY).as_posix()
    if config.get("path") != expected_path:
        raise SummaryError("source config path does not match the generated manifest")
    comparisons = {
        "benchmark_id": contract["benchmark_id"],
        "prompt_ids": contract["prompt_ids"],
        "profiles": contract["profile_ids"],
        "requests_per_cell": contract["requests_per_cell"],
    }
    for field, expected in comparisons.items():
        if manifest.get(field) != expected:
            raise SummaryError(f"generated manifest {field} does not match the source config")
    expected_bundle = manifest.get("bundle")
    actual_bundle = tree_binding(bundle)
    if expected_bundle != actual_bundle:
        raise SummaryError("the supplied bundle does not match the generated config manifest")


def validate_promptfoo_binding(
    raw: Mapping[str, Any],
    promptfoo_config: Mapping[str, Any],
    contract: Mapping[str, Any],
) -> None:
    embedded = raw.get("config")
    if not isinstance(embedded, dict):
        raise SummaryError("raw results have no embedded Promptfoo config")
    for key, value in promptfoo_config.items():
        if embedded.get(key) != value:
            raise SummaryError(f"raw results do not embed the supplied Promptfoo config key {key!r}")
    expected_description = f"{contract['benchmark_id']}:compare"
    if promptfoo_config.get("description") != expected_description:
        raise SummaryError("compiled Promptfoo description does not bind the expected benchmark")
    providers = promptfoo_config.get("providers")
    if not isinstance(providers, list) or not all(isinstance(item, dict) for item in providers):
        raise SummaryError("compiled Promptfoo config has invalid providers")
    provider_ids = [item.get("label") for item in providers]
    if provider_ids != contract["profile_ids"]:
        raise SummaryError("compiled Promptfoo profiles do not exactly match source-config order")
    for provider in providers:
        profile_id = provider["label"]
        config = provider.get("config")
        if not isinstance(config, dict):
            raise SummaryError(f"compiled provider {profile_id} has no config")
        if config.get("profile_id") != profile_id or config.get("provider_id") != profile_id:
            raise SummaryError(f"compiled provider {profile_id} has inconsistent profile identity")
        routes = config.get("routes")
        if not isinstance(routes, dict) or list(routes) != contract["variant_ids"]:
            raise SummaryError(f"compiled provider {profile_id} has the wrong variants")
        for variant_id, route in routes.items():
            nested = route.get("provider", {}).get("config", {}) if isinstance(route, dict) else {}
            if nested.get("model") != contract["variant_models"][variant_id]:
                raise SummaryError(f"compiled provider {profile_id}/{variant_id} has the wrong model")
    tests = promptfoo_config.get("tests")
    if not isinstance(tests, list) or not all(isinstance(item, dict) for item in tests):
        raise SummaryError("compiled Promptfoo config has invalid tests")
    expected_pairs = {
        (prompt_id, variant_id)
        for prompt_id in contract["prompt_ids"]
        for variant_id in contract["variant_ids"]
    }
    observed_pairs: set[tuple[str, str]] = set()
    for test in tests:
        metadata = test.get("metadata")
        variables = test.get("vars")
        if not isinstance(metadata, dict) or not isinstance(variables, dict):
            raise SummaryError("compiled Promptfoo test lacks metadata/vars")
        prompt_id, variant_id = metadata.get("promptId"), metadata.get("variantId")
        if not isinstance(prompt_id, str) or not isinstance(variant_id, str):
            raise SummaryError("compiled Promptfoo test lacks prompt/variant identity")
        pair = (prompt_id, variant_id)
        if pair in observed_pairs:
            raise SummaryError(f"compiled Promptfoo test is duplicated: {pair}")
        observed_pairs.add(pair)
        if metadata.get("benchmarkId") != contract["benchmark_id"]:
            raise SummaryError(f"compiled Promptfoo test {pair} has the wrong benchmark")
        if metadata.get("rowId") != f"{variant_id}:{prompt_id}":
            raise SummaryError(f"compiled Promptfoo test {pair} has the wrong rowId")
        if variables.get("variantId") != variant_id:
            raise SummaryError(f"compiled Promptfoo test {pair} has inconsistent variant vars")
        if variables.get("taskPrompt") != contract["prompt_text"].get(prompt_id):
            raise SummaryError(f"compiled Promptfoo test {pair} does not match the source prompt")
        if test.get("assert") != contract["assertions_by_prompt"].get(prompt_id):
            raise SummaryError(f"compiled Promptfoo test {pair} does not match source assertions")
    if observed_pairs != expected_pairs:
        raise SummaryError("compiled Promptfoo tests are not the exact prompt-by-variant product")


def validate_result_cells(rows: Sequence[Mapping[str, Any]], contract: Mapping[str, Any]) -> None:
    expected = {
        (prompt_id, profile_id, variant_id)
        for prompt_id in contract["prompt_ids"]
        for profile_id in contract["profile_ids"]
        for variant_id in contract["variant_ids"]
    }
    if len(rows) != len(expected):
        raise SummaryError(f"accepted run must contain {len(expected)} completed cells, found {len(rows)}")
    observed: set[tuple[str, str, str]] = set()
    for row in rows:
        test_case = row.get("testCase")
        provider = row.get("provider")
        metadata = row.get("metadata")
        prompt = row.get("prompt")
        if not all(isinstance(value, dict) for value in (test_case, provider, metadata, prompt)):
            raise SummaryError("result cell lacks testCase/provider/metadata/prompt objects")
        test_metadata = test_case.get("metadata")
        variables = test_case.get("vars")
        if not isinstance(test_metadata, dict) or not isinstance(variables, dict):
            raise SummaryError("result cell lacks test metadata/vars")
        prompt_id = test_metadata.get("promptId")
        profile_id = provider.get("id")
        variant_id = test_metadata.get("variantId")
        if not all(isinstance(value, str) and value for value in (prompt_id, profile_id, variant_id)):
            raise SummaryError("result cell lacks prompt/profile/variant identity")
        identity = (prompt_id, profile_id, variant_id)
        if identity in observed:
            raise SummaryError(f"duplicate result cell: {identity}")
        observed.add(identity)
        if test_metadata.get("benchmarkId") != contract["benchmark_id"]:
            raise SummaryError(f"result cell {identity} has the wrong benchmark")
        if test_metadata.get("rowId") != f"{variant_id}:{prompt_id}":
            raise SummaryError(f"result cell {identity} has the wrong rowId")
        if metadata.get("profileId") != profile_id or provider.get("label") != profile_id:
            raise SummaryError(f"result cell {identity} has inconsistent profile metadata")
        if metadata.get("variantId") != variant_id or variables.get("variantId") != variant_id:
            raise SummaryError(f"result cell {identity} has inconsistent variant metadata")
        expected_prompt = contract["prompt_text"].get(prompt_id)
        if variables.get("taskPrompt") != expected_prompt or prompt.get("raw") != expected_prompt:
            raise SummaryError(f"result cell {identity} does not contain the exact source prompt")
        if test_case.get("assert") != contract["assertions_by_prompt"].get(prompt_id):
            raise SummaryError(f"result cell {identity} does not contain the exact source assertions")
    if observed != expected:
        missing, extra = sorted(expected - observed), sorted(observed - expected)
        raise SummaryError(f"result cells do not match the exact Cartesian contract; missing={missing}, extra={extra}")


def ledger_claim_evidence(
    bundle: Path,
    expected_count: int,
) -> dict[str, dict[str, Any]]:
    identity = load_json(EVALUATION / "corpus/source-combination.json")["identity_by_source"]
    result: dict[str, dict[str, Any]] = {}
    for record in load_jsonl(bundle / "semantic/records.jsonl"):
        source_id = record.get("source_id")
        attributes = record.get("attributes")
        if not isinstance(source_id, str) or not source_id.startswith("claims-") or not isinstance(attributes, dict):
            continue
        claim_id = record.get("record_id")
        interpretation = attributes.get("interpretation")
        if not isinstance(claim_id, str) or claim_id in result or not isinstance(interpretation, str) or not interpretation:
            raise SummaryError(f"invalid or duplicate reviewed claim in ledger: {claim_id!r}")
        result[claim_id] = {
            "concept_path": record["concept_path"],
            "paper_id": identity[source_id],
            "source_path": record["source_path"],
            "evidence_locator": attributes["evidence_locator"],
            "evidence_text_sha256": attributes["evidence_text_sha256"],
            "interpretation": interpretation,
        }
    if len(result) != expected_count:
        raise SummaryError(f"expected {expected_count} reviewed ledger claims, found {len(result)}")
    return result


def audit_evidence(output: Mapping[str, Any], ledger: Mapping[str, Mapping[str, Any]]) -> tuple[bool, list[str]]:
    evidence = output.get("evidence")
    if not isinstance(evidence, list) or not evidence:
        return False, ["evidence must be a non-empty array"]
    errors: list[str] = []
    claim_ids = [item.get("claim_id") for item in evidence if isinstance(item, dict)]
    if len(claim_ids) != len(evidence):
        errors.append("an evidence row is not an object")
    if len(set(claim_ids)) != len(claim_ids):
        errors.append("evidence claim IDs are not unique")
    if claim_ids != sorted(claim_ids):
        errors.append("evidence claim IDs are not sorted")
    for item in evidence:
        if not isinstance(item, dict):
            continue
        claim_id = item.get("claim_id")
        expected = ledger.get(claim_id) if isinstance(claim_id, str) else None
        if expected is None:
            errors.append(f"unknown claim ID: {claim_id!r}")
            continue
        for key in EVIDENCE_FIELDS:
            if item.get(key) != expected[key]:
                errors.append(f"{claim_id}.{key}: expected {expected[key]!r}, found {item.get(key)!r}")
    return not errors, errors


def audit_claim_fidelity(
    output: Mapping[str, Any],
    ledger: Mapping[str, Mapping[str, Any]],
) -> tuple[bool, list[str]]:
    answer = output.get("answer")
    claims = answer.get("claims") if isinstance(answer, dict) else None
    evidence = output.get("evidence")
    if not isinstance(claims, list) or not claims:
        return False, ["answer.claims must be a non-empty array"]
    if not isinstance(evidence, list):
        return False, ["evidence must be an array"]
    errors: list[str] = []
    used_ids: list[str] = []
    for number, claim in enumerate(claims, 1):
        if not isinstance(claim, dict):
            errors.append(f"claim {number} is not an object")
            continue
        supporting = claim.get("supporting_claim_ids")
        if not isinstance(supporting, list) or len(supporting) != 1 or not isinstance(supporting[0], str):
            errors.append(f"claim {number} must bind exactly one reviewed claim ID")
            continue
        claim_id = supporting[0]
        used_ids.append(claim_id)
        expected = ledger.get(claim_id)
        if expected is None:
            errors.append(f"claim {number} uses unknown reviewed claim ID {claim_id!r}")
        elif claim.get("statement") != expected["interpretation"]:
            errors.append(f"claim {number} statement differs from reviewed interpretation {claim_id}")
    if len(set(used_ids)) != len(used_ids):
        errors.append("reviewed claim IDs are duplicated across answer claims")
    if used_ids != sorted(used_ids):
        errors.append("reviewed claim IDs are not sorted across answer claims")
    evidence_ids = [item.get("claim_id") for item in evidence if isinstance(item, dict)]
    if used_ids != evidence_ids:
        errors.append("answer claim IDs and evidence claim IDs differ in identity or order")
    return not errors, errors


def result_rows(raw: Mapping[str, Any]) -> list[dict[str, Any]]:
    wrapper = raw.get("results")
    if not isinstance(wrapper, dict) or not isinstance(wrapper.get("results"), list):
        raise SummaryError("Promptfoo results do not contain results.results")
    rows = wrapper["results"]
    if not all(isinstance(row, dict) for row in rows):
        raise SummaryError("Promptfoo results contain a non-object cell")
    return rows


def compact_cell(
    row: Mapping[str, Any],
    ledger: Mapping[str, Mapping[str, Any]],
    metrics: Sequence[str],
) -> dict[str, Any]:
    metadata = row["testCase"]["metadata"]
    provider = row["provider"]
    prompt_id, profile_id, variant_id = metadata["promptId"], provider["id"], metadata["variantId"]
    response = row.get("response")
    output_text = response.get("output") if isinstance(response, dict) else None
    if not isinstance(output_text, str):
        output_text = ""
    try:
        output = json.loads(output_text)
    except json.JSONDecodeError:
        output = {}
    grading = row.get("gradingResult")
    named = grading.get("namedScores") if isinstance(grading, dict) else None
    if not isinstance(named, dict):
        named = {}
    unknown_named = sorted(set(named) - set(metrics))
    if unknown_named:
        raise SummaryError(f"result {prompt_id}/{profile_id}/{variant_id} has unknown metrics: {unknown_named}")
    metric_values = {metric: int(named.get(metric) == 1) for metric in metrics}
    independently_valid, evidence_errors = audit_evidence(output, ledger)
    claim_fidelity, claim_errors = audit_claim_fidelity(output, ledger)
    if "evidence-validity" in metric_values and metric_values["evidence-validity"] != int(independently_valid):
        raise SummaryError(
            f"native and independent evidence validity disagree for {prompt_id}/{profile_id}/{variant_id}"
        )
    for claim_metric in ("claim-fidelity", "reviewed-claim-fidelity"):
        if claim_metric in metric_values and metric_values[claim_metric] != int(claim_fidelity):
            raise SummaryError(
                f"native and independent claim fidelity disagree for {prompt_id}/{profile_id}/{variant_id}"
            )
    answer = output.get("answer") if isinstance(output, dict) else None
    claims = answer.get("claims") if isinstance(answer, dict) else []
    summary = answer.get("summary") if isinstance(answer, dict) else None
    papers = answer.get("paper_ids") if isinstance(answer, dict) else []
    evidence = output.get("evidence") if isinstance(output, dict) else []
    cell = {
        "prompt_id": prompt_id,
        "profile_id": profile_id,
        "variant_id": variant_id,
        "success": bool(row.get("success")),
        "score": float(row.get("score", 0.0)),
        "latency_ms": int(row.get("latencyMs", 0)),
        "metrics": metric_values,
        "independent_ledger_evidence_valid": independently_valid,
        "evidence_errors": evidence_errors,
        "independent_reviewed_claim_fidelity": claim_fidelity,
        "claim_fidelity_errors": claim_errors,
        "output_sha256": sha256_bytes(output_text.encode("utf-8")),
        "answer_summary_word_count": len(summary.split()) if isinstance(summary, str) else 0,
        "claim_count": len(claims) if isinstance(claims, list) else 0,
        "evidence_count": len(evidence) if isinstance(evidence, list) else 0,
        "paper_ids": papers if isinstance(papers, list) else [],
    }
    if prompt_id == SHOWCASE_ID:
        cell["actual_answer_summary"] = summary
        cell["claim_ids"] = sorted(
            {
                claim_id
                for claim in claims
                if isinstance(claim, dict)
                for claim_id in claim.get("supporting_claim_ids", [])
                if isinstance(claim_id, str)
            }
        )
        cell["evidence_claim_ids"] = [
            item.get("claim_id") for item in evidence if isinstance(item, dict)
        ]
    return cell


def aggregate(
    cells: Sequence[Mapping[str, Any]],
    profile_ids: Sequence[str],
    variants: Sequence[str],
    prompt_count: int,
    metrics: Sequence[str],
) -> dict[str, Any]:
    grouped: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for cell in cells:
        grouped[cell["profile_id"]].append(cell)
    expected_per_profile = prompt_count * len(variants)
    if set(grouped) != set(profile_ids) or any(len(grouped[profile]) != expected_per_profile for profile in profile_ids):
        raise SummaryError("accepted run has an invalid number of cells per profile")
    result: dict[str, Any] = {}
    for profile in profile_ids:
        rows = grouped[profile]
        result[profile] = {
            "cells": len(rows),
            "compound_passes": sum(bool(row["success"]) for row in rows),
            "mean_score": statistics.fmean(float(row["score"]) for row in rows),
            "mean_latency_ms": statistics.fmean(int(row["latency_ms"]) for row in rows),
            "metric_pass_counts": {
                metric: sum(int(row["metrics"][metric]) for row in rows) for metric in metrics
            },
            "metric_pass_rates": {
                metric: statistics.fmean(int(row["metrics"][metric]) for row in rows) for metric in metrics
            },
        }
    if len(profile_ids) == 2:
        control, treatment = result[profile_ids[0]], result[profile_ids[1]]
        result["treatment_minus_control"] = {
            "mean_score": treatment["mean_score"] - control["mean_score"],
            "mean_latency_ms": treatment["mean_latency_ms"] - control["mean_latency_ms"],
            "metric_pass_rates": {
                metric: treatment["metric_pass_rates"][metric] - control["metric_pass_rates"][metric]
                for metric in metrics
            },
        }
    return result


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPOSITORY).as_posix()
    except ValueError:
        return str(path.resolve())


def artifact_descriptor(path: Path) -> dict[str, Any]:
    return {"path": _display_path(path), "bytes": path.stat().st_size, "sha256": sha256_file(path)}


def superseded_descriptor(path: Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    raw = load_json(path)
    return {
        "eval_id": raw.get("evalId"),
        "artifact": artifact_descriptor(path),
        "disposition": "excluded from causal interpretation",
        "reason": "a previous evaluator generation did not enforce the final exact reviewed-claim contract",
    }


def render_markdown(report: Mapping[str, Any]) -> str:
    aggregate_rows = report["aggregate"]
    profiles = report["execution"]["profile_ids"]
    metrics = report["execution"]["metric_ids"]
    per_profile = report["execution"]["cells_per_profile"]
    lines = [
        "# Isolated Skill Arena hard-question diagnostic",
        "",
        f"This is a live, no-MCP, paired control/treatment diagnostic over {report['execution']['prompt_count']} prompts. Every raw cell was bound to the exact benchmark, prompt, profile, variant, model, source config, generated config manifest, compiled Promptfoo config, and immutable bundle before aggregation. With one request per cell, results are descriptive and do not establish a stable population effect.",
        "",
        f"Accepted eval ID: `{report['eval_id']}`. All {report['execution']['completed']} cells completed with {report['execution']['errors']} runtime errors.",
        "",
        "| Profile | Compound pass | Mean score | Mean latency |",
        "| --- | ---: | ---: | ---: |",
    ]
    for profile in profiles:
        row = aggregate_rows[profile]
        lines.append(
            f"| {profile} | {row['compound_passes']}/{per_profile} | {row['mean_score']:.3f} | "
            f"{row['mean_latency_ms'] / 1000:.1f} s |"
        )
    lines.extend(["", "## Metric pass rates", "", "| Metric | " + " | ".join(profiles) + " |", "| --- | " + " | ".join("---:" for _ in profiles) + " |"])
    for metric in metrics:
        lines.append(
            f"| {metric} | "
            + " | ".join(f"{aggregate_rows[profile]['metric_pass_rates'][metric]:.0%}" for profile in profiles)
            + " |"
        )
    delta = aggregate_rows.get("treatment_minus_control")
    if isinstance(delta, dict):
        lines.extend(
            [
                "",
                "## Interpretation",
                "",
                f"The treatment-minus-control mean-score difference was {delta['mean_score']:+.3f}; mean latency changed by {delta['mean_latency_ms'] / 1000:+.1f} seconds. Component gates are more informative than compound pass because a single failed strict gate fails a cell.",
                "",
                "| Metric | Treatment minus control |",
                "| --- | ---: |",
            ]
        )
        for metric in metrics:
            lines.append(f"| {metric} | {delta['metric_pass_rates'][metric]:+.0%} |")
    lines.extend(
        [
            "",
            f"Evidence validity was independently recomputed from all {report['execution']['reviewed_ledger_claim_count']} reviewed ledger claims. Reviewed-claim fidelity was also independently checked by requiring each answer statement to equal the bound claim's reviewed interpretation and to have a one-to-one evidence row.",
            "",
            "## Per-question cells",
            "",
            "| Prompt | Profile | Variant | Pass | Score | Evidence valid | Claim fidelity | Latency |",
            "| --- | --- | --- | --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for cell in report["cells"]:
        lines.append(
            f"| `{cell['prompt_id']}` | {cell['profile_id']} | {cell['variant_id']} | "
            f"{'yes' if cell['success'] else 'no'} | {cell['score']:.3f} | "
            f"{int(cell['independent_ledger_evidence_valid'])} | "
            f"{int(cell['independent_reviewed_claim_fidelity'])} | {cell['latency_ms'] / 1000:.1f} s |"
        )
    showcase = [cell for cell in report["cells"] if cell["prompt_id"] == SHOWCASE_ID]
    if showcase:
        lines.extend(["", f"## Actual answers for `{SHOWCASE_ID}`", ""])
        for cell in showcase:
            lines.extend(
                [
                    f"### {cell['profile_id']} / {cell['variant_id']}",
                    "",
                    cell.get("actual_answer_summary") or "No non-null answer summary was returned.",
                    "",
                    f"Claims: {cell['claim_count']}; evidence rows: {cell['evidence_count']}; summary words: {cell['answer_summary_word_count']}; exact ledger evidence valid: {'yes' if cell['independent_ledger_evidence_valid'] else 'no'}; exact reviewed-claim fidelity: {'yes' if cell['independent_reviewed_claim_fidelity'] else 'no'}.",
                    "",
                ]
            )
    if report.get("superseded_run"):
        lines.extend(
            [
                "## Superseded evaluator run",
                "",
                f"Eval `{report['superseded_run']['eval_id']}` is excluded from causal interpretation because it predates the final exact reviewed-claim evaluator contract. Its raw artifact hash remains recorded in the compact JSON report.",
                "",
            ]
        )
    return "\n".join(lines)


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(content, encoding="utf-8", newline="\n")
    os.replace(temporary, path)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="Accepted promptfoo-results.json")
    parser.add_argument(
        "--raw-promptfoo-config",
        type=Path,
        required=True,
        help="The promptfooconfig.yaml emitted beside --input; used to bind raw results explicitly.",
    )
    parser.add_argument("--source-config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--config-manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument(
        "--bundle",
        type=Path,
        required=True,
        help="Exact classical bundle used by the run; checked against the generated manifest.",
    )
    parser.add_argument("--superseded-input", type=Path, help="Optional prior result with a known evaluator defect")
    parser.add_argument("--json-output", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--markdown-output", type=Path, default=DEFAULT_MARKDOWN)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    input_path = args.input.resolve(strict=True)
    raw_promptfoo_path = args.raw_promptfoo_config.resolve(strict=True)
    source_path = args.source_config.resolve(strict=True)
    manifest_path = args.config_manifest.resolve(strict=True)
    bundle = args.bundle.resolve(strict=True)
    if input_path.parent != raw_promptfoo_path.parent:
        raise SummaryError("--input and --raw-promptfoo-config must come from the same append-only run directory")
    source = load_yaml(source_path)
    manifest = load_json(manifest_path)
    contract = source_contract(source)
    validate_manifest_binding(manifest, contract, source_path, bundle)
    raw = load_json(input_path)
    promptfoo_config = load_yaml(raw_promptfoo_path)
    validate_promptfoo_binding(raw, promptfoo_config, contract)
    rows = result_rows(raw)
    validate_result_cells(rows, contract)
    stats = raw["results"].get("stats")
    if not isinstance(stats, dict) or int(stats.get("errors", 0)) != 0:
        raise SummaryError("accepted run has missing stats or nonzero runtime errors")
    expected_claim_count = manifest.get("reviewed_ledger_claim_count")
    if isinstance(expected_claim_count, bool) or not isinstance(expected_claim_count, int) or expected_claim_count < 1:
        raise SummaryError("generated manifest has no valid reviewed_ledger_claim_count")
    ledger = ledger_claim_evidence(bundle, expected_claim_count)
    cells = [compact_cell(row, ledger, contract["metrics"]) for row in rows]
    cells.sort(
        key=lambda row: (
            contract["prompt_ids"].index(row["prompt_id"]),
            contract["profile_ids"].index(row["profile_id"]),
            contract["variant_ids"].index(row["variant_id"]),
        )
    )
    expected_cells = len(contract["prompt_ids"]) * len(contract["profile_ids"]) * len(contract["variant_ids"])
    report = {
        "schema_version": "semantic-okf-endocrine-hygiene-skill-arena-diagnostic/1.1",
        "status": "pass",
        "interpretation_status": "descriptive-paired-diagnostic",
        "eval_id": raw.get("evalId"),
        "benchmark_id": contract["benchmark_id"],
        "execution": {
            "requested": expected_cells,
            "completed": len(rows),
            "errors": int(stats.get("errors", 0)),
            "mcp_used": False,
            "requests_per_cell": contract["requests_per_cell"],
            "prompt_count": len(contract["prompt_ids"]),
            "cells_per_profile": len(contract["prompt_ids"]) * len(contract["variant_ids"]),
            "profile_ids": contract["profile_ids"],
            "variant_ids": contract["variant_ids"],
            "variant_models": contract["variant_models"],
            "variant_adapters": contract["variant_adapters"],
            "metric_ids": contract["metrics"],
            "reviewed_ledger_claim_count": expected_claim_count,
        },
        "binding": {
            "status": "pass",
            "checks": [
                "source config digest equals generated manifest",
                "bundle tree equals generated manifest",
                "compiled Promptfoo config is embedded in raw results",
                "benchmark, prompt, assertion, profile, variant, and model identities match",
                "result cells are the unique complete Cartesian product",
            ],
            "source_config": artifact_descriptor(source_path),
            "generated_config_manifest": artifact_descriptor(manifest_path),
            "raw_promptfoo_config": artifact_descriptor(raw_promptfoo_path),
            "raw_embedded_config_sha256": sha256_bytes(canonical_json(raw["config"]).encode("utf-8")),
            "bundle": tree_binding(bundle),
        },
        "raw_results": artifact_descriptor(input_path),
        "superseded_run": superseded_descriptor(
            args.superseded_input.resolve(strict=True) if args.superseded_input else None
        ),
        "aggregate": aggregate(
            cells,
            contract["profile_ids"],
            contract["variant_ids"],
            len(contract["prompt_ids"]),
            contract["metrics"],
        ),
        "cells": cells,
        "limitations": [
            f"n={len(contract['prompt_ids'])} questions per profile and one request per cell",
            "development questions rather than an untouched holdout",
            "compound pass requires every strict binary component gate",
            "one model family and one consultation-skill treatment only",
        ],
    }
    atomic_write(args.json_output.resolve(), json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    atomic_write(args.markdown_output.resolve(), render_markdown(report))
    print(json.dumps({"status": "pass", "eval_id": report["eval_id"], "cells": len(cells)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
