#!/usr/bin/env python3
"""Generate the compact q031 consultation comparison after MCP retirement."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[3]
EVALUATION = ROOT / "evaluations" / "semantic-okf-ensemble"
CURRENT_OUTPUT = EVALUATION / "cli-q031-current-output.json"
OUTPUT_JSON = EVALUATION / "cli-q031-comparison.json"
OUTPUT_MARKDOWN = EVALUATION / "cli-q031-comparison.md"
GROUND_TRUTH = EVALUATION / "reviewed-benchmark" / "hard-ground-truth.jsonl"
BUNDLE = (
    EVALUATION
    / "results"
    / "runs"
    / "20260715-ensemble-final-03"
    / "workspace-a"
    / "knowledge"
)
QUESTION_ID = "q031-graph-routing-boundary"
GATES = (
    "response-format",
    "response-contract",
    "evidence-validity",
    "atomic-answer-completeness",
    "important-negative-coverage",
)

RAW_SPECS = (
    {
        "id": "legacy",
        "display_name": "Legacy lexical",
        "provider_id": "legacy-consult-treatment",
        "result_id": "0f1c8221-5945-41be-92c1-6baf3eca219a",
        "path": "results/semantic-okf-legacy-hard10-paired/2026-07-14T10-44-29-188Z-compare/promptfoo-results.json",
    },
    {
        "id": "embeddings",
        "display_name": "Embeddings",
        "provider_id": "embedding-consult-treatment",
        "result_id": "03080c33-0b9c-4ee6-abd6-4f5a8fe394c0",
        "path": "results/semantic-okf-embedding-hard10-paired-retry-01/2026-07-14T10-55-43-243Z-compare/promptfoo-results.json",
    },
    {
        "id": "classical",
        "display_name": "Classical text processing",
        "provider_id": "classical-consult-treatment",
        "result_id": "d93aedfb-6991-4b38-be7c-7f2df24ec88f",
        "path": "results/semantic-okf-classical-hard10-paired/2026-07-14T10-24-08-885Z-compare/promptfoo-results.json",
    },
    {
        "id": "entity_graph",
        "display_name": "Entity graph",
        "provider_id": "entity-graph-consult-treatment",
        "result_id": "e241c82b-bd52-484f-bc5a-6d190f64ca9c",
        "path": "results/semantic-okf-entity-graph-hard10-paired/2026-07-14T13-24-34-018Z-compare/promptfoo-results.json",
    },
    {
        "id": "adaptive",
        "display_name": "Adaptive hybrid",
        "provider_id": "adaptive-consult-control",
        "result_id": "7119644d-9130-4635-91c6-3e64370f465b",
        "path": "results/semantic-okf-ensemble-hard10-three-arm/2026-07-15T15-24-19-159Z-compare/promptfoo-results.json",
    },
)

HISTORICAL_SPEC = {
    "id": "historical_mcp_ensemble",
    "display_name": "Historical definitive ensemble (retired MCP runtime)",
    "provider_id": "ensemble-consult-treatment",
    "result_id": "3f118e39-ac2e-4b43-8b8c-f16319c06b93",
    "path": "results/semantic-okf-ensemble-hard10-three-arm/2026-07-15T15-24-19-159Z-compare/promptfoo-results.json",
}

# These are the exact bundle bindings independently emitted by the finalizer and
# frozen by the q031 response contract. Keeping them here makes --check useful even
# when the large ignored bundle and Promptfoo runs are not present in a clone.
CURRENT_EXPECTED_BINDINGS = {
    "claim-2402-07630v3-039": {
        "concept_path": "concepts/claims-2402-07630v3/claim-2402-07630v3-039-d27e10fdca.md",
        "paper_id": "2402.07630v3",
        "source_path": "sources/claims/2402.07630v3.jsonl",
        "locators": ["PDF-page-8"],
    },
    "claim-2503-13804v1-038": {
        "concept_path": "concepts/claims-2503-13804v1/claim-2503-13804v1-038-9479e2cab6.md",
        "paper_id": "2503.13804v1",
        "source_path": "sources/claims/2503.13804v1.jsonl",
        "locators": ["PDF-page-3"],
    },
    "claim-2506-05690v3-043": {
        "concept_path": "concepts/claims-2506-05690v3/claim-2506-05690v3-043-862c0ca707.md",
        "paper_id": "2506.05690v3",
        "source_path": "sources/claims/2506.05690v3.jsonl",
        "locators": ["PDF-page-7", "PDF-page-8"],
    },
    "claim-2506-05690v3-044": {
        "concept_path": "concepts/claims-2506-05690v3/claim-2506-05690v3-044-a72d99898c.md",
        "paper_id": "2506.05690v3",
        "source_path": "sources/claims/2506.05690v3.jsonl",
        "locators": ["PDF-page-7", "PDF-page-8"],
    },
}


class ComparisonError(RuntimeError):
    """Raised when a retained answer or comparison binding is inconsistent."""


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _file_sha256(path: Path) -> str:
    return _sha256(path.read_bytes())


def _canonical_response(response: Mapping[str, Any]) -> str:
    return json.dumps(response, ensure_ascii=False, separators=(",", ":"))


def _finalizer_stdout(response: Mapping[str, Any]) -> str:
    """Match the finalizer's json.dumps output before any terminal newline."""
    return json.dumps(response, ensure_ascii=False)


