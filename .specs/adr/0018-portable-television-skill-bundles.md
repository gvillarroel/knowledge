---
adr: "0018"
title: "ADR 0018: Generate Portable Television Skill Bundles"
summary: "Keep simple know-backed channels while using a standalone validated generator for advanced cross-platform Television configuration, bounded channel chains, and typed previews."
status: "Accepted"
date: "2026-07-13"
product: "knowledge"
owner: "Platform Architecture"
area: "Agent Skills"
tags:
  - television
  - skills
  - portability
  - previews
  - configuration
---

# ADR 0018: Generate Portable Television Skill Bundles

## Status

Accepted.

## Context

The Television skill previously documented only simple `know add tv` workflows. That interface can express one source, one preview, and one default action, but it cannot reproduce the complete Television channel model, platform-specific user configuration, named source cycling, rich UI, arbitrary keybindings, or associated navigation across several channels.

The skill also assumed one Unix-style cable location and named `commands.json` as a generated artifact even though the adapter did not write the manifest. Its evaluation covered four offline plans but did not inspect generated TOML, macOS and Windows differences, CSV previews, optional dependencies, or Enter-driven chains.

Current Television releases distinguish macOS and Windows default configuration directories, support environment overrides, and model channels through metadata, source, preview, UI, history, keybinding, and action sections. Their current Rust types occasionally differ from older prose examples.

## Decision

Use two explicit generation paths.

- Keep `know add tv` and `know sync television` for simple persisted channels backed by the knowledge store.
- Reuse the installed `know list`, `know search`, and `know browse` Television formats exactly as exposed; do not invent alternate adapters or flags. Treat `commands.json` as the simple-path platform manifest and retain the generated cable, README, and source metadata names.
- Bundle a standard-library-only JSON-to-TOML generator inside `skills/television/` for advanced standalone output.
- Generate separate macOS and Windows trees containing optional `config.toml`, cable files, a manifest, a dependency inventory, and safe platform installers.
- Honor `TELEVISION_CONFIG` and `XDG_CONFIG_HOME`; otherwise use `$HOME/.config/television` on macOS and `%LOCALAPPDATA%\television\config` on Windows.
- Install cables by default but require an explicit opt-in before replacing user `config.toml`.
- Model Enter-driven association as a validated linear graph of one to three channels. Require selected-row context at each transition and reject cycles, skipped levels, a fourth level, or a next-channel action on the final level.
- Accept selected-row context in either the transition command or its action environment, so platform quoting can remain safe without losing the association.
- Support typed finite preview presets for text, code, Markdown, JSON, YAML, CSV, TSV, directories, images, PDFs, media, and archives. CSV and TSV previews must use a table-aware parser.
- Add every binary invoked by a preset to channel metadata and to a generated dependency inventory. Generate installation guidance but never install optional preview tools implicitly.
- Default generated cables to the stable Television 0.14-compatible source schema. Expose the current named-source schema only through an explicit `channelSchema: "current"` opt-in and validate that output separately, because released and main-branch schemas can differ.
- Treat installed Television behavior, current source types, and shipped cables as authoritative when they conflict with stale prose documentation.
- Expand the isolated evaluation corpus beyond four prompts and record an explicit quality matrix covering the complete promised surface.
- Diagnose upgrade drift read-only from copied evidence while capturing the exact effective-path variables and preserving registered sources and generated artifacts.
- Make `TelevisionSource.sync()` write the command manifest and README already required by the project specification.

## Consequences

Positive:

- the skill can generate and validate useful artifacts without this checkout;
- platform paths, shell syntax, and configuration replacement are explicit;
- three-level navigation has a bounded, testable association contract;
- CSV and other data previews carry auditable runtime requirements;
- evaluation evidence can inspect actual configuration content instead of rewarding unsupported artifact claims.

Negative:

- the skill owns a small TOML renderer and must track Television schema changes;
- advanced bundles are separate from knowledge-store source registration unless a user also records them through `know`;
- platform variants may duplicate logically equivalent channel definitions;
- richer preview output requires additional executables on the user's `PATH`.
