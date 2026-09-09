# Classical: three diversity ties and a second catalog round

All three declared relevance-diversity variants tied exactly with retained candidate-011 at **60.097820% primary nDCG@10**. The controller stopped this mechanism after three consecutive qualified non-improvements. The first catalog round is complete, with all 17 variants exercised and six retained gains over its course.

| Candidate | Relevance / topic novelty / source novelty | Weighted nDCG@10 | Consecutive misses | Native job minutes |
| --- | --- | ---: | ---: | ---: |
| candidate-015 | 1 / 0 / 0 | 60.097820 | 1 | 28.53 |
| candidate-016 | 0.9 / 0.05 / 0.05 | 60.097820 | 2 | 27.16 |
| candidate-017 | 0.5 / 0.25 / 0.25 | 60.097820 | 3 | 26.72 |

Each variant ties candidate-011 on all 112 eligible question nDCG values; eight questions without references remain outside retrieval scoring. The comparison includes the four original jobs, all with evidence integrity 1.0, no errors and no retries. These are measured ties, not inferred zeros or missing results.

The completed round improved from the initial 55.042133% to 60.097820%. Under the frozen outer-round rule, that improvement starts a second round instead of ending the family search. The next sealed candidate-018 changes only `bm25.b` to `0.25` on the retained candidate-011 settings. It tests a new combined profile; an earlier value tested on a different parent is not automatically a duplicate.

The full seventeen-variant prefix, all native case metrics and exact profiles, counters, mechanism stop, first-round result and next mutation contract replayed successfully. The family has not reached a complete non-improving round or its five-round limit.

The existing [source-group audit](../classical-source-cap-001/README.md) explains why altering novelty weights leaves the application-level identity cap in place. These three ties cover the declared weight variants; they do not exhaust the separate identity-cap opportunity or every possible diversification method.

Scope: 120 stratified development questions, 112 eligible questions, population weight 470 and 6,000 reference-enriched complete documents. Native durations are observations, not campaign wall time or an invoice. This report runs no new trial or model call and uses no private validation. Joint selection, the all-500 comparison and promotion remain pending.

[Exact metrics, stopping events and source hashes](aggregate.json) · [Retained gain](../classical-progress-006/README.md) · [Campaign](../README.md)