def _json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def _load_ground_truth() -> dict[str, Any]:
    for line in GROUND_TRUTH.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        if row.get("id") == QUESTION_ID:
            return row
    raise ComparisonError(f"{QUESTION_ID} is absent from {GROUND_TRUTH}")


def _sorted_unique(items: list[Any]) -> bool:
    return len(set(items)) == len(items) and items == sorted(items)


def _response_contract(response: Mapping[str, Any]) -> bool:
    if list(response) != ["question_id", "answer", "evidence"]:
        return False
    if response.get("question_id") != QUESTION_ID or not isinstance(response.get("evidence"), list):
        return False
    answer = response.get("answer")
    if answer is None:
        return response["evidence"] == []
    if not isinstance(answer, dict) or list(answer) != ["summary", "claims", "paper_ids", "citations"]:
        return False
    words = re.findall(r"\S+", answer.get("summary", "")) if isinstance(answer.get("summary"), str) else []
    if not 180 <= len(words) <= 320:
        return False
    claims = answer.get("claims")
    paper_ids = answer.get("paper_ids")
    citations = answer.get("citations")
    evidence = response["evidence"]
    if not all(isinstance(value, list) and value for value in (claims, paper_ids, citations, evidence)):
        return False
    if not all(isinstance(item, str) for item in paper_ids) or not _sorted_unique(paper_ids):
        return False
    for claim in claims:
        if not isinstance(claim, dict) or list(claim) != ["statement", "supporting_claim_ids"]:
            return False
        ids = claim.get("supporting_claim_ids")
        if not isinstance(claim.get("statement"), str) or not claim["statement"].strip():
            return False
        if not isinstance(ids, list) or not all(isinstance(item, str) for item in ids) or not _sorted_unique(ids):
            return False
    cited = [item.get("paper_id") for item in citations if isinstance(item, dict)]
    if len(cited) != len(citations) or not _sorted_unique(cited):
        return False
    for citation in citations:
        if list(citation) != ["paper_id", "pages"] or citation["paper_id"] not in paper_ids:
            return False
        pages = citation.get("pages")
        if not isinstance(pages, list) or not pages or not _sorted_unique(pages):
            return False
        if not all(isinstance(page, int) and not isinstance(page, bool) and page > 0 for page in pages):
            return False
    evidence_ids = [item.get("claim_id") for item in evidence if isinstance(item, dict)]
    if len(evidence_ids) != len(evidence) or not _sorted_unique(evidence_ids):
        return False
    for item in evidence:
        if list(item) != ["claim_id", "concept_path", "paper_id", "source_path", "locators"]:
            return False
        if not all(isinstance(item[key], str) for key in ("claim_id", "concept_path", "paper_id", "source_path")):
            return False
        if not isinstance(item["locators"], list) or not _sorted_unique(item["locators"]):
            return False
    return True


