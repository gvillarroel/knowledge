# All routes of retained family profiles

[Primary comparison](comparison.md)

These 18 diagnostic rows belong to the already-selected family incumbents. Secondary routes did not choose another candidate or alter the frozen validation decision. The source development report retains every attempted profile, including rejected candidates.

| Family | Candidate | Route | Selection route | nDCG@10 | Recall@10 | MRR@10 | Query P95 ms |
|---|---|---|---|---:|---:|---:|---:|
| adaptive | candidate-013 | adaptive | Yes | 58.62% | 62.20% | 60.36% | 1305.60 ms |
| classical | candidate-014 | fusion | Yes | 48.21% | 45.86% | 57.50% | 39.30 ms |
| classical | candidate-014 | association | No | 48.21% | 45.86% | 57.50% | 38.69 ms |
| classical | candidate-014 | bm25 | No | 59.15% | 64.98% | 60.53% | 37.97 ms |
| classical | candidate-014 | topic | No | 48.29% | 46.22% | 57.50% | 39.60 ms |
| embeddings | baseline | hybrid | Yes | 63.19% | 68.38% | 64.38% | 171.35 ms |
| embeddings | baseline | lexical | No | 59.07% | 61.86% | 61.50% | 8.87 ms |
| embeddings | baseline | vector | No | 60.70% | 68.94% | 60.82% | 173.39 ms |
| ensemble | candidate-018 | quality | Yes | 61.37% | 62.76% | 63.12% | 1518.88 ms |
| ensemble | candidate-018 | fast | No | 58.81% | 62.76% | 60.31% | 1251.49 ms |
| ensemble | candidate-018 | robust | No | 58.00% | 62.76% | 59.25% | 1225.30 ms |
| entity-graph | candidate-010 | fusion | Yes | 48.19% | 58.59% | 48.34% | 39.53 ms |
| entity-graph | candidate-010 | entity | No | 45.25% | 56.58% | 46.67% | 41.09 ms |
| entity-graph | candidate-010 | lexical | No | 57.13% | 63.73% | 57.44% | 41.42 ms |
| entity-graph | candidate-010 | traversal | No | 45.25% | 56.58% | 46.67% | 40.21 ms |
| graphify | candidate-010 | search | Yes | 60.36% | 63.24% | 62.50% | 140.04 ms |
| legacy | candidate-003 | lexical | Yes | 59.62% | 62.48% | 61.50% | 9.63 ms |
| turso | candidate-003 | lexical-sql | Yes | 59.62% | 62.48% | 61.50% | 8.66 ms |

[Source development comparison](../development-001/README.md). Source aggregate SHA-256: `111f6a97df7e08b69a8cfd92eaa5678f01215a8e1c3847df0541ccd6932ee28d`.
