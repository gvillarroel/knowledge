# EnterpriseRAG E14: Turso improves to 72.13 with BM25 k1=2.0

Date: 2026-09-11. **Turso's retained development nDCG@10 rises from 72.08 to 72.13**, a gain of **0.04949 points** on the 0–100 scale. The native owner qualified and retained `versioned-001`. This is a small observed primary-metric gain; statistical significance was not evaluated and the candidate is not promoted.

The fixed workload is 120 stratified questions, 112 retrieval-eligible questions, 6,000 complete documents and eligible population weight 470. This consultation treatment changes BM25 `k1` from 1.2 to 2.0 while the builder remains frozen.

| Metric (x100) | Previous incumbent | New incumbent | Delta points |
| --- | --- | --- | --- |
| nDCG@10 | 72.08 | 72.13 | +0.04949 |
| Recall@10 | 82.51 | 82.11 | -0.39770 |
| MRR@10 | 71.61 | 71.06 | -0.55128 |
| Full-reference coverage@10 | 77.26 | 77.14 | -0.12190 |

The primary nDCG metric improves while recall, MRR and complete-reference coverage fall slightly. At question level, **18 improve, 12 regress and 82 tie**; eight more questions lack retrieval references. Frozen population weights determine aggregate scores. Displayed values and deltas are rounded independently from full precision.

## Search accounting and provenance

This is one new native observation and one new proposal claim. Turso now has **3 / 55 cumulative claims**, including the two inherited claims. The observed improvement resets the current mechanism's consecutive evaluable misses to zero. Its three-miss rule, five-round ceiling and family cap remain in force. The earlier `k1=0.6` miss remains recorded.

The reconciled Turso prefix contains four completed native records: the exact original E13 reference and three E14 records. All have zero execution errors, zero retries, validated native locks and 252-file evaluated package commitments. The report operation dispatched no native job. The g1 report and its already-consumed pending identity remain unchanged.

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

Legacy remains first in this internal development comparison; Turso remains second. [The updated six-family view](comparison.md) shows the highest retained scores by application and category. Entity Graph and Ensemble remain unavailable after their [original execution errors](../starting-execution-errors-001/README.md), with outstanding evolution hypotheses.

## Verification and remaining work

Current application gate 052 passed 1,643 tests and 373 subtests with 90.5% total application coverage. This report copies reconciled development evidence and does not change application code, skill packages, datasets or private gates. All eight opportunity obligations, paired joint replay, one whole-bundle freeze, the all-500 comparison and independent acceptance remain required. These retrieval numbers are not answer-quality scores or public leaderboard ranks.

[Turso applications and categories](groups.md) · [Updated six-family comparison](comparison.md) · [CTA](cta.md) · [Full-precision aggregate](aggregate.json) · [E14 overview](../README.md)
