# GraphRAG quality-latency Pareto frontier

## Quality-latency Pareto frontier

| Pos. | Pair / strategy | Recall@10 | MRR@10 | nDCG@10 | Stable queries | P95 |
|---:|---|---:|---:|---:|---:|---:|
| 1 | Classical association | 100.00% | 100.00% | 99.60% | 100.00% | 664.65 ms |
| 2 | RustMallet BM25 | 98.33% | 100.00% | 98.11% | 100.00% | 650.81 ms |
| 3 | Tantivy BM25 | 100.00% | 96.25% | 96.25% | 100.00% | 128.27 ms |
| 4 | Tika/MALLET fusion | 99.44% | 90.85% | 91.28% | 100.00% | 99.48 ms |
| 5 | Legacy lexical | 97.78% | 49.69% | 60.54% | 100.00% | 9.96 ms |

A strategy is on the frontier when no other deterministic, evidence-valid strategy has both equal-or-higher nDCG@10 and equal-or-lower representative P95, with at least one strict gain.
