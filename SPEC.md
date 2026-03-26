# SPEC

## Objective

Build a Python CLI called `know` to manage a local knowledge base in `~/.knowledge`, capable of:

- creating named knowledge keys as independent local collections;
- attaching external sources to a key through declarative metadata;
- synchronizing content from multiple systems into a raw local store;
- processing video sources by extracting or generating transcriptions;
- exporting normalized Markdown documents with YAML frontmatter;
- preserving traceability back to the original source;
- supporting repeatable updates through explicit commands stored with each key;
- browsing knowledge interactively with sync-status indicators;
- integrating with Television (`tv`) for terminal-based fuzzy finding and previewing.

## Expected Outcome

The tool should allow a user to create a key, attach sources such as Confluence spaces, arXiv papers, websites, videos, Jira projects, Aha workspaces, Google Cloud release note feeds, and GitHub repositories, then sync and export those sources into a navigable Markdown library ready for search, reading, and downstream tooling.

Television channel definitions may also be attached when a key needs reproducible terminal discovery workflows backed by explicit commands.

## Principles

- The local store in `~/.knowledge` is the operational source of truth.
- Every integration must be reproducible from declarative configuration.
- Source content should remain reproducible from the registered source configuration.
- Every exported document must include source metadata in YAML frontmatter.
- Integrations must support repeatable re-sync without manual intervention.
- Optional dependencies must not block use of the base CLI.
- The default user-facing command is `know`.
- Command naming should remain short and task-oriented: `add`, `list`, `search`, `sync`, `export`, `browse`.
- Video sources must be normalized through transcription before export so they can be consumed like the rest of the text-oriented library.
- Cross-platform compatibility: use `tempfile.gettempdir()` instead of hard-coded paths.

## Non-functional Requirements

- Coverage should be more than 90%.
- Be consistent with patterns and always try to maintain it simple and easy to understand.
- Custom error types for user-facing failures (`KnowledgeError`, `CredentialNotFoundError`, `SourceNotFoundError`, `InvalidURLError`).
- Docstrings on every public class and function.
- URL validation on source registration for `arxiv`, `site`, and `google-releases`.

## Installation

The preferred installation flow is `uv tool install` from GitHub.

```bash
uv tool install git+https://github.com/<owner>/<repo>.git
```

Optional extras may be installed when required by a source adapter.

```bash
uv tool install 'git+https://github.com/<owner>/<repo>.git'
```

## Primary CLI

The CLI binary is `know`.

### Global flags

| Flag | Description |
|---|---|
| `--store <PATH>` | Override the default `~/.knowledge` store path. |
| `--json` | Emit command output as JSON. |
| `--verbose` | Print progress messages during sync and export. |
| `--quiet` | Suppress non-error output. |

### Top-level commands

```
know --help
know init
know add ...
know list ...
know search ...
know sync ...
know del ...
know set ...
know export ...
know import ...
know browse ...
```

### `know add` — Create keys and attach sources

```bash
know add key <KEY>
know add confluence --space <SPACE> --key <KEY> [--base-url URL] [--username REF] [--token REF] [--limit N]
know add arxiv <URL> --key <KEY>
know add site <URL> --key <KEY> [--max-depth N] [--max-pages N]
know add video <VIDEO_URL_OR_PATH> --key <KEY> [--language LANG ...]
know add tv <CHANNEL_NAME> --key <KEY> --source-command <CMD> [--preview-command CMD] [--description TEXT] [--source-display TPL] [--action-command CMD]
know add github-repo <REPO_URL> --key <KEY> [--branch BRANCH ...]
know add google-releases <FEED_URL> --key <KEY>
know add jira-project <PROJECT> --key <KEY> [--base-url URL] [--username REF] [--token REF] [--jql JQL] [--field FIELD ...] [--limit N]
know add aha <WORKSPACE> --key <KEY> [--base-url URL] [--token REF] [--limit N]
```

### `know list` — Inspect keys, credentials, and sources

```bash
know list keys [--format json|television|television-preview] [--entry ROW]
know list credentials [--format json|television|television-preview] [--entry ROW]
know list sources [--key KEY] [--type TYPE] [--format json|television|television-preview] [--entry ROW]
```

### `know search` — Live search against remote APIs

```bash
know search confluence "text" [filters...] [--format json|television|television-preview] [--entry ROW]
know search jira "text" [filters...] [--format json|television|television-preview] [--entry ROW]
know search arxiv "query" [--max-results N] [--sort-by FIELD] [--sort-order DIR] [--format json|television|television-preview] [--entry ROW]
```

