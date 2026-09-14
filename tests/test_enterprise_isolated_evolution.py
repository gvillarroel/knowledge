"""Behavioral checks for the finite policy, authority and one-way lifecycle."""
from __future__ import annotations

import copy
import json
from pathlib import Path, PurePosixPath
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest.mock import Mock, patch
from types import SimpleNamespace

from evaluations.enterprise_isolated_evolution.authority import ExclusiveAuthority, Journal, safe_path, verify_journal
from evaluations.enterprise_isolated_evolution.broker import Broker
from evaluations.enterprise_isolated_evolution.files import REPO, inventory, parse_json
from evaluations.enterprise_isolated_evolution.planner import FAMILIES, OPEN_FAMILIES, FamilySearch, Planner, ProtocolError, digest, validate_plan


def example_plan():
    caps, claims = (55, 55, 100, 40, 85, 65, 80, 105), (16, 16, 29, 6, 37, 24, 9, 3)
    return {"schema": "enterprise-isolated-planner/1.0", "study_id": "synthetic-e16", "authority_sha256": "a"*64,
            "policy": {"maximum_rounds": 5, "consecutive_misses": 3, "maximum_batch_size": 2,
                       "initial_claims": 140, "cumulative_cap": 585, "strict_gain_epsilon": 1e-12},
            "families": {f: {"reference_id": "reference", "reference_score": None if f in OPEN_FAMILIES else .5,
                              "source_tree_sha256": digest(f), "profile": {"plan": {"x": 0}, "search": {}},
                              "claims": claim, "cap": cap, "seen_profile_digests": [],
                              "catalog": [{"id": "synthetic", "rationale": "Exercise finite misses.",
                                           "variants": [{"x": x} for x in (0, 1, 2, 3, 4)]}] if f in OPEN_FAMILIES else []}
                         for f, cap, claim in zip(FAMILIES, caps, claims)}}


class SyntheticAdapter:
    def __init__(self, plan):
        self.plan, self.calls, self.final_calls = plan, [], []
        self.gain = False
        self.failure = False

    def verify_admission(self, phase):
        self.final_calls.append("admit:" + phase)

    def execute_development(self, request):
        self.calls.append(request)
        if request["operation"] == "measure":
            value = .6 if self.gain and request["phase"] == "mutation" else .5
            scores = {request["family"]: value}
            checksum = self.plan["families"][request["family"]]["source_tree_sha256"] if request["phase"] == "qualification" else digest(request)
        else:
            key = "reference_score" if request["phase"] == "joint-reference" else "selected_score"
            scores = {f: row[key] for f, row in request["families"].items()}
            changed = self.gain and request["phase"] == "joint-selected"
            checksum = digest("selected" if changed else "baseline")
        return {"request_sha256": digest(request), "candidate_id": request["candidate_id"], "skill_digest": checksum,
                "evaluable": not self.failure, "qualified": not self.failure, "promotion_eligible": True,
                "exploratory": False, "expected_trials": len(scores), "completed_trials": len(scores), "error_count": 0,
                "case_scores": scores, "native_record_sha256": digest([request, "record"]),
                "archive_sha256": digest([request, "archive"]), "archive_member": True}

    def verify_selection(self, selection):
        self.final_calls.append("verify-selection")

    def freeze(self, selection):
        self.final_calls.append("freeze")

    def recalculate(self, selection, arm):
        self.final_calls.append("recalculate:" + arm)
        return {"arm": arm}

    def complete_recalculation(self, selection, records):
        if [r["arm"] for r in records] != ["baseline", "frozen"]:
            raise AssertionError("missing frozen comparison")
        self.final_calls.append("comparison-complete")

    def accept_private(self, selection):
        self.final_calls.append("private-acceptance")
        return {"schema": "enterprise-independent-acceptance/1.0", "accepted": True,
                "decision": "accepted-for-declared-scope", "validation_released": True,
                "selected_tree_sha256": selection["selected_tree_sha256"], "native_promotion_sha256": "b"*64,
                "native_qualified": True, "native_strict_gain_passed": True, "all_family_gates_passed": True}

    def publish(self, selection, outcome):
        self.final_calls.append("publish")
        return {"draft": True}


