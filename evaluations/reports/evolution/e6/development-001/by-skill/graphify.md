# graphify evolution

[General comparison](../README.md)

| Candidate | Strategy | Qualified | nDCG@10 | Improved incumbent | Consecutive misses |
|---|---|---|---:|---|---:|
| baseline | baseline | True | 13.63 | False | 0 |
| candidate-001 | traversal-depth | True | 9.11 | False | 1 |
| candidate-002 | traversal-depth | True | 9.11 | False | 2 |
| candidate-003 | traversal-depth | True | 51.44 | True | 0 |
| candidate-004 | traversal-depth | True | 53.75 | True | 0 |
| candidate-005 | traversal-depth | True | 53.75 | False | 1 |
| candidate-006 | traversal-depth | True | 53.75 | False | 2 |
| candidate-007 | lexical-graph-fusion | True | 57.63 | True | 0 |
| candidate-008 | lexical-graph-fusion | True | 56.93 | False | 1 |
| candidate-009 | lexical-graph-fusion | True | 58.38 | True | 0 |
| candidate-010 | lexical-graph-fusion | True | 60.36 | True | 0 |
| candidate-011 | fusion-rank-decay | True | 58.39 | False | 1 |
| candidate-012 | fusion-rank-decay | True | 57.13 | False | 2 |
| candidate-013 | fusion-rank-decay | True | 56.93 | False | 3 |
