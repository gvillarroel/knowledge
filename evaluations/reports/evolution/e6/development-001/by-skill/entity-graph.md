# entity-graph evolution

[General comparison](../README.md)

| Candidate | Strategy | Qualified | nDCG@10 | Improved incumbent | Consecutive misses |
|---|---|---|---:|---|---:|
| baseline | baseline | True | 47.28 | False | 0 |
| candidate-001 | length-normalization | True | 47.73 | True | 0 |
| candidate-002 | length-normalization | True | 46.90 | False | 1 |
| candidate-003 | length-normalization | True | 46.88 | False | 2 |
| candidate-004 | bm25-saturation | True | 47.73 | False | 1 |
| candidate-005 | bm25-saturation | True | 47.73 | False | 2 |
| candidate-006 | bm25-saturation | True | 47.68 | False | 3 |
| candidate-007 | graph-reach | True | 47.77 | True | 0 |
| candidate-008 | graph-reach | True | 47.73 | False | 1 |
| candidate-009 | graph-reach | True | 47.73 | False | 2 |
| candidate-010 | graph-noise | True | 48.19 | True | 0 |
| candidate-011 | graph-noise | True | 48.16 | False | 1 |
| candidate-012 | graph-noise | True | 47.73 | False | 2 |
| candidate-013 | section-granularity | True | 48.19 | False | 1 |
| candidate-014 | section-granularity | True | 48.19 | False | 2 |
| candidate-015 | section-granularity | True | 48.19 | False | 3 |
