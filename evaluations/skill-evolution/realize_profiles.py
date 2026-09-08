"""Realize predeclared profiles through the installed candidate sealing contract."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

from prepare_experiment import HERE, REPO, WORK, sha, write_json
from prepare_study import organize


REALIZER = Path("C:/Users/villa/.codex/skills/harbor-realize-skill-candidate/scripts/realize_skill_candidate.py")


def call(command, path):
    result = subprocess.run([sys.executable, "-B", str(REALIZER), command, str(path)], capture_output=True, text=True, encoding="utf-8", check=False)
    if result.returncode:
        raise ValueError("Candidate realization failed: " + result.stderr.strip())
    return json.loads(result.stdout)


def realize(identifier, operations, instruction, parent, parent_digest, evidence):
    root = WORK / "realizations"
    root.mkdir(parents=True, exist_ok=True)
    config = {"schemaVersion": 1, "realization": {"id": "profile-" + identifier, "candidateId": identifier, "parentSkill": str(parent), "expectedParentTreeSha256": parent_digest,
        "workspaceDir": str(root / (identifier + "-workspace")), "outputDir": str(root / (identifier + "-sealed")),
        "operator": {"operatorId": "profile-" + identifier, "instruction": instruction, "origin": "predeclared-development-hypothesis", "parentOperatorIds": []},
        "allowedChanges": ["SKILL.md", "scripts/apply_retrieval_profile.py", "assets/retrieval-profile.json", "references/retrieval-profile.md"],
        "developmentEvidence": [{"id": "development-hypothesis", "role": "development", "path": str(evidence), "sha256": "sha256:" + sha(evidence)}],
        "trustedValidationCommands": True, "validationCommands": [{"id": "synthetic-profile-contract", "argv": [sys.executable, "-B", str(HERE / "validate_profile_candidate.py")], "timeoutSeconds": 60},
        {"id": "skill-frontmatter", "argv": [sys.executable, "-B", "C:/Users/villa/.codex/skills/.system/skill-creator/scripts/quick_validate.py", "."], "timeoutSeconds": 60}]}}
    path = root / (identifier + ".json")
    write_json(path, config)
    prepared = call("prepare", path)
    # The documented canonical workspace layout is verified by the realizer.
    candidate = root / (identifier + "-workspace") / "candidate/skills/build-semantic-okf-knowledge-skill"
    if not (candidate / "SKILL.md").is_file():
        raise ValueError("Unexpected realizer workspace layout")
    shutil.copyfile(HERE / "apply_retrieval_profile.template.py", candidate / "scripts/apply_retrieval_profile.py")
    write_json(candidate / "assets/retrieval-profile.json", {"schema_version": "retrieval-profile/1.0", "operations": operations})
    (candidate / "references/retrieval-profile.md").write_text("""# Explicit construction profile

This package includes a reproducible candidate profile. Read the exact operations
in `assets/retrieval-profile.json` before using it. Apply the profile only to a
closed plan for the selected family, before building and validating knowledge:

```bash
python -B scripts/apply_retrieval_profile.py --family FAMILY --input PLAN.json --output PROFILED_PLAN.json
```

Pass `PROFILED_PLAN.json` to the ordinary knowledge-skill generator with `--plan`.
Then run every matched family validator, deterministic rebuild and generated
expert verification required by the existing workflow. The transformation
preserves source selection, chunking, authoritative records and consultation
implementations. Planless families retain their normal commands. A mechanism
affects only existing supported parameters; it never invents missing plan fields.

A sentence-transformer operation requires the exact declared local model revision
and the matched optional locks. No download or fallback is authorized. A profile
is an experimental construction option until a separate frozen evaluation has
established its applicable scope; do not infer a universal ranking from its name.
""", encoding="utf-8")
    skill = candidate / "SKILL.md"
    text = skill.read_text(encoding="utf-8")
    insertion = "\nFor this candidate, read [retrieval-profile.md](references/retrieval-profile.md)\nand apply the explicit bundled construction profile to the selected plan before\nbuilding. Keep every existing validation and evidence requirement.\n"
    if insertion not in text:
        skill.write_text(text.replace("## Workflow\n", insertion + "\n## Workflow\n", 1), encoding="utf-8")
    sealed = call("seal", path)
    verified = call("verify", path)
    write_json(root / (identifier + "-receipt.json"), {"prepare": prepared, "seal": sealed, "verify": verified})
    print(json.dumps({"stage": "candidate-realization", "candidate": identifier, "status": "sealed"}), flush=True)
    return root / (identifier + "-sealed") / "candidate/skills/build-semantic-okf-knowledge-skill"


def main():
    parent = WORK / "baseline/build-semantic-okf-knowledge-skill"
    digest = call("digest", parent)["treeSha256"]
    organize("transition", "--stage-id", "realize", "--status", "running")
    grid = json.loads((HERE / "proposal-grid.json").read_text(encoding="utf-8"))
    candidates = {"baseline": str(parent)}
    for row in grid["generation_zero"]:
        operations = [{key: value for key, value in row.items() if key not in {"id", "mechanism"}}]
        candidate = realize(row["id"], operations, row["mechanism"] + " Keep every vendored implementation unchanged, use the exact reviewed profile helper, and preserve all authoritative identities.", parent, digest, HERE / "proposal-grid.json")
        candidates[row["id"]] = str(candidate)
        organize("record-evidence", "--evidence-id", "realized-" + row["id"], "--stage-id", "realize", "--kind", "candidate", "--role", "lineage", "--path", WORK / "realizations" / (row["id"] + "-sealed"))
    write_json(WORK / "generation-zero-candidates.json", candidates)
    organize("record-evidence", "--evidence-id", "realized-generation-zero", "--stage-id", "realize", "--kind", "other", "--role", "lineage", "--path", WORK / "generation-zero-candidates.json")
    organize("transition", "--stage-id", "realize", "--status", "completed")


if __name__ == "__main__":
    main()
