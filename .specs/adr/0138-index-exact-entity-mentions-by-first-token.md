# Index exact Entity Graph mentions by their first token

Status: Accepted for offline candidate preparation; native qualification pending.

Date: 2026-09-09

## Context

The original E11 Entity Graph construction reached its 3,600-second agent limit
without producing a ranking. The [public diagnosis](../../evaluations/reports/evolution/e11/entity-graph-matching-diagnosis-001/README.md)
identified an avoidable cost in exact mention matching: every section position
was tested against every alias length, including lengths whose aliases could
not start with the section's current token. This is a construction hypothesis;
the original native timeout does not provide a phase-level causal measurement.

## Decision

Reserve `entity-prefix-matching-001` as one nonrefundable construction proposal
under [ADR 0137](0137-charge-construction-corrections-within-enterprise-search-caps.md).
It consumes one of Entity Graph's 80 claims, leaving 79. Together with 81
historical claims and the separate Ensemble proposal, 83 claims are charged
against the unchanged 585 limit. No catalog, miss counter, pending obligation,
closed search or five-round limit is reset.

Change only `derive_mentions` in the standalone Entity Graph builder. Index
alias lengths by their first normalized token, then inspect only those lengths
at each section position. Keep the existing complete tuple lookup, aliases,
normalization, duplicate counts, overlap behavior, source identities, mention
ordering and error contracts. Preserve all other 251 files, every consultation
skill and the separate Entity Graph implementation inside Ensemble.

Realize the complete candidate through the maintained realizer. Require exact
ordered parent/candidate comparisons across both schemas and token thresholds,
an independent count oracle, complete artifact and query parity in both storage
layouts, corruption rejection and refusal to overwrite existing output. Keep
all fixture inputs free of benchmark questions and relevance labels.

The sealed candidate's first native measurement remains an exclusive obligation
with no allocation yet assigned. Before native execution, require the finite
prospective allocation, exact task/package binding and independent admission
specified by [ADR 0133](0133-version-exact-builder-bindings-in-feasibility-tasks.md)
and [ADR 0134](0134-requalify-versioned-enterprise-profiles-without-resetting-search.md).
The original failed attempt remains immutable and consumed.

## Evidence and consequences

All seven declared validation commands and the subsequent realization verify
passed. The [candidate report](../../evaluations/reports/evolution/e11/entity-prefix-candidate-validation-001/README.md)
records 1,120 ordered matching comparisons, four integration cells, 16 completed
builds, 32 nonempty query pairs and 40 corruption rejections. A preserved V1
harness error concerned the overwrite response shape; correcting that assertion
preceded candidate realization and introduced no extra proposal or native trial.

The neutral stress fixture constructed 4,001,920 lookup tuples with the parent
and 160 with the candidate while returning the same 32 mentions. These are
instrumented operation counts, not an EnterpriseRAG speedup or memory result.

The candidate tree is
`sha256:886840868c7e47d2d7f35d5ecdf677100dfffc49d8750f8a890c273efc0c1f9d`.
Full-workload feasibility, retrieval quality and independent acceptance remain
unmeasured. The canonical skill is not changed by this preparation decision.
