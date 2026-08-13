# Ensemble Bundle Format

## Layer boundary

The bundle contains one authoritative Semantic OKF core and four derived roots:

- `adaptive/`: deterministic BM25F, PPMI association, topic, aspect-routing, and
  optional verified answer-binding artifacts;
- `entity-graph/`: deterministic document or legacy paper sections, entities,
  mentions, edges, and lexical statistics;
- `retrieval/`: pinned chunks and vectors for the declared offline embedding
  provider; and
- `ensemble/`: the common plan, algorithm identities, component bindings, identity
  crosswalk when applicable, core parity binding, and build report.

All four roots are non-authoritative and discovery-only. Their files never add facts
to concept Markdown, the record ledger, RDF, ontology, shapes, or provenance.

## Closed artifacts

Schema `1.0` preserves the legacy closed set:

```text
ensemble/
  index.json
  build-report.json
```

Schema `2.0` contains exactly one additional derived artifact:

```text
ensemble/
  index.json
  identity-crosswalk.jsonl
  build-report.json
```

`index.json` persists the complete plan and canonical SHA-256, all three child-plan
digests, common authoritative core binding, exact component index artifacts, fixed
algorithm identities, the crosswalk artifact binding, and summary counts.
`build-report.json` must equal the independently reproduced live report.

## Identity crosswalk 2.0

Every selected authoritative ledger record produces exactly one canonical JSONL row.
Rows are sorted by `(source_id, record_id)` and contain only:

- exact `source_id`, `record_id`, and `record_sha256`;
- exact `concept_id`, `concept_type`, `concept_path`, and actual `source_path` copied
  from the ledger;
- governed `group_namespace` and `group_key`, plus their deterministic `group_id`;
- an exact `record-body` Unicode character-range locator;
- the authoritative body `text_sha256`; and
- a deterministic `evidence_id` bound to the complete record identity, locator, and
  text hash.

The crosswalk is total over the selected records, closed-schema, canonical, and
hash-bound. It is derived evidence metadata, not an authoritative equivalence graph.
Only explicit plan overrides may place multiple records in one group.

## Independent validation

Each component retains its own closed artifact schema and deterministic validator.
All component core objects are byte-for-byte equal. The ensemble validator also:

1. recomputes every child-plan digest and compares stored child plans where present;
2. rederives the complete crosswalk from `semantic/records.jsonl`;
3. requires canonical crosswalk bytes and exact hash/count binding;
4. requires adaptive documents, graph sections, and embedding chunks to cover the
   identical `(source_id, record_id, record_sha256)` set; and
5. rejects stale reports, unknown artifacts, unsafe filesystem indirection, or any
   authority-marker change.

The builder creates the core and all projections in one private sibling candidate,
writes the ensemble binding after all child validators pass, validates the completed
candidate, and publishes once. A failed build removes the candidate and leaves the
requested output absent.
