# GraphRAG 40-question best-answer second-pass review

## Outcome

Forty independent question assignments rechecked all **175** locally reviewable historical responses, **200** authored semantic targets, and all **94** hard-question evidence anchors.

The review retained **26** answers and replaced **14**. Every verdict and every final response passed exact contract, ledger-identity, first-use order, independent-document, and hard-anchor validation.

This is curated evaluator reference material, not a live Harbor model campaign and not empirical performance evidence.

## Question decisions

| Question | Verdict | History | Targets | Evidence / documents | Hard anchors |
|---|---:|---:|---:|---:|---:|
| q001 | keep | 3 | 4 | 15 / 15 | 0 |
| q002 | keep | 35 | 4 | 8 / 8 | 0 |
| q003 | keep | 37 | 4 | 8 / 8 | 0 |
| q004 | keep | 31 | 4 | 11 / 11 | 0 |
| q005 | keep | 10 | 4 | 5 / 5 | 0 |
| q006 | keep | 1 | 4 | 6 / 6 | 0 |
| q007 | keep | 2 | 4 | 5 / 5 | 0 |
| q008 | keep | 1 | 4 | 13 / 6 | 0 |
| q009 | revise | 1 | 4 | 6 / 6 | 0 |
| q010 | revise | 9 | 4 | 19 / 7 | 0 |
| q011 | keep | 1 | 4 | 14 / 7 | 0 |
| q012 | revise | 1 | 4 | 9 / 9 | 0 |
| q013 | keep | 1 | 4 | 17 / 7 | 0 |
| q014 | keep | 1 | 4 | 10 / 10 | 0 |
| q015 | revise | 8 | 4 | 7 / 7 | 0 |
| q016 | keep | 1 | 4 | 16 / 10 | 0 |
| q017 | keep | 1 | 4 | 23 / 8 | 0 |
| q018 | keep | 1 | 4 | 9 / 9 | 0 |
| q019 | keep | 1 | 4 | 14 / 6 | 0 |
| q020 | keep | 7 | 4 | 7 / 7 | 0 |
| q021 | revise | 1 | 4 | 10 / 7 | 0 |
| q022 | keep | 1 | 4 | 6 / 6 | 0 |
| q023 | keep | 1 | 5 | 20 / 11 | 0 |
| q024 | keep | 1 | 4 | 24 / 8 | 0 |
| q025 | keep | 9 | 4 | 5 / 5 | 0 |
| q026 | revise | 1 | 4 | 15 / 9 | 0 |
| q027 | revise | 1 | 4 | 6 / 6 | 0 |
| q028 | revise | 0 | 4 | 19 / 8 | 0 |
| q029 | revise | 6 | 4 | 9 / 9 | 0 |
| q030 | revise | 1 | 5 | 35 / 15 | 0 |
| q031 | revise | 0 | 7 | 3 / 3 | 6 |
| q032 | keep | 0 | 9 | 5 / 5 | 7 |
| q033 | keep | 0 | 7 | 3 / 3 | 8 |
| q034 | keep | 0 | 7 | 4 / 4 | 6 |
| q035 | keep | 0 | 7 | 4 / 4 | 8 |
| q036 | revise | 0 | 9 | 4 / 4 | 9 |
| q037 | revise | 0 | 9 | 3 / 3 | 19 |
| q038 | keep | 0 | 7 | 4 / 4 | 12 |
| q039 | keep | 0 | 8 | 4 / 4 | 8 |
| q040 | revise | 0 | 8 | 4 / 4 | 11 |

## Corrections

### q009

**Findings:**

- KAG's faster LFS variant is not graph-only: it uses subgraph answers when available and supporting_chunks when graph reasoning yields no result, whereas LFSH disables Graph Retrieval and uses Hybrid Retrieval for all answers.
- The current answer groups call limits, traversal depth, retries, and no-agent operation into a generic coverage-for-cost claim; the records directly establish those bounds, the retry quality-efficiency balance, and the no-agent complex-reasoning degradation, but do not report one common coverage effect for every control.

**Applied changes:**

- Describe KAG as a graph-first logical-form solver with chunk fallback, and state its reported speed-versus-incomplete-SPO accuracy trade-off relative to the all-Hybrid-Retrieval variant.
- Present GraphReader's call cap, Youtu-GraphRAG's DFS depth cap and no-agent variant, and PolyG's retry cap as distinct controls, reserving measured performance claims for the no-agent ablation and Cypher repair trade-off.

### q010

**Findings:**

- The source-fidelity paragraph and claim add qualifiers and loss from community compression or summarization, while the cited limitation record specifically supports examples, quotations, and citations that graph extraction may fail to retain.
- The current summary says agent planning and reflection spend intermediate tokens, but the cited KAG record supports planning-stage intermediate-token overhead and does not mention reflection.
- The final sentence calls one synthesized pattern the strongest design even though the cited methods were evaluated in different studies and the reviewed evidence supports workload-dependent trade-offs rather than a universal winner.