`know search <SOURCE> --help` shows all available filters for that source.

### `know sync` — Synchronize content

```bash
know sync --key <KEY>
know sync confluence --space <SPACE> --key <KEY>
know sync arxiv <URL> --key <KEY>
know sync site <URL> --key <KEY>
know sync video <URL_OR_PATH> --key <KEY>
know sync television <CHANNEL_NAME> --key <KEY>
know sync github-repo <REPO_URL> --key <KEY> [--branch BRANCH ...]
know sync google-releases <FEED_URL> --key <KEY>
know sync jira-project <PROJECT> --key <KEY>
know sync aha <WORKSPACE> --key <KEY>
```

### `know del` — Delete a registered source

```bash
know del --key <KEY> <SOURCE_ID>
```

### `know set` — Store configuration values

```bash
know set credential <NAME> <VALUE>
```

### `know export` — Export to zip

```bash
know export [--key KEY]
```

Generates a zip of one or more keys containing normalized Markdown with YAML frontmatter. For video sources, the exported Markdown is generated from the transcription and follows the same frontmatter and traceability rules as every other exported document. If timestamps, speaker segments, chapters, or source transcript metadata are available, they are preserved in raw data and reflected in Markdown when useful.

### `know import` — Import a zip archive

```bash
know import <ARCHIVE.zip>
```

Updates and merges the zipped structure with the current store, merging metadata and adding sources to the local folder.

### `know browse` — Interactive knowledge browsing

The `browse` family provides sync-status-aware views of local and remote knowledge, with Television-compatible output for interactive terminal use.

#### Per-source-type browsers

Each shows items from that source type with synced/unsynced indicators:

```bash
know browse jira [--key KEY] [--format FMT] [--entry ROW]
know browse confluence [--key KEY] [--format FMT] [--entry ROW]
know browse github [--key KEY] [--format FMT] [--entry ROW]
know browse github-activity <OWNER/REPO> [--format FMT] [--entry ROW]
know browse arxiv [--key KEY] [--format FMT] [--entry ROW]
know browse aha [--key KEY] [--format FMT] [--entry ROW]
know browse releases [--key KEY] [--format FMT] [--entry ROW]
know browse videos [--key KEY] [--format FMT] [--entry ROW]
know browse sites [--key KEY] [--format FMT] [--entry ROW]
know browse local [--key KEY] [--type TYPE] [--format FMT] [--entry ROW]
know browse confluence-spaces [--format FMT] [--entry ROW]
know browse confluence-pages --space <SPACE> [--format FMT] [--entry ROW]
know browse jira-projects [--format FMT] [--entry ROW]
```

#### Cross-key aggregate browsers

These operate across all keys for high-level navigation:

```bash
know browse by-key [--format FMT] [--entry ROW]          # Keys with source counts; drill into key
know browse by-type [--format FMT] [--entry ROW]          # Source types with counts; drill into type
know browse papers [--format FMT] [--entry ROW]           # All arXiv papers across keys
know browse repos [--format FMT] [--entry ROW]            # All GitHub repos across keys
know browse repo-files [--repo NAME] [--format FMT] [--entry ROW]  # Files inside a synced repo
know browse files [--query TEXT] [--key KEY] [--format FMT] [--entry ROW]  # Full-text searchable files
know browse recent [--limit N] [--format FMT] [--entry ROW]  # Recently synced sources
know browse stale [--days N] [--format FMT] [--entry ROW]    # Sources not synced in N days
know browse unsynced [--format FMT] [--entry ROW]            # Sources never synced
know browse timeline [--format FMT] [--entry ROW]            # Chronological source timeline
know browse commands [--format FMT] [--entry ROW]            # All sync/delete/export commands
know browse stats [--format FMT] [--entry ROW]               # Knowledge base statistics
know browse crossref [--format FMT] [--entry ROW]            # Sources shared across multiple keys
```

#### Drill-down chain browsers

Used as fork targets from the key or source browsers:

```bash
know browse key-sources --key <KEY> [--format FMT] [--entry ROW]
know browse source-files --key <KEY> --source-id <ID> [--format FMT] [--entry ROW]
```

## Store Structure