def drive(planner, adapter, broker=None):
    for _ in range(200):
        batch = planner.next_batch()
        response = broker.execute_batch(batch) if broker else {"batch_sha256": digest(batch), "results": [adapter.execute_development(r) for r in batch["requests"]]}
        selection = planner.accept(response)
        if selection is not None:
            return selection
    raise AssertionError("Unbounded policy")


class PlannerTests(unittest.TestCase):
    def test_public_groups_use_native_rewards_and_declared_weights(self):
        from evaluations.enterprise_isolated_evolution.publication import public_case_groups
        task = {"questions": [{"relevant": ["a"], "weight": 1, "category": "basic"},
                              {"relevant": ["a", "b"], "weight": 3, "category": "multi"},
                              {"relevant": [], "weight": 10, "category": "unanswerable"}],
                "record_identities": {"a": {"source_id": "jira"}, "b": {"source_id": "gmail"}}}
        diagnostics = {"cases": {"route": [{"ndcg_at_10": .25}, {"ndcg_at_10": .75}, {"ndcg_at_10": None}]}}
        result = public_case_groups(task, diagnostics, "route")
        self.assertEqual(.625, result["all:all"]["ndcg_at_10"])
        self.assertEqual(.625, result["application:jira"]["ndcg_at_10"])
        self.assertEqual(.75, result["application:gmail"]["ndcg_at_10"])
        self.assertEqual(2, result["all:all"]["eligible_questions"])
        self.assertIsNone(result["category:unanswerable"]["ndcg_at_10"])
        self.assertEqual(0, result["category:unanswerable"]["eligible_questions"])
        with self.assertRaises(ProtocolError):
            public_case_groups(task, {"cases": {"route": []}}, "route")

    def test_complete_catalog_three_misses_and_joint_replay(self):
        plan = example_plan()
        adapter = SyntheticAdapter(plan)
        planner = Planner(plan)
        selection = drive(planner, adapter)
        self.assertTrue(selection["unchanged"])
        self.assertEqual(10, len(adapter.calls))  # 2 references, 6 mutations, 2 joint arms.
        for family in OPEN_FAMILIES:
            row = selection["families"][family]
            self.assertEqual(row["claims"], plan["families"][family]["claims"] + 3)
            self.assertTrue(any(e.get("reason") == "three-misses" for e in row["events"]))
            self.assertEqual(row["stop_reason"], "full-round-without-improvement")
        with self.assertRaises(ProtocolError):
            planner.next_batch()

    def test_gain_resets_misses_and_requires_another_complete_round(self):
        plan = example_plan()
        adapter = SyntheticAdapter(plan)
        adapter.gain = True
        selection = drive(Planner(plan), adapter)
        self.assertFalse(selection["unchanged"])
        for f in OPEN_FAMILIES:
            row = selection["families"][f]
            self.assertEqual(.6, row["selected_score"])
            self.assertEqual("variant-001", row["selected_id"])
            rounds = [e for e in row["events"] if e["event"] == "round-finished"]
            self.assertEqual([True, False], [r["improved"] for r in rounds])
            self.assertEqual(4, row["claims"] - plan["families"][f]["claims"])

    def test_outer_round_and_family_caps_are_real_stops(self):
        source = example_plan()["families"]["entity-graph"]
        source["catalog"] = [{"id": "a", "rationale": "a", "variants": [{"x": x} for x in (1, 2)]},
                             {"id": "b", "rationale": "b", "variants": [{"y": y} for y in range(1, 12)]}]
        state = FamilySearch("entity-graph", source)
        state.qualify({"skill_digest": source["source_tree_sha256"], "archive_member": True, "case_scores": {"entity-graph": .01}})
        while request := state.next_mutation():
            state.observe(request, {"case_scores": {"entity-graph": state.best_score + .001}, "archive_member": True, "skill_digest": digest(request)})
        self.assertIn(state.stop_reason, {"outer-round-budget-exhausted", "full-round-without-improvement"})
        state = FamilySearch("entity-graph", source)
        state.reference_score = state.best_score = state.round_start_score = .4
        state.claims = source["cap"]
        self.assertIsNone(state.next_mutation())
        self.assertEqual("family-proposal-cap", state.stop_reason)

    def test_non_evaluable_result_stops_without_quality_miss_or_later_request(self):
        plan = example_plan()
        planner, adapter = Planner(plan), SyntheticAdapter(plan)
        batch = planner.next_batch()
        results = [adapter.execute_development(r) for r in batch["requests"]]
        results[1]["qualified"] = False
        with self.assertRaises(ProtocolError):
            planner.accept({"batch_sha256": digest(batch), "results": results})
        self.assertEqual("stopped", planner.phase)
        self.assertEqual([], planner.families["entity-graph"].events)
        self.assertEqual(0, planner.families["entity-graph"].misses)
        with self.assertRaises(ProtocolError):
            planner.next_batch()

    def test_joint_must_reproduce_every_family(self):
        plan, planner = example_plan(), Planner(example_plan())
        adapter = SyntheticAdapter(plan)
        while True:
            batch = planner.next_batch()
            results = [adapter.execute_development(r) for r in batch["requests"]]
            if batch["requests"][0]["phase"] == "joint-reference":
                results[0]["case_scores"]["legacy"] += .01
                with self.assertRaises(ProtocolError):
                    planner.accept({"batch_sha256": digest(batch), "results": results})
                break
            planner.accept({"batch_sha256": digest(batch), "results": results})

    def test_input_identity_and_closed_family_rules(self):
        for modify in (lambda p: p["policy"].update(consecutive_misses=4),
                       lambda p: p["families"]["legacy"].update(reference_score=float("nan")),
                       lambda p: p["families"]["ensemble"].update(reference_id="../escape"),
                       lambda p: p["families"]["legacy"].update(catalog=[{}]),
                       lambda p: p["families"]["ensemble"].update(claims=4)):
            plan = example_plan()
            modify(plan)
            with self.assertRaises(ProtocolError):
                validate_plan(plan)
        for payload in ('{"x":1,"x":2}', '{"x":NaN}'):
            with self.assertRaises(ProtocolError):
                parse_json(payload)


