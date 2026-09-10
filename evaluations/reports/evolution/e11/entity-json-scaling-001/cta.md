# Entity public JSON diagnostic: cost, time and scope

These are deterministic software profiles, separate from native EnterpriseRAG
jobs and generated-answer measurements. [Outcome](README.md) · [Aggregate](aggregate.json).

| Records | Operation | Elapsed seconds | Candidate extraction seconds | Mention matching seconds |
| ---: | --- | ---: | ---: | ---: |
| 256 | build | 11.019 | 3.091 | 0.717 |
| 256 | validate | 3.532 | 1.051 | 0.223 |
| 256 | consult-deep | 2.329 | 1.071 | 0.212 |
| 1024 | build | 42.700 | 13.645 | 3.086 |
| 1024 | validate | 13.167 | 4.504 | 0.994 |
| 1024 | consult-deep | 9.608 | 4.586 | 1.051 |

The failed original 1,024-record build adds 31.853 observed seconds, without a
completed profile or valid snapshot. Across both declarations, two containers
attempted seven child commands: six passed, one ended with signal 11, and two
original commands were never attempted. The failed cell remains visible.

All commands retained 2 CPU, 6 GiB and a 300-second limit. Configured memory is
not observed peak use. Staging, snapshot inventory checks and export occur
outside the command profiles. Function times are nested and cannot be summed
with command time. No host compute price or model usage was recorded; costs
and missing telemetry remain unavailable.

There is one source family, one observation per successful cell and no native
retrieval quality score. The instrumentation differs across input sizes. No
speedup ratio, uncertainty interval, public rank or complete-workload result is
claimed. Candidate and proposal counts remain unchanged at 86 cumulative claims.
