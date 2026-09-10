# Collect completed semantic-validation state after its frame returns

Status: Accepted as a prospective construction treatment; no native acceptance
or canonical installation.

Date: 2026-09-10

## Context

The first correction under [ADR 0137](0137-charge-construction-corrections-within-enterprise-search-caps.md)
still failed during full-workload standalone Ensemble validation with a
container OOM event. Its precise allocation site remains unknown. A bounded
public observation found five parsed RDF graphs and one returned SHACL graph
alive immediately after the unchanged semantic validator returned. A later
snapshot found them reclaimed, but did not isolate manual collection from
automatic collection during the intervening operations.

## Decision

Charge a second, separate Ensemble construction proposal within the inherited
caps. Change only its builder's vendored `_semantic_okf.py`: retain the entire
original validation body under a private function name and use the unchanged
public signature to call it once, collect after its complete frame returns,
and return that same result. Preserve invalid result objects and propagate
inner exceptions without interception. Freeze consultation and all other files.

Keep artifact, query, report and rejection behavior as hard correctness
requirements. Preserve both previous consumed construction measurements. This
proposal owns one distinct prospective first measurement, with no automatic
retry; its reservation brings cumulative claims to 84 and Ensemble claims to 2.
Full native evaluation requires the exact task binding under
[ADR 0133](0133-version-exact-builder-bindings-in-feasibility-tasks.md), the
original workload and resource limits, and independent execution review.

## Evidence and consequences

The [candidate report](../../evaluations/reports/evolution/e11/ensemble-semantic-return-001/README.md)
records five passing sealed commands and a retained Python 3.12.13 fixture
with identical 35-file outputs, all three nonempty query responses, and one
exact corruption-rejection JSON pair. Only one file changed; 251 are unchanged.
This establishes finite correctness compatibility, not full-corpus resource
fit or retrieval improvement.

Post-frame collection cannot lower a peak inside validation itself and can
add runtime overhead. Public introspection and traceback structure change
because the original body is now private and the wrapper adds a frame. Do not
claim their identity or the original OOM cause from these tests. Keep the exact
candidate sealed and canonical skills unchanged pending native qualification
and the declared final acceptance boundaries.
