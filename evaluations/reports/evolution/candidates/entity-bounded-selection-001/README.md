# Entity Graph: exact bounded candidate selection

Date: 2026-09-12. A new Entity Graph construction candidate passed **eight declared
software checks**, was sealed, and passed read-only verification. It changes
only the candidate-selection function in one builder file; the other 251 files
remain unchanged. Its EnterpriseRAG score is **unavailable** until its new
native first measurement is admitted and completed.

## Change and preserved behavior

The builder previously sorted every eligible phrase before retaining a limited
number per section and globally. The candidate uses bounded selection with the
same ranking keys, limits and tie rules. Counting, extraction eligibility,
scores, score rounding, selected order and the previous token-prefix improvement
are preserved. All bytes outside the function, all consultants and all other
families remain unchanged.

This is a distinct construction opportunity under
[ADR 0156](../../../../../.specs/adr/0156-bound-entity-candidate-selection-with-exact-order.md).
Earlier public scaling diagnostics precede the existing token-prefix change;
they do not establish this selection work as the current dominant bottleneck.

## Retained software evidence

| Check | Observed result |
| --- | --- |
| Scope and skill format | Passed; one changed function and 251 unchanged package files |
| Independent extraction and limit oracles | 4,208 comparisons and two hand-counted cases passed |
| Local selection stress | 352,539 to 38,288 ordering/equality comparisons, an 89.14% reduction |
| Global selection stress | 326,660 to 27,310 ordering/equality comparisons, a 91.64% reduction |
| Scientific and generic schemas, each with two storage layouts | Four complete parity cells passed |

The stress cells use fixed public synthetic inputs, a fixed hash seed and
independent output oracles. These are algorithmic operation counts, not measured
native speedups, peak memory reductions or retrieval gains.

The four integration cells retained 16 complete builds, 16 independent
validations, 32 paired queries, eight consultant deep validations, 40 builder
corruption rejections, 40 consultant corruption rejections and eight overwrite
rejections. Every cell contains nonempty query evidence. Complete artifact
inventories match. Original command receipts, stdout/stderr and generated
software-fixture artifacts remain in the ignored local evidence directory,
bound by the aggregate's inventory commitment. The realizer itself keeps
deterministic receipts and does not attest external effects of trusted commands.

The sealed candidate is
`sha256:255fb106596f0b032e9513ecbf3a2fe2d73bd84cb6795c2f779691eeb025d24f`.
Its validation receipt object is
`sha256:51450d9560d10e1d0cf685776f44892ad685064dafe53b76af39f427c28c4f8f`.

## Opportunity accounting and remaining gate

This proposal consumes one nonrefundable opportunity, bringing Entity Graph to
**9 / 80**, with 71 remaining. At reservation, the combined ledger was
**110 / 585**: 91 inherited claims, 17 new E14 claims, the already reserved
Ensemble construction debit and this Entity debit. This is a reservation-time
snapshot; active E14 families can add later claims. Both extra construction
debits must enter a future controller exactly once.

The exclusive `entity-bounded-selection-001-first-measurement` identity is
unassigned, with zero dispatched attempts and zero retries. Earlier failed
attempts remain consumed. The frozen E14 controller and its miss counters were
not changed. Native admission requires a separately registered prospective
controller with truthful predecessor closure, exact full-workload bindings,
preserved resource limits and fresh independent validation.

The [current EnterpriseRAG comparison](../../e14/graphify-generation-004-001/comparison.md)
remains unchanged by this software candidate. Entity Graph and Ensemble are
still unqualified. No canonical skill was promoted. Application coverage gate
054 passed 1,643 tests and 373 subtests at **90.5%**.

[CTA](cta.md) · [Source-bound aggregate](aggregate.json) · [Candidate catalog](../README.md)
