# EnterpriseRAG closure: cost, time and quality

Each measured row transcribes an original completed E14 native observation.
Job and agent times are descriptive; two-build time includes the reproducibility
build pair. They are not wall-time totals for the entire evolution campaign.

| Family | nDCG@10 ×100 | Job seconds | Agent seconds | Two-build seconds | Query p95 ms | Knowledge bytes | Reported provider USD |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Legacy | 72.38 | 123.980 | 77.135 | 60.576 | 98.090 | 180168866 | 0.0 |
| Turso | 72.38 | 233.211 | 184.574 | 164.718 | 103.962 | 842070178 | 0.0 |
| Adaptive | 66.21 | 1327.367 | 1277.898 | 562.077 | 8479.284 | 557899136 | 0.0 |
| Graphify | 63.72 | 2830.152 | 2781.530 | 2664.846 | 904.768 | 240091223 | 0.0 |
| Embeddings | 63.51 | 1047.799 | 1000.296 | 580.000 | 1988.105 | 249909785 | 0.0 |
| Classical | 62.10 | 1571.806 | 1522.887 | 578.193 | 2041.407 | 557897958 | 0.0 |
| Entity Graph | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable |
| Ensemble | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable |

Provider cost and benchmark model calls are zero for these deterministic
retrieval observations. Host, electricity and orchestration costs were not priced.
The original failed Entity Graph and Ensemble attempts did consume runtime;
their unavailable retained-row values do not erase that cost. See the
[original execution-error report](../../e14/starting-execution-errors-001/README.md).

## Closure accounting

| Item | This closure / E15 result |
| --- | --- |
| New native trials and benchmark model calls | 0 |
| New proposal charges, retries and quality misses | 0 |
| Private releases | 0 |
| Newly qualified families and promotions | 0 |
| Private preparation review | Rejected for optimizer access isolation |
| Repository tests | 1,697 tests and 373 subtests passed |
| Total application coverage | 90.5%; threshold 80% |

The earlier 63.72-second preflight was configuration/software work, not agent
evaluation. No comparison time, acceptance score or cost is invented for
the stages that never ran. The separate [Luna/full-corpus CTA](../../../enterprise-classical-full/cta.md)
retains the historical model workload's own cost contract.

[Final table and limitations](README.md) · [Applications and categories](groups.md) · [Aggregate](aggregate.json)
