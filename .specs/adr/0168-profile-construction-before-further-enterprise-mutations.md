# ADR 0168: Profile construction before further EnterpriseRAG mutations

Date: 2026-09-15.

Status: Accepted for prospective preparation; measured execution requires independent admission.

## Context

The [reviewed all-500 catalog](../../evaluations/reports/datasets/enterprise-all500-first-executions-001/README.md)
contains six qualified retrieval observations. Entity Graph and Ensemble remain
unavailable after interruption. Their consumed original conditions and E16's
terminal outcome cannot be replaced by another attempt under a new output name.
The user continues to request useful improvements and complete measurements.

Source inspection suggests repeated graph derivation may contribute to
construction cost. It does not establish where the interrupted runs spent time.
Changing the algorithms before measuring their phases would leave that question
unanswered and could mix a construction change with a retrieval change.

## Decision

Prepare one ordinary, public construction diagnostic with the unchanged full
reference skill. Use two nested, approximately equal-count application-balanced
workloads of 256 and 1,024 complete records. Measure Entity Graph and Ensemble
at each size, in that order within each size. Preserve the inspected original
hashing embedding provider for Ensemble and the `source-packed-v1` layout.

The four-original job has one attempt per cell, zero retries, concurrency two,
two CPUs and 6 GiB per cell, and a 1,800-second whole-agent limit. Each cell
attempts two complete constructions, matched additional validations, and exact
output equality. Bounded stack samples contain code locations only. Construction
integrity and phase costs are the outcomes; there are no queries or retrieval
scores. See the [fixed protocol](../../docs/enterprise-construction-profile.md).

Before admission, independently review actual image/input/plan continuity,
native task and artifact contracts, and a finite functional rehearsal: six
constructions of one nine-record fictional fixture and two no-constructor native
transport trials. A substantive rehearsal failure stops admission under this
proposal. Image-reference preparation failures remain preserved separately and
do not consume or replenish constructor or native trial allocations.

## Consequences

The diagnostic can identify a concrete construction phase to optimize. It cannot
fill the missing all-500 scores, prove the cause of an earlier failure, select a
candidate, release private data or promote a skill. The four cells are related
variants of one public source family, not four independent samples.

Any later skill mutation and selection requires a separately registered study,
a frozen development protocol and fresh independent validation before evolution.
Keep the current skill and all historical results unchanged until that workflow
supports a promotion. Preserve complete and partial native evidence, publish only
reviewed aggregates, and keep all data and execution artifacts ignored.
