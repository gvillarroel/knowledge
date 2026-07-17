"""Tests for the standalone Television skill package and bundle generator."""

from __future__ import annotations

import json
import subprocess
import sys
import tomllib
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPO_ROOT / "skills" / "television"
GENERATOR = SKILL_ROOT / "scripts" / "generate_bundle.py"
EVALUATION_ROOT = REPO_ROOT / "evaluations" / "television"


def _three_level_spec() -> dict[str, object]:
    """Return a representative cross-platform bundle specification."""

    return {
        "bundle": "catalog-browser",
        "channelSchema": "stable-0.14",
        "config": {
            "default_channel": "accounts",
            "history_size": 100,
            "ui": {
                "theme": {
                    "by_platform": {"macos": "nord-dark", "windows": "dracula"}
                },
                "orientation": "landscape",
            },
        },
        "channels": [
            {
                "name": "accounts",
                "description": "Select an account",
                "requirements": ["tv", "catalogctl"],
                "watch": 5,
                "source": {
                    "command": [
                        "catalogctl accounts --active --format tsv",
                        "catalogctl accounts --format tsv",
                    ],
                    "output": "{split:\\t:0}",
                    "no_sort": True,
                },
                "preview": {"preset": "json", "target": "{split:\\t:0}"},
                "ui": {"preview_panel": {"size": 60, "header": "Account {split:\\t:0}"}},
                "enter": {
                    "to": "account-projects",
                    "command": "tv account-projects",
                    "env": {"TV_ACCOUNT_ID": "{split:\\t:0}"},
                    "mode": "fork",
                },
            },
            {
                "name": "account-projects",
                "description": "Select a project",
                "requirements": ["tv", "catalogctl"],
                "source": {
                    "command": {
                        "by_platform": {
                            "macos": "catalogctl projects --account '$TV_ACCOUNT_ID' --format tsv",
                            "windows": "catalogctl projects --account '$env:TV_ACCOUNT_ID' --format tsv",
                        }
                    },
                    "output": "{split:\\t:0}",
                },
                "enter": {
                    "to": "project-datasets",
                    "command": "tv project-datasets",
                    "env": {"TV_PROJECT_ID": "{split:\\t:0}"},
                    "mode": "fork",
                },
            },
            {
                "name": "project-datasets",
                "description": "Select a dataset",
                "requirements": ["catalogctl"],
                "source": {
                    "command": {
                        "by_platform": {
                            "macos": "catalogctl datasets --project '$TV_PROJECT_ID' --format tsv",
                            "windows": "catalogctl datasets --project '$env:TV_PROJECT_ID' --format tsv",
                        }
                    },
                    "output": "{split:\\t:0}",
                },
                "preview": {"preset": "csv", "target": "{split:\\t:1}"},
            },
        ],
    }


