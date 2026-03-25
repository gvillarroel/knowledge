# Television Integration

Television (`tv`) is a terminal fuzzy-finder that reads rows from a source command and shows a preview pane for the selected row. The `know` CLI integrates with Television in two ways:

1. **Output formats** — every `list` and `search` command supports `--format television` and `--format television-preview` to emit rows and previews directly consumable by `tv`.
2. **Television source adapter** — `know add television` registers a reproducible channel definition inside the knowledge store, generating a TOML cable file and install helpers.

---

## Quick Start

### 1. Browse keys interactively

```bash
tv \
  --source-command "know list keys --format television" \
  --preview-command "know list keys --format television-preview --entry '{}'"
```

### 2. Browse sources for a key

```bash
tv \
  --source-command "know list sources --key research --format television" \
  --preview-command "know list sources --key research --format television-preview --entry '{}'"
```

### 3. Search arXiv papers

```bash
tv \
  --source-command 'know search arxiv "attention is all you need" --format television --max-results 20 --sort-by submittedDate' \
  --preview-command 'know search arxiv "attention is all you need" --format television-preview --entry "{}"'
```

No installation step is required — just pipe the commands to `tv` inline.

---

## Output Formats

### `--format television`

Emits **one line per result** separated by `|`. This is the format `tv` expects from a source command. Each command uses a layout appropriate to its data:

| Command | Row layout |
|---|---|
| `know list keys` | `key_name` |
| `know list credentials` | `credential_name` |
| `know list sources` | `source_id \| type \| key \| title` |
| `know search confluence` | `title \| space \| key \| url` |
| `know search jira` | `issue_key \| summary \| status \| project \| assignee` |
| `know search arxiv` | `title \| primary_category \| published` |

### `--format television-preview`

Renders a **Markdown detail pane** for the currently highlighted row. Must be used together with `--entry '{}'`, where `{}` is replaced by `tv` with the selected row text.

For `know list sources`, the preview reads the synchronized `.md` files from the source directory and displays their content **without YAML frontmatter**. If the source has not been synced yet or has no Markdown files, the preview falls back to showing source metadata (id, type, key, timestamps, config, and commands).

### Example: Confluence search

```bash
tv \
  --source-command 'know search confluence "postmortem" --space ENG --format television' \
  --preview-command 'know search confluence "postmortem" --space ENG --format television-preview --entry "{}"'
```

### Example: Jira search

```bash
tv \
  --source-command 'know search jira "" --project KAN --format television' \
  --preview-command 'know search jira "" --project KAN --format television-preview --entry "{}"'
```

---

## Television Source Adapter

When you need a **persistent, reproducible** channel definition stored in the knowledge base, use the Television source adapter instead of inline commands.

### Register a channel

```bash
know add television <CHANNEL_NAME> --key <KEY> \
  --source-command "<COMMAND>" \
  [--preview-command "<COMMAND>"] \
  [--description "<TEXT>"] \
  [--source-display "<TEMPLATE>"] \
  [--action-command "<COMMAND>"]
```

**Required arguments:**

| Argument | Description |
|---|---|
| `<CHANNEL_NAME>` | Name for the Television channel (used as `tv <CHANNEL_NAME>`). |
| `--key <KEY>` | Knowledge key the channel belongs to. |
| `--source-command` | Shell command that produces the row list for `tv`. |

**Optional arguments:**

| Argument | Description |
|---|---|
| `--description` | Human-readable description stored in the channel TOML. |
| `--preview-command` | Command that renders the preview pane for the selected row. |
| `--source-display` | Display template for the source rows (passed to `tv`). |
| `--action-command` | Command bound to `Ctrl-O` to open or act on the selected row. |

### Sync the channel

```bash
know sync television <CHANNEL_NAME> --key <KEY>
```

This generates three files under `~/.knowledge/<KEY>/television/<source-id>/`:

| File | Purpose |
|---|---|
| `<channel-slug>.toml` | Television cable definition ready to copy into `~/.config/television/cable/`. |
| `commands.json` | Install, run, and sync commands for the channel. |
| `README.md` | Human-readable instructions with all commands. |

### Install the generated cable

After syncing, install the TOML cable file so `tv` discovers the channel automatically:

```bash
# Unix / macOS
mkdir -p ~/.config/television/cable
cp ~/.knowledge/<KEY>/television/<source-id>/<channel-slug>.toml ~/.config/television/cable/

# PowerShell
New-Item -ItemType Directory -Force -Path $HOME/.config/television/cable | Out-Null
Copy-Item -Force "<channel-path>.toml" "$HOME/.config/television/cable/<channel-slug>.toml"
```

Or use the commands in `commands.json`:

```bash
cat ~/.knowledge/<KEY>/television/<source-id>/commands.json | python -m json.tool
```

### Run the channel

```bash
tv <CHANNEL_NAME>
```

---

## Recipes

### Browse arXiv search results

