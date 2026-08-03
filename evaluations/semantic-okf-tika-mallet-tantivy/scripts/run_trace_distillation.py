#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = ["harbor==0.18.0", "PyYAML>=6,<7"]
# ///
"""Run Harbor trace distillation with a Harbor 0.18 multi-skill path adapter."""

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from typing import Any, Sequence


def _load_distiller(path: Path) -> ModuleType:
    specification = importlib.util.spec_from_file_location(
        "installed_harbor_trace_distillation",
        path,
    )
    if specification is None or specification.loader is None:
        raise RuntimeError(f"cannot load Harbor trace distiller: {path}")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def _install_multiskill_adapter(module: ModuleType) -> None:
    """Keep the staged candidate when Harbor resolves remaining string skills."""

    original = module.candidate_job_config

    def candidate_job_config(
        source: Any,
        *,
        baseline_skill: Path,
        candidate_skill: Path,
    ) -> Any:
        candidate = original(
            source,
            baseline_skill=baseline_skill,
            candidate_skill=candidate_skill,
        )
        agents = [
            agent.model_copy(
                update={"skills": [str(skill) for skill in agent.skills]}
            )
            for agent in candidate.agents
        ]
        return candidate.model_copy(update={"agents": agents})

    module.candidate_job_config = candidate_job_config


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--distiller", type=Path, required=True)
    arguments, remaining = parser.parse_known_args(argv)
    distiller = arguments.distiller.resolve()
    if not distiller.is_file():
        raise SystemExit(f"Harbor trace distiller is absent: {distiller}")

    module = _load_distiller(distiller)
    _install_multiskill_adapter(module)
    sys.argv = [str(Path(__file__).resolve()), *remaining]
    module.main()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
