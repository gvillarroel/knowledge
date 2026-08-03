from __future__ import annotations

import importlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from types import ModuleType

import pytest
import yaml

from tika_mallet_test_support import (
    CONSULT_ROOT,
    CONSULT_SCRIPTS,
    build_portable_bundle,
    tree_hashes,
)


QUERY = CONSULT_SCRIPTS / "query_semantic_okf_tika_mallet.py"


@pytest.fixture(scope="module")
def bundle(tmp_path_factory: pytest.TempPathFactory) -> Path:
    root = tmp_path_factory.mktemp("consult-tika-mallet")
    output, *_ = build_portable_bundle(root)
    return output


def run_query(bundle_path: Path, *args: str) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment.pop("PYTHONPATH", None)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run(
        [sys.executable, "-B", str(QUERY), str(bundle_path), *args],
        cwd=CONSULT_ROOT,
        env=environment,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=60,
        check=False,
    )


def load_consult_module() -> ModuleType:
    for name in ("_safe_paths", "_mallet_topics", "_tika_snapshot", "_tika_mallet_snapshot"):
        sys.modules.pop(name, None)
    sys.path.insert(0, str(CONSULT_SCRIPTS))
    try:
        return importlib.import_module("_tika_mallet_snapshot")
    finally:
        sys.path.remove(str(CONSULT_SCRIPTS))


def test_skill_metadata_runtime_and_okf_projection_are_complete() -> None:
    skill = (CONSULT_ROOT / "SKILL.md").read_text(encoding="utf-8")
    metadata = yaml.safe_load(skill.split("---", 2)[1])
    package_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in CONSULT_ROOT.rglob("*")
        if path.is_file() and path.suffix in {".md", ".py", ".yaml"}
    )

    assert set(metadata) == {"name", "description"}
    assert metadata["name"] == "consult-semantic-okf-tika-mallet"
    assert "read-only" in metadata["description"]
    assert "## Standalone and read-only boundary" in skill
    assert "--deep-validation" in skill
    assert "TODO" not in package_text
    assert "pyrmallet" not in package_text.casefold()
    assert "subprocess" not in (
        CONSULT_SCRIPTS / "_tika_mallet_snapshot.py"
    ).read_text(encoding="utf-8")
    requirements = (CONSULT_SCRIPTS / "requirements.txt").read_text(encoding="utf-8")
    assert "pyyaml==6.0.3" in requirements
    assert "$consult-semantic-okf-tika-mallet" in (
        CONSULT_ROOT / "agents" / "openai.yaml"
    ).read_text(encoding="utf-8")
    assert (CONSULT_ROOT / "references" / "tika-mallet-format.md").is_file()
    assert (CONSULT_ROOT / "references" / "querying.md").is_file()
    assert "paired builder skill" not in package_text


def test_consultant_replays_verbatim_contract_and_ascii_tokenization() -> None:
    module = load_consult_module()
    tika = sys.modules["_tika_snapshot"]
    source = {
        "id": "canonical-text",
        "path": "sources/canonical.md",
        "concept_type": "Canonical Text",
        "body_mode": "utf8-verbatim-tika-verified",
    }
    plan = {"sources": [source]}
    frontmatter, body = tika._split_frontmatter(
        "---\ntika_handler: utf8-verbatim-tika-metadata-verified-v1\n"
        "---\nAlpha\nβeta\u001fvalue\nOmega\n"
    )

    assert tika._handler(source) == (
        "utf8-verbatim-tika-metadata-verified-v1"
    )
    assert tika._plan_algorithm(plan) == (
        "apache-tika-4.0.0-beta-1-hybrid-markdown-or-"
        "utf8-verbatim-verified-v1"
    )
    assert frontmatter["tika_handler"] == tika.VERBATIM_HANDLER
    assert body == "Alpha\nβeta\u001fvalue\nOmega"
    assert module.TOKEN_RE.findall("ıve") == ["ve"]
    assert all(term.isascii() for term in module.TOKEN_RE.findall("naïve ıve"))


