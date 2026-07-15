---
type: Agent Skill
title: Consult Semantic OKF Embeddings
description: Consult an existing embedding-enabled Semantic OKF snapshot through deterministic
  lexical, exact-vector, or hybrid retrieval while preserving exact concept paths
  and read-only authority boundaries. Use when Codex needs semantic discovery, paraphrase
  search, source- or concept-scoped retrieval, index inspection, explicit fallback
  without an embedding runtime, or grounded follow-up reading from a published snapshot.
  This skill never builds, repairs, refreshes, downloads models for, or modifies knowledge.
tags:
- codex
- skill
skill_name: consult-semantic-okf-embeddings
source_path: skills/consult-semantic-okf-embeddings/SKILL.md
---

# Consult Semantic OKF Embeddings

Discover relevant chunks in an immutable Semantic OKF snapshot, then verify claims against its authoritative ledger, concepts, or selected RDF graph.

## Standalone boundary

- Use only this skill's `SKILL.md`, `references/`, `scripts/`, and declared requirements.
- Treat the supplied bundle and any local model cache as explicit external inputs.
- Do not import a sibling skill, repository helper, evaluation fixture, or repository document.
- Keep the standard-library hashing and lexical runtime usable without optional packages.

## Read-only boundary

- Never write a cache, query, lock, model, repaired file, or derived answer into the bundle.
- Require a passing `semantic/build-report.json` and validate the complete retrieval binding before returning any hit.
- Stop on a stale digest, malformed row, orphan chunk, unsafe path, invalid vector, or core-tree mismatch. A corrupt declared index never qualifies for fallback.
- Treat retrieval scores and chunk text as discovery aids, not domain evidence.
- Verify final claims in `semantic/records.jsonl`, the exact returned `concept_path`, or the explicitly selected RDF graph.
- Do not use the web, model recall, or an unmounted corpus when the snapshot is authoritative.

## Workflow

1. Inspect the snapshot and verify its immutable core and retrieval artifacts.
2. Select the cheapest layer for the requested operation.
3. Use lexical, vector, or hybrid search only for conceptual discovery.
4. Apply source and concept filters before ranking.
5. Open the exact returned concept path and verify the relevant locator and text.
6. Use the ledger for exact metadata or RDF for joins, aggregation, schema, lineage, shapes, or validation.
7. Cite authoritative artifacts; never cite a similarity score as support.

Read [retrieval-format.md](../../skills/consult-semantic-okf-embeddings/references/retrieval-format.md) when inspecting integrity or diagnosing a bundle. Read [querying.md](../../skills/consult-semantic-okf-embeddings/references/querying.md) before choosing a search mode or interpreting fallback and scores.

## Environment

Run commands from the directory containing this `SKILL.md`, or prefix script paths with the skill root.

The hashing, lexical, inspection, and validation baseline uses only the Python standard library:

```bash
python scripts/runtime_smoke.py
python scripts/query_semantic_okf_embeddings.py BUNDLE inspect
```

Set `PYTHONDONTWRITEBYTECODE=1` or use `python -B` when the copied skill directory itself must remain byte-for-byte read-only. The consultant never writes inside the supplied bundle.

Install the optional local SentenceTransformers runtime only when the index declares that provider:

```bash
python -m pip install -r scripts/requirements-embeddings.txt
python scripts/runtime_smoke.py --embedding
```

Model weights are not bundled. The helper resolves the exact namespace/repository and immutable revision through `huggingface_hub.snapshot_download(..., local_files_only=True)` under offline flags, verifies that the resolved snapshot directory ends in that commit, and passes only the local path to SentenceTransformers on CPU with remote code disabled. It never chooses a default model or downloads missing weights.

## Choose a consultation layer

1. Use `semantic/records.jsonl` for exact identifiers, types, mapped attributes, counts, and literal paths.
2. Use retrieval search for fuzzy lexical discovery, paraphrases, or candidate ranking.
3. Read the exact `concepts/**/*.md` path returned by a hit for human-readable evidence.
4. Use `semantic/data.ttl` for accepted facts that require joins, traversal, typed filtering, or aggregation.
5. Add `ontology.ttl` only for schema, `provenance.ttl` only for lineage, and use shapes or validation graphs only for their declared contracts.

Do not union RDF graphs by default. Do not use embeddings for exact counts, business identity, conflict resolution, or semantic entailment.

## Inspect

```bash
python scripts/query_semantic_okf_embeddings.py BUNDLE inspect
```

`inspect` requires exactly four regular non-symlink files under `retrieval/`, validates the retrieval build report against the live index and artifacts, then validates raw artifact hashes, the pre-retrieval core-tree digest, record and source bindings, exact concept paths and locators, chunk coverage, vector dimensions and finiteness, normalization tolerance, and sorted one-to-one chunk/vector identities. It reports capabilities and authoritative paths without loading a model.

## Search

Automatic hybrid retrieval with an explicit source filter:

The identifiers below are illustrative. Replace them with source or concept IDs reported by `inspect` for the supplied snapshot.

```bash
python scripts/query_semantic_okf_embeddings.py BUNDLE search \
  --query "retention requirements for accepted records" \
  --mode auto --source-id policies --top-k 5
```

Exact lexical fallback without an embedding runtime:

```bash
python scripts/query_semantic_okf_embeddings.py BUNDLE search \
  --query "INC-2048" --mode lexical --top-k 10
```

Explicit vector search fails when the exact provider is unavailable. Permit a declared lexical fallback only when that behavior is acceptable:

```bash
python scripts/query_semantic_okf_embeddings.py BUNDLE search \
  --query "how access begins for a new employee" \
  --mode vector --allow-fallback --top-k 5
```

Repeat `--source-id`, `--concept-id`, or `--concept-type` to select a union of allowed values within that filter. Different filter kinds combine with logical AND.

## Interpret results

- Check `requested_mode`, `effective_mode`, and `fallback` before using hits.
- Require `discovery_only: true`; it prevents accidental promotion of ranking output to authoritative evidence.
- Preserve the snapshot and retrieval hashes beside any reproducible result.
- Copy `concept_path` and `locator` exactly. Do not reconstruct hashed filenames or approximate character ranges.
- Use component `scores` and `ranks` only to explain retrieval order. Hybrid ranking uses reciprocal-rank fusion rather than incomparable raw-score addition.
- If `returned` is zero, report that the selected retrieval mode and filters found no candidate; do not invent an answer.

## Completion gate

Before answering, confirm:

- inspection passed and the snapshot tree remained unchanged;
- corrupt-index fallback was not used;
- requested and effective modes are disclosed;
- every filter was applied before ranking;
- every cited path exists below the bundle and matches its ledger record;
- every factual statement was verified in an authoritative layer;
- no retrieval score, model output, web result, or guess is presented as evidence.
