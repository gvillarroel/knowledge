# EnterpriseRAG E14: Graphify gain and retained-family CTA

Each row is an original completed native observation. Model calls and reported provider cost are zero; host and orchestration costs are unpriced. Timing is descriptive for the fixed workflow; no significance or service-level speedup is claimed.

## Graphify measured profiles

| Profile | nDCG x100 | Job seconds | Agent seconds | Two-build seconds | Query p95 ms | Knowledge bytes | Reported provider USD |
| --- | --- | --- | --- | --- | --- | --- | --- |
| baseline | 8.12 | 3086.715 | 3037.652 | 2920.905 | 830.242 | 240091223 | 0.0 |
| versioned-001 | 7.03 | 3101.809 | 3055.472 | 2938.085 | 841.188 | 240091223 | 0.0 |
| versioned-002 | 6.85 | 3109.632 | 3060.040 | 2942.837 | 828.517 | 240091223 | 0.0 |
| versioned-003 | 27.90 | 3065.076 | 3012.700 | 2895.148 | 908.760 | 240091223 | 0.0 |
| versioned-004 | 27.94 | 3089.998 | 3043.847 | 2927.010 | 842.133 | 240091223 | 0.0 |
| versioned-005 | 27.93 | 3112.389 | 3062.329 | 2945.025 | 839.052 | 240091223 | 0.0 |
| versioned-006 | 27.93 | 3110.764 | 3057.317 | 2937.184 | 860.645 | 240091223 | 0.0 |
| versioned-007 | 34.16 | 3071.225 | 3020.158 | 2894.397 | 935.123 | 240091223 | 0.0 |
| versioned-008 | 52.33 | 2995.954 | 2948.095 | 2818.045 | 960.697 | 240091223 | 0.0 |

These 9 rows are cumulative; only `versioned-008` is new in this report. All have one attempt and zero retries. The original reference and earlier observations remain consumed.

## Retained family profiles

| Profile | nDCG x100 | Job seconds | Agent seconds | Two-build seconds | Query p95 ms | Knowledge bytes | Reported provider USD |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Legacy | 72.38 | 123.980 | 77.135 | 60.576 | 98.090 | 180168866 | 0.0 |
| Turso | 72.38 | 233.211 | 184.574 | 164.718 | 103.962 | 842070178 | 0.0 |
| Adaptive | 66.21 | 1327.367 | 1277.898 | 562.077 | 8479.284 | 557899136 | 0.0 |
| Embeddings | 63.51 | 1047.799 | 1000.296 | 580.000 | 1988.105 | 249909785 | 0.0 |
| Classical | 62.10 | 1571.806 | 1522.887 | 578.193 | 2041.407 | 557897958 | 0.0 |
| Graphify | 52.33 | 2995.954 | 2948.095 | 2818.045 | 960.697 | 240091223 | 0.0 |

[Result and accounting](README.md) · [Paired groups](groups.md) · [General comparison](comparison.md)
