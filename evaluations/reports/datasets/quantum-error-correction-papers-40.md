# Quantum error correction (40)

## Direct comparison

| Pos. | Pair / strategy | nDCG@10 | Recall@10 | MRR@10 | P95 (ms) |
|---:|---|---:|---:|---:|---:|
| 1 | specialized-expert / retrospective-supervised-ngram | 100.00% | 100.00% | 100.00% | 34.01 ms |
| 2 | specialized-expert / baseline-lexical | 36.67% | 74.58% | 27.40% | 123.55 ms |

All 40 qrels were exposed to supervised-profile construction. In-sample fixed-workload comparison only; no promotion or unseen-query claim.

[Original report](../../../evaluations/quantum-error-correction-papers/reports/retrospective-supervised-expert-evaluation.md) · [Report hub](../README.md) · [CTA](../cta/README.md)

Primary comparison: **nDCG@10**. N/A is an unavailable or unmeasured value. This table does not score generated-answer correctness.

Publication source SHA-256: `4e9aca1f74f6ac6590f037f3baf87c5840b9c18e982ccf296f44ea18f7c4def6`.
