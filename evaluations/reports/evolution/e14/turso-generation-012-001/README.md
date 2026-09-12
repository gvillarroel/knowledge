# EnterpriseRAG E14: Turso generation 12 retains its incumbent

Date: 2026-09-12. The qualified consultation variant `{"engine": "bm25", "k1": 3.0}` scored **71.36 nDCG@10 x100**, compared with **72.38** for the retained `versioned-007`. The native owner records **3 consecutive evaluable misses** in `bm25-saturation`. The third consecutive miss requires the next step to change mechanism.

The unchanged workload contains 120 stratified questions, 112 retrieval-eligible questions, 6,000 complete documents and eligible population weight 470. Construction is frozen for this consultation treatment.

| Metric (x100) | Retained incumbent | Candidate | Delta points |
| --- | --- | --- | --- |
| nDCG@10 | 72.38 | 71.36 | -1.01597 |
| Recall@10 | 81.99 | 81.18 | -0.80748 |
| MRR@10 | 71.51 | 70.79 | -0.71760 |
| Full-reference coverage@10 | 76.43 | 75.95 | -0.47651 |

At question level, **14 improve, 12 regress and 86 tie**; eight questions lack retrieval references. The frozen weights and size of each change determine the aggregate result. Displayed scores and differences are rounded independently from full precision.

## Opportunity accounting

This observation adds one proposal charge, bringing Turso to **13 / 55 claims**, including **11 new E14 claims**. The current mechanism is `bm25-saturation`, round **2**, with **4 / 4** catalog entries visited and **3 / 3** consecutive evaluable misses. The third consecutive miss requires the next step to change mechanism. The family retains its other declared opportunities, inherited five-round ceiling and remaining cap. Original identities and charges are preserved, with no retry or budget reset.

The owner skipped the already seen `k1=2.0` profile before the final entry. That duplicate adds no proposal charge, native rerun or quality miss. The four visited catalog entries therefore contain three unique evaluated variants and one skipped duplicate. The third evaluated miss requires the next mechanism.

The report contains **14 cumulative original native records** and **one new observation**. All records have zero execution errors and zero retries. The complete captured history includes dominated candidates. Native normalization, owning receipt/progress and the common reconciler agree on qualification and retention. Reporting dispatched no native job.

## Retained eight-family comparison

| Family | Retained nDCG@10 x100 | Qualification |
| --- | --- | --- |
| legacy | 72.38 | Qualified |
| turso | 72.38 | Qualified |
| adaptive | 66.21 | Qualified |
| embeddings | 63.51 | Qualified |
| classical | 62.10 | Qualified |
| graphify | 27.94 | Qualified |
| ensemble | Unavailable | Execution error; not qualified |
| entity-graph | Unavailable | Execution error; not qualified |

The [retained application/category comparison](../graphify-generation-004-001/comparison.md) remains unchanged. All 20 retained groups for this family were checked against that exact comparison. Entity Graph and Ensemble remain unqualified after their original execution errors, with unexercised hypotheses.

## Verification and remaining work

The source-bound application gate 052 passed 1,643 tests and 373 subtests at 90.5% coverage. The publication audit also verified gate 056 with the same totals. This publication changes no application, canonical skill, dataset or frozen runtime. Original native artifacts and reporting sources are digest-bound in the aggregate. All eight opportunity obligations, joint development replay, whole-bundle freeze, the all-500 comparison and independent acceptance remain unfinished. These are internal retrieval results; no generated-answer Overall, public leaderboard position or final promotion is assigned.

[Applications and categories](groups.md) · [CTA](cta.md) · [Full-precision aggregate](aggregate.json) · [E14 overview](../README.md)
