# E7 Embeddings: development search completed

Family completion snapshot at 2026-09-08T18:58:48.452885+00:00. The campaign is still running.

**Embeddings retains its initial 63.51% weighted nDCG@10 on the fixed hybrid route.** Six distinct construction variants received original native trials. Each exceeded the builder time limit before producing retrieval measurements, so none qualified as an improvement.

The frozen history was replayed against every original native archive. Three consecutive misses stopped semantic segmentation, and three stopped neighboring-sentence context. The complete catalog round produced no gain and the unchanged baseline was retained. This is exhaustion of the declared search under its runtime budget, not evidence about every possible Embeddings change.

| Candidate | Mechanism | Weighted nDCG@10 | Qualified | Execution errors | Consecutive misses |
| --- | --- | ---: | --- | ---: | ---: |
| baseline | baseline | 63.51 | True | 0 | 0 |
| candidate-001 | semantic-segmentation | N/A | False | 1 | 1 |
| candidate-002 | semantic-segmentation | N/A | False | 1 | 2 |
| candidate-003 | semantic-segmentation | N/A | False | 1 | 3 |
| candidate-004 | semantic-context | N/A | False | 1 | 1 |
| candidate-005 | semantic-context | N/A | False | 1 | 2 |
| candidate-006 | semantic-context | N/A | False | 1 | 3 |

N/A means the original trial produced no retrieval score. The controller uses a zero penalty for an unqualified attempt; that penalty is not a measured zero nDCG. The baseline is the only qualified original job in this family search.

## Useful findings and limits

- The tested semantic thresholds 95, 90 and 80 failed their fixed construction budget. Thresholds 70 and 50 were skipped after the third consecutive miss; they are declared options, not executed trials.
- Context buffers 2, 3 and 4 also failed the same builder budget. All six original tracebacks identify the native Embeddings builder and a 2,400-second subprocess timeout.
- These outcomes establish a construction-time limitation for these profiles on this full-text workload and runtime. They do not establish that semantic chunking has worse retrieval relevance, because no candidate reached that measurement.
- The initial pinned MiniLM profile remains unchanged. No failed trial was retried and no diagnostic route was substituted for the declared hybrid primary route.

## Cost, scope and pending work

The six failed original jobs consumed 14590.40 seconds (243.17 minutes). Including the qualified baseline, original native job durations sum to 15675.66 seconds (261.26 minutes). These are summed job durations, excluding host staging and later stages; they are not campaign wall time or a provider invoice. Native LLM calls: zero. Provider cost: N/A.

The study uses 120 stratified development questions, 112 with qrels, on 6,000 reference-enriched complete documents. Category weights total 470 eligible public questions. The other family searches, joint replay and freeze, actual all-500 comparison and single private gate remain pending. No private feedback was used and no retrieval profile was promoted.

[Exact aggregate and native hashes](aggregate.json) · [Campaign](../README.md)