```text
~/.knowledge/
  config.yaml
  keys.yaml                  # credential store for integrations
  exports/                   # zip export output
  <key>/
    metadata.yaml
    confluence/
      <source-id>/
        *.md
    arxiv/
      <source-id>/
        *.md
    video/
      <source-id>/
        *.md                 # exported Markdown from transcription
        raw_transcript.*     # raw transcription output (kept separate)
    github/
      <source-id>/
        *                    # cloned repo files
    jira/
      <source-id>/
        *.md
    aha/
      <source-id>/
        *.json
    site/
      <source-id>/
        *.md
    google_releases/
      <source-id>/
        feed.xml             # raw Atom XML
        entries/
          *.md               # one Markdown per feed entry
    television/
      <source-id>/
        <channel-slug>.toml  # Television cable definition
        commands.json         # install/run/sync helpers
        README.md             # human-readable instructions
```

## Key Metadata

Each `~/.knowledge/<key>/metadata.yaml` file must contain:
- store version;
- key name;
- creation timestamp;
- update timestamp;
- the list of registered sources for that key;
- commands that can be used to inspect, sync, or export that key again.

Example:

```yaml
version: 1
name: research
created_at: 2026-03-22T18:00:00+00:00
updated_at: 2026-03-22T18:00:00+00:00
sources:
  - type: confluence
    id: <id>
    title: <title>
    created_at: 2026-03-22T18:00:00+00:00
    updated_at: 2026-03-22T18:00:00+00:00
    update_command: know sync confluence --space <SPACE> --key <KEY>
    delete_command: know del --key <KEY> <id>
    config:
      space: <SPACE>
      base_url: <URL>
      username: $credential_ref
      token: $credential_ref
  - type: arxiv
    id: <id>
    title: <title>
    created_at: 2026-03-22T18:05:00+00:00
    updated_at: 2026-03-22T18:05:00+00:00
    update_command: know sync arxiv <URL> --key <KEY>
    delete_command: know del --key <KEY> <id>
    config:
      url: <URL>
  - type: video
    id: <id>
    title: <title>
    created_at: 2026-03-22T18:10:00+00:00
    updated_at: 2026-03-22T18:10:00+00:00
    update_command: know sync video <VIDEO_URL_OR_PATH> --key <KEY>
    delete_command: know del --key <KEY> <id>
    config:
      url: <VIDEO_URL_OR_PATH>
```

## Source Registration Rules

### `know add key <KEY>`
- Creates `~/.knowledge/<key>/`.
- Creates/updates `metadata.yaml`.
- Fails with a clear error if the key already exists.

### `know add confluence --space <SPACE> --key <KEY>`
- Registers a Confluence space under the selected key.
- Stores the source in key metadata with config for space, base_url, username, token.
- Creates a source record under `~/.knowledge/<key>/confluence/`.

### `know add arxiv <URL> --key <KEY>`
- Validates the URL (must be http/https).
- Registers an arXiv source under the selected key.
- Stores the original URL in the source config.
- Creates a source record under `~/.knowledge/<key>/arxiv/`.

### `know add video <VIDEO_URL_OR_PATH> --key <KEY>`
- Registers a video source under the selected key.
- Stores the original local path or URL in the source config.
- Creates a source record under `~/.knowledge/<key>/video/`.
- During sync, the implementation must obtain a transcription for the video and store the raw transcription output separately from the exported Markdown.

### `know add site <URL> --key <KEY>`
- Validates the URL.
- Registers a website source with optional crawl depth and page limits.
- Creates a source record under `~/.knowledge/<key>/site/`.

### `know add github-repo <REPO_URL> --key <KEY>`
- Registers a GitHub repository source with optional branch filters.
- Creates a source record under `~/.knowledge/<key>/github/`.

### `know add jira-project <PROJECT> --key <KEY>`
- Registers a Jira project source with optional JQL, field selection, and credentials.
- Creates a source record under `~/.knowledge/<key>/jira/`.

### `know add aha <WORKSPACE> --key <KEY>`
- Registers an Aha workspace source. Credentials can be read from environment via `$env:` references.
- Creates a source record under `~/.knowledge/<key>/aha/`.

### `know add google-releases <FEED_URL> --key <KEY>`
- Validates the URL.
- Registers a Google Cloud release notes Atom feed source.
- Creates a source record under `~/.knowledge/<key>/google_releases/`.

### `know add tv <CHANNEL_NAME> --key <KEY>`
- Registers a Television channel definition with source-command and optional preview-command, action-command.
- Creates a source record under `~/.knowledge/<key>/television/`.
- During sync, generates TOML cable file, commands.json, and README.md.

## Search Behavior

### `know search confluence "text search"`
Supports live search against configured Confluence credentials.
Expected output shape:
- the original query string;
- the matching source registrations;
- the key associated with each source;
- the Confluence space associated with each source.

