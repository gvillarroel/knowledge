"""Closed, source-generic construction and consultation mutation inventory."""
from __future__ import annotations

import argparse
import copy
import json
import math
import re
from collections import Counter
from pathlib import Path

FAMILIES = ("legacy", "embeddings", "classical", "adaptive", "entity-graph", "ensemble", "graphify", "turso")
CONSTRUCTION = {"embeddings", "classical", "adaptive", "entity-graph", "ensemble"}
MODEL = {"provider": "sentence-transformers", "model_id": "sentence-transformers/all-MiniLM-L6-v2", "revision": "1110a243fdf4706b3f48f1d95db1a4f5529b4d41", "dimension": 384, "normalize": True}


def baseline_profile():
    """Carry each family's best fully measured historical Enterprise profile."""
    value = {family: {"plan": {}, "search": {}} for family in FAMILIES}
    value["embeddings"]["plan"]["embedding"] = MODEL.copy()
    value["ensemble"]["plan"]["embedding.embedding"] = MODEL.copy()
    value["ensemble"]["plan"]["adaptive.bm25.title_weight"] = 4.0
    value["classical"]["plan"].update({"expansion.association_weight": 0.0875, "expansion.topic_weight": 0.05})
    value["adaptive"]["plan"]["bm25.b"] = 0.25
    value["entity-graph"]["plan"]["bm25.b"] = 0.25
    return value


def strategy(identifier, rationale, variants):
    return {"id": identifier, "rationale": rationale, "variants": variants}


def inventory(family):
    """Return a finite, ordered universe; stop each strategy after three misses."""
    if family not in FAMILIES:
        raise ValueError("Unknown knowledge family")
    if family in {"legacy", "turso"}:
        return [
            strategy("bm25-saturation", "Test term saturation against unbounded overlap on long enterprise records.", [{"engine": "bm25", "k1": x} for x in (1.2, 0.6, 2.0, 3.0)]),
            strategy("length-normalization", "Test sensitivity to heterogeneous record lengths.", [{"engine": "bm25", "b": x} for x in (0.25, 0.0, 0.5, 1.0)]),
            strategy("title-weight", "Test whether descriptive titles improve lexical evidence discovery.", [{"engine": "bm25", "title_weight": x} for x in (2.0, 4.0, 8.0)]),
        ]
    if family == "graphify":
        return [
            strategy("traversal-depth", "Test graph neighborhood reach while preserving native node ranking.", [{"depth": x} for x in (0, 1, 3, 4, 5, 6)]),
            strategy("lexical-graph-fusion", "Test complementary lexical discovery fused with native graph candidates.", [{"lexical_weight": x} for x in (0.5, 1.0, 2.0, 4.0)]),
            strategy("fusion-rank-decay", "Test reciprocal-rank decay with the retained lexical-graph mix.", [{"lexical_weight": 1.0, "rrf_k": x} for x in (5, 20, 60)]),
        ]
    if family == "embeddings":
        return [strategy("semantic-segmentation", "Test local semantic passages instead of truncating long records into one vector.", [{"chunking.strategy": "semantic", "chunking.breakpoint_percentile_threshold": x} for x in (95, 90, 80, 70, 50)]),
                strategy("semantic-context", "Test neighboring sentence context at a fixed semantic threshold.", [{"chunking.strategy": "semantic", "chunking.buffer_size": x} for x in (2, 3, 4)])]
    prefix = "adaptive." if family == "ensemble" else ""
    items = [
        strategy("length-normalization", "Reduce long-record penalties without changing authoritative evidence.", [{prefix + "bm25.b": x} for x in (0.25, 0.0, 0.5, 1.0)]),
        strategy("bm25-saturation", "Test saturation of repeated enterprise terminology.", [{prefix + "bm25.k1": x} for x in (0.6, 2.0, 3.0)]),
    ]
    if family == "entity-graph":
        return items + [
            strategy("graph-reach", "Test how many extraction links remain useful for discovery.", [{"query.max_hops": x} for x in (1, 2, 4)]),
            strategy("graph-noise", "Test candidate-edge trust without changing evidence authority.", [{"query.candidate_edge_weight": x} for x in (0.0, 0.1, 0.6)]),
            strategy("section-granularity", "Test bounded graph sections on heterogeneous document lengths.", [{"sectioning.maximum_characters": x} for x in (6000, 3000, 18000)]),
        ]
    items += [
        strategy("title-weight", "Test title emphasis independently from record body evidence.", [{prefix + "bm25.title_weight": x} for x in (4.0, 8.0, 1.0)]),
        strategy("expansion-strength", "Reduce or increase unsupervised expansion noise.", [{prefix + "expansion.association_weight": 0.35*x, prefix + "expansion.topic_weight": 0.2*x} for x in (0.25, 0.0, 0.5, 2.0)]),
        strategy("relevance-diversity", "Test relevance against topic/source novelty at a constant candidate pool.", [{prefix + "reranking.relevance_weight": x, prefix + "reranking.topic_novelty_weight": (1-x)/2, prefix + "reranking.source_novelty_weight": (1-x)/2} for x in (1.0, 0.9, 0.5)]),
    ]
    if family == "adaptive":
        items.append(strategy("aspect-allocation", "Test the contribution of decomposed query aspects.", [{"adaptive.aspect_weight": x} for x in (0.0, 0.5, 1.0)]))
    if family == "ensemble":
        items.append(strategy("ensemble-allocation", "Increase the contribution of the previously useful learned representation.", [{"policies.quality.weights": x} for x in ([4, 1, 5, 3], [2, 1, 3, 5], [1, 1, 1, 8])]))
    return items


