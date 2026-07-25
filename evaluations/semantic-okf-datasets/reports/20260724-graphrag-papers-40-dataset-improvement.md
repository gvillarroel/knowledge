# GraphRAG 40-question dataset improvement

Date: 2026-07-24

## Finding

The earlier 18-response audit was correctly scoped to the v36
trace-distillation evidence, but it was not a full-dataset audit. The canonical
dataset contains 40 questions.

The expanded inventory found:

- 180 local Harbor trials with 143 complete raw JSON responses;
- 320 trials in the preserved campaign report with 32 complete, manually
  reviewed responses;
- 175 individually reviewable responses in total;
- 60 older comparison cells whose response bodies are no longer present and
  therefore cannot be re-reviewed individually;
- complete-response coverage for 29 of 40 questions;
- no complete response for q028 or q031-q040; and
- 97 of 143 raw responses concentrated on q002-q004.

The companion
[`response coverage audit`](20260724-graphrag-papers-40-response-coverage-audit.md)
lists all 40 questions and all 175 reviewable responses separately. Its
semantic adjudication contains 3 passes, 168 partial answers, and 4 failures.

## Dataset corrections

### Non-exhaustive focus sets

The qrel paper lists were authored as focus-paper sets. Evaluation traces
regularly cited valid, on-topic papers outside those lists. Treating every
off-list paper as irrelevant made the public minimum-document gate disagree
with the task instruction and produced false negatives.

Dataset contract 1.1 introduced, and the current contract 1.2 retains:

- `qrel_scope: non-exhaustive-focus-set`;
- `minimum_document_gate_basis: valid-evidence-document-count`;
- `semantic_ranking_gate: manual-review-required`; and
- `full_dataset_coverage_required: true`.

Generated questions carry this policy into the hidden grader.

### Separated document diagnostics

The grader now reports these independently:

- cited document count;
- valid independent document count;
- covered focus-document count;
- public minimum-document gate; and
- focus-set minimum diagnostic.

Only exact valid evidence can contribute to the public minimum. Focus coverage
continues to contribute to the mechanical retrieval utility, but it no longer
silently defines semantic relevance.

### Explicit reward semantics

Every scored answer now records that reward is
`mechanical-contract-and-focus-coverage-only`. Semantic ranking is ineligible
until review. This also applies to q031-q040: hard-evidence anchor coverage is
not treated as claim entailment.

### Full-dataset coverage gate

The new response-audit utility separates questions, trials, complete responses,
unique response payloads, and summary-only historical cells. It refuses an
adjudication whose digest does not match the raw response inventory and marks a
full-dataset claim ineligible unless all 40 questions have a complete response.

## Regression evidence

Two v36 baseline responses that previously failed only because of focus-set
overlap now pass the corrected public minimum:

| Response | Valid independent docs | Focus docs | Minimum | Old reward | New reward | Semantic state |
|---|---:|---:|---:|---:|---:|---|
| q005 baseline | 6 | 3 | 4 | 0.000000 | 0.701818 | manual review required; partial |
| q020 baseline | 7 | 3 | 5 | 0.000000 | 0.590008 | manual review required; partial |

Strict release checks remain non-compensating:

- q004 still scores zero because its evidence is not in first-use order, even
  though every evidence row is exact and its document minimum passes.
- q025 still scores zero because its locator values violate the evidence
  contract.

The correction therefore removes qrel-minimum false negatives without making
malformed evidence acceptable.

## Question-by-question review

All q001-q030 questions were compared with their authored required points. All
q031-q040 questions were checked against their answer claims, derivations,
important negatives, and exact authoritative evidence. No question-content or
ground-truth defect was found.

The remaining live-evaluation gap is empirical coverage, not question count:

- q028 needs at least one complete response;
- q031-q040 need complete hard-question responses; and
- a future full-dataset comparison must avoid the present q002-q004 iteration
  concentration.

## Reference-answer completion

Every q001-q040 question now has a curated reference answer in
[`20260724-graphrag-papers-40-best-answers.json`](20260724-graphrag-papers-40-best-answers.json).
The forty question-level reviews account for all 175 historical responses
exactly once, satisfy all 200 authored semantic targets, and contain 243
supported claims with 408 exact evidence rows. The hard-question answers cover
all 94 authoritative evidence anchors.

Dataset contract 1.2 pins this collection by SHA-256. The reference answers are
evaluator material, not newly executed model trials, so they do not alter the
live full-dataset coverage restriction above.

## Current-metrics recalculation

The
[`current-metrics table`](20260724-graphrag-papers-40-current-metrics-table.md)
applies the contract 1.2 policy and diagnostics schema 3.0 to all 180 preserved
raw Harbor trials. It made no new model calls and did not modify the append-only
result artifacts. Each response was evaluated against its native ledger and
source-combination crosswalk so family-specific exact record identities remain
valid.

- 180/180 raw trials produced complete current-metric diagnostics.
- 99 trials pass the current mechanical qualification gate.
- Among 174 trials with a comparable stored reward, 46 rewards increased, none
  decreased, and 128 were unchanged.
- Mean reward across those comparable trials changed from 0.244128 to 0.402476.
- The manual semantic result remains 3 pass, 168 partial, and 4 fail.
- Empirical question coverage remains 29/40; the recalculation does not turn
  references into live trials.
- All 40 curated references pass the current strict response and mechanical
  qualification contract.

The recalculation also exposed and corrected a serialization defect in the
reference collection. Recursive key sorting had preserved content but changed
the strict `question_id`, `answer`, `evidence` member order. The aggregator now
preserves response-contract order, the dataset validator checks that order, and
the descriptor pins the corrected collection.

## Validation

- Dataset descriptors pass Draft 2020-12 JSON Schema validation.
- Schema 1.2 requires both the evaluation policy and pinned reference answers;
  schema 1.1 permits only the policy, and schema 1.0 permits neither.
- `dataset_tool.py validate --dataset all` passes both registered datasets.
- A fresh 40-task consult-only tree was generated deterministically.
- All 40 hidden oracles pass the production grader.
- Hidden-value leak checks pass.
- Excluding the descriptor-bound manifest, all 528 generated task files remain
  byte-identical to the pre-reference-answer tree.
- The response-audit JSON and Markdown regenerate with identical SHA-256
  digests.
- The best-answer JSON and Markdown regenerate with identical SHA-256 digests.
- The current-metrics JSON and Markdown regenerate byte-identically.
- Targeted grader, dataset, campaign-runner, and summary-hardening regressions
  pass: 59 tests, with one environment-dependent test skipped.
- The repository coverage gate passes: 716 tests and 90.9% application
  coverage against an 80% threshold.
