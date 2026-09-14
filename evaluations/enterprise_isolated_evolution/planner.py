"""Finite development decisions for a restricted, filesystem-free optimizer.

The trusted broker supplies only frozen public inputs and native development
observations. The planner emits typed requests, never commands or host paths.
After joint replay it emits one selection and exits. It has no validation API.
"""
from __future__ import annotations

import copy
import hashlib
import json
import math
import re
import sys
from typing import Any

FAMILIES = ("legacy", "turso", "adaptive", "embeddings", "classical", "graphify", "entity-graph", "ensemble")
OPEN_FAMILIES = ("entity-graph", "ensemble")
EPSILON = 1e-12


class ProtocolError(ValueError):
    """Reject incomplete, unexpected or inconsistent development evidence."""


def digest(value: Any) -> str:
    """Hash a finite canonical JSON value."""
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     allow_nan=False).encode()).hexdigest()


def exact(value: Any, fields: set[str], label: str) -> None:
    """Require a complete field inventory without silent extensions."""
    if type(value) is not dict or set(value) != fields:
        raise ProtocolError(f"Unexpected {label} fields")


def identifier(value: Any) -> None:
    """Require a portable logical identity without path syntax."""
    if type(value) is not str or re.fullmatch(r"[a-z0-9][a-z0-9-]{0,127}", value) is None:
        raise ProtocolError("Invalid logical identity")


def sha_value(value: Any) -> None:
    """Require one lowercase SHA-256 string."""
    if type(value) is not str or re.fullmatch(r"[0-9a-f]{64}", value) is None:
        raise ProtocolError("Invalid SHA-256")


def score(value: Any) -> float:
    """Validate an already computed native reward without scoring a task."""
    if type(value) not in (int, float) or not math.isfinite(value) or not 0 <= value <= 1:
        raise ProtocolError("Invalid native score")
    return value


def validate_plan(plan: dict) -> None:
    """Validate the entire public decision contract before emitting requests."""
    exact(plan, {"schema", "study_id", "families", "policy", "authority_sha256"}, "plan")
    if plan["schema"] != "enterprise-isolated-planner/1.0":
        raise ProtocolError("Unsupported planner contract")
    identifier(plan["study_id"])
    sha_value(plan["authority_sha256"])
    if plan["policy"] != {"maximum_rounds": 5, "consecutive_misses": 3,
                           "maximum_batch_size": 2, "initial_claims": 140,
                           "cumulative_cap": 585, "strict_gain_epsilon": EPSILON}:
        raise ProtocolError("Inherited finite policy changed")
    if type(plan["families"]) is not dict or set(plan["families"]) != set(FAMILIES):
        raise ProtocolError("All eight families are required")
    expected_caps = dict(zip(FAMILIES, (55, 55, 100, 40, 85, 65, 80, 105)))
    expected_claims = dict(zip(FAMILIES, (16, 16, 29, 6, 37, 24, 9, 3)))
    for family, row in plan["families"].items():
        exact(row, {"reference_id", "reference_score", "profile", "claims", "cap",
                    "catalog", "seen_profile_digests", "source_tree_sha256"}, "family")
        identifier(row["reference_id"])
        sha_value(row["source_tree_sha256"])
        if type(row["claims"]) is not int or type(row["cap"]) is not int:
            raise ProtocolError("Claims and caps must be integers")
        if (row["claims"], row["cap"]) != (expected_claims[family], expected_caps[family]):
            raise ProtocolError("Inherited family accounting changed")
        exact(row["profile"], {"plan", "search"}, "family profile")
        if any(type(row["profile"][key]) is not dict for key in ("plan", "search")):
            raise ProtocolError("Profile channels must be mappings")
        digest(row["profile"])
        if type(row["seen_profile_digests"]) is not list or len(set(row["seen_profile_digests"])) != len(row["seen_profile_digests"]):
            raise ProtocolError("Invalid inherited profile identities")
        for value in row["seen_profile_digests"]:
            sha_value(value)
        if family not in OPEN_FAMILIES:
            score(row["reference_score"])
            if row["catalog"] != []:
                raise ProtocolError("A closed family cannot acquire new opportunities")
            continue
        if row["reference_score"] is not None:
            raise ProtocolError("Prospective reference must be measured once")
        if type(row["catalog"]) is not list or not row["catalog"]:
            raise ProtocolError("Open family requires its finite catalog")
        catalog_ids = set()
        for mechanism in row["catalog"]:
            exact(mechanism, {"id", "rationale", "variants"}, "mechanism")
            identifier(mechanism["id"])
            if mechanism["id"] in catalog_ids:
                raise ProtocolError("Repeated mechanism")
            catalog_ids.add(mechanism["id"])
            if type(mechanism["rationale"]) is not str or not mechanism["rationale"]:
                raise ProtocolError("A mechanism needs a public rationale")
            if type(mechanism["variants"]) is not list or not mechanism["variants"]:
                raise ProtocolError("Empty mechanism")
            for variant in mechanism["variants"]:
                if type(variant) is not dict or not variant:
                    raise ProtocolError("Invalid catalog variant")
                if any(type(key) is not str or not key or "/" in key or "\\" in key for key in variant):
                    raise ProtocolError("Variant cannot name host files")
                digest(variant)


