"""Validate candidate configuration scope using synthetic source selections."""
import importlib.util
import json
from pathlib import Path

from profiles import FAMILIES, CONSTRUCTION, baseline_profile, inventory, apply_plan
from prepare import REPO


def validate(root):
    profile = json.loads((root / "assets/retrieval-profile.json").read_text())
    if set(profile) != set(FAMILIES):
        raise ValueError("Family membership drift")
    seed = baseline_profile()
    helper = REPO / "evaluations/private-book-strategy-comparison/scripts/prepare_strategy_bundles.py"
    spec = importlib.util.spec_from_file_location("synthetic_build_plans", helper)
    plans = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(plans)
    for family in FAMILIES:
        if set(profile[family]) != {"plan", "search"}:
            raise ValueError("Treatment schema drift")
        channel = "plan" if family in CONSTRUCTION else "search"
        allowed = {}
        for key, value in seed[family][channel].items():
            allowed.setdefault(key, []).append(value)
        for strategy in inventory(family):
            for variant in strategy["variants"]:
                for key, value in variant.items():
                    allowed.setdefault(key, []).append(value)
        if profile[family]["search" if channel == "plan" else "plan"]:
            raise ValueError("Builder and consultation treatments cannot mix")
        for key, value in profile[family][channel].items():
            if key not in allowed or value not in allowed[key]:
                raise ValueError("Value outside the closed mutation inventory")
        if channel == "plan":
            name = ("embedding" if family == "embeddings" else family.replace("-", "_")) + "_plan"
            original = getattr(plans, name)(["synthetic-source"])
            first = apply_plan(original, profile, family)
            if first != apply_plan(original, profile, family):
                raise ValueError("Plan transformation is not deterministic")
    return True


if __name__ == "__main__":
    validate(Path.cwd())
    print("Closed profile and treatment validation passed.")
