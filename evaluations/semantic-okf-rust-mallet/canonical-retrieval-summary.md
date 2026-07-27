# Reference-aware RustMallet Canonical Retrieval Summary

## Outcome

The reference-aware RustMallet candidate completed the canonical 40-question
direct-retrieval evaluation at Top 10 and pool 100. All four routes ran without
errors, every returned hit passed exact evidence validation, the authoritative
core matched the canonical bundle, and deep validation independently rederived
the fixed-seed topic model.

RustMallet is now reported in the general direct-retrieval table as an
experimental comparator. This reporting change does not add a ninth family to
the canonical Harbor registry.

## Canonical Top-10 results

| Route | All-40 Recall@10 | All-40 MRR@10 | All-40 nDCG@10 | Hard-10 Recall@10 | Hard-10 MRR@10 | Hard-10 nDCG@10 | Mean ms | P95 ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `rust_mallet_bm25` | 49.72% | 95.83% | 60.94% | 63.17% | 95.00% | 69.31% | 194.77 | 226.69 |
| `rust_mallet_topic` | 80.80% | 95.00% | 81.86% | 88.50% | 95.00% | 82.75% | 206.08 | 238.70 |
| `rust_mallet_association` | 79.49% | 94.58% | 80.84% | 86.50% | 95.00% | 81.18% | 191.92 | 224.30 |
| `rust_mallet_fusion` | 80.28% | 95.83% | 81.84% | 86.00% | 95.00% | 81.40% | 199.92 | 232.25 |

The shared deep-validation setup took 12,150.39 ms. The complete Top-10
evaluator, including setup and all 160 timed route/question queries, took
44,746.75 ms.

## Pool-100 and reference parity

The independent pool-100 evaluator took 48,463.00 ms. Topic, association, and
fusion retained their Top-10-scored quality metrics. BM25 improved when given
the larger returned pool, as expected from the existing candidate-budget
analysis.

The final reference parity gate executed 320 comparisons across 40 questions,
four modes, and both returned-pool sizes. It checked 7,267 returned reference
rows, exercised 728 distinct compact IDs, and found zero ranking mismatches.

## Interpretation

The strongest RustMallet route by all-40 recall is `rust_mallet_topic` at
80.80%. It remains below classical fusion at 83.46%, adaptive fusion at 83.82%,
and the definitive ensemble policies at 83.82%. Its order quality is strong:
`rust_mallet_topic` reaches 81.86% all-40 nDCG and
`rust_mallet_fusion` reaches 81.84%, both above the entity-graph fusion row's
79.86%.

Latency is diagnostic rather than causal across families because setup,
dependencies, and candidate work differ. The canonical table therefore reports
the directly measured per-route P95 and separately discloses the shared
deep-validation setup and full evaluator wall time.
