from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from types import ModuleType

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPO_ROOT / "skills" / "consult-semantic-okf"
SCRIPTS = SKILL_ROOT / "scripts"
BUNDLE = REPO_ROOT / "evaluations" / "graphrag-cross-paper" / "bundle"
PAPER_SOURCE = "paper-2402-07630v3"
PAPER_TITLE = (
    "G-Retriever: Retrieval-Augmented Generation for Textual Graph Understanding and Question Answering"
)
CLAIM_SUBJECT = (
    "https://example.org/graphrag-cross-paper/resource/claims-2402-07630v3/"
    "claim-2402-07630v3-001"
)
CROSS_SOURCE_QUESTION = (
    "Compare path-centric, connected-subgraph, and graph-query approaches to multi-hop "
    "reasoning. How does each retrieve bridges between facts, organize evidence, and control "
    "irrelevant context?"
)
CROSS_SOURCE_DIMENSIONS = [
    "retrieval-unit",
    "retrieval-strategy",
    "organization-synthesis",
    "limitation",
]


def load_script(name: str) -> ModuleType:
    """Load a self-contained consultant script under its runtime import name."""

    pytest.importorskip("rdflib")
    support_path = SCRIPTS / "_consult_semantic_okf.py"
    support_spec = importlib.util.spec_from_file_location("_consult_semantic_okf", support_path)
    assert support_spec and support_spec.loader
    support = importlib.util.module_from_spec(support_spec)
    sys.modules[support_spec.name] = support
    support_spec.loader.exec_module(support)

    path = SCRIPTS / name
    spec = importlib.util.spec_from_file_location(f"test_consult_{path.stem}", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def run_query(*args: str, timeout: int = 120) -> subprocess.CompletedProcess[str]:
    """Run the consultant helper exactly as an isolated skill consumer would."""

    return subprocess.run(
        [sys.executable, str(SCRIPTS / "query_semantic_okf.py"), str(BUNDLE), *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=timeout,
        check=False,
    )


def run_prepare(*args: str, timeout: int = 120) -> subprocess.CompletedProcess[str]:
    """Run the deterministic cross-source evidence planner."""

    return subprocess.run(
        [
            sys.executable,
            str(SCRIPTS / "prepare_cross_source_evidence.py"),
            str(BUNDLE),
            *args,
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=timeout,
        check=False,
    )


def run_preflight(candidate: str, *args: str, timeout: int = 120) -> subprocess.CompletedProcess[str]:
    """Pipe one candidate through the fail-closed answer gate."""

    return subprocess.run(
        [
            sys.executable,
            str(SCRIPTS / "validate_cross_source_answer.py"),
            str(BUNDLE),
            "--stdin",
            *args,
        ],
        cwd=REPO_ROOT,
        input=candidate,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=timeout,
        check=False,
    )


def cross_source_args() -> list[str]:
    """Return one fixed discovery-only contract for helper integration tests."""

    args = [
        "--question-id",
        "integration-cross-source",
        "--question",
        CROSS_SOURCE_QUESTION,
    ]
    for dimension in CROSS_SOURCE_DIMENSIONS:
        args.extend(["--dimension", dimension])
    args.extend(["--min-sources", "5", "--reserve", "5"])
    return args


def json_output(result: subprocess.CompletedProcess[str]) -> dict[str, object]:
    payload = json.loads(result.stdout)
    assert isinstance(payload, dict)
    return payload


def tree_sha256(root: Path) -> str:
    """Hash names and bytes so consultation mutations cannot hide in timestamps."""

    digest = hashlib.sha256()
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        digest.update(path.relative_to(root).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def test_consult_skill_metadata_dependencies_and_command_boundary() -> None:
    skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
    metadata = (SKILL_ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
    direct = (SCRIPTS / "requirements.in").read_text(encoding="utf-8").splitlines()
    compiled = (SCRIPTS / "requirements.txt").read_text(encoding="utf-8").lower()
    support = (SCRIPTS / "_consult_semantic_okf.py").read_text(encoding="utf-8")
    helper = (SCRIPTS / "query_semantic_okf.py").read_text(encoding="utf-8")
    builder = REPO_ROOT / "skills" / "build-semantic-okf"

    assert "name: consult-semantic-okf" in skill
    assert "Read-only boundary" in skill
    assert "$build-semantic-okf" in skill
    assert "query_semantic_okf.py" in skill
    assert "prepare_cross_source_evidence.py" in skill
    assert "validate_cross_source_answer.py" in skill
    assert "status: pass" in skill
    assert "cross-source-synthesis.md" in skill
    assert "source-boundaries.md" in skill
    assert "TODO" not in skill
    assert "$consult-semantic-okf" in metadata
    assert "Query and synthesize validated semantic knowledge" in metadata
    assert direct == ["rdflib==7.6.0"]
    assert "rdflib==7.6.0" in compiled
    assert "pyparsing==3.3.2" in compiled

    assert (SCRIPTS / "query_semantic_okf.py").is_file()
    assert (SCRIPTS / "_cross_source.py").is_file()
    assert (SCRIPTS / "prepare_cross_source_evidence.py").is_file()
    assert (SCRIPTS / "validate_cross_source_answer.py").is_file()
    assert (SCRIPTS / "runtime_smoke.py").is_file()
    assert not (SCRIPTS / "build_semantic_okf.py").exists()
    assert not (SCRIPTS / "refresh_semantic_okf.py").exists()
    assert not (SCRIPTS / "validate_semantic_okf.py").exists()
    assert (builder / "scripts" / "build_semantic_okf.py").is_file()
    assert (builder / "scripts" / "refresh_semantic_okf.py").is_file()
    assert not (builder / "scripts" / "query_semantic_okf.py").exists()
    assert "_semantic_okf" not in support
    assert "build-semantic-okf" not in support
    assert "from _consult_semantic_okf import" in helper
    assert "from _semantic_okf import" not in helper
    for script_name in (
        "_cross_source.py",
        "prepare_cross_source_evidence.py",
        "validate_cross_source_answer.py",
    ):
        script = (SCRIPTS / script_name).read_text(encoding="utf-8")
        assert "build_semantic_okf" not in script
        assert "refresh_semantic_okf" not in script
        assert "urllib" not in script
        assert "requests" not in script


def test_consult_references_define_efficient_grounded_synthesis() -> None:
    querying = (SKILL_ROOT / "references" / "querying.md").read_text(encoding="utf-8")
    synthesis = (SKILL_ROOT / "references" / "cross-source-synthesis.md").read_text(
        encoding="utf-8"
    )
    boundaries = (SKILL_ROOT / "references" / "source-boundaries.md").read_text(
        encoding="utf-8"
    )

    assert "Choose the cheapest layer" in querying
    assert "Do not union all graphs by default" in querying
    assert "Treat discovery and evidence separately" in querying
    assert "breadth-before-depth" in synthesis.lower()
    assert "exact concept path" in synthesis.lower()
    assert "page locator" in synthesis.lower()
    assert "coverage ledger" in synthesis.lower()
    assert "deterministic preflight" in synthesis.lower()
    assert "normalized_response" in synthesis
    assert "Separate authorities" in boundaries
    assert "Homogeneous partition union" in boundaries
    assert "Shared dimensions or matching strings" in boundaries


def test_runtime_smoke_reports_read_only_standalone_runtime() -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "runtime_smoke.py")],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=60,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "pass"
    assert payload["mode"] == "read-only"
    assert payload["network"] == "none"


def test_ledger_filters_typed_attributes_and_opens_exact_content() -> None:
    paper = run_query(
        "ledger",
        "--source-id",
        PAPER_SOURCE,
        "--type",
        "Research Paper",
        "--show-content",
        "--format",
        "json",
    )
    assert paper.returncode == 0, paper.stderr
    payload = json_output(paper)
    assert payload["returned"] == 1
    record = payload["records"][0]
    assert record["title"] == PAPER_TITLE
    assert record["concept_path"].startswith(f"concepts/{PAPER_SOURCE}/")
    assert "## PDF page 1" in record["content"]

    claims = run_query(
        "ledger",
        "--source-id",
        "claims-2402-07630v3",
        "--attribute",
        "claim_kind",
        "graph-representation",
        "--limit",
        "1",
        "--format",
        "json",
    )
    assert claims.returncode == 0, claims.stderr
    claim_payload = json_output(claims)
    assert claim_payload["returned"] == 1
    assert claim_payload["truncated"] is True
    assert claim_payload["matched"] is None
    assert claim_payload["records"][0]["attributes"]["claim_kind"] == "graph-representation"


def test_sparql_select_ask_graph_ownership_and_rejections(tmp_path: Path) -> None:
    count = run_query(
        "sparql",
        "--query",
        "SELECT (COUNT(?paper) AS ?count) WHERE { "
        "?paper a <https://example.org/ontology/graphrag-cross-paper#Paper> . }",
        "--graph",
        "data",
        "--format",
        "json",
    )
    assert count.returncode == 0, count.stderr
    count_payload = json_output(count)
    assert count_payload["graphs"] == ["data"]
    assert count_payload["query_type"] == "SELECT"
    assert count_payload["rows"][0]["count"]["value"] == "15"

    lineage_query = (
        f"ASK {{ <{CLAIM_SUBJECT}> "
        "<http://www.w3.org/ns/prov#wasDerivedFrom> ?source . }"
    )
    data_only = run_query(
        "sparql", "--query", lineage_query, "--graph", "data", "--format", "json"
    )
    with_provenance = run_query(
        "sparql",
        "--query",
        lineage_query,
        "--graph",
        "data",
        "--graph",
        "provenance",
        "--format",
        "json",
    )
    assert data_only.returncode == 0, data_only.stderr
    assert with_provenance.returncode == 0, with_provenance.stderr
    assert json_output(data_only)["boolean"] is False
    assert json_output(with_provenance)["boolean"] is True

    shape = run_query(
        "sparql",
        "--query",
        "ASK { ?shape a <http://www.w3.org/ns/shacl#NodeShape> . }",
        "--graph",
        "shapes",
        "--format",
        "json",
    )
    report = run_query(
        "sparql",
        "--query",
        "ASK { ?report a <http://www.w3.org/ns/shacl#ValidationReport> . }",
        "--graph",
        "validation",
        "--format",
        "json",
    )
    assert json_output(shape)["boolean"] is True
    assert json_output(report)["boolean"] is True

    rejected = [
        "CONSTRUCT { ?s ?p ?o } WHERE { ?s ?p ?o }",
        "INSERT DATA { <https://example.org/s> <https://example.org/p> <https://example.org/o> }",
        "SELECT * FROM <https://example.org/remote> WHERE { ?s ?p ?o }",
        "SELECT * WHERE { SERVICE <https://example.org/sparql> { ?s ?p ?o } }",
    ]
    for query in rejected:
        result = run_query("sparql", "--query", query, "--format", "json")
        assert result.returncode == 3
        error = json_output(result)
        assert error["status"] == "error"
        assert error["code"] == "query-rejected"

    oversized_query = tmp_path / "oversized.rq"
    oversized_query.write_text(
        "SELECT * WHERE { ?s ?p ?o } #" + ("x" * (64 * 1024)), encoding="utf-8"
    )
    too_large = run_query(
        "sparql",
        "--query-file",
        str(oversized_query),
        "--format",
        "json",
    )
    assert too_large.returncode == 3
    assert json_output(too_large)["code"] == "query-rejected"


def test_snapshot_gate_exact_paths_and_consultation_are_immutable(tmp_path: Path) -> None:
    support = load_script("_consult_semantic_okf.py")

    with pytest.raises(support.SnapshotError, match="unsafe query artifact path"):
        support.snapshot_file(BUNDLE, "../outside.txt")
    with pytest.raises(support.SnapshotError, match="unsafe concept_path"):
        support.safe_concept_path(BUNDLE, "../semantic/data.ttl")
    with pytest.raises(support.SnapshotError, match="unsafe concept_path"):
        support.safe_concept_path(BUNDLE, "concepts\\guessed.md")
    with pytest.raises(support.SnapshotError, match="escapes or is missing"):
        support.safe_concept_path(BUNDLE, "concepts/guessed-deadbeef00.md")

    invalid = tmp_path / "invalid"
    (invalid / "semantic").mkdir(parents=True)
    (invalid / "semantic" / "build-report.json").write_text(
        json.dumps({"status": "fail", "valid": False}), encoding="utf-8"
    )
    with pytest.raises(support.SnapshotError, match="passing snapshot"):
        support.validate_snapshot(invalid, full_read_surface=False)

    before = tree_sha256(BUNDLE)
    validated = run_query(
        "ledger",
        "--source-id",
        PAPER_SOURCE,
        "--validate",
        "--format",
        "paths",
    )
    assert validated.returncode == 0, validated.stderr
    assert validated.stdout.strip().startswith(f"concepts/{PAPER_SOURCE}/")
    after = tree_sha256(BUNDLE)
    assert after == before


def test_cross_source_planner_is_deterministic_aligned_and_immutable() -> None:
    before = tree_sha256(BUNDLE)
    args = [*cross_source_args(), "--alternate-limit", "3"]
    first = run_prepare(*args)
    second = run_prepare(*args)

    assert first.returncode == 0, first.stderr
    assert second.returncode == 0, second.stderr
    assert first.stdout == second.stdout
    payload = json_output(first)
    assert payload["status"] == "pass"
    assert payload["mode"] == "read-only"
    assert payload["source_gate"] == {
        "hard_minimum": 5,
        "reserve": 5,
        "required_total": 10,
        "selected": 10,
        "available": 15,
    }
    selected = payload["selected_papers"]
    seed = payload["response_seed"]
    paper_ids = sorted(item["paper_id"] for item in selected)
    assert seed["answer"]["paper_ids"] == paper_ids
    assert [item["paper_id"] for item in seed["answer"]["citations"]] == paper_ids
    assert seed["answer"]["dimensions"] == sorted(CROSS_SOURCE_DIMENSIONS)
    assert seed["evidence"] == sorted(set(seed["evidence"]))
    assert len(seed["evidence"]) <= len(selected) + len(CROSS_SOURCE_DIMENSIONS)
    for item in selected:
        assert item["selection_score"] > 0
        assert item["rank_components"]["matched_dimensions"] > 0
        assert item["selected_claims"]
    for path in seed["evidence"]:
        assert (BUNDLE / path).is_file()
    assert tree_sha256(BUNDLE) == before


def test_cross_source_preflight_passes_seed_and_exposes_independent_counts() -> None:
    planned = run_prepare(*cross_source_args(), "--alternate-limit", "0")
    assert planned.returncode == 0, planned.stderr
    seed = json_output(planned)["response_seed"]
    seed["answer"]["summary"] = " ".join(["grounded"] * 200)

    result = run_preflight(
        json.dumps(seed, ensure_ascii=False),
        *cross_source_args(),
        "--min-words",
        "180",
        "--max-words",
        "300",
    )

    assert result.returncode == 0, result.stdout
    report = json_output(result)
    assert report["status"] == "pass"
    assert report["errors"] == []
    assert report["normalized_response_status"] == "pass"
    assert report["counts"] == {
        "summary_words": 200,
        "paper_ids": 10,
        "citation_sources": 10,
        "claim_evidence_sources": 10,
        "locally_relevant_sources": 10,
        "required_dimensions": 4,
        "required_dimensions_covered": 4,
        "required_source_total": 10,
    }


def test_cross_source_preflight_repairs_safe_ordering_but_rejects_guesses() -> None:
    planned = run_prepare(*cross_source_args(), "--alternate-limit", "0")
    seed = json_output(planned)["response_seed"]
    seed["answer"]["summary"] = " ".join(["grounded"] * 200)
    seed["evidence"] = list(reversed(seed["evidence"]))

    unsorted = run_preflight(json.dumps(seed), *cross_source_args())
    assert unsorted.returncode == 3
    report = json_output(unsorted)
    assert report["status"] == "fail"
    assert {item["code"] for item in report["errors"]} == {"evidence-order"}
    assert report["normalized_response_status"] == "pass"
    assert report["normalized_response"]["evidence"] == sorted(seed["evidence"])

    canonical = report["normalized_response"]
    exact = canonical["evidence"][0]
    canonical["evidence"][0] = f"{exact[:-4]}ffff.md"
    guessed = run_preflight(json.dumps(canonical), *cross_source_args())
    assert guessed.returncode == 3
    guess_report = json_output(guessed)
    guess_errors = [
        item for item in guess_report["errors"] if item["code"] == "unknown-evidence-path"
    ]
    assert guess_errors
    assert "exact ledger concept_path" in guess_errors[0]["repair"]
    assert guess_report["normalized_response_status"] == "needs-semantic-repair"


def test_cross_source_preflight_rejects_duplicate_or_trailing_json() -> None:
    duplicate = (
        '{"question_id":"integration-cross-source",'
        '"question_id":"integration-cross-source","answer":{},"evidence":[]}'
    )
    duplicated = run_preflight(duplicate, *cross_source_args())
    assert duplicated.returncode == 3
    assert json_output(duplicated)["errors"][0]["code"] == "candidate-parse"
    assert "duplicate JSON object key" in duplicated.stdout

    trailing = run_preflight('{"question_id":"x"} {"evidence":[]}', *cross_source_args())
    assert trailing.returncode == 3
    assert json_output(trailing)["errors"][0]["code"] == "candidate-parse"
