# Generated Expert Contract

## Contents

- [Required inputs](#required-inputs)
- [Closed output](#closed-output)
- [Source selection coverage](#source-selection-coverage)
- [Consultation semantics](#consultation-semantics)
- [Acceptance evidence](#acceptance-evidence)

## Required inputs

Each build receives one closed source manifest, reviewed application guidance,
an exact family ID, and a new destination. Embeddings, classical, adaptive,
entity-graph, and ensemble additionally require their family-specific closed
plan. Planless families reject a plan instead of ignoring it.

Guidance is executable policy for the generated expert. It must be specific
enough to decide scope, workflow, evidence requirements, negative evidence,
and limitations; placeholder text is invalid.

JSON/CSV sources with schema fields beyond `id_field` and `title_field` must
declare a `fields` object. Map exactly the intended knowledge fields. A selective
map is valid; use `fields: {}` for an intentional title-only expert. An absent
decision fails before the canonical builder runs. Identity/title-only schemas
may omit the map. Invalid mappings remain subject to canonical validation.

## Closed output

`expert-manifest.json` binds:

- the schema, skill identity, description, and complete canonical family
  contract;
- source-manifest and optional plan input digests;
- the built concept layout and deep-validation requirement;
- every non-knowledge regular file by relative path, byte count, and SHA-256;
- the complete knowledge tree by canonical path/length/content digest;
- the ledger record count and build-report digest; and
- the active generated consultation requirements.

The manifest itself is excluded from its artifact list to avoid a circular
digest. The validator requires its exact closed schema and rejects every
unbound file, link, or special file. Generated experts contain the matched
consultant scripts and documentation, but never builder code.

## Source selection coverage

Every new expert includes `references/source-coverage.json`, bound by the existing
artifact list. Its schema is `semantic-okf-source-coverage/1.0` and it binds the
original source-manifest SHA-256. Each source row records declared schema fields,
identity fields, mapped fields, omitted fields, and whether the raw declaration
explicitly included a map. Omitted fields exclude identity/title fields.

`scope` is `mapped-fields` or `title-only` for structured sources, `native` for
nonstructured sources, and `derived` for ledger source identities absent from
the original declarations. A declared source with no retained records still
has a row with zero counts. `record_count` counts normalized ledger records;
`mapped_value_count` counts present non-null mapped attribute values, while
`null_mapped_value_count` counts present null values. Missing mapped attributes
are a construction error for structured records. `text_characters` sums normalized
ledger body lengths, including the adapter's title and field rendering.

This audit does not compare raw file contents with normalized values. It always
sets `raw_source_fidelity_verified` to false and never certifies complete raw
document retention or that an embedding encoder processed every retained token.
Use the source adapter's rendering contract and independent raw-to-ledger checks
when complete content fidelity is required. Canonical builders and consultants,
knowledge bytes, native payloads and query behavior are unchanged.

## Consultation semantics

The stable helper verifies the complete static binding before every operation,
executes the matched native consultant with CPython `-B`, and checks the
knowledge tree again afterward. Embedding runtimes are forced offline; a
missing pinned local model is an error, not permission to download or silently
fall back.

Search does not normalize away native fields. It translates the stable query,
mode/policy, cutoff, and supported filters to the native CLI, parses its exact
JSON, and recursively adds physical citation fields wherever an authoritative
ledger identity resolves. Every top-level search hit must resolve.

`get` reads the authoritative ledger directly and returns one exact record.
For `source-packed-v1`, its citation uses a digest-derived unique anchor and
the validator confirms that the exact body occurs after that anchor and before
the next record anchor.

## Acceptance evidence

Mechanical parity requires the same canonical input, plan, build layout,
consultant code, query text, route, filters, and cutoff. Compare:

1. complete knowledge tree digest and file count;
2. native payload after removing only generated citation/expert additions;
3. ordered authoritative identities and native score/rank fields;
4. every returned and every ledger-level physical evidence locator;
5. independent family validation and generated deep verification;
6. deterministic reconstruction through `--check`; and
7. absence of query errors or snapshot writes.

These gates establish construction and retrieval equivalence. Semantic answer
quality still requires a separate, sealed evaluation with complete responses
and appropriate adjudication. Do not use a deterministic parity run as a proxy
for a Harbor or human-reviewed grounded-answer score.
