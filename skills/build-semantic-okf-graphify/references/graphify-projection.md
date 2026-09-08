# Graphify Projection Contract

Graphify is a derived discovery layer, never the factual authority. The builder
uses `graphifyy==0.9.17` structural Markdown extraction without semantic LLM
extraction or clustering. Temporary views expose reviewed ledger attributes as
headings and reviewed object IRIs as local links. Scalar text is neutralized for
Markdown structural punctuation, so only links emitted by the builder can add
edges. Views and external Graphify caches must be verifiably absent before
publication.

For `source-packed-v1`, the builder reconstructs the exact legacy
`record-per-file-v1` concept and index Markdown in memory and runs Graphify over
those virtual paths. The expanded concepts are never written to the bundle.
The resulting canonical graph bytes and retrieval rankings must be identical
to the record-per-file release; file reduction alone is not sufficient.

Graphify 0.9.17 leaves an absolute file-stem ID on an empty Markdown heading.
Normalize that exact residual ID after extraction using the relative source
path and source location. Keep a separate, collision-checked heading identity
and remap both edge endpoints; never merge it into the document root. Preserve
all labels, source fields, and relationships. Both physical layouts must produce
the same graph across unrelated temporary build directories.

The published `retrieval/graphify/index.json` binds the native node-link graph to
the complete Semantic OKF core, `records.jsonl`, every normalized record, and the
deterministic view-input digest. A release is invalid when any core artifact,
record, graph node, edge endpoint, source path, count, or digest drifts.
Validation regenerates every view in memory from the ledger and compares the
complete derived record, paper, node, link, and view identity rather than
trusting self-declared index metadata.

Graph labels and traversal paths are discovery evidence only. Open the bound
`concept_path` before citing a fact.

## Harbor lexical-root evolution

The evolved builder keeps the original temporary-view, label, and index schemas
so the published `consult-semantic-okf-graphify` package remains unchanged. It
marks the generated filename node for each record as `record-root`, computes
binary TF-IDF cosine similarity from the authoritative title, record ID,
concept type, and body, and connects roots only when each is the other's nearest
neighbor in a different record-ID partition. A partition is the first path
segment after the corpus-wide common record-ID prefix; a single-partition corpus
falls back to unrestricted reciprocal neighbors. This reciprocal bridge rule
prevents hubs and dense same-section clusters from crowding out complementary
guides and references. Neighbor selection is deterministic and independent of
evaluation questions or relevance judgments.

Each derived edge declares `projection: harbor-lexical-similarity`. Validation
must regenerate all roots and edges from `records.jsonl` and reject any
mismatch. Similarity and traversal remain non-authoritative and must never be
cited instead of the bound concept file.
