---
name: consult-semantic-okf-tantivy
description: Consult an existing classical Semantic OKF snapshot with Tantivy's native Rust BM25 engine, field-aware lexical ranking, syntax-aware natural-query normalization, bounded identity-diversified result selection, pre-ranking filters, and exact authoritative evidence locators. Use when Codex needs fast model-free full-text discovery through Tantivy, comparison with the Python classical BM25 route, or grounded reading of a validated classical snapshot. This standalone skill is read-only and never builds, repairs, refreshes, or modifies knowledge.
---

# Consult Semantic OKF with Tantivy

Use Tantivy's Rust search engine to rank validated classical passages in memory, then verify every factual statement in the authoritative concept, ledger record, or purpose-selected RDF graph.

## Standalone and read-only boundary

- Use only this directory's instructions, references, scripts, and requirements.
- Treat the supplied classical Semantic OKF bundle as an explicit external input.
- Never write an index, cache, query, answer, lock, or repaired artifact into the bundle.
- Build a fresh Tantivy index in memory after applying all requested filters.
- Stop on a stale core binding, closed-schema violation, symlink, unsafe path, orphan passage, invalid locator, artifact hash mismatch, or failing build report.
- Treat Tantivy scores as discovery signals rather than domain evidence.

## Required references

- Read [tantivy-runtime.md](references/tantivy-runtime.md) before installing or diagnosing the pinned native dependency.
- Read [querying.md](references/querying.md) before interpreting query syntax, scores, filters, or evidence.

## Workflow

1. Install the pinned package requirements outside the snapshot.
2. Run the runtime preflight and inspect the bundle.
3. Apply source, concept, and type filters before indexing.
4. Normalize syntax-free natural text against the persisted classical unigram
   lexicon while preserving explicit Tantivy syntax.
5. Search title and passage text through Tantivy BM25. From the bounded native
   candidate pool, seed at most two distinct semantic concept types, then fill
   in native score order while applying the plan's evidence-identity cap.
   Never change the Tantivy scores.
6. Preserve the engine version, tokenizer, boosts, snapshot hashes, score, and exact evidence identity.
7. Open each selected `concept_path` and resolve its locator against `semantic/records.jsonl`.
8. Use the ledger for exact metadata and selected RDF graphs for joins, aggregation, schema, or lineage.
9. Cite authoritative paths and locators; never cite a retrieval score as factual support.

## Environment and inspection

```bash
python -m pip install -r scripts/requirements.txt
python scripts/runtime_smoke.py
python scripts/query_semantic_okf_tantivy.py BUNDLE inspect
```

Use `python -B` or set `PYTHONDONTWRITEBYTECODE=1` when the copied skill directory itself must remain byte-for-byte unchanged. The query helper creates no filesystem index and does not write inside the bundle.

## Search

```bash
python scripts/query_semantic_okf_tantivy.py BUNDLE search \
  --query '"Prize-Collecting Steiner Tree" OR graph retrieval' \
  --top-k 10
```

The query accepts Tantivy query syntax over the `title` and `body` fields. Regular expressions are disabled. Repeat `--source-id`, `--concept-id`, or `--concept-type` to select a union within that filter; different filter kinds combine with logical AND.

The result retains native score order but limits repeated passages using the
classical plan's `candidate_pool` and `max_per_evidence_identity`. It reports
the pool size, cap, identity policy, and number of returned identities.

Inspect `parsed_query` and `engine.query_normalization`. Quoted phrases, field
selectors, grouping, and uppercase Boolean operators bypass natural-query
normalization.

## Completion gate

Before answering, confirm:

- runtime preflight and bundle inspection passed;
- filters were applied before the in-memory index was built;
- the reported engine is pinned Tantivy 0.26.0 with native BM25 scoring;
- every cited concept path exists and binds to the returned record;
- every locator resolves to the returned text and text hash;
- factual claims were checked in an authoritative layer; and
- the bundle tree remained unchanged.