def compute_current_gates(response: Mapping[str, Any], ground_truth: Mapping[str, Any]) -> dict[str, int]:
    """Recompute the five q031 Skill Arena gates without invoking a model."""
    answer = response.get("answer") if isinstance(response, dict) else None
    claims = answer.get("claims", []) if isinstance(answer, dict) else []
    evidence = response.get("evidence", []) if isinstance(response, dict) else []
    used = {
        claim_id
        for claim in claims
        if isinstance(claim, dict)
        for claim_id in claim.get("supporting_claim_ids", [])
    }
    evidence_ids = {
        item.get("claim_id") for item in evidence if isinstance(item, dict) and isinstance(item.get("claim_id"), str)
    }
    cited_pages = {
        item.get("paper_id"): {f"PDF-page-{page}" for page in item.get("pages", [])}
        for item in (answer.get("citations", []) if isinstance(answer, dict) else [])
        if isinstance(item, dict)
    }
    evidence_valid = bool(evidence)
    for item in evidence:
        expected = CURRENT_EXPECTED_BINDINGS.get(item.get("claim_id")) if isinstance(item, dict) else None
        if expected is None:
            evidence_valid = False
            break
        if any(item.get(key) != expected[key] for key in ("concept_path", "paper_id", "source_path")):
            evidence_valid = False
            break
        if not all(locator in expected["locators"] for locator in item.get("locators", [])):
            evidence_valid = False
            break
        if not all(locator in cited_pages.get(item.get("paper_id"), set()) for locator in item.get("locators", [])):
            evidence_valid = False
            break

    truth = ground_truth["ground_truth"]
    expected_sets = [claim["evidence_claim_ids"] for claim in truth["answer_claims"]]
    atomic = all(any(claim_id in used and claim_id in evidence_ids for claim_id in options) for options in expected_sets)
    required_papers = truth["required_paper_ids"]
    atomic = atomic and isinstance(answer, dict) and all(
        paper in answer.get("paper_ids", []) for paper in required_papers
    )
    negative_sets = [item["evidence_claim_ids"] for item in truth["important_negatives"]]
    negative = all(any(claim_id in used and claim_id in evidence_ids for claim_id in options) for options in negative_sets)
    return {
        "response-format": 1,
        "response-contract": int(_response_contract(response)),
        "evidence-validity": int(evidence_valid),
        "atomic-answer-completeness": int(atomic),
        "important-negative-coverage": int(negative),
    }


def _raw_entry(spec: Mapping[str, str]) -> dict[str, Any] | None:
    path = ROOT / spec["path"]
    if not path.is_file():
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = payload["results"]["results"]
    matches = [row for row in rows if row.get("id") == spec["result_id"]]
    if len(matches) != 1:
        raise ComparisonError(f"expected one retained row {spec['result_id']} in {spec['path']}")
    row = matches[0]
    if row.get("provider", {}).get("id") != spec["provider_id"]:
        raise ComparisonError(f"provider differs for retained row {spec['result_id']}")
    if f"`{QUESTION_ID}`" not in row.get("vars", {}).get("taskPrompt", ""):
        raise ComparisonError(f"question differs for retained row {spec['result_id']}")
    raw_output = row["response"]["output"].strip()
    response = json.loads(raw_output)
    named = {gate: int(row["namedScores"][gate]) for gate in GATES}
    entry = {
        "id": spec["id"],
        "display_name": spec["display_name"],
        "evaluation_status": "archived Skill Arena treatment row",
        "provenance": {
            "kind": "archived-skill-arena-treatment",
            "artifact_path": spec["path"],
            "artifact_sha256": _file_sha256(path),
            "provider_id": spec["provider_id"],
            "result_id": spec["result_id"],
            "canonical_response_sha256": _sha256(_canonical_response(response).encode("utf-8")),
            "summary_sha256": _sha256(response["answer"]["summary"].encode("utf-8")),
        },
        "named_gates": named,
        "passed_gate_count": sum(named.values()),
        "gate_count": len(GATES),
        "score": float(row["score"]),
        "response": response,
    }
    return entry


def _fallback_entry(report: Mapping[str, Any], entry_id: str) -> dict[str, Any]:
    candidates = list(report.get("main_alternatives", []))
    historical = report.get("historical_reference")
    if isinstance(historical, dict):
        candidates.append(historical)
    for entry in candidates:
        if entry.get("id") == entry_id:
            return entry
    raise ComparisonError(f"checked comparison has no fallback for {entry_id}")


def _archived_entry(spec: Mapping[str, str], prior: Mapping[str, Any] | None) -> dict[str, Any]:
    raw = _raw_entry(spec)
    if raw is not None:
        return raw
    if prior is None:
        raise ComparisonError(f"raw result {spec['path']} is absent and no checked fallback exists")
    return _fallback_entry(prior, spec["id"])


