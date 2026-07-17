# Zotero CLI proof of concept

This POC verifies whether Zotero plus `zotero-mcp-server` can replace the
agent-facing parts of `know`. It uses a local Zotero 9 library, a real public
arXiv PDF, `zotero-cli`, the Zotero local API, and `rg`.

## Prerequisites

- Zotero 7 or newer, running locally.
- In Zotero Settings → Advanced, enable **Allow other applications on this
  computer to communicate with Zotero**.
- Install the community CLI:

```powershell
uv tool install zotero-mcp-server
```

- Install `rg` and make it available on `PATH`.

The local API is read-only and unauthenticated on loopback. Never expose port
`23119` to another host.

## Run

The first run creates two tagged fixtures in the current Zotero user library:
a journal article with a real 25-page PDF and a generic webpage record.

```powershell
$env:NO_PROXY = "localhost,127.0.0.1"
python pocs/zotero_cli/run_poc.py --seed `
  --output pocs/zotero_cli/results/windows-zotero-9.json
```

Subsequent runs reuse the fixture:

```powershell
python pocs/zotero_cli/run_poc.py
```

The POC fails when a required read, metadata, full-text, attachment, or `rg`
probe fails. Expected product gaps are recorded in the report but do not make
the process fail.

## Direct agent commands

Use UTF-8 explicitly on Windows:

```powershell
$env:ZOTERO_LOCAL = "true"
$env:NO_PROXY = "localhost,127.0.0.1"
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"

zotero-cli search "superhuman synthesis"
zotero-cli get metadata <ITEM_KEY>
zotero-cli get children <ITEM_KEY>
zotero-cli get fulltext <ITEM_KEY> | rg -n -i "Gather Evidence"
```

Avoid `rg -m` directly on the CLI pipe: when `rg` exits after reaching its
match limit, Python reports a broken pipe. Capture the full text first when a
match limit is needed.

Zotero also materializes indexed PDF text in managed cache files:

```powershell
rg --hidden -n -i "Gather Evidence" "$HOME\Zotero\storage" `
  -g ".zotero-ft-cache"
```

This cache is useful evidence, but it is not a stable agent contract: its
folders use opaque attachment keys and agents must never modify Zotero's data
directory.

Optional local semantic retrieval was also verified:

```powershell
uv tool install --force "zotero-mcp-server[semantic]"
zotero-cli db update --fulltext --force-rebuild
zotero-cli search --mode semantic "agentic scientific literature synthesis"
```

The extra installed 166 Python packages and downloaded an approximately 79 MB
embedding model. Its index is separate from Zotero and updates manually by
default.

## Important boundary

`zotero-cli` local mode can read the desktop library, but its write commands
require `ZOTERO_API_KEY` and `ZOTERO_LIBRARY_ID`. A local-only attempt to run
`collections create` or `add url` is rejected. The POC fixture is therefore
created through the local Zotero Connector endpoint, which is the same public
interface used by the browser extension.

See [COVERAGE.md](COVERAGE.md) for the verified replacement matrix.
