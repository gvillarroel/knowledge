# Closed Harbor Answer Contract

## Authority model

TF-IDF scores, facets, support IDs, ranks, and excerpts are derived discovery artifacts. They are
non-authoritative. The finalizer copies public evidence metadata from the validated
`semantic/records.jsonl` row and hashes the complete record body selected by the closed locator
`{"kind":"record","target":"record.body"}`.

The bundle remains read-only. The compiler writes only to standard output unless the caller chooses
shell redirection outside the bundle.

## Support pack

`prepare` binds these values into `support_pack_sha256`:

- schema version;
- exact question ID and SHA-256 of the exact normalized question input;
- all retrieval parameters;
- ordered facet text; and
- ordered supports, including their ledger identities, body hashes, and bounded excerpts.

Copy the emitted `draft_template`; do not synthesize its binding values. A support ID is opaque. It
must not be shortened or recreated.

## Draft schema

The draft has exactly `question_id`, `question_sha256`, `parameters`, `support_pack_sha256`, `answer`,
and `evidence`. `answer` has exactly `summary` and `claims`. Keep the summary within 450 words and
the claim array within 64 items. Each claim has exactly `statement` and
`evidence_indices`.

The draft `evidence` array contains support ID strings, not evidence objects. List a support at the
position where a claim first needs it. Every listed support must be used, every claim must cite at
least one valid index, and duplicate indices or support IDs are forbidden.

## Public result

`finalize` emits exactly:

1. `question_id`;
2. `answer`, with `summary` followed by `claims`; and
3. `evidence` in first-use order.

Each evidence row contains exactly `source_id`, `record_id`, `concept_path`, `source_path`,
`record_sha256`, `locator`, and `text_sha256`. Do not edit this output. A hand-transcribed locator,
path, or hash invalidates the evidence binding.

## Failure handling

Treat a nonzero exit as a closed gate. Repair the draft or rerun `prepare`; never bypass validation
by assembling public evidence manually. If the question or any parameter changes, discard the old
draft and support pack.
