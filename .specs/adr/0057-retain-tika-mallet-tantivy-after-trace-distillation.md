---
adr: "0057"
title: "ADR 0057: Retain Tika/MALLET/Tantivy After Trace Distillation"
summary: "Reject the v36 consultation candidate after a complete schema-2 Harbor gate because its small mean holdout gain included a severe task regression."
status: "Accepted"
date: "2026-07-24"
product: "knowledge"
owner: "Platform Architecture"
area: "Semantic Knowledge Retrieval"
tags: [knowledge, okf, tika, mallet, tantivy, harbor, trace-distillation, holdout]
---

# ADR 0057: Retain Tika/MALLET/Tantivy After Trace Distillation

## Status

Accepted. This extends ADR 0055 and records the requested evolution stopping
condition.

## Context

The `consult-semantic-okf-tika-mallet-tantivy` skill was evolved with the
`harbor-trace-distillation` workflow. The campaign used Harbor 0.18.0
schema-2 jobs, exact skill locks, one attempt per task, zero retries, and
separate development and holdout cohorts.

The v36 candidate protected only the final identity suffix of selected concept
paths. Its digest was
`sha256:ee66117d0ddd2ec8d22e2d7e41957e83f02db39b77d0ee22f04bb8f8d4248736`.
It passed all three development tasks and all required response, evidence,
reference, and mechanical qualification gates. Development rewards were
`0.818615`, `0.795629`, and `0.733706`.

The untouched six-task holdout compared the frozen production baseline with
the exact v36 candidate under matching agent, model, task checksum, retry, and
evaluation profiles. Both jobs completed without errors or retries.

## Decision

Reject v36 and retain the production baseline digest
`sha256:263701cf37b49448b76413bd58fe7f5ee129ec01c264c89f70b1bb67392504ba`.

The candidate increased mean holdout reward from `0.130857` to `0.133380`, a
gain of `0.002523`, and improved q015 from `0` to `0.800281`. However, q010
regressed from `0.785142` to `0`, and five of six candidate holdout trials did
not satisfy all qualification gates. The strict promotion policy requires no
task regressions, so `harbor-trace-distillation` returned `keep-baseline`.

Stop this evolution campaign at the no-promotion boundary. Do not copy the
candidate into the live skill.

## Consequences

The published Tika/MALLET/Tantivy consultation skill remains unchanged. The
complete development and holdout evidence is retained under
`evaluations/semantic-okf-tika-mallet-tantivy/generated/trace-distillation/`.

The six holdout tasks are now observed and cannot be reused as untouched
holdout evidence. Any future evolution requires a new prospective cohort and
must preserve or improve q010-style document coverage rather than optimizing
only aggregate reward.
