---
type: Agent Skill
title: Television
description: Create, generate, install, validate, or troubleshoot Television (`tv`)
  channels and user configuration, including standalone `know`-backed channels, macOS
  and Windows bundles, associated Enter-driven chains of up to three levels, rich
  previews for CSV and other data types, optional preview-tool guidance, source templates,
  UI, history, keybindings, and actions. Use when Codex needs reproducible Television
  cable TOML, `config.toml`, platform install commands, preview recipes, dependency
  preflights, or recovery from a broken channel.
tags:
- codex
- skill
skill_name: television
source_path: skills/television/SKILL.md
---

# Television

Create reproducible Television channels and configuration without assuming access to this repository.

## Standalone boundary

- Treat `tv` and each command invoked by a channel as explicit external prerequisites.
- Treat `know` as optional and require it only for `know`-backed sources.
- Use only this skill package, installed executables, and user-supplied inputs. Do not require root documentation, source modules, repository cables, fixtures, or another skill.
- Run `tv --version`, `tv --help`, and `tv list-channels` before relying on an installed command surface. Run the relevant command's `--help` before composing its source, preview, or action command.

## Choose the generation path

1. Use `know add tv` plus `know sync television` for a simple persisted channel that needs one source, one preview, and at most the default action. Read [know-backed-channels.md](../../skills/television/references/know-backed-channels.md) and reuse native `know --format television` output instead of rebuilding an available adapter.
2. Use `scripts/generate_bundle.py` for `config.toml`, platform variants, named or cycling sources, rich UI, typed previews, arbitrary actions, or a chain of two or three associated channels.
3. Keep generated macOS and Windows outputs separate whenever commands use platform-specific shells, paths, openers, pipelines, or quoting.

## Generate an advanced bundle

Read [bundle-spec.md](../../skills/television/references/bundle-spec.md), then create a JSON specification and run:

```text
python scripts/generate_bundle.py bundle.json --output output/television
python scripts/generate_bundle.py bundle.json --check
```

The generator validates TOML, emits macOS and Windows cable trees, generates opt-in-safe installers, and writes `manifest.json` plus `requirements.json`. It rejects more than three channels and rejects a chain that skips levels, cycles, omits selected-row context, or launches a fourth Television session.

## Cover the complete channel surface

Before finalizing a channel, review [channel-capabilities.md](../../skills/television/references/channel-capabilities.md). Decide explicitly whether the result needs:

- metadata and exact binary requirements;
- one, multiple, or named source commands; display/output templates; ANSI; delimiters; ordering; frecency; or watch mode;
- one or cycling previews; environment, shell, offset, caching, and preview-panel presentation;
- input, results, preview, status, help, remote-control, theme, scale, layout, and history behavior;
- selection output, standard keybindings, external actions, multi-select separators, and `fork` versus `execute`.

Do not combine `source.ansi = true` with `source.display`; transform ANSI output through `source.output` with `strip_ansi` instead.

## Build associated chains

Read [platforms-and-chains.md](../../skills/television/references/platforms-and-chains.md) whenever Enter opens another channel.

- Generate one cable per level and stop at three levels.
- Bind `enter` to a named action on levels one and two only.
- Pass a stable selected identifier or path into the child command; do not associate levels by display text when a stable field exists.
- Prefer `[actions.<name>.env]` for selected context when the installed version supports templated action environments; otherwise use a quoted platform-specific command.
- Prefer `mode = "fork"` on both platforms when users must return to the parent. Account for Windows treating `execute` as `fork`.
- Quote the selected-row template at command level and keep untrusted values out of shell program text.

## Select previews and dependencies

Read [previews-and-tools.md](../../skills/television/references/previews-and-tools.md) whenever a preview is requested or an existing preview fails.

- Select a finite, non-interactive preview command for the real data type.
- Use a table-aware parser for CSV or TSV; never split rows naively on commas or tabs.
- Declare every invoked binary in `metadata.requirements`.
- Name requirements by executable (`rg`, `mlr`, `pdftotext`), not by package label (`ripgrep`, `miller`, `poppler`).
- Treat optional tools as enhancements until a generated cable invokes them; then they are requirements for that cable.
- Generate preflight and installation guidance, but never install packages unless the user explicitly requests installation.
- Provide a graceful fallback or a clear missing-tool error for optional renderers.

## Preserve the simple `know` lifecycle

For a simple channel:

```text
know add tv <CHANNEL> --key <KEY> --source-command <COMMAND> --preview-command <COMMAND>
know sync television <CHANNEL> --key <KEY>
```

Use existing `know list`, `know search`, or `know browse` Television output whenever it covers the source. Do not create a custom network adapter or cache for a source already exposed by `know`.

For an arXiv query, use `know search arxiv <QUERY> --format television` for
rows and the same search with `--format television-preview --entry '{}'` for
the selected-row preview. Do not invent `know browse arxiv <QUERY>`, a
`--preview` flag, or a custom arXiv adapter. `know search arxiv` may require
network access at channel runtime even when generating its cable is an offline
planning task.

Inspect the generated `<CHANNEL>.toml`, `commands.json`, `README.md`, and
`source-metadata.yaml`. These are the generated files; do not substitute
`manifest.json` or `source.json`. Use the commands in `commands.json`, including
`install_macos` or `install_windows`, instead of assuming one cable directory.

## Diagnose an existing channel

Read [diagnostics.md](../../skills/television/references/diagnostics.md) when a source, preview, action,
or cable path changed after an upgrade. Capture the exact values of
`TELEVISION_CONFIG`, `XDG_CONFIG_HOME`, `HOME`, and `LOCALAPPDATA` as applicable;
generic searches for names containing `TELEVISION` are not sufficient evidence
of the effective directory. Preserve the registered source and generated files
and use copied artifacts for isolated tests.

## Validate before delivery

1. Parse every generated TOML file and inspect every `metadata.requirements` entry against the commands it invokes.
2. Run the generated installer only when installation was requested; configuration replacement is opt-in.
3. Load the isolated bundle with `tv --cable-dir <DIR> list-channels` or the installed equivalent.
4. Run each source and preview command directly; record exit code, stdout, and stderr.
5. Exercise both Enter transitions for a three-level chain and confirm the last level has no next-channel action.
6. Verify platform paths in the manifest and run `tv <CHANNEL>` as the final smoke test.

When diagnosing drift, preserve registered sources and generated artifacts until raw commands, effective config paths, installed versions, and TOML parsing have been inspected.