**Applied changes:**

- Describe source-text backstops as restoring source detail, including examples, quotations, and citations that graph extraction may omit, without adding unsupported qualifiers or summarization loss.
- Attribute intermediate-token overhead specifically to planning and replace the universal strongest-design conclusion with a workload-dependent balance among relation preservation, compression, deduplication, and source-text fidelity.

### q012

**Findings:**

- The current classical-NLP paragraph overstates the dependency alternative: it avoids expensive LLM triple extraction, but not every API or LLM dependency in the full system, and noun-phrase extraction belongs to query processing rather than graph construction.
- The current online-flexibility paragraph calls shallow modes faster without cited support; the records instead support a lighter no-agent variant and measured single-step-versus-iterative retrieval savings.
- The explainability trade-off is stronger when stated operationally: explicit logical forms, paths, and source links are inspectable, whereas aggregate PPR scores and compressed summaries are not themselves proof traces unless the system preserves the underlying passages and citations.

**Applied changes:**

- Describe the dependency path as a lower-cost alternative to LLM triple extraction, list only its actual construction operations, and explicitly retain embedding and answer-generation costs.
- Replace the unsupported shallow-mode assertion with the cited no-agent and single-step retrieval comparisons, keeping the reported cost and accuracy consequences system-specific.
- Tie explainability to whether paths, logical forms, intermediate state, and original source chunks remain available rather than treating every graph retrieval result as inherently explanatory.

### q015

**Findings:**

- Current claim 1 says incremental approaches add high-confidence schema elements, but its evidence indices omit Youtu-GraphRAG, the cited paper that actually defines confidence- and frequency-gated entity-type, relation-type, and attribute-type expansion.
- The current wording blends implemented addition mechanisms with inferred requirements for corrections and deletions. The papers support the engineering inference, but the stronger formulation is that the cited addition protocols do not establish end-to-end propagation of source corrections or retractions across every derived representation.

**Applied changes:**

- Bind confidence-gated schema expansion and construction/retrieval schema agreement explicitly to the Youtu-GraphRAG evidence row, while keeping LightRAG, HippoRAG, and ROGRAG attached to their documented incremental mechanisms.
- Separate directly implemented behavior from consistency requirements, and state correction/retraction handling as a protocol gap that limits freshness guarantees for removals.

### q021

**Findings:**

- Claim 3 and the summary list Hit@1 as a QA evaluation metric, but none of claim 3's cited ranges contains or establishes Hit@1.
- Claim 3 says fact-checking measures source reliability, while the exact MedGraphRAG range establishes an evidence-based reliability objective, validation on health fact-checking benchmarks, and inclusion of credible source documentation and definitions, not a distinct source-reliability measurement.

**Applied changes:**

- Remove Hit@1 from the evaluation comparison because answer accuracy, exact match, and F1 already satisfy the QA criterion with exact support.
- Describe the fact-checking evidence criterion as classification accuracy plus checking for credible, source-documented support rather than as a measured source-reliability score.

### q026

**Findings:**

- The current summary says that a defensible faithfulness claim needs causal intervention or ablation when actual evidence use is asserted, but none of its 15 cited ledger records establishes such a causal-use test; the cited evidence supports provenance, downstream synthesis separation, prompt leakage, and pre-generation context-support checking instead.

**Applied changes:**

- Replace the unsupported intervention-or-ablation prescription with the supported conclusion that provenance and pre-generation support checks strengthen auditability but still do not prove the generator's causal reliance on the displayed evidence.

### q027

**Findings:**

- The current summary and claim 8 overgeneralize MedGraphRAG's no-link design: only the semantic grouping of separate Meta-MedGraphs avoids cross-graph node links; the underlying graphs themselves contain linked entities and relations.
- The current resolution discussion turns a defensible synthesis into an unqualified causal claim by saying repeated compression loses detail and cross-community questions require aggregation; the records support a possible omission risk and show aggregation or retained path routes as mitigations, but do not provide a dedicated causal ablation.

**Applied changes:**

- Describe MedGraphRAG as clustering tag summaries without adding node links between the grouped Meta-MedGraphs, while preserving its linked entity/triple evidence inside each graph and repository tier.
- Frame fine-detail and cross-community effects as conditional risks of coarse/report-based retrieval and topology-favoring partitions, and tie the mitigation precisely to multi-community aggregation or retained relation/path retrieval.

### q028

**Findings:**

- The phrase "posterior usefulness" overstates what the filtering evidence establishes: the paper supplies thresholded attention and LLM relevance judgments, not a posterior or calibration result.
- The current RRF limitation is imprecise. RRF is explicitly used to fuse graph and dense retrieval, so it can mitigate absent graph-ranked evidence when the dense list contains the candidate; only candidates absent from every fused list are unrecoverable.
- The current wording partially conflates the broader high-recall/precision-oriented cascade with RRF itself; RRF's narrower objective is rank-based fusion that balances the structural and semantic result lists.

