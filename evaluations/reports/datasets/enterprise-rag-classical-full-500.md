# EnterpriseRAG full corpus: Classical (500)

## Direct comparison

| Pos. | Pair / strategy | nDCG@10 | Recall@10 | MRR@10 | P95 (ms) |
|---:|---|---:|---:|---:|---:|
| 1 | classical / Classical / BM25 | 59.03% | 67.97% | 59.53% | 286.40 ms |

All 511,962 physical documents and all 500 public questions; retrieval quality means on the 470 questions with original qrels, latency on all 500. One unchanged Classical BM25 route, Top-10, one pass, disk-backed native-score adapter. Classical is the only measured alternative, so its local row number is not a public rank or evidence of superiority over other skills. This catalog row measures retrieval only; the source report owns the separate GPT-5.4 answer-stage status and official Overall availability. It does not measure a complete Semantic OKF bundle, agent skill selection or an independent promotion gate. The 985-document comparisons remain separate.

[Original report](../../../evaluations/reports/enterprise-classical-full/README.md) · [Report hub](../README.md) · [CTA](../cta/README.md)

Primary comparison: **nDCG@10**. N/A is an unavailable or unmeasured value. This table does not score generated-answer correctness.

Publication source SHA-256: `5c9e108eb5163c7f87332ba427ee8c2192e4cb6b0c54c1d0788cc97218a07f14`.
