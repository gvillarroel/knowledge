from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any

import pytest
import yaml

from tika_mallet_test_support import (
    BUILD_ROOT,
    build_portable_bundle,
    load_build_modules,
    plans,
    tree_hashes,
    write_json,
)


def test_skill_metadata_and_references_are_complete() -> None:
    skill = (BUILD_ROOT / "SKILL.md").read_text(encoding="utf-8")
    metadata = yaml.safe_load(skill.split("---", 2)[1])
    package_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in BUILD_ROOT.rglob("*")
        if path.is_file() and path.suffix in {".md", ".py", ".yaml"}
    )

    assert set(metadata) == {"name", "description"}
    assert metadata["name"] == "build-semantic-okf-tika-mallet"
    assert "Tika 4.0.0-beta-1" in metadata["description"]
    assert "## Standalone and authority boundary" in skill
    assert "preview" in skill
    assert "non-authoritative" in skill
    assert "TODO" not in package_text
    assert "pyrmallet" not in package_text.casefold()
    assert (BUILD_ROOT / "references" / "tika-mallet-contract.md").is_file()
    assert (BUILD_ROOT / "references" / "tika-mallet-format.md").is_file()
    runtime_reference = (BUILD_ROOT / "references" / "python-runtime.md").read_text(
        encoding="utf-8"
    )
    assert "py -3.12" not in runtime_reference
    assert "sys.version_info[:2] == (3, 12)" in runtime_reference
    assert "python scripts/runtime_smoke.py\n" not in runtime_reference
    assert "$build-semantic-okf-tika-mallet" in (
        BUILD_ROOT / "agents" / "openai.yaml"
    ).read_text(encoding="utf-8")


def test_portable_full_pipeline_is_deterministic_and_okf_authoritative(
    tmp_path: Path,
) -> None:
    first, *_ = build_portable_bundle(tmp_path / "first")
    second, *_ = build_portable_bundle(tmp_path / "second")

    assert tree_hashes(first) == tree_hashes(second)
    assert {path.name for path in (first / "tika").iterdir()} == {
        "index.json",
        "documents.jsonl",
        "extracted",
        "metadata",
    }
    assert {path.name for path in (first / "classical").iterdir()} == {
        "index.json",
        "documents.jsonl",
        "lexicon.json",
        "associations.jsonl",
        "topics.json",
        "build-report.json",
    }
    semantic_report = json.loads(
        (first / "semantic" / "build-report.json").read_text(encoding="utf-8")
    )
    tika_index = json.loads(
        (first / "tika" / "index.json").read_text(encoding="utf-8")
    )
    classical_index = json.loads(
        (first / "classical" / "index.json").read_text(encoding="utf-8")
    )
    assert semantic_report["status"] == "pass"
    assert tika_index["algorithm"] == (
        "apache-tika-4.0.0-beta-1-default-markdown-verified-v1"
    )
    assert tika_index["summary"] == {"documents": 2, "sources": 2}
    assert classical_index["authoritative"] is False
    assert classical_index["algorithms"]["topics"] == (
        "mallet-2.1.0-parallel-topic-model-v1"
    )
    assert classical_index["plan"]["topics"]["num_threads"] == 1
    assert (first / "semantic" / "ontology.ttl").is_file()
    assert (first / "semantic" / "shapes.ttl").is_file()
    assert len(list((first / "concepts").rglob("*.md"))) == 2


@pytest.mark.parametrize(
    ("section", "field", "value", "message"),
    [
        ("topics", "num_threads", 2, "num_threads must be 1"),
        ("topics", "random_seed", 0, "random_seed"),
        ("topics", "timeout_seconds", True, "timeout_seconds"),
        ("associations", "max_vocabulary", 31, "max_vocabulary"),
    ],
)
def test_retrieval_plan_rejects_non_reproducible_values(
    tmp_path: Path,
    section: str,
    field: str,
    value: Any,
    message: str,
) -> None:
    _, retrieval, _ = load_build_modules()
    _, plan_path = plans(tmp_path)
    payload = json.loads(plan_path.read_text(encoding="utf-8"))
    payload[section][field] = value
    write_json(plan_path, payload)

    with pytest.raises(retrieval.ClassicalError, match=message):
        retrieval.load_plan(plan_path)