def _current_entry(response: Mapping[str, Any], ground_truth: Mapping[str, Any]) -> dict[str, Any]:
    gates = compute_current_gates(response, ground_truth)
    return {
        "id": "definitive_ensemble_cli",
        "display_name": "Definitive ensemble (current CLI-only)",
        "evaluation_status": "direct deterministic finalizer run; not fresh Skill Arena/model generation",
        "provenance": {
            "kind": "current-cli-finalizer",
            "artifact_path": CURRENT_OUTPUT.relative_to(ROOT).as_posix(),
            "artifact_sha256": _file_sha256(CURRENT_OUTPUT),
            "provider_id": "consult-semantic-okf-ensemble/finalize-answer",
            "result_id": None,
            "canonical_response_sha256": _sha256(_canonical_response(response).encode("utf-8")),
            "finalizer_stdout_without_newline_sha256": _sha256(
                _finalizer_stdout(response).encode("utf-8")
            ),
            "summary_sha256": _sha256(response["answer"]["summary"].encode("utf-8")),
            "run_id": "20260715-ensemble-final-03",
            "bundle_path": BUNDLE.relative_to(ROOT).as_posix(),
            "bundle_tree_sha256": "ed9386b63e4e087eea0fe62cd53eeb22e8f9cc4d5973b45eae7d736d9b77f868",
            "coverage_pack_sha256": "881dec7d573003631c7ee5bb6c55ba4568393df1f911c26dbaa7bfa5c0619ac7",
            "priority_order_sha256": "9ec21df4d02d0e1fba2a9dac3555c68e424968d347ff4d48d8df768351e1b25b",
            "mcp_used": False,
            "model_generation": False,
        },
        "named_gates": gates,
        "passed_gate_count": sum(gates.values()),
        "gate_count": len(GATES),
        "score": sum(gates.values()) / len(GATES),
        "response": response,
    }


def _validate_entry(entry: Mapping[str, Any]) -> None:
    if list(entry.get("named_gates", {})) != list(GATES):
        raise ComparisonError(f"gate order differs for {entry.get('id')}")
    values = list(entry["named_gates"].values())
    if any(value not in (0, 1) for value in values):
        raise ComparisonError(f"gate value differs for {entry.get('id')}")
    if entry.get("passed_gate_count") != sum(values) or entry.get("gate_count") != len(GATES):
        raise ComparisonError(f"gate count differs for {entry.get('id')}")
    if entry.get("score") != sum(values) / len(GATES):
        raise ComparisonError(f"score differs for {entry.get('id')}")
    response = entry.get("response")
    if not isinstance(response, dict) or response.get("question_id") != QUESTION_ID:
        raise ComparisonError(f"response differs for {entry.get('id')}")
    canonical_hash = _sha256(_canonical_response(response).encode("utf-8"))
    summary_hash = _sha256(response["answer"]["summary"].encode("utf-8"))
    if entry["provenance"].get("canonical_response_sha256") != canonical_hash:
        raise ComparisonError(f"response hash differs for {entry.get('id')}")
    stdout_hash = entry["provenance"].get("finalizer_stdout_without_newline_sha256")
    if stdout_hash is not None and stdout_hash != _sha256(_finalizer_stdout(response).encode("utf-8")):
        raise ComparisonError(f"finalizer stdout hash differs for {entry.get('id')}")
    if entry["provenance"].get("summary_sha256") != summary_hash:
        raise ComparisonError(f"summary hash differs for {entry.get('id')}")


def build_report() -> dict[str, Any]:
    prior = json.loads(OUTPUT_JSON.read_text(encoding="utf-8")) if OUTPUT_JSON.is_file() else None
    ground_truth = _load_ground_truth()
    current_response = json.loads(CURRENT_OUTPUT.read_text(encoding="utf-8"))
    main = [_archived_entry(spec, prior) for spec in RAW_SPECS]
    main.append(_current_entry(current_response, ground_truth))
    historical = _archived_entry(HISTORICAL_SPEC, prior)
    historical = dict(historical)
    historical["evaluation_status"] = "historical reference only; depended on the retired MCP runtime"
    report = {
        "schema_version": "semantic-okf-cli-q031-comparison/1.0",
        "question": {
            "id": QUESTION_ID,
            "text": ground_truth["question"],
            "ground_truth_path": GROUND_TRUTH.relative_to(ROOT).as_posix(),
            "ground_truth_sha256": _file_sha256(GROUND_TRUTH),
        },
        "comparison_policy": {
            "gate_order": list(GATES),
            "score_definition": "unweighted mean of the five binary q031 mechanical gates",
            "cross_family_interpretation": "descriptive only; rows came from separate retained treatment runs and the current definitive row is a direct deterministic finalizer run",
            "causal_claim": False,
        },
        "main_alternatives": main,
        "historical_reference": historical,
        "observations": [
            "The current CLI-only definitive finalizer passes all five mechanical gates (1.0).",
            "Embeddings has the strongest retained non-ensemble row (0.6); the other pre-definitive rows score 0.4 on this question.",
            "The historical MCP ensemble also scored 1.0, but it is retained only as historical evidence and is not the current runtime.",
            "These gates test JSON shape, exact evidence bindings, atomic ground-truth coverage, and the required negative; they are not a blinded semantic-quality review.",
        ],
    }
    for entry in [*main, historical]:
        _validate_entry(entry)
    if main[-1]["named_gates"] != {gate: 1 for gate in GATES}:
        raise ComparisonError("current CLI-only answer does not pass all five q031 gates")
    return report


