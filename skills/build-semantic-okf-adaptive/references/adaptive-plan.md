# Adaptive Retrieval Plan

## Closed root

The root contains exactly `schema_version`, `selection`, `passages`, `evidence_identity`, `tokenization`, `bm25`, `associations`, `topics`, `expansion`, `reranking`, and `adaptive`. `schema_version` is `"1.1"`. Unknown members fail and no default is inferred. Version 1.1 makes explicit passage and evidence-identity mappings mandatory and is intentionally incompatible with the experimental 1.0 plan.

```json
{
  "schema_version": "1.1",
  "selection": {"source_ids": ["catalog", "research-notes"]},
  "passages": {
    "default_mode": "full-record",
    "markdown_pdf_page_source_ids": []
  },
  "evidence_identity": {
    "default_mode": "source-record",
    "paper_ids_by_source": {}
  },
  "tokenization": {
    "tokenizer": "ascii-alphanumeric-v1",
    "stopwords": "english-v1",
    "min_token_length": 2,
    "ngram_range": [1, 2]
  },
  "bm25": {"k1": 1.2, "b": 0.75, "title_weight": 2.0, "body_weight": 1.0},
  "associations": {
    "window_size": 8,
    "min_document_frequency": 2,
    "min_cooccurrence": 2,
    "max_vocabulary": 3000,
    "max_neighbors": 8,
    "minimum_ppmi": 0.0
  },
  "topics": {"topic_count": 16, "max_iterations": 20, "top_terms": 20},
  "expansion": {
    "association_terms": 6,
    "topic_terms": 6,
    "association_weight": 0.35,
    "topic_weight": 0.2
  },
  "reranking": {
    "candidate_pool": 100,
    "relevance_weight": 0.7,
    "topic_novelty_weight": 0.15,
    "source_novelty_weight": 0.15,
    "max_per_evidence_identity": 1,
    "rrf_k": 60
  },
  "adaptive": {
    "maximum_aspects": 8,
    "minimum_aspect_tokens": 4,
    "full_query_weight": 2.0,
    "aspect_weight": 0.25,
    "best_aspect_weight": 0.0,
    "rrf_k": 0,
    "protected_full_results": 9,
    "maximum_novel_aspect_rank": 1
  }
}
```

`selection.source_ids` is sorted, unique, nonempty, and must resolve to records. The selected physical-source inventory is hashed from each source ID and authoritative content digest.

## Passage and evidence identities

The generic default is one full-record passage and the collision-safe identity tuple `(source_id, record_id)`. These defaults work for every source format supported by the bundled Semantic OKF core and never infer an identity from a title, filename, or body.

`passages.markdown_pdf_page_source_ids` may explicitly select sources whose reviewed Markdown conversion uses `## PDF page N` headings. Only those sources are split into exact character-range passages; the first passage includes any title preamble before PDF page 1. Whitespace trimming changes the bounds so `record.body[start:end]` always equals the persisted text exactly.

`evidence_identity.paper_ids_by_source` is an explicit source-to-versioned-arXiv-ID mapping. It may group multiple declared sources, such as a paper conversion and its reviewed claim ledger, only when the plan author records the same paper ID for both. Keys must be selected source IDs and values must be canonical `YYYY.NNNNNvN` identities. An empty mapping disables paper grouping. No record ID, path, title, or body is searched for an identity.

## Token and lexical statistics

The bundled tokenizer Unicode-casefolds input, extracts ASCII alphanumeric tokens, removes the versioned stopword set, applies the minimum length, and optionally adds adjacent bigrams. Title and body bags remain separate. The lexicon persists document frequency, corpus frequency, Okapi BM25 IDF, and average title/body lengths.

## Associations and topics

Association vocabulary is selected deterministically by document frequency, corpus frequency, and lexical tie-break. A bounded local window counts unordered term co-occurrences. Positive pointwise mutual information is rounded to eight decimals, and only the configured strongest neighbors survive.

Topics are statistical term communities, not ontology classes. The algorithm chooses diverse central seed terms, fixes each seed to one topic, and deterministically propagates weighted labels through the symmetric PPMI graph. Document topic weights sum TF-IDF mass by community and normalize it. Every output is reproducible from the authoritative records and closed plan.

## Query behavior recorded by the plan

The consultant uses association and topic counts and weights only when their named route participates. Reranking weights must sum to one. A deeper candidate pool and `max_per_evidence_identity` cap permit diversity-aware selection without changing the requested final result count. Evidence identity is a plan-reviewed paper identity when explicitly mapped and otherwise the authoritative `(source_id, record_id)` tuple, so separate sources may safely reuse local record IDs. Component fusion uses the reranking `rrf_k` and never combines incomparable raw scores.

Adaptive mode deterministically splits the query at bounded punctuation and contrast/coordinator boundaries. `minimum_aspect_tokens` counts base unigrams, not generated bigrams. Short fragments are merged into a neighbor, excess fragments are merged into the final bounded aspect, and an aspect equal to the complete query is removed; query content is never silently discarded or redundantly rerun. It ranks the full query and each remaining aspect through component fusion, aggregates evidence identities with the adaptive weights and adaptive `rrf_k`, and protects the first `protected_full_results` full-query identities. An identity outside the full-query top-k may enter only when it ranks at or above `maximum_novel_aspect_rank` in at least one aspect; this is a deterministic confidence gate against weak aspect-only substitutions. A zero adaptive `rrf_k` intentionally emphasizes early aspect ranks. These values are part of the release contract rather than hidden runtime defaults.
