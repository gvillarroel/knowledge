# E8 development: classical

Snapshot: 2026-09-09T09:48:49.837741+00:00.

The observed candidate is `continuation-008`. Its weighted nDCG@10 changed by +5.85 percentage points versus baseline and -1.21 versus the previous incumbent `continuation-002`.

Recorded retention: `continuation-002`. Consecutive misses after this opportunity: 1. These decisions were replayed from the complete cumulative prefix.

| Candidate | Weighted nDCG@10 | Recall@10 | MRR@10 | Full evidence@10 | Historical job |
| --- | ---: | ---: | ---: | ---: | --- |
| baseline | 55.04 | 57.08 | 58.94 | 50.07 | True |
| continuation-002 | 62.10 | 64.17 | 66.38 | 57.82 | False |
| continuation-008 | 60.89 | 62.96 | 65.02 | 56.99 | False |

Quality columns are percentages. The primary route remains `fusion`. The comparison uses 120 exposed development questions, 112 eligible cases and category weights totaling 470, on 6,000 reference-enriched complete documents. Eight questions without references have no retrieval score.

Mechanism: `length-normalization`. Treatment: construction.

```json
{
  "bm25.b": 0.25
}
```

This is an intermediate retrieval measurement. It does not establish all-500 performance, answer Overall, an official public rank, final selection, acceptance or installation. Diagnostic routes and application subgroups do not change retention. The separate native diagnostic reward threshold is 0.8.

[Applications and categories](groups.md) · [All diagnostic routes](routes.md) · [Cost, time and quality](cta.md) · [Exact aggregate and evidence hashes](aggregate.json) · [Campaign](../README.md)
