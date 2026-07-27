---
name: consult-semantic-okf-tika-mallet
description: Inspect and consult an immutable Semantic OKF snapshot whose heterogeneous local documents were extracted by Apache Tika 4.0.0-beta-1 and indexed with Java MALLET 2.1.0. Use for read-only integrity checks, format-aware provenance review, BM25 search, MALLET topic expansion, PPMI association search, reciprocal-rank fusion, or exact grounded follow-up reading. The skill validates Tika-to-ledger parity and treats every topic and retrieval score as non-authoritative; it never builds, repairs, refreshes, or modifies knowledge.
---

# Consult Semantic OKF with Tika and MALLET

Discover exact passages in a validated Tika/MALLET snapshot, then ground every
factual statement in the authoritative Semantic OKF concept, ledger, or selected
RDF graph.

## Standalone and read-only boundary

- Use only this directory's instructions, references, scripts, and requirements.
- Treat the supplied bundle and optional Java/MALLET paths as explicit external inputs.
- Do not import a sibling skill, repository helper, evaluation fixture, or root file.
- Never write a cache, query, answer, lock, repaired file, or derived artifact into
  the bundle.
- Do not re-extract raw sources. The immutable receipt proves their hashes but does
  not include the binaries.
- Stop on a stale hash, closed-schema violation, symlink, unsafe path, Tika/ledger
  mismatch, orphan document, invalid locator, lexical mismatch, or failing report.
- Treat BM25, MALLET topics, PPMI edges, fusion, and reranking as discovery signals,
  not facts.

## Read the relevant references

- Read [tika-mallet-format.md](references/tika-mallet-format.md) before integrity
  review, deep validation, or diagnosis.
- Read [querying.md](references/querying.md) before choosing a mode, interpreting
  expansions, applying filters, or citing results.

## Workflow

1. Inspect the snapshot. This validates the authoritative build report, closed Tika
   receipt, generated ontology and ledger parity, MALLET projection, hashes,
   statistics, topics, paths, and locators without requiring external Java.
   A hybrid receipt may contain explicitly declared UTF-8-verbatim textual sources;
   require their line-ending-only body contract and distinct handler identity.
2. For a newly received, release-critical, or evaluation snapshot, run deep
   validation once with explicit Java 17+ and the exact hash-bound MALLET `2.1.0`
   distribution. It retrains in temporary storage only.
3. Select the least expansive discovery mode and apply source, concept, and type
   filters before ranking. For a time-bounded multi-source answer, use exactly one
   `answer-pack` call with three to five broad queries, `--top-k 6`, and
   `--max-sources 10`. It validates the snapshot once, fuses repeated hits, retains
   at most one passage per source ID, assigns small support IDs, and writes a compact
   exact-evidence pack outside the bundle. Do not use `search`, `batch-search`, ad
   hoc bundle reads, per-source probes, or phrase follow-ups in that workflow. If
   the pack does not support the required answer, return the declared null response.
4. Draft only `question_id`, `summary`, and claims containing `statement` plus
   `support_ids`. Run `finalize-answer` with that draft and the unmodified pack. It
   constructs first-use indices, copies exact evidence, validates the complete
   response, and publishes a new final JSON file outside the bundle. Return that
   file unchanged. Never retype or normalize an ID, path, hash, locator, or evidence
   index.
5. Preserve requested and effective mode, query expansions, activated topics,
   toolchain and index hashes, component ranks, and filters.
6. Open each returned `concept_path` and resolve the exact locator against the
   authoritative ledger text.
7. Use the ledger for exact metadata or a purpose-selected RDF graph for joins,
   schema, lineage, aggregation, shapes, or validation.
8. For a manually assembled structured answer outside the bounded workflow, run
   `validate-answer`. Return it only after the validator confirms first-use ordering
   and exact evidence identities.
9. Cite authoritative paths and locators. Never cite a topic name or score as
   factual evidence.

## Environment and inspection

Install the single pinned Python dependency, then inspect:

```bash
python -m pip install -r scripts/requirements.txt
python -B scripts/runtime_smoke.py
python -B scripts/query_semantic_okf_tika_mallet.py BUNDLE inspect
```

Deep inspection requires the exact MALLET runtime bound in the snapshot:

```bash
python -B scripts/runtime_smoke.py --java JAVA --mallet-home MALLET_HOME
python -B scripts/query_semantic_okf_tika_mallet.py BUNDLE inspect --deep-validation --java JAVA --mallet-home MALLET_HOME
```

Ordinary inspection and search need neither Java nor Tika. Deep validation needs
MALLET and Java but never needs the Tika distribution because it verifies the
persisted extraction receipt rather than rebuilding it.

## Search modes

Exact terms, identifiers, values, and filenames:

```bash
python -B scripts/query_semantic_okf_tika_mallet.py BUNDLE search --query "invoice 2026-041" --mode bm25 --top-k 10
```

Conceptual MALLET topic expansion:

```bash
python -B scripts/query_semantic_okf_tika_mallet.py BUNDLE search --query "document retention and audit evidence" --mode topic --top-k 10
```

Two-step PPMI association propagation:

```bash
python -B scripts/query_semantic_okf_tika_mallet.py BUNDLE search --query "spreadsheet validation" --mode association --top-k 10
```

Reciprocal-rank fusion of all three independent rankings:

```bash
python -B scripts/query_semantic_okf_tika_mallet.py BUNDLE search --query "compare extraction acceptance criteria" --mode fusion --top-k 10
```

Several broad queries with one snapshot validation and compact exact evidence:

```bash
python -B scripts/query_semantic_okf_tika_mallet.py BUNDLE batch-search --query "community retrieval" --query "hierarchical synthesis" --mode fusion --top-k 8 --evidence-only
```

Create a bounded support pack, then compile a support-ID draft:

```bash
python -B scripts/query_semantic_okf_tika_mallet.py BUNDLE answer-pack \
  --query "community retrieval" --query "hierarchical synthesis" \
  --query "direct entity or chunk retrieval" --mode fusion --top-k 6 \
  --max-sources 10 --output /tmp/answer-pack.json
python -B scripts/query_semantic_okf_tika_mallet.py BUNDLE finalize-answer \
  --pack /tmp/answer-pack.json --draft /tmp/answer-draft.json \
  --output /tmp/final-answer.json
```

Repeat `--source-id`, `--concept-id`, or `--concept-type` for unions within that
filter. Different filter kinds combine with logical AND.

## Completion gate

Before answering, confirm:

- inspection passed; evaluation-critical snapshots passed deep fixed-seed MALLET
  rederivation; and a path-and-hash inventory proves the bundle did not change;
- the Tika receipt, generated Semantic plan, ledger attributes, and persisted bodies
  have exact parity, including the distinct line-ending-only contract for any
  UTF-8-verbatim textual source;
- filters were applied before ranking and requested/effective modes are disclosed;
- expansion terms and activated topics are visible;
- every cited concept path exists and every locator resolves to returned text and hash;
- the final structured response passed `validate-answer`, including exact nested
  evidence copies and complete first-use order, or was compiled and passed by
  `finalize-answer`;
- factual claims were checked in an authoritative OKF layer; and
- no Tika metadata guess, MALLET topic, association, score, rank, web result, or model
  memory is presented as ground truth.
