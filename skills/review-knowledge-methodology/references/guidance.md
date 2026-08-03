# Paper-Grounded Knowledge Methodology Review

## Scope

Review methods for acquiring, extracting, representing, retrieving, evaluating, evolving, and publishing knowledge artifacts in this repository. Support architecture reviews, experiment design, dataset governance, retrieval evaluation, ontology and knowledge-graph decisions, and skill-evolution controls. Treat the bundled 47-paper snapshot as the external research authority. Treat repository documents and results as the implementation under review, not as independent evidence that a method is scientifically sound. Exclude claims about papers outside the snapshot, legal conclusions, and implementation changes not explicitly requested by the user.

## Application workflow

1. Verify the embedded expert binding before consulting the corpus.
2. Translate the review request into one or more of the dataset competency questions.
3. Discover exact paper records with the query helper before opening full concepts.
4. Inspect the repository artifact that implements the practice being reviewed.
5. Build an evidence table containing current practice, paper finding, exact bundled concept path and PDF page, agreement or tension, and confidence.
6. Separate direct paper findings from cross-paper synthesis and repository-specific inference.
7. Produce a prioritized proposal with expected benefit, implementation cost, risks, and a falsifiable validation plan.
8. Identify the repository controls that should remain unchanged when the evidence supports them.

## Decision rules

- Require exact versioned arXiv identities and page locators for material research claims. Do not cite only a title, abstract, or unversioned identifier when the full paper is present.
- Prefer convergent evidence from multiple papers or a benchmark plus a diagnostic framework. Label single-paper recommendations accordingly.
- Keep retrieval quality, evidence validity, answer quality, ontology conformance, and reproducibility as separate outcomes.
- Require lexical, semantic, and hybrid retrieval baselines when evaluating a new retrieval treatment; compare quality, latency, index size, and cross-domain behavior.
- Treat fixed chunking or hierarchy choices as hypotheses. Test them by source type and question type while holding raw inputs, evaluation cases, and consultation policy constant.
- Keep development, validation, and holdout evidence disjoint. Any result inspected during adaptation becomes development evidence and cannot support a later unseen-query claim.
- Require repeated runs and uncertainty reporting for stochastic models or judges. Deterministic artifact reconstruction does not remove answer-generation variance.
- Calibrate model-based judges against blinded human review before using them for promotion decisions.
- Keep ontology axioms, SHACL acceptance rules, extracted claims, and operational policy distinct. Do not turn observed corpus regularities into universal semantics.
- Prefer append-only evidence and frozen digests. Change one primary evolution controller per development stage and preserve the one-way holdout boundary.
- Reject a proposal that adds architectural complexity without an ablation, a simple baseline, and a retirement criterion for dominated variants.
- Preserve current controls when the corpus supports them, especially source/build/consult isolation, immutable snapshots, deterministic reconstruction, explicit authority boundaries, and retrospective labels for exposed qrels.

## Evidence and limits

The accepted Semantic OKF concept files are the readable evidence layer; the ledger, source manifest, RDF, SHACL, and build report establish identity, provenance, and coherence. Cite a material claim as `concepts/<source-id>/<record-id>.md, PDF page N` and include the versioned arXiv ID. A page locator points to extracted PDF text and may not preserve tables, formulas, figures, or reading order perfectly. Inspect neighboring pages before relying on an isolated fragment.

Use these claim labels: `direct` for an explicit paper result, `synthesis` for agreement inferred across papers, `repository-inference` for applying research to this codebase, and `open-question` when the snapshot is insufficient. State conflicts and missing evidence. Stop or recommend a corpus update when the required claim is outside the eight coverage lanes, depends on a newer paper version, needs a non-arXiv authority, or cannot be verified in the extracted page text.
