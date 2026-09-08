"""Apply one explicit construction profile without changing source or evidence identity."""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path


def apply_profile(plan, operations):
    """Return a new plan; mutate only existing, supported retrieval parameters."""
    result = copy.deepcopy(plan)
    def visit(node):
        if not isinstance(node, dict):
            return
        for child in list(node.values()):
            visit(child)
        for operation in operations:
            kind = operation["operation"]
            if kind == "learned-embedding" and node.get("provider") == "hashing":
                node.update(provider="sentence-transformers", model_id=operation["model_id"], revision=operation["revision"], dimension=operation["dimension"])
            elif kind == "expansion-scale" and "association_weight" in node and "topic_weight" in node:
                node["association_weight"] *= operation["factor"]
                node["topic_weight"] *= operation["factor"]
            elif kind == "bm25-b" and "k1" in node and "b" in node:
                node["b"] = operation["value"]
            elif kind == "title-weight" and "title_weight" in node and "body_weight" in node:
                node["title_weight"] = operation["value"]
    visit(result)
    return result


def main():
    """Transform a declared plan and require subsequent matched family validation."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--family", choices=["embeddings", "classical", "adaptive", "entity-graph", "ensemble"], required=True)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() or args.output.resolve() == args.input.resolve():
        parser.error("Use a new output plan path")
    profile = json.loads((Path(__file__).resolve().parents[1] / "assets/retrieval-profile.json").read_text(encoding="utf-8"))
    result = apply_profile(json.loads(args.input.read_text(encoding="utf-8")), profile["operations"])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
