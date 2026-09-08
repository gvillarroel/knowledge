# E7 adaptive development baseline

Snapshot: 2026-09-08T19:24:02.036302+00:00. This is an initial reference measurement; no family improvement is established.

| Route | Weighted nDCG@10 | Weighted recall@10 | Weighted MRR@10 | Weighted full qrel coverage@10 |
| --- | ---: | ---: | ---: | ---: |
| adaptive | 60.04 | 69.19 | 60.70 | 62.39 |

Quality columns are percentages. The frozen primary route is `adaptive`. All metrics were reaggregated from the original native per-question results, using the same 120-question stratified development selection, 112 eligible questions and category weights totaling 470. The remaining eight questions have no original document references.

| Original native job | Agent execution | Double build and validation | Knowledge size | Primary query P95 |
| ---: | ---: | ---: | ---: | ---: |
| 1388.00 s | 1339.79 s | 589.04 s | 532.05 MiB | 8415.33 ms |

The single original job completed with evidence integrity 1.0, zero execution errors and zero retries. The observed reward is below the separate 0.8 diagnostic threshold; that threshold does not determine native qualification or development retention. Timing is measured for this job, excludes candidate staging and supervisor overhead, and is not the campaign wall time or an invoice. No language model calls were made.

The corpus contains 6,000 reference-enriched complete documents. This internal retrieval baseline does not establish an answer Overall score, public leaderboard position or performance on all 500 public questions. The family mutations, joint selection and freeze, all-500 paired comparison and private transfer gate remain pending. No retrieval profile is promoted by this baseline report.

[Exact aggregate and native evidence hashes](aggregate.json) · [Campaign](../README.md) · [Predeclared opportunities](../strategy-coverage.md)
