"""Synthetic-only contract and closure tests; no native jobs or private data."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

REPO = Path(__file__).resolve().parents[1]
ROOT = REPO / "tmp/enterprise-authority-tests"
ROOT.mkdir(parents=True, exist_ok=True)
from evaluations.enterprise_isolated_evolution import curator_authority as a


def fixtures():
    mapping = {f"synthetic-{family}-{i}": family for family in a.FAMILIES for i in range(2)}
    records = []
    for arm in ("baseline", "selected"):
        records.append({"candidateId":arm,"skillDigest": "native-" + arm,"jobDirectory":str(ROOT / "synthetic-jobs" / arm),
          "qualification":{"passed":True,"missingRequiredRewards":0},"evaluable":True,"promotionEligibleProvenance":True,
          "exploratory":False,"summary":{"expectedTrials":16,"completedTrials":16,"errorCount":0},
          "cases":[{"taskName":name,"attempts":1,"evaluable":True,"meanReward":0.5,"errorCount":0} for name in mapping]})
    holdout = {key:True for key in ("evaluable","skillChanged","baselineEvaluable","candidateEvaluable","baselineQualified",
               "candidateQualified","profileMatchesDeclared","baselinePromotionEligibleProvenance","candidatePromotionEligibleProvenance",
               "requiredRewardsComplete","promoted")}
    holdout.update(blocked=False,baselineCandidate="baseline",selectedCandidate="selected",meanGain=0.1,
                   baselineMeanReward=0.5,candidateMeanReward=0.6,
                   perCase=[{"taskName":name,"caseKey":name,"evaluable":True,"baselineMeanReward":0.5,
                             "candidateMeanReward":0.6,"delta":0.1} for name in mapping])
    promotion = {"source":"harbor","strategy":"reflective-pareto-search","holdout":holdout,"selectedSkillDigest":"native-selected",
                 "jobs":{"baseline":records[0]["jobDirectory"],"candidate":records[1]["jobDirectory"]}}
    selection = {"selected_id":"selected","selected_tree_sha256":"a" * 64}
    return promotion, records, mapping, selection


class AuthorityTests(unittest.TestCase):
    def outcome(self, values):
        return a.safe_acceptance(*values, "b" * 64)

    def test_exact_safe_schema_and_conjunction(self):
        result = self.outcome(fixtures())
        self.assertEqual(set(result), {"schema","decision","accepted","validation_released","selected_tree_sha256",
                                      "native_promotion_sha256","native_qualified","native_strict_gain_passed","all_family_gates_passed"})
        self.assertTrue(result["accepted"])
        self.assertEqual(result["decision"], "accepted-for-declared-scope")

    def test_zero_aggregate_fails_even_native_promoted(self):
        values = fixtures()
        values[0]["holdout"].update(meanGain=0,candidateMeanReward=0.5)
        result = self.outcome(values)
        self.assertFalse(result["accepted"])
        self.assertTrue(result["native_qualified"])
        self.assertFalse(result["native_strict_gain_passed"])

    def test_individual_regression_allowed_if_family_mean_nonnegative(self):
        values = fixtures()
        rows = values[0]["holdout"]["perCase"]
        rows[0].update(delta=-0.1,candidateMeanReward=0.4)
        rows[1].update(delta=0.1,candidateMeanReward=0.6)
        self.assertTrue(self.outcome(values)["all_family_gates_passed"])

    def test_family_loss_cannot_be_offset_by_other_family(self):
        values = fixtures()
        rows = values[0]["holdout"]["perCase"]
        rows[0].update(delta=-0.2,candidateMeanReward=0.3)
        result = self.outcome(values)
        self.assertFalse(result["all_family_gates_passed"])
        self.assertFalse(result["accepted"])

    def test_baseline_qualification_mandatory(self):
        values = fixtures()
        values[1][0]["qualification"]["passed"] = False
        self.assertFalse(self.outcome(values)["native_qualified"])

    def test_incomplete_original_cannot_qualify(self):
        values = fixtures()
        values[1][0]["summary"]["completedTrials"] = 15
        self.assertFalse(self.outcome(values)["accepted"])

    def test_identity_drift_rejected(self):
        values = fixtures()
        values[1][1]["skillDigest"] = "wrong"
        with self.assertRaises(a.Refused): self.outcome(values)

    def test_duplicate_case_rejected(self):
        values = fixtures()
        values[0]["holdout"]["perCase"][-1] = values[0]["holdout"]["perCase"][0]
        with self.assertRaises(a.Refused): self.outcome(values)

    def test_unavailable_case_fails_family_gate(self):
        values = fixtures()
        values[0]["holdout"]["perCase"][0].update(evaluable=False,delta=None)
        self.assertFalse(self.outcome(values)["accepted"])

    def test_numeric_boolean_not_a_gain(self):
        values = fixtures()
        values[0]["holdout"]["meanGain"] = True
        self.assertFalse(self.outcome(values)["native_strict_gain_passed"])

    def test_json_duplicate_and_nonfinite_rejected(self):
        with tempfile.TemporaryDirectory(dir=ROOT, prefix="synthetic-json-") as folder:
            path = Path(folder) / "data.json"
            for text in ('{"x":1,"x":2}', '{"x":NaN}'):
                path.write_text(text)
                with self.assertRaises(a.Refused): a.read(path)

    def test_uninstalled_authority_cannot_admit(self):
        result = subprocess.run([sys.executable,"-B",str(Path(a.__file__)),"admit","development",str(ROOT)],capture_output=True,text=True)
        self.assertEqual(result.returncode,1)
        self.assertEqual(result.stdout,"")
        self.assertEqual(result.stderr.strip(),"Independent curator authority refused this operation.")

    def test_exclusive_writes_and_escape_rejected(self):
        with tempfile.TemporaryDirectory(dir=ROOT,prefix="synthetic-write-") as folder:
            folder = Path(folder)
            path = folder / "once.json"
            a.write_new(path,{"synthetic":True},folder)
            with self.assertRaises(FileExistsError): a.write_new(path,{},folder)
            with self.assertRaises(a.Refused): a.write_new(folder.parent / "escaped.json",{},folder)

    def test_realizer_inventory_matches_public_helper(self):
        sys.path.insert(0,str(REPO))
        from evaluations.enterprise_isolated_evolution.files import inventory
        with tempfile.TemporaryDirectory(dir=ROOT,prefix="synthetic-tree-") as folder:
            folder = Path(folder)
            (folder / "empty").mkdir()
            (folder / "synthetic.txt").write_text("synthetic-data\n")
            self.assertEqual(a.tree(folder),inventory(folder)[0])

    def test_metadata_closure_uses_only_ledger_and_study_json(self):
        source = REPO.parent / "skill-arena/skills/harbor-organize-evaluations/scripts/manage_harbor_evaluations.py"
        if not source.exists():
            source = Path("C:/Users/villa/dev/skill-arena/skills/harbor-organize-evaluations/scripts/manage_harbor_evaluations.py")
        organizer = a.load_pinned(source,a.sha(source),"synthetic_metadata_organizer")
        with tempfile.TemporaryDirectory(dir=ROOT,prefix="synthetic-metadata-") as folder:
            folder = Path(folder)
            a.write_new(folder / "study.json",{"studyId":"enterprise-e16","schemaVersion":2},folder)
            seal = {"private_review":"DO-NOT-OPEN","synthetic_only":True}
            definition = {"kind":"evolution","ownerSkill":"harbor-reflective-pareto-search","datasetIds":["dev"],"dependsOn":[]}
            state = {"events":[],"headSha256":"0"*64}
            for kind,payload in (("study_initialized",{"studyId":"enterprise-e16","studySha256":a.sha(folder / "study.json")}),
                                 ("stage_added",dict(definition,stageId="evolve",label="Synthetic")),("design_sealed",seal),
                                 ("stage_transitioned",{"stageId":"evolve","fromStatus":"planned","toStatus":"running","note":""})):
                event = organizer.append_event(folder,state,kind,payload,organizer.timestamp(None))
                state["events"].append(event)
                state["headSha256"] = event["eventSha256"]
            anchor = {"study_id":"enterprise-e16","design_seal_sha256":a.digest(seal),"stage_definitions":{"evolve":definition}}
            original = Path.read_text
            reads = []
            def controlled(path,*args,**kwargs):
                reads.append(path.name)
                self.assertIn(path.name,{"ledger.jsonl","study.json"})
                return original(path,*args,**kwargs)
            with patch.object(Path,"read_text",controlled):
                replay = a.metadata_state(organizer,folder,anchor)
            self.assertEqual(replay["stages"]["evolve"]["status"],"running")
            self.assertEqual(set(reads),{"ledger.jsonl","study.json"})

    def test_public_policy_replay_rejects_early_joint_and_wrong_retention(self):
        sys.path.insert(0,str(REPO))
        test_source = REPO / "tests/test_enterprise_isolated_evolution.py"
        helpers = a.load_pinned(test_source,a.sha(test_source),"e16_public_policy_test_helpers")
        plan = helpers.example_plan()
        optimizer = helpers.Planner(plan)
        adapter = helpers.SyntheticAdapter(plan)
        adapter.gain = True
        events = []
        selection = None
        while selection is None:
            batch = optimizer.next_batch()
            events.append({"kind":"batch-received","payload":batch})
            response = {"batch_sha256":helpers.digest(batch),"results":[adapter.execute_development(row) for row in batch["requests"]]}
            events.append({"kind":"batch-complete","payload":response})
            selection = optimizer.accept(response)
        events.append({"kind":"optimizer-terminated","payload":{"exit_code":0,"selection_sha256":a.digest(selection)}})
        subject = a.Authority.__new__(a.Authority)
        subject.plan = plan
        code = REPO / "evaluations/enterprise_isolated_evolution"
        subject.contract = {"optimizer_code":a.linux(code)}
        subject.anchor = {"planner_source_sha256":a.sha(code / "planner.py")}
        self.assertEqual(subject.replay(events),selection)
        early = copy.deepcopy(events)
        joint = next(row for row in early if row["kind"] == "batch-received" and row["payload"]["requests"][0]["phase"] == "joint-reference")
        early[2] = joint
        with self.assertRaises(a.Refused): subject.replay(early)
        changed = copy.deepcopy(events)
        mutation = next(row for row in changed if row["kind"] == "batch-received" and row["payload"]["requests"][0]["phase"] == "mutation")
        mutation["payload"]["requests"][0]["parent_id"] = "invented-parent"
        with self.assertRaises(a.Refused): subject.replay(changed)

    def test_journal_tampering_and_duplicate_identity_refused(self):
        with tempfile.TemporaryDirectory(dir=ROOT,prefix="synthetic-journal-") as folder:
            path = Path(folder) / "journal.jsonl"
            rows, head = [], "0"*64
            for index in range(2):
                event = {"sequence":index,"previous_sha256":head,"kind":"allocated","payload":{"identity":["synthetic","family","same-id"]}}
                event["sha256"] = head = a.digest(event)
                rows.append(event)
            path.write_text("\n".join(json.dumps(row) for row in rows)+"\n")
            with self.assertRaises(a.Refused): a.journal(path)
            rows = rows[:1]
            rows[0]["payload"]["identity"][2] = "tampered"
            path.write_text(json.dumps(rows[0])+"\n")
            with self.assertRaises(a.Refused): a.journal(path)


if __name__ == "__main__": unittest.main(verbosity=2)
