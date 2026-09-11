# Evaluation report hub

[Graphify generation 2](evolution/e14/graphify-generation-002-001/README.md): `{"depth": 1}` scored **6.85**, retaining **8.12**. The `traversal-depth` mechanism records **2 / 3 consecutive evaluable misses** and the family **2 / 65 claims**. [Paired applications/categories](evolution/e14/graphify-generation-002-001/groups.md) and [CTA](evolution/e14/graphify-generation-002-001/cta.md) preserve this observation.

[Turso generation 4](evolution/e14/turso-generation-004-001/README.md): `{"b": 0.25, "engine": "bm25"}` scored **66.80**, retaining **72.13**. The `length-normalization` mechanism records **1 / 3 consecutive evaluable misses** and the family **5 / 55 claims**. [Paired applications/categories](evolution/e14/turso-generation-004-001/groups.md) and [CTA](evolution/e14/turso-generation-004-001/cta.md) preserve this observation.

[Adaptive reaches three normalization misses](evolution/e14/adaptive-generation-003-001/README.md): construction `bm25.b=0.5` scored **65.78**, below retained **66.21**. This is the third consecutive unique evaluable miss in the mechanism, with **22 / 100 claims**. Its other search opportunities remain open. [Paired applications/categories](evolution/e14/adaptive-generation-003-001/groups.md) and [CTA](evolution/e14/adaptive-generation-003-001/cta.md) preserve the measured result. The retained six-family ranking is unchanged.

[New qualified EnterpriseRAG observations](evolution/e14/turso-003-adaptive-002-observations-001/README.md): Turso `k1=3.0` scored 71.13 versus retained 72.13; Adaptive `bm25.b=0.0` scored 62.31 versus retained 66.21. Both add one new proposal, with zero errors and retries. The eight-family retained ranking is unchanged.

[Latest Graphify development observation](evolution/e14/graphify-generation-001-001/README.md): consultation `depth=0` scored **7.03** versus retained **8.12**, with no execution error or retry. This is the first evaluable miss in its traversal-depth mechanism. The retained ranking, including Turso's 72.13 incumbent, is unchanged.

[Latest EnterpriseRAG gain](evolution/e14/turso-generation-002-001/README.md): Turso now retains **72.13** after the qualified `k1=2.0` observation. The primary-metric gain is 0.04949 points, with secondary-metric regressions and no promotion. [Updated retained comparison by application and category](evolution/e14/turso-generation-002-001/comparison.md).

[Earlier EnterpriseRAG evolution observations](evolution/e14/generation-001-pending-variants-001/README.md): Turso's pending variant scored 69.31 versus its retained 72.08; Adaptive's scored 64.53 versus 66.21. Both qualified and count as one evaluable miss each. The eight-family retained comparison is unchanged.

Reviewed results organized by dataset, skill, and cost/time/quality (CTA).

[By skill](skills/README.md) · [CTA](cta/README.md) · [Evolution studies](evolution/README.md) · [Report catalog](../COMPARISON-REPORTS.md)

[Latest EnterpriseRAG starting outcomes](evolution/e14/starting-execution-errors-001/README.md): Entity Graph timed out after 3,600 seconds; Ensemble encountered an out-of-memory event under the fixed 6 GiB limit. Both remain unqualified, with unavailable retrieval scores and unexercised evolution hypotheses. The six qualified starting scores are unchanged; execution errors are not mutation quality misses.

[EnterpriseRAG cross-family comparison: six qualified retained profiles by application, question category and CTA](evolution/e14/turso-generation-002-001/comparison.md).

The latest [EnterpriseRAG E14 checkpoint](evolution/e14/README.md) completes **six of eight current starting qualifications: Legacy, Turso, Adaptive, Embeddings, Classical and Graphify**. Classical's two new jobs reproduce **55.04** for the reference and **62.10 weighted nDCG@10 x100** for the retained profile. Its recorded catalog stop and inherited charges remain preserved. The other retained scores are unchanged. All ten native records included in the six family reports are qualified and error-free; there is no new champion. See the [eight-family comparison and remaining opportunities](evolution/e14/classical-starting-qualified-001/README.md#retained-eight-family-comparison), [Classical CTA](evolution/e14/classical-starting-qualified-001/cta.md), [nine-application and ten-category breakdown](evolution/e14/classical-starting-qualified-001/groups.md) and [dataset view](datasets/enterprise-rag-stratified-development-120.md). Five inherited searches, the all-500 comparison and independent acceptance remain incomplete.

The earlier [EnterpriseRAG E13 report](evolution/e13/README.md) preserves the completed **45.43** Turso reference and a subsequent cache phase-declaration controller stop. Its four stages are closed and verified. The original measurement remains consumed; E14 reuses it under the same identity.

