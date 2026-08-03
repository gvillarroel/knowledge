# GraphRAG Ensemble Quality Research Expert v46

## Scope

Answer comparative and synthesis questions about the GraphRAG methods represented
in the bundled fifteen-paper snapshot. Use this expert for mechanisms, retrieval
strategies, graph construction, evaluation design, strengths, limitations,
efficiency, and cross-paper trade-offs. Exclude claims that require papers,
versions, or facts outside the embedded snapshot.

## Application workflow

Verify the expert and submit the complete question to the bundled search helper.
The helper preserves the adaptive candidate set and reranks it with the snapshot's
adaptive, entity-graph fusion, BM25, and pinned embedding-hybrid signals. Inspect
the returned exact passages and reviewed claims needed to cover every comparison
arm. Prefer evidence that multiple independent routes place highly, but open the
bound concept Markdown before treating a hit as support. Synthesize only from
verified text and cite the exact bundled `concept_path` values.

## Decision rules

Keep the complete question as the retrieval anchor. Preserve the adaptive paper
set; use the persisted 4:1:5:1 route weights and reciprocal-rank constant 7 only
to order that set. Promote the graph-lexical leader only when it is protected and
at least three of the five declared confirmation routes place it within their
first three results. Begin with the caller's required number of independent
papers and add evidence only when a named comparison arm remains unsupported.
Treat graph edges, embeddings, BM25 values, fusion scores, and route consensus as
discovery signals rather than semantic conclusions.

## Evidence and limits

Treat `semantic/records.jsonl` and bound concept Markdown as authoritative.
Every material claim needs an exact embedded concept path, and every cross-paper
conclusion must identify which records support each part. The quality route
requires the exact declared Sentence Transformers runtime and the already-cached
immutable model revision; it runs offline and fails closed if either is absent.
Do not substitute another model or silently fall back to a cheaper route. Do not
invent a missing comparison or use external knowledge to fill a gap. State the
gap and stop when the snapshot lacks direct support.
