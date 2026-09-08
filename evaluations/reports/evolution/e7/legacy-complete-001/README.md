# E7 Legacy: development search completed

Family completion snapshot at 2026-09-08T15:55:02.539034+00:00. The other families and final comparison remain in progress.

**Legacy retained 72.38% weighted nDCG@10, up from 61.11% (+11.27 percentage points).** The selected consultation profile uses BM25 with k1=2.0 and title weight=4.0. Construction remains unchanged.

The frozen scheduler evaluated 16 distinct variants in two rounds. The second complete round produced no improvement, so this family stopped by its preregistered plateau rule. This establishes a plateau within the tested catalog; it does not prove that all possible retrieval changes are exhausted.

All 17 original native jobs, including the baseline, qualified with zero execution errors. The final history was replayed against the frozen scheduler and every native archive. Its decisions, miss counts, skipped duplicates, retained profile and stop reason matched.

| Candidate | Mechanism | Weighted nDCG@10 | Improved | Consecutive misses |
| --- | --- | ---: | --- | ---: |
| baseline | baseline | 61.11 | False | 0 |
| candidate-001 | bm25-saturation | 72.08 | True | 0 |
| candidate-002 | bm25-saturation | 69.31 | False | 1 |
| candidate-003 | bm25-saturation | 72.13 | True | 0 |
| candidate-004 | bm25-saturation | 71.13 | False | 1 |
| candidate-005 | length-normalization | 66.80 | False | 1 |
| candidate-006 | length-normalization | 61.35 | False | 2 |
| candidate-007 | length-normalization | 70.44 | False | 3 |
| candidate-008 | title-weight | 72.12 | False | 1 |
| candidate-009 | title-weight | 72.38 | True | 0 |
| candidate-010 | title-weight | 72.12 | False | 1 |
| candidate-011 | bm25-saturation | 71.97 | False | 1 |
| candidate-012 | bm25-saturation | 69.24 | False | 2 |
| candidate-013 | bm25-saturation | 71.36 | False | 3 |
| candidate-014 | length-normalization | 66.70 | False | 1 |
| candidate-015 | length-normalization | 61.38 | False | 2 |
| candidate-016 | length-normalization | 69.72 | False | 3 |

## Retained lessons

- Replacing overlap ranking with BM25 produced most of the gain. The later k1=2.0 adjustment added a smaller increment to that improvement.
- A title weight of 4.0 added a smaller gain after saturation improved. Higher title weight did not improve it.
- The tested reductions in length normalization did not improve either retained configuration. The three-miss rule stopped that mechanism in each round; the remaining catalog option was not evaluated.
- Repeating the catalog with the improved title weight found no further gain. Previously tested complete profiles were skipped, preserving all earlier observations.

## Cost, scope and pending gates

Original native job durations sum to 2222.39 seconds (37.04 minutes). This is workload elapsed time, excluding host staging and later campaign stages; it is not campaign wall time. LLM calls: zero. Provider cost: N/A.

These scores use 120 stratified questions, 112 with qrels, on 6,000 reference-enriched full-text documents. Category weighting targets the 470 eligible public questions. The complete all-500 comparison, joint replay, joint selection freeze and private transfer gate remain pending. This family result does not authorize promotion and is not an answer Overall or public leaderboard score.

[Exact aggregate and native hashes](aggregate.json) · [Campaign](../README.md)
