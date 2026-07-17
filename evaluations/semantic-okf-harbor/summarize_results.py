#!/usr/bin/env python3
"""Create compact paired Harbor baseline/evolved reports from append-only jobs."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import statistics
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

HERE = Path(__file__).resolve().parent
QUESTION_ID = re.compile(r"q\d{3}")


class SummaryError(ValueError):
    """Raised when accepted comparison inputs are incomplete or incomparable."""


def sha256_file(path: Path) -> str:
    """Hash one result binding."""

    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> Any:
    """Load one result JSON file."""

    return json.loads(path.read_text(encoding="utf-8"))


def seconds(timing: Any) -> float | None:
    """Return duration from one Harbor TimingInfo object."""

    if not isinstance(timing, Mapping):
        return None
    start, finish = timing.get("started_at"), timing.get("finished_at")
    if not isinstance(start, str) or not isinstance(finish, str):
        return None
    try:
        return (datetime.fromisoformat(finish) - datetime.fromisoformat(start)).total_seconds()
    except ValueError:
        return None


def result_rows(root: Path, generation: str) -> list[dict[str, Any]]:
    """Load terminal trial results without retaining prompts, answers, or traces."""

    rows: list[dict[str, Any]] = []
    for path in sorted(root.rglob("result.json")):
        value = load_json(path)
        if not isinstance(value, Mapping) or "task_name" not in value or "config" not in value:
            continue
        match = QUESTION_ID.search(str(value.get("task_name")))
        if match is None:
            continue
        verifier = value.get("verifier_result")
        rewards = verifier.get("rewards") if isinstance(verifier, Mapping) else None
        rewards = {str(key): float(metric) for key, metric in rewards.items()} if isinstance(rewards, Mapping) else {}
        agent = value.get("agent_result") if isinstance(value.get("agent_result"), Mapping) else {}
        lock = path.parent / "lock.json"
        rows.append(
            {
                "generation": generation,
                "question_id": match.group(0),
                "trial_name": value.get("trial_name"),
                "result_path": path.relative_to(root).as_posix(),
                "result_sha256": sha256_file(path),
                "lock_sha256": sha256_file(lock) if lock.is_file() else None,
                "rewards": rewards,
                "exception_type": value.get("exception_info", {}).get("exception_type") if isinstance(value.get("exception_info"), Mapping) else None,
                "latency_seconds": seconds(value.get("agent_execution")),
                "input_tokens": agent.get("n_input_tokens"),
                "cache_tokens": agent.get("n_cache_tokens"),
                "output_tokens": agent.get("n_output_tokens"),
                "cost_usd": agent.get("cost_usd"),
            }
        )
    return rows


def assign_attempts(rows: list[dict[str, Any]]) -> dict[tuple[str, int], dict[str, Any]]:
    """Assign stable within-question attempt ordinals."""

    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[row["question_id"]].append(row)
    result: dict[tuple[str, int], dict[str, Any]] = {}
    for question, members in grouped.items():
        for attempt, row in enumerate(sorted(members, key=lambda item: (str(item["trial_name"]), item["result_path"])), 1):
            row["attempt"] = attempt
            result[(question, attempt)] = row
    return result


def mean(values: Iterable[float]) -> float | None:
    """Return a mean or null for no values."""

    rows = list(values)
    return statistics.fmean(rows) if rows else None


def aggregate(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Aggregate independent reward and resource dimensions."""

    metric_names = sorted({name for row in rows for name in row.get("rewards", {})})
    return {
        "trials": len(rows),
        "runtime_errors": sum(row.get("exception_type") is not None for row in rows),
        "metrics": {
            name: mean(float(row["rewards"][name]) for row in rows if name in row.get("rewards", {}))
            for name in metric_names
        },
        "mean_latency_seconds": mean(float(row["latency_seconds"]) for row in rows if row.get("latency_seconds") is not None),
        "mean_input_tokens": mean(float(row["input_tokens"]) for row in rows if row.get("input_tokens") is not None),
        "mean_output_tokens": mean(float(row["output_tokens"]) for row in rows if row.get("output_tokens") is not None),
        "total_cost_usd": sum(float(row["cost_usd"]) for row in rows if row.get("cost_usd") is not None),
    }


