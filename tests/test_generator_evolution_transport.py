"""Safety and replay contracts for the deterministic native generator adapter."""
import importlib.util
import json
from pathlib import Path
import tomllib

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "evaluations/integrated-semantic-okf-knowledge-skill/evolution"


def load(name):
    spec = importlib.util.spec_from_file_location("generator_transport_" + name, SCRIPTS / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_materializer_replays_exact_isolated_tasks_and_preserves_drifted_tree(tmp_path, monkeypatch):
    module = load("materialize")
    case = tmp_path / "cases/opaque-case"
    (case / "input").mkdir(parents=True)
    (case / "tests").mkdir()
    (case / "input/source.txt").write_text("Current source only.")
    (case / "request.json").write_text(json.dumps({"output": "/workspace/declared/expert"}))
    (case / "tests/test.sh").write_text("#!/bin/sh\nexit 0\n")
    (case / "tests/oracle.json").write_text('{"private":true}')
    calls = []
    def docker(args):
        calls.append(args)
        if args[0] == "build":
            return "built"
        return "sha256:" + ("a" if args[2] == "runtime:fixed" else "b") * 64
    monkeypatch.setattr(module, "docker", docker)
    output = tmp_path / "tasks"
    receipt = module.materialize(case.parent, output, "runtime:fixed")
    assert receipt["task_count"] == 1
    task, = output.iterdir()
    contract = tomllib.loads((task / "task.toml").read_text())
    assert contract["verifier"]["environment_mode"] == "separate"
    assert contract["environment"]["docker_image"] == "sha256:" + "b" * 64
    assert contract["verifier"]["environment"]["docker_image"] == "sha256:" + "a" * 64
    # Explicit destinations force native copying, including the conventional log
    # directory, instead of Harbor's unguarded mounted-directory inspection.
    assert contract["artifacts"] == [
        {"source": "/logs/artifacts", "destination": "published-artifacts"},
        {"source": "/workspace", "destination": "workspace"},
    ]
    mounts = yaml.safe_load((task / "environment/docker-compose.yaml").read_text())["services"]["main"]
    assert mounts["network_mode"] == "none" and mounts["volumes"][0]["read_only"] is True
    assert not (task / "environment/input/oracle.json").exists()
    before = module.hashes(output)
    assert module.materialize(case.parent, output, "runtime:fixed", check=True) == receipt
    assert module.hashes(output) == before
    assert all("--provenance=false" in args and "--network=none" in args for args in calls if args[0] == "build")
    (case / "input/source.txt").write_text("A changed task must not overwrite old evidence.")
    with pytest.raises(ValueError, match="replay differs"):
        module.materialize(case.parent, output, "runtime:fixed", check=True)
    assert module.hashes(output) == before
    with pytest.raises(FileExistsError):
        module.materialize(case.parent, output, "runtime:fixed")


def test_materializer_rejects_linked_sources(tmp_path):
    module = load("materialize")
    target = tmp_path / "actual.txt"
    target.write_text("data")
    link = tmp_path / "linked.txt"
    try:
        link.symlink_to(target)
    except OSError as error:
        pytest.skip(f"Host does not permit test symlinks: {error}")
    with pytest.raises(ValueError, match="links"):
        module.hashes(tmp_path)


def test_generator_transport_rejects_undeclared_schema_before_execution(monkeypatch):
    module = load("run_generator")
    monkeypatch.setattr(module.subprocess, "run", lambda *a, **k: pytest.fail("Unexpected execution"))
    with pytest.raises(ValueError, match="request schema"):
        module.execute(Path("unused"), {"command": "arbitrary"})


def test_generator_transport_rejects_input_escape_before_execution(monkeypatch):
    module = load("run_generator")
    monkeypatch.setattr(module.subprocess, "run", lambda *a, **k: pytest.fail("Unexpected execution"))
    request = dict(manifest="/outside/private.json", guidance="/dataset/guidance.md", family="legacy",
                   name="expert", description="evidence", output="/workspace/expert", plan=None,
                   concept_layout="source-packed-v1")
    with pytest.raises(ValueError, match="escaped"):
        module.execute(Path("unused"), request)
