---
type: Agent Skill
title: Consult Semantic OKF Tika + MALLET + Tantivy
description: Inspect and consult an immutable Semantic OKF snapshot whose heterogeneous
  local documents were extracted by Apache Tika 4.0.0-beta-1 and modeled with Java
  MALLET 2.1.0, using Tantivy 0.26.0 native Rust BM25 for in-memory lexical ranking
  plus MALLET topic expansion, PPMI association search, and reciprocal-rank fusion.
  Use for format-aware provenance review, fast model-free search, topic-assisted discovery,
  retrieval comparison, or exact grounded reading of a Tika/MALLET snapshot. This
  standalone skill is read-only and never builds, repairs, refreshes, or modifies
  knowledge.
tags:
- codex
- skill
skill_name: consult-semantic-okf-tika-mallet-tantivy
source_path: skills/consult-semantic-okf-tika-mallet-tantivy/SKILL.md
---

# Consult Semantic OKF with Tika, MALLET, and Tantivy

Validate the complete Tika extraction and MALLET projection, rank filtered passages
through an ephemeral Tantivy index, and ground every factual statement in an
authoritative Semantic OKF concept, ledger record, or selected RDF graph.

## Standalone and read-only boundary

- Use only this directory's instructions, references, scripts, and requirements.
- Treat the supplied bundle and optional Java/MALLET paths as explicit external inputs.
- Do not import a sibling skill, repository helper, evaluation fixture, or root file.
- Never write an index, cache, query, answer, lock, repair, or sidecar into the bundle.
- Build Tantivy only in memory after applying all source, concept, and type filters.
- Do not re-extract raw sources. The Tika receipt proves their identity but does not
  contain the original binaries.
- Stop on a stale hash, closed-schema violation, symlink, unsafe path, Tika/ledger
  mismatch, MALLET inconsistency, orphan passage, invalid locator, unsupported BM25
  settings, Tantivy version drift, or failing report.
- Treat Tika metadata as provenance and all Tantivy scores, MALLET topics, PPMI
  associations, fusion ranks, and reranking values as non-authoritative discovery data.

## Required references

- Read [tika-mallet-format.md](../../skills/consult-semantic-okf-tika-mallet-tantivy/references/tika-mallet-format.md) before integrity
  review, deep validation, or diagnosis.
- Read [tantivy-runtime.md](../../skills/consult-semantic-okf-tika-mallet-tantivy/references/tantivy-runtime.md) before installing or
  diagnosing the native dependency.
- Read [querying.md](../../skills/consult-semantic-okf-tika-mallet-tantivy/references/querying.md) before selecting a mode, using syntax,
  applying filters, interpreting expansions, or citing results.

## Workflow

1. Install the pinned dependencies outside the snapshot and run runtime preflight.
2. Inspect the bundle. Require a passing authoritative build, a closed Tika receipt,
   Tika-to-ledger parity, a closed MALLET projection, valid hashes and statistics,
   exact paths and locators, supported `k1=1.2` and `b=0.75`, and Tantivy `0.26.0`.
3. For a new, release-critical, or evaluation snapshot, run deep validation once
   with explicit Java 17+ and the exact hash-bound MALLET `2.1.0` distribution.
   Retrain only in temporary storage outside the immutable bundle.
4. Apply filters before indexing. Use `tantivy` for exact lexical discovery,
   `topic` for MALLET-assisted vocabulary, `association` for PPMI neighbors, or
   `fusion` to combine all three rankings. Preserve the requested and effective mode.
5. Prefer one `batch-search` for several broad queries. For a bounded answer, use
   one `answer-pack` call, draft claims with its support IDs, then run
   `finalize-answer`. Write these derived JSON files only to new paths outside the
   bundle.
6. Open each selected `concept_path`, resolve the locator against
   `semantic/records.jsonl`, and verify returned text and hashes.
7. Use the ledger for exact metadata and purpose-selected RDF graphs for joins,
   aggregation, schema, lineage, shapes, or validation.
8. Cite authoritative paths and locators. Never cite a score, topic, association,
   extraction guess, or model memory as factual support.

## Environment and inspection

```bash
python -m pip install -r scripts/requirements.txt
python -B scripts/runtime_smoke.py
python -B scripts/query_semantic_okf_tika_mallet_tantivy.py BUNDLE inspect
```

Deep inspection requires the exact MALLET runtime bound in the snapshot:

```bash
python -B scripts/runtime_smoke.py --java JAVA --mallet-home MALLET_HOME
python -B scripts/query_semantic_okf_tika_mallet_tantivy.py BUNDLE inspect \
  --deep-validation --java JAVA --mallet-home MALLET_HOME
```

Ordinary inspection and search require neither Java nor Tika. Deep validation
requires Java and MALLET but validates the persisted Tika receipt rather than
re-extracting source files.

## Search

Native Tantivy BM25 with syntax-free query normalization:

```bash
python -B scripts/query_semantic_okf_tika_mallet_tantivy.py BUNDLE search \
  --query "invoice 2026-041" --mode tantivy --top-k 10
```

MALLET topic-assisted retrieval:

```bash
python -B scripts/query_semantic_okf_tika_mallet_tantivy.py BUNDLE search \
  --query "document retention and audit evidence" --mode topic --top-k 10
```

PPMI association retrieval:

```bash
python -B scripts/query_semantic_okf_tika_mallet_tantivy.py BUNDLE search \
  --query "spreadsheet validation" --mode association --top-k 10
```

Reciprocal-rank fusion of native Tantivy, association, and topic routes:

```bash
python -B scripts/query_semantic_okf_tika_mallet_tantivy.py BUNDLE search \
  --query "compare extraction acceptance criteria" --mode fusion --top-k 10
```

Use Tantivy query syntax only when intentional. Quoted phrases, field selectors,
grouping, and uppercase Boolean operators preserve explicit syntax; regex queries
are disabled. Syntax-free natural text is bounded to the persisted unigram lexicon.

Repeat `--source-id`, `--concept-id`, or `--concept-type` to form a union within one
filter kind. Different filter kinds combine with logical AND.

## Bounded grounding

```bash
python -B scripts/query_semantic_okf_tika_mallet_tantivy.py BUNDLE answer-pack \
  --query "community retrieval" --query "hierarchical synthesis" \
  --query "direct entity or chunk retrieval" --mode fusion --top-k 6 \
  --max-sources 10 --output ANSWER_PACK.json
python -B scripts/query_semantic_okf_tika_mallet_tantivy.py BUNDLE finalize-answer \
  --pack ANSWER_PACK.json --draft ANSWER_DRAFT.json --output FINAL_ANSWER.json
```

Copy support IDs rather than retyping evidence identities. `finalize-answer`
constructs first-use evidence indices and validates exact paths, hashes, locators,
and selected passages. Use `validate-answer` for a manually assembled response.

## Completion gate

Before answering, confirm:

- runtime preflight and structural inspection passed, and evaluation-critical
  snapshots passed independent fixed-seed MALLET rederivation;
- the Tika receipt, generated Semantic plan, ledger attributes, bodies, MALLET
  artifacts, and authoritative core remain mutually hash-bound;
- filters were applied before the pathless Tantivy index was built;
- the output discloses Tantivy `0.26.0`, native Rust BM25, in-memory storage,
  tokenizer, boosts, indexed count, lexical queries, expansions, and modes;
- every cited concept path exists and every locator resolves to the returned text;
- the final structured response passed exact-evidence validation; and
- a before/after path-and-hash inventory proves the bundle did not change.
