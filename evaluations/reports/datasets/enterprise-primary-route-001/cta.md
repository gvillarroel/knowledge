# EnterpriseRAG: cost, time and quality

All rows use the same 500 public questions, 470 retrieval-eligible questions and 6,000 complete documents. Quality is native nDCG@10 multiplied by 100. Entity Graph and Ensemble execute only their primary outer route; the other six rows retain the earlier all-declared-routes treatment. These are source-linked observations across three jobs, with different mode exposure, cache history and observation times.

New native job wall time: **10861.23 seconds**. Requested/completed/qualified originals: 2/2/1. Execution errors: 1; verifier failures: 0.

| Strategy | nDCG@10 x100 | Trial seconds | Agent seconds | Two-build seconds | Primary query p95 ms | Knowledge bytes | Provider USD | Treatment |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| legacy | 70.72 | 155.44 | 104.97 | 60.21 | 104.95 | 180168866 | 0.0000 | all-declared-routes |
| turso | 70.72 | 439.88 | 372.33 | 288.07 | 185.25 | 842070178 | 0.0000 | all-declared-routes |
| embeddings | 64.04 | 2315.76 | 2268.49 | 578.32 | 1978.98 | 249909785 | 0.0000 | all-declared-routes |
| adaptive | 63.61 | 3274.57 | 3229.75 | 545.06 | 7872.87 | 557899136 | 0.0000 | all-declared-routes |
| graphify | 60.50 | 4456.90 | 4395.99 | 4074.41 | 947.69 | 240091223 | 0.0000 | all-declared-routes |
| classical | 56.16 | 4144.29 | 4096.60 | 565.30 | 1938.83 | 557897958 | 0.0000 | all-declared-routes |
| entity-graph | 34.96 | 4328.13 | 4274.39 | 1024.73 | 6681.72 | 1245401286 | 0.0000 | primary-route-only |
| ensemble | Unavailable | 10849.42 | 10800.03 | Unavailable | Unavailable | Unavailable | Unavailable | primary-route-only |

Each row retains its source study from the [catalog](README.md). Two-build seconds include both constructions, the explicit validators and byte parity under the original timer. Primary query p95 covers search and hit normalization, excluding journal writes. Build and query times do not add up to the full job wall time.

New-job usage coverage: provider cost 1/2; total tokens 1/2; agent latency 2/2. Observed provider USD total: 0.0000; observed total tokens: 0.

Total tokens mean input plus output; cached input is a subset. Missing usage remains unavailable. Zero provider cost excludes local compute, electricity and orchestration. This deterministic runtime makes no LLM calls.

Different outer-route workloads, concurrency/cache history and timestamps prevent a matched speed ranking. [Phase accounting](phases.md) records only observed boundaries.
