# Transfer builder state lifetimes to Entity Graph

Status: Accepted for isolated construction qualification; no native acceptance
or canonical skill promotion.

Date: 2026-09-10

## Context

The [Entity extraction correction](../../evaluations/reports/evolution/e11/entity-ngram-eligibility-native-001/README.md)
preserved exact software outputs but reached the fixed 3,600-second native
agent limit. A read-only snapshot during its second build recorded the
container at its unchanged 6 GiB memory limit, with swap use and major page
faults. This identifies memory pressure at that instant, not the eventual
timeout phase or the responsible allocation.

The [source-bound resource diagnosis](../../evaluations/reports/evolution/e11/entity-ngram-eligibility-native-001/resources.md)
identified two matching Entity builder files whose Ensemble counterparts
already release persisted RDF and projection state before independent checks.
The donor includes the post-return collection boundary from
[ADR 0140](0140-collect-semantic-validation-state-after-frame-return.md).

## Decision

Reserve one new, nonrefundable Entity construction proposal under
[ADR 0137](0137-charge-construction-corrections-within-enterprise-search-caps.md).
`entity-memory-lifetime-001` raises cumulative claims to 88 of 585 and Entity
claims to 5 of 80. Preserve all six consumed construction measurements,
historical pending measurements, closed searches, five catalog rounds and
the rule of three consecutive unique evaluable misses per mechanism.
The proposal owns one future first measurement, with zero retries and no
native allocation at realization.

Transfer only the builder's `_semantic_okf.py` and `_entity_graph_build.py`
from the sealed Ensemble donor. Preserve the original public semantic
validator docstring on its new wrapper. Release persisted RDF graphs before
independent validation, scope reconstructed graphs so that they can be
collected before subsequent SHACL checks, collect after the complete semantic
validator returns, and retain only selection and summary before releasing
the persisted projection mapping for independent rederivation.

Freeze the complete Entity consultant and the other 250 package files,
including the existing extraction and mention-matching corrections. Preserve
all source records, artifact bytes, ranking algorithms, routes, validation,
corruption rejection, error results, atomic publication and resource limits.
The Ensemble matching/extraction transfer and Entity consultant extraction
transfer remain separate future proposals.

## Evidence and consequences

The complete candidate is sealed as
`sha256:810ca4eee999ce0c93f19a3b0302a31de6f28cfd9ba1ee09c39e6014c056ddb5`.
Its nine software checks passed: exact two-file scope, skill format,
validator forwarding, four schema/layout parity cells, lifetime observations
and paired atomic failures. The four integration cells preserve 16 complete
builds, 16 independent validations, 32 nonempty paired query responses and
both layers' corruption rejections.

In the lifetime fixture, the parent retained four generated graphs at the
first independent validation entry; the candidate retained zero. The
candidate also released reconstructed graphs before the later SHACL checks
and the outer projection mapping before revalidation. The projection probe
uses a shallow instrumented mapping without copying its arrays. At semantic
validation return, five parsed graphs and one SHACL result graph remained
live for the parent and none for the candidate. Automatic garbage collection
was unchanged; these observations are not native peak-memory measurements.

The [software and runtime report](../../evaluations/reports/evolution/e11/entity-memory-lifetime-001/README.md)
also records the completed 1,024-record Python 3.12.13 fixture: construction,
standalone validation and deep consultation passed, with all 19 existing
reference files preserved. This was one candidate-only execution; the
reference was not run again.

Collection can add runtime overhead and cannot reduce peaks inside a still
active validation phase. The wrapper preserves its signature, docstring,
returned object and exception identity, but adds a traceback frame. Exact
software compatibility does not establish full-workload feasibility, a
causal speedup or a retrieval improvement. Fresh native qualification and
reserved independent whole-bundle acceptance remain separate evidence
boundaries before any canonical promotion.
