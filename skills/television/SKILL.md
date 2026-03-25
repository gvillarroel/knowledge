---
name: television
description: Use when Codex needs to create, update, or troubleshoot Television (`tv`) channels in this repository, especially when wiring `know add television`, `know sync television`, or `know search arxiv --format television` into reproducible terminal discovery workflows.
---

# Overview

Use this skill to build reproducible `tv` channels backed by `know`.

## Follow the standard workflow

1. Register a channel with `know add television <CHANNEL> --key <KEY> --source-command <COMMAND>`.
2. Add `--preview-command` when the selected row needs a richer detail pane.
3. Materialize the channel bundle with `know sync television <CHANNEL> --key <KEY>`.
4. Use the generated `commands.json` to install the TOML file into `~/.config/television/cable/`.

## Prefer repository-native patterns

- Keep channel definitions reproducible through `know`; do not hand-author ad hoc files when the CLI can generate them.
- Store channels under `~/.knowledge/<key>/television/<source-id>/`.
- Preserve `update_command` and `delete_command` in key metadata.
- Keep all examples and generated documents in English.

## arXiv recipe

Use `know search arxiv ... --format television` for the source list and `--format television-preview --entry '{}'` for the preview pane.

Example:

```bash
know add television arxiv-transformers --key research \
  --description "Browse arXiv search results for transformers" \
  --source-command "know search arxiv \"attention is all you need\" --format television --max-results 20 --sort-by submittedDate" \
  --preview-command "know search arxiv \"attention is all you need\" --format television-preview --entry '{}'"
know sync television arxiv-transformers --key research
```

## Source inventory recipe

Use `know list sources --key <KEY> --json` as the source command when the goal is to browse registered integrations for a key.

Example:

```bash
know add television knowledge-sources --key research \
  --description "Browse registered knowledge sources" \
  --source-command "know list sources --key research --json"
know sync television knowledge-sources --key research
```

## What to inspect when something breaks

- Read `src/knowledge/sources/television.py` for generated TOML structure and install commands.
- Read `src/knowledge/commands.py` and `src/knowledge/cli.py` for CLI surface and arXiv television formatting.
- Read `docs/cli.md` and `README.md` for repository examples before inventing a new command shape.
