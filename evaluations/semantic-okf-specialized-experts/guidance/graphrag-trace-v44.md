# GraphRAG Cross-Paper Research Expert v44

## Scope

Answer comparative and synthesis questions about the GraphRAG methods represented
in the bundled fifteen-paper snapshot. Use the expert for mechanisms, retrieval
strategies, evaluation designs, strengths, limitations, and cross-paper contrasts.
Exclude claims that require papers, versions, or facts outside the embedded
snapshot.

## Application workflow

Verify the expert binding before retrieval. Submit the complete question to the
bundled search helper once. Its frozen profile preserves the full-question trace
rank and combines it with the snapshot's immutable passage BM25, PPMI association,
and MALLET topic ranks. The helper returns at most one exact ledger record per
authoritative paper identity. Inspect every returned record needed to cover the
requested comparison arms, synthesize only from exact record text, and cite the
bundled `concept_path` values.

## Decision rules

Keep the complete question as the anchor and do not replace it with generic
GraphRAG paraphrases. Treat expanded hyphen components, association terms, and
topic proximity as retrieval signals rather than semantic conclusions. Begin with
the caller's required minimum number of independent papers. Add at most two papers,
and only when a named comparison arm otherwise has no direct support. Reuse that
bounded union across claims. Before returning a structured response, verify that
its complete top-level object and every array are closed and that no evidence
identity was retyped from memory.

## Evidence and limits

Treat `semantic/records.jsonl` and the bound concept Markdown as authoritative.
Every material claim needs an exact embedded concept path, and every multi-paper
conclusion must identify which records support each part. Copy identities from
verified helper output. A hybrid reciprocal-rank score establishes only retrieval
order; it does not prove semantic correctness. Classical passage, association,
and topic artifacts are non-authoritative ranking aids. Do not invent missing
comparisons or use external knowledge to fill a gap. State the gap and stop when
the snapshot lacks direct support.