def test_ingestion_plan_is_closed_and_paths_are_portable(tmp_path: Path) -> None:
    ingestion, _, _ = load_build_modules()
    ingestion_path, _ = plans(tmp_path)
    payload = json.loads(ingestion_path.read_text(encoding="utf-8"))
    payload["sources"][0]["path"] = "../outside/*.xlsx"
    write_json(ingestion_path, payload)

    with pytest.raises(ingestion.TikaIngestionError, match="portable plan-relative"):
        ingestion.load_ingestion_plan(ingestion_path)

    payload["sources"][0]["path"] = "C:/outside/*.xlsx"
    write_json(ingestion_path, payload)
    with pytest.raises(ingestion.TikaIngestionError, match="portable plan-relative"):
        ingestion.load_ingestion_plan(ingestion_path)

    payload["sources"][0]["path"] = "inputs/*.xlsx"
    payload["tika"]["implicit_default"] = True
    write_json(ingestion_path, payload)
    with pytest.raises(ingestion.TikaIngestionError, match="unsupported"):
        ingestion.load_ingestion_plan(ingestion_path)


def test_unmatched_and_oversized_sources_fail_closed(tmp_path: Path) -> None:
    ingestion, _, _ = load_build_modules()
    ingestion_path, _ = plans(tmp_path)
    payload = json.loads(ingestion_path.read_text(encoding="utf-8"))
    payload["sources"][0]["path"] = "inputs/*.docx"
    write_json(ingestion_path, payload)
    with pytest.raises(ingestion.TikaIngestionError, match="matched no regular files"):
        ingestion._discover(ingestion.load_ingestion_plan(ingestion_path))

    payload["sources"][0]["path"] = "inputs/*.xlsx"
    payload["tika"]["max_input_bytes"] = 1
    write_json(ingestion_path, payload)
    with pytest.raises(ingestion.TikaIngestionError, match="exceeds max_input_bytes"):
        ingestion._discover(ingestion.load_ingestion_plan(ingestion_path))


def test_source_symlink_or_reparse_point_is_rejected(tmp_path: Path) -> None:
    ingestion, _, _ = load_build_modules()
    ingestion_path, _ = plans(tmp_path)
    link = tmp_path / "inputs" / "linked.pdf"
    try:
        link.symlink_to(tmp_path / "inputs" / "guide.pdf")
    except OSError as exc:
        pytest.skip(f"symbolic links are unavailable: {exc}")

    with pytest.raises(ingestion.TikaIngestionError, match="unsafe input"):
        ingestion._discover(ingestion.load_ingestion_plan(ingestion_path))


