from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest


REPO = Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "evaluations" / "semantic-okf-endocrine-hygiene" / "scripts"
RETRIEVAL_HELPERS = SCRIPTS / "_retrieval_eval.py"
EVALUATOR = SCRIPTS / "evaluate_retrieval.py"


def _load_module(name: str, path: Path) -> ModuleType:
    specification = importlib.util.spec_from_file_location(name, path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


@pytest.fixture
def runtimes() -> tuple[ModuleType, ModuleType]:
    retrieval = _load_module("_retrieval_eval", RETRIEVAL_HELPERS)
    evaluator = _load_module("endocrine_hygiene_retrieval_gate_evaluator", EVALUATOR)
    return retrieval, evaluator


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _bundle(retrieval: ModuleType, root: Path) -> tuple[Path, dict[str, Any]]:
    bundle = root / "bundle"
    (bundle / "semantic").mkdir(parents=True)
    concept_path = "concepts/paper-pmc1001/record-1.md"
    (bundle / concept_path).parent.mkdir(parents=True)
    (bundle / concept_path).write_text("# Verified concept\n", encoding="utf-8")
    record: dict[str, Any] = {
        "source_id": "paper-pmc1001",
        "source_kind": "json",
        "source_path": "sources/semantic/paper-pmc1001.jsonl",
        "record_id": "record-1",
        "subject_iri": "https://example.test/resource/paper-pmc1001/record-1",
        "ontology_class_iri": "https://example.test/ontology#Evidence",
        "concept_type": "Evidence",
        "title": "Verified record",
        "body": "triclosan exposure evidence",
        "attributes": {"fixture": True},
        "concept_id": concept_path.removesuffix(".md"),
        "concept_path": concept_path,
    }
    digest_payload = {field: record[field] for field in retrieval.RECORD_DIGEST_FIELDS}
    record["record_sha256"] = retrieval.sha256_bytes(_canonical_json(digest_payload).encode("utf-8"))
    (bundle / "semantic" / "records.jsonl").write_text(
        _canonical_json(record) + "\n", encoding="utf-8", newline="\n"
    )
    return bundle, record


def _hit(retrieval: ModuleType, record: dict[str, Any], *, record_sha256: str | None) -> Any:
    return retrieval.RetrievalHit(
        source_id=record["source_id"],
        paper_id="PMC1001",
        record_id=record["record_id"],
        record_sha256=record_sha256,
        concept_id=record["concept_id"],
        concept_path=record["concept_path"],
        source_path=record["source_path"],
        locator={"kind": "record"},
        text=record["body"],
        text_sha256=retrieval.sha256_bytes(record["body"].encode("utf-8")),
        score=1.0,
        retrieval_id="fixture-hit",
    )


@pytest.mark.parametrize("field,replacement", [("body", "tampered evidence"), ("title", "Tampered title")])
def test_ledger_recomputes_canonical_record_digest(
    runtimes: tuple[ModuleType, ModuleType], tmp_path: Path, field: str, replacement: str
) -> None:
    retrieval, _ = runtimes
    bundle, record = _bundle(retrieval, tmp_path)
    assert retrieval.AuthoritativeLedger(bundle).records[0]["record_sha256"] == record["record_sha256"]

    record[field] = replacement
    (bundle / "semantic" / "records.jsonl").write_text(
        _canonical_json(record) + "\n", encoding="utf-8", newline="\n"
    )

    with pytest.raises(retrieval.EvaluationError, match="canonical source-derived fields"):
        retrieval.AuthoritativeLedger(bundle)


def test_hit_requires_exact_record_digest_and_serializes_it(
    runtimes: tuple[ModuleType, ModuleType], tmp_path: Path
) -> None:
    retrieval, _ = runtimes
    bundle, record = _bundle(retrieval, tmp_path)
    ledger = retrieval.AuthoritativeLedger(bundle)
    exact = _hit(retrieval, record, record_sha256=record["record_sha256"])
    missing = _hit(retrieval, record, record_sha256=None)
    mismatched = _hit(retrieval, record, record_sha256="f" * 64)

    assert ledger.validate_hit(exact) == {"valid": True, "issues": []}
    assert ledger.validate_hit(missing) == {"valid": False, "issues": ["missing record_sha256"]}
    assert "record_sha256 does not match the ledger" in ledger.validate_hit(mismatched)["issues"]
    unknown = retrieval.RetrievalHit(**{**missing.__dict__, "record_id": "unknown"})
    assert ledger.validate_hit(unknown)["issues"][:2] == [
        "source_id and record_id do not bind a ledger record",
        "missing record_sha256",
    ]
    assert retrieval.compact_hit(exact, {"valid": True, "issues": []}, 1)["record_sha256"] == record[
        "record_sha256"
    ]


def test_hashless_consult_hit_can_be_bound_only_by_exact_ledger_identity(
    runtimes: tuple[ModuleType, ModuleType], tmp_path: Path
) -> None:
    retrieval, _ = runtimes
    bundle, record = _bundle(retrieval, tmp_path)
    ledger = retrieval.AuthoritativeLedger(bundle)
    missing = _hit(retrieval, record, record_sha256=None)

    bound = ledger.bind_missing_record_sha256(missing)
    assert bound.record_sha256 == record["record_sha256"]
    assert bound.record_sha256_provenance == "authoritative-ledger-identity-join"
    assert ledger.validate_hit(bound) == {"valid": True, "issues": []}

    unknown = retrieval.RetrievalHit(**{**missing.__dict__, "record_id": "unknown"})
    assert ledger.bind_missing_record_sha256(unknown) == unknown
    mismatched = retrieval.RetrievalHit(**{**missing.__dict__, "record_sha256": "f" * 64})
    assert ledger.bind_missing_record_sha256(mismatched) == mismatched
    assert "record_sha256 does not match the ledger" in ledger.validate_hit(mismatched)["issues"]


def test_invalid_evidence_makes_route_partial_and_top_level_error(
    runtimes: tuple[ModuleType, ModuleType], tmp_path: Path
) -> None:
    retrieval, evaluator = runtimes
    bundle, record = _bundle(retrieval, tmp_path)
    ledger = retrieval.AuthoritativeLedger(bundle)
    question = retrieval.RetrievalQuestion(
        "q-hard-fixture",
        "hard",
        "What evidence exists?",
        ("PMC1001",),
        ("paper-pmc1001",),
    )
    route = evaluator._evaluate_route(
        "legacy",
        "legacy_lexical",
        [question],
        ledger,
        lambda _query: [_hit(retrieval, record, record_sha256=None)],
    )

    assert route["status"] == "partial"
    assert route["overall"]["evidence_validity"] == {"returned": 1, "valid": 0, "invalid": 1, "ratio": 0.0}
    assert evaluator._evaluation_status([route]) == "error"
    assert evaluator._evaluation_status([evaluator._na_route("entity-graph", "entity", "expected")]) == "pass"
    assert evaluator._evaluation_status([{"status": "pass", "overall": None}]) == "error"


def test_initialization_failure_is_error_not_not_applicable(runtimes: tuple[ModuleType, ModuleType]) -> None:
    _, evaluator = runtimes
    route = evaluator._error_route("classical", "bm25", "initialization failed")

    assert route["status"] == "error"
    assert route["execution"] == "consult initialization attempted"
    assert evaluator._evaluation_status([route]) == "error"


def test_main_persists_failure_report_and_returns_nonzero(
    runtimes: tuple[ModuleType, ModuleType], tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    _, evaluator = runtimes
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    raw = tmp_path / "raw.json"
    compact = tmp_path / "compact.json"
    markdown = tmp_path / "compact.md"
    report = {
        "schema_version": evaluator.SCHEMA_VERSION,
        "status": "error",
        "routes": [evaluator._error_route("classical", "bm25", "fixture failure")],
        "families": [],
    }
    monkeypatch.setattr(evaluator, "evaluate", lambda _args: report)
    monkeypatch.setattr(evaluator, "_render_markdown", lambda _report: "# Failed evaluation\n")

    exit_code = evaluator.main(
        [
            "--run-dir",
            str(run_dir),
            "--raw-output",
            str(raw),
            "--compact-json",
            str(compact),
            "--compact-markdown",
            str(markdown),
        ]
    )

    assert exit_code == 1
    assert json.loads(raw.read_text(encoding="utf-8"))["status"] == "error"
    assert json.loads(compact.read_text(encoding="utf-8"))["status"] == "error"
    diagnostic = json.loads(capsys.readouterr().err)
    assert diagnostic == {
        "status": "error",
        "error": "executable retrieval routes did not pass",
        "routes": ["classical/bm25=error"],
    }
