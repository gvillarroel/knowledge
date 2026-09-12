# EnterpriseRAG E14: Turso generation 14 retains its incumbent

Date: 2026-09-12. The qualified consultation variant `{"b": 0.0, "engine": "bm25"}` scored **61.38 nDCG@10 x100**, compared with **72.38** for the retained `versioned-007`. The native owner records **2 consecutive evaluable misses** in `length-normalization`. The mechanism remains open under the three-consecutive-miss rule.

The unchanged workload contains 120 stratified questions, 112 retrieval-eligible questions, 6,000 complete documents and eligible population weight 470. Construction is frozen for this consultation treatment.

| Metric (x100) | Retained incumbent | Candidate | Delta points |
| --- | --- | --- | --- |
| nDCG@10 | 72.38 | 61.38 | -10.99527 |
| Recall@10 | 81.99 | 69.95 | -12.04319 |
| MRR@10 | 71.51 | 61.88 | -9.62853 |
| Full-reference coverage@10 | 76.43 | 64.94 | -11.49158 |

At question level, **8 improve, 44 regress and 60 tie**; eight questions lack retrieval references. The frozen weights and size of each change determine the aggregate result. Displayed scores and differences are rounded independently from full precision.

## Opportunity accounting

This observation adds one proposal charge, bringing Turso to **15 / 55 claims**, including **13 new E14 claims**. The current mechanism is `length-normalization`, round **2**, with **2 / 4** listed variants issued and **2 / 3** consecutive evaluable misses. The mechanism remains open under the three-consecutive-miss rule. The family retains its other declared opportunities, inherited five-round ceiling and remaining cap. Original identities and charges are preserved, with no retry or budget reset.

The report contains **16 cumulative original native records** and **one new observation**. All records have zero execution errors and zero retries. The complete captured history includes dominated candidates. Native normalization, owning receipt/progress and the common reconciler agree on qualification and retention. Reporting dispatched no native job.

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

The source-bound application gate 052 passed 1,643 tests and 373 subtests at 90.5% coverage. The publication audit also verified gate 056 with the same totals. This publication changes no application, canonical skill, dataset or frozen runtime. Original native artifacts and reporting sources are digest-bound in the aggregate. The remaining family qualification and opportunity obligations, joint development replay, whole-bundle freeze, the all-500 comparison and independent acceptance remain unfinished. These are internal retrieval results; no generated-answer Overall, public leaderboard position or final promotion is assigned.

[Applications and categories](groups.md) · [CTA](cta.md) · [Full-precision aggregate](aggregate.json) · [E14 overview](../README.md)
