# Reuse Entity snapshot evidence indexes

Status: Accepted for isolated development. Exact native qualification and
independent whole-bundle acceptance remain required before canonical promotion.

Date: 2026-09-11

## Context

The adjacency-reuse candidate preserved exact responses and passed its public
software checks, but its original EnterpriseRAG measurement still reached the
unchanged 3,600-second agent limit without a qualified ranking. Its retained
public runtime profile showed repeated query computation across a route-major
sweep. Source inspection identified record, section, claim-evidence and reverse
edge-evidence lookups rebuilt from the same immutable snapshot on every query.
These observations do not identify the native timeout function.

## Decision

Change only the Entity consultant snapshot module. Cache those four source-derived
lookups in one entry under the existing reentrant query lock. Bind the entry to
weak snapshot identity and root/index/core/plan digests. Release its references
before constructing a replacement and when its snapshot owner is collected.
Retain dictionary last-write behavior, evidence order and duplicate entries.

Keep the builder and all other package files frozen. Preserve scoring arithmetic,
tokenization, traversal, filters, validation, artifact bytes, public errors and
returned-evidence isolation. Keep the preceding-query cache capacity and the
evaluation's route order unchanged. Read-only snapshots remain the supported
contract; this cache does not add recursive mutation tracking or cache validation.

Charge one distinct proposal under [ADR 0137](0137-charge-construction-corrections-within-enterprise-search-caps.md):
91 cumulative claims, Entity Graph 8 of 80, nine previously consumed construction
first measurements and one new unassigned first-measurement identity. Preserve
historical stops, pending claims, unavailable originals and all acceptance gates.

## Evidence and consequences

The [software report](../../evaluations/reports/evolution/e11/entity-evidence-index-reuse-001/README.md)
binds nine passed realization checks, including 96 lookup comparisons, 192
concurrent comparisons, four complete schema/layout cells and 96 warm response
pairs with public rejection and returned-evidence mutation checks. Only one of
the 252 package files changed. The sealed candidate is
`sha256:c4d3c66cb4567ac4bbb6236e183c17bccaad9f4cccac77f67a382cfdbc735faf`.

The pinned public replay reproduced all 48 retained responses, building evidence
and traversal indexes once each. Observed profiled query time was 6.578693354
seconds, compared with the parent's retained 7.784848780 seconds. The parent was
not re-executed. This sequential observation includes profiling overhead and is
not a causal speedup, native resource qualification or retrieval-quality gain.
Exact EnterpriseRAG qualification, the final all-500 comparison and independent
whole-bundle acceptance remain unfinished.