def qualified_observation(request: dict, result: dict, families: tuple[str, ...]) -> dict:
    """Require exact native identity, provenance and full qualification."""
    exact(result, {"request_sha256", "candidate_id", "skill_digest", "evaluable",
                   "qualified", "promotion_eligible", "exploratory", "expected_trials",
                   "completed_trials", "error_count", "case_scores", "native_record_sha256",
                   "archive_sha256", "archive_member"}, "native observation")
    if result["request_sha256"] != digest(request) or result["candidate_id"] != request["candidate_id"]:
        raise ProtocolError("Native observation belongs to another request")
    for key in ("skill_digest", "native_record_sha256", "archive_sha256"):
        sha_value(result[key])
    for key in ("evaluable", "qualified", "promotion_eligible", "exploratory", "archive_member"):
        if type(result[key]) is not bool:
            raise ProtocolError("Invalid native qualification flag")
    for key in ("expected_trials", "completed_trials", "error_count"):
        if type(result[key]) is not int:
            raise ProtocolError("Native counts must be integers")
    if not all(result[key] for key in ("evaluable", "qualified", "promotion_eligible")) or result["exploratory"]:
        raise ProtocolError("Unqualified native result; preserve it without a quality miss")
    if result["error_count"] != 0 or result["expected_trials"] != len(families) or result["completed_trials"] != len(families):
        raise ProtocolError("Incomplete or errored native observation")
    if type(result["case_scores"]) is not dict or set(result["case_scores"]) != set(families):
        raise ProtocolError("Native case inventory differs")
    for value in result["case_scores"].values():
        score(value)
    return result


