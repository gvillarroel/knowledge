# Graphify Projection Contract

Graphify is a derived discovery layer, never the factual authority. The builder
uses `graphifyy==0.9.17` structural Markdown extraction without semantic LLM
extraction or clustering. Temporary views expose reviewed ledger attributes as
headings and reviewed object IRIs as local links. Scalar text is neutralized for
Markdown structural punctuation, so only links emitted by the builder can add
edges. Views and external Graphify caches must be verifiably absent before
publication.

The published `retrieval/graphify/index.json` binds the native node-link graph to
the complete Semantic OKF core, `records.jsonl`, every normalized record, and the
deterministic view-input digest. A release is invalid when any core artifact,
record, graph node, edge endpoint, source path, count, or digest drifts.
Validation regenerates every view in memory from the ledger and compares the
complete derived record, paper, node, link, and view identity rather than
trusting self-declared index metadata.

Graph labels and traversal paths are discovery evidence only. Open the bound
`concept_path` before citing a fact.
