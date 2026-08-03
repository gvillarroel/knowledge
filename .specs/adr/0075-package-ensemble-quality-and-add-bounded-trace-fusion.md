# ADR 0075: Package Ensemble quality and add bounded trace fusion

## Status

Accepted on 2026-07-28 for an experimental deterministic retrieval candidate
and retrospective ranking. This is not a holdout-qualified promotion or a
grounded answer-quality claim.

## Context

The canonical Ensemble `quality` policy ranked first on the frozen
`graphrag-papers-40` direct-retrieval table with 83.82% Recall@10, 100.00%
MRR@10, and 85.20% nDCG@10. Its validated knowledge snapshot contained the
complete adaptive, entity-graph, BM25, and pinned embedding artifacts, but no
standalone expert package preserved that exact multi-file runtime.

Earlier trace-distillation work produced an independent fielded-BM25 paper
ranking. That route had complementary coverage, but replacing the quality
policy would discard its stronger ordering. Every registered question and
qrel had prior exposure, so no remaining cohort could support prospective
promotion.

## Decision

Extend `build-specialized-skill` with repeatable, hash-bound `--query-support`
files for custom query adapters. Require every support file to be a regular
direct child of the generated `scripts/` directory, reject duplicate or
reserved names, bind every byte in `expert-manifest.json`, and reject unbound
support files during validation.

First package the exact quality policy as
`graphrag-ensemble-quality-expert-v46`. Fix its internal candidate budget at
ten so caller limits cannot change the protected set. Require the exact offline
Sentence Transformers model and immutable revision. The package must reproduce
the canonical quality metrics before any evolution is considered.

Then run a closed retrospective search on q001-q024 over 1,800 global
quality/trace fusion operators. Restrict both contributing ranks and the union
to their exact Top-10 budgets. Exclude the schema-1.0 selection and v47 package
because the selector incorrectly credited trace ranks below ten even though
the executable adapter did not.

Freeze schema 1.1 with a regression test for the candidate-budget boundary.
Select the union operator with quality weight 9, trace weight 5, RRF constant
0, and stable quality-first ties. Package it as
`graphrag-ensemble-quality-trace-expert-v48` under retrieval contract
`ensemble-quality-trace-union-rrf-v3`.

Evaluate the immutable v48 package independently at Top 10 and pool 100 on all
forty questions. Replace the Ensemble `quality` predecessor in the comparable
table instead of counting both stages of the same evolution.

## Consequences

- The pure v46 expert reproduces Ensemble `quality` exactly: 83.82% Recall@10,
  100.00% MRR@10, and 85.20% nDCG@10.
- V48 reaches 85.39% Recall@10, 100.00% MRR@10, and 86.02% nDCG@10.
- Relative to pure quality, Recall@10 rises by 1.57 percentage points and
  nDCG@10 rises by 0.82 points.
- V48 remains position 1 of 24 under the nDCG-first ranking contract.
- Hard-10 Recall@10 remains 95.50%, while hard-10 nDCG@10 decreases by 1.71
  points to 86.56%.
- Selected P95 latency rises from 1461.92 ms to 2012.48 ms.
- All forty queries succeed, all 400 Top-10 evidence rows validate, and the
  Top-10 run is an exact prefix of the pool-100 run.
- The expert, its 904-file knowledge snapshot, and every support module remain
  hash-bound and byte-identical across evaluation.
- The result is retrospective. A new untouched cohort and a separate grounded
  answer evaluation are required for promotion.
