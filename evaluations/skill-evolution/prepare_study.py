"""Register native datasets and the one-way study; never run candidate selection."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys

from prepare_experiment import HERE, REPO, WORK, TASKS, PROTOCOL, sha, tree, write_json, wsl_path


ORGANIZER = REPO.parent / "skill-arena/skills/harbor-organize-evaluations/scripts/manage_harbor_evaluations.py"
STUDY = WORK / "study"


def organize(command, *arguments):
    result = subprocess.run([sys.executable, "-B", str(ORGANIZER), command, str(STUDY), *map(str, arguments)], capture_output=True, text=True, encoding="utf-8", check=False)
    logs = WORK / "logs/organizer"
    logs.mkdir(parents=True, exist_ok=True)
    index = len(list(logs.glob("*.log")))
    (logs / f"{index:03d}-{command}.log").write_text(result.stdout + result.stderr, encoding="utf-8")
    if result.returncode:
        raise ValueError(f"Organizer {command} failed; inspect private log")


def register():
    organize("init", "--study-id", "knowledge-retrieval-" + WORK.name, "--title", "Construction profile evolution across internal retrieval workloads", "--objective", "Compare four source-generic construction mutations with the frozen multi-family baseline; preserve complementary development candidates and apply one terminal source-separated validation gate.", "--comparison-profile", "deterministic-retrieval-v1-cpu-offline")
    for name, split in [("internal-development-v1", "development"), ("transfer-fiqa-v1", "validation"), ("transfer-scifact-v1", "validation")]:
        organize("add-dataset", "--dataset-id", name, "--split", split, "--source", TASKS / name)
    organize("add-stage", "--stage-id", "realize", "--kind", "realization", "--owner-skill", "harbor-realize-skill-candidate")
    organize("add-stage", "--stage-id", "evolve", "--kind", "evolution", "--owner-skill", "harbor-reflective-pareto-search", "--dataset-id", "internal-development-v1", "--depends-on", "realize")
    organize("add-stage", "--stage-id", "validate", "--kind", "validation", "--owner-skill", "harbor-reflective-pareto-search", "--dataset-id", "transfer-fiqa-v1", "--dataset-id", "transfer-scifact-v1", "--depends-on", "evolve")
    organize("add-stage", "--stage-id", "publish", "--kind", "publication", "--owner-skill", "harbor-organize-evaluations", "--depends-on", "validate")
    print(json.dumps({"stage": "study-registration", "datasets": 3, "stages": 4, "status": "registered-unsealed"}))


def protocol():
    root = PROTOCOL
    root.mkdir(parents=True, exist_ok=False)
    grid = json.loads((HERE / "proposal-grid.json").read_text(encoding="utf-8"))
    baseline = WORK / "baseline/build-semantic-okf-knowledge-skill"
    for phase, datasets in [("development", ["internal-development-v1"]), ("validation", ["transfer-fiqa-v1", "transfer-scifact-v1"])]:
        job = {"job_name": "retrieval-" + phase, "jobs_dir": wsl_path(WORK / "native-jobs"), "n_attempts": 1, "n_concurrent_trials": 2, "quiet": True,
               "retry": {"max_retries": 0},
               "environment": {"type": "docker", "delete": True, "mounts": [{"type": "bind", "source": wsl_path(WORK / "models/hub"), "target": "/models/huggingface/hub", "read_only": True, "bind": {"create_host_path": False}}]},
               "agents": [{"name": "skill-retrieval", "import_path": "native_agent:SkillRetrievalAgent", "model_name": "local/deterministic-retrieval-v1", "skills": [wsl_path(baseline)]}],
               "datasets": [{"path": wsl_path(TASKS / name)} for name in datasets]}
        write_json(root / (phase + ".yaml"), job)
    write_json(root / "frozen-inputs.json", {"proposal_grid": grid, "proposal_sha256": sha(HERE / "proposal-grid.json"),
               "baseline": tree(baseline), "bridge_sha256": sha(HERE / "bridge.py"), "native_agent_sha256": sha(HERE / "native_agent.py"),
               "profile_template_sha256": sha(HERE / "apply_retrieval_profile.template.py"),
               "verifier_sha256": sha(HERE / "verifier.py"), "runtime": json.loads((WORK / "runtime.json").read_text()),
               "model_inventory_sha256": sha(WORK / "model-inventory.json"), "dataset_task_bytes": tree(TASKS),
               "correctness_qualification": json.loads((WORK / "correctness-qualification.json").read_text(encoding="utf-8")),
               "controller_file_sha256": {name: sha(HERE / name) for name in ("run_search.py", "prepare_study.py", "prepare_experiment.py", "realize_profiles.py", "validate_profile_candidate.py", "neutralize_inputs.py")},
               "job_template_sha256": {name: sha(root / name) for name in ("development.yaml", "validation.yaml")}})
    text = """# Frozen construction-profile study protocol

