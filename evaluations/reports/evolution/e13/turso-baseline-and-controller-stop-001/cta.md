# E13 Turso reference: cost, time and quality

The original Turso baseline completed once. These are descriptive measurements
of that single native job on the unchanged stratified EnterpriseRAG workload.
They do not establish a speedup or a new retained retrieval champion.

| Measure | Observed value | Scope |
| --- | ---: | --- |
| Native job duration | 415.52 seconds | Job start to terminal result |
| Agent duration | 365.15 seconds | Native agent execution interval |
| Two-build duration | 174.34 seconds | Determinism build work reported by the task |
| Query p95 | 2,442.05 milliseconds | Turso lexical-sql route, 120 queries |
| Knowledge size | 842,070,178 bytes | Task-reported generated snapshot |
| Weighted nDCG@10 x100 | 45.43 | 112 eligible questions; population weight 470 |
| Completed trials / native errors / retries | 1 / 0 / 0 | Original allocated baseline |
| Model calls / reported model cost | 0 / USD 0.00 | Deterministic retrieval agent |
| Machine cost, engineering time and energy | Unavailable | Not measured |

The job, agent and build intervals overlap; do not add them. The zero reported
model cost excludes host computation and engineering effort. No new answer
generation or Luna judge call occurred in E13.

Adaptive's denied admission and the shared controller stop are separate from
the completed Turso job. They consumed no additional native trial or mechanism
quality miss. Reporting and software checks also do not count as new benchmark
measurements.

[Current native result](README.md#current-measurement)
· [Retained family comparison](README.md#retained-eight-family-comparison)
· [Application and category aggregates](groups.md) · [Aggregate](aggregate.json)
