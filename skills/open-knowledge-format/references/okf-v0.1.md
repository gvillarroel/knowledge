# Open Knowledge Format v0.1 Reference

Use this reference when generating, repairing, or auditing Open Knowledge Format bundles.

## Primary Sources

- Google Cloud announcement, "Introducing the Open Knowledge Format", published June 12, 2026: https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing
- Draft v0.1 specification in `GoogleCloudPlatform/knowledge-catalog`: https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md
- Specification revision reviewed for this skill: `ee67a5ca27044ebe7c38385f5b6cffc2305a9c1a` (June 12, 2026).

## Format Summary

An OKF bundle is a self-contained directory tree of Markdown files. Every normal `.md` file is a concept document. The concept ID is the file path relative to the bundle root without the `.md` suffix.

Each concept document must:

- be UTF-8 Markdown;
- begin with parseable YAML frontmatter delimited by `---`;
- include a non-empty top-level `type` field;
- keep the body as ordinary Markdown.

Recommended frontmatter fields:

- `title`: display name;
- `description`: one-sentence summary;
- `resource`: canonical URI for the asset described by the concept;
- `tags`: YAML list of short categorization strings;
- `timestamp`: ISO 8601 time of the last meaningful change.

Producer-specific fields are allowed. Consumers should preserve unknown fields and tolerate unknown `type` values.

## Reserved Filenames

`index.md` and `log.md` are reserved at every directory level.

Use `index.md` for progressive disclosure: list concepts or subdirectories with Markdown links and short descriptions. A root `index.md` may declare `okf_version: "0.1"` in frontmatter; avoid frontmatter in non-root index files.

Use `log.md` for chronological update history. Date headings should use `YYYY-MM-DD`.

## Links And Citations

Concepts can link to each other with standard Markdown links. Prefer bundle-root absolute links such as `/tables/orders.md` when stable cross-links matter. Relative links are valid. Broken links are not a conformance failure because bundles may be partially generated.

When external sources support claims, add a `# Citations` section near the end of the concept and list numbered links.

## Conformance Checklist

- Every non-reserved `.md` file has parseable YAML frontmatter.
- Every concept frontmatter has a non-empty `type`.
- `index.md` and `log.md` are used only for their reserved meanings.
- Consumers do not reject missing optional fields, unknown fields, unknown types, broken links, or missing indexes.

## Native Skill Compatibility

Codex `SKILL.md` is not itself an OKF concept document. Its discovery frontmatter uses `name` and `description`, while a normal OKF concept requires a top-level `type`. Do not merge those contracts or hide `type` under a nested compatibility marker.

To exchange project skills through OKF:

1. Keep each native `SKILL.md` valid for its agent runtime.
2. Create a dedicated OKF bundle subdirectory.
3. Project each skill into a normal concept with `type: Agent Skill`, a display `title`, its trigger `description`, and source-traceability extension fields.
4. Copy the skill's Markdown instructions into the concept body.
5. Regenerate and validate the projection whenever skills change.

From the copied skill root, use `python scripts/build_project_okf_bundle.py <project-root>` for projects that follow the `skills/<name>/SKILL.md` layout.
