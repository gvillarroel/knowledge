# Entity-Graph Format

`entity-graph/` is a closed, non-authoritative retrieval projection bound to the authoritative core tree, record ledger digest, exact selected-source inventory, complete plan, algorithm identifiers, artifact hashes, and summary counts.

## Artifacts

- `entities.jsonl`: reviewed method, dimension, paper, and claim identities plus extracted candidate phrases. Reviewed rows bind exact source, record, concept, subject IRI, and record digest. Candidate rows contain extraction statistics instead.
- `sections.jsonl`: exact paper-page text, character range, fragment, record and concept identities, text hash, token counts, and paper identity.
- `mentions.jsonl`: deterministic normalized phrase matches from an entity to a section. All mention assertions are candidates.
- `edges.jsonl`: graph edges with review state, semantic source, optional claim record ID, exact evidence section IDs, and weight.
- `lexicon.json`: section-level BM25 document frequency, inverse document frequency, and average length.
- `index.json`: authority marker, core and source bindings, plan, algorithms, artifacts, and summary.
- `build-report.json`: independently reproduced validation result.

## Edge semantics

Reviewed claim projection uses `hasReviewedClaim`, `objectTerm`, `aboutPaper`, and `supportedBySection`. `partOfPaper` binds exact page sections to their authoritative paper. `mentionedInSection` and `coMentionedWith` are deterministic candidates. Every edge remains part of a discovery projection even when it mirrors a reviewed core fact.

Multi-page claims create one `supportedBySection` edge per page. The other reviewed claim edges retain the complete evidence-section set.

## Validation

Validation rejects unknown files, symlinks, unsafe paths, duplicate IDs, broken references, stale core or source hashes, invalid text slices, non-finite weights, missing evidence, schema drift, non-reviewed accepted claims, artifact mismatch, and any difference from full deterministic rederivation.
