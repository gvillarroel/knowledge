# ADR 0002: Minimal Source Output Layout

## Status

Accepted

## Context

The current source sync layout mixes final reader-facing documents with transient conversion artifacts such as JSON sidecars, XML snapshots, auxiliary manifests, and generated helper files. That creates unnecessary output noise, makes exports harder to reason about, and diverges from the user-facing contract that downstream consumers mostly need:

- final Markdown documents with YAML frontmatter; and
- one source-level metadata file with enough information to refresh the source later.

The repository already moved `site` toward a compact layout, but the same rule is not applied consistently across processed source types.

## Decision

Processed source sync commands must write the minimum durable output needed for reading and future refreshes:

- keep only final Markdown documents with YAML frontmatter;
- keep exactly one source-level metadata file: `source-metadata.yaml`;
- omit temporary, intermediate, and redundant sidecar files from the final source directory;
- avoid parallel raw/library trees for processed sources; the synced source directory is the final layout.

`source-metadata.yaml` is the only required non-document artifact per processed source. It must contain the minimum fields needed to understand and refresh the source later:

- `knowledge_key`
- `source_id`
- `source_type`
- `title`
- `last_synced_at`
- `update_command`
- `delete_command`
- `config`
- `stats`

## Per-source consequences

- `confluence` and `jira` already fit the model closely and should keep Markdown-only outputs plus `source-metadata.yaml`.
- `site` must always write page Markdown under `pages/` and stop writing page sidecars or page indexes.
- `arxiv` must sync directly to `paper.md` and stop writing raw feed/XML helper files.
- `video` must sync directly to `transcript.md` and stop writing JSON transcript and metadata sidecars.
- `google_releases` must keep entry Markdown documents and stop writing feed snapshots and entry manifests.
- `aha` must write Markdown documents instead of JSON-only payload dumps.
- `television` must keep only the generated channel TOML plus `source-metadata.yaml`; helper manifests and README files are redundant.

## Non-goals

This ADR does not yet redefine the `github` repository source. Its current purpose is preserving repository files rather than producing normalized Markdown documents, so it needs a separate decision.

## Implementation notes

- `sync` is responsible for producing the final layout.
- `export` must treat already-final source layouts as pass-through and must not generate duplicate derived files for them.
- legacy raw files may still be recognized during import/export compatibility paths, but new sync runs must not emit them.
