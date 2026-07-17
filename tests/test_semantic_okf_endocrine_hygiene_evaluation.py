from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import math
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
EVALUATION_ROOT = REPO_ROOT / "evaluations" / "semantic-okf-endocrine-hygiene"
PREPARE_CORPUS = EVALUATION_ROOT / "scripts" / "prepare_corpus.py"
RETRIEVAL_EVAL = EVALUATION_ROOT / "scripts" / "_retrieval_eval.py"
MANUAL_QUERY_REPORT = EVALUATION_ROOT / "reports" / "manual-query-verification.json"


def _load_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _bioc_body(pmcid: str, title: str) -> tuple[str, str]:
    passage = {
        "offset": 0,
        "infons": {
            "article-id_doi": f"10.9999/{pmcid.casefold()}",
            "article-id_pmid": pmcid.removeprefix("PMC"),
            "name_0": "given-names:Ada;surname:Lovelace",
            "section_type": "TITLE",
            "type": "title",
            "year": "2024",
        },
        "text": title,
    }
    payload = [
        {
            "documents": [
                {
                    "id": pmcid,
                    "infons": {"license": "CC BY 4.0"},
                    "passages": [passage],
                }
            ]
        }
    ]
    return _canonical_json(payload), _sha256(title.encode("utf-8"))


def _write_know_page(
    prepare: ModuleType,
    store: Path,
    key: str,
    pmcid: str,
    body: str,
    *,
    metadata_sha256: str | None = None,
    metadata_bytes: int | None = None,
    newline: str = "\n",
) -> Path:
    body_bytes = body.encode("utf-8")
    metadata_sha256 = metadata_sha256 or _sha256(body_bytes)
    metadata_bytes = len(body_bytes) if metadata_bytes is None else metadata_bytes
    header_lines = [
        "---",
        f"knowledge_key: {key}",
        f"source_id: {pmcid.casefold()}",
        f"url: {prepare.BIOC_URL.format(pmcid=pmcid)}",
        "source_metadata:",
        "  content_format: json",
        "  content_type: application/json; charset=utf-8",
        f"  raw_content_bytes: {metadata_bytes}",
        f"  raw_content_sha256: {metadata_sha256}",
        "---",
    ]
    path = store / key / "site" / pmcid.casefold() / "pages" / "source.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes((newline.join(header_lines) + newline + body).encode("utf-8"))
    return path


def _selection_row(pmcid: str) -> dict[str, str]:
    return {
        "pmcid": pmcid,
        "role": "core",
        "relevance": f"Fixture evidence for {pmcid}.",
        "caution": "Synthetic fixture; not scientific evidence.",
    }


