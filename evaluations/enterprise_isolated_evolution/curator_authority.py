"""Independent E16 admission, one-way native acceptance, and terminal closure.

This source is frozen before private curation. It cannot admit any work until
an independent curator installs a complete, source-bound authority-anchor.json.
Only fixed control commands are accepted; private details never reach stdout.
"""
from __future__ import annotations

import contextlib
import copy
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
import traceback
import uuid

FAMILIES = ("legacy", "turso", "adaptive", "embeddings", "classical", "graphify", "entity-graph", "ensemble")
HEX = re.compile(r"[a-f0-9]{64}\Z")
SCHEMA = "enterprise-independent-curator-anchor/1.0"
REPO = Path("C:/Users/villa/dev/knowledge") if os.name == "nt" else Path("/mnt/c/Users/villa/dev/knowledge")


class Refused(RuntimeError):
    """Details are retained privately, never reflected to the broker."""


def require(condition, message):
    if not condition:
        raise Refused(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def host(value):
    value = str(value)
    if os.name == "nt" and value.startswith("/mnt/c/"):
        return Path("C:/" + value[7:])
    if os.name != "nt" and value[:3].lower() in ("c:/", "c:\\"):
        return Path("/mnt/c/" + value[3:].replace("\\", "/"))
    return Path(value)


def linux(path):
    value = path.absolute().as_posix()
    return "/mnt/c/" + value[3:] if value[:3].lower() == "c:/" else value


def regular(path, *, directory=False):
    path = host(path).absolute()
    current = path
    while True:
        if current.exists() or current.is_symlink():
            info = current.lstat()
            require(not stat.S_ISLNK(info.st_mode) and not getattr(info, "st_file_attributes", 0) & 0x400,
                    "Linked authority path")
        if current.parent == current:
            break
        current = current.parent
    require(path.is_dir() if directory else path.is_file(), "Missing authority artifact")
    return path


def scoped(path, root):
    path = host(path).absolute()
    require(path.resolve().is_relative_to(root.resolve()), "Authority path escape")
    current = path
    while current != root:
        if current.exists() or current.is_symlink():
            info = current.lstat()
            require(not stat.S_ISLNK(info.st_mode) and not getattr(info, "st_file_attributes", 0) & 0x400,
                    "Linked output path")
        current = current.parent
    return path


def read(path):
    def unique(pairs):
        value = {}
        for key, item in pairs:
            require(key not in value, "Duplicate JSON key")
            value[key] = item
        return value
    def invalid(_):
        raise Refused("Nonfinite JSON")
    return json.loads(regular(path).read_text(encoding="utf-8"), object_pairs_hook=unique, parse_constant=invalid)


def sha(path):
    output = hashlib.sha256()
    with regular(path).open("rb") as stream:
        while block := stream.read(1024 * 1024):
            output.update(block)
    return output.hexdigest()


def tree(path):
    root = regular(path, directory=True)
    entries, pending = [], [root]
    while pending:
        for node in os.scandir(pending.pop()):
            item, info = Path(node.path), node.stat(follow_symlinks=False)
            require(not stat.S_ISLNK(info.st_mode) and not getattr(info, "st_file_attributes", 0) & 0x400,
                    "Linked inventory node")
            kind = "directory" if stat.S_ISDIR(info.st_mode) else "file" if stat.S_ISREG(info.st_mode) else None
            require(kind is not None, "Special inventory node")
            entries.append((item.relative_to(root).as_posix(), kind, item))
            if kind == "directory": pending.append(item)
    value = hashlib.sha256()
    for relative, kind, item in sorted(entries, key=lambda row: (row[0].encode(), row[1])):
        value.update((b"D\0" if kind == "directory" else b"F\0") + relative.encode() + b"\0")
        if kind == "file":
            with item.open("rb") as stream:
                while block := stream.read(1024 * 1024): value.update(block)
            value.update(b"\0")
    return value.hexdigest()


def write_new(path, value, root):
    path = scoped(path, root)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())


