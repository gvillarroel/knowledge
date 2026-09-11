# EnterpriseRAG E14: Turso improves to 72.38

Date: 2026-09-11. **Turso's retained development nDCG@10 rises from 72.13 to 72.38**, a gain of **0.24838 points** on the 0–100 scale. The native owner qualified and retained `versioned-007` with `{"engine": "bm25", "title_weight": 4.0}`. This is an observed development gain; statistical significance was not evaluated and the candidate is not promoted.

The fixed workload contains 120 stratified questions, 112 retrieval-eligible questions, 6,000 complete documents and eligible population weight 470. The builder remains frozen for this consultation treatment.

| Metric (x100) | Previous incumbent | New incumbent | Delta points |
| --- | --- | --- | --- |
| nDCG@10 | 72.13 | 72.38 | +0.24838 |
| Recall@10 | 82.11 | 81.99 | -0.11820 |
| MRR@10 | 71.06 | 71.51 | +0.45302 |
| Full-reference coverage@10 | 77.14 | 76.43 | -0.70922 |

At question level, **7 improve, 12 regress and 93 tie**; eight questions lack retrieval references. The frozen weights and the size of each change determine the aggregate result. Displayed scores and deltas are rounded independently from full precision.

## Search accounting and provenance

This is one new native observation and one new proposal charge. Turso has **9 / 55 cumulative claims**, including **7 new E14 claims**. The improvement resets consecutive evaluable misses to **0 / 3** in `title-weight`, round **1**, with **2 / 3** declared variants issued. Earlier misses remain recorded. The same mechanism continues while it has unused variants, subject to the inherited three-miss rule, five-round ceiling and family cap.

The reconciled prefix contains **10 cumulative original native records** and **one new observation**, including dominated candidates. All have zero execution errors, zero retries, verified native locks and 252-file evaluated package commitments. The reporting operation dispatched no native job.

## Retained eight-family comparison

| Family | Retained nDCG@10 x100 | Qualification |
| --- | --- | --- |
| Legacy | 72.38 | Qualified |
| Turso | 72.38 | Qualified |
| Adaptive | 66.21 | Qualified |
| Embeddings | 63.51 | Qualified |
| Classical | 62.10 | Qualified |
| Graphify | 27.90 | Qualified |
| Ensemble | Unavailable | Execution error; not qualified |
| Entity Graph | Unavailable | Execution error; not qualified |

[The updated general comparison](comparison.md) replaces only Turso; the other five qualified profiles and their 20 groups remain exactly unchanged. Entity Graph and Ensemble remain unavailable after their [original execution errors](../starting-execution-errors-001/README.md), with outstanding evolution opportunities. The [separate Ensemble construction candidate](../../candidates/ensemble-mention-automaton-transfer-001/README.md) has passed software checks but has no native first measurement. Inherited counts in the aggregate retain their registration meaning; prospective construction debits are recorded in that separate candidate report.

## Verification and remaining work

Legacy and Turso now share the highest retained overall nDCG. Their four aggregate retrieval metrics match at full precision in all 18 groups with retrieval references. The two groups without retrieval references remain unavailable for both. Their measured cost and time profiles are preserved separately in the CTA.

Application gate 053 passed 1,643 tests and 373 subtests with 90.5% total application coverage. This publication changes no application, canonical skill, dataset or frozen runtime. The original native artifacts and reporting sources are digest-bound. All eight opportunity obligations, joint development replay, one whole-bundle freeze, the all-500 comparison and independent acceptance remain unfinished. These retrieval scores are not generated-answer Overall scores or public leaderboard positions.

[Paired applications/categories](groups.md) · [General comparison](comparison.md) · [CTA](cta.md) · [Full-precision aggregate](aggregate.json) · [E14 overview](../README.md)
