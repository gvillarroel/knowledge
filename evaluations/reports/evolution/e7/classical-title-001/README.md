# E7 Classical: rejected title-weight mutation

`bm25.title_weight=4.0` reduced the fixed fusion nDCG@10 from 58.67% to 50.59%, a loss of 8.08 percentage points. The original job qualified without execution errors. The controller rejected candidate-008 and retained candidate-007; this is the first miss of the title-weight mechanism. The tested profile keeps the incumbent `bm25.b=1.0` and `bm25.k1=3.0`.

| Configuration | Weighted nDCG@10 | Weighted recall@10 | Weighted MRR@10 | Weighted full qrel coverage@10 |
| --- | ---: | ---: | ---: | ---: |
| candidate-007 | 58.67 | 62.11 | 62.86 | 54.84 |
| candidate-008 | 50.59 | 56.21 | 53.26 | 48.83 |

The reference here is the retained candidate-007, not the study initial baseline. Metric columns are percentages.

Against that incumbent, 2 eligible questions improve, 22 regress and 88 tie. These counts are unweighted; the aggregate uses the frozen category weights. Eight questions without references have no retrieval score.

| Diagnostic route | Retained nDCG@10 | Tested nDCG@10 | Delta pp |
| --- | ---: | ---: | ---: |
| bm25 | 61.54 | 56.46 | -5.08 |
| topic | 58.65 | 50.54 | -8.11 |
| association | 58.65 | 50.54 | -8.11 |
| fusion | 58.67 | 50.59 | -8.08 |

The diagnostic routes do not replace fusion as the selection objective. The declined mutation is preserved as measured evidence. Remaining title weights and later mechanisms still have to run; a single miss does not establish that title weighting cannot help.

Both original jobs have evidence integrity 1.0, no execution errors, no retries and no language model calls. The 0.8 diagnostic threshold is separate from native qualification and development retention. Native timings, skill and artifact digests are preserved in the aggregate.

Scope: the fixed 120-question stratified development sample, 112 eligible questions, eligible population weight 470, and 6,000 reference-enriched complete documents. No all-500 performance, private transfer result, answer Overall score or public rank is established by this snapshot.

[Exact aggregates and native hashes](aggregate.json) · [Retained Classical gain](../classical-progress-004/README.md) · [Campaign](../README.md)
