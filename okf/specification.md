---
type: Project Specification
title: knowledge specification
description: Requirements and architecture for knowledge.
tags:
- requirements
- okf
source_path: SPEC.md
---

# SPEC

## Objective

Build a Python CLI called `know` to manage a local knowledge base in `~/.knowledge`, capable of:

- creating named knowledge keys as independent local collections;
- attaching external sources to a key through declarative metadata;
- synchronizing content from multiple systems into a raw local store;
- round-tripping published Confluence Cloud pages without flattening macros, Smart Links, statuses, images, attachments, labels, or dynamic extension data;
- processing video sources by extracting or generating transcriptions;
- exporting normalized Markdown documents with YAML frontmatter;
- exporting Open Knowledge Format (OKF) v0.1-compatible Markdown concept documents;
- publishing a strict, generated OKF v0.1 subdirectory for the project and every repository skill;
- selecting a reviewed Semantic OKF source-combination topology that either preserves source boundaries or treats compatible physical partitions as one logical source;
- refreshing generated Semantic OKF snapshots by fully reprocessing their declared sources;
- consulting Semantic OKF knowledge efficiently through ledger, Markdown, and local SPARQL workflows;
- optionally deriving hash-bound embedding retrieval projections without changing authoritative OKF records or RDF identities;
- consulting embedding-enabled snapshots through explicit lexical, vector, and hybrid discovery followed by authoritative concept verification;
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
- Every exported Markdown concept document must include a non-empty OKF `type` field.
- Exported Markdown should populate OKF `title`, `description`, `resource`, `tags`, and `timestamp` when those values can be derived from source metadata without guessing.
- Integrations must support repeatable re-sync without manual intervention.
- Optional dependencies must not block use of the base CLI.
- Advanced Television skill bundles must remain usable without this checkout, generate separate macOS and Windows artifacts, and never install optional preview tools or replace user configuration implicitly.
- The default user-facing command is `know`.
- Command naming should remain short and task-oriented: `add`, `list`, `search`, `sync`, `export`, `browse`.
- Video sources must be normalized through transcription before export so they can be consumed like the rest of the text-oriented library.
- Cross-platform compatibility: use `tempfile.gettempdir()` instead of hard-coded paths.
- Native `SKILL.md` frontmatter must remain limited to `name` and `description`; OKF skill interoperability is provided by a generated projection rather than nested compatibility metadata.
- Every repository skill must be a standalone package by default: keep required instructions, references, scripts, assets, and dependency declarations inside its own directory, while treating explicitly declared tools, services, credentials, browsers, and user-supplied data as public inputs rather than hidden package dependencies.
- Semantic OKF refreshes must rebuild complete snapshots, validate before promotion, report additions/changes/removals, and never merge generated trees in place.
- Semantic OKF query workflows must select the cheapest authoritative layer and keep domain data, ontology, provenance, and validation graphs distinct unless a query explicitly requires their union.
- Semantic OKF multi-input plans must distinguish source-scoped separation, homogeneous partition union, and upstream entity fusion; they must never silently deduplicate, select winners, or imply access isolation that the generated default data graph does not provide.
- Semantic OKF CSV ingestion must match exact physical header names independently of JSON schema member order, apply deterministic strict Python scalar parsing, and reject ambiguous or lossy input.
- Semantic OKF adapters must reprocess every declared source, detect both content changes and glob-membership changes, and remain deterministic without an external data-processing engine.
- Semantic OKF embedding chunks and vectors are non-authoritative discovery projections: they must bind to exact records, concepts, source locators, input hashes, provider, model revision, dimensions, and chunking configuration.
- Embedding workflows must keep a network-free deterministic baseline, require explicit allowlisted providers and implementations, and never select, download, or cache a model implicitly.
- GitHub repository synchronization must retain Markdown-compatible MDX files as text inputs so documentation repositories can be acquired at an exact commit without a rendered-site dependency.
- Derived Semantic OKF retrieval packages must preserve their accepted version-1 contracts while offering a version-2 source-generic contract that never infers paper, arXiv, PDF, filename-prefix, or title identities.

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
know list credentials
know list sources [--key KEY] [--type TYPE] [--format json|television|television-preview] [--entry ROW]
```

### `know search` — Live search against remote APIs

```bash
know search confluence "text" [filters...] [--format json|television|television-preview] [--entry ROW]
know search jira "text" [filters...] [--format json|television|television-preview] [--entry ROW]
know search arxiv "query" [--max-results N] [--sort-by FIELD] [--sort-order DIR] [--format json|television|television-preview] [--entry ROW]
know search brave "text" [--count N] [--format json|television|television-preview] [--entry ROW]
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

