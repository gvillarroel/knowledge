# Tika/MALLET/Tantivy Canonical Retrieval Audit

- Status: `pass`
- Ranking eligible: `true`
- Questions: `40`
- Selected route: `tika_mallet_tantivy_fusion`
- Replicated Top-10 and pool-100 rankings: exact
- Top-10/pool-100 prefix parity in both bundles: exact
- Evaluator inputs and immutable bundle identities: exact
- Exact evidence validity: `1.0000`

| Recall@10 | Hard Recall@10 | MRR@10 | nDCG@10 | Mean ms | P95 ms |
|---:|---:|---:|---:|---:|---:|
| 0.7350 | 0.7383 | 0.8479 | 0.7175 | 353.41 | 470.74 |

ADR 0055 defined the selected fusion route before this evaluation. Latency excludes shared deep validation. This audit measures retrieval and evidence mechanics, not prose-level semantic answer quality.
