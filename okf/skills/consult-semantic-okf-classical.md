---
type: Agent Skill
title: Consult Semantic OKF Classical
description: Consult an existing classical Semantic OKF snapshot through deterministic
  BM25, co-occurrence topic, PPMI association, or reciprocal-rank-fusion retrieval
  with diversity-aware reranking and exact evidence locators. Use when Codex needs
  model-free lexical discovery, query expansion, multi-paper evidence diversity, index
  inspection, or grounded follow-up reading. This standalone skill is read-only and
  never builds, repairs, refreshes, or modifies knowledge.
tags:
- codex
- skill
skill_name: consult-semantic-okf-classical
source_path: skills/consult-semantic-okf-classical/SKILL.md
---

# Consult Semantic OKF Classical

Discover relevant page and claim passages in an immutable Semantic OKF snapshot, then verify every factual statement against an authoritative concept, ledger record, or purpose-selected RDF graph.

## Standalone and read-only boundary

- Use only this directory's instructions, references, scripts, and requirements.
- Treat the supplied bundle as an explicit external input.
- Do not import a sibling skill, repository helper, fixture, or root document.
- Never write a cache, query, answer, lock, repaired file, or derived artifact into the bundle.
- Stop on a stale hash, closed-schema violation, symlink, unsafe path, orphan document, invalid locator, token-statistic mismatch, or failing build report.
- Treat BM25, topic, PPMI, fusion, and reranking scores as discovery signals rather than domain evidence.

## Required references

- Read [classical-format.md](../../skills/consult-semantic-okf-classical/references/classical-format.md) when inspecting integrity or diagnosing a bundle.
- Read [querying.md](../../skills/consult-semantic-okf-classical/references/querying.md) before selecting a mode, interpreting expansion, or citing results.

## Workflow

1. Inspect the snapshot; require a passing core and classical projection. For a newly received or evaluation-critical snapshot, add `--deep-validation` once to independently rederive every document, lexical statistic, PPMI edge, topic, and document-topic weight.
2. Select the cheapest authoritative or discovery layer.
3. Apply source, concept, and type filters before ranking.
4. Use `bm25`, `topic`, `association`, or `fusion` for candidate discovery.
5. Preserve requested/effective mode, query expansions, topic activations, index hashes, and component ranks.
6. Open the exact returned `concept_path`; resolve its locator to authoritative record text.
7. Use the ledger for exact metadata or selected RDF graphs for joins, aggregation, schema, lineage, shapes, or validation.
8. Cite authoritative paths and page locators. Never cite a retrieval score as factual support.

## Environment and inspection

The package uses only the Python standard library:

```bash
python scripts/runtime_smoke.py
python scripts/query_semantic_okf_classical.py BUNDLE inspect
python scripts/query_semantic_okf_classical.py BUNDLE inspect --deep-validation
```

Use `python -B` or set `PYTHONDONTWRITEBYTECODE=1` when the copied skill directory itself must remain byte-for-byte unchanged. The helper does not write inside the bundle.

## Search modes

Exact lexical terminology and identifiers:

```bash
python scripts/query_semantic_okf_classical.py BUNDLE search --query "Prize-Collecting Steiner Tree" --mode bm25 --top-k 10
```

Topic-aware query expansion and topic-diverse evidence:

```bash
python scripts/query_semantic_okf_classical.py BUNDLE search --query "global sensemaking from graph communities" --mode topic --top-k 10
```

Two-step propagation over the PPMI term graph:

```bash
python scripts/query_semantic_okf_classical.py BUNDLE search --query "adaptive traversal and pruning" --mode association --top-k 10
```

Reciprocal-rank fusion of all three independent rankings:

```bash
python scripts/query_semantic_okf_classical.py BUNDLE search --query "compare evidence organization mechanisms" --mode fusion --top-k 10
```

Repeat `--source-id`, `--concept-id`, or `--concept-type` to select a union within that filter. Different filter kinds combine with logical AND.

## Completion gate

Before answering, confirm:

- inspection passed, evaluation-critical snapshots passed independent deep rederivation, and the bundle tree remained unchanged;
- filters were applied before ranking;
- requested and effective mode are identical and disclosed;
- expansion terms and activated topics are visible rather than hidden;
- every cited concept path exists and binds to the returned record;
- every locator resolves to the returned text and text hash;
- factual claims were checked in an authoritative layer; and
- no topic label, association edge, retrieval score, web result, or model memory is presented as ground truth.
