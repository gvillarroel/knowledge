# EnterpriseRAG: stratified development, 120 questions

This view covers **120 stratified development questions, 112 retrieval-eligible
questions and 6,000 complete documents**. Scores are frozen-category-weighted
**nDCG@10 multiplied by 100**. The eligible population weight is 470.

## Retained comparison

Published comparison through Graphify generation 7, verified on 2026-09-12.

| Strategy | Retained score | Qualified source |
| --- | ---: | --- |
| Legacy | 72.38 | [E14 reproduced incumbent](../evolution/e14/legacy-starting-qualified-001/README.md) |
| Turso | 72.38 | [E14 generation-eight gain](../evolution/e14/turso-generation-008-001/README.md) |
| Adaptive | 66.21 | [E14 reproduced incumbent](../evolution/e14/adaptive-starting-qualified-001/README.md) |
| Embeddings | 63.51 | [E14 reproduced reference](../evolution/e14/embeddings-starting-qualified-001/README.md) |
| Classical | 62.10 | [E14 reproduced incumbent](../evolution/e14/classical-starting-qualified-001/README.md) |
| Graphify | 34.16 | [E14 generation-seven gain](../evolution/e14/graphify-generation-007-001/README.md) |
| Entity Graph | Unavailable | [E14 starting timeout](../evolution/e14/starting-execution-errors-001/README.md) |
| Ensemble | Unavailable | [E14 starting memory failure](../evolution/e14/starting-execution-errors-001/README.md) |

Legacy and Turso share the highest retained score in this development
comparison. Graphify's latest measured gain is **27.94 to 34.16**: 28 questions
improve, one regresses, 83 tie and eight lack retrieval references.
[The full-precision aggregate](../evolution/e14/graphify-generation-007-001/aggregate.json)
binds the original results and the unchanged metrics of the other families.

## Current evolution status

Snapshot through published **Graphify generation 7, Turso generation 15 and
Adaptive generation 10**, verified on 2026-09-12. **Six of eight families have
qualified retrieval references; five have recorded catalog stops.** Legacy,
Turso, Adaptive, Embeddings and Classical have stopped their finite catalogs.
Graphify remains open; Ensemble and Entity Graph still need valid full-workload
evidence. Adaptive and Classical each retain one unavailable historical
hypothesis, so catalog closure does not imply complete measurement coverage.

The [verified catalog inventory](../evolution/e14/opportunity-accounting-002/README.md)
provides the terminal-state evidence and limitations. Its fixed 03:39 UTC
snapshot predates Graphify's latest gain; use the comparison above for the
retained scores. Claims in each historical observation describe that
observation's completion, not a live reservation count.

The remaining work includes valid qualification and remaining opportunities
for the open families, the paired joint development replay, one whole-bundle
freeze, the all-500 comparison and independent acceptance. Validation remains
sealed until the selected candidate is frozen.

## Applications, categories and CTA

The [general application/category comparison](../evolution/e14/graphify-generation-007-001/comparison.md)
covers nine overlapping application cohorts. Embeddings leads Confluence,
GitHub and Slack; Classical leads Fireflies and Linear; Legacy and Turso share
the highest values in Gmail, Google Drive, HubSpot and Jira. Adaptive leads
the completeness category. These are descriptive subgroup results.

