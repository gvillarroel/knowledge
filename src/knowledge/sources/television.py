from __future__ import annotations

import json
import shlex
from pathlib import Path

from .base import SourceAdapter


class TelevisionSource(SourceAdapter):
    """Adapter that generates Television channel definitions for ``tv``."""

    def sync(self) -> dict[str, object]:
        self.clear_source_dir()

        channel_name = self.config.get("channel") or self.source["title"]
        channel_slug = self.source["id"].removeprefix("television-")
        channel_path = self.raw_dir / f"{channel_slug}.toml"

        self.write_text(channel_path, self._build_channel_toml(channel_name))

        return self.finalize_sync(
            {
                "channel": channel_name,
                "files": 1,
                "channel_file": str(channel_path),
            }
        )

    def _build_channel_toml(self, channel_name: str) -> str:
        lines = [
            "[metadata]",
            f'name = "{_escape_toml(channel_name)}"',
            f'description = "{_escape_toml(self.config.get("description") or "")}"',
            "",
            "[source]",
            f'command = "{_escape_toml(self.config["source_command"])}"',
        ]
        source_display = self.config.get("source_display")
        if source_display:
            lines.append(f'display = "{_escape_toml(source_display)}"')
        preview_command = self.config.get("preview_command")
        if preview_command:
            lines.extend(
                [
                    "",
                    "[preview]",
                    f'command = "{_escape_toml(preview_command)}"',
                ]
            )
        action_command = self.config.get("action_command")
        if action_command:
            lines.extend(
                [
                    "",
                    "[keybindings]",
                    'ctrl-o = "actions:open"',
                    "",
                    "[actions.open]",
                    f'command = "{_escape_toml(action_command)}"',
                    'mode = "execute"',
                ]
            )
        return "\n".join(lines) + "\n"

    def _build_command_manifest(self, channel_name: str, channel_path: Path) -> dict[str, str]:
        cable_path = f"~/.config/television/cable/{channel_path.name}"
        quoted_channel_path = _shell_quote(str(channel_path))
        return {
            "sync": self.source["update_command"],
            "install_unix": f"mkdir -p ~/.config/television/cable && cp {quoted_channel_path} {cable_path}",
            "install_powershell": (
                "New-Item -ItemType Directory -Force -Path "
                "$HOME/.config/television/cable | Out-Null; "
                f'Copy-Item -Force "{channel_path}" "$HOME/.config/television/cable/{channel_path.name}"'
            ),
            "run_after_install": f"tv {channel_name}",
            "run_inline": self._build_inline_run_command(),
        }

    def _build_inline_run_command(self) -> str:
        parts = ["tv", f"--source-command={_shell_quote(self.config['source_command'])}"]
        source_display = self.config.get("source_display")
        if source_display:
            parts.append(f"--source-display={_shell_quote(source_display)}")
        preview_command = self.config.get("preview_command")
        if preview_command:
            parts.append(f"--preview-command={_shell_quote(preview_command)}")
        return " ".join(parts)

def _escape_toml(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def _shell_quote(value: str) -> str:
    return shlex.quote(value)
