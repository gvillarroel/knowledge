#!/usr/bin/env python3
"""Generate validated cross-platform Television configuration bundles from JSON."""

from __future__ import annotations

import argparse
import json
import re
import sys
import tomllib
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any


PLATFORMS = ("macos", "windows")
CHANNEL_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
BARE_TOML_KEY_RE = re.compile(r"^[A-Za-z0-9_-]+$")
TEMPLATE_RE = re.compile(r"\{[^}]*\}")


class SpecError(ValueError):
    """Raised when a bundle specification cannot produce a safe valid bundle."""


PREVIEW_PRESETS: dict[str, dict[str, Any]] = {
    "text": {
        "requirements": ["bat"],
        "command": "bat --color=always --style=plain --paging=never -- '{target}'",
    },
    "code": {
        "requirements": ["bat"],
        "command": "bat -n --color=always --paging=never -- '{target}'",
    },
    "markdown": {
        "requirements": ["glow"],
        "command": "glow -s dark -w 100 '{target}'",
    },
    "json": {
        "requirements": ["jq"],
        "command": "jq -C . '{target}'",
    },
    "yaml": {
        "requirements": ["yq"],
        "command": "yq -C . '{target}'",
    },
    "csv": {
        "requirements": ["mlr"],
        "command": "mlr --icsv --opprint --barred head -n 100 '{target}'",
    },
    "tsv": {
        "requirements": ["mlr"],
        "command": "mlr --itsv --opprint --barred head -n 100 '{target}'",
    },
    "directory": {
        "requirements": ["eza"],
        "command": "eza --tree --level=2 --color=always -- '{target}'",
    },
    "image": {
        "requirements": ["chafa"],
        "command": "chafa -s 80x40 '{target}'",
    },
    "pdf": {
        "requirements": ["pdftotext"],
        "command": {
            "macos": "pdftotext -l 2 -layout '{target}' - | head -100",
            "windows": "pdftotext -l 2 -layout '{target}' - | Select-Object -First 100",
        },
    },
    "media": {
        "requirements": ["ffprobe", "jq"],
        "command": (
            "ffprobe -v quiet -print_format json -show_format -show_streams "
            "'{target}' | jq -C ."
        ),
    },
    "archive": {
        "requirements": ["7z"],
        "command": "7z l '{target}'",
    },
}


