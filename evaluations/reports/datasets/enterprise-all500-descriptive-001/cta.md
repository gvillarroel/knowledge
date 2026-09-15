# EnterpriseRAG: cost, time and quality

Only the four settled strategies have qualified native resource observations. Incomplete strategy costs remain unavailable. Native trial and agent durations are separate from total job wall time. Two-build time includes the reproducibility pair. No remote generative-model calls were requested. Missing usage remains unavailable; reported provider cost excludes local compute, electricity and orchestration. Query timings are descriptive under the fixed concurrent workload.

The reported quality and query p95 use the predeclared primary route. The planned workload includes two knowledge constructions and all declared routes; failed trials may execute only part of it. Total trial/agent time is not an isolated primary-route execution cost. Planned query counts below describe the fixed contract.

| Strategy | Reported primary route | Declared routes | Planned query executions |
| --- | --- | --- | ---: |
| legacy | lexical | lexical | 500 |
| embeddings | hybrid | lexical, vector, hybrid | 1500 |
| adaptive | adaptive | adaptive | 500 |
| classical | fusion | bm25, topic, association, fusion | 2000 |
| ensemble | quality | fast, quality, robust | 1500 |
| entity-graph | fusion | lexical, entity, traversal, fusion | 2000 |
| graphify | search | search | 500 |
| turso | lexical-sql | lexical-sql | 500 |

Native job wall time is unavailable because the native job has no final timestamp.

| Strategy | nDCG@10 ×100 | Trial seconds | Agent seconds | Two-build seconds | Query p95 ms | Knowledge bytes | Provider USD |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| legacy | 70.72 | 155.44 | 104.97 | 60.21 | 104.95 | 180168866 | 0.0000 |
| embeddings | 64.04 | 2315.76 | 2268.49 | 578.32 | 1978.98 | 249909785 | 0.0000 |
| adaptive | 63.61 | 3274.57 | 3229.75 | 545.06 | 7872.87 | 557899136 | 0.0000 |
| classical | 56.16 | 4144.29 | 4096.60 | 565.30 | 1938.83 | 557897958 | 0.0000 |
| ensemble | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable |
| entity-graph | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable |
| graphify | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable |
| turso | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable |

[All strategy outcomes](README.md).