def test_structural_inspection_validates_tika_mallet_and_preserves_tree(
    bundle: Path,
) -> None:
    before = tree_hashes(bundle)
    completed = run_query(bundle, "inspect")
    after = tree_hashes(bundle)

    assert completed.returncode == 0, completed.stdout + completed.stderr
    result = json.loads(completed.stdout)
    assert result["status"] == "pass"
    assert result["authoritative"] is False
    assert result["discovery_only"] is True
    assert result["validation"] == {
        "structural": True,
        "independent_rederivation": False,
    }
    assert result["tika"]["tika_version"] == "4.0.0-beta-1"
    assert result["mallet"]["version"] == "2.1.0"
    assert result["mallet"]["algorithm"] == (
        "mallet-2.1.0-parallel-topic-model-v1"
    )
    assert result["summary"]["documents"] == 2
    assert before == after


@pytest.mark.parametrize("mode", ["bm25", "topic", "association", "fusion"])
def test_all_search_modes_return_exact_authoritative_locators(
    bundle: Path, mode: str
) -> None:
    before = tree_hashes(bundle)
    completed = run_query(
        bundle,
        "search",
        "--query",
        "audit evidence extraction",
        "--mode",
        mode,
        "--top-k",
        "5",
    )
    after = tree_hashes(bundle)

    assert completed.returncode == 0, completed.stdout + completed.stderr
    result = json.loads(completed.stdout)
    assert result["requested_mode"] == result["effective_mode"] == mode
    assert result["authoritative"] is False
    assert result["discovery_only"] is True
    assert result["results"]
    assert set(result["expansion"]) == {
        "association_terms",
        "query_topics",
        "topic_terms",
    }
    assert all(
        row["source"] == "java-mallet-2.1.0-lda"
        for row in result["expansion"]["topic_terms"]
    )
    records = {
        (row["source_id"], row["record_id"]): row
        for row in (
            json.loads(line)
            for line in (bundle / "semantic" / "records.jsonl")
            .read_text(encoding="utf-8")
            .splitlines()
        )
    }
    for hit in result["results"]:
        record = records[(hit["source_id"], hit["record_id"])]
        assert hit["locator"] == {"kind": "record"}
        assert hit["text"] == record["body"]
        assert (bundle / hit["concept_path"]).is_file()
    assert before == after


