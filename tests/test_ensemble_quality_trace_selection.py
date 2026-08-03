"""Tests for frozen Ensemble quality/trace fusion selection."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
SELECTOR_PATH = (
    REPO_ROOT
    / "evaluations"
    / "semantic-okf-specialized-experts"
    / "scripts"
    / "select_ensemble_quality_trace_fusion.py"
)


def _load_selector() -> object:
    specification = importlib.util.spec_from_file_location(
        "test_ensemble_quality_trace_selector",
        SELECTOR_PATH,
    )
    assert specification is not None
    assert specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


def test_trace_fusion_ignores_ranks_beyond_the_frozen_candidate_budget() -> None:
    """A trace-only rank eleven cannot change the protected quality ordering."""

    selector = _load_selector()
    quality = [f"paper-{index:02d}" for index in range(1, 11)]
    trace = [
        "paper-20",
        "paper-19",
        "paper-18",
        "paper-17",
        "paper-16",
        "paper-15",
        "paper-14",
        "paper-13",
        "paper-12",
        "paper-11",
        "paper-10",
    ]

    ranking = selector._candidate_ranking(
        quality,
        trace,
        scope="protected",
        rrf_k=0,
        quality_weight=1,
        trace_weight=10,
    )

    assert ranking == quality


def test_union_fusion_uses_only_the_first_ten_trace_candidates() -> None:
    """Union scope never introduces a trace result below rank ten."""

    selector = _load_selector()
    quality = [f"quality-{index:02d}" for index in range(1, 11)]
    trace = [f"trace-{index:02d}" for index in range(1, 12)]

    ranking = selector._candidate_ranking(
        quality,
        trace,
        scope="union",
        rrf_k=0,
        quality_weight=1,
        trace_weight=10,
    )

    assert "trace-11" not in ranking
    assert ranking[0] == "trace-01"
