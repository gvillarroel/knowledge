from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Any, Callable

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPO_ROOT / "skills" / "consult-semantic-okf-embeddings"
SCRIPTS = SKILL_ROOT / "scripts"
QUERY = SCRIPTS / "query_semantic_okf_embeddings.py"
RUNTIME_SMOKE = SCRIPTS / "runtime_smoke.py"
def canonical_json(value: Any) -> str:
    """Mirror the public canonical JSON contract without importing the implementation."""

    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def file_sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def write_json(path: Path, value: Any) -> None:
    path.write_text(f"{canonical_json(value)}\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text(
        "".join(f"{canonical_json(row)}\n" for row in rows),
        encoding="utf-8",
    )


def core_tree_sha256(root: Path) -> str:
    members = []
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        relative = path.relative_to(root)
        if relative.parts[0] == "retrieval":
            continue
        members.append({"path": relative.as_posix(), "sha256": file_sha256(path)})
    return sha256_bytes(canonical_json(members).encode("utf-8"))


def tree_sha256(root: Path) -> str:
    members = [
        {"path": path.relative_to(root).as_posix(), "sha256": file_sha256(path)}
        for path in sorted(item for item in root.rglob("*") if item.is_file())
    ]
    return sha256_bytes(canonical_json(members).encode("utf-8"))


def hashing_vector(text: str, dimension: int = 8) -> list[float]:
    values = [0.0] * dimension
    for token in re.findall(r"\w+", text.casefold(), flags=re.UNICODE):
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        bucket = int.from_bytes(digest[:8], "big") % dimension
        values[bucket] += 1.0 if digest[8] & 1 else -1.0
    norm = math.sqrt(sum(item * item for item in values))
    if norm == 0:
        digest = hashlib.sha256(b"fallback\0" + text.encode("utf-8")).digest()
        values[int.from_bytes(digest[:8], "big") % dimension] = 1.0
        norm = 1.0
    first = [round(item / norm, 8) for item in values]
    second_norm = math.sqrt(sum(item * item for item in first))
    return [round(item / second_norm, 8) for item in first]


def expected_chunk_id(row: dict[str, Any]) -> str:
    identity = {
        "source_id": row["source_id"],
        "record_id": row["record_id"],
        "record_sha256": row["record_sha256"],
        "ordinal": row["ordinal"],
        "text_sha256": row["text_sha256"],
    }
    return "chunk-" + sha256_bytes(canonical_json(identity).encode("utf-8"))[:32]


def write_retrieval_report(root: Path) -> None:
    """Reconstruct the builder's closed retrieval report from live fixture files."""

    retrieval = root / "retrieval"
    index_path = retrieval / "index.json"
    chunks_path = retrieval / "chunks.jsonl"
    embeddings_path = retrieval / "embeddings.jsonl"
    index = json.loads(index_path.read_text(encoding="utf-8"))
    records = read_rows(root / "semantic" / "records.jsonl")
    chunks = read_rows(chunks_path)
    embeddings = read_rows(embeddings_path)
    eligible = set(index["selection"]["eligible_source_ids"])
    report = {
        "schema_version": "1.0",
        "valid": True,
        "status": "pass",
        "errors": [],
        "warnings": [],
        "retrieval_plan_sha256": index["retrieval_plan_sha256"],
        "core": index["core"],
        "selection": index["selection"],
        "summary": {
            "inputs": index["selection"]["input_count"],
            "records": sum(row["source_id"] in eligible for row in records),
            "chunks": len(chunks),
            "embeddings": len(embeddings),
            "dimension": index["embedding"]["dimension"],
        },
        "artifacts": {
            "index": {
                "path": "retrieval/index.json",
                "sha256": file_sha256(index_path),
            },
            "chunks": {
                "path": "retrieval/chunks.jsonl",
                "sha256": file_sha256(chunks_path),
                "count": len(chunks),
            },
            "embeddings": {
                "path": "retrieval/embeddings.jsonl",
                "sha256": file_sha256(embeddings_path),
                "count": len(embeddings),
            },
        },
    }
    write_json(retrieval / "build-report.json", report)


