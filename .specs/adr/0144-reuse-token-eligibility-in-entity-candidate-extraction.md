# Reuse token eligibility in Entity candidate extraction

Status: Accepted for an isolated builder candidate. Software correctness and
pinned-runtime compatibility passed; full EnterpriseRAG qualification and
promotion remain pending.

Date: 2026-09-10

## Context

The [public JSON diagnosis](../../evaluations/reports/evolution/e11/entity-json-scaling-001/README.md)
identified candidate extraction as a substantial part of completed software
profiles. The builder's `_candidate_statistics` checked each token's stopword
membership and digit status repeatedly in overlapping n-gram windows. The
previous native timeout remains consumed and its exact phase is unresolved.

The extraction contract fixes eligible windows, excluded aliases, counts,
document frequencies, scores, local selection and deterministic global ties.
Repeated eligibility checks can be removed without changing that contract.

## Decision

Charge `entity-ngram-eligibility-001` as one additional nonrefundable Entity
proposal under [ADR 0137](0137-charge-construction-corrections-within-enterprise-search-caps.md).
The total becomes 87 of 585, with four of Entity's 80 claims and 76 remaining.
Preserve five consumed construction measurements, both historical pending
measurements, closed family searches, five catalog rounds and the rule of
three consecutive unique evaluable misses per mechanism. Resource failures
remain separate from quality misses.

Use the complete consultant-automaton package as the frozen parent. Modify
only the builder's `_candidate_statistics` body: accumulate the number of
disallowed tokens at each boundary, then reject a window when its two boundary
counts differ. Keep the existing eligible-window order and excluded-alias
lookup, all counts and score arithmetic, rounding, tie keys and output order.
Freeze every consultation file and the other 251 package files.

Preserve all builds, independent complete validation, corruption rejection,
records, artifact bytes, query modes, resources and extraction parameters.
This treatment must not combine builder and consultant optimizations.

Before materialization, declare exact scope and format checks, independent
occurrence-counting and hand-counted oracles, measured predicate counts, and
four complete schema/layout integration cells. Use the maintained realizer to
prepare, validate, seal and verify the complete candidate.

After sealing, execute the new candidate once in the pinned runtime on the
existing public 1,024-record JSON input. Compare the complete output inventory
with the retained reference; do not repeat the old reference execution. Keep
cProfile explicit and asynchronous traceback collection disabled. The profile
does not replace a native qualification or independent acceptance gate.

## Evidence and consequences

The [candidate report](../../evaluations/reports/evolution/e11/entity-ngram-eligibility-001/README.md)
records seven passed checks, 4,080 exact independent comparisons, two hand-counted
oracles and 192 integration child commands. It preserves 32 nonempty paired
query responses and 40 corruption rejections at each validation layer.
The declared predicate-count cell uses 1,968 tokens: membership checks are
28,704 in the parent and 1,968 in the candidate, with exactly equal results.

The pinned runtime completed construction, independent validation and deep
consultation, with all 19 output files matching the retained reference. Its
single instrumented observations are descriptive; they do not establish a
native speedup, a 6,000-document resource fit or improved retrieval quality.

The candidate is
`sha256:1805605cb708f5e37f9f035fcc2eac397f3500d173ea34cf327433511e1e5df7`,
from parent
`sha256:15d7fd9ffc0e83a1585a901bf6a2ee8133d2c58407130e3c0918cb7acdf39cbc`.
Reservation:
`730a19ef2954bd7aaba3fc28fc910374ceaf763c6096be03cd26624193c6285c`.
Public aggregate:
`3cd1bd0c8b8f9215248a668cffecb40e160d1d585ce7c85dd05a092c38adbafe`.

The candidate's first native measurement remains unassigned. A new reviewed
controller must bind the exact builder bytes, current custody and preserved
accounting before allocation; stopped studies and consumed attempts cannot be
reopened. No canonical skill is promoted. The five open searches, composed
reference, all-500 comparison and one-way whole-bundle acceptance remain open.
