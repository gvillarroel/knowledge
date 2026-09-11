# EnterpriseRAG E14: Turso gain and retained-family CTA

Each row is an original native observation. The Turso baseline is the exact E13 job and was not rerun. Reported provider cost and model calls are zero; host and orchestration costs are unpriced. Elapsed time differences are descriptive and were not tested for significance.

## Turso measured profiles

| Profile | nDCG x100 | Job seconds | Agent seconds | Two-build seconds | Query p95 ms | Knowledge bytes | Reported provider USD |
| --- | --- | --- | --- | --- | --- | --- | --- |
| baseline | 45.43 | 415.515 | 365.147 | 174.339 | 2442.047 | 842070178 | 0.0 |
| retained-start | 72.08 | 246.684 | 195.422 | 175.684 | 102.276 | 842070178 | 0.0 |
| versioned-000-pending-continuation-002 | 69.31 | 249.963 | 196.893 | 176.918 | 104.684 | 842070178 | 0.0 |
| versioned-001 | 72.13 | 230.526 | 182.149 | 162.446 | 104.090 | 842070178 | 0.0 |

## Retained family profiles

| Profile | nDCG x100 | Job seconds | Agent seconds | Two-build seconds | Query p95 ms | Knowledge bytes | Reported provider USD |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Legacy | 72.38 | 123.980 | 77.135 | 60.576 | 98.090 | 180168866 | 0.0 |
| Turso | 72.13 | 230.526 | 182.149 | 162.446 | 104.090 | 842070178 | 0.0 |
| Adaptive | 66.21 | 1327.367 | 1277.898 | 562.077 | 8479.284 | 557899136 | 0.0 |
| Embeddings | 63.51 | 1047.799 | 1000.296 | 580.000 | 1988.105 | 249909785 | 0.0 |
| Classical | 62.10 | 1571.806 | 1522.887 | 578.193 | 2041.407 | 557897958 | 0.0 |
| Graphify | 8.12 | 3086.715 | 3037.652 | 2920.905 | 830.242 | 240091223 | 0.0 |

[Result and search accounting](README.md) · [Paired groups](groups.md) · [Six-family comparison](comparison.md)
