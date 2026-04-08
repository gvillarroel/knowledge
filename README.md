# knowledge

`know` is a Python CLI for building a local knowledge base in `~/.knowledge`.

Each knowledge key is an independent local collection with declarative source registrations, raw synchronized content, exported Markdown, and repeatable commands stored in metadata.

## Install

```bash
uv tool install .
```

From GitHub:

```bash
uv tool install git+https://github.com/<owner>/<repo>.git
```

The installed executable is `know`.

For browser-assisted `site` capture on Windows, install `know` with Python 3.12 explicitly:

```powershell
uv python install 3.12
uv tool install --python 3.12 --force .
```

Use the same pattern for GitHub installs:

```powershell
uv python install 3.12
uv tool install --python 3.12 --force git+https://github.com/<owner>/<repo>.git
```

This matters because the CDP BFS site workflow depends on the Python `playwright` package in the tool runtime. In this workspace, Python 3.14 was not a reliable runtime for the full `site` stack, while Python 3.12 worked with the required dependencies.

## Quick Start

```bash
know add key research
know set credential jira_token secret-token
know add confluence --space ENG --key research
know add aha PROD --key research
know add arxiv https://arxiv.org/abs/1706.03762 --key research
know add google-releases https://docs.cloud.google.com/feeds/gcp-release-notes.xml --key research
know add github-repo https://github.com/example/repo.git --key research --branch main --branch develop
know add tv research-sources --key research --source-command "know list sources --key research --json"
know list sources --key research
know search confluence "incident postmortem"
know search arxiv "attention is all you need" --max-results 5 --sort-by submittedDate
know sync --key research
know export --key research
```

## Typical Workflow

1. Create a key with `know add key <KEY>`.
2. Register one or more sources under that key.
3. Inspect registrations with `know list sources --key <KEY>`.
4. Run `know sync --key <KEY>` to materialize raw source data locally.
5. Run `know export --key <KEY>` to build Markdown output and a zip archive.

The command family stays consistent across source types, so the same pattern works for Confluence, Jira, arXiv, websites, videos, GitHub repositories, Google release feeds, Aha workspaces, and Television channel definitions.

## Browser-Assisted Site Capture

The `site` source supports a browser-assisted capture mode for sites that rate-limit plain HTTP scraping.
There is no separate `know cdp-bfs` command. You keep using the normal `site` commands:

- `know add site ...`
- `know sync site ...`

The default site strategy is now BFS over HTTP whenever possible.
If `KNOW_SITE_CDP_URL` is set, that same BFS flow can reuse your live browser session.
Use `KNOW_SITE_FORCE_CRAWL4AI=1` only when you explicitly want the `crawl4ai` strategy instead.

Set `KNOW_SITE_CDP_URL` to a live Chrome or Brave DevTools endpoint such as `http://127.0.0.1:9222`.
When that variable is present, `know` reuses cookies from the connected browser session and applies them to the HTTP crawler.

This is especially useful for `docs.cloud.google.com`, where:

- plain automated requests can be redirected to Google `sorry` pages
- HTTP BFS crawling with the browser session cookies can capture the intended documentation subtree more reliably
- scoped extraction from the primary page content produces cleaner Markdown than full-document stripping

Recommended workflow:

```powershell
& "$env:ProgramFiles\\Google\\Chrome\\Application\\chrome.exe" `
  --remote-debugging-port=9222 `
  --remote-debugging-address=127.0.0.1 `
  --user-data-dir="$env:TEMP\\chrome-cdp-profile"

