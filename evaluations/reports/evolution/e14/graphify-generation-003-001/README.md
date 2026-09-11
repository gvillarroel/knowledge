# EnterpriseRAG E14: Graphify improves to 27.90

Date: 2026-09-11. **Graphify's retained development nDCG@10 rises from 8.12 to 27.90**, a gain of **19.78675 points** on the 0–100 scale. The native owner qualified and retained `versioned-003` with `{"depth": 3}`. This is an observed development gain; statistical significance was not evaluated and the candidate is not promoted.

The fixed workload contains 120 stratified questions, 112 retrieval-eligible questions, 6,000 complete documents and eligible population weight 470. The builder remains frozen for this consultation treatment.

| Metric (x100) | Previous incumbent | New incumbent | Delta points |
| --- | --- | --- | --- |
| nDCG@10 | 8.12 | 27.90 | +19.78675 |
| Recall@10 | 14.85 | 35.42 | +20.57304 |
| MRR@10 | 6.71 | 29.03 | +22.32217 |
| Full-reference coverage@10 | 12.53 | 31.49 | +18.96055 |

At question level, **32 improve, 10 regress and 70 tie**; eight questions lack retrieval references. The frozen weights and the size of each change determine the aggregate result. Displayed scores and deltas are rounded independently from full precision.

## Search accounting and provenance

This is one new native observation and one new proposal charge. Graphify has **3 / 65 cumulative claims**, including **3 new E14 claims**. The improvement resets consecutive evaluable misses to **0 / 3** in `traversal-depth`, round **1**, with **3 / 6** declared variants issued. Earlier misses remain recorded. The same mechanism continues while it has unused variants, subject to the inherited three-miss rule, five-round ceiling and family cap.

The reconciled prefix contains **4 cumulative original native records** and **one new observation**, including dominated candidates. All have zero execution errors, zero retries, verified native locks and 252-file evaluated package commitments. The reporting operation dispatched no native job.

## Retained eight-family comparison

| Family | Retained nDCG@10 x100 | Qualification |
| --- | --- | --- |
| Legacy | 72.38 | Qualified |
| Turso | 72.13 | Qualified |
| Adaptive | 66.21 | Qualified |
| Embeddings | 63.51 | Qualified |
| Classical | 62.10 | Qualified |
| Graphify | 27.90 | Qualified |
| Ensemble | Unavailable | Execution error; not qualified |
| Entity Graph | Unavailable | Execution error; not qualified |

[The updated general comparison](comparison.md) replaces only Graphify; the other five qualified profiles and their 20 groups remain exactly unchanged. Entity Graph and Ensemble remain unavailable after their [original execution errors](../starting-execution-errors-001/README.md), with outstanding evolution opportunities. The [separate Ensemble construction candidate](../../candidates/ensemble-mention-automaton-transfer-001/README.md) has passed software checks but has no native first measurement. Inherited counts in the aggregate retain their registration meaning; prospective construction debits are recorded in that separate candidate report.

## Verification and remaining work

Application gate 053 passed 1,643 tests and 373 subtests with 90.5% total application coverage. This publication changes no application, canonical skill, dataset or frozen runtime. The original native artifacts and reporting sources are digest-bound. All eight opportunity obligations, joint development replay, one whole-bundle freeze, the all-500 comparison and independent acceptance remain unfinished. These retrieval scores are not generated-answer Overall scores or public leaderboard positions.

[Paired applications/categories](groups.md) · [General comparison](comparison.md) · [CTA](cta.md) · [Full-precision aggregate](aggregate.json) · [E14 overview](../README.md)