The earlier [EnterpriseRAG E12 checkpoint](evolution/e12/README.md) stopped before native allocation because its controller treated a template path as a loaded configuration. The four stages are closed and verified. A separate correction passed nine integration tests with the actual native configuration API; no new benchmark score, quality miss or first measurement resulted. Its [retained comparison](evolution/e12/preallocation-failure-001/README.md#retained-enterpriserag-comparison), [CTA](evolution/e12/preallocation-failure-001/cta.md) and [dataset availability](evolution/e12/preallocation-failure-001/groups.md) preserve that earlier checkpoint.

The original [EnterpriseRAG continuation E11](evolution/e11/README.md) stopped after [twelve starting roles settled](evolution/e11/starting-terminal-001/README.md): ten qualified across six families, while Ensemble exceeded 6 GiB and Entity Graph timed out. All nine required historical scores reproduced exactly; the [CTA](evolution/e11/starting-terminal-001/cta.md) separates nine new jobs from three E10 imports. Five family searches and final acceptance remain unfinished. The earlier E8 [five-family matrix](evolution/e8/retained-cross-family-002/README.md) preserves retained development profiles by application and category, including the first [Turso gain](evolution/e8/turso-progress-001/README.md). These partial results do not enter the final all-500 table.

The new [Entity evidence-index candidate](evolution/e11/entity-evidence-index-reuse-001/README.md) passed nine software checks and reproduced all 48 retained public runtime responses. Observed profiled query time changed from 7.785 to 6.579 seconds with one evidence-index build. Its [eight-family context](evolution/e11/entity-evidence-index-reuse-001/README.md#retained-enterpriserag-comparison) preserves all six native scores and records 91 charged proposals. The new native measurement is unassigned. See [CTA](evolution/e11/entity-evidence-index-reuse-001/cta.md) for the software timing scope.

The latest [Entity traversal adjacency native outcome](evolution/e11/entity-traversal-adjacency-reuse-native-001/README.md) settled without a qualified retrieval score. The workload remains 120 stratified questions, 112 retrieval-eligible questions and 6,000 complete documents. Its [eight-family comparison](evolution/e11/entity-traversal-adjacency-reuse-native-001/README.md#eight-family-comparison) preserves the six previous qualified scores; [opportunity accounting](evolution/e11/entity-traversal-adjacency-reuse-native-001/README.md#opportunity-accounting) distinguishes completed attempts, unavailable originals and pending measurements. See [application/category results](evolution/e11/entity-traversal-adjacency-reuse-native-001/groups.md) and [CTA](evolution/e11/entity-traversal-adjacency-reuse-native-001/cta.md). The checkpoint accounts for 90 proposals and nine consumed construction first measurements. Five family searches, the all-500 comparison and independent whole-bundle acceptance remain unfinished.

The [earlier traversal software checkpoint](evolution/e11/entity-traversal-adjacency-reuse-001/README.md) preserves eight software checks, 48 exact reference responses and the observed profiled query-time change from 15.727 to 7.785 seconds. Its native status was unassigned at that checkpoint; the native outcome above supersedes that status. See [software CTA](evolution/e11/entity-traversal-adjacency-reuse-001/cta.md) for the limited timing scope.

The previous [Entity consultant eligibility native outcome](evolution/e11/entity-consultant-ngram-eligibility-native-001/README.md) records another 3,600-second timeout. Both build logs and both standalone validation logs reported success, but no qualified retrieval score was produced. Its [eight-family comparison](evolution/e11/entity-consultant-ngram-eligibility-native-001/README.md#eight-family-comparison), [application/category availability](evolution/e11/entity-consultant-ngram-eligibility-native-001/groups.md) and [CTA](evolution/e11/entity-consultant-ngram-eligibility-native-001/cta.md) preserve the six retained scores and the unavailable Entity/Ensemble measurements. Claims remain 89 of 585; all eight construction first measurements are consumed. Five searches, the all-500 comparison and independent acceptance remain unfinished.

The preceding [software and runtime checkpoint](evolution/e11/entity-consultant-ngram-eligibility-001/README.md) preserves seven passed software checks and exact deep-validation parity on a retained 1,024-record snapshot. These checks do not establish a native retrieval gain.

The earlier [Entity Graph builder lifetime native outcome](evolution/e11/entity-memory-lifetime-native-001/README.md) records a 3,600-second timeout without a ranking, with 88 cumulative proposals and seven consumed construction attempts. Both complete build logs and both independent validator logs reported success before the timeout. Its [eight-family comparison](evolution/e11/entity-memory-lifetime-native-001/README.md#eight-family-comparison), [application/category availability](evolution/e11/entity-memory-lifetime-native-001/groups.md) and [CTA](evolution/e11/entity-memory-lifetime-native-001/cta.md) preserve retained results and missing evidence. No final all-500 result or canonical skill promotion is established by this component evaluation.

The [stratified Enterprise evolution E7](evolution/e7/README.md) records the original eight-family work on 120 development questions and 6,000 complete documents. Its [strategy coverage](evolution/e7/strategy-coverage.md) distinguishes declared mechanisms, native attempts and completed searches. Later continuations preserve those attempts and limits; interim development scores do not enter the completed all-500 comparison table.

The earlier [Enterprise evolution sweep E6](evolution/e6/README.md) follows eight knowledge families through a fixed tactic catalog, with three consecutive misses per tactic and a separate final validation gate. Its campaign page records the execution and publication status.

The [agent-selected source-skill comparison](enterprise-source-skills/README.md) evaluates a unified expert and nine application experts with complete document bodies. The [ingestion scope correction](enterprise-source-skills/ingestion-scope-20260907.md) binds historical Enterprise v1/e6 retrieval to a title-only projection. Do not pool the two contracts.

The [knowledge-skill generator evolution](evolution/generator-g2/README.md) compares explicit source selection and normalized coverage auditing with the incoming generator, using a separate independent construction gate. Its metric is not a retrieval or answer score.

The [EnterpriseRAG generator replay](enterprise-generator-g2/README.md) compares the incoming and G2 versions on identical complete documents, with family, category and CTA views.

The [full-corpus Classical run](enterprise-classical-full/README.md) covers all 511,962 documents and 500 questions. Only Classical BM25 is measured; its retrieval result does not establish an official answer-quality score or public-table position.

The [internal Luna answer evaluation](enterprise-classical-full/luna.md) reuses that full-corpus retrieval with Luna for both answering and judging; its score is separate from the public GPT-5.4 judge contract.

The earlier [construction-profile study](evolution/e5/README.md) records controlled comparisons across EnterpriseRAG, Astro, architecture and data science. Its reports provide skill, profile, dataset and CTA views, with completion status and independent-validation availability kept explicit.

## Historical retrieval comparisons

The table identifies the highest observed primary metric within each published contract. Ties at the source's precision are preserved. These are retrieval measurements; generated-answer correctness, promotion, and a universal cross-dataset winner are not established.

| Dataset | Highest observed skill / route | Primary metric | Value |
|---|---|---|---:|
| [GraphRAG generalization (60)](datasets/graphrag-papers-parallel-eval-60-v1.md) | classical / Classical association | nDCG@10 | 99.60% |
| [GraphRAG contradictions (40)](datasets/graphrag-papers-contradiction-eval-40-v1.md) | specialized-expert / Specialized expert early confidence-gated hybrid | Full evidence@10 | 92.50% |
| [Software architecture books (40)](datasets/software-architecture-books-40.md) | classical / Fusion | nDCG@10 | 92.58% |
| [Data science / AI / ML books (40)](datasets/data-science-ai-ml-books-40.md) | ensemble / Fast | nDCG@10 | 94.44% |
| [Astro documentation (40)](datasets/astro-40.md) | classical / association; adaptive / association | nDCG@10 | 83.50% |
| [Endocrine hygiene](datasets/endocrine-hygiene.md) | classical / bm25; adaptive / bm25 | nDCG@10 | 95.30% |
| [Quantum error correction (40)](datasets/quantum-error-correction-papers-40.md) | specialized-expert / retrospective-supervised-ngram | nDCG@10 | 100.00% |
| [tau3 banking knowledge (97)](datasets/tau3-banking-knowledge-97.md) | integrated-classical / Local topic | nDCG@10 | 42.90% |
| [EnterpriseRAG reduced corpus (40)](datasets/enterprise-rag-bench-40-v1.md) | entity-graph / Lexical | nDCG@10 | 59.40% |
| [EnterpriseRAG e6 development (40)](datasets/enterprise-rag-e6-development-40.md) | embeddings / baseline / hybrid | nDCG@10 | 63.19% |
| [EnterpriseRAG complete documents: incoming / G2 (40)](datasets/enterprise-rag-generator-g2-fulltext-40.md) | ensemble / Incoming / Quality; ensemble / G2 / Quality | nDCG@10 | 97.86% |
| [EnterpriseRAG full corpus: Classical (500)](datasets/enterprise-rag-classical-full-500.md) | classical / Classical / BM25 | nDCG@10 | 59.03% |
| [EnterpriseRAG stratified development (120; partial)](datasets/enterprise-rag-stratified-development-120.md) | legacy / retained development profile | Weighted nDCG@10 | 72.38% |

Historical reports keep their original source locations and meanings. The hub reads only reviewed aggregate sources and does not reopen sealed tasks. Latency and costs from different hosts, cache policies, models, or cohorts must be interpreted separately.

[Data storage and reproduction](../../docs/evaluation-datasets-and-reports.md)
