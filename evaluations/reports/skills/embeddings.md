# embeddings: dataset results

[Report hub](../README.md) · [All skills](README.md)

This is a navigation and diagnostic view of published results. Dataset pages own the bound primary rankings.

[Skill package](../../../skills/consult-semantic-okf-embeddings/SKILL.md)

[Enterprise evolution of this family](../evolution/e6/README.md)

## GraphRAG generalization (60)

Released evaluation-only 60-question cohort; authoritative-paper Top-10; no new execution.

[All compared skills](../datasets/graphrag-papers-parallel-eval-60-v1.md)

| Skill family / route | nDCG@10 | Recall@10 | MRR@10 | P95 (ms) |
|---|---:|---:|---:|---:|
| embeddings / Embeddings lexical | 92.05% | 98.89% | 91.94% | 298.04 |
| embeddings / Embeddings hybrid | 65.33% | 79.72% | 65.61% | 545.45 |
| embeddings / Embeddings vector | 52.60% | 69.44% | 53.58% | 251.61 |

## GraphRAG contradictions (40)

Released evaluation-only contradiction cohort; complete evidence is the primary metric; 25 compatible routes.

[All compared skills](../datasets/graphrag-papers-contradiction-eval-40-v1.md)

| Skill family / route | Full evidence@10 | Recall@10 | MRR@10 | nDCG@10 | P95 (ms) |
|---|---:|---:|---:|---:|---:|
| embeddings / Embeddings lexical | 47.50% | 77.92% | 62.96% | 61.23% | 259.01 |
| embeddings / Embeddings hybrid | 37.50% | 70.00% | 81.75% | 66.96% | 472.63 |
| embeddings / Embeddings vector | 32.50% | 65.83% | 71.50% | 57.74% | 222.01 |

## Software architecture books (40)

Private book corpus; 18 direct routes, Top-10, three repetitions; published rounded aggregates.

[All compared skills](../datasets/software-architecture-books-40.md)

| Skill family / route | nDCG@10 | Recall@10 | MRR@10 | P95 (ms) |
|---|---:|---:|---:|---:|
| embeddings / Hybrid | 73.39% | 92.08% | 72.92% | 1182.23 |
| embeddings / Lexical | 72.13% | 92.92% | 71.57% | 1154.39 |
| embeddings / Vector | 65.56% | 84.38% | 65.99% | 2.98 |

## Data science / AI / ML books (40)

Private book corpus; 18 direct routes, Top-10, three repetitions; published rounded aggregates.

[All compared skills](../datasets/data-science-ai-ml-books-40.md)

| Skill family / route | nDCG@10 | Recall@10 | MRR@10 | P95 (ms) |
|---|---:|---:|---:|---:|
| embeddings / Lexical | 63.24% | 83.33% | 58.19% | 2387.46 |
| embeddings / Hybrid | 60.97% | 88.96% | 53.25% | 2393.27 |
| embeddings / Vector | 39.38% | 70.42% | 29.13% | 5.09 |

## Astro documentation (40)

Published best route for six families; raw pool 100, document deduplication; standalone selected-route P95.

[All compared skills](../datasets/astro-40.md)

| Skill family / route | nDCG@10 | Recall@10 | MRR@10 | P95 (ms) |
|---|---:|---:|---:|---:|
| embeddings / lexical | 78.30% | 89.80% | 81.20% | 107.80 |

## Endocrine hygiene

Published best route per family; entity-graph and ensemble are unavailable on this historical contract, not zero-score rows.

[All compared skills](../datasets/endocrine-hygiene.md)

| Skill family / route | nDCG@10 | Recall@10 | MRR@10 | P95 (ms) |
|---|---:|---:|---:|---:|
| embeddings / lexical | 92.80% | 98.70% | 93.30% | 36.00 |

## EnterpriseRAG reduced corpus (40)

Pinned Onyx v1.0.0; 40 stratified questions, 985 documents including 900 distractors. Retrieval only; not the full official benchmark.

[All compared skills](../datasets/enterprise-rag-bench-40-v1.md)

| Skill family / route | nDCG@10 | Recall@10 | MRR@10 | P95 (ms) |
|---|---:|---:|---:|---:|
| embeddings / Lexical | 59.07% | 61.86% | 61.50% | 10.28 |
| embeddings / Hybrid | 51.47% | 59.91% | 53.97% | 47.66 |
| embeddings / Vector | 32.64% | 36.92% | 37.80% | 34.76 |

## EnterpriseRAG e6 development (40)

Forty exposed development queries on a reference-enriched 985-document corpus. Eight retained primary routes from frozen experimental profiles: five construction and three consultation treatments. Eighteen retained-profile routes are available separately as diagnostics. These maxima do not describe installed defaults, unseen-query quality or official generated-answer accuracy; the terminal decision is separate.

[All compared skills](../datasets/enterprise-rag-e6-development-40.md)

| Skill family / route | nDCG@10 | Recall@10 | MRR@10 | P95 (ms) |
|---|---:|---:|---:|---:|
| embeddings / baseline / hybrid | 63.19% | 68.38% | 64.38% | 171.35 |

## EnterpriseRAG complete documents: incoming / G2 (40)

Fixed incoming-versus-G2 generator replay: 985 complete documents, 40 exposed questions, eight families, eighteen routes and two versions. Both versions use identical explicit body mappings, plans and consultation code. Embeddings uses pinned MiniLM; Ensemble retains hashing. One query pass, descriptive P95, no generated answers, no independent retrieval gate and no promotion. Legacy lexical and Turso SQL are comparator routes. Do not pool with title-only v1/e6 or the S2 agent-answer contract. Each same-route version pair ties in all relevance metrics; numbered catalog rows enumerate alternatives and preserve these ties.

[All compared skills](../datasets/enterprise-rag-generator-g2-fulltext-40.md)

| Skill family / route | nDCG@10 | Recall@10 | MRR@10 | P95 (ms) |
|---|---:|---:|---:|---:|
| embeddings / G2 / Lexical | 93.63% | 94.88% | 95.62% | 203.23 |
| embeddings / Incoming / Lexical | 93.63% | 94.88% | 95.62% | 203.68 |
| embeddings / G2 / Hybrid | 88.38% | 94.83% | 89.11% | 388.36 |
| embeddings / Incoming / Hybrid | 88.38% | 94.83% | 89.11% | 395.33 |
| embeddings / G2 / Vector | 76.98% | 82.28% | 79.67% | 176.50 |
| embeddings / Incoming / Vector | 76.98% | 82.28% | 79.67% | 188.07 |

[Cost, time, quality, and measurement limits](../cta/README.md)