The target is the exact frozen integrated build-semantic-okf-knowledge-skill
package after the separately qualified Graphify correctness repair in ADR 0118.
Four historical internal corpora are development only: EnterpriseRAG
(40 queries, 985 documents), Astro (40, 416), architecture books (40, 18), and
data-science books (40, 38). Their shared local annotation workflow is treated
conservatively as one independence group. FiQA and SciFact have independently
authored source/annotation families and supply two validation groups, twelve
seeded test queries and 985 reference-enriched documents each. The same generic
machine interface is a measurement contract, not a semantic question template.
All actual questions and relevance labels remain source-specific.

This new campaign uses the short ignored repository-local tmp/e5 namespace.
Preserve 20260906-r2, which stopped before verification after mounted-artifact
collection failed on DrvFS, and e3, which exposed a Windows CRLF shell-entrypoint
defect and one real Graphify repeated-build determinism failure. Both campaigns
have zero valid retrieval scores and no private gate release. The Graphify
failure is a semantic construction defect, not an external retry opportunity.
Do not merge or replace either earlier native job. Correct the empty-heading
identity generically, verify two complete independent builds and source-generic
layout/link examples, then freeze the repaired baseline before this study.
Keep that correctness treatment separate from every construction-profile
mutation below. Generate task shell entrypoints with explicit LF and require an
independent native smoke that runs actual generated tasks without rewriting
their bytes, with production cleanup and concurrent trials. Bind those actual
qualification receipts in frozen-inputs.json. Reuse the exact unconsumed input
portfolio, seeds, model, runtime, hypotheses, and acceptance rules; task contracts
are regenerated against the new baseline and corrected adapter. Validation has
never been released and remains unavailable to diagnosis and candidate design.

Also preserve e4, which completed all 32 native baseline trials with zero errors
and full integrity, but failed the owning controller's declared/observed agent
profile check before any candidate job or accepted archive. Its 32 native scores
are diagnostic only and excluded from selection and promotion. The agent name
was null in JobConfig while Harbor truthfully recorded skill-retrieval. This
campaign explicitly declares that unchanged name beside the identical custom
import and local model marker. Do not alter or repair e4 native artifacts.
Require an independent source-generic smoke through the installed owning
controller, including baseline consolidation, real candidate dispatch and valid
archive creation. Bind its actual evidence and the e4 stop receipt before sealing.
Keep the exact unconsumed validation, historical development, predeclared
hypotheses, seeds, model, runtime and acceptance rules; this correction changes
declared identity metadata, not retrieval behavior. Prior attempts and synthetic
qualification are reported separately from this campaign's fixed trial budget.

The estimand is binary nDCG@10 averaged equally over dataset x family task cells,
using each family's predeclared default route. Each cell contains its complete
query cohort and also records every declared route (18 total). Recall@10, MRR@10,
full reference coverage, query P95, construction time and storage are secondary.
A descriptive cell pass means nDCG >=0.8; candidate qualification uses the
independent integrity gate and absence of errors, not this descriptive cutoff.
Query order and Top-10 are fixed. Relative changes in milliseconds are descriptive:
two concurrent trials, two numerical-library threads, two virtual CPU limits
per container, cold process per trial, warmed local model weights, no network, 12 GiB
agent memory ceiling and 8 GiB separate verifier ceiling. Record actual host
hardware and native runtime locks. One attempt, zero retries, 3600-second agent
timeout, 180-second verifier timeout. The native custom agent calls no LLM and
reports model identity local/deterministic-retrieval-v1 honestly as a local marker.

Generation zero evaluates baseline first, followed by the four frozen hypotheses
in proposal-grid.json. Only SKILL.md, scripts/apply_retrieval_profile.py,
assets/retrieval-profile.json and references/retrieval-profile.md may change.
The reviewed helper is fixed; mutations are closed profile operations. Every
vendored builder/consultant remains unchanged. Exact full package digests are
sealed by the realizer and native Harbor staging. Imported consultant hashes and
all returned authoritative record identities must match independent contracts.
Legacy and Turso ranking use frozen historical comparators; other routes execute
their staged native consultants. Two complete builds must have identical bytes.
The outer expert generator is separately forward-tested with synthetic data.