class FamilySearch:
    """Keep one inherited finite construction catalog and strict incumbent."""

    def __init__(self, family: str, source: dict):
        self.family, self.source = family, copy.deepcopy(source)
        self.reference_id = self.best_id = source["reference_id"]
        self.reference_score = self.best_score = source["reference_score"]
        self.profile = copy.deepcopy(source["profile"])
        self.claims = source["claims"]
        self.round = 1
        self.operator = self.variant = self.misses = self.generation = 0
        self.round_start_score = self.best_score
        self.seen = set(source["seen_profile_digests"]) | {digest(self.profile)}
        self.events: list[dict] = []
        self.stop_reason = None if family in OPEN_FAMILIES else "inherited-catalog-closed"
        self.reference_digest = source["source_tree_sha256"]
        self.best_digest = self.reference_digest

    def qualify(self, result: dict) -> None:
        """Establish a new reference, without credit against a failed original."""
        if self.reference_score is not None:
            raise ProtocolError("First measurement already consumed")
        if result["skill_digest"] != self.reference_digest or not result["archive_member"]:
            raise ProtocolError("First measurement changed its source or lacks archive membership")
        self.reference_score = self.best_score = self.round_start_score = result["case_scores"][self.family]
        self.events.append({"event": "reference-qualified", "score": self.best_score, "gain_claimed": False})

    def next_mutation(self) -> dict | None:
        """Advance the full declared catalog until one unique variant or stop."""
        if self.reference_score is None:
            raise ProtocolError("Evolution requires a qualified first measurement")
        while self.stop_reason is None:
            catalog = self.source["catalog"]
            if self.operator == len(catalog):
                gained = self.best_score > self.round_start_score + EPSILON
                self.events.append({"event": "round-finished", "round": self.round, "improved": gained})
                if not gained or self.round == 5:
                    self.stop_reason = "full-round-without-improvement" if not gained else "outer-round-budget-exhausted"
                    break
                self.round += 1
                self.operator = self.variant = self.misses = 0
                self.round_start_score = self.best_score
                continue
            mechanism = catalog[self.operator]
            if self.misses == 3 or self.variant == len(mechanism["variants"]):
                self.events.append({"event": "mechanism-finished", "id": mechanism["id"],
                                    "round": self.round, "reason": "three-misses" if self.misses == 3 else "catalog-exhausted",
                                    "misses": self.misses})
                self.operator += 1
                self.variant = self.misses = 0
                continue
            variant = mechanism["variants"][self.variant]
            self.variant += 1
            profile = copy.deepcopy(self.profile)
            profile["plan"].update(copy.deepcopy(variant))
            profile_digest = digest(profile)
            if profile_digest in self.seen:
                self.events.append({"event": "duplicate-skipped", "profile_sha256": profile_digest})
                continue
            if self.claims == self.source["cap"]:
                self.stop_reason = "family-proposal-cap"
                break
            self.claims += 1
            self.generation += 1
            self.seen.add(profile_digest)
            return {"operation": "measure", "phase": "mutation", "family": self.family,
                    "candidate_id": f"variant-{self.generation:03d}", "parent_id": self.best_id,
                    "profile": profile, "profile_sha256": profile_digest,
                    "generation": self.generation, "mechanism": mechanism["id"],
                    "round": self.round, "cumulative_claims": self.claims}
        return None

    def observe(self, request: dict, result: dict) -> None:
        """Apply a qualified owner score and preserve ties as misses."""
        current = result["case_scores"][self.family]
        improved = current > self.best_score + EPSILON
        if improved:
            if not result["archive_member"]:
                raise ProtocolError("An improving candidate must belong to the native archive")
            self.best_id, self.best_score, self.best_digest = request["candidate_id"], current, result["skill_digest"]
            self.profile = copy.deepcopy(request["profile"])
            self.misses = 0
        else:
            self.misses += 1
        self.events.append({"event": "qualified-observation", "candidate_id": request["candidate_id"],
                            "score": current, "improved": improved, "misses": self.misses})

    def selection(self) -> dict:
        """Expose the exact terminal reference and retained family choice."""
        if self.stop_reason is None:
            raise ProtocolError("A family still has unvisited opportunities")
        return {"reference_id": self.reference_id, "reference_score": self.reference_score,
                "reference_tree_sha256": self.reference_digest, "selected_id": self.best_id,
                "selected_score": self.best_score, "selected_tree_sha256": self.best_digest,
                "selected_profile": copy.deepcopy(self.profile), "claims": self.claims,
                "cap": self.source["cap"], "stop_reason": self.stop_reason,
                "events": copy.deepcopy(self.events)}


