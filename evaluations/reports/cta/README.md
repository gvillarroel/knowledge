# CTA: cost, time, and quality

[Report hub](../README.md) · [By skill](../skills/README.md) · [Enterprise evolution](../evolution/e6/README.md) · [Construction-profile evolution](../evolution/e5/README.md)

[Stratified Enterprise evolution E7](../evolution/e7/README.md) records native development time, qualified retrieval scores and execution errors. Its declared model-call budget is zero; a timed-out attempt has no retrieval quality measurement. Follow the campaign for completion of all eight families, the paired all-500 comparison and the separate transfer gate.

The evolution studies report query P95, two-build construction time, full native execution time and storage under their fixed runtimes. Follow each campaign's execution and publication status. The historical comparisons below retain their own measurement contracts.

CTA is interpreted here as cost, time, and accuracy/quality. Retrieval relevance is measured by nDCG, Recall, MRR, or complete evidence; it is not generated-answer accuracy. Missing USD costs or answer-quality measurements remain N/A.

## Retrieval time and quality by dataset

P95 covers the exact route and runtime described in each source report. Initialization, warm caches, hardware, and corpus sizes vary across historical studies. No cross-host latency winner or cost-to-quality composite is computed.

| Dataset | Highest primary-metric route(s) | P95 (ms), in route order | Provider USD for new local retrieval |
|---|---|---:|---:|
| [GraphRAG generalization (60)](../datasets/graphrag-papers-parallel-eval-60-v1.md) | Classical association | 664.65 | N/A |
| [GraphRAG contradictions (40)](../datasets/graphrag-papers-contradiction-eval-40-v1.md) | Specialized expert early confidence-gated hybrid | 941.60 | N/A |
| [Software architecture books (40)](../datasets/software-architecture-books-40.md) | Fusion | 1832.07 | N/A |
| [Data science / AI / ML books (40)](../datasets/data-science-ai-ml-books-40.md) | Fast | 16155.87 | N/A |
| [Astro documentation (40)](../datasets/astro-40.md) | association; association | 1430.10; 1443.60 | N/A |
| [Endocrine hygiene](../datasets/endocrine-hygiene.md) | bm25; bm25 | 20.60; 26.30 | N/A |
| [Quantum error correction (40)](../datasets/quantum-error-correction-papers-40.md) | retrospective-supervised-ngram | 34.01 | N/A |
| [tau3 banking knowledge (97)](../datasets/tau3-banking-knowledge-97.md) | Local topic | N/A | N/A |
| [EnterpriseRAG reduced corpus (40)](../datasets/enterprise-rag-bench-40-v1.md) | Lexical | 83.17 | 0.00 |
| [EnterpriseRAG e6 development (40)](../datasets/enterprise-rag-e6-development-40.md) | embeddings / baseline / hybrid | 171.35 | N/A |
| [EnterpriseRAG complete documents: incoming / G2 (40)](../datasets/enterprise-rag-generator-g2-fulltext-40.md) | Incoming / Quality; G2 / Quality | 2838.14; 2839.98 | N/A |
| [EnterpriseRAG full corpus: Classical (500)](../datasets/enterprise-rag-classical-full-500.md) | Classical / BM25 | 286.40 | N/A |

## Historical agent token usage: construction

These are actual agent tokens on the GraphRAG construction contract, not dollar prices. All eight arms produced two qualified folders under the same published model and runtime.

[Exact contract and original report](../../../evaluations/semantic-okf-datasets/reports/20260730-semantic-okf-token-usage.md)

| Skill | Calls | Qualified | Mean tokens / folder |
|---|---:|---:|---:|
| Classical | 2 | 2/2 | 5,734.50 |
| Entity Graph | 2 | 2/2 | 6,299.00 |
| Embeddings | 2 | 2/2 | 6,543.00 |
| Adaptive | 2 | 2/2 | 6,882.00 |
| Legacy | 2 | 2/2 | 7,003.50 |
| Ensemble | 2 | 2/2 | 7,291.00 |
| Turso | 2 | 2/2 | 8,557.00 |
| Graphify | 2 | 2/2 | 9,836.00 |

## Historical agent token usage: consultation

Every family received the same six questions. Runtime errors remain visible in the denominator. The complete zero-error arms are Legacy and Turso; early failures cannot establish efficiency.

| Skill | Queries | Complete | Runtime errors | Mean tokens / submitted query |
|---|---:|---:|---:|---:|
| Graphify | 6 | 0 | 6 | 325,279.00 |
| Ensemble | 6 | 0 | 6 | 1,099,499.50 |
| Embeddings | 6 | 5 | 1 | 1,397,144.33 |
| Classical | 6 | 5 | 1 | 1,539,005.33 |
| Legacy | 6 | 6 | 0 | 1,585,536.83 |
| Adaptive | 6 | 4 | 2 | 1,871,644.67 |
| Turso | 6 | 6 | 0 | 2,109,545.83 |
| Entity Graph | 6 | 3 | 3 | 2,433,148.67 |

Harbor input already includes cached input; total is input plus output. Deterministic EnterpriseRAG retrieval used zero model calls and zero LLM tokens. Local machine cost was not measured.

## Generated-answer quality

Use the [comparison catalog](../../COMPARISON-REPORTS.md) for the current isolated semantic audit and the incomplete historical multi-family campaigns. Those results have separate cohort and evidence gates; they are not pooled with document-retrieval scores.

[Agent-selected Enterprise source skills and their separate answer/CTA contract](../enterprise-source-skills/README.md)

[Knowledge-skill generator: deterministic construction quality and execution cost](../evolution/generator-g2/README.md)

[EnterpriseRAG generator replay: fixed full-text retrieval and construction costs](../enterprise-generator-g2/cta.md)

[EnterpriseRAG full corpus: Classical construction, 500-query latency and separate answer-stage usage](../enterprise-classical-full/cta.md)

[Turso E8: original SQL baseline versus retained BM25 candidate, build time and query latency](../evolution/e8/turso-progress-001/cta.md)

[Classical E8: title-weight regression versus the retained incumbent, build time and query latency](../evolution/e8/classical-progress-001/cta.md)

[Classical E8: zero-expansion gain, paired quality and native execution time](../evolution/e8/classical-progress-002/cta.md)