TOOL_CATALOG: dict[str, dict[str, Any]] = {
    "tv": {
        "purpose": "Television runtime",
        "install": {
            "macos": ["brew install television"],
            "windows": [
                "winget install --exact --id alexpasmantier.television",
                "scoop bucket add extras; scoop install television",
            ],
        },
    },
    "fd": {
        "purpose": "Fast file discovery",
        "install": {"macos": ["brew install fd"], "windows": ["winget install sharkdp.fd"]},
    },
    "bat": {
        "purpose": "ANSI text and source-code preview",
        "install": {"macos": ["brew install bat"], "windows": ["winget install sharkdp.bat"]},
    },
    "rg": {
        "purpose": "Fast text search",
        "install": {
            "macos": ["brew install ripgrep"],
            "windows": ["winget install BurntSushi.ripgrep.MSVC"],
        },
    },
    "jq": {
        "purpose": "Colored JSON preview",
        "install": {"macos": ["brew install jq"], "windows": ["winget install jqlang.jq"]},
    },
    "yq": {
        "purpose": "YAML, TOML, and XML preview",
        "install": {"macos": ["brew install yq"], "windows": ["winget install MikeFarah.yq"]},
    },
    "eza": {
        "purpose": "Directory-tree preview",
        "install": {"macos": ["brew install eza"], "windows": ["winget install eza-community.eza"]},
    },
    "glow": {
        "purpose": "Markdown preview",
        "install": {
            "macos": ["brew install glow"],
            "windows": ["winget install charmbracelet.glow"],
        },
    },
    "mlr": {
        "purpose": "CSV and TSV table preview",
        "install": {
            "macos": ["brew install miller"],
            "windows": ["winget install Miller.Miller"],
        },
    },
    "qsv": {
        "purpose": "Alternative CSV preview and transformation",
        "install": {"macos": ["brew install qsv"], "windows": ["scoop install qsv"]},
    },
    "chafa": {
        "purpose": "ANSI image preview",
        "install": {
            "macos": ["brew install chafa"],
            "windows": ["Install the native archive from https://hpjansson.org/chafa/download/"],
        },
    },
    "pdftotext": {
        "purpose": "Bounded PDF text preview",
        "install": {
            "macos": ["brew install poppler"],
            "windows": [
                "Install Poppler from https://github.com/oschwartz10612/poppler-windows and add Library\\bin to PATH"
            ],
        },
    },
    "ffprobe": {
        "purpose": "Audio and video metadata preview",
        "install": {
            "macos": ["brew install ffmpeg"],
            "windows": ["winget install Gyan.FFmpeg"],
        },
    },
    "7z": {
        "purpose": "Archive listing preview",
        "install": {
            "macos": ["brew install sevenzip"],
            "windows": ["winget install 7zip.7zip"],
        },
    },
}


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate validated macOS and Windows Television bundles from JSON.",
    )
    parser.add_argument("spec", type=Path, help="Path to the JSON bundle specification.")
    parser.add_argument("--output", type=Path, help="Output directory for generated artifacts.")
    parser.add_argument(
        "--platform",
        choices=("both", *PLATFORMS),
        default="both",
        help="Generate both platforms or one platform only (default: both).",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate and render in memory without writing artifacts.",
    )
    args = parser.parse_args(argv)
    if not args.check and args.output is None:
        parser.error("--output is required unless --check is used")
    return args


