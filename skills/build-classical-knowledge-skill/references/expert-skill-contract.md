# Generated Classical Expert Contract

## Contents

- [Inputs](#inputs)
- [Output](#output)
- [Manifest](#manifest)
- [Read-only query contract](#read-only-query-contract)
- [Citation resolution](#citation-resolution)
- [Validation and comparison](#validation-and-comparison)

## Inputs

The generator accepts four authority-bearing inputs:

1. a closed Semantic OKF source manifest;
2. a closed classical retrieval plan;
3. a reviewed application-guidance Markdown file; and
4. a new output directory whose basename is the generated skill name.

The guidance must describe application behavior, not duplicate the corpus. It
must include Scope, Application workflow, Decision rules, and Evidence and
limits. The builder normalizes it to UTF-8 LF and binds the accepted bytes.

## Output

The generated skill has this closed executable surface:

```text
<skill-name>/
  SKILL.md
  expert-manifest.json
  agents/openai.yaml
  references/
    guidance.md
    knowledge/
      index.md
      concepts/
      semantic/
      classical/
  scripts/
    query_expert_knowledge.py
    _classical_snapshot.py
    runtime_smoke.py
    requirements.txt
```

The knowledge tree may contain every file required by the Semantic OKF core and
the six-file classical projection. The scripts directory is closed to the four
listed regular files. Consultation requires only the Python standard library.

## Manifest

`expert-manifest.json` uses schema `classical-knowledge-skill/1.0`. It binds:

- skill name and trigger description;
- generator identity, concept layout, default query mode, input manifest hash,
  plan-input hash, and completed deep-validation state;
- complete embedded-knowledge tree digest and file count;
- authoritative record count and core-tree digest;
- classical index and canonical plan digests; and
- path, byte count, and SHA-256 for every generated instruction, guidance,
  runtime, requirements, and interface artifact.

It contains no timestamp or absolute input path. The manifest itself is part of
the complete generated-skill tree digest returned by the builder.

## Read-only query contract

Every command verifies the expert manifest, every bound executable artifact,
the complete knowledge tree, the authoritative record count, and the classical
index before operating. It creates no cache, bytecode, query, or answer file.

- `verify` checks every record-to-physical-evidence binding. Add
  `--deep-validation` to independently rederive documents, term statistics,
  PPMI associations, topics, and document-topic weights.
- `inspect` returns the classical capabilities and exact snapshot digests.
- `search` preserves the standalone classical result identity, scores, ranks,
  expansion terms, modes, filters, and locators while adding physical citation
  fields.
- `get` returns one exact `(source_id, record_id)` ledger record and optionally
  its body.

`--query` and `--contains` are aliases. `--top-k` and `--limit` are aliases.
The default route is `fusion`; callers may select any classical route directly.

## Citation resolution

The authoritative ledger keeps a logical `concept_path` per record. Under
`record-per-file-v1`, that path is also the physical file. Under
`source-packed-v1`, repeated CSV, JSON, or RDF records are stored in
`concepts/<source_id>.md` and addressed by
`record-<first-16-record-sha256-hex>`.

The generated helper verifies both layouts and returns an existing
`evidence_path`, an optional `evidence_anchor`, and their combined `citation`.
It rejects a missing collection, missing anchor, changed body, path escape,
symlink, stale index, or tree drift before returning a result.

## Validation and comparison

A passing package requires:

- deep core and classical validation;
- every ledger record bound to exact physical Markdown;
- no unknown or unsafe artifact;
- deterministic `--check` reproduction;
- successful generated runtime smoke and representative queries; and
- identical per-mode ranked document IDs to the standalone classical query
  runtime over the same built snapshot.

For dataset claims, keep direct retrieval, exact evidence, deterministic build,
latency, and grounded answer quality separate. The integrated artifact is a
three-stage build/package/consult path. It does not redefine the canonical
`build-consult` or `consult-only` mount contracts.
