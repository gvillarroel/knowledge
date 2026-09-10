# Use a token automaton for exact Entity Graph mention matching

Status: Accepted for isolated candidate preparation and software validation;
EnterpriseRAG qualification and promotion remain pending.

Date: 2026-09-10

## Context

The first Entity Graph construction correction indexes alias lengths by their
first normalized token. It passes exact correctness checks but its original
6,000-document native attempt timed out. That attempt remains consumed.

Public profiling of the unchanged corrected parent found that host-backed
filesystem costs can obscure algorithm costs. A separately declared storage
control staged identical inputs and package bytes into a container-local
workspace, preserving all 145 output files. That storage treatment is separate
from skill evolution and does not explain the original native timeout.

In the container-local 128-record profile, mention matching consumed 0.835
seconds across the build's three calls and 0.274 seconds during independent
validation. The existing public metadata audit also found many distinct alias
lengths. A shared-first-token stress input exercises unnecessary tuple windows
even with the first correction's index. This supports a new bounded matching
hypothesis; it does not establish full-corpus speed or retrieval quality.

## Decision

Reserve `entity-token-automaton-001` before materialization as one additional,
nonrefundable Entity Graph construction proposal under
[ADR 0137](0137-charge-construction-corrections-within-enterprise-search-caps.md).
Cumulative claims become 85 of 585, including two of Entity Graph's 80 claims.
Preserve all historical closed, pending and unavailable entries and the
five-round and three-consecutive-evaluable-miss rules.

Change only the builder's `derive_mentions` function. Build a sparse trie from
the unchanged normalized alias map. Breadth-first failure links support
continuation after a mismatch; output links visit suffix terminals without
copying inherited binding arrays. Preserve duplicate bindings, overlapping
occurrences, original alias strings, exact counts, identities and ordering.
All other functions, imports, validators, consultation files, family copies and
retrieval parameters remain unchanged.

Keep the implementation in its isolated, digest-sealed candidate until the
declared native execution and acceptance gates pass. The reserved first
measurement has no allocation yet. A future controller must include this
construction charge; existing executed controllers must not be edited or
restarted to accommodate it.

## Verification and consequences

The [candidate report](../../evaluations/reports/evolution/e11/entity-token-automaton-001/README.md)
records seven passed realization checks, 1,120 ordered differential comparisons,
two independent count oracles and four complete integration cells. The stress
case reduces tuple constructions from 3,996,464 to 128 while preserving its 32
mentions. A separate 128-record fixture in the pinned Python 3.12 runtime
reproduces all 145 parent artifacts and passes independent validation.

The sealed candidate is
`sha256:6414475543ea62006f6cc2ea7bb330577279b90bf775154fe0596854143119f4`.
Its parent is
`sha256:886840868c7e47d2d7f35d5ecdf677100dfffc49d8750f8a890c273efc0c1f9d`.
Only one function in one file changed; the remaining 251 files are identical.

Single profiled observations cannot establish a general speed improvement.
The existing consultant and Ensemble matcher retain their previous costs.
Resource feasibility, the common reference, remaining family searches, paired
all-500 results and independent acceptance still need their declared evidence.
No EnterpriseRAG score, public rank or production promotion follows from this
software validation.
