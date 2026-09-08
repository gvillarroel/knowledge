# graphify: dataset results

[Report hub](../README.md) · [All skills](README.md)

This is a navigation and diagnostic view of published results. Dataset pages own the bound primary rankings.

[Skill package](../../../skills/consult-semantic-okf-graphify/SKILL.md)

[Stratified Enterprise evolution E7 and this family's opportunity status](../evolution/e7/README.md)

[Earlier Enterprise evolution E6](../evolution/e6/README.md)

## Software architecture books (40)

Private book corpus; 18 direct routes, Top-10, three repetitions; published rounded aggregates.

[All compared skills](../datasets/software-architecture-books-40.md)

| Skill family / route | nDCG@10 | Recall@10 | MRR@10 | P95 (ms) |
|---|---:|---:|---:|---:|
| graphify / Graph search | 57.10% | 59.58% | 67.92% | 211.65 |

## Data science / AI / ML books (40)

Private book corpus; 18 direct routes, Top-10, three repetitions; published rounded aggregates.

[All compared skills](../datasets/data-science-ai-ml-books-40.md)

| Skill family / route | nDCG@10 | Recall@10 | MRR@10 | P95 (ms) |
|---|---:|---:|---:|---:|
| graphify / Graph search | 54.41% | 53.96% | 62.50% | 737.82 |

## EnterpriseRAG reduced corpus (40)

Pinned Onyx v1.0.0; 40 stratified questions, 985 documents including 900 distractors. Retrieval only; not the full official benchmark.

[All compared skills](../datasets/enterprise-rag-bench-40-v1.md)

| Skill family / route | nDCG@10 | Recall@10 | MRR@10 | P95 (ms) |
|---|---:|---:|---:|---:|
| graphify / Graph search | 13.63% | 17.37% | 20.42% | 128.30 |

## EnterpriseRAG e6 development (40)

Forty exposed development queries on a reference-enriched 985-document corpus. Eight retained primary routes from frozen experimental profiles: five construction and three consultation treatments. Eighteen retained-profile routes are available separately as diagnostics. These maxima do not describe installed defaults, unseen-query quality or official generated-answer accuracy; the terminal decision is separate.

[All compared skills](../datasets/enterprise-rag-e6-development-40.md)

| Skill family / route | nDCG@10 | Recall@10 | MRR@10 | P95 (ms) |
|---|---:|---:|---:|---:|
| graphify / candidate-010 / search | 60.36% | 63.24% | 62.50% | 140.04 |

## EnterpriseRAG complete documents: incoming / G2 (40)

Fixed incoming-versus-G2 generator replay: 985 complete documents, 40 exposed questions, eight families, eighteen routes and two versions. Both versions use identical explicit body mappings, plans and consultation code. Embeddings uses pinned MiniLM; Ensemble retains hashing. One query pass, descriptive P95, no generated answers, no independent retrieval gate and no promotion. Legacy lexical and Turso SQL are comparator routes. Do not pool with title-only v1/e6 or the S2 agent-answer contract. Each same-route version pair ties in all relevance metrics; numbered catalog rows enumerate alternatives and preserve these ties.

[All compared skills](../datasets/enterprise-rag-generator-g2-fulltext-40.md)

| Skill family / route | nDCG@10 | Recall@10 | MRR@10 | P95 (ms) |
|---|---:|---:|---:|---:|
| graphify / G2 / Graph search | 19.00% | 23.85% | 23.30% | 208.93 |
| graphify / Incoming / Graph search | 19.00% | 23.85% | 23.30% | 213.57 |

[Cost, time, quality, and measurement limits](../cta/README.md)
