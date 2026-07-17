---
adr: "0019"
title: "ADR 0019: Add Classical Text-Derived Retrieval to Semantic OKF"
summary: "Keep the Semantic OKF core authoritative while deriving deterministic BM25, topic-community, and PPMI association indexes through a separate standalone skill pair."
status: "Accepted"
date: "2026-07-14"
product: "knowledge"
owner: "Platform Architecture"
area: "Semantic Knowledge Retrieval"
tags:
  - knowledge
  - okf
  - bm25
  - topics
  - lexical-statistics
  - retrieval
---

# ADR 0019: Add Classical Text-Derived Retrieval to Semantic OKF

## Status

Accepted.

This decision extends ADR 0008, ADR 0010, ADR 0012, ADR 0014, ADR 0015, and the
embedding-derived retrieval decision in ADR 0017. It does not modify the legacy or embedding
skill packages or their completed evaluation artifacts.

## Context

The legacy Semantic OKF consultation guidance permits fixed-string `rg` discovery alongside ledger,
concept, and RDF navigation. Its frozen retrieval evaluator is a separate in-memory TF-IDF-like
query-token ranker over authoritative records; it does not execute `rg` or `grep`. The embedding
alternative adds model-dependent chunks, vectors, and hybrid ranking. Those approaches establish
useful baselines, but they do not isolate the contribution of richer classical corpus statistics,
topic structure, query expansion, or diversity-aware reranking.

The pinned GraphRAG corpus contains fifteen paper Markdown files, fifteen reviewed-claim JSONL
files, and one separately declared analysis vocabulary. Paper bodies preserve exact PDF-page
headings, while reviewed claims retain evidence locators. This permits a deterministic retrieval
projection whose passages remain exact slices of authoritative records and whose statistical
signals can be reproduced without a model, network access, or mutable cache.

## Decision

Ship two additional standalone skills:

1. `build-semantic-okf-classical` creates and independently validates a Semantic OKF snapshot
   plus a non-authoritative classical retrieval projection.
2. `consult-semantic-okf-classical` validates and consults that projection read-only.

The four existing Semantic OKF packages remain unchanged and independently installable. The new
skills may duplicate stable core-format code, but they must not import or execute a sibling skill,
repository helper, evaluation fixture, or repository document.

The builder first materializes the authoritative Semantic OKF core without semantic changes. It
then writes a closed `classical/` tree containing:

- `documents.jsonl`, with exact page or record passages, record and concept identity, character
  locators, bag-of-words counts, field lengths, and topic weights;
- `lexicon.json`, with tokenizer identity, corpus and document frequencies, BM25 inverse-document
  frequencies, and average field lengths;
- `associations.jsonl`, with bounded positive-PMI term neighbors derived from deterministic local
  co-occurrence windows;
- `topics.json`, with deterministic weighted label-propagation term communities and their top
  terms;
- `index.json`, which closes the schema and binds the plan, authoritative core, selected inputs,
  algorithms, parameters, counts, and artifact hashes; and
- `build-report.json`, which reports validation and summaries but is not domain evidence.

The projection is derived and non-authoritative. It must not add passages, terms, topics, or
association edges to `records.jsonl`, concept Markdown, or RDF graphs. A passage is either a full
record or an exact character range under an authoritative record body. Every result preserves the
source, record, concept, source-path, text hash, and locator needed to reconstruct evidence.

The closed plan selects source IDs explicitly and fixes tokenizer, n-gram, BM25, association,
topic, query-expansion, and reranking parameters. Unknown members fail. The portable baseline uses
only deterministic Python text processing after the package-local Semantic OKF runtime is
installed. It performs no model selection, download, cache write, hosted request, or arbitrary
code loading.

Consultation exposes four named modes:

- `bm25` ranks weighted title/body bags of words with persisted Okapi BM25 statistics;
- `topic` expands a query through activated topic communities and combines BM25 with document-topic
  similarity;
- `association` propagates query weight over the persisted PPMI term graph before lexical scoring;
  this is a distinct graph-of-terms resolution rather than a parameter variation of topic search;
- `fusion` combines the three independent rankings with reciprocal-rank fusion.

Topic, association, and fusion modes apply deterministic maximal-marginal-relevance reranking over
a larger candidate pool and a plan-pinned cap per paper or source evidence identity. The reranker balances normalized relevance, topic novelty, and paper or
source novelty. Filters apply before scoring, ties resolve by document ID, and the response exposes
component scores, expansion terms, topics, requested and effective mode, index digest, and exact
evidence identities. Scores remain discovery signals; factual answers must be checked in the
authoritative concept, ledger, or purpose-selected RDF graph.

Builds publish atomically from a private sibling candidate only after core and projection
validation. Independent validation checks the closed file set, safe paths, core and input hashes,
document identities and locators, token counts, lexical statistics, associations, topic weights,
artifact hashes, and report equality. Two unchanged builds must have identical sorted path-and-byte
trees before a release is accepted.

The comparison retains the prior thirty retrieval questions and adds ten evidence-first hard
questions. Hard-question ground truth is versioned separately from task prompts and records atomic
answer claims, required paper and source identities, exact authoritative paths and locators or text
hashes, derivation logic, acceptable variants, and important negatives. Generation and validation
must reject stale hashes, invalid locators, duplicated questions, leaked answer text in task
prompts, or unsupported ground-truth claims.

Retrieval and grounded-answer evaluation remain separate. The retrieval benchmark compares legacy
lexical, embedding lexical, vector, hybrid, BM25, topic, association, and fusion routes on the same
forty questions with evidence-valid schema 1.2 or a strictly stronger successor. Skill Arena causal
claims use isolated profiles with identical prompts and knowledge: a knowledge-only control and one
single-skill treatment per consultant. An all-skills portfolio is only a routing smoke.

Large bundles and live runs remain append-only and ignored. Compact plans, inventories, question
banks, ground truth, validation reports, causal configs, and comparison summaries are checked in.

## Consequences

Positive:

- classical lexical statistics and topic structure can be measured independently from embeddings;
- every signal is persisted or deterministically reproducible and participates in evidence choice;
- the PPMI association route can recover related terminology without a vector model;
- exact page and claim locators preserve an auditable path from ranking to authoritative evidence;
- the baseline is offline, model-free, deterministic, and independently installable; and
- diversity-aware ranking directly addresses repeated chunks or claims from one paper dominating a
  synthesis context.

Negative:

- duplicated standalone core code must be kept compatible through tests;
- term co-occurrence and topic artifacts increase bundle size and build time;
- corpus-derived expansion can amplify ambiguous terms, so expansion weights and returned terms
  must remain visible;
- deterministic topic communities are statistical summaries, not ontology classes or semantic
  truth; and
- retrieval improvements do not establish answer correctness without a separate grounded-answer
  evaluation.
