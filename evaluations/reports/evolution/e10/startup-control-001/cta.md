# E10 starting cost, time and quality

[Startup report](README.md)

The three new native jobs consumed **1284.42 summed job seconds** (21.41 job minutes) and 1136.79 summed agent seconds. These are workload totals; overlapping jobs mean they are not campaign wall time. They exclude staging, custody checks, review, reporting and other host overhead.

| Family | Native role | nDCG@10 | Job s | Agent s | Double build s | Query P95 ms | Knowledge MiB |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| embeddings | baseline | 63.51 | 1035.12 | 986.25 | 568.59 | 1940.37 | 238.33 |
| legacy | baseline | 61.11 | 123.58 | 72.20 | 60.96 | 71.49 | 171.82 |
| legacy | retained-start | 72.38 | 125.73 | 78.35 | 61.69 | 101.36 | 171.82 |

Each job reports zero input, cache and output tokens and native cost 0.0, using the deterministic retrieval adapter with no LLM calls. This is not an invoice or evidence that host compute is free; host cost remains unpriced. Embedding inference runs locally on CPU.

Build time includes two builds and their matched validations. Query P95 is one descriptive pass, not an independent latency experiment. Eight no-reference questions remain in execution and latency without a retrieval score. Every completed job has integrity 1, zero errors and zero retries.

The maintained report uses the separate diagnostic threshold `reward >= 0.8`, so all three rows appear as verifier failures at that threshold. Their finite native measurements remain valid; this threshold neither explains the custody refusal nor establishes all-family acceptance.

These three E10 jobs are additional to the [83 E7/E8 jobs](../../e8/development-cta-003/README.md) and the [single E9 feasibility job](../../e9/feasibility-001/cta.md). Each original is counted once in its own scope. No unstarted role receives zero time or a fabricated measurement.
