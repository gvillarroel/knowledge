#!/usr/bin/env python3
"""Validate the closed Semantic OKF ensemble evaluation scaffold."""

from __future__ import annotations

import ast
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any, Sequence

import yaml

from _evaluation import (
    ENSEMBLE_PLAN,
    REPO_ROOT,
    EvaluationError,
    benchmark_rows,
    canonical_json,
    load_json,
    module_from_path,
    sha256,
    validate_frozen,
)
from _answer_output import load_contract as load_answer_output_contract
from summarize_population_search import validate_config, validate_generation, validate_report


EVALUATION_ROOT = REPO_ROOT / "evaluations/semantic-okf-ensemble"
CONTRACT = EVALUATION_ROOT / "evaluation-contract.json"
POPULATION = EVALUATION_ROOT / "population-search.json"
GENERATION = EVALUATION_ROOT / "generation-000.json"
POPULATION_RESULTS = EVALUATION_ROOT / "population-search-results.json"
BASELINES = EVALUATION_ROOT / "baselines"
BUILD_VALIDATION = EVALUATION_ROOT / "build-validation-final.json"
MANUAL_VERIFICATION = EVALUATION_ROOT / "manual-query-verification-final.json"
EXPECTED_ID_AUDIT = EVALUATION_ROOT / "expected-id-audit-final.json"
EXPECTED_ID_AUDIT_MARKDOWN = EVALUATION_ROOT / "EXPECTED-ID-AUDIT.md"
EXPECTED_ID_AUDIT_SHA256 = "0e3e96c85aeac99365ff55690b52af734c9b9525fefd2d37c256d9e48440816a"
HISTORICAL_ANSWER_BINDINGS_SHA256 = (
    "7ff6a6673ffb38d8ec2dc7ba03827ec036137397e4626bc99a408af473084bed"
)
ANSWER_OUTPUT_CONTRACT = EVALUATION_ROOT / "answer-output-evaluation-contract.json"
ANSWER_OUTPUT_REPORT = EVALUATION_ROOT / "answer-output-comparison-final.json"
ANSWER_OUTPUT_MARKDOWN = EVALUATION_ROOT / "answer-output-comparison-final.md"
SKILL_ARENA_CONFIG = EVALUATION_ROOT / "skill-arena/ensemble-hard10.yaml"
SKILL_ARENA_MANIFEST = EVALUATION_ROOT / "skill-arena/config-manifest.json"
MCP_RUNTIME_ATTESTATION = EVALUATION_ROOT / "skill-arena-mcp-runtime-attestation-final.json"
MCP_RUNTIME_ATTESTATION_MARKDOWN = EVALUATION_ROOT / "skill-arena-mcp-runtime-attestation-final.md"
HISTORICAL_MCP_EVIDENCE = EVALUATION_ROOT / "historical-mcp-evaluation-binding.json"
HISTORICAL_MCP_SOURCE_COMMIT = "3a5df66baf99c6c34ef6ff96d35aa44740b906c6"
ACTIVE_CONSULT_SKILL = REPO_ROOT / "skills/consult-semantic-okf-ensemble"
FINALIZER_COPY_DIAGNOSTIC = EVALUATION_ROOT / "finalizer-copy-integrity-diagnostic-20260715.json"
FINALIZER_COPY_DIAGNOSTIC_MARKDOWN = EVALUATION_ROOT / "finalizer-copy-integrity-diagnostic-20260715.md"
FINALIZER_COPY_DIAGNOSTIC_SHA256 = "0ce8e9df47ed3f226acbaa254143f528473331cfc9ce78222a96d4c0f41026f3"
FINALIZER_COPY_DIAGNOSTIC_MARKDOWN_SHA256 = "3a325b4985764bb7ffccdee93e8071b766d85c3280c7a0fe697031a529bd1eac"
HOST_PUBLICATION_DIAGNOSTIC = (
    EVALUATION_ROOT / "host-publication-mutation-diagnostic-20260715.json"
)
HOST_PUBLICATION_DIAGNOSTIC_MARKDOWN = (
    EVALUATION_ROOT / "host-publication-mutation-diagnostic-20260715.md"
)
HOST_PUBLICATION_DIAGNOSTIC_SHA256 = (
    "950d295ff35a7b132fd94a970ae2c8977e274a9da1004b8f329a3bdde4feb21c"
)
HOST_PUBLICATION_DIAGNOSTIC_MARKDOWN_SHA256 = (
    "adb9165e542e3a0b5b8389ce880b2329168c29054453b8f37573b5bfe41cabbc"
)
SOURCE_PROVENANCE_DIAGNOSTIC = (
    EVALUATION_ROOT / "source-provenance-drift-diagnostic-20260715.json"
)
SOURCE_PROVENANCE_DIAGNOSTIC_MARKDOWN = (
    EVALUATION_ROOT / "source-provenance-drift-diagnostic-20260715.md"
)
SOURCE_PROVENANCE_DIAGNOSTIC_SHA256 = (
    "3974bae9d5f83ec464e7e7c136aa98465f47d15521868d443b6653dadef4d2f2"
)
SOURCE_PROVENANCE_DIAGNOSTIC_MARKDOWN_SHA256 = (
    "e67184d21bd924bb5ad3bf46a402e49a1c841ed943b87c78c922cf63f5302dae"
)
CANDIDATE_COPY_DIAGNOSTIC = (
    EVALUATION_ROOT / "candidate-copy-confirmation-failure-diagnostic-20260715.json"
)
CANDIDATE_COPY_DIAGNOSTIC_SHA256 = (
    "e0047fbaab4c2fe55bd21bcefae25c3c3bf0cfbe26f8a22d0a034bcf6adbf136"
)
SKILL_BOOTSTRAP_ISOLATION_DIAGNOSTIC = (
    EVALUATION_ROOT / "skill-bootstrap-isolation-diagnostic-20260715.json"
)
SKILL_BOOTSTRAP_ISOLATION_DIAGNOSTIC_MARKDOWN = (
    EVALUATION_ROOT / "skill-bootstrap-isolation-diagnostic-20260715.md"
)
SKILL_BOOTSTRAP_ISOLATION_DIAGNOSTIC_SHA256 = (
    "cb2d63d1564dc82218ae57fc2e412d2a732d3aa357caeee9b26cac2aaa5daeb5"
)
SKILL_BOOTSTRAP_ISOLATION_DIAGNOSTIC_MARKDOWN_SHA256 = (
    "d9813a63f6bfa53919ae059954366e8efb91d1d0536418d635e8d49830cadf3f"
)
BOOTSTRAP_ISOLATION_TECHNICAL_PREFLIGHT = (
    EVALUATION_ROOT / "bootstrap-isolation-technical-preflight-final.json"
)
BOOTSTRAP_ISOLATION_TECHNICAL_PREFLIGHT_MARKDOWN = (
    EVALUATION_ROOT / "bootstrap-isolation-technical-preflight-final.md"
)
BOOTSTRAP_ISOLATION_TECHNICAL_PREFLIGHT_SHA256 = (
    "2432db96eaf632d55070ccc934417293f32624df42a658ab80ce0d66e97f78dc"
)
BOOTSTRAP_ISOLATION_TECHNICAL_PREFLIGHT_MARKDOWN_SHA256 = (
    "1904cb18575b0062a4a7a6616387adf00139fcb56216f6cba70cbcca73c36554"
)
REVIEWED_BENCHMARK_ROOT = EVALUATION_ROOT / "reviewed-benchmark"
REVIEWED_FROZEN_BENCHMARK = REVIEWED_BENCHMARK_ROOT / "frozen-answer-benchmark.json"
REVIEWED_GROUND_TRUTH = REVIEWED_BENCHMARK_ROOT / "hard-ground-truth.jsonl"
REVIEWED_GROUND_TRUTH_MANIFEST = (
    REVIEWED_BENCHMARK_ROOT / "hard-ground-truth-manifest.json"
)
REVIEWED_BENCHMARK_GENERATOR = (
    EVALUATION_ROOT / "scripts/generate_reviewed_answer_benchmark.py"
)
SKILL_ARENA_CONFIG_GENERATOR = EVALUATION_ROOT / "scripts/generate_skill_arena_config.py"
COVERAGE_REPORT = (
    EVALUATION_ROOT
    / "hard10-coverage-pack-multisignal-diversified-publication-gate-final.json"
)
COVERAGE_REPORT_MARKDOWN = (
    EVALUATION_ROOT
    / "hard10-coverage-pack-multisignal-diversified-publication-gate-final.md"
)
ACCEPTED_COVERAGE_RUNTIME_TREE_SHA256 = (
    "5d09022d024cf31e34fa8a42ad58d71b96dcf1a5c50fe324708874c77c74b4e9"
)
ACCEPTED_COVERAGE_RUNTIME_SHA256 = (
    "a9fed3d8364d35b8460142b13bc48b2041fe5ed6947ea2e6a8da9eba95648c1a"
)
QUESTION_ID = re.compile(r"(?<![a-z0-9])q\d{3}(?:[-_][a-z0-9-]+)?(?![a-z0-9])", re.IGNORECASE)
ABSOLUTE_WINDOWS = re.compile(r"^[A-Za-z]:[\\/]")
CONTRACT_KEYS = {
    "schema_version",
    "scope",
    "frozen_benchmark",
    "ensemble_plan",
    "component_plans",
    "authority",
    "route_bindings",
    "ranking_contract",
    "protocol",
    "hard_gates",
    "objective_reference_observations",
    "population_objectives",
}
SKILL_ARENA_MANIFEST_KEYS = {
    "schema_version",
    "status",
    "reviewed_benchmark",
    "question_count",
    "run_id",
    "config_generator",
    "configs",
    "coverage_path",
    "coverage_sha256",
    "workspace_bundle",
    "profiles",
    "variant",
    "required_host_environment_variables",
    "mcp_runtime",
    "publication_runtime",
    "embedding_runtime",
    "consult_skills",
    "skill_tree_hash_algorithm",
}
HISTORICAL_MCP_ARTIFACTS = {
    "skill_arena_config": SKILL_ARENA_CONFIG,
    "skill_arena_manifest": SKILL_ARENA_MANIFEST,
    "answer_output_report": ANSWER_OUTPUT_REPORT,
    "answer_output_markdown": ANSWER_OUTPUT_MARKDOWN,
    "runtime_attestation_report": MCP_RUNTIME_ATTESTATION,
    "runtime_attestation_markdown": MCP_RUNTIME_ATTESTATION_MARKDOWN,
    "runtime_attestor": (
        EVALUATION_ROOT / "scripts/attest_skill_arena_mcp_runtime.py"
    ),
}
HISTORICAL_MCP_ARTIFACT_SHA256 = {
    "skill_arena_config": (
        "5042a9dae24bdac352ddf1c1f7482a5fe9cf76b0b771ae6d606a514eff5ad4ac"
    ),
    "skill_arena_manifest": (
        "e9c5a337a28384bc9b59d6d583bb624077d76cf1362ffb506f21039385066bdf"
    ),
    "answer_output_report": (
        "6f48c963e8c1f85f9c1355a2d1d796ff8821239c05fb19ad72f78488a6acd5ae"
    ),
    "answer_output_markdown": (
        "2e37ec6602839d89ee27e1eb6fe6b8a8f1a8b3da24dbd5576ecaef08dad10178"
    ),
    "runtime_attestation_report": (
        "8085e666cced0d8b6d5a0b32095c29d836756bf67d1a515412c3ce7d9df5d77d"
    ),
    "runtime_attestation_markdown": (
        "4644215daeb3be1e5435ce31123cc5a5c01d7a620c7931f688474db54eba1a14"
    ),
    "runtime_attestor": (
        "38bcdb15311cace85f1bdc3a3952c6b73f39f7267cfbc5501bb2f42b3eece3a9"
    ),
}
HISTORICAL_ENSEMBLE_SKILL_BINDING = {
    "skill_id": "consult-semantic-okf-ensemble",
    "path": "skills/consult-semantic-okf-ensemble",
    "tree_sha256": "8b5a8200a5049b9613e7b6cd5e6afb63405b3702deee13bc9f4c86603d8f1649",
    "skill_md_sha256": "ec80687beb701f5fc8b6cd13d5ec779cbe5e1f52baffbf3a4a41db4f390717c2",
}
MCP_TRANSPORT_MARKERS = {
    "semantic_okf_bootstrap_skill",
    "semantic_okf_inspect",
    "semantic_okf_coverage_brief",
    "semantic_okf_prepare_answer",
    "semantic_okf_confirm_answer",
}


def exact_keys(value: Any, expected: set[str], label: str) -> dict[str, Any]:
    """Require one closed object."""

    if not isinstance(value, dict):
        raise EvaluationError(f"{label} must be an object")
    actual = set(value)
    if actual != expected:
        raise EvaluationError(
            f"{label} uses a closed schema; missing={sorted(expected - actual)}, "
            f"unknown={sorted(actual - expected)}"
        )
    return value


def bound_file(entry: Any, label: str) -> Path:
    """Resolve and verify one repository-local path/SHA binding."""

    binding = exact_keys(entry, {"path", "sha256"}, label)
    if not isinstance(binding["path"], str) or not isinstance(binding["sha256"], str):
        raise EvaluationError(f"{label} path and sha256 must be strings")
    path = (REPO_ROOT / binding["path"]).resolve(strict=True)
    try:
        path.relative_to(REPO_ROOT.resolve())
    except ValueError as exc:
        raise EvaluationError(f"{label} escapes the repository") from exc
    if sha256(path) != binding["sha256"]:
        raise EvaluationError(f"{label} SHA-256 differs")
    return path


def skill_tree_sha256(root: Path) -> str:
    """Hash stable package files with the algorithm declared by the manifest."""

    rows: list[bytes] = []
    for path in sorted(root.rglob("*")):
        if (
            not path.is_file()
            or path.suffix.lower() in {".pyc", ".pyo"}
            or "__pycache__" in path.parts
        ):
            continue
        relative = path.relative_to(root).as_posix().encode("utf-8")
        rows.append(relative + b"\0" + sha256(path).encode("ascii") + b"\n")
    return hashlib.sha256(b"".join(rows)).hexdigest()


def validate_historical_mcp_evidence_binding() -> dict[str, Any]:
    """Bind retired MCP evaluation evidence without consulting an active runtime."""

    binding = load_json(HISTORICAL_MCP_EVIDENCE)
    exact_keys(
        binding,
        {
            "schema_version",
            "status",
            "source_commit",
            "active_runtime_required",
            "artifacts",
        },
        "historical MCP evaluation binding",
    )
    if (
        binding["schema_version"]
        != "semantic-okf-historical-mcp-evaluation-binding/1.0"
        or binding["status"] != "retired-immutable-evidence"
        or binding["source_commit"] != HISTORICAL_MCP_SOURCE_COMMIT
        or binding["active_runtime_required"] is not False
    ):
        raise EvaluationError("historical MCP evaluation identity differs")
    artifacts = exact_keys(
        binding["artifacts"],
        set(HISTORICAL_MCP_ARTIFACTS),
        "historical MCP evaluation artifacts",
    )
    for name, expected_path in HISTORICAL_MCP_ARTIFACTS.items():
        artifact = exact_keys(
            artifacts[name],
            {"path", "sha256"},
            f"historical MCP evaluation artifact {name}",
        )
        expected_relative = expected_path.relative_to(REPO_ROOT).as_posix()
        expected_sha256 = HISTORICAL_MCP_ARTIFACT_SHA256[name]
        if artifact != {"path": expected_relative, "sha256": expected_sha256}:
            raise EvaluationError(
                f"historical MCP evaluation artifact binding differs: {name}"
            )
        if bound_file(artifact, f"historical MCP evaluation artifact {name}") != (
            expected_path.resolve()
        ):
            raise EvaluationError(
                f"historical MCP evaluation artifact path differs: {name}"
            )
    expected_bytes = (
        json.dumps(binding, indent=2, ensure_ascii=False) + "\n"
    ).encode("utf-8")
    if HISTORICAL_MCP_EVIDENCE.read_bytes() != expected_bytes:
        raise EvaluationError(
            "historical MCP evaluation binding is not canonical JSON"
        )
    return binding


