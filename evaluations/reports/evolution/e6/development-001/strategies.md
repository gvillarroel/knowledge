# Strategy stopping ledger

[General comparison](README.md)

Three consecutive misses stop a tactic. A gain resets the counter. A shorter finite catalog can end before three misses. Duplicate profiles do not count as attempts. This is exhaustion of the declared catalog, not every possible future research strategy.

| Family | Strategy | Stop reason | Final miss streak | Unused variants |
|---|---|---|---:|---:|
| legacy | bm25-saturation | catalog-exhausted | 1 | 0 |
| legacy | length-normalization | three-consecutive-failures | 3 | 1 |
| legacy | title-weight | three-consecutive-failures | 3 | 0 |
| embeddings | semantic-segmentation | three-consecutive-failures | 3 | 2 |
| embeddings | semantic-context | three-consecutive-failures | 3 | 0 |
| classical | length-normalization | catalog-exhausted | 0 | 0 |
| classical | bm25-saturation | three-consecutive-failures | 3 | 0 |
| classical | title-weight | catalog-exhausted | 0 | 0 |
| classical | expansion-strength | three-consecutive-failures | 3 | 0 |
| classical | relevance-diversity | catalog-exhausted | 2 | 0 |
| adaptive | length-normalization | catalog-exhausted | 0 | 0 |
| adaptive | bm25-saturation | three-consecutive-failures | 3 | 0 |
| adaptive | title-weight | catalog-exhausted | 0 | 0 |
| adaptive | expansion-strength | three-consecutive-failures | 3 | 1 |
| adaptive | relevance-diversity | catalog-exhausted | 2 | 0 |
| adaptive | aspect-allocation | three-consecutive-failures | 3 | 0 |
| entity-graph | length-normalization | catalog-exhausted | 2 | 0 |
| entity-graph | bm25-saturation | three-consecutive-failures | 3 | 0 |
| entity-graph | graph-reach | catalog-exhausted | 2 | 0 |
| entity-graph | graph-noise | catalog-exhausted | 2 | 0 |
| entity-graph | section-granularity | three-consecutive-failures | 3 | 0 |
| ensemble | length-normalization | catalog-exhausted | 1 | 0 |
| ensemble | bm25-saturation | three-consecutive-failures | 3 | 0 |
| ensemble | title-weight | catalog-exhausted | 2 | 0 |
| ensemble | expansion-strength | three-consecutive-failures | 3 | 1 |
| ensemble | relevance-diversity | catalog-exhausted | 2 | 0 |
| ensemble | ensemble-allocation | catalog-exhausted | 0 | 0 |
| graphify | traversal-depth | catalog-exhausted | 2 | 0 |
| graphify | lexical-graph-fusion | catalog-exhausted | 0 | 0 |
| graphify | fusion-rank-decay | three-consecutive-failures | 3 | 0 |
| turso | bm25-saturation | catalog-exhausted | 1 | 0 |
| turso | length-normalization | three-consecutive-failures | 3 | 1 |
| turso | title-weight | three-consecutive-failures | 3 | 0 |

Skipped duplicate profiles: 4.
