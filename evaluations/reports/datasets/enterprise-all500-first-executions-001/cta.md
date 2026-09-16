# EnterpriseRAG: cost, time and quality by source observation

Trial and agent durations belong to each row's source study. Primary-route p95 and quality are distinguished from the planned all-route workload and two knowledge constructions. Different concurrency partners prevent interpreting these times as a matched runtime comparison. Missing usage stays unavailable; zero reported provider cost excludes local compute, electricity and orchestration. No remote generative-model requests were made.

New two-trial job wall time: 4475.76 seconds. The previous incomplete job has no final wall time.

| Strategy | nDCG@10 x100 | Trial seconds | Agent seconds | Two-build seconds | Query p95 ms | Knowledge bytes | Provider USD | Source study |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| legacy | 70.72 | 155.44 | 104.97 | 60.21 | 104.95 | 180168866 | 0.0000 | enterprise-all500-descriptive-001 |
| turso | 70.72 | 439.88 | 372.33 | 288.07 | 185.25 | 842070178 | 0.0000 | enterprise-all500-first-executions-001 |
| embeddings | 64.04 | 2315.76 | 2268.49 | 578.32 | 1978.98 | 249909785 | 0.0000 | enterprise-all500-descriptive-001 |
| adaptive | 63.61 | 3274.57 | 3229.75 | 545.06 | 7872.87 | 557899136 | 0.0000 | enterprise-all500-descriptive-001 |
| graphify | 60.50 | 4456.90 | 4395.99 | 4074.41 | 947.69 | 240091223 | 0.0000 | enterprise-all500-first-executions-001 |
| classical | 56.16 | 4144.29 | 4096.60 | 565.30 | 1938.83 | 557897958 | 0.0000 | enterprise-all500-descriptive-001 |
| ensemble | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | enterprise-all500-descriptive-001 |
| entity-graph | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | enterprise-all500-descriptive-001 |

| Strategy | Primary route | Declared routes | Planned query executions |
| --- | --- | --- | ---: |
| legacy | lexical | lexical | 500 |
| turso | lexical-sql | lexical-sql | 500 |
| embeddings | hybrid | lexical, vector, hybrid | 1500 |
| adaptive | adaptive | adaptive | 500 |
| graphify | search | search | 500 |
| classical | fusion | bm25, topic, association, fusion | 2000 |
| ensemble | quality | fast, quality, robust | 1500 |
| entity-graph | fusion | lexical, entity, traversal, fusion | 2000 |

Planned work is not evidence that an interrupted or failed allocation completed every route. [All outcomes](README.md).
