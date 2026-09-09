# Charge construction corrections within existing Enterprise search caps

Status: Accepted for prospective offline preparation; no native admission.

Date: 2026-09-09

## Context

The [E11 starting run](../../evaluations/reports/evolution/e11/starting-terminal-001/README.md)
settled with ten qualified measurements and two execution failures. Ensemble
exceeded its 6 GiB memory limit; Entity Graph reached its 3,600-second agent
limit. Reissuing those attempts or resetting the search would discard relevant
history and conflict with [ADR 0134](0134-requalify-versioned-enterprise-profiles-without-resetting-search.md).

Ensemble source inspection identifies overlapping live state: materialization
retains its original RDF graphs while independent validation reparses the
snapshot, and reconstructed expected graphs survive until a later SHACL check.
Projection builders also retain persisted arrays during independent validation.
This supports a prospective lifetime correction. It does not identify the
original OOM allocation site or prove that the correction will fit the limit.

## Decision

Treat a construction correction as a distinct, nonrefundable proposal within
the existing family and global caps. The single proposal
`ensemble-memory-lifetime-001` consumes one of Ensemble's 105 claims: 104 remain,
and total known claims increase from 81 to 82 within the unchanged 585 cap.
The five-round catalog limit, closed searches, unique-profile history and two
already charged pending first measurements remain unchanged. A validation-only
amendment before realization adds no candidate charge.

Allow offline realization against the frozen complete parent, changing only
five Ensemble builder assets. Release persisted graphs, arrays and the embedder
after their last use, and reclaim unreachable objects between completed
construction/validation phases. Preserve every validation, source document,
algorithm, artifact byte, public error and atomic publication path. Freeze all
consultation files and other families. Public hashing fixtures must demonstrate
complete output/query parity, corruption rejection and the intended graph
lifetimes with explicit callback counts; empty observations cannot pass.

The original failed starting attempt remains consumed and unchanged. The
reservation gives the prospective candidate one exclusive first-measurement
identity but assigns no native allocation. A future reviewed controller must
enforce construction plus catalog charges together under both inherited caps.
The existing E11 controller cannot enforce this extra construction debit and
must not be edited after execution.

## Consequences

Realization supplies a complete candidate for review, not retrieval fitness or
native feasibility. Production-provider behavior, atomic-failure cleanup and
the complete diff need appropriate verification. Native work additionally
requires truthful predecessor closure, current custody, a finite declared
allocation and versioned complete-bundle task bindings under
[ADR 0133](0133-version-exact-builder-bindings-in-feasibility-tasks.md).
Entity Graph's separate timeout still needs its own diagnosis.

The original reservation, rejected V1 lifetime validator, corrected V2
validation declaration and independent accounting review remain append-only
local evidence. The reviewed declaration is bound by SHA-256
`146e066b71f336deaca05c00edda3ea10157c2000073327c23a17ed6e0137d6a`;
the independent review receipt is
`a80ea65cec088314974cfb7d12c8bbbf87652b16298749d2708de1914e3166de`.
No private evaluation feedback informed this correction.

## Initial realization evidence

The complete candidate was prepared, sealed and verified through the maintained
realizer. Only the five declared files changed; the other 247 files and the
original parent stayed byte-identical. All five declared commands passed:
syntax, skill format, complete build/query/corruption parity in each of two
layouts, and released graph lifetimes with the expected callback counts.
These public hashing fixtures contain four source-scoped records. They do not
measure the 6,000-document production workload or native peak memory.

The candidate tree is
`sha256:d41f9aa819ff9e6154d5d3eea08e7963e060d86f67e7ab1a104225c828180eef`;
its validation receipt object digest is
`sha256:12814a1caa81aa1e6cb6df466edcf9eecbbecf32305f46988d37c61f46ee90e3`.
Canonical repository skills remain unmodified pending the required native
evaluation and acceptance.
