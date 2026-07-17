# Platform configuration and associated chains

Read this reference when generating install artifacts, `config.toml`, shell-specific commands, or Enter-driven navigation.

Official sources:

- [Configuration paths and overrides](https://alexpasmantier.github.io/television/user-guide/configuration/)
- [Installation](https://alexpasmantier.github.io/television/getting-started/installation/)
- [Current path implementation](https://github.com/alexpasmantier/television/blob/main/television/config/mod.rs)
- [Current shell support](https://github.com/alexpasmantier/television/blob/main/television/utils/shell.rs)
- [Current action execution behavior](https://github.com/alexpasmantier/television/blob/main/television/utils/command.rs)

## Effective configuration directories

Resolve paths in this order:

1. `TELEVISION_CONFIG` as the complete Television configuration directory.
2. `XDG_CONFIG_HOME/television` when `XDG_CONFIG_HOME` is set.
3. The platform default.

| Platform | Default `config.toml` | Default cable directory |
|---|---|---|
| macOS | `$HOME/.config/television/config.toml` | `$HOME/.config/television/cable/` |
| Windows | `%LOCALAPPDATA%\television\config\config.toml` | `%LOCALAPPDATA%\television\config\cable\` |

Do not assume `~/Library/Application Support` on macOS. Do not use `$HOME/.config` as the only Windows destination.

Generate separate platform variants when commands contain `$HOME`, `$env:...`, `head`, `Select-Object`, `2>/dev/null`, `open`, `Start-Process`, `xdg-open`, `&&`, or platform-specific quoting.

## Television installation

```sh
brew install television
```

```powershell
winget install --exact --id alexpasmantier.television
# Alternative:
scoop bucket add extras
scoop install television
```

Do not install automatically. Verify with `tv --version`, `tv --help`, and `tv list-channels`.

## Configuration replacement policy

- Install cable files by default.
- Generate `config.toml` when requested, but make replacement of an existing user configuration opt-in.
- Honor `--config-file` and `--cable-dir` when the user wants an isolated smoke test.
- Preserve an existing configuration or create a backup before any authorized replacement.

## Linear association contract

A chain contains one, two, or three channels. For a three-level chain:

```text
level 1 selection -> Enter action -> level 2 source
level 2 selection -> Enter action -> level 3 source
level 3 selection -> final output or domain action
```

Require all of the following:

- exactly one cable per logical level and per requested platform;
- a stable selection identifier propagated at both transitions;
- `enter = "actions:<name>"` on levels one and two;
- no next-channel Enter action on level three;
- no cycles, skipped levels, or more than three levels;
- explicit `fork` or `execute` semantics.

`mode = "execute"` replaces the Television process on macOS. Windows cannot replace the process and falls back to fork behavior. Prefer explicit `fork` on both variants when the navigation must return to its parent consistently.

## Passing association context

For a selected directory, Television can pass the path as the child's positional working directory:

```toml
[keybindings]
enter = "actions:next"

[actions.next]
description = "Open the associated child channel"
command = "tv child-channel '{}'"
mode = "fork"
```

For an arbitrary stable identifier, prefer a templated action environment and let the child source read it:

```toml
[actions.next]
description = "Open projects for the selected account"
command = "tv account-projects"
mode = "fork"

[actions.next.env]
TV_ACCOUNT_ID = "{split:\t:0}"
```

This avoids inserting selected data into shell program text. Verify support with an isolated load because older Television versions may require a platform-specific command instead.

macOS fallback:

```toml
[actions.next]
description = "Open projects for the selected account"
command = "TV_ACCOUNT_ID='{split:\t:0}' tv account-projects"
shell = "bash"
mode = "fork"
```

Windows fallback:

```toml
[actions.next]
description = "Open projects for the selected account"
command = "$env:TV_ACCOUNT_ID='{split:\t:0}'; tv account-projects"
shell = "powershell"
mode = "fork"
```

The level-two source reads `$TV_ACCOUNT_ID` on macOS or `$env:TV_ACCOUNT_ID` on Windows. Use a new variable such as `TV_PROJECT_ID` for the second transition so level three can still access both identifiers.

Treat selected rows as untrusted data. Extract the smallest stable field with a Television template, quote it at command level, and never splice it into executable program text.