def load_pinned(path, expected, name):
    require(HEX.fullmatch(expected) and sha(path) == expected, "Executable source drift")
    spec = importlib.util.spec_from_file_location(name, host(path))
    require(spec is not None and spec.loader is not None, "No module loader")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def journal(path):
    events, head, identities = [], "0" * 64, set()
    for line in regular(path).read_text(encoding="utf-8").splitlines():
        # Preserve strict duplicate/nonfinite checks without opening arbitrary paths.
        def unique(pairs):
            value = {}
            for key, item in pairs:
                require(key not in value, "Duplicate journal field")
                value[key] = item
            return value
        event = json.loads(line, object_pairs_hook=unique, parse_constant=lambda _: (_ for _ in ()).throw(Refused("Nonfinite journal")))
        require(set(event) == {"sequence", "previous_sha256", "kind", "payload", "sha256"}, "Journal fields")
        require(not events or events[-1]["kind"] != "terminal", "Post-terminal journal")
        claimed = event.pop("sha256")
        require(type(event["sequence"]) is int and event["sequence"] == len(events)
                and event["previous_sha256"] == head and digest(event) == claimed, "Journal integrity")
        event["sha256"] = head = claimed
        if event["kind"] == "allocated":
            identity = tuple(event["payload"]["identity"])
            require(identity not in identities, "Duplicate allocated identity")
            identities.add(identity)
        events.append(event)
    return events


def finite(value):
    return type(value) in (int, float) and math.isfinite(value)


def qualified_record(record, task_families):
    summary = record["summary"]
    cases = record["cases"]
    return (record["qualification"]["passed"] is True and record["evaluable"] is True
            and record["promotionEligibleProvenance"] is True and record["exploratory"] is False
            and summary["expectedTrials"] == summary["completedTrials"] == len(task_families)
            and type(summary["errorCount"]) is int and summary["errorCount"] == 0
            and record["qualification"]["missingRequiredRewards"] == 0
            and len(cases) == len(task_families)
            and {row["taskName"] for row in cases} == set(task_families)
            and all(row["attempts"] == 1 and row["evaluable"] is True and finite(row["meanReward"])
                    and row["errorCount"] == 0 for row in cases))


def safe_acceptance(promotion, records, task_families, selection, promotion_sha256):
    """Project native evidence to the exact public schema, including family gate."""
    require(len(task_families) == 16 and set(task_families.values()) == set(FAMILIES)
            and all(list(task_families.values()).count(family) == 2 for family in FAMILIES), "Private family partition")
    require(HEX.fullmatch(promotion_sha256) and HEX.fullmatch(selection["selected_tree_sha256"]), "Acceptance hashes")
    require(promotion["source"] == "harbor" and promotion["strategy"] == "reflective-pareto-search", "Native promotion authority")
    holdout = promotion["holdout"]
    require(len(records) == 2 and records[0]["candidateId"] == holdout["baselineCandidate"] == "baseline"
            and records[1]["candidateId"] == holdout["selectedCandidate"] == selection["selected_id"]
            and records[1]["skillDigest"] == promotion["selectedSkillDigest"], "Native arm or skill identity")
    require(host(records[0]["jobDirectory"]) == host(promotion["jobs"]["baseline"])
            and host(records[1]["jobDirectory"]) == host(promotion["jobs"]["candidate"]), "Native job binding")
    rows = holdout["perCase"]
    require(len(rows) == 16 and {row["taskName"] for row in rows} == set(task_families), "Acceptance case coverage")
    require(len({row["caseKey"] for row in rows}) == 16, "Repeated paired case")
    family_deltas = {family: [] for family in FAMILIES}
    for row in rows:
        delta = row["delta"]
        if row["evaluable"] is not True or not finite(delta):
            family_deltas[task_families[row["taskName"]]].append(None)
            continue
        require(finite(row["baselineMeanReward"]) and finite(row["candidateMeanReward"])
                and abs(delta - (row["candidateMeanReward"] - row["baselineMeanReward"])) <= 1e-12,
                "Native paired delta mismatch")
        family_deltas[task_families[row["taskName"]]].append(delta)
    native = (len(records) == 2 and all(qualified_record(record, task_families) for record in records)
              and holdout["promoted"] is True and holdout["blocked"] is False
              and all(holdout[name] is True for name in ("evaluable", "skillChanged", "baselineEvaluable", "candidateEvaluable",
                  "baselineQualified", "candidateQualified", "profileMatchesDeclared", "baselinePromotionEligibleProvenance",
                  "candidatePromotionEligibleProvenance", "requiredRewardsComplete")))
    strict = finite(holdout["meanGain"]) and holdout["meanGain"] > 0
    if finite(holdout["meanGain"]):
        require(finite(holdout["baselineMeanReward"]) and finite(holdout["candidateMeanReward"])
                and abs(holdout["meanGain"] - (holdout["candidateMeanReward"] - holdout["baselineMeanReward"])) <= 1e-12,
                "Native aggregate delta mismatch")
    families = all(len(values) == 2 and all(finite(value) for value in values) and math.fsum(values) / 2 >= 0
                   for values in family_deltas.values())
    accepted = bool(native and strict and families)
    return {"schema": "enterprise-independent-acceptance/1.0", "decision": "accepted-for-declared-scope" if accepted else "keep-baseline",
            "accepted": accepted, "validation_released": True, "selected_tree_sha256": selection["selected_tree_sha256"],
            "native_promotion_sha256": promotion_sha256, "native_qualified": bool(native),
            "native_strict_gain_passed": bool(strict), "all_family_gates_passed": bool(families)}


