# EnterpriseRAG E14: Adaptive reaches three normalization misses

Date: 2026-09-11. **The qualified construction variant `bm25.b=0.5` scored 65.78 nDCG@10 x100, below the retained 66.21.** The native owner keeps `retained-start` and records the third consecutive unique evaluable miss in the length-normalization mechanism. This boundary requires the next search step to change mechanism; it does not exhaust Adaptive's other opportunities.

The unchanged workload contains 120 stratified questions, 112 retrieval-eligible questions, 6,000 complete documents and eligible population weight 470. This is a builder-plan treatment with consultation frozen. All five cumulative original native observations completed without execution errors or retries.

| Metric (x100) | Retained incumbent | b=0.5 candidate | Delta points |
| --- | --- | --- | --- |
| nDCG@10 | 66.21 | 65.78 | -0.43085 |
| Recall@10 | 74.02 | 73.92 | -0.10638 |
| MRR@10 | 67.37 | 66.38 | -0.99067 |
| Full-reference coverage@10 | 69.27 | 69.27 | +0.00000 |

At question level, **13 improve, 20 regress and 79 tie**; eight further questions have no retrieval references. The frozen population weights and size of each change determine the aggregate result. Rounded display values and deltas come from full precision.

## Opportunity accounting

The three observations in this mechanism were `b=0.25` at **64.53**, `b=0.0` at **62.31**, and now `b=0.5` at **65.78**. All fell below **66.21**. The already charged pending `b=0.25` observation added no proposal charge; each subsequent variant added one. Adaptive now accounts for **22 / 100 claims**, including **two new E14 claims**, with three consecutive misses in round two. Three of four listed variants have been issued. The three-miss rule closes this mechanism's current turn before exhausting that list. The family retains other declared mechanisms, the inherited five-round ceiling and its remaining cap. No identity is retried or recharged.

The complete five-job inventory preserves both starting roles and every subsequent observation, including dominated candidates. Native normalization, the owning receipt/progress and the common reconciler agree on qualification and retention. Reporting checked original job locks, trial results, skill provenance and output routes; it dispatched no new job.

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

The [current application/category comparison](../turso-generation-002-001/comparison.md) remains unchanged. Entity Graph and Ensemble have unavailable quality after their original execution errors and still have unexercised hypotheses.

## Verification and remaining work

Application gate 052 remains current: 1,643 tests, 373 subtests and 90.5% total application coverage. No application, canonical skill, dataset or frozen runtime source changed. The exact observations and reporting sources are digest-bound in the aggregate. All eight opportunity obligations, joint development replay, whole-bundle freeze, the all-500 comparison and independent acceptance remain required. These are internal retrieval results; no generated-answer Overall, public leaderboard position or final skill promotion is assigned.

[Applications and categories](groups.md) · [CTA](cta.md) · [Full-precision aggregate](aggregate.json) · [E14 overview](../README.md)
