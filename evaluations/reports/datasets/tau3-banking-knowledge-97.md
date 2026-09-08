# tau3 banking knowledge (97)

## Direct comparison

| Pos. | Pair / strategy | nDCG@10 | Recall@10 | MRR@10 |
|---:|---|---:|---:|---:|
| 1 | integrated-classical / Local topic | 42.90% | 35.27% | 69.20% |
| 2 | integrated-classical / Local BM25 | 42.80% | 35.41% | 67.20% |
| 3 | integrated-classical / Local association | 42.70% | 35.29% | 68.20% |
| 4 | integrated-classical / Local fusion | 42.10% | 35.09% | 68.00% |
| 5 | upstream-bm25 / Upstream BM25 | 15.60% | 14.72% | 33.80% |

P95 is not available for every measured alternative and is omitted from this primary table.

Retrospective oracle-context diagnostic. Local integrated Classical and chunked Classical have identical rankings. Official conversations and answer correctness were not measured.

[Original report](../../../evaluations/tau3-banking-knowledge/REPORT.md) · [Report hub](../README.md) · [CTA](../cta/README.md)

Primary comparison: **nDCG@10**. N/A is an unavailable or unmeasured value. This table does not score generated-answer correctness.

Publication source SHA-256: `55932d4955faf4eb6093394aa3ceb178c86b06d449bab027d467a0d9192a6a41`.
