# Enterprise generator replay: question categories

[Comparison](README.md)

Eight exposed categories contain five questions each. Every paired ranking is identical. These are descriptive retrieval strata, not independent validation families. Values are nDCG@10 on a 0–100 scale.

## Basic

| Route | Incoming | G2 | Change (points) |
|---|---:|---:|---:|
| legacy-lexical | 100.00 | 100.00 | 0.00 |
| embeddings-lexical | 100.00 | 100.00 | 0.00 |
| embeddings-vector | 80.00 | 80.00 | 0.00 |
| embeddings-hybrid | 80.00 | 80.00 | 0.00 |
| classical-bm25 | 100.00 | 100.00 | 0.00 |
| classical-topic | 100.00 | 100.00 | 0.00 |
| classical-association | 100.00 | 100.00 | 0.00 |
| classical-fusion | 100.00 | 100.00 | 0.00 |
| adaptive-fusion | 100.00 | 100.00 | 0.00 |
| entity-graph-lexical | 100.00 | 100.00 | 0.00 |
| entity-graph-entity | 100.00 | 100.00 | 0.00 |
| entity-graph-traversal | 66.67 | 66.67 | 0.00 |
| entity-graph-fusion | 92.62 | 92.62 | 0.00 |
| ensemble-fast | 100.00 | 100.00 | 0.00 |
| ensemble-quality | 100.00 | 100.00 | 0.00 |
| ensemble-robust | 100.00 | 100.00 | 0.00 |
| graphify-search | 20.00 | 20.00 | 0.00 |
| turso-lexical-sql | 82.62 | 82.62 | 0.00 |

## Completeness

| Route | Incoming | G2 | Change (points) |
|---|---:|---:|---:|
| legacy-lexical | 53.09 | 53.09 | 0.00 |
| embeddings-lexical | 73.41 | 73.41 | 0.00 |
| embeddings-vector | 77.43 | 77.43 | 0.00 |
| embeddings-hybrid | 86.09 | 86.09 | 0.00 |
| classical-bm25 | 91.45 | 91.45 | 0.00 |
| classical-topic | 47.74 | 47.74 | 0.00 |
| classical-association | 47.74 | 47.74 | 0.00 |
| classical-fusion | 47.74 | 47.74 | 0.00 |
| adaptive-fusion | 73.62 | 73.62 | 0.00 |
| entity-graph-lexical | 79.70 | 79.70 | 0.00 |
| entity-graph-entity | 72.06 | 72.06 | 0.00 |
| entity-graph-traversal | 22.95 | 22.95 | 0.00 |
| entity-graph-fusion | 62.52 | 62.52 | 0.00 |
| ensemble-fast | 77.54 | 77.54 | 0.00 |
| ensemble-quality | 84.49 | 84.49 | 0.00 |
| ensemble-robust | 73.62 | 73.62 | 0.00 |
| graphify-search | 36.28 | 36.28 | 0.00 |
| turso-lexical-sql | 23.53 | 23.53 | 0.00 |

## Conflicting info

| Route | Incoming | G2 | Change (points) |
|---|---:|---:|---:|
| legacy-lexical | 100.00 | 100.00 | 0.00 |
| embeddings-lexical | 100.00 | 100.00 | 0.00 |
| embeddings-vector | 82.70 | 82.70 | 0.00 |
| embeddings-hybrid | 93.02 | 93.02 | 0.00 |
| classical-bm25 | 100.00 | 100.00 | 0.00 |
| classical-topic | 100.00 | 100.00 | 0.00 |
| classical-association | 100.00 | 100.00 | 0.00 |
| classical-fusion | 100.00 | 100.00 | 0.00 |
| adaptive-fusion | 100.00 | 100.00 | 0.00 |
| entity-graph-lexical | 100.00 | 100.00 | 0.00 |
| entity-graph-entity | 81.61 | 81.61 | 0.00 |
| entity-graph-traversal | 63.52 | 63.52 | 0.00 |
| entity-graph-fusion | 84.53 | 84.53 | 0.00 |
| ensemble-fast | 100.00 | 100.00 | 0.00 |
| ensemble-quality | 100.00 | 100.00 | 0.00 |
| ensemble-robust | 100.00 | 100.00 | 0.00 |
| graphify-search | 23.51 | 23.51 | 0.00 |
| turso-lexical-sql | 95.95 | 95.95 | 0.00 |

## Constrained

| Route | Incoming | G2 | Change (points) |
|---|---:|---:|---:|
| legacy-lexical | 100.00 | 100.00 | 0.00 |
| embeddings-lexical | 100.00 | 100.00 | 0.00 |
| embeddings-vector | 92.62 | 92.62 | 0.00 |
| embeddings-hybrid | 100.00 | 100.00 | 0.00 |
| classical-bm25 | 100.00 | 100.00 | 0.00 |
| classical-topic | 100.00 | 100.00 | 0.00 |
| classical-association | 100.00 | 100.00 | 0.00 |
| classical-fusion | 100.00 | 100.00 | 0.00 |
| adaptive-fusion | 100.00 | 100.00 | 0.00 |
| entity-graph-lexical | 100.00 | 100.00 | 0.00 |
| entity-graph-entity | 100.00 | 100.00 | 0.00 |
| entity-graph-traversal | 87.74 | 87.74 | 0.00 |
| entity-graph-fusion | 92.62 | 92.62 | 0.00 |
| ensemble-fast | 100.00 | 100.00 | 0.00 |
| ensemble-quality | 100.00 | 100.00 | 0.00 |
| ensemble-robust | 100.00 | 100.00 | 0.00 |
| graphify-search | 0.00 | 0.00 | 0.00 |
| turso-lexical-sql | 100.00 | 100.00 | 0.00 |

