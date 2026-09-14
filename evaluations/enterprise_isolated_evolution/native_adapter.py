"""Fixed trusted study lifecycle around the installed native Harbor tools."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import subprocess
import sys

from .composition import compose
from .files import PROFILE, REPO, SKILL_NAME, host, inventory, posix, read, sha, write
from .planner import FAMILIES, OPEN_FAMILIES, ProtocolError, digest


class HarborAdapter:
    """Resolve closed requests to precommitted sources and native operations."""

    def __init__(self, work: Path, plan: dict, contract: dict):
        self.work, self.plan, self.contract = work, plan, contract
        self.candidates = {family: [{"id": row["reference_id"], "skill": contract["sources"][family],
                                    "parents": [], "rationale": "Exact prospectively registered family reference."}]
                           for family, row in plan["families"].items()}
        self.joint = []
        self.archives = {}
        self.gate_path = None
        self.recalculation = []

    def _run(self, argv: list[str], log: Path) -> None:
        log.parent.mkdir(parents=True, exist_ok=True)
        with log.open("xb") as stream:
            result = subprocess.run(argv, cwd=REPO, stdout=stream, stderr=subprocess.STDOUT, check=False)
        if result.returncode:
            raise ProtocolError(f"Trusted native operation failed; original log retained ({log.name})")

    def _organize(self, action: str, *arguments) -> None:
        counter = len(list((self.work / "organizer-logs").glob("*.log")))
        self._run([sys.executable, "-B", str(host(self.contract["organizer"])), action,
                   str(self.work / "study"), *map(str, arguments)], self.work / "organizer-logs" / f"{counter:03d}-{action}.log")

    def verify_admission(self, phase: str) -> None:
        """Recheck all implementation inputs and independent current admission."""
        for path, expected in self.contract["source_files"].items():
            if sha(host(path)) != expected:
                raise ProtocolError("Frozen source file changed")
        for path, expected in self.contract["source_trees"].items():
            if inventory(host(path))[0] != expected:
                raise ProtocolError("Frozen source inventory changed")
        if self.contract["curator_authority"] not in self.contract["source_files"]:
            raise ProtocolError("Curator authority has no precommitted implementation digest")
        # The independently authored authority verifies the organizer replay,
        # exact dataset locks, private nonrelease and the frozen launch digest.
        completed = subprocess.run([sys.executable, "-B", str(host(self.contract["curator_authority"])),
                                    "admit", phase, str(self.work)], cwd=REPO, capture_output=True, check=False)
        if completed.returncode:
            raise ProtocolError("Independent current study admission refused")
        if json.loads(completed.stdout) != {"admitted": True, "phase": phase, "study_id": self.plan["study_id"]}:
            raise ProtocolError("Unexpected independent admission response")

    def _worker(self, operation: str, config_path: Path, candidate_id: str, output: Path, task_group: str) -> dict:
        output.mkdir(parents=True, exist_ok=False)
        request = {"operation": operation, "owner": self.contract["owner"], "owner_sha256": self.contract["owner_sha256"],
                   "runtime_contract": posix(self.work / "runtime-contract.json"),
                   "runtime_contract_sha256": sha(self.work / "runtime-contract.json"),
                   "config": posix(config_path), "candidate_id": candidate_id, "output": posix(output),
                   "task_families": self.contract["task_families"].get(task_group, {}),
                   "reporter": self.contract["reporter"], "reporter_sha256": self.contract["reporter_sha256"]}
        write(output / "request.json", request)
        self._run(["wsl", "-d", "Ubuntu", "--cd", posix(REPO), "--", "env",
                   "PYTHONPATH=" + posix(host(self.contract["agent_directory"])),
                   self.contract["harbor_python"], "-B", "-m", "evaluations.enterprise_isolated_evolution.native_worker",
                   posix(output / "request.json")], output / "native.log")
        return read(output / "response.json")

    def _config(self, group: str, generation: int, candidates: list[dict]) -> dict:
        baseline = candidates[0]
        raw = {"schemaVersion": 1, "search": {"id": self.plan["study_id"] + "-" + group,
                 "baselineSkill": baseline["skill"], "baselineCandidate": baseline["id"],
                 "outputDir": posix(self.work / "recalculation/native" if group == "recalculation" else self.work / "search" / group), "generation": generation},
               "harbor": {"developmentJob": self.contract["jobs"][group],
                          "holdoutJob": self.contract["validation_job"], "rewardKey": "reward",
                          "passThreshold": .8, "requiredRewards": {"evidence_integrity": 1}, "requiredEnv": []},
               "candidates": copy.deepcopy(candidates),
               "promotion": {"minimumMeanGain": 0.0, "allowCaseRegressions": group == "joint", "requireNoErrors": True}}
        if generation:
            raw["search"]["previousGenerationLog"] = posix(self.archives[group])
        return raw

    def _realize(self, request: dict) -> Path:
        family, identifier = request["family"], request["candidate_id"]
        parent = host(next(c["skill"] for c in self.candidates[family] if c["id"] == request["parent_id"]))
        root = self.work / "realizations" / family / identifier
        profile = read(parent / PROFILE)
        profile[family] = request["profile"]
        write(root / "mutation.json", request)
        validation = {"expected_profile": profile, "parent_files": inventory(parent)[1]}
        write(root / "validation-contract.json", validation)
        config = {"schemaVersion": 1, "realization": {
            "id": family + "-" + identifier, "candidateId": identifier, "parentSkill": str(parent),
            "expectedParentTreeSha256": "sha256:" + inventory(parent)[0], "workspaceDir": str(root / "workspace"),
            "outputDir": str(root / "sealed"), "operator": {"operatorId": request["mechanism"],
                "instruction": "Apply exactly the bound public family profile. Preserve every other package byte.",
                "origin": "predeclared-development-hypothesis", "parentOperatorIds": []},
            "allowedChanges": [PROFILE], "trustedValidationCommands": True,
            "validationCommands": [{"id": "exact-family-profile", "argv": [sys.executable, "-B",
                str(Path(__file__).with_name("validate_candidate.py")), str(root / "validation-contract.json")], "timeoutSeconds": 60}],
            "developmentEvidence": [{"id": "finite-public-mutation", "role": "development", "path": str(root / "mutation.json"),
                                     "sha256": "sha256:" + sha(root / "mutation.json")},
                                    {"id": "native-parent-archive", "role": "development", "path": str(self.archives[family]),
                                     "sha256": "sha256:" + sha(self.archives[family])}]}}
        write(root / "realizer.json", config)
        def realize(action):
            self._run([sys.executable, "-B", str(host(self.contract["realizer"])), action, str(root / "realizer.json")], root / (action + ".log"))
        realize("prepare")
        target = root / "workspace/candidate/skills" / SKILL_NAME / PROFILE
        target.write_text(json.dumps(profile, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8", newline="\n")
        realize("seal")
        realize("verify")
        return root / "sealed/candidate/skills" / SKILL_NAME

    def execute_development(self, request: dict) -> dict:
        """Realize an exact profile, or replay one exact composed bundle."""
        if request["operation"] == "measure":
            group = request["family"]
            generation = request.get("generation", 0)
            candidates = self.candidates[group]
            if request["phase"] == "mutation":
                candidate = self._realize(request)
                candidates.append({"id": request["candidate_id"], "skill": posix(candidate),
                                   "parents": [request["parent_id"]], "rationale": "Exact isolated planner request " + digest(request)})
        else:
            group, candidates = "joint", self.joint
            generation = 0 if request["phase"] == "joint-reference" else 1
            if generation == 0:
                skill = host(self.contract["reference_composition"])
            else:
                sources = {f: host(next(c["skill"] for c in self.candidates[f] if c["id"] == request["families"][f]["selected_id"])) for f in FAMILIES}
                skill = self.work / "composition/selected" / SKILL_NAME
                receipt = compose(host(self.contract["reference_base"]), sources, skill,
                                  expected={f: request["families"][f]["selected_tree_sha256"] for f in FAMILIES},
                                  external_drift=self.contract["external_drift"])
                write(self.work / "composition/selected-receipt.json", receipt)
            candidates.append({"id": request["candidate_id"], "skill": posix(skill), "parents": [] if generation == 0 else ["baseline"],
                               "rationale": "Exact disjoint-family composition; mandatory joint reproduction."})
        output = self.work / "dispatch" / group / f"generation-{generation:03d}"
        config_path = output.parent / (f"generation-{generation:03d}.json")
        write(config_path, self._config(group, generation, candidates))
        result = self._worker("development", config_path, request["candidate_id"], output, group)
        analyzed = read(output / "analyzed.json")
        candidates[:] = analyzed["candidates"]
        self.archives[group] = self.work / "search" / group / "development" / f"generation-{generation:03d}" / "pareto-archive.json"
        if group == "joint" and generation == 1:
            self.gate_path = output / "analyzed.json"
        return dict(result, request_sha256=digest(request))

    def verify_selection(self, selection: dict) -> None:
        """Check the archive member and exact complete bundle without selection."""
        if self.gate_path is None or sha(self.archives["joint"]) != selection["archive_sha256"]:
            raise ProtocolError("Final selection has no exact current joint archive")
        archive = read(self.archives["joint"])
        member = next((m for m in archive["archive"] if m["candidateId"] == selection["selected_id"]), None)
        if member is None or not member["qualified"] or not member["promotionEligibleProvenance"]:
            raise ProtocolError("Final selection lacks qualified native archive membership")
        for key, identifier in (("selected_tree_sha256", selection["selected_id"]), ("baseline_tree_sha256", "baseline")):
            candidate = next(c for c in self.joint if c["id"] == identifier)
            if inventory(host(candidate["skill"]))[0] != selection[key]:
                raise ProtocolError("Frozen bundle changed")
        if type(selection["unchanged"]) is not bool or selection["unchanged"] != (selection["selected_tree_sha256"] == selection["baseline_tree_sha256"]):
            raise ProtocolError("Unchanged selection flag differs from exact bundles")

    def freeze(self, selection: dict) -> None:
        """Bind one archive-selected candidate and close optimizer-visible work."""
        write(self.work / "selection.json", selection)
        gate = read(self.gate_path)
        gate["search"].update(selectedCandidate=selection["selected_id"], developmentArchive=posix(self.archives["joint"]),
                              outputDir=posix(self.work / "curator/native-acceptance"))
        write(self.work / "gate.json", gate)
        self._worker("verify-selection", self.work / "gate.json", selection["selected_id"], self.work / "freeze-verification", "joint")
        for identifier, kind, role, path in (
            ("native-development", "evolution-report", "development", self.work / "search"),
            ("frozen-selection", "decision", "decision", self.work / "selection.json"),
            ("frozen-candidate", "candidate", "development", host(next(c["skill"] for c in self.joint if c["id"] == selection["selected_id"]))),
        ):
            self._organize("record-evidence", "--evidence-id", identifier, "--stage-id", "evolve", "--kind", kind,
                           "--role", role, "--path", path)
        self._organize("transition", "--stage-id", "evolve", "--status", "completed")
        self._organize("transition", "--stage-id", "recalculate", "--status", "running")

    def recalculate(self, selection: dict, arm: str) -> dict:
        """Run one fixed all-500 arm after the optimizer process has exited."""
        candidate_id = "baseline" if arm == "baseline" else selection["selected_id"]
        candidate = next(c for c in self.joint if c["id"] == candidate_id)
        self.recalculation.append({"id": arm, "skill": candidate["skill"], "parents": [] if arm == "baseline" else ["baseline"],
                                   "rationale": "Frozen all-500 comparison only; no reselection."})
        raw = self._config("recalculation", 0, self.recalculation)
        config = self.work / "recalculation" / (arm + ".json")
        write(config, raw)
        result = self._worker("recalculation", config, arm, self.work / "recalculation" / arm, "recalculation")
        self.recalculation[:] = read(host(result["config"]))["candidates"]
        return result

    def complete_recalculation(self, selection: dict, records: list[dict]) -> None:
        """Require native comparison, qualification and source parity for 16 trials."""
        if len(records) != 2 or inventory(host(self.recalculation[-1]["skill"]))[0] != selection["selected_tree_sha256"]:
            raise ProtocolError("Frozen comparison does not cover the selected bundle")
        config = self.work / "recalculation/compare.json"
        write(config, self._config("recalculation", 0, self.recalculation))
        self._worker("compare", config, "frozen", self.work / "recalculation/comparison", "recalculation")
        self._organize("record-evidence", "--evidence-id", "all-500-native-comparison", "--stage-id", "recalculate",
                       "--kind", "final-report", "--role", "development", "--path", self.work / "recalculation/comparison")
        self._organize("transition", "--stage-id", "recalculate", "--status", "completed")

    def accept_private(self, selection: dict) -> dict:
        """Invoke independent fixed acceptance after complete optimizer termination."""
        self._run([sys.executable, "-B", str(host(self.contract["curator_authority"])), "accept", str(self.work)],
                  self.work / "curator-invocation.log")
        return read(self.work / "safe-acceptance.json")

    def stop_study(self) -> None:
        """Close remaining stages after admitted originals and optimizer have ended."""
        path = self.contract["curator_authority"]
        if self.contract["source_files"].get(path) != sha(host(path)):
            raise ProtocolError("Cannot execute an unbound stop authority")
        self._run([sys.executable, "-B", str(host(path)), "stop", str(self.work)], self.work / "curator-stop.log")

    def publish(self, selection: dict, outcome: dict) -> dict:
        """Record a terminal aggregate artifact; canonical installation is separate."""
        from .publication import publish
        result = publish(self.work, self.plan, selection, outcome)
        if selection["unchanged"]:
            self._organize("transition", "--stage-id", "validate", "--status", "stopped", "--note", "Unchanged bundle; private portfolio remains unopened.")
        # The curator closes acceptance and opens publication for changed bundles.
        self._organize("transition", "--stage-id", "publish", "--status", "running")
        self._organize("record-evidence", "--evidence-id", "reviewable-aggregate-draft", "--stage-id", "publish",
                       "--kind", "final-report", "--role", "development", "--path", self.work / "aggregate-draft")
        self._organize("transition", "--stage-id", "publish", "--status", "completed")
        return result
