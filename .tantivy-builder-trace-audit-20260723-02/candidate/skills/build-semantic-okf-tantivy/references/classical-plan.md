# Classical Retrieval Plan

## Closed root

The root contains exactly `schema_version`, `selection`, `tokenization`, `bm25`, `associations`, `topics`, `expansion`, and `reranking`. `schema_version` is `"1.0"`. Unknown members fail and no default is inferred.

```json
{
  "schema_version": "1.0",
  "selection": {"source_ids": ["claims-a", "paper-a"]},
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
  }
}
```

`selection.source_ids` is sorted, unique, nonempty, and must resolve to records. The selected physical-source inventory is hashed from each source ID and authoritative content digest.

## Passage boundary

Paper records containing `## PDF page N` headings become exact page passages. The first passage includes any title preamble before PDF page 1. Other records remain one full-record passage. Whitespace trimming changes the character bounds so `record.body[start:end]` always equals the persisted text exactly.

## Token and lexical statistics

The bundled tokenizer Unicode-casefolds input, extracts ASCII alphanumeric tokens, removes the versioned stopword set, applies the minimum length, and optionally adds adjacent bigrams. Title and body bags remain separate. The lexicon persists document frequency, corpus frequency, Okapi BM25 IDF, and average title/body lengths.

## Associations and topics

Association vocabulary is selected deterministically by document frequency, corpus frequency, and lexical tie-break. A bounded local window counts unordered term co-occurrences. Positive pointwise mutual information is rounded to eight decimals, and only the configured strongest neighbors survive.

Topics are statistical term communities, not ontology classes. The algorithm chooses diverse central seed terms, fixes each seed to one topic, and deterministically propagates weighted labels through the symmetric PPMI graph. Document topic weights sum TF-IDF mass by community and normalize it. Every output is reproducible from the authoritative records and closed plan.

## Query behavior recorded by the plan

The consultant uses association and topic counts and weights only when their named mode is selected. Reranking weights must sum to one. A deeper candidate pool and `max_per_evidence_identity` cap permit diversity-aware selection without changing the requested final result count. Reciprocal-rank fusion uses the configured `rrf_k` and never combines incomparable raw component scores.