def validate_active_cli_consult_skill(
    skill_root: Path = ACTIVE_CONSULT_SKILL,
) -> dict[str, Any]:
    """Require the current definitive consultation package to be CLI-only."""

    root = skill_root.resolve(strict=True)
    forbidden_directories = ["mcp-runtime", "publication-runtime"]
    present_forbidden = [
        name for name in forbidden_directories if (root / name).exists()
    ]
    if present_forbidden:
        raise EvaluationError(
            "active CLI-only consult package contains retired runtime directories: "
            f"{present_forbidden}"
        )

    required = {
        "skill": root / "SKILL.md",
        "launcher": root / "scripts/run_query.ps1",
        "query_cli": root / "scripts/query_semantic_okf_ensemble.py",
        "finalizer": root / "scripts/_ensemble_snapshot.py",
    }
    missing = sorted(name for name, path in required.items() if not path.is_file())
    if missing:
        raise EvaluationError(
            f"active CLI-only consult package is missing required files: {missing}"
        )

    text_suffixes = {
        ".cmd",
        ".in",
        ".json",
        ".md",
        ".ps1",
        ".py",
        ".txt",
        ".yaml",
        ".yml",
    }
    transport_occurrences: list[str] = []
    for path in sorted(root.rglob("*")):
        if (
            not path.is_file()
            or path.suffix.lower() not in text_suffixes
            or "__pycache__" in path.parts
        ):
            continue
        text = path.read_text(encoding="utf-8")
        markers = sorted(marker for marker in MCP_TRANSPORT_MARKERS if marker in text)
        if markers:
            transport_occurrences.append(
                f"{path.relative_to(root).as_posix()}:{','.join(markers)}"
            )
    if transport_occurrences:
        raise EvaluationError(
            "active CLI-only consult package contains retired semantic_okf transport "
            f"markers: {transport_occurrences}"
        )

    skill_text = required["skill"].read_text(encoding="utf-8")
    required_skill_markers = {
        "CLI-only structured-answer gate",
        "--deep-validation inspect",
        "coverage-brief",
        "finalize-answer --draft -",
        "last successful finalizer JSON verbatim",
    }
    missing_skill_markers = sorted(
        marker for marker in required_skill_markers if marker not in skill_text
    )
    if missing_skill_markers:
        raise EvaluationError(
            "active CLI-only SKILL.md omits required consultation gates: "
            f"{missing_skill_markers}"
        )

    query_text = required["query_cli"].read_text(encoding="utf-8")
    try:
        query_tree = ast.parse(query_text, filename=required["query_cli"].as_posix())
    except SyntaxError as exc:
        raise EvaluationError(f"active consultation query CLI is invalid: {exc}") from exc
    string_literals = {
        node.value
        for node in ast.walk(query_tree)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
    }
    required_cli_literals = {
        "--deep-validation",
        "inspect",
        "search",
        "coverage-brief",
        "finalize-answer",
        "--draft",
        "--question-id",
        "--query",
    }
    missing_cli_literals = sorted(required_cli_literals - string_literals)
    required_query_contract = {
        "draft_payload=sys.stdin.read()",
        'sort_keys=args.command != "finalize-answer"',
    }
    missing_query_contract = sorted(
        marker for marker in required_query_contract if marker not in query_text
    )
    if missing_cli_literals or missing_query_contract:
        raise EvaluationError(
            "active consultation query CLI omits the required finalizer contract: "
            f"literals={missing_cli_literals}, code={missing_query_contract}"
        )

    launcher_text = required["launcher"].read_text(encoding="utf-8")
    required_launcher_markers = {
        "query_semantic_okf_ensemble.py",
        "SEMANTIC_OKF_PYTHON",
        "SEMANTIC_OKF_HF_HUB_CACHE",
        "$PipelineInput | & $python $queryScript @QueryArguments",
        "exit $LASTEXITCODE",
    }
    missing_launcher_markers = sorted(
        marker for marker in required_launcher_markers if marker not in launcher_text
    )
    if missing_launcher_markers or "2>&1" in launcher_text:
        raise EvaluationError(
            "active consultation launcher violates the CLI-only stdout/stderr contract: "
            f"missing={missing_launcher_markers}"
        )

    return {
        "schema_version": "semantic-okf-active-cli-consult-validation/1.0",
        "status": "pass",
        "skill_id": "consult-semantic-okf-ensemble",
        "path": root.relative_to(REPO_ROOT.resolve()).as_posix(),
        "tree_sha256": skill_tree_sha256(root),
        "retired_runtime_directories_present": [],
        "retired_transport_marker_count": 0,
        "commands": [
            "inspect",
            "search",
            "coverage-brief",
            "finalize-answer",
        ],
    }


