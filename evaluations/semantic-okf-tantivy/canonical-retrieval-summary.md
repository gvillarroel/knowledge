# Tantivy Canonical Direct-Retrieval Summary

The native Tantivy BM25 candidate completed the canonical 40-question Top-10 comparison, an exact replay, and a pool-100 sensitivity run. All 120 queries completed without error and every returned evidence identity passed the independent validator.

| Route | All-40 Recall@10 | MRR@10 | nDCG@10 | Hard-10 Recall@10 | MRR@10 | nDCG@10 | Evidence validity | P95 ms |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Tantivy BM25 (experimental) | 80.74% | 93.75% | 81.05% | 92.17% | 90.00% | 80.54% | 100.00% | 90.92 |
| Classical BM25 (accepted reference) | 49.72% | 95.83% | 60.94% | 63.17% | 95.00% | 69.31% | 100.00% | 99.46 |
| Tantivy minus Classical | +31.02 pp | -2.08 pp | +20.12 pp | +29.00 pp | -5.00 pp | +11.22 pp | 0.00 pp | -8.54 |

## Gates

- Top-10 execution: 40/40 queries, zero errors, 400/400 valid evidence rows.
- Exact replay: identical ranked Top-10 results for all 40 questions.
- Pool-100: 40/40 queries, zero errors, 527/527 valid evidence rows; the ranked Top-10 prefix and Recall@10 remained 80.74%.
- Candidate state: experimental comparator; the eight-family Harbor registry is unchanged.

Tantivy materially improves retrieval coverage and nDCG over Classical BM25 in this direct diagnostic while slightly reducing MRR. Its measured P95 is also lower, but cross-family timing remains operational rather than an SLA comparison. Report the row; keep registry admission separate.
