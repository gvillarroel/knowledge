# ADR 0116: Keep evaluation payloads local and publish dataset-scoped skill reports

Status: Accepted. Date: 2026-09-06.

## Context

The user requested an EnterpriseRAG-Bench dataset, executed comparisons, local
dataset storage excluded from Git, and reports organized by skill, CTA, dataset,
and overall dataset-specific leaders. Existing evaluations mix raw corpora,
processed snapshots, public summaries, and multiple incompatible measurement
contracts. Ignore rules alone do not remove previously tracked data.

## Decision

1. Add `evaluations/enterprise-rag-bench/` as a standalone retrospective direct
   retrieval diagnostic. Pin Onyx document release `v1.0.0`, question commit,
   archive, questions, and license hashes. Do not silently add a retrieval-only
   dataset to the canonical dual-mode Harbor registry.
2. Freeze a 40-question reduced population before strategy results: five per
   grounded category, all 85 required reference documents, and 100 deterministic
   distractors per source type. Retain the complete archive locally. State the
   reference-enrichment bias, unsupported no-qrel categories, one-organization
   family boundary, and absence of answer scoring or promotion eligibility.
3. Preserve original bytes. Normalize repeated qrel entries as sets. Quarantine
   all colliding document identities and fail if a selected reference is
   ambiguous. Never choose a document by archive iteration order.
4. Use the existing eight skill families, unchanged source-generic plans, and
   18 direct retrieval routes. Require independent build validation, duplicate
   deterministic builds, exact core identity parity, frozen code/data bindings,
   one fresh process per route, and three repetitions. Use hashing embeddings
   with no model calls. Keep raw results append-only and local.
5. Preserve existing dataset paths and bytes while removing ignored payloads
   from the index. Keep acquisition manifests, runtime code and locks, schemas,
   generators, and reports tracked. Do not rewrite Git history, move sealed
   evidence, or modify skill packages as part of the storage change.
6. Publish a generated `evaluations/reports/` hub using an explicit source
   catalog. Produce per-dataset and per-skill pages, a CTA cost/time/quality
   page, and a dataset-specific highest-primary-metric table. Read reviewed
   aggregate publications only and retain SHA-256 provenance.
7. Preserve metric units, missing values, ties, source contracts, error
   denominators, and release limits. Do not pool datasets or conflate retrieval,
   answer correctness, model tokens, dollars, and local runtime. Historical
   source reports remain authoritative in their existing locations.

## Consequences

The reduced EnterpriseRAG test is feasible on the local machine and replayable
without external model credentials. It does not establish official Onyx
performance or untouched validation. Its question-independent projections
cannot be tuned against this report for a future independent claim.

Future commits exclude downloaded and generated dataset bytes while preserving
the user's local data. Earlier Git history still contains old payloads. Fresh
clones must reacquire public data or restore authorized private fixtures before
running historical dataset-dependent checks. Aggregate hub regeneration uses
tracked publications alone and remains available without those fixtures.

The canonical dataset registry and prior ADRs governing Harbor execution,
independent validation, skill promotion, and evidence release retain their
authority. This decision introduces no new optimizer or Harbor scorer.

## Verification

Run deterministic dataset regeneration, existing registry validation, the new
adapter/catalog/index unit tests, report regeneration checks, local link
validation, and `python scripts/check_coverage.py --threshold 80`. Inspect the
pytest exit status separately from the reported coverage total.