def compare(baseline_root: Path, evolved_root: Path, split: str, allow_incomplete: bool) -> dict[str, Any]:
    """Create a strict paired comparison over identical question/attempt keys."""

    baseline = assign_attempts(result_rows(baseline_root, "baseline"))
    evolved = assign_attempts(result_rows(evolved_root, "evolved"))
    common = sorted(set(baseline) & set(evolved))
    missing_baseline = sorted(set(evolved) - set(baseline))
    missing_evolved = sorted(set(baseline) - set(evolved))
    if not common:
        raise SummaryError("no paired trial results found")
    if not allow_incomplete and (missing_baseline or missing_evolved):
        raise SummaryError("baseline/evolved trial matrices are incomplete")
    split_ids = set(load_json(HERE / "splits.json")["cohorts"][split])
    if any(question not in split_ids for question, _ in common):
        raise SummaryError("result contains a question outside the declared split")
    baseline_rows = [baseline[key] for key in common]
    evolved_rows = [evolved[key] for key in common]
    baseline_aggregate, evolved_aggregate = aggregate(baseline_rows), aggregate(evolved_rows)
    metric_names = sorted(set(baseline_aggregate["metrics"]) & set(evolved_aggregate["metrics"]))
    deltas = {
        name: evolved_aggregate["metrics"][name] - baseline_aggregate["metrics"][name]
        for name in metric_names
        if baseline_aggregate["metrics"][name] is not None and evolved_aggregate["metrics"][name] is not None
    }
    paired = []
    for key in common:
        before, after = baseline[key], evolved[key]
        paired.append(
            {
                "question_id": key[0],
                "attempt": key[1],
                "baseline_result_sha256": before["result_sha256"],
                "evolved_result_sha256": after["result_sha256"],
                "metric_deltas": {
                    name: after["rewards"].get(name, 0.0) - before["rewards"].get(name, 0.0)
                    for name in sorted(set(before["rewards"]) | set(after["rewards"]))
                },
            }
        )
    return {
        "schema_version": "semantic-okf-harbor-paired-summary/1.0",
        "status": "complete" if not missing_baseline and not missing_evolved else "incomplete",
        "split": split,
        "paired_trials": len(common),
        "missing_baseline": [{"question_id": key[0], "attempt": key[1]} for key in missing_baseline],
        "missing_evolved": [{"question_id": key[0], "attempt": key[1]} for key in missing_evolved],
        "baseline": baseline_aggregate,
        "evolved": evolved_aggregate,
        "evolved_minus_baseline": deltas,
        "paired": paired,
        "interpretation": "Deterministic evidence metrics remain separate from semantic answer correctness. A failed quality gate cannot be offset by another score.",
    }


def markdown(report: Mapping[str, Any]) -> str:
    """Render the compact comparison table."""

    lines = [
        "# Semantic OKF Harbor Paired Comparison",
        "",
        f"Split: `{report['split']}`. Paired trials: {report['paired_trials']}. Status: `{report['status']}`.",
        "",
        "| Metric | Baseline | Evolved | Delta |",
        "|---|---:|---:|---:|",
    ]
    for name, delta in report["evolved_minus_baseline"].items():
        before = report["baseline"]["metrics"][name]
        after = report["evolved"]["metrics"][name]
        lines.append(f"| {name} | {before:.4f} | {after:.4f} | {delta:+.4f} |")
    lines.extend(
        [
            "",
            "Latency, tokens, and cost are diagnostic dimensions and are not folded into evidence quality.",
            "",
            f"- Baseline mean latency: {report['baseline']['mean_latency_seconds']}",
            f"- Evolved mean latency: {report['evolved']['mean_latency_seconds']}",
            f"- Baseline total cost: {report['baseline']['total_cost_usd']}",
            f"- Evolved total cost: {report['evolved']['total_cost_usd']}",
            "",
            report["interpretation"],
            "",
        ]
    )
    return "\n".join(lines)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse paired job roots and compact output paths."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--evolved", type=Path, required=True)
    parser.add_argument("--split", choices=("train", "dev", "holdout"), required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-markdown", type=Path, required=True)
    parser.add_argument("--allow-incomplete", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    """Summarize two append-only job roots without copying raw answers."""

    args = parse_args(argv)
    report = compare(args.baseline.resolve(), args.evolved.resolve(), args.split, args.allow_incomplete)
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_markdown.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.output_markdown.write_text(markdown(report), encoding="utf-8")
    print(json.dumps({"status": report["status"], "paired_trials": report["paired_trials"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
