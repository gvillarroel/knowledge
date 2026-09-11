# EnterpriseRAG: stratified development, 120 questions

This dataset view separates the retained internal strategy comparison from
the latest incomplete continuation. The fixed workload uses **120 stratified
questions, 112 retrieval-eligible questions and 6,000 complete documents**.
The primary metric is frozen-category-weighted **nDCG@10 multiplied by 100**.

## Retained comparison

| Strategy | Retained score | Source |
| --- | ---: | --- |
| Legacy | 72.38 | Historical reviewed development result |
| Turso | 72.08 | Historical incumbent exactly reproduced by E14 |
| Adaptive | 66.21 | Historical reviewed development result |
| Embeddings | 63.51 | Historical reviewed development result |
| Classical | 62.10 | Historical reviewed development result |
| Graphify | 8.12 | Historical reviewed development result |
| Entity Graph | Unavailable | No qualified ranking |
| Ensemble | Unavailable | No qualified ranking |

Legacy has the highest retained score in this partial development comparison.
This does not establish a winner on the all-500 workload, on other datasets,
or on generated-answer quality. Exact evidence and opportunity limits are in
the [eight-family report](../evolution/e14/turso-starting-qualified-001/README.md#retained-eight-family-comparison).

## Latest continuation

[E14](../evolution/e14/README.md) completes **Turso's starting qualification**.
One new retained-profile trial exactly reproduces **72.08**, paired with the
preserved original E13 reference at **45.43**. Both records are qualified and
error-free; only the retained-profile execution is new. This checkpoint
establishes no new champion. One of eight current family qualifications is
complete; five inherited searches and the final all-eight comparison remain
unfinished. Private validation is unopened.

The [earlier E13 study](../evolution/e13/README.md) remains closed after its
cache phase-declaration controller stop. Its reference is reused under its
original job and staged-skill identity.

- [Nine applications and ten question categories](../evolution/e14/turso-starting-qualified-001/groups.md)
- [Native cost, time and quality](../evolution/e14/turso-starting-qualified-001/cta.md)
- [Machine-readable checkpoint](../evolution/e14/turso-starting-qualified-001/aggregate.json)
- [Earlier five-family retained application/category matrix](../evolution/e8/retained-cross-family-002/README.md)

Keep this contract separate from the [full-corpus Classical 500-question run](enterprise-rag-classical-full-500.md),
the [internal Luna answer evaluation](../enterprise-classical-full/luna.md),
and the [historical comparisons across datasets](../README.md#historical-retrieval-comparisons).
No current public leaderboard rank is assigned by these development metrics.

[Report hub](../README.md) · [Family index](../../../docs/enterprise-family-report-index.md)
