# Manual answer review: GraphRAG papers consultation campaign

This append-only review audits campaign `20260717-papers-consult-gpt53-spark-01`. It does not alter the 320 raw Harbor results. The campaign is structurally complete but invalid for strategy comparison because only 32 trials emitted a complete final response; all 80 hard-question trials ended at the provider quota boundary.

## Review method

- Scope: every one of the 32 traces classified as `answer-emitted` by the terminal Pi trace classifier.
- Questions q001–q030: compare the answer against every authored `required_point` in the pinned paper blueprint and the original `min_papers` threshold.
- Questions q031–q040: compare against hard answer claims, derivations, acceptable variants, and important negatives. No hard response was available to review.
- Conservative point rule: a required point counts only when the answer addresses all material clauses.
- Semantic pass rule: every required point is covered and the original relevant-document minimum is met.
- Protocol shorthand: `C` is the closed response contract, `R` is evidence first-use order, and `E` is exact valid evidence rows. `Docs` counts qrel-mapped document identities; an identity can remain observable even when the corresponding evidence row violates the closed locator/hash contract.

This is a documented manual adjudication, not a blinded independent judge run. It is suitable for diagnosing the failed campaign but not for publishing a family ranking.

## Results

| Family | Question | Docs/min | Points | Missing required themes | Protocol observation | Semantic verdict |
|---|---|---:|---:|---|---|---|
| Adaptive | q002 | 5/6 | 1/4 | Schema and pre-existing inputs; community/generated-query/fused retrieval; updateability and task-scope trade-offs | C yes; R no; E 12/12 | Partial |
| Adaptive | q003 | 2/6 | 1/4 | Community/topology evidence; task overlap and sensemaking/fact verification; extraction cost/error versus schema/coverage constraints | C yes; R yes; E 7/7 | Partial |
| Adaptive | q010 | 5/6 | 2/4 | Complete report/subgraph/path/chunk/memory comparison; abstraction and token-budget trade-offs | C yes; R yes; E 9/9 | Partial |
| Adaptive | q015 | 5/5 | 2/4 | Deduplication, mutual indexes, schema/community maintenance; cost and error accumulation | C no; R yes; E 0/11, scalar locator and invalid text hash | Partial |
| Adaptive | q025 | 3/4 | 4/4 | No semantic theme missing; insufficient cross-paper breadth | C no; R yes; E 0/18, scalar locator | Partial |
| Classical | q003 | 2/6 | 1/4 | Community/topology evidence; task overlap; construction cost/error versus supplied-graph constraints | Corrected C yes; R yes; E 15/15. Historical grader imposed undeclared evidence-member order. | Partial |
| Classical | q005 | 2/4 | 3/4 | Redundancy, token cost, abstraction, and local-detail loss are only lightly treated | C yes; R yes; E 14/14 | Partial |
| Classical | q010 | 5/6 | 3/4 | Token-budget and abstraction-loss trade-offs | C yes; R yes; E 9/9 | Partial |
| Classical | q020 | 4/5 | 1/4 | Domain-specific risk/type/task choices; reusable context/generation patterns; transfer cost and ontology/benchmark mismatch | C yes; R no; E 6/9, three path transcription errors | Partial |
| Classical | q025 | 1/4 | 3/4 | Leakage/unrelated-question effects and LLM-judge bias | C yes; R no; E 1/16, fifteen source-path transcription errors | Partial |
| Classical | q029 | 2/6 | 3/4 | Nondeterminism, error propagation, and the full latency/token trade-off | C yes; R yes; E 7/7 | Partial |
| Embeddings | q003 | 2/6 | 2/4 | Task overlap and sensemaking/fact verification; extraction cost/error versus schema/coverage | C yes; R yes; E 14/14 | Partial |
| Embeddings | q005 | 4/4 | 3/4 | Redundancy, abstraction, and local-detail loss | C yes; R no; E 14/14 | Partial |
| Embeddings | q010 | 6/6 | 1/4 | Full context-unit comparison; original chunks/excerpts for fidelity; redundancy, abstraction, and token budgets | C yes; R yes; E 14/14 | Partial |
| Embeddings | q025 | 1/4 | 3/4 | LLM-judge, leakage, and unrelated-question bias | C no; R yes; E 5/6, one copied hash error | Partial |
| Entity graph | q015 | 5/5 | 2/4 | Deduplication, mutual indexes, schema/community maintenance; cost and error accumulation | C no; R yes; E 0/10, scalar locator | Partial |
| Entity graph | q020 | 4/5 | 2/4 | Domain-specific risk/type/task choices; transfer cost and ontology/benchmark mismatch | C no; R yes; E 1/5, record/text-hash errors | Partial |
| Entity graph | q025 | 2/4 | 2/4 | Explicit LLM-judge/leakage analysis; separate construction/retrieval/generation evaluation | C yes; R yes; E 4/6, two concept-path errors | Partial |
| Entity graph | q029 | 0/6 | 3/4 | Nondeterminism/error propagation; no evidence emitted | C no; R no; E 0/0, missing top-level evidence | Fail |
| Legacy | q001 | 14/8 | 2/4 | Distinct diffusion and agentic families; hybrids and benchmark paper; answer overstates clean exclusivity | C no; R yes; E 0/41, scalar provenance locators | Partial |
| Legacy | q002 | 6/6 | 2/4 | LLM/classical/schema contrast; accuracy, cost, and updateability trade-offs | C no; R no; E 0/33, scalar locators and row order | Partial |
| Legacy | q004 | 4/7 | 0/4 | Precision/fragmentation; path/subgraph search cost; abstraction/local-detail loss; hybrid multi-granular retrieval | C no; R no; E 0/11, scalar locators and row order | Partial |
| Legacy | q007 | 4/4 | 3/4 | Agentic, query-conditioned sequential traversal | C no; R yes; E 0/18, scalar provenance locators | Partial |
| Legacy | q005 | 4/4 | 2/4 | Explicit summary-generation process; abstraction/redundancy/token/local-detail trade-offs | C no; R yes; E 0/14, scalar provenance locators | Partial |
| Legacy | q010 | 2/6 | 2/4 | Community reports/partial answers and subgraphs; redundancy, abstraction, and token budgets | C no; R yes; E 0/8, scalar provenance locators | Partial |
| Legacy | q015 | 5/5 | 3/4 | Deduplication, mutual indexes, schema, and community-maintenance mechanics | C no; R no; E 0/10, scalar locators and row order | Partial |
| Turso | q005 | 3/4 | 3/4 | Full abstraction, token-cost, and local-detail-loss trade-off | C no; R no; E 0/22, scalar locators and row order | Partial |
| Turso | q010 | 3/6 | 2/4 | Community reports/subgraphs; abstraction and token-budget trade-offs | C no; R yes; E 0/10, scalar locators | Partial |
| Turso | q015 | 5/5 | 3/4 | Deduplication, mutual indexes, schema, and community maintenance | C no; R no; E 0/12, scalar locators and row order | Partial |
| Turso | q020 | 4/5 | 2/4 | Domain-specific risk/type/task choices; transfer cost and ontology/benchmark mismatch | C no; R no; E 0/30, scalar locators and row order | Partial |
| Turso | q025 | 4/4 | 3/4 | Leakage or unrelated-question effects are not explicitly analyzed | C no; R yes; E 0/20, scalar locators | Partial |
| Turso | q029 | 5/6 | 3/4 | Nondeterminism and error-propagation trade-offs | C no; R yes; E 0/13, scalar locators | Partial |