Recommended filters:
- `--cql` CQL override;
- `--space` space key;
- `--type` content type;
- `--label` labels (repeatable);
- `--title-contains` title text filter;
- `--text-contains` body text filter;
- `--created-after`, `--created-before` created date filters;
- `--updated-after`, `--updated-before` updated date filters;
- `--limit` maximum results;
- `--cursor` pagination cursor.

### `know search jira "text search"`
Executes live search against Jira REST API v3 when credentials are configured.
Filters:
- `--project` project key;
- `--jql` explicit JQL override;
- `--status` status (repeatable);
- `--issue-type` issue type (repeatable);
- `--assignee` assignee;
- `--reporter` reporter;
- `--created-after`, `--created-before` created date filters;
- `--updated-after`, `--updated-before` updated date filters;
- `--order-by` ORDER BY fragment (repeatable);
- `--field` fields to request (repeatable);
- `--property` entity properties (repeatable);
- `--expand` expand values (repeatable);
- `--fields-by-keys` interpret fields by keys;
- `--limit` maximum results;
- `--next-page-token` pagination token.

### `know search arxiv "query"`
Searches the arXiv public API.
Filters:
- `--start` result offset;
- `--max-results` maximum results;
- `--sort-by` sort field (`relevance`, `lastUpdatedDate`, `submittedDate`);
- `--sort-order` sort direction (`ascending`, `descending`).

`know search <SOURCE> --help` shows all available filters for that source.

## Credential Management

```bash
know set credential <NAME> <VALUE>
know list credentials
```

Credentials are stored in `~/.knowledge/keys.yaml`. Sources reference them using `$name` syntax. Environment variables can also be referenced using `$env:ENV_VAR_NAME` syntax. The `.env` file in the working directory is loaded automatically at CLI startup.

## Source Adapters

### Confluence (`confluence.py`)
- Syncs pages from a Confluence space using the search API.
- Stores one Markdown file per page with YAML frontmatter (title, source_url, space, type).
- Search uses CQL with extensive filter support.

### Jira (`jira.py`)
- Syncs issues from a Jira project using REST API v3.
- Stores one Markdown file per issue with YAML frontmatter.
- Search uses JQL with full filter parameter support.

### arXiv (`arxiv.py`)
- Syncs paper metadata and content from arXiv URLs.
- Stores Markdown files under the source directory.
- Search uses the arXiv API with query expression support.

### GitHub Repository (`github_repo.py`)
- Clones or fetches repository content for specified branches.
- Stores raw repository files under the source directory.

### GitHub API (`github_api.py`)
- Provides `list_user_repos` for browsing repos the user has interacted with.
- Provides `list_repo_activity` for browsing issues, PRs, and discussions.
- Provides `render_issue_thread_markdown` for full thread rendering.

### Video (`video.py`)
- Obtains transcription from video sources (YouTube or local).
- Stores raw transcription separately from exported Markdown.
- Supports language preference via `--language`.

### Website / crawl4ai (`crawl4ai_site.py`)
- Crawls websites to specified depth and page limits.
- Strips HTML to text and stores as Markdown with frontmatter.

### Google Releases (`google_releases.py`)
- Fetches Google Cloud release notes Atom feeds.
- Stores the raw XML plus one normalized Markdown per entry under `entries/`.

### Aha (`aha.py`)
- Syncs features from an Aha workspace.
- Reads `AHA_BASE_URL` and `AHA_TOKEN` from `.env`; stores tokens as `$env:` references.

### Television (`sources/television.py`)
- Generates a Television cable TOML file, command manifest, and README during sync.
- Cable files can be installed into `~/.config/television/cable/` for `tv` discovery.

## Television Integration

Television (`tv`) is a terminal fuzzy-finder. The `know` CLI integrates with it in two ways:

### 1. Output formats

Every `list`, `search`, and `browse` command supports three output formats:

| Format | Flag | Purpose |
|---|---|---|
| JSON | `--format json` (default) | Structured data for scripts |
| Television rows | `--format television` | One line per result for `tv` source command |
| Television preview | `--format television-preview --entry '{}'` | Markdown detail pane for `tv` preview command |

### 2. Television source adapter

`know add tv` registers a persistent channel definition that generates a TOML cable file during sync.

### Pre-built cables

Ready-to-use Television cable definitions live in `cables/` at the repository root:

