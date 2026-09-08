"""Curator-only pre-seal audits; print aggregate checks, never private task content."""
from __future__ import annotations

import copy
import hashlib
import json
import re
from collections import defaultdict

from prepare_datasets import load, read_jsonl
from prepare_experiment import HERE, REPO, WORK, TASKS, sha, tree, write_json


def normalized(text):
    return " ".join(re.findall(r"\w+", text.casefold()))


def shingles(text):
    words = normalized(text).split()
    return {" ".join(words[i:i+5]) for i in range(max(1, len(words)-4))}


def reference_artifact(contract, full):
    records = contract["record_identities"]
    routes = {}
    for route in contract["routes"]:
        rows = []
        for question in contract["questions"]:
            selected = sorted(question["relevant"], reverse=full)
            if full:
                selected += sorted(set(records) - set(selected))
            hits = [{**records[key], "rank": rank} for rank, key in enumerate(selected[:10], 1)]
            rows.append({"id": question["id"], "hits": hits, "milliseconds": 1.0})
        routes[route] = {"queries": rows, "p95_ms": 1.0}
    return {"schema_version": "skill-retrieval-trial/1.0", "family": contract["family"], "primary_route": contract["primary_route"],
            "routes": routes, "record_identities": records, "skill_files": contract["skill_files"], "imported_candidate_modules": contract["imported_candidate_modules"],
            "knowledge_files": {"semantic/records.jsonl": "0"*64}, "builds_byte_identical": True, "build_seconds": 1.0,
            "knowledge_bytes": 1, "llm_calls": 0, "answer_quality_evaluated": False}


def audit_verifiers():
    verifier = load("curator_locked_verifier", HERE / "verifier.py")
    evaluator = load("curator_locked_metrics", REPO / "evaluations/private-book-strategy-comparison/scripts/evaluate_all_routes.py")
    checked = []
    for path in sorted(TASKS.glob("*/*/tests/contract.json")):
        contract = json.loads(path.read_text(encoding="utf-8"))
        if not contract["questions"] or len({q["id"] for q in contract["questions"]}) != len(contract["questions"]):
            raise ValueError("Empty or repeated oracle queries")
        if any(not q["relevant"] or not set(q["relevant"]).issubset(contract["records"]) for q in contract["questions"]):
            raise ValueError("Missing relevance identity")
        for full in (False, True):
            answer = reference_artifact(contract, full)
            reward, _ = verifier.evaluate(answer, contract, evaluator)
            repeated, _ = verifier.evaluate(copy.deepcopy(answer), contract, evaluator)
            if reward != repeated or abs(reward["reward"]-1) > 1e-12 or reward["evidence_integrity"] != 1:
                raise ValueError("Valid retrieval equivalence or deterministic oracle failed")
        rejected = 0
        for bad in ({}, None, {**answer, "routes": []}, {**answer, "builds_byte_identical": "false"}, {**answer, "skill_files": {}}):
            try:
                verifier.evaluate(bad, contract, evaluator)
            except (KeyError, TypeError, ValueError):
                rejected += 1
        if rejected != 5:
            raise ValueError("Invalid reference shortcut accepted")
        changed = copy.deepcopy(answer)
        key = next(iter(changed["record_identities"]))
        changed["record_identities"][key]["concept_path"] = "../../outside.md"
        for result in changed["routes"].values():
            for row in result["queries"]:
                for hit in row["hits"]:
                    if hit["record_id"] == key:
                        hit["concept_path"] = "../../outside.md"
        try:
            verifier.evaluate(changed, contract, evaluator)
        except ValueError:
            pass
        else:
            raise ValueError("Coordinated reference-identity mutation accepted")
        checked.append({"contract_sha256": sha(path), "two_valid_answers": True, "deterministic": True, "invalid_shortcuts_rejected": 6})
    if len(checked) != 48:
        raise ValueError("Incomplete native task portfolio")
    return {"status": "pass", "task_count": len(checked), "checks": checked, "scope": "Verifier unit oracles, not candidate fitness or proof of runtime execution; actual synthetic native smoke is separate."}


def audit_overlap():
    groups = {"internal": ["enterprise", "astro", "architecture", "data-science"], "fiqa": ["fiqa"], "scifact": ["scifact"]}
    contents, queries = {}, {}
    for group, cohorts in groups.items():
        contents[group], queries[group] = [], []
        for cohort in cohorts:
            rows = read_jsonl(WORK / f"curator/cores/{cohort}/semantic/records.jsonl")
            contents[group].extend(row["body"] for row in rows)
            split = "development" if group == "internal" else "validation"
            questions = json.loads((WORK / f"curator/{split}/{cohort}-oracle.json").read_text(encoding="utf-8"))["questions"]
            queries[group].extend(row["question"] for row in questions)
    pairs = []
    for left, right in (("internal", "fiqa"), ("internal", "scifact"), ("fiqa", "scifact")):
        exact = len({hashlib.sha256(normalized(x).encode()).hexdigest() for x in contents[left]} & {hashlib.sha256(normalized(x).encode()).hexdigest() for x in contents[right]})
        sets = [shingles(x) for x in contents[left]]
        inverted = defaultdict(set)
        for i, values in enumerate(sets):
            for value in values:
                inverted[value].add(i)
        near = []
        for j, text in enumerate(contents[right]):
            values = shingles(text)
            candidates = set().union(*(inverted.get(value, set()) for value in values))
            for i in candidates:
                other = sets[i]
                if min(len(values), len(other)) / max(1, max(len(values), len(other))) < .8:
                    continue
                score = len(values & other) / max(1, len(values | other))
                if score >= .8:
                    near.append({"left_index": i, "right_index": j, "jaccard": score})
        qnear = sum(len(set(normalized(a).split()) & set(normalized(b).split())) / max(1, len(set(normalized(a).split()) | set(normalized(b).split()))) >= .8 for a in queries[left] for b in queries[right])
        pairs.append({"groups": [left, right], "exact_document_matches": exact, "near_documents": near, "near_queries": qnear})
    return {"status": "needs-review" if any(p["exact_document_matches"] or p["near_documents"] or p["near_queries"] for p in pairs) else "pass", "pairs": pairs,
            "method": "Normalized document SHA-256, five-token-shingle Jaccard >=0.8, query-token Jaccard >=0.8. A screening queue, not a semantic independence proof."}


def main():
    output = WORK / "curator/quality"
    output.mkdir(parents=True, exist_ok=False)
    oracle = audit_verifiers()
    write_json(output / "verifier-quality.json", oracle)
    print(json.dumps({"stage": "verifier-oracle-audit", "status": oracle["status"], "tasks": oracle["task_count"]}), flush=True)
    overlap = audit_overlap()
    write_json(output / "overlap.json", overlap)
    write_json(output / "input-bindings.json", {"tasks": tree(TASKS), "adapter_sha256": sha(HERE / "prepare_datasets.py"), "verifier_sha256": sha(HERE / "verifier.py")})
    print(json.dumps({"stage": "cross-family-overlap", "status": overlap["status"], "group_pairs": 3}), flush=True)


if __name__ == "__main__":
    main()
