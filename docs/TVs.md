# Television Guide

This document covers Television (`tv`) usage with the `know` CLI.

Use this guide together with:

- [README.md](README.md): documentation map
- [cli.md](cli.md): general CLI workflows
- [COMMANDS.md](COMMANDS.md): compact command lookup

The project supports `tv` in three ways:

1. Run a bundled channel directly, such as `tv know-keys`.
2. Run `tv` inline with a `know ... --format television` source command.
3. Register a reusable channel with `know add tv ...` and generate its cable with `know sync television ...`.

## Prerequisites

Install the bundled cable files so Television can discover the channels:

```bash
# Unix / macOS
mkdir -p ~/.config/television/cable
cp cables/*.toml ~/.config/television/cable/
```

```powershell
# Windows PowerShell
New-Item -ItemType Directory -Force -Path $HOME/.config/television/cable | Out-Null
Copy-Item cables/*.toml $HOME/.config/television/cable/
```

## Hub Channel

### `tv know`

Open the hub channel that lists available `know` channels.

```bash
tv know
```

Underlying source command:

```bash
tv list-channels
```

## Bundled Channels

These channels work after copying the bundled `.toml` files into `~/.config/television/cable/`.

| `tv` command | Purpose | Backing `know` command |
|---|---|---|
| `tv know-keys` | Browse knowledge keys. | `know list keys --format television` |
| `tv know-sources` | Browse all registered sources. | `know list sources --format television` |
| `tv know-confluence` | Search Confluence pages. | `know search confluence "" --format television` |
| `tv know-confluence-sync` | Browse Confluence pages with sync status. | `know browse confluence --format television` |
| `tv know-jira` | Search Jira issues. | `know search jira "" --format television` |
| `tv know-jira-sync` | Browse Jira issues with sync status. | `know browse jira --format television` |
| `tv know-arxiv` | Search arXiv papers. | `know search arxiv "all:$SEARCH" --format television --max-results 20 --sort-by submittedDate` |
| `tv know-brave` | Search the web with Brave Search API. | `know search brave "$SEARCH" --format television --count 20` |
| `tv know-arxiv-sync` | Browse arXiv papers with sync status. | `know browse arxiv --format television` |
| `tv know-aha-sync` | Browse Aha features with sync status. | `know browse aha --format television` |
| `tv know-releases-sync` | Browse Google release notes with sync status. | `know browse releases --format television` |
| `tv know-github-view` | Browse GitHub repositories. | `know browse github --format television` |
| `tv know-follow` | Inspect follow-up items from GitHub, starred GitHub repos, and Jira; `Enter` opens the selected item through PowerShell `start`. | `know browse follow --format television` |
| `tv know-videos-browse` | Browse video sources with sync status. | `know browse videos --format television` |
| `tv know-sites-browse` | Browse website sources with sync status. | `know browse sites --format television` |
| `tv know-local` | Browse all local knowledge files. | `know browse local --format television` |
| `tv know-by-key` | Browse keys, then drill into sources. | `know browse by-key --format television` |
| `tv know-by-type` | Browse source types, then drill into local items of that type. | `know browse by-type --format television` |
| `tv know-papers` | Browse all arXiv papers across keys. | `know browse papers --format television` |
| `tv know-repos` | Browse synced repositories, then drill into repo files. | `know browse repos --format television` |
| `tv know-files` | Browse files across the local knowledge store. | `know browse files --format television` |
| `tv know-recent` | Browse recently synced sources. | `know browse recent --format television` |
| `tv know-stale` | Browse stale sources. | `know browse stale --format television` |
| `tv know-unsynced` | Browse never-synced sources. | `know browse unsynced --format television` |
| `tv know-timeline` | Browse the source timeline. | `know browse timeline --format television` |
| `tv know-commands` | Browse saved operational commands. | `know browse commands --format television` |
| `tv know-stats` | Browse knowledge base statistics. | `know browse stats --format television` |
| `tv know-crossref` | Browse sources shared across multiple keys. | `know browse crossref --format television` |

## Inline `tv` Commands With Parameters

Use inline mode when you need to pass parameters that the bundled channel does not expose directly.

### Filter by key

Browse sources for one key:

```bash
tv --source-command='know list sources --key research --format television' \
   --preview-command='know list sources --key research --format television-preview --entry "{}"'
```

Browse Jira items for one key:

```bash
tv --source-command='know browse jira --key work --format television' \
   --preview-command='know browse jira --key work --format television-preview --entry "{}"'
```

Browse local files for one key:

```bash
tv --source-command='know browse local --key research --format television' \
   --preview-command='know browse local --key research --format television-preview --entry "{}"'
```

### Filter by type, repo, or source

Browse only one local source type:

```bash
tv --source-command='know browse local --type arxiv --format television' \
   --preview-command='know browse local --type arxiv --format television-preview --entry "{}"'
```

Browse files inside one synced repository:

```bash
tv --source-command='know browse repo-files --repo owner/myrepo --format television' \
   --preview-command='know browse repo-files --repo owner/myrepo --format television-preview --entry "{}"'
```

Browse files inside one registered source:

```bash
tv --source-command='know browse source-files --key research --source-id arxiv-2401.12345 --format television' \
   --preview-command='know browse source-files --key research --source-id arxiv-2401.12345 --format television-preview --entry "{}"'
```

### Search with input parameters

Search arXiv with a query and result controls:

```bash
tv --source-command='know search arxiv "all:machine learning" --format television --max-results 20 --sort-by submittedDate' \
   --preview-command='know search arxiv "all:machine learning" --format television-preview --max-results 20 --sort-by submittedDate --entry "{}"'
```

Search the web through Brave Search:

```bash
tv --source-command='know search brave "openai codex" --format television --count 10' \
   --preview-command='know search brave "openai codex" --format television-preview --count 10 --entry "{}"'
```

Search Jira for one project:

```bash
tv --source-command='know search jira "" --project KAN --format television' \
   --preview-command='know search jira "" --project KAN --format television-preview --entry "{}"'
```

Search Confluence in one space:

```bash
tv --source-command='know search confluence "" --space ENG --format television' \
   --preview-command='know search confluence "" --space ENG --format television-preview --entry "{}"'
```

Browse recently synced sources with a custom limit:

```bash
tv --source-command='know browse recent --limit 10 --format television' \
   --preview-command='know browse recent --format television-preview --entry "{}"'
```

Browse stale sources with a custom age threshold:

```bash
tv --source-command='know browse stale --days 30 --format television' \
   --preview-command='know browse stale --format television-preview --entry "{}"'
```

Browse files using a full-text query:

```bash
tv --source-command='know browse files --query "incident" --format television' \
   --preview-command='know browse files --query "incident" --format television-preview --entry "{}"'
```

## Follow Channel URL Handling

The bundled `know-follow` cable opens the selected item by resolving the URL with `know browse follow-url '{}'` and passing it to PowerShell `start`.

- `know browse follow-url <ROW>` resolves and prints the target URL.
- The bundled cable runs `powershell -NoProfile -Command "`$url = know browse follow-url '{}'; if (`$url) { start `$url }"` on `Enter`.
- `know browse follow-open <ROW>` still exists as a Python `webbrowser` fallback if you want to call it directly.
- The preview command still pipes Markdown through `bat` for syntax-highlighted rendering in Television.

## Drill-Down Channels

Some bundled channels open another `tv` session when you press `Enter`.

| Channel | Enter action |
|---|---|
| `tv know` | Opens the selected channel with `tv {channel}`. |
| `tv know-by-key` | Runs `know browse key-sources --key <selected-key> ...`. |
| `tv know-by-type` | Runs `know browse local --type <selected-type> ...`. |
| `tv know-repos` | Runs `know browse repo-files --repo <selected-repo> ...`. |
| `tv know-github-view` | Runs `know browse github-activity <selected-owner/repo> ...`. |

## Register A Custom Television Channel

Use `know add tv` when you want a reusable `tv` channel stored in the knowledge base.

Command shape:

```bash
know add tv <NAME> --key <KEY> --source-command <COMMAND> \
  [--description <TEXT>] \
  [--source-display <TEMPLATE>] \
  [--preview-command <COMMAND>] \
  [--action-command <COMMAND>]
```

Examples:

```bash
know add tv research-sources --key research \
  --description "Browse sources attached to the research key" \
  --source-command "know list sources --key research --format television" \
  --preview-command "know list sources --key research --format television-preview --entry '{}'"

know sync television research-sources --key research
```

```bash
know add tv jira-kan --key work \
  --description "Browse Jira issues for project KAN" \
  --source-command "know search jira \"\" --project KAN --format television" \
  --preview-command "know search jira \"\" --project KAN --format television-preview --entry '{}'"

know sync television jira-kan --key work
```

`know add television` is an alias for `know add tv`.

If you omit the channel name and run `know add tv`, the command installs the bundled cable files instead of registering a knowledge source.