```bash
know add television arxiv-transformers --key research \
  --description "Browse arXiv search results for transformer papers" \
  --source-command 'know search arxiv "attention is all you need" --format television --max-results 20' \
  --preview-command 'know search arxiv "attention is all you need" --format television-preview --entry "{}"'

know sync television arxiv-transformers --key research
```

### Browse registered sources for a key

```bash
know add television research-sources --key research \
  --description "Browse registered sources for the research key" \
  --source-command "know list sources --key research --format television" \
  --preview-command "know list sources --key research --format television-preview --entry '{}'"

know sync television research-sources --key research
```

### Browse Jira issues

```bash
know add television jira-browse --key work \
  --description "Browse Jira KAN issues" \
  --source-command 'know search jira "" --project KAN --format television' \
  --preview-command 'know search jira "" --project KAN --format television-preview --entry "{}"'

know sync television jira-browse --key work
```

### Browse Confluence pages

```bash
know add television confluence-eng --key work \
  --description "Search Confluence ENG space" \
  --source-command 'know search confluence "" --space ENG --format television' \
  --preview-command 'know search confluence "" --space ENG --format television-preview --entry "{}"'

know sync television confluence-eng --key work
```

---

## Pre-built Cables

The repository includes ready-to-use Television cable files in `cables/` at the repository root. Each file is a standalone TOML channel definition that wires a `know` command into `tv`.

| Cable file | Channel | Description |
|---|---|---|
| `know-keys.toml` | `know-keys` | Browse knowledge keys |
| `know-sources.toml` | `know-sources` | Browse all registered sources |
| `know-credentials.toml` | `know-credentials` | Browse stored credentials |
| `know-confluence.toml` | `know-confluence` | Search Confluence pages |
| `know-jira.toml` | `know-jira` | Search Jira issues |
| `know-arxiv.toml` | `know-arxiv` | Search arXiv papers |

### Installing cables

Television discovers custom channels from TOML files in `~/.config/television/cable/`. To install the pre-built cables:

**Unix / macOS:**

```bash
mkdir -p ~/.config/television/cable
cp cables/*.toml ~/.config/television/cable/
```

**PowerShell (Windows):**

```powershell
New-Item -ItemType Directory -Force -Path $HOME/.config/television/cable | Out-Null
Copy-Item cables/*.toml $HOME/.config/television/cable/
```

To install a single cable:

```bash
# Unix / macOS
cp cables/know-arxiv.toml ~/.config/television/cable/

# PowerShell
Copy-Item cables/know-arxiv.toml $HOME/.config/television/cable/
```

### Verifying the installation

After copying the files, run any channel by name:

```bash
tv know-keys
tv know-sources
tv know-arxiv
```

Television will read the TOML definition, execute the `source.command` to populate the row list, and render the `preview.command` output for the highlighted row.

### Customizing a cable

Each cable file follows a simple structure. Edit the TOML directly to change search queries, filters, or display settings:

```toml
[metadata]
name = "know-arxiv"
description = "Search arXiv papers"

[source]
command = "know search arxiv \"all:machine learning\" --format television --max-results 20 --sort-by submittedDate"

[preview]
command = "know search arxiv \"all:machine learning\" --format television-preview --max-results 20 --sort-by submittedDate --entry '{}'"
```

Change the search query or add filters as needed. The `'{}'` placeholder in the preview command is replaced by Television with the currently selected row.

### Uninstalling cables

Remove the TOML files from the cable directory:

```bash
# Unix / macOS
rm ~/.config/television/cable/know-*.toml

# PowerShell
Remove-Item $HOME/.config/television/cable/know-*.toml
```

---

## Generated TOML Structure

The Television source adapter produces a TOML cable file with the following sections:

```toml
[metadata]
name = "channel-name"
description = "Human-readable description"

[source]
command = "know search arxiv ... --format television"
display = "{0}"        # optional display template

[preview]
command = "know search arxiv ... --format television-preview --entry '{}'"

[keybindings]
ctrl-o = "actions:open"

[actions.open]
command = "xdg-open {0}"   # only present when --action-command is set
mode = "execute"
```

---

## Architecture

The Television integration is split across two modules:

| Module | Responsibility |
|---|---|
| `src/knowledge/television.py` | Output formatting functions (`format_*_television`, `format_*_preview`) and the `TV_FORMAT_CHOICES` constant. |
| `src/knowledge/sources/television.py` | `TelevisionSource` adapter that generates TOML cable files, command manifests, and README files during `sync`. |

The CLI (`src/knowledge/cli.py`) wires the `--format` flag to the formatters and exposes `know add television` and `know sync television` subcommands.

---

## Related Documentation

- [CLI reference](cli.md) — full command listing including Television flags.
- [Know skill](know-skill.md) — Codex skill with Television patterns.
- [SPEC.md](../SPEC.md) — project specification mentioning Television channel definitions.