def load_support() -> ModuleType:
    path = SCRIPTS / "_embedding_snapshot.py"
    spec = importlib.util.spec_from_file_location("_embedding_snapshot", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def build_bundle(
    root: Path,
    *,
    vectors: dict[str, list[float]] | None = None,
) -> Path:
    """Create a small valid snapshot without using implementation code under test."""

    semantic = root / "semantic"
    concepts = root / "concepts"
    retrieval = root / "retrieval"
    semantic.mkdir(parents=True)
    concepts.mkdir()

    bodies = {
        "concept-a": "Database backups must be retained for thirty days.",
        "concept-b": "New employees receive access on their first day.",
        "concept-c": "The incident response plan requires weekly drills.",
    }
    sources = {"concept-a": "alpha", "concept-b": "beta", "concept-c": "alpha"}
    records: list[dict[str, Any]] = []
    for concept_id in sorted(bodies):
        source_id = sources[concept_id]
        concept_path = f"concepts/{concept_id}.md"
        body = bodies[concept_id]
        (root / concept_path).write_text(
            f"---\ntype: Note\ntitle: {concept_id}\n---\n\n{body}\n",
            encoding="utf-8",
        )
        records.append(
            {
                "attributes": {"topic": concept_id.removeprefix("concept-")},
                "body": body,
                "concept_id": concept_id,
                "concept_path": concept_path,
                "concept_type": "Note",
                "record_id": f"record-{concept_id[-1]}",
                "record_sha256": sha256_bytes(f"record:{concept_id}:{body}".encode("utf-8")),
                "source_id": source_id,
                "source_path": f"sources/{source_id}.md",
                "subject_iri": f"https://example.test/resource/{concept_id}",
                "title": concept_id,
            }
        )
    write_jsonl(semantic / "records.jsonl", records)
    source_entries = [
        {
            "id": source_id,
            "content_sha256": sha256_bytes(f"source:{source_id}".encode("utf-8")),
        }
        for source_id in ("alpha", "beta")
    ]
    write_json(
        semantic / "source-manifest.json",
        {"schema_version": "1.0", "sources": source_entries},
    )
    write_json(semantic / "build-report.json", {"status": "pass", "valid": True})
    write_json(semantic / "semantic-plan.json", {"bundle": {"title": "fixture"}})
    for name in (
        "data.ttl",
        "ontology.ttl",
        "provenance.ttl",
        "shapes.ttl",
        "validation-report.ttl",
    ):
        (semantic / name).write_text("# fixture\n", encoding="utf-8")
    (root / "index.md").write_text(
        '---\nokf_version: "0.1"\n---\n\n# Fixture\n', encoding="utf-8"
    )

    core_hash = core_tree_sha256(root)
    records_by_concept = {row["concept_id"]: row for row in records}
    chunk_rows: list[dict[str, Any]] = []
    for concept_id in sorted(bodies):
        record = records_by_concept[concept_id]
        text = bodies[concept_id]
        row = {
            "source_id": record["source_id"],
            "record_id": record["record_id"],
            "concept_id": concept_id,
            "concept_path": record["concept_path"],
            "record_sha256": record["record_sha256"],
            "source_path": record["source_path"],
            "locator": {"kind": "record"},
            "ordinal": 0,
            "text": text,
            "text_sha256": sha256_bytes(text.encode("utf-8")),
        }
        row["chunk_id"] = expected_chunk_id(row)
        chunk_rows.append(row)
    chunk_rows.sort(key=lambda row: row["chunk_id"])
    retrieval.mkdir()
    write_jsonl(retrieval / "chunks.jsonl", chunk_rows)
    vector_values = vectors or {
        row["concept_id"]: hashing_vector(row["text"]) for row in chunk_rows
    }
    embedding_rows = [
        {"chunk_id": row["chunk_id"], "vector": vector_values[row["concept_id"]]}
        for row in chunk_rows
    ]
    write_jsonl(retrieval / "embeddings.jsonl", embedding_rows)

    selected_inputs = [
        {"source_id": item["id"], "content_sha256": item["content_sha256"]}
        for item in source_entries
    ]
    index = {
        "schema_version": "1.0",
        "authoritative": False,
        "core": {
            "tree_sha256": core_hash,
            "records_sha256": file_sha256(semantic / "records.jsonl"),
            "record_count": len(records),
        },
        "retrieval_plan_sha256": sha256_bytes(canonical_json({"fixture": 1}).encode("utf-8")),
        "selection": {
            "requested_source_ids": ["alpha", "beta"],
            "eligible_source_ids": ["alpha", "beta"],
            "excluded_source_ids": [],
            "input_count": 2,
            "input_sha256": sha256_bytes(canonical_json(selected_inputs).encode("utf-8")),
        },
        "chunking": {
            "implementation": "native",
            "strategy": "record",
            "buffer_size": 1,
            "breakpoint_percentile_threshold": 95,
        },
        "embedding": {
            "provider": "hashing",
            "model_id": "knowledge-hashing-embedding",
            "revision": "1",
            "dimension": 8,
            "normalize": True,
            "vector_precision": 8,
            "metric": "cosine",
            "encoding": {"document": "symmetric", "query": "symmetric"},
        },
        "artifacts": {
            "chunks": {
                "path": "retrieval/chunks.jsonl",
                "sha256": file_sha256(retrieval / "chunks.jsonl"),
                "count": len(chunk_rows),
            },
            "embeddings": {
                "path": "retrieval/embeddings.jsonl",
                "sha256": file_sha256(retrieval / "embeddings.jsonl"),
                "count": len(embedding_rows),
            },
        },
        "chunk_count": len(chunk_rows),
        "embedding_count": len(embedding_rows),
    }
    write_json(retrieval / "index.json", index)
    write_retrieval_report(root)
    return root


def run_cli(bundle: Path, *args: str, script: Path = QUERY) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment.pop("PYTHONPATH", None)
    return subprocess.run(
        [sys.executable, str(script), str(bundle), *args],
        cwd=script.parents[1],
        env=environment,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=60,
        check=False,
    )


def read_rows(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def rewrite_artifact(bundle: Path, name: str, rows: list[dict[str, Any]]) -> None:
    artifact = bundle / "retrieval" / f"{name}.jsonl"
    write_jsonl(artifact, rows)
    index_path = bundle / "retrieval" / "index.json"
    index = json.loads(index_path.read_text(encoding="utf-8"))
    index["artifacts"][name]["sha256"] = file_sha256(artifact)
    index["artifacts"][name]["count"] = len(rows)
    singular = "chunk_count" if name == "chunks" else "embedding_count"
    index[singular] = len(rows)
    write_json(index_path, index)
    write_retrieval_report(bundle)


def rewrite_index(bundle: Path, mutate: Callable[[dict[str, Any]], None]) -> None:
    index_path = bundle / "retrieval" / "index.json"
    index = json.loads(index_path.read_text(encoding="utf-8"))
    mutate(index)
    write_json(index_path, index)
    write_retrieval_report(bundle)


def test_metadata_resources_and_no_placeholders() -> None:
    skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
    metadata = (SKILL_ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
    assert "name: consult-semantic-okf-embeddings" in skill
    assert "## Standalone boundary" in skill
    assert "## Read-only boundary" in skill
    assert "discovery" in skill.lower()
    assert "query_semantic_okf_embeddings.py" in skill
    assert "TODO" not in skill
    assert "$consult-semantic-okf-embeddings" in metadata
    assert (SKILL_ROOT / "references" / "retrieval-format.md").is_file()
    assert (SKILL_ROOT / "references" / "querying.md").is_file()
    requirements = (SCRIPTS / "requirements-embeddings.txt").read_text(encoding="utf-8")
    assert requirements.endswith(
        "huggingface-hub==1.23.0\nsentence-transformers==5.6.0\n"
    )
    for path in SKILL_ROOT.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        assert "build-semantic-okf" not in text
        assert "consult-semantic-okf/scripts" not in text


def test_standard_library_runtime_smoke_passes() -> None:
    result = subprocess.run(
        [sys.executable, str(RUNTIME_SMOKE)],
        cwd=SKILL_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=30,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "pass"
    assert payload["base_runtime"] == "stdlib"
    assert payload["network"] == "none"


def test_inspect_validates_hashes_and_is_immutable(tmp_path: Path) -> None:
    bundle = build_bundle(tmp_path / "bundle")
    before = tree_sha256(bundle)
    result = run_cli(bundle, "inspect")
    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "pass"
    assert payload["read_only"] is True
    assert payload["discovery_only"] is True
    assert payload["counts"] == {"sources": 2, "records": 3, "chunks": 3, "embeddings": 3}
    assert payload["embedding"]["runtime"] == "available"
    assert payload["hashes"]["core_tree_sha256"] == core_tree_sha256(bundle)
    assert tree_sha256(bundle) == before


@pytest.mark.parametrize("case", ["missing", "unknown", "directory"])
def test_retrieval_artifact_set_is_closed_and_regular(tmp_path: Path, case: str) -> None:
    bundle = build_bundle(tmp_path / "bundle")
    retrieval = bundle / "retrieval"
    if case == "missing":
        (retrieval / "build-report.json").unlink()
    elif case == "unknown":
        (retrieval / "cache.bin").write_bytes(b"undeclared")
    else:
        (retrieval / "build-report.json").unlink()
        (retrieval / "build-report.json").mkdir()
    support = load_support()
    expected = "artifact set is closed" if case != "directory" else "regular non-symlink"
    with pytest.raises(support.SnapshotError, match=expected):
        support.load_snapshot(bundle)


def test_retrieval_artifact_symlink_is_rejected(tmp_path: Path) -> None:
    bundle = build_bundle(tmp_path / "bundle")
    report = bundle / "retrieval" / "build-report.json"
    target = tmp_path / "report-target.json"
    report.replace(target)
    try:
        report.symlink_to(target)
    except OSError:
        pytest.skip("symlink creation is not permitted on this host")
    support = load_support()
    with pytest.raises(support.SnapshotError, match="regular non-symlink"):
        support.load_snapshot(bundle)


@pytest.mark.parametrize("section", ["core", "selection", "counts", "artifact"])
def test_retrieval_build_report_must_equal_live_validation(
    tmp_path: Path, section: str
) -> None:
    bundle = build_bundle(tmp_path / "bundle")
    report_path = bundle / "retrieval" / "build-report.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    if section == "core":
        report["core"]["tree_sha256"] = "0" * 64
    elif section == "selection":
        report["selection"]["input_count"] += 1
    elif section == "counts":
        report["summary"]["chunks"] += 1
    else:
        report["artifacts"]["index"]["sha256"] = "0" * 64
    write_json(report_path, report)
    support = load_support()
    with pytest.raises(support.SnapshotError, match="report differs from live validation"):
        support.load_snapshot(bundle)


def test_index_buffer_size_is_bounded(tmp_path: Path) -> None:
    bundle = build_bundle(tmp_path / "bundle")
    rewrite_index(bundle, lambda index: index["chunking"].__setitem__("buffer_size", 17))
    support = load_support()
    with pytest.raises(support.SnapshotError, match="buffer_size.*1-16"):
        support.load_snapshot(bundle)


@pytest.mark.parametrize("body", [None, ""], ids=["non-string", "empty"])
def test_record_ledger_requires_nonempty_bodies(tmp_path: Path, body: Any) -> None:
    bundle = build_bundle(tmp_path / "bundle")
    records_path = bundle / "semantic" / "records.jsonl"
    records = read_rows(records_path)
    records[0]["body"] = body
    write_jsonl(records_path, records)

    def bind_changed_core(index: dict[str, Any]) -> None:
        index["core"]["records_sha256"] = file_sha256(records_path)
        index["core"]["tree_sha256"] = core_tree_sha256(bundle)

    rewrite_index(bundle, bind_changed_core)
    support = load_support()
    with pytest.raises(support.SnapshotError, match=r"record ledger line 1\.body"):
        support.load_snapshot(bundle)


def test_locator_kind_must_match_chunking_strategy(tmp_path: Path) -> None:
    support = load_support()
    record_bundle = build_bundle(tmp_path / "record")
    record_chunks = read_rows(record_bundle / "retrieval" / "chunks.jsonl")
    record_chunks[0]["locator"] = {
        "kind": "character-range",
        "start": 0,
        "end": len(record_chunks[0]["text"]),
    }
    rewrite_artifact(record_bundle, "chunks", record_chunks)
    with pytest.raises(support.SnapshotError, match="must be 'record' for record chunking"):
        support.load_snapshot(record_bundle)

    semantic_bundle = build_bundle(tmp_path / "semantic")
    rewrite_index(
        semantic_bundle,
        lambda index: index["chunking"].__setitem__("strategy", "semantic"),
    )
    with pytest.raises(
        support.SnapshotError,
        match="must be 'character-range' for semantic chunking",
    ):
        support.load_snapshot(semantic_bundle)


def test_semantic_locator_must_identify_exact_body_substring(tmp_path: Path) -> None:
    bundle = build_bundle(tmp_path / "bundle")
    rewrite_index(bundle, lambda index: index["chunking"].__setitem__("strategy", "semantic"))
    chunks = read_rows(bundle / "retrieval" / "chunks.jsonl")
    for row in chunks:
        row["locator"] = {"kind": "character-range", "start": 0, "end": len(row["text"])}
    chunks[0]["locator"]["end"] -= 1
    rewrite_artifact(bundle, "chunks", chunks)
    support = load_support()
    with pytest.raises(support.SnapshotError, match="exact record text"):
        support.load_snapshot(bundle)


@pytest.mark.parametrize(
    "model_id",
    ("sentence-transformers", "org/re..po", "org/re--po", "org/repo/extra"),
)
def test_sentence_transformer_model_id_is_closed_and_safe(
    tmp_path: Path, model_id: str
) -> None:
    bundle = build_bundle(tmp_path / "bundle")

    def select_provider(index: dict[str, Any]) -> None:
        index["embedding"]["provider"] = "sentence-transformers"
        index["embedding"]["model_id"] = model_id
        index["embedding"]["revision"] = "a" * 40

    rewrite_index(bundle, select_provider)
    support = load_support()
    with pytest.raises(support.SnapshotError, match="namespace/repository"):
        support.load_snapshot(bundle)


def test_sentence_transformer_uses_verified_local_snapshot_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    support = load_support()
    model_id = "sentence-transformers/all-MiniLM-L6-v2"
    revision = "ABCDEF0123456789ABCDEF0123456789ABCDEF01"
    snapshot = tmp_path / revision.lower()
    snapshot.mkdir()
    calls: dict[str, Any] = {}

    def snapshot_download(**kwargs: Any) -> str:
        calls["download"] = kwargs
        calls["download_offline"] = (
            os.environ.get("HF_HUB_OFFLINE"),
            os.environ.get("TRANSFORMERS_OFFLINE"),
        )
        return str(snapshot)

    class FakeModel:
        def __init__(self, path: str, **kwargs: Any) -> None:
            calls["model_path"] = path
            calls["model_kwargs"] = kwargs
            calls["model_offline"] = (
                os.environ.get("HF_HUB_OFFLINE"),
                os.environ.get("TRANSFORMERS_OFFLINE"),
            )

        def encode(self, _texts: list[str], **_kwargs: Any) -> list[list[float]]:
            return [[1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]]

    versions = {
        "sentence-transformers": "5.6.0",
        "huggingface-hub": "1.23.0",
    }
    modules = {
        "sentence_transformers": SimpleNamespace(SentenceTransformer=FakeModel),
        "huggingface_hub": SimpleNamespace(snapshot_download=snapshot_download),
    }
    monkeypatch.setattr(support.importlib.metadata, "version", versions.__getitem__)
    monkeypatch.setattr(support.importlib, "import_module", modules.__getitem__)
    config = {
        "model_id": model_id,
        "revision": revision,
        "dimension": 8,
        "normalize": True,
        "encoding": {"query": "symmetric"},
    }
    vector = support.sentence_transformer_embedding("query", config)
    assert list(vector) == [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    assert calls["download"] == {
        "repo_id": model_id,
        "revision": revision,
        "local_files_only": True,
    }
    assert calls["download_offline"] == ("1", "1")
    assert calls["model_path"] == str(snapshot.resolve())
    assert calls["model_path"] != model_id
    assert calls["model_kwargs"] == {
        "device": "cpu",
        "local_files_only": True,
        "trust_remote_code": False,
    }
    assert calls["model_offline"] == ("1", "1")


@pytest.mark.parametrize("failure", ["missing", "mismatch"])
def test_unavailable_or_mismatched_model_snapshot_is_provider_unavailable(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, failure: str
) -> None:
    support = load_support()
    revision = "a" * 40
    wrong = tmp_path / ("b" * 40)
    wrong.mkdir()

    def snapshot_download(**_kwargs: Any) -> str:
        if failure == "missing":
            raise FileNotFoundError("not cached")
        return str(wrong)

    modules = {"huggingface_hub": SimpleNamespace(snapshot_download=snapshot_download)}
    monkeypatch.setattr(
        support.importlib.metadata,
        "version",
        lambda name: "1.23.0" if name == "huggingface-hub" else "5.6.0",
    )
    monkeypatch.setattr(support.importlib, "import_module", modules.__getitem__)
    config = {
        "model_id": "sentence-transformers/all-MiniLM-L6-v2",
        "revision": revision,
    }
    with pytest.raises(support.ProviderUnavailable, match="snapshot"):
        support._resolve_sentence_transformer_snapshot(config)


def test_lexical_vector_hybrid_filters_and_ties(tmp_path: Path) -> None:
    vectors = {
        "concept-a": [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        "concept-b": [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        "concept-c": [0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    }
    bundle = build_bundle(tmp_path / "bundle", vectors=vectors)
    support = load_support()
    snapshot = support.load_snapshot(bundle)
    fake = lambda _text, _config: [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

    vector = support.search_snapshot(
        snapshot, "conceptual query", requested_mode="vector", top_k=3, embedder=fake
    )
    tied_ids = sorted(
        row["chunk_id"]
        for row in snapshot.chunks
        if row["concept_id"] in {"concept-a", "concept-b"}
    )
    concept_c_id = next(
        row["chunk_id"] for row in snapshot.chunks if row["concept_id"] == "concept-c"
    )
    assert [hit["chunk_id"] for hit in vector["hits"]] == [*tied_ids, concept_c_id]
    assert vector["hits"][0]["scores"]["vector"] == 1.0
    assert vector["hits"][0]["discovery_only"] if "discovery_only" in vector["hits"][0] else True

    hybrid = support.search_snapshot(
        snapshot,
        "employees access",
        requested_mode="hybrid",
        top_k=3,
        embedder=fake,
    )
    assert hybrid["hits"][0]["concept_id"] == "concept-b"
    assert hybrid["hits"][0]["scores"]["hybrid"] is not None

    filtered = support.search_snapshot(
        snapshot,
        "access",
        requested_mode="lexical",
        top_k=3,
        source_ids=["beta"],
        concept_types=["Note"],
    )
    assert filtered["candidate_count"] == 1
    assert [hit["concept_id"] for hit in filtered["hits"]] == ["concept-b"]
    assert filtered["hits"][0]["concept_path"] == "concepts/concept-b.md"
    assert filtered["discovery_only"] is True


def test_hashing_cli_auto_is_deterministic_and_grounded(tmp_path: Path) -> None:
    bundle = build_bundle(tmp_path / "bundle")
    before = tree_sha256(bundle)
    first = run_cli(bundle, "search", "--query", "database backups retained", "--mode", "auto")
    second = run_cli(bundle, "search", "--query", "database backups retained", "--mode", "auto")
    assert first.returncode == 0, first.stdout
    assert first.stdout == second.stdout
    payload = json.loads(first.stdout)
    assert payload["requested_mode"] == "auto"
    assert payload["effective_mode"] == "hybrid"
    assert payload["fallback"] is None
    assert payload["hits"][0]["concept_id"] == "concept-a"
    assert (bundle / payload["hits"][0]["concept_path"]).is_file()
    assert tree_sha256(bundle) == before


def test_provider_fallback_is_explicit_but_explicit_vector_fails(tmp_path: Path) -> None:
    bundle = build_bundle(tmp_path / "bundle")
    support = load_support()
    snapshot = support.load_snapshot(bundle)

    def unavailable(_text: str, _config: dict[str, Any]) -> list[float]:
        raise support.ProviderUnavailable("fixture model is not local")

    automatic = support.search_snapshot(
        snapshot,
        "employees access",
        requested_mode="auto",
        top_k=3,
        embedder=unavailable,
    )
    assert automatic["effective_mode"] == "lexical"
    assert automatic["fallback"] == {
        "code": "embedding-provider-unavailable",
        "from": "hybrid",
        "to": "lexical",
        "reason": "fixture model is not local",
    }
    with pytest.raises(support.ProviderUnavailable):
        support.search_snapshot(
            snapshot,
            "employees access",
            requested_mode="vector",
            top_k=3,
            embedder=unavailable,
        )
    explicit = support.search_snapshot(
        snapshot,
        "employees access",
        requested_mode="vector",
        top_k=3,
        allow_fallback=True,
        embedder=unavailable,
    )
    assert explicit["requested_mode"] == "vector"
    assert explicit["effective_mode"] == "lexical"
    assert explicit["hits"][0]["concept_id"] == "concept-b"


def test_ephemeral_query_vector_uses_builder_precision_rules(tmp_path: Path) -> None:
    bundle = build_bundle(
        tmp_path / "bundle",
        vectors={
            "concept-a": [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            "concept-b": [0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            "concept-c": [0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        },
    )
    support = load_support()
    snapshot = support.load_snapshot(bundle)
    value = 1.0 / math.sqrt(2.0)
    result = support.search_snapshot(
        snapshot,
        "unrounded provider output",
        requested_mode="vector",
        top_k=3,
        embedder=lambda _text, _config: [value, value, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    )
    assert result["effective_mode"] == "vector"
    assert result["hits"][0]["scores"]["vector"] == pytest.approx(value, abs=1e-7)


def test_nested_retrieval_name_remains_part_of_core_tree(tmp_path: Path) -> None:
    bundle = build_bundle(tmp_path / "bundle")
    nested = bundle / "concepts" / "retrieval"
    nested.mkdir()
    (nested / "note.txt").write_text("authoritative core file\n", encoding="utf-8")
    index_path = bundle / "retrieval" / "index.json"
    index = json.loads(index_path.read_text(encoding="utf-8"))
    index["core"]["tree_sha256"] = core_tree_sha256(bundle)
    write_json(index_path, index)
    write_retrieval_report(bundle)
    support = load_support()
    assert support.load_snapshot(bundle).hashes["core_tree_sha256"] == core_tree_sha256(bundle)


def test_corrupt_declared_index_never_falls_back(tmp_path: Path) -> None:
    bundle = build_bundle(tmp_path / "bundle")
    chunks = bundle / "retrieval" / "chunks.jsonl"
    chunks.write_text(chunks.read_text(encoding="utf-8") + "{}\n", encoding="utf-8")
    before = tree_sha256(bundle)
    result = run_cli(
        bundle,
        "search",
        "--query",
        "database backup",
        "--mode",
        "auto",
        "--allow-fallback",
    )
    assert result.returncode == 3
    payload = json.loads(result.stdout)
    assert payload["code"] == "bundle-invalid"
    assert "hash" in payload["error"]
    assert tree_sha256(bundle) == before


@pytest.mark.parametrize(
    "mutate, expected",
    [
        (
            lambda chunks, embeddings: chunks.__setitem__(
                0, {**chunks[0], "concept_id": "concept-missing"}
            ),
            "orphan chunk",
        ),
        (
            lambda chunks, embeddings: chunks.__setitem__(
                0, {**chunks[0], "concept_path": "../outside.md"}
            ),
            "concept_path",
        ),
        (
            lambda chunks, embeddings: embeddings.__setitem__(
                0, {**embeddings[0], "vector": [1.0, 0.0]}
            ),
            "exactly 8",
        ),
        (
            lambda chunks, embeddings: embeddings.__setitem__(
                0, {**embeddings[0], "vector": [float("nan")] + [0.0] * 7}
            ),
            "non-finite",
        ),
    ],
    ids=("orphan", "path-traversal", "wrong-dimension", "nan"),
)
def test_deep_index_validation_rejects_unsafe_rows(
    tmp_path: Path,
    mutate: Callable[[list[dict[str, Any]], list[dict[str, Any]]], None],
    expected: str,
) -> None:
    bundle = build_bundle(tmp_path / "bundle")
    chunks = read_rows(bundle / "retrieval" / "chunks.jsonl")
    embeddings = read_rows(bundle / "retrieval" / "embeddings.jsonl")
    mutate(chunks, embeddings)
    rewrite_artifact(bundle, "chunks", chunks)
    rewrite_artifact(bundle, "embeddings", embeddings)
    support = load_support()
    with pytest.raises(support.SnapshotError, match=expected):
        support.load_snapshot(bundle)


def test_core_mutation_and_symlink_escape_are_rejected(tmp_path: Path) -> None:
    support = load_support()
    bundle = build_bundle(tmp_path / "core-mutation")
    report = bundle / "semantic" / "build-report.json"
    report.write_text(report.read_text(encoding="utf-8") + " ", encoding="utf-8")
    with pytest.raises(support.SnapshotError, match="core.tree_sha256"):
        support.load_snapshot(bundle)

    if hasattr(os, "symlink"):
        symlink_bundle = build_bundle(tmp_path / "symlink")
        concept = symlink_bundle / "concepts" / "concept-a.md"
        target = symlink_bundle / "concepts" / "real.md"
        concept.rename(target)
        try:
            concept.symlink_to(target)
        except OSError:
            pytest.skip("symlink creation is not permitted on this host")
        with pytest.raises(support.SnapshotError, match="symlink"):
            support.load_snapshot(symlink_bundle)


def test_skill_runs_after_copy_outside_repository(tmp_path: Path) -> None:
    bundle = build_bundle(tmp_path / "bundle")
    copied = tmp_path / "copied-skill"
    shutil.copytree(SKILL_ROOT, copied, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    result = run_cli(
        bundle,
        "search",
        "--query",
        "weekly incident drills",
        "--mode",
        "lexical",
        script=copied / "scripts" / "query_semantic_okf_embeddings.py",
    )
    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["hits"][0]["concept_id"] == "concept-c"