Generates a zip of one or more keys containing normalized Markdown with OKF-compatible YAML frontmatter. For video sources, the exported Markdown is generated from the transcription and follows the same frontmatter and traceability rules as every other exported document. If timestamps, speaker segments, chapters, or source transcript metadata are available, they are preserved in raw data and reflected in Markdown when useful.

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

### `know search brave "text"`
Executes a web search through the Brave Search API.
Filters:
- `--count` maximum results to request from Brave.
Authentication:
- `X-Subscription-Token` from `BRAVE_SEARCH_API_KEY` or stored credential `brave_search_api_key`.

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
- Manifest install commands honor `TELEVISION_CONFIG` and `XDG_CONFIG_HOME`, then use the platform default Television configuration directory.

## Television Integration

Television (`tv`) is a terminal fuzzy-finder. The `know` CLI integrates with it in two ways:

### 1. Output formats

`know list keys`, `know list sources`, every `search`, and every `browse` command support three output formats:

| Format | Flag | Purpose |
|---|---|---|
| JSON | `--format json` (default) | Structured data for scripts |
| Television rows | `--format television` | One line per result for `tv` source command |
| Television preview | `--format television-preview --entry '{}'` | Markdown detail pane for `tv` preview command |

### 2. Television source adapter

`know add tv` registers a persistent channel definition that generates a TOML cable file during sync.

### 3. Standalone Television skill bundles

The standalone `skills/television/` package provides deterministic advanced generation when a request exceeds the simple source adapter.

- Input is a declarative JSON bundle specification.
- Output may include `config.toml`, cable TOML files, a manifest, a dependency inventory, and installers for macOS and Windows.
- Channel bundles support the complete source, preview, UI, history, keybinding, action, and template surface exposed by current Television channel types.
- Associated Enter-driven navigation is a linear graph of one to three channels. Every transition must propagate a stable selected value; the third level cannot launch a fourth channel.
- Preview recipes cover text, code, Markdown, JSON, YAML, CSV, TSV, directories, images, PDFs, media, and archives. CSV and TSV parsing must be table-aware rather than delimiter splitting.
- Every invoked binary is declared in channel requirements. Optional preview-tool installation is explicit and user-authorized.

### Pre-built cables

Ready-to-use Television cable definitions live in `cables/` at the repository root:

| Cable file | Channel | Description |
|---|---|---|
| `know.toml` | `know` | Hub: list all know channels |
| `know-keys.toml` | `know-keys` | Browse knowledge keys |
| `know-sources.toml` | `know-sources` | Browse all registered sources |
| `know-confluence.toml` | `know-confluence` | Search Confluence pages |
| `know-confluence-sync.toml` | `know-confluence-sync` | Browse Confluence with sync status |
| `know-jira.toml` | `know-jira` | Search Jira issues |
| `know-jira-sync.toml` | `know-jira-sync` | Browse Jira with sync status |
| `know-arxiv.toml` | `know-arxiv` | Search arXiv papers |
| `know-brave.toml` | `know-brave` | Search the web with Brave Search API |
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
| `know-follow.toml` | `know-follow` | Follow-up items from GitHub activity, starred repos, and Jira |
| `know-cspaces.toml` | `know-cspaces` | Confluence spaces → drill into pages |
| `know-jprojects.toml` | `know-jprojects` | Jira projects → drill into issues |
| `know-grepos.toml` | `know-grepos` | GitHub repos → drill into activity |

Install cables:

