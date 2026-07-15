#!/usr/bin/env python3
"""Shared deterministic helpers for the Semantic OKF ensemble evaluation."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import statistics
import sys
from pathlib import Path
from types import ModuleType
from typing import Any, Iterable, Sequence


REPO_ROOT = Path(__file__).resolve().parents[3]
FROZEN_MANIFEST = REPO_ROOT / "evaluations/semantic-okf-adaptive-evolution/frozen-benchmark.json"
FROZEN_MANIFEST_SHA256 = "2f905bd9a7ad07991fe215e0b82b3c7bfdcccbff9431ee5bd20095d99b8f4414"
ENSEMBLE_PLAN = REPO_ROOT / "evaluations/semantic-okf-ensemble/ensemble-plan.json"


class EvaluationError(ValueError):
    """Describe a closed-contract evaluation failure."""


def _object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise EvaluationError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_json(path: Path) -> dict[str, Any]:
    """Load one JSON object while rejecting duplicate keys."""

    try:
        value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_object)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise EvaluationError(f"cannot load JSON object {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise EvaluationError(f"expected a JSON object: {path}")
    return value


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    """Load JSONL objects while rejecting blank rows and duplicate keys."""

    rows: list[dict[str, Any]] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        raise EvaluationError(f"cannot read JSONL {path}: {exc}") from exc
    for number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            value = json.loads(line, object_pairs_hook=_object)
        except json.JSONDecodeError as exc:
            raise EvaluationError(f"invalid JSONL row {path}:{number}: {exc}") from exc
        if not isinstance(value, dict):
            raise EvaluationError(f"expected object at {path}:{number}")
        rows.append(value)
    return rows


def sha256(path: Path) -> str:
    """Return the byte SHA-256 of one file."""

    return hashlib.sha256(path.read_bytes()).hexdigest()


def display_path(path: Path) -> str:
    """Return a stable repository-relative path when possible."""

    resolved = path.resolve()
    try:
        return resolved.relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return resolved.as_posix()


def canonical_json(value: Any) -> str:
    """Serialize JSON deterministically for logical identity checks."""

    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def write_new(path: Path, text: str) -> None:
    """Create one append-only output without replacing an earlier artifact."""

    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise EvaluationError(f"refusing to overwrite existing output: {path}")
    path.write_text(text, encoding="utf-8", newline="\n")


def module_from_path(name: str, path: Path) -> ModuleType:
    """Import one repository module from an explicit file."""

    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise EvaluationError(f"cannot import module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def validate_frozen(manifest_path: Path = FROZEN_MANIFEST) -> dict[str, Any]:
    """Run the accepted validator and require the exact frozen manifest identity."""

    manifest_path = manifest_path.resolve(strict=True)
    if sha256(manifest_path) != FROZEN_MANIFEST_SHA256:
        raise EvaluationError("frozen benchmark manifest SHA-256 differs")
    validator = module_from_path(
        "semantic_okf_ensemble_frozen_validator",
        REPO_ROOT / "evaluations/semantic-okf-adaptive-evolution/scripts/validate_frozen_benchmark.py",
    )
    result = validator.validate(REPO_ROOT, manifest_path)
    if result.get("status") != "pass" or result.get("manifest_sha256") != FROZEN_MANIFEST_SHA256:
        raise EvaluationError("frozen benchmark validation did not pass")
    return result


def benchmark_rows(manifest_path: Path = FROZEN_MANIFEST) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    """Return the validated manifest, retrieval questions, and hard ground truth."""

    validate_frozen(manifest_path)
    manifest = load_json(manifest_path)
    retrieval_path = REPO_ROOT / manifest["cohorts"]["retrieval_questions"]["path"]
    truth_path = REPO_ROOT / manifest["cohorts"]["hard_ground_truth"]["path"]
    questions = load_jsonl(retrieval_path)
    truth = load_jsonl(truth_path)
    if [row["id"] for row in questions[-10:]] != [row["id"] for row in truth]:
        raise EvaluationError("hard ground-truth identities differ from the retrieval suffix")
    return manifest, questions, truth


def find_route(report: dict[str, Any], route_name: str) -> dict[str, Any]:
    """Find exactly one route in an evidence-valid comparison report."""

    routes = report.get("routes")
    if not isinstance(routes, list):
        raise EvaluationError("comparison report routes must be an array")
    matches = [route for route in routes if isinstance(route, dict) and route.get("name") == route_name]
    if len(matches) != 1:
        raise EvaluationError(f"expected exactly one route named {route_name!r}")
    return matches[0]


def deduplicate(values: Iterable[str | None]) -> list[str]:
    """Retain the first occurrence of each non-empty string."""

    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        if isinstance(value, str) and value and value not in seen:
            seen.add(value)
            result.append(value)
    return result


def recall_at_k(ranked: Sequence[str], relevant: set[str], k: int) -> float:
    """Return recall at k for one ranked identity list."""

    return len(set(ranked[:k]) & relevant) / len(relevant) if relevant else 1.0


def reciprocal_rank_at_k(ranked: Sequence[str], relevant: set[str], k: int) -> float:
    """Return reciprocal rank at k for one ranked identity list."""

    for index, value in enumerate(ranked[:k], 1):
        if value in relevant:
            return 1.0 / index
    return 0.0


def ndcg_at_k(ranked: Sequence[str], relevant: set[str], k: int) -> float:
    """Return binary nDCG at k for one ranked identity list."""

    if not relevant:
        return 1.0
    dcg = sum(1.0 / math.log2(index + 1) for index, value in enumerate(ranked[:k], 1) if value in relevant)
    ideal = sum(1.0 / math.log2(index + 1) for index in range(1, min(k, len(relevant)) + 1))
    return dcg / ideal if ideal else 0.0


def ranking_metrics(ranked: Sequence[str], relevant: set[str]) -> dict[str, float]:
    """Return the repository's direct retrieval metric family."""

    return {
        "recall_at_1": recall_at_k(ranked, relevant, 1),
        "recall_at_3": recall_at_k(ranked, relevant, 3),
        "recall_at_5": recall_at_k(ranked, relevant, 5),
        "recall_at_10": recall_at_k(ranked, relevant, 10),
        "mrr_at_10": reciprocal_rank_at_k(ranked, relevant, 10),
        "ndcg_at_10": ndcg_at_k(ranked, relevant, 10),
    }


def mean(values: Iterable[float]) -> float:
    """Return a safe arithmetic mean."""

    items = list(values)
    return statistics.fmean(items) if items else 0.0


def percentile(values: Sequence[float], fraction: float) -> float:
    """Return a deterministic linearly interpolated percentile."""

    if not values:
        return 0.0
    ordered = sorted(values)
    position = (len(ordered) - 1) * fraction
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return float(ordered[lower])
    return float(ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower))


def aggregate_metrics(rows: Sequence[dict[str, Any]], key: str) -> dict[str, float]:
    """Macro-average one ranking metric object across questions."""

    names = ("recall_at_1", "recall_at_3", "recall_at_5", "recall_at_10", "mrr_at_10", "ndcg_at_10")
    return {name: mean(float(row[key][name]) for row in rows) for name in names}


def geometric_mean(values: Iterable[float]) -> float:
    """Return a geometric mean over finite values in the closed unit interval."""

    items = list(values)
    if not items:
        raise EvaluationError("cannot compute a geometric mean of no values")
    if any(not math.isfinite(value) or value < 0.0 or value > 1.0 for value in items):
        raise EvaluationError("fitness objectives must be finite values in the range 0..1")
    if any(value == 0.0 for value in items):
        return 0.0
    return math.exp(sum(math.log(value) for value in items) / len(items))
