# EnterpriseRAG E14: Graphify generation 20 cost, time and quality

Each row is one original completed native observation. Model calls and reported provider cost are zero; host and orchestration costs are unpriced. Timing is descriptive for the fixed evaluation workflow, with no tested significance or service-level speedup claim.

| Candidate | nDCG x100 | Job seconds | Agent seconds | Two-build seconds | Query p95 ms | Knowledge bytes | Reported provider USD |
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
| versioned-009 | 57.63 | 2971.901 | 2921.719 | 2789.978 | 1096.017 | 240091223 | 0.0 |
| versioned-010 | 63.46 | 3074.904 | 3023.143 | 2878.057 | 1069.005 | 240091223 | 0.0 |
| versioned-011 | 59.35 | 2951.727 | 2903.249 | 2778.698 | 942.157 | 240091223 | 0.0 |
| versioned-012 | 54.45 | 2912.948 | 2859.062 | 2738.842 | 1028.413 | 240091223 | 0.0 |
| versioned-013 | 52.33 | 2872.140 | 2816.814 | 2698.482 | 910.358 | 240091223 | 0.0 |
| versioned-014 | 60.49 | 2825.620 | 2777.555 | 2659.194 | 894.487 | 240091223 | 0.0 |
| versioned-015 | 60.48 | 2817.325 | 2769.592 | 2652.356 | 893.774 | 240091223 | 0.0 |
| versioned-016 | 63.72 | 2830.152 | 2781.530 | 2664.846 | 904.768 | 240091223 | 0.0 |
| versioned-017 | 63.46 | 2816.410 | 2767.346 | 2648.224 | 919.664 | 240091223 | 0.0 |
| versioned-018 | 63.46 | 2815.164 | 2766.753 | 2648.297 | 920.351 | 240091223 | 0.0 |
| versioned-019 | 34.08 | 2816.933 | 2769.374 | 2649.648 | 929.864 | 240091223 | 0.0 |
| versioned-020 | 52.42 | 2831.217 | 2781.524 | 2664.581 | 913.800 | 240091223 | 0.0 |

The 21 rows are cumulative; only `versioned-020` is new in this report. All have one attempt and zero retries. The original reference and all earlier observations remain consumed.

[Result and accounting](README.md) · [Paired groups](groups.md)
