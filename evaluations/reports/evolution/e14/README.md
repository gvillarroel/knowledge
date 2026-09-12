# EnterpriseRAG E14: starting results and inherited evolution

[Graphify generation 12](graphify-generation-012-001/README.md): `{"lexical_weight": 1.0, "rrf_k": 20}` scored **54.45**, retaining **63.46**. The `fusion-rank-decay` mechanism records **2 / 3 consecutive evaluable misses** and the family **12 / 65 claims**. [Paired applications/categories](graphify-generation-012-001/groups.md) and [CTA](graphify-generation-012-001/cta.md) preserve this observation.

[Graphify generation 11](graphify-generation-011-001/README.md): `{"lexical_weight": 1.0, "rrf_k": 5}` scored **59.35**, retaining **63.46**. The `fusion-rank-decay` mechanism records **1 / 3 consecutive evaluable misses** and the family **11 / 65 claims**. [Paired applications/categories](graphify-generation-011-001/groups.md) and [CTA](graphify-generation-011-001/cta.md) preserve this observation.

[Graphify generation 10](graphify-generation-010-001/README.md): `{"lexical_weight": 4.0}` raises retained nDCG from **57.63 to 63.46**, resets consecutive evaluable misses to **0 / 3**, and brings the family to **10 / 65 claims**. **[Latest general application/category comparison](graphify-generation-010-001/comparison.md)** · [Paired groups](graphify-generation-010-001/groups.md) · [CTA](graphify-generation-010-001/cta.md).

[Graphify generation 9](graphify-generation-009-001/README.md): `{"lexical_weight": 2.0}` raises retained nDCG from **52.33 to 57.63**, resets consecutive evaluable misses to **0 / 3**, and brings the family to **9 / 65 claims**. **[Comparison at this observation](graphify-generation-009-001/comparison.md)** · [Paired groups](graphify-generation-009-001/groups.md) · [CTA](graphify-generation-009-001/cta.md).

[Graphify generation 8](graphify-generation-008-001/README.md): `{"lexical_weight": 1.0}` raises retained nDCG from **34.16 to 52.33**, resets consecutive evaluable misses to **0 / 3**, and brings the family to **8 / 65 claims**. **[Comparison at this observation](graphify-generation-008-001/comparison.md)** · [Paired groups](graphify-generation-008-001/groups.md) · [CTA](graphify-generation-008-001/cta.md).

## Verified development status

Explicitly selected published observation: **Graphify generation 10**, published 2026-09-12T07:07:00.428137+00:00. [Source-bound result](graphify-generation-010-001/README.md).

The fixed development workload contains **120 stratified questions, 112 retrieval-eligible questions and 6,000 complete documents**. Scores are frozen-category-weighted **nDCG@10 x100**; the eligible population weight is 470.

| Family | Retained nDCG@10 x100 | Qualification |
| --- | ---: | --- |
| Legacy | 72.38 | Qualified |
| Turso | 72.38 | Qualified |
| Adaptive | 66.21 | Qualified |
| Embeddings | 63.51 | Qualified |
| Classical | 62.10 | Qualified |
| Graphify | 63.46 | Qualified |
| Ensemble | Unavailable | Unavailable after execution error |
| Entity Graph | Unavailable | Unavailable after execution error |

The selected Graphify gain is **57.63 to 63.46**. Paired questions: **46 improve, 4 regress and 62 tie**; eight questions lack retrieval references. Other retained families keep their original observations.

### Catalog status and remaining work

The [catalog inventory](opportunity-accounting-002/README.md) is a separate snapshot at **2026-09-12T03:39:49.038282+00:00**. It records **5 catalog stops**: Legacy, Turso, Adaptive, Embeddings, Classical. It also preserves **2 unavailable historical hypotheses** among stopped families. Catalog closure does not imply complete historical measurement coverage. This dated inventory does not supply current reservation counts or replace the newer retained scores above.

**6 of eight families have qualified retrieval references** in this comparison. Remaining work includes outstanding family qualification and evolution, the paired joint development replay, one whole-bundle freeze, the all-500 comparison and independent acceptance. Validation stays sealed until the selected candidate is frozen.

### Applications, categories and CTA

[General application/category comparison](graphify-generation-010-001/comparison.md) · [Paired groups](graphify-generation-010-001/groups.md) · [Retained-family CTA](graphify-generation-010-001/cta.md).

Application cohorts overlap. Highest values describe the supplied comparison; no application router is tested.

| Application | Highest retained nDCG |
| --- | --- |
| Confluence | Embeddings |
| Fireflies | Classical |
| GitHub | Graphify |
| Gmail | Legacy, Turso |
| Google Drive | Graphify |
| HubSpot | Legacy, Turso |
| Jira | Legacy, Turso |
| Linear | Classical |
| Slack | Embeddings |