**Applied changes:**

- Describe filtering as an operational relevance/noise gate under context and evaluation-cost constraints, without probabilistic terminology.
- Describe RRF as rank-based structural-semantic fusion and state its recall limit as absence from both input rankings.
- Keep the determinism comparison explicitly layered: fixed numerical operators and executed queries are conditionally reproducible, while LLM planning, judging, routing, and repair add adaptability without the same operator-level guarantee.

### q029

**Findings:**

- The current summary and claim 3 state that repeated LLM-controlled branches reduce reproducibility and produce more run-to-run variability without saying that this is an inference; the current output's own caveat acknowledges that the cited corpus does not directly measure nondeterminism.

**Applied changes:**

- Separate directly measured latency and token costs and explicitly documented error propagation from the inferred nondeterminism risk, and state that the cited studies do not quantify run-to-run variability.

### q030

**Findings:**

- The current construction and graph-quality claims turn plausible design inferences into general rules: their cited rows establish reuse, schema bounds, provenance, extraction errors, and build cost, but claim 1 does not cite the available exact graph-versus-hybrid text fallback record.
- The current safety claim says parametric reasoning should be used in lower-risk modes and be calibrated, while its cited records only establish open versus reject prompting and complementarity; the exact independent-confidence-threshold integration record is omitted.
- The current evaluation claim promises robustness testing with missing evidence but cites only injected noisy paths, and its operational source-link phrase is attached to evidence that supports tables and paths rather than provenance links.

**Applied changes:**

- Use the exact reuse and construction gates and add claim-2409-13731v3-016 for the structured-versus-hybrid graph-and-text fallback.
- Distinguish declared open and reject policies without inferring a lower-risk category, and cite claim-2503-13804v1-044 for separate confidence-threshold integration.
- Add claim-2402-07630v3-056 for the missing-evidence versus distracting-context robustness tradeoff, and attach source-link explainability to the originating-chunk provenance record.

### q031

**Findings:**

- Claim 5's basic-RAG fallback is not supported by its cited evidence indices [1, 2]; the exact supporting 2506.05690v3 record is evidence index 0. This is a claim-level grounding defect even though that record appears elsewhere in the response.

**Applied changes:**

- Retain the current synthesis and evidence array, but change claim 5's evidence indices to [0, 1, 2] so each component of the fallback boundary is supported by the records cited on that claim.

### q036

**Findings:**

- Claim 5 conflates retrieval-stage success with retrieval-grounded end-to-end success. When audited evidence recall and context relevance are strong but the reject-mode answer is wrong, unfaithful, or needlessly abstains, the retriever succeeded and the generator failed; the current rule would misclassify that case as no retrieval success.

**Applied changes:**

- Retain the staged metrics, paired prompts, contamination/reference control, judge caveat, evidence rows, and deterministic evidence order, but replace the decision rule with an explicit outcome matrix that distinguishes retrieval success, grounded-generation success, parametric-only success, and grounding violations.

### q037

**Findings:**

- The current summary and claim 6 prescribe versioning and adjudication for schema expansion. Youtu-GraphRAG supports feedback-driven schema expansion and use of the same schema at query time, but not those additional process controls.
- The current summary attaches normalization and deduplication specifically to OpenIE promotion and ties OpenIE directly to domain-shift discovery. The KAG anchors support a lower construction threshold plus alignment and multi-round consistency problems; normalization is documented for the dependency pipeline, and the OpenIE/domain-shift linkage is not stated.
- The 61.87% versus 65.83% comparison should be explicitly scoped to the cited paper's evaluated enterprise/code-migration setting rather than read as a corpus-independent expectation.

**Applied changes:**

- Retain the staged cascade but replace unsupported OpenIE controls with the documented knowledge-alignment and repeated-extraction consistency checks.
- Describe feedback-driven schema expansion and same-schema construction/query alignment without adding mandatory versioning or adjudication.
- Qualify the reported dependency-versus-LLM result as setting-specific while preserving all exact evidence identities and their first-use order.

### q040

**Findings:**

- The summary and claim 4 add a provenance-disclosure requirement, but the cited records distinguish graph and LLM-only branches without requiring provenance disclosure in the final answer.
- The ROGRAG accuracy comparison is more precise when qualified as the paper's logic-form retrieval experiment, and NEI should be identified as the fact-verification label while abstention is the grounded answer-policy action.

**Applied changes:**

- Remove the unsupported provenance-disclosure clause while retaining the evidence-backed separation and confidence gating of graph and parametric candidates.
- Qualify the 0.75 versus 0.72 result by its experimental context and state the NEI-label versus abstention-action distinction explicitly.

## Reproducibility

Per-question verdicts and their validator live under `evaluations/runs/graphrag-best-answer-second-pass-20260724/`. Each durable review row records the verdict-file digest and the canonical final-response digest.
