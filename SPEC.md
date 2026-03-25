# SPEC

## Objective

Build a Python CLI called `know` to manage a local knowledge base in `~/.knowledge`, capable of:

- creating named knowledge keys as independent local collections;
- attaching external sources to a key through declarative metadata;
- synchronizing content from multiple systems into a raw local store;
- processing video sources by extracting or generating transcriptions;
- exporting normalized Markdown documents with YAML frontmatter;
- preserving traceability back to the original source;
- supporting repeatable updates through explicit commands stored with each key.

## Expected Outcome

The tool should allow a user to create a key, attach sources such as Confluence spaces, arXiv papers, websites, videos, Jira projects, Aha workspaces, and GitHub repositories, then sync and export those sources into a navigable Markdown library ready for search, reading, and downstream tooling.

Television channel definitions may also be attached when a key needs reproducible terminal discovery workflows backed by explicit commands.

## Principles

- The local store in `~/.knowledge` is the operational source of truth.
- Every integration must be reproducible from declarative configuration.
- Source content should remain reproducible from the registered source configuration.
- Every exported document must include source metadata in YAML frontmatter.
- Integrations must support repeatable re-sync without manual intervention.
- Optional dependencies must not block use of the base CLI.
- The default user-facing command is `know`.
- Command naming should remain short and task-oriented: `add`, `list`, `search`, `sync`, `export`.
- Video sources must be normalized through transcription before export so they can be consumed like the rest of the text-oriented library.

## No functional requirments
- coverage should more than 90%
- be consistent with pattern and always try to maintain it simple and easy to understand 
## Requimenets

The preferred installation flow is `uv tool install` from GitHub.

Example:

```bash
uv tool install git+https://github.com/<owner>/<repo>.git
```

Optional extras may be installed when required by a source adapter.

Example:

```bash
uv tool install 'git+https://github.com/<owner>/<repo>.git'
```

## Primary CLI

The CLI binary is `know`.

The following commands must work:

```bash
know --help
know add key <KEY>
know list keys
know list sources --key <KEY>
know add confluence --space <SPACE> --key <KEY>
know search confluence "text search"
know add arxiv <URL> --key <KEY>
```

The command family should expand consistently for future sources.

Examples:

```bash
know add github-repo <REPO_URL> --key <KEY> --branch <BRANCH> --branch <BRANCH_2>
know add jira-project <PROJECT> --key <KEY>
know add video <VIDEO_URL_OR_PATH> --key <KEY>
know list sources --key <KEY>
know sync --key <KEY>
know export --key <KEY>
```

## Store Structure

```text
~/.knowledge/
  config.yaml
  keys.yaml                  # optional credential store for integrations
  <key>/
    metadata.yaml
    confluence/
    arxiv/
    video/
    github/
    jira/
    aha/
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
    updated_at: 2026-03-22T18:00:00+00:00
    update_command: know sync confluence --SPACE <SPACE> 
    delete_command: know del confluence <id>
  - type: arxiv
    id: <id>
    updated_at: 2026-03-22T18:05:00+00:00
    update_command: know sync arxiv <URL>
    delete_command: know del arxiv <id>
  - type: video
    id: <id>
    updated_at: 2026-03-22T18:10:00+00:00
    update_command: know sync video <VIDEO_URL_OR_PATH>
    delete_command: know del video <id>
```

## Source Registration Rules

### `know add key <KEY>`
- Creates `~/.knowledge/<key>/`.
- Creates/update `metadata.yaml`.
- Fails with a clear error if the key already exists.

### `know add confluence <SPACE> --key <KEY>`
- Registers a Confluence space under the selected key.
- Stores the source in key metadata.
- Creates a source record under `~/.knowledge/<key>/confluence/`.

### `know add arxiv <URL> --key <KEY>`
- Registers an arXiv source under the selected key.
- Stores the original URL in the source config.
- Creates a source record under `~/.knowledge/<key>/arxiv/`.

### `know add video <VIDEO_URL_OR_PATH> --key <KEY>`
- Registers a video source under the selected key.
- Stores the original local path or URL in the source config.
- Creates a source record under `~/.knowledge/<key>/video/`.
- During sync, the implementation must obtain a transcription for the video and store the raw transcription output separately from the exported Markdown.

## Search Behavior
### `know search confluence "text search"`
This command must support live search against configured Confluence credentials.
Expected output shape:
- the original query string;
- the matching source registrations;
- the key associated with each source;
- the Confluence space associated with each source.

Recommended filters include source API parameters such as:
- CQL override;
- space;
- content type;
- labels;
- title/body text filters;
- created and updated date filters;
- pagination cursor.

### `know search jira "text search"`
This command must execute live search against Jira REST API v3 when credentials are configured.
Expected filters include:
- project;
- explicit JQL override;
- status;
- issue type;
- assignee and reporter;
- created and updated date filters;
- field, property, expand, and pagination controls supported by the API.

know search <SOURCE> --help will show all the available filters for that source

## Export Format
This generate a zip one or more keys, that would be just defined sources or everything.

For video sources, the exported Markdown must be generated from the transcription and follow the same frontmatter and traceability rules as every other exported document. If timestamps, speaker segments, chapters, or source transcript metadata are available, they should be preserved in raw data and reflected in Markdown when useful.

## Import
Just update and merge zipped structure and current one, merging metadata and adding both sources to the local folder


## SKill
on skills/know should be create a SKILL.md with information how to use this cli

## Docs
Human documentation should be inside docs

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
`add arxiv`, `add site`, and `add video` must reject clearly invalid URLs
before persisting them.

### D-07  Custom error types for user-facing failures
Introduce `KnowledgeError`, `CredentialNotFoundError`, and
`SourceNotFoundError` in a dedicated `errors.py` module so that the CLI can
present friendly messages.

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