```bash
# Unix / macOS
mkdir -p ~/.config/television/cable && cp cables/*.toml ~/.config/television/cable/

# PowerShell (Windows default; honor TELEVISION_CONFIG first when set)
$ConfigDir = if ($env:TELEVISION_CONFIG) { $env:TELEVISION_CONFIG } else { Join-Path $env:LOCALAPPDATA 'television\config' }
$CableDir = Join-Path $ConfigDir 'cable'
New-Item -ItemType Directory -Force -Path $CableDir | Out-Null
Copy-Item cables/*.toml $CableDir/
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
- All synchronized Markdown files with OKF-compatible YAML frontmatter preserving source traceability.
- A non-empty OKF `type` field on every non-reserved Markdown concept document.
- For video sources, the exported Markdown is generated from the transcription.
- Raw transcription data is kept separate from exported Markdown.
- The archive is written to `~/.knowledge/exports/`.

## Import

`know import <ARCHIVE.zip>` merges the zipped structure with the current store:
- Merges metadata, combining source lists.
- Adds source files to the local folder.
- Preserves existing data that doesn't conflict.

## Skill

Every direct `skills/<name>/` package must remain usable after its directory is copied outside this repository. A skill may require the external executable or service named by its public purpose, but it must not require sibling skills, root documentation, repository source modules, fixtures, evaluation artifacts, or repository-relative runtime helpers. Bundled Python scripts must declare third-party packages within the same skill directory. Optional performance tools and model-assisted workflows must not replace the package's supported baseline. Portability tests must verify local links, dependency declarations, and copied-package entry points.

Skill evolution must use isolated Skill Arena comparisons by default: one no-skill control versus one treatment containing exactly one copied canonical skill, with identical prompts and fixtures. The all-skills portfolio comparison is a routing smoke and must not be used as causal evidence for an individual skill. Broad-skill iteration suites must include naturalistic, generalization, and boundary or recovery cases while keeping evaluator knowledge outside task prompts.

A `SKILL.md` file in `skills/know/` provides usage instructions for the CLI, including Television integration patterns and credential management.

The repository also ships `skills/open-knowledge-format/`, which documents the reviewed Google Cloud OKF v0.1 contract and provides deterministic bundle generation and validation scripts.

The repository ships `skills/roundtrip-confluence-pages/` as an independent write-capable Confluence page skill. It must use storage XML as the editable body contract, retain ADF and rendered HTML as verification evidence, preserve attachment bytes, media types, and page metadata, reject concurrent page and attachment version conflicts by default, and require both a verified API report and a verified authenticated-browser ground-truth record before reporting a successful upload. It must not mutate page parent/space, restrictions, permissions, comments, watchers, likes, analytics, owners, classifications, or content properties.

The repository also ships `skills/md2conf/` as a standalone Markdown-authoritative Confluence publishing skill. It must target the active `markdown-to-confluence` distribution, verify the installed CLI version and options, stage conversion with offline local output, expose whole-page replacement and source-update choices explicitly, and require review of attachment deletion, label/property replacement, mailto-driven user mentions and their notification effects, hierarchy changes, and partial-failure recovery before a live publish. It must not claim lossless preservation of native Confluence content or use a Markdown publication workflow when the existing page remains authoritative.

The repository must expose Semantic OKF lifecycle and consultation as two standalone skills with mutually exclusive responsibilities and no dependency on files, scripts, instructions, or sibling skills outside their own directories. Third-party Python packages are permitted only when declared by the skill's bundled requirements files.

The write-capable `skills/build-semantic-okf/` skill must:

- exclusively own construction and maintenance of the reviewed source definition and generated knowledge folder;
- choose and record whether multiple inputs remain separate, form one homogeneous partition union, or require upstream canonicalization;
- create a new coherent bundle from a reviewed manifest;
- add, change, or remove declared sources and their reviewed mappings without silently changing domain meaning;
- refresh an existing bundle by reprocessing all original sources into a validated replacement snapshot; and
- validate semantic, provenance, SHACL, and OKF coherence before publication or promotion using only validators bundled in the skill;
- exclude searching, answering, comparing, citing, and synthesis instructions or commands.

The read-only `skills/consult-semantic-okf/` skill must:

- exclusively provide general context and read-only local helpers for navigating an already generated knowledge folder efficiently;
- consume an existing validated snapshot without modifying its manifest, sources, generated concepts, semantic graphs, or reports;
- choose the cheapest authoritative consultation layer: `records.jsonl` for exact metadata, concept Markdown for lexical discovery and reading, and explicitly selected RDF graphs for joins, aggregation, schema, lineage, or validation questions;
- answer and synthesize knowledge across one or more sources with verified citations, page locators, and exact artifact paths; and
- keep domain data, ontology, provenance, shapes, and validation results distinct unless the question explicitly requires a reviewed union;
- exclude source acquisition, manifest authoring, materialization, validation repair, refresh, promotion, rollback, and recovery instructions or commands.

Each skill must remain installable and executable when its directory is copied outside this repository. Neither skill may name the other skill as a prerequisite or handoff target. Invalid or missing inputs must produce an in-scope diagnostic instead of routing through an external skill.

The source-generic entity-graph and definitive-ensemble skill pairs must:

- use the authoritative `(source_id, record_id)` ledger identity, plus the authoritative record hash, as the only default document identity;
- support arbitrary selected sources, multiple records per source, claimless corpora, Markdown headings, and deterministic bounded record-body passages;
- bind every returned passage to an exact `semantic/records.jsonl` body range and text hash that independent validation can rederive;
- treat graph nodes, mentions, co-mentions, lexical statistics, embeddings, crosswalks, and rankings as derived and non-authoritative;
- publish closed, hash-bound schemas atomically and validate child-plan parity, authoritative-core parity, complete identity coverage, component group parity, locator validity, and deterministic rebuilds;
- allow explicit identity overrides only through a closed reviewed crosswalk, never through filename or title heuristics; and
- reject claim-only coverage when the authoritative corpus supplies no exact reviewed answer bindings, while retaining read-only passage retrieval and permitting deterministic source-generic finalization only from full-query support IDs bound to exact supporting substrings and independently reconstructed authoritative identity fields.

Requests that create, expand, reprocess, repair, or otherwise mutate a Semantic OKF snapshot must route to `build-semantic-okf`. Requests that search, query, compare, explain, or cite knowledge from an existing snapshot must route to `consult-semantic-okf`. Ontology learning and evidence-led semantic model authoring remain a separate pre-build responsibility of `extract-ontologies`.

Separate declarations scope non-RDF identity and provenance but share one accepted data graph and one release lifecycle. One glob-backed declaration is a homogeneous append-only partition union and requires unique record IDs across all members. True entity fusion, conflict resolution, and multi-origin lineage require an upstream canonicalization contract. Refresh remains a full rebuild rather than an incremental file merge so deleted source records cannot leave stale concepts or triples. Consultation must retain source identity and prefer `records.jsonl` for metadata lookups, Markdown for human/full-text reading, and selected RDF graphs for joins, aggregation, or lineage.

### Semantic OKF embedding retrieval

The repository also ships `skills/build-semantic-okf-embeddings/` and `skills/consult-semantic-okf-embeddings/` as a second standalone pair for explicitly requested embedding, vector, hybrid, or LlamaIndex workflows. They do not replace or depend on the deterministic Semantic OKF skill pair.

The write-capable embedding builder must:

- materialize and validate the same authoritative Semantic OKF core before creating a retrieval projection;
- keep retrieval chunks out of the OKF record ledger and RDF graphs unless their semantic identity is separately declared and reviewed;
- write canonical, hash-bound retrieval artifacts under `retrieval/`, including chunks, embeddings, a closed index manifest, and a build report;
- provide a deterministic local hashing and native-splitting baseline;
- permit Sentence Transformers and LlamaIndex only as explicit, allowlisted, package-declared optional backends; a Sentence Transformers repository ID and immutable revision must resolve to that exact preloaded Hugging Face snapshot before only its local path is passed to the CPU model loader, with no implicit network, hosted provider, remote code, or cache writes; and
- validate input coverage, record/chunk/vector bindings, ordering, counts, dimensions, finite normalized values, paths, artifact hashes, and deterministic rebuild behavior before publication.

The read-only embedding consultant must:

- inspect and validate the retrieval projection before using it;
- provide deterministic lexical, exact-cosine vector, and reciprocal-rank-fusion hybrid discovery with filters applied before ranking and stable tie-breaking;
- identify requested and effective modes, any explicit fallback, snapshot and index digests, and exact concept paths and locators in machine-readable output;
- treat retrieval scores as discovery-only and require opening authoritative concept Markdown before citing a hit;
- fail closed for a corrupt or stale declared index, and never download a model, create cache state, or mutate the snapshot; and
- retain ledger, Markdown, and selected RDF graphs as the authoritative layers for exact facts, reading, joins, aggregation, schema, provenance, and validation questions.

Requests that explicitly require embedding-based separation, LlamaIndex processing, vector retrieval, or hybrid retrieval must route to this pair. Other Semantic OKF lifecycle and consultation requests continue to route to the deterministic pair.

The repository must keep a separate reproducible comparison under `evaluations/semantic-okf-embeddings/`. It must pin the fifteen GraphRAG Markdown files and fifteen corresponding claim JSONL files by path and SHA-256, retain the shared vocabulary as a separately identified required auxiliary input, preserve the historical snapshot, use append-only run directories for new large artifacts, and compare legacy lexical, new lexical, vector, and hybrid retrieval on identical questions. Reports must include source coverage, core semantic parity, artifact size and timing, Recall at fixed cutoffs, MRR, nDCG, and evidence validity against the authoritative ledger, identity fields, text digest, safe concept path, and exact record or character-range locator.

### Semantic OKF Graphify retrieval

The repository also ships `skills/build-semantic-okf-graphify/` and `skills/consult-semantic-okf-graphify/` as a standalone pair for deterministic Markdown-graph discovery. The pair must preserve a byte-identical authoritative Semantic OKF core and publish Graphify only as a derived retrieval projection.

- The builder must pin `graphifyy==0.9.17`, use structural Markdown extraction without semantic LLM extraction or clustering, expose reviewed record values through deterministic temporary headings, neutralize Markdown structural punctuation in scalar text, expose reviewed object-IRI relationships through builder-generated local links, and verify deletion of every temporary view and cache before publication.
- `retrieval/graphify/index.json` must bind the native node-link graph to the complete core tree, record ledger, per-record and derived paper identity, record digest, deterministic view-input digest, node and edge counts, and graph physical and logical digests.
- Validation must regenerate every view digest from the authoritative ledger and reject runtime drift, changed core bytes, derived identity drift, missing record coverage, malformed closed schemas, unsafe or missing source paths, duplicate nodes, dangling edges, orphan nodes, invalid counts, and graph or index tampering with a classified diagnostic.
- The consultant must validate the complete binding, run pinned Graphify scoring and bounded BFS in memory, return deterministic structured traversal output with exact concept-file evidence locators, hydrate every selected `concept_path`, and leave every published byte unchanged.
- Exact identity and grouped counts remain ledger operations. Graphify labels, scores, and edges are discovery evidence rather than authoritative domain facts, and fallback to another route must be explicit.
- The storage-version comparison must reuse the frozen 31-source, 874-record GraphRAG corpus, its existing 30 retrieval questions, and a digest-frozen historical baseline so core parity, determinism, size, build time, exact lookup, aggregation, structural discovery quality, and evidence validity are directly comparable. Graphify hit validity must prove complete ledger identity, a recomputed record digest, ledger-derived paper identity, a safe exact concept locator, byte-identical content, and the exact authoritative record body.

### Semantic OKF consultation benchmark

The repository must keep an isolated Skill Arena benchmark under `evaluations/semantic-okf-reader/` that evaluates grounded semantic correctness across the consultation layers of a pinned Semantic OKF snapshot.

- The canonical battery contains exactly 300 semantically distinct questions with stable IDs, hidden normalized answers, reviewed alternative minimal evidence sets, wording-independent query descriptors and signatures, category labels, and difficulty labels. Answer hashing must normalize equivalent offset-bearing ISO date-times to UTC milliseconds.
- The control profile receives neither Semantic OKF knowledge nor a consultation skill. The treatment profile receives both the pinned knowledge snapshot and an independently pinned `consult-semantic-okf` snapshot through one profile-only workspace overlay; it must not receive the write-capable builder skill.
- Both profiles use the same PI route, prompt, sandbox, network policy, and deterministic answer assertions. Every active run must call `openai-codex/gpt-5.6-luna` directly; no GPT-5.3 route or cross-model fallback is permitted. Every question is an independent model request and must not depend on workspace mutations or session state from another question.
- Semantic accuracy, evidence grounding, evidence-path validity, and response-contract compliance are separate named metrics. Grounding requires a reviewed sufficient subset and permits additional existing snapshot artifacts. A control abstention is contract-compliant but does not count as a correct semantic answer.
- The battery covers typed facts, relation traversal, multi-hop joins, typed filtering, aggregation, provenance, ontology and SHACL contracts, integrity and missingness, and bundle inventory.
- The initial full evaluation expands to 600 Skill Arena cells. A five-question smoke manifest must remain available for a ten-cell live rehearsal. Same-model technical retries are additional Luna calls and must be reported separately.
- Generation must be deterministic and expose a check-only mode. Tests must reject duplicate IDs, duplicate question text, duplicate semantic signatures, missing evidence, stale derived files, knowledge or evaluated-skill snapshot drift, or knowledge leakage into the control profile.
- Live PI execution is intentionally separate from generation and validation because it consumes model quota. A dry-run is required before any live compare.
- The runtime wrapper must invoke GPT-5.6 Luna exactly once per cell, preserve diagnostic stderr, identify the model that answered, and never select a different model after runtime or assertion failure. Each attempt must have a 90-second hard timeout that terminates its complete process tree and normalizes a timeout to exit 124. PI 0.80.6 or newer is required for GPT-5.6 Luna.
- A host-side technical resume builder must classify completeness only from nonblank `response.output` and absent `response.error`. Its merger must bind every result file to its exact source manifest, join cells by prompt and profile IDs, restore canonical identity and indices, recompute Promptfoo aggregates, persist source hashes and attempt chains, and reject duplicate or unresolved cells. A host credential reference may expose only the explicitly named same-name environment variable and must never serialize its value.
- An optional host-side semantic retry builder may read a technically complete composite and the exact manifest used for that run, verify every treatment prompt identity and text, select only unsuccessful `skill` cells, persist their IDs, and emit a GPT-5.6 Luna-only retry manifest. It must never retry control cells or passing treatment cells. Composite reporting substitutes every bound retry result for its selected prompt, including failed retries, to prevent best-of-attempt cherry-picking, and reports technical and semantic retries separately. Completed mixed-model manifests remain historical artifacts and must not be used as active configurations.
- Windows prompt transport must preserve UTF-8 through the Skill Arena PowerShell boundary for both prompt input and model stdout.
- Query-layer labels demonstrate coverage only. Runtime efficiency, latency, tokens, and tool calls are outside this benchmark until tracing and explicit efficiency assertions are added.

This two-arm design estimates the value of the complete consultation-skill-and-knowledge access path. A future causal study that needs to isolate procedural skill value must add a third profile with the same knowledge snapshot but no consultation skill.

### Source-generic Astro documentation benchmark

The repository must keep a reproducible source-generic comparison under `evaluations/semantic-okf-astro/`.

- Acquisition must use the `know` CLI against the official `withastro/docs` GitHub repository at a recorded immutable commit and freeze the complete English technical-documentation set selected from `src/content/docs/en/**/*.mdx`.
- The corpus manifest, input inventory, acquisition metadata, plans, compact reports, and checked-in documentation must bind file counts, paths, byte sizes, and SHA-256 hashes. Large run bundles remain append-only and ignored.
- One shared battery contains 40 stable questions: 30 normal questions plus 10 evidence-first hard questions requiring multi-document synthesis, exclusions, conditional reasoning, or mechanism comparison.
- Every hard ground truth records atomic answer claims, required source-record identities, exact authoritative evidence paths and body locators or text hashes, derivation or join logic, acceptable variants, and important negatives. A validator must independently rederive every locator and hash before evaluation.
- Direct retrieval evaluation must exercise every compatible route in the legacy, embedding, classical, adaptive, entity-graph, and definitive-ensemble families with the same questions, candidate pool, identity grouping, cutoffs, and independent evidence-validity checks. Retrieval quality, grounded answer quality, response-contract compliance, build validity, deterministic rebuilds, latency, and authoritative-core parity remain separate metrics.
- At least one hard question must retain the actual grounded answer returned by every compatible consultation alternative so qualitative differences can be inspected beside the numeric results.
- Any Skill Arena comparison used as causal evidence must isolate one consultation treatment against a knowledge-identical control; an all-skills portfolio is descriptive only. Config generation, validation, dry-run, execution, and result aggregation follow the checked-in Skill Arena workflows and must not require MCP.

## Project OKF Bundle

The `okf/` directory is the strict OKF v0.1 interoperability boundary for this repository. It is a generated bundle and must contain:

- a root `index.md` that declares `okf_version: "0.1"`;
- `project.md`, projected from `README.md`;
- `specification.md`, projected from `SPEC.md`;
- `skills/index.md` for progressive disclosure;
- one `skills/<name>.md` concept for every `skills/*/SKILL.md` file.

Generate or refresh the bundle with:

```bash
python skills/open-knowledge-format/scripts/build_project_okf_bundle.py . --output okf
```

Check drift and conformance without writing files with:

```bash
python skills/open-knowledge-format/scripts/build_project_okf_bundle.py . --output okf --check
python skills/open-knowledge-format/scripts/validate_okf_bundle.py okf
```

Every native skill remains authoritative for agent execution. Its projected OKF concept preserves the instructions in the body and records `skill_name` and `source_path` as producer-defined traceability fields.

## Documentation

Human documentation lives inside `docs/`:

| File | Content |
|---|---|
| `docs/cli.md` | Full CLI reference with examples |
| `docs/TVs.md` | Television integration guide |
| `docs/COMMANDS.md` | Compact command reference |
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
  okf.py                  # Open Knowledge Format frontmatter normalization
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
- OKF compatibility is applied as an additive metadata layer: existing source provenance fields remain intact, while `type`, `resource`, `tags`, and `timestamp` are derived where possible.
- Project and skill compatibility is delivered as a strict generated bundle under `okf/`; the repository root itself is not treated as an OKF bundle.

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