Use [Graphify's paired groups](../evolution/e14/graphify-generation-007-001/groups.md)
for its observed changes and [the retained-family CTA](../evolution/e14/graphify-generation-007-001/cta.md)
for native job/build time, query latency, knowledge size and reported provider
cost. Host and orchestration costs are unpriced.

## Measurement boundaries

These development retrieval metrics do not establish all-500 results,
generated-answer quality, statistical significance, canonical promotion or a
public leaderboard position. The [Classical 500-question run](enterprise-rag-classical-full-500.md),
[internal Luna answer evaluation](../enterprise-classical-full/luna.md) and
[comparisons across datasets](../README.md#historical-retrieval-comparisons)
retain their own workload and scoring contracts.

## Observation history

The entries below preserve the state at each observation, newest first.
Their scores, proposal counts and open-mechanism descriptions are historical.

[Graphify generation 7](../evolution/e14/graphify-generation-007-001/README.md): `{"lexical_weight": 0.5}` raises retained nDCG from **27.94 to 34.16**, resets consecutive evaluable misses to **0 / 3**, and brings the family to **7 / 65 claims**. **[Latest general application/category comparison](../evolution/e14/graphify-generation-007-001/comparison.md)** · [Paired groups](../evolution/e14/graphify-generation-007-001/groups.md) · [CTA](../evolution/e14/graphify-generation-007-001/cta.md).

[Turso generation 15](../evolution/e14/turso-generation-015-001/README.md): `{"b": 0.5, "engine": "bm25"}` scored **69.72**, retaining **72.38**. The `length-normalization` mechanism records **3 / 3 consecutive evaluable misses** and the family **16 / 55 claims**. [Paired applications/categories](../evolution/e14/turso-generation-015-001/groups.md) and [CTA](../evolution/e14/turso-generation-015-001/cta.md) preserve this observation.

[Turso generation 14](../evolution/e14/turso-generation-014-001/README.md): `{"b": 0.0, "engine": "bm25"}` scored **61.38**, retaining **72.38**. The `length-normalization` mechanism records **2 / 3 consecutive evaluable misses** and the family **15 / 55 claims**. [Paired applications/categories](../evolution/e14/turso-generation-014-001/groups.md) and [CTA](../evolution/e14/turso-generation-014-001/cta.md) preserve this observation.

[Turso generation 13](../evolution/e14/turso-generation-013-001/README.md): `{"b": 0.25, "engine": "bm25"}` scored **66.70**, retaining **72.38**. The `length-normalization` mechanism records **1 / 3 consecutive evaluable misses** and the family **14 / 55 claims**. [Paired applications/categories](../evolution/e14/turso-generation-013-001/groups.md) and [CTA](../evolution/e14/turso-generation-013-001/cta.md) preserve this observation.

[Graphify generation 6](../evolution/e14/graphify-generation-006-001/README.md): `{"depth": 6}` scored **27.93**, retaining **27.94**. The `traversal-depth` mechanism records **2 / 3 consecutive evaluable misses** and the family **6 / 65 claims**. [Paired applications/categories](../evolution/e14/graphify-generation-006-001/groups.md) and [CTA](../evolution/e14/graphify-generation-006-001/cta.md) preserve this observation.

[Adaptive generation 10](../evolution/e14/adaptive-generation-010-001/README.md): `{"expansion.association_weight": 0.7, "expansion.topic_weight": 0.4}` scored **66.04**, retaining **66.21**. The `expansion-strength` mechanism records **3 / 3 consecutive evaluable misses** and the family **29 / 100 claims**. [Paired applications/categories](../evolution/e14/adaptive-generation-010-001/groups.md) and [CTA](../evolution/e14/adaptive-generation-010-001/cta.md) preserve this observation.

[Turso generation 12](../evolution/e14/turso-generation-012-001/README.md): `{"engine": "bm25", "k1": 3.0}` scored **71.36**, retaining **72.38**. The `bm25-saturation` mechanism records **3 / 3 consecutive evaluable misses** and the family **13 / 55 claims**. [Paired applications/categories](../evolution/e14/turso-generation-012-001/groups.md) and [CTA](../evolution/e14/turso-generation-012-001/cta.md) preserve this observation.

[Adaptive generation 9](../evolution/e14/adaptive-generation-009-001/README.md): `{"expansion.association_weight": 0.0, "expansion.topic_weight": 0.0}` scored **65.12**, retaining **66.21**. The `expansion-strength` mechanism records **2 / 3 consecutive evaluable misses** and the family **28 / 100 claims**. [Paired applications/categories](../evolution/e14/adaptive-generation-009-001/groups.md) and [CTA](../evolution/e14/adaptive-generation-009-001/cta.md) preserve this observation.

[Turso generation 11](../evolution/e14/turso-generation-011-001/README.md): `{"engine": "bm25", "k1": 0.6}` scored **69.24**, retaining **72.38**. The `bm25-saturation` mechanism records **2 / 3 consecutive evaluable misses** and the family **12 / 55 claims**. [Paired applications/categories](../evolution/e14/turso-generation-011-001/groups.md) and [CTA](../evolution/e14/turso-generation-011-001/cta.md) preserve this observation.

[Graphify generation 5](../evolution/e14/graphify-generation-005-001/README.md): `{"depth": 5}` scored **27.93**, retaining **27.94**. The `traversal-depth` mechanism records **1 / 3 consecutive evaluable misses** and the family **5 / 65 claims**. [Paired applications/categories](../evolution/e14/graphify-generation-005-001/groups.md) and [CTA](../evolution/e14/graphify-generation-005-001/cta.md) preserve this observation.

[Turso generation 10](../evolution/e14/turso-generation-010-001/README.md): `{"engine": "bm25", "k1": 1.2}` scored **71.97**, retaining **72.38**. The `bm25-saturation` mechanism records **1 / 3 consecutive evaluable misses** and the family **11 / 55 claims**. [Paired applications/categories](../evolution/e14/turso-generation-010-001/groups.md) and [CTA](../evolution/e14/turso-generation-010-001/cta.md) preserve this observation.

[Adaptive generation 8](../evolution/e14/adaptive-generation-008-001/README.md): `{"expansion.association_weight": 0.0875, "expansion.topic_weight": 0.05}` scored **65.47**, retaining **66.21**. The `expansion-strength` mechanism records **1 / 3 consecutive evaluable misses** and the family **27 / 100 claims**. [Paired applications/categories](../evolution/e14/adaptive-generation-008-001/groups.md) and [CTA](../evolution/e14/adaptive-generation-008-001/cta.md) preserve this observation.

[Turso generation 9](../evolution/e14/turso-generation-009-001/README.md): `{"engine": "bm25", "title_weight": 8.0}` scored **72.12**, retaining **72.38**. The `title-weight` mechanism records **1 / 3 consecutive evaluable misses** and the family **10 / 55 claims**. [Paired applications/categories](../evolution/e14/turso-generation-009-001/groups.md) and [CTA](../evolution/e14/turso-generation-009-001/cta.md) preserve this observation.

[Adaptive generation 7](../evolution/e14/adaptive-generation-007-001/README.md): `{"bm25.title_weight": 8.0}` scored **47.65**, retaining **66.21**. The `title-weight` mechanism records **2 / 3 consecutive evaluable misses** and the family **26 / 100 claims**. [Paired applications/categories](../evolution/e14/adaptive-generation-007-001/groups.md) and [CTA](../evolution/e14/adaptive-generation-007-001/cta.md) preserve this observation.

[Prospective Entity bounded-selection candidate](../evolution/candidates/entity-bounded-selection-001/README.md): eight sealed software checks passed, one builder function changed and Entity Graph reached **9 / 80 proposals**. Its new native first measurement is unassigned; retained EnterpriseRAG scores are unchanged.

[Graphify generation 4](../evolution/e14/graphify-generation-004-001/README.md): `{"depth": 4}` raises retained nDCG from **27.90 to 27.94**, resets consecutive evaluable misses to **0 / 3**, and brings the family to **4 / 65 claims**. **[Comparison at this observation](../evolution/e14/graphify-generation-004-001/comparison.md)** · [Paired groups](../evolution/e14/graphify-generation-004-001/groups.md) · [CTA](../evolution/e14/graphify-generation-004-001/cta.md).

[Turso generation 8](../evolution/e14/turso-generation-008-001/README.md): `{"engine": "bm25", "title_weight": 4.0}` raises retained nDCG from **72.13 to 72.38**, resets consecutive evaluable misses to **0 / 3**, and brings the family to **9 / 55 claims**. **[Comparison at this observation](../evolution/e14/turso-generation-008-001/comparison.md)** · [Paired groups](../evolution/e14/turso-generation-008-001/groups.md) · [CTA](../evolution/e14/turso-generation-008-001/cta.md).

[Adaptive generation 6](../evolution/e14/adaptive-generation-006-001/README.md): `{"bm25.title_weight": 4.0}` scored **54.79**, retaining **66.21**. The `title-weight` mechanism records **1 / 3 consecutive evaluable misses** and the family **25 / 100 claims**. [Paired applications/categories](../evolution/e14/adaptive-generation-006-001/groups.md) and [CTA](../evolution/e14/adaptive-generation-006-001/cta.md) preserve this observation.

[Turso generation 7](../evolution/e14/turso-generation-007-001/README.md): `{"engine": "bm25", "title_weight": 2.0}` scored **72.12**, retaining **72.13**. The `title-weight` mechanism records **1 / 3 consecutive evaluable misses** and the family **8 / 55 claims**. [Paired applications/categories](../evolution/e14/turso-generation-007-001/groups.md) and [CTA](../evolution/e14/turso-generation-007-001/cta.md) preserve this observation.

[Adaptive generation 5](../evolution/e14/adaptive-generation-005-001/README.md): `{"bm25.k1": 2.0}` scored **65.61**, retaining **66.21**. The `bm25-saturation` mechanism records **2 / 3 consecutive evaluable misses** and the family **24 / 100 claims**. [Paired applications/categories](../evolution/e14/adaptive-generation-005-001/groups.md) and [CTA](../evolution/e14/adaptive-generation-005-001/cta.md) preserve this observation.

[Graphify generation 3](../evolution/e14/graphify-generation-003-001/README.md): `{"depth": 3}` raises retained nDCG from **8.12 to 27.90**, resets consecutive evaluable misses to **0 / 3**, and brings the family to **3 / 65 claims**. **[Comparison at this observation](../evolution/e14/graphify-generation-003-001/comparison.md)** · [Paired groups](../evolution/e14/graphify-generation-003-001/groups.md) · [CTA](../evolution/e14/graphify-generation-003-001/cta.md).

[Prospective Ensemble mention-automaton candidate](../evolution/candidates/ensemble-mention-automaton-transfer-001/README.md): five sealed software checks passed, one builder function changed and Ensemble reached **3 / 105 proposals**. Its new native first measurement is unassigned; retained EnterpriseRAG scores are unchanged.

[Turso generation 6](../evolution/e14/turso-generation-006-001/README.md): `{"b": 0.5, "engine": "bm25"}` scored **70.44**, retaining **72.13**. The `length-normalization` mechanism records **3 / 3 consecutive evaluable misses** and the family **7 / 55 claims**. [Paired applications/categories](../evolution/e14/turso-generation-006-001/groups.md) and [CTA](../evolution/e14/turso-generation-006-001/cta.md) preserve this observation.

[Adaptive generation 4](../evolution/e14/adaptive-generation-004-001/README.md): `{"bm25.k1": 0.6}` scored **65.52**, retaining **66.21**. The `bm25-saturation` mechanism records **1 / 3 consecutive evaluable misses** and the family **23 / 100 claims**. [Paired applications/categories](../evolution/e14/adaptive-generation-004-001/groups.md) and [CTA](../evolution/e14/adaptive-generation-004-001/cta.md) preserve this observation.

[Turso generation 5](../evolution/e14/turso-generation-005-001/README.md): `{"b": 0.0, "engine": "bm25"}` scored **61.35**, retaining **72.13**. The `length-normalization` mechanism records **2 / 3 consecutive evaluable misses** and the family **6 / 55 claims**. [Paired applications/categories](../evolution/e14/turso-generation-005-001/groups.md) and [CTA](../evolution/e14/turso-generation-005-001/cta.md) preserve this observation.

[Graphify generation 2](../evolution/e14/graphify-generation-002-001/README.md): `{"depth": 1}` scored **6.85**, retaining **8.12**. The `traversal-depth` mechanism records **2 / 3 consecutive evaluable misses** and the family **2 / 65 claims**. [Paired applications/categories](../evolution/e14/graphify-generation-002-001/groups.md) and [CTA](../evolution/e14/graphify-generation-002-001/cta.md) preserve this observation.

[Turso generation 4](../evolution/e14/turso-generation-004-001/README.md): `{"b": 0.25, "engine": "bm25"}` scored **66.80**, retaining **72.13**. The `length-normalization` mechanism records **1 / 3 consecutive evaluable misses** and the family **5 / 55 claims**. [Paired applications/categories](../evolution/e14/turso-generation-004-001/groups.md) and [CTA](../evolution/e14/turso-generation-004-001/cta.md) preserve this observation.

[Adaptive reaches three normalization misses](../evolution/e14/adaptive-generation-003-001/README.md): construction `bm25.b=0.5` scored **65.78**, below retained **66.21**. This is the third consecutive unique evaluable miss in the mechanism, with **22 / 100 claims**. Its other search opportunities were still open at this observation. [Paired applications/categories](../evolution/e14/adaptive-generation-003-001/groups.md) and [CTA](../evolution/e14/adaptive-generation-003-001/cta.md) preserve the measured result. The retained six-family ranking is unchanged.

This dataset view separates the retained internal strategy comparison from
the latest incomplete continuation. The fixed workload uses **120 stratified
questions, 112 retrieval-eligible questions and 6,000 complete documents**.
The primary metric is frozen-category-weighted **nDCG@10 multiplied by 100**.

## Earlier retained comparison: Turso 2 and Graphify 1

| Strategy | Retained score | Source |
| --- | ---: | --- |
| Legacy | 72.38 | Historical incumbent exactly reproduced by E14 |
| Turso | 72.13 | [Qualified E14 generation-two incumbent](../evolution/e14/turso-generation-002-001/README.md) |
| Adaptive | 66.21 | Historical incumbent exactly reproduced by E14 |
| Embeddings | 63.51 | Historical reference exactly reproduced by E14 |
| Classical | 62.10 | Historical incumbent exactly reproduced by E14 |
| Graphify | 8.12 | [Reference retained after the qualified depth-zero miss](../evolution/e14/graphify-generation-001-001/README.md) |
| Entity Graph | Unavailable | E14 starting timeout; no qualified ranking |
| Ensemble | Unavailable | E14 starting memory failure; no qualified ranking |

Legacy has the highest retained score in this partial development comparison.
This does not establish a winner on the all-500 workload, on other datasets,
or on generated-answer quality. Exact evidence and opportunity limits are in
the [eight-family report](../evolution/e14/turso-generation-002-001/README.md#retained-eight-family-comparison).

The [consolidated six-family comparison](../evolution/e14/turso-generation-002-001/comparison.md)
shows the retained scores for every application and question category, their
observed leaders and the corresponding native cost/time measurements. These
descriptive subgroup results do not select a candidate or evaluate a router.

## Earlier continuation and starting qualification

The [earlier Turso and Adaptive variants](../evolution/e14/turso-003-adaptive-002-observations-001/README.md) scored **71.13** and **62.31**, below retained **72.13** and **66.21**. Both are qualified observations, with one proposal each and no errors or retries. The retained dataset ranking is unchanged.

The [Graphify depth-zero candidate](../evolution/e14/graphify-generation-001-001/README.md) scored **7.03** against its retained **8.12** reference. It is one qualified evaluable miss on this exact workload, with zero errors or retries. The dataset ranking is unchanged.

The [qualified Turso `k1=2.0` observation](../evolution/e14/turso-generation-002-001/README.md) improves its retained nDCG to **72.13**. The gain is 0.04949 points; recall and MRR fall slightly. Legacy remains first overall. The updated application comparison puts Turso first in Jira and tied with Legacy in HubSpot.

The [earlier pending Turso and Adaptive variants](../evolution/e14/generation-001-pending-variants-001/README.md) scored **69.31** and **64.53**, retaining **72.08** and **66.21**. Both are qualified observations on this exact workload, with one evaluable miss each and zero new proposal charges. The retained dataset ranking is unchanged.

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
checkpoints establish no new champion. At this earlier checkpoint, Turso, Adaptive and Graphify still had open
inherited searches. The two failed family starts, their unexercised
hypotheses and the final all-eight comparison remain unresolved. Private
validation is unopened.

The [earlier E13 study](../evolution/e13/README.md) remains closed after its
cache phase-declaration controller stop. Its reference is reused under its
original job and staged-skill identity.

- [Classical results across nine applications and ten question categories](../evolution/e14/classical-starting-qualified-001/groups.md)
- [Classical native cost, time and quality](../evolution/e14/classical-starting-qualified-001/cta.md)
- [Starting-qualification aggregate](../evolution/e14/classical-starting-qualified-001/aggregate.json)
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
