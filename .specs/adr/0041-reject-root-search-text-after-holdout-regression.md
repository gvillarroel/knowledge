---
adr: "0041"
title: "ADR 0041: Reject Root Search Text After a Holdout Regression"
summary: "Keep Graphify Next unchanged because bounded root-node search text wins both development tasks but regresses the Astro holdout task under the no-regression promotion policy."
status: "Accepted"
date: "2026-07-20"
product: "knowledge"
owner: "Platform Architecture"
area: "Semantic Knowledge Retrieval"
tags: [knowledge, okf, graphify, harbor, evolution, holdout]
---

# ADR 0041: Reject Root Search Text After a Holdout Regression

## Status

Accepted. This extends ADR 0040 and leaves `build-semantic-okf-graphify-next`
and `consult-semantic-okf-graphify` unchanged.

## Context

A builder-only Harbor harness was created from the canonical prepared Astro and
GraphRAG inputs. Each native job installed exactly one builder skill. An Oracle
agent deterministically ran that locked builder, and a hidden verifier invoked
the unchanged Graphify consultation implementation against disjoint question
cohorts.

The candidate attaches a normalized search-only string to each existing
`record-root`. It derives the string from the authoritative title, record ID,
concept type, scalar attributes, and at most 4,096 body characters. It does not
change visible labels, edges, views, ledger records, or consultation code.

## Decision

Do not promote or merge the candidate. Preserve it as diagnostic evidence.

On development, its mean Harbor reward is `0.800566` versus `0.686165` for the
baseline. It wins both task signatures, passes both non-compensating validity
gates, and is the sole member of the reflective Pareto archive.

On holdout, its overall mean is `0.853655` versus `0.846293`, but the Astro task
regresses from `0.922432` to `0.918986`. The frozen promotion policy forbids
case regressions, so population search records `task-regression` and
`promoted: false`. The GraphRAG holdout improves from `0.770154` to `0.788323`.

Do not tune another candidate against this opened holdout. A future attempt
requires a new prospective holdout or a predeclared policy that permits the
observed trade-off.

## Consequences

- The source builder and consultant remain byte-for-byte unchanged by this pass.
- The sealed candidate remains available for a future dataset or a GraphRAG-
  specific branch, but it is not an official improvement.
- Population search and reflective Pareto search provide positive development
  evidence; the final population holdout gate is authoritative for release.
- GEPA cannot express the script-owned mutation because it edits only
  `SKILL.md`. Trace, operator, and retry analyzers also exposed stricter harness
  identity or retry-lock requirements; those are evaluation-infrastructure
  follow-ups, not reasons to waive the holdout result.