def _load_spec(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SpecError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise SpecError("the bundle specification root must be an object")
    return payload


def _requested_platforms(value: str) -> tuple[str, ...]:
    return PLATFORMS if value == "both" else (value,)


def _resolve_platform(value: Any, platform: str, path: str) -> Any:
    if isinstance(value, dict) and set(value) == {"by_platform"}:
        choices = value["by_platform"]
        if not isinstance(choices, dict):
            raise SpecError(f"{path}.by_platform must be an object")
        if platform in choices:
            return _resolve_platform(choices[platform], platform, path)
        if "default" in choices:
            return _resolve_platform(choices["default"], platform, path)
        raise SpecError(f"{path} has no value for requested platform {platform}")
    if isinstance(value, dict):
        return {
            str(key): _resolve_platform(child, platform, f"{path}.{key}")
            for key, child in value.items()
        }
    if isinstance(value, list):
        return [
            _resolve_platform(child, platform, f"{path}[{index}]")
            for index, child in enumerate(value)
        ]
    return value


def _require_mapping(value: Any, path: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise SpecError(f"{path} must be an object")
    return value


def _require_string(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise SpecError(f"{path} must be a non-empty string")
    return value


def _validate_root(spec: Mapping[str, Any]) -> tuple[str, str, list[dict[str, Any]]]:
    allowed = {"bundle", "channelSchema", "config", "channels"}
    unknown = sorted(set(spec) - allowed)
    if unknown:
        raise SpecError(f"unknown root fields: {', '.join(unknown)}")
    bundle = _require_string(spec.get("bundle"), "bundle")
    if not CHANNEL_NAME_RE.fullmatch(bundle):
        raise SpecError("bundle must use letters, digits, dots, underscores, or hyphens")
    channel_schema = spec.get("channelSchema", "stable-0.14")
    if channel_schema not in {"stable-0.14", "current"}:
        raise SpecError("channelSchema must be stable-0.14 or current")
    channels = spec.get("channels")
    if not isinstance(channels, list) or not 1 <= len(channels) <= 3:
        raise SpecError("channels must contain between one and three channel objects")
    if not all(isinstance(channel, dict) for channel in channels):
        raise SpecError("every channels item must be an object")
    typed_channels = list(channels)
    names = [_require_string(channel.get("name"), f"channels[{index}].name") for index, channel in enumerate(typed_channels)]
    if len(set(names)) != len(names):
        raise SpecError("channel names must be unique")
    for name in names:
        if not CHANNEL_NAME_RE.fullmatch(name):
            raise SpecError(f"invalid channel name: {name}")
    return bundle, str(channel_schema), typed_channels


def _preview_from_preset(
    preview: dict[str, Any],
    platform: str,
    channel_path: str,
) -> tuple[dict[str, Any], list[str]]:
    preset = preview.pop("preset", None)
    target = preview.pop("target", "{}")
    if preset is None:
        return preview, []
    preset_name = _require_string(preset, f"{channel_path}.preview.preset").lower()
    if preset_name not in PREVIEW_PRESETS:
        choices = ", ".join(sorted(PREVIEW_PRESETS))
        raise SpecError(f"unsupported preview preset {preset_name!r}; choose one of: {choices}")
    target_text = _require_string(target, f"{channel_path}.preview.target")
    if "'" in target_text:
        raise SpecError(f"{channel_path}.preview.target cannot contain a single quote")
    if not TEMPLATE_RE.search(target_text):
        raise SpecError(f"{channel_path}.preview.target must contain a Television template")
    if "command" in preview:
        raise SpecError(f"{channel_path}.preview cannot combine preset and command")
    recipe = PREVIEW_PRESETS[preset_name]
    command_template = recipe["command"]
    if isinstance(command_template, dict):
        command_template = command_template[platform]
    preview["command"] = command_template.format(target=target_text)
    return preview, list(recipe["requirements"])


def _normalize_channel(
    raw_channel: Mapping[str, Any],
    platform: str,
    index: int,
    names: list[str],
    channel_schema: str,
) -> tuple[dict[str, Any], set[str]]:
    channel_path = f"channels[{index}]"
    channel = _resolve_platform(dict(raw_channel), platform, channel_path)
    allowed = {
        "name",
        "description",
        "requirements",
        "watch",
        "source",
        "preview",
        "ui",
        "history",
        "keybindings",
        "actions",
        "enter",
    }
    unknown = sorted(set(channel) - allowed)
    if unknown:
        raise SpecError(f"{channel_path} has unknown fields: {', '.join(unknown)}")

    name = _require_string(channel["name"], f"{channel_path}.name")
    source = _require_mapping(channel.get("source"), f"{channel_path}.source")
    if "command" not in source or source["command"] in (None, "", []):
        raise SpecError(f"{channel_path}.source.command is required")
    if _is_array_of_tables(source["command"]) and channel_schema != "current":
        raise SpecError(
            f"{channel_path}.source.command uses named commands, which require "
            "channelSchema=current; stable-0.14 accepts a string array"
        )

    requirements_value = channel.get("requirements", [])
    if not isinstance(requirements_value, list) or not all(
        isinstance(item, str) and item.strip() for item in requirements_value
    ):
        raise SpecError(f"{channel_path}.requirements must be a string array")
    requirements = {item.strip() for item in requirements_value}

    preview = channel.get("preview")
    if preview is not None:
        preview_mapping = _require_mapping(preview, f"{channel_path}.preview")
        preview_mapping, preset_requirements = _preview_from_preset(
            dict(preview_mapping), platform, channel_path
        )
        requirements.update(preset_requirements)
        preview = preview_mapping

    metadata: dict[str, Any] = {"name": name}
    description = channel.get("description")
    if description is not None:
        metadata["description"] = _require_string(description, f"{channel_path}.description")
    if requirements:
        metadata["requirements"] = sorted(requirements)

    document: dict[str, Any] = {}
    if "watch" in channel:
        watch = channel["watch"]
        if not isinstance(watch, (int, float)) or isinstance(watch, bool) or watch < 0:
            raise SpecError(f"{channel_path}.watch must be a non-negative number")
        document["watch"] = watch
    document["metadata"] = metadata
    document["source"] = source
    if preview is not None:
        document["preview"] = preview
    for section in ("ui", "history"):
        if section in channel:
            document[section] = _require_mapping(channel[section], f"{channel_path}.{section}")

    keybindings = dict(
        _require_mapping(channel.get("keybindings", {}), f"{channel_path}.keybindings")
    )
    actions = dict(_require_mapping(channel.get("actions", {}), f"{channel_path}.actions"))
    enter = channel.get("enter")
    if enter is not None:
        if index == len(names) - 1:
            raise SpecError(f"{channel_path}.enter is not allowed on the final channel")
        enter_mapping = _require_mapping(enter, f"{channel_path}.enter")
        target = _require_string(enter_mapping.get("to"), f"{channel_path}.enter.to")
        expected_target = names[index + 1]
        if target != expected_target:
            raise SpecError(
                f"{channel_path}.enter.to must target the immediately following channel {expected_target!r}"
            )
        command = _require_string(
            enter_mapping.get("command"), f"{channel_path}.enter.command"
        )
        association_context = command
        if "env" in enter_mapping:
            association_context += json.dumps(enter_mapping["env"], sort_keys=True)
        if not TEMPLATE_RE.search(association_context):
            raise SpecError(
                f"{channel_path}.enter must propagate a selected-row template in command or env"
            )
        if not re.search(rf"\btv(?:\.exe)?\s+{re.escape(target)}(?:\s|$)", command, re.IGNORECASE):
            raise SpecError(f"{channel_path}.enter.command must launch tv {target}")
        action_id = str(enter_mapping.get("action", "next"))
        if not CHANNEL_NAME_RE.fullmatch(action_id):
            raise SpecError(f"{channel_path}.enter.action is invalid")
        if "enter" in keybindings:
            raise SpecError(f"{channel_path} defines enter in both keybindings and enter")
        if action_id in actions:
            raise SpecError(f"{channel_path} action {action_id!r} conflicts with enter")
        mode = enter_mapping.get("mode", "fork")
        if mode not in {"fork", "execute"}:
            raise SpecError(f"{channel_path}.enter.mode must be fork or execute")
        action: dict[str, Any] = {
            "description": str(
                enter_mapping.get("description", f"Open associated channel {target}")
            ),
            "command": command,
            "mode": mode,
        }
        for optional in ("shell", "separator", "env", "interactive"):
            if optional in enter_mapping:
                action[optional] = enter_mapping[optional]
        keybindings["enter"] = f"actions:{action_id}"
        actions[action_id] = action

    if keybindings:
        document["keybindings"] = keybindings
    if actions:
        for action_name, action in actions.items():
            if not CHANNEL_NAME_RE.fullmatch(str(action_name)):
                raise SpecError(f"{channel_path}.actions has invalid id {action_name!r}")
            _require_mapping(action, f"{channel_path}.actions.{action_name}")
        document["actions"] = actions
    return document, requirements


def _toml_key(value: str) -> str:
    return value if BARE_TOML_KEY_RE.fullmatch(value) else json.dumps(value, ensure_ascii=False)


def _toml_value(value: Any, path: str) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return str(value).lower()
    if isinstance(value, list):
        if any(isinstance(item, (dict, list)) for item in value):
            raise SpecError(f"{path} contains a nested list or object where a scalar array is required")
        return "[" + ", ".join(_toml_value(item, path) for item in value) + "]"
    raise SpecError(f"{path} has unsupported TOML value {value!r}")


def _is_array_of_tables(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(isinstance(item, dict) for item in value)


def _render_table(path: tuple[str, ...], table: Mapping[str, Any], lines: list[str]) -> None:
    lines.append("[" + ".".join(_toml_key(part) for part in path) + "]")
    for key, value in table.items():
        if not isinstance(value, dict) and not _is_array_of_tables(value):
            lines.append(f"{_toml_key(str(key))} = {_toml_value(value, '.'.join((*path, str(key))))}")
    for key, value in table.items():
        child_path = (*path, str(key))
        if isinstance(value, dict):
            lines.append("")
            _render_table(child_path, value, lines)
        elif _is_array_of_tables(value):
            for item in value:
                lines.append("")
                lines.append("[[" + ".".join(_toml_key(part) for part in child_path) + "]]" )
                _render_table_body(child_path, item, lines)


def _render_table_body(path: tuple[str, ...], table: Mapping[str, Any], lines: list[str]) -> None:
    for key, value in table.items():
        if not isinstance(value, dict) and not _is_array_of_tables(value):
            lines.append(f"{_toml_key(str(key))} = {_toml_value(value, '.'.join((*path, str(key))))}")
    for key, value in table.items():
        child_path = (*path, str(key))
        if isinstance(value, dict):
            lines.append("")
            _render_table(child_path, value, lines)
        elif _is_array_of_tables(value):
            for item in value:
                lines.append("")
                lines.append("[[" + ".".join(_toml_key(part) for part in child_path) + "]]" )
                _render_table_body(child_path, item, lines)


def _render_toml(document: Mapping[str, Any]) -> str:
    lines: list[str] = []
    for key, value in document.items():
        if not isinstance(value, dict) and not _is_array_of_tables(value):
            lines.append(f"{_toml_key(str(key))} = {_toml_value(value, str(key))}")
    for key, value in document.items():
        if isinstance(value, dict):
            if lines:
                lines.append("")
            _render_table((str(key),), value, lines)
        elif _is_array_of_tables(value):
            for item in value:
                if lines:
                    lines.append("")
                lines.append(f"[[{_toml_key(str(key))}]]")
                _render_table_body((str(key),), item, lines)
    rendered = "\n".join(lines).rstrip() + "\n"
    tomllib.loads(rendered)
    return rendered


def _macos_installer(has_config: bool) -> str:
    config_copy = """
if [ "${INSTALL_TELEVISION_CONFIG:-0}" = "1" ]; then
  cp "$script_dir/config.toml" "$config_dir/config.toml"
fi
""" if has_config else ""
    return f"""#!/usr/bin/env sh
set -eu
script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
config_dir="${{TELEVISION_CONFIG:-${{XDG_CONFIG_HOME:-$HOME/.config}}/television}}"
cable_dir="$config_dir/cable"
mkdir -p "$cable_dir"
cp "$script_dir"/cable/*.toml "$cable_dir/"
{config_copy}tv list-channels
"""


def _windows_installer(has_config: bool) -> str:
    config_copy = """
if ($InstallConfig) {
    Copy-Item -Force (Join-Path $PSScriptRoot 'config.toml') (Join-Path $ConfigDir 'config.toml')
}
""" if has_config else ""
    return f"""param([switch]$InstallConfig)
$ErrorActionPreference = 'Stop'
if ($env:TELEVISION_CONFIG) {{
    $ConfigDir = $env:TELEVISION_CONFIG
}} elseif ($env:XDG_CONFIG_HOME) {{
    $ConfigDir = Join-Path $env:XDG_CONFIG_HOME 'television'
}} else {{
    $ConfigDir = Join-Path $env:LOCALAPPDATA 'television\\config'
}}
$CableDir = Join-Path $ConfigDir 'cable'
New-Item -ItemType Directory -Force -Path $CableDir | Out-Null
Get-ChildItem (Join-Path $PSScriptRoot 'cable\\*.toml') | Copy-Item -Destination $CableDir -Force
{config_copy}tv list-channels
"""


def _requirements_payload(required_by: Mapping[str, set[str]]) -> dict[str, Any]:
    tools: list[dict[str, Any]] = []
    for name in sorted(required_by):
        catalog = TOOL_CATALOG.get(name)
        tool: dict[str, Any] = {
            "name": name,
            "requiredByChannels": sorted(required_by[name]),
            "requiredForGeneratedCable": True,
        }
        if catalog:
            tool.update(catalog)
        else:
            tool.update(
                {
                    "purpose": "External command required by a generated channel",
                    "install": {},
                    "note": "Provide this command on PATH using its authoritative installation instructions.",
                }
            )
        tools.append(tool)
    return {"schemaVersion": 1, "tools": tools}


def _build_bundle(spec: Mapping[str, Any], platforms: tuple[str, ...]) -> dict[str, Any]:
    bundle, channel_schema, raw_channels = _validate_root(spec)
    names = [str(channel["name"]) for channel in raw_channels]
    rendered_platforms: dict[str, Any] = {}
    required_by: dict[str, set[str]] = {}
    for platform in platforms:
        config = spec.get("config")
        config_text = None
        if config is not None:
            resolved_config = _resolve_platform(config, platform, "config")
            config_text = _render_toml(_require_mapping(resolved_config, "config"))
        channels: dict[str, str] = {}
        for index, raw_channel in enumerate(raw_channels):
            normalized, requirements = _normalize_channel(
                raw_channel, platform, index, names, channel_schema
            )
            channel_name = str(normalized["metadata"]["name"])
            channels[f"{channel_name}.toml"] = _render_toml(normalized)
            for requirement in requirements:
                required_by.setdefault(requirement, set()).add(channel_name)
        rendered_platforms[platform] = {
            "config": config_text,
            "channels": channels,
            "installer": _macos_installer(config_text is not None)
            if platform == "macos"
            else _windows_installer(config_text is not None),
        }
    return {
        "bundle": bundle,
        "channelSchema": channel_schema,
        "platforms": rendered_platforms,
        "requirements": _requirements_payload(required_by),
    }


def _manifest(bundle: Mapping[str, Any]) -> dict[str, Any]:
    platform_manifest: dict[str, Any] = {}
    for platform, artifacts in bundle["platforms"].items():
        platform_manifest[platform] = {
            "config": f"{platform}/config.toml" if artifacts["config"] is not None else None,
            "cables": [
                f"{platform}/cable/{name}" for name in sorted(artifacts["channels"])
            ],
            "installer": f"{platform}/install.{'sh' if platform == 'macos' else 'ps1'}",
        }
    return {
        "schemaVersion": 1,
        "bundle": bundle["bundle"],
        "channelSchema": bundle["channelSchema"],
        "platforms": platform_manifest,
        "requirements": "requirements.json",
    }


def _write_bundle(bundle: Mapping[str, Any], output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    for platform, artifacts in bundle["platforms"].items():
        platform_dir = output / platform
        cable_dir = platform_dir / "cable"
        cable_dir.mkdir(parents=True, exist_ok=True)
        if artifacts["config"] is not None:
            (platform_dir / "config.toml").write_text(artifacts["config"], encoding="utf-8")
        for filename, content in artifacts["channels"].items():
            (cable_dir / filename).write_text(content, encoding="utf-8")
        extension = "sh" if platform == "macos" else "ps1"
        (platform_dir / f"install.{extension}").write_text(
            artifacts["installer"], encoding="utf-8", newline="\n"
        )
    (output / "requirements.json").write_text(
        json.dumps(bundle["requirements"], indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (output / "manifest.json").write_text(
        json.dumps(_manifest(bundle), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main(argv: Sequence[str] | None = None) -> int:
    """Run the Television bundle generator command-line interface."""

    args = _parse_args(argv)
    try:
        spec = _load_spec(args.spec)
        bundle = _build_bundle(spec, _requested_platforms(args.platform))
        summary = _manifest(bundle)
        summary["validatedTomlFiles"] = sum(
            len(artifacts["channels"]) + (1 if artifacts["config"] is not None else 0)
            for artifacts in bundle["platforms"].values()
        )
        if args.check:
            print(json.dumps(summary, indent=2, sort_keys=True))
            return 0
        _write_bundle(bundle, args.output)
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0
    except (OSError, SpecError, tomllib.TOMLDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
