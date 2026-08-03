# Software Architecture Books Corpus Scope

## Purpose

Build a private, deterministic, page-addressable corpus from the exact eighteen
PDFs supplied by the user and evaluate model-free retrieval across software
architecture, design, delivery, requirements, APIs, concurrency, and
performance engineering.

## Competency questions

The corpus must support evidence-backed comparison across:

- domain boundaries, coupling, modular monoliths, microservices, and
  volatility-based decomposition;
- architectural principles, quality attributes, decisions, evolution, and
  technical debt;
- requirements discovery, domain storytelling, stakeholder communication, and
  asynchronous collaboration;
- API contracts, affordances, integration patterns, and evolution;
- object-oriented and functional design, concurrency, testing, and feedback;
  and
- measurement-led diagnosis of latency, queues, utilization, and software
  dynamics.

## Authority and limits

Only PDFs whose filenames, byte counts, page counts, metadata, and SHA-256
values match `book-selection.json` are authoritative. Derived Markdown page
headings are stable evidence locators. The raw PDFs, extracted full text,
Semantic OKF bundle, generated Harbor tasks, and raw results remain local and
ignored because the source material is private and marked against
redistribution.

The forty qrels are reviewed, non-exhaustive focus sets. Direct evaluation
measures discovery of relevant books and reviewed page locators; it does not
measure generated-answer correctness, establish exhaustive relevance, or
justify unseen-domain generalization.
