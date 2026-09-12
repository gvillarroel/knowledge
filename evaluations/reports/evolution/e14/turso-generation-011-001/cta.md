# EnterpriseRAG E14: Turso generation 11 cost, time and quality

Each row is one original completed native observation. Model calls and reported provider cost are zero; host and orchestration costs are unpriced. Timing is descriptive for the fixed evaluation workflow, with no tested significance or service-level speedup claim.

| Candidate | nDCG x100 | Job seconds | Agent seconds | Two-build seconds | Query p95 ms | Knowledge bytes | Reported provider USD |
| --- | --- | --- | --- | --- | --- | --- | --- |
| baseline | 45.43 | 415.515 | 365.147 | 174.339 | 2442.047 | 842070178 | 0.0 |
| retained-start | 72.08 | 246.684 | 195.422 | 175.684 | 102.276 | 842070178 | 0.0 |
| versioned-000-pending-continuation-002 | 69.31 | 249.963 | 196.893 | 176.918 | 104.684 | 842070178 | 0.0 |
| versioned-001 | 72.13 | 230.526 | 182.149 | 162.446 | 104.090 | 842070178 | 0.0 |
| versioned-002 | 71.13 | 229.063 | 178.903 | 158.845 | 106.755 | 842070178 | 0.0 |
| versioned-003 | 66.80 | 246.432 | 200.646 | 180.992 | 101.799 | 842070178 | 0.0 |
| versioned-004 | 61.35 | 262.840 | 214.227 | 194.294 | 106.165 | 842070178 | 0.0 |
| versioned-005 | 70.44 | 251.183 | 202.867 | 183.154 | 100.656 | 842070178 | 0.0 |
| versioned-006 | 72.12 | 239.743 | 189.410 | 169.650 | 100.270 | 842070178 | 0.0 |
| versioned-007 | 72.38 | 233.211 | 184.574 | 164.718 | 103.962 | 842070178 | 0.0 |
| versioned-008 | 72.12 | 247.243 | 195.441 | 175.311 | 101.509 | 842070178 | 0.0 |
| versioned-009 | 71.97 | 246.421 | 197.608 | 177.318 | 113.728 | 842070178 | 0.0 |
| versioned-010 | 69.24 | 246.103 | 198.890 | 178.443 | 110.673 | 842070178 | 0.0 |

The 13 rows are cumulative; only `versioned-010` is new in this report. All have one attempt and zero retries. The original reference and all earlier observations remain consumed.

[Result and accounting](README.md) · [Paired groups](groups.md)
