# know CLI

`know` manages a local knowledge store in `~/.knowledge`.

## Core commands

```bash
know --help
know add key research
know set credential jira_token secret-token
know add confluence --space ENG --key research
know add jira-project KAN --key research
know add aha-workspace PROD --key research
know add arxiv https://arxiv.org/abs/1706.03762 --key research
know add google-releases https://docs.cloud.google.com/feeds/gcp-release-notes.xml --key research
know add site https://openai.com/index/harness-engineering/ --key research
know add github-repo https://github.com/example/repo.git --key research --branch main --branch develop
know add television research-sources --key research --source-command "know list sources --key research --json"
know list keys
know list credentials
know list sources --key research
know search confluence "incident postmortem" --space ENG --type page --label runbook
know search jira "search bug" --project KAN --status "In Progress" --field summary --field status
know search arxiv "all:transformer" --max-results 10 --sort-by relevance
know sync --key research
know export --key research
know import ~/.knowledge/exports/knowledge-export-20260322T180000Z.zip
```

## Recommended flow

1. Create a key with `know add key research`.
2. Attach one or more sources with `know add ... --key research`.
3. Use `know list sources --key research` to confirm the registrations and saved commands.
4. Use `know sync --key research` to fetch or generate raw source content.
5. Use `know export --key research` to build normalized Markdown and a zip archive.

When you need an interactive terminal browser, prefer `television` output formats or register a dedicated Television source.

## Store shape

```text
~/.knowledge/
  config.yaml
  keys.yaml
  exports/
  <key>/
    metadata.yaml
    confluence/
      <source-id>/
        *.md
    arxiv/
      <source-id>/
    google_releases/
      <source-id>/
    site/
      <source-id>/
    github/
      <source-id>/
    jira/
      <source-id>/
    aha/
      <source-id>/
    television/
      <source-id>/
```

## Source behavior

- Confluence sync stores one Markdown file per page with YAML frontmatter.
- Jira sync stores one Markdown file per issue with YAML frontmatter.
- Confluence search uses the current Confluence search API with CQL filters.
- Jira search uses Jira REST API v3 search.
- Television sync stores a `channel.toml`, a command manifest, and install/run instructions for `tv`.
- Google release feeds store the raw Atom XML plus one normalized Markdown file per feed entry under `entries/`.
- Aha workspaces can read `AHA_BASE_URL` and `AHA_TOKEN` from `.env`, and the token is stored as a `$env:` reference instead of being persisted directly in source metadata.

## Television output formats

These commands can emit Television-compatible rows directly:

- `know list keys --format television`
- `know list credentials --format television`
- `know list sources --format television`
- `know search confluence ... --format television`
- `know search jira ... --format television`
- `know search arxiv ... --format television`

The matching preview mode is `--format television-preview --entry '{}'`.

## Television examples

### Browse keys with `tv`

```bash
tv \
  --source-command "know list keys --format television" \
  --preview-command "know list keys --format television-preview --entry '{}'"
```

### Browse sources attached to one key

```bash
tv \
  --source-command "know list sources --key research --format television" \
  --preview-command "know list sources --key research --format television-preview --entry '{}'"
```

### Browse arXiv search results in `tv`

```bash
tv \
  --source-command "know search arxiv \"attention is all you need\" --format television --max-results 20 --sort-by submittedDate" \
  --preview-command "know search arxiv \"attention is all you need\" --format television-preview --entry '{}'"
```

### Persist an arXiv Television channel in the knowledge store

```bash
know add television arxiv-transformers --key research \
  --description "Browse arXiv search results for transformer papers" \
  --source-command "know search arxiv \"attention is all you need\" --format television --max-results 20" \
  --preview-command "know search arxiv \"attention is all you need\" --format television-preview --entry '{}'"
know sync television arxiv-transformers --key research
```

### Persist a source inventory Television channel

```bash
know add television research-sources --key research \
  --description "Browse registered sources for the research key" \
  --source-command "know list sources --key research --format television" \
  --preview-command "know list sources --key research --format television-preview --entry '{}'"
know sync television research-sources --key research
```

After `know sync television ...`, the generated source directory contains:

- `channel.toml` for Television.
- `commands.json` with install and run helpers.
- `README.md` describing how to install or run the channel.

## Flags

- `--json` — Emit output as JSON.
- `--store <PATH>` — Override the default store path.
- `--verbose` — Print progress messages during sync and export.
- `--quiet` — Suppress all non-error output.
- `--format television` — Emit one-line-per-result output for `tv` source commands.
- `--format television-preview` — Render a detail pane for the selected `tv` row.
- `--entry <ROW>` — Identify the selected row when using `--format television-preview`.

## Television integration

Every list and search command supports `--format television` and `--format television-preview`.
Use them as `tv` source and preview commands respectively.

### Ready-to-use cables

Pre-built cable definitions live in `cables/` at the repository root.  Copy any `.toml`
file into `~/.config/television/cable/` and run `tv <channel-name>`.

| Cable file | Channel | Description |
|---|---|---|
| `know-keys.toml` | `know-keys` | Browse knowledge keys |
| `know-sources.toml` | `know-sources` | Browse all registered sources |
| `know-credentials.toml` | `know-credentials` | Browse stored credentials |
| `know-confluence.toml` | `know-confluence` | Search Confluence pages |
| `know-jira.toml` | `know-jira` | Search Jira issues |
| `know-arxiv.toml` | `know-arxiv` | Search arXiv papers |

### Quick install

```bash
# Unix / macOS
cp cables/*.toml ~/.config/television/cable/

# PowerShell
Copy-Item cables/*.toml $HOME/.config/television/cable/
```

### Inline usage without installing cables

```bash
# Browse keys
tv --source-command='know list keys --format television' \
   --preview-command='know list keys --format television-preview --entry "{}"'

# Browse sources for a key
tv --source-command='know list sources --key research --format television' \
   --preview-command='know list sources --key research --format television-preview --entry "{}"'

# Search Confluence
tv --source-command='know search confluence "postmortem" --format television' \
   --preview-command='know search confluence "postmortem" --format television-preview --entry "{}"'

# Search Jira
tv --source-command='know search jira "" --project KAN --format television' \
   --preview-command='know search jira "" --project KAN --format television-preview --entry "{}"'

# Search arXiv
tv --source-command='know search arxiv "attention is all you need" --format television --max-results 20' \
   --preview-command='know search arxiv "attention is all you need" --format television-preview --max-results 20 --entry "{}"'
```

### Register a cable as a knowledge source

```bash
know add television jira-browse --key work \
  --description "Browse Jira KAN issues in tv" \
  --source-command "know search jira \"\" --project KAN --format television" \
  --preview-command "know search jira \"\" --project KAN --format television-preview --entry '{}'"
know sync television jira-browse --key work
```
