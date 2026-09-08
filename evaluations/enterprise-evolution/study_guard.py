"""Verify the organizer ledger on the Windows host that registered its paths."""
import argparse
import importlib.util
import json
import sys
from pathlib import Path

from prepare import WORK, REPO, ORGANIZER, read, sha


def verify(phase):
    manifest = read(WORK / "execution-contract.json")
    for relative, expected in manifest["source_files"].items():
        if sha(REPO / relative) != expected:
            raise ValueError("Frozen execution source drift: " + relative)
    for relative, expected in manifest["workspace_files"].items():
        if sha(WORK / relative) != expected:
            raise ValueError("Frozen workspace input drift: " + relative)
    for name, expected in manifest["external_read_only_files"].items():
        if not name.startswith("/mnt/c/") or sha(Path("C:/"+name[len("/mnt/c/"):])) != expected:
            raise ValueError("Frozen owner or model drift")
    spec = importlib.util.spec_from_file_location("enterprise_guard_organizer", ORGANIZER)
    owner = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = owner
    spec.loader.exec_module(owner)
    state = owner.build_state(WORK / "study", verify_sources=True)
    if not state["designSeal"]:
        raise ValueError("Unsealed study")
    if phase == "development":
        if state["validationRelease"] or state["holdoutRelease"] or state["stages"]["evolve"]["status"] != "running":
            raise ValueError("Evolution is not active with unopened gates")
    elif not state["validationRelease"] or state["holdoutRelease"] or state["stages"]["validate"]["status"] != "running" or state["stages"]["evolve"]["status"] != "completed":
        raise ValueError("Validation has not been released for a frozen winner")
    return {"phase": phase, "status": "verified", "source_verification": True, "validation_released": bool(state["validationRelease"])}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=["development", "validation"])
    print(json.dumps(verify(parser.parse_args().phase)))
