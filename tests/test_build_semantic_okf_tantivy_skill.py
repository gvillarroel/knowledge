from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPO_ROOT / "skills" / "build-semantic-okf-tantivy"
SCRIPTS = SKILL_ROOT / "scripts"


def load_retrieval_module():
    sys.path.insert(0, str(SCRIPTS))
    try:
        name = "test_tantivy_dedicated_builder_retrieval"
        spec = importlib.util.spec_from_file_location(
            name,
            SCRIPTS / "_classical_retrieval.py",
        )
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
        return module
    finally:
        sys.path.remove(str(SCRIPTS))


def test_dedicated_builder_is_standalone_and_bound_to_frozen_consult() -> None:
    skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
    metadata = yaml.safe_load(skill.split("---", 2)[1])
    entrypoint = (SCRIPTS / "build_semantic_okf_tantivy.py").read_text(
        encoding="utf-8"
    )
    validator = (SCRIPTS / "validate_semantic_okf_tantivy.py").read_text(
        encoding="utf-8"
    )

    assert set(metadata) == {"name", "description"}
    assert metadata["name"] == "build-semantic-okf-tantivy"
    assert "## Frozen-consumer boundary" in skill
    assert "Do not import or execute a sibling skill" in skill
    assert "$build-semantic-okf-tantivy" in (
        SKILL_ROOT / "agents" / "openai.yaml"
    ).read_text(encoding="utf-8")
    assert "Run one atomic Tantivy-compatible Semantic OKF build" in entrypoint
    assert "_build_semantic_okf_core" in entrypoint
    assert "_classical_retrieval" in entrypoint
    assert "Validate one published Tantivy-compatible bundle" in validator
    assert "build-semantic-okf-classical" not in entrypoint + validator
    assert (SKILL_ROOT / "references" / "tantivy-consumer-contract.md").is_file()


def test_projection_serializers_force_utf8_lf_bytes(tmp_path: Path) -> None:
    module = load_retrieval_module()
    json_path = tmp_path / "artifact.json"
    jsonl_path = tmp_path / "artifact.jsonl"

    module._write_json(json_path, {"title": "café", "rows": [1, 2]})
    module._write_jsonl(jsonl_path, [{"title": "café"}, {"title": "graph"}])

    for path in (json_path, jsonl_path):
        payload = path.read_bytes()
        assert payload.endswith(b"\n")
        assert b"\r\n" not in payload
        assert "café" in payload.decode("utf-8")


def test_long_non_paper_records_add_one_exact_overview_passage() -> None:
    module = load_retrieval_module()
    overview = "A" * module.LONG_RECORD_MIN_CHARS
    body = f"{overview}\n\n## Details\nExact supporting evidence."

    assert module._passage_ranges({"body": body}) == [
        (0, len(body)),
        (0, len(overview)),
    ]
    assert module._passage_ranges({"body": "Short.\n\n## Details\nMore."}) == [
        (0, len("Short.\n\n## Details\nMore.")),
    ]

    paper = "Preamble\n\n## PDF page 1\nFirst\n\n## PDF page 2\nSecond"
    second_page = paper.index("## PDF page 2")
    assert module._passage_ranges({"body": paper}) == [
        (0, len(paper[:second_page].rstrip())),
        (second_page, len(paper)),
    ]


def test_package_local_runtime_smoke_passes() -> None:
    completed = subprocess.run(
        [sys.executable, str(SCRIPTS / "runtime_smoke.py")],
        cwd=SKILL_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=30,
        check=False,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["status"] == "pass"
    assert payload["model_required"] is False
    assert set(payload["packages"]) == {"pyshacl", "rdflib", "yaml"}
