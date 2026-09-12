# EnterpriseRAG E14: starting results and inherited evolution

[Graphify generation 4](graphify-generation-004-001/README.md): `{"depth": 4}` raises retained nDCG from **27.90 to 27.94**, resets consecutive evaluable misses to **0 / 3**, and brings the family to **4 / 65 claims**. **[Latest general application/category comparison](graphify-generation-004-001/comparison.md)** · [Paired groups](graphify-generation-004-001/groups.md) · [CTA](graphify-generation-004-001/cta.md).

[Turso generation 8](turso-generation-008-001/README.md): `{"engine": "bm25", "title_weight": 4.0}` raises retained nDCG from **72.13 to 72.38**, resets consecutive evaluable misses to **0 / 3**, and brings the family to **9 / 55 claims**. **[Latest general application/category comparison](turso-generation-008-001/comparison.md)** · [Paired groups](turso-generation-008-001/groups.md) · [CTA](turso-generation-008-001/cta.md).

[Adaptive generation 6](adaptive-generation-006-001/README.md): `{"bm25.title_weight": 4.0}` scored **54.79**, retaining **66.21**. The `title-weight` mechanism records **1 / 3 consecutive evaluable misses** and the family **25 / 100 claims**. [Paired applications/categories](adaptive-generation-006-001/groups.md) and [CTA](adaptive-generation-006-001/cta.md) preserve this observation.

[Turso generation 7](turso-generation-007-001/README.md): `{"engine": "bm25", "title_weight": 2.0}` scored **72.12**, retaining **72.13**. The `title-weight` mechanism records **1 / 3 consecutive evaluable misses** and the family **8 / 55 claims**. [Paired applications/categories](turso-generation-007-001/groups.md) and [CTA](turso-generation-007-001/cta.md) preserve this observation.

[Adaptive generation 5](adaptive-generation-005-001/README.md): `{"bm25.k1": 2.0}` scored **65.61**, retaining **66.21**. The `bm25-saturation` mechanism records **2 / 3 consecutive evaluable misses** and the family **24 / 100 claims**. [Paired applications/categories](adaptive-generation-005-001/groups.md) and [CTA](adaptive-generation-005-001/cta.md) preserve this observation.

[Graphify generation 3](graphify-generation-003-001/README.md): `{"depth": 3}` raises retained nDCG from **8.12 to 27.90**, resets consecutive evaluable misses to **0 / 3**, and brings the family to **3 / 65 claims**. **[Latest general application/category comparison](graphify-generation-003-001/comparison.md)** · [Paired groups](graphify-generation-003-001/groups.md) · [CTA](graphify-generation-003-001/cta.md).

[Prospective Ensemble mention-automaton candidate](../candidates/ensemble-mention-automaton-transfer-001/README.md): five sealed software checks passed, one builder function changed and Ensemble reached **3 / 105 proposals**. Its new native first measurement is unassigned; retained EnterpriseRAG scores are unchanged.

[Turso generation 6](turso-generation-006-001/README.md): `{"b": 0.5, "engine": "bm25"}` scored **70.44**, retaining **72.13**. The `length-normalization` mechanism records **3 / 3 consecutive evaluable misses** and the family **7 / 55 claims**. [Paired applications/categories](turso-generation-006-001/groups.md) and [CTA](turso-generation-006-001/cta.md) preserve this observation.

[Adaptive generation 4](adaptive-generation-004-001/README.md): `{"bm25.k1": 0.6}` scored **65.52**, retaining **66.21**. The `bm25-saturation` mechanism records **1 / 3 consecutive evaluable misses** and the family **23 / 100 claims**. [Paired applications/categories](adaptive-generation-004-001/groups.md) and [CTA](adaptive-generation-004-001/cta.md) preserve this observation.

[Turso generation 5](turso-generation-005-001/README.md): `{"b": 0.0, "engine": "bm25"}` scored **61.35**, retaining **72.13**. The `length-normalization` mechanism records **2 / 3 consecutive evaluable misses** and the family **6 / 55 claims**. [Paired applications/categories](turso-generation-005-001/groups.md) and [CTA](turso-generation-005-001/cta.md) preserve this observation.

