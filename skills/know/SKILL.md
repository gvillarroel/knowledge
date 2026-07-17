---
name: know
description: Operate the `know` CLI to create local knowledge keys, register sources, inspect configuration, synchronize content into `~/.knowledge`, export normalized Markdown libraries, import archives, or connect Television output. Use when Codex needs to run or explain a reproducible `know` knowledge-base workflow.
---

# Know CLI

Use the `know` CLI to build and maintain a local, reproducible knowledge base inside `~/.knowledge`.

## Standalone boundary

- Treat the installed `know` executable, configured remote services, and user credentials as explicit external prerequisites.
- Use this `SKILL.md` as the operational contract. Do not require root documentation, source modules, cable files, or another skill.
- Run `know --help` and the relevant subcommand `--help` before using a command that is not covered below. If the executable or a requested integration is unavailable, return that diagnostic without searching a repository checkout for missing behavior.

## Follow the standard workflow

1. Create a key with `know add key <KEY>`.
2. Attach sources with commands such as:
   `know add confluence --space <SPACE> --key <KEY>`
   `know add arxiv <URL> --key <KEY>`
   `know add google-releases <FEED_URL> --key <KEY>`
   `know add github-repo <REPO_URL> --key <KEY> --branch <BRANCH>`
   `know add jira-project <PROJECT> --key <KEY>`
   `know add television <CHANNEL> --key <KEY> --source-command <COMMAND>`
   `know add video <VIDEO_URL_OR_PATH> --key <KEY>`
3. Inspect registered sources with `know list sources --key <KEY>`.


## Preserve operational expectations

- Keep documents in English.
- Prefer the command shape `know <verb> <object>` consistently and avoid noun-first top-level forms such as `know key ...`.
- Preserve source content under `<key>/<source-type>/<source-id>/`.
- Ensure exported Markdown includes YAML frontmatter with source provenance.
- Ensure exported Markdown remains Open Knowledge Format compatible: every concept document needs a non-empty `type` field and should preserve `resource`, `tags`, and `timestamp` when they can be derived.
- Verify unfamiliar command shapes through the installed CLI's `--help` output.

## Use credentials and metadata consistently

- Read `~/.knowledge/keys.yaml` when integrations refer to credential aliases such as `$name`.
- Keep source registrations traceable through each key's `metadata.yaml`.
- Preserve update and delete command fields when modifying registered sources.

## Update sources
Synchronize content with `know sync --key <KEY>`.
## Export data
Export normalized Markdown and a zip archive with `know export --key <KEY>`.
## Import Data
Import an archive with `know import <ARCHIVE.zip>`.

## Useful flags

Place global flags before the command name. For example, use `know --store ./stores/lab --json list sources --key research`, not `know list sources --store ./stores/lab --json`.

- `--json` — Emit structured JSON output. It is a global flag, so place it before the command, for example `know --json list sources --key research`; use a subcommand's `--format json` option when available.
- `--verbose` — Show progress messages during sync and export.
- `--quiet` — Suppress non-error output.
- `--store <PATH>` — Override the default `~/.knowledge` store path.
- `--format television` — Emit one-line-per-result output for `tv` source commands.
- `--format television-preview` — Render a detail pane for the selected `tv` row.
- `--entry <ROW>` — Select the row to preview when using `--format television-preview`.

## Television integration

All list and search commands support `--format television` and `--format television-preview` so they can
be wired directly into `tv` as source and preview commands.

### Cable files

Generate reproducible cable files through `know add television` and `know sync television`, or use the inline commands below. Treat any pre-built cable supplied by a target project as optional user input, not as a prerequisite of this skill.

### Inline tv usage

```bash
tv --source-command='know list keys --format television' \
   --preview-command='know list keys --format television-preview --entry "{}"'

tv --source-command='know search jira "" --project KAN --format television' \
   --preview-command='know search jira "" --project KAN --format television-preview --entry "{}"'
```

### Register a television channel as a source

```bash
know add television jira-browse --key work \
  --description "Browse Jira KAN issues in tv" \
  --source-command "know search jira \"\" --project KAN --format television" \
  --preview-command "know search jira \"\" --project KAN --format television-preview --entry '{}'"
know sync television jira-browse --key work
```

For `television` recipes, prefer `know search arxiv ... --format television` as the source command and `--format television-preview --entry '{}'` as the preview command when listing arXiv search results in `tv`.
