# EnterpriseRAG E16: terminal execution failures

Both corrected first-measurement implementations reached the frozen 3,600-second agent limit. Harbor completed two trials with two AgentTimeoutError outcomes and no qualified retrieval score. The verifier's zero rewards are error artifacts, not measured zero nDCG values.

The launcher drained both original jobs, removed the optimizer and closed the study. It emitted no selection and did not execute joint replay, all-500 comparison or private acceptance. E16 is terminal and cannot be restarted. The requested final comparison remains incomplete in E16.

## Retained development observations

These six scores are preserved E14 observations on 120 stratified questions, 112 retrieval-eligible questions and 6,000 complete documents. They use the frozen category-weighted nDCG@10, multiplied by 100. They are not new E16 measurements or official full-corpus answer-quality scores.

| Strategy | Retained nDCG@10 ×100 | Current evidence |
| --- | ---: | --- |
| legacy | 72.38 | Preserved E14 development observation |
| turso | 72.38 | Preserved E14 development observation |
| adaptive | 66.21 | Preserved E14 development observation |
| graphify | 63.72 | Preserved E14 development observation |
| embeddings | 63.51 | Preserved E14 development observation |
| classical | 62.10 | Preserved E14 development observation |
| entity-graph | Unavailable | E16 original timed out; no qualified score |
| ensemble | Unavailable | E16 original timed out; no qualified score |

## Accounting and interpretation

Two previously reserved construction identities were measured once and are now consumed. The cumulative development allocation count is 63. No new profile mutation, proposal charge, quality miss, retry, or canonical skill promotion occurred. Proposal claims remain 140 of the 585 cumulative cap; closed-family unused capacity remains nontransferable.

The six completed finite catalogs remain closed. The two remaining catalogs are blocked by failed qualification; their hypotheses have not been exhausted. Software checks proved the local behavior of the corrected implementations, but did not establish acceptable end-to-end runtime under this benchmark condition.

[Cost, time and quality](cta.md) · [Applications, categories and datasets](groups.md) · [Machine-readable aggregate](aggregate.json) · [Runtime verification](../public-freeze-001/README.md)
