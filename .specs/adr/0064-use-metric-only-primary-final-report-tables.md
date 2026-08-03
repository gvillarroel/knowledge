---
adr: "0064"
title: "ADR 0064: Use Metric-Only Primary Tables in Final Evaluation Reports"
summary: "Lead current-facing final reports with a compact ranked table containing an identity column and dataset-specific metrics, while keeping status and eligibility outside that table."
status: "Accepted"
date: "2026-07-27"
product: "knowledge"
owner: "Platform Architecture"
area: "Evaluation Reporting"
tags: [knowledge, evaluation, reporting, metrics, ranking]
---

# ADR 0064: Use Metric-Only Primary Tables in Final Evaluation Reports

## Status

Accepted. This refines the presentation requirements in ADRs 0047, 0048, and
0049 without changing the accepted or experimental disposition of any route.

## Context

Final comparison tables accumulated status, decision, route-detail, and
placeholder columns beside test metrics. That made the main result harder to
scan and allowed alternatives evaluated under different contracts to appear
like directly comparable rows.

Status remains important, but it is a governance conclusion rather than a
dataset metric. Missing measurements also do not become comparable merely
because a placeholder is inserted into a ranked table.

## Decision

Every current-facing final evaluation report leads with one compact primary
comparison table:

1. a sequential position;
2. a strategy, pair, candidate, or version identity; and
3. only metrics emitted by the named test dataset and evaluation contract.

The primary table has no status, decision, outcome, acceptance, or promotion
column. Those conclusions remain explicit in adjacent prose or a separate
eligibility section.

Only rows measured under the same dataset, cohort, candidate budget, identity
grouping, and metric contract may receive a position. An alternative missing
any displayed metric is omitted and explained directly after the table. A
separate diagnostic table may describe incomplete or non-rankable evidence,
but it must not use the ranked-table presentation.

Current-facing final reports also ship a machine-readable
`final-report-comparison/1.0` companion. It declares the shared dataset scope,
one aggregation, unit, direction, and display precision per metric, and one
complete numeric metric map per alternative. The Markdown table is a checked
projection of that contract: alternatives are rows and aggregate dataset
metrics are columns. Governance conclusions are not permitted in either the
metric definitions or alternative rows.

Historical and digest-bound reports remain immutable. The new presentation
applies to `evaluations/LATEST-REPORT.md` and to final reports generated after
this decision.

## Consequences

Positive:

- the principal result is compact and immediately comparable;
- every numeric column has a direct dataset interpretation;
- missing or cross-dataset measurements cannot masquerade as ranked evidence;
  and
- eligibility and promotion decisions remain visible without being confused
  with measured quality.

Negative:

- readers must consult adjacent prose for acceptance or experimental status;
- detailed route diagnostics move below the primary result or remain in
  supporting reports; and
- report generators need validation to prevent presentation drift.
