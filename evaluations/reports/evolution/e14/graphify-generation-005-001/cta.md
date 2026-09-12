# EnterpriseRAG E14: Graphify generation 5 cost, time and quality

Each row is one original completed native observation. Model calls and reported provider cost are zero; host and orchestration costs are unpriced. Timing is descriptive for the fixed evaluation workflow, with no tested significance or service-level speedup claim.

| Candidate | nDCG x100 | Job seconds | Agent seconds | Two-build seconds | Query p95 ms | Knowledge bytes | Reported provider USD |
| --- | --- | --- | --- | --- | --- | --- | --- |
| baseline | 8.12 | 3086.715 | 3037.652 | 2920.905 | 830.242 | 240091223 | 0.0 |
| versioned-001 | 7.03 | 3101.809 | 3055.472 | 2938.085 | 841.188 | 240091223 | 0.0 |
| versioned-002 | 6.85 | 3109.632 | 3060.040 | 2942.837 | 828.517 | 240091223 | 0.0 |
| versioned-003 | 27.90 | 3065.076 | 3012.700 | 2895.148 | 908.760 | 240091223 | 0.0 |
| versioned-004 | 27.94 | 3089.998 | 3043.847 | 2927.010 | 842.133 | 240091223 | 0.0 |
| versioned-005 | 27.93 | 3112.389 | 3062.329 | 2945.025 | 839.052 | 240091223 | 0.0 |

The 6 rows are cumulative; only `versioned-005` is new in this report. All have one attempt and zero retries. The original reference and all earlier observations remain consumed.

[Result and accounting](README.md) · [Paired groups](groups.md)
