# classical evolution

[General comparison](../README.md)

| Candidate | Strategy | Qualified | nDCG@10 | Improved incumbent | Consecutive misses |
|---|---|---|---:|---|---:|
| baseline | baseline | True | 44.35 | False | 0 |
| candidate-001 | length-normalization | True | 44.63 | True | 0 |
| candidate-002 | length-normalization | True | 41.70 | False | 1 |
| candidate-003 | length-normalization | True | 44.84 | True | 0 |
| candidate-004 | length-normalization | True | 45.82 | True | 0 |
| candidate-005 | bm25-saturation | True | 44.60 | False | 1 |
| candidate-006 | bm25-saturation | True | 45.75 | False | 2 |
| candidate-007 | bm25-saturation | True | 45.75 | False | 3 |
| candidate-008 | title-weight | True | 45.82 | False | 1 |
| candidate-009 | title-weight | True | 45.82 | False | 2 |
| candidate-010 | title-weight | True | 46.20 | True | 0 |
| candidate-011 | expansion-strength | True | 44.62 | False | 1 |
| candidate-012 | expansion-strength | True | 45.82 | False | 2 |
| candidate-013 | expansion-strength | True | 43.53 | False | 3 |
| candidate-014 | relevance-diversity | True | 48.21 | True | 0 |
| candidate-015 | relevance-diversity | True | 47.35 | False | 1 |
| candidate-016 | relevance-diversity | True | 43.30 | False | 2 |