| Cable file | Channel | Description |
|---|---|---|
| `know.toml` | `know` | Hub: list all know channels |
| `know-keys.toml` | `know-keys` | Browse knowledge keys |
| `know-sources.toml` | `know-sources` | Browse all registered sources |
| `know-credentials.toml` | `know-credentials` | Browse stored credentials |
| `know-confluence.toml` | `know-confluence` | Search Confluence pages |
| `know-confluence-sync.toml` | `know-confluence-sync` | Browse Confluence with sync status |
| `know-jira.toml` | `know-jira` | Search Jira issues |
| `know-jira-sync.toml` | `know-jira-sync` | Browse Jira with sync status |
| `know-arxiv.toml` | `know-arxiv` | Search arXiv papers |
| `know-arxiv-sync.toml` | `know-arxiv-sync` | Browse arXiv with sync status |
| `know-aha-sync.toml` | `know-aha-sync` | Browse Aha with sync status |
| `know-releases-sync.toml` | `know-releases-sync` | Browse releases with sync status |
| `know-github-view.toml` | `know-github-view` | Browse GitHub repos / activity |
| `know-videos-browse.toml` | `know-videos-browse` | Browse video sources |
| `know-sites-browse.toml` | `know-sites-browse` | Browse crawled sites |
| `know-local.toml` | `know-local` | Browse all local knowledge files |
| `know-by-key.toml` | `know-by-key` | Keys overview → drill into sources |
| `know-by-type.toml` | `know-by-type` | Source types overview → drill into type |
| `know-papers.toml` | `know-papers` | All arXiv papers across keys |
| `know-repos.toml` | `know-repos` | All GitHub repos across keys |
| `know-files.toml` | `know-files` | Full-text searchable file browser |
| `know-recent.toml` | `know-recent` | Recently synced sources |
| `know-stale.toml` | `know-stale` | Sources not synced recently |
| `know-unsynced.toml` | `know-unsynced` | Sources never synced |
| `know-timeline.toml` | `know-timeline` | Chronological source timeline |
| `know-commands.toml` | `know-commands` | All sync/delete/export commands |
| `know-stats.toml` | `know-stats` | Knowledge base statistics |
| `know-crossref.toml` | `know-crossref` | Sources shared across keys |
| `know-cspaces.toml` | `know-cspaces` | Confluence spaces → drill into pages |
| `know-jprojects.toml` | `know-jprojects` | Jira projects → drill into issues |
| `know-grepos.toml` | `know-grepos` | GitHub repos → drill into activity |

Install cables:

```bash
# Unix / macOS
mkdir -p ~/.config/television/cable && cp cables/*.toml ~/.config/television/cable/

# PowerShell (Windows)
New-Item -ItemType Directory -Force -Path $HOME/.config/television/cable | Out-Null
Copy-Item cables/*.toml $HOME/.config/television/cable/
```

### Inline usage without cables

```bash
tv --source-command='know list keys --format television' \
   --preview-command='know list keys --format television-preview --entry "{}"'

tv --source-command='know browse by-key --format television' \
   --preview-command='know browse by-key --format television-preview --entry "{}"'

tv --source-command='know search jira "" --project KAN --format television' \
   --preview-command='know search jira "" --project KAN --format television-preview --entry "{}"'
```

## Export Format

`know export [--key KEY]` generates a zip archive of one or more keys containing:
- All synchronized Markdown files with YAML frontmatter preserving source traceability.
- For video sources, the exported Markdown is generated from the transcription.
- Raw transcription data is kept separate from exported Markdown.
- The archive is written to `~/.knowledge/exports/`.

## Import

`know import <ARCHIVE.zip>` merges the zipped structure with the current store:
- Merges metadata, combining source lists.
- Adds source files to the local folder.
- Preserves existing data that doesn't conflict.

## Skill

A `SKILL.md` file in `skills/know/` provides usage instructions for the CLI, including Television integration patterns and credential management.

## Documentation

Human documentation lives inside `docs/`:

| File | Content |
|---|---|
| `docs/cli.md` | Full CLI reference with examples |
| `docs/television.md` | Television integration guide |
| `docs/know-skill.md` | Skill reference for agent use |

## Error Handling

The `errors.py` module defines custom exception types:

| Error | Use |
|---|---|
| `KnowledgeError` | Base error for all user-facing failures |
| `CredentialNotFoundError` | Raised when a `$credential_ref` cannot be resolved |
| `SourceNotFoundError` | Raised when a source ID does not exist in a key |
| `InvalidURLError` | Raised when URL validation fails on `add arxiv`, `add site`, `add google-releases` |

## Architecture

