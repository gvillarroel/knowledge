# Three-cohort GraphRAG retrieval comparison

The formal position is controlled only by the sixty-question evaluation-only
cohort. The exposed cohorts are diagnostic columns.

| Pos. | Frozen strategy | Exposed-40 nDCG | Post-v51-20 nDCG | Eval-only-60 Recall | Eval-only-60 MRR | Eval-only-60 nDCG | Stability | P95 |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | `v44-classical-hybrid` | 83.47% | 97.52% | 100.00% | 100.00% | 99.64% | 100.00% | 982.84 ms |
| 2 | `v45-early-confidence` | 83.75% | 97.52% | 100.00% | 99.17% | 99.03% | 100.00% | 989.63 ms |
| 3 | `v46-ensemble-quality` | 85.20% | 97.92% | 100.00% | 96.67% | 97.30% | 100.00% | 4469.44 ms |
| 4 | `v48-ensemble-quality-trace` | 86.02% | 98.22% | 100.00% | 96.67% | 97.24% | 100.00% | 4855.90 ms |
| 5 | `v43-fielded-bm25` | 81.76% | 99.26% | 100.00% | 91.39% | 91.66% | 100.00% | 344.82 ms |
| 6 | `v51-supervised-profiles` | 100.00% | 52.36% | 71.11% | 34.11% | 41.03% | 43.33% | 142.67 ms |
| 7 | `v39-default-lexical` | 66.57% | 34.85% | 70.28% | 27.15% | 36.05% | 100.00% | 420.97 ms |

The forty canonical questions are exposed fixed-workload evidence. The twenty
post-v51 questions are opened evaluation evidence. The sixty-question cohort
is registered as evaluation-only and is forbidden from construction,
retrieval-profile forging, evolution, trace distillation, candidate selection,
or optimizer-visible fitness.

All metrics measure direct Top-10 paper retrieval rather than generated-answer
correctness. Expected answers are bound to reviewed claims and exact source
pages, without a new independent human adjudication.