def test_tika_uses_one_private_raw_snapshot(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    ingestion, _, _ = load_build_modules()
    ingestion_path, _ = plans(tmp_path)
    plan = ingestion.load_ingestion_plan(ingestion_path)
    initial = {
        path.name: (hashlib.sha256(path.read_bytes()).hexdigest(), path.stat().st_size)
        for path in (tmp_path / "inputs").iterdir()
    }
    runtime = ingestion.TikaRuntime(
        java=tmp_path / "java",
        java_version='openjdk version "17.0.12"',
        tika_home=tmp_path / "tika",
        tika_jar=tmp_path / "tika" / "tika-app-4.0.0-beta-1.jar",
        tika_version="4.0.0-beta-1",
        jar_inventory=(
            {"path": "tika-app-4.0.0-beta-1.jar", "sha256": "a" * 64},
        ),
        jar_tree_sha256=ingestion.sha256_json(
            [{"path": "tika-app-4.0.0-beta-1.jar", "sha256": "a" * 64}]
        ),
    )
    observed_snapshots: list[Path] = []

    def extract(runtime_value: Any, path: Path, *, timeout: int) -> tuple[str, dict[str, str]]:
        del runtime_value, timeout
        observed_snapshots.append(path)
        payload = path.read_bytes()
        original = tmp_path / "inputs" / path.name
        original.write_bytes(b"mutated only after private snapshot")
        return payload.decode("utf-8").strip(), {
            "Content-Type": "application/pdf" if path.suffix == ".pdf" else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "X-TIKA:resourceName": path.name,
        }

    monkeypatch.setattr(ingestion, "_extract_one", extract)
    output = tmp_path / "tika-output"
    ingestion.extract_tika_sources(plan, runtime, output)
    rows = [
        json.loads(line)
        for line in (output / "tika" / "documents.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
    ]

    assert len(observed_snapshots) == 2
    assert all(path.parent.parent.name.startswith("semantic-okf-tika-raw-") for path in observed_snapshots)
    assert all(not path.exists() for path in observed_snapshots)
    for row in rows:
        name = Path(row["source_locator"]).name
        assert (row["raw_sha256"], row["raw_bytes"]) == initial[name]


def test_tika_runs_default_markdown_explicit_markdown_and_json(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    ingestion, _, _ = load_build_modules()
    runtime = ingestion.TikaRuntime(
        java=tmp_path / "java",
        java_version='openjdk version "17.0.12"',
        tika_home=tmp_path,
        tika_jar=tmp_path / "tika-app-4.0.0-beta-1.jar",
        tika_version="4.0.0-beta-1",
        jar_inventory=(),
        jar_tree_sha256="0" * 64,
    )
    input_path = tmp_path / "source.pdf"
    input_path.write_bytes(b"fixture")
    commands: list[list[str]] = []

    def run(command: list[str], **kwargs: Any) -> tuple[str, str]:
        del kwargs
        commands.append(command)
        if "--json" in command:
            return '{"Content-Type":"application/pdf","dc:title":"Guide"}', ""
        return "# Guide\r\n\r\nEvidence\r\n", ""

    monkeypatch.setattr(ingestion, "_run", run)
    body, metadata = ingestion._extract_one(runtime, input_path, timeout=30)

    assert body == "# Guide\n\nEvidence"
    assert metadata["Content-Type"] == "application/pdf"
    assert len(commands) == 3
    assert "--md" not in commands[0]
    assert "--md" in commands[1]
    assert "--json" in commands[2]

    def mismatch(command: list[str], **kwargs: Any) -> tuple[str, str]:
        del kwargs
        return ("explicit" if "--md" in command else "default"), ""

    monkeypatch.setattr(ingestion, "_run", mismatch)
    with pytest.raises(ingestion.TikaIngestionError, match="differs"):
        ingestion._extract_one(runtime, input_path, timeout=30)


def test_verbatim_text_mode_preserves_utf8_and_control_bytes_after_lf_normalization(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    ingestion, _, _ = load_build_modules()
    ingestion_path, _ = plans(tmp_path)
    source_path = tmp_path / "inputs" / "canonical.md"
    source_path.write_bytes("Alpha\r\nβeta\u001fvalue\r\nOmega\n".encode("utf-8"))
    payload = json.loads(ingestion_path.read_text(encoding="utf-8"))
    payload["sources"] = [
        {
            "id": "canonical-text",
            "path": "inputs/canonical.md",
            "concept_type": "Canonical Text",
            "body_mode": "utf8-verbatim-tika-verified",
        }
    ]
    write_json(ingestion_path, payload)
    plan = ingestion.load_ingestion_plan(ingestion_path)
    runtime = ingestion.TikaRuntime(
        java=tmp_path / "java",
        java_version='openjdk version "17.0.12"',
        tika_home=tmp_path / "tika",
        tika_jar=tmp_path / "tika" / "tika-app-4.0.0-beta-1.jar",
        tika_version="4.0.0-beta-1",
        jar_inventory=(
            {"path": "tika-app-4.0.0-beta-1.jar", "sha256": "a" * 64},
        ),
        jar_tree_sha256=ingestion.sha256_json(
            [{"path": "tika-app-4.0.0-beta-1.jar", "sha256": "a" * 64}]
        ),
    )
    monkeypatch.setattr(
        ingestion,
        "_extract_one",
        lambda *args, **kwargs: (
            "# Tika-rendered body is intentionally not authoritative",
            {
                "Content-Type": "text/markdown; charset=UTF-8",
                "X-TIKA:resourceName": "canonical.md",
            },
        ),
    )

    output = tmp_path / "verbatim-output"
    index = ingestion.extract_tika_sources(plan, runtime, output)
    document = json.loads(
        (output / "tika/documents.jsonl").read_text(encoding="utf-8")
    )
    markdown = output / document["markdown_path"]
    frontmatter, body = ingestion._split_frontmatter(
        markdown.read_text(encoding="utf-8")
    )

    assert index["algorithm"] == (
        "apache-tika-4.0.0-beta-1-hybrid-markdown-or-"
        "utf8-verbatim-verified-v1"
    )
    assert index["plan"]["sources"][0]["body_mode"] == (
        "utf8-verbatim-tika-verified"
    )
    assert ingestion.generate_semantic_manifest(plan.raw)["sources"][0][
        "body_normalization"
    ] == "line-endings-only"
    assert frontmatter["tika_handler"] == (
        "utf8-verbatim-tika-metadata-verified-v1"
    )
    assert body == "Alpha\nβeta\u001fvalue\nOmega"
    assert document["body_sha256"] == hashlib.sha256(
        body.encode("utf-8")
    ).hexdigest()


def test_verbatim_text_mode_rejects_non_utf8_bom_and_non_text_media(
    tmp_path: Path,
) -> None:
    ingestion, _, _ = load_build_modules()
    source = tmp_path / "source.md"

    source.write_bytes(b"\xffinvalid")
    with pytest.raises(ingestion.TikaIngestionError, match="not strict UTF-8"):
        ingestion._verified_utf8_body(
            source, {"Content-Type": "text/markdown"}
        )

    source.write_bytes(b"\xef\xbb\xbfbody")
    with pytest.raises(ingestion.TikaIngestionError, match="byte-order mark"):
        ingestion._verified_utf8_body(
            source, {"Content-Type": "text/markdown"}
        )

    source.write_bytes(b"body")
    with pytest.raises(ingestion.TikaIngestionError, match="textual media type"):
        ingestion._verified_utf8_body(
            source, {"Content-Type": "application/pdf"}
        )


def test_ascii_tokenizer_does_not_casefold_dotless_i_into_the_vocabulary(
    tmp_path: Path,
) -> None:
    _, retrieval, _ = load_build_modules()
    _, retrieval_path = plans(tmp_path)
    plan = retrieval.load_plan(retrieval_path)

    assert retrieval.TOKEN_RE.findall("ıve") == ["ve"]
    assert retrieval._unigrams("ıve", plan) == ["ve"]
    assert all(
        term.isascii()
        for term in retrieval._unigrams("naïve ıve résumé", plan)
    )


def test_mallet_command_detects_exit_zero_errors_and_retries_transient_jshell(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _, retrieval, _ = load_build_modules()
    runtime = retrieval.MalletRuntime(
        java=tmp_path / "java",
        java_version='openjdk version "17"',
        mallet_home=tmp_path,
        mallet_version="2.1.0",
        jar_inventory=(),
        jar_tree_sha256="0" * 64,
    )
    monkeypatch.setattr(
        retrieval,
        "_run_java",
        lambda *args, **kwargs: ("", "Missing argument for option --input", 0),
    )
    with pytest.raises(retrieval.ClassicalError, match="reported"):
        retrieval._require_mallet_run(
            ["java"], runtime=runtime, timeout=10, label="MALLET import-file"
        )

    responses = iter(
        [
            (
                "",
                "Launching JShell execution engine threw: "
                "TransportTimeoutException: timeout waiting for connection",
                1,
            ),
            ("ok", "", 0),
        ]
    )
    calls = 0

    def transient(*args: Any, **kwargs: Any) -> tuple[str, str, int]:
        nonlocal calls
        del args, kwargs
        calls += 1
        return next(responses)

    monkeypatch.setattr(retrieval, "_run_java", transient)
    assert retrieval._require_mallet_run(
        ["java"], runtime=runtime, timeout=10, label="MALLET import-file"
    ) == ("ok", "")
    assert calls == 2


def test_mallet_classpath_is_explicit_and_rechecked(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _, retrieval, _ = load_build_modules()
    home = tmp_path / "mallet"
    library = home / "lib"
    library.mkdir(parents=True)
    java = tmp_path / "java.exe"
    java.write_bytes(b"java")
    for name in ("dependency.jar", "mallet-2.1.0.jar"):
        (library / name).write_bytes(name.encode("ascii"))
    inventory, tree_sha256 = retrieval._mallet_inventory(home)
    runtime = retrieval.MalletRuntime(
        java=java,
        java_version='openjdk version "17"',
        mallet_home=home,
        mallet_version="2.1.0",
        jar_inventory=inventory,
        jar_tree_sha256=tree_sha256,
        java_identity=retrieval.file_identity(java),
        home_identity=retrieval.file_identity(home),
    )
    command = retrieval._mallet_command(runtime, "cc.mallet.Example")
    classpath = command[command.index("-classpath") + 1]
    assert "*" not in classpath
    assert classpath.split(os.pathsep) == [
        str(home.joinpath(*Path(row["path"]).parts)) for row in inventory
    ]

    (library / "dependency.jar").write_bytes(b"changed")
    executed = False

    def run(*args: Any, **kwargs: Any) -> tuple[str, str, int]:
        nonlocal executed
        del args, kwargs
        executed = True
        return "", "", 0

    monkeypatch.setattr(retrieval, "_run_java", run)
    with pytest.raises(retrieval.ClassicalError, match="classpath changed"):
        retrieval._require_mallet_run(
            command, runtime=runtime, timeout=10, label="MALLET mutation test"
        )
    assert executed is False


def test_integrated_atomic_failure_leaves_no_destination(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    ingestion, retrieval, wrapper = load_build_modules()
    ingestion_path, retrieval_path = plans(tmp_path)
    stage = tmp_path / "stage"
    stage.mkdir()
    manifest = stage / "manifest.json"
    manifest.write_text("{}", encoding="utf-8")
    runtime = retrieval.MalletRuntime(
        java=tmp_path / "java",
        java_version='openjdk version "17"',
        mallet_home=tmp_path,
        mallet_version="2.1.0",
        jar_inventory=(),
        jar_tree_sha256="0" * 64,
    )
    monkeypatch.setattr(wrapper, "load_plan", lambda path: object())
    monkeypatch.setattr(wrapper, "preflight_mallet", lambda *args: runtime)
    monkeypatch.setattr(
        wrapper,
        "stage_tika_inputs",
        lambda *args, **kwargs: (stage, manifest, object(), {}),
    )
    monkeypatch.setattr(wrapper, "build_core", lambda source, output: output.mkdir())
    monkeypatch.setattr(wrapper, "copy_tika_tree", lambda source, output: None)
    monkeypatch.setattr(wrapper, "validate_tika_semantic_bindings", lambda root: {})
    monkeypatch.setattr(
        wrapper,
        "build_projection",
        lambda *args: (_ for _ in ()).throw(retrieval.ClassicalError("forced failure")),
    )
    output = tmp_path / "failed-output"

    with pytest.raises(retrieval.ClassicalError, match="forced failure"):
        wrapper.atomic_build(
            ingestion_path,
            retrieval_path,
            output,
            java=tmp_path / "java",
            tika_home=tmp_path / "tika",
            mallet_home=tmp_path / "mallet",
        )

    assert not output.exists()
    assert not list(tmp_path.glob(".failed-output.tika-mallet-candidate-*"))
    assert not stage.exists()


def test_no_replace_publication_preserves_concurrent_destination(tmp_path: Path) -> None:
    _, retrieval, wrapper = load_build_modules()
    source = tmp_path / "candidate"
    destination = tmp_path / "published"
    source.mkdir()
    destination.mkdir()

    with pytest.raises(retrieval.ClassicalError, match="already exists"):
        wrapper._publish_no_replace(source, destination)

    assert source.is_dir()
    assert destination.is_dir()

    dangling = tmp_path / "dangling-output"
    try:
        dangling.symlink_to(tmp_path / "missing-target", target_is_directory=True)
    except OSError:
        return
    with pytest.raises(retrieval.ClassicalError, match="already exists"):
        wrapper._publish_no_replace(source, dangling)
    assert dangling.is_symlink()


def test_candidate_setup_failure_cleans_tika_stage(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _, retrieval, wrapper = load_build_modules()
    ingestion_path, retrieval_path = plans(tmp_path)
    stage = tmp_path / "stage"
    stage.mkdir()
    manifest = stage / "semantic-manifest.json"
    manifest.write_text("{}", encoding="utf-8")
    runtime = retrieval.MalletRuntime(
        java=tmp_path / "java",
        java_version='openjdk version "17"',
        mallet_home=tmp_path / "mallet",
        mallet_version="2.1.0",
        jar_inventory=(),
        jar_tree_sha256="0" * 64,
    )
    monkeypatch.setattr(wrapper, "load_plan", lambda path: object())
    monkeypatch.setattr(wrapper, "preflight_mallet", lambda *args: runtime)
    monkeypatch.setattr(
        wrapper,
        "stage_tika_inputs",
        lambda *args, **kwargs: (stage, manifest, object(), {}),
    )
    monkeypatch.setattr(
        wrapper.tempfile,
        "mkdtemp",
        lambda *args, **kwargs: (_ for _ in ()).throw(OSError("candidate setup failed")),
    )
    output = tmp_path / "candidate-failure"

    with pytest.raises(OSError, match="candidate setup failed"):
        wrapper.atomic_build(
            ingestion_path,
            retrieval_path,
            output,
            java=tmp_path / "java",
            tika_home=tmp_path / "tika",
            mallet_home=tmp_path / "mallet",
        )

    assert not output.exists()
    assert not stage.exists()
    assert not list(tmp_path.glob(".candidate-failure.tika-mallet-work-*"))
