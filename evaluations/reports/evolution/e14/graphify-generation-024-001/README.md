# EnterpriseRAG E14: Graphify generation 24 retains its incumbent

Date: 2026-09-12. The qualified consultation variant `{"lexical_weight": 1.0, "rrf_k": 60}` scored **52.42 nDCG@10 x100**, compared with **63.72** for the retained `versioned-016`. The native owner records **3 consecutive evaluable misses** in `fusion-rank-decay`. The third consecutive miss requires the next step to change mechanism.

The unchanged workload contains 120 stratified questions, 112 retrieval-eligible questions, 6,000 complete documents and eligible population weight 470. Construction is frozen for this consultation treatment.

| Metric (x100) | Retained incumbent | Candidate | Delta points |
| --- | --- | --- | --- |
| nDCG@10 | 63.72 | 52.42 | -11.30029 |
| Recall@10 | 81.79 | 77.21 | -4.57299 |
| MRR@10 | 60.45 | 47.98 | -12.46341 |
| Full-reference coverage@10 | 76.43 | 70.33 | -6.09486 |

At question level, **7 improve, 65 regress and 40 tie**; eight questions lack retrieval references. The frozen weights and size of each change determine the aggregate result. Displayed scores and differences are rounded independently from full precision.

## Opportunity accounting

This observation adds one proposal charge, bringing Graphify to **24 / 65 claims**, including **24 new E14 claims**. The current mechanism is `fusion-rank-decay`, round **2**, with **3 / 3** listed variants issued and **3 / 3** consecutive evaluable misses. The third consecutive miss requires the next step to change mechanism. The family retains its other declared opportunities, inherited five-round ceiling and remaining cap. Original identities and charges are preserved, with no retry or budget reset.

After this observation, the unchanged owner skipped only already-consumed profile digests, recorded both remaining Graphify mechanisms as catalog-exhausted, and closed round **3** with `full-round-without-improvement`. It issued no Graphify generation 25 claim. The overall controller then terminated fail-closed because the required Entity Graph and Ensemble starts remained unqualified. That later coordination state does not alter the retained score or claim accounting in this observation, and it does not establish all-family completion.

The report contains **25 cumulative original native records** and **one new observation**. All records have zero execution errors and zero retries. The complete captured history includes dominated candidates. Native normalization, owning receipt/progress and the common reconciler agree on qualification and retention. Reporting dispatched no native job.

## Retained eight-family comparison

| Family | Retained nDCG@10 x100 | Qualification |
| --- | --- | --- |
| legacy | 72.38 | Qualified |
| turso | 72.38 | Qualified |
| adaptive | 66.21 | Qualified |
| embeddings | 63.51 | Qualified |
| classical | 62.10 | Qualified |
| graphify | 63.72 | Qualified |
| ensemble | Unavailable | Execution error; not qualified |
| entity-graph | Unavailable | Execution error; not qualified |

The [retained application/category comparison](../graphify-generation-016-001/comparison.md) remains unchanged. All 20 retained groups for this family were checked against that exact comparison. Entity Graph and Ensemble remain unqualified after their original execution errors, with unexercised hypotheses.

## Verification and remaining work

Application gate 061 remains current: 1,697 tests, 373 subtests and 90.5% coverage. The publication audit also verified application gate 061. This publication changes no application, canonical skill, dataset or frozen runtime. Original native artifacts and reporting sources are digest-bound in the aggregate. All eight opportunity obligations, joint development replay, whole-bundle freeze, the all-500 comparison and independent acceptance remain unfinished. These are internal retrieval results; no generated-answer Overall, public leaderboard position or final promotion is assigned.

[Applications and categories](groups.md) · [CTA](cta.md) · [Full-precision aggregate](aggregate.json) · [E14 overview](../README.md)
