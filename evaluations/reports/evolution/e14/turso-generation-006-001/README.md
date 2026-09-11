# EnterpriseRAG E14: Turso generation 6 retains its incumbent

Date: 2026-09-11. The qualified consultation variant `{"b": 0.5, "engine": "bm25"}` scored **70.44 nDCG@10 x100**, compared with **72.13** for the retained `versioned-001`. The native owner records **3 consecutive evaluable misses** in `length-normalization`. The third consecutive miss requires the next step to change mechanism.

The unchanged workload contains 120 stratified questions, 112 retrieval-eligible questions, 6,000 complete documents and eligible population weight 470. Construction is frozen for this consultation treatment.

| Metric (x100) | Retained incumbent | Candidate | Delta points |
| --- | --- | --- | --- |
| nDCG@10 | 72.13 | 70.44 | -1.68418 |
| Recall@10 | 82.11 | 80.09 | -2.02029 |
| MRR@10 | 71.06 | 69.59 | -1.46270 |
| Full-reference coverage@10 | 77.14 | 74.52 | -2.61525 |

At question level, **7 improve, 23 regress and 82 tie**; eight questions lack retrieval references. The frozen weights and size of each change determine the aggregate result. Displayed scores and differences are rounded independently from full precision.

## Opportunity accounting

This observation adds one proposal charge, bringing Turso to **7 / 55 claims**, including **5 new E14 claims**. The current mechanism is `length-normalization`, round **1**, with **3 / 4** listed variants issued and **3 / 3** consecutive evaluable misses. The third consecutive miss requires the next step to change mechanism. The family retains its other declared opportunities, inherited five-round ceiling and remaining cap. Original identities and charges are preserved, with no retry or budget reset.

The report contains **8 cumulative original native records** and **one new observation**. All records have zero execution errors and zero retries. The complete captured history includes dominated candidates. Native normalization, owning receipt/progress and the common reconciler agree on qualification and retention. Reporting dispatched no native job.

## Retained eight-family comparison

| Family | Retained nDCG@10 x100 | Qualification |
| --- | --- | --- |
| legacy | 72.38 | Qualified |
| turso | 72.13 | Qualified |
| adaptive | 66.21 | Qualified |
| embeddings | 63.51 | Qualified |
| classical | 62.10 | Qualified |
| graphify | 8.12 | Qualified |
| ensemble | Unavailable | Execution error; not qualified |
| entity-graph | Unavailable | Execution error; not qualified |

The [retained application/category comparison](../turso-generation-002-001/comparison.md) remains unchanged. All 20 retained groups for this family were checked against that exact comparison. Entity Graph and Ensemble remain unqualified after their original execution errors, with unexercised hypotheses.

## Verification and remaining work

Application gate 052 remains current: 1,643 tests, 373 subtests and 90.5% coverage. This publication changes no application, canonical skill, dataset or frozen runtime. Original native artifacts and reporting sources are digest-bound in the aggregate. All eight opportunity obligations, joint development replay, whole-bundle freeze, the all-500 comparison and independent acceptance remain unfinished. These are internal retrieval results; no generated-answer Overall, public leaderboard position or final promotion is assigned.

[Applications and categories](groups.md) · [CTA](cta.md) · [Full-precision aggregate](aggregate.json) · [E14 overview](../README.md)
