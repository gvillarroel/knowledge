from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from tika_mallet_test_support import REPO_ROOT, build_portable_bundle, tree_hashes


SKILL_ROOT = REPO_ROOT / "skills" / "consult-semantic-okf-tika-mallet-bounded"
SCRIPT = SKILL_ROOT / "scripts" / "bounded_answer.py"
EVIDENCE_FIELDS = {
    "source_id",
    "record_id",
    "concept_path",
    "source_path",
    "record_sha256",
    "locator",
    "text_sha256",
}


@pytest.fixture(scope="module")
def bundle(tmp_path_factory: pytest.TempPathFactory) -> Path:
    output, *_ = build_portable_bundle(
        tmp_path_factory.mktemp("consult-tika-mallet-bounded")
    )
    return output


def run_bounded(
    bundle_path: Path,
    output: Path,
    *,
    minimum_sources: int,
    maximum_sources: int,
) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment.pop("PYTHONPATH", None)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run(
        [
            sys.executable,
            "-B",
            str(SCRIPT),
            str(bundle_path),
            "--question-id",
            "q999",
            "--question",
            "Compare audit evidence extraction and spreadsheet validation.",
            "--query",
            "audit evidence extraction",
            "--query",
            "spreadsheet validation",
            "--query",
            "document controls",
            "--mode",
            "fusion",
            "--top-k",
            "6",
            "--minimum-sources",
            str(minimum_sources),
            "--max-sources",
            str(maximum_sources),
            "--output",
            str(output),
        ],
        cwd=SKILL_ROOT,
        env=environment,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=60,
        check=False,
    )


def test_bounded_skill_is_standalone_and_low_freedom() -> None:
    skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
    metadata = yaml.safe_load(skill.split("---", 2)[1])
    package_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in SKILL_ROOT.rglob("*")
        if path.is_file() and path.suffix in {".md", ".py", ".yaml"}
    )

    assert metadata["name"] == "consult-semantic-okf-tika-mallet-bounded"
    assert set(metadata) == {"name", "description"}
    assert "exactly one compiler invocation" in skill
    assert "Do not list, search, grep, or read `/knowledge` directly." in skill
    assert "TODO" not in package_text
    assert "$consult-semantic-okf-tika-mallet-bounded" in (
        SKILL_ROOT / "agents" / "openai.yaml"
    ).read_text(encoding="utf-8")
    assert (SKILL_ROOT / "scripts" / "_tika_mallet_snapshot.py").is_file()
    assert "consult-semantic-okf-tika-mallet/" not in package_text
    assert SKILL_ROOT.parent == REPO_ROOT / "skills"
    assert not (REPO_ROOT / "okf").exists()


def test_bounded_compiler_emits_closed_source_diverse_answer(
    bundle: Path,
    tmp_path: Path,
) -> None:
    before = tree_hashes(bundle)
    output = tmp_path / "answer.json"
    completed = run_bounded(
        bundle,
        output,
        minimum_sources=2,
        maximum_sources=2,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
    answer = json.loads(completed.stdout)
    assert json.loads(output.read_text(encoding="utf-8")) == answer
    assert list(answer) == ["question_id", "answer", "evidence"]
    assert answer["question_id"] == "q999"
    assert list(answer["answer"]) == ["summary", "claims"]
    assert len(answer["answer"]["summary"].split()) <= 450
    assert len(answer["answer"]["claims"]) == len(answer["evidence"]) == 2
    assert [
        claim["evidence_indices"]
        for claim in answer["answer"]["claims"]
    ] == [[0], [1]]
    assert all(set(row) == EVIDENCE_FIELDS for row in answer["evidence"])
    assert len({row["source_id"] for row in answer["evidence"]}) == 2
    assert tree_hashes(bundle) == before

    repeated = run_bounded(
        bundle,
        output,
        minimum_sources=2,
        maximum_sources=2,
    )
    assert repeated.returncode == 2
    assert "refusing to overwrite" in json.loads(repeated.stderr)["error"]
    assert tree_hashes(bundle) == before


def test_bounded_compiler_returns_closed_null_when_diversity_is_insufficient(
    bundle: Path,
    tmp_path: Path,
) -> None:
    output = tmp_path / "null-answer.json"
    completed = run_bounded(
        bundle,
        output,
        minimum_sources=3,
        maximum_sources=3,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert json.loads(completed.stdout) == {
        "question_id": "q999",
        "answer": None,
        "evidence": [],
    }


def test_bounded_compiler_rejects_output_inside_snapshot(
    bundle: Path,
) -> None:
    completed = run_bounded(
        bundle,
        bundle / "forbidden-answer.json",
        minimum_sources=2,
        maximum_sources=2,
    )

    assert completed.returncode == 2
    assert "inside the snapshot" in json.loads(completed.stderr)["error"]
    assert not (bundle / "forbidden-answer.json").exists()