class Planner:
    """Emit a complete finite development sequence and one irreversible freeze."""

    def __init__(self, plan: dict):
        validate_plan(plan)
        self.plan = copy.deepcopy(plan)
        self.plan_digest = digest(plan)
        self.families = {f: FamilySearch(f, plan["families"][f]) for f in FAMILIES}
        self.phase = "qualification"
        self.sequence = 0
        self.pending: dict | None = None
        self.joint_reference_digest: str | None = None
        self.joint_reference_archive: str | None = None
        self.failure: str | None = None

    def next_batch(self) -> dict:
        """Return a deterministic request; reject reissue of unobserved work."""
        if self.pending is not None or self.phase in ("frozen", "stopped"):
            raise ProtocolError("Planner is pending or terminal")
        if self.phase == "qualification":
            requests = [{"operation": "measure", "phase": "qualification", "family": f,
                         "candidate_id": self.families[f].reference_id} for f in OPEN_FAMILIES]
        elif self.phase == "mutation":
            requests = [r for f in OPEN_FAMILIES if (r := self.families[f].next_mutation()) is not None]
            if not requests:
                self.phase = "joint-reference"
                return self.next_batch()
        else:
            requests = [{"operation": "joint-replay", "phase": self.phase,
                         "candidate_id": "baseline" if self.phase == "joint-reference" else "selected",
                         "families": {f: self.families[f].selection() for f in FAMILIES}}]
        self.pending = {"schema": "enterprise-optimizer-batch/1.0", "plan_sha256": self.plan_digest,
                        "sequence": self.sequence, "requests": requests}
        return copy.deepcopy(self.pending)

    def accept(self, envelope: dict) -> dict | None:
        """Consume one exact batch; any unavailable result stops development."""
        if self.pending is None or self.phase in ("frozen", "stopped"):
            raise ProtocolError("No pending development batch")
        try:
            exact(envelope, {"batch_sha256", "results"}, "response envelope")
            if envelope["batch_sha256"] != digest(self.pending):
                raise ProtocolError("Response envelope belongs to another batch")
            requests = self.pending["requests"]
            if type(envelope["results"]) is not list or len(envelope["results"]) != len(requests):
                raise ProtocolError("Incomplete batch result inventory")
            # Validate the entire batch before any retention mutation. A failed
            # record never lets another family's next allocation slip through.
            checked = [qualified_observation(req, res, (req["family"],) if req["operation"] == "measure" else FAMILIES)
                       for req, res in zip(requests, envelope["results"])]
            old_phase = self.phase
            if old_phase == "qualification":
                for req, res in zip(requests, checked):
                    self.families[req["family"]].qualify(res)
                self.phase = "mutation"
            elif old_phase == "mutation":
                for req, res in zip(requests, checked):
                    self.families[req["family"]].observe(req, res)
            else:
                result = checked[0]
                attribute = "reference_score" if old_phase == "joint-reference" else "best_score"
                if any(abs(result["case_scores"][f] - getattr(self.families[f], attribute)) > EPSILON for f in FAMILIES):
                    raise ProtocolError("Joint replay did not reproduce every family's native score")
                if old_phase == "joint-reference":
                    self.joint_reference_digest = result["skill_digest"]
                    self.joint_reference_archive = result["archive_sha256"]
                    self.phase = "joint-selected"
                else:
                    unchanged = result["skill_digest"] == self.joint_reference_digest
                    if not unchanged and not result["archive_member"]:
                        raise ProtocolError("Frozen selection is absent from the native archive")
                    self.phase = "frozen"
                    selection = {"schema": "enterprise-optimizer-selection/1.0", "plan_sha256": self.plan_digest,
                                 "baseline_tree_sha256": self.joint_reference_digest,
                                 "selected_tree_sha256": result["skill_digest"],
                                 "selected_id": "baseline" if unchanged else "selected",
                                 "archive_sha256": result["archive_sha256"], "unchanged": unchanged,
                                 "families": {f: self.families[f].selection() for f in FAMILIES},
                                 "validation_observed": False, "further_optimization_permitted": False}
                    self.pending = None
                    return selection
            self.sequence += 1
            self.pending = None
            return None
        except (ValueError, TypeError, KeyError) as error:
            self.phase, self.failure = "stopped", str(error)
            raise


def main() -> None:
    """Use a bounded inherited stdio protocol; never resolve an input path."""
    def receive():
        line = sys.stdin.buffer.readline(2_000_001)
        if not line or len(line) > 2_000_000 or not line.endswith(b"\n"):
            raise ProtocolError("Missing or oversized broker input")
        def unique(pairs):
            value = {}
            for key, item in pairs:
                if key in value:
                    raise ProtocolError("Duplicate JSON key")
                value[key] = item
            return value
        return json.loads(line, object_pairs_hook=unique,
                          parse_constant=lambda _: (_ for _ in ()).throw(ProtocolError("Nonfinite JSON")))

    def emit(value):
        print(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False), flush=True)

    planner = Planner(receive())
    while planner.phase != "frozen":
        emit(planner.next_batch())
        selected = planner.accept(receive())
        if selected is not None:
            emit(selected)
            return


if __name__ == "__main__":
    main()