## Adjudication summary

| Outcome | Count |
|---|---:|
| Complete final responses reviewed | 32 |
| Semantic pass | 0 |
| Semantic partial | 31 |
| Semantic fail | 1 |
| Original relevant-document minimum met | 11 |
| All required points covered | 1 |
| Hard-question responses available | 0 |

Adaptive q025 is the only answer that covers all four authored points, but it cites only three of the four required relevant documents and therefore remains partial. Embeddings q010 is the only historically reported gate pass that also meets its six-paper minimum, but it covers only one of four semantic points under the conservative review.

The truncated Embeddings q020 trace is excluded because its terminal `stopReason` is `length`; it is not a complete final response even though partial JSON text exists.

## Evaluator corrections established by this review

1. The historical `quality_gate` measured response/evidence mechanics, not answer correctness. It is replaced by explicitly mechanical gates.
2. Six of seven historical gate passes fail the original paper minimum because the Harbor adapter dropped that requirement.
3. Classical q003 was a verifier false negative: the response schema and prompt did not require evidence-object member order. The corrected grader accepts its 15 exact rows, but the answer still fails the six-paper minimum and semantic rubric.
4. Hard anchor coverage cannot be called atomic-claim or negative semantic completeness because the deterministic scorer never tests candidate entailment. The corrected metric names say `anchor_coverage`.
5. No semantic family comparison is possible from this campaign. A fresh append-only run needs 40 evaluable responses per family followed by blinded semantic review.
