"""Fixed-request broker; private acceptance occurs after optimizer termination.

The broker is a trusted execution authority, not an adaptive optimizer. It
accepts no commands, arbitrary paths, model messages, or user-selected variants.
It delegates native scoring and provenance to the owning Harbor adapter.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import copy
import threading
from typing import Protocol

from .authority import Journal
from .planner import (FAMILIES, OPEN_FAMILIES, ProtocolError, digest, exact,
                      identifier, qualified_observation, sha_value, validate_plan)


class NativeAdapter(Protocol):
    """Implement only fixed native operations against a sealed study."""

    def verify_admission(self, phase: str) -> None: ...
    def execute_development(self, request: dict) -> dict: ...
    def verify_selection(self, selection: dict) -> None: ...
    def freeze(self, selection: dict) -> None: ...
    def recalculate(self, selection: dict, arm: str) -> dict: ...
    def complete_recalculation(self, selection: dict, records: list[dict]) -> None: ...
    def accept_private(self, selection: dict) -> dict: ...
    def publish(self, selection: dict, outcome: dict) -> dict: ...
    def stop_study(self) -> None: ...


class Broker:
    """Validate closed requests, drain admitted jobs and finalize once."""

    def __init__(self, plan: dict, journal: Journal, adapter: NativeAdapter):
        validate_plan(plan)
        self.plan, self.journal, self.adapter = copy.deepcopy(plan), journal, adapter
        self.sequence = 0
        self.phase = "qualification"
        self.stop = threading.Event()
        self.lock = threading.Lock()
        self.latest_batch = None
        self.profiles = {f: {row["reference_id"]: copy.deepcopy(row["profile"])} for f, row in plan["families"].items()}
        self.claims = {f: row["claims"] for f, row in plan["families"].items()}
        self.generations = dict.fromkeys(OPEN_FAMILIES, 0)
        self.references_qualified = False
        self.optimizer_dead = False
        self.finalized = False
        self.selection_sha256 = None

    def _validate_request(self, request: dict) -> None:
        phase = request.get("phase")
        if phase == "qualification":
            exact(request, {"operation", "phase", "family", "candidate_id"}, "qualification request")
            family = request["family"]
            if self.phase != phase or request["operation"] != "measure" or family not in OPEN_FAMILIES:
                raise ProtocolError("Unscheduled qualification")
            if request["candidate_id"] != self.plan["families"][family]["reference_id"]:
                raise ProtocolError("Qualification identity changed")
        elif phase == "mutation":
            exact(request, {"operation", "phase", "family", "candidate_id", "parent_id", "profile",
                            "profile_sha256", "generation", "mechanism", "round", "cumulative_claims"}, "mutation request")
            family = request["family"]
            if not self.references_qualified or self.phase not in ("qualification", "mutation") or family not in OPEN_FAMILIES or request["operation"] != "measure":
                raise ProtocolError("Mutation is outside the frozen development lane")
            if request["parent_id"] not in self.profiles[family]:
                raise ProtocolError("Unknown candidate parent")
            generation = self.generations[family] + 1
            if request["generation"] != generation or request["candidate_id"] != f"variant-{generation:03d}":
                raise ProtocolError("Mutation generation was skipped or repeated")
            if type(request["round"]) is not int or not 1 <= request["round"] <= 5:
                raise ProtocolError("Invalid catalog round")
            if request["cumulative_claims"] != self.claims[family] + 1 or request["cumulative_claims"] > self.plan["families"][family]["cap"]:
                raise ProtocolError("Proposal cap or cumulative charge differs")
            if digest(request["profile"]) != request["profile_sha256"]:
                raise ProtocolError("Mutation profile digest differs")
            mechanism = next((r for r in self.plan["families"][family]["catalog"] if r["id"] == request["mechanism"]), None)
            if mechanism is None:
                raise ProtocolError("Unknown mutation mechanism")
            allowed = []
            for variant in mechanism["variants"]:
                profile = copy.deepcopy(self.profiles[family][request["parent_id"]])
                profile["plan"].update(variant)
                allowed.append(profile)
            if request["profile"] not in allowed:
                raise ProtocolError("Mutation is outside the declared finite catalog")
        else:
            exact(request, {"operation", "phase", "candidate_id", "families"}, "joint request")
            if request["operation"] != "joint-replay" or set(request["families"]) != set(FAMILIES):
                raise ProtocolError("Incomplete joint replay request")
            if phase == "joint-reference":
                if not self.references_qualified or self.phase not in ("qualification", "mutation") or request["candidate_id"] != "baseline":
                    raise ProtocolError("Joint reference is out of order")
            elif phase == "joint-selected":
                if self.phase != "joint-reference" or request["candidate_id"] != "selected":
                    raise ProtocolError("Joint selected arm is out of order")
            else:
                raise ProtocolError("Unknown development operation")
            for family, selection in request["families"].items():
                if selection["reference_id"] != self.plan["families"][family]["reference_id"]:
                    raise ProtocolError("Joint reference identity changed")
                if selection["selected_id"] not in self.profiles[family] or selection["selected_profile"] != self.profiles[family][selection["selected_id"]]:
                    raise ProtocolError("Joint selection contains an unknown family profile")
                if selection["claims"] != self.claims[family] or not selection["stop_reason"]:
                    raise ProtocolError("Joint family accounting is incomplete")
        identifier(request["candidate_id"])

    def execute_batch(self, batch: dict) -> dict:
        """Admit one exact batch; latch invalid native qualification before reuse."""
        try:
            self.journal.authority.require()
            if self.stop.is_set() or self.optimizer_dead or self.finalized:
                raise ProtocolError("Development authority is terminal")
            exact(batch, {"schema", "plan_sha256", "sequence", "requests"}, "optimizer batch")
            if batch["schema"] != "enterprise-optimizer-batch/1.0" or batch["plan_sha256"] != digest(self.plan) or batch["sequence"] != self.sequence:
                raise ProtocolError("Optimizer contract or sequence drift")
            requests = batch["requests"]
            if type(requests) is not list or not 1 <= len(requests) <= 2:
                raise ProtocolError("Invalid native batch size")
            for request in requests:
                self._validate_request(request)
            if len({r.get("family", "joint") for r in requests}) != len(requests):
                raise ProtocolError("Repeated family in one batch")
            if len({r["phase"] for r in requests}) != 1:
                raise ProtocolError("Mixed native phases")
            phase = requests[0]["phase"]
            if phase == "qualification" and {r["family"] for r in requests} != set(OPEN_FAMILIES):
                raise ProtocolError("Both first measurements are required")
            self.journal.append("batch-received", batch)

            def execute(request):
                try:
                    with self.lock:
                        if self.stop.is_set():
                            raise ProtocolError("Another native request stopped the batch")
                        self.adapter.verify_admission("development")
                        self.journal.consume(request)
                    # The OS authority lease remains held by the parent for
                    # the complete native operation and its qualification.
                    result = self.adapter.execute_development(request)
                    qualified_observation(request, result, (request["family"],) if request["operation"] == "measure" else FAMILIES)
                    with self.lock:
                        self.journal.append("native-observed", result)
                    return result
                except BaseException:
                    self.stop.set()
                    raise

            with ThreadPoolExecutor(max_workers=2) as pool:
                futures = [pool.submit(execute, request) for request in requests]
                # Retrieve every admitted original even if another fails.
                results, errors = [], []
                for future in futures:
                    try:
                        results.append(future.result())
                    except BaseException as error:
                        errors.append(error)
                if errors:
                    raise errors[0]
            for req in requests:
                if phase == "mutation":
                    family = req["family"]
                    self.profiles[family][req["candidate_id"]] = copy.deepcopy(req["profile"])
                    self.claims[family] += 1
                    self.generations[family] += 1
            self.references_qualified |= phase == "qualification"
            self.phase = phase
            self.sequence += 1
            self.latest_batch = copy.deepcopy(batch)
            envelope = {"batch_sha256": digest(batch), "results": results}
            self.journal.append("batch-complete", envelope)
            return envelope
        except BaseException as error:
            self.stop.set()
            if not self.journal.terminal:
                self.journal.append("terminal", {"status": "development-stopped", "reason": type(error).__name__,
                                                 "private_release": False, "retry_permitted": False})
            raise

    def optimizer_exited(self, exit_code: int, selection: dict) -> None:
        """Admit one final selection only after the optimizer process exited."""
        exact(selection, {"schema", "plan_sha256", "baseline_tree_sha256", "selected_tree_sha256",
                          "selected_id", "archive_sha256", "unchanged", "families", "validation_observed",
                          "further_optimization_permitted"}, "selection")
        if type(exit_code) is not int or exit_code != 0 or self.phase != "joint-selected" or self.optimizer_dead or self.stop.is_set():
            raise ProtocolError("Optimizer has not completed its one-way development sequence")
        if selection["schema"] != "enterprise-optimizer-selection/1.0" or selection["plan_sha256"] != digest(self.plan):
            raise ProtocolError("Selection contract differs")
        if selection["validation_observed"] is not False or selection["further_optimization_permitted"] is not False:
            raise ProtocolError("Selection crossed the private boundary")
        for key in ("baseline_tree_sha256", "selected_tree_sha256", "archive_sha256"):
            sha_value(selection[key])
        if selection["families"] != self.latest_batch["requests"][0]["families"]:
            raise ProtocolError("Selection differs from the exact joint replay")
        self.adapter.verify_selection(selection)
        self.journal.append("optimizer-terminated", {"exit_code": 0, "selection_sha256": digest(selection)})
        self.selection_sha256 = digest(selection)
        self.optimizer_dead = True

    def finalize(self, selection: dict) -> dict:
        """Execute frozen comparison and one private gate with no optimizer alive."""
        if not self.optimizer_dead or self.finalized or self.stop.is_set():
            raise ProtocolError("Finalization requires a terminated optimizer")
        try:
            if digest(selection) != self.selection_sha256:
                raise ProtocolError("Finalization changed the terminated optimizer selection")
            self.adapter.verify_selection(selection)
            self.journal.append("freeze-requested", selection)
            self.adapter.freeze(selection)
            records = []
            for arm in ("baseline", "frozen"):
                self.adapter.verify_admission("recalculation")
                request = {"phase": "recalculation", "candidate_id": arm, "selection_sha256": digest(selection)}
                self.journal.consume(request)
                records.append(self.adapter.recalculate(selection, arm))
            self.adapter.complete_recalculation(selection, records)
            if selection["unchanged"]:
                outcome = {"decision": "baseline-retained", "accepted": False, "validation_released": False,
                           "reason": "no-skill-change", "selected_tree_sha256": selection["selected_tree_sha256"]}
            else:
                self.journal.append("private-gate-requested", {"selection_sha256": digest(selection)})
                outcome = self.adapter.accept_private(selection)
                exact(outcome, {"schema", "decision", "accepted", "validation_released", "selected_tree_sha256",
                                "native_promotion_sha256", "native_qualified", "native_strict_gain_passed",
                                "all_family_gates_passed"}, "safe acceptance")
                for key in ("selected_tree_sha256", "native_promotion_sha256"):
                    sha_value(outcome[key])
                flags = ("native_qualified", "native_strict_gain_passed", "all_family_gates_passed")
                if (outcome["schema"] != "enterprise-independent-acceptance/1.0"
                        or any(type(outcome[k]) is not bool for k in (*flags, "accepted"))
                        or outcome["accepted"] != all(outcome[k] for k in flags)
                        or outcome["decision"] != ("accepted-for-declared-scope" if outcome["accepted"] else "keep-baseline")
                        or outcome["selected_tree_sha256"] != selection["selected_tree_sha256"]
                        or outcome["validation_released"] is not True):
                    raise ProtocolError("Independent acceptance returned an incomplete frozen result")
            publication = self.adapter.publish(selection, outcome)
            self.journal.append("terminal", {"status": "complete", "outcome": outcome,
                                             "publication": publication, "reselection_permitted": False})
            self.finalized = True
            return outcome
        except BaseException as error:
            self.stop.set()
            self.journal.append("terminal", {"status": "finalization-stopped", "reason": type(error).__name__,
                                             "optimizer_terminated": True, "retry_permitted": False})
            raise
