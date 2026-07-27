---
adr: "0062"
title: "ADR 0062: Inventory Every Available GraphRAG Trial Artifact in the Diagnostic Rescore"
summary: "Expand the diagnostic current-metrics inventory from one 180-trial directory to 516 local trial artifacts while exposing incomplete parent jobs and keeping summary-only cells and curated references separate."
status: "Accepted"
date: "2026-07-24"
product: "knowledge"
owner: "Platform Architecture"
area: "Semantic Knowledge Evaluation"
tags: [knowledge, okf, graphrag, harbor, evaluation, rescore, inventory]
---

# ADR 0062: Inventory Every Available GraphRAG Trial Artifact in the Diagnostic Rescore

## Status

Accepted. This corrects the raw-trial inventory in ADR 0060 without changing
its native-ledger scoring method or the empirical-coverage boundary in ADR
0058.

## Context

ADR 0060 counted 180 raw Harbor trials under
`evaluations/semantic-okf-datasets/results`. A repository-wide GraphRAG trace
inventory found 517 local Pi traces:

- 180 trials in the primary result tree;
- 15 complete and distinct Tika-Mallet-Tantivy trace-distillation trials;
- 320 trials in the original eight-family campaign;
- one completed provider-quota retry in the second campaign; and
- one errored trial belonging to an unfinished six-trial Rust-Mallet job.

The 15 distillation trials come from compact v28, transport v29, direct-units
v30, canonical-first-use v31, and atomic-facts v32 jobs. All five jobs have a
final timestamp, three completed trials, no pending or running trials, and no
execution exceptions. Their trial identifiers and trace hashes are distinct
from the primary result tree.

The original campaign's 320 trial artifacts are complete even though only 32
produced responses with historical semantic adjudication. The second campaign
contains one settled provider-quota retry. The Rust-Mallet job is unfinished
and therefore fails the Harbor completion gate.

The primary 180-trial directory itself contains 13 trial artifacts from four
parent jobs that did not reach the job completion gate. Those rows are useful
for failure and response diagnostics, but they are not complete-job comparison
evidence.

The repository also contains 60 summary-only comparison cells and 40 curated
reference calibrations. Those artifacts are not live trial responses and must
not be added to the raw-trial count.

## Decision

Search every explicitly declared append-only result root recursively and fail
closed on duplicate response identities. Bind every rescored row to its
artifact root and record the complete ordered root list in the metric contract.

The artifact-only current-metrics table includes all 516 selected local trial
artifacts:

1. the 180 primary trials;
2. the 15 complete trace-distillation trials;
3. the original campaign's 320 trials; and
4. the completed provider-quota retry.

Join the 32 historical semantic adjudications back to raw campaign trials by
immutable Harbor trial id. Preserve any unmatched historical adjudication as a
legacy row. Record parent-job completion on every raw trial and report complete-
parent and incomplete-parent counts separately. Do not present the diagnostic
table as a native final Harbor comparison.

Do not include the separate incomplete Rust-Mallet study, summary-only cells,
or curated references as current-metrics model trials.

Keep semantic state separate from mechanical state. Raw responses without a
digest-bound or trial-id-bound adjudication remain explicitly unreviewed.
Curated references remain calibration-only evaluator material.

## Consequences

The raw current-metrics inventory increases from 180 to 516 trial artifacts.
Of these, 503 belong to complete parent jobs and 13 belong to four incomplete
parent jobs. Across the full diagnostic inventory, 209 emit an answer and 115
pass the current mechanical qualification gate.

The number of semantically reviewed responses remains 175. Another 15 complete
raw responses await semantic review, while 19 emitted primary responses are
not part of the adjudicated inventory. Empirical question coverage remains 29
of 40 because the newly recovered trials do not supply q028 or q031-q040.

The strategy summary now exposes all eight original families and five later
Tika-Mallet strategy variants. It is still ineligible for ranking: provider and
agent failures leave many family/cohort cells without an evaluable response,
and mechanical reward is not semantic correctness.

Future recalculations must preserve source-root provenance, expose Harbor
completion boundaries, and avoid double-counting recovered historical
adjudications.