### Module layout

```text
src/knowledge/
  __init__.py
  cli.py                  # Argument parser, entry point, URL validation, dotenv loader
  commands.py             # Handlers for add, list, search, sync, del, set, export, import
  store.py                # KnowledgeStore: key/source/credential CRUD, metadata persistence
  exporter.py             # Markdown export and zip archive generation
  registry.py             # Source adapter registry
  errors.py               # Custom exception types
  television.py           # Television output formatters for list/search commands
  browse_commands.py      # Per-source-type browse handlers (jira, confluence, github, etc.)
  browse_extended.py      # Cross-key aggregate browse handlers (by-key, stats, timeline, etc.)
  browse_tv.py            # Television formatters for browse commands
  sources/
    __init__.py
    base.py               # Base source adapter class
    confluence.py          # Confluence space adapter and search
    jira.py               # Jira project adapter and search
    arxiv.py              # arXiv paper adapter and search
    github_repo.py        # GitHub repository clone/fetch adapter
    github_api.py         # GitHub REST API client (repos, activity, threads)
    video.py              # Video transcription adapter
    crawl4ai_site.py      # Website crawl adapter
    google_releases.py    # Google Cloud release notes Atom feed adapter
    aha.py                # Aha workspace adapter
    television.py         # Television cable file generator
```

### Key design patterns

- **KnowledgeStore** is the central data layer; all commands receive it from parsed CLI args.
- **Source adapters** implement sync logic per source type; they are dispatched via the registry.
- **Television formatters** are kept in dedicated modules (`television.py`, `browse_tv.py`) separate from command logic.
- **Browse commands** merge local file state with optional remote API data to show sync-status indicators.
- **Credential resolution** uses `$name` references into `keys.yaml` and `$env:VAR` for environment variables.
- The `.env` file in the working directory is loaded automatically at startup.
- The sync attribute map (`_SYNC_ATTR_MAP`) replaces the long `if/elif` chain for resolving `match_value` from CLI args.

## Architectural Decisions

The following decisions were adopted after a project-wide review on 2026-03-25.

### D-01  Cross-platform temp directory
`TEMP_ROOT` in `store.py` must use `tempfile.gettempdir()` instead of a
hard-coded `/tmp` path so the tool works correctly on Windows, macOS, and
Linux.

### D-02  Fix broken regex in crawl4ai HTML stripper
`_html_to_text()` in `crawl4ai_site.py` uses `</\\1>` which never matches.
The correct back-reference is `</\1>`.

### D-03  Fix unclosed code fence in docs/cli.md
The Markdown file has a missing closing fence that breaks renderers.

### D-04  Create SKILL.md for `skills/know/`
SPEC requires a `SKILL.md` with usage instructions for the CLI; it must be
created and kept up to date.

### D-05  Simplify sync match_value resolution
Replace the long `if/elif` chain in `cli.py` `main()` with a dictionary
mapping `sync_command → attribute name`.

### D-06  Add URL validation on source registration
`add arxiv`, `add site`, and `add google-releases` must reject clearly invalid URLs
before persisting them.

### D-07  Custom error types for user-facing failures
Introduce `KnowledgeError`, `CredentialNotFoundError`,
`SourceNotFoundError`, and `InvalidURLError` in a dedicated `errors.py` module so
that the CLI can present friendly messages.

### D-08  Add docstrings to every public class and function
All source adapters, `KnowledgeStore`, the exporter, and the registry must
carry docstrings that explain purpose and parameters.

### D-09  Improve test coverage to 90 %+
- Raise the coverage gate threshold to 90 %.
- Add unit tests for uncovered paths in `crawl4ai_site`, `exporter`, and
  `base`.
- Add tests for new error types and URL validation.

### D-10  Verbose / quiet CLI flags
Add `--verbose` and `--quiet` flags to `know` for optional progress output
during sync and export operations.

### D-11  Browse command family
Add `know browse` subcommands that merge local file state with optional remote
API data to show sync-status indicators for all source types. Provide both
per-source-type browsers (jira, confluence, github, etc.) and cross-key
aggregate browsers (by-key, by-type, timeline, stats, etc.).

### D-12  Extended browse with drill-down chains
Support drill-down navigation from key → sources → files through the
`key-sources` and `source-files` fork-target browsers, wired into Television
cable files with `enter` keybindings.

### D-13  Pre-built Television cables
Ship ready-to-use `.toml` cable definitions in `cables/` for every browse and
search command, including a hub channel (`know.toml`) that lists all available
channels.
