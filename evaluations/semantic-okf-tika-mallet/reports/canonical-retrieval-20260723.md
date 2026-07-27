# Tika/MALLET Canonical Retrieval Audit

- Status: `pass`
- Ranking eligible: `true`
- Questions: `40`
- Selected route: `tika_mallet_fusion`
- Replicated Top-10 rankings and pool-100 rankings: exact
- Top-10/pool-100 prefix parity in both builds: exact
- Exact evidence validity: `1.0000`

| Recall@10 | Hard Recall@10 | MRR@10 | nDCG@10 | Mean ms | p95 ms |
|---:|---:|---:|---:|---:|---:|
| 0.7482 | 0.7183 | 0.8750 | 0.7544 | 77.13 | 86.36 |

Latency excludes the shared deep-validation setup. This audit measures retrieval and evidence mechanics only, not prose-level semantic answer quality.
