# Bundle generator specification

Use `scripts/generate_bundle.py` when a request needs advanced cables, both platforms, user configuration, typed previews, or a chain.

## Command

```text
python scripts/generate_bundle.py <SPEC.json> --output <DIRECTORY> [--platform both|macos|windows]
python scripts/generate_bundle.py <SPEC.json> --check [--platform both|macos|windows]
```

`--check` validates and renders in memory without writing files.

## Root fields

| Field | Required | Meaning |
|---|---|---|
| `bundle` | yes | Stable bundle slug. |
| `channelSchema` | no | `stable-0.14` by default, or `current` for current-main features such as named source commands. |
| `config` | no | Generic Television `config.toml` object. |
| `channels` | yes | Ordered list of one to three channel objects. |

Any value may use `{"by_platform":{"macos":VALUE,"windows":VALUE}}`. Include both requested platforms or provide `default` inside `by_platform`.

## Channel fields

| Field | Required | Meaning |
|---|---|---|
| `name` | yes | Cable filename and `[metadata] name`. |
| `description` | no | Metadata description. |
| `requirements` | no | Binaries invoked by this cable. |
| `watch` | no | Top-level source refresh interval. |
| `source` | yes | Television source table; `command` is required. |
| `preview` | no | Preview table, or `preset` plus `target`. |
| `ui` | no | UI table and nested panel tables. |
| `history` | no | History table. |
| `keybindings` | no | Standard and custom bindings. |
| `actions` | no | Mapping from action id to action table. |
| `enter` | no | Validated association to the immediately following channel. |

The generator accepts scalar TOML values, scalar arrays, nested tables, and arrays of tables. Use a list of strings for source cycling with Television 0.14.x. Set `channelSchema` to `current` before using `{name, run, ...}` objects for named commands, and verify that the installed `tv` accepts them. The generator does not silently downgrade named sources because doing so would discard their labels.

## Typed preview presets

Use `preview.preset` with `preview.target` when a standard finite preview is sufficient. Supported presets are `text`, `code`, `markdown`, `json`, `yaml`, `csv`, `tsv`, `directory`, `image`, `pdf`, `media`, and `archive`. The generator writes the command and adds its tools to `metadata.requirements` and `requirements.json`.

Example:

```json
"preview": {
  "preset": "csv",
  "target": "{split:\\t:0}",
  "cached": true
}
```

## Enter association

`enter` has these fields:

| Field | Required | Meaning |
|---|---|---|
| `to` | yes | Name of the immediately following channel. |
| `command` | yes | String or platform value that launches the target and contains a selected-row template. |
| `action` | no | Action id; defaults to `next`. |
| `description` | no | Action description. |
| `mode` | no | `fork` or `execute`; defaults to `fork`. |
| `shell` | no | Explicit supported shell when platform syntax requires it. |
| `env` | no | Action environment; may carry the selected-row template instead of interpolating it into command text. |

The last channel cannot contain `enter`. The command must name the target channel, and either `command` or `env` must include a Television template so the relationship is not lost.

## Complete three-level example

```json
{
  "bundle": "catalog-browser",
  "channelSchema": "stable-0.14",
  "config": {
    "default_channel": "accounts",
    "ui": {"theme": "nord-dark", "orientation": "landscape"}
  },
  "channels": [
    {
      "name": "accounts",
      "description": "Select an account",
      "requirements": ["tv", "catalogctl"],
      "source": {
        "command": ["catalogctl accounts --active --format tsv", "catalogctl accounts --format tsv"],
        "output": "{split:\\t:0}"
      },
      "preview": {"preset": "json", "target": "{split:\\t:0}"},
      "enter": {
        "to": "account-projects",
        "command": {
          "by_platform": {
            "macos": "TV_ACCOUNT_ID='{split:\\t:0}' tv account-projects",
            "windows": "$env:TV_ACCOUNT_ID='{split:\\t:0}'; tv account-projects"
          }
        },
        "shell": {"by_platform": {"macos": "bash", "windows": "powershell"}},
        "mode": "fork"
      }
    },
    {
      "name": "account-projects",
      "description": "Select a project",
      "requirements": ["tv", "catalogctl"],
      "source": {
        "command": {
          "by_platform": {
            "macos": "catalogctl projects --account '$TV_ACCOUNT_ID' --format tsv",
            "windows": "catalogctl projects --account '$env:TV_ACCOUNT_ID' --format tsv"
          }
        },
        "output": "{split:\\t:0}"
      },
      "enter": {
        "to": "project-datasets",
        "command": {
          "by_platform": {
            "macos": "TV_PROJECT_ID='{split:\\t:0}' tv project-datasets",
            "windows": "$env:TV_PROJECT_ID='{split:\\t:0}'; tv project-datasets"
          }
        },
        "shell": {"by_platform": {"macos": "bash", "windows": "powershell"}},
        "mode": "fork"
      }
    },
    {
      "name": "project-datasets",
      "description": "Select a dataset",
      "requirements": ["catalogctl", "mlr"],
      "source": {
        "command": {
          "by_platform": {
            "macos": "catalogctl datasets --account '$TV_ACCOUNT_ID' --project '$TV_PROJECT_ID' --format tsv",
            "windows": "catalogctl datasets --account '$env:TV_ACCOUNT_ID' --project '$env:TV_PROJECT_ID' --format tsv"
          }
        },
        "output": "{split:\\t:0}"
      },
      "preview": {"preset": "csv", "target": "{split:\\t:1}"}
    }
  ]
}
```

## Outputs

The output root contains:

```text
manifest.json
requirements.json
macos/
  config.toml              # only when config was requested
  cable/*.toml
  install.sh
windows/
  config.toml              # only when config was requested
  cable/*.toml
  install.ps1
```

Installers copy cables by default. Replacing `config.toml` requires `INSTALL_TELEVISION_CONFIG=1` on macOS or `-InstallConfig` on Windows.