class AuthorityTests(unittest.TestCase):
    def setUp(self):
        (REPO / "tmp").mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=REPO / "tmp", prefix="e16-unit-")
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def test_exclusive_lease_and_consumed_identity_survive_close(self):
        path = self.root / "authority.lock"
        with ExclusiveAuthority(path, root=REPO) as owner:
            script = "from pathlib import Path; from evaluations.enterprise_isolated_evolution.authority import ExclusiveAuthority; " \
                     "from evaluations.enterprise_isolated_evolution.files import REPO; " \
                     "ExclusiveAuthority(Path(__import__('sys').argv[1]),root=REPO).__enter__()"
            result = subprocess.run([sys.executable, "-B", "-c", script, str(path)], cwd=REPO, capture_output=True)
            self.assertNotEqual(0, result.returncode)
            journal = Journal(self.root / "journal.jsonl", owner, root=REPO)
            request = {"phase": "qualification", "family": "ensemble", "candidate_id": "reference"}
            journal.consume(request)
            with self.assertRaises(ProtocolError):
                journal.consume(request)
            journal.close()
        with ExclusiveAuthority(path, root=REPO) as owner:
            with self.assertRaises(FileExistsError):
                Journal(self.root / "journal.jsonl", owner, root=REPO)

    def test_finalize_is_one_way_and_changed_selection_cannot_be_injected(self):
        for changed in (False, True):
            with self.subTest(changed=changed), ExclusiveAuthority(self.root / (str(changed)+".lock"), root=REPO) as owner:
                journal = Journal(self.root / (str(changed)+".jsonl"), owner, root=REPO)
                plan = example_plan()
                adapter = SyntheticAdapter(plan)
                adapter.gain = changed
                broker = Broker(plan, journal, adapter)
                selected = drive(Planner(plan), adapter, broker)
                with self.assertRaises(ProtocolError):
                    broker.finalize(selected)
                broker.optimizer_exited(0, selected)
                result = broker.finalize(selected)
                self.assertEqual(changed, result["validation_released"])
                if changed:
                    self.assertGreater(adapter.final_calls.index("private-acceptance"), adapter.final_calls.index("comparison-complete"))
                with self.assertRaises(ProtocolError):
                    broker.finalize(selected)
                journal.close()
                verify_journal(self.root / (str(changed)+".jsonl"))
        with ExclusiveAuthority(self.root / "tamper.lock", root=REPO) as owner:
            journal = Journal(self.root / "tamper.jsonl", owner, root=REPO)
            plan, adapter = example_plan(), SyntheticAdapter(example_plan())
            broker = Broker(plan, journal, adapter)
            selected = drive(Planner(plan), adapter, broker)
            broker.optimizer_exited(0, selected)
            selected["selected_tree_sha256"] = "f"*64
            with self.assertRaises(ProtocolError):
                broker.finalize(selected)
            self.assertNotIn("freeze", adapter.final_calls)
            journal.close()

    def test_invalid_batch_and_paths_fail_before_any_dispatch(self):
        with ExclusiveAuthority(self.root / "guard.lock", root=REPO) as owner:
            journal = Journal(self.root / "guard.jsonl", owner, root=REPO)
            plan, adapter = example_plan(), SyntheticAdapter(example_plan())
            broker = Broker(plan, journal, adapter)
            batch = Planner(plan).next_batch()
            batch["requests"][0]["command"] = "arbitrary"
            with self.assertRaises(ProtocolError):
                broker.execute_batch(batch)
            self.assertEqual([], adapter.calls)
            journal.close()
        with self.assertRaises(ProtocolError):
            safe_path(REPO.parent / "outside.txt", REPO)
        with self.assertRaises(ProtocolError):
            safe_path(self.root / ".." / ".." / ".." / ".." / "outside", REPO)

    def test_admitted_batch_drains_on_qualification_failure(self):
        plan = example_plan()
        barrier = threading.Barrier(2)
        class FailingAdapter(SyntheticAdapter):
            def execute_development(self, request):
                result = super().execute_development(request)
                barrier.wait(timeout=5)
                if request["family"] == "entity-graph":
                    result["qualified"] = False
                return result
        adapter = FailingAdapter(plan)
        with ExclusiveAuthority(self.root / "drain.lock", root=REPO) as owner:
            journal = Journal(self.root / "drain.jsonl", owner, root=REPO)
            broker = Broker(plan, journal, adapter)
            batch = Planner(plan).next_batch()
            with self.assertRaises(ProtocolError):
                broker.execute_batch(batch)
            self.assertEqual(2, len(adapter.calls))
            self.assertTrue(broker.stop.is_set())
            self.assertTrue(journal.terminal)
            self.assertEqual(2, len(journal.consumed))
            with self.assertRaises(ProtocolError):
                broker.execute_batch(batch)
            self.assertEqual(2, len(adapter.calls))
            journal.close()

    def test_private_extra_field_never_reaches_publication(self):
        plan, adapter = example_plan(), SyntheticAdapter(example_plan())
        adapter.gain = True
        original = adapter.accept_private
        adapter.accept_private = lambda selection: dict(original(selection), private_diagnostic="must not publish")
        with ExclusiveAuthority(self.root / "private.lock", root=REPO) as owner:
            journal = Journal(self.root / "private.jsonl", owner, root=REPO)
            broker = Broker(plan, journal, adapter)
            selected = drive(Planner(plan), adapter, broker)
            broker.optimizer_exited(0, selected)
            with self.assertRaises(ProtocolError):
                broker.finalize(selected)
            self.assertNotIn("publish", adapter.final_calls)
            journal.close()
            self.assertNotIn("must not publish", (self.root / "private.jsonl").read_text())

    def test_failed_all500_original_is_preserved_before_next_allocation(self):
        from evaluations.enterprise_isolated_evolution.native_worker import run
        from evaluations.enterprise_isolated_evolution.files import sha
        source, config, output = self.root / "owner.py", self.root / "config.json", self.root / "native"
        source.write_text("# synthetic owner fixture\n")
        config.write_text(json.dumps({"search": {"baselineCandidate": "baseline"},
                                      "candidates": [{"id": "baseline", "skill": "synthetic"}]}))
        output.mkdir()
        record = {"candidateId": "baseline", "evaluatedSkill": "synthetic-staged", "jobDirectory": "synthetic-job",
                  "qualification": {"passed": False}, "evaluable": True, "promotionEligibleProvenance": True,
                  "exploratory": False, "summary": {"errorCount": 1, "expectedTrials": 8, "completedTrials": 8}, "cases": [{}]*8}
        owner = Mock()
        owner.normalize_config.return_value = {"developmentJob": "synthetic-template"}
        owner.load_job_template.return_value.model_dump.return_value = {
            "n_attempts": 1, "retry": {"max_retries": 0}, "n_concurrent_trials": 2, "tasks": [{}]*8, "agents": [{}]}
        owner.run_candidate_jobs.return_value = [record]
        request = {"operation": "recalculation", "owner": str(source), "owner_sha256": sha(source),
                   "runtime_contract": str(config), "runtime_contract_sha256": sha(config),
                   "config": str(config), "candidate_id": "baseline", "output": str(output),
                   "task_families": {f"synthetic-{i}": f for i, f in enumerate(FAMILIES)},
                   "reporter": "unused", "reporter_sha256": "a"*64}
        with patch("evaluations.enterprise_isolated_evolution.native_worker.load", return_value=owner), \
                patch("evaluations.enterprise_isolated_evolution.native_worker.install"):
            with self.assertRaises(ProtocolError):
                run(request)
        self.assertEqual(record, json.loads((output / "record.json").read_text()))
        owner.development.assert_not_called()
        self.assertEqual(1, owner.run_candidate_jobs.call_count)


