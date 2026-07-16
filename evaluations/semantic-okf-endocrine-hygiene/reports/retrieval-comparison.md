# Endocrine-Hygiene Retrieval Comparison

All quality metrics use the same frozen question battery, a raw candidate pool of 100, first-occurrence paper deduplication, and exact evidence validation against the authoritative Semantic OKF ledger. `N/A` means the unchanged builder could not represent this corpus; it is not a zero score.

## Best route by builder/consult family

| Family | Status | Best route | Recall@10 overall | Recall@10 hard | MRR@10 | nDCG@10 | Evidence valid | Mean ms | p95 ms | Reason |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| legacy | pass | legacy_lexical | 98.9% | 97.1% | 0.967 | 0.947 | 100.0% | 0.6 | 0.8 |  |
| embeddings | pass | lexical | 98.7% | 100.0% | 0.933 | 0.928 | 100.0% | 33.4 | 36.0 |  |
| classical | pass | bm25 | 98.9% | 97.1% | 0.950 | 0.953 | 100.0% | 19.0 | 20.6 |  |
| entity-graph | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | paper record sources/markdown/PMC11764522 has no PDF page headings |
| adaptive | pass | bm25 | 98.9% | 97.1% | 0.950 | 0.953 | 100.0% | 24.0 | 26.3 |  |
| ensemble | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | ensemble component plan adaptive is invalid: paper identity mappings must contain canonical versioned arXiv IDs |

## Route-level results

| Family | Route | Status | Recall@1 | Recall@3 | Recall@5 | Recall@10 | Hard Recall@10 | MRR@10 | nDCG@10 | Evidence valid | Mean ms |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| legacy | legacy_lexical | pass | 63.4% | 80.0% | 91.1% | 98.9% | 97.1% | 0.967 | 0.947 | 100.0% | 0.6 |
| embeddings | lexical | pass | 60.9% | 81.2% | 87.4% | 98.7% | 100.0% | 0.933 | 0.928 | 100.0% | 33.4 |
| embeddings | vector | pass | 50.4% | 65.6% | 75.0% | 94.2% | 79.8% | 0.805 | 0.805 | 100.0% | 45.1 |
| embeddings | hybrid | pass | 54.4% | 69.9% | 82.5% | 95.9% | 94.3% | 0.875 | 0.858 | 100.0% | 92.1 |
| classical | bm25 | pass | 62.2% | 84.0% | 92.9% | 98.9% | 97.1% | 0.950 | 0.953 | 100.0% | 19.0 |
| classical | topic | pass | 61.5% | 84.0% | 92.9% | 98.2% | 97.1% | 0.928 | 0.940 | 100.0% | 82.5 |
| classical | association | pass | 62.2% | 84.0% | 92.9% | 99.5% | 97.1% | 0.944 | 0.952 | 100.0% | 71.1 |
| classical | fusion | pass | 62.2% | 84.8% | 92.9% | 98.9% | 97.1% | 0.944 | 0.949 | 100.0% | 82.4 |
| entity-graph | lexical | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| entity-graph | entity | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| entity-graph | traversal | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| entity-graph | fusion | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| adaptive | bm25 | pass | 62.2% | 84.0% | 92.9% | 98.9% | 97.1% | 0.950 | 0.953 | 100.0% | 24.0 |
| adaptive | topic | pass | 61.5% | 84.0% | 92.9% | 98.2% | 97.1% | 0.928 | 0.940 | 100.0% | 508.6 |
| adaptive | association | pass | 62.2% | 84.0% | 92.9% | 99.5% | 97.1% | 0.944 | 0.952 | 100.0% | 339.6 |
| adaptive | fusion | pass | 62.2% | 84.8% | 92.9% | 98.9% | 97.1% | 0.944 | 0.949 | 100.0% | 510.9 |
| adaptive | adaptive | pass | 62.2% | 84.8% | 92.9% | 98.9% | 97.1% | 0.944 | 0.949 | 100.0% | 1671.6 |
| ensemble | quality | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| ensemble | fast | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| ensemble | robust | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |

The legacy row is explicitly an evaluator-side deterministic TF-IDF-like ledger baseline. The legacy consult package exposes validated ledger and SPARQL reads but no ranked natural-language search command; this row does not invoke `grep` or `rg` and is not mislabeled as a consult CLI search.