def mutate(parent, family, variant):
    result = copy.deepcopy(parent)
    channel = "plan" if family in CONSTRUCTION else "search"
    result[family][channel].update(copy.deepcopy(variant))
    return result


def apply_plan(plan, profile, family):
    result = copy.deepcopy(plan)
    for path, value in profile[family]["plan"].items():
        node = result
        parts = path.split(".")
        for part in parts[:-1]:
            node = node[part]
        if parts[-1] not in node:
            raise ValueError("Mutation cannot invent a plan field: " + path)
        node[parts[-1]] = copy.deepcopy(value)
    return result


def tokens(value):
    return [word.lower() for word in re.findall(r"[A-Za-z0-9]+", value) if len(word) >= 2]


class LexicalIndex:
    """Deterministic BM25 over record text; returned evidence is always original."""
    def __init__(self, records, settings):
        self.settings = settings
        self.records = sorted(records, key=lambda row: row["record_id"])
        title_weight = settings.get("title_weight", 1.0)
        self.counts = []
        frequency = Counter()
        for row in self.records:
            count = Counter(tokens(str(row.get("body", ""))))
            for token, number in Counter(tokens(str(row.get("title", "")))).items():
                count[token] += number * title_weight
            self.counts.append(count)
            frequency.update(count.keys())
        self.lengths = [sum(count.values()) for count in self.counts]
        self.average = sum(self.lengths) / max(1, len(self.lengths)) or 1.0
        n = len(self.records)
        self.idf = {token: math.log(1 + (n - seen + 0.5)/(seen + 0.5)) for token, seen in frequency.items()}

    def search(self, query, limit=10):
        k1, b = self.settings.get("k1", 1.2), self.settings.get("b", 0.75)
        ranked = []
        for row, count, length in zip(self.records, self.counts, self.lengths):
            score = 0.0
            for token in sorted(set(tokens(query))):
                tf = count.get(token, 0)
                if tf:
                    score += self.idf[token] * tf * (k1+1) / (tf + k1*(1-b+b*length/self.average))
            if score > 0:
                ranked.append((-score, row["record_id"], row))
        ranked.sort(key=lambda item: (item[0], item[1]))
        return [row for _, _, row in ranked[:limit]]


def fuse(graph, lexical, settings):
    weight, decay = settings.get("lexical_weight", 0.0), settings.get("rrf_k", 60)
    scores, rows = {}, {}
    for values, factor in ((graph, 1.0), (lexical, weight)):
        for rank, row in enumerate(values, 1):
            key = row["record_id"]
            rows[key] = row
            scores[key] = scores.get(key, 0.0) + factor / (decay + rank)
    return [rows[key] for key in sorted(scores, key=lambda key: (-scores[key], key))[:10]]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--family", choices=FAMILIES, required=True)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    profile = json.loads((Path(__file__).resolve().parents[1]/"assets/retrieval-profile.json").read_text())
    with args.output.open("x", encoding="utf-8") as output:
        json.dump(apply_plan(json.loads(args.input.read_text()), profile, args.family), output, sort_keys=True, allow_nan=False)


if __name__ == "__main__":
    main()
