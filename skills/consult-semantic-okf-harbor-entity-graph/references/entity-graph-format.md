# Entity-Graph Format

The `entity-graph/` directory is a closed, hash-bound, discovery-only projection. `entities.jsonl` stores authoritative record identities and extracted candidates; `sections.jsonl` stores exact record-body slices; `mentions.jsonl` stores candidate phrase matches; `edges.jsonl` stores structural and candidate paths; and `lexicon.json` stores BM25 statistics.

Schema `2.0` keys documents by `(source_id, record_id)`. Each section also binds `record_sha256`, `source_content_sha256`, subject IRI, concept/source paths, a `record-body` character range, and exact text hash. `document_id` is a deterministic convenience identifier; the structured identity and hashes remain the provenance contract.

`partOfDocument` is an authoritative structural binding only. Candidate phrases, mentions, co-mentions, weights, graph paths, and rankings are not domain facts. Legacy schema `1.0` additionally mirrors reviewed claim relations and PDF-page evidence without changing their frozen representation.

Ordinary inspection verifies closed files, hashes, references, source-record identities, exact character ranges, index, and report. Deep inspection additionally rebuilds every entity, section, mention, edge, and lexical statistic in memory. Neither inspection nor search writes to the bundle.
