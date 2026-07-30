# Knowledge Methodology Papers: Scope and Competency Questions

## Purpose

This dataset supports evidence-grounded review of the repository's methodology
for acquiring, constructing, representing, retrieving, validating, evaluating,
evolving, and publishing knowledge. It is a curated research corpus rather than
a leaderboard or a claim of exhaustive literature coverage.

The dataset combines:

- thirty-two newly selected, version-pinned arXiv papers; and
- the fifteen already pinned papers in `graphrag-cross-paper-2026-07`.

Every selected paper is available as page-delimited Markdown. Newly acquired
papers also retain the exact PDF bytes and SHA-256 digest. Reused GraphRAG papers
retain their existing accepted PDF binding and provenance.

## Competency questions

1. Which knowledge representation should be authoritative, and which retrieval
   indexes should remain non-authoritative projections?
2. When do lexical, dense, late-interaction, graph, hybrid, hierarchical, or
   agentic retrieval methods improve discovery, and what do they cost?
3. How should document structure and chunk size be selected and evaluated rather
   than assumed?
4. How should ontology learning, entity extraction, identity resolution, and
   graph validation divide work between automation and expert review?
5. Which metrics diagnose retrieval, grounding, semantic answer quality,
   robustness, and efficiency without conflating them?
6. How should repeated prompt or skill evolution protect development, validation,
   and holdout evidence from adaptive overfitting?
7. Which sources of evaluator, judge, provider, and benchmark variance must be
   measured before a candidate is called better?
8. What provenance, deterministic rebuilding, source fidelity, and publication
   evidence are required for a reproducible knowledge artifact?
9. Which current repository practices are supported by research evidence, which
   are merely engineering conventions, and which should change?

## Authority and limits

The paper texts are authoritative only for what their authors report. Selection
annotations and repository implications are review metadata, not paper claims.
Retrieval scores and generated summaries are discovery aids and never replace
page-level verification.

The corpus intentionally includes both mature and recent work. A single paper,
especially a recent preprint, cannot establish a universal design rule. Reviews
must distinguish replicated evidence, one-study findings, surveys, position
papers, and formal results.
