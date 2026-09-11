# EnterpriseRAG: stratified development, 120 questions

This dataset view separates the retained internal strategy comparison from
the latest incomplete continuation. The fixed workload uses **120 stratified
questions, 112 retrieval-eligible questions and 6,000 complete documents**.
The primary metric is frozen-category-weighted **nDCG@10 multiplied by 100**.

## Retained comparison

| Strategy | Retained score | Source |
| --- | ---: | --- |
| Legacy | 72.38 | Historical incumbent exactly reproduced by E14 |
| Turso | 72.08 | Historical incumbent exactly reproduced by E14 |
| Adaptive | 66.21 | Historical incumbent exactly reproduced by E14 |
| Embeddings | 63.51 | Historical reference exactly reproduced by E14 |
| Classical | 62.10 | Historical incumbent exactly reproduced by E14 |
| Graphify | 8.12 | Historical reference exactly reproduced by E14 |
| Entity Graph | Unavailable | E14 starting timeout; no qualified ranking |
| Ensemble | Unavailable | E14 starting memory failure; no qualified ranking |

Legacy has the highest retained score in this partial development comparison.
This does not establish a winner on the all-500 workload, on other datasets,
or on generated-answer quality. Exact evidence and opportunity limits are in
the [eight-family report](../evolution/e14/classical-starting-qualified-001/README.md#retained-eight-family-comparison).

The [consolidated six-family comparison](../evolution/e14/qualified-starts-comparison-001/README.md)
shows the retained scores for every application and question category, their
observed leaders and the corresponding native cost/time measurements. These
descriptive subgroup results do not select a candidate or evaluate a router.

## Latest continuation

The [new pending Turso and Adaptive variants](../evolution/e14/generation-001-pending-variants-001/README.md) scored **69.31** and **64.53**, retaining **72.08** and **66.21**. Both are qualified observations on this exact workload, with one evaluable miss each and zero new proposal charges. The retained dataset ranking is unchanged.

The [original Entity Graph and Ensemble starts](../evolution/e14/starting-execution-errors-001/README.md)
finished with execution errors: a 3,600-second timeout and a Docker out-of-memory
event under the fixed 6 GiB limit, respectively. Both stopped locally before
qualification. Their remaining evolution hypotheses are still outstanding;
the failures are not mutation quality misses or measured zero retrieval scores.

[E14](../evolution/e14/README.md) completes **six current starting
qualifications: Legacy, Turso, Adaptive, Embeddings, Classical and Graphify**.
Classical's two new jobs reproduce **55.04** for the reference and **62.10** for
the retained profile. Its recorded catalog stop and inherited charges remain
preserved. The other retained scores are unchanged. All ten native records
included in the six family reports are qualified and error-free. These
checkpoints establish no new champion. Turso, Adaptive and Graphify can continue
their inherited searches. The two failed family starts, their unexercised
hypotheses and the final all-eight comparison remain unresolved. Private
validation is unopened.

The [earlier E13 study](../evolution/e13/README.md) remains closed after its
cache phase-declaration controller stop. Its reference is reused under its
original job and staged-skill identity.

- [Classical results across nine applications and ten question categories](../evolution/e14/classical-starting-qualified-001/groups.md)
- [Classical native cost, time and quality](../evolution/e14/classical-starting-qualified-001/cta.md)
- [Latest machine-readable checkpoint](../evolution/e14/classical-starting-qualified-001/aggregate.json)
- [Preserved Embeddings application/category results](../evolution/e14/embeddings-starting-qualified-001/groups.md) and [CTA](../evolution/e14/embeddings-starting-qualified-001/cta.md)
- [Preserved Graphify application/category results](../evolution/e14/graphify-starting-qualified-001/groups.md) and [CTA](../evolution/e14/graphify-starting-qualified-001/cta.md)
- [Preserved Legacy application/category results](../evolution/e14/legacy-starting-qualified-001/groups.md) and [CTA](../evolution/e14/legacy-starting-qualified-001/cta.md)
- [Preserved Adaptive application/category results](../evolution/e14/adaptive-starting-qualified-001/groups.md) and [CTA](../evolution/e14/adaptive-starting-qualified-001/cta.md)
- [Preserved Turso application/category results](../evolution/e14/turso-starting-qualified-001/groups.md) and [CTA](../evolution/e14/turso-starting-qualified-001/cta.md)
- [Earlier five-family retained application/category matrix](../evolution/e8/retained-cross-family-002/README.md)

Keep this contract separate from the [full-corpus Classical 500-question run](enterprise-rag-classical-full-500.md),
the [internal Luna answer evaluation](../enterprise-classical-full/luna.md),
and the [historical comparisons across datasets](../README.md#historical-retrieval-comparisons).
No current public leaderboard rank is assigned by these development metrics.

[Report hub](../README.md) · [Family index](../../../docs/enterprise-family-report-index.md)
