#!/usr/bin/env python3
"""Generate one isolated control/treatment Skill Arena diagnostic for five hard questions."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any, Mapping, Sequence

import yaml


REPO = Path(__file__).resolve().parents[3]
EVALUATION = Path(__file__).resolve().parents[1]
PROMPT_IDS = (
    "q026-receptor-to-gestation-boundary",
    "q027-feminine-risk-reconciliation",
    "q028-phthalate-name-normalization",
    "q029-label-gate-validity",
    "q030-causal-evidence-map",
)
DEFAULT_BUNDLE = EVALUATION / "results/runs/20260715-endocrine-builds-05/bundles/classical-a"
DEFAULT_RUNNER = REPO / "evaluations/semantic-okf-builder/fixtures/workspaces/base/bin"
DEFAULT_CONFIG = EVALUATION / "skill-arena/classical-hard4.yaml"
DEFAULT_MANIFEST = EVALUATION / "skill-arena/classical-hard4-manifest.json"
PROMPT_COVERAGE = EVALUATION / "skill-arena/prompt-coverage.json"
HARD_CLAIM_REQUIREMENTS = EVALUATION / "benchmark/hard-claim-requirements.json"
HEX_64_RE = re.compile(r"[0-9a-f]{64}")


class ConfigError(RuntimeError):
    """Describe an invalid frozen input or generated comparison."""


class Literal(str):
    """Render one YAML value as a literal block."""


class Dumper(yaml.SafeDumper):
    def increase_indent(self, flow: bool = False, indentless: bool = False) -> Any:
        return super().increase_indent(flow, False)


def _literal(dumper: Dumper, value: Literal) -> yaml.ScalarNode:
    return dumper.represent_scalar("tag:yaml.org,2002:str", value, style="|")


Dumper.add_representer(Literal, _literal)


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            raise ConfigError(f"blank JSONL row at {path}:{number}")
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ConfigError(f"expected an object at {path}:{number}")
        rows.append(value)
    return rows


def tree_binding(root: Path) -> dict[str, Any]:
    rows: list[bytes] = []
    total = 0
    count = 0
    for path in sorted(root.rglob("*"), key=lambda item: item.relative_to(root).as_posix()):
        relative = path.relative_to(root)
        if "__pycache__" in relative.parts or path.suffix == ".pyc":
            continue
        if path.is_symlink():
            raise ConfigError(f"tree contains a symbolic link: {relative.as_posix()}")
        if not path.is_file():
            continue
        payload = path.read_bytes()
        rows.append(relative.as_posix().encode("utf-8") + b"\0" + sha256_bytes(payload).encode("ascii") + b"\n")
        count += 1
        total += len(payload)
    if not rows:
        raise ConfigError(f"tree is empty: {root}")
    return {"tree_sha256": sha256_bytes(b"".join(rows)), "file_count": count, "bytes": total}


def hard_truth() -> dict[str, dict[str, Any]]:
    rows = load_jsonl(EVALUATION / "benchmark/hard-ground-truth.jsonl")
    result = {row["id"]: row for row in rows if row.get("id") in PROMPT_IDS}
    if set(result) != set(PROMPT_IDS):
        raise ConfigError("the five hard ground-truth records must be unique and complete")
    return result


def hard_questions() -> dict[str, str]:
    rows = load_jsonl(EVALUATION / "benchmark/hard-questions.jsonl")
    result = {row["id"]: row["question"] for row in rows if row.get("id") in PROMPT_IDS}
    if set(result) != set(PROMPT_IDS):
        raise ConfigError("the five hard questions must be unique and complete")
    return result


def source_claim_ledger() -> dict[str, dict[str, str]]:
    """Load the complete reviewed claim ledger directly from the frozen corpus."""

    identity = json.loads((EVALUATION / "corpus/source-combination.json").read_text(encoding="utf-8"))["identity_by_source"]
    ledger: dict[str, dict[str, str]] = {}
    claim_root = EVALUATION / "corpus/sources/claims"
    paths = sorted(claim_root.glob("PMC*.jsonl"), key=lambda path: path.name)
    if not paths:
        raise ConfigError("the frozen corpus contains no reviewed claim sources")
    for path in paths:
        source_id = f"claims-{path.stem.casefold()}"
        paper_id = identity.get(source_id)
        if not isinstance(paper_id, str):
            raise ConfigError(f"claim source has no canonical paper identity: {source_id}")
        for row in load_jsonl(path):
            if row.get("review_state") != "reviewed":
                raise ConfigError(f"claim is not reviewed: {row.get('id')}")
            claim_id = row.get("id")
            if not isinstance(claim_id, str) or not claim_id:
                raise ConfigError(f"claim source has an invalid ID: {path}")
            if claim_id in ledger:
                raise ConfigError(f"duplicate reviewed claim ID in the corpus: {claim_id}")
            item = {
                "paper_id": paper_id,
                "source_path": f"sources/claims/{path.name}",
                "evidence_locator": row.get("evidence_locator"),
                "evidence_text_sha256": row.get("evidence_text_sha256"),
                "interpretation": row.get("interpretation"),
            }
            if not all(isinstance(value, str) and value for value in item.values()):
                raise ConfigError(f"claim {claim_id} has incomplete reviewed fields")
            if not HEX_64_RE.fullmatch(item["evidence_text_sha256"]):
                raise ConfigError(f"claim {claim_id} has an invalid evidence digest")
            ledger[claim_id] = item
    return dict(sorted(ledger.items()))


def ledger_claim_evidence(bundle: Path) -> dict[str, dict[str, str]]:
    """Bind every corpus claim to its exact published concept and evidence row."""

    records = load_jsonl(bundle / "semantic/records.jsonl")
    identity = json.loads((EVALUATION / "corpus/source-combination.json").read_text(encoding="utf-8"))["identity_by_source"]
    expected_ledger = source_claim_ledger()
    ledger: dict[str, dict[str, str]] = {}
    for record in records:
        source_id = record.get("source_id")
        attributes = record.get("attributes")
        if not isinstance(source_id, str) or not source_id.startswith("claims-") or not isinstance(attributes, dict):
            continue
        claim_id = record.get("record_id")
        if not isinstance(claim_id, str) or not claim_id:
            raise ConfigError("published claim record has an invalid ID")
        if claim_id in ledger:
            raise ConfigError(f"duplicate reviewed claim ID in the published ledger: {claim_id}")
        item = {
            "concept_path": record["concept_path"],
            "paper_id": identity[source_id],
            "source_path": record["source_path"],
            "evidence_locator": attributes["evidence_locator"],
            "evidence_text_sha256": attributes["evidence_text_sha256"],
            "interpretation": attributes["interpretation"],
        }
        if not HEX_64_RE.fullmatch(item["evidence_text_sha256"]):
            raise ConfigError(f"claim {claim_id} has an invalid evidence digest")
        ledger[claim_id] = item
    if not ledger:
        raise ConfigError("the frozen ledger contains no reviewed claims")
    if set(ledger) != set(expected_ledger):
        missing = sorted(set(expected_ledger).difference(ledger))
        extra = sorted(set(ledger).difference(expected_ledger))
        raise ConfigError(f"published claim ledger differs from the corpus: missing={missing}, extra={extra}")
    for claim_id, expected in expected_ledger.items():
        actual = ledger[claim_id]
        for key, value in expected.items():
            if actual[key] != value:
                raise ConfigError(f"published claim {claim_id} differs from the corpus field {key}")
    return dict(sorted(ledger.items()))


def hard_claim_requirements(
    truths: Mapping[str, Mapping[str, Any]],
    ledger: Mapping[str, Mapping[str, str]],
) -> dict[str, dict[str, dict[str, list[str]]]]:
    """Validate and index the exact reviewed claims required by each answer atom."""

    raw = json.loads(HARD_CLAIM_REQUIREMENTS.read_text(encoding="utf-8"))
    if set(raw) != {"schema_version", "contract", "questions"}:
        raise ConfigError("hard claim requirements use an unexpected top-level schema")
    rows = raw["questions"]
    if not isinstance(rows, list):
        raise ConfigError("hard claim requirements questions must be an array")
    by_question: dict[str, dict[str, dict[str, list[str]]]] = {}
    for row in rows:
        if not isinstance(row, dict) or set(row) != {"id", "answer_claims", "important_negatives"}:
            raise ConfigError("hard claim requirement rows use an unexpected schema")
        identifier = row["id"]
        if identifier in by_question:
            raise ConfigError(f"duplicate hard claim requirement question: {identifier}")
        if identifier not in truths:
            raise ConfigError(f"unknown hard claim requirement question: {identifier}")
        question_groups: dict[str, dict[str, list[str]]] = {}
        evidence = {item["id"]: item for item in truths[identifier]["authoritative_evidence"]}
        for group_name in ("answer_claims", "important_negatives"):
            groups = row[group_name]
            if not isinstance(groups, list):
                raise ConfigError(f"{identifier} {group_name} must be an array")
            indexed: dict[str, list[str]] = {}
            truth_groups = {item["id"]: item for item in truths[identifier]["ground_truth"][group_name]}
            for group in groups:
                if not isinstance(group, dict) or set(group) != {"id", "required_claim_ids"}:
                    raise ConfigError(f"{identifier} {group_name} group uses an unexpected schema")
                group_id = group["id"]
                claim_ids = group["required_claim_ids"]
                if group_id in indexed or group_id not in truth_groups:
                    raise ConfigError(f"{identifier} has an invalid {group_name} ID: {group_id}")
                if (
                    not isinstance(claim_ids, list)
                    or not claim_ids
                    or any(not isinstance(item, str) or item not in ledger for item in claim_ids)
                    or claim_ids != sorted(set(claim_ids))
                ):
                    raise ConfigError(f"{identifier} {group_id} has invalid exact required claim IDs")
                expected_signatures = {
                    (evidence[evidence_id]["paper_id"], evidence[evidence_id]["text_sha256"])
                    for evidence_id in truth_groups[group_id]["evidence_ids"]
                }
                actual_signatures = {
                    (ledger[claim_id]["paper_id"], ledger[claim_id]["evidence_text_sha256"])
                    for claim_id in claim_ids
                }
                if actual_signatures != expected_signatures:
                    raise ConfigError(f"{identifier} {group_id} exact claims do not bind its authoritative evidence")
                indexed[group_id] = claim_ids
            if set(indexed) != set(truth_groups):
                raise ConfigError(f"{identifier} {group_name} requirements are incomplete")
            question_groups[group_name] = dict(sorted(indexed.items()))
        by_question[identifier] = question_groups
    if set(by_question) != set(PROMPT_IDS):
        raise ConfigError("the five hard claim requirement records must be unique and complete")
    return {identifier: by_question[identifier] for identifier in PROMPT_IDS}


def prompt(
    identifier: str,
    question: str,
    truth: Mapping[str, Any],
    requirements: Mapping[str, Mapping[str, list[str]]],
    ledger_evidence: Mapping[str, Any],
) -> dict[str, Any]:
    required_papers = truth["ground_truth"]["required_paper_ids"]
    atomic_groups = requirements["answer_claims"]
    negative_groups = requirements["important_negatives"]
    evidence_ledger = {
        claim_id: {key: value for key, value in item.items() if key != "interpretation"}
        for claim_id, item in ledger_evidence.items()
    }
    interpretation_ledger = {
        claim_id: item["interpretation"] for claim_id, item in ledger_evidence.items()
    }
    response_contract = """try {
  const actual = JSON.parse(output.trim());
  if (JSON.stringify(Object.keys(actual)) !== JSON.stringify(['question_id','answer','evidence'])) return false;
  if (actual.question_id !== 'q030-causal-evidence-map' || !Array.isArray(actual.evidence)) return false;
  if (actual.answer === null) return actual.evidence.length === 0;
  if (JSON.stringify(Object.keys(actual.answer)) !== JSON.stringify(['summary','claims','paper_ids'])) return false;
  const words = typeof actual.answer.summary === 'string' ? actual.answer.summary.trim().split(/\\s+/).filter(Boolean).length : 0;
  if (words < 180 || words > 360 || !Array.isArray(actual.answer.claims) || !Array.isArray(actual.answer.paper_ids)) return false;
  const sortedUnique = (items) => Array.isArray(items) && new Set(items).size === items.length && JSON.stringify([...items].sort()) === JSON.stringify(items);
  if (!sortedUnique(actual.answer.paper_ids)) return false;
  if (!actual.answer.claims.every((item) => JSON.stringify(Object.keys(item)) === JSON.stringify(['statement','supporting_claim_ids']) && typeof item.statement === 'string' && item.statement.trim() && sortedUnique(item.supporting_claim_ids))) return false;
  return actual.evidence.every((item) => JSON.stringify(Object.keys(item)) === JSON.stringify(['claim_id','concept_path','paper_id','source_path','evidence_locator','evidence_text_sha256']));
} catch { return false; }""".replace("q030-causal-evidence-map", identifier)
    evidence_validity = f"""try {{
  const actual = JSON.parse(output.trim());
  if (actual.answer === null || actual.evidence.length === 0) return false;
  const allowed = {canonical_json(evidence_ledger)};
  const ids = actual.evidence.map((item) => item.claim_id);
  if (new Set(ids).size !== ids.length || JSON.stringify([...ids].sort()) !== JSON.stringify(ids)) return false;
  return actual.evidence.every((item) => {{
    const expected = allowed[item.claim_id];
    return expected && Object.keys(expected).every((key) => item[key] === expected[key]);
  }});
}} catch {{ return false; }}"""
    claim_fidelity = f"""try {{
  const actual = JSON.parse(output.trim());
  if (actual.answer === null || actual.answer.claims.length === 0) return false;
  const interpretations = {canonical_json(interpretation_ledger)};
  const claimIds = [];
  for (const row of actual.answer.claims) {{
    if (row.supporting_claim_ids.length !== 1) return false;
    const claimId = row.supporting_claim_ids[0];
    const expected = interpretations[claimId];
    if (typeof expected !== 'string' || row.statement !== expected) return false;
    claimIds.push(claimId);
  }}
  const evidenceIds = actual.evidence.map((item) => item.claim_id);
  if (new Set(claimIds).size !== claimIds.length) return false;
  if (JSON.stringify([...claimIds].sort()) !== JSON.stringify(claimIds)) return false;
  return JSON.stringify(claimIds) === JSON.stringify(evidenceIds);
}} catch {{ return false; }}"""
    atomic = f"""try {{
  const actual = JSON.parse(output.trim());
  if (actual.answer === null) return false;
  const used = new Set(actual.answer.claims.flatMap((item) => item.supporting_claim_ids));
  const evidence = new Set(actual.evidence.map((item) => item.claim_id));
  const groups = {canonical_json(atomic_groups)};
  return Object.values(groups).every((claimIds) => claimIds.every((id) => used.has(id) && evidence.has(id)));
}} catch {{ return false; }}"""
    negatives = f"""try {{
  const actual = JSON.parse(output.trim());
  if (actual.answer === null) return false;
  const used = new Set(actual.answer.claims.flatMap((item) => item.supporting_claim_ids));
  const evidence = new Set(actual.evidence.map((item) => item.claim_id));
  const groups = {canonical_json(negative_groups)};
  return Object.values(groups).every((claimIds) => claimIds.every((id) => used.has(id) && evidence.has(id)));
}} catch {{ return false; }}"""
    papers = f"""try {{
  const actual = JSON.parse(output.trim());
  if (actual.answer === null) return false;
  const required = {canonical_json(required_papers)};
  const derived = [...new Set(actual.evidence.map((item) => item.paper_id))].sort();
  if (JSON.stringify(actual.answer.paper_ids) !== JSON.stringify(derived)) return false;
  return required.every((paper) => derived.includes(paper));
}} catch {{ return false; }}"""
    instruction = (
        "Answer the following research-synthesis question using only the published Semantic OKF snapshot "
        "available at `knowledge/`. Do not use the web, model memory, or guesses. If the snapshot cannot "
        "support an answer, return `answer: null` and an empty `evidence` array. "
        f"Question: {question} "
        "Return JSON only with top-level keys `question_id`, `answer`, and `evidence`, in that order. "
        f"Set `question_id` to `{identifier}`. A non-null `answer` must contain `summary`, `claims`, and "
        "`paper_ids`, in that order. Write a comparative 180-360 word summary that preserves limitations "
        "and explicitly states what evidence is still missing for causality. Each claim must contain exactly "
        "`statement` and `supporting_claim_ids`, cite exactly one reviewed claim record ID, and copy that record's "
        "reviewed `interpretation` exactly as `statement`. Sort claims by their one claim ID. Set `paper_ids` to "
        "the sorted unique canonical PMCIDs derived from the returned evidence rows. Sort `evidence` by `claim_id`; "
        "every evidence item must contain "
        "exactly `claim_id`, `concept_path`, `paper_id`, `source_path`, `evidence_locator`, and "
        "`evidence_text_sha256`. Every path, locator, and hash must be copied exactly from the snapshot."
    )
    return {
        "id": identifier,
        "description": "hard synthesis: reviewed evidence comparison and causal boundary",
        "prompt": Literal(instruction),
        "evaluation": {
            "assertions": [
                {"type": "javascript", "metric": "response-contract", "value": Literal(response_contract)},
                {"type": "javascript", "metric": "evidence-validity", "value": Literal(evidence_validity)},
                {"type": "javascript", "metric": "claim-fidelity", "value": Literal(claim_fidelity)},
                {"type": "javascript", "metric": "atomic-answer-completeness", "value": Literal(atomic)},
                {"type": "javascript", "metric": "important-negative-coverage", "value": Literal(negatives)},
                {"type": "javascript", "metric": "required-paper-coverage", "value": Literal(papers)},
            ]
        },
    }


def config(bundle: Path, runner: Path, prompt_values: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    return {
        "schemaVersion": 1,
        "benchmark": {
            "id": "semantic-okf-endocrine-hygiene-classical-hard5-paired",
            "description": "An isolated paired diagnostic of a classical consultation skill on five frozen hard questions.",
            "tags": ["compare", "semantic-okf", "endocrine-hygiene", "hard-question", "isolated", "paired", "cli"],
        },
        "task": {"prompts": list(prompt_values)},
        "workspace": {
            "sources": [
                {"id": "classical-bundle", "type": "local-path", "path": bundle.relative_to(REPO).as_posix(), "target": "/knowledge"},
                {"id": "pi-luna-runner", "type": "local-path", "path": runner.relative_to(REPO).as_posix(), "target": "/bin"},
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
        "evaluation": {"assertions": [{"type": "is-json", "metric": "response-format"}], "requests": 1, "timeoutMs": 600000, "tracing": False, "maxConcurrency": 1, "noCache": True},
        "comparison": {
            "profiles": [
                {
                    "id": "knowledge-only-control",
                    "description": "Isolated control with the pinned bundle and no declared consultation skill.",
                    "isolation": {"inheritSystem": False},
                    "capabilities": {},
                    "output": {"tags": ["control", "knowledge-only"], "labels": {"capability": "none", "causal_role": "passive-control"}},
                },
                {
                    "id": "classical-cli-consult-treatment",
                    "description": "Isolated treatment with only the classical CLI consultation skill over the same bundle.",
                    "isolation": {"inheritSystem": False},
                    "capabilities": {
                        "skills": [
                            {
                                "source": {"type": "local-path", "path": "skills/consult-semantic-okf-classical", "skillId": "consult-semantic-okf-classical"},
                                "install": {"strategy": "workspace-overlay"},
                            }
                        ]
                    },
                    "output": {"tags": ["treatment", "classical", "cli"], "labels": {"capability": "consult-semantic-okf-classical", "causal_role": "treatment"}},
                },
            ],
            "variants": [
                {
                    "id": "pi-luna-only",
                    "description": "The same PI GPT-5.6 Luna route for both isolated cells.",
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
                        "cliEnv": {"PI_MODEL_TIMEOUT_SECONDS": "600"},
                        "envPassthrough": ["SEMANTIC_OKF_PYTHON", "SEMANTIC_OKF_HF_HUB_CACHE"],
                        "config": {},
                    },
                    "output": {"tags": ["pi", "gpt-5.6-luna", "isolated", "cli"], "labels": {"variantDisplayName": "PI GPT-5.6 Luna"}},
                }
            ],
        },
    }


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(content, encoding="utf-8", newline="\n")
    os.replace(temporary, path)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, default=DEFAULT_BUNDLE)
    parser.add_argument("--runner", type=Path, default=DEFAULT_RUNNER)
    parser.add_argument("--output", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    args = parser.parse_args(argv)
    bundle, runner = args.bundle.resolve(strict=True), args.runner.resolve(strict=True)
    truths = hard_truth()
    questions = hard_questions()
    ledger_evidence = ledger_claim_evidence(bundle)
    requirements = hard_claim_requirements(truths, ledger_evidence)
    prompt_values: list[dict[str, Any]] = []
    required_claim_count_by_prompt: dict[str, dict[str, int]] = {}
    for identifier in PROMPT_IDS:
        prompt_values.append(
            prompt(
                identifier,
                questions[identifier],
                truths[identifier],
                requirements[identifier],
                ledger_evidence,
            )
        )
        answer_ids = {
            claim_id
            for claim_ids in requirements[identifier]["answer_claims"].values()
            for claim_id in claim_ids
        }
        negative_ids = {
            claim_id
            for claim_ids in requirements[identifier]["important_negatives"].values()
            for claim_id in claim_ids
        }
        required_claim_count_by_prompt[identifier] = {
            "answer_distinct": len(answer_ids),
            "negative_distinct": len(negative_ids),
            "union_distinct": len(answer_ids | negative_ids),
        }
    value = config(bundle, runner, prompt_values)
    yaml_text = yaml.dump(value, Dumper=Dumper, allow_unicode=True, sort_keys=False, width=120)
    atomic_write(args.output.resolve(), yaml_text)
    manifest = {
        "schema_version": "semantic-okf-endocrine-hygiene-skill-arena-config/2.0",
        "status": "pass",
        "benchmark_id": value["benchmark"]["id"],
        "prompt_ids": list(PROMPT_IDS),
        "profiles": [item["id"] for item in value["comparison"]["profiles"]],
        "requests_per_cell": 1,
        "config": {"path": args.output.relative_to(REPO).as_posix(), "sha256": sha256_bytes(yaml_text.encode("utf-8"))},
        "bundle": tree_binding(bundle),
        "consult_skill": tree_binding(REPO / "skills/consult-semantic-okf-classical"),
        "hard_claim_requirements": {
            "path": HARD_CLAIM_REQUIREMENTS.relative_to(REPO).as_posix(),
            "sha256": sha256_file(HARD_CLAIM_REQUIREMENTS),
        },
        "prompt_coverage": {
            "path": PROMPT_COVERAGE.relative_to(REPO).as_posix(),
            "sha256": sha256_file(PROMPT_COVERAGE),
        },
        "required_claim_count_by_prompt": required_claim_count_by_prompt,
        "reviewed_ledger_claim_count": len(ledger_evidence),
        "assertion_metrics": [
            "response-format",
            "response-contract",
            "evidence-validity",
            "claim-fidelity",
            "atomic-answer-completeness",
            "important-negative-coverage",
            "required-paper-coverage",
        ],
        "varied_capability_surfaces": ["skills"],
        "causal_scope": "paired five-question diagnostic only; not a portfolio ranking or stable aggregate estimate",
    }
    atomic_write(args.manifest.resolve(), json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n")
    print(canonical_json(manifest))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
