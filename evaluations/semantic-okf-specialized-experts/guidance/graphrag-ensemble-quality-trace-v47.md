# GraphRAG Ensemble Quality and Trace Research Expert v47

## Scope

Answer comparative and synthesis questions about the GraphRAG methods represented
in the bundled fifteen-paper snapshot. Use this expert for mechanisms, retrieval
strategies, graph construction, evaluation design, strengths, limitations,
efficiency, and cross-paper trade-offs. Exclude claims that require papers,
versions, or facts outside the embedded snapshot.

## Application workflow

Verify the expert and submit the complete question once. The helper forms a
bounded union of the snapshot's Ensemble quality Top-10 and a full-question
fielded-BM25 Top-10 calculated over the same immutable ledger. It reranks that
union with one global reciprocal-rank rule, returns no more than ten independent
paper identities, and preserves exact evidence rows. Inspect the passages or
reviewed claims needed to cover every comparison arm, open their bound concept
Markdown, and cite the exact bundled `concept_path` values.

## Decision rules

Keep the complete question as the anchor. Within the quality route, preserve the
adaptive candidate set and its validated multiroute gates. Add only papers that
enter through the independent fielded-BM25 Top-10, then fuse quality and trace
ranks with weights 7 and 2 and reciprocal-rank constant 0. Break ties by quality
rank, trace rank, and canonical paper ID. Begin with the caller's required number
of independent papers and add evidence only when a named comparison arm remains
unsupported. Treat graph edges, embeddings, lexical values, and fusion scores as
discovery signals rather than semantic conclusions.

## Evidence and limits

Treat `semantic/records.jsonl` and bound concept Markdown as authoritative.
Every material claim needs an exact embedded concept path, and every cross-paper
conclusion must identify which records support each part. The quality component
requires the exact declared Sentence Transformers runtime and already-cached
immutable model revision; it runs offline and fails closed if either is absent.
Do not substitute a model, silently drop a route, invent a missing comparison, or
use external knowledge to fill a gap. State the gap and stop when the snapshot
lacks direct support. The selected global fusion constants are retrieval
parameters, not evidence that any returned claim is correct.
