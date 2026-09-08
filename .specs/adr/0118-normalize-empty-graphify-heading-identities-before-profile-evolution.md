# ADR 0118: Normalize empty Graphify heading identities before profile evolution

Status: Accepted. Date: 2026-09-06.

## Context

The first short-path native profile campaign exposed a real construction
failure: two Graphify builds of an exposed development corpus produced different
graph and index bytes while every authoritative core artifact was identical.
An independent forward test reproduced this with and without a fixed Python
hash seed. A synthetic document with an empty Markdown heading and a relative
link isolated the cause without retrieval questions or relevance labels.

Graphify 0.9.17 relativizes heading IDs only when an underscore follows the
absolute file stem. An empty heading has exactly the bare stem, so its ID and
incoming edge retain the randomly named temporary directory. Replacing it with
the relative file-root ID would incorrectly merge two different nodes.

## Decision

After native extraction, normalize only the exact residual absolute-stem node.
Bind a separate heading ID to the full SHA-256 of its relative source path and
source location, reject collisions and missing locations, and remap both edge
endpoints. Preserve all labels, node fields, relations, and authoritative data.
Apply the same normalization to record-per-file and virtual source-packed
extraction. Keep the pinned Graphify runtime and reciprocal lexical algorithm.

Update the canonical builder and its exact integrated vendored copy, as required
by ADRs 0039 and 0103. Preserve historical Harbor and experimental next packages.
Use source-generic regression tests, independent full repeated builds, and
synthetic production layout/link checks to qualify this correctness repair.
No retrieval improvement or answer-quality gain is asserted by those checks.

Start a new profile study from the corrected frozen baseline. The code repair
is complete before realization and is present in every candidate and control;
it is not mixed into one profile mutation. Preserve the failed earlier native
jobs and all error denominators. In particular, the Graphify failure is not an
external infrastructure failure and must not be selectively retried or replaced.

Generate the native verifier's shell entrypoint with explicit LF bytes. The
earlier Windows default CRLF output prevented kernel execution despite passing
text-oriented checks. A regression must invoke the actual task generator, and
the independent native smoke must execute generated files without post-generation
rewriting. Keep this adapter correction distinct from the builder repair.

## Consequences

Previously unaffected documents keep their graph IDs. Empty headings retain
their own deterministic node and all links across temporary roots. Existing
published snapshots remain immutable; rebuilding affected sources changes the
derived graph digest while preserving authoritative core bytes.

The new study retains the fixed hypotheses, budgets, and acceptance rules of
ADR 0117. Its private portfolio has never been released and remains sealed;
neither correctness diagnostics nor candidate proposals may inspect it. Fresh
task and baseline digests, actual qualification receipts, and independent design
review are required before the new development stage.

See the [profile workflow](../../docs/retrieval-profile-evolution.md),
[profile experiment](0117-evolve-retrieval-construction-profiles-with-native-harbor.md),
and [Graphify projection contract](../../skills/build-semantic-okf-graphify/references/graphify-projection.md).
