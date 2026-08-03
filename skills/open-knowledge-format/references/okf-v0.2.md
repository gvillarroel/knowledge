# Open Knowledge Format v0.2 Reference

Use this reference when generating, migrating, repairing, or auditing Open
Knowledge Format bundles.

## Primary sources

- Google Cloud announcement, "Introducing the Open Knowledge Format", published June 12, 2026: https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing
- Current specification in `GoogleCloudPlatform/knowledge-catalog`: https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md
- Specification revision reviewed for this skill: `3fcbb9f828c2f23d109c855ee403c3a4c81f3a96` (July 24, 2026).

## Format summary

An OKF bundle is a self-contained directory tree of UTF-8 Markdown files.
Every normal `.md` file is a concept document. The concept ID is the file path
relative to the bundle root without the `.md` suffix.

Each concept document must:

- begin with parseable YAML frontmatter delimited by `---`;
- include a non-empty top-level `type` field; and
- keep the body as ordinary Markdown.

Recommended frontmatter fields are `title`, `description`, `resource`, and
`tags`. Producer-specific fields are allowed. Consumers must tolerate unknown
fields and unknown `type` values.

## Provenance, trust, and lifecycle

Use `sources` for materials from which the concept derives. Every entry requires
a non-empty `resource`; `id`, `title`, `author`, `usage_count`, and
`last_modified` are optional. Put `usage_window: {from, to}` beside `sources`,
or on one source entry as an override, whenever `usage_count` is present. Use a
Markdown footnote label matching `sources[].id` for per-claim attribution.

Use `generated: {by, at}` to record who or what produced the current content
and, when known, the time of its last meaningful change. `generated.by` is
required whenever `generated` is present. Use `verified` for independent
verification events; accept either one `{by, at}` mapping or a list of them.

Actors use `<producer>/<version>`, `human:<id>`, or `process:<id>`. A consumer
derives trust as unverified when `verified` is absent, machine-confirmed when
only non-human actors verified it, and human-reviewed when any `human:` actor
verified it.

Use `status: draft|stable|deprecated`; omission means `stable`. Use an absolute
`stale_after: YYYY-MM-DD` date when a supported freshness boundary exists.
Omission of any optional family never makes a concept invalid.

## Attested Computation

An independently sanctioned computation is its own concept with
`type: Attested Computation` and a required non-empty `runtime`. Optional
contract fields are:

- `parameters`: typed named values an agent may supply;
- `computation`: a path to the immutable computation, used instead of an
  inline `# Computation` code block;
- `executor`: a resource plus the receipt fields returned by execution; and
- `attester`: deterministic, non-LLM code that checks the receipt.

Do not treat verification as attestation. Verification confirms that the
definition still matches its sources; attestation checks one execution result.
Do not invent either contract from narrative prose.

## Reserved filenames

`index.md` and `log.md` are reserved at every directory level.

Use `index.md` for progressive disclosure. A root `index.md` may declare
`okf_version: "0.2"` in frontmatter; avoid frontmatter in non-root index files.
Use `log.md` for chronological update history with `YYYY-MM-DD` headings,
newest first.

## Links and migration

Concepts may use normal Markdown links. Prefer bundle-root absolute links when
stable cross-links matter; relative links are valid. Broken links are not a
conformance failure.

When migrating v0.1:

1. move legacy `timestamp` into `generated.at` and add an evidence-backed
   `generated.by`;
2. move body `# Citations` entries into `sources`;
3. use keyed footnotes for claim-level attribution when the source-to-claim
   relationship is known; and
4. preserve legacy or producer-specific fields only when needed for lossless
   round-tripping.

Consumers may fall back to legacy `timestamp` and `# Citations`, but v0.2
producers should emit `generated` and `sources`.

## Conformance checklist

- Every non-reserved `.md` file has parseable YAML frontmatter.
- Every concept frontmatter has a non-empty `type`.
- `index.md` and `log.md` are used only for their reserved meanings.
- Optional v0.2 families follow their documented shapes when present.
- Consumers do not reject missing optional fields, unknown fields, unknown
  types, broken links, or missing indexes.

## Native skill compatibility

Codex `SKILL.md` is not itself an OKF concept document. Keep its discovery
frontmatter limited to `name` and `description`. Project each skill into a
dedicated OKF bundle concept with `type: Agent Skill`, `sources` pointing back
to the native file, and `generated.by` identifying the deterministic projector.

From the copied skill root, use
`python scripts/build_project_okf_bundle.py <project-root>` for projects that
follow the `skills/<name>/SKILL.md` layout. The default generated bundle is
`<project-root>/build/okf`; native skills remain authoritative under `skills/`.
