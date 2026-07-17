# Astro Documentation Retrieval Comparison

All routes use the same 40 questions, the same explicit source-record-to-document crosswalk, a raw pool of 100, first-occurrence document deduplication, and independent validation against `semantic/records.jsonl`. Ranking and evidence validity are separate gates.

## Best route by knowledge builder/consult alternative

| Family | Best route | Recall@10 | Hard Recall@10 | MRR@10 | nDCG@10 | Evidence valid | Mean ms | p95 ms |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| legacy | legacy_tfidf | 82.3% | 71.7% | 0.706 | 0.685 | 100.0% | 1.9 | 3.6 |
| embeddings | lexical | 89.8% | 80.8% | 0.812 | 0.783 | 100.0% | 99.1 | 107.8 |
| classical | association | 88.8% | 74.2% | 0.915 | 0.835 | 100.0% | 1327.6 | 1430.1 |
| adaptive | association | 88.8% | 74.2% | 0.915 | 0.835 | 100.0% | 1341.0 | 1443.6 |
| entity-graph | entity | 88.1% | 78.3% | 0.729 | 0.706 | 100.0% | 1152.2 | 1626.6 |
| ensemble | quality | 89.6% | 77.5% | 0.890 | 0.819 | 100.0% | 6770.2 | 10938.4 |

## Every consultation route

| Family | Route | Status | R@1 | R@3 | R@5 | R@10 | R@20 | Hard R@10 | MRR@10 | nDCG@10 | Evidence valid | Marginal mean ms |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| legacy | legacy_tfidf | pass | 42.7% | 60.0% | 69.0% | 82.3% | 91.9% | 71.7% | 0.706 | 0.685 | 100.0% | 1.9 |
| embeddings | lexical | pass | 44.6% | 76.5% | 85.0% | 89.8% | 92.9% | 80.8% | 0.812 | 0.783 | 100.0% | 116.3 |
| embeddings | vector | pass | 24.0% | 50.0% | 58.1% | 80.0% | 91.5% | 65.0% | 0.598 | 0.580 | 100.0% | 125.5 |
| embeddings | hybrid | pass | 43.8% | 68.5% | 79.4% | 90.4% | 94.6% | 80.8% | 0.813 | 0.767 | 100.0% | 237.4 |
| classical | bm25 | pass | 59.6% | 72.1% | 84.0% | 88.8% | 93.5% | 74.2% | 0.921 | 0.831 | 100.0% | 58.9 |
| classical | topic | pass | 58.8% | 73.8% | 84.0% | 88.8% | 93.5% | 74.2% | 0.915 | 0.834 | 100.0% | 1370.5 |
| classical | association | pass | 58.8% | 73.8% | 84.0% | 88.8% | 93.5% | 74.2% | 0.915 | 0.835 | 100.0% | 1327.2 |
| classical | fusion | pass | 58.8% | 73.8% | 83.1% | 88.8% | 93.5% | 74.2% | 0.915 | 0.834 | 100.0% | 1349.1 |
| adaptive | bm25 | pass | 59.6% | 72.1% | 84.0% | 88.8% | 93.5% | 74.2% | 0.921 | 0.831 | 100.0% | 59.6 |
| adaptive | topic | pass | 58.8% | 73.8% | 84.0% | 88.8% | 93.5% | 74.2% | 0.915 | 0.834 | 100.0% | 1382.2 |
| adaptive | association | pass | 58.8% | 73.8% | 84.0% | 88.8% | 93.5% | 74.2% | 0.915 | 0.835 | 100.0% | 1378.1 |
| adaptive | fusion | pass | 58.8% | 73.8% | 83.1% | 88.8% | 93.5% | 74.2% | 0.915 | 0.834 | 100.0% | 1391.5 |
| adaptive | adaptive | pass | 58.8% | 73.8% | 83.1% | 88.8% | 93.5% | 74.2% | 0.915 | 0.834 | 100.0% | 5401.1 |
| entity-graph | lexical | pass | 44.6% | 66.5% | 78.8% | 82.5% | 91.0% | 65.8% | 0.820 | 0.727 | 100.0% | 1222.1 |
| entity-graph | entity | pass | 37.9% | 63.7% | 71.7% | 88.1% | 90.4% | 78.3% | 0.729 | 0.706 | 100.0% | 15.0 |
| entity-graph | traversal | pass | 23.5% | 40.8% | 44.2% | 58.8% | 65.8% | 48.3% | 0.519 | 0.460 | 100.0% | 8.2 |
| entity-graph | fusion | pass | 37.7% | 60.8% | 72.5% | 82.3% | 92.7% | 75.0% | 0.750 | 0.682 | 100.0% | 6.9 |
| ensemble | quality | pass | 52.1% | 74.6% | 84.8% | 89.6% | 94.4% | 77.5% | 0.890 | 0.819 | 100.0% | 6789.3 |
| ensemble | fast | pass | 49.6% | 73.8% | 83.5% | 88.8% | 93.5% | 74.2% | 0.873 | 0.801 | 100.0% | 7.5 |
| ensemble | robust | pass | 58.8% | 73.8% | 83.1% | 88.8% | 93.5% | 74.2% | 0.915 | 0.834 | 100.0% | 7.2 |

The legacy row is an evaluator-side deterministic TF-IDF baseline because the legacy consult skill exposes ledger/SPARQL reads but no ranked natural-language-search command. It does not invoke `grep` or `rg`.

The best-family table uses a second pass that times only the selected route, one query at a time, without sibling-route cache priming. Those standalone numbers are comparable. The every-route table retains query-major marginal timings used during metric collection; because later sibling routes can reuse bounded computation from the same query, those marginal timings are diagnostic and are not comparable as standalone route latency. Deep CLI inspection and one-time setup are excluded and reported separately.

All derived indexes are discovery-only. A high ranking score does not make a passage authoritative; only the separately checked ledger locator and hash establish evidence validity. No MCP participates.