### Measurement boundaries

These development retrieval metrics do not establish all-500 results, generated-answer Overall, statistical significance, canonical promotion or a public leaderboard position. Host and orchestration costs are unpriced. Historical observations below retain their original scope and counts.

The earlier [Classical full-corpus run](../../datasets/enterprise-rag-classical-full-500.md), [Luna answer audit](../../enterprise-classical-full/luna.md) and [cross-dataset comparisons](../../README.md#historical-retrieval-comparisons) retain their separate workloads and scoring contracts.

## Published observation history

Each entry below describes the state at its own checkpoint. A mechanism that
was open in an earlier entry may have a later verified catalog stop.

[Graphify generation 7](graphify-generation-007-001/README.md): `{"lexical_weight": 0.5}` raises retained nDCG from **27.94 to 34.16**, resets consecutive evaluable misses to **0 / 3**, and brings the family to **7 / 65 claims**. **[Comparison at this observation](graphify-generation-007-001/comparison.md)** · [Paired groups](graphify-generation-007-001/groups.md) · [CTA](graphify-generation-007-001/cta.md).

[Five verified catalog stops and remaining EnterpriseRAG work](opportunity-accounting-002/README.md): snapshot at 2026-09-12 03:39 UTC. Six qualified references, three families without a catalog closure, and two historical fitness gaps among the stopped families remain distinct. The inventory preserves all eight strategies and exact proposal accounting.

[Turso generation 15](turso-generation-015-001/README.md): `{"b": 0.5, "engine": "bm25"}` scored **69.72**, retaining **72.38**. The `length-normalization` mechanism records **3 / 3 consecutive evaluable misses** and the family **16 / 55 claims**. [Paired applications/categories](turso-generation-015-001/groups.md) and [CTA](turso-generation-015-001/cta.md) preserve this observation.

[Turso generation 14](turso-generation-014-001/README.md): `{"b": 0.0, "engine": "bm25"}` scored **61.38**, retaining **72.38**. The `length-normalization` mechanism records **2 / 3 consecutive evaluable misses** and the family **15 / 55 claims**. [Paired applications/categories](turso-generation-014-001/groups.md) and [CTA](turso-generation-014-001/cta.md) preserve this observation.

[Turso generation 13](turso-generation-013-001/README.md): `{"b": 0.25, "engine": "bm25"}` scored **66.70**, retaining **72.38**. The `length-normalization` mechanism records **1 / 3 consecutive evaluable misses** and the family **14 / 55 claims**. [Paired applications/categories](turso-generation-013-001/groups.md) and [CTA](turso-generation-013-001/cta.md) preserve this observation.

[Graphify generation 6](graphify-generation-006-001/README.md): `{"depth": 6}` scored **27.93**, retaining **27.94**. The `traversal-depth` mechanism records **2 / 3 consecutive evaluable misses** and the family **6 / 65 claims**. [Paired applications/categories](graphify-generation-006-001/groups.md) and [CTA](graphify-generation-006-001/cta.md) preserve this observation.

[Adaptive generation 10](adaptive-generation-010-001/README.md): `{"expansion.association_weight": 0.7, "expansion.topic_weight": 0.4}` scored **66.04**, retaining **66.21**. The `expansion-strength` mechanism records **3 / 3 consecutive evaluable misses** and the family **29 / 100 claims**. [Paired applications/categories](adaptive-generation-010-001/groups.md) and [CTA](adaptive-generation-010-001/cta.md) preserve this observation.

[Opportunity inventory for all eight families](opportunity-accounting-001/README.md): snapshot at 2026-09-12 02:07 UTC, with three inherited catalog stops, five open family obligations and two families still awaiting valid native evidence. Reservations and pending trials are counted separately.

[Turso generation 12](turso-generation-012-001/README.md): `{"engine": "bm25", "k1": 3.0}` scored **71.36**, retaining **72.38**. The `bm25-saturation` mechanism records **3 / 3 consecutive evaluable misses** and the family **13 / 55 claims**. [Paired applications/categories](turso-generation-012-001/groups.md) and [CTA](turso-generation-012-001/cta.md) preserve this observation.

[Adaptive generation 9](adaptive-generation-009-001/README.md): `{"expansion.association_weight": 0.0, "expansion.topic_weight": 0.0}` scored **65.12**, retaining **66.21**. The `expansion-strength` mechanism records **2 / 3 consecutive evaluable misses** and the family **28 / 100 claims**. [Paired applications/categories](adaptive-generation-009-001/groups.md) and [CTA](adaptive-generation-009-001/cta.md) preserve this observation.

[Turso generation 11](turso-generation-011-001/README.md): `{"engine": "bm25", "k1": 0.6}` scored **69.24**, retaining **72.38**. The `bm25-saturation` mechanism records **2 / 3 consecutive evaluable misses** and the family **12 / 55 claims**. [Paired applications/categories](turso-generation-011-001/groups.md) and [CTA](turso-generation-011-001/cta.md) preserve this observation.

[Graphify generation 5](graphify-generation-005-001/README.md): `{"depth": 5}` scored **27.93**, retaining **27.94**. The `traversal-depth` mechanism records **1 / 3 consecutive evaluable misses** and the family **5 / 65 claims**. [Paired applications/categories](graphify-generation-005-001/groups.md) and [CTA](graphify-generation-005-001/cta.md) preserve this observation.

[Turso generation 10](turso-generation-010-001/README.md): `{"engine": "bm25", "k1": 1.2}` scored **71.97**, retaining **72.38**. The `bm25-saturation` mechanism records **1 / 3 consecutive evaluable misses** and the family **11 / 55 claims**. [Paired applications/categories](turso-generation-010-001/groups.md) and [CTA](turso-generation-010-001/cta.md) preserve this observation.

[Adaptive generation 8](adaptive-generation-008-001/README.md): `{"expansion.association_weight": 0.0875, "expansion.topic_weight": 0.05}` scored **65.47**, retaining **66.21**. The `expansion-strength` mechanism records **1 / 3 consecutive evaluable misses** and the family **27 / 100 claims**. [Paired applications/categories](adaptive-generation-008-001/groups.md) and [CTA](adaptive-generation-008-001/cta.md) preserve this observation.

[Turso generation 9](turso-generation-009-001/README.md): `{"engine": "bm25", "title_weight": 8.0}` scored **72.12**, retaining **72.38**. The `title-weight` mechanism records **1 / 3 consecutive evaluable misses** and the family **10 / 55 claims**. [Paired applications/categories](turso-generation-009-001/groups.md) and [CTA](turso-generation-009-001/cta.md) preserve this observation.

[Adaptive generation 7](adaptive-generation-007-001/README.md): `{"bm25.title_weight": 8.0}` scored **47.65**, retaining **66.21**. The `title-weight` mechanism records **2 / 3 consecutive evaluable misses** and the family **26 / 100 claims**. [Paired applications/categories](adaptive-generation-007-001/groups.md) and [CTA](adaptive-generation-007-001/cta.md) preserve this observation.

[Prospective Entity bounded-selection candidate](../candidates/entity-bounded-selection-001/README.md): eight sealed software checks passed, one builder function changed and Entity Graph reached **9 / 80 proposals**. Its new native first measurement is unassigned; retained EnterpriseRAG scores are unchanged.

[Graphify generation 4](graphify-generation-004-001/README.md): `{"depth": 4}` raises retained nDCG from **27.90 to 27.94**, resets consecutive evaluable misses to **0 / 3**, and brings the family to **4 / 65 claims**. **[Comparison at this observation](graphify-generation-004-001/comparison.md)** · [Paired groups](graphify-generation-004-001/groups.md) · [CTA](graphify-generation-004-001/cta.md).

[Turso generation 8](turso-generation-008-001/README.md): `{"engine": "bm25", "title_weight": 4.0}` raises retained nDCG from **72.13 to 72.38**, resets consecutive evaluable misses to **0 / 3**, and brings the family to **9 / 55 claims**. **[Comparison at this observation](turso-generation-008-001/comparison.md)** · [Paired groups](turso-generation-008-001/groups.md) · [CTA](turso-generation-008-001/cta.md).

[Adaptive generation 6](adaptive-generation-006-001/README.md): `{"bm25.title_weight": 4.0}` scored **54.79**, retaining **66.21**. The `title-weight` mechanism records **1 / 3 consecutive evaluable misses** and the family **25 / 100 claims**. [Paired applications/categories](adaptive-generation-006-001/groups.md) and [CTA](adaptive-generation-006-001/cta.md) preserve this observation.

[Turso generation 7](turso-generation-007-001/README.md): `{"engine": "bm25", "title_weight": 2.0}` scored **72.12**, retaining **72.13**. The `title-weight` mechanism records **1 / 3 consecutive evaluable misses** and the family **8 / 55 claims**. [Paired applications/categories](turso-generation-007-001/groups.md) and [CTA](turso-generation-007-001/cta.md) preserve this observation.

[Adaptive generation 5](adaptive-generation-005-001/README.md): `{"bm25.k1": 2.0}` scored **65.61**, retaining **66.21**. The `bm25-saturation` mechanism records **2 / 3 consecutive evaluable misses** and the family **24 / 100 claims**. [Paired applications/categories](adaptive-generation-005-001/groups.md) and [CTA](adaptive-generation-005-001/cta.md) preserve this observation.

[Graphify generation 3](graphify-generation-003-001/README.md): `{"depth": 3}` raises retained nDCG from **8.12 to 27.90**, resets consecutive evaluable misses to **0 / 3**, and brings the family to **3 / 65 claims**. **[Comparison at this observation](graphify-generation-003-001/comparison.md)** · [Paired groups](graphify-generation-003-001/groups.md) · [CTA](graphify-generation-003-001/cta.md).

[Prospective Ensemble mention-automaton candidate](../candidates/ensemble-mention-automaton-transfer-001/README.md): five sealed software checks passed, one builder function changed and Ensemble reached **3 / 105 proposals**. Its new native first measurement is unassigned; retained EnterpriseRAG scores are unchanged.

[Turso generation 6](turso-generation-006-001/README.md): `{"b": 0.5, "engine": "bm25"}` scored **70.44**, retaining **72.13**. The `length-normalization` mechanism records **3 / 3 consecutive evaluable misses** and the family **7 / 55 claims**. [Paired applications/categories](turso-generation-006-001/groups.md) and [CTA](turso-generation-006-001/cta.md) preserve this observation.

[Adaptive generation 4](adaptive-generation-004-001/README.md): `{"bm25.k1": 0.6}` scored **65.52**, retaining **66.21**. The `bm25-saturation` mechanism records **1 / 3 consecutive evaluable misses** and the family **23 / 100 claims**. [Paired applications/categories](adaptive-generation-004-001/groups.md) and [CTA](adaptive-generation-004-001/cta.md) preserve this observation.

[Turso generation 5](turso-generation-005-001/README.md): `{"b": 0.0, "engine": "bm25"}` scored **61.35**, retaining **72.13**. The `length-normalization` mechanism records **2 / 3 consecutive evaluable misses** and the family **6 / 55 claims**. [Paired applications/categories](turso-generation-005-001/groups.md) and [CTA](turso-generation-005-001/cta.md) preserve this observation.

[Graphify generation 2](graphify-generation-002-001/README.md): `{"depth": 1}` scored **6.85**, retaining **8.12**. The `traversal-depth` mechanism records **2 / 3 consecutive evaluable misses** and the family **2 / 65 claims**. [Paired applications/categories](graphify-generation-002-001/groups.md) and [CTA](graphify-generation-002-001/cta.md) preserve this observation.

[Turso generation 4](turso-generation-004-001/README.md): `{"b": 0.25, "engine": "bm25"}` scored **66.80**, retaining **72.13**. The `length-normalization` mechanism records **1 / 3 consecutive evaluable misses** and the family **5 / 55 claims**. [Paired applications/categories](turso-generation-004-001/groups.md) and [CTA](turso-generation-004-001/cta.md) preserve this observation.

[Adaptive reaches three normalization misses](adaptive-generation-003-001/README.md): construction `bm25.b=0.5` scored **65.78**, below retained **66.21**. This is the third consecutive unique evaluable miss in the mechanism, with **22 / 100 claims**. Its other search opportunities were still open at this observation. [Paired applications/categories](adaptive-generation-003-001/groups.md) and [CTA](adaptive-generation-003-001/cta.md) preserve the measured result. The retained six-family ranking is unchanged.

The [earlier qualified Turso and Adaptive candidates](turso-003-adaptive-002-observations-001/README.md) scored **71.13** and **62.31**, retaining **72.13** and **66.21**. Their cumulative claim counts are 4 / 55 and 21 / 100 at these observations. The [accounting report](turso-003-adaptive-002-observations-001/README.md#search-accounting) distinguishes Turso's exhausted saturation variant list from Adaptive's second consecutive miss. See [paired groups](turso-003-adaptive-002-observations-001/groups.md) and [CTA](turso-003-adaptive-002-observations-001/cta.md).

The [qualified Graphify depth-zero observation](graphify-generation-001-001/README.md) scored **7.03**, below its retained **8.12** reference. It records one evaluable miss and 1 / 65 claims, with no execution error or retry. See [paired application/category results](graphify-generation-001-001/groups.md) and [CTA](graphify-generation-001-001/cta.md). The retained six-family comparison remains unchanged.

The [qualified Turso generation-two result](turso-generation-002-001/README.md) raises its retained development nDCG@10 to **72.13**. The observed gain is **0.04949 points**, while recall and MRR fall slightly. It is a new family development incumbent, with no final promotion. See the [updated six-family application/category comparison](turso-generation-002-001/comparison.md), [paired Turso groups](turso-generation-002-001/groups.md) and [CTA](turso-generation-002-001/cta.md).

The [first pending Turso and Adaptive variants](generation-001-pending-variants-001/README.md) have now completed and been reconciled. Turso measured **69.31** and Adaptive **64.53**, retaining **72.08** and **66.21** respectively. Each adds one evaluable miss to its current mechanism and zero proposal charges. See [applications and categories](generation-001-pending-variants-001/groups.md) and [cost, time and quality](generation-001-pending-variants-001/cta.md).

The original Entity Graph and Ensemble starting attempts have now finished with
execution errors: **Entity Graph timed out after 3,600 seconds; Ensemble
encountered an out-of-memory event under the fixed 6 GiB limit**. Their retrieval
scores remain unavailable. Both were stopped locally before qualification;
their remaining evolution hypotheses have not been exhausted. The
[failure report](starting-execution-errors-001/README.md) preserves the native
errors, cost/time measurements and auxiliary build evidence. These errors do
not count as mutation quality misses.

The starting checkpoints completed **six of eight current family
starting qualifications: Legacy, Turso, Adaptive, Embeddings, Classical and
Graphify**. Classical's new pair exactly reproduces **55.04** for the reference
and **62.10 weighted nDCG@10 x100** for the retained profile. Its recorded
catalog stop and inherited charges remain preserved. The other retained scores
are unchanged. All ten included native records are qualified, with zero errors
and zero retries. Turso's reference remains the exact original E13 job. These
checkpoints reproduce existing results and establish no new champion or promotion.

- [Entity query arithmetic diagnostic: preserved operation order and rejected shortcuts](entity-query-arithmetic-diagnostic-001/README.md)
- [Original native starting errors: Entity Graph timeout and Ensemble memory failure](starting-execution-errors-001/README.md)
- [Failure evidence and unchanged eight-family ranking](starting-execution-errors-001/aggregate.json)
- [Cross-family comparison: six qualified retained profiles by application, category and CTA](qualified-starts-comparison-001/README.md)
- [Starting qualification, retained eight-family comparison and remaining opportunities](classical-starting-qualified-001/README.md)
- [Classical cost, time and quality](classical-starting-qualified-001/cta.md)
- [Classical results across nine applications and ten question categories](classical-starting-qualified-001/groups.md)
- [Starting-qualification aggregate and source commitments](classical-starting-qualified-001/aggregate.json)
- [Preserved Embeddings starting role](embeddings-starting-qualified-001/README.md), [CTA](embeddings-starting-qualified-001/cta.md) and [applications/categories](embeddings-starting-qualified-001/groups.md)
- [Preserved Graphify starting role](graphify-starting-qualified-001/README.md), [CTA](graphify-starting-qualified-001/cta.md) and [applications/categories](graphify-starting-qualified-001/groups.md)
- [Preserved Legacy starting pair](legacy-starting-qualified-001/README.md), [CTA](legacy-starting-qualified-001/cta.md) and [applications/categories](legacy-starting-qualified-001/groups.md)
- [Preserved Adaptive starting pair](adaptive-starting-qualified-001/README.md), [CTA](adaptive-starting-qualified-001/cta.md) and [applications/categories](adaptive-starting-qualified-001/groups.md)
- [Preserved Turso starting pair](turso-starting-qualified-001/README.md), [CTA](turso-starting-qualified-001/cta.md) and [applications/categories](turso-starting-qualified-001/groups.md)
- [Stratified EnterpriseRAG dataset view](../../datasets/enterprise-rag-stratified-development-120.md)

The actual E14 design is registered and sealed. The workload remains 120
stratified questions, 112 retrieval-eligible questions and 6,000 complete
documents. At the earlier starting checkpoint, six family qualifications were
complete. Turso, Adaptive and Graphify still had open inherited searches;
Entity Graph and Ensemble stopped locally before qualification, with unexercised
hypotheses still outstanding. Private validation is unopened. The original
three-miss rule, five-round ceiling, family caps and consumed identities remain
preserved.

The full objective still requires all eight family qualifications and inherited
searches, the paired joint replay, one frozen whole bundle, the all-500
comparison and the independent acceptance gate. This intermediate report does
not assign an answer-quality Overall score or public leaderboard position.

[Family index](../../../../docs/enterprise-family-report-index.md)
· [Evolution studies](../README.md) · [Report hub](../../README.md)
· [Preserved E13 outcome](../e13/README.md)