def test_batch_search_validates_once_and_emits_compact_exact_evidence(
    bundle: Path,
    tmp_path: Path,
) -> None:
    before = tree_hashes(bundle)
    completed = run_query(
        bundle,
        "batch-search",
        "--query",
        "audit evidence",
        "--query",
        "spreadsheet validation",
        "--mode",
        "fusion",
        "--top-k",
        "2",
        "--evidence-only",
    )
    after = tree_hashes(bundle)

    assert completed.returncode == 0, completed.stdout + completed.stderr
    result = json.loads(completed.stdout)
    assert result["status"] == "pass"
    assert result["query_count"] == 2
    assert result["result_view"] == "exact-evidence-excerpt"
    assert [row["query"] for row in result["searches"]] == [
        "audit evidence",
        "spreadsheet validation",
    ]
    expected_fields = {
        "rank",
        "evidence",
        "text_chars",
        "text_excerpt_start",
        "text_excerpt_end",
        "text_excerpt",
    }
    evidence_fields = {
        "source_id",
        "record_id",
        "concept_path",
        "source_path",
        "record_sha256",
        "locator",
        "text_sha256",
    }
    authoritative_passages = {
        row["text_sha256"]: row["text"]
        for row in (
            json.loads(line)
            for line in (bundle / "classical/documents.jsonl")
            .read_text(encoding="utf-8")
            .splitlines()
        )
    }
    for search in result["searches"]:
        assert search["result_view"] == "exact-evidence-excerpt"
        assert search["excerpt_chars"] == 1800
        assert "expansion" not in search
        assert search["results"]
        assert all(set(row) == expected_fields for row in search["results"])
        for row in search["results"]:
            assert set(row["evidence"]) == evidence_fields
            assert len(row["text_excerpt"]) <= 1800
            assert row["text_excerpt_end"] - row["text_excerpt_start"] == len(
                row["text_excerpt"]
            )
            assert row["text_chars"] >= len(row["text_excerpt"])
            text = authoritative_passages[row["evidence"]["text_sha256"]]
            assert row["text_chars"] == len(text)
            assert row["text_excerpt"] == text[
                row["text_excerpt_start"] : row["text_excerpt_end"]
            ]
    assert before == after

    selected: list[dict[str, object]] = []
    serialized: set[str] = set()
    for search in result["searches"]:
        for row in search["results"]:
            key = json.dumps(row["evidence"], sort_keys=True)
            if key not in serialized:
                serialized.add(key)
                selected.append(row["evidence"])
            if len(selected) == 2:
                break
        if len(selected) == 2:
            break
    assert len(selected) == 2
    candidate = {
        "question_id": "q999",
        "answer": {
            "summary": "The exact retrieved evidence supports the test response.",
            "claims": [
                {"statement": "First supported claim.", "evidence_indices": [0]},
                {"statement": "Second supported claim.", "evidence_indices": [1]},
            ],
        },
        "evidence": selected,
    }
    answer_path = tmp_path / "candidate-answer.json"
    answer_path.write_text(
        json.dumps(candidate, ensure_ascii=False),
        encoding="utf-8",
    )
    validated = run_query(
        bundle,
        "validate-answer",
        "--answer",
        str(answer_path),
    )
    assert validated.returncode == 0, validated.stdout + validated.stderr
    validation = json.loads(validated.stdout)
    assert validation["status"] == "pass"
    assert validation["first_use_order"] is True
    assert validation["exact_evidence"] is True
    assert validation["evidence_count"] == 2

    candidate["answer"]["claims"][0]["evidence_indices"] = [1]
    candidate["answer"]["claims"][1]["evidence_indices"] = [0]
    answer_path.write_text(
        json.dumps(candidate, ensure_ascii=False),
        encoding="utf-8",
    )
    wrong_order = run_query(
        bundle,
        "validate-answer",
        "--answer",
        str(answer_path),
    )
    assert wrong_order.returncode == 2
    assert "first-use order" in json.loads(wrong_order.stdout)["error"]
    candidate["answer"]["claims"][0]["evidence_indices"] = [0]
    candidate["answer"]["claims"][1]["evidence_indices"] = [1]
    candidate["evidence"][0]["concept_path"] += ".drift"
    answer_path.write_text(
        json.dumps(candidate, ensure_ascii=False),
        encoding="utf-8",
    )
    rejected = run_query(
        bundle,
        "validate-answer",
        "--answer",
        str(answer_path),
    )
    assert rejected.returncode == 2
    assert "not an exact validated consultation hit" in json.loads(
        rejected.stdout
    )["error"]

    duplicate = run_query(
        bundle,
        "batch-search",
        "--query",
        "audit evidence",
        "--query",
        "audit evidence",
        "--evidence-only",
    )
    assert duplicate.returncode == 2
    assert "distinct" in json.loads(duplicate.stdout)["error"]


