#!/usr/bin/env python3
"""Generate paired Skill Arena configs for the ten hard Semantic OKF questions."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import yaml


SCHEMA_VERSION = "semantic-okf-hard-answer-configs/1.0"
RUN_ID = "20260714-classical-final-01"

METHODS = {
    "legacy": {
        "benchmark_id": "semantic-okf-legacy-hard10-paired",
        "bundle_kind": "authoritative-core-only",
        "skill_id": "consult-semantic-okf",
        "skill_path": "skills/consult-semantic-okf",
    },
    "embedding": {
        "benchmark_id": "semantic-okf-embedding-hard10-paired",
        "bundle_kind": "embedding-derived",
        "skill_id": "consult-semantic-okf-embeddings",
        "skill_path": "skills/consult-semantic-okf-embeddings",
    },
    "classical": {
        "benchmark_id": "semantic-okf-classical-hard10-paired",
        "bundle_kind": "classical-text-derived",
        "skill_id": "consult-semantic-okf-classical",
        "skill_path": "skills/consult-semantic-okf-classical",
    },
}

CASE_METADATA = {
    "q031-graph-routing-boundary": ("boundary-recovery", "retrieval-routing"),
    "q032-incremental-update-maturity": ("generalization", "knowledge-lifecycle"),
    "q033-corruption-specific-defenses": ("boundary-recovery", "robustness-defense"),
    "q034-nonmonotonic-context-budget": ("generalization", "context-budgeting"),
    "q035-lossless-enough-evidence-organization": ("naturalistic-forward", "evidence-organization"),
    "q036-evaluation-leakage-and-stage-separation": ("naturalistic-forward", "evaluation-design"),
    "q037-domain-construction-under-constraints": ("generalization", "graph-construction"),
    "q038-failure-aware-query-router": ("boundary-recovery", "retrieval-routing"),
    "q039-baseline-bound-efficiency-claims": ("naturalistic-forward", "efficiency-comparison"),
    "q040-answer-source-control": ("boundary-recovery", "answer-grounding-policy"),
}


class LiteralString(str):
    """A YAML scalar that should be represented with literal block style."""


class Dumper(yaml.SafeDumper):
    def increase_indent(self, flow: bool = False, indentless: bool = False) -> Any:
        """Indent sequence items so the config-author static parser can audit them."""

        return super().increase_indent(flow, False)


def _represent_literal(dumper: Dumper, value: LiteralString) -> yaml.ScalarNode:
    return dumper.represent_scalar("tag:yaml.org,2002:str", value, style="|")


Dumper.add_representer(LiteralString, _represent_literal)


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"{path}:{line_number}: expected an object")
        rows.append(value)
    return rows


def _load_claim_records(bundle: Path) -> dict[str, dict[str, Any]]:
    records = _load_jsonl(bundle / "semantic" / "records.jsonl")
    claims: dict[str, dict[str, Any]] = {}
    for record in records:
        record_id = record.get("record_id")
        if isinstance(record_id, str) and record_id.startswith("claim-"):
            claims[record_id] = record
    return claims


def _claim_contract(question: dict[str, Any], records: dict[str, dict[str, Any]]) -> dict[str, Any]:
    evidence = question["authoritative_evidence"]
    claim_ids = sorted({item["claim_id"] for item in evidence})
    allowed: dict[str, dict[str, Any]] = {}
    for item in evidence:
        claim_id = item["claim_id"]
        record = records.get(claim_id)
        if record is None:
            raise ValueError(f"No Semantic OKF record for {claim_id}")
        locator = record.get("attributes", {}).get("evidence_locator")
        locators = []
        if isinstance(locator, str):
            locators = sorted(
                part.rsplit("#", 1)[-1]
                for part in locator.split(";")
                if "#" in part
            )
        allowed[claim_id] = {
            "concept_path": record["concept_path"],
            "paper_id": item["paper_id"],
            "source_path": record["source_path"],
            "locators": locators,
        }
    atom_sets = [
        sorted(set(item["evidence_claim_ids"]))
        for item in question["ground_truth"]["answer_claims"]
    ]
    negative_sets = [
        sorted(set(item["evidence_claim_ids"]))
        for item in question["ground_truth"]["important_negatives"]
    ]
    return {
        "allowed": allowed,
        "atom_sets": atom_sets,
        "claim_ids": claim_ids,
        "negative_sets": negative_sets,
        "required_papers": question["ground_truth"]["required_paper_ids"],
    }


def _prompt(question: dict[str, Any]) -> str:
    question_id = question["id"]
    return (
        "Answer the following research-synthesis question using only the published Semantic OKF "
        "snapshot available at `knowledge/`. Do not use the web, model memory, or guesses. If the "
        "snapshot cannot support an answer, return `answer: null` and an empty `evidence` array.\n"
        f"Question: {question['question']}\n"
        "Return JSON only with top-level keys `question_id`, `answer`, and `evidence`, in that order. "
        f"Set `question_id` to `{question_id}`. A non-null `answer` must contain `summary`, `claims`, "
        "`paper_ids`, and `citations`, in that order. Write a comparative 180-320 word `summary`. "
        "Each `claims` item must have exactly `statement` and `supporting_claim_ids`; use the exact "
        "authoritative claim record IDs that support the statement. Use sorted, unique versioned arXiv "
        "IDs in `paper_ids`. Sort `citations` by `paper_id`; each item must have exactly `paper_id` and "
        "sorted unique integer PDF `pages`. Sort `evidence` by `claim_id`; each item must have exactly "
        "`claim_id`, `concept_path`, `paper_id`, `source_path`, and sorted unique page `locators`. Every "
        "path must exist in the snapshot, and every conclusion must be traceable to the listed evidence."
    )


def _response_contract_js(question_id: str) -> str:
    expected_id = json.dumps(question_id)
    return f"""try {{
  const actual = JSON.parse(output.trim());
  if (JSON.stringify(Object.keys(actual)) !== JSON.stringify(['question_id','answer','evidence'])) return false;
  if (actual.question_id !== {expected_id} || !Array.isArray(actual.evidence)) return false;
  if (actual.answer === null) return actual.evidence.length === 0;
  if (JSON.stringify(Object.keys(actual.answer)) !== JSON.stringify(['summary','claims','paper_ids','citations'])) return false;
  const words = typeof actual.answer.summary === 'string' ? actual.answer.summary.trim().split(/\\s+/).filter(Boolean).length : 0;
  if (words < 180 || words > 320 || !Array.isArray(actual.answer.claims) || actual.answer.claims.length === 0) return false;
  if (!Array.isArray(actual.answer.paper_ids) || !Array.isArray(actual.answer.citations) || actual.evidence.length === 0) return false;
  const sortedUnique = (items) => new Set(items).size === items.length && JSON.stringify([...items].sort()) === JSON.stringify(items);
  if (!actual.answer.paper_ids.every((item) => typeof item === 'string') || !sortedUnique(actual.answer.paper_ids)) return false;
  for (const claim of actual.answer.claims) {{
    if (JSON.stringify(Object.keys(claim)) !== JSON.stringify(['statement','supporting_claim_ids'])) return false;
    if (typeof claim.statement !== 'string' || !claim.statement.trim() || !Array.isArray(claim.supporting_claim_ids) || !sortedUnique(claim.supporting_claim_ids)) return false;
  }}
  const cited = actual.answer.citations.map((item) => item.paper_id);
  if (!sortedUnique(cited)) return false;
  for (const item of actual.answer.citations) {{
    if (JSON.stringify(Object.keys(item)) !== JSON.stringify(['paper_id','pages'])) return false;
    if (!actual.answer.paper_ids.includes(item.paper_id) || !Array.isArray(item.pages) || item.pages.length === 0) return false;
    if (new Set(item.pages).size !== item.pages.length || JSON.stringify([...item.pages].sort((a,b) => a-b)) !== JSON.stringify(item.pages)) return false;
    if (!item.pages.every((page) => Number.isInteger(page) && page > 0)) return false;
  }}
  const evidenceIds = actual.evidence.map((item) => item.claim_id);
  if (!sortedUnique(evidenceIds)) return false;
  return actual.evidence.every((item) =>
    JSON.stringify(Object.keys(item)) === JSON.stringify(['claim_id','concept_path','paper_id','source_path','locators']) &&
    typeof item.claim_id === 'string' && typeof item.concept_path === 'string' && typeof item.paper_id === 'string' &&
    typeof item.source_path === 'string' && Array.isArray(item.locators) && sortedUnique(item.locators)
  );
}} catch {{ return false; }}"""


def _evidence_validity_js(contract: dict[str, Any]) -> str:
    allowed = json.dumps(contract["allowed"], sort_keys=True, separators=(",", ":"))
    return f"""try {{
  const actual = JSON.parse(output.trim());
  if (actual.answer === null) return false;
  const allowed = {allowed};
  for (const item of actual.evidence) {{
    const expected = allowed[item.claim_id];
    if (!expected) return false;
    if (item.concept_path !== expected.concept_path || item.paper_id !== expected.paper_id || item.source_path !== expected.source_path) return false;
    if (!item.locators.every((locator) => expected.locators.includes(locator))) return false;
  }}
  const citedPages = new Map(actual.answer.citations.map((item) => [item.paper_id, new Set(item.pages.map((page) => `PDF-page-${{page}}`))]));
  return actual.evidence.every((item) => item.locators.every((locator) => citedPages.get(item.paper_id)?.has(locator)));
}} catch {{ return false; }}"""


def _coverage_js(contract: dict[str, Any], *, negative: bool) -> str:
    sets = contract["negative_sets" if negative else "atom_sets"]
    expected_sets = json.dumps(sets, separators=(",", ":"))
    required_papers = json.dumps(contract["required_papers"], separators=(",", ":"))
    paper_check = "" if negative else (
        f"const requiredPapers = {required_papers};\n"
        "  if (!requiredPapers.every((paper) => actual.answer.paper_ids.includes(paper))) return false;\n  "
    )
    return f"""try {{
  const actual = JSON.parse(output.trim());
  if (actual.answer === null) return false;
  {paper_check}const used = new Set(actual.answer.claims.flatMap((item) => item.supporting_claim_ids));
  const evidence = new Set(actual.evidence.map((item) => item.claim_id));
  const expectedSets = {expected_sets};
  return expectedSets.every((options) => options.some((claimId) => used.has(claimId) && evidence.has(claimId)));
}} catch {{ return false; }}"""


def _prompt_entry(question: dict[str, Any], records: dict[str, dict[str, Any]]) -> dict[str, Any]:
    contract = _claim_contract(question, records)
    case_kind, task_family = CASE_METADATA[question["id"]]
    return {
        "id": question["id"],
        "description": f"{case_kind}: {task_family}",
        "prompt": LiteralString(_prompt(question)),
        "evaluation": {
            "assertions": [
                {
                    "type": "javascript",
                    "metric": "response-contract",
                    "value": LiteralString(_response_contract_js(question["id"])),
                },
                {
                    "type": "javascript",
                    "metric": "evidence-validity",
                    "value": LiteralString(_evidence_validity_js(contract)),
                },
                {
                    "type": "javascript",
                    "metric": "atomic-answer-completeness",
                    "value": LiteralString(_coverage_js(contract, negative=False)),
                },
                {
                    "type": "javascript",
                    "metric": "important-negative-coverage",
                    "value": LiteralString(_coverage_js(contract, negative=True)),
                },
            ]
        },
    }


def _config(
    method: str,
    questions: list[dict[str, Any]],
    records: dict[str, dict[str, Any]],
    run_id: str,
) -> dict[str, Any]:
    spec = METHODS[method]
    return {
        "schemaVersion": 1,
        "benchmark": {
            "id": spec["benchmark_id"],
            "description": (
                f"Paired knowledge-only control and {method} consult-skill treatment over the same "
                "pinned Semantic OKF bundle and ten hard synthesis questions."
            ),
            "tags": ["compare", "semantic-okf", "hard-questions", "paired", method],
        },
        "task": {"prompts": [_prompt_entry(question, records) for question in questions]},
        "workspace": {
            "sources": [
                {
                    "id": f"{method}-pinned-workspace",
                    "type": "local-path",
                    "path": f"evaluations/semantic-okf-classical/results/runs/{run_id}/workspaces/{method}",
                    "target": "/",
                }
            ],
            "setup": {
                "initializeGit": True,
                "env": {
                    "HF_HUB_OFFLINE": "1",
                    "PYTHONDONTWRITEBYTECODE": "1",
                    "SEMANTIC_OKF_BUNDLE": "$WORKSPACE/knowledge",
                    "TRANSFORMERS_OFFLINE": "1",
                },
            },
        },
        "evaluation": {
            "assertions": [{"type": "is-json", "metric": "response-format"}],
            "requests": 1,
            "timeoutMs": 600000,
            "tracing": False,
            "maxConcurrency": 2,
            "noCache": True,
        },
        "comparison": {
            "profiles": [
                {
                    "id": "knowledge-only-control",
                    "description": "Isolated control with the pinned bundle and no declared consult skill.",
                    "isolation": {"inheritSystem": False},
                    "capabilities": {},
                    "output": {
                        "tags": ["control", method, "knowledge-on"],
                        "labels": {"capability": "none", "bundle_kind": spec["bundle_kind"]},
                    },
                },
                {
                    "id": f"{method}-consult-treatment",
                    "description": f"Isolated treatment with only the standalone {spec['skill_id']} skill.",
                    "isolation": {"inheritSystem": False},
                    "capabilities": {
                        "skills": [
                            {
                                "source": {
                                    "type": "local-path",
                                    "path": spec["skill_path"],
                                    "skillId": spec["skill_id"],
                                },
                                "install": {"strategy": "workspace-overlay"},
                            }
                        ]
                    },
                    "output": {
                        "tags": ["treatment", method, "knowledge-on"],
                        "labels": {"capability": spec["skill_id"], "bundle_kind": spec["bundle_kind"]},
                    },
                },
            ],
            "variants": [
                {
                    "id": "pi-luna-only",
                    "description": "PI with the same GPT-5.6 Luna route for every isolated answer request.",
                    "agent": {
                        "adapter": "pi",
                        "model": "openai-codex/gpt-5.6-luna",
                        "executionMethod": "command",
                        "commandPath": "bin/pi-luna.ps1",
                        "sandboxMode": "read-only",
                        "approvalPolicy": "never",
                        "webSearchEnabled": False,
                        "networkAccessEnabled": True,
                        "reasoningEffort": "medium",
                        "additionalDirectories": [],
                        "cliEnv": {"PI_MODEL_TIMEOUT_SECONDS": "240"},
                        "config": {},
                    },
                    "output": {
                        "tags": ["pi", "gpt-5.6-luna", "isolated"],
                        "labels": {"variantDisplayName": "PI GPT-5.6 Luna"},
                    },
                }
            ],
        },
    }


def _canonical_sha256(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ground-truth", type=Path, required=True)
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--run-id", default=RUN_ID)
    args = parser.parse_args()

    questions = _load_jsonl(args.ground_truth)
    if len(questions) != 10 or set(CASE_METADATA) != {item.get("id") for item in questions}:
        raise ValueError("Expected the exact ten reviewed hard questions")
    records = _load_claim_records(args.bundle)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    generated = []
    for method in METHODS:
        config = _config(method, questions, records, args.run_id)
        output = args.output_dir / f"{method}-hard10.yaml"
        rendered = yaml.dump(
            config,
            Dumper=Dumper,
            allow_unicode=True,
            sort_keys=False,
            width=120,
        )
        output.write_text(rendered, encoding="utf-8", newline="\n")
        generated.append({"method": method, "path": output.as_posix(), "sha256": hashlib.sha256(rendered.encode()).hexdigest()})

    coverage = {
        "schemaVersion": 1,
        "policy": {
            "minimumPrompts": 10,
            "minimumTaskFamilies": 6,
            # The shared strict JSON/evidence contract is an essential observable
            # requirement of every grounded-answer row, so these limits are wider
            # than the defaults used for unconstrained natural-language prompts.
            "maximumPromptWords": 210,
            "maximumPairwiseJaccard": 0.65,
            "requiredCaseKinds": ["naturalistic-forward", "generalization", "boundary-recovery"],
        },
        "cases": [
            {"promptId": item["id"], "caseKind": CASE_METADATA[item["id"]][0], "taskFamily": CASE_METADATA[item["id"]][1]}
            for item in questions
        ],
    }
    coverage_path = args.output_dir / "prompt-coverage.json"
    coverage_path.write_text(json.dumps(coverage, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")

    manifest = {
        "schema_version": SCHEMA_VERSION,
        "ground_truth_sha256": hashlib.sha256(args.ground_truth.read_bytes()).hexdigest(),
        "ground_truth_canonical_sha256": _canonical_sha256(questions),
        "question_count": len(questions),
        "run_id": args.run_id,
        "configs": generated,
        "coverage_path": coverage_path.as_posix(),
        "coverage_sha256": hashlib.sha256(coverage_path.read_bytes()).hexdigest(),
    }
    manifest_path = args.output_dir / "config-manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