def _run_generator(spec_path: Path, *args: str) -> subprocess.CompletedProcess[str]:
    """Run the copied-package-safe generator and capture its result."""

    return subprocess.run(
        [sys.executable, str(GENERATOR), str(spec_path), *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=30,
        check=False,
    )


def test_generator_emits_valid_macos_and_windows_three_level_bundle(tmp_path: Path) -> None:
    spec_path = tmp_path / "bundle.json"
    output = tmp_path / "generated"
    spec_path.write_text(json.dumps(_three_level_spec()), encoding="utf-8")

    completed = _run_generator(spec_path, "--output", str(output))

    assert completed.returncode == 0, completed.stderr
    summary = json.loads(completed.stdout)
    assert summary["validatedTomlFiles"] == 8
    assert len(summary["platforms"]["macos"]["cables"]) == 3
    assert len(summary["platforms"]["windows"]["cables"]) == 3

    mac_config = tomllib.loads((output / "macos" / "config.toml").read_text(encoding="utf-8"))
    win_config = tomllib.loads((output / "windows" / "config.toml").read_text(encoding="utf-8"))
    assert mac_config["default_channel"] == "accounts"
    assert mac_config["ui"]["theme"] == "nord-dark"
    assert win_config["ui"]["theme"] == "dracula"

    mac_accounts = tomllib.loads(
        (output / "macos" / "cable" / "accounts.toml").read_text(encoding="utf-8")
    )
    win_accounts = tomllib.loads(
        (output / "windows" / "cable" / "accounts.toml").read_text(encoding="utf-8")
    )
    final_channel = tomllib.loads(
        (output / "windows" / "cable" / "project-datasets.toml").read_text(
            encoding="utf-8"
        )
    )
    assert mac_accounts["source"]["command"] == [
        "catalogctl accounts --active --format tsv",
        "catalogctl accounts --format tsv",
    ]
    assert mac_accounts["watch"] == 5
    assert mac_accounts["keybindings"]["enter"] == "actions:next"
    assert mac_accounts["actions"]["next"]["mode"] == "fork"
    assert mac_accounts["actions"]["next"]["env"] == {
        "TV_ACCOUNT_ID": "{split:\\t:0}"
    }
    assert win_accounts["actions"]["next"]["env"] == {
        "TV_ACCOUNT_ID": "{split:\\t:0}"
    }
    assert "account-projects" in win_accounts["actions"]["next"]["command"]
    assert "enter" not in final_channel.get("keybindings", {})
    assert "mlr" in final_channel["metadata"]["requirements"]
    assert "--icsv" in final_channel["preview"]["command"]

    requirements = json.loads((output / "requirements.json").read_text(encoding="utf-8"))
    tools = {tool["name"]: tool for tool in requirements["tools"]}
    assert {"catalogctl", "jq", "mlr", "tv"} <= set(tools)
    assert tools["mlr"]["purpose"] == "CSV and TSV table preview"
    assert "brew install miller" in tools["mlr"]["install"]["macos"]
    assert "winget install Miller.Miller" in tools["mlr"]["install"]["windows"]

    mac_installer = (output / "macos" / "install.sh").read_text(encoding="utf-8")
    win_installer = (output / "windows" / "install.ps1").read_text(encoding="utf-8")
    assert "TELEVISION_CONFIG" in mac_installer
    assert "XDG_CONFIG_HOME" in mac_installer
    assert "INSTALL_TELEVISION_CONFIG" in mac_installer
    assert "LOCALAPPDATA" in win_installer
    assert "television\\config" in win_installer
    assert "[switch]$InstallConfig" in win_installer


def test_generator_check_validates_without_writing(tmp_path: Path) -> None:
    spec_path = tmp_path / "bundle.json"
    spec_path.write_text(json.dumps(_three_level_spec()), encoding="utf-8")

    completed = _run_generator(spec_path, "--check", "--platform", "macos")

    assert completed.returncode == 0, completed.stderr
    summary = json.loads(completed.stdout)
    assert set(summary["platforms"]) == {"macos"}
    assert summary["validatedTomlFiles"] == 4
    assert list(tmp_path.iterdir()) == [spec_path]


def test_generator_rejects_more_than_three_channels(tmp_path: Path) -> None:
    spec = _three_level_spec()
    spec["channels"].append(
        {"name": "fourth", "source": {"command": "printf fourth"}}
    )
    spec_path = tmp_path / "four-level.json"
    spec_path.write_text(json.dumps(spec), encoding="utf-8")

    completed = _run_generator(spec_path, "--check")

    assert completed.returncode == 2
    assert "between one and three" in completed.stderr


def test_generator_rejects_unassociated_or_skipped_enter_target(tmp_path: Path) -> None:
    spec = _three_level_spec()
    spec["channels"][0]["enter"] = {
        "to": "project-datasets",
        "command": "tv project-datasets",
    }
    spec_path = tmp_path / "skipped-level.json"
    spec_path.write_text(json.dumps(spec), encoding="utf-8")

    completed = _run_generator(spec_path, "--check")

    assert completed.returncode == 2
    assert "immediately following channel" in completed.stderr


def test_generator_version_gates_named_source_commands(tmp_path: Path) -> None:
    spec = {
        "bundle": "named-sources",
        "channels": [
            {
                "name": "incidents",
                "source": {
                    "command": [
                        {"name": "Active", "run": "incidentctl list --active"},
                        {"name": "All", "run": "incidentctl list"},
                    ]
                },
            }
        ],
    }
    spec_path = tmp_path / "named.json"
    spec_path.write_text(json.dumps(spec), encoding="utf-8")

    stable = _run_generator(spec_path, "--check")
    assert stable.returncode == 2
    assert "channelSchema=current" in stable.stderr

    spec["channelSchema"] = "current"
    spec_path.write_text(json.dumps(spec), encoding="utf-8")
    output = tmp_path / "current"
    current = _run_generator(spec_path, "--output", str(output), "--platform", "macos")
    assert current.returncode == 0, current.stderr
    cable = tomllib.loads(
        (output / "macos" / "cable" / "incidents.toml").read_text(encoding="utf-8")
    )
    assert [command["name"] for command in cable["source"]["command"]] == ["Active", "All"]


def test_skill_routes_complete_capabilities_to_package_references() -> None:
    skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")

    for reference in (
        "bundle-spec.md",
        "channel-capabilities.md",
        "diagnostics.md",
        "know-backed-channels.md",
        "platforms-and-chains.md",
        "previews-and-tools.md",
    ):
        assert f"references/{reference}" in skill
        assert (SKILL_ROOT / "references" / reference).is_file()
    assert "scripts/generate_bundle.py" in skill
    assert "between one and three" not in skill  # Keep detailed schema in the reference.
    assert "up to three" in skill
    assert "CSV" in skill
    assert "macOS" in skill and "Windows" in skill
    assert "know search arxiv" in skill
    assert "television-preview --entry '{}'" in skill
    assert "source-metadata.yaml" in skill


def test_diagnostic_reference_names_exact_path_inputs() -> None:
    diagnostics = (SKILL_ROOT / "references" / "diagnostics.md").read_text(
        encoding="utf-8"
    )

    for variable in ("TELEVISION_CONFIG", "XDG_CONFIG_HOME", "LOCALAPPDATA", "HOME"):
        assert variable in diagnostics
    assert "$HOME/.config/television" in diagnostics
    assert "$env:LOCALAPPDATA\\television\\config" in diagnostics
    assert "tv --cable-dir" in diagnostics
    assert "exit code, stdout" in diagnostics


def test_television_evaluation_qualities_cover_declared_surface() -> None:
    coverage = json.loads(
        (EVALUATION_ROOT / "prompt-coverage.json").read_text(encoding="utf-8")
    )
    required = set(coverage["policy"]["requiredQualities"])
    covered = {
        quality for case in coverage["cases"] for quality in case.get("qualities", [])
    }

    assert covered == required
    assert {
        "macos-generation",
        "windows-generation",
        "three-level-chain",
        "csv-preview",
        "heterogeneous-previews",
        "dependency-guidance",
    } <= covered
