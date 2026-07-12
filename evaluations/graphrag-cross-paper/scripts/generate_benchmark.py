"""Generate the 30-question isolated PI GraphRAG cross-paper benchmark."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / "fixtures" / "workspaces" / "skill-overlay" / "knowledge"
SKILL_ID = "consult-semantic-okf"
SKILL_SNAPSHOT = ROOT / "fixtures" / "workspaces" / "skill-overlay" / "skills" / SKILL_ID
QUESTION_COUNT = 30
SMOKE_IDS = {
    "q001-methodology-taxonomy",
    "q006-path-subgraph-reasoning",
    "q016-noise-redundancy",
    "q024-evaluation-practices",
    "q030-design-decision-framework",
}
HOLDOUT_IDS = {
    "q005-community-hierarchy",
    "q010-context-organization",
    "q015-incremental-updates",
    "q020-domain-adaptation",
    "q025-benchmark-bias",
    "q029-static-agentic-retrieval",
}
TECHNICAL_RECOVERY_IDS = {
    "q009-query-processing-routing",
    "q017-imperfect-graphs",
}
CLAIM_KINDS = {
    "methodology",
    "graph-representation",
    "graph-construction",
    "retrieval-unit",
    "retrieval-strategy",
    "organization-synthesis",
    "task",
    "evaluation",
    "strength",
    "limitation",
    "efficiency-update",
    "safety-grounding",
    "comparison",
}


class BenchmarkError(RuntimeError):
    """Raised when benchmark inputs cannot support a valid isolated comparison."""


class LiteralString(str):
    """Request YAML literal-block rendering for prompts, rubrics, and JavaScript."""


class BenchmarkDumper(yaml.SafeDumper):
    """Render benchmark YAML without escaping human-readable Unicode."""


def represent_literal(dumper: BenchmarkDumper, value: LiteralString) -> yaml.ScalarNode:
    """Represent a literal string with YAML block style."""
    return dumper.represent_scalar("tag:yaml.org,2002:str", value, style="|")


BenchmarkDumper.add_representer(LiteralString, represent_literal)


def canonical_json(value: Any) -> str:
    """Return stable compact JSON."""
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def tree_sha256(root: Path) -> str:
    """Hash a logical file tree independently of Git line-ending conversion."""
    members: list[dict[str, str]] = []
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        content = path.read_bytes()
        if b"\x00" not in content:
            content = content.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
        members.append(
            {"path": path.relative_to(root).as_posix(), "sha256": hashlib.sha256(content).hexdigest()}
        )
    return hashlib.sha256(canonical_json(members).encode("utf-8")).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    """Load one JSON object."""
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise BenchmarkError(f"Expected a JSON object: {path}")
    return value


def load_records() -> list[dict[str, Any]]:
    """Load every normalized record from the pinned treatment snapshot."""
    path = BUNDLE / "semantic" / "records.jsonl"
    records = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if len(records) != 874:
        raise BenchmarkError(f"Expected 874 pinned records, found {len(records)}.")
    return records


def paper_metadata(records: list[dict[str, Any]]) -> tuple[dict[str, str], dict[str, int]]:
    """Return paper-to-concept and paper-to-page-count maps from the ledger."""
    concept_paths: dict[str, str] = {}
    page_counts: dict[str, int] = {}
    for record in records:
        if record.get("concept_type") != "Research Paper":
            continue
        attributes = record.get("attributes", {})
        paper_id = attributes.get("paper_id")
        if not isinstance(paper_id, str):
            raise BenchmarkError("A Research Paper record lacks paper_id.")
        concept_paths[paper_id] = record["concept_path"]
        page_counts[paper_id] = int(attributes["page_count"])
    if len(concept_paths) != 15:
        raise BenchmarkError(f"Expected 15 paper concepts, found {len(concept_paths)}.")
    return dict(sorted(concept_paths.items())), dict(sorted(page_counts.items()))


def artifact_paths() -> list[str]:
    """List every treatment snapshot path that an answer may cite."""
    return sorted(path.relative_to(BUNDLE).as_posix() for path in BUNDLE.rglob("*") if path.is_file())


def semantic_signature(question: dict[str, Any]) -> str:
    """Hash semantic intent independently from question wording and category labels."""
    descriptor = {
        "operation": "cross-paper-synthesis",
        "dimensions": sorted(question["dimensions"]),
        "focus_papers": sorted(question["focus_papers"]),
        "min_papers": question["min_papers"],
        "required_points": question["required_points"],
    }
    return hashlib.sha256(canonical_json(descriptor).encode("utf-8")).hexdigest()


def validate_blueprint(value: dict[str, Any], paper_ids: set[str]) -> list[dict[str, Any]]:
    """Validate question count, semantic uniqueness, and multi-source coverage."""
    questions = value.get("questions")
    if not isinstance(questions, list) or len(questions) != QUESTION_COUNT:
        raise BenchmarkError(f"Blueprint must contain exactly {QUESTION_COUNT} questions.")
    ids: set[str] = set()
    signatures: set[str] = set()
    for question in questions:
        identifier = question.get("id")
        if not isinstance(identifier, str) or identifier in ids:
            raise BenchmarkError(f"Duplicate or invalid question ID: {identifier!r}")
        ids.add(identifier)
        dimensions = question.get("dimensions")
        focus = question.get("focus_papers")
        points = question.get("required_points")
        minimum = question.get("min_papers")
        if not isinstance(dimensions, list) or not dimensions or not set(dimensions) <= CLAIM_KINDS:
            raise BenchmarkError(f"Invalid dimensions for {identifier}.")
        if len(set(dimensions)) != len(dimensions):
            raise BenchmarkError(f"Dimensions must be unique for {identifier}.")
        if not isinstance(focus, list) or len(set(focus)) != len(focus) or not set(focus) <= paper_ids:
            raise BenchmarkError(f"Invalid focus papers for {identifier}.")
        if focus != sorted(focus):
            raise BenchmarkError(f"Focus papers must be sorted for {identifier}.")
        if not isinstance(minimum, int) or minimum < 3 or minimum > len(focus):
            raise BenchmarkError(f"Invalid minimum paper coverage for {identifier}.")
        if not isinstance(points, list) or len(points) < 3 or any(not isinstance(point, str) for point in points):
            raise BenchmarkError(f"Invalid semantic rubric for {identifier}.")
        signature = semantic_signature(question)
        if signature in signatures:
            raise BenchmarkError(f"Duplicate semantic signature for {identifier}.")
        signatures.add(signature)
    if SMOKE_IDS - ids:
        raise BenchmarkError(f"Smoke IDs are missing: {sorted(SMOKE_IDS - ids)}")
    if HOLDOUT_IDS - ids:
        raise BenchmarkError(f"Holdout IDs are missing: {sorted(HOLDOUT_IDS - ids)}")
    return questions


def build_prompt(question: dict[str, Any]) -> LiteralString:
    """Build one identical cross-profile prompt without embedding the gold rubric."""
    identifier = question["id"]
    required_dimensions = json.dumps(sorted(question["dimensions"]))
    minimum_papers = question["min_papers"]
    return LiteralString(
        "Answer one cross-paper GraphRAG synthesis question. The authoritative Semantic OKF snapshot is available "
        "only when your declared capabilities provide it at `knowledge/`. Use only that snapshot; do not use the web, "
        "prior knowledge, or guesses.\n\n"
        "Consult the snapshot efficiently: use the ledger for discovery, SPARQL over `semantic/data.ttl` for claim-kind "
        "joins, and the cited paper concepts for page-level verification. Compare formulations across independent papers; "
        "do not treat shared analysis dimensions as proof that methods are equivalent.\n\n"
        f"Question: {question['question']}\n\n"
        "Return JSON only with exactly these top-level keys in this order: `question_id`, `answer`, `evidence`. "
        f"Set `question_id` to `{identifier}`. If the snapshot is unavailable, return `answer: null` and an empty "
        "`evidence` array. Otherwise `answer` must be an object with exactly these keys in this order: `summary`, "
        "`dimensions`, `paper_ids`, `citations`. Write a comparative 180-300 word `summary`; do not merely list papers. "
        f"Include every required controlled claim-kind ID {required_dimensions} in sorted, unique `dimensions`; "
        "additional relevant controlled claim-kind IDs are allowed. Use sorted, unique versioned "
        "arXiv IDs in `paper_ids`. `citations` must be sorted by `paper_id`, with objects shaped exactly as "
        "`{\"paper_id\":\"...\",\"pages\":[1,2]}` and sorted unique PDF page numbers. Cite enough independent papers "
        f"to support the synthesis, with at least {minimum_papers} independent papers. `evidence` must contain "
        "sorted, unique existing paths that trace to those papers; paper concepts and paper-specific claim concepts "
        "both count, and additional existing semantic artifacts are allowed."
    )


def structure_assertion(question: dict[str, Any], all_papers: list[str]) -> LiteralString:
    """Require expected analysis dimensions and a sufficient focus-paper intersection."""
    expected_dimensions = json.dumps(sorted(question["dimensions"]))
    focus = json.dumps(sorted(question["focus_papers"]))
    valid = json.dumps(all_papers)
    minimum = question["min_papers"]
    identifier = json.dumps(question["id"])
    return LiteralString(
        "try {\n"
        "  const actual = JSON.parse(output.trim());\n"
        f"  if (actual.question_id !== {identifier} || actual.answer === null) return false;\n"
        f"  const expectedDimensions = {expected_dimensions};\n"
        f"  const focus = new Set({focus});\n"
        f"  const valid = new Set({valid});\n"
        "  const dimensions = actual.answer.dimensions;\n"
        "  const papers = actual.answer.paper_ids;\n"
        "  if (!Array.isArray(dimensions) || !Array.isArray(papers)) return false;\n"
        "  if (new Set(dimensions).size !== dimensions.length || new Set(papers).size !== papers.length) return false;\n"
        "  if (JSON.stringify([...dimensions].sort()) !== JSON.stringify(dimensions)) return false;\n"
        "  if (JSON.stringify([...papers].sort()) !== JSON.stringify(papers)) return false;\n"
        "  if (!expectedDimensions.every((item) => dimensions.includes(item))) return false;\n"
        "  if (!dimensions.every((item) => " + json.dumps(sorted(CLAIM_KINDS)) + ".includes(item))) return false;\n"
        "  if (!papers.every((item) => valid.has(item))) return false;\n"
        f"  return papers.filter((item) => focus.has(item)).length >= {minimum};\n"
        "} catch { return false; }"
    )


def citation_assertion(question: dict[str, Any], page_counts: dict[str, int]) -> LiteralString:
    """Require valid, page-bounded citations from enough independent focus papers."""
    focus = json.dumps(sorted(question["focus_papers"]))
    pages = json.dumps(page_counts, sort_keys=True)
    minimum = question["min_papers"]
    return LiteralString(
        "try {\n"
        "  const actual = JSON.parse(output.trim());\n"
        "  if (actual.answer === null) return false;\n"
        "  const citations = actual.answer.citations;\n"
        f"  const focus = new Set({focus});\n"
        f"  const pageCounts = {pages};\n"
        "  const papers = new Set(actual.answer.paper_ids);\n"
        "  if (!Array.isArray(citations) || citations.length === 0) return false;\n"
        "  const cited = citations.map((item) => item.paper_id);\n"
        "  if (new Set(cited).size !== cited.length || JSON.stringify([...cited].sort()) !== JSON.stringify(cited)) return false;\n"
        "  for (const item of citations) {\n"
        "    if (JSON.stringify(Object.keys(item)) !== JSON.stringify(['paper_id', 'pages'])) return false;\n"
        "    if (!papers.has(item.paper_id) || !(item.paper_id in pageCounts)) return false;\n"
        "    if (!Array.isArray(item.pages) || item.pages.length === 0 || new Set(item.pages).size !== item.pages.length) return false;\n"
        "    if (JSON.stringify([...item.pages].sort((a,b) => a-b)) !== JSON.stringify(item.pages)) return false;\n"
        "    if (!item.pages.every((page) => Number.isInteger(page) && page >= 1 && page <= pageCounts[item.paper_id])) return false;\n"
        "  }\n"
        f"  return cited.filter((item) => focus.has(item)).length >= {minimum};\n"
        "} catch { return false; }"
    )


def evidence_assertion(question: dict[str, Any], concept_paths: dict[str, str]) -> LiteralString:
    """Require enough paper-traceable concept paths from independent focus papers."""
    patterns: dict[str, dict[str, Any]] = {}
    for paper in question["focus_papers"]:
        paper_path = concept_paths[paper]
        paper_directory = paper_path.split("/", 2)[1]
        slug = paper_directory.removeprefix("paper-")
        patterns[paper] = {
            "exact": paper_path,
            "prefixes": [
                f"concepts/claims-{slug}/",
                f"concepts/analysis-vocabulary/method-{slug}-",
            ],
        }
    focus = json.dumps(sorted(question["focus_papers"]))
    encoded_patterns = json.dumps(patterns, sort_keys=True)
    minimum = question["min_papers"]
    return LiteralString(
        "const normalize = (value) => value.replaceAll('\\\\', '/').replace(/^\\.\\//, '').replace(/^knowledge\\//, '');\n"
        "try {\n"
        "  const actual = JSON.parse(output.trim());\n"
        "  if (actual.answer === null) return false;\n"
        f"  const patterns = {encoded_patterns};\n"
        f"  const focus = new Set({focus});\n"
        "  const normalized = actual.evidence.map(normalize);\n"
        "  const citedPapers = new Set();\n"
        "  for (const path of normalized) {\n"
        "    for (const [paper, pattern] of Object.entries(patterns)) {\n"
        "      if (path === pattern.exact || pattern.prefixes.some((prefix) => path.startsWith(prefix))) citedPapers.add(paper);\n"
        "    }\n"
        "  }\n"
        f"  return [...citedPapers].filter((paper) => focus.has(paper)).length >= {minimum};\n"
        "} catch { return false; }"
    )


def prompt_entry(
    question: dict[str, Any], all_papers: list[str], concept_paths: dict[str, str], page_counts: dict[str, int]
) -> dict[str, Any]:
    """Build one prompt row and its hidden evaluation assertions."""
    return {
        "id": question["id"],
        "description": f"Cross-paper GraphRAG synthesis: {question['category']}",
        "prompt": build_prompt(question),
        "evaluation": {
            "assertions": [
                {"type": "javascript", "metric": "semantic-structure", "value": structure_assertion(question, all_papers)},
                {"type": "javascript", "metric": "page-citation-grounding", "value": citation_assertion(question, page_counts)},
                {"type": "javascript", "metric": "cross-paper-evidence", "value": evidence_assertion(question, concept_paths)},
            ]
        },
    }


def shared_assertions(known_paths: list[str]) -> list[dict[str, Any]]:
    """Return response-shape and evidence-path assertions shared by all prompts."""
    contract = LiteralString(
        "try {\n"
        "  const actual = JSON.parse(output.trim());\n"
        "  if (JSON.stringify(Object.keys(actual)) !== JSON.stringify(['question_id', 'answer', 'evidence'])) return false;\n"
        "  if (typeof actual.question_id !== 'string' || !Array.isArray(actual.evidence)) return false;\n"
        "  if (new Set(actual.evidence).size !== actual.evidence.length || JSON.stringify([...actual.evidence].sort()) !== JSON.stringify(actual.evidence)) return false;\n"
        "  if (actual.answer === null) return actual.evidence.length === 0;\n"
        "  if (JSON.stringify(Object.keys(actual.answer)) !== JSON.stringify(['summary', 'dimensions', 'paper_ids', 'citations'])) return false;\n"
        "  const words = actual.answer.summary.trim().split(/\\s+/).filter(Boolean).length;\n"
        "  return typeof actual.answer.summary === 'string' && words >= 180 && words <= 300\n"
        "    && Array.isArray(actual.answer.dimensions) && Array.isArray(actual.answer.paper_ids)\n"
        "    && Array.isArray(actual.answer.citations) && actual.evidence.length > 0;\n"
        "} catch { return false; }"
    )
    path_check = LiteralString(
        "const normalize = (value) => value.replaceAll('\\\\', '/').replace(/^\\.\\//, '').replace(/^knowledge\\//, '');\n"
        "try {\n"
        "  const actual = JSON.parse(output.trim());\n"
        f"  const known = new Set({json.dumps(known_paths)});\n"
        "  return actual.evidence.every((item) => typeof item === 'string' && known.has(normalize(item)));\n"
        "} catch { return false; }"
    )
    return [
        {"type": "is-json", "metric": "response-format"},
        {"type": "javascript", "metric": "response-contract", "value": contract},
        {"type": "javascript", "metric": "evidence-path-validity", "value": path_check},
    ]


def evaluation_manifest(prompts: list[dict[str, Any]], known_paths: list[str], description: str) -> dict[str, Any]:
    """Build a valid Skill Arena V1 compare manifest."""
    return {
        "schemaVersion": 1,
        "benchmark": {
            "id": "graphrag-cross-paper-30-compare",
            "description": description,
            "tags": ["graphrag", "semantic-okf", "cross-paper", "pi", "compare", "30-questions"],
        },
        "task": {"prompts": prompts},
        "workspace": {
            "sources": [
                {
                    "id": "isolated-base",
                    "type": "local-path",
                    "path": "evaluations/graphrag-cross-paper/fixtures/workspaces/base",
                    "target": "/",
                }
            ],
            "setup": {"initializeGit": True, "env": {"SEMANTIC_OKF_BUNDLE": "$WORKSPACE/knowledge"}},
        },
        "evaluation": {
            "assertions": shared_assertions(known_paths),
            "requests": 1,
            "timeoutMs": 600000,
            "tracing": False,
            "maxConcurrency": 2,
            "noCache": True,
        },
        "comparison": {
            "profiles": [
                {
                    "id": "no-skill",
                    "description": "Isolated control with neither the reader skill nor the paper snapshot.",
                    "isolation": {"inheritSystem": False},
                    "capabilities": {},
                    "output": {
                        "tags": ["control", "knowledge-off"],
                        "labels": {"skill_state": "off", "knowledge_access": "off"},
                    },
                },
                {
                    "id": "consult-skill",
                    "description": (
                        "Isolated treatment with the pinned read-only Semantic OKF consultation "
                        "skill and GraphRAG snapshot."
                    ),
                    "isolation": {"inheritSystem": False},
                    "capabilities": {
                        "skills": [
                            {
                                "source": {
                                    "type": "local-path",
                                    "path": "evaluations/graphrag-cross-paper/fixtures/workspaces/skill-overlay",
                                    "skillId": SKILL_ID,
                                },
                                "install": {"strategy": "workspace-overlay"},
                            }
                        ]
                    },
                    "output": {
                        "tags": ["consult-skill", "knowledge-on", "read-only"],
                        "labels": {"skill_state": "consult", "knowledge_access": "on"},
                    },
                },
            ],
            "variants": [
                {
                    "id": "pi-luna-only",
                    "description": "PI with GPT-5.6 Luna for every isolated answer request.",
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
                        "cliEnv": {
                            "PI_MODEL_TIMEOUT_SECONDS": "240",
                        },
                        "config": {},
                    },
                    "output": {
                        "tags": ["pi", "gpt-5.6-luna", "luna-only", "isolated"],
                        "labels": {
                            "variantDisplayName": "PI GPT-5.6 Luna",
                            "adapter_family": "pi",
                            "model": "openai-codex/gpt-5.6-luna",
                            "routing": "luna-only",
                        },
                    },
                }
            ],
        },
    }


def holdout_evaluation_manifest(
    prompt_rows: list[dict[str, Any]], known_paths: list[str]
) -> dict[str, Any]:
    """Derive a one-profile validation manifest for the fixed holdout split."""
    rows = [row for row in prompt_rows if row["id"] in HOLDOUT_IDS]
    if len(rows) != len(HOLDOUT_IDS):
        raise BenchmarkError(f"Expected {len(HOLDOUT_IDS)} holdout prompts, found {len(rows)}.")
    manifest = evaluation_manifest(
        rows,
        known_paths,
        "Validate the Semantic OKF consultation skill on six fixed GraphRAG holdout questions.",
    )
    manifest["benchmark"].update(
        {
            "id": "graphrag-cross-paper-holdout-6-validation",
            "tags": [
                "graphrag",
                "semantic-okf",
                "cross-paper",
                "pi",
                "holdout",
                "6-questions",
            ],
        }
    )
    treatment = next(
        profile
        for profile in manifest["comparison"]["profiles"]
        if profile["id"] == "consult-skill"
    )
    treatment.update(
        {
            "description": (
                "Isolated holdout treatment with the read-only Semantic OKF consultation skill "
                "and pinned GraphRAG snapshot."
            ),
            "output": {
                "tags": ["consult-skill", "knowledge-on", "read-only", "holdout"],
                "labels": {
                    "skill_state": "consult",
                    "knowledge_access": "on",
                    "split": "holdout",
                },
            },
        }
    )
    manifest["comparison"]["profiles"] = [treatment]
    return manifest


def skill_only_evaluation_manifest(
    prompt_rows: list[dict[str, Any]], known_paths: list[str]
) -> dict[str, Any]:
    """Derive the post-evolution 30-question treatment-only manifest."""

    manifest = evaluation_manifest(
        prompt_rows,
        known_paths,
        (
            "Re-evaluate the evolved Semantic OKF consultation skill on all 30 GraphRAG "
            "questions without rerunning the frozen no-skill control."
        ),
    )
    manifest["benchmark"].update(
        {
            "id": "graphrag-cross-paper-30-consult-skill-retest",
            "tags": [
                "graphrag",
                "semantic-okf",
                "cross-paper",
                "pi",
                "skill-only",
                "30-questions",
            ],
        }
    )
    treatment = next(
        profile
        for profile in manifest["comparison"]["profiles"]
        if profile["id"] == "consult-skill"
    )
    treatment.update(
        {
            "description": (
                "Isolated evolved-skill treatment with the pinned read-only Semantic OKF "
                "consultation skill and GraphRAG snapshot."
            ),
            "output": {
                "tags": ["consult-skill", "knowledge-on", "read-only", "post-evolution"],
                "labels": {
                    "skill_state": "consult-evolved",
                    "knowledge_access": "on",
                    "evaluation_scope": "skill-only",
                },
            },
        }
    )
    manifest["comparison"]["profiles"] = [treatment]
    manifest["evaluation"]["maxConcurrency"] = 4
    return manifest


def technical_recovery_evaluation_manifest(
    prompt_rows: list[dict[str, Any]], known_paths: list[str]
) -> dict[str, Any]:
    """Build a separately reported retry for the two timed-out full-run cells."""

    rows = [row for row in prompt_rows if row["id"] in TECHNICAL_RECOVERY_IDS]
    if len(rows) != len(TECHNICAL_RECOVERY_IDS):
        raise BenchmarkError(
            f"Expected {len(TECHNICAL_RECOVERY_IDS)} recovery prompts, found {len(rows)}."
        )
    manifest = skill_only_evaluation_manifest(rows, known_paths)
    manifest["benchmark"].update(
        {
            "id": "graphrag-cross-paper-technical-recovery-2",
            "description": (
                "Supplemental skill-only rerun of the two cells that hit the strict 240-second "
                "Luna wrapper timeout; never merge these results into the primary 30-cell score."
            ),
            "tags": [
                "graphrag",
                "semantic-okf",
                "pi",
                "skill-only",
                "technical-recovery",
                "2-questions",
            ],
        }
    )
    profile = manifest["comparison"]["profiles"][0]
    profile["output"] = {
        "tags": ["consult-skill", "knowledge-on", "read-only", "technical-recovery"],
        "labels": {
            "skill_state": "consult-evolved",
            "knowledge_access": "on",
            "evaluation_scope": "technical-recovery-only",
            "score_merge": "forbidden",
        },
    }
    manifest["comparison"]["variants"][0]["agent"]["cliEnv"] = {
        "PI_MODEL_TIMEOUT_SECONDS": "360"
    }
    manifest["evaluation"]["maxConcurrency"] = 2
    return manifest


def yaml_text(value: dict[str, Any]) -> str:
    """Serialize a compare manifest with stable readable YAML."""
    return yaml.dump(
        value,
        Dumper=BenchmarkDumper,
        allow_unicode=True,
        sort_keys=False,
        default_flow_style=False,
        width=120,
    )


def build_outputs() -> dict[Path, str]:
    """Build every deterministic benchmark artifact in memory."""
    records = load_records()
    concept_paths, page_counts = paper_metadata(records)
    all_papers = sorted(concept_paths)
    blueprint = load_json(ROOT / "questions-blueprint.json")
    questions = validate_blueprint(blueprint, set(all_papers))
    known_paths = artifact_paths()
    prompt_rows = [prompt_entry(question, all_papers, concept_paths, page_counts) for question in questions]
    full_manifest = evaluation_manifest(
        prompt_rows,
        known_paths,
        "Compare isolated PI cross-paper synthesis with no knowledge access against a pinned Semantic OKF GraphRAG corpus and reader skill.",
    )
    smoke_rows = [row for row in prompt_rows if row["id"] in SMOKE_IDS]
    smoke_manifest = evaluation_manifest(
        smoke_rows,
        known_paths,
        "Five-question live rehearsal of the isolated 30-question GraphRAG cross-paper comparison.",
    )
    holdout_manifest = holdout_evaluation_manifest(prompt_rows, known_paths)
    skill_only_manifest = skill_only_evaluation_manifest(prompt_rows, known_paths)
    recovery_manifest = technical_recovery_evaluation_manifest(prompt_rows, known_paths)

    question_lines: list[str] = []
    paper_coverage: Counter[str] = Counter()
    dimension_coverage: Counter[str] = Counter()
    category_coverage: Counter[str] = Counter()
    for question, row in zip(questions, prompt_rows, strict=True):
        signature = semantic_signature(question)
        paper_coverage.update(question["focus_papers"])
        dimension_coverage.update(question["dimensions"])
        category_coverage.update([question["category"]])
        question_lines.append(
            canonical_json(
                {
                    **question,
                    "semantic_signature": signature,
                    "prompt": str(row["prompt"]),
                    "paper_concept_paths": {paper: concept_paths[paper] for paper in question["focus_papers"]},
                }
            )
        )
    coverage = {
        "benchmark_id": blueprint["benchmark_id"],
        "question_count": len(questions),
        "semantic_signature_count": len({semantic_signature(question) for question in questions}),
        "smoke_question_count": len(smoke_rows),
        "holdout_question_count": len(holdout_manifest["task"]["prompts"]),
        "skill_only_question_count": len(skill_only_manifest["task"]["prompts"]),
        "technical_recovery_question_count": len(recovery_manifest["task"]["prompts"]),
        "paper_focus_counts": dict(sorted(paper_coverage.items())),
        "dimension_counts": dict(sorted(dimension_coverage.items())),
        "category_counts": dict(sorted(category_coverage.items())),
        "snapshot_tree_sha256": tree_sha256(BUNDLE),
        "skill_id": SKILL_ID,
        "skill_snapshot_tree_sha256": tree_sha256(SKILL_SNAPSHOT),
        "record_count": len(records),
        "paper_count": len(all_papers),
    }
    if min(paper_coverage.values()) < 8:
        raise BenchmarkError(f"Every paper must appear in at least eight focus sets: {coverage['paper_focus_counts']}")
    return {
        ROOT / "evaluation.yaml": yaml_text(full_manifest),
        ROOT / "smoke-evaluation.yaml": yaml_text(smoke_manifest),
        ROOT / "holdout-evaluation.yaml": yaml_text(holdout_manifest),
        ROOT / "skill-only-evaluation.yaml": yaml_text(skill_only_manifest),
        ROOT / "technical-recovery-evaluation.yaml": yaml_text(recovery_manifest),
        ROOT / "questions.jsonl": "\n".join(question_lines) + "\n",
        ROOT / "coverage.json": json.dumps(coverage, ensure_ascii=False, indent=2) + "\n",
    }


def write_or_check(outputs: dict[Path, str], *, check: bool) -> None:
    """Write deterministic artifacts or verify byte-for-byte drift."""
    drift: list[str] = []
    for path, content in outputs.items():
        if check:
            if not path.is_file() or path.read_text(encoding="utf-8") != content:
                drift.append(path.name)
        else:
            path.write_text(content, encoding="utf-8")
    if drift:
        raise BenchmarkError(f"Generated benchmark drift: {', '.join(sorted(drift))}")


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Verify generated files without rewriting them.")
    return parser


def main() -> int:
    """Generate or verify the benchmark artifacts."""
    args = build_parser().parse_args()
    outputs = build_outputs()
    write_or_check(outputs, check=args.check)
    coverage = json.loads(outputs[ROOT / "coverage.json"])
    print(
        canonical_json(
            {
                "question_count": coverage["question_count"],
                "semantic_signature_count": coverage["semantic_signature_count"],
                "snapshot_tree_sha256": coverage["snapshot_tree_sha256"],
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
