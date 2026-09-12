# EnterpriseRAG E14: Graphify generation 12 retains its incumbent

Date: 2026-09-12. The qualified consultation variant `{"lexical_weight": 1.0, "rrf_k": 20}` scored **54.45 nDCG@10 x100**, compared with **63.46** for the retained `versioned-010`. The native owner records **2 consecutive evaluable misses** in `fusion-rank-decay`. The mechanism remains open under the three-consecutive-miss rule.

The unchanged workload contains 120 stratified questions, 112 retrieval-eligible questions, 6,000 complete documents and eligible population weight 470. Construction is frozen for this consultation treatment.

| Metric (x100) | Retained incumbent | Candidate | Delta points |
| --- | --- | --- | --- |
| nDCG@10 | 63.46 | 54.45 | -9.00653 |
| Recall@10 | 80.99 | 77.00 | -3.98493 |
| MRR@10 | 60.25 | 50.37 | -9.88351 |
| Full-reference coverage@10 | 75.63 | 70.25 | -5.38564 |

At question level, **5 improve, 59 regress and 48 tie**; eight questions lack retrieval references. The frozen weights and size of each change determine the aggregate result. Displayed scores and differences are rounded independently from full precision.

## Opportunity accounting

This observation adds one proposal charge, bringing Graphify to **12 / 65 claims**, including **12 new E14 claims**. The current mechanism is `fusion-rank-decay`, round **1**, with **2 / 3** listed variants issued and **2 / 3** consecutive evaluable misses. The mechanism remains open under the three-consecutive-miss rule. The family retains its other declared opportunities, inherited five-round ceiling and remaining cap. Original identities and charges are preserved, with no retry or budget reset.

The report contains **13 cumulative original native records** and **one new observation**. All records have zero execution errors and zero retries. The complete captured history includes dominated candidates. Native normalization, owning receipt/progress and the common reconciler agree on qualification and retention. Reporting dispatched no native job.

## Retained eight-family comparison

| Family | Retained nDCG@10 x100 | Qualification |
| --- | --- | --- |
| legacy | 72.38 | Qualified |
| turso | 72.38 | Qualified |
| adaptive | 66.21 | Qualified |
| embeddings | 63.51 | Qualified |
| classical | 62.10 | Qualified |
| graphify | 63.46 | Qualified |
| ensemble | Unavailable | Execution error; not qualified |
| entity-graph | Unavailable | Execution error; not qualified |

The [retained application/category comparison](../graphify-generation-010-001/comparison.md) remains unchanged. All 20 retained groups for this family were checked against that exact comparison. Entity Graph and Ensemble remain unqualified after their original execution errors, with unexercised hypotheses.

## Verification and remaining work

Application gate 052 remains current: 1,643 tests, 373 subtests and 90.5% coverage. This publication changes no application, canonical skill, dataset or frozen runtime. Original native artifacts and reporting sources are digest-bound in the aggregate. All eight opportunity obligations, joint development replay, whole-bundle freeze, the all-500 comparison and independent acceptance remain unfinished. These are internal retrieval results; no generated-answer Overall, public leaderboard position or final promotion is assigned.

The publication audit also verified application gate 061: **1,697 tests and 373 subtests passed, with 90.5% total application coverage**. The artifact-only reporter normalized all thirteen completed native records through the pinned Harbor 0.18.0 environment. Reporting made no native job, agent, model or retrieval call and did not change any measured result.

[Applications and categories](groups.md) · [CTA](cta.md) · [Full-precision aggregate](aggregate.json) · [E14 overview](../README.md)
