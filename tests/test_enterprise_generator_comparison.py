"""Check the public comparator against real tiny experts and invalid evidence."""
from __future__ import annotations

import importlib.util
from contextlib import ExitStack
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

REPO = Path(__file__).resolve().parents[1]


@pytest.fixture
def comparison(monkeypatch):
    root = REPO / "evaluations/enterprise-rag-bench"
    monkeypatch.syspath_prepend(str(root))
    spec = importlib.util.spec_from_file_location("enterprise_generator_test", root / "compare_generator_versions.py")
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def question(**changes):
    return {"id": "example-question", "question": "Which project approved the migration?",
            "relevant": ["mail-1"], "category": "basic", "cohort": "development", **changes}


@pytest.mark.parametrize("changes", [
    {"relevant": ["unknown"]}, {"relevant": ["mail-1", "mail-1"]},
    {"relevant": [True]}, {"question": " "}, {"category": None},
])
def test_invalid_questions_fail_before_measurement(comparison, changes):
    with pytest.raises(ValueError, match="Invalid or unresolved"):
        comparison.validate_questions([question(**changes)], {"mail-1": {}})


def test_repeated_questions_are_not_independent_evidence(comparison):
    with pytest.raises(ValueError, match="Duplicate question"):
        comparison.validate_questions([question(), question()], {"mail-1": {}})


def test_result_writes_preserve_existing_evidence_and_reject_nonfinite_values(comparison, tmp_path):
    path = tmp_path / "receipt.json"
    comparison.write_once(path, {"status": "pass"})
    original = path.read_bytes()
    with pytest.raises(FileExistsError):
        comparison.write_once(path, {"status": "replaced"})
    assert path.read_bytes() == original
    bad = tmp_path / "invalid.json"
    with pytest.raises(ValueError):
        comparison.write_once(bad, {"metric": float("nan")})
    assert not bad.exists()


def test_turso_sidecars_stay_in_a_disposable_working_copy(comparison, tmp_path):
    database = tmp_path / "knowledge.db"
    database.write_bytes(b"Immutable published database fixture")
    opened = []
    closed = []

    def state(path):
        return {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                for p in (path, Path(str(path) + "-wal")) if p.exists()}

    def connect(path):
        assert path != database and path.read_bytes() == database.read_bytes()
        Path(str(path) + "-wal").write_bytes(b"Engine connection sidecar")
        opened.append(path)
        return SimpleNamespace(close=lambda: closed.append(True))

    runtime = SimpleNamespace(database_file_state=state, connect_read_only=connect,
                              require_valid_database=lambda connection, full: None)
    original = state(database)
    with ExitStack() as stack:
        comparison.turso_connection(database, runtime, stack)
        assert opened[0].exists()
        assert state(database) == original
    assert closed == [True] and not opened[0].parent.exists()
    assert state(database) == original
    Path(str(database) + "-wal").write_bytes(b"Unquiescent release")
    with ExitStack() as stack, pytest.raises(ValueError, match="active sidecars"):
        comparison.turso_connection(database, runtime, stack)
    assert len(opened) == 1


def test_real_fulltext_expert_retrieval_and_source_fidelity(comparison, tmp_path):
    dataset = comparison.module("enterprise_comparator_fixture", REPO / "evaluations/enterprise-rag-bench/dataset_tool.py")
    source = tmp_path / "source"
    (source / "documents").mkdir(parents=True)
    manifest = comparison.fidelity.fulltext_manifest(dataset.manifest(["gmail"], "synthetic"))
    comparison.fidelity.write_json(source / "manifest.json", manifest)
    records = [
        {"id": "mail-1", "title": "Approved migration", "body": "Project Kestrel approved the database migration."},
        {"id": "mail-2", "title": "Office notice", "body": "Office refreshments are available on Monday."},
    ]
    (source / "documents/gmail.jsonl").write_text("\n".join(json.dumps(r) for r in records) + "\n", encoding="utf-8")
    (source / "guidance.md").write_text(
        "# Archived email evidence\n\n## Scope\nRead archived enterprise email.\n\n"
        "## Application workflow\nSearch and read the original supporting records.\n\n"
        "## Decision rules\nDistinguish proposed changes from approved decisions.\n\n"
        "## Evidence and limits\nCite exact source evidence and state missing information.\n", encoding="utf-8")
    expert = tmp_path / "enterprise-expert"
    before = comparison.fidelity.tree_hashes(source)
    built = comparison.build(SimpleNamespace(input=source, family="legacy", expert=expert,
        generator=REPO / "skills/build-semantic-okf-knowledge-skill", plan=None, output=tmp_path / "build.json"))
    assert built["source_fidelity"]["all_source_bodies_exact"]
    assert built["source_fidelity"]["records"] == 2
    assert comparison.fidelity.tree_hashes(source) == before
    helpers = tmp_path / "helpers"
    helpers.mkdir()
    for name, original in {
        "evaluate_all_routes.py": REPO / "evaluations/private-book-strategy-comparison/scripts/evaluate_all_routes.py",
        "compare_retrieval.py": REPO / "evaluations/semantic-okf-embeddings/scripts/compare_retrieval.py",
    }.items():
        (helpers / name).write_bytes(original.read_bytes())
    questions = tmp_path / "questions.json"
    comparison.write_once(questions, [question(question="Project Kestrel database migration")])
    measured = comparison.score(SimpleNamespace(expert=expert, family="legacy", questions=questions, helpers=helpers))
    assert measured["expert_unchanged"]
    assert len(measured["routes"]) == 1
    route = measured["routes"][0]
    assert route["metrics"]["ndcg_at_10"] == 1
    assert route["categories"]["basic"]["question_count"] == 1
    assert "query_stability_ratio" not in route
    assert route["replicates"][0]["queries"][0]["hits"][0]["record_id"] == "mail-1"
