# Bind EnterpriseRAG application heatmaps to published comparisons

Status: Accepted

Date: 2026-09-12

## Context

EnterpriseRAG reports compare six measured strategies across nine overlapping
application cohorts, with two strategies still lacking qualified measurements.
The tables preserve the evidence, but a visual view makes complementary
application strengths easier to inspect without inferring a universal winner.

## Decision

Render an explicitly named public E14 comparison and SHA-256 digest into a new
report directory. Reuse the presentation-contract validation introduced in
[ADR 0160](0160-refresh-bounded-enterprise-current-views.md), including an exact
dated inventory binding. Do not discover a candidate, traverse private
provenance, dispatch evaluations or modify any existing observation.

Keep all eight strategy columns and the overall and application rows. Preserve
full numeric precision in a JSON companion, display nDCG@10 on a fixed 0–100
scale, outline the supplied row leaders using full-precision ties, and mask
unavailable cells instead of assigning zero. Show cohort counts and explicitly
state that applications overlap. Distinguish development retrieval from
generated-answer quality, all-500 results, public ranking and routing policy.

Publish PNG and SVG together with the numeric matrix, input digests, plotting
version, renderer and validator digests, and image hashes. Matplotlib remains
an optional reporting dependency. Keep its cache inside the repository's
ignored temporary directory. Refuse existing or escaping output paths and
retain partial output on failure. Review the rendered figure before publication.

## Consequences

Visual reports are immutable observations with explicit source identities.
They do not become current-score authorities or replace the frozen publisher
and its native evidence checks. Later scores require a new figure directory;
historical figures remain correctly labeled. The plot uses only public
aggregate fields and can be reproduced without raw datasets or private traces.

The [report procedure](../../docs/evaluation-datasets-and-reports.md#render-a-public-application-comparison)
documents exact inputs and append-only output behavior.
