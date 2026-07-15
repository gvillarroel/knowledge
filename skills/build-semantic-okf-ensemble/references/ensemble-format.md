# Ensemble Bundle Format

## Layer boundary

The bundle contains one authoritative Semantic OKF core and four derived roots:

- `adaptive/`: deterministic BM25F, PPMI association, topic, aspect-routing, and verified answer-binding artifacts;
- `entity-graph/`: deterministic paper sections, reviewed and candidate entities, mentions, edges, and lexical statistics;
- `retrieval/`: pinned chunks and vectors for the declared embedding provider; and
- `ensemble/`: the common plan, algorithm identities, component index bindings, core parity binding, and build report.

All four roots are non-authoritative and discovery-only. Their files never add facts to concept Markdown, the record ledger, RDF, ontology, shapes, or provenance.

## Closed ensemble artifacts

`ensemble/` contains exactly `index.json` and `build-report.json`, both regular non-symlink files. `index.json` persists the complete closed plan and canonical SHA-256, the common authoritative core binding, exact component index paths/bytes/hashes, fixed algorithm identities, and summary counts. `build-report.json` must equal the independently reproduced live report.

Each component retains its own closed artifact schema and complete deterministic validator. All component core objects must be byte-for-byte equal. Core inventory hashing excludes only the four declared derived roots, so adding or validating one component cannot change another component's authoritative binding.

## Validation and publication

Validation rejects an incomplete or unknown artifact set, unsafe filesystem indirection, a malformed plan or index, stale component hashes, failed child validation, component/core mismatch, or a report that differs from live reconstruction.

The builder creates the core and all projections in one private sibling candidate, writes the ensemble binding after the child validators pass, validates the completed candidate, and publishes the payload once. A failed build removes the candidate and leaves the requested output absent.
