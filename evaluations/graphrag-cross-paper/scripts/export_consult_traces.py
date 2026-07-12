#!/usr/bin/env python3
"""Export immutable consult-skill Promptfoo results as traced-evolution records."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


METRIC_ISSUES = {
    "response-format": "invalid-response-format",
    "response-contract": "output-contract-violation",
    "evidence-path-validity": "reconstructed-evidence-path",
    "semantic-structure": "insufficient-relevant-source-breadth",
    "page-citation-grounding": "insufficient-page-citation-breadth",
    "cross-paper-evidence": "insufficient-paper-evidence-breadth",
}
SUCCESS_STRENGTHS = [
    "strong-output-contract",
    "strong-deterministic-ordering",
    "exact-evidence-paths",
    "sufficient-source-breadth",
    "page-citation-grounding",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("results", type=Path, help="Promptfoo results JSON from the frozen run.")
    parser.add_argument("output", type=Path, help="Directory that receives one JSON file per trace.")
    parser.add_argument("--profile", default="consult-skill")
    parser.add_argument("--benchmark-id", default="graphrag-cross-paper-30-compare")
    parser.add_argument("--holdout", action="append", default=[])
    return parser.parse_args()


def load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected a JSON object: {path}")
    return value


def component_metrics(result: dict[str, Any]) -> tuple[list[str], list[str]]:
    grading = result.get("gradingResult")
    if not isinstance(grading, dict):
        raise ValueError("result has no gradingResult object")
    components = grading.get("componentResults")
    if not isinstance(components, list) or not components:
        raise ValueError("result has no component assertion results")
    passed: list[str] = []
    failed: list[str] = []
    for component in components:
        assertion = component.get("assertion", {})
        metric = assertion.get("metric")
        if not isinstance(metric, str) or not metric:
            raise ValueError("component assertion has no metric")
        (passed if component.get("pass") is True else failed).append(metric)
    return sorted(set(passed)), sorted(set(failed))


def trace_from_result(result: dict[str, Any], benchmark_id: str) -> dict[str, Any]:
    metadata = result.get("metadata")
    if not isinstance(metadata, dict):
        raise ValueError("result has no metadata object")
    prompt_id = metadata.get("promptId")
    if not isinstance(prompt_id, str) or not prompt_id:
        raise ValueError("result metadata has no promptId")
    passed_metrics, failed_metrics = component_metrics(result)
    success = result.get("success") is True
    if success and failed_metrics:
        raise ValueError(f"successful result {prompt_id} contains failed assertions")
    if not success and not failed_metrics:
        raise ValueError(f"failed result {prompt_id} has no failed assertions")
    issues = sorted({METRIC_ISSUES[metric] for metric in failed_metrics})
    if not success:
        issues.append("missing-hard-gates")
        issues = sorted(set(issues))
    score = len(passed_metrics) / (len(passed_metrics) + len(failed_metrics))
    return {
        "traceId": f"consult-{prompt_id}",
        "outcome": "success" if success else "failure",
        "benchmarkId": benchmark_id,
        "promptId": prompt_id,
        "issues": issues,
        "strengths": SUCCESS_STRENGTHS if success else [],
        "notes": (
            f"Frozen Promptfoo result. Passed metrics: {', '.join(passed_metrics)}. "
            f"Failed metrics: {', '.join(failed_metrics) if failed_metrics else 'none'}."
        ),
        "filesTouched": [],
        "score": round(score, 6),
    }


def main() -> int:
    args = parse_args()
    payload = load_object(args.results)
    result_container = payload.get("results")
    if not isinstance(result_container, dict) or not isinstance(result_container.get("results"), list):
        raise ValueError("Promptfoo payload has no results.results array")
    holdout = set(args.holdout)
    args.output.mkdir(parents=True, exist_ok=True)
    traces: list[dict[str, Any]] = []
    for result in result_container["results"]:
        provider = result.get("provider", {})
        metadata = result.get("metadata", {})
        if provider.get("label") != args.profile or metadata.get("benchmarkId") != args.benchmark_id:
            continue
        trace = trace_from_result(result, args.benchmark_id)
        if trace["promptId"] in holdout:
            continue
        traces.append(trace)
    traces.sort(key=lambda item: item["traceId"])
    if not traces:
        raise ValueError("no matching non-holdout traces were found")
    if len({trace["traceId"] for trace in traces}) != len(traces):
        raise ValueError("duplicate trace IDs were produced")
    for trace in traces:
        target = args.output / f"{trace['traceId']}.json"
        target.write_text(json.dumps(trace, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    summary = {
        "benchmark_id": args.benchmark_id,
        "failures": sum(trace["outcome"] == "failure" for trace in traces),
        "holdout": sorted(holdout),
        "profile": args.profile,
        "successes": sum(trace["outcome"] == "success" for trace in traces),
        "traces": len(traces),
    }
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
