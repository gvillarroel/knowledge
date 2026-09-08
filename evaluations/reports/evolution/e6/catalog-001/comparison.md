# EnterpriseRAG: selected development profiles

## Direct comparison

| Pos. | Pair / strategy | nDCG@10 | Recall@10 | MRR@10 | Query P95 (ms) |
|---:|---|---:|---:|---:|---:|
| 1 | embeddings / baseline / hybrid | 63.19% | 68.38% | 64.38% | 171.35 ms |
| 2 | ensemble / candidate-018 / quality | 61.37% | 62.76% | 63.12% | 1518.88 ms |
| 3 | graphify / candidate-010 / search | 60.36% | 63.24% | 62.50% | 140.04 ms |
| 4 | legacy / candidate-003 / lexical | 59.62% | 62.48% | 61.50% | 9.63 ms |
| 5 | turso / candidate-003 / lexical-sql | 59.62% | 62.48% | 61.50% | 8.66 ms |
| 6 | adaptive / candidate-013 / adaptive | 58.62% | 62.20% | 60.36% | 1305.60 ms |
| 7 | classical / candidate-014 / fusion | 48.21% | 45.86% | 57.50% | 39.30 ms |
| 8 | entity-graph / candidate-010 / fusion | 48.19% | 58.59% | 48.34% | 39.53 ms |

[Source development comparison](../development-001/README.md) · [Exact family profiles](profiles.md) · [All retained-profile routes](routes.md)

Each row transcribes the predeclared primary route of that family's already-selected incumbent. It does not select a different route using secondary metrics. Forty exposed queries on a reference-enriched 985-document corpus form one Enterprise source/annotation group.

These development maxima do not establish unseen-query performance, official generated-answer quality or canonical skill promotion. Consult the campaign's terminal decision for independent validation. Shared-host query P95 is descriptive and is not combined across attempts.

Source aggregate SHA-256: `111f6a97df7e08b69a8cfd92eaa5678f01215a8e1c3847df0541ccd6932ee28d`.
