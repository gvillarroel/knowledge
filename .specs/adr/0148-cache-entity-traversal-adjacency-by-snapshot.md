# Cache Entity traversal adjacency by snapshot

Status: Accepted for isolated development; native qualification and independent
whole-bundle acceptance remain required before canonical promotion.

Date: 2026-09-11

## Context

The previous Entity consultant candidate again reached the fixed one-hour agent
limit without a qualified ranking, despite successful build and standalone
validation logs. A separately declared public query profile then measured the
unchanged consultant on a 1,024-record synthetic snapshot. Traversal accounted
for 73.2% of the query profile, and all 48 calls recomputed their query because
the route-major sweep exceeded the existing one-entry full-query cache.
This profile does not identify the native timeout phase.

Source inspection showed that each traversal rebuilt the same undirected
adjacency lists and section identity set. Reuse must preserve edge insertion
order, duplicate edges and both insertions of a self-loop because propagation
accumulates floating-point values and evidence in that order. A second strong
snapshot cache could prolong the lifetime of a large graph after a failed or
interleaved query.

## Decision

Keep the builder and all other package files frozen. Change only the Entity
consultant snapshot module to maintain one traversal index, guarded by the
existing reentrant query lock and bound to weak snapshot identity plus root,
index, core and plan digests. Clear the old entry before constructing a new
one. A weak-reference callback clears graph references when the owner dies;
active queries retain their own local index references safely.

Preserve scoring arithmetic, traversal order, propagation, mentions, filters,
evidence, public errors, deep validation and all four routes. Do not combine
this treatment with alias indexing, a larger query cache, query reordering or
precomputed propagation arithmetic. Read-only snapshots remain the supported
contract; the frozen dataclass does not promise recursive mutability tracking.

Charge this separate proposal under the existing
[construction accounting policy](0137-charge-construction-corrections-within-enterprise-search-caps.md):
90 cumulative proposals, Entity 7 of 80, eight previous construction first
measurements consumed and one new unassigned first measurement with zero retries.
Preserve all historical search states and the one-way acceptance boundary.

## Evidence and consequences

The [software and runtime report](../../evaluations/reports/evolution/e11/entity-traversal-adjacency-reuse-001/README.md)
binds eight passed checks: exact scoring scope, skill format, 192 traversal
comparisons, 96 concurrent comparisons, lifetime/failure checks and four complete
schema/layout artifact, query and rejection cells. The sealed candidate is
`sha256:37015e173891f7a267b9cd8ffd88567a8f8200dccdea7827180df4e375770f66`.

The pinned runtime reproduced all 48 retained responses with one adjacency
build. Observed profiled query time fell from 15.726572549 to 7.784848780 seconds.
The [CTA](../../evaluations/reports/evolution/e11/entity-traversal-adjacency-reuse-001/cta.md)
keeps the public synthetic workload, profiling overhead and sequential timing
scope explicit. This is not a native speedup, peak-memory measurement or
EnterpriseRAG quality gain. Exact native qualification is the next required
measurement; the final all-500 comparison and independent acceptance remain open.
