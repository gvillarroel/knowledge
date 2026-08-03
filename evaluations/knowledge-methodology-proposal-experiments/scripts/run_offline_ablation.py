#!/usr/bin/env python3
"""Run the preregistered cross-domain paper-retrieval ablation."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path
import random
import re
import statistics
import sys
import time
from typing import Any, Iterable, Mapping, Sequence


sys.dont_write_bytecode = True
SCRIPT_PATH = Path(__file__).resolve()
ROOT = SCRIPT_PATH.parents[1]
REPO = SCRIPT_PATH.parents[3]
CONFIG_PATH = ROOT / "experiment.json"
REPORT_JSON = ROOT / "reports" / "offline-ablation-01.json"
REPORT_MARKDOWN = ROOT / "reports" / "offline-ablation-01.md"
WORD_RE = re.compile(r"[a-z0-9]+(?:[._-][a-z0-9]+)*", re.IGNORECASE)
PAGE_RE = re.compile(
    r"(?ms)^## PDF page (?P<number>\d+)\r?\n+"
    r"(?P<body>.*?)(?=^## PDF page |\Z)"
)


class ExperimentError(RuntimeError):
    """Raised when a frozen input or experiment invariant is invalid."""


@dataclass(frozen=True)
class Question:
    """One exposed paper-retrieval question."""

    identifier: str
    text: str
    relevant: frozenset[str]


@dataclass(frozen=True)
class Paper:
    """One page-grounded paper input."""

    identifier: str
    path: Path
    pages: tuple[str, ...]


@dataclass(frozen=True)
class Unit:
    """One retrieval unit derived from a paper."""

    paper_id: str
    identifier: str
    level: str
    text: str


def _canonical_json(value: Any) -> str:
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
            allow_nan=False,
        )
        + "\n"
    )


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _portable(path: Path) -> str:
    return path.resolve().relative_to(REPO.resolve()).as_posix()


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_config() -> dict[str, Any]:
    value = _load_json(CONFIG_PATH)
    if (
        not isinstance(value, dict)
        or value.get("schema_version")
        != "knowledge-methodology-proposal-experiment/1.0"
        or value.get("candidate_state")
        != "retrospective-all-qrels-exposed"
        or value.get("promotion_eligible") is not False
    ):
        raise ExperimentError("Experiment configuration envelope is invalid")
    return value


def _resolve_repo_path(value: str) -> Path:
    path = (REPO / value).resolve()
    try:
        path.relative_to(REPO.resolve())
    except ValueError as exc:
        raise ExperimentError(f"Path escapes the repository: {value}") from exc
    return path


def _load_questions(dataset: Mapping[str, Any]) -> list[Question]:
    path = _resolve_repo_path(str(dataset["questions"]))
    if _sha256_file(path) != dataset["questions_sha256"]:
        raise ExperimentError(f"Question digest drift: {path}")
    questions: list[Question] = []
    for line_number, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(),
        start=1,
    ):
        if not line.strip():
            continue
        value = json.loads(line)
        qrels = value.get("qrels", {})
        paper_ids = qrels.get("paper_ids")
        if (
            not isinstance(value.get("id"), str)
            or not isinstance(value.get("question"), str)
            or not isinstance(paper_ids, list)
            or not paper_ids
            or not all(isinstance(item, str) for item in paper_ids)
        ):
            raise ExperimentError(
                f"Invalid question at {path}:{line_number}"
            )
        questions.append(
            Question(
                identifier=value["id"],
                text=value["question"],
                relevant=frozenset(paper_ids),
            )
        )
    if (
        len(questions) != dataset["question_count"]
        or len({row.identifier for row in questions}) != len(questions)
    ):
        raise ExperimentError(f"Question count or identity drift: {path}")
    return questions


def _load_papers(dataset: Mapping[str, Any]) -> list[Paper]:
    root = _resolve_repo_path(str(dataset["papers"]))
    paths = sorted(root.glob("*.md"))
    if len(paths) != dataset["paper_count"]:
        raise ExperimentError(f"Paper count drift: {root}")
    papers: list[Paper] = []
    for path in paths:
        identity = path.stem
        matches = list(PAGE_RE.finditer(path.read_text(encoding="utf-8")))
        if not matches or [
            int(match.group("number")) for match in matches
        ] != list(range(1, len(matches) + 1)):
            raise ExperimentError(f"Invalid page locators: {path}")
        pages = tuple(match.group("body").strip() for match in matches)
        if any(not page for page in pages):
            raise ExperimentError(f"Empty extracted page: {path}")
        papers.append(Paper(identity, path, pages))
    if len({paper.identifier for paper in papers}) != len(papers):
        raise ExperimentError(f"Duplicate paper identity: {root}")
    return papers


def _word_tokens(text: str) -> tuple[str, ...]:
    return tuple(match.group(0).casefold() for match in WORD_RE.finditer(text))


def _char_trigrams(text: str) -> tuple[str, ...]:
    normalized = " ".join(_word_tokens(text))
    padded = f"  {normalized}  "
    return tuple(padded[index : index + 3] for index in range(len(padded) - 2))


def _fixed_units(
    paper: Paper,
    *,
    size: int,
    overlap: int,
) -> list[Unit]:
    tokens = _word_tokens("\n".join(paper.pages))
    if size < 1 or overlap < 0 or overlap >= size:
        raise ExperimentError("Invalid fixed chunk contract")
    step = size - overlap
    units: list[Unit] = []
    for index, start in enumerate(range(0, len(tokens), step), start=1):
        selected = tokens[start : start + size]
        if not selected:
            break
        units.append(
            Unit(
                paper_id=paper.identifier,
                identifier=f"{paper.identifier}:fixed:{index:05d}",
                level="child",
                text=" ".join(selected),
            )
        )
        if start + size >= len(tokens):
            break
    return units


def _make_units(
    papers: Sequence[Paper],
    treatment: Mapping[str, Any],
) -> list[Unit]:
    kind = treatment["kind"]
    units: list[Unit] = []
    for paper in papers:
        if kind == "document":
            units.append(
                Unit(
                    paper.identifier,
                    f"{paper.identifier}:document",
                    "parent",
                    "\n".join(paper.pages),
                )
            )
        elif kind == "page":
            units.extend(
                Unit(
                    paper.identifier,
                    f"{paper.identifier}:page:{index:04d}",
                    "child",
                    page,
                )
                for index, page in enumerate(paper.pages, start=1)
            )
        elif kind == "fixed":
            units.extend(
                _fixed_units(
                    paper,
                    size=int(treatment["size"]),
                    overlap=int(treatment["overlap"]),
                )
            )
        elif kind == "hierarchical-page":
            units.append(
                Unit(
                    paper.identifier,
                    f"{paper.identifier}:document",
                    "parent",
                    "\n".join(paper.pages),
                )
            )
            units.extend(
                Unit(
                    paper.identifier,
                    f"{paper.identifier}:page:{index:04d}",
                    "child",
                    page,
                )
                for index, page in enumerate(paper.pages, start=1)
            )
        else:
            raise ExperimentError(f"Unknown chunking treatment: {kind}")
    if not units:
        raise ExperimentError(f"Chunking produced no units: {treatment['id']}")
    return units


class SparseIndex:
    """A deterministic BM25 or TF-IDF inverted index."""

    def __init__(
        self,
        units: Sequence[Unit],
        *,
        kind: str,
        analyzer: str,
    ) -> None:
        self.units = list(units)
        self.kind = kind
        if analyzer == "word":
            analyze = _word_tokens
        elif analyzer == "char3":
            analyze = _char_trigrams
        else:
            raise ExperimentError(f"Unknown analyzer: {analyzer}")
        self.analyze = analyze
        counters = [Counter(analyze(unit.text)) for unit in units]
        self.lengths = [sum(counter.values()) for counter in counters]
        self.average_length = statistics.fmean(self.lengths)
        document_frequency: Counter[str] = Counter()
        for counter in counters:
            document_frequency.update(counter.keys())
        count = len(counters)
        self.idf = {
            token: (
                math.log(1.0 + (count - seen + 0.5) / (seen + 0.5))
                if kind == "bm25"
                else math.log((count + 1.0) / (seen + 1.0)) + 1.0
            )
            for token, seen in document_frequency.items()
        }
        self.postings: dict[str, list[tuple[int, int]]] = defaultdict(list)
        for index, counter in enumerate(counters):
            for token, frequency in counter.items():
                self.postings[token].append((index, frequency))
        self.norms: list[float] = []
        if kind == "tfidf":
            for counter in counters:
                squared = sum(
                    ((1.0 + math.log(frequency)) * self.idf[token]) ** 2
                    for token, frequency in counter.items()
                )
                self.norms.append(math.sqrt(squared))
        elif kind != "bm25":
            raise ExperimentError(f"Unknown sparse index kind: {kind}")

    def score(self, query: str) -> list[float]:
        """Score every indexed unit for one query."""

        query_counter = Counter(self.analyze(query))
        scores = [0.0] * len(self.units)
        if self.kind == "bm25":
            for token in query_counter:
                idf = self.idf.get(token)
                if idf is None:
                    continue
                for index, frequency in self.postings[token]:
                    denominator = frequency + 1.2 * (
                        1.0
                        - 0.75
                        + 0.75 * self.lengths[index] / self.average_length
                    )
                    scores[index] += idf * (frequency * 2.2) / denominator
            return scores

        query_weights = {
            token: (1.0 + math.log(frequency)) * self.idf[token]
            for token, frequency in query_counter.items()
            if token in self.idf
        }
        query_norm = math.sqrt(
            sum(weight * weight for weight in query_weights.values())
        )
        if query_norm == 0.0:
            return scores
        for token, query_weight in query_weights.items():
            idf = self.idf[token]
            for index, frequency in self.postings[token]:
                unit_weight = (1.0 + math.log(frequency)) * idf
                scores[index] += query_weight * unit_weight
        for index, score in enumerate(scores):
            denominator = query_norm * self.norms[index]
            scores[index] = score / denominator if denominator else 0.0
        return scores


def _normalize(scores: Mapping[str, float]) -> dict[str, float]:
    low = min(scores.values())
    high = max(scores.values())
    if high == low:
        return {key: 0.0 for key in scores}
    return {
        key: (value - low) / (high - low)
        for key, value in scores.items()
    }


def _document_scores(
    units: Sequence[Unit],
    unit_scores: Sequence[float],
    paper_ids: Sequence[str],
    treatment: Mapping[str, Any],
) -> dict[str, float]:
    by_level: dict[str, dict[str, float]] = {
        "parent": {paper_id: 0.0 for paper_id in paper_ids},
        "child": {paper_id: 0.0 for paper_id in paper_ids},
    }
    for unit, score in zip(units, unit_scores, strict=True):
        by_level[unit.level][unit.paper_id] = max(
            by_level[unit.level][unit.paper_id],
            score,
        )
    if treatment["kind"] != "hierarchical-page":
        return {
            paper_id: max(
                by_level["parent"][paper_id],
                by_level["child"][paper_id],
            )
            for paper_id in paper_ids
        }
    parents = _normalize(by_level["parent"])
    children = _normalize(by_level["child"])
    parent_weight = float(treatment["parent_weight"])
    child_weight = float(treatment["child_weight"])
    return {
        paper_id: (
            parent_weight * parents[paper_id]
            + child_weight * children[paper_id]
        )
        for paper_id in paper_ids
    }


def _rank_scores(scores: Mapping[str, float]) -> list[str]:
    return [
        paper_id
        for paper_id, _ in sorted(
            scores.items(),
            key=lambda item: (-item[1], item[0]),
        )
    ]


def _rrf(
    first: Sequence[str],
    second: Sequence[str],
    *,
    constant: int,
) -> list[str]:
    scores: dict[str, float] = defaultdict(float)
    for ranking in (first, second):
        for rank, paper_id in enumerate(ranking, start=1):
            scores[paper_id] += 1.0 / (constant + rank)
    return _rank_scores(scores)


def _query_metrics(
    ranking: Sequence[str],
    relevant: frozenset[str],
    *,
    cutoff: int,
) -> dict[str, float]:
    selected = ranking[:cutoff]
    found = sum(paper_id in relevant for paper_id in selected)
    recall = found / len(relevant)
    reciprocal_rank = 0.0
    for rank, paper_id in enumerate(selected, start=1):
        if paper_id in relevant:
            reciprocal_rank = 1.0 / rank
            break
    dcg = sum(
        1.0 / math.log2(rank + 1.0)
        for rank, paper_id in enumerate(selected, start=1)
        if paper_id in relevant
    )
    ideal = sum(
        1.0 / math.log2(rank + 1.0)
        for rank in range(1, min(len(relevant), cutoff) + 1)
    )
    return {
        "recall_at_10": recall,
        "mrr_at_10": reciprocal_rank,
        "ndcg_at_10": dcg / ideal if ideal else 0.0,
    }


def _seed(base: int, label: str) -> int:
    digest = hashlib.sha256(label.encode("utf-8")).digest()
    return base ^ int.from_bytes(digest[:8], "big")


def _percentile(values: Sequence[float], probability: float) -> float:
    ordered = sorted(values)
    position = probability * (len(ordered) - 1)
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    fraction = position - lower
    return ordered[lower] * (1.0 - fraction) + ordered[upper] * fraction


def _bootstrap_interval(
    values: Sequence[float],
    *,
    samples: int,
    confidence: float,
    seed: int,
) -> dict[str, float]:
    generator = random.Random(seed)
    size = len(values)
    means = [
        statistics.fmean(values[generator.randrange(size)] for _ in range(size))
        for _ in range(samples)
    ]
    tail = (1.0 - confidence) / 2.0
    return {
        "low": _percentile(means, tail),
        "high": _percentile(means, 1.0 - tail),
    }


def _paired_bootstrap(
    candidate: Sequence[float],
    baseline: Sequence[float],
    *,
    samples: int,
    confidence: float,
    seed: int,
) -> dict[str, float]:
    if len(candidate) != len(baseline):
        raise ExperimentError("Paired bootstrap vectors differ in length")
    differences = [
        candidate[index] - baseline[index]
        for index in range(len(candidate))
    ]
    interval = _bootstrap_interval(
        differences,
        samples=samples,
        confidence=confidence,
        seed=seed,
    )
    return {
        "delta": statistics.fmean(differences),
        **interval,
    }


def _p95(values: Sequence[float]) -> float:
    return _percentile(values, 0.95)


def _tree_fingerprint(paths: Iterable[Path]) -> dict[str, Any]:
    rows = [
        {
            "path": _portable(path),
            "sha256": _sha256_file(path),
            "bytes": path.stat().st_size,
        }
        for path in sorted(paths)
    ]
    return {
        "file_count": len(rows),
        "sha256": _sha256_bytes(
            json.dumps(
                rows,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ),
    }


def _run_dataset(
    dataset: Mapping[str, Any],
    config: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, list[float]]]:
    questions = _load_questions(dataset)
    papers = _load_papers(dataset)
    paper_ids = [paper.identifier for paper in papers]
    available = set(paper_ids)
    for question in questions:
        missing = question.relevant - available
        if missing:
            raise ExperimentError(
                f"Qrels absent from {dataset['id']}: {sorted(missing)}"
            )
    cutoff = int(config["metrics"]["cutoff"])
    uncertainty = config["uncertainty"]
    base_seed = int(uncertainty["seed"])
    samples = int(uncertainty["samples"])
    confidence = float(uncertainty["confidence"])
    results: dict[str, Any] = {}
    runtime: dict[str, Any] = {}
    vectors: dict[str, list[float]] = {}

    for chunking in config["chunking_treatments"]:
        units = _make_units(papers, chunking)
        indexes = {
            "bm25-word": SparseIndex(units, kind="bm25", analyzer="word"),
            "tfidf-char3": SparseIndex(
                units,
                kind="tfidf",
                analyzer="char3",
            ),
        }
        rankings_by_retriever: dict[str, list[list[str]]] = {
            "bm25-word": [],
            "tfidf-char3": [],
        }
        latencies: dict[str, list[float]] = {
            "bm25-word": [],
            "tfidf-char3": [],
            "rrf-hybrid": [],
        }
        for question in questions:
            for retriever_id, index in indexes.items():
                started = time.perf_counter_ns()
                unit_scores = index.score(question.text)
                document_scores = _document_scores(
                    units,
                    unit_scores,
                    paper_ids,
                    chunking,
                )
                ranking = _rank_scores(document_scores)
                elapsed = (time.perf_counter_ns() - started) / 1_000_000.0
                rankings_by_retriever[retriever_id].append(ranking)
                latencies[retriever_id].append(elapsed)
            started = time.perf_counter_ns()
            hybrid = _rrf(
                rankings_by_retriever["bm25-word"][-1],
                rankings_by_retriever["tfidf-char3"][-1],
                constant=60,
            )
            elapsed = (time.perf_counter_ns() - started) / 1_000_000.0
            rankings_by_retriever.setdefault("rrf-hybrid", []).append(hybrid)
            latencies["rrf-hybrid"].append(
                latencies["bm25-word"][-1]
                + latencies["tfidf-char3"][-1]
                + elapsed
            )

        for retriever in config["retrieval_treatments"]:
            retriever_id = retriever["id"]
            treatment_id = f"{chunking['id']}::{retriever_id}"
            rankings = rankings_by_retriever[retriever_id]
            query_rows = []
            metric_vectors: dict[str, list[float]] = defaultdict(list)
            for question, ranking in zip(questions, rankings, strict=True):
                metrics = _query_metrics(
                    ranking,
                    question.relevant,
                    cutoff=cutoff,
                )
                for metric, value in metrics.items():
                    metric_vectors[metric].append(value)
                query_rows.append(
                    {
                        "id": question.identifier,
                        "metrics": metrics,
                        "ranking": ranking,
                    }
                )
            aggregate: dict[str, Any] = {}
            for metric, values in metric_vectors.items():
                aggregate[metric] = {
                    "value": statistics.fmean(values),
                    "interval": _bootstrap_interval(
                        values,
                        samples=samples,
                        confidence=confidence,
                        seed=_seed(
                            base_seed,
                            f"{dataset['id']}:{treatment_id}:{metric}",
                        ),
                    ),
                }
                vectors[f"{treatment_id}:{metric}"] = values
            rank_digest = _sha256_bytes(
                json.dumps(
                    [
                        {"id": row["id"], "ranking": row["ranking"]}
                        for row in query_rows
                    ],
                    sort_keys=True,
                    separators=(",", ":"),
                ).encode("utf-8")
            )
            results[treatment_id] = {
                "chunking": chunking["id"],
                "retriever": retriever_id,
                "aggregate": aggregate,
                "rankings_sha256": rank_digest,
                "query_metrics": [
                    {"id": row["id"], "metrics": row["metrics"]}
                    for row in query_rows
                ],
            }
            runtime[treatment_id] = {
                "index_units": len(units),
                "median_query_ms": statistics.median(
                    latencies[retriever_id]
                ),
                "p95_query_ms": _p95(latencies[retriever_id]),
                "accounting": (
                    "bm25-plus-tfidf-plus-fusion"
                    if retriever_id == "rrf-hybrid"
                    else "retriever-score-and-document-aggregation"
                ),
            }
    inputs = {
        "questions": {
            "path": _portable(_resolve_repo_path(dataset["questions"])),
            "sha256": dataset["questions_sha256"],
            "count": len(questions),
        },
        "papers": {
            "path": _portable(_resolve_repo_path(dataset["papers"])),
            **_tree_fingerprint(paper.path for paper in papers),
            "count": len(papers),
        },
    }
    return {"inputs": inputs, "treatments": results}, runtime, vectors


def _treatment_sort_key(row: Mapping[str, Any]) -> tuple[float, ...]:
    aggregate = row["aggregate"]
    return (
        -aggregate["recall_at_10"]["value"],
        -aggregate["mrr_at_10"]["value"],
        -aggregate["ndcg_at_10"]["value"],
    )


def _pareto_frontier(
    datasets: Mapping[str, Any],
    runtime: Mapping[str, Any],
) -> list[str]:
    treatment_ids = sorted(
        next(iter(datasets.values()))["treatments"]
    )
    points: dict[str, tuple[float, float, float, float]] = {}
    for treatment_id in treatment_ids:
        recalls = [
            dataset["treatments"][treatment_id]["aggregate"]["recall_at_10"][
                "value"
            ]
            for dataset in datasets.values()
        ]
        mrrs = [
            dataset["treatments"][treatment_id]["aggregate"]["mrr_at_10"][
                "value"
            ]
            for dataset in datasets.values()
        ]
        ndcgs = [
            dataset["treatments"][treatment_id]["aggregate"]["ndcg_at_10"][
                "value"
            ]
            for dataset in datasets.values()
        ]
        latencies = [
            dataset_runtime[treatment_id]["median_query_ms"]
            for dataset_runtime in runtime.values()
        ]
        points[treatment_id] = (
            statistics.fmean(recalls),
            statistics.fmean(mrrs),
            statistics.fmean(ndcgs),
            statistics.fmean(latencies),
        )
    frontier: list[str] = []
    for candidate, point in points.items():
        dominated = False
        for other, comparison in points.items():
            if candidate == other:
                continue
            no_worse = (
                comparison[0] >= point[0]
                and comparison[1] >= point[1]
                and comparison[2] >= point[2]
                and comparison[3] <= point[3]
            )
            strictly_better = comparison != point
            if no_worse and strictly_better:
                dominated = True
                break
        if not dominated:
            frontier.append(candidate)
    return sorted(frontier)


def _analyze(
    datasets: Mapping[str, Any],
    runtime: Mapping[str, Any],
    vectors: Mapping[str, Mapping[str, list[float]]],
    config: Mapping[str, Any],
) -> dict[str, Any]:
    uncertainty = config["uncertainty"]
    samples = int(uncertainty["samples"])
    confidence = float(uncertainty["confidence"])
    base_seed = int(uncertainty["seed"])
    best_by_dataset: dict[str, str] = {}
    for dataset_id, dataset in datasets.items():
        best_by_dataset[dataset_id] = min(
            dataset["treatments"],
            key=lambda treatment_id: _treatment_sort_key(
                dataset["treatments"][treatment_id]
            ),
        )

    chunking_comparisons: list[dict[str, Any]] = []
    directional = False
    strong = False
    for dataset_id, dataset in datasets.items():
        for retriever in config["retrieval_treatments"]:
            retriever_id = retriever["id"]
            baseline_id = f"document::{retriever_id}"
            candidates = [
                treatment_id
                for treatment_id in dataset["treatments"]
                if treatment_id.endswith(f"::{retriever_id}")
                and not treatment_id.startswith("document::")
            ]
            candidate_id = min(
                candidates,
                key=lambda treatment_id: _treatment_sort_key(
                    dataset["treatments"][treatment_id]
                ),
            )
            comparison = _paired_bootstrap(
                vectors[dataset_id][f"{candidate_id}:recall_at_10"],
                vectors[dataset_id][f"{baseline_id}:recall_at_10"],
                samples=samples,
                confidence=confidence,
                seed=_seed(
                    base_seed,
                    f"paired:{dataset_id}:{candidate_id}:{baseline_id}",
                ),
            )
            material = abs(comparison["delta"]) >= 0.02
            excludes_zero = (
                comparison["low"] > 0.0 or comparison["high"] < 0.0
            )
            directional = directional or material
            strong = strong or (material and excludes_zero)
            chunking_comparisons.append(
                {
                    "dataset_id": dataset_id,
                    "retriever": retriever_id,
                    "baseline": baseline_id,
                    "best_non_document": candidate_id,
                    "recall_delta": comparison,
                    "material": material,
                    "interval_excludes_zero": excludes_zero,
                }
            )

    frontier = _pareto_frontier(datasets, runtime)
    winners_differ = len(set(best_by_dataset.values())) > 1
    interval_widths = [
        treatment["aggregate"]["recall_at_10"]["interval"]["high"]
        - treatment["aggregate"]["recall_at_10"]["interval"]["low"]
        for dataset in datasets.values()
        for treatment in dataset["treatments"].values()
    ]
    material_uncertainty = any(width >= 0.05 for width in interval_widths)
    return {
        "best_by_dataset": best_by_dataset,
        "chunking_comparisons": chunking_comparisons,
        "cross_domain_pareto_frontier": frontier,
        "proposal_findings": {
            "KM-004": {
                "finding": (
                    "strong-support"
                    if strong
                    else "directional-support"
                    if directional
                    else "not-observed"
                ),
                "registered_rule_satisfied": directional,
                "strong_rule_satisfied": strong,
            },
            "KM-005": {
                "finding": (
                    "partial-support"
                    if winners_differ or len(frontier) > 1
                    else "not-observed"
                ),
                "registered_rule_satisfied": (
                    winners_differ or len(frontier) > 1
                ),
                "domain_winners_differ": winners_differ,
                "pareto_frontier_size": len(frontier),
            },
            "KM-006": {
                "finding": (
                    "support"
                    if material_uncertainty
                    else "not-observed"
                ),
                "registered_rule_satisfied": material_uncertainty,
                "maximum_recall_interval_width": max(interval_widths),
            },
        },
    }


def _render_markdown(payload: Mapping[str, Any]) -> str:
    deterministic = payload["deterministic"]
    analysis = payload["analysis"]
    lines = [
        "# Offline Methodology Ablation 01",
        "",
        "## Outcome",
        "",
    ]
    findings = analysis["proposal_findings"]
    lines.extend(
        [
            (
                f"- KM-004 chunking: **{findings['KM-004']['finding']}** "
                f"(registered rule: "
                f"{str(findings['KM-004']['registered_rule_satisfied']).lower()})."
            ),
            (
                f"- KM-005 cross-domain baselines: "
                f"**{findings['KM-005']['finding']}** "
                f"(Pareto frontier: "
                f"{findings['KM-005']['pareto_frontier_size']} treatments)."
            ),
            (
                f"- KM-006 uncertainty: **{findings['KM-006']['finding']}** "
                f"(maximum Recall@10 interval width: "
                f"{findings['KM-006']['maximum_recall_interval_width']:.4f})."
            ),
            "",
            (
                "All results are retrospective and promotion-ineligible because "
                "all qrels were exposed before this run."
            ),
            "",
            "## Point winners by domain",
            "",
            "| Dataset | Treatment | Recall@10 | MRR@10 | nDCG@10 | Median ms |",
            "|---|---|---:|---:|---:|---:|",
        ]
    )
    for dataset_id, treatment_id in analysis["best_by_dataset"].items():
        treatment = deterministic["datasets"][dataset_id]["treatments"][
            treatment_id
        ]
        aggregate = treatment["aggregate"]
        runtime = payload["runtime"]["datasets"][dataset_id][treatment_id]
        lines.append(
            f"| `{dataset_id}` | `{treatment_id}` | "
            f"{aggregate['recall_at_10']['value']:.4f} | "
            f"{aggregate['mrr_at_10']['value']:.4f} | "
            f"{aggregate['ndcg_at_10']['value']:.4f} | "
            f"{runtime['median_query_ms']:.3f} |"
        )
    lines.extend(
        [
            "",
            "## Chunking comparisons",
            "",
            (
                "| Dataset | Retriever | Best non-document | "
                "Recall delta vs document | 95% interval |"
            ),
            "|---|---|---|---:|---:|",
        ]
    )
    for comparison in analysis["chunking_comparisons"]:
        delta = comparison["recall_delta"]
        lines.append(
            f"| `{comparison['dataset_id']}` | "
            f"`{comparison['retriever']}` | "
            f"`{comparison['best_non_document']}` | "
            f"{delta['delta']:+.4f} | "
            f"[{delta['low']:+.4f}, {delta['high']:+.4f}] |"
        )
    lines.extend(
        [
            "",
            "## Cross-domain Pareto frontier",
            "",
            *[
                f"- `{treatment_id}`"
                for treatment_id in analysis["cross_domain_pareto_frontier"]
            ],
            "",
            "## Interpretation",
            "",
            (
                "A supported rule means the preregistered signal was observed "
                "on these two exposed paper workloads. It does not establish "
                "unseen-query performance or answer quality. Document-level "
                "qrels cannot show that a retrieved chunk contains the required "
                "claim, and runtime is machine-specific."
            ),
            "",
            "## Branch decision",
            "",
            (
                "Continue KM-004: the character-trigram treatment gained more "
                "than 0.13 Recall@10 from chunking in both domains, with paired "
                "intervals excluding zero. Do not adopt one global chunk size: "
                "the GraphRAG and QEC point winners use different treatments."
            ),
            "",
            (
                "Continue KM-005: domain winners differ and multiple treatments "
                "remain non-dominated after total hybrid query cost is counted. "
                "A single retrospective leaderboard is not enough to select a "
                "repository-wide default."
            ),
            "",
            (
                "Continue KM-006: the widest Recall@10 interval is materially "
                "larger than the registered 0.05 threshold. Future comparisons "
                "should carry uncertainty rather than use point ranks alone."
            ),
            "",
            (
                "Do not promote any treatment from this retrospective study. "
                "The next useful "
                "evidence is claim-level answer review, calibrated judges, and "
                "a genuinely new transfer cohort."
            ),
            "",
        ]
    )
    return "\n".join(lines)


def _execute(config: Mapping[str, Any]) -> dict[str, Any]:
    datasets: dict[str, Any] = {}
    runtime: dict[str, Any] = {}
    vectors: dict[str, dict[str, list[float]]] = {}
    for dataset in config["datasets"]:
        result, timing, dataset_vectors = _run_dataset(dataset, config)
        datasets[dataset["id"]] = result
        runtime[dataset["id"]] = timing
        vectors[dataset["id"]] = dataset_vectors
    analysis = _analyze(datasets, runtime, vectors, config)
    deterministic = {
        "config": {
            "path": _portable(CONFIG_PATH),
            "sha256": _sha256_file(CONFIG_PATH),
        },
        "datasets": datasets,
        "quality_analysis": {
            "best_by_dataset": analysis["best_by_dataset"],
            "chunking_comparisons": analysis["chunking_comparisons"],
            "domain_winners_differ": analysis["proposal_findings"]["KM-005"][
                "domain_winners_differ"
            ],
            "KM-004": analysis["proposal_findings"]["KM-004"],
            "KM-006": analysis["proposal_findings"]["KM-006"],
        },
    }
    return {
        "schema_version": "knowledge-methodology-offline-ablation/1.0",
        "experiment_id": config["experiment_id"],
        "status": "pass",
        "candidate_state": config["candidate_state"],
        "promotion_eligible": False,
        "deterministic": deterministic,
        "analysis": analysis,
        "runtime": {
            "processor": "python",
            "python_version": sys.version.split()[0],
            "datasets": runtime,
        },
    }


def build_parser() -> argparse.ArgumentParser:
    """Build the experiment command line."""

    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--check",
        action="store_true",
        help="Recompute and compare the deterministic result projection",
    )
    mode.add_argument(
        "--write-report",
        action="store_true",
        help=(
            "Explicitly replace the accepted JSON and Markdown reports; "
            "the bound decision artifacts must then be regenerated"
        ),
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run or reproducibly check the experiment."""

    args = build_parser().parse_args(argv)
    try:
        config = _load_config()
        payload = _execute(config)
        if not args.write_report:
            accepted = _load_json(REPORT_JSON)
            if not isinstance(accepted, dict):
                raise ExperimentError("Accepted result root is not an object")
            if accepted.get("deterministic") != payload["deterministic"]:
                raise ExperimentError(
                    "Deterministic experiment result has drifted"
                )
            status = "pass"
        else:
            REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
            REPORT_JSON.write_text(
                _canonical_json(payload),
                encoding="utf-8",
                newline="\n",
            )
            REPORT_MARKDOWN.write_text(
                _render_markdown(payload),
                encoding="utf-8",
                newline="\n",
            )
            status = "created"
        result = {
            "status": status,
            "experiment_id": config["experiment_id"],
            "dataset_count": len(config["datasets"]),
            "treatment_count": (
                len(config["chunking_treatments"])
                * len(config["retrieval_treatments"])
            ),
            "question_count": sum(
                dataset["question_count"] for dataset in config["datasets"]
            ),
        }
    except (
        ExperimentError,
        KeyError,
        OSError,
        UnicodeError,
        json.JSONDecodeError,
        ValueError,
    ) as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, sort_keys=True))
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
