from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPO_ROOT / "skills" / "build-semantic-okf-embeddings"
SCRIPTS = SKILL_ROOT / "scripts"
BUILD = SCRIPTS / "build_semantic_okf_embeddings.py"
VALIDATE = SCRIPTS / "validate_semantic_okf_embeddings.py"


def write_fixture(root: Path) -> tuple[Path, Path]:
    """Write two small, separately selectable Markdown authorities."""

    sources = root / "sources"
    sources.mkdir(parents=True)
    (sources / "primary.md").write_text(
        "---\ntitle: Primary Note\ncode: DOC-1\n---\n\n"
        "# Primary Note\n\nGraph retrieval links facts. Semantic chunks find related evidence.\n",
        encoding="utf-8",
    )
    (sources / "auxiliary.md").write_text(
        "---\ntitle: Auxiliary Note\ncode: AUX-1\n---\n\n"
        "# Auxiliary Note\n\nThis source remains authoritative but is excluded from retrieval.\n",
        encoding="utf-8",
    )
    manifest_payload = {
        "schema_version": "1.0",
        "bundle": {
            "title": "Embedding fixture",
            "description": "Two reviewed documents for retrieval tests.",
            "base_iri": "https://example.org/embedding-fixture/",
            "ontology_iri": "https://example.org/ontology/embedding-fixture",
            "version_iri": "https://example.org/ontology/embedding-fixture/1.0.0",
            "prefix": "fixture",
            "owl_profile": "rl",
        },
        "ontology": {
            "classes": [{"name": "Document", "label": "document"}],
            "properties": [
                {
                    "name": "code",
                    "kind": "datatype",
                    "domain": "Document",
                    "range": "xsd:string",
                }
            ],
        },
        "rules": [
            {
                "name": "DocumentCodeRule",
                "target_class": "Document",
                "path": "code",
                "min_count": 1,
                "datatype": "xsd:string",
                "message": "Every document requires a reviewed code.",
                "basis": {"kind": "operational-policy", "references": ["FIXTURE-1"]},
            }
        ],
        "sources": [
            {
                "id": "auxiliary",
                "kind": "markdown",
                "path": "sources/auxiliary.md",
                "concept_type": "Document",
                "ontology_class": "Document",
                "fields": {"code": "code"},
            },
            {
                "id": "primary",
                "kind": "markdown",
                "path": "sources/primary.md",
                "concept_type": "Document",
                "ontology_class": "Document",
                "fields": {"code": "code"},
            },
        ],
    }
    plan_payload = {
        "schema_version": "1.0",
        "selection": {"source_ids": ["primary"]},
        "chunking": {
            "implementation": "native",
            "strategy": "semantic",
            "buffer_size": 1,
            "breakpoint_percentile_threshold": 50,
        },
        "embedding": {
            "provider": "hashing",
            "model_id": "knowledge-hashing-embedding",
            "revision": "1",
            "dimension": 32,
            "normalize": True,
        },
    }
    manifest = root / "manifest.json"
    plan = root / "retrieval-plan.json"
    manifest.write_text(json.dumps(manifest_payload, indent=2) + "\n", encoding="utf-8")
    plan.write_text(json.dumps(plan_payload, indent=2) + "\n", encoding="utf-8")
    return manifest, plan


