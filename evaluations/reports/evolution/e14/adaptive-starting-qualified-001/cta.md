# Adaptive starting roles: cost, time and quality

| Role | Job seconds | Agent seconds | Two-build seconds | Query P95, ms | Knowledge bytes | nDCG@10 x100 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline | 1,356.011 | 1,305.630 | 577.116 | 8,356.394 | 557,899,137 | 60.04 |
| retained-start | 1,327.367 | 1,277.898 | 562.077 | 8,479.284 | 557,899,136 | 66.21 |

New E14 work in this report totals **2,683.378 job seconds** and **2,583.528 agent seconds**. These are summed completed job durations, excluding any historical imports, other families and controller overhead. They are not total campaign wall time.

All included native jobs report zero model calls, zero provider tokens and USD 0.00 provider cost. Host compute and orchestration costs are not priced, so a complete dollar total is unavailable. No Luna answering or judging stage is included. Timing is descriptive on a shared host, which also performed application coverage checks; it is not an isolated causal speed comparison.

The initial coverage run encountered one `PermissionError` in the Confluence snapshot test. The targeted test and a fresh complete run passed without an application-source change: **1,636 tests, 373 subtests and 90.5% application coverage**. The failed run remains preserved. This software test outcome did not repeat a native retrieval trial or consume a mutation quality miss.

[Quality and opportunities](README.md) · [Applications and categories](groups.md) · [Aggregate](aggregate.json)
