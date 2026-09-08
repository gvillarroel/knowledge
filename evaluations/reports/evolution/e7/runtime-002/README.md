# E7 Embeddings: three misses and a verified mechanism change

Observed at 2026-09-08T16:54:37.425582+00:00. The family search is still running.

**Three semantic-segmentation variants exceeded the original 2,400-second builder subprocess limit.** The native scheduler recorded consecutive misses 1, 2 and 3, retained the qualified baseline, and moved to the next predeclared mechanism. A live container for candidate004, neighboring-sentence context with `chunking.buffer_size=2`, was verified at observation.

| Candidate | Semantic threshold | Weighted nDCG@10 (%) | Native job seconds | Execution errors | Consecutive misses |
| --- | ---: | ---: | ---: | ---: | ---: |
| baseline | default | 63.51 | 1085.26 | 0 | 0 |
| candidate-001 | 95 | N/A | 2432.92 | 1 | 1 |
| candidate-002 | 90 | N/A | 2431.70 | 1 | 2 |
| candidate-003 | 80 | N/A | 2432.49 | 1 | 3 |

The failed candidates have no ranking or verifier score. Their native scheduler objectives are zero and are kept separately from the unavailable retrieval measurements. There were no retries and no demonstrated external outage. Thresholds 70 and 50 were skipped after the third miss, as required by the frozen stopping rule.

The three failed native jobs consumed 121.62 minutes in total, excluding candidate staging and supervisor overhead. This consumed time remains part of the campaign cost account. The baseline remains at 63.51% weighted development nDCG@10.

The useful finding is operational: changing the semantic threshold to 95, 90 or 80 did not make these candidates finish within this CPU and time contract. Their semantic retrieval quality remains unknown. The next context mechanism requires its own original evidence before any quality claim or retention decision.

Scope: 120 category-stratified development questions, 112 eligible, and 6,000 reference-enriched complete documents. This is not a completed family search, final all-500 comparison, answer Overall score or public rank. Private validation remains sealed and no retrieval profile is promoted.

[Exact aggregates and evidence hashes](aggregate.json) · [First timeout](../runtime-001/README.md) · [Campaign](../README.md)
