# Semantic OKF Adaptive Retrieval Comparison

All routes used the same 40 questions, authoritative Semantic OKF core, direct top-10 protocol, and evidence-valid schema 1.2 contract. Metrics are paper-level; evidence validity is independently checked.

| Builder / consultant | Route | All recall@10 | All MRR@10 | All nDCG@10 | Hard recall@10 | Hard MRR@10 | Hard nDCG@10 | Evidence | Mean ms |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Legacy | `legacy_lexical` | 79.31% | 78.96% | 74.22% | 80.67% | 57.50% | 56.81% | 100% | 3.02 |
| Embedding | `new_lexical` | 54.75% | 88.83% | 60.92% | 73.50% | 80.33% | 65.78% | 100% | 70.94 |
| Embedding | `vector` | 50.40% | 78.75% | 54.77% | 61.00% | 66.67% | 53.05% | 100% | 110.60 |
| Embedding | `hybrid` | 48.34% | 88.54% | 56.51% | 65.17% | 87.50% | 64.60% | 100% | 202.46 |
| Entity graph | `entity_graph_lexical` | 79.76% | 96.67% | 81.14% | 84.67% | 86.67% | 74.47% | 100% | 116.94 |
| Entity graph | `entity_graph_entity` | 79.58% | 86.04% | 76.72% | 85.00% | 71.67% | 66.08% | 100% | 120.73 |
| Entity graph | `entity_graph_traversal` | 78.49% | 80.21% | 74.03% | 86.67% | 75.00% | 69.65% | 100% | 117.54 |
| Entity graph | `entity_graph_fusion` | 80.84% | 93.12% | 79.86% | 91.67% | 90.00% | 76.32% | 100% | 110.71 |
| Classical | `classical_bm25` | 49.72% | 95.83% | 60.94% | 63.17% | 95.00% | 69.31% | 100% | 86.43 |
| Classical | `classical_topic` | 82.42% | 93.33% | 82.25% | 93.00% | 95.00% | 83.75% | 100% | 94.62 |
| Classical | `classical_association` | 82.56% | 94.58% | 82.58% | 93.00% | 95.00% | 84.76% | 100% | 94.64 |
| Classical | `classical_fusion` | 83.46% | 95.83% | 83.23% | 95.50% | 95.00% | 84.98% | 100% | 94.63 |
| Adaptive | `adaptive_fusion` | 83.82% | 95.83% | 83.43% | 95.50% | 95.00% | 84.98% | 100% | 296.45 |

## Interpretation

Adaptive fusion has the highest observed all-40 recall@10 (83.82%) and nDCG@10 (83.43%). Relative to classical fusion, the deltas are +0.36 percentage points of recall and +0.20 points of nDCG.

On the hard ten, adaptive and classical fusion tie exactly at 95.50% recall, 95.00% MRR, and 84.98% nDCG.

Only 1 of 40 questions changed recall@10, MRR@10, or nDCG@10 between adaptive and classical fusion: q011-vector-graph-hybrid. The paired descriptive 95% bootstrap intervals, in percentage points, are [+0.00, +1.07] for recall and [+0.00, +0.60] for nDCG; intervals that include zero do not establish a general advantage.

The trade-off is compute: adaptive mean query time is 3.13x classical fusion in this in-process diagnostic. Every route returned 100% independently valid evidence with zero errors, so the accuracy difference is not caused by stale or fabricated hits.
