# E7 runtime evidence: semantic segmentation exceeded the build limit

Partial development snapshot at 2026-09-08T15:33:34.862144+00:00. The campaign continues.

The first Embeddings semantic-segmentation candidate exceeded the frozen 2,400-second native builder subprocess limit before producing a ranking or verifier reward. The candidate is unqualified and cannot replace the baseline. Its retrieval score is unavailable.

| Arm | Weighted development nDCG@10 | Native job seconds | Execution errors | Status |
| --- | ---: | ---: | ---: | --- |
| baseline | 63.51 | 1085.26 | 0 | qualified |
| candidate-001 | N/A | 2432.92 | 1 | native-execution-error |

The native scheduler assigns an error objective of zero and counts one miss for this completed failed attempt. That objective is preserved separately in the aggregate; it is not a measured zero nDCG. There was no automatic retry. The next distinct predeclared variant continues with the same hardware and time limits.

This establishes that this exact candidate did not finish under the declared CPU budget. It does not establish semantic segmentation quality, failure under other hardware, or an external infrastructure outage. The later missing ranking artifact followed the builder timeout.

Scope: 120 category-stratified questions, 112 with qrels, and 6,000 reference-enriched full-text documents. No final all-500 result, private release, profile promotion, answer Overall or public leaderboard comparison is implied.

[Aggregate and source hashes](aggregate.json) · [Campaign](../README.md)
