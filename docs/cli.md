# know CLI

`know` manages a local knowledge store in `~/.knowledge`.

## Core commands

```bash
know --help
know add key research
know set credential jira_token secret-token
know add confluence --space ENG --key research
know add jira-project KAN --key research
know add aha PROD --key research
know add arxiv https://arxiv.org/abs/1706.03762 --key research
know add google-releases https://docs.cloud.google.com/feeds/gcp-release-notes.xml --key research
know add site https://openai.com/index/harness-engineering/ --key research
know add site https://docs.cloud.google.com/bigquery/docs --key research --max-depth 1 --max-pages 10 --compact
know add github-repo https://github.com/example/repo.git --key research --branch main --branch develop
know add tv research-sources --key research --source-command "know list sources --key research --json"
know list keys
know list sources --key research
know search confluence "incident postmortem" --space ENG --type page --label runbook
know search jira "search bug" --project KAN --status "In Progress" --field summary --field status
know search arxiv "all:transformer" --max-results 10 --sort-by relevance
know search brave "text to search" --count 5
know search brave "local coffee" --country US --search-lang en --ui-lang en-US --safesearch moderate --result-filter web --result-filter locations --loc-lat 40.7 --loc-long -74.0 --loc-city "New York"
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
- Site sync detects anti-bot pages and fails the sync instead of overwriting a healthy source directory.
- Site sync can reuse a live Chrome or Brave session through `KNOW_SITE_CDP_URL=http://127.0.0.1:9222`, loading browser cookies into the HTTP crawler for browser-assisted capture.
- For `docs.cloud.google.com`, the default strategy with `KNOW_SITE_CDP_URL` is a browser-assisted CDP BFS crawl that reuses Chrome cookies and keeps traversal inside the documentation subtree.
- The CDP BFS path extracts `main` or `article` content before converting to Markdown, which produces cleaner output than stripping the entire HTML document.
- Television sync stores a `channel.toml`, a command manifest, and install/run instructions for `tv`.
- Google release feeds store the raw Atom XML plus one normalized Markdown file per feed entry under `entries/`.
- Aha workspaces can read `AHA_BASE_URL` and `AHA_TOKEN` from `.env`, and the token is stored as a `$env:` reference instead of being persisted directly in source metadata.

## Browser-assisted site capture

When a site blocks plain automated requests but works in a real browser session, launch Chrome or Brave with remote debugging and point `KNOW_SITE_CDP_URL` at that session:

```powershell
& "$env:ProgramFiles\\Google\\Chrome\\Application\\chrome.exe" `
  --remote-debugging-port=9222 `
  --remote-debugging-address=127.0.0.1 `
  --user-data-dir="$env:TEMP\\chrome-cdp-profile"

$env:KNOW_SITE_CDP_URL = "http://127.0.0.1:9222"
know sync site https://docs.cloud.google.com/bigquery/docs --key research
```

This mode does not require the `site` source itself to be driven entirely by `crawl4ai`.
For `docs.cloud.google.com`, `know` reuses cookies from the connected browser and runs the HTTP crawler inside the intended documentation subtree.

Relevant environment variables:

- `KNOW_SITE_CDP_URL` — DevTools endpoint for a live browser session
- `KNOW_SITE_FORCE_CRAWL4AI=1` — force deep crawl even on hosts that normally prefer the HTTP crawler
- `KNOW_SITE_HTTP_MAX_ATTEMPTS` — retry count for HTTP fetches
- `KNOW_SITE_HTTP_RETRY_BASE_SECONDS` — linear backoff base for blocked responses

The CDP mode relies on the Python `playwright` package but connects to your existing Chrome or Brave session. It does not require a separate Playwright-managed browser installation for this workflow.

## Compact site output

Use `know add site ... --compact` when you want the `site` source to keep only final page Markdown plus minimal metadata.

Compact `site` layout:

- `pages/*.md` with YAML frontmatter
- `pages.json` containing URL, title, and relative Markdown path
- `source-metadata.yaml` with crawl settings and page count

Compact mode does not write per-page JSON sidecars and is the recommended layout for downstream pipelines that only need final text plus enough metadata to refresh the source later.

## Television output formats

These commands can emit Television-compatible rows directly:

- `know list keys --format television`
- `know list sources --format television`
- `know search confluence ... --format television`
- `know search jira ... --format television`
- `know search arxiv ... --format television`
- `know search brave ... --format television`

The matching preview mode is `--format television-preview --entry '{}'`.

`know search brave` uses the Brave Search API. Configure the key with
`BRAVE_SEARCH_API_KEY` or store it with
`know set credential brave_search_api_key <VALUE>`.
The CLI exposes Brave query parameters such as `--country`, `--search-lang`,
`--ui-lang`, `--offset`, `--safesearch`, `--freshness`, repeatable
`--result-filter`, repeatable `--goggles`, boolean toggles like
`--spellcheck` / `--no-spellcheck`, and location headers like `--loc-lat`,
`--loc-long`, `--loc-timezone`, and `--loc-city`.

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
know add tv arxiv-transformers --key research \
  --description "Browse arXiv search results for transformer papers" \
  --source-command "know search arxiv \"attention is all you need\" --format television --max-results 20" \
  --preview-command "know search arxiv \"attention is all you need\" --format television-preview --entry '{}'"
know sync television arxiv-transformers --key research
```

### Persist a source inventory Television channel

```bash
know add tv research-sources --key research \
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

`know list keys`, `know list sources`, and every `know search ...` command support
`--format television` and `--format television-preview`. Use them as `tv`
source and preview commands respectively.

### Ready-to-use cables

Pre-built cable definitions live in `cables/` at the repository root.  Copy any `.toml`
file into `~/.config/television/cable/` and run `tv <channel-name>`.

| Cable file | Channel | Description |
|---|---|---|
| `know-keys.toml` | `know-keys` | Browse knowledge keys |
| `know-sources.toml` | `know-sources` | Browse all registered sources |
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
know add tv jira-browse --key work \
  --description "Browse Jira KAN issues in tv" \
  --source-command "know search jira \"\" --project KAN --format television" \
  --preview-command "know search jira \"\" --project KAN --format television-preview --entry '{}'"
know sync television jira-browse --key work
```
