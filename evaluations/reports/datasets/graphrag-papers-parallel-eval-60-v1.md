# GraphRAG generalization (60)

## Direct comparison

| Pos. | Pair / strategy | nDCG@10 | Recall@10 | MRR@10 | P95 (ms) |
|---:|---|---:|---:|---:|---:|
| 1 | classical / Classical association | 99.60% | 100.00% | 100.00% | 664.65 ms |
| 2 | adaptive / Adaptive fusion | 99.38% | 100.00% | 100.00% | 2405.80 ms |
| 3 | classical / Classical fusion | 99.38% | 100.00% | 100.00% | 671.43 ms |
| 4 | ensemble / Ensemble `robust` | 99.38% | 100.00% | 100.00% | 2486.93 ms |
| 5 | classical / Classical topic | 99.31% | 100.00% | 100.00% | 665.76 ms |
| 6 | specialized-expert / Specialized expert early confidence-gated hybrid | 99.03% | 100.00% | 99.17% | 989.63 ms |
| 7 | rust-mallet / RustMallet association | 98.91% | 100.00% | 100.00% | 677.64 ms |
| 8 | rust-mallet / RustMallet fusion | 98.85% | 100.00% | 100.00% | 684.80 ms |
| 9 | rust-mallet / RustMallet topic | 98.68% | 100.00% | 100.00% | 682.38 ms |
| 10 | classical / Classical BM25 | 98.11% | 98.33% | 100.00% | 665.72 ms |
| 11 | rust-mallet / RustMallet BM25 | 98.11% | 98.33% | 100.00% | 650.81 ms |
| 12 | ensemble / Ensemble `fast` | 97.58% | 100.00% | 96.67% | 2794.83 ms |
| 13 | specialized-expert / Specialized expert Ensemble quality + trace v48 | 97.24% | 100.00% | 96.67% | 4855.90 ms |
| 14 | tantivy / Tantivy BM25 | 96.25% | 100.00% | 96.25% | 128.27 ms |
| 15 | entity-graph / Entity Graph lexical | 92.70% | 98.89% | 92.55% | 485.78 ms |
| 16 | embeddings / Embeddings lexical | 92.05% | 98.89% | 91.94% | 298.04 ms |
| 17 | tika-mallet / Tika/MALLET fusion | 91.28% | 99.44% | 90.85% | 99.48 ms |
| 18 | entity-graph / Entity Graph fusion | 86.05% | 97.78% | 86.81% | 478.67 ms |
| 19 | entity-graph / Entity Graph entity | 81.77% | 95.83% | 82.39% | 471.66 ms |
| 20 | entity-graph / Entity Graph traversal | 75.89% | 93.89% | 75.22% | 478.05 ms |
| 21 | tika-mallet-tantivy / Tika/MALLET/Tantivy fusion | 66.38% | 93.06% | 61.30% | 2883.27 ms |
| 22 | embeddings / Embeddings hybrid | 65.33% | 79.72% | 65.61% | 545.45 ms |
| 23 | legacy / Legacy lexical | 60.54% | 97.78% | 49.69% | 9.96 ms |
| 24 | embeddings / Embeddings vector | 52.60% | 69.44% | 53.58% | 251.61 ms |
| 25 | specialized-expert / Specialized expert supervised profiles v51 | 41.03% | 71.11% | 34.11% | 142.67 ms |

Released evaluation-only 60-question cohort; authoritative-paper Top-10; no new execution.

[Original report](../../../evaluations/LATEST-REPORT.md) · [Report hub](../README.md) · [CTA](../cta/README.md)

Primary comparison: **nDCG@10**. N/A is an unavailable or unmeasured value. This table does not score generated-answer correctness.

Publication source SHA-256: `8f3b62149f3ac7b5cb89505ff395cb6fcaa617ab881af8873081fa0a17e76f9a`.