def test_answer_pack_and_finalizer_bound_context_and_compile_exact_evidence(
    bundle: Path,
    tmp_path: Path,
) -> None:
    before = tree_hashes(bundle)
    pack_path = tmp_path / "answer-pack.json"
    packed = run_query(
        bundle,
        "answer-pack",
        "--query",
        "audit evidence",
        "--query",
        "spreadsheet validation",
        "--mode",
        "fusion",
        "--top-k",
        "6",
        "--max-sources",
        "4",
        "--output",
        str(pack_path),
    )

    assert packed.returncode == 0, packed.stdout + packed.stderr
    pack = json.loads(packed.stdout)
    assert json.loads(pack_path.read_text(encoding="utf-8")) == pack
    assert pack["schema_version"] == "semantic-okf-tika-mallet-answer-pack/1.0"
    assert pack["query_count"] == 2
    assert 2 <= pack["source_count"] <= 4
    assert [row["support_id"] for row in pack["results"]] == [
        f"s{index:02d}" for index in range(1, pack["source_count"] + 1)
    ]
    assert len({row["evidence"]["source_id"] for row in pack["results"]}) == pack[
        "source_count"
    ]
    assert all(len(row["text_excerpt"]) <= 1200 for row in pack["results"])

    first, second = pack["results"][0]["support_id"], pack["results"][1]["support_id"]
    draft = {
        "question_id": "q999",
        "summary": "The compact support pack grounds both parts of this answer.",
        "claims": [
            {"statement": "Second support is used first.", "support_ids": [second]},
            {"statement": "First support is used next.", "support_ids": [first]},
        ],
    }
    draft_path = tmp_path / "answer-draft.json"
    draft_path.write_text(json.dumps(draft), encoding="utf-8")
    final_path = tmp_path / "final-answer.json"
    finalized = run_query(
        bundle,
        "finalize-answer",
        "--pack",
        str(pack_path),
        "--draft",
        str(draft_path),
        "--output",
        str(final_path),
    )

    assert finalized.returncode == 0, finalized.stdout + finalized.stderr
    confirmation = json.loads(finalized.stdout)
    assert confirmation["status"] == "pass"
    assert confirmation["support_count"] == 2
    answer = json.loads(final_path.read_text(encoding="utf-8"))
    assert list(answer) == ["question_id", "answer", "evidence"]
    assert answer["answer"]["claims"][0]["evidence_indices"] == [0]
    assert answer["answer"]["claims"][1]["evidence_indices"] == [1]
    evidence_by_support = {
        row["support_id"]: row["evidence"] for row in pack["results"]
    }
    assert answer["evidence"] == [
        evidence_by_support[second],
        evidence_by_support[first],
    ]
    assert tree_hashes(bundle) == before

    no_replace = run_query(
        bundle,
        "finalize-answer",
        "--pack",
        str(pack_path),
        "--draft",
        str(draft_path),
        "--output",
        str(final_path),
    )
    assert no_replace.returncode == 2
    assert "refusing to overwrite" in json.loads(no_replace.stdout)["error"]


def test_filters_are_applied_before_ranking(bundle: Path) -> None:
    completed = run_query(
        bundle,
        "search",
        "--query",
        "audit evidence",
        "--mode",
        "fusion",
        "--source-id",
        "pdf-documents",
        "--concept-type",
        "PDF Document",
    )

    assert completed.returncode == 0
    result = json.loads(completed.stdout)
    assert result["filters"] == {
        "source_ids": ["pdf-documents"],
        "concept_ids": [],
        "concept_types": ["PDF Document"],
    }
    assert result["results"]
    assert {row["source_id"] for row in result["results"]} == {"pdf-documents"}