def run_build(manifest: Path, plan: Path, output: Path, *, script: Path = BUILD) -> dict[str, object]:
    env = os.environ.copy()
    env.pop("PYTHONPATH", None)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    completed = subprocess.run(
        [
            sys.executable,
            str(script),
            str(manifest),
            str(plan),
            str(output),
            "--output-format",
            "json",
        ],
        cwd=manifest.parent,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=90,
        check=False,
        env=env,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    return json.loads(completed.stdout)


def tree_hashes(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def load_retrieval_module() -> ModuleType:
    sys.path.insert(0, str(SCRIPTS))
    try:
        spec = importlib.util.spec_from_file_location(
            "test_embedding_retrieval", SCRIPTS / "_embedding_retrieval.py"
        )
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        return module
    finally:
        sys.path.remove(str(SCRIPTS))


def test_skill_metadata_and_documents_are_complete() -> None:
    skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
    metadata = yaml.safe_load(skill.split("---", 2)[1])

    assert set(metadata) == {"name", "description"}
    assert metadata["name"] == SKILL_ROOT.name
    assert "## Standalone boundary" in skill
    assert "TODO" not in "\n".join(
        path.read_text(encoding="utf-8")
        for path in SKILL_ROOT.rglob("*")
        if path.is_file() and path.suffix in {".md", ".py", ".yaml"}
    )
    assert (SKILL_ROOT / "references" / "retrieval-plan.md").is_file()
    assert "$build-semantic-okf-embeddings" in (
        SKILL_ROOT / "agents" / "openai.yaml"
    ).read_text(encoding="utf-8")
    assert (
        SKILL_ROOT / "scripts" / "requirements-sentence-transformers.in"
    ).read_text(encoding="utf-8").splitlines() == [
        "huggingface-hub==1.23.0",
        "sentence-transformers==5.6.0",
    ]


def test_plan_is_closed_and_optional_backends_are_lazy(tmp_path: Path) -> None:
    module = load_retrieval_module()
    _, plan_path = write_fixture(tmp_path)
    payload = json.loads(plan_path.read_text(encoding="utf-8"))
    payload["embedding"]["provider"] = "openai"
    plan_path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(module.RetrievalError, match="hashing or sentence-transformers"):
        module.load_plan(plan_path)

    source = (SCRIPTS / "_embedding_retrieval.py").read_text(encoding="utf-8")
    assert "import sentence_transformers" not in source
    assert "import llama_index" not in source
    assert "local_files_only=True" in source
    assert "trust_remote_code=False" in source


def test_strict_json_rejects_duplicate_keys_at_nested_depth() -> None:
    module = load_retrieval_module()

    with pytest.raises(module.RetrievalError, match="duplicate object key 'dimension'"):
        module.strict_json_loads(
            '{"embedding":{"dimension":384,"dimension":768}}',
            label="retrieval-plan.json",
        )


@pytest.mark.parametrize(
    "model_id",
    [
        "all-MiniLM-L6-v2",
        "./sentence-transformers/all-MiniLM-L6-v2",
        "../sentence-transformers/all-MiniLM-L6-v2",
        "/sentence-transformers/all-MiniLM-L6-v2",
        r"C:\models\all-MiniLM-L6-v2",
        r"sentence-transformers\all-MiniLM-L6-v2",
        "sentence-transformers/../all-MiniLM-L6-v2",
        "sentence--transformers/all-MiniLM-L6-v2",
    ],
)
def test_sentence_transformers_plan_rejects_raw_paths_and_invalid_repo_ids(
    tmp_path: Path, model_id: str
) -> None:
    module = load_retrieval_module()
    _, plan_path = write_fixture(tmp_path)
    payload = json.loads(plan_path.read_text(encoding="utf-8"))
    payload["embedding"] = {
        "provider": "sentence-transformers",
        "model_id": model_id,
        "revision": "1" * 40,
        "dimension": 384,
        "normalize": True,
    }
    plan_path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(module.RetrievalError, match="namespace/repository"):
        module.load_plan(plan_path)


def test_sentence_transformers_resolves_exact_offline_snapshot_before_model_load(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = load_retrieval_module()
    revision = "A" * 40
    snapshot = tmp_path / "hub" / "snapshots" / revision.lower()
    snapshot.mkdir(parents=True)
    calls: dict[str, object] = {"imports": []}

    def snapshot_download(**kwargs: object) -> str:
        calls["snapshot_download"] = kwargs
        return str(snapshot)

    class FakeSentenceTransformer:
        def __init__(self, *args: object, **kwargs: object) -> None:
            calls["sentence_transformer"] = {"args": args, "kwargs": kwargs}

    def fake_import(name: str) -> object:
        imports = calls["imports"]
        assert isinstance(imports, list)
        imports.append(name)
        if name == "huggingface_hub":
            return SimpleNamespace(snapshot_download=snapshot_download)
        if name == "sentence_transformers":
            return SimpleNamespace(SentenceTransformer=FakeSentenceTransformer)
        raise AssertionError(f"unexpected import: {name}")

    monkeypatch.setattr(module, "importlib", SimpleNamespace(import_module=fake_import))
    monkeypatch.setenv("HF_HUB_OFFLINE", "0")
    monkeypatch.setenv("TRANSFORMERS_OFFLINE", "0")
    plan = module.RetrievalPlan(
        raw={},
        source_ids=("primary",),
        implementation="native",
        strategy="record",
        buffer_size=1,
        percentile=95.0,
        provider="sentence-transformers",
        model_id="sentence-transformers/all-MiniLM-L6-v2",
        revision=revision,
        dimension=384,
        normalize=True,
    )

    module.SentenceTransformersEmbedder(plan)

    assert calls["imports"] == ["huggingface_hub", "sentence_transformers"]
    assert calls["snapshot_download"] == {
        "repo_id": plan.model_id,
        "revision": revision,
        "local_files_only": True,
    }
    model_call = calls["sentence_transformer"]
    assert isinstance(model_call, dict)
    assert model_call["args"] == (str(snapshot.resolve()),)
    assert model_call["kwargs"] == {
        "local_files_only": True,
        "trust_remote_code": False,
        "device": "cpu",
    }
    assert plan.model_id not in model_call["args"]
    assert os.environ["HF_HUB_OFFLINE"] == "1"
    assert os.environ["TRANSFORMERS_OFFLINE"] == "1"


def test_sentence_transformers_rejects_cache_revision_mismatch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = load_retrieval_module()
    requested_revision = "a" * 40
    mismatched_snapshot = tmp_path / "snapshots" / ("b" * 40)
    mismatched_snapshot.mkdir(parents=True)

    def fake_import(name: str) -> object:
        if name == "huggingface_hub":
            return SimpleNamespace(snapshot_download=lambda **_: str(mismatched_snapshot))
        raise AssertionError("SentenceTransformers must not load for a mismatched snapshot")

    monkeypatch.setattr(module, "importlib", SimpleNamespace(import_module=fake_import))
    plan = module.RetrievalPlan(
        raw={},
        source_ids=("primary",),
        implementation="native",
        strategy="record",
        buffer_size=1,
        percentile=95.0,
        provider="sentence-transformers",
        model_id="sentence-transformers/all-MiniLM-L6-v2",
        revision=requested_revision,
        dimension=384,
        normalize=True,
    )

    with pytest.raises(module.RetrievalError, match="does not match the requested revision"):
        module.SentenceTransformersEmbedder(plan)


def test_core_inventory_excludes_only_the_root_retrieval_projection(tmp_path: Path) -> None:
    module = load_retrieval_module()
    root = tmp_path / "bundle"
    nested = root / "concepts" / "retrieval"
    projection = root / "retrieval"
    nested.mkdir(parents=True)
    projection.mkdir()
    (nested / "evidence.md").write_text("# Authoritative evidence\n", encoding="utf-8")
    (projection / "index.json").write_text("{}\n", encoding="utf-8")

    paths = [row["path"] for row in module._core_inventory(root)]

    assert paths == ["concepts/retrieval/evidence.md"]


def test_hashing_native_build_is_deterministic_and_hash_bound(tmp_path: Path) -> None:
    manifest, plan = write_fixture(tmp_path / "inputs")
    first = tmp_path / "first"
    second = tmp_path / "second"

    first_report = run_build(manifest, plan, first)
    second_report = run_build(manifest, plan, second)

    assert first_report == second_report
    assert tree_hashes(first) == tree_hashes(second)
    index = json.loads((first / "retrieval" / "index.json").read_text(encoding="utf-8"))
    chunks = [
        json.loads(line)
        for line in (first / "retrieval" / "chunks.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
    ]
    embeddings = [
        json.loads(line)
        for line in (first / "retrieval" / "embeddings.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
    ]

    assert index["authoritative"] is False
    assert index["selection"]["requested_source_ids"] == ["primary"]
    assert index["selection"]["eligible_source_ids"] == ["primary"]
    assert index["selection"]["excluded_source_ids"] == ["auxiliary"]
    assert index["selection"]["input_count"] == 1
    assert index["embedding"]["vector_precision"] == 8
    assert index["chunk_count"] == len(chunks) == len(embeddings)
    assert [row["chunk_id"] for row in chunks] == sorted(row["chunk_id"] for row in chunks)
    assert [row["chunk_id"] for row in embeddings] == [row["chunk_id"] for row in chunks]
    for artifact in ("chunks", "embeddings"):
        entry = index["artifacts"][artifact]
        assert hashlib.sha256((first / entry["path"]).read_bytes()).hexdigest() == entry["sha256"]
        assert entry["count"] == len(chunks)

    completed = subprocess.run(
        [sys.executable, str(VALIDATE), str(first), "--output-format", "json"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=60,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert json.loads(completed.stdout)["valid"] is True


def test_validator_rejects_nan_zero_dimension_and_orphan_vectors(tmp_path: Path) -> None:
    manifest, plan = write_fixture(tmp_path / "inputs")
    clean = tmp_path / "clean"
    run_build(manifest, plan, clean)

    def mutate_nan(path: Path) -> None:
        target = path / "retrieval" / "embeddings.jsonl"
        lines = target.read_text(encoding="utf-8").splitlines()
        row = json.loads(lines[0])
        row["vector"][0] = float("nan")
        lines[0] = json.dumps(row, allow_nan=True, sort_keys=True, separators=(",", ":"))
        target.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def mutate_zero(path: Path) -> None:
        target = path / "retrieval" / "embeddings.jsonl"
        lines = target.read_text(encoding="utf-8").splitlines()
        row = json.loads(lines[0])
        row["vector"] = [0.0] * len(row["vector"])
        lines[0] = json.dumps(row, sort_keys=True, separators=(",", ":"))
        target.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def mutate_dimension(path: Path) -> None:
        target = path / "retrieval" / "embeddings.jsonl"
        lines = target.read_text(encoding="utf-8").splitlines()
        row = json.loads(lines[0])
        row["vector"] = row["vector"][:-1]
        lines[0] = json.dumps(row, sort_keys=True, separators=(",", ":"))
        target.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def mutate_orphan(path: Path) -> None:
        target = path / "retrieval" / "embeddings.jsonl"
        lines = target.read_text(encoding="utf-8").splitlines()
        row = json.loads(lines[0])
        row["chunk_id"] = "chunk-" + "0" * 32
        lines[0] = json.dumps(row, sort_keys=True, separators=(",", ":"))
        target.write_text("\n".join(lines) + "\n", encoding="utf-8")

    cases = [
        ("nan", mutate_nan, "non-finite"),
        ("zero", mutate_zero, "zero"),
        ("dimension", mutate_dimension, "dimension"),
        ("orphan", mutate_orphan, "orphaned"),
    ]
    for name, mutation, expected in cases:
        candidate = tmp_path / name
        shutil.copytree(clean, candidate)
        mutation(candidate)
        completed = subprocess.run(
            [sys.executable, str(VALIDATE), str(candidate), "--output-format", "json"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=60,
            check=False,
        )
        assert completed.returncode == 2
        result = json.loads(completed.stdout)
        assert result["valid"] is False
        assert expected in result["errors"][0]["message"]


def test_thirty_requested_inputs_exclude_only_auxiliary_vocabulary(tmp_path: Path) -> None:
    module = load_retrieval_module()
    source_ids = sorted(
        [f"paper-{index:02d}" for index in range(15)]
        + [f"claims-{index:02d}" for index in range(15)]
    )
    sources = [
        {
            "id": source_id,
            "content_sha256": hashlib.sha256(source_id.encode("utf-8")).hexdigest(),
        }
        for source_id in source_ids + ["analysis-vocabulary"]
    ]
    records = [
        {"source_id": source_id, "record_id": f"record-{index:02d}"}
        for index, source_id in enumerate(source_ids)
    ]
    plan = module.RetrievalPlan(
        raw={},
        source_ids=tuple(source_ids),
        implementation="native",
        strategy="record",
        buffer_size=1,
        percentile=95.0,
        provider="hashing",
        model_id="knowledge-hashing-embedding",
        revision="1",
        dimension=32,
        normalize=True,
    )

    selected, selection = module._selection(records, sources, plan)

    assert len(selected) == 30
    assert selection["input_count"] == 30
    assert selection["eligible_source_ids"] == source_ids
    assert selection["excluded_source_ids"] == ["analysis-vocabulary"]


def test_package_builds_after_copy_outside_checkout(tmp_path: Path) -> None:
    copied = tmp_path / "copied-skill"
    shutil.copytree(SKILL_ROOT, copied, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    manifest, plan = write_fixture(tmp_path / "inputs")
    output = tmp_path / "copied-output"

    report = run_build(
        manifest,
        plan,
        output,
        script=copied / "scripts" / "build_semantic_okf_embeddings.py",
    )

    assert report["status"] == "pass"
    copied_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in copied.rglob("*")
        if path.is_file() and path.suffix in {".py", ".md", ".yaml"}
    )
    assert "skills/build-semantic-okf/" not in copied_text


def test_invalid_plan_publishes_no_partial_output(tmp_path: Path) -> None:
    manifest, plan = write_fixture(tmp_path / "inputs")
    payload = json.loads(plan.read_text(encoding="utf-8"))
    payload["chunking"]["hosted_default"] = True
    plan.write_text(json.dumps(payload), encoding="utf-8")
    output = tmp_path / "failed-output"

    completed = subprocess.run(
        [
            sys.executable,
            str(BUILD),
            str(manifest),
            str(plan),
            str(output),
            "--output-format",
            "json",
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=60,
        check=False,
    )

    assert completed.returncode == 2
    assert json.loads(completed.stdout)["code"] == "retrieval-error"
    assert not output.exists()
    assert not list(tmp_path.glob(".failed-output.embedding-candidate-*"))