## Intra document reasoning

| Route | Incoming | G2 | Change (points) |
|---|---:|---:|---:|
| legacy-lexical | 100.00 | 100.00 | 0.00 |
| embeddings-lexical | 100.00 | 100.00 | 0.00 |
| embeddings-vector | 90.00 | 90.00 | 0.00 |
| embeddings-hybrid | 100.00 | 100.00 | 0.00 |
| classical-bm25 | 100.00 | 100.00 | 0.00 |
| classical-topic | 100.00 | 100.00 | 0.00 |
| classical-association | 100.00 | 100.00 | 0.00 |
| classical-fusion | 100.00 | 100.00 | 0.00 |
| adaptive-fusion | 100.00 | 100.00 | 0.00 |
| entity-graph-lexical | 100.00 | 100.00 | 0.00 |
| entity-graph-entity | 61.23 | 61.23 | 0.00 |
| entity-graph-traversal | 52.62 | 52.62 | 0.00 |
| entity-graph-fusion | 86.31 | 86.31 | 0.00 |
| ensemble-fast | 100.00 | 100.00 | 0.00 |
| ensemble-quality | 100.00 | 100.00 | 0.00 |
| ensemble-robust | 100.00 | 100.00 | 0.00 |
| graphify-search | 10.00 | 10.00 | 0.00 |
| turso-lexical-sql | 46.67 | 46.67 | 0.00 |

## Miscellaneous

| Route | Incoming | G2 | Change (points) |
|---|---:|---:|---:|
| legacy-lexical | 92.62 | 92.62 | 0.00 |
| embeddings-lexical | 92.62 | 92.62 | 0.00 |
| embeddings-vector | 92.62 | 92.62 | 0.00 |
| embeddings-hybrid | 92.62 | 92.62 | 0.00 |
| classical-bm25 | 100.00 | 100.00 | 0.00 |
| classical-topic | 100.00 | 100.00 | 0.00 |
| classical-association | 100.00 | 100.00 | 0.00 |
| classical-fusion | 100.00 | 100.00 | 0.00 |
| adaptive-fusion | 100.00 | 100.00 | 0.00 |
| entity-graph-lexical | 92.62 | 92.62 | 0.00 |
| entity-graph-entity | 52.62 | 52.62 | 0.00 |
| entity-graph-traversal | 32.36 | 32.36 | 0.00 |
| entity-graph-fusion | 52.62 | 52.62 | 0.00 |
| ensemble-fast | 100.00 | 100.00 | 0.00 |
| ensemble-quality | 100.00 | 100.00 | 0.00 |
| ensemble-robust | 100.00 | 100.00 | 0.00 |
| graphify-search | 41.23 | 41.23 | 0.00 |
| turso-lexical-sql | 80.00 | 80.00 | 0.00 |

## Project related

| Route | Incoming | G2 | Change (points) |
|---|---:|---:|---:|
| legacy-lexical | 85.65 | 85.65 | 0.00 |
| embeddings-lexical | 90.39 | 90.39 | 0.00 |
| embeddings-vector | 67.87 | 67.87 | 0.00 |
| embeddings-hybrid | 91.55 | 91.55 | 0.00 |
| classical-bm25 | 98.70 | 98.70 | 0.00 |
| classical-topic | 82.27 | 82.27 | 0.00 |
| classical-association | 82.27 | 82.27 | 0.00 |
| classical-fusion | 82.27 | 82.27 | 0.00 |
| adaptive-fusion | 94.72 | 94.72 | 0.00 |
| entity-graph-lexical | 91.12 | 91.12 | 0.00 |
| entity-graph-entity | 92.76 | 92.76 | 0.00 |
| entity-graph-traversal | 87.68 | 87.68 | 0.00 |
| entity-graph-fusion | 92.34 | 92.34 | 0.00 |
| ensemble-fast | 95.11 | 95.11 | 0.00 |
| ensemble-quality | 98.42 | 98.42 | 0.00 |
| ensemble-robust | 94.72 | 94.72 | 0.00 |
| graphify-search | 20.94 | 20.94 | 0.00 |
| turso-lexical-sql | 73.85 | 73.85 | 0.00 |

## Semantic

| Route | Incoming | G2 | Change (points) |
|---|---:|---:|---:|
| legacy-lexical | 79.29 | 79.29 | 0.00 |
| embeddings-lexical | 92.62 | 92.62 | 0.00 |
| embeddings-vector | 32.62 | 32.62 | 0.00 |
| embeddings-hybrid | 63.76 | 63.76 | 0.00 |
| classical-bm25 | 92.62 | 92.62 | 0.00 |
| classical-topic | 92.62 | 92.62 | 0.00 |
| classical-association | 92.62 | 92.62 | 0.00 |
| classical-fusion | 92.62 | 92.62 | 0.00 |
| adaptive-fusion | 92.62 | 92.62 | 0.00 |
| entity-graph-lexical | 100.00 | 100.00 | 0.00 |
| entity-graph-entity | 41.23 | 41.23 | 0.00 |
| entity-graph-traversal | 35.78 | 35.78 | 0.00 |
| entity-graph-fusion | 52.62 | 52.62 | 0.00 |
| ensemble-fast | 100.00 | 100.00 | 0.00 |
| ensemble-quality | 100.00 | 100.00 | 0.00 |
| ensemble-robust | 92.62 | 92.62 | 0.00 |
| graphify-search | 0.00 | 0.00 | 0.00 |
| turso-lexical-sql | 52.62 | 52.62 | 0.00 |