$env:KNOW_SITE_CDP_URL = "http://127.0.0.1:9222"
know add site https://docs.cloud.google.com/bigquery/docs --key research --max-depth 1 --max-pages 10
know sync site https://docs.cloud.google.com/bigquery/docs --key research
```

What happens in that flow:

1. Chrome or Brave stays open with your authenticated browser session.
2. `know` connects to the DevTools endpoint from `KNOW_SITE_CDP_URL`.
3. For `docs.cloud.google.com`, the `site` adapter prefers the CDP-assisted BFS HTTP path.
4. The crawler reuses browser cookies, stays inside the documentation subtree, and extracts primary page content before converting it to Markdown.

Safety behavior:

- anti-bot pages are detected and fail the sync instead of overwriting a healthy corpus
- site sync prefers BFS by default
- when `KNOW_SITE_CDP_URL` is present, the BFS path can reuse the connected browser session
- `KNOW_SITE_FORCE_CRAWL4AI=1` switches the primary strategy to `crawl4ai`
- the CDP mode requires the Python `playwright` package, but it connects to your existing Chrome session and does not require a bundled Playwright browser install

For a cleaner on-disk layout, register site sources with `--compact`:

```bash
know add site https://docs.cloud.google.com/bigquery/docs --key research --max-depth 1 --max-pages 10 --compact
```

Compact site output keeps only:

- `pages/*.md` with YAML frontmatter
- `pages.json` as the page index
- `source-metadata.yaml` as source-level sync metadata

It does not write per-page JSON sidecars.

### Verifying that CDP BFS was used

After sync, inspect the generated Markdown frontmatter under the site source directory. The page metadata should include a fetch mode such as:

- `http_cdp_bfs` for the HTTP crawler seeded with browser cookies
- `browser_cdp` for pages fetched directly through the live browser session

If you do not set `KNOW_SITE_CDP_URL`, the same site source falls back to the regular non-CDP path.

### When to use `site-spikes`

The production workflow above is for normal `know sync site ...` usage.
If you want to compare multiple crawl strategies side by side, use the separate benchmark runner documented in [docs/site-spikes.md](docs/site-spikes.md).

## Store Layout

```text
~/.knowledge/
  config.yaml
  keys.yaml
  exports/
  <key>/
    metadata.yaml
    confluence/
    arxiv/
    google_releases/
    github/
    jira/
    aha/
    raw/
    library/
    cache/
```

## Common Commands

```bash
know --help
know add key <KEY>
know set credential <NAME> <VALUE>
know list keys
know list sources --key <KEY>
know add confluence --space <SPACE> --key <KEY>
know search confluence "text search"
know search arxiv "all:transformer" --max-results 10
know add arxiv <URL> --key <KEY>
know add google-releases <FEED_URL> --key <KEY>
know add github-repo <REPO_URL> --key <KEY> --branch <BRANCH>
know add jira-project <PROJECT> --key <KEY>
know add aha <PRODUCT> --key <KEY>
know add tv
know add tv <CHANNEL> --key <KEY> --source-command <COMMAND>
know sync --key <KEY>
know export --key <KEY>
know import <ARCHIVE.zip>
```

## Television Workflows

`know` supports Television in two complementary ways:

- You can register a `television` source so a reusable `channel.toml` is generated and stored under the knowledge key.
- Several list and search commands can emit `--format television` or `--format television-preview` output directly for `tv`.

### Browse knowledge keys in Television

```bash
tv \
  --source-command "know list keys --format television" \
  --preview-command "know list keys --format television-preview --entry '{}'"
```

### Browse registered sources for one key

```bash
tv \
  --source-command "know list sources --key research --format television" \
  --preview-command "know list sources --key research --format television-preview --entry '{}'"
```

### Install the bundled Television cables

```bash
know add tv
```

This copies the repository's pre-built `.toml` channel files into `~/.config/television/cable/`.

### Create a reusable Television channel from `know list sources`

```bash
know add tv research-sources --key research \
  --description "Browse all registered sources for the research key" \
  --source-command "know list sources --key research --format television" \
  --preview-command "know list sources --key research --format television-preview --entry '{}'"
know sync television research-sources --key research
```

### Create a reusable Television channel from arXiv search

```bash
know add tv arxiv-transformers --key research \
  --description "Browse arXiv search results for transformer papers" \
  --source-command "know search arxiv \"attention is all you need\" --format television --max-results 20 --sort-by submittedDate" \
  --preview-command "know search arxiv \"attention is all you need\" --format television-preview --entry '{}'"
know sync television arxiv-transformers --key research
```

After sync, the generated Television source writes a `channel.toml`, a command manifest, and a short README under the source raw directory. You can either copy the generated channel into `~/.config/television/cable/` or run the inline command from the manifest.

### Pre-built cables

The repository includes ready-to-use Television cable files in the `cables/` directory at the repository root:

| Cable file | Channel | Description |
|---|---|---|
| `know-keys.toml` | `know-keys` | Browse knowledge keys |
| `know-sources.toml` | `know-sources` | Browse all registered sources |
| `know-confluence.toml` | `know-confluence` | Search Confluence pages |
| `know-jira.toml` | `know-jira` | Search Jira issues |
| `know-arxiv.toml` | `know-arxiv` | Search arXiv papers |
| `know-brave.toml` | `know-brave` | Search the web with Brave Search API |
| `know-follow.toml` | `know-follow` | Inspect follow-up items from GitHub, starred GitHub repos, and Jira |

Install them all at once:

```bash
# Unix / macOS
mkdir -p ~/.config/television/cable
cp cables/*.toml ~/.config/television/cable/

# PowerShell
New-Item -ItemType Directory -Force -Path $HOME/.config/television/cable | Out-Null
Copy-Item cables/*.toml $HOME/.config/television/cable/
```

Then run any channel:

```bash
tv know-keys
tv know-arxiv
tv know-brave
tv know-jira
tv know-follow
```

The bundled `know-follow` cable uses PowerShell `start` on `Enter`, opening the URL returned by `know browse follow-url`. If you want a Python-managed fallback, `know browse follow-open` is still available as a CLI command. GitHub follow items are collected from both your accessible repositories and repositories you have starred, then filtered down to recently active repos before loading open issues, PRs, and discussions.

## Notes

- `keys.yaml` stores named credentials that can be referenced as `$name`.
- Credential management also follows the `know <verb> <object>` pattern: `know set credential ...` and `know list credentials`.
- `know add aha <PRODUCT> --key <KEY>` can read `AHA_BASE_URL` and `AHA_TOKEN` from `.env`, storing the token as `$env:AHA_TOKEN` instead of copying the secret into metadata.
- Exported Markdown always includes YAML frontmatter with source provenance.
- `know export` renders Markdown into each key library and also produces a zip archive for import or transfer.
- Television channel sources materialize a reusable `channel.toml` plus install/run commands for `tv`.
- Google release feeds are normalized into one Markdown document per feed entry date plus the raw `feed.xml`.
- Human docs are in `docs/`.
- Coverage gate command: `python scripts/check_coverage.py --threshold 80`