def test_deep_validation_requires_explicit_runtime_and_is_read_only(
    bundle: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = load_consult_module()
    with pytest.raises(module.SnapshotError, match="requires both"):
        module.load_snapshot(bundle, deep_validation=True)

    ordinary = module.load_snapshot(bundle)
    binding = ordinary.index["toolchain"]
    runtime = module.MalletRuntime(
        java=Path("java"),
        java_version=binding["java_version"],
        mallet_home=Path("mallet"),
        mallet_version=binding["mallet_version"],
        jar_inventory=tuple(binding["mallet_jar_inventory"]),
        jar_tree_sha256=binding["mallet_jar_tree_sha256"],
    )
    monkeypatch.setattr(module, "preflight_mallet", lambda java, home: runtime)

    def derived(
        records: object,
        plan: object,
        supplied: object,
        *,
        forbidden_roots: object = (),
    ) -> tuple[object, ...]:
        del records, plan
        assert supplied is runtime
        assert tuple(forbidden_roots) == (bundle, runtime.mallet_home)
        return (
            json.loads(json.dumps(list(ordinary.documents))),
            json.loads(json.dumps(ordinary.lexicon)),
            json.loads(json.dumps(list(ordinary.associations))),
            json.loads(json.dumps(ordinary.topics)),
        )

    monkeypatch.setattr(module, "_derive_all", derived)
    before = tree_hashes(bundle)
    deep = module.load_snapshot(
        bundle,
        deep_validation=True,
        java=Path("java"),
        mallet_home=Path("mallet"),
    )
    after = tree_hashes(bundle)

    assert deep.deep_validation is True
    assert module.inspect_snapshot(deep)["validation"]["independent_rederivation"] is True
    assert before == after


def test_tika_metadata_tamper_is_rejected_before_search(
    bundle: Path, tmp_path: Path
) -> None:
    tampered = tmp_path / "tampered"
    shutil.copytree(bundle, tampered)
    metadata = next((tampered / "tika" / "metadata").rglob("*.json"))
    payload = json.loads(metadata.read_text(encoding="utf-8"))
    payload["Content-Type"] = "application/octet-stream"
    metadata.write_text(json.dumps(payload), encoding="utf-8")

    completed = run_query(tampered, "inspect")

    assert completed.returncode == 2
    result = json.loads(completed.stdout)
    assert result["code"] == "tika-mallet-error"
    assert "metadata" in result["error"].casefold()


def test_closed_classical_tree_and_toolchain_binding_reject_tamper(
    bundle: Path, tmp_path: Path
) -> None:
    unknown = tmp_path / "unknown"
    shutil.copytree(bundle, unknown)
    (unknown / "classical" / "cache.bin").write_bytes(b"not allowed")
    completed = run_query(unknown, "inspect")
    assert completed.returncode == 2
    assert "closed" in json.loads(completed.stdout)["error"]

    toolchain = tmp_path / "toolchain"
    shutil.copytree(bundle, toolchain)
    index_path = toolchain / "classical" / "index.json"
    index = json.loads(index_path.read_text(encoding="utf-8"))
    index["toolchain"]["mallet_version"] = "2.0.8"
    index_path.write_text(json.dumps(index), encoding="utf-8")
    completed = run_query(toolchain, "inspect")
    assert completed.returncode == 2
    assert "version" in json.loads(completed.stdout)["error"].casefold()


def test_closed_concept_tree_rejects_unknown_and_linked_entries(
    bundle: Path, tmp_path: Path
) -> None:
    unknown = tmp_path / "unknown-concept-directory"
    shutil.copytree(bundle, unknown)
    (unknown / "concepts" / "unbound-empty-directory").mkdir()
    completed = run_query(unknown, "inspect")
    assert completed.returncode == 2
    assert "concept tree" in json.loads(completed.stdout)["error"].casefold()

    linked = tmp_path / "linked-concept-directory"
    shutil.copytree(bundle, linked)
    target = next(path for path in (linked / "concepts").iterdir() if path.is_dir())
    alias = linked / "concepts" / "linked-alias"
    try:
        alias.symlink_to(target, target_is_directory=True)
    except OSError:
        return
    completed = run_query(linked, "inspect")
    assert completed.returncode == 2
    assert any(
        marker in json.loads(completed.stdout)["error"].casefold()
        for marker in ("symbolic link", "reparse point")
    )


def test_deep_scratch_rejects_bundle_temp_root(
    bundle: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    load_consult_module()
    mallet = sys.modules["_mallet_topics"]
    before = tree_hashes(bundle)
    monkeypatch.setattr(mallet.tempfile, "gettempdir", lambda: str(bundle))

    with pytest.raises(mallet.MalletRuntimeError, match="temporary root is inside"):
        with mallet._private_scratch((bundle,)):
            pytest.fail("unsafe scratch was created")

    assert tree_hashes(bundle) == before


def test_cli_rejects_external_runtime_without_deep_validation(bundle: Path) -> None:
    completed = run_query(bundle, "inspect", "--java", "java")

    assert completed.returncode == 2
    result = json.loads(completed.stdout)
    assert result["code"] == "tika-mallet-error"
    assert "only accepted" in result["error"]


def test_stored_mallet_toolchain_rejects_unsafe_or_incomplete_jar_paths() -> None:
    module = load_consult_module()
    valid = {
        "java_version": 'openjdk version "17.0.12"',
        "mallet_jar_inventory": [
            {"path": "lib/mallet-2.1.0.jar", "sha256": "a" * 64}
        ],
        "mallet_jar_tree_sha256": "",
        "mallet_version": "2.1.0",
    }
    valid["mallet_jar_tree_sha256"] = module.sha256_canonical(
        valid["mallet_jar_inventory"]
    )
    assert module.validate_toolchain(valid)["mallet_version"] == "2.1.0"

    unsafe = json.loads(json.dumps(valid))
    unsafe["mallet_jar_inventory"][0]["path"] = "C:/mallet.jar"
    unsafe["mallet_jar_tree_sha256"] = module.sha256_canonical(
        unsafe["mallet_jar_inventory"]
    )
    with pytest.raises(module.MalletRuntimeError, match="malformed"):
        module.validate_toolchain(unsafe)
