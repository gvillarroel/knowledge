# ADR 0084: Reserve parallel questions for evaluation-only ranking

## Status

Accepted on 2026-07-30.

## Context

The canonical forty-question GraphRAG benchmark was fully exposed to the v51
supervised retrieval profile. ADR 0083 added twenty post-v51 questions, but
opening that cohort for diagnosis means it can no longer serve as an untouched
reusable boundary. A durable leaderboard needs a larger question extension
over the same fifteen papers whose bytes are never used for knowledge
construction or candidate improvement.

## Decision

Create `graphrag-papers-parallel-eval-60-v1` as an evaluation-only extension:

- sixty new questions over the existing fifteen-paper corpus;
- thirty hard single-paper audits, twenty two-paper comparisons, and ten
  three-paper syntheses;
- five to twelve reviewed claim anchors per question, bound to exact PDF pages;
- three independent process repetitions for each of the seven frozen expert
  strategies;
- a public digest registry and a private deny-by-default payload;
- ranking controlled by the evaluation-only cohort, with exposed cohorts used
  only as diagnostics; and
- publication limited to aggregate metrics and stability.

The registered question and ground-truth digests are forbidden inputs to:

- knowledge or retrieval-profile construction;
- skill, query-adapter, or mutation-operator evolution;
- trace distillation;
- candidate realization or selection; and
- discovery, development, or validation fitness.

The specialized-expert builder rejects registered evaluation-only question
bytes and local `EVALUATION_ONLY.json` markers before profile forging.
Copying, renaming, or reformatting the dataset does not change its policy.

## Consequences

- A candidate must be complete and frozen before it is evaluated on this
  cohort.
- Per-question rankings and diagnostics remain private and must not drive a
  later mutation.
- An aggregate result may rank already frozen candidates, but a failed
  candidate may not be repaired against this dataset.
- A candidate changed after seeing this leaderboard requires a different,
  newly sealed evaluation-only dataset version.
- The result measures same-corpus unseen-question retrieval, not unseen-corpus
  transfer or generated-answer correctness.
- Expected answers have reviewed claim and page provenance but no new
  independent human adjudication.
