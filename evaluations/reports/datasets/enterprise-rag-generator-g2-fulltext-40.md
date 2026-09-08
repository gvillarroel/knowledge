# EnterpriseRAG complete documents: incoming / G2 (40)

## Direct comparison

| Pos. | Pair / strategy | nDCG@10 | Recall@10 | MRR@10 | P95 (ms) |
|---:|---|---:|---:|---:|---:|
| 1 | ensemble / G2 / Quality | 97.86% | 97.48% | 100.00% | 2839.98 ms |
| 2 | ensemble / Incoming / Quality | 97.86% | 97.48% | 100.00% | 2838.14 ms |
| 3 | classical / G2 / BM25 | 97.85% | 98.59% | 98.75% | 256.65 ms |
| 4 | classical / Incoming / BM25 | 97.85% | 98.59% | 98.75% | 252.10 ms |
| 5 | ensemble / G2 / Fast | 96.58% | 97.48% | 100.00% | 2308.27 ms |
| 6 | ensemble / Incoming / Fast | 96.58% | 97.48% | 100.00% | 2337.99 ms |
| 7 | entity-graph / G2 / Lexical | 95.43% | 96.01% | 97.50% | 770.35 ms |
| 8 | entity-graph / Incoming / Lexical | 95.43% | 96.01% | 97.50% | 762.10 ms |
| 9 | adaptive / G2 / Adaptive fusion | 95.12% | 97.48% | 98.75% | 1608.32 ms |
| 10 | adaptive / Incoming / Adaptive fusion | 95.12% | 97.48% | 98.75% | 1590.00 ms |
| 11 | ensemble / G2 / Robust | 95.12% | 97.48% | 98.75% | 1570.69 ms |
| 12 | ensemble / Incoming / Robust | 95.12% | 97.48% | 98.75% | 1577.58 ms |
| 13 | embeddings / G2 / Lexical | 93.63% | 94.88% | 95.62% | 203.23 ms |
| 14 | embeddings / Incoming / Lexical | 93.63% | 94.88% | 95.62% | 203.68 ms |
| 15 | classical / G2 / Association | 90.33% | 88.64% | 98.75% | 251.54 ms |
| 16 | classical / G2 / Fusion | 90.33% | 88.64% | 98.75% | 252.28 ms |
| 17 | classical / G2 / Topic | 90.33% | 88.64% | 98.75% | 251.49 ms |
| 18 | classical / Incoming / Association | 90.33% | 88.64% | 98.75% | 248.69 ms |
| 19 | classical / Incoming / Fusion | 90.33% | 88.64% | 98.75% | 247.81 ms |
| 20 | classical / Incoming / Topic | 90.33% | 88.64% | 98.75% | 249.50 ms |
| 21 | legacy / G2 / Lexical | 88.83% | 92.50% | 91.19% | 6.84 ms |
| 22 | legacy / Incoming / Lexical | 88.83% | 92.50% | 91.19% | 6.89 ms |
| 23 | embeddings / G2 / Hybrid | 88.38% | 94.83% | 89.11% | 388.36 ms |
| 24 | embeddings / Incoming / Hybrid | 88.38% | 94.83% | 89.11% | 395.33 ms |
| 25 | entity-graph / G2 / Fusion | 77.02% | 82.67% | 79.69% | 776.15 ms |
| 26 | entity-graph / Incoming / Fusion | 77.02% | 82.67% | 79.69% | 766.50 ms |
| 27 | embeddings / G2 / Vector | 76.98% | 82.28% | 79.67% | 176.50 ms |
| 28 | embeddings / Incoming / Vector | 76.98% | 82.28% | 79.67% | 188.07 ms |
| 29 | entity-graph / G2 / Entity | 75.19% | 81.30% | 77.50% | 773.58 ms |
| 30 | entity-graph / Incoming / Entity | 75.19% | 81.30% | 77.50% | 771.29 ms |
| 31 | turso / G2 / Lexical SQL comparator | 69.40% | 77.36% | 71.48% | 379.12 ms |
| 32 | turso / Incoming / Lexical SQL comparator | 69.40% | 77.36% | 71.48% | 384.85 ms |
| 33 | entity-graph / G2 / Traversal | 56.17% | 69.51% | 56.52% | 769.98 ms |
| 34 | entity-graph / Incoming / Traversal | 56.17% | 69.51% | 56.52% | 764.75 ms |
| 35 | graphify / G2 / Graph search | 19.00% | 23.85% | 23.30% | 208.93 ms |
| 36 | graphify / Incoming / Graph search | 19.00% | 23.85% | 23.30% | 213.57 ms |

Fixed incoming-versus-G2 generator replay: 985 complete documents, 40 exposed questions, eight families, eighteen routes and two versions. Both versions use identical explicit body mappings, plans and consultation code. Embeddings uses pinned MiniLM; Ensemble retains hashing. One query pass, descriptive P95, no generated answers, no independent retrieval gate and no promotion. Legacy lexical and Turso SQL are comparator routes. Do not pool with title-only v1/e6 or the S2 agent-answer contract. Each same-route version pair ties in all relevance metrics; numbered catalog rows enumerate alternatives and preserve these ties.

[Original report](../../../evaluations/reports/enterprise-generator-g2/README.md) · [Report hub](../README.md) · [CTA](../cta/README.md)

Primary comparison: **nDCG@10**. N/A is an unavailable or unmeasured value. This table does not score generated-answer correctness.

Publication source SHA-256: `fe111e6739cc604a380453d5e650940ba391ad608ca2bcc3ed077cd3c868a07e`.
