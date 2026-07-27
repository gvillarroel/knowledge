#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = ["harbor==0.18.0", "PyYAML>=6,<7"]
# ///
"""Run trace distillation while preserving mixed static and staged skills."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from typing import Any


def _load(path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location("harbor_trace_distiller", path)
    if spec is None or spec.loader is None:
        raise SystemExit(f"cannot load trace distiller: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> None:
    if len(sys.argv) < 3:
        raise SystemExit(
            "usage: run_trace_distillation_multiskill.py DISTILLER CONFIG [OPTIONS]"
        )
    distiller = Path(sys.argv[1]).expanduser().resolve()
    module = _load(distiller)
    original = module.candidate_job_config

    def candidate_job_config(*args: Any, **kwargs: Any) -> Any:
        config = original(*args, **kwargs)
        agents = [
            agent.model_copy(
                update={"skills": [str(skill) for skill in agent.skills]}
            )
            for agent in config.agents
        ]
        return config.model_copy(update={"agents": agents})

    module.candidate_job_config = candidate_job_config
    sys.argv = [str(distiller), *sys.argv[2:]]
    module.main()


if __name__ == "__main__":
    main()
