# Private Book All-Route Summary

Both studies use 40 frozen questions, Top-10 retrieval, three repetitions, and
the same 18-route population. All rankings were 100% stable across repetitions,
and every returned record identity and hash passed exact ledger validation.

| Route | Architecture Recall | Architecture MRR | Architecture nDCG | DS/AI/ML Recall | DS/AI/ML MRR | DS/AI/ML nDCG |
|---|---:|---:|---:|---:|---:|---:|
| Legacy / Lexical | 95.00% | 80.62% | 81.55% | 95.00% | 81.75% | 83.22% |
| Embeddings / Lexical | 92.92% | 71.57% | 72.13% | 83.33% | 58.19% | 63.24% |
| Embeddings / Vector | 84.38% | 65.99% | 65.56% | 70.42% | 29.13% | 39.38% |
| Embeddings / Hybrid | 92.08% | 72.92% | 73.39% | 88.96% | 53.25% | 60.97% |
| Classical / BM25 | 83.75% | 95.00% | 84.18% | 98.33% | 94.06% | 93.08% |
| Classical / Topic | 97.29% | 97.50% | 92.56% | 78.54% | 91.25% | 80.54% |
| Classical / Association | 97.29% | 97.50% | 92.56% | 78.54% | 91.25% | 80.54% |
| Classical / Fusion | 97.29% | 97.50% | 92.58% | 78.54% | 91.25% | 80.54% |
| Adaptive / Adaptive fusion | 95.21% | 90.50% | 85.61% | 99.17% | 93.23% | 91.78% |
| Entity Graph / Lexical | 98.33% | 89.25% | 88.98% | 99.17% | 88.75% | 90.31% |
| Entity Graph / Entity | 93.54% | 81.15% | 81.76% | 96.67% | 78.42% | 80.29% |
| Entity Graph / Traversal | 92.92% | 80.92% | 80.30% | 79.58% | 43.55% | 51.20% |
| Entity Graph / Fusion | 97.50% | 81.33% | 83.50% | 97.50% | 86.88% | 85.83% |
| Ensemble / Fast | 95.21% | 89.38% | 86.04% | 99.17% | 96.75% | 94.44% |
| Ensemble / Quality | 95.21% | 88.00% | 85.01% | 99.17% | 94.11% | 92.78% |
| Ensemble / Robust | 95.21% | 90.50% | 85.61% | 99.17% | 93.23% | 91.78% |
| Graphify / Graph search | 59.58% | 67.92% | 57.10% | 53.96% | 62.50% | 54.41% |
| Turso / Lexical SQL comparator | 86.25% | 52.72% | 58.40% | 74.38% | 31.79% | 40.16% |

Classical fusion ranks first for the software-architecture corpus with 92.58%
nDCG@10. Ensemble fast ranks first for the data-science, AI, and
machine-learning corpus with 94.44% nDCG@10. These are corpus-specific
retrieval results, not generated-answer quality or unseen-corpus
generalization claims.
