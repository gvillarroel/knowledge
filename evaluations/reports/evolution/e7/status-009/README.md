# E7 all-family progress audit

Snapshot: 2026-09-08T19:15:23.228330+00:00. Native Docker containers were inspected at this time; later status changes do not rewrite this snapshot.

Completed family searches: **2/8**. Completed qualified baselines: **3/8**. Families with a live trial verified at observation: **2**. The campaign is incomplete.

| Family | Native state | Baseline nDCG@10 | Retained nDCG@10 | Completed variants | Qualified variants | Execution errors |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| legacy | family-complete | 61.11 | 72.38 | 16 | 16 | 0 |
| embeddings | family-complete | 63.51 | 63.51 | 6 | 0 | 6 |
| classical | trial-running | 55.04 | 58.24 | 6 | 6 | 0 |
| adaptive | trial-running | N/A | N/A | 0 | 0 | 0 |
| entity-graph | not-started | N/A | N/A | 0 | 0 | 0 |
| ensemble | not-started | N/A | N/A | 0 | 0 | 0 |
| graphify | not-started | N/A | N/A | 0 | 0 | 0 |
| turso | not-started | N/A | N/A | 0 | 0 | 0 |

Scores are category-weighted development retrieval nDCG@10 percentages on 112 eligible questions from the 120-question stratified subset and 6,000 reference-enriched full-text documents. A baseline score is not evidence that the family improved. Unqualified execution attempts have no retrieval measurement and are counted separately as errors.

Only native completed archives supply the displayed scores. An unfinished trial is called running only when a matching live container was observed. Queued families are not counted as tested. Completed family histories were replayed against the frozen scheduler and native evidence; unfinished families still require their terminal stopping audits.

The remaining completion requirements are terminal opportunity/stopping evidence for every family, exact joint replay and freeze, the all-500 paired comparison, the private gate, the final family/category/application/CTA reports and catalog, and any permitted promotion. No answer Overall or public leaderboard rank is established by this internal snapshot.

[Aggregate and native evidence hashes](aggregate.json) · [Campaign](../README.md) · [Strategy coverage](../strategy-coverage.md)
