"""Validate a candidate profile on synthetic plans without reading evaluation data."""
from __future__ import annotations

import ast
import importlib.util
import json
from pathlib import Path


def main():
    """Check closed mutation declarations and preservation of authoritative input keys."""
    root = Path.cwd()
    helper = root / "scripts/apply_retrieval_profile.py"
    ast.parse(helper.read_text(encoding="utf-8"))
    spec = importlib.util.spec_from_file_location("candidate_profile", helper)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    profile = json.loads((root / "assets/retrieval-profile.json").read_text(encoding="utf-8"))
    if set(profile) != {"schema_version", "operations"} or profile["schema_version"] != "retrieval-profile/1.0":
        raise ValueError("Unexpected profile schema")
    expected_keys = {"learned-embedding": {"operation", "model_id", "revision", "dimension"}, "expansion-scale": {"operation", "factor"}, "bm25-b": {"operation", "value"}, "title-weight": {"operation", "value"}}
    operations = profile["operations"]
    if not operations or len({row["operation"] for row in operations}) != len(operations):
        raise ValueError("Empty or repeated profile mechanism")
    for operation in operations:
        if set(operation) != expected_keys.get(operation["operation"]):
            raise ValueError("Unexpected operation fields")
    original = {"schema_version": "synthetic", "selection": {"source_ids": ["manuals"]}, "embedding": {"provider": "hashing", "model_id": "knowledge-hashing-embedding", "revision": "1", "dimension": 384, "normalize": True},
                "bm25": {"k1": 1.2, "b": .75, "title_weight": 2., "body_weight": 1.},
                "expansion": {"association_weight": .35, "topic_weight": .2}, "chunking": {"strategy": "record"}}
    before = json.dumps(original, sort_keys=True)
    changed = module.apply_profile(original, operations)
    if json.dumps(original, sort_keys=True) != before or changed == original:
        raise ValueError("Profile mutated its input or had no declared effect")
    for key in ("selection", "schema_version", "chunking"):
        if original[key] != changed[key]:
            raise ValueError("Authoritative plan scope drift")
    if module.apply_profile(original, operations) != changed:
        raise ValueError("Non-deterministic profile")
    print("Synthetic construction-profile validation passed.")


if __name__ == "__main__":
    main()
