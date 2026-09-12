# EnterpriseRAG E14: Adaptive generation 9 retains its incumbent

Date: 2026-09-12. The qualified construction variant `{"expansion.association_weight": 0.0, "expansion.topic_weight": 0.0}` scored **65.12 nDCG@10 x100**, compared with **66.21** for the retained `retained-start`. The native owner records **2 consecutive evaluable misses** in `expansion-strength`. The mechanism remains open under the three-consecutive-miss rule.

The unchanged workload contains 120 stratified questions, 112 retrieval-eligible questions, 6,000 complete documents and eligible population weight 470. Consultation is frozen for this construction treatment.

| Metric (x100) | Retained incumbent | Candidate | Delta points |
| --- | --- | --- | --- |
| nDCG@10 | 66.21 | 65.12 | -1.09287 |
| Recall@10 | 74.02 | 72.58 | -1.44577 |
| MRR@10 | 67.37 | 66.43 | -0.94233 |
| Full-reference coverage@10 | 69.27 | 67.02 | -2.24956 |

At question level, **4 improve, 9 regress and 99 tie**; eight questions lack retrieval references. The frozen weights and size of each change determine the aggregate result. Displayed scores and differences are rounded independently from full precision.

## Opportunity accounting

This observation adds one proposal charge, bringing Adaptive to **28 / 100 claims**, including **8 new E14 claims**. The current mechanism is `expansion-strength`, round **2**, with **2 / 4** listed variants issued and **2 / 3** consecutive evaluable misses. The mechanism remains open under the three-consecutive-miss rule. The family retains its other declared opportunities, inherited five-round ceiling and remaining cap. Original identities and charges are preserved, with no retry or budget reset.

The report contains **11 cumulative original native records** and **one new observation**. All records have zero execution errors and zero retries. The complete captured history includes dominated candidates. Native normalization, owning receipt/progress and the common reconciler agree on qualification and retention. Reporting dispatched no native job.

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
