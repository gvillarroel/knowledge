# GraphRAG Papers Expert Guidance

## Scope

Use this expert for questions about the fifteen reviewed GraphRAG papers in the
embedded snapshot: their graph construction, representation, retrieval units,
retrieval strategies, organization and synthesis, tasks, evaluations,
strengths, limitations, and cross-paper trade-offs. The reviewed claims
records are the preferred evidence layer. The paper records provide fuller
context when a claim collection is not sufficient.

Do not generalize from this corpus to every GraphRAG system. Do not treat a
method's reported benchmark result as a universal ranking. Distinguish claims
made by paper authors from classifications or comparisons introduced by the
review.

## Application workflow

1. Decompose the request into explicit comparison dimensions, such as graph
   construction, retrieval unit, query scope, synthesis method, task fit,
   evidence, and limitations.
2. Search with the complete question first. If necessary, run one focused
   search for each missing dimension or named method.
3. Prefer `claims-*` records for reviewed, page-located statements. Open the
   paired `paper-*` record only when more context is required.
4. Build an evidence matrix before writing a taxonomy or comparison. Keep one
   row per paper and one column per requested dimension.
5. Synthesize common patterns only after recording method-specific evidence.
   Cite exact bundled concept paths for every material distinction.

## Decision rules

- Classify evidence organization separately from retrieval. Community reports,
  local subgraphs, paths, triples, nodes, and hybrid textual/graph contexts are
  different retrieval or synthesis units even when they share an upstream
  knowledge graph.
- Separate corpus-time construction from query-time selection. Entity and
  relation extraction, clustering, community summarization, embedding, graph
  traversal, and reranking belong to different stages.
- Match task fit to query scope. Corpus-wide thematic questions favor global
  summaries; entity-centered and multi-hop questions favor local graph
  expansion or connected-subgraph retrieval; precise factual questions require
  direct evidence and citation recovery.
- When methods are complementary, state the complement instead of forcing a
  total order. Quality, latency, token cost, connectivity, traceability, and
  global coverage are independent axes.
- Treat absence as unknown unless the reviewed record explicitly identifies a
  missing stage, evaluation, or capability.
- For conflicting evidence, report both claims with their paper identities and
  explain the difference in task, corpus, metric, or experimental setting.

## Evidence and limits

Every substantive statement must resolve to an exact `source_id`, `record_id`,
and `concept_path` in the embedded Semantic OKF ledger. Prefer reviewed claims
with explicit page locators. Clearly label cross-paper synthesis as inference.

The routing profile was learned retrospectively from all forty exposed
retrieval questions and qrels. It contains no exact-question lookup, but its
retrieval score is in-sample and cannot support a holdout-qualified promotion
or a generalization claim. The immutable knowledge remains authoritative; the
profile only accelerates discovery. If the snapshot does not support an answer,
state the gap instead of using outside knowledge.
