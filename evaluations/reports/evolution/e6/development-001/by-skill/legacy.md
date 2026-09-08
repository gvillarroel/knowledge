# legacy evolution

[General comparison](../README.md)

| Candidate | Strategy | Qualified | nDCG@10 | Improved incumbent | Consecutive misses |
|---|---|---|---:|---|---:|
| baseline | baseline | True | 57.50 | False | 0 |
| candidate-001 | bm25-saturation | True | 58.68 | True | 0 |
| candidate-002 | bm25-saturation | True | 58.14 | False | 1 |
| candidate-003 | bm25-saturation | True | 59.62 | True | 0 |
| candidate-004 | bm25-saturation | True | 59.52 | False | 1 |
| candidate-005 | length-normalization | True | 57.78 | False | 1 |
| candidate-006 | length-normalization | True | 56.52 | False | 2 |
| candidate-007 | length-normalization | True | 58.48 | False | 3 |
| candidate-008 | title-weight | True | 58.97 | False | 1 |
| candidate-009 | title-weight | True | 58.77 | False | 2 |
| candidate-010 | title-weight | True | 58.08 | False | 3 |