def _configure_tiny_corpus(
    prepare: ModuleType,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> tuple[Path, Path]:
    evaluation = tmp_path / "evaluation"
    corpus = evaluation / "corpus"
    store = tmp_path / "know"
    key = "fixture-bioc-key"
    export_name = "fixture-export.zip"
    export_payload = b"immutable fixture export"
    export_path = store / "exports" / export_name
    export_path.parent.mkdir(parents=True)
    export_path.write_bytes(export_payload)

    pmcids = [f"PMC{number}" for number in range(1001, 1016)]
    selections: list[dict[str, str]] = []
    claims: list[dict[str, Any]] = []
    for pmcid in pmcids:
        title = f"{pmcid} triclosan and hygiene product evidence <preserved>"
        body, passage_sha256 = _bioc_body(pmcid, title)
        _write_know_page(prepare, store, key, pmcid, body)
        selections.append(_selection_row(pmcid))
        claims.append(
            {
                "id": f"claim-{pmcid.casefold()}-001",
                "paper_id": pmcid,
                "passage": 1,
                "passage_sha256": passage_sha256,
                "claim_kind": "methodology",
                "dimension_id": "dimension-methodology",
                "interpretation": f"{pmcid} supplies a synthetic methodology fixture.",
                "claim_origin": "manual-review:bioc-passage",
                "confidence": "high",
            }
        )

    corpus.mkdir(parents=True)
    selection_path = corpus / "acquisition-selection.json"
    claims_path = corpus / "claims-seed.json"
    selection_path.write_text(
        json.dumps(
            {
                "schema_version": "semantic-okf-endocrine-hygiene-acquisition-selection/1.0",
                "know_key": key,
                "source_kind": "site",
                "accepted_export": {
                    "filename": export_name,
                    "bytes": len(export_payload),
                    "sha256": _sha256(export_payload),
                },
                "papers": selections,
            }
        ),
        encoding="utf-8",
    )
    claims_path.write_text(
        json.dumps(
            {
                "schema_version": "semantic-okf-endocrine-hygiene-claims-seed/1.0",
                "claims": claims,
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(prepare, "EVALUATION", evaluation)
    monkeypatch.setattr(prepare, "CORPUS", corpus)
    monkeypatch.setattr(prepare, "SELECTION_PATH", selection_path)
    monkeypatch.setattr(prepare, "CLAIMS_SEED_PATH", claims_path)
    return store, corpus


def _write_questions(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text("".join(_canonical_json(row) + "\n" for row in rows), encoding="utf-8")


def _question(
    *,
    paper_id: str = "PMC1001",
    source_id: str = "paper-pmc1001",
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    row: dict[str, Any] = {
        "id": "q-hard-fixture",
        "question": "Which exact evidence is relevant?",
        "question_type": "hard",
        "qrels": {"paper_ids": [paper_id], "source_ids": [source_id]},
    }
    if extra:
        row.update(extra)
    return row


def _ledger_bundle(retrieval: ModuleType, root: Path, bodies: list[tuple[str, str]]) -> tuple[Path, list[dict[str, Any]]]:
    bundle = root / "knowledge"
    semantic = bundle / "semantic"
    concepts = bundle / "concepts"
    semantic.mkdir(parents=True)
    concepts.mkdir(parents=True)
    records: list[dict[str, Any]] = []
    for index, (source_id, body) in enumerate(bodies, 1):
        concept_path = f"concepts/concept-{index}.md"
        (bundle / concept_path).write_text(f"# Concept {index}\n", encoding="utf-8")
        record = {
            "source_id": source_id,
            "source_kind": "markdown",
            "source_path": f"sources/source-{index}.md",
            "record_id": f"record-{index}",
            "subject_iri": f"https://example.test/resource/record-{index}",
            "ontology_class_iri": "https://example.test/ontology#Evidence",
            "concept_type": "Evidence",
            "title": f"Record {index}",
            "body": body,
            "attributes": {"fixture": index},
            "concept_id": f"concept-{index}",
            "concept_path": concept_path,
        }
        digest_payload = {field: record[field] for field in retrieval.RECORD_DIGEST_FIELDS}
        record["record_sha256"] = retrieval.sha256_bytes(
            _canonical_json(digest_payload).encode("utf-8")
        )
        records.append(record)
    (semantic / "records.jsonl").write_text(
        "".join(_canonical_json(record) + "\n" for record in records), encoding="utf-8"
    )
    return bundle, records


def _hit(
    retrieval: ModuleType,
    record: dict[str, Any],
    *,
    locator: dict[str, Any] | None = None,
    text: str | None = None,
    record_sha256: str | None = None,
) -> Any:
    retained = record["body"] if text is None else text
    return retrieval.RetrievalHit(
        source_id=record["source_id"],
        paper_id="PMC1001",
        record_id=record["record_id"],
        record_sha256=record["record_sha256"] if record_sha256 is None else record_sha256,
        concept_id=record["concept_id"],
        concept_path=record["concept_path"],
        source_path=record["source_path"],
        locator={"kind": "record"} if locator is None else locator,
        text=retained,
        text_sha256=retrieval.sha256_bytes(retained.encode("utf-8")),
        score=1.0,
        retrieval_id="fixture-hit",
    )


def test_split_okf_markdown_accepts_crlf_and_preserves_raw_bytes(tmp_path: Path) -> None:
    prepare = _load_module("endocrine_hygiene_prepare_crlf", PREPARE_CORPUS)
    body = '{"value":"literal <tag> content"}'
    path = tmp_path / "crlf.md"
    raw = (
        "---\r\n"
        "knowledge_key: crlf-fixture\r\n"
        "source_metadata:\r\n"
        "  content_format: json\r\n"
        "---\r\n"
        + body
    ).encode("utf-8")
    path.write_bytes(raw)

    frontmatter, parsed_body, parsed_raw = prepare.split_okf_markdown(path)

    assert frontmatter == {
        "knowledge_key": "crlf-fixture",
        "source_metadata": {"content_format": "json"},
    }
    assert parsed_body == body
    assert parsed_raw == raw


def test_paper_record_requires_lossless_json_hash_and_byte_binding(tmp_path: Path) -> None:
    prepare = _load_module("endocrine_hygiene_prepare_hash", PREPARE_CORPUS)
    store = tmp_path / "know"
    key = "lossless-fixture"
    pmcid = "PMC1001"
    title = "Toothpaste <i>triclosan</i> must remain literal JSON text"
    body, _ = _bioc_body(pmcid, title)
    page = _write_know_page(prepare, store, key, pmcid, body, newline="\r\n")

    record = prepare.paper_record(_selection_row(pmcid), store, key)

    assert record["raw_bioc_sha256"] == _sha256(body.encode("utf-8"))
    assert record["raw_bioc_bytes"] == len(body.encode("utf-8"))
    assert record["passages"][0]["text"] == title
    assert "<i>triclosan</i>" in record["passages"][0]["text"]

    _write_know_page(prepare, store, key, pmcid, body, metadata_sha256="0" * 64)
    with pytest.raises(prepare.PreparationError, match="raw-content hash or byte count"):
        prepare.paper_record(_selection_row(pmcid), store, key)

    assert page.is_file()


def test_tiny_generated_corpus_write_and_check_detects_drift(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    prepare = _load_module("endocrine_hygiene_prepare_tiny", PREPARE_CORPUS)
    store, corpus = _configure_tiny_corpus(prepare, tmp_path, monkeypatch)

    assert prepare.main(["--know-store", str(store)]) == 0
    written = json.loads(capsys.readouterr().out)
    assert written["status"] == "pass"
    assert written["mode"] == "write"
    assert written["output_files"] == 35
    assert len(list((corpus / "sources" / "markdown").glob("PMC*.md"))) == 15
    assert len(list((corpus / "sources" / "claims").glob("PMC*.jsonl"))) == 15

    assert prepare.main(["--know-store", str(store), "--check"]) == 0
    checked = json.loads(capsys.readouterr().out)
    assert checked["mode"] == "check"

    generated = corpus / "sources" / "markdown" / "PMC1001.md"
    generated.write_bytes(generated.read_bytes() + b"drift\n")
    drifted = generated.read_bytes()
    assert prepare.main(["--know-store", str(store), "--check"]) == 1
    failure = capsys.readouterr()
    assert "stale or missing: corpus/sources/markdown/PMC1001.md" in failure.err
    assert generated.read_bytes() == drifted


def test_checked_in_corpus_matches_pinned_know_acquisition_when_available(
    capsys: pytest.CaptureFixture[str],
) -> None:
    selection = json.loads(
        (EVALUATION_ROOT / "corpus" / "acquisition-selection.json").read_text(encoding="utf-8")
    )
    know_store = REPO_ROOT / "tmp" / "endocrine-hygiene-know"
    export = know_store / "exports" / selection["accepted_export"]["filename"]
    if not export.is_file():
        pytest.skip("The ignored, append-only Know acquisition is not present in this checkout.")
    prepare = _load_module("endocrine_hygiene_prepare_pinned", PREPARE_CORPUS)

    assert prepare.main(["--know-store", str(know_store), "--check"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "pass"
    assert result["mode"] == "check"
    assert result["output_files"] == 35


def test_question_loader_enforces_closed_schema_and_canonical_identity(tmp_path: Path) -> None:
    retrieval = _load_module("endocrine_hygiene_retrieval_questions", RETRIEVAL_EVAL)
    identity = {"paper-pmc1001": "PMC1001"}
    path = tmp_path / "questions.jsonl"
    _write_questions(path, [_question()])

    questions = retrieval.load_questions(path, identity)

    assert questions == [
        retrieval.RetrievalQuestion(
            "q-hard-fixture",
            "hard",
            "Which exact evidence is relevant?",
            ("PMC1001",),
            ("paper-pmc1001",),
        )
    ]

    with_extra = _question(extra={"answer": "leaked"})
    _write_questions(path, [with_extra])
    with pytest.raises(retrieval.EvaluationError, match="closed schema"):
        retrieval.load_questions(path, identity)

    _write_questions(path, [_question(source_id="Paper-PMC1001")])
    with pytest.raises(retrieval.EvaluationError, match="unknown sources"):
        retrieval.load_questions(path, identity)

    _write_questions(path, [_question(paper_id="2506.05690v3")])
    with pytest.raises(retrieval.EvaluationError, match="noncanonical PMCID"):
        retrieval.load_questions(path, identity)


def test_checked_benchmark_has_lowercase_source_ids_and_no_arxiv_aliases() -> None:
    retrieval = _load_module("endocrine_hygiene_retrieval_real_ids", RETRIEVAL_EVAL)
    combination = json.loads(
        (EVALUATION_ROOT / "corpus" / "source-combination.json").read_text(encoding="utf-8")
    )
    identity = combination["identity_by_source"]
    questions = retrieval.load_questions(
        EVALUATION_ROOT / "benchmark" / "retrieval-questions.jsonl", identity
    )

    assert identity
    assert all(source_id == source_id.casefold() for source_id in identity)
    assert all(retrieval.PMCID_RE.fullmatch(paper_id) for paper_id in identity.values())
    assert all(source_id == source_id.casefold() for question in questions for source_id in question.source_ids)
    assert all(
        retrieval.PMCID_RE.fullmatch(paper_id)
        for question in questions
        for paper_id in question.paper_ids
    )
    serialized_ids = _canonical_json(
        {
            "identity": identity,
            "qrels": [question.paper_ids for question in questions],
        }
    ).casefold()
    assert "arxiv" not in serialized_ids
    assert "2506." not in serialized_ids


def test_hard_evidence_manifest_distinguishes_bindings_from_unique_passages() -> None:
    ground_truth = [
        json.loads(line)
        for line in (EVALUATION_ROOT / "benchmark" / "hard-ground-truth.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
        if line
    ]
    bindings = [
        evidence
        for record in ground_truth
        for evidence in record["authoritative_evidence"]
    ]
    unique_passages = {
        (evidence["paper_id"], evidence["locator"], evidence["text_sha256"])
        for evidence in bindings
    }
    counts = json.loads(
        (EVALUATION_ROOT / "benchmark" / "benchmark-manifest.json").read_text(encoding="utf-8")
    )["counts"]

    assert len(bindings) == counts["hard_evidence_bindings"] == 60
    assert len(unique_passages) == counts["distinct_authoritative_passages"] == 34


def test_manual_query_report_covers_every_family_and_proves_read_only_bundles() -> None:
    report = json.loads(MANUAL_QUERY_REPORT.read_text(encoding="utf-8"))

    assert report["status"] == "pass"
    assert report["question_id"] == "q030-causal-evidence-map"
    assert report["execution_contract"] == {
        "read_only": True,
        "mcp_used": False,
        "compatible_family_count": 4,
        "not_applicable_family_count": 2,
        "all_returned_hits_independently_validated": True,
    }
    assert {row["family"] for row in report["compatible_families"]} == {
        "legacy",
        "embeddings",
        "classical",
        "adaptive",
    }
    assert all(row["status"] == "pass" for row in report["compatible_families"])
    assert all(row["bundle_unchanged"] for row in report["compatible_families"])
    assert all(
        row["bundle_tree_sha256_before"] == row["bundle_tree_sha256_after"]
        for row in report["compatible_families"]
    )
    assert {row["family"] for row in report["incompatible_families"]} == {
        "entity-graph",
        "ensemble",
    }


def test_deduplication_and_ranking_metrics_use_first_occurrence() -> None:
    retrieval = _load_module("endocrine_hygiene_retrieval_metrics", RETRIEVAL_EVAL)

    ranked = retrieval.deduplicate(
        ["PMC1002", "PMC1002", None, "", "PMC1001", "PMC1002"]
    )
    metrics = retrieval.ranking_metrics(ranked, {"PMC1001", "PMC1003"})

    assert ranked == ["PMC1002", "PMC1001"]
    assert metrics["recall_at_1"] == 0.0
    assert metrics["recall_at_3"] == 0.5
    assert metrics["recall_at_5"] == 0.5
    assert metrics["recall_at_10"] == 0.5
    assert metrics["mrr_at_10"] == 0.5
    expected_dcg = 1.0 / math.log2(3)
    expected_ideal = 1.0 + 1.0 / math.log2(3)
    assert metrics["ndcg_at_10"] == pytest.approx(expected_dcg / expected_ideal)
    with pytest.raises(retrieval.EvaluationError, match="qrels cannot be empty"):
        retrieval.ranking_metrics(ranked, set())


def test_authoritative_ledger_validates_exact_record_and_character_range(tmp_path: Path) -> None:
    retrieval = _load_module("endocrine_hygiene_retrieval_evidence", RETRIEVAL_EVAL)
    bundle, records = _ledger_bundle(retrieval, tmp_path, [("paper-pmc1001", "alpha beta gamma")])
    ledger = retrieval.AuthoritativeLedger(bundle)
    record = records[0]

    exact_record = _hit(retrieval, record)
    exact_range = _hit(
        retrieval,
        record,
        locator={"kind": "character-range", "start": 6, "end": 10},
        text="beta",
    )
    assert ledger.validate_hit(exact_record) == {"valid": True, "issues": []}
    assert ledger.validate_hit(exact_range) == {"valid": True, "issues": []}

    wrong_record_hash = _hit(retrieval, record, record_sha256="f" * 64)
    wrong_record_text = _hit(retrieval, record, text="alpha")
    wrong_range = _hit(
        retrieval,
        record,
        locator={"kind": "character-range", "start": 6, "end": 10},
        text="BETX",
    )
    extra_range_member = _hit(
        retrieval,
        record,
        locator={"kind": "character-range", "start": 6, "end": 10, "unit": "char"},
        text="beta",
    )

    assert "record_sha256 does not match the ledger" in ledger.validate_hit(wrong_record_hash)["issues"]
    assert "record locator does not bind the complete ledger body" in ledger.validate_hit(wrong_record_text)["issues"]
    assert "character-range text differs from the ledger slice" in ledger.validate_hit(wrong_range)["issues"]
    assert "character-range locator has invalid members" in ledger.validate_hit(extra_range_member)["issues"]


def test_evaluate_hits_deduplicates_paper_and_source_rankings(tmp_path: Path) -> None:
    retrieval = _load_module("endocrine_hygiene_retrieval_dedup_hits", RETRIEVAL_EVAL)
    bundle, records = _ledger_bundle(retrieval, tmp_path, [("paper-pmc1001", "triclosan evidence")])
    ledger = retrieval.AuthoritativeLedger(bundle)
    hit = _hit(retrieval, records[0])
    question = retrieval.RetrievalQuestion(
        "q-hard-fixture",
        "hard",
        "What is the triclosan evidence?",
        ("PMC1001",),
        ("paper-pmc1001",),
    )

    evaluated = retrieval.evaluate_hits(question, [hit, copy.copy(hit)], ledger, 1.25, None)

    assert evaluated["paper_ids"] == ["PMC1001"]
    assert evaluated["source_ids"] == ["paper-pmc1001"]
    assert evaluated["paper_metrics"]["recall_at_1"] == 1.0
    assert evaluated["source_metrics"]["recall_at_1"] == 1.0
    assert evaluated["evidence_validity"] == {"returned": 2, "valid": 2, "invalid": 0}


def test_legacy_tfidf_prefers_specific_repeated_terms_and_returns_bound_evidence(
    tmp_path: Path,
) -> None:
    retrieval = _load_module("endocrine_hygiene_retrieval_legacy", RETRIEVAL_EVAL)
    bundle, _ = _ledger_bundle(
        retrieval,
        tmp_path,
        [
            ("paper-pmc1001", "triclosan toothpaste triclosan urinary biomarker"),
            ("paper-pmc1002", "triclosan soap exposure"),
            ("paper-pmc1003", "toothpaste triclosan excluded identity"),
        ],
    )
    ledger = retrieval.AuthoritativeLedger(bundle)
    identity = {
        "paper-pmc1001": "PMC1001",
        "paper-pmc1002": "PMC1002",
    }
    index = retrieval.LegacyLexicalIndex(ledger, identity)

    hits = index.search("Which toothpaste triclosan biomarker evidence?", top_k=10)

    assert index.idf["triclosan"] == pytest.approx(1.0)
    assert index.idf["toothpaste"] == pytest.approx(1.0 + math.log(3 / 2))
    assert all(value >= 1.0 for value in index.idf.values())
    assert [hit.paper_id for hit in hits] == ["PMC1001", "PMC1002"]
    assert hits[0].score > hits[1].score > 0
    assert all(hit.locator == {"kind": "record"} for hit in hits)
    assert all(ledger.validate_hit(hit)["valid"] for hit in hits)
    assert index.search("which the and", top_k=10) == []
    assert all(hit.paper_id != "2506.05690v3" for hit in hits)
