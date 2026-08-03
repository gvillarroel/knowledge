from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ADAPTER = (
    ROOT
    / "evaluations/semantic-okf-tika-mallet-tantivy/scripts"
    / "run_trace_distillation.py"
)


def test_adapter_preserves_every_skill_as_a_string_before_harbor_create() -> None:
    source = ADAPTER.read_text(encoding="utf-8")

    assert "module.candidate_job_config = candidate_job_config" in source
    assert '[str(skill) for skill in agent.skills]' in source
    assert 'harbor==0.18.0' in source
