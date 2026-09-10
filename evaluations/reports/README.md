# Evaluation report hub

Reviewed results organized by dataset, skill, and cost/time/quality (CTA).

[By skill](skills/README.md) · [CTA](cta/README.md) · [Evolution studies](evolution/README.md) · [Report catalog](../COMPARISON-REPORTS.md)

The [EnterpriseRAG continuation E11](evolution/e11/README.md) stopped after [twelve starting roles settled](evolution/e11/starting-terminal-001/README.md): ten qualified across six families, while Ensemble exceeded 6 GiB and Entity Graph timed out. All nine required historical scores reproduced exactly; the [CTA](evolution/e11/starting-terminal-001/cta.md) separates nine new jobs from three E10 imports. Five family searches and final acceptance remain unfinished. The earlier E8 [five-family matrix](evolution/e8/retained-cross-family-002/README.md) preserves retained development profiles by application and category, including the first [Turso gain](evolution/e8/turso-progress-001/README.md). These partial results do not enter the final all-500 table.

The subsequent [Entity Graph token-automaton native outcome](evolution/e11/entity-token-automaton-native-001/README.md) records the original fixed measurement with 85 cumulative proposals. Its [eight-family comparison](evolution/e11/entity-token-automaton-native-001/README.md#eight-family-comparison), [application/category availability](evolution/e11/entity-token-automaton-native-001/groups.md) and [CTA](evolution/e11/entity-token-automaton-native-001/cta.md) preserve qualified results and missing evidence. No final all-500 result or canonical skill promotion is established by this component evaluation.

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

Historical reports keep their original source locations and meanings. The hub reads only reviewed aggregate sources and does not reopen sealed tasks. Latency and costs from different hosts, cache policies, models, or cohorts must be interpreted separately.

[Data storage and reproduction](../../docs/evaluation-datasets-and-reports.md)