class ExecutorPolicyTests(unittest.TestCase):
    def fixture(self):
        class Trial:
            def __init__(self):
                self.task = SimpleNamespace(config=SimpleNamespace(
                    verifier=SimpleNamespace(environment_mode="separate"), steps=None))
                self.agent_env_paths = SimpleNamespace(verifier_dir=PurePosixPath("/logs/verifier"))
                self.paths = SimpleNamespace(verifier_dir=REPO / "tmp/synthetic-feedback")
                self.extra = []

            @property
            def _agent_env_mounts(self):
                return [{"type": "bind", "source": self.paths.verifier_dir.resolve().as_posix(), "target": "/logs/verifier"},
                        {"type": "bind", "source": "synthetic-artifacts", "target": "/logs/artifacts"}] + self.extra

            def _verifier_env_mounts(self, config):
                return [{"type": "bind", "source": self.paths.verifier_dir.resolve().as_posix(), "target": "/logs/verifier"}]

        return Trial, Trial()

    def test_feedback_never_shares_results_but_verifier_and_artifacts_keep_original_mounts(self):
        from evaluations.enterprise_isolated_evolution.executor_policy import _install_trial
        trial_class, trial = self.fixture()
        verifier = trial._verifier_env_mounts(None)
        before = trial._agent_env_mounts
        _install_trial(trial_class, dict, ("a"*64, "b"*64))
        self.assertEqual({"type": "tmpfs", "target": "/logs/verifier"}, trial._agent_env_mounts[0])
        self.assertEqual(before[1:], trial._agent_env_mounts[1:])
        self.assertEqual(verifier, trial._verifier_env_mounts(None))
        _install_trial(trial_class, dict, ("a"*64, "b"*64))
        with self.assertRaises(ProtocolError):
            _install_trial(trial_class, dict, ("c"*64, "b"*64))
        trial_class._agent_env_mounts = property(lambda self: before)
        with self.assertRaises(ProtocolError):
            _install_trial(trial_class, dict, ("a"*64, "b"*64))

    def test_combined_verification_steps_and_duplicate_feedback_fail_closed(self):
        from evaluations.enterprise_isolated_evolution.executor_policy import _install_trial
        for mode, steps, extra in (("same", None, []), ("separate", ["synthetic-step"], []),
                                   ("separate", None, [{"type": "tmpfs", "target": "/logs/verifier"}])):
            with self.subTest(mode=mode, steps=steps, extra=extra):
                trial_class, trial = self.fixture()
                trial.task.config.verifier.environment_mode = mode
                trial.task.config.steps, trial.extra = steps, extra
                _install_trial(trial_class, dict, ("a"*64, "b"*64))
                with self.assertRaises(ProtocolError):
                    _ = trial._agent_env_mounts

    def test_large_workspace_uses_private_disk_and_verifier_artifacts_have_no_duplicate_mount(self):
        from evaluations.enterprise_isolated_evolution.executor_policy import compose_policy
        for verifier in (False, True):
            main = compose_policy(verifier=verifier)["services"]["main"]
            self.assertEqual({"type": "volume", "target": "/workspace", "volume": {"nocopy": True}}, main["volumes"][0])
            self.assertFalse(any(p.startswith("/workspace:") for p in main["tmpfs"]))
            self.assertEqual(verifier, any(p.startswith("/logs/artifacts:") for p in main["tmpfs"]))
            self.assertTrue(main["read_only"])
            self.assertEqual(["ALL"], main["cap_drop"])


if __name__ == "__main__":
    unittest.main()
