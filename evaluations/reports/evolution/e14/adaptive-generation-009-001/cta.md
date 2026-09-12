# EnterpriseRAG E14: Adaptive generation 9 cost, time and quality

Each row is one original completed native observation. Model calls and reported provider cost are zero; host and orchestration costs are unpriced. Timing is descriptive for the fixed evaluation workflow, with no tested significance or service-level speedup claim.

| Candidate | nDCG x100 | Job seconds | Agent seconds | Two-build seconds | Query p95 ms | Knowledge bytes | Reported provider USD |
| --- | --- | --- | --- | --- | --- | --- | --- |
| baseline | 60.04 | 1356.011 | 1305.630 | 577.116 | 8356.394 | 557899137 | 0.0 |
| retained-start | 66.21 | 1327.367 | 1277.898 | 562.077 | 8479.284 | 557899136 | 0.0 |
| versioned-000-pending-continuation-001 | 64.53 | 1315.955 | 1268.433 | 565.299 | 7878.641 | 557899136 | 0.0 |
| versioned-001 | 62.31 | 1338.888 | 1287.717 | 573.127 | 8293.559 | 557899134 | 0.0 |
| versioned-002 | 65.78 | 1323.299 | 1276.661 | 561.518 | 8330.636 | 557899134 | 0.0 |
| versioned-003 | 65.52 | 1375.860 | 1325.606 | 572.182 | 8576.669 | 557899136 | 0.0 |
| versioned-004 | 65.61 | 1318.217 | 1271.261 | 579.663 | 8158.884 | 557899136 | 0.0 |
| versioned-005 | 54.79 | 1330.339 | 1281.685 | 564.720 | 8377.184 | 557899136 | 0.0 |
| versioned-006 | 47.65 | 1310.781 | 1262.113 | 553.158 | 8222.328 | 557899136 | 0.0 |
| versioned-007 | 65.47 | 1301.464 | 1248.247 | 560.135 | 7744.366 | 557899138 | 0.0 |
| versioned-008 | 65.12 | 1330.699 | 1277.062 | 583.240 | 7910.434 | 557899134 | 0.0 |

The 11 rows are cumulative; only `versioned-008` is new in this report. All have one attempt and zero retries. The original reference and all earlier observations remain consumed.

[Result and accounting](README.md) · [Paired groups](groups.md)
