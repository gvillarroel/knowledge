# ADR 0070: Promote the qualified-runtime builder after Pareto holdout

## Status

Accepted on 2026-07-27.

## Context

ADR 0068 rejected builder candidate v45 because its mixed build-consult reward
could not isolate builder quality. The repository subsequently gained direct
builder tasks that mount immutable ingestion and retrieval plans, a qualified
Linux JDK 17 runtime, and read-only Tika and MALLET installations. Each task
requires two independently validated builds and a byte-identical sorted
path/SHA-256 inventory.

The first direct verifier counted duplicate Pi tool calls from both
`message_start` and `message_end` events and counted `--help` probes as real build
or validation invocations. Those completed attempts remain append-only evidence,
but their command-efficiency values are not suitable for selection.

Task schema 1.2 corrects the parser by accepting only completed Pi events and by
excluding help probes. Candidate v46 adds a qualified-runtime branch: when the
caller forbids installation, it verifies all pinned Python distributions and uses
the supplied CPython 3.12 interpreter without creating an empty environment,
installing packages, or accessing the network. It also prescribes one runtime
smoke, two builds, two validations, and one inventory comparison.

In corrected development, the source baseline scored `0.7917` and `0.6250`;
v46 scored `1.0000` in both cases. Frozen holdout used two attempts on each of two
untouched cases. The baseline mean was `0.7500`, the candidate mean was `1.0000`,
and no case regressed.

A simultaneous reflective Pareto search on the consultation skill did not produce
a qualified archive member. Its candidates violated exact evidence identities or
the minimum independent-document contract, so consultation holdout remained
closed.

## Decision

Use Harbor reflective Pareto search for this evolution round and preserve
development and holdout as separate append-only cohorts.

Promote builder candidate `v46-qualified-runtime`, sealed as
`sha256:3a1d2bfb66def8a911ffe7197740eef90a9638dab0522eb39f12a8c369f5c908`.
Require the production builder bundle to match the holdout-copied candidate
exactly.

Reject the consultation candidates and leave the source consultation skill
unchanged. A failed development archive must not open consultation holdout.

## Consequences

- The builder now follows the caller's no-install boundary and avoids unnecessary
  package installation and network access in a prequalified runtime.
- The prescribed workflow is deterministic and efficient: one preflight, two
  builds, two independent validations, and one inventory comparison.
- The builder promotion is supported by direct causal metrics rather than
  downstream answer variation.
- Duplicate-event and help-probe behavior is covered by a regression test.
- The consultation failure remains useful negative evidence but is not promoted.
- Direct retrieval Recall@10, nDCG@10, and P95 results remain a separate evaluation
  surface and are not reinterpreted from Harbor builder rewards.
