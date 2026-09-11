# Graphify starting roles: cost, time and quality

| Role | Job seconds | Agent seconds | Two-build seconds | Query P95, ms | Knowledge bytes | nDCG@10 x100 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline | 3,086.715 | 3,037.652 | 2,920.905 | 830.242 | 240,091,223 | 8.12 |

New E14 work in this report totals **3,086.715 job seconds** and **3,037.652 agent seconds**. These are summed completed job durations, excluding any historical imports, other families and controller overhead. They are not total campaign wall time.

All included native jobs report zero model calls, zero provider tokens and USD 0.00 provider cost. Host compute and orchestration costs are not priced, so a complete dollar total is unavailable. No Luna answering or judging stage is included. Timing is descriptive on a shared host, which also performed application coverage checks; it is not an isolated causal speed comparison.

The initial coverage run encountered one `PermissionError` in the Confluence snapshot test. The targeted test and a fresh complete run passed without an application-source change: **1,636 tests, 373 subtests and 90.5% application coverage**. The failed run remains preserved. This software test outcome did not repeat a native retrieval trial or consume a mutation quality miss.

[Quality and opportunities](README.md) · [Applications and categories](groups.md) · [Aggregate](aggregate.json)