def validate_reviewed_benchmark() -> dict[str, Any]:
    """Rebuild and validate the immutable reviewed hard-answer benchmark."""

    generator = module_from_path(
        "semantic_okf_ensemble_checked_reviewed_benchmark_generator",
        REVIEWED_BENCHMARK_GENERATOR,
    )
    try:
        first = generator.build_outputs(REPO_ROOT)
        second = generator.build_outputs(REPO_ROOT)
    except (OSError, UnicodeError, ValueError, KeyError, TypeError, RuntimeError) as exc:
        raise EvaluationError(f"reviewed benchmark regeneration failed: {exc}") from exc
    expected_names = {
        "hard-ground-truth.jsonl",
        "hard-questions.jsonl",
        "retrieval-questions.jsonl",
        "hard-ground-truth-manifest.json",
        "frozen-answer-benchmark.json",
    }
    if set(first) != expected_names or first != second:
        raise EvaluationError("reviewed benchmark generation is incomplete or nondeterministic")
    for name, payload in first.items():
        checked = REVIEWED_BENCHMARK_ROOT / name
        if not checked.is_file() or checked.read_bytes() != payload:
            raise EvaluationError(f"reviewed benchmark checked output differs: {name}")

    manifest = load_json(REVIEWED_FROZEN_BENCHMARK)
    exact_keys(
        manifest,
        {
            "schema_version",
            "benchmark_id",
            "status",
            "frozen_on",
            "mutation_policy",
            "parent_frozen_benchmark",
            "amendments",
            "generator",
            "cohorts",
            "invariants",
            "audit_summary",
        },
        "reviewed frozen answer benchmark",
    )
    if (
        manifest["schema_version"] != "semantic-okf-frozen-answer-benchmark/1.0"
        or manifest["benchmark_id"]
        != "semantic-okf-ensemble-reviewed-answer-40-plus-hard10-v1"
        or manifest["status"] != "frozen"
    ):
        raise EvaluationError("reviewed frozen answer benchmark identity differs")
    ground_truth = [
        json.loads(line)
        for line in REVIEWED_GROUND_TRUTH.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    hard = exact_keys(
        manifest.get("cohorts", {}).get("hard_ground_truth"),
        {"path", "sha256", "count", "ordered_ids"},
        "reviewed hard-ground-truth cohort",
    )
    if hard != {
        "path": REVIEWED_GROUND_TRUTH.relative_to(REPO_ROOT).as_posix(),
        "sha256": sha256(REVIEWED_GROUND_TRUTH),
        "count": len(ground_truth),
        "ordered_ids": [row.get("id") for row in ground_truth],
    }:
        raise EvaluationError("reviewed hard-ground-truth cohort binding differs")
    if manifest["audit_summary"] != {
        "questions": 10,
        "atomic_answer_claims": 44,
        "important_negatives": 13,
        "parent_expected_id_links": 72,
        "appended_atomic_option_links": 22,
        "appended_negative_option_links": 19,
        "reviewed_expected_id_links": 113,
        "parent_unique_expected_claim_ids": 42,
        "added_unique_claim_ids": 26,
        "reviewed_unique_expected_claim_ids": 68,
        "parent_authoritative_evidence_objects": 44,
        "added_authoritative_evidence_objects": 27,
        "reviewed_authoritative_evidence_objects": 71,
        "rejected_close_alternatives": 38,
    }:
        raise EvaluationError("reviewed benchmark audit summary differs")
    return {
        "manifest": manifest,
        "ground_truth": ground_truth,
        "manifest_sha256": sha256(REVIEWED_FROZEN_BENCHMARK),
        "ground_truth_sha256": sha256(REVIEWED_GROUND_TRUTH),
        "ground_truth_manifest_sha256": sha256(REVIEWED_GROUND_TRUTH_MANIFEST),
    }


def validate_generated_skill_arena_artifacts() -> dict[str, str]:
    """Rebuild the config twice and require exact checked bytes without writing."""

    generator = module_from_path(
        "semantic_okf_ensemble_checked_skill_arena_generator",
        SKILL_ARENA_CONFIG_GENERATOR,
    )
    try:
        first = generator.build_artifacts(REPO_ROOT)
        second = generator.build_artifacts(REPO_ROOT)
    except (OSError, UnicodeError, ValueError, KeyError, TypeError, RuntimeError) as exc:
        raise EvaluationError(f"Skill Arena config regeneration failed: {exc}") from exc
    if list(first) != ["ensemble-hard10.yaml", "prompt-coverage.json"] or first != second:
        raise EvaluationError("Skill Arena config generation is incomplete or nondeterministic")
    result: dict[str, str] = {}
    for name, payload in first.items():
        checked = EVALUATION_ROOT / "skill-arena" / name
        if not checked.is_file() or checked.read_bytes() != payload:
            raise EvaluationError(f"Skill Arena generated output differs: {name}")
        result[name] = hashlib.sha256(payload).hexdigest()
    return result


def validate_skill_arena_manifest() -> dict[str, Any]:
    """Validate the retired Skill Arena experiment as immutable historical evidence."""

    if sha256(SKILL_ARENA_MANIFEST) != HISTORICAL_MCP_ARTIFACT_SHA256[
        "skill_arena_manifest"
    ]:
        raise EvaluationError("historical Skill Arena manifest SHA-256 differs")
    if sha256(SKILL_ARENA_CONFIG) != HISTORICAL_MCP_ARTIFACT_SHA256[
        "skill_arena_config"
    ]:
        raise EvaluationError("historical Skill Arena config SHA-256 differs")
    manifest = load_json(SKILL_ARENA_MANIFEST)
    exact_keys(manifest, SKILL_ARENA_MANIFEST_KEYS, "Skill Arena config manifest")
    if manifest["schema_version"] != "semantic-okf-hard-answer-configs/2.2":
        raise EvaluationError("Skill Arena config manifest schema_version differs")
    if manifest["status"] != "validated-dry-run":
        raise EvaluationError("Skill Arena config manifest status differs")

    reviewed = validate_reviewed_benchmark()
    truth = reviewed["ground_truth"]
    truth_canonical = hashlib.sha256(canonical_json(truth).encode("utf-8")).hexdigest()
    benchmark = exact_keys(
        manifest["reviewed_benchmark"],
        {
            "benchmark_id",
            "frozen_manifest",
            "ground_truth",
            "ground_truth_manifest",
        },
        "Skill Arena reviewed benchmark",
    )
    if benchmark["benchmark_id"] != reviewed["manifest"]["benchmark_id"]:
        raise EvaluationError("Skill Arena reviewed benchmark identity differs")
    frozen_binding = exact_keys(
        benchmark["frozen_manifest"],
        {"path", "sha256"},
        "Skill Arena reviewed frozen manifest",
    )
    if bound_file(frozen_binding, "Skill Arena reviewed frozen manifest") != REVIEWED_FROZEN_BENCHMARK.resolve():
        raise EvaluationError("Skill Arena reviewed frozen manifest path differs")
    truth_binding = exact_keys(
        benchmark["ground_truth"],
        {"path", "sha256", "canonical_sha256", "schema_version"},
        "Skill Arena reviewed ground truth",
    )
    if bound_file(
        {"path": truth_binding["path"], "sha256": truth_binding["sha256"]},
        "Skill Arena reviewed ground truth",
    ) != REVIEWED_GROUND_TRUTH.resolve():
        raise EvaluationError("Skill Arena reviewed ground-truth path differs")
    if (
        truth_binding["canonical_sha256"] != truth_canonical
        or truth_binding["schema_version"] != "semantic-okf-hard-ground-truth/1.0"
    ):
        raise EvaluationError("Skill Arena reviewed ground-truth contract differs")
    truth_manifest_binding = exact_keys(
        benchmark["ground_truth_manifest"],
        {"path", "sha256"},
        "Skill Arena reviewed ground-truth manifest",
    )
    if bound_file(
        truth_manifest_binding,
        "Skill Arena reviewed ground-truth manifest",
    ) != REVIEWED_GROUND_TRUTH_MANIFEST.resolve():
        raise EvaluationError("Skill Arena reviewed ground-truth manifest path differs")
    if manifest["question_count"] != len(truth) or manifest["run_id"] != "20260715-ensemble-final-03":
        raise EvaluationError("Skill Arena question count or run ID differs")

    generator_binding = exact_keys(
        manifest["config_generator"],
        {"path", "sha256", "deterministic", "check_mode"},
        "Skill Arena config generator",
    )
    # This manifest records the generator bytes used for the retired experiment.
    # The active generator is replayed immediately below against checked-in
    # publication evidence, so its current bytes need not equal that historical
    # digest after a maintenance change.
    if {
        "path": generator_binding["path"],
        "sha256": generator_binding["sha256"],
    } != {
        "path": SKILL_ARENA_CONFIG_GENERATOR.relative_to(REPO_ROOT).as_posix(),
        "sha256": "c77d0717ef57b2c3ac0fe2bd77a9e238f79a4e764d4d571167b3d899b3c30857",
    }:
        raise EvaluationError("historical Skill Arena config-generator binding differs")
    if generator_binding["deterministic"] is not True or generator_binding["check_mode"] is not True:
        raise EvaluationError("Skill Arena config generator gates differ")
    generated = validate_generated_skill_arena_artifacts()

    configs = manifest["configs"]
    if not isinstance(configs, list) or len(configs) != 1:
        raise EvaluationError("Skill Arena manifest must bind exactly one causal config")
    config = exact_keys(configs[0], {"method", "path", "sha256"}, "Skill Arena config")
    if config["method"] != "ensemble_three_arm":
        raise EvaluationError("Skill Arena config method differs")
    config_path = bound_file(
        {"path": config["path"], "sha256": config["sha256"]},
        "Skill Arena config",
    )
    if config_path != (EVALUATION_ROOT / "skill-arena/ensemble-hard10.yaml").resolve():
        raise EvaluationError("Skill Arena manifest binds a different config")
    if config["sha256"] != generated["ensemble-hard10.yaml"]:
        raise EvaluationError("Skill Arena config differs from deterministic generation")
    compare_payload = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    variants = (
        compare_payload.get("comparison", {}).get("variants")
        if isinstance(compare_payload, dict)
        else None
    )
    if not isinstance(variants, list) or len(variants) != 1:
        raise EvaluationError("Skill Arena config must declare exactly one variant")
    configured_variant = variants[0]
    configured_agent = (
        configured_variant.get("agent") if isinstance(configured_variant, dict) else None
    )
    if not isinstance(configured_agent, dict):
        raise EvaluationError("Skill Arena config variant has no agent contract")
    if configured_variant.get("id") != "codex-luna-tools" or {
        "adapter": configured_agent.get("adapter"),
        "commandPath": configured_agent.get("commandPath"),
        "model": configured_agent.get("model"),
        "sandboxMode": configured_agent.get("sandboxMode"),
        "approvalPolicy": configured_agent.get("approvalPolicy"),
        "webSearchEnabled": configured_agent.get("webSearchEnabled"),
        "networkAccessEnabled": configured_agent.get("networkAccessEnabled"),
        "envPassthrough": configured_agent.get("envPassthrough"),
        "config": configured_agent.get("config"),
    } != {
        "adapter": "codex",
        "commandPath": "publication-runtime\\run_codex.cmd",
        "model": "gpt-5.6-luna",
        "sandboxMode": "workspace-write",
        "approvalPolicy": "never",
        "webSearchEnabled": False,
        "networkAccessEnabled": False,
        "envPassthrough": [
            "SEMANTIC_OKF_PYTHON",
            "SEMANTIC_OKF_HF_HUB_CACHE",
        ],
        "config": {
            "mcp_servers": {
                "semantic_okf": {
                    "command": "cmd.exe",
                    "args": ["/d", "/c", "mcp-runtime\\run_server.cmd"],
                    "env_vars": [
                        "SKILL_ARENA_ALLOWED_SKILLS",
                        "CODEX_HOME",
                        "SEMANTIC_OKF_BUNDLE",
                        "SEMANTIC_OKF_PYTHON",
                        "SEMANTIC_OKF_HF_HUB_CACHE",
                        "HF_HUB_OFFLINE",
                        "TRANSFORMERS_OFFLINE",
                        "PYTHONDONTWRITEBYTECODE",
                    ],
                    "enabled_tools": [
                        "semantic_okf_bootstrap_skill",
                        "semantic_okf_inspect",
                        "semantic_okf_coverage_brief",
                        "semantic_okf_prepare_answer",
                        "semantic_okf_confirm_answer",
                    ],
                    "startup_timeout_sec": 60,
                    "tool_timeout_sec": 600,
                }
            }
        },
    }:
        raise EvaluationError("Skill Arena config agent runtime contract differs")

    workspace_sources = (
        compare_payload.get("workspace", {}).get("sources")
        if isinstance(compare_payload, dict)
        else None
    )
    if workspace_sources != [
        {
            "id": "semantic-okf-ensemble-final-bundle",
            "type": "local-path",
            "path": (
                "evaluations/semantic-okf-ensemble/results/runs/"
                "20260715-ensemble-final-03/workspace-a/knowledge"
            ),
            "target": "/knowledge",
        },
        {
            "id": "semantic-okf-profile-gated-mcp-runtime",
            "type": "local-path",
            "path": "skills/consult-semantic-okf-ensemble/mcp-runtime",
            "target": "/mcp-runtime",
        },
        {
            "id": "semantic-okf-confirmed-output-publication-runtime",
            "type": "local-path",
            "path": "skills/consult-semantic-okf-ensemble/publication-runtime",
            "target": "/publication-runtime",
        },
    ]:
        raise EvaluationError("Skill Arena workspace source contract differs")

    coverage_path = bound_file(
        {"path": manifest["coverage_path"], "sha256": manifest["coverage_sha256"]},
        "Skill Arena prompt coverage",
    )
    if manifest["coverage_sha256"] != generated["prompt-coverage.json"]:
        raise EvaluationError("Skill Arena prompt coverage differs from deterministic generation")
    coverage = load_json(coverage_path)
    cases = coverage.get("cases")
    if not isinstance(cases, list) or [case.get("promptId") for case in cases] != [row["id"] for row in truth]:
        raise EvaluationError("Skill Arena prompt coverage differs from the frozen hard ten")

    build = load_json(BUILD_VALIDATION)
    workspace = exact_keys(
        manifest["workspace_bundle"],
        {"path", "target", "ensemble_index_sha256"},
        "Skill Arena workspace bundle",
    )
    if workspace["path"] != (
        "evaluations/semantic-okf-ensemble/results/runs/"
        "20260715-ensemble-final-03/workspace-a/knowledge"
    ) or workspace["target"] != "/knowledge":
        raise EvaluationError("Skill Arena workspace bundle path or target differs")
    if workspace["ensemble_index_sha256"] != build["publication"]["ensemble_index_sha256"]:
        raise EvaluationError("Skill Arena workspace ensemble-index identity differs")

    if manifest["profiles"] != [
        "knowledge-only-control",
        "adaptive-consult-control",
        "ensemble-consult-treatment",
    ]:
        raise EvaluationError("Skill Arena profile identities differ")
    if manifest["variant"] != {
        "id": "codex-luna-tools",
        "adapter": "codex",
        "command_path": "publication-runtime\\run_codex.cmd",
        "model": "gpt-5.6-luna",
        "sandbox_mode": "workspace-write",
        "web_search_enabled": False,
        "network_access_enabled": False,
        "requests_per_cell": 3,
        "maximum_concurrency": 2,
        "no_cache": True,
    }:
        raise EvaluationError("Skill Arena variant contract differs")
    if manifest["required_host_environment_variables"] != [
        "SEMANTIC_OKF_PYTHON",
        "SEMANTIC_OKF_HF_HUB_CACHE",
    ]:
        raise EvaluationError("Skill Arena required host runtime variables differ")
    mcp = exact_keys(
        manifest["mcp_runtime"],
        {
            "path", "tree_sha256", "server_sha256", "launcher_sha256",
            "server_version", "allowed_skill_id", "controls_expose_tools",
            "bootstrap_tool", "bootstrap_schema", "bootstrap_key_order",
            "bootstrap_skill_id", "bootstrap_skill_sha256",
            "bootstrap_skill_byte_count", "bootstrap_exactly_once",
            "bootstrap_first", "bootstrap_failure_poison",
            "protocol_tools", "mode_argument", "minimum_successful_prepares",
            "prepared_answer_schema", "prepared_answer_key_order",
            "candidate_digest_binding", "confirmation_argument",
            "confirmation_argument_pattern", "confirmation_receipt_schema",
            "confirmation_receipt_key_order", "confirmation_one_use",
            "confirmation_terminal", "confirmation_idempotent",
            "failed_protocol_call_publishes",
            "failed_protocol_call_clears_transaction",
            "failure_requires_fresh_prepare",
            "final_transaction_must_be_clean",
            "coverage_priority_order", "priority_order_session_bound", "tools",
        },
        "Skill Arena MCP runtime",
    )
    if mcp != {
        "path": "skills/consult-semantic-okf-ensemble/mcp-runtime",
        "tree_sha256": "a1d75372355b9d44f1fa8fa4f29585cd1cb8744bcf7fa0e5ce36b0f9706d51ee",
        "server_sha256": "bef33f807ad339563a076402edf96b65c9cd66f81eb0af3484a49a8945d940c2",
        "launcher_sha256": "d2527a45a76e1eab182acff7c545ab8092a3301cdcdb81f3990c0423533289a2",
        "server_version": "1.5.0",
        "allowed_skill_id": "consult-semantic-okf-ensemble",
        "controls_expose_tools": False,
        "bootstrap_tool": "semantic_okf_bootstrap_skill",
        "bootstrap_schema": "semantic-okf-skill-bootstrap/1.0",
        "bootstrap_key_order": [
            "schema",
            "skill_id",
            "skill_sha256",
            "byte_count",
            "skill_markdown",
        ],
        "bootstrap_skill_id": "consult-semantic-okf-ensemble",
        "bootstrap_skill_sha256": (
            "ec80687beb701f5fc8b6cd13d5ec779cbe5e1f52baffbf3a4a41db4f390717c2"
        ),
        "bootstrap_skill_byte_count": 15699,
        "bootstrap_exactly_once": True,
        "bootstrap_first": True,
        "bootstrap_failure_poison": True,
        "protocol_tools": [
            "semantic_okf_prepare_answer",
            "semantic_okf_confirm_answer",
        ],
        "mode_argument": False,
        "minimum_successful_prepares": 1,
        "prepared_answer_schema": "semantic-okf-prepared-answer/1.0",
        "prepared_answer_key_order": [
            "schema",
            "candidate_json",
            "response_sha256",
            "byte_count",
        ],
        "candidate_digest_binding": "sha256-lowercase-hex-of-utf8-candidate-json",
        "confirmation_argument": "response_sha256",
        "confirmation_argument_pattern": "^[0-9a-f]{64}$",
        "confirmation_receipt_schema": "semantic-okf-answer-confirmation-receipt/1.0",
        "confirmation_receipt_key_order": [
            "schema",
            "status",
            "response_sha256",
            "byte_count",
        ],
        "confirmation_one_use": True,
        "confirmation_terminal": True,
        "confirmation_idempotent": False,
        "failed_protocol_call_publishes": False,
        "failed_protocol_call_clears_transaction": True,
        "failure_requires_fresh_prepare": True,
        "final_transaction_must_be_clean": True,
        "coverage_priority_order": "persisted-idf-facet-consensus-priority-v1",
        "priority_order_session_bound": True,
        "tools": [
            "semantic_okf_bootstrap_skill",
            "semantic_okf_inspect",
            "semantic_okf_coverage_brief",
            "semantic_okf_prepare_answer",
            "semantic_okf_confirm_answer",
        ],
    }:
        raise EvaluationError("historical Skill Arena MCP runtime contract differs")
    publication = exact_keys(
        manifest["publication_runtime"],
        {
            "path",
            "tree_sha256",
            "script_sha256",
            "launcher_sha256",
            "command_path",
            "protocol_tools",
            "mode_argument",
            "prepared_answer_schema",
            "prepared_answer_key_order",
            "candidate_digest_binding",
            "confirmation_argument",
            "confirmation_argument_pattern",
            "confirmation_receipt_schema",
            "confirmation_receipt_key_order",
            "confirmation_terminal",
            "confirmation_idempotent",
            "failed_protocol_call_publishes",
            "failed_protocol_call_clears_transaction",
            "failure_requires_fresh_prepare",
            "final_transaction_must_be_clean",
            "published_bytes_source",
            "confirmed_bytes_atomic_replace",
            "treatment_skill_id",
            "treatment_shell_tool_disabled",
            "shell_disable_arguments",
            "shell_isolation_receipt_schema",
            "shell_isolation_receipt_key_order",
            "controls_shell_policy_unchanged",
            "controls_transparent",
        },
        "Skill Arena publication runtime",
    )
    if publication != {
        "path": "skills/consult-semantic-okf-ensemble/publication-runtime",
        "tree_sha256": "b8a6e9117df4bd9b7608547eaef4ce55609e01c02cb69a263c60c6e78b0624fc",
        "script_sha256": "6db622318acba2301b272504e6687bb34055d2704a0ce4f1c7425ee9bb8570b1",
        "launcher_sha256": "9ae819d2814490a1f9c990aae2617a9bc2873f370d7b3c8cbaf52d3bb6b5f443",
        "command_path": "publication-runtime\\run_codex.cmd",
        "protocol_tools": [
            "semantic_okf_prepare_answer",
            "semantic_okf_confirm_answer",
        ],
        "mode_argument": False,
        "prepared_answer_schema": "semantic-okf-prepared-answer/1.0",
        "prepared_answer_key_order": [
            "schema",
            "candidate_json",
            "response_sha256",
            "byte_count",
        ],
        "candidate_digest_binding": "sha256-lowercase-hex-of-utf8-candidate-json",
        "confirmation_argument": "response_sha256",
        "confirmation_argument_pattern": "^[0-9a-f]{64}$",
        "confirmation_receipt_schema": (
            "semantic-okf-answer-confirmation-receipt/1.0"
        ),
        "confirmation_receipt_key_order": [
            "schema",
            "status",
            "response_sha256",
            "byte_count",
        ],
        "confirmation_terminal": True,
        "confirmation_idempotent": False,
        "failed_protocol_call_publishes": False,
        "failed_protocol_call_clears_transaction": True,
        "failure_requires_fresh_prepare": True,
        "final_transaction_must_be_clean": True,
        "published_bytes_source": "prepared-envelope-candidate-json-bytes",
        "confirmed_bytes_atomic_replace": True,
        "treatment_skill_id": "consult-semantic-okf-ensemble",
        "treatment_shell_tool_disabled": True,
        "shell_disable_arguments": ["--disable", "shell_tool"],
        "shell_isolation_receipt_schema": (
            "semantic-okf-shell-isolation-receipt/1.0"
        ),
        "shell_isolation_receipt_key_order": [
            "schema",
            "skill_id",
            "shell_tool_disabled",
        ],
        "controls_shell_policy_unchanged": True,
        "controls_transparent": True,
    }:
        raise EvaluationError("historical Skill Arena publication runtime contract differs")
    runtime = exact_keys(
        manifest["embedding_runtime"],
        {
            "environment_variable",
            "model_cache_environment_variable",
            "model_id",
            "revision",
            "python_version",
            "python_executable_sha256",
            "sentence_transformers_version",
            "huggingface_hub_version",
            "offline",
            "build_lock_sha256",
        },
        "Skill Arena embedding runtime",
    )
    if runtime != {
        "environment_variable": "SEMANTIC_OKF_PYTHON",
        "model_cache_environment_variable": "SEMANTIC_OKF_HF_HUB_CACHE",
        "model_id": "sentence-transformers/all-MiniLM-L6-v2",
        "revision": "1110a243fdf4706b3f48f1d95db1a4f5529b4d41",
        "python_version": build["runtime"]["python"],
        "python_executable_sha256": "b2e61d457cf26a449ac044769222720af5fd73d6f197bfa67591d4119001d0ea",
        "sentence_transformers_version": "5.6.0",
        "huggingface_hub_version": "1.23.0",
        "offline": True,
        "build_lock_sha256": build["inputs"]["locks"]["sentence_transformers_sha256"],
    }:
        raise EvaluationError("Skill Arena embedding runtime contract differs")

    skill_entries = manifest["consult_skills"]
    if not isinstance(skill_entries, list) or len(skill_entries) != 2:
        raise EvaluationError("Skill Arena consult-skill set differs")
    expected_skill_bindings = [
        {
            "skill_id": "consult-semantic-okf-adaptive",
            "path": "skills/consult-semantic-okf-adaptive",
            "tree_sha256": "731318f38a09113b57792c6e3cd93801eedb08a1cb0e7ef9cf72e19e4fe9cdac",
            "skill_md_sha256": "c1bbbca6d96d9ce514de39b79db60625ed162d0ed33c396e3ce6a25e26a96fa5",
        },
        HISTORICAL_ENSEMBLE_SKILL_BINDING,
    ]
    for entry, expected in zip(skill_entries, expected_skill_bindings, strict=True):
        binding = exact_keys(
            entry,
            {"skill_id", "path", "tree_sha256", "skill_md_sha256"},
            f"historical Skill Arena skill {expected['skill_id']}",
        )
        if binding != expected:
            raise EvaluationError(
                f"historical Skill Arena skill binding differs: {expected['skill_id']}"
            )
    if manifest["skill_tree_hash_algorithm"] != (
        "SHA-256 over sorted package-relative-path NUL file-SHA-256 newline rows; "
        "generated __pycache__ and .pyc files excluded"
    ):
        raise EvaluationError("Skill Arena skill-tree hash algorithm differs")
    return manifest


def validate_accepted_coverage_report(plan: dict[str, Any]) -> dict[str, Any]:
    """Require the accepted multisignal report and all local provenance bindings."""

    if not COVERAGE_REPORT.is_file() or not COVERAGE_REPORT_MARKDOWN.is_file():
        raise EvaluationError("accepted diversified coverage report or Markdown is missing")
    evaluator_path = EVALUATION_ROOT / "scripts/evaluate_hard10_coverage_pack.py"
    evaluator = module_from_path(
        "semantic_okf_ensemble_checked_coverage_evaluator",
        evaluator_path,
    )
    report = load_json(COVERAGE_REPORT)
    evaluator.validate_report(report)
    if COVERAGE_REPORT.read_bytes() != (
        json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    ).encode("utf-8"):
        raise EvaluationError("accepted diversified coverage JSON is not canonical")
    if COVERAGE_REPORT_MARKDOWN.read_text(encoding="utf-8") != evaluator.render_markdown(report):
        raise EvaluationError("accepted diversified coverage Markdown differs from the report")
    if (
        report["status"] != "pass"
        or report["candidate"]
        != "definitive-ensemble-quality-paper-diversified-publication-gate-v1"
    ):
        raise EvaluationError("accepted diversified coverage status or candidate differs")
    reviewed = validate_reviewed_benchmark()
    if report["benchmark"] != {
        "id": reviewed["manifest"]["benchmark_id"],
        "manifest_sha256": reviewed["manifest_sha256"],
        "hard_questions": 10,
    }:
        raise EvaluationError("accepted diversified coverage benchmark differs")

    inputs = report["inputs"]
    build = load_json(BUILD_VALIDATION)
    manual = load_json(MANUAL_VERIFICATION)
    expected_bundle = (
        "evaluations/semantic-okf-ensemble/results/runs/"
        "20260715-ensemble-final-03/workspace-a/knowledge"
    )
    if inputs["bundle"] != expected_bundle:
        raise EvaluationError("accepted multisignal coverage bundle path differs")
    if inputs["bundle_tree_sha256"] != manual["bundle"]["recursive_sha256_before"]:
        raise EvaluationError("accepted multisignal coverage bundle tree differs")
    if inputs["ensemble_index_sha256"] != build["publication"]["ensemble_index_sha256"]:
        raise EvaluationError("accepted multisignal coverage ensemble index differs")
    if inputs["core_tree_sha256"] != build["authoritative_core"]["tree_sha256"]:
        raise EvaluationError("accepted multisignal coverage core tree differs")
    if inputs["plan"] != "evaluations/semantic-okf-ensemble/ensemble-plan.json":
        raise EvaluationError("accepted multisignal coverage plan path differs")
    if inputs["plan_sha256"] != sha256(ENSEMBLE_PLAN):
        raise EvaluationError("accepted multisignal coverage plan file SHA-256 differs")
    canonical_plan = hashlib.sha256(canonical_json(plan).encode("utf-8")).hexdigest()
    if inputs["plan_canonical_sha256"] != canonical_plan:
        raise EvaluationError("accepted multisignal coverage canonical plan SHA-256 differs")

    runtime_path = REPO_ROOT / inputs["runtime"]
    skill_root = REPO_ROOT / "skills/consult-semantic-okf-ensemble"
    if runtime_path != skill_root / "scripts/_ensemble_snapshot.py":
        raise EvaluationError("accepted multisignal coverage runtime path differs")
    # This report is immutable historical evidence. The current consultation runtime
    # is hash-bound separately by the Skill Arena manifest and may legitimately evolve
    # after the retrieval experiment (for example, to tighten publication semantics).
    if inputs["runtime_sha256"] != ACCEPTED_COVERAGE_RUNTIME_SHA256:
        raise EvaluationError("accepted diversified coverage runtime SHA-256 differs")
    if inputs["runtime_tree_sha256"] != ACCEPTED_COVERAGE_RUNTIME_TREE_SHA256:
        raise EvaluationError("accepted diversified coverage runtime tree SHA-256 differs")
    if inputs["evaluator"] != "evaluations/semantic-okf-ensemble/scripts/evaluate_hard10_coverage_pack.py":
        raise EvaluationError("accepted multisignal coverage evaluator path differs")
    if inputs["evaluator_sha256"] != sha256(evaluator_path):
        raise EvaluationError("accepted multisignal coverage evaluator SHA-256 differs")
    inventory_path = REPO_ROOT / inputs["inventory"]
    if inputs["inventory"] != "evaluations/semantic-okf-embeddings/input-inventory.json":
        raise EvaluationError("accepted multisignal coverage inventory path differs")
    if inputs["inventory_sha256"] != sha256(inventory_path):
        raise EvaluationError("accepted multisignal coverage inventory SHA-256 differs")
    if inputs["ground_truth_sha256"] != reviewed["ground_truth_sha256"]:
        raise EvaluationError("accepted diversified coverage ground-truth SHA-256 differs")

    if any(value is not True for value in report["hard_gates"].values()):
        raise EvaluationError("accepted multisignal coverage has a failed hard gate")
    counts = report["metrics"]["group_counts"]
    if counts["answer_claims"] != {
        "total": 44,
        "adaptive_covered": 39,
        "graph_covered": 24,
        "embedding_covered": 39,
        "union_covered": 44,
    }:
        raise EvaluationError("accepted diversified answer-group counts differ")
    if counts["important_negatives"] != {
        "total": 13,
        "adaptive_covered": 13,
        "graph_covered": 11,
        "embedding_covered": 13,
        "union_covered": 13,
    }:
        raise EvaluationError("accepted diversified negative-group counts differ")
    if report["metrics"]["evidence_validation"] != {
        "unique_returned_bindings": 713,
        "valid_unique_bindings": 713,
        "ratio": 1.0,
    }:
        raise EvaluationError("accepted multisignal evidence-validity counts differ")
    truth = reviewed["ground_truth"]
    if [row["id"] for row in report["questions"]] != [row["id"] for row in truth]:
        raise EvaluationError("accepted diversified question identities differ")
    return report


def validate_builder_plan() -> dict[str, Any]:
    """Use the actual standalone builder validator for the executable plan."""

    scripts = REPO_ROOT / "skills/build-semantic-okf-ensemble/scripts"
    if str(scripts) not in sys.path:
        sys.path.insert(0, str(scripts))
    try:
        from _ensemble_build import EnsembleError, load_plan
    except ImportError as exc:
        raise EvaluationError(f"cannot import the ensemble builder validator: {exc}") from exc
    try:
        return load_plan(ENSEMBLE_PLAN)
    except EnsembleError as exc:
        raise EvaluationError(f"ensemble builder rejected the plan: {exc}") from exc


def validate_policy(plan: dict[str, Any]) -> None:
    """Require the reviewed policy values used by the evaluation design."""

    policies = plan["policies"]
    expected = {
        "default": "quality",
        "quality": {
            "routes": ["adaptive", "graph_fusion", "bm25", "embedding_hybrid"],
            "weights": [4, 1, 5, 1],
            "rrf_k": 7,
            "protected_route": "adaptive",
            "promotion": {
                "route": "graph_lexical",
                "confirmation_routes": ["adaptive", "graph_lexical", "graph_fusion", "bm25", "embedding_hybrid"],
                "confirmation_depth": 3,
                "minimum_confirmations": 3,
                "maximum_protected_rank": 10,
            },
        },
        "fast": {
            "routes": ["adaptive", "graph_lexical"],
            "weights": [4, 1],
            "rrf_k": 5,
            "protected_route": "adaptive",
            "promotion": {
                "route": "graph_lexical",
                "confirmation_routes": ["adaptive", "graph_lexical"],
                "confirmation_depth": 3,
                "minimum_confirmations": 2,
                "maximum_protected_rank": 3,
            },
        },
        "robust": {
            "routes": ["adaptive"],
            "weights": [1],
            "rrf_k": 0,
            "protected_route": "adaptive",
            "promotion": {
                "route": "adaptive",
                "confirmation_routes": ["adaptive"],
                "confirmation_depth": 1,
                "minimum_confirmations": 1,
                "maximum_protected_rank": 1,
            },
        },
    }
    if policies != expected:
        raise EvaluationError("ensemble policies differ from the reviewed evaluation design")
    if plan["quality_gates"]["maximum_graph_claims_total"] != 80:
        raise EvaluationError("maximum_graph_claims_total must preserve the observed graph union")
    if plan["quality_gates"].get("maximum_embedding_claims_per_facet") != 20:
        raise EvaluationError("maximum_embedding_claims_per_facet must equal the reviewed semantic gate")
    if plan["quality_gates"].get("maximum_embedding_claims_total") != 240:
        raise EvaluationError("maximum_embedding_claims_total must equal the reviewed semantic gate")
    if plan["quality_gates"].get("reviewed_embedding_claims_only") is not True:
        raise EvaluationError("reviewed_embedding_claims_only must remain true")


def validate_contract(plan: dict[str, Any]) -> dict[str, Any]:
    """Validate evaluation-only bindings and component equality."""

    contract = load_json(CONTRACT)
    exact_keys(contract, CONTRACT_KEYS, "evaluation contract")
    if contract["schema_version"] != "semantic-okf-ensemble-evaluation-contract/1.0":
        raise EvaluationError("evaluation contract schema_version differs")
    if contract["scope"] != {
        "purpose": "Evaluation-only bindings, gates, and scoring rules for the standalone Semantic OKF ensemble",
        "builder_input": False,
        "contains_results": False,
    }:
        raise EvaluationError("evaluation contract scope differs")
    frozen = contract["frozen_benchmark"]
    if frozen.get("sha256") != validate_frozen()["manifest_sha256"] or frozen.get("mutation_policy") != "read-only":
        raise EvaluationError("evaluation contract frozen benchmark binding differs")
    if bound_file(contract["ensemble_plan"], "contract ensemble plan") != ENSEMBLE_PLAN.resolve():
        raise EvaluationError("evaluation contract binds a different ensemble plan")

    components = exact_keys(
        contract["component_plans"], {"adaptive", "entity_graph", "embedding"}, "component plans"
    )
    for key in ("adaptive", "entity_graph", "embedding"):
        source = load_json(bound_file(components[key], f"component plan {key}"))
        if plan[key] != source:
            raise EvaluationError(f"nested {key} plan differs from its source")
    if contract["route_bindings"] != {
        "adaptive": {"component": "adaptive", "route": "adaptive_fusion"},
        "graph_fusion": {"component": "entity_graph", "route": "entity_graph_fusion"},
        "graph_lexical": {"component": "entity_graph", "route": "entity_graph_lexical"},
        "bm25": {"component": "adaptive", "route": "classical_bm25"},
        "embedding_hybrid": {"component": "embedding", "route": "hybrid"},
    }:
        raise EvaluationError("evaluation route bindings differ")
    return contract


def validate_no_candidate_leakage(generation: dict[str, Any]) -> None:
    """Reject benchmark question IDs from candidate hypotheses and mutations."""

    for candidate in generation["candidates"]:
        encoded = json.dumps(candidate, sort_keys=True)
        match = QUESTION_ID.search(encoded)
        if match:
            raise EvaluationError(
                f"candidate {candidate['candidate_id']} leaks evaluation question ID {match.group(0)}"
            )


def validate_checked_reports() -> None:
    """Require the compact checked reports to retain their frozen identities and validity gates."""

    manifest, retrieval, truth = benchmark_rows()
    benchmark_id = manifest["benchmark_id"]
    manifest_sha256 = sha256(EVALUATION_ROOT.parent / "semantic-okf-adaptive-evolution/frozen-benchmark.json")
    expected_question_ids = [row["id"] for row in retrieval]
    direct_reports = {
        "adaptive-direct-replay.json": ("adaptive_fusion", "adaptive-fusion-reference"),
        "ensemble-fast-current-direct.json": ("ensemble_fast", "ensemble-fast-final-current"),
        "ensemble-robust-current-direct.json": ("ensemble_robust", "ensemble-robust-final-current"),
        "ensemble-quality-winner-direct.json": (
            "ensemble_quality",
            "ensemble-quality-population-winner",
        ),
    }
    direct_keys = {
        "schema_version",
        "status",
        "candidate_label",
        "route",
        "benchmark",
        "inputs",
        "contract",
        "evidence_validity",
        "timing_ms",
        "cohorts",
        "paper_metric_deltas_vs_adaptive_incumbent",
        "issues",
        "questions",
    }
    for filename, (route, label) in direct_reports.items():
        report = load_json(BASELINES / filename)
        exact_keys(report, direct_keys, filename)
        if report["schema_version"] != "semantic-okf-ensemble-direct-retrieval-comparison/1.0":
            raise EvaluationError(f"{filename} schema_version differs")
        if report["status"] != "pass" or report["issues"]:
            raise EvaluationError(f"{filename} does not retain a clean pass status")
        if report["route"] != route or report["candidate_label"] != label:
            raise EvaluationError(f"{filename} route or candidate label differs")
        if report["benchmark"] != {
            "id": benchmark_id,
            "manifest_sha256": manifest_sha256,
            "question_count": len(expected_question_ids),
        }:
            raise EvaluationError(f"{filename} frozen benchmark binding differs")
        if report["evidence_validity"] != {
            "returned": 400,
            "valid": 400,
            "invalid": 0,
            "ratio": 1.0,
        }:
            raise EvaluationError(f"{filename} evidence-validity gate differs")
        questions = report["questions"]
        if not isinstance(questions, list) or [row.get("id") for row in questions if isinstance(row, dict)] != expected_question_ids:
            raise EvaluationError(f"{filename} question identities differ from the frozen order")

    graph = load_json(BASELINES / "entity-graph-hard10-coverage.json")
    if graph.get("schema_version") != "semantic-okf-ensemble-hard10-graph-coverage/1.0":
        raise EvaluationError("entity graph coverage schema_version differs")
    if graph.get("status") != "pass" or graph.get("issues"):
        raise EvaluationError("entity graph coverage does not retain a clean pass status")
    if graph.get("benchmark") != {
        "id": benchmark_id,
        "manifest_sha256": manifest_sha256,
        "hard_question_count": len(truth),
    }:
        raise EvaluationError("entity graph coverage frozen benchmark binding differs")
    if graph.get("evidence_validity") != {"returned": 100, "valid": 100, "invalid": 0, "ratio": 1.0}:
        raise EvaluationError("entity graph coverage evidence-validity gate differs")
    if graph.get("page_locator_mapping") != {"mapped": 100, "unmapped": 0, "ratio": 1.0}:
        raise EvaluationError("entity graph coverage page-locator gate differs")
    if [row.get("id") for row in graph.get("questions", []) if isinstance(row, dict)] != [row["id"] for row in truth]:
        raise EvaluationError("entity graph coverage question identities differ from hard-ten truth")

    determinism = load_json(BASELINES / "ensemble-determinism.json")
    exact_keys(determinism, {"schema_version", "status", "benchmark", "bundle", "runtime", "policies"}, "determinism report")
    if determinism["schema_version"] != "semantic-okf-ensemble-ranking-determinism/1.0" or determinism["status"] != "pass":
        raise EvaluationError("determinism report status or schema_version differs")
    if determinism["benchmark"] != {
        "benchmark_id": benchmark_id,
        "manifest_sha256": manifest_sha256,
        "question_count": len(retrieval),
        "top_k": 10,
    }:
        raise EvaluationError("determinism report frozen benchmark binding differs")
    policies = determinism["policies"]
    if not isinstance(policies, dict) or set(policies) != {"fast", "robust", "quality"}:
        raise EvaluationError("determinism report policy set differs")
    for name, expected_repetitions in {"fast": 3, "robust": 3, "quality": 4}.items():
        policy = policies[name]
        if policy.get("repetitions") != expected_repetitions or policy.get("all_rankings_equal") is not True:
            raise EvaluationError(f"determinism evidence for {name} differs")
        ranking_hash = policy.get("rankings_sha256")
        if not isinstance(ranking_hash, str) or re.fullmatch(r"[0-9a-f]{64}", ranking_hash) is None:
            raise EvaluationError(f"determinism ranking hash for {name} is invalid")


def validate_checked_answer_output_report() -> dict[str, Any]:
    """Validate the checked compact answer report and its exact publication bytes."""

    if not ANSWER_OUTPUT_REPORT.is_file():
        raise EvaluationError(
            "checked answer-output comparison JSON is missing: "
            f"{ANSWER_OUTPUT_REPORT.as_posix()}"
        )
    if not ANSWER_OUTPUT_MARKDOWN.is_file():
        raise EvaluationError(
            "checked answer-output comparison Markdown is missing: "
            f"{ANSWER_OUTPUT_MARKDOWN.as_posix()}"
        )

    aggregator_path = EVALUATION_ROOT / "scripts/aggregate_answer_output_evaluation.py"
    aggregator = module_from_path(
        "semantic_okf_ensemble_checked_answer_output_aggregator",
        aggregator_path,
    )
    report = load_json(ANSWER_OUTPUT_REPORT)
    contract = load_answer_output_contract(ANSWER_OUTPUT_CONTRACT)
    try:
        checked = aggregator.validate_summary(report, contract)
    except (OSError, UnicodeError, ValueError) as exc:
        raise EvaluationError(f"checked answer-output comparison is invalid: {exc}") from exc
    if not isinstance(checked, dict) or checked != report:
        raise EvaluationError(
            "checked answer-output comparison validator did not preserve the report"
        )

    # This is the exact append-only publication encoding emitted by the aggregator.
    # Comparing bytes, rather than reparsing, also rejects reordered members, CRLF,
    # missing final newlines, BOMs, and alternate escaping of equivalent JSON.
    expected_json = (
        json.dumps(checked, indent=2, ensure_ascii=False) + "\n"
    ).encode("utf-8")
    if ANSWER_OUTPUT_REPORT.read_bytes() != expected_json:
        raise EvaluationError(
            "checked answer-output comparison JSON differs from canonical publication bytes"
        )

    expected_markdown = aggregator.render_markdown(checked).encode("utf-8")
    if ANSWER_OUTPUT_MARKDOWN.read_bytes() != expected_markdown:
        raise EvaluationError(
            "checked answer-output comparison Markdown differs from the validated JSON"
        )
    return checked


def validate_checked_mcp_runtime_attestation(
    answer_output_report: dict[str, Any],
) -> dict[str, Any]:
    """Validate retired MCP evidence without resolving the retired active runtime."""

    if not MCP_RUNTIME_ATTESTATION.is_file():
        raise EvaluationError(
            "checked Skill Arena MCP runtime attestation JSON is missing: "
            f"{MCP_RUNTIME_ATTESTATION.as_posix()}"
        )
    if not MCP_RUNTIME_ATTESTATION_MARKDOWN.is_file():
        raise EvaluationError(
            "checked Skill Arena MCP runtime attestation Markdown is missing: "
            f"{MCP_RUNTIME_ATTESTATION_MARKDOWN.as_posix()}"
        )
    if sha256(MCP_RUNTIME_ATTESTATION) != HISTORICAL_MCP_ARTIFACT_SHA256[
        "runtime_attestation_report"
    ]:
        raise EvaluationError(
            "checked historical MCP runtime attestation SHA-256 differs"
        )
    if sha256(MCP_RUNTIME_ATTESTATION_MARKDOWN) != HISTORICAL_MCP_ARTIFACT_SHA256[
        "runtime_attestation_markdown"
    ]:
        raise EvaluationError(
            "checked historical MCP runtime attestation Markdown SHA-256 differs"
        )
    report = load_json(MCP_RUNTIME_ATTESTATION)
    exact_keys(
        report,
        {
            "schema_version",
            "status",
            "benchmark",
            "inputs",
            "implementation",
            "trace_contract",
            "gates",
            "aggregates",
            "rows",
        },
        "historical MCP runtime attestation",
    )
    if (
        report["schema_version"]
        != "semantic-okf-ensemble-skill-arena-mcp-runtime-attestation/1.7"
        or report["status"] != "pass"
    ):
        raise EvaluationError(
            "checked historical MCP runtime attestation identity differs"
        )
    benchmark = report["benchmark"]
    if not isinstance(benchmark, dict) or benchmark.get("answer_count") != 90:
        raise EvaluationError("checked historical MCP runtime benchmark differs")
    inputs = report["inputs"]
    if not isinstance(inputs, dict) or inputs.get("answer_output_report") != {
        "path": ANSWER_OUTPUT_REPORT.relative_to(REPO_ROOT).as_posix(),
        "sha256": HISTORICAL_MCP_ARTIFACT_SHA256["answer_output_report"],
    }:
        raise EvaluationError(
            "checked historical MCP runtime answer-report binding differs"
        )
    if inputs.get("skill_arena_config") != {
        "path": SKILL_ARENA_CONFIG.relative_to(REPO_ROOT).as_posix(),
        "sha256": HISTORICAL_MCP_ARTIFACT_SHA256["skill_arena_config"],
    } or inputs.get("skill_arena_manifest") != {
        "path": SKILL_ARENA_MANIFEST.relative_to(REPO_ROOT).as_posix(),
        "sha256": HISTORICAL_MCP_ARTIFACT_SHA256["skill_arena_manifest"],
    }:
        raise EvaluationError(
            "checked historical MCP runtime Skill Arena binding differs"
        )
    implementation = report["implementation"]
    if implementation != {
        "path": HISTORICAL_MCP_ARTIFACTS["runtime_attestor"]
        .relative_to(REPO_ROOT)
        .as_posix(),
        "sha256": HISTORICAL_MCP_ARTIFACT_SHA256["runtime_attestor"],
    }:
        raise EvaluationError(
            "checked historical MCP runtime attestor binding differs"
        )
    gates = report["gates"]
    if not isinstance(gates, dict) or not gates or any(
        value is not True for value in gates.values()
    ):
        raise EvaluationError("checked historical MCP runtime contains a failed gate")
    aggregates = report["aggregates"]
    if not isinstance(aggregates, dict) or {
        "answer_count": aggregates.get("answer_count"),
        "trace_count": aggregates.get("trace_count"),
        "archived_trace_count": aggregates.get("archived_trace_count"),
        "unique_trace_sha256_count": aggregates.get("unique_trace_sha256_count"),
        "treatment_answer_count": aggregates.get("treatment_answer_count"),
        "confirmed_treatment_count": aggregates.get("confirmed_treatment_count"),
    } != {
        "answer_count": 90,
        "trace_count": 90,
        "archived_trace_count": 90,
        "unique_trace_sha256_count": 90,
        "treatment_answer_count": 30,
        "confirmed_treatment_count": 30,
    }:
        raise EvaluationError("checked historical MCP runtime aggregate differs")
    rows = report["rows"]
    if not isinstance(rows, list) or len(rows) != 90:
        raise EvaluationError("checked historical MCP runtime row count differs")
    identities = {
        (row.get("profile_id"), row.get("question_id"), row.get("repetition"))
        for row in rows
        if isinstance(row, dict)
    }
    if len(identities) != 90:
        raise EvaluationError("checked historical MCP runtime row identities differ")
    if answer_output_report.get("answer_count") != 90:
        raise EvaluationError(
            "checked historical MCP runtime answer count is not bound to the answer report"
        )
    expected_json = (
        json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    ).encode("utf-8")
    if MCP_RUNTIME_ATTESTATION.read_bytes() != expected_json:
        raise EvaluationError(
            "checked Skill Arena MCP runtime attestation JSON differs from canonical publication bytes"
        )
    return report


def _reject_absolute_paths(value: Any, label: str = "diagnostic") -> None:
    """Reject machine-local paths from one compact checked diagnostic."""

    if isinstance(value, dict):
        for key, item in value.items():
            _reject_absolute_paths(item, f"{label}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _reject_absolute_paths(item, f"{label}[{index}]")
    elif isinstance(value, str) and (
        ABSOLUTE_WINDOWS.match(value)
        or value.startswith(("/home/", "/Users/", "/tmp/"))
        or value.startswith("\\\\")
    ):
        raise EvaluationError(f"compact diagnostic has an absolute path at {label}")


def validate_skill_bootstrap_isolation_diagnostic() -> dict[str, Any]:
    """Validate the rejected shell-bootstrap run without admitting its scores."""

    if not SKILL_BOOTSTRAP_ISOLATION_DIAGNOSTIC.is_file():
        raise EvaluationError("skill-bootstrap isolation diagnostic JSON is missing")
    if not SKILL_BOOTSTRAP_ISOLATION_DIAGNOSTIC_MARKDOWN.is_file():
        raise EvaluationError("skill-bootstrap isolation diagnostic Markdown is missing")
    report = load_json(SKILL_BOOTSTRAP_ISOLATION_DIAGNOSTIC)
    exact_keys(
        report,
        {
            "schema_version",
            "status",
            "date",
            "scope",
            "persisted_rows",
            "trigger",
            "decision",
            "raw_retention",
        },
        "skill-bootstrap isolation diagnostic",
    )
    if (
        report["schema_version"]
        != "semantic-okf-ensemble-skill-bootstrap-isolation-diagnostic/1.0"
        or report["status"] != "rejected-diagnostic"
        or report["date"] != "2026-07-15"
    ):
        raise EvaluationError("skill-bootstrap isolation diagnostic identity differs")

    scope = exact_keys(
        report["scope"],
        {
            "compare_run",
            "evaluation_id",
            "planned_answers",
            "persisted_rows_at_stop",
            "accepted_benchmark_rows",
            "quality_metrics_published",
        },
        "skill-bootstrap isolation diagnostic scope",
    )
    if scope != {
        "compare_run": "2026-07-15T14-29-07-959Z-compare",
        "evaluation_id": "eval-T27-2026-07-15T14:29:15",
        "planned_answers": 90,
        "persisted_rows_at_stop": 17,
        "accepted_benchmark_rows": 0,
        "quality_metrics_published": False,
    }:
        raise EvaluationError("skill-bootstrap isolation diagnostic scope differs")

    persisted = exact_keys(
        report["persisted_rows"],
        {
            "knowledge-only-control",
            "adaptive-consult-control",
            "ensemble-consult-treatment",
            "provider_response_errors",
        },
        "skill-bootstrap isolation diagnostic persisted rows",
    )
    expected_persisted = {
        "knowledge-only-control": 6,
        "adaptive-consult-control": 6,
        "ensemble-consult-treatment": 5,
        "provider_response_errors": 0,
    }
    if (
        persisted != expected_persisted
        or sum(persisted[profile] for profile in expected_persisted if profile != "provider_response_errors")
        != scope["persisted_rows_at_stop"]
        or scope["accepted_benchmark_rows"] != 0
        or scope["quality_metrics_published"] is not False
    ):
        raise EvaluationError("skill-bootstrap isolation diagnostic row accounting differs")

    trigger = exact_keys(
        report["trigger"],
        {
            "row_id",
            "profile_id",
            "question_id",
            "test_index",
            "classification",
            "command_shape",
            "command_exit_code",
            "command_status",
            "command_output_binding",
            "later_semantic_protocol_completed",
            "host_publication_completed",
            "response_contract_score",
            "evidence_validity_score",
            "atomic_answer_completeness_score",
            "important_negative_coverage_score",
        },
        "skill-bootstrap isolation diagnostic trigger",
    )
    if trigger != {
        "row_id": "ed9ff150-11ec-4ce3-870b-6f7c95cf2523",
        "profile_id": "ensemble-consult-treatment",
        "question_id": "q032-incremental-update-maturity",
        "test_index": 4,
        "classification": "uncontracted-skill-bootstrap-shell-read",
        "command_shape": (
            "Get-Content -LiteralPath '<isolated CODEX_HOME>/skills/"
            "consult-semantic-okf-ensemble/SKILL.md' -Raw"
        ),
        "command_exit_code": 0,
        "command_status": "completed",
        "command_output_binding": (
            "frozen SKILL.md UTF-8 bytes followed by one PowerShell CRLF"
        ),
        "later_semantic_protocol_completed": True,
        "host_publication_completed": True,
        "response_contract_score": 1,
        "evidence_validity_score": 1,
        "atomic_answer_completeness_score": 0,
        "important_negative_coverage_score": 1,
    }:
        raise EvaluationError(
            "skill-bootstrap isolation diagnostic q032 treatment shell-read differs"
        )

    decision = exact_keys(
        report["decision"],
        {"reason", "remediation", "causal_use"},
        "skill-bootstrap isolation diagnostic decision",
    )
    if decision != {
        "reason": (
            "The frozen v1.4.0 attestor required zero treatment command-execution "
            "events. Skill Arena supplied the skill identity and path but not the full "
            "SKILL.md body, so the faithful bootstrap read violated that predeclared "
            "gate even though it was read-only and the later publication transaction "
            "succeeded."
        ),
        "remediation": (
            "Replace shell bootstrap with the no-argument, digest-bound, one-shot "
            "semantic_okf_bootstrap_skill tool; disable the general shell tool for the "
            "exact treatment; require bootstrap before every consultation call; and "
            "rerun all 90 answers under MCP v1.5.0."
        ),
        "causal_use": (
            "None. The partial run is retained only as design evidence and must not be "
            "merged with the replacement run."
        ),
    }:
        raise EvaluationError("skill-bootstrap isolation diagnostic causal-use decision differs")
    if report["raw_retention"] != (
        "The append-only raw compare directory and Promptfoo database rows remain "
        "ignored. This compact report contains no answer text, temporary absolute "
        "path, or accepted quality aggregate."
    ):
        raise EvaluationError("skill-bootstrap isolation diagnostic raw-retention note differs")

    _reject_absolute_paths(report, "skill-bootstrap isolation diagnostic")
    canonical = (json.dumps(report, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    if SKILL_BOOTSTRAP_ISOLATION_DIAGNOSTIC.read_bytes() != canonical:
        raise EvaluationError("skill-bootstrap isolation diagnostic JSON is not canonical")
    if (
        sha256(SKILL_BOOTSTRAP_ISOLATION_DIAGNOSTIC)
        != SKILL_BOOTSTRAP_ISOLATION_DIAGNOSTIC_SHA256
    ):
        raise EvaluationError("skill-bootstrap isolation diagnostic JSON binding differs")
    if (
        sha256(SKILL_BOOTSTRAP_ISOLATION_DIAGNOSTIC_MARKDOWN)
        != SKILL_BOOTSTRAP_ISOLATION_DIAGNOSTIC_MARKDOWN_SHA256
    ):
        raise EvaluationError("skill-bootstrap isolation diagnostic Markdown binding differs")
    return report


def validate_bootstrap_isolation_technical_preflight() -> dict[str, Any]:
    """Validate the one-row, non-causal bootstrap and shell-isolation preflight."""

    if not BOOTSTRAP_ISOLATION_TECHNICAL_PREFLIGHT.is_file():
        raise EvaluationError("bootstrap-isolation technical preflight JSON is missing")
    if not BOOTSTRAP_ISOLATION_TECHNICAL_PREFLIGHT_MARKDOWN.is_file():
        raise EvaluationError("bootstrap-isolation technical preflight Markdown is missing")
    report = load_json(BOOTSTRAP_ISOLATION_TECHNICAL_PREFLIGHT)
    exact_keys(
        report,
        {
            "schema_version",
            "status",
            "evidence_class",
            "date",
            "scope",
            "inputs",
            "retained_raw_bindings",
            "runtime",
            "publication",
            "promptfoo_assertions",
            "decision",
        },
        "bootstrap-isolation technical preflight",
    )
    if (
        report["schema_version"]
        != "semantic-okf-ensemble-bootstrap-isolation-preflight/1.0"
        or report["status"] != "pass"
        or report["evidence_class"] != "non-causal-technical-preflight"
        or report["date"] != "2026-07-15"
    ):
        raise EvaluationError("bootstrap-isolation technical preflight identity differs")

    scope = exact_keys(
        report["scope"],
        {
            "benchmark_id",
            "compare_run",
            "evaluation_id",
            "profile_id",
            "question_id",
            "requested_answers",
            "completed_answers",
            "causal_or_portfolio_metric",
        },
        "bootstrap-isolation technical preflight scope",
    )
    if scope != {
        "benchmark_id": "semantic-okf-ensemble-bootstrap-q031-preflight-v1",
        "compare_run": "2026-07-15T15-19-09-193Z-compare",
        "evaluation_id": "eval-jpH-2026-07-15T15:19:14",
        "profile_id": "ensemble-consult-treatment",
        "question_id": "q031-graph-routing-boundary",
        "requested_answers": 1,
        "completed_answers": 1,
        "causal_or_portfolio_metric": False,
    }:
        raise EvaluationError("bootstrap-isolation technical preflight scope differs")

    inputs = exact_keys(
        report["inputs"],
        {
            "source_full_config_sha256",
            "derived_preflight_config_sha256",
            "mcp_server_version",
            "mcp_server_sha256",
            "publication_script_sha256",
            "skill_sha256",
            "skill_byte_count",
        },
        "bootstrap-isolation technical preflight inputs",
    )
    expected_inputs = {
        "source_full_config_sha256": (
            "5042a9dae24bdac352ddf1c1f7482a5fe9cf76b0b771ae6d606a514eff5ad4ac"
        ),
        "derived_preflight_config_sha256": (
            "77eb06df24b2846054d72bf693ea4e6e080f58a6d371c6dff28d62498bd6d26c"
        ),
        "mcp_server_version": "1.5.0",
        "mcp_server_sha256": (
            "bef33f807ad339563a076402edf96b65c9cd66f81eb0af3484a49a8945d940c2"
        ),
        "publication_script_sha256": (
            "6db622318acba2301b272504e6687bb34055d2704a0ce4f1c7425ee9bb8570b1"
        ),
        "skill_sha256": (
            "ec80687beb701f5fc8b6cd13d5ec779cbe5e1f52baffbf3a4a41db4f390717c2"
        ),
        "skill_byte_count": 15699,
    }
    # The MCP, publication wrapper, and treatment skill bindings describe the
    # immutable historical run. They intentionally are not re-resolved against the
    # active CLI-only package after runtime retirement.
    if (
        inputs != expected_inputs
        or sha256(SKILL_ARENA_CONFIG)
        != expected_inputs["source_full_config_sha256"]
    ):
        raise EvaluationError("bootstrap-isolation technical preflight source binding differs")

    retained = exact_keys(
        report["retained_raw_bindings"],
        {
            "promptfoo_results_path",
            "promptfoo_results_sha256",
            "trace_sha256",
            "raw_artifacts_ignored",
        },
        "bootstrap-isolation technical preflight retained raw bindings",
    )
    if retained != {
        "promptfoo_results_path": (
            "results/semantic-okf-ensemble-bootstrap-q031-preflight-v1/"
            "2026-07-15T15-19-09-193Z-compare/promptfoo-results.json"
        ),
        "promptfoo_results_sha256": (
            "e264e3324fb59e007d891f3b9ac451b3d094fb028d3a9e44c586c1b05198b979"
        ),
        "trace_sha256": (
            "b30b316958f9cdf02e6d7c59e64e210e0cef664df5617a0dbfb5b16698b16405"
        ),
        "raw_artifacts_ignored": True,
    } or Path(retained["promptfoo_results_path"]).is_absolute():
        raise EvaluationError("bootstrap-isolation technical preflight raw bindings differ")

    runtime = exact_keys(
        report["runtime"],
        {
            "process_exit_code",
            "provider_errors",
            "latency_ms",
            "command_execution_count",
            "semantic_tool_order",
            "bootstrap",
            "shell_isolation",
        },
        "bootstrap-isolation technical preflight runtime",
    )
    if (
        runtime["process_exit_code"] != 0
        or runtime["provider_errors"] != 0
        or runtime["latency_ms"] != 153486
        or runtime["command_execution_count"] != 0
    ):
        raise EvaluationError("bootstrap-isolation technical preflight runtime counts differ")
    expected_tool_order = [
        "semantic_okf_bootstrap_skill",
        "semantic_okf_inspect",
        "semantic_okf_coverage_brief",
        "semantic_okf_coverage_brief",
        "semantic_okf_coverage_brief",
        "semantic_okf_coverage_brief",
        "semantic_okf_coverage_brief",
        "semantic_okf_prepare_answer",
        "semantic_okf_confirm_answer",
    ]
    if runtime["semantic_tool_order"] != expected_tool_order:
        raise EvaluationError("bootstrap-isolation technical preflight tool order differs")
    bootstrap = exact_keys(
        runtime["bootstrap"],
        {"schema", "skill_sha256", "byte_count"},
        "bootstrap-isolation technical preflight bootstrap receipt",
    )
    if bootstrap != {
        "schema": "semantic-okf-skill-bootstrap/1.0",
        "skill_sha256": inputs["skill_sha256"],
        "byte_count": inputs["skill_byte_count"],
    }:
        raise EvaluationError("bootstrap-isolation technical preflight bootstrap binding differs")
    shell = exact_keys(
        runtime["shell_isolation"],
        {
            "schema",
            "skill_id",
            "shell_tool_disabled",
            "canonical_receipt_sha256",
            "canonical_receipt_byte_count",
        },
        "bootstrap-isolation technical preflight shell receipt",
    )
    receipt_record = {
        "schema": "semantic-okf-shell-isolation-receipt/1.0",
        "skill_id": "consult-semantic-okf-ensemble",
        "shell_tool_disabled": True,
    }
    receipt_bytes = json.dumps(
        receipt_record, ensure_ascii=False, separators=(",", ":")
    ).encode("utf-8")
    if shell != {
        **receipt_record,
        "canonical_receipt_sha256": hashlib.sha256(receipt_bytes).hexdigest(),
        "canonical_receipt_byte_count": len(receipt_bytes),
    }:
        raise EvaluationError("bootstrap-isolation technical preflight shell receipt differs")

    publication = exact_keys(
        report["publication"],
        {
            "prepared_candidate_sha256",
            "confirmation_receipt_sha256",
            "published_output_sha256",
            "published_byte_count",
            "published_equals_prepared_candidate",
            "raw_agent_message_equals_prepared_candidate",
            "host_publication_correction_applied",
        },
        "bootstrap-isolation technical preflight publication",
    )
    expected_candidate_sha256 = (
        "a6bf8dfd8438b181f343fffbb46aa496d49790bb27abdf4716a372e69433bdf7"
    )
    if publication != {
        "prepared_candidate_sha256": expected_candidate_sha256,
        "confirmation_receipt_sha256": expected_candidate_sha256,
        "published_output_sha256": expected_candidate_sha256,
        "published_byte_count": 8872,
        "published_equals_prepared_candidate": True,
        "raw_agent_message_equals_prepared_candidate": False,
        "host_publication_correction_applied": True,
    }:
        raise EvaluationError(
            "bootstrap-isolation technical preflight publication digest binding differs"
        )

    assertions = exact_keys(
        report["promptfoo_assertions"],
        {
            "response_format",
            "response_contract",
            "evidence_validity",
            "atomic_answer_completeness",
            "important_negative_coverage",
        },
        "bootstrap-isolation technical preflight Promptfoo assertions",
    )
    if any(type(value) is not int or value != 1 for value in assertions.values()):
        raise EvaluationError("bootstrap-isolation technical preflight assertions differ")
    if report["decision"] != (
        "The live provider path is ready for a fresh full 90-answer run. This "
        "one-row preflight validates transport and isolation only and must not be "
        "presented as causal or aggregate answer-quality evidence."
    ):
        raise EvaluationError("bootstrap-isolation technical preflight decision differs")

    _reject_absolute_paths(report, "bootstrap-isolation technical preflight")
    canonical = (json.dumps(report, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    if BOOTSTRAP_ISOLATION_TECHNICAL_PREFLIGHT.read_bytes() != canonical:
        raise EvaluationError("bootstrap-isolation technical preflight JSON is not canonical")
    if (
        sha256(BOOTSTRAP_ISOLATION_TECHNICAL_PREFLIGHT)
        != BOOTSTRAP_ISOLATION_TECHNICAL_PREFLIGHT_SHA256
    ):
        raise EvaluationError("bootstrap-isolation technical preflight JSON binding differs")
    if (
        sha256(BOOTSTRAP_ISOLATION_TECHNICAL_PREFLIGHT_MARKDOWN)
        != BOOTSTRAP_ISOLATION_TECHNICAL_PREFLIGHT_MARKDOWN_SHA256
    ):
        raise EvaluationError("bootstrap-isolation technical preflight Markdown binding differs")
    return report


def validate_host_publication_mutation_diagnostic() -> dict[str, Any]:
    """Validate the compact rejected run that motivated the host publication gate."""

    if not HOST_PUBLICATION_DIAGNOSTIC.is_file():
        raise EvaluationError("host publication mutation diagnostic JSON is missing")
    if not HOST_PUBLICATION_DIAGNOSTIC_MARKDOWN.is_file():
        raise EvaluationError("host publication mutation diagnostic Markdown is missing")
    report = load_json(HOST_PUBLICATION_DIAGNOSTIC)
    exact_keys(
        report,
        {
            "schema_version",
            "status",
            "evidence_class",
            "date",
            "comparison",
            "provenance",
            "scope",
            "aggregates",
            "rows",
            "decision",
            "raw_retention",
        },
        "host publication mutation diagnostic",
    )
    if (
        report["schema_version"]
        != "semantic-okf-ensemble-host-publication-mutation-diagnostic/1.0"
        or report["status"] != "rejected"
        or report["evidence_class"] != "diagnostic-only-non-benchmark"
        or report["date"] != "2026-07-15"
    ):
        raise EvaluationError("host publication diagnostic identity differs")
    comparison = exact_keys(
        report["comparison"],
        {
            "run_id",
            "promptfoo_eval_id",
            "planned_answer_count",
            "completed_answer_count_at_interruption",
            "termination",
            "benchmark_eligible",
            "exclusion_reason",
        },
        "host publication diagnostic comparison",
    )
    if comparison != {
        "run_id": "2026-07-15T11-08-27-398Z-compare",
        "promptfoo_eval_id": "eval-RBD-2026-07-15T11:08:32",
        "planned_answer_count": 90,
        "completed_answer_count_at_interruption": 38,
        "termination": "intentional-quality-gate-stop",
        "benchmark_eligible": False,
        "exclusion_reason": (
            "The run was incomplete and used the pre-gate free-form host publication path."
        ),
    }:
        raise EvaluationError("host publication diagnostic comparison differs")
    exact_keys(
        report["provenance"],
        {
            "execution_log",
            "generated_promptfoo_config",
            "database_source",
            "database_projection",
            "trace_projection",
        },
        "host publication diagnostic provenance",
    )
    for key in ("execution_log", "generated_promptfoo_config"):
        binding = exact_keys(
            report["provenance"][key],
            {"path", "sha256"},
            f"host publication diagnostic {key}",
        )
        if (
            not isinstance(binding["path"], str)
            or not binding["path"]
            or not isinstance(binding["sha256"], str)
            or re.fullmatch(r"[0-9a-f]{64}", binding["sha256"]) is None
        ):
            raise EvaluationError(f"host publication diagnostic {key} binding differs")
    if report["scope"] != {
        "question_id": "q031-graph-routing-boundary",
        "profile_id": "ensemble-consult-treatment",
        "treatment_row_count": 3,
    }:
        raise EvaluationError("host publication diagnostic scope differs")
    aggregates = exact_keys(
        report["aggregates"],
        {
            "canonical_prepare_confirmation_success_count",
            "receipt_binding_pass_count",
            "host_output_matches_final_agent_message_count",
            "host_output_matches_confirmed_candidate_count",
            "host_publication_mutation_row_count",
            "mutated_field_count",
            "terminal_prepare_confirm_sequence_count",
            "post_confirmation_prepare_row_count",
            "free_form_publication_failure_rate",
            "observed_trace_command",
        },
        "host publication diagnostic aggregates",
    )
    if aggregates != {
        "canonical_prepare_confirmation_success_count": 3,
        "receipt_binding_pass_count": 3,
        "host_output_matches_final_agent_message_count": 3,
        "host_output_matches_confirmed_candidate_count": 0,
        "host_publication_mutation_row_count": 3,
        "mutated_field_count": 6,
        "terminal_prepare_confirm_sequence_count": 2,
        "post_confirmation_prepare_row_count": 1,
        "free_form_publication_failure_rate": 1.0,
        "observed_trace_command": "codex",
    }:
        raise EvaluationError("host publication diagnostic aggregates differ")
    rows = report["rows"]
    if not isinstance(rows, list) or len(rows) != 3:
        raise EvaluationError("host publication diagnostic row count differs")
    mutation_count = 0
    terminal_count = 0
    post_confirmation_count = 0
    row_ids: set[str] = set()
    row_keys = {
        "raw_row_id",
        "database_projection_sha256",
        "database_response_sha256",
        "database_metadata_sha256",
        "trace_sha256",
        "trace_byte_count",
        "trace_event_count",
        "trace_tool_event_count",
        "trace_command",
        "finalizer_completed_sequence",
        "successful_prepare_count",
        "failed_prepare_count",
        "confirmation_count",
        "post_confirmation_prepare_count",
        "confirmed_candidate",
        "confirmation_receipt",
        "final_agent_message",
        "host_published_output",
        "mutations",
    }
    for row in rows:
        exact_keys(row, row_keys, "host publication diagnostic row")
        row_id = row["raw_row_id"]
        if not isinstance(row_id, str) or not row_id or row_id in row_ids:
            raise EvaluationError("host publication diagnostic row identity differs")
        row_ids.add(row_id)
        for key in (
            "database_projection_sha256",
            "database_response_sha256",
            "database_metadata_sha256",
            "trace_sha256",
        ):
            if not isinstance(row[key], str) or re.fullmatch(r"[0-9a-f]{64}", row[key]) is None:
                raise EvaluationError("host publication diagnostic row SHA-256 differs")
        candidate = exact_keys(
            row["confirmed_candidate"],
            {"sha256", "byte_count", "canonical_json"},
            "host publication diagnostic candidate",
        )
        receipt = exact_keys(
            row["confirmation_receipt"],
            {"schema", "status", "sha256", "byte_count", "matches_candidate"},
            "host publication diagnostic receipt",
        )
        message = exact_keys(
            row["final_agent_message"],
            {"sha256", "byte_count"},
            "host publication diagnostic final message",
        )
        published = exact_keys(
            row["host_published_output"],
            {
                "sha256",
                "byte_count",
                "matches_final_agent_message",
                "matches_confirmed_candidate",
            },
            "host publication diagnostic host output",
        )
        for item, label in (
            (candidate, "candidate"),
            (receipt, "receipt"),
            (message, "final message"),
            (published, "host output"),
        ):
            if (
                not isinstance(item["sha256"], str)
                or re.fullmatch(r"[0-9a-f]{64}", item["sha256"]) is None
                or not isinstance(item["byte_count"], int)
                or isinstance(item["byte_count"], bool)
                or item["byte_count"] <= 0
            ):
                raise EvaluationError(
                    f"host publication diagnostic {label} binding differs"
                )
        if (
            candidate["canonical_json"] is not True
            or receipt["schema"] != "semantic-okf-answer-confirmation-receipt/1.0"
            or receipt["status"] != "confirmed"
            or receipt["matches_candidate"] is not True
            or published["matches_final_agent_message"] is not True
            or published["matches_confirmed_candidate"] is not False
            or published["sha256"] != message["sha256"]
            or published["byte_count"] != message["byte_count"]
            or published["sha256"] == candidate["sha256"]
        ):
            raise EvaluationError("host publication diagnostic publication identity differs")
        mutations = row["mutations"]
        if not isinstance(mutations, list) or not mutations:
            raise EvaluationError("host publication diagnostic mutations differ")
        for mutation in mutations:
            exact_keys(
                mutation,
                {"path", "confirmed", "host_published"},
                "host publication diagnostic mutation",
            )
            if mutation["confirmed"] == mutation["host_published"]:
                raise EvaluationError("host publication diagnostic mutation is not a change")
        mutation_count += len(mutations)
        sequence = row["finalizer_completed_sequence"]
        if isinstance(sequence, list) and sequence and sequence[-1] == "confirm:completed":
            terminal_count += 1
        post_confirmation_count += row["post_confirmation_prepare_count"]
    if (
        mutation_count != aggregates["mutated_field_count"]
        or terminal_count != aggregates["terminal_prepare_confirm_sequence_count"]
        or post_confirmation_count != aggregates["post_confirmation_prepare_row_count"]
    ):
        raise EvaluationError("host publication diagnostic row aggregates differ")
    decision = exact_keys(
        report["decision"],
        {"observed_failure", "remediation", "acceptance_rule"},
        "host publication diagnostic decision",
    )
    if any(not isinstance(value, str) or not value for value in decision.values()):
        raise EvaluationError("host publication diagnostic decision differs")
    if not isinstance(report["raw_retention"], str) or not report["raw_retention"]:
        raise EvaluationError("host publication diagnostic raw-retention note differs")
    _reject_absolute_paths(report, "host publication diagnostic")
    expected_json = (json.dumps(report, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    if HOST_PUBLICATION_DIAGNOSTIC.read_bytes() != expected_json:
        raise EvaluationError("host publication diagnostic JSON is not canonical")
    if sha256(HOST_PUBLICATION_DIAGNOSTIC) != HOST_PUBLICATION_DIAGNOSTIC_SHA256:
        raise EvaluationError("host publication diagnostic JSON binding differs")
    if (
        sha256(HOST_PUBLICATION_DIAGNOSTIC_MARKDOWN)
        != HOST_PUBLICATION_DIAGNOSTIC_MARKDOWN_SHA256
    ):
        raise EvaluationError("host publication diagnostic Markdown binding differs")
    return report


def validate_source_provenance_drift_diagnostic() -> dict[str, Any]:
    """Keep the interrupted source-drift run closed and benchmark-ineligible."""

    if not SOURCE_PROVENANCE_DIAGNOSTIC.is_file():
        raise EvaluationError("source-provenance diagnostic JSON is missing")
    if not SOURCE_PROVENANCE_DIAGNOSTIC_MARKDOWN.is_file():
        raise EvaluationError("source-provenance diagnostic Markdown is missing")
    report = load_json(SOURCE_PROVENANCE_DIAGNOSTIC)
    exact_keys(
        report,
        {
            "schema_version",
            "status",
            "evidence_class",
            "date",
            "comparison",
            "provenance",
            "materialized_source",
            "final_frozen_source",
            "persisted_rows",
            "decision",
            "raw_retention",
        },
        "source-provenance diagnostic",
    )
    if (
        report["schema_version"]
        != "semantic-okf-ensemble-source-provenance-drift-diagnostic/1.0"
        or report["status"] != "rejected"
        or report["evidence_class"] != "diagnostic-only-non-benchmark"
        or report["date"] != "2026-07-15"
    ):
        raise EvaluationError("source-provenance diagnostic identity differs")

    comparison = exact_keys(
        report["comparison"],
        {
            "run_id",
            "promptfoo_eval_id",
            "planned_answer_count",
            "stop_decision_completed_row_count",
            "persisted_row_count_after_process_exit",
            "termination",
            "benchmark_eligible",
            "exclusion_reason",
        },
        "source-provenance diagnostic comparison",
    )
    if comparison != {
        "run_id": "2026-07-15T13-25-43-918Z-compare",
        "promptfoo_eval_id": "eval-UTJ-2026-07-15T13:25:51",
        "planned_answer_count": 90,
        "stop_decision_completed_row_count": 10,
        "persisted_row_count_after_process_exit": 12,
        "termination": "intentional-source-provenance-gate-stop",
        "benchmark_eligible": False,
        "exclusion_reason": (
            "The consultation skill instructions changed after workspace materialization, "
            "so the materialized treatment was not byte-identical to the final frozen package."
        ),
    }:
        raise EvaluationError("source-provenance diagnostic comparison differs")

    provenance = exact_keys(
        report["provenance"],
        {
            "execution_log",
            "generated_promptfoo_config",
            "database_projection",
            "promptfoo_results_file_present",
        },
        "source-provenance diagnostic provenance",
    )
    expected_raw_paths = {
        "execution_log": (
            "results/semantic-okf-ensemble-hard10-three-arm/"
            "2026-07-15T13-25-43-918Z-compare/execution.log"
        ),
        "generated_promptfoo_config": (
            "results/semantic-okf-ensemble-hard10-three-arm/"
            "2026-07-15T13-25-43-918Z-compare/promptfooconfig.yaml"
        ),
    }
    expected_raw_hashes = {
        "execution_log": "e1bd818fc25027974e0ffa8cf10ccc45acf2c92c251da8b46c9ce01f58d669f2",
        "generated_promptfoo_config": (
            "c704483180a81d0ce3eb09f0d28d64812be4b78693dadf28b62bb58a2f2b30db"
        ),
    }
    for key, expected_path in expected_raw_paths.items():
        binding = exact_keys(
            provenance[key],
            {"path", "sha256"},
            f"source-provenance diagnostic {key}",
        )
        if binding != {"path": expected_path, "sha256": expected_raw_hashes[key]}:
            raise EvaluationError(f"source-provenance diagnostic {key} binding differs")
    projection = exact_keys(
        provenance["database_projection"],
        {"description", "sha256", "row_count"},
        "source-provenance diagnostic database projection",
    )
    if (
        projection["sha256"]
        != "f97f3375224396265c361dfcb5126250a06bb0691c57f6548ba9e1d0e12cb0b6"
        or projection["row_count"] != 12
        or not isinstance(projection["description"], str)
        or not projection["description"]
        or provenance["promptfoo_results_file_present"] is not False
    ):
        raise EvaluationError("source-provenance diagnostic database projection differs")

    materialized = exact_keys(
        report["materialized_source"],
        {
            "skill_arena_config_sha256",
            "skill_arena_config_manifest_sha256",
            "consult_skill_tree_sha256",
            "consult_skill_md_sha256",
        },
        "source-provenance diagnostic materialized source",
    )
    if materialized != {
        "skill_arena_config_sha256": (
            "be443278a2eab287a78945f5bf8f42a5bcb7f49153476901b042b8aeb2d9564b"
        ),
        "skill_arena_config_manifest_sha256": (
            "aef045edf27f97f608ac51b760147396e9c8781703419b50ac9d4c8137f90c97"
        ),
        "consult_skill_tree_sha256": (
            "e99b40283a67a2c801cee7cc4815e07015b400c802d02d00756d6731e8f52544"
        ),
        "consult_skill_md_sha256": (
            "fe975a3ef7f525bbe5355ccacce359312bd61fdc1bb315febd04e1894998f7f8"
        ),
    }:
        raise EvaluationError("source-provenance diagnostic materialized source differs")

    final_source = exact_keys(
        report["final_frozen_source"],
        {
            "skill_arena_config_sha256",
            "skill_arena_config_manifest_sha256",
            "consult_skill_tree_sha256",
            "consult_skill_md_sha256",
            "querying_reference_sha256",
        },
        "source-provenance diagnostic final source",
    )
    # These are the exact replacement identities frozen for the immediately
    # following (also historical) rerun, not aliases for the current package.
    expected_final_source = {
        "skill_arena_config_sha256": (
            "be443278a2eab287a78945f5bf8f42a5bcb7f49153476901b042b8aeb2d9564b"
        ),
        "skill_arena_config_manifest_sha256": (
            "4d4eea215d8b819baf363c0e52cbe974fa57f90757ce4a43a4a59fd2bcb85235"
        ),
        "consult_skill_tree_sha256": (
            "773b36e85d761f9d1bff1c46840386ec4c3c027e9aca906ee8612827883ddf37"
        ),
        "consult_skill_md_sha256": (
            "5d5970fcd4bc7a4fff655da06ddc41dcc7f8c2e10438b3d2e8731f720e5a09be"
        ),
        "querying_reference_sha256": (
            "84e906c78e9c0f7a72f5ca270d777c0ab850efc534e802b63ecbfc150d82b635"
        ),
    }
    if final_source != expected_final_source:
        raise EvaluationError("source-provenance diagnostic final frozen source differs")
    if final_source["consult_skill_tree_sha256"] == materialized["consult_skill_tree_sha256"]:
        raise EvaluationError("source-provenance diagnostic does not prove source drift")

    persisted = exact_keys(
        report["persisted_rows"],
        {"total", "by_profile", "quality_metrics_published"},
        "source-provenance diagnostic persisted rows",
    )
    if persisted != {
        "total": 12,
        "by_profile": {
            "knowledge-only-control": 4,
            "adaptive-consult-control": 4,
            "ensemble-consult-treatment": 4,
        },
        "quality_metrics_published": False,
    }:
        raise EvaluationError("source-provenance diagnostic persisted rows differ")
    decision = exact_keys(
        report["decision"],
        {"observed_failure", "acceptance_rule", "remediation"},
        "source-provenance diagnostic decision",
    )
    if any(not isinstance(value, str) or not value for value in decision.values()):
        raise EvaluationError("source-provenance diagnostic decision differs")
    if not isinstance(report["raw_retention"], str) or not report["raw_retention"]:
        raise EvaluationError("source-provenance diagnostic raw-retention note differs")
    _reject_absolute_paths(report, "source-provenance diagnostic")
    canonical = (json.dumps(report, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    if SOURCE_PROVENANCE_DIAGNOSTIC.read_bytes() != canonical:
        raise EvaluationError("source-provenance diagnostic JSON is not canonical")
    if sha256(SOURCE_PROVENANCE_DIAGNOSTIC) != SOURCE_PROVENANCE_DIAGNOSTIC_SHA256:
        raise EvaluationError("source-provenance diagnostic JSON binding differs")
    if (
        sha256(SOURCE_PROVENANCE_DIAGNOSTIC_MARKDOWN)
        != SOURCE_PROVENANCE_DIAGNOSTIC_MARKDOWN_SHA256
    ):
        raise EvaluationError("source-provenance diagnostic Markdown binding differs")
    return report


def validate_candidate_copy_failure_diagnostic() -> dict[str, Any]:
    """Keep the failed long-candidate confirmation run out of benchmark metrics."""

    if not CANDIDATE_COPY_DIAGNOSTIC.is_file():
        raise EvaluationError("candidate-copy diagnostic JSON is missing")
    report = load_json(CANDIDATE_COPY_DIAGNOSTIC)
    exact_keys(
        report,
        {
            "schema_version",
            "status",
            "evidence_class",
            "date",
            "comparison",
            "provenance",
            "materialized_source",
            "observed_failure",
            "replacement_protocol",
            "persisted_rows",
            "decision",
            "raw_retention",
        },
        "candidate-copy diagnostic",
    )
    if (
        report["schema_version"]
        != "semantic-okf-ensemble-candidate-copy-confirmation-failure-diagnostic/1.0"
        or report["status"] != "rejected"
        or report["evidence_class"] != "diagnostic-only-non-benchmark"
        or report["date"] != "2026-07-15"
    ):
        raise EvaluationError("candidate-copy diagnostic identity differs")

    comparison = exact_keys(
        report["comparison"],
        {
            "run_id",
            "promptfoo_eval_id",
            "planned_answer_count",
            "stop_decision_completed_row_count",
            "persisted_row_count_after_process_exit",
            "termination",
            "benchmark_eligible",
            "exclusion_reason",
        },
        "candidate-copy diagnostic comparison",
    )
    if comparison != {
        "run_id": "2026-07-15T13-50-35-550Z-compare",
        "promptfoo_eval_id": "eval-d9Z-2026-07-15T13:50:43",
        "planned_answer_count": 90,
        "stop_decision_completed_row_count": 4,
        "persisted_row_count_after_process_exit": 5,
        "termination": "intentional-protocol-quality-gate-stop",
        "benchmark_eligible": False,
        "exclusion_reason": (
            "The first ensemble-treatment row failed long candidate_json confirmation, "
            "so the incomplete comparison does not satisfy the publication protocol gate."
        ),
    }:
        raise EvaluationError("candidate-copy diagnostic comparison differs")

    provenance = exact_keys(
        report["provenance"],
        {
            "execution_log",
            "generated_promptfoo_config",
            "database_projection",
            "promptfoo_results_file_present",
        },
        "candidate-copy diagnostic provenance",
    )
    if provenance["execution_log"] != {
        "path": (
            "results/semantic-okf-ensemble-hard10-three-arm/"
            "2026-07-15T13-50-35-550Z-compare/execution.log"
        ),
        "sha256": "b762ea1763d3b169369a9e68adbf39531ef47061906a1b93f5c3c261e5a17b1b",
    } or provenance["generated_promptfoo_config"] != {
        "path": (
            "results/semantic-okf-ensemble-hard10-three-arm/"
            "2026-07-15T13-50-35-550Z-compare/promptfooconfig.yaml"
        ),
        "sha256": "31ce9b7ae940bc5ba99e547679bf065afe04593861dd9e4d1d2efdb4c18b065b",
    }:
        raise EvaluationError("candidate-copy diagnostic raw provenance differs")
    projection = exact_keys(
        provenance["database_projection"],
        {"description", "sha256", "row_count"},
        "candidate-copy diagnostic database projection",
    )
    if (
        projection["sha256"]
        != "332e7fcea3d167b2e3baace36965ab058a21862b1e9caef1ee9c98138a27d6a6"
        or projection["row_count"] != 5
        or not isinstance(projection["description"], str)
        or not projection["description"]
        or provenance["promptfoo_results_file_present"] is not False
    ):
        raise EvaluationError("candidate-copy diagnostic database projection differs")

    materialized = exact_keys(
        report["materialized_source"],
        {
            "skill_arena_config_sha256",
            "skill_arena_config_manifest_sha256",
            "consult_skill_tree_sha256",
            "consult_skill_md_sha256",
            "mcp_server_version",
            "mcp_runtime_tree_sha256",
            "mcp_server_sha256",
            "publication_runtime_tree_sha256",
            "publication_script_sha256",
        },
        "candidate-copy diagnostic materialized source",
    )
    if materialized != {
        "skill_arena_config_sha256": (
            "be443278a2eab287a78945f5bf8f42a5bcb7f49153476901b042b8aeb2d9564b"
        ),
        "skill_arena_config_manifest_sha256": (
            "4d4eea215d8b819baf363c0e52cbe974fa57f90757ce4a43a4a59fd2bcb85235"
        ),
        "consult_skill_tree_sha256": (
            "773b36e85d761f9d1bff1c46840386ec4c3c027e9aca906ee8612827883ddf37"
        ),
        "consult_skill_md_sha256": (
            "5d5970fcd4bc7a4fff655da06ddc41dcc7f8c2e10438b3d2e8731f720e5a09be"
        ),
        "mcp_server_version": "1.3.1",
        "mcp_runtime_tree_sha256": (
            "f2dd193140a092dc1ac7497605f3f06c6e5b51ef7048bc8ea1c72ef77c57782b"
        ),
        "mcp_server_sha256": (
            "4dcdc12980754d1ce9a757fa62a1ca3a38b0e3fd6157f70a2d5f3a536faeca00"
        ),
        "publication_runtime_tree_sha256": (
            "e4afa47f3d576d0cc86d4eb26684c3db2325d82113a0dbabaa4ca2a07a9e281e"
        ),
        "publication_script_sha256": (
            "27be691c18f76f364bf4910b905e54ad6bbaa15f38b8ca948676318fe6c553a5"
        ),
    }:
        raise EvaluationError("candidate-copy diagnostic materialized source differs")

    failure = exact_keys(
        report["observed_failure"],
        {
            "profile_id",
            "question_id",
            "test_index",
            "classification",
            "protocol_sequence",
            "provider_error_sha256",
            "provider_error_byte_count",
        },
        "candidate-copy diagnostic observed failure",
    )
    if failure != {
        "profile_id": "ensemble-consult-treatment",
        "question_id": "q031-graph-routing-boundary",
        "test_index": 0,
        "classification": "long-candidate-confirmation-copy-failure",
        "protocol_sequence": "[prepare:completed:no-error,confirm:failed:no-error]",
        "provider_error_sha256": (
            "5a22fed71c603b03d6523cb294c60135fd3ccd8a4ea900a6d07202e298a7a19e"
        ),
        "provider_error_byte_count": 160,
    }:
        raise EvaluationError("candidate-copy diagnostic observed failure differs")

    replacement = exact_keys(
        report["replacement_protocol"],
        {
            "mcp_server_version",
            "mcp_runtime_tree_sha256",
            "mcp_server_sha256",
            "publication_runtime_tree_sha256",
            "publication_script_sha256",
            "prepared_answer_schema",
            "prepared_answer_key_order",
            "candidate_digest_binding",
            "confirmation_argument",
            "confirmation_argument_pattern",
            "confirmation_receipt_schema",
            "confirmation_receipt_key_order",
            "published_bytes_source",
        },
        "candidate-copy diagnostic replacement protocol",
    )
    expected_replacement = {
        "mcp_server_version": "1.4.0",
        # These identities belong to the retained v1.4.0 diagnostic.  They are
        # intentionally historical rather than aliases for the active v1.5.0
        # runtime, whose files have since evolved.
        "mcp_runtime_tree_sha256": (
            "8c499ee0b485c3abc9f1883e199b2b2131dfe062642740e9072ea7cda088386b"
        ),
        "mcp_server_sha256": (
            "1a0f4f952934dcd6f5bfa8ac08a5817c8e5dd8a9e0d44d1e67ad0737d6522cd4"
        ),
        "publication_runtime_tree_sha256": (
            "f020129e302ebe52c0d6d55978a559a7a40c8081d38bcdd5c031680ad004cbf2"
        ),
        "publication_script_sha256": (
            "f8d420ce792ccd72fb0ed187462ae9c467f850af422739deca61e4d1b058ff95"
        ),
        "prepared_answer_schema": "semantic-okf-prepared-answer/1.0",
        "prepared_answer_key_order": [
            "schema",
            "candidate_json",
            "response_sha256",
            "byte_count",
        ],
        "candidate_digest_binding": "sha256-lowercase-hex-of-utf8-candidate-json",
        "confirmation_argument": "response_sha256",
        "confirmation_argument_pattern": "^[0-9a-f]{64}$",
        "confirmation_receipt_schema": "semantic-okf-answer-confirmation-receipt/1.0",
        "confirmation_receipt_key_order": [
            "schema",
            "status",
            "response_sha256",
            "byte_count",
        ],
        "published_bytes_source": "prepared-envelope-candidate-json-bytes",
    }
    if replacement != expected_replacement:
        raise EvaluationError("candidate-copy diagnostic replacement protocol differs")

    persisted = exact_keys(
        report["persisted_rows"],
        {"total", "by_profile", "quality_metrics_published"},
        "candidate-copy diagnostic persisted rows",
    )
    if persisted != {
        "total": 5,
        "by_profile": {
            "knowledge-only-control": 2,
            "adaptive-consult-control": 2,
            "ensemble-consult-treatment": 1,
        },
        "quality_metrics_published": False,
    }:
        raise EvaluationError("candidate-copy diagnostic persisted rows differ")
    decision = exact_keys(
        report["decision"],
        {"observed_failure", "acceptance_rule", "remediation"},
        "candidate-copy diagnostic decision",
    )
    if any(not isinstance(value, str) or not value for value in decision.values()):
        raise EvaluationError("candidate-copy diagnostic decision differs")
    if not isinstance(report["raw_retention"], str) or not report["raw_retention"]:
        raise EvaluationError("candidate-copy diagnostic raw-retention note differs")
    _reject_absolute_paths(report, "candidate-copy diagnostic")
    canonical = (json.dumps(report, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    if CANDIDATE_COPY_DIAGNOSTIC.read_bytes() != canonical:
        raise EvaluationError("candidate-copy diagnostic JSON is not canonical")
    if sha256(CANDIDATE_COPY_DIAGNOSTIC) != CANDIDATE_COPY_DIAGNOSTIC_SHA256:
        raise EvaluationError("candidate-copy diagnostic JSON binding differs")
    return report


def validate_finalizer_copy_integrity_diagnostic() -> dict[str, Any]:
    """Retain the rejected single-phase run as closed, explicitly non-accepted evidence."""

    if not FINALIZER_COPY_DIAGNOSTIC.is_file():
        raise EvaluationError("finalizer copy-integrity diagnostic JSON is missing")
    if not FINALIZER_COPY_DIAGNOSTIC_MARKDOWN.is_file():
        raise EvaluationError("finalizer copy-integrity diagnostic Markdown is missing")
    report = load_json(FINALIZER_COPY_DIAGNOSTIC)
    exact_keys(
        report,
        {
            "schema_version",
            "status",
            "date",
            "comparison",
            "bindings",
            "completed_rows",
            "treatment_copy_integrity",
            "per_question",
            "observed_failure",
            "raw_retention",
        },
        "finalizer copy-integrity diagnostic",
    )
    if (
        report["schema_version"]
        != "semantic-okf-ensemble-finalizer-copy-integrity-diagnostic/1.0"
        or report["status"] != "rejected"
        or report["date"] != "2026-07-15"
    ):
        raise EvaluationError("finalizer copy-integrity diagnostic schema, status, or date differs")
    comparison = exact_keys(
        report["comparison"],
        {
            "run_id",
            "promptfoo_eval_id",
            "planned_answer_count",
            "completed_answer_count",
            "termination",
        },
        "finalizer diagnostic comparison",
    )
    if comparison != {
        "run_id": "2026-07-15T09-58-38-815Z-compare",
        "promptfoo_eval_id": "eval-C2x-2026-07-15T09:58:45",
        "planned_answer_count": 90,
        "completed_answer_count": 46,
        "termination": "intentional-quality-gate-stop",
    }:
        raise EvaluationError("finalizer copy-integrity diagnostic comparison differs")
    bindings = exact_keys(
        report["bindings"],
        {
            "skill_arena_config_sha256",
            "skill_arena_config_manifest_sha256",
            "consult_skill_package_tree_sha256",
            "consult_skill_sha256",
            "mcp_runtime_tree_sha256",
            "mcp_server_sha256",
        },
        "finalizer diagnostic bindings",
    )
    if any(
        not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{64}", value) is None
        for value in bindings.values()
    ):
        raise EvaluationError("finalizer copy-integrity diagnostic contains an invalid SHA-256")
    completed = exact_keys(
        report["completed_rows"],
        {
            "knowledge-only-control",
            "adaptive-consult-control",
            "ensemble-consult-treatment",
        },
        "finalizer diagnostic completed rows",
    )
    if completed != {
        "knowledge-only-control": 16,
        "adaptive-consult-control": 15,
        "ensemble-consult-treatment": 15,
    } or sum(completed.values()) != comparison["completed_answer_count"]:
        raise EvaluationError("finalizer copy-integrity diagnostic completed-row counts differ")
    integrity = exact_keys(
        report["treatment_copy_integrity"],
        {
            "completed_single_phase_finalizer_calls",
            "exact_visible_output_matches",
            "mismatches",
            "exact_match_rate",
            "comparison",
        },
        "finalizer diagnostic treatment integrity",
    )
    total = integrity["completed_single_phase_finalizer_calls"]
    matches = integrity["exact_visible_output_matches"]
    mismatches = integrity["mismatches"]
    if (
        total != completed["ensemble-consult-treatment"]
        or matches != 5
        or mismatches != 10
        or matches + mismatches != total
        or not isinstance(integrity["exact_match_rate"], (int, float))
        or abs(float(integrity["exact_match_rate"]) - matches / total) > 1e-8
        or integrity["comparison"]
        != "UTF-8 finalizer text and visible model output after trimming outer whitespace"
    ):
        raise EvaluationError("finalizer copy-integrity diagnostic arithmetic differs")
    questions = report["per_question"]
    expected_questions = [
        ("q031-graph-routing-boundary", 3, 0),
        ("q032-incremental-update-maturity", 3, 2),
        ("q033-corruption-specific-defenses", 3, 1),
        ("q034-nonmonotonic-context-budget", 3, 1),
        ("q035-lossless-enough-evidence-organization", 3, 1),
    ]
    if not isinstance(questions, list) or len(questions) != len(expected_questions):
        raise EvaluationError("finalizer copy-integrity per-question rows differ")
    for row, expected in zip(questions, expected_questions, strict=True):
        exact_keys(
            row,
            {"question_id", "treatment_rows", "exact_matches"},
            "finalizer diagnostic question row",
        )
        if (row["question_id"], row["treatment_rows"], row["exact_matches"]) != expected:
            raise EvaluationError("finalizer copy-integrity per-question counts differ")
    if (
        sum(row["treatment_rows"] for row in questions) != total
        or sum(row["exact_matches"] for row in questions) != matches
    ):
        raise EvaluationError("finalizer copy-integrity per-question arithmetic differs")
    failure = exact_keys(
        report["observed_failure"],
        {"class", "example", "impact", "required_remediation"},
        "finalizer diagnostic observed failure",
    )
    if failure["class"] != "post-finalizer-copy-mutation" or any(
        not isinstance(failure[key], str) or not failure[key]
        for key in ("example", "impact", "required_remediation")
    ):
        raise EvaluationError("finalizer copy-integrity observed failure differs")
    if not isinstance(report["raw_retention"], str) or not report["raw_retention"]:
        raise EvaluationError("finalizer copy-integrity raw-retention note differs")
    _reject_absolute_paths(report)
    expected_json = (json.dumps(report, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    if FINALIZER_COPY_DIAGNOSTIC.read_bytes() != expected_json:
        raise EvaluationError("finalizer copy-integrity JSON is not canonical")
    if sha256(FINALIZER_COPY_DIAGNOSTIC) != FINALIZER_COPY_DIAGNOSTIC_SHA256:
        raise EvaluationError("finalizer copy-integrity JSON binding differs")
    if sha256(FINALIZER_COPY_DIAGNOSTIC_MARKDOWN) != FINALIZER_COPY_DIAGNOSTIC_MARKDOWN_SHA256:
        raise EvaluationError("finalizer copy-integrity Markdown binding differs")
    return report


def validate_final_integrity_reports(plan: dict[str, Any]) -> None:
    """Validate compact build and manual-query evidence without requiring ignored bundles."""

    build = load_json(BUILD_VALIDATION)
    exact_keys(
        build,
        {
            "schema_version", "status", "run_id", "runtime", "inputs", "publication",
            "authoritative_core", "deterministic_rebuild", "gates",
        },
        "final build validation",
    )
    if build["schema_version"] != "semantic-okf-ensemble-build-validation/1.0":
        raise EvaluationError("final build validation schema_version differs")
    if build["status"] != "pass" or build["run_id"] != "20260715-ensemble-final-03":
        raise EvaluationError("final build validation status or run_id differs")
    plan_binding = build.get("inputs", {}).get("ensemble_plan", {})
    if plan_binding.get("path") != "evaluations/semantic-okf-ensemble/ensemble-plan.json":
        raise EvaluationError("final build validation plan path differs")
    if plan_binding.get("file_sha256") != sha256(ENSEMBLE_PLAN):
        raise EvaluationError("final build validation plan file SHA-256 differs")
    canonical_plan_sha = hashlib.sha256(canonical_json(plan).encode("utf-8")).hexdigest()
    if plan_binding.get("canonical_sha256") != canonical_plan_sha:
        raise EvaluationError("final build validation canonical plan SHA-256 differs")
    publication = build.get("publication", {})
    if publication.get("authoritative") is not False or publication.get("discovery_only") is not True:
        raise EvaluationError("final build validation authority boundary differs")
    if publication.get("atomic") is not True or publication.get("independently_validated") is not True:
        raise EvaluationError("final build publication gates differ")
    core = build.get("authoritative_core", {})
    if core != {
        "record_count": 874,
        "records_sha256": "df06f8ed7fd0ca4b2b8b5761c637a79d525595a2c180aeaf6885555e266754dc",
        "tree_sha256": "331af2f1064463484f64dfaa58bc17d6c6b2f75ef3fca9d371473450deb84424",
        "matches_preexisting_alternatives": True,
    }:
        raise EvaluationError("final build authoritative-core identity differs")
    rebuild = build.get("deterministic_rebuild", {})
    if rebuild.get("build_count") != 2 or rebuild.get("path_or_sha256_differences") != 0:
        raise EvaluationError("final build deterministic-rebuild counts differ")
    if rebuild.get("exact_match") is not True or rebuild.get("files_a") != rebuild.get("files_b"):
        raise EvaluationError("final build deterministic-rebuild gate differs")
    gates = build.get("gates", {})
    if not isinstance(gates, dict) or not gates or any(value is not True for value in gates.values()):
        raise EvaluationError("one or more final build gates did not pass")

    manual = load_json(MANUAL_VERIFICATION)
    exact_keys(
        manual,
        {
            "schema_version", "status", "run_id", "question", "bundle", "search",
            "coverage", "finalizer", "conclusion",
        },
        "final manual-query verification",
    )
    if manual["schema_version"] != "semantic-okf-ensemble-manual-query-verification/1.0":
        raise EvaluationError("final manual-query schema_version differs")
    if manual["status"] != "pass" or manual["run_id"] != build["run_id"]:
        raise EvaluationError("final manual-query status or run_id differs")
    question = manual.get("question", {})
    question_path = REPO_ROOT / str(question.get("source_path", ""))
    if question.get("id") != "q031-graph-routing-boundary" or not question_path.is_file():
        raise EvaluationError("final manual-query question binding differs")
    if question.get("source_sha256") != sha256(question_path):
        raise EvaluationError("final manual-query question SHA-256 differs")
    bundle = manual.get("bundle", {})
    if bundle.get("unchanged") is not True or bundle.get("recursive_sha256_before") != bundle.get("recursive_sha256_after"):
        raise EvaluationError("final manual-query read-only tree gate differs")
    if bundle.get("ensemble_index_sha256") != publication.get("ensemble_index_sha256"):
        raise EvaluationError("manual-query and build ensemble-index identities differ")
    if bundle.get("ensemble_plan_sha256") != plan_binding.get("canonical_sha256"):
        raise EvaluationError("manual-query and build canonical plan identities differ")
    if bundle.get("core_tree_sha256") != core.get("tree_sha256"):
        raise EvaluationError("manual-query and build core identities differ")
    search = manual.get("search", {})
    if search.get("status") != "pass" or search.get("algorithm") != "protected-multisignal-paper-rerank-v2":
        raise EvaluationError("final manual-query search identity differs")
    if search.get("protected_candidate_set_preserved") is not True or search.get("promotion_gate_passed") is not True:
        raise EvaluationError("final manual-query search gates differ")
    if search.get("required_papers_returned") != search.get("required_papers_expected"):
        raise EvaluationError("final manual-query required-paper gate differs")
    coverage = manual.get("coverage", {})
    coverage_path = REPO_ROOT / str(coverage.get("report_path", ""))
    if not coverage_path.is_file() or coverage.get("report_sha256") != sha256(coverage_path):
        raise EvaluationError("final manual-query coverage report binding differs")
    if coverage.get("status") != "pass" or coverage.get("important_negative_groups_covered") != coverage.get("important_negative_groups_expected"):
        raise EvaluationError("final manual-query coverage gates differ")
    finalizer = manual.get("finalizer", {})
    draft_path = REPO_ROOT / str(finalizer.get("draft_path", ""))
    if not draft_path.is_file() or finalizer.get("draft_sha256") != sha256(draft_path):
        raise EvaluationError("final manual-query draft binding differs")
    if finalizer.get("status") != "pass" or finalizer.get("only_gated_claim_ids_used") is not True:
        raise EvaluationError("final manual-query finalizer gate differs")
    if finalizer.get("citation_pages_are_integers") is not True or finalizer.get("evidence_paths_are_relative") is not True:
        raise EvaluationError("final manual-query output-contract gate differs")

    if sha256(EXPECTED_ID_AUDIT) != EXPECTED_ID_AUDIT_SHA256:
        raise EvaluationError("final expected-ID audit binding differs")
    expected_ids = load_json(EXPECTED_ID_AUDIT)
    exact_keys(
        expected_ids,
        {
            "schema_version",
            "status",
            "run_id",
            "reviewed_benchmark_id",
            "inputs",
            "counts",
            "gates",
            "report_markdown",
            "conclusion",
        },
        "final expected-ID audit",
    )
    if expected_ids["schema_version"] != "semantic-okf-ensemble-expected-id-audit/1.1":
        raise EvaluationError("final expected-ID audit schema_version differs")
    if expected_ids["status"] != "pass" or expected_ids["run_id"] != build["run_id"]:
        raise EvaluationError("final expected-ID audit status or run_id differs")
    reviewed = validate_reviewed_benchmark()
    if expected_ids["reviewed_benchmark_id"] != reviewed["manifest"]["benchmark_id"]:
        raise EvaluationError("final expected-ID audit reviewed benchmark differs")
    inputs = expected_ids.get("inputs", {})
    exact_keys(
        inputs,
        {
            "audit_script",
            "frozen_benchmark",
            "hard_ground_truth_manifest",
            "hard_ground_truth",
            "skill_arena_config",
            "answer_bindings",
            "authoritative_records",
        },
        "final expected-ID audit inputs",
    )
    expected_bound_paths = {
        "audit_script": REPO_ROOT
        / "evaluations/semantic-okf-adaptive-evolution/scripts/audit_expected_ids.py",
        "frozen_benchmark": REVIEWED_FROZEN_BENCHMARK,
        "hard_ground_truth_manifest": REVIEWED_GROUND_TRUTH_MANIFEST,
        "hard_ground_truth": REVIEWED_GROUND_TRUTH,
        "skill_arena_config": SKILL_ARENA_CONFIG,
    }
    for key, expected_path in expected_bound_paths.items():
        if bound_file(inputs[key], f"final expected-ID audit {key}") != expected_path.resolve():
            raise EvaluationError(f"final expected-ID audit {key} path differs")
    bundle_root = REPO_ROOT / (
        "evaluations/semantic-okf-ensemble/results/runs/"
        "20260715-ensemble-final-03/workspace-a/knowledge"
    )
    answer_bindings = exact_keys(
        inputs["answer_bindings"],
        {"bundle_path", "path", "sha256", "count"},
        "final expected-ID audit answer bindings",
    )
    if answer_bindings != {
        "bundle_path": bundle_root.relative_to(REPO_ROOT).as_posix(),
        "path": "adaptive/answer-bindings.jsonl",
        "sha256": HISTORICAL_ANSWER_BINDINGS_SHA256,
        "count": 831,
    }:
        raise EvaluationError("final expected-ID audit answer-binding identity differs")
    records = inputs["authoritative_records"]
    if records != {
        "bundle_path": bundle_root.relative_to(REPO_ROOT).as_posix(),
        "path": "semantic/records.jsonl",
        "sha256": core["records_sha256"],
        "count": 874,
    }:
        raise EvaluationError("final expected-ID audit authoritative-record binding differs")
    if expected_ids.get("counts") != {
        "questions": 10,
        "atomic_answer_groups": 44,
        "important_negative_groups": 13,
        "reviewed_expected_id_links": 113,
        "unique_authoritative_claims": 68,
        "authoritative_evidence_objects": 71,
        "config_question_checks": 10,
        "config_assertion_blocks": 40,
    }:
        raise EvaluationError("final expected-ID audit counts differ")
    expected_gates = expected_ids.get("gates", {})
    if not isinstance(expected_gates, dict) or not expected_gates or any(value is not True for value in expected_gates.values()):
        raise EvaluationError("one or more final expected-ID audit gates did not pass")
    markdown_binding = exact_keys(
        expected_ids["report_markdown"],
        {"path", "sha256"},
        "final expected-ID audit Markdown",
    )
    if bound_file(markdown_binding, "final expected-ID audit Markdown") != EXPECTED_ID_AUDIT_MARKDOWN.resolve():
        raise EvaluationError("final expected-ID audit Markdown path differs")

    # Reproduce the authoritative claim universe from the checked-in publication
    # bundle. The ignored final-03 runtime supplied the same Semantic records, but
    # is historical run output and is deliberately absent from a clean checkout.
    generator = module_from_path(
        "semantic_okf_ensemble_checked_integrity_generator",
        SKILL_ARENA_CONFIG_GENERATOR,
    )
    try:
        replay_questions = generator._load_reviewed_ground_truth(REPO_ROOT)
        evidence_bundle, claim_records = generator._load_claim_records(REPO_ROOT)
        all_allowed = generator._all_claim_bindings(evidence_bundle, claim_records)
        replay_contracts = [
            generator._claim_contract(
                question,
                evidence_bundle,
                claim_records,
                all_allowed,
            )
            for question in replay_questions
        ]
    except (OSError, UnicodeError, ValueError, KeyError, TypeError, RuntimeError) as exc:
        raise EvaluationError(f"reviewed expected-ID audit reproduction failed: {exc}") from exc
    replay_links = [
        claim_id
        for question in replay_questions
        for family in ("answer_claims", "important_negatives")
        for option in question["ground_truth"][family]
        for claim_id in option["evidence_claim_ids"]
    ]
    if (
        len(replay_questions) != 10
        or len(replay_contracts) != 10
        or len(all_allowed) != answer_bindings["count"]
        or len(replay_links) != 113
        or len(set(replay_links)) != 68
        or any(contract["allowed"] != all_allowed for contract in replay_contracts)
    ):
        raise EvaluationError("reviewed expected-ID audit reproduction counts differ")
    if "or_option_sets" not in expected_bound_paths["audit_script"].read_text(encoding="utf-8"):
        raise EvaluationError("reviewed expected-ID audit omits OR-set semantics")
    expected_bytes = (json.dumps(expected_ids, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    if EXPECTED_ID_AUDIT.read_bytes() != expected_bytes:
        raise EvaluationError("final expected-ID audit JSON is not canonical")


def validate() -> dict[str, Any]:
    """Validate every checked-in scaffold contract without writing state."""

    validate_frozen()
    historical_mcp_evidence = validate_historical_mcp_evidence_binding()
    active_cli_consult = validate_active_cli_consult_skill()
    reviewed_benchmark = validate_reviewed_benchmark()
    plan = validate_builder_plan()
    validate_policy(plan)
    validate_contract(plan)
    config = validate_config(load_json(POPULATION))
    generation = load_json(GENERATION)
    candidate_ids = validate_generation(generation, config)
    validate_no_candidate_leakage(generation)
    validate_report(load_json(POPULATION_RESULTS), config, generation)
    validate_checked_reports()
    validate_final_integrity_reports(plan)
    coverage_report = validate_accepted_coverage_report(plan)
    skill_arena_manifest = validate_skill_arena_manifest()
    answer_output_report = validate_checked_answer_output_report()
    mcp_runtime_attestation = validate_checked_mcp_runtime_attestation(
        answer_output_report
    )
    finalizer_copy_diagnostic = validate_finalizer_copy_integrity_diagnostic()
    host_publication_diagnostic = validate_host_publication_mutation_diagnostic()
    source_provenance_diagnostic = validate_source_provenance_drift_diagnostic()
    candidate_copy_diagnostic = validate_candidate_copy_failure_diagnostic()
    skill_bootstrap_diagnostic = validate_skill_bootstrap_isolation_diagnostic()
    bootstrap_preflight = validate_bootstrap_isolation_technical_preflight()
    required_scripts = {
        "_answer_output.py",
        "aggregate_answer_output_evaluation.py",
        "attest_skill_arena_mcp_runtime.py",
        "compare_direct_retrieval.py",
        "evaluate_hard10_coverage_pack.py",
        "evaluate_hard10_graph_coverage.py",
        "generate_reviewed_answer_benchmark.py",
        "generate_skill_arena_config.py",
        "prepare_answer_output_evaluation.py",
        "rank_population.py",
        "run_blinded_answer_reviews.py",
        "run_frozen_retrieval.py",
        "summarize_population_search.py",
        "validate_scaffold.py",
    }
    missing = sorted(name for name in required_scripts if not (EVALUATION_ROOT / "scripts" / name).is_file())
    if missing:
        raise EvaluationError(f"missing evaluation scripts: {missing}")
    return {
        "status": "pass",
        "frozen_benchmark_sha256": validate_frozen()["manifest_sha256"],
        "reviewed_answer_benchmark_sha256": reviewed_benchmark["manifest_sha256"],
        "reviewed_ground_truth_sha256": reviewed_benchmark["ground_truth_sha256"],
        "ensemble_plan_sha256": sha256(ENSEMBLE_PLAN),
        "evaluation_contract_sha256": sha256(CONTRACT),
        "population_config_sha256": sha256(POPULATION),
        "generation_sha256": sha256(GENERATION),
        "population_results_sha256": sha256(POPULATION_RESULTS),
        "answer_output_contract_sha256": sha256(ANSWER_OUTPUT_CONTRACT),
        "answer_output_report_sha256": sha256(ANSWER_OUTPUT_REPORT),
        "answer_output_markdown_sha256": sha256(ANSWER_OUTPUT_MARKDOWN),
        "answer_output_answer_count": answer_output_report["answer_count"],
        "historical_mcp_source_commit": historical_mcp_evidence["source_commit"],
        "historical_mcp_evidence_binding_sha256": sha256(
            HISTORICAL_MCP_EVIDENCE
        ),
        "mcp_runtime_attestation_sha256": sha256(MCP_RUNTIME_ATTESTATION),
        "mcp_runtime_attestation_markdown_sha256": sha256(
            MCP_RUNTIME_ATTESTATION_MARKDOWN
        ),
        "mcp_runtime_attested_trace_count": mcp_runtime_attestation["aggregates"][
            "trace_count"
        ],
        "active_consult_transport": "cli-only",
        "active_consult_skill_tree_sha256": active_cli_consult["tree_sha256"],
        "finalizer_copy_diagnostic_sha256": sha256(FINALIZER_COPY_DIAGNOSTIC),
        "finalizer_copy_diagnostic_markdown_sha256": sha256(
            FINALIZER_COPY_DIAGNOSTIC_MARKDOWN
        ),
        "finalizer_copy_diagnostic_completed_answers": finalizer_copy_diagnostic[
            "comparison"
        ]["completed_answer_count"],
        "host_publication_diagnostic_sha256": sha256(HOST_PUBLICATION_DIAGNOSTIC),
        "host_publication_diagnostic_markdown_sha256": sha256(
            HOST_PUBLICATION_DIAGNOSTIC_MARKDOWN
        ),
        "host_publication_diagnostic_mutated_fields": host_publication_diagnostic[
            "aggregates"
        ]["mutated_field_count"],
        "source_provenance_diagnostic_sha256": sha256(
            SOURCE_PROVENANCE_DIAGNOSTIC
        ),
        "source_provenance_diagnostic_markdown_sha256": sha256(
            SOURCE_PROVENANCE_DIAGNOSTIC_MARKDOWN
        ),
        "source_provenance_diagnostic_persisted_rows": (
            source_provenance_diagnostic["persisted_rows"]["total"]
        ),
        "candidate_copy_diagnostic_sha256": sha256(CANDIDATE_COPY_DIAGNOSTIC),
        "candidate_copy_diagnostic_persisted_rows": (
            candidate_copy_diagnostic["persisted_rows"]["total"]
        ),
        "skill_bootstrap_diagnostic_sha256": sha256(
            SKILL_BOOTSTRAP_ISOLATION_DIAGNOSTIC
        ),
        "skill_bootstrap_diagnostic_markdown_sha256": sha256(
            SKILL_BOOTSTRAP_ISOLATION_DIAGNOSTIC_MARKDOWN
        ),
        "skill_bootstrap_diagnostic_persisted_rows": skill_bootstrap_diagnostic[
            "scope"
        ]["persisted_rows_at_stop"],
        "bootstrap_isolation_preflight_sha256": sha256(
            BOOTSTRAP_ISOLATION_TECHNICAL_PREFLIGHT
        ),
        "bootstrap_isolation_preflight_markdown_sha256": sha256(
            BOOTSTRAP_ISOLATION_TECHNICAL_PREFLIGHT_MARKDOWN
        ),
        "bootstrap_isolation_preflight_completed_answers": bootstrap_preflight[
            "scope"
        ]["completed_answers"],
        "coverage_report_sha256": sha256(COVERAGE_REPORT),
        "coverage_report_markdown_sha256": sha256(COVERAGE_REPORT_MARKDOWN),
        "coverage_candidate": coverage_report["candidate"],
        "skill_arena_manifest_sha256": sha256(SKILL_ARENA_MANIFEST),
        "skill_arena_run_id": skill_arena_manifest["run_id"],
        "candidate_count": len(candidate_ids),
    }


def main(argv: Sequence[str] | None = None) -> int:
    """Run the validator."""

    if argv:
        print("error: validate_scaffold.py accepts no arguments")
        return 2
    try:
        report = validate()
    except (EvaluationError, OSError, ValueError) as exc:
        print(f"error: {exc}")
        return 2
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