class Authority:
    def __init__(self, work):
        self.work = regular(host(work).absolute(), directory=True)
        require(self.work.is_relative_to(REPO), "Work outside authorized workspace")
        require(self.work == Path(__file__).absolute().parent.parent, "Authority installation scope")
        self.curator = regular(self.work / "curator", directory=True)
        self.anchor = read(self.curator / "authority-anchor.json")
        require(self.anchor["schema"] == SCHEMA and self.anchor["study_id"] == "enterprise-e16"
                and host(self.anchor["work"]).absolute() == self.work, "Unrecognized curator anchor")
        self.contract = read(self.work / "runtime-contract.json")
        self.plan = read(self.work / "plan.json")
        require(sha(self.work / "runtime-contract.json") == self.anchor["runtime_contract_sha256"]
                and digest(self.plan) == self.anchor["plan_sha256"] == self.contract["plan_sha256"], "Frozen public input changed")
        self.source_files = self.contract["source_files"]
        require(linux(Path(__file__)) in self.source_files and sha(Path(__file__)) == self.source_files[linux(Path(__file__))],
                "Curator executable was not frozen before curation")
        require(self.anchor["independent_review_completed"] is True and self.anchor["fresh_validation"] is True
                and self.anchor["private_task_families_path"] == linux(self.curator / "private-task-families.json"), "Incomplete independent anchor")
        require({linux(self.curator / "private-task-families.json"), self.contract["validation_job"]}
                .issubset(self.anchor["sealed_files"]), "Private bindings missing from sealed source inventory")
        self.organizer = None

    def source_check(self, *, private=True):
        for path, expected in self.source_files.items(): require(sha(path) == expected, "Public source drift")
        for path, expected in self.contract["source_trees"].items(): require(tree(path) == expected, "Public inventory drift")
        if private:
            for path, expected in self.anchor["sealed_files"].items(): require(sha(path) == expected, "Curator sealed source drift")
            for path, expected in self.anchor["sealed_trees"].items(): require(tree(path) == expected, "Curator sealed tree drift")
        path = self.contract["organizer"]
        self.organizer = load_pinned(path, self.source_files[path], "enterprise_e16_independent_organizer")

    def state(self, *, verify_sources=True):
        # The maintained organizer validates the full replay, dataset inventory,
        # review evidence and artifact digests. Its output remains in this process.
        state = self.organizer.build_state(self.work / "study", verify_sources=verify_sources)
        require(state["study"]["studyId"] == self.anchor["study_id"] and state["study"]["schemaVersion"] == 2, "Study identity")
        require(digest(state["designSeal"]) == self.anchor["design_seal_sha256"], "Independent seal drift")
        require({key: row["sha256"] for key, row in state["datasets"].items()} == self.anchor["dataset_digests"], "Registered dataset drift")
        definitions = {key: {field: row[field] for field in ("kind", "ownerSkill", "datasetIds", "dependsOn")}
                       for key, row in state["stages"].items()}
        require(definitions == self.anchor["stage_definitions"], "Prospective stage graph drift")
        return state

    def replay(self, events):
        """Validate recorded public requests against the frozen pure policy."""
        planner_path = linux(host(self.contract["optimizer_code"]) / "planner.py")
        expected = self.anchor["planner_source_sha256"]
        planner = load_pinned(planner_path, expected, "enterprise_e16_policy_replay").Planner(self.plan)
        pending, selected = None, None
        for event in events:
            if event["kind"] == "batch-received":
                require(pending is None and selected is None, "Unexpected optimizer batch")
                pending = planner.next_batch()
                require(event["payload"] == pending, "Recorded batch departs from finite public policy")
            elif event["kind"] == "batch-complete":
                require(pending is not None, "Completion without policy batch")
                selected = planner.accept(event["payload"])
                pending = None
            elif event["kind"] == "optimizer-terminated":
                require(selected is not None and event["payload"] == {"exit_code": 0, "selection_sha256": digest(selected)}, "Terminal selection differs from finite policy")
        return selected

    def optimizer_dead(self):
        receipt = read(self.work / "optimizer-exited.json")
        require(HEX.fullmatch(receipt["container_id"]) and receipt["state"]["Running"] is False
                and receipt["state"]["ExitCode"] == 0 and receipt["state"]["Pid"] == 0
                and receipt["stdin_closed"] is True and receipt["restart_permitted"] is False, "Optimizer remains resumable")
        result = subprocess.run(["wsl", "-d", "Ubuntu", "--", "docker", "container", "ls", "--all", "--no-trunc", "--format", "{{.ID}}"],
                                capture_output=True, check=False, timeout=45)
        require(result.returncode == 0 and receipt["container_id"] not in result.stdout.decode().splitlines(), "Optimizer container not removed")

    def frozen_selection(self, events):
        self.optimizer_dead()
        selected = self.replay(events)
        require(selected is not None and read(self.work / "selection.json") == selected, "Selection is not the completed public policy")
        gate = read(self.work / "gate.json")
        require(host(gate["search"]["outputDir"]) == self.curator / "native-acceptance"
                and gate["harbor"]["holdoutJob"] == self.contract["validation_job"]
                and gate["search"]["selectedCandidate"] == selected["selected_id"], "Fixed gate binding")
        require(gate["promotion"] == {"minimumMeanGain": 0.0, "allowCaseRegressions": True, "requireNoErrors": True}, "Predeclared native acceptance rules")
        require(sha(gate["search"]["developmentArchive"]) == selected["archive_sha256"], "Selected archive drift")
        candidate = next(row for row in gate["candidates"] if row["id"] == selected["selected_id"])
        baseline = next(row for row in gate["candidates"] if row["id"] == "baseline")
        require(tree(candidate["skill"]) == selected["selected_tree_sha256"]
                and tree(baseline["skill"]) == selected["baseline_tree_sha256"], "Exact selected bundle drift")
        return selected, gate

    def admit(self, phase):
        require(phase in ("development", "recalculation"), "Unknown admission phase")
        self.source_check()
        state = self.state()
        require(state["validationRelease"] is None and state["holdoutRelease"] is None
                and not (self.curator / "acceptance-attempt.json").exists(), "Private boundary already consumed")
        require(state["stages"]["validate"]["status"] == state["stages"]["publish"]["status"] == "planned", "Premature downstream lifecycle")
        events = journal(self.work / "authority.jsonl")
        require(not events or events[-1]["kind"] != "terminal", "Terminal campaign")
        if phase == "development":
            require(state["stages"]["evolve"]["status"] == "running"
                    and state["stages"]["recalculate"]["status"] == "planned"
                    and not (self.work / "optimizer-exited.json").exists(), "Development outside sealed lane")
            require(self.replay(events) is None, "Development policy already selected")
        else:
            require(state["stages"]["evolve"]["status"] == "completed"
                    and state["stages"]["recalculate"]["status"] == "running", "Recalculation order")
            self.frozen_selection(events)
        return {"admitted": True, "phase": phase, "study_id": self.anchor["study_id"]}

    def organize(self, action, *arguments):
        argv = [action, str(self.work / "study"), *map(str, arguments)]
        log = self.curator / "logs" / (uuid.uuid4().hex + "-" + action + ".log")
        scoped(log, self.work).parent.mkdir(parents=True, exist_ok=True)
        with log.open("x", encoding="utf-8") as stream, contextlib.redirect_stdout(stream), contextlib.redirect_stderr(stream):
            require(self.organizer.main(argv) == 0, "Native organizer operation refused")

    def accept(self):
        self.source_check()
        state = self.state()
        events = journal(self.work / "authority.jsonl")
        require(events and events[-1]["kind"] == "private-gate-requested", "No fixed broker private request")
        selected, gate = self.frozen_selection(events)
        require(selected["unchanged"] is False and events[-1]["payload"] == {"selection_sha256": digest(selected)}, "Private request is not exact frozen selection")
        require(state["validationRelease"] is None and state["holdoutRelease"] is None
                and state["stages"]["evolve"]["status"] == state["stages"]["recalculate"]["status"] == "completed"
                and state["stages"]["validate"]["status"] == state["stages"]["publish"]["status"] == "planned", "Acceptance lifecycle")
        require(not (self.curator / "native-acceptance").exists() and not (self.work / "safe-acceptance.json").exists(), "Private gate already attempted")
        mapping = read(self.anchor["private_task_families_path"])
        require(len(mapping) == 16 and set(mapping.values()) == set(FAMILIES)
                and all(list(mapping.values()).count(f) == 2 for f in FAMILIES), "Private partition")
        job = read(self.contract["validation_job"])
        require(job["n_attempts"] == 1 and job["retry"]["max_retries"] == 0 and job["n_concurrent_trials"] == 2
                and len(job["agents"]) == 1 and not job.get("datasets")
                and len(job["tasks"]) == 16 and {host(t["path"]).name for t in job["tasks"]} == set(mapping), "Registered native allocation")
        write_new(self.curator / "acceptance-attempt.json", {"schema":"enterprise-private-consumption/1.0", "selection_sha256":digest(selected),
                  "validation_job_sha256":sha(self.contract["validation_job"]), "dataset_digests":self.anchor["dataset_digests"],
                  "native_cap":32, "retry_permitted":False}, self.work)
        candidate = next(row for row in gate["candidates"] if row["id"] == selected["selected_id"])
        self.organize("release-validation", "--selection-id", "frozen-joint", "--selected-stage", "evolve", "--candidate-evidence", host(candidate["skill"]))
        self.organize("transition", "--stage-id", "validate", "--status", "running")
        released = self.state()
        write_new(self.curator / "release-authorization.json", {"schema":"enterprise-private-native-release/1.0",
                  "organizer_head_sha256":released["headSha256"], "gate_sha256":sha(self.work / "gate.json"),
                  "selection_sha256":digest(selected), "one_way":True}, self.work)
        for name in ("runtime-home", "runtime-temp", "runtime-cache"):
            (self.curator / name).mkdir(exist_ok=False)
        command = "import runpy,sys; scope=runpy.run_path(sys.argv[1],run_name='e16_curator_worker'); scope['native_gate'](sys.argv[2])"
        argv = ["wsl", "-d", "Ubuntu", "--cd", linux(REPO), "--", "env", "--ignore-environment",
                "PATH=/home/villa/.local/share/uv/tools/harbor/bin:/usr/local/bin:/usr/bin:/bin",
                "HOME=" + linux(self.curator / "runtime-home"), "TMPDIR=" + linux(self.curator / "runtime-temp"),
                "XDG_CACHE_HOME=" + linux(self.curator / "runtime-cache"), "PYTHONPATH=" + self.contract["agent_directory"],
                "PYTHONDONTWRITEBYTECODE=1", "HF_HUB_OFFLINE=1", "TRANSFORMERS_OFFLINE=1",
                self.contract["harbor_python"], "-B", "-c", command, linux(Path(__file__)), linux(self.work)]
        with (self.curator / "native-gate.log").open("xb") as stream:
            result = subprocess.run(argv, cwd=REPO, stdout=stream, stderr=subprocess.STDOUT, check=False)
        require(result.returncode == 0, "Native one-way gate did not complete; original artifacts retained")
        promotion_path = self.curator / "native-acceptance/holdout/promotion.json"
        promotion = read(promotion_path)
        records = [read(self.curator / "native-records" / (arm + ".json")) for arm in ("baseline", "selected")]
        require(tree(promotion["candidateSkill"]) == selected["selected_tree_sha256"], "Native candidate output drift")
        outcome = safe_acceptance(promotion, records, mapping, selected, sha(promotion_path))
        write_new(self.curator / "private-decision.json", {"safe":outcome, "promotion_sha256":sha(promotion_path),
                  "record_sha256":{arm:sha(self.curator / "native-records" / (arm + ".json")) for arm in ("baseline", "selected")}}, self.work)
        for arm in ("baseline", "candidate"):
            self.organize("record-evidence", "--evidence-id", "validation-native-" + arm, "--stage-id", "validate",
                          "--kind", "native-job", "--role", "validation", "--path", host(promotion["jobs"][arm]))
        self.organize("record-evidence", "--evidence-id", "validation-native-promotion", "--stage-id", "validate",
                      "--kind", "final-report", "--role", "validation", "--path", promotion_path)
        self.organize("record-evidence", "--evidence-id", "validation-independent-decision", "--stage-id", "validate",
                      "--kind", "decision", "--role", "validation", "--path", self.curator / "private-decision.json")
        self.organize("transition", "--stage-id", "validate", "--status", "completed")
        self.state()
        write_new(self.work / "safe-acceptance.json", outcome, self.work)

    def stop(self):
        # Deliberately avoid sealed_sources, task data, review payloads, rewards,
        # and release commands. The maintained replay checks recorded metadata.
        path = self.contract["organizer"]
        self.organizer = load_pinned(path, self.source_files[path], "enterprise_e16_independent_organizer")
        events = journal(self.work / "authority.jsonl")
        require(events and events[-1]["kind"] == "terminal" and events[-1]["payload"].get("status") != "complete",
                "Closure requires a drained terminal error")
        created = self.work / "optimizer-created.json"
        if created.exists():
            identity = read(created)["inspection"]["Id"]
            require(HEX.fullmatch(identity), "Optimizer identity")
            result = subprocess.run(["wsl", "-d", "Ubuntu", "--", "docker", "container", "ls", "--all", "--no-trunc", "--format", "{{.ID}}"],
                                    capture_output=True, timeout=45, check=False)
            require(result.returncode == 0 and identity not in result.stdout.decode().splitlines(), "Optimizer still exists")
        study = self.work / "study"
        # Normal organizer transition reconstructs review quality even with
        # verify_sources=False. Reuse its native event/transition primitives
        # here so terminal closure never opens private review or task files.
        with self.organizer.study_lock(study):
            state = metadata_state(self.organizer, study, self.anchor)
            for stage_id in reversed(state["stageOrder"]):
                stage = state["stages"][stage_id]
                if stage["status"] not in ("completed", "stopped"):
                    payload = {"stageId":stage_id, "fromStatus":stage["status"], "toStatus":"stopped",
                               "note":"Terminal native failure; admitted originals drained, optimizer closed, no retry or further release."}
                    self.organizer._apply_transition(state, payload)
                    event = self.organizer.append_event(study, state, "stage_transitioned", payload, self.organizer.timestamp(None))
                    state["events"].append(event)
                    state["headSha256"] = event["eventSha256"]