def render_markdown(report: Mapping[str, Any]) -> str:
    lines = [
        "# q031 consultation comparison after MCP retirement",
        "",
        "## Scope",
        "",
        f"**Question:** {report['question']['text']}",
        "",
        "The five gates below are reproduced from the retained q031 Skill Arena contract. Cross-family results are descriptive, not causal: the archived treatment rows came from separate runs and bundles. The current definitive row is a direct, deterministic CLI finalizer run over a reviewed draft and complete bounded coverage; it is not a fresh Skill Arena or model generation.",
        "",
        "## Mechanical comparison",
        "",
        "| Alternative | Format | Contract | Evidence | Atomic answer | Negative | Score |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for entry in report["main_alternatives"]:
        gates = entry["named_gates"]
        values = ["pass" if gates[gate] else "fail" for gate in GATES]
        lines.append(
            f"| {entry['display_name']} | {values[0]} | {values[1]} | {values[2]} | {values[3]} | {values[4]} | {entry['score']:.1f} |"
        )
    lines.extend(
        [
            "",
            "A score is the unweighted mean of the five binary gates. The current CLI-only definitive answer is the only current main alternative that passes all five. Embeddings is the strongest retained non-ensemble row at 0.6. A failed mechanical gate does not prove every sentence is wrong; it means the exact benchmark contract was not fully satisfied.",
            "",
            "## Exact answer summaries",
            "",
            "The full response objects, evidence bindings, result IDs, artifact hashes, response hashes, and named gates are preserved in `cli-q031-comparison.json`.",
            "",
        ]
    )
    for entry in report["main_alternatives"]:
        lines.extend(
            [
                f"### {entry['display_name']}",
                "",
                f"Provenance: `{entry['provenance']['kind']}`; result ID: `{entry['provenance']['result_id'] or 'not applicable'}`; canonical response SHA-256: `{entry['provenance']['canonical_response_sha256']}`.",
                "",
                entry["response"]["answer"]["summary"],
                "",
            ]
        )
    historical = report["historical_reference"]
    lines.extend(
        [
            "## Historical MCP reference (not current runtime)",
            "",
            f"The retired MCP treatment scored **{historical['score']:.1f}** (five of five gates). It remains useful as a historical reference, but must not be described as the active definitive consultation path.",
            "",
            f"Result ID: `{historical['provenance']['result_id']}`; canonical response SHA-256: `{historical['provenance']['canonical_response_sha256']}`.",
            "",
            historical["response"]["answer"]["summary"],
            "",
            "## Reproduce",
            "",
            "```powershell",
            "python evaluations/semantic-okf-ensemble/scripts/generate_cli_q031_comparison.py --check",
            "```",
            "",
            "When the ignored append-only Promptfoo results are present, the generator cross-checks the retained rows by result ID. When they are absent, it validates their checked compact response objects and hashes internally. No MCP service is needed.",
            "",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if checked artifacts differ")
    args = parser.parse_args(argv)
    try:
        report = build_report()
        json_bytes = _json_bytes(report)
        markdown_bytes = render_markdown(report).encode("utf-8")
        if args.check:
            if not OUTPUT_JSON.is_file() or OUTPUT_JSON.read_bytes() != json_bytes:
                raise ComparisonError(f"{OUTPUT_JSON.relative_to(ROOT)} is stale")
            if not OUTPUT_MARKDOWN.is_file() or OUTPUT_MARKDOWN.read_bytes() != markdown_bytes:
                raise ComparisonError(f"{OUTPUT_MARKDOWN.relative_to(ROOT)} is stale")
            print("CLI q031 comparison artifacts are current")
            return 0
        OUTPUT_JSON.write_bytes(json_bytes)
        OUTPUT_MARKDOWN.write_bytes(markdown_bytes)
        print(f"wrote {OUTPUT_JSON.relative_to(ROOT)}")
        print(f"wrote {OUTPUT_MARKDOWN.relative_to(ROOT)}")
        return 0
    except (ComparisonError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
