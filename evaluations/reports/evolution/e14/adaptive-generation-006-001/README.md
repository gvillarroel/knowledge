# EnterpriseRAG E14: Adaptive generation 6 retains its incumbent

Date: 2026-09-11. The qualified construction variant `{"bm25.title_weight": 4.0}` scored **54.79 nDCG@10 x100**, compared with **66.21** for the retained `retained-start`. The native owner records **1 consecutive evaluable miss** in `title-weight`. The mechanism remains open under the three-consecutive-miss rule.

The unchanged workload contains 120 stratified questions, 112 retrieval-eligible questions, 6,000 complete documents and eligible population weight 470. Consultation is frozen for this construction treatment.

| Metric (x100) | Retained incumbent | Candidate | Delta points |
| --- | --- | --- | --- |
| nDCG@10 | 66.21 | 54.79 | -11.42222 |
| Recall@10 | 74.02 | 66.37 | -7.64923 |
| MRR@10 | 67.37 | 54.19 | -13.17741 |
| Full-reference coverage@10 | 69.27 | 60.25 | -9.02039 |

At question level, **6 improve, 45 regress and 61 tie**; eight questions lack retrieval references. The frozen weights and size of each change determine the aggregate result. Displayed scores and differences are rounded independently from full precision.

## Opportunity accounting

This observation adds one proposal charge, bringing Adaptive to **25 / 100 claims**, including **5 new E14 claims**. The current mechanism is `title-weight`, round **2**, with **1 / 3** listed variants issued and **1 / 3** consecutive evaluable misses. The mechanism remains open under the three-consecutive-miss rule. The family retains its other declared opportunities, inherited five-round ceiling and remaining cap. Original identities and charges are preserved, with no retry or budget reset.

Before this generation, the owner skipped the already seen `bm25.k1=3.0` profile and closed `bm25-saturation` for `catalog-exhausted`, with two evaluable misses and zero unused variants. The skipped duplicate was not rerun or charged as a new proposal. This transition exhausted the declared unique variants; it does not record or imply a third failed evaluation. Generation 6 starts the separate `title-weight` mechanism.

The report contains **8 cumulative original native records** and **one new observation**. All records have zero execution errors and zero retries. The complete captured history includes dominated candidates. Native normalization, owning receipt/progress and the common reconciler agree on qualification and retention. Reporting dispatched no native job.

## Retained eight-family comparison

| Family | Retained nDCG@10 x100 | Qualification |
| --- | --- | --- |
| legacy | 72.38 | Qualified |
| turso | 72.13 | Qualified |
| adaptive | 66.21 | Qualified |
| embeddings | 63.51 | Qualified |
| classical | 62.10 | Qualified |
| graphify | 27.90 | Qualified |
| ensemble | Unavailable | Execution error; not qualified |
| entity-graph | Unavailable | Execution error; not qualified |

The [retained application/category comparison](../graphify-generation-003-001/comparison.md) remains unchanged. All 20 retained groups for this family were checked against that exact comparison. Entity Graph and Ensemble remain unqualified after their original execution errors, with unexercised hypotheses.

## Verification and remaining work

Application gate 052 remains current: 1,643 tests, 373 subtests and 90.5% coverage. This publication changes no application, canonical skill, dataset or frozen runtime. Original native artifacts and reporting sources are digest-bound in the aggregate. All eight opportunity obligations, joint development replay, whole-bundle freeze, the all-500 comparison and independent acceptance remain unfinished. These are internal retrieval results; no generated-answer Overall, public leaderboard position or final promotion is assigned.

[Applications and categories](groups.md) · [CTA](cta.md) · [Full-precision aggregate](aggregate.json) · [E14 overview](../README.md)
