# Trace-Improved Specialized Expert Study

Date: 2026-07-28

## Evidence boundary

The Harbor trace-distillation workflow was rerun under Harbor 0.18.0 for both
source studies. Schema-2 `--dry-run` and `--doctor` passed, and fresh
`--analyze-only` outputs reproduced the accepted v39 and v42 proposal states
without executing a model or opening deferred Harbor holdout.

The direct-retrieval mutation was selected only on the registered 24-question
discovery cohort. The canonical six-question holdout had prior task exposure and
is therefore labeled descriptive rather than untouched. After candidate freeze,
q031-q040 served as the independent confirmation cohort.

## Frozen candidate

`graphrag-trace-expert-v43` preserves the complete question, retains and expands
exact hyphenated facets, scores papers and reviewed claims with fielded BM25, and
fuses both channels before selecting one exact record per paper identity.

- Expert tree:
  `2532924b2c254fc17d1c6f6049d227568887b05e7403db6d800837e39f2546df`
- Knowledge tree:
  `e787e3ef4a2c2a3a624be0803a3536ab24c2dcdd66e4b894c2d0ec10634f1d9e`
- Retrieval contract: `trace-bm25-field-fusion-v1`
- Parameters: `k1=5.0`, `b=0.75`, paper weight `1.0`, claims weight `0.5`

The package validator, skill validator, manifest verification, representative
query, and byte-identical `--check` rebuild all passed.

## Cohort results

| Stage | Questions | Recall@10 | MRR@10 | nDCG@10 | Evidence |
|---|---:|---:|---:|---:|---:|
| Discovery development | 24 | 80.98% | 95.14% | 85.86% | 100.00% |
| Frozen confirmation | 10 | 85.50% | 67.26% | 70.40% | 100.00% |
| Canonical holdout, prior exposure | 6 | 86.12% | 91.67% | 84.34% | 100.00% |
| Canonical all-40 | 40 | 82.88% | 87.65% | 81.76% | 100.00% |

The development result improves nDCG@10 on 18 of 24 questions and regresses it
slightly on three. All three trace-source cases q006-q008 improve. The candidate
was not changed after the development result.

## Ranking

The checked
[improved retrieval audit](trace-improved-retrieval-20260728.md) replaces the
predecessor expert row under the same all-40 Top-10 contract. Exact Top-10
rankings are prefixes of the pool-100 run, every query has zero errors, every
returned evidence row validates, and the expert remains byte-identical.

The new version moves from position **19 to 10 of 24**:

| Version | Recall@10 | nDCG@10 | P95 | Position |
|---|---:|---:|---:|---:|
| Stable raw occurrence | 72.20% | 66.57% | 170.78 ms | 19 |
| Trace-derived fielded BM25 | 82.88% | 81.76% | 229.86 ms | 10 |

This is a deterministic retrieval rank, not a grounded answer-quality rank.

## Repository verification

- Focused builder, expert, evaluator, and audit tests: 8 passed.
- Complete repository suite: 2,103 passed and 16 skipped. Its only three
  failures are pre-existing standalone-boundary checks in three untouched
  skills.
- Required application coverage gate: 754 passed, 90.9% total coverage against
  an 80.0% threshold.
- Skill package validation, deterministic rebuild, report validation,
  comparison-contract validation, and all dataset registry checks passed.
