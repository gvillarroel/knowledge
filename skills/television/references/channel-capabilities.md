# Television channel capability checklist

Use this checklist when designing or reviewing a cable. Prefer the current Television channel types and shipped cables when older prose documentation disagrees.

Official sources:

- [Channel guide](https://alexpasmantier.github.io/television/user-guide/channels/)
- [Channel specification](https://alexpasmantier.github.io/television/reference/channel-spec/)
- [Current channel types](https://github.com/alexpasmantier/television/blob/main/television/channels/prototypes.rs)
- [Actions reference](https://alexpasmantier.github.io/television/reference/actions/)
- [Template system](https://alexpasmantier.github.io/television/advanced/template-system/)

## Capability map

| Area | Decisions to make |
|---|---|
| Metadata | Stable `name`, concise `description`, and every binary invoked by source, preview, or actions in `requirements`. |
| Source commands | One command, a command list, or version-gated named `[[source.command]]` entries; optional command `env`, `shell`, and `interactive`. |
| Source shaping | `display` for the UI, `output` for the final selection, `entry_delimiter` for multiline records, `ansi`, `no_sort`, and `frecency`. |
| Refresh | Top-level `watch` for periodic reload and `reload_source` for an explicit keybinding. Current Rust types place `watch` at channel top level. |
| Preview | One command, cycling commands, `offset`, `cached`, and command-level `env`, `shell`, or `interactive`. Keep preview commands finite and non-interactive. |
| UI | `ui_scale`, `layout`, `theme`, `theme_overrides`, input bar, results panel, preview panel, status bar, help panel, and remote control. |
| History | `[history] global_mode` when navigation must span channels instead of staying channel-local. |
| Keybindings | Standard actions, `shortcut`, arrays of keys, custom `actions:<name>`, preview/source cycling, selection, reload, and panel toggles. |
| External actions | `description`, templated `command`, `mode = "fork"` or `"execute"`, multi-selection `separator`, and optional `env`, `shell`, or `interactive`. |
| Templates | Whole row `{}`, positional fields such as `{0}`, `split`, slices, `strip_ansi`, `trim`, `regex_extract`, `map`, `filter`, `sort`, and `join`. |

## Invariants

- Require `[metadata] name` and `[source] command` for every cable.
- Use a string array for source cycling on Television 0.14.x. Named `[[source.command]]` entries require a compatible newer build and an isolated load test.
- Keep the cable filename and metadata name aligned.
- Do not set `source.display` with `source.ansi = true`; ANSI-aware sources should use `source.output` with `strip_ansi` where needed.
- Use `source.output` to emit a stable identifier rather than a decorated display row.
- Use a non-default `entry_delimiter` only when a source really emits multiline records or NUL-separated values.
- Set `no_sort = true` when source order is authoritative. Set `frecency = false` only when match sorting remains useful but history-based ranking does not.
- Set `preview.cached = false` only for data that must update while selected.
- Put preview headers and footers under `[ui.preview_panel]` for current Television versions.
- Declare an action key only after defining the matching `[actions.<name>]` table.
- Prefer `fork` for actions that should return to the current picker; prefer `execute` for a deliberate process handoff.

## Minimal complete example

```toml
watch = 5.0

[metadata]
name = "incidents"
description = "Browse active incidents"
requirements = ["incidentctl", "jq"]

[source]
command = ["incidentctl list --state active", "incidentctl list --state all"]
output = "{split:\t:0}"
no_sort = true

[preview]
command = "incidentctl show '{split:\t:0}' --json | jq -C ."
cached = false

[ui]
layout = "landscape"

[ui.preview_panel]
size = 65
header = "Incident {split:\t:0}"
border_type = "rounded"

[keybindings]
enter = "actions:open"
ctrl-r = "reload_source"

[actions.open]
description = "Open the incident"
command = "incidentctl open '{split:\t:0}'"
mode = "fork"
```
