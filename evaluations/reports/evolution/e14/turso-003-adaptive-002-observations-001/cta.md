# EnterpriseRAG E14: Turso generation-three and Adaptive generation-two CTA

Each row is its original native measurement; the Turso E13 reference was not rerun. All report zero model calls and provider cost. Host and orchestration costs remain unpriced. Time differences are descriptive and were not tested for significance.

| Family | Candidate | Role | nDCG x100 | Job seconds | Agent seconds | Two-build seconds | Query p95 ms | Knowledge bytes | Reported provider USD |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Turso | baseline | Original reference | 45.43 | 415.515 | 365.147 | 174.339 | 2442.047 | 842070178 | 0.0 |
| Turso | retained-start | Earlier measured candidate | 72.08 | 246.684 | 195.422 | 175.684 | 102.276 | 842070178 | 0.0 |
| Turso | versioned-000-pending-continuation-002 | Earlier measured candidate | 69.31 | 249.963 | 196.893 | 176.918 | 104.684 | 842070178 | 0.0 |
| Turso | versioned-001 | Retained incumbent | 72.13 | 230.526 | 182.149 | 162.446 | 104.090 | 842070178 | 0.0 |
| Turso | versioned-002 | Latest observation | 71.13 | 229.063 | 178.903 | 158.845 | 106.755 | 842070178 | 0.0 |
| Adaptive | baseline | Original reference | 60.04 | 1356.011 | 1305.630 | 577.116 | 8356.394 | 557899137 | 0.0 |
| Adaptive | retained-start | Retained incumbent | 66.21 | 1327.367 | 1277.898 | 562.077 | 8479.284 | 557899136 | 0.0 |
| Adaptive | versioned-000-pending-continuation-001 | Earlier measured candidate | 64.53 | 1315.955 | 1268.433 | 565.299 | 7878.641 | 557899136 | 0.0 |
| Adaptive | versioned-001 | Latest observation | 62.31 | 1338.888 | 1287.717 | 573.127 | 8293.559 | 557899134 | 0.0 |

Primary routes are `lexical-sql` for Turso and `adaptive` for Adaptive. Construction and consultation treatments retain their separate contracts.

[Results and accounting](README.md) · [Application/category groups](groups.md) · [Retained-family CTA](../turso-generation-002-001/cta.md)
