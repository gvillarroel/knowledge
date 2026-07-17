#!/usr/bin/env python3
"""Create a narrow append-only retry config from validated Skill Arena prompts."""

from __future__ import annotations

import argparse
from pathlib import Path

import yaml


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--prompt-id", action="append", required=True)
    parser.add_argument("--suffix", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(f"Refusing to replace retry config: {args.output}")
    config = yaml.safe_load(args.config.read_text(encoding="utf-8"))
    prompts = config.get("task", {}).get("prompts", [])
    by_id = {prompt.get("id"): prompt for prompt in prompts if isinstance(prompt, dict)}
    if len(set(args.prompt_id)) != len(args.prompt_id):
        raise ValueError("Retry prompt IDs must be unique")
    missing = [prompt_id for prompt_id in args.prompt_id if prompt_id not in by_id]
    if missing:
        raise ValueError("Unknown retry prompt IDs: " + ", ".join(missing))
    config["benchmark"]["id"] = f"{config['benchmark']['id']}-{args.suffix}"
    config["benchmark"]["description"] = (
        f"Append-only retry {args.suffix} for transient execution failures in an already validated paired benchmark."
    )
    config["benchmark"]["tags"] = [*config["benchmark"].get("tags", []), "retry", args.suffix]
    config["task"]["prompts"] = [by_id[prompt_id] for prompt_id in args.prompt_id]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        yaml.safe_dump(config, allow_unicode=True, sort_keys=False, width=120),
        encoding="utf-8",
        newline="\n",
    )
    print(f"{args.output}: {len(args.prompt_id)} retry prompts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
