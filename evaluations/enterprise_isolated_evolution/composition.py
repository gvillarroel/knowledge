"""Compose disjoint family implementations while preserving common bytes."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import shutil

from .authority import safe_path
from .files import PROFILE, REPO, inventory, read
from .executor_policy import compose_policy
from .planner import FAMILIES, ProtocolError


def compose(base: Path, sources: dict[str, Path], destination: Path, *, expected: dict[str, str],
            external_drift: dict[str, list[str]]) -> dict:
    """Transfer each bound family subtree and its profile entry exactly once."""
    safe_path(destination, REPO)
    if destination.exists() or set(sources) != set(FAMILIES) or set(expected) != set(FAMILIES):
        raise ProtocolError("Invalid or reused composition destination")
    _, base_files = inventory(base)
    observations, profile = {}, copy.deepcopy(read(base / PROFILE))
    for family in FAMILIES:
        checksum, files = inventory(sources[family])
        if checksum != expected[family] or files.keys() != base_files.keys():
            raise ProtocolError("Composition source digest or inventory differs")
        prefix = f"assets/families/{family}/"
        external = sorted(p for p in files if files[p] != base_files[p]
                          and p != PROFILE and not p.startswith(prefix))
        if external != sorted(external_drift.get(family, [])):
            raise ProtocolError("Undeclared external family ancestry")
        observations[family] = {"tree_sha256": checksum, "external_ancestry_ignored": external,
                                "files": {p: s for p, s in files.items() if p.startswith(prefix)}}
        profile[family] = read(sources[family] / PROFILE)[family]
    shutil.copytree(base, destination)
    for family in FAMILIES:
        relative = Path("assets/families") / family
        shutil.copytree(sources[family] / relative, destination / relative, dirs_exist_ok=True)
    (destination / PROFILE).write_text(json.dumps(profile, indent=2, allow_nan=False) + "\n", encoding="utf-8", newline="\n")
    checksum, files = inventory(destination)
    for family, row in observations.items():
        if any(files.get(p) != s for p, s in row["files"].items()):
            raise ProtocolError("Composition transfer did not preserve family bytes")
    protected = {p: s for p, s in base_files.items() if p != PROFILE and not p.startswith("assets/families/")}
    if files.keys() != base_files.keys() or any(files[p] != s for p, s in protected.items()):
        raise ProtocolError("Composition changed protected files")
    return {"tree_sha256": checksum, "families": observations, "requires_native_joint_replay": True}


def rebind_task(source: Path, destination: Path, skill: Path) -> dict:
    """Version implementation bindings and executor isolation, preserving scoring."""
    import yaml
    safe_path(destination, REPO)
    _, before = inventory(source)
    _, skill_files = inventory(skill)
    contract = read(source / "tests/contract.json")
    if contract["mutable_skill_paths"] != [PROFILE] or set(contract["skill_files"]) != set(skill_files):
        raise ProtocolError("Task mutation boundary or complete skill inventory differs")
    changed = copy.deepcopy(contract)
    changed["skill_files"] = skill_files
    changed["imported_candidate_modules"] = {p: skill_files[p] for p in contract["imported_candidate_modules"]}
    shutil.copytree(source, destination)
    (destination / "tests/contract.json").write_text(json.dumps(changed, sort_keys=True, indent=2) + "\n", encoding="utf-8", newline="\n")
    for relative, verifier in (("environment/docker-compose.yaml", False), ("tests/docker-compose.yaml", True)):
        inherited = {"network_mode": "none"}
        if verifier:
            inherited["volumes"] = [{"type": "bind", "source": ".", "target": "/tests", "read_only": True}]
        if yaml.safe_load((source / relative).read_text(encoding="utf-8")) != {"services": {"main": inherited}}:
            raise ProtocolError("Unexpected inherited executor configuration")
        (destination / relative).write_text(json.dumps(compose_policy(verifier=verifier), sort_keys=True, indent=2) + "\n",
                                           encoding="utf-8", newline="\n")
    _, after = inventory(destination)
    differing = sorted(p for p in before if before[p] != after[p])
    allowed = {"tests/contract.json", "environment/docker-compose.yaml", "tests/docker-compose.yaml"}
    if before.keys() != after.keys() or any(p not in allowed for p in differing):
        raise ProtocolError("Task version changed data, instructions, verifier or resources")
    return {"source_tree_sha256": inventory(source)[0], "task_tree_sha256": inventory(destination)[0],
            "implementation_tree_sha256": inventory(skill)[0], "changed_files": differing,
            "changed_contract_fields": ["skill_files", "imported_candidate_modules"],
            "executor_policy": "separate-feedback-readonly-root-private-disk-workspace",
            "cpu_memory_time_limits_changed": False,
            "scoring_or_data_changed": False}