def metadata_state(organizer, study, anchor):
    """Read-only stage replay for stop; never opens dataset/review/evidence data."""
    events = organizer.load_events(study)
    study_value = read(study / "study.json")
    require(study_value["studyId"] == anchor["study_id"] and events[0]["event"] == "study_initialized"
            and events[0]["payload"]["studySha256"] == sha(study / "study.json"), "Closure study identity")
    state = {"study":study_value,"events":events,"headSha256":events[-1]["eventSha256"],
             "stages":{},"stageOrder":[],"datasets":{},"evidence":{},"designSeal":None,
             "validationRelease":None,"holdoutRelease":None}
    for event in events[1:]:
        kind, payload = event["event"], event["payload"]
        if kind == "stage_added":
            stage_id = payload["stageId"]
            require(stage_id not in state["stages"], "Duplicate closure stage")
            state["stages"][stage_id] = dict(payload, status="planned", evidenceIds=[], lastNote="")
            state["stageOrder"].append(stage_id)
        elif kind == "stage_transitioned":
            stage = state["stages"][payload["stageId"]]
            require(stage["status"] == payload["fromStatus"] and payload["toStatus"] in organizer.TRANSITIONS[stage["status"]], "Closure transition drift")
            stage["status"] = payload["toStatus"]
        elif kind == "design_sealed":
            require(state["designSeal"] is None and digest(payload) == anchor["design_seal_sha256"], "Closure seal drift")
            state["designSeal"] = payload
        elif kind in ("dataset_registered", "evidence_recorded", "validation_released", "holdout_released"):
            pass
        else:
            raise Refused("Unknown closure event")
    require(state["designSeal"] is not None and {key:{field:row[field] for field in ("kind","ownerSkill","datasetIds","dependsOn")}
            for key,row in state["stages"].items()} == anchor["stage_definitions"], "Closure graph differs from anchor")
    return state


