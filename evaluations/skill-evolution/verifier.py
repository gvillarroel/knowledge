"""Verifier-side scoring of locked queries; never installed with the agent."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import re
import statistics
import sys
from pathlib import Path, PurePosixPath


def strict_json(text):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("Duplicate JSON member")
            result[key] = value
        return result
    def nonfinite(value):
        raise ValueError("Non-finite JSON number")
    return json.loads(text, object_pairs_hook=pairs, parse_constant=nonfinite)


def nonnegative(value):
    if type(value) not in (int, float) or value < 0 or value > 1e12 or not math.isfinite(value):
        raise ValueError("Invalid resource measurement")
    return value


def file_map(value, *, empty=False):
    if not isinstance(value, dict) or (not value and not empty):
        raise ValueError("Missing file attestation")
    for name, digest in value.items():
        path = PurePosixPath(name)
        if path.is_absolute() or ".." in path.parts or "\\" in name or ":" in name or path.as_posix() != name:
            raise ValueError("Invalid attested path")
        if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise ValueError("Invalid file digest")
    return value


def evaluate(answer, contract, evaluator):
    if not isinstance(answer, dict) or answer.get("schema_version") != "skill-retrieval-trial/1.0":
        raise ValueError("Invalid answer schema")
    if answer.get("family") != contract["family"] or answer.get("builds_byte_identical") is not True:
        raise ValueError("Family or deterministic build contract failed")
    nonnegative(answer["build_seconds"])
    if type(answer["knowledge_bytes"]) is not int or answer["knowledge_bytes"] <= 0:
        raise ValueError("Invalid storage measurement")
    if type(answer["llm_calls"]) is not int or answer["llm_calls"] != 0 or answer["answer_quality_evaluated"] is not False:
        raise ValueError("Execution scope drift")
    submitted = file_map(answer["skill_files"])
    expected = contract["skill_files"]
    mutable = set(contract.get("mutable_skill_paths", []))
    if not set(expected).issubset(submitted) or set(submitted) - set(expected) - mutable:
        raise ValueError("Candidate file membership drift")
    if any(submitted[key] != value for key, value in expected.items() if key not in mutable):
        raise ValueError("Frozen candidate file drift")
    imported = file_map(answer["imported_candidate_modules"], empty=True)
    if imported != contract["imported_candidate_modules"] or any(submitted.get(key) != value for key, value in imported.items()):
        raise ValueError("Imported candidate binding drift")
    file_map(answer["knowledge_files"])
    records = answer["record_identities"]
    if records != contract["record_identities"]:
        raise ValueError("Authoritative evidence identity drift")
    for record_id, record in records.items():
        if record.get("record_sha256") != contract["records"][record_id]:
            raise ValueError("Authoritative record hash drift")
    if not isinstance(answer["routes"], dict) or set(answer["routes"]) != set(contract["routes"]):
        raise ValueError("Missing or unexpected retrieval route")
    questions = contract["questions"]
    if answer["primary_route"] != contract["primary_route"]:
        raise ValueError("Primary route drift")
    aggregates, cases = {}, {}
    for mode, result in answer["routes"].items():
        if not isinstance(result, dict) or not isinstance(result.get("queries"), list) or any(not isinstance(row, dict) for row in result["queries"]):
            raise ValueError("Invalid route response shape")
        p95 = result["p95_ms"]
        nonnegative(p95)
        rows = result["queries"]
        if [row["id"] for row in rows] != [q["id"] for q in questions]:
            raise ValueError("Query membership or order drift")
        vector = []
        for row, question in zip(rows, questions):
            nonnegative(row["milliseconds"])
            hits = row["hits"]
            if not isinstance(hits, list) or any(not isinstance(hit, dict) for hit in hits):
                raise ValueError("Invalid hit response shape")
            if len(hits) > 10 or len({h["record_id"] for h in hits}) != len(hits):
                raise ValueError("Duplicate hits or cutoff drift")
            for rank, hit in enumerate(hits, 1):
                record = contract["record_identities"].get(hit.get("record_id"))
                if record is None or type(hit.get("rank")) is not int or hit["rank"] != rank:
                    raise ValueError("Unknown record or invalid rank")
                if any(hit.get(key) != record.get(key) for key in ("record_sha256", "concept_id", "concept_path", "source_id")):
                    raise ValueError("Invalid evidence identity")
            vector.append(evaluator.metrics(hits, question["relevant"]))
        measured_p95 = sorted(row["milliseconds"] for row in rows)[max(0, math.ceil(len(rows) * .95) - 1)]
        if not math.isclose(p95, measured_p95, rel_tol=1e-12, abs_tol=1e-9):
            raise ValueError("Latency aggregate does not match query measurements")
        aggregates[mode] = {key: statistics.fmean(row[key] for row in vector) for key in vector[0]}
        aggregates[mode]["p95_ms"] = result["p95_ms"]
        cases[mode] = vector
    primary = aggregates[contract["primary_route"]]
    return {
        "reward": primary["ndcg_at_10"], "evidence_integrity": 1.0,
        "recall_at_10": primary["recall_at_10"], "mrr_at_10": primary["mrr_at_10"],
        "full_qrel_coverage_at_10": primary["full_qrel_coverage_at_10"],
    }, {"status": "pass", "routes": aggregates, "cases": cases,
        "question_count": len(questions), "build_seconds": answer["build_seconds"],
        "knowledge_bytes": answer["knowledge_bytes"],
        "skill_files": answer["skill_files"], "imported_candidate_modules": answer["imported_candidate_modules"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tests", type=Path, default=Path("/tests"))
    parser.add_argument("--logs", type=Path, default=Path("/logs/verifier"))
    parser.add_argument("--scoring", type=Path)
    args = parser.parse_args()
    args.logs.mkdir(parents=True, exist_ok=True)
    spec = importlib.util.spec_from_file_location("locked_scoring", args.scoring or args.tests / "evaluate_all_routes.py")
    evaluator = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = evaluator
    spec.loader.exec_module(evaluator)
    contract = strict_json((args.tests / "contract.json").read_text(encoding="utf-8"))
    try:
        answer = strict_json(Path(contract["verifier_output_path"]).read_text(encoding="utf-8"))
        rewards, diagnostics = evaluate(answer, contract, evaluator)
    except (KeyError, ValueError, TypeError, OSError, ZeroDivisionError) as exc:
        rewards = {"reward": 0.0, "evidence_integrity": 0.0}
        diagnostics = {"status": "failed", "error_type": type(exc).__name__, "message": str(exc)}
    (args.logs / "reward.json").write_text(json.dumps(rewards, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    (args.logs / "diagnostics.json").write_text(json.dumps(diagnostics, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
