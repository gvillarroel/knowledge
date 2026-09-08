# Cost, time, and answer quality

Answering costs below use the Pi model catalog estimate; they are not measured subscription charges. Input tokens include cached input; the cached column is a subset, not an additional token charge.

| Metric | Unified expert | Nine source skills |
|---|---:|---:|
| Mean input tokens | 24341 | 52608 |
| Mean cached input tokens | 486 | 614 |
| Mean output tokens | 761 | 964 |
| Estimated answering cost, USD total | 0.22775 | 0.46273 |
| Mean agent seconds | 39.05 | 55.99 |
| p95 agent seconds | 59.40 | 80.30 |
| Mean model rounds | 4.45 | 4.28 |
| Mean searches | 1.50 | 4.17 |
| Mean document reads | 1.93 | 2.05 |
| Required-fact coverage | 90.15% | 78.12% |
| Complete semantic review pairs | 33/40 | 33/40 |

Semantic percentages describe only the complete paired review cohort. See the general comparison for missing-review counts and full-cohort bounds; absent judgments are not observed zero scores.

The separate semantic audit used 80 high-reasoning calls, 159,761 input and 94,122 output tokens, with estimated catalog cost USD 0.14490. Usage is available for 80 calls, including invalid reviewer outputs. These review costs are excluded from per-arm answering cost.

Building, independently validating, and deterministically reconstructing the unified expert took 477.2 seconds. The corresponding summed work for nine source experts took 653.9 seconds. Separate parity checks, technical rehearsals, image preparation, and queue/setup overhead are excluded from answering latency. Hardware and filesystem effects limit transfer of these timings.

[General comparison](README.md)
