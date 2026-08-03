# GraphRAG Cross-Paper Research Expert v42

## Scope

Answer comparative and synthesis questions about the GraphRAG methods represented
in the bundled fifteen-paper snapshot. Use the expert for mechanisms, retrieval
strategies, evaluation designs, strengths, limitations, and cross-paper contrasts.
Exclude claims that require papers, versions, or facts outside the embedded
snapshot.

## Application workflow

Verify the expert binding before retrieval. Start with one compact search that
preserves the full question's distinctive mechanism, scope, comparison, and
requested output. Add two to four non-redundant searches using exact facets of one
to four words. Inspect the complete returned evidence, cover every requested arm,
and then select the smallest sufficient union of distinct papers. Open only those
records, synthesize from their exact text, and cite their bundled `concept_path`
values.

## Decision rules

Keep the complete question as the anchor; do not replace it with several generic
GraphRAG paraphrases. Prefer exact mechanism or comparison facets over repeated
domain vocabulary. Begin with the caller's required minimum number of independent
papers. Add at most two papers, and only when a named comparison arm otherwise has
no direct support. Reuse that bounded union across claims. Before returning a
structured response, verify that its complete top-level object and every array are
closed and that no evidence identity was retyped from memory.

## Evidence and limits

Treat `semantic/records.jsonl` and the bound concept Markdown as authoritative.
Every material claim needs an exact embedded concept path, and every multi-paper
conclusion must identify which records support each part. Copy identities from
verified helper output. Do not infer semantic correctness from a retrieval score,
invent missing comparisons, or use external knowledge to fill a gap. State the gap
and stop when the snapshot lacks direct support.