def native_gate(work):
    """Pinned Linux evaluator entrypoint; no optimizer or general commands."""
    require(os.name != "nt", "Native authority must run under the declared Linux runtime")
    authority = Authority(work)
    authority.source_check()
    require((authority.curator / "acceptance-attempt.json").is_file(), "No consumed private attempt")
    # Windows organizer locks contain Windows source paths. The Linux worker
    # authenticates the native ledger and release head without reinterpreting
    # those dataset paths under Linux; the Windows authority verified sources.
    authorization = read(authority.curator / "release-authorization.json")
    events = authority.organizer.load_events(authority.work / "study")
    require(authorization["schema"] == "enterprise-private-native-release/1.0" and authorization["one_way"] is True
            and authorization["organizer_head_sha256"] == events[-1]["eventSha256"]
            and authorization["gate_sha256"] == sha(authority.work / "gate.json")
            and authorization["selection_sha256"] == digest(read(authority.work / "selection.json"))
            and events[-1]["event"] == "stage_transitioned"
            and events[-1]["payload"]["stageId"] == "validate" and events[-1]["payload"]["toStatus"] == "running"
            and sum(e["event"] == "validation_released" for e in events) == 1, "No registered native release")
    mapping = read(authority.anchor["private_task_families_path"])
    policy_path = authority.contract["executor_policy"]
    policy = load_pinned(policy_path, authority.source_files[policy_path],
                         "evaluations.enterprise_isolated_evolution.executor_policy")
    policy.install(authority.contract)
    owner = load_pinned(authority.contract["owner"], authority.contract["owner_sha256"], "enterprise_e16_private_native_owner")
    config = owner.normalize_config(authority.work / "gate.json")
    original_run = owner.run_candidate_jobs

    def guarded_run(config, *, phase, analyze_only, candidate_ids):
        require(phase == "holdout" and analyze_only is False
                and candidate_ids == [config["baselineCandidate"], config["selectedCandidate"]], "Unexpected private native request")
        records = []
        for identifier in candidate_ids:
            arm = "baseline" if identifier == config["baselineCandidate"] else "selected"
            write_new(authority.curator / "native-records" / (arm + "-allocated.json"),
                      {"candidate_id":identifier,"trials":16,"attempts":1,"automatic_retries":0}, authority.work)
            row = original_run(config, phase="holdout", analyze_only=False, candidate_ids=[identifier])[0]
            write_new(authority.curator / "native-records" / (arm + ".json"), row, authority.work)
            require(qualified_record(row, mapping), "Original private arm failed qualification; no subsequent allocation")
            records.append(row)
        return records

    owner.run_candidate_jobs = guarded_run
    try:
        result = owner.holdout(config, analyze_only=False)
        write_new(authority.curator / "native-result.json", result, authority.work)
    finally:
        owner.run_candidate_jobs = original_run


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    action = args[0] if args else ""
    require((action == "admit" and len(args) == 3) or (action in ("accept", "stop") and len(args) == 2), "Unsupported curator command")
    authority = Authority(args[-1])
    if action == "admit":
        print(json.dumps(authority.admit(args[1]), sort_keys=True))
    elif action == "accept":
        authority.accept()
    else:
        authority.stop()
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception:
        # A generic refusal is the entire caller-facing error channel. Write a
        # diagnostic only to this installed authority's own workspace subtree.
        try:
            root = Path(__file__).absolute().parent
            require(root.is_relative_to(REPO) and root.name == "curator", "No installed private log directory")
            root.joinpath("logs").mkdir(exist_ok=True)
            with (root / "logs" / (uuid.uuid4().hex + "-refusal.log")).open("x", encoding="utf-8") as stream:
                traceback.print_exc(file=stream)
        except Exception:
            pass
        print("Independent curator authority refused this operation.", file=sys.stderr)
        raise SystemExit(1)
