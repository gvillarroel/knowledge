# ensemble evolution

[General comparison](../README.md)

| Candidate | Strategy | Qualified | nDCG@10 | Improved incumbent | Consecutive misses |
|---|---|---|---:|---|---:|
| baseline | baseline | True | 55.66 | False | 0 |
| candidate-001 | length-normalization | True | 55.77 | True | 0 |
| candidate-002 | length-normalization | True | 56.43 | True | 0 |
| candidate-003 | length-normalization | True | 57.34 | True | 0 |
| candidate-004 | length-normalization | True | 55.72 | False | 1 |
| candidate-005 | bm25-saturation | True | 56.69 | False | 1 |
| candidate-006 | bm25-saturation | True | 56.01 | False | 2 |
| candidate-007 | bm25-saturation | True | 55.62 | False | 3 |
| candidate-008 | title-weight | True | 57.34 | False | 1 |
| candidate-009 | title-weight | True | 57.34 | False | 2 |
| candidate-010 | expansion-strength | True | 56.09 | False | 1 |
| candidate-011 | expansion-strength | True | 56.20 | False | 2 |
| candidate-012 | expansion-strength | True | 56.09 | False | 3 |
| candidate-013 | relevance-diversity | True | 59.32 | True | 0 |
| candidate-014 | relevance-diversity | True | 58.71 | False | 1 |
| candidate-015 | relevance-diversity | True | 47.68 | False | 2 |
| candidate-016 | ensemble-allocation | True | 60.28 | True | 0 |
| candidate-017 | ensemble-allocation | True | 61.35 | True | 0 |
| candidate-018 | ensemble-allocation | True | 61.37 | True | 0 |
