# EnterpriseRAG E14: Graphify improves to 63.72

Date: 2026-09-12. **Graphify's retained development nDCG@10 rises from 63.46 to 63.72**, a gain of **0.26547 points** on the 0–100 scale. The native owner qualified and retained `versioned-016` with `{"depth": 3}`. This is an observed development gain; statistical significance was not evaluated and the candidate is not promoted.

The fixed workload contains 120 stratified questions, 112 retrieval-eligible questions, 6,000 complete documents and eligible population weight 470. The builder remains frozen for this consultation treatment.

| Metric (x100) | Previous incumbent | New incumbent | Delta points |
| --- | --- | --- | --- |
| nDCG@10 | 63.46 | 63.72 | +0.26547 |
| Recall@10 | 80.99 | 81.79 | +0.79787 |
| MRR@10 | 60.25 | 60.45 | +0.19799 |
| Full-reference coverage@10 | 75.63 | 76.43 | +0.79787 |

At question level, **2 improve, 1 regress and 109 tie**; eight questions lack retrieval references. The frozen weights and the size of each change determine the aggregate result. Displayed scores and deltas are rounded independently from full precision.

## Search accounting and provenance

This is one new native observation and one new proposal charge. Graphify has **16 / 65 cumulative claims**, including **16 new E14 claims**. The improvement resets consecutive evaluable misses to **0 / 3** in `traversal-depth`, round **2**, with **3 / 6** declared variants issued. Earlier misses remain recorded. The same mechanism continues while it has unused variants, subject to the inherited three-miss rule, five-round ceiling and family cap.

The reconciled prefix contains **17 cumulative original native records** and **one new observation**, including dominated candidates. All have zero execution errors, zero retries, verified native locks and 252-file evaluated package commitments. The reporting operation dispatched no native job.

## Retained eight-family comparison

| Family | Retained nDCG@10 x100 | Qualification |
| --- | --- | --- |
| Legacy | 72.38 | Qualified |
| Turso | 72.38 | Qualified |
| Adaptive | 66.21 | Qualified |
| Embeddings | 63.51 | Qualified |
| Classical | 62.10 | Qualified |
| Graphify | 63.72 | Qualified |
| Ensemble | Unavailable | Execution error; not qualified |
| Entity Graph | Unavailable | Execution error; not qualified |

[The updated general comparison](comparison.md) replaces only Graphify; the other five qualified profiles and their 20 groups remain exactly unchanged. Entity Graph and Ensemble remain unavailable after their [original execution errors](../starting-execution-errors-001/README.md), with outstanding evolution opportunities. The [separate Ensemble construction candidate](../../candidates/ensemble-mention-automaton-transfer-001/README.md) has passed software checks but has no native first measurement. Inherited counts in the aggregate retain their registration meaning; prospective construction debits are recorded in that separate candidate report.

The [application heatmap](../application-heatmap-016/README.md) displays this exact retained comparison, including both unavailable strategies.

## Verification and remaining work

Application gate 053 passed 1,643 tests and 373 subtests with 90.5% total application coverage. This publication changes no application, canonical skill, dataset or frozen runtime. The original native artifacts and reporting sources are digest-bound. All eight opportunity obligations, joint development replay, one whole-bundle freeze, the all-500 comparison and independent acceptance remain unfinished. These retrieval scores are not generated-answer Overall scores or public leaderboard positions.

The publication audit also verified application gate 061: 1,697 tests, 373 subtests and 90.5% total application coverage. No tracked implementation changed after that gate.

[Paired applications/categories](groups.md) · [General comparison](comparison.md) · [CTA](cta.md) · [Full-precision aggregate](aggregate.json) · [E14 overview](../README.md)
