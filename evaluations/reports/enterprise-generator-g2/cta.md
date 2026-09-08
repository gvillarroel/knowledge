# Enterprise generator replay: cost, time and quality

[Comparison](README.md)

These cost measures cover benchmark execution. Codex authoring usage is excluded.

Provider USD and LLM tokens are zero; local compute cost is not measured. MiniLM runs locally. There is no new model-generated answer-quality score. Builds run in pairs, each with two CPUs and eight GiB. Query scoring is serial in fresh family/version containers. Each family shares its validated snapshot across routes. P95 covers one pass over forty queries and is descriptive only. Snapshot loading is excluded; lazy work performed inside a query remains in its latency.

| Family | Incoming build (s) | G2 build (s) | Incoming expert (MiB) | G2 expert (MiB) |
|---|---:|---:|---:|---:|
| legacy | 116.55 | 116.57 | 28.975 | 28.980 |
| embeddings | 183.25 | 182.74 | 40.000 | 40.006 |
| classical | 186.72 | 186.67 | 111.306 | 111.311 |
| adaptive | 186.39 | 186.27 | 111.367 | 111.372 |
| entity-graph | 188.26 | 188.40 | 129.144 | 129.149 |
| ensemble | 439.74 | 440.63 | 222.586 | 222.591 |
| graphify | 726.74 | 726.75 | 38.355 | 38.360 |
| turso | 177.16 | 177.25 | 134.900 | 134.905 |

| Route | Incoming P95 (ms) | G2 P95 (ms) | nDCG change (points) |
|---|---:|---:|---:|
| legacy-lexical | 6.89 | 6.84 | 0.00 |
| embeddings-lexical | 203.68 | 203.23 | 0.00 |
| embeddings-vector | 188.07 | 176.50 | 0.00 |
| embeddings-hybrid | 395.33 | 388.36 | 0.00 |
| classical-bm25 | 252.10 | 256.65 | 0.00 |
| classical-topic | 249.50 | 251.49 | 0.00 |
| classical-association | 248.69 | 251.54 | 0.00 |
| classical-fusion | 247.81 | 252.28 | 0.00 |
| adaptive-fusion | 1590.00 | 1608.32 | 0.00 |
| entity-graph-lexical | 762.10 | 770.35 | 0.00 |
| entity-graph-entity | 771.29 | 773.58 | 0.00 |
| entity-graph-traversal | 764.75 | 769.98 | 0.00 |
| entity-graph-fusion | 766.50 | 776.15 | 0.00 |
| ensemble-fast | 2337.99 | 2308.27 | 0.00 |
| ensemble-quality | 2838.14 | 2839.98 | 0.00 |
| ensemble-robust | 1577.58 | 1570.69 | 0.00 |
| graphify-search | 213.57 | 208.93 | 0.00 |
| turso-lexical-sql | 384.85 | 379.12 | 0.00 |

Independent reconstruction, verification, test execution and the rejected setup attempt are excluded from these build/query timings. Do not interpret timing noise as an efficiency gain. All versions retain identical ordered evidence.
