# Classical full corpus: question categories

[Main report](README.md) · [CTA](cta.md)

Quality uses original qrels and a 0–100 scale. Counts identify the denominator. Unavailable quality for categories without qrels is not zero. One fixed Top-10 pass.

| Category | Queries | With qrels | nDCG@10 | Recall@10 | MRR@10 | Full evidence@10 | P95 (ms) |
|---|---:|---:|---:|---:|---:|---:|---:|
| basic | 175 | 175 | 66.18 | 76.00 | 63.06 | 76.00 | 248.57 |
| completeness | 20 | 20 | 62.85 | 62.87 | 80.00 | 25.00 | 332.54 |
| conflicting_info | 20 | 20 | 84.61 | 85.00 | 91.25 | 75.00 | 159.73 |
| constrained | 30 | 30 | 87.97 | 93.33 | 90.00 | 90.00 | 370.78 |
| high_level | 10 | 0 | N/A | N/A | N/A | N/A | 103.44 |
| info_not_found | 20 | 0 | N/A | N/A | N/A | N/A | 246.73 |
| intra_document_reasoning | 40 | 40 | 90.65 | 95.00 | 89.17 | 95.00 | 238.40 |
| miscellaneous | 20 | 20 | 88.09 | 95.00 | 85.83 | 95.00 | 219.59 |
| project_related | 40 | 40 | 59.67 | 64.67 | 81.90 | 25.00 | 258.91 |
| semantic | 125 | 125 | 22.38 | 36.80 | 18.07 | 36.80 | 305.54 |

## Luna internal answer quality by question category

All categories use Luna answers and a Luna judge under the same fixed protocol.

| Category | Questions | Overall | Correctness | Completeness |
|---|---:|---:|---:|---:|
| basic | 175 | 54.38% | 78.29% | 55.01% |
| completeness | 20 | 20.13% | 55.00% | 33.81% |
| conflicting_info | 20 | 56.16% | 85.00% | 63.09% |
| constrained | 30 | 79.73% | 86.67% | 87.52% |
| high_level | 10 | 53.00% | 70.00% | 53.00% |
| info_not_found | 20 | 100.00% | 100.00% | 100.00% |
| intra_document_reasoning | 40 | 67.29% | 87.50% | 71.04% |
| miscellaneous | 20 | 52.17% | 90.00% | 54.67% |
| project_related | 40 | 32.96% | 57.50% | 52.38% |
| semantic | 125 | 25.20% | 45.60% | 28.99% |

Category scores are descriptive breakdowns; no category drove a mutation or selection.
