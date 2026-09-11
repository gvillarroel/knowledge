# EnterpriseRAG E14: pending-variant cost, time and quality

Each row describes one original native observation. The Turso reference is the original E13 job; it was not rerun. Provider cost is the value recorded by the native agent. All six records report zero model calls. Host and orchestration costs are unpriced. Differences in elapsed time are descriptive and were not tested for significance.

| Family | Role | nDCG x100 | Job seconds | Agent seconds | Two-build seconds | Query p95 ms | Knowledge bytes | Reported provider USD |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Turso | Original reference | 45.43 | 415.515 | 365.147 | 174.339 | 2442.047 | 842070178 | 0.0 |
| Turso | Retained incumbent | 72.08 | 246.684 | 195.422 | 175.684 | 102.276 | 842070178 | 0.0 |
| Turso | New pending measurement | 69.31 | 249.963 | 196.893 | 176.918 | 104.684 | 842070178 | 0.0 |
| Adaptive | Original reference | 60.04 | 1356.011 | 1305.630 | 577.116 | 8356.394 | 557899137 | 0.0 |
| Adaptive | Retained incumbent | 66.21 | 1327.367 | 1277.898 | 562.077 | 8479.284 | 557899136 | 0.0 |
| Adaptive | New pending measurement | 64.53 | 1315.955 | 1268.433 | 565.299 | 7878.641 | 557899136 | 0.0 |

Both families use the frozen workload and their registered treatment separation: Turso consultation and Adaptive construction. The primary routes are `lexical-sql` for Turso and `adaptive` for Adaptive. No cost-adjusted winner or answer-generation score is selected. Full route metrics are preserved in [aggregate.json](aggregate.json).

[Results and search accounting](README.md) · [Application/category comparison](groups.md)
