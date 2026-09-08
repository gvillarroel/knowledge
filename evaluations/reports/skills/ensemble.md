# ensemble: dataset results

[Report hub](../README.md) · [All skills](README.md)

This is a navigation and diagnostic view of published results. Dataset pages own the bound primary rankings.

[Skill package](../../../skills/consult-semantic-okf-ensemble/SKILL.md)

[Stratified Enterprise evolution E7 and this family's opportunity status](../evolution/e7/README.md)

[Earlier Enterprise evolution E6](../evolution/e6/README.md)

## GraphRAG generalization (60)

Released evaluation-only 60-question cohort; authoritative-paper Top-10; no new execution.

[All compared skills](../datasets/graphrag-papers-parallel-eval-60-v1.md)

| Skill family / route | nDCG@10 | Recall@10 | MRR@10 | P95 (ms) |
|---|---:|---:|---:|---:|
| ensemble / Ensemble `robust` | 99.38% | 100.00% | 100.00% | 2486.93 |
| ensemble / Ensemble `fast` | 97.58% | 100.00% | 96.67% | 2794.83 |

## GraphRAG contradictions (40)

Released evaluation-only contradiction cohort; complete evidence is the primary metric; 25 compatible routes.

[All compared skills](../datasets/graphrag-papers-contradiction-eval-40-v1.md)

| Skill family / route | Full evidence@10 | Recall@10 | MRR@10 | nDCG@10 | P95 (ms) |
|---|---:|---:|---:|---:|---:|
| ensemble / Ensemble fast | 87.50% | 96.25% | 84.58% | 84.06% | 2308.88 |
| ensemble / Ensemble robust | 87.50% | 96.25% | 88.33% | 86.22% | 2017.18 |

## Software architecture books (40)

Private book corpus; 18 direct routes, Top-10, three repetitions; published rounded aggregates.

[All compared skills](../datasets/software-architecture-books-40.md)

| Skill family / route | nDCG@10 | Recall@10 | MRR@10 | P95 (ms) |
|---|---:|---:|---:|---:|
| ensemble / Fast | 86.04% | 95.21% | 89.38% | 7820.74 |
| ensemble / Robust | 85.61% | 95.21% | 90.50% | 3901.24 |
| ensemble / Quality | 85.01% | 95.21% | 88.00% | 9788.55 |

## Data science / AI / ML books (40)

Private book corpus; 18 direct routes, Top-10, three repetitions; published rounded aggregates.

[All compared skills](../datasets/data-science-ai-ml-books-40.md)

| Skill family / route | nDCG@10 | Recall@10 | MRR@10 | P95 (ms) |
|---|---:|---:|---:|---:|
| ensemble / Fast | 94.44% | 99.17% | 96.75% | 16155.87 |
| ensemble / Quality | 92.78% | 99.17% | 94.11% | 22566.20 |
| ensemble / Robust | 91.78% | 99.17% | 93.23% | 5403.21 |

## Astro documentation (40)

Published best route for six families; raw pool 100, document deduplication; standalone selected-route P95.

[All compared skills](../datasets/astro-40.md)

| Skill family / route | nDCG@10 | Recall@10 | MRR@10 | P95 (ms) |
|---|---:|---:|---:|---:|
| ensemble / quality | 81.90% | 89.60% | 89.00% | 10938.40 |

## Endocrine hygiene

Published best route per family; entity-graph and ensemble are unavailable on this historical contract, not zero-score rows.

[All compared skills](../datasets/endocrine-hygiene.md)

| Skill family / route | nDCG@10 | Recall@10 | MRR@10 | P95 (ms) |
|---|---:|---:|---:|---:|
| ensemble / N/A | N/A | N/A | N/A | N/A |

## EnterpriseRAG reduced corpus (40)

Pinned Onyx v1.0.0; 40 stratified questions, 985 documents including 900 distractors. Retrieval only; not the full official benchmark.

[All compared skills](../datasets/enterprise-rag-bench-40-v1.md)

| Skill family / route | nDCG@10 | Recall@10 | MRR@10 | P95 (ms) |
|---|---:|---:|---:|---:|
| ensemble / Quality | 55.38% | 59.00% | 60.36% | 1315.92 |
| ensemble / Fast | 52.29% | 59.00% | 59.07% | 1224.41 |
| ensemble / Robust | 50.34% | 59.00% | 57.47% | 1141.87 |

## EnterpriseRAG e6 development (40)

Forty exposed development queries on a reference-enriched 985-document corpus. Eight retained primary routes from frozen experimental profiles: five construction and three consultation treatments. Eighteen retained-profile routes are available separately as diagnostics. These maxima do not describe installed defaults, unseen-query quality or official generated-answer accuracy; the terminal decision is separate.

[All compared skills](../datasets/enterprise-rag-e6-development-40.md)

| Skill family / route | nDCG@10 | Recall@10 | MRR@10 | P95 (ms) |
|---|---:|---:|---:|---:|
| ensemble / candidate-018 / quality | 61.37% | 62.76% | 63.12% | 1518.88 |

## EnterpriseRAG complete documents: incoming / G2 (40)

Fixed incoming-versus-G2 generator replay: 985 complete documents, 40 exposed questions, eight families, eighteen routes and two versions. Both versions use identical explicit body mappings, plans and consultation code. Embeddings uses pinned MiniLM; Ensemble retains hashing. One query pass, descriptive P95, no generated answers, no independent retrieval gate and no promotion. Legacy lexical and Turso SQL are comparator routes. Do not pool with title-only v1/e6 or the S2 agent-answer contract. Each same-route version pair ties in all relevance metrics; numbered catalog rows enumerate alternatives and preserve these ties.

[All compared skills](../datasets/enterprise-rag-generator-g2-fulltext-40.md)

| Skill family / route | nDCG@10 | Recall@10 | MRR@10 | P95 (ms) |
|---|---:|---:|---:|---:|
| ensemble / G2 / Quality | 97.86% | 97.48% | 100.00% | 2839.98 |
| ensemble / Incoming / Quality | 97.86% | 97.48% | 100.00% | 2838.14 |
| ensemble / G2 / Fast | 96.58% | 97.48% | 100.00% | 2308.27 |
| ensemble / Incoming / Fast | 96.58% | 97.48% | 100.00% | 2337.99 |
| ensemble / G2 / Robust | 95.12% | 97.48% | 98.75% | 1570.69 |
| ensemble / Incoming / Robust | 95.12% | 97.48% | 98.75% | 1577.58 |

[Cost, time, quality, and measurement limits](../cta/README.md)
