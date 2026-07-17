# Read-only Television diagnostics

Use this workflow when a registered channel changes behavior after a Television
or dependency upgrade. Diagnose from preserved evidence before editing,
regenerating, synchronizing, installing, or moving anything.

## Preserve the source of truth

Record and copy the registered cable, its generated directory, `commands.json`,
`README.md`, `source-metadata.yaml`, effective `config.toml`, and any invoked
scripts. Record paths, timestamps, sizes, and SHA-256 hashes. Keep the originals
in place and run isolated tests from the copies.

## Capture the exact effective-path inputs

macOS:

```sh
printf 'TELEVISION_CONFIG=%s\nXDG_CONFIG_HOME=%s\nHOME=%s\n' \
  "${TELEVISION_CONFIG-}" "${XDG_CONFIG_HOME-}" "${HOME-}"
```

Windows PowerShell:

```powershell
"TELEVISION_CONFIG=$env:TELEVISION_CONFIG"
"XDG_CONFIG_HOME=$env:XDG_CONFIG_HOME"
"LOCALAPPDATA=$env:LOCALAPPDATA"
"HOME=$HOME"
```

Resolve `TELEVISION_CONFIG` first, `XDG_CONFIG_HOME/television` second, and then
the platform default: `$HOME/.config/television` on macOS or
`$env:LOCALAPPDATA\television\config` on Windows. Do not probe
`~/Library/Application Support` as though it were Television's macOS default.

## Capture command surfaces and raw behavior

1. Record `tv --version`, `tv --help`, and `tv list-channels`.
2. Record `--version` and relevant `--help` output for every executable invoked
   by source, preview, or action definitions.
3. Parse copied TOML without rewriting it and inspect table types and nesting.
4. Run the copied source command directly. Record its exit code, stdout, and
   stderr separately and preserve one raw selected row.
5. Expand the preview template for that row according to the installed
   Television version, run the preview directly, and record exit code, stdout,
   and stderr.
6. Inspect the Enter binding, named action, exact child name, selected stable
   field, quoting, action environment, shell, and mode.
7. Load only the copied cables with
   `tv --cable-dir <COPIED_CABLE_DIR> list-channels`, then launch the copied
   parent and exercise its transition only if that action is non-mutating.

If a direct preview fails, diagnose its binary, flags, input, shell,
environment, or working directory. If it succeeds directly but fails inside
Television, compare template expansion and the preview environment. If the
child is listed but Enter fails, focus on action schema and selected context;
if the child is absent, focus on the resolved cable directory and TOML load.

Do not run installers, replace active configuration, call `know sync`, upgrade
packages, or execute a mutating action during diagnosis.
