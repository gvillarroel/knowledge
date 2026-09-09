# E11 starting measurements: cost, time and quality

The [terminal aggregate](aggregate.json) accounts for twelve original jobs:
nine genuinely new E11 executions and three original E10 imports. Imported
job time is shown separately and must not be charged twice. Execution errors
remain in the totals even though they provide no retrieval-quality measurement.

| Family and role | New E11 execution | Job seconds | Agent seconds | Qualified nDCG@10, 0–100 |
| --- | --- | ---: | ---: | ---: |
| Legacy baseline | No: E10 import | 123.58 | 72.20 | 61.11 |
| Legacy retained | No: E10 import | 125.73 | 78.35 | 72.38 |
| Embeddings baseline | No: E10 import | 1,035.12 | 986.25 | 63.51 |
| Classical baseline | Yes | 1,536.53 | 1,488.46 | 55.04 |
| Classical retained | Yes | 1,471.63 | 1,424.32 | 62.10 |
| Adaptive baseline | Yes | 1,273.95 | 1,225.12 | 60.04 |
| Adaptive retained | Yes | 1,268.29 | 1,220.46 | 66.21 |
| Entity Graph baseline | Yes | 3,649.14 | 3,600.09 | Unavailable: timeout |
| Ensemble baseline | Yes | 484.69 | 455.54 | Unavailable: memory failure |
| Graphify baseline | Yes | 3,091.79 | 3,040.09 | 8.12 |
| Turso baseline | Yes | 420.40 | 373.02 | 45.43 |
| Turso retained | Yes | 221.33 | 173.54 | 72.08 |

New E11 jobs accumulated **13,417.74 seconds (3.73 hours)**, including
**13,000.64 agent seconds (3.61 hours)**. These are summed job durations, not
campaign wall-clock duration: some jobs ran concurrently. The imported E10
jobs contribute a separate **1,284.42 seconds**, already counted in E10.

The ten qualified deterministic retrieval jobs report zero model tokens and
zero native model cost. The two errored jobs have missing usage telemetry.
Host compute has no recorded price. Consequently, a complete dollar total is
unavailable; missing telemetry and unpriced compute must not become zero cost.
These jobs do not include a Luna answer-generation or judge stage.

Job and agent time include construction and the task's validation/retrieval
work. They are not isolated query latency or build-time measurements. The
[family evidence index](../../../../../docs/enterprise-family-report-index.md)
links earlier component timing reports under their own exact workloads.

[Quality and qualification details](README.md) · [E11 overview](../README.md)
