# Graphify Projection Contract

Graphify is a derived discovery layer, never the factual authority. The builder
uses `graphifyy==0.9.17` structural Markdown extraction without semantic LLM
extraction or clustering. Temporary views expose reviewed ledger attributes as
headings and reviewed object IRIs as local links. Scalar text is neutralized for
Markdown structural punctuation, so only links emitted by the builder can add
edges. Views and external Graphify caches must be verifiably absent before
publication.

For `source-packed-v1`, Graphify must not parse the aggregate collection shape:
that would make discovery scores depend on physical storage. The builder
reconstructs the exact record-per-file Markdown and root index in memory from
the authoritative ledger and semantic plan, passes those virtual inputs through
the pinned Markdown extractor, and publishes no expanded concepts. The graph
bytes must equal a record-per-file build over the same logical records.

The published `retrieval/graphify/index.json` binds the native node-link graph to
the complete Semantic OKF core, `records.jsonl`, every normalized record, and the
deterministic view-input digest. A release is invalid when any core artifact,
record, graph node, edge endpoint, source path, count, or digest drifts.
Validation regenerates every view in memory from the ledger and compares the
complete derived record, paper, node, link, and view identity rather than
trusting self-declared index metadata.

Graph labels and traversal paths are discovery evidence only. Resolve the bound
logical `concept_path` through the declared layout and verify either the exact
concept file or the record's hash-derived collection anchor and complete body
before citing a fact.

## Harbor lexical-root evolution

The evolved builder keeps the original temporary-view, label, and index schemas
so the published `consult-semantic-okf-graphify` package remains unchanged. It
marks the generated filename node for each record as `record-root` and retains
the official reciprocal top-one binary TF-IDF bridge derived from authoritative
title, record ID, concept type, and body. It adds a second bridge when two
authoritative record bodies contain internal `/en/.../` documentation links to
each other's routes. Routes are derived from ledger record IDs; one-way
references and nodes whose reciprocal-reference degree exceeds six are ignored
to constrain hubs. The lexical signal connects records
only when each is the other's nearest neighbor in a different record-ID
partition. A partition is the first path segment after the corpus-wide common
record-ID prefix; a single-partition corpus falls back to unrestricted
reciprocal neighbors. Both rules are deterministic and independent of evaluation
questions or relevance judgments.

Content-derived edges declare `projection: harbor-lexical-similarity` and mutual
documentation links declare `projection: harbor-reciprocal-reference`.
Validation must regenerate all roots and both edge sets from `records.jsonl` and
reject any mismatch. Similarity and traversal remain non-authoritative and must
never be cited instead of the bound concept file or anchored collection record.
