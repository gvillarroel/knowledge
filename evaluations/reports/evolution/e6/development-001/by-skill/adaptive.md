# adaptive evolution

[General comparison](../README.md)

| Candidate | Strategy | Qualified | nDCG@10 | Improved incumbent | Consecutive misses |
|---|---|---|---:|---|---:|
| baseline | baseline | True | 50.69 | False | 0 |
| candidate-001 | length-normalization | True | 50.58 | False | 1 |
| candidate-002 | length-normalization | True | 51.54 | True | 0 |
| candidate-003 | length-normalization | True | 51.90 | True | 0 |
| candidate-004 | bm25-saturation | True | 51.04 | False | 1 |
| candidate-005 | bm25-saturation | True | 51.84 | False | 2 |
| candidate-006 | bm25-saturation | True | 49.85 | False | 3 |
| candidate-007 | title-weight | True | 51.90 | False | 1 |
| candidate-008 | title-weight | True | 51.90 | False | 2 |
| candidate-009 | title-weight | True | 51.93 | True | 0 |
| candidate-010 | expansion-strength | True | 51.64 | False | 1 |
| candidate-011 | expansion-strength | True | 50.82 | False | 2 |
| candidate-012 | expansion-strength | True | 51.59 | False | 3 |
| candidate-013 | relevance-diversity | True | 58.62 | True | 0 |
| candidate-014 | relevance-diversity | True | 56.32 | False | 1 |
| candidate-015 | relevance-diversity | True | 46.27 | False | 2 |
| candidate-016 | aspect-allocation | True | 58.62 | False | 1 |
| candidate-017 | aspect-allocation | True | 58.62 | False | 2 |
| candidate-018 | aspect-allocation | True | 58.62 | False | 3 |
