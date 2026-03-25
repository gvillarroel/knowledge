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

## Quick Start

```bash
know add key research
know set credential jira_token secret-token
know add confluence --space ENG --key research
know add aha-workspace PROD --key research
know add arxiv https://arxiv.org/abs/1706.03762 --key research
know add google-releases https://docs.cloud.google.com/feeds/gcp-release-notes.xml --key research
know add github-repo https://github.com/example/repo.git --key research --branch main --branch develop
know add television research-sources --key research --source-command "know list sources --key research --json"
know list credentials
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
know list credentials
know list sources --key <KEY>
know add confluence --space <SPACE> --key <KEY>
know search confluence "text search"
know search arxiv "all:transformer" --max-results 10
know add arxiv <URL> --key <KEY>
know add google-releases <FEED_URL> --key <KEY>
know add github-repo <REPO_URL> --key <KEY> --branch <BRANCH>
know add jira-project <PROJECT> --key <KEY>
know add aha-workspace <PRODUCT> --key <KEY>
know add television <CHANNEL> --key <KEY> --source-command <COMMAND>
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

### Create a reusable Television channel from `know list sources`

```bash
know add television research-sources --key research \
  --description "Browse all registered sources for the research key" \
  --source-command "know list sources --key research --format television" \
  --preview-command "know list sources --key research --format television-preview --entry '{}'"
know sync television research-sources --key research
```

### Create a reusable Television channel from arXiv search

```bash
know add television arxiv-transformers --key research \
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
| `know-credentials.toml` | `know-credentials` | Browse stored credentials |
| `know-confluence.toml` | `know-confluence` | Search Confluence pages |
| `know-jira.toml` | `know-jira` | Search Jira issues |
| `know-arxiv.toml` | `know-arxiv` | Search arXiv papers |

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
tv know-jira
```

## Notes

- `keys.yaml` stores named credentials that can be referenced as `$name`.
- Credential management also follows the `know <verb> <object>` pattern: `know set credential ...` and `know list credentials`.
- `know add aha-workspace <PRODUCT> --key <KEY>` can read `AHA_BASE_URL` and `AHA_TOKEN` from `.env`, storing the token as `$env:AHA_TOKEN` instead of copying the secret into metadata.
- Exported Markdown always includes YAML frontmatter with source provenance.
- `know export` renders Markdown into each key library and also produces a zip archive for import or transfer.
- Television channel sources materialize a reusable `channel.toml` plus install/run commands for `tv`.
- Google release feeds are normalized into one Markdown document per feed entry date plus the raw `feed.xml`.
- Human docs are in `docs/`.
- Coverage gate command: `python scripts/check_coverage.py --threshold 80`
