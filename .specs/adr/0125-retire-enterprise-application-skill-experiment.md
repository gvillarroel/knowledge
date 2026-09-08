# ADR 0125: Retire the Enterprise application-skill experiment

## Status

Accepted on 2026-09-07 after the fixed comparison, at the user's request.

## Context

ADR 0123 compared a unified Embeddings expert with nine application experts,
all available to the model on each of forty exposed questions. All eighty native
trials completed. The split treatment's raw final-evidence nDCG@10 was 82.37
versus 84.26 for the unified expert, with 2.13 times the tokens and 1.43 times
the latency. Complete-pair semantic results also favored the unified arm,
but seven missing pairs prevent a full-cohort semantic winner claim under
ADR 0124's bounds. No independent validation, installation, or promotion occurred.

The user requested that an unsuccessful split remain documented and that only
useful lessons remain in active work.

## Decision

Retire the application-split experiment without more model calls. Preserve all
native study evidence, generated experts, failed reviewer outputs, exact
implementation, tests, and original execution instructions in the ignored local
study archive. Remove experiment-specific runtime and orchestration from active
tracked source. Keep reviewed aggregate reports by application, category, CTA,
and general comparison, with explicit metric scopes and missing-review limits.

Retain two small tools with the canonical Enterprise adapter: a separately
versioned full-text input projection with source-to-ledger fidelity checks, and
the audit binding historical e6 results to title-only normalized records.
Preserve existing ontology/field declarations, original source bytes, and
deterministic v1 regeneration. Never rewrite historical datasets or scores.
Add the general structured-field and content-fidelity lesson to the canonical
multi-family builder instructions; do not introduce a retrieval-family or
application-routing default from this pilot.

Document citation marker/quotation failures, reviewer schema availability, and
routing overhead as observed failure modes. Do not weaken scoring, repair
historical answers, or treat usage frequency as individual skill quality.

## Validation

Require focused ingestion regression tests, a real canonical-builder fixture,
exact full-body verification of all ten completed experts, reproduction of the
114-trial scope audit, unchanged frozen study digests, resolved report links,
dataset exclusion checks, and the repository coverage gate of at least 80%.

[Completed findings and retained commands](../../docs/enterprise-source-skills.md)