[Graphify generation 2](graphify-generation-002-001/README.md): `{"depth": 1}` scored **6.85**, retaining **8.12**. The `traversal-depth` mechanism records **2 / 3 consecutive evaluable misses** and the family **2 / 65 claims**. [Paired applications/categories](graphify-generation-002-001/groups.md) and [CTA](graphify-generation-002-001/cta.md) preserve this observation.

[Turso generation 4](turso-generation-004-001/README.md): `{"b": 0.25, "engine": "bm25"}` scored **66.80**, retaining **72.13**. The `length-normalization` mechanism records **1 / 3 consecutive evaluable misses** and the family **5 / 55 claims**. [Paired applications/categories](turso-generation-004-001/groups.md) and [CTA](turso-generation-004-001/cta.md) preserve this observation.

[Adaptive reaches three normalization misses](adaptive-generation-003-001/README.md): construction `bm25.b=0.5` scored **65.78**, below retained **66.21**. This is the third consecutive unique evaluable miss in the mechanism, with **22 / 100 claims**. Its other search opportunities remain open. [Paired applications/categories](adaptive-generation-003-001/groups.md) and [CTA](adaptive-generation-003-001/cta.md) preserve the measured result. The retained six-family ranking is unchanged.

The [latest qualified Turso and Adaptive candidates](turso-003-adaptive-002-observations-001/README.md) scored **71.13** and **62.31**, retaining **72.13** and **66.21**. Their cumulative claim counts are 4 / 55 and 21 / 100 at these observations. The [accounting report](turso-003-adaptive-002-observations-001/README.md#search-accounting) distinguishes Turso's exhausted saturation variant list from Adaptive's second consecutive miss. See [paired groups](turso-003-adaptive-002-observations-001/groups.md) and [CTA](turso-003-adaptive-002-observations-001/cta.md).

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
- [Latest native starting errors: Entity Graph timeout and Ensemble memory failure](starting-execution-errors-001/README.md)
- [Failure evidence and unchanged eight-family ranking](starting-execution-errors-001/aggregate.json)
- [Cross-family comparison: six qualified retained profiles by application, category and CTA](qualified-starts-comparison-001/README.md)
- [Latest starting qualification, retained eight-family comparison and remaining opportunities](classical-starting-qualified-001/README.md)
- [Classical cost, time and quality](classical-starting-qualified-001/cta.md)
- [Classical results across nine applications and ten question categories](classical-starting-qualified-001/groups.md)
- [Latest machine-readable aggregate and source commitments](classical-starting-qualified-001/aggregate.json)
- [Preserved Embeddings starting role](embeddings-starting-qualified-001/README.md), [CTA](embeddings-starting-qualified-001/cta.md) and [applications/categories](embeddings-starting-qualified-001/groups.md)
- [Preserved Graphify starting role](graphify-starting-qualified-001/README.md), [CTA](graphify-starting-qualified-001/cta.md) and [applications/categories](graphify-starting-qualified-001/groups.md)
- [Preserved Legacy starting pair](legacy-starting-qualified-001/README.md), [CTA](legacy-starting-qualified-001/cta.md) and [applications/categories](legacy-starting-qualified-001/groups.md)
- [Preserved Adaptive starting pair](adaptive-starting-qualified-001/README.md), [CTA](adaptive-starting-qualified-001/cta.md) and [applications/categories](adaptive-starting-qualified-001/groups.md)
- [Preserved Turso starting pair](turso-starting-qualified-001/README.md), [CTA](turso-starting-qualified-001/cta.md) and [applications/categories](turso-starting-qualified-001/groups.md)
- [Stratified EnterpriseRAG dataset view](../../datasets/enterprise-rag-stratified-development-120.md)

The actual E14 design is registered and sealed. The workload remains 120
stratified questions, 112 retrieval-eligible questions and 6,000 complete
documents. At this published checkpoint, six current family qualifications are
complete. Turso, Adaptive and Graphify can continue their inherited searches;
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