Reflective Pareto search is the sole evolution controller. A qualified candidate
must be error-free with evidence_integrity=1 on every development task. Preserve
non-dominated vectors across all 32 cells. Generation one is optional: materialize
at most four non-conflicting profile merges only when the native archive's merge
plan and complementary development cells support their archived parents. Include
the unchanged baseline again. Stop on no supported merge or after generation one.
Maximum 9 unique profiles including baseline, 352 study trials (160 generation
zero, at most 160 generation one, 32 final validation), zero model-provider calls.
Synthetic authoring/adapter smokes are separate and must be reported as such.
No semantic retry, selective task omission, seed search, or candidate rerun is
allowed. Preserve failures. Infrastructure corrections require a new campaign
or the separate external-failure recovery contract, never silent replay.

Select one qualified final-archive member by greatest mean development nDCG,
then fewer case regressions against baseline, then fewer profile operations,
then lexical candidate ID. A finalist must exceed baseline mean by at least 0.01
before consuming validation. If none does, retain baseline and leave validation
sealed. Record the exact finalist as candidate evidence and complete evolution
before the organizer releases the entire validation portfolio once.

The owning Pareto controller's holdout phase implements this study's mandatory
independent validation. It must preserve the exact development profile and both
candidate and baseline identities. Acceptance requires mean validation gain >=
0.01, no regression in any of the 16 dataset x family cells, no execution error,
and evidence_integrity=1 everywhere. This small transfer gate has two independent
source groups; do not infer statistical significance or broad generalization.
No additional holdout is declared. A rejected or non-evaluable gate is terminal:
do not mutate, merge, reselect, or rerun against it. Freeze complementary options
as experimental candidates; change canonical defaults only if the gate and
ordinary package tests support that scoped decision.

Curator authoring and independent review precede evolution. The host controller
is trusted and technically can read local files; filesystem hiding is not claimed
as adversarial isolation. Candidate execution receives only its current
evaluator-free corpus/queries, staged skill and read-only model cache in a Docker
container without networking. This WSL Docker kernel lacks the FIB nftables
feature required by Harbor's dynamic egress sidecar. Both environment/ and tests/
therefore contain digest-locked docker-compose.yaml files with main.network_mode:
none. The verifier Compose file additionally mounts its own task-local tests
directory read-only at /tests; the agent has no such mount. Harbor does not
automatically upload tests when the separate verifier uses a Compose definition.
Native phase policies are public only to leave network management to those
static Compose files; both physical containers must have no external interface.
Agent setup and verifier startup reject anything except loopback. The independent
native smoke inspects both containers' actual Docker NetworkMode. No Harbor
runtime, lock, scorer or result implementation is patched. Gold references and
verifiers are delivered to a
separate container after the agent. Validation tasks, seeds, references and all
case-level outcomes are excluded from root's candidate-generation inputs. A
separate reviewer inspects private validation and returns only quality approval
or aggregate blocking reasons before sealing. Public/pretraining contamination
cannot be excluded. Upstream archives and derived inputs are digest-bound.

Published results are aggregate retrieval diagnostics, not official EnterpriseRAG
scores, full-BEIR performance, autonomous-agent rankings, or grounded-answer
quality. Keep raw payloads, traces, skills-in-trials and all private cases ignored.
Publish only reviewed English reports with dataset, skill, route, cost/time and
failure denominators, source digests and explicit validation decision. Preserve
the existing report catalog and historical evidence.
"""
    text += "\n## Frozen input commitments\n\n" + "\n".join(f"- `{name}`: SHA-256 `{sha(root / name)}`." for name in ("development.yaml", "validation.yaml", "frozen-inputs.json")) + "\n"
    (root / "protocol.md").write_text(text, encoding="utf-8")
    print(json.dumps({"stage": "protocol", "status": "written-for-independent-review"}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=["register", "protocol", "seal"])
    args = parser.parse_args()
    if args.stage == "register":
        register()
    elif args.stage == "protocol":
        protocol()
    else:
        organize("seal-design", "--protocol", PROTOCOL / "protocol.md", "--baseline", WORK / "baseline/build-semantic-okf-knowledge-skill", "--review", WORK / "curator/review")
        print(json.dumps({"stage": "design-seal", "status": "sealed"}))
