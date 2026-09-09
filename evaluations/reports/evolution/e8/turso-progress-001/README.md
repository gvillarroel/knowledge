# E8 development: turso

Snapshot: 2026-09-09T05:58:49.361467+00:00.

The observed candidate is `continuation-001`. Its weighted nDCG@10 changed by +26.65 percentage points versus baseline and +26.65 versus the previous incumbent `baseline`.

Recorded retention: `continuation-001`. Consecutive misses after this opportunity: 0. These decisions were replayed from the complete cumulative prefix.

| Candidate | Weighted nDCG@10 | Recall@10 | MRR@10 | Full evidence@10 | Historical job |
| --- | ---: | ---: | ---: | ---: | --- |
| baseline | 45.43 | 54.48 | 46.88 | 48.28 | False |
| continuation-001 | 72.08 | 82.51 | 71.61 | 77.26 | False |

Quality columns are percentages. The primary route remains `lexical-sql`. The comparison uses 120 exposed development questions, 112 eligible cases and category weights totaling 470, on 6,000 reference-enriched complete documents. Eight questions without references have no retrieval score.

Mechanism: `bm25-saturation`. Treatment: consultation.

```json
{
  "engine": "bm25",
  "k1": 1.2
}
```

This is an intermediate retrieval measurement. It does not establish all-500 performance, answer Overall, an official public rank, final selection, acceptance or installation. Diagnostic routes and application subgroups do not change retention. The separate native diagnostic reward threshold is 0.8.

[Applications and categories](groups.md) · [All diagnostic routes](routes.md) · [Cost, time and quality](cta.md) · [Exact aggregate and evidence hashes](aggregate.json) · [Campaign](../README.md)

The registered `lexical-sql` route keeps its identifier across two execution modes. The original empty-profile baseline ranks parameterized SQL substring presence. A nonempty candidate profile loads canonical records from Turso and ranks normalized tokens with BM25 in memory. The first gain therefore includes an algorithm and token-matching change; later changes must be assessed against their actual BM25 parent. No SQL BM25 index or database schema change is implied.

The [generated-expert delivery audit](../../e7/turso-generated-expert-001/README.md) also distinguishes this measured consultation wrapper from the portable expert default. A profile gain does not prove automatic inheritance by generated experts.
