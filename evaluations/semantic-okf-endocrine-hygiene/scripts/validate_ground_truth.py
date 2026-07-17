#!/usr/bin/env python3
"""Validate the endocrine-hygiene retrieval benchmark and reviewed hard ground truth."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Mapping


EVALUATION = Path(__file__).resolve().parent.parent
REPOSITORY = EVALUATION.parent.parent
BENCHMARK = EVALUATION / "benchmark"
CORPUS = EVALUATION / "corpus"
QUESTIONS_PATH = BENCHMARK / "retrieval-questions.jsonl"
HARD_QUESTIONS_PATH = BENCHMARK / "hard-questions.jsonl"
GROUND_TRUTH_PATH = BENCHMARK / "hard-ground-truth.jsonl"
HARD_CLAIM_REQUIREMENTS_PATH = BENCHMARK / "hard-claim-requirements.json"
BENCHMARK_MANIFEST_PATH = BENCHMARK / "benchmark-manifest.json"
CORPUS_MANIFEST_PATH = CORPUS / "manifest.json"

QUESTION_ID = re.compile(r"q([0-9]{3})-[a-z0-9]+(?:-[a-z0-9]+)*")
PMCID = re.compile(r"PMC[1-9][0-9]*")
SHA256 = re.compile(r"[0-9a-f]{64}")
SOURCE_ID = re.compile(r"(?:paper|claims)-pmc[1-9][0-9]*")
LOCATOR = re.compile(r"BioC-passage-([0-9]{4})")
CLAIM_ID = re.compile(r"claim-(?P<paper>pmc[1-9][0-9]*)-(?P<ordinal>[0-9]{3})")
CLAIM_LOCATOR = re.compile(
    r"sources/markdown/(?P<paper>PMC[1-9][0-9]*)\.md#BioC-passage-(?P<passage>[0-9]{4})"
)
HARD_QUESTION_IDS = (
    "q026-receptor-to-gestation-boundary",
    "q027-feminine-risk-reconciliation",
    "q028-phthalate-name-normalization",
    "q029-label-gate-validity",
    "q030-causal-evidence-map",
)
QUESTION_TYPES = {"direct", "cross-paper", "hard"}
EVIDENCE_ROLES = {
    "data-quality-warning",
    "interpretive-hypothesis",
    "label-evidence",
    "limitation",
    "mechanistic-review",
    "methodology",
    "modeled-risk",
    "null-result",
    "observed-association",
    "observed-result",
    "product-content",
}
DERIVATION_OPERATIONS = {
    "conditional",
    "contrast",
    "evidence-map",
    "exclusion",
    "gap-analysis",
    "intersection",
    "join",
    "normalization",
}


class ValidationError(RuntimeError):
    """Describe a closed-schema or evidence-integrity failure."""


def exact_keys(value: Mapping[str, Any], expected: set[str], label: str) -> None:
    actual = set(value)
    if actual != expected:
        raise ValidationError(
            f"{label} has a closed schema; missing={sorted(expected - actual)}, "
            f"unknown={sorted(actual - expected)}"
        )


def reject_constant(value: str) -> Any:
    raise ValidationError(f"non-standard JSON number {value!r} is forbidden")


def reject_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValidationError(f"duplicate JSON member {key!r}")
        result[key] = value
    return result


def strict_json(text: str, label: str) -> Any:
    try:
        return json.loads(
            text,
            object_pairs_hook=reject_duplicates,
            parse_constant=reject_constant,
        )
    except json.JSONDecodeError as exc:
        raise ValidationError(f"{label} is invalid JSON: {exc}") from exc


def load_json(path: Path) -> Any:
    try:
        return strict_json(path.read_text(encoding="utf-8"), path.as_posix())
    except OSError as exc:
        raise ValidationError(f"cannot read {path.as_posix()}: {exc}") from exc


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ValidationError(f"cannot read {path.as_posix()}: {exc}") from exc
    if "\r" in text:
        raise ValidationError(f"{path.as_posix()} must use LF line endings")
    rows: list[dict[str, Any]] = []
    for number, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            raise ValidationError(f"{path.as_posix()}:{number} is blank")
        value = strict_json(line, f"{path.as_posix()}:{number}")
        if not isinstance(value, dict):
            raise ValidationError(f"{path.as_posix()}:{number} must be an object")
        rows.append(value)
    if not rows:
        raise ValidationError(f"{path.as_posix()} must not be empty")
    return rows


def load_corpus_claims(
    corpus_sources: Mapping[str, Mapping[str, Any]],
) -> dict[str, tuple[str, str]]:
    """Load canonical claim identity to (paper ID, evidence-text hash) bindings."""

    claims: dict[str, tuple[str, str]] = {}
    claim_sources = [
        (source_id, source)
        for source_id, source in corpus_sources.items()
        if source_id.startswith("claims-pmc")
    ]
    if not claim_sources:
        raise ValidationError("corpus manifest does not declare claims-pmc sources")
    for source_id, source in sorted(claim_sources):
        paper_id = source_id.removeprefix("claims-").upper()
        if PMCID.fullmatch(paper_id) is None:
            raise ValidationError(f"corpus claim source {source_id} has a noncanonical paper ID")
        expected_path = f"sources/claims/{paper_id}.jsonl"
        if source.get("path") != expected_path:
            raise ValidationError(f"corpus claim source {source_id} has a noncanonical path")
        candidate = (CORPUS / expected_path).resolve()
        try:
            candidate.relative_to(CORPUS.resolve())
        except ValueError as exc:
            raise ValidationError(f"corpus claim source {source_id} escapes the corpus") from exc
        for number, row in enumerate(load_jsonl(candidate), start=1):
            claim_id = row.get("id")
            claim_match = CLAIM_ID.fullmatch(claim_id) if isinstance(claim_id, str) else None
            if claim_match is None or claim_match.group("paper").upper() != paper_id:
                raise ValidationError(f"{source_id} claim {number} has a noncanonical claim ID")
            if claim_id in claims:
                raise ValidationError(f"corpus claims contain duplicate claim ID {claim_id}")
            locator = row.get("evidence_locator")
            locator_match = CLAIM_LOCATOR.fullmatch(locator) if isinstance(locator, str) else None
            if locator_match is None or locator_match.group("paper") != paper_id:
                raise ValidationError(f"{claim_id} has a noncanonical evidence locator")
            text_sha256 = row.get("evidence_text_sha256")
            if not isinstance(text_sha256, str) or SHA256.fullmatch(text_sha256) is None:
                raise ValidationError(f"{claim_id}.evidence_text_sha256 is invalid")
            claims[claim_id] = (paper_id, text_sha256)
    return claims


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sorted_unique_strings(value: Any, label: str) -> list[str]:
    if not isinstance(value, list) or not value or any(not isinstance(item, str) or not item for item in value):
        raise ValidationError(f"{label} must be a nonempty string array")
    if value != sorted(set(value)):
        raise ValidationError(f"{label} must be sorted and duplicate-free")
    return value


def unique_strings(value: Any, label: str) -> list[str]:
    if not isinstance(value, list) or not value or any(not isinstance(item, str) or not item for item in value):
        raise ValidationError(f"{label} must be a nonempty string array")
    if len(value) != len(set(value)):
        raise ValidationError(f"{label} must be duplicate-free")
    return value


def expected_source_ids(paper_ids: Iterable[str]) -> list[str]:
    return sorted(
        source_id
        for paper_id in paper_ids
        for source_id in (f"paper-{paper_id.casefold()}", f"claims-{paper_id.casefold()}")
    )


def validate_question(row: Mapping[str, Any], label: str) -> None:
    exact_keys(row, {"id", "qrels", "question", "question_type"}, label)
    identifier = row["id"]
    question = row["question"]
    question_type = row["question_type"]
    qrels = row["qrels"]
    if not isinstance(identifier, str) or QUESTION_ID.fullmatch(identifier) is None:
        raise ValidationError(f"{label}.id is invalid")
    if not isinstance(question, str) or len(question.split()) < 10 or question[-1] not in "?.":
        raise ValidationError(f"{label}.question must be a substantive question")
    if question_type not in QUESTION_TYPES:
        raise ValidationError(f"{label}.question_type is invalid")
    if not isinstance(qrels, dict):
        raise ValidationError(f"{label}.qrels must be an object")
    exact_keys(qrels, {"paper_ids", "source_ids"}, f"{label}.qrels")
    papers = sorted_unique_strings(qrels["paper_ids"], f"{label}.qrels.paper_ids")
    sources = sorted_unique_strings(qrels["source_ids"], f"{label}.qrels.source_ids")
    if any(PMCID.fullmatch(paper) is None for paper in papers):
        raise ValidationError(f"{label} has a noncanonical paper ID")
    if any(SOURCE_ID.fullmatch(source) is None for source in sources):
        raise ValidationError(f"{label} has an invalid lowercase source ID")
    if sources != expected_source_ids(papers):
        raise ValidationError(f"{label} must name both paper and claim sources for every qrel paper")
    minimum = {"direct": 1, "cross-paper": 2, "hard": 3}[question_type]
    maximum = 1 if question_type == "direct" else None
    if len(papers) < minimum or (maximum is not None and len(papers) != maximum):
        raise ValidationError(f"{label} has an invalid qrel count for {question_type}")
    if PMCID.search(question) or SHA256.search(question) or SOURCE_ID.search(question.casefold()):
        raise ValidationError(f"{label}.question leaks an identity or evidence hash")
    if "evaluations/" in question.casefold() or "bioc-passage-" in question.casefold():
        raise ValidationError(f"{label}.question leaks an authoritative locator")


def validate_questions(
    questions: list[dict[str, Any]],
    hard_questions: list[dict[str, Any]],
    corpus_paper_ids: set[str],
) -> dict[str, dict[str, Any]]:
    for number, row in enumerate(questions, start=1):
        validate_question(row, f"retrieval question {number}")
    identifiers = [row["id"] for row in questions]
    if len(identifiers) != len(set(identifiers)):
        raise ValidationError("retrieval question IDs must be unique")
    ordinals = [int(QUESTION_ID.fullmatch(identifier).group(1)) for identifier in identifiers]
    if ordinals != list(range(1, len(questions) + 1)):
        raise ValidationError("retrieval question ordinals must be contiguous and ordered")
    types = [row["question_type"] for row in questions]
    type_rank = {"direct": 0, "cross-paper": 1, "hard": 2}
    if [type_rank[item] for item in types] != sorted(type_rank[item] for item in types):
        raise ValidationError("question cohorts must be ordered direct, cross-paper, then hard")
    direct_papers = [row["qrels"]["paper_ids"][0] for row in questions if row["question_type"] == "direct"]
    if set(direct_papers) != corpus_paper_ids or len(direct_papers) != len(corpus_paper_ids):
        raise ValidationError("direct questions must cover every corpus paper exactly once")
    all_qrel_papers = {paper for row in questions for paper in row["qrels"]["paper_ids"]}
    if not all_qrel_papers <= corpus_paper_ids:
        raise ValidationError(f"questions cite papers outside the corpus: {sorted(all_qrel_papers - corpus_paper_ids)}")
    for number, row in enumerate(hard_questions, start=1):
        validate_question(row, f"hard question {number}")
        if row["question_type"] != "hard":
            raise ValidationError("hard-questions.jsonl may contain only hard questions")
    expected_hard = [row for row in questions if row["question_type"] == "hard"]
    if hard_questions != expected_hard:
        raise ValidationError("hard-questions.jsonl must be the exact hard subset of retrieval questions")
    return {row["id"]: row for row in questions}


def validate_string(value: Any, label: str, minimum_words: int = 1) -> str:
    if not isinstance(value, str) or len(value.split()) < minimum_words:
        raise ValidationError(f"{label} must be a nonempty substantive string")
    return value


def validate_evidence(
    evidence: Mapping[str, Any],
    question_id: str,
    required_papers: set[str],
    corpus_sources: Mapping[str, Mapping[str, Any]],
) -> None:
    exact_keys(
        evidence,
        {"evidence_role", "id", "locator", "paper_id", "passage", "path", "source_id", "text_sha256"},
        f"{question_id} evidence",
    )
    evidence_id = evidence["id"]
    paper_id = evidence["paper_id"]
    passage = evidence["passage"]
    source_id = evidence["source_id"]
    path = evidence["path"]
    if not isinstance(evidence_id, str) or re.fullmatch(re.escape(question_id[:4]) + r"-e[1-9][0-9]*", evidence_id) is None:
        raise ValidationError(f"{question_id} has an invalid evidence ID {evidence_id!r}")
    if paper_id not in required_papers:
        raise ValidationError(f"{evidence_id} names a paper outside required_paper_ids")
    if isinstance(passage, bool) or not isinstance(passage, int) or passage < 1 or passage > 9999:
        raise ValidationError(f"{evidence_id}.passage must be an integer from 1 through 9999")
    if evidence["locator"] != f"BioC-passage-{passage:04d}":
        raise ValidationError(f"{evidence_id} locator does not match its passage number")
    if source_id != f"paper-{paper_id.casefold()}":
        raise ValidationError(f"{evidence_id}.source_id is not the canonical lowercase paper source")
    expected_path = f"evaluations/semantic-okf-endocrine-hygiene/corpus/sources/markdown/{paper_id}.md"
    if path != expected_path:
        raise ValidationError(f"{evidence_id}.path is not the deterministic authoritative paper path")
    if evidence["evidence_role"] not in EVIDENCE_ROLES:
        raise ValidationError(f"{evidence_id}.evidence_role is unsupported")
    if not isinstance(evidence["text_sha256"], str) or SHA256.fullmatch(evidence["text_sha256"]) is None:
        raise ValidationError(f"{evidence_id}.text_sha256 is invalid")
    source = corpus_sources.get(source_id)
    if source is None or source.get("path") != f"sources/markdown/{paper_id}.md":
        raise ValidationError(f"{evidence_id} is not bound to the declared corpus manifest source")


def validate_ground_truth_record(
    record: Mapping[str, Any],
    question: Mapping[str, Any],
    corpus_sources: Mapping[str, Mapping[str, Any]],
) -> None:
    question_id = question["id"]
    exact_keys(
        record,
        {"authoritative_evidence", "ground_truth", "id", "question", "schema_version"},
        question_id,
    )
    if record["schema_version"] != "semantic-okf-endocrine-hygiene-hard-ground-truth/1.0":
        raise ValidationError(f"{question_id} has an unsupported schema version")
    if record["id"] != question_id or record["question"] != question["question"]:
        raise ValidationError(f"{question_id} does not reproduce its frozen question exactly")
    ground_truth = record["ground_truth"]
    if not isinstance(ground_truth, dict):
        raise ValidationError(f"{question_id}.ground_truth must be an object")
    exact_keys(
        ground_truth,
        {
            "acceptable_variants",
            "answer_claims",
            "derivation",
            "failure_conditions",
            "important_negatives",
            "required_paper_ids",
            "required_source_ids",
        },
        f"{question_id}.ground_truth",
    )
    required_papers = sorted_unique_strings(
        ground_truth["required_paper_ids"], f"{question_id}.required_paper_ids"
    )
    required_sources = sorted_unique_strings(
        ground_truth["required_source_ids"], f"{question_id}.required_source_ids"
    )
    if required_papers != question["qrels"]["paper_ids"]:
        raise ValidationError(f"{question_id} required papers differ from retrieval qrels")
    if required_sources != question["qrels"]["source_ids"] or required_sources != expected_source_ids(required_papers):
        raise ValidationError(f"{question_id} required sources differ from retrieval qrels")
    for source_id in required_sources:
        if source_id not in corpus_sources:
            raise ValidationError(f"{question_id} requires unknown corpus source {source_id}")
    evidence_rows = record["authoritative_evidence"]
    if not isinstance(evidence_rows, list) or len(evidence_rows) < len(required_papers):
        raise ValidationError(f"{question_id} needs evidence for every required paper")
    evidence_ids: set[str] = set()
    evidence_papers: set[str] = set()
    for evidence in evidence_rows:
        if not isinstance(evidence, dict):
            raise ValidationError(f"{question_id}.authoritative_evidence must contain objects")
        validate_evidence(evidence, question_id, set(required_papers), corpus_sources)
        if evidence["id"] in evidence_ids:
            raise ValidationError(f"{question_id} has duplicate evidence ID {evidence['id']}")
        evidence_ids.add(evidence["id"])
        evidence_papers.add(evidence["paper_id"])
    if evidence_papers != set(required_papers):
        raise ValidationError(f"{question_id} does not include evidence for every required paper")

    claims = ground_truth["answer_claims"]
    if not isinstance(claims, list) or len(claims) < 3:
        raise ValidationError(f"{question_id} needs at least three atomic answer claims")
    claim_ids: set[str] = set()
    for claim in claims:
        if not isinstance(claim, dict):
            raise ValidationError(f"{question_id}.answer_claims must contain objects")
        exact_keys(claim, {"evidence_ids", "id", "statement"}, f"{question_id} answer claim")
        claim_id = claim["id"]
        if not isinstance(claim_id, str) or re.fullmatch(re.escape(question_id[:4]) + r"-a[1-9][0-9]*", claim_id) is None:
            raise ValidationError(f"{question_id} has an invalid answer claim ID")
        if claim_id in claim_ids:
            raise ValidationError(f"{question_id} has duplicate answer claim ID {claim_id}")
        claim_ids.add(claim_id)
        validate_string(claim["statement"], f"{claim_id}.statement", minimum_words=8)
        references = unique_strings(claim["evidence_ids"], f"{claim_id}.evidence_ids")
        if not set(references) <= evidence_ids:
            raise ValidationError(f"{claim_id} references unknown evidence")

    derivations = ground_truth["derivation"]
    if not isinstance(derivations, list) or len(derivations) < 2:
        raise ValidationError(f"{question_id} needs at least two explicit derivation steps")
    for number, derivation in enumerate(derivations, start=1):
        if not isinstance(derivation, dict):
            raise ValidationError(f"{question_id}.derivation must contain objects")
        exact_keys(derivation, {"conclusion", "inputs", "operation"}, f"{question_id} derivation {number}")
        if derivation["operation"] not in DERIVATION_OPERATIONS:
            raise ValidationError(f"{question_id} derivation {number} has an unsupported operation")
        inputs = unique_strings(derivation["inputs"], f"{question_id} derivation {number}.inputs")
        if not set(inputs) <= claim_ids:
            raise ValidationError(f"{question_id} derivation {number} references an unknown answer claim")
        validate_string(derivation["conclusion"], f"{question_id} derivation {number}.conclusion", minimum_words=8)

    negatives = ground_truth["important_negatives"]
    if not isinstance(negatives, list) or len(negatives) < 2:
        raise ValidationError(f"{question_id} needs at least two important negatives")
    negative_ids: set[str] = set()
    for negative in negatives:
        if not isinstance(negative, dict):
            raise ValidationError(f"{question_id}.important_negatives must contain objects")
        exact_keys(negative, {"evidence_ids", "id", "statement"}, f"{question_id} negative")
        negative_id = negative["id"]
        if not isinstance(negative_id, str) or re.fullmatch(re.escape(question_id[:4]) + r"-n[1-9][0-9]*", negative_id) is None:
            raise ValidationError(f"{question_id} has an invalid important-negative ID")
        if negative_id in negative_ids:
            raise ValidationError(f"{question_id} has duplicate important-negative ID {negative_id}")
        negative_ids.add(negative_id)
        validate_string(negative["statement"], f"{negative_id}.statement", minimum_words=6)
        references = unique_strings(negative["evidence_ids"], f"{negative_id}.evidence_ids")
        if not set(references) <= evidence_ids:
            raise ValidationError(f"{negative_id} references unknown evidence")

    variants = ground_truth["acceptable_variants"]
    failures = ground_truth["failure_conditions"]
    if not isinstance(variants, list) or len(variants) < 2:
        raise ValidationError(f"{question_id} needs at least two acceptable variants")
    if not isinstance(failures, list) or len(failures) < 3:
        raise ValidationError(f"{question_id} needs at least three failure conditions")
    if len(set(variants)) != len(variants) or len(set(failures)) != len(failures):
        raise ValidationError(f"{question_id} variants and failure conditions must be duplicate-free")
    for number, value in enumerate(variants, start=1):
        validate_string(value, f"{question_id} acceptable variant {number}", minimum_words=6)
    for number, value in enumerate(failures, start=1):
        validate_string(value, f"{question_id} failure condition {number}", minimum_words=5)

    normalized_question = " ".join(re.findall(r"[a-z0-9]+", question["question"].casefold()))
    answer_texts = [claim["statement"] for claim in claims] + [item["statement"] for item in negatives]
    for answer_text in answer_texts:
        normalized_answer = " ".join(re.findall(r"[a-z0-9]+", answer_text.casefold()))
        if normalized_answer and normalized_answer in normalized_question:
            raise ValidationError(f"{question_id} leaks a complete answer claim in its prompt")


def validate_hard_claim_requirements(
    requirements: Mapping[str, Any],
    ground_truth: list[dict[str, Any]],
    corpus_claims: Mapping[str, tuple[str, str]],
) -> dict[str, int]:
    """Validate exact reviewed-claim requirements for every hard answer atom and negative."""

    exact_keys(
        requirements,
        {"contract", "questions", "schema_version"},
        "hard claim requirements",
    )
    if requirements["schema_version"] != "semantic-okf-endocrine-hygiene-hard-claim-requirements/1.0":
        raise ValidationError("hard claim requirements schema version is unsupported")
    validate_string(requirements["contract"], "hard claim requirements contract", minimum_words=8)
    question_rows = requirements["questions"]
    if not isinstance(question_rows, list):
        raise ValidationError("hard claim requirements questions must be an array")
    requirement_ids = [row.get("id") if isinstance(row, dict) else None for row in question_rows]
    ground_truth_ids = [row.get("id") for row in ground_truth]
    if requirement_ids != list(HARD_QUESTION_IDS) or ground_truth_ids != list(HARD_QUESTION_IDS):
        raise ValidationError("hard claim requirements and ground truth must contain the exact five hard question IDs")

    ground_truth_by_id = {row["id"]: row for row in ground_truth}
    required_claim_bindings = 0
    required_claim_ids: set[str] = set()
    answer_claims = 0
    important_negatives = 0

    for question_row in question_rows:
        question_id = question_row["id"]
        exact_keys(
            question_row,
            {"answer_claims", "id", "important_negatives"},
            f"{question_id} claim requirements",
        )
        record = ground_truth_by_id[question_id]
        evidence_by_id = {
            evidence["id"]: evidence for evidence in record["authoritative_evidence"]
        }
        ground_truth_sections = {
            "answer_claims": record["ground_truth"]["answer_claims"],
            "important_negatives": record["ground_truth"]["important_negatives"],
        }
        seen_requirement_ids: set[str] = set()
        for section_name, expected_rows in ground_truth_sections.items():
            requirement_rows = question_row[section_name]
            if not isinstance(requirement_rows, list):
                raise ValidationError(f"{question_id}.{section_name} requirements must be an array")
            expected_ids = [row["id"] for row in expected_rows]
            observed_ids = [row.get("id") if isinstance(row, dict) else None for row in requirement_rows]
            if observed_ids != expected_ids:
                raise ValidationError(
                    f"{question_id}.{section_name} requirements must match ground truth exactly; "
                    f"expected={expected_ids}, observed={observed_ids}"
                )
            if len(observed_ids) != len(set(observed_ids)):
                raise ValidationError(f"{question_id}.{section_name} requirement IDs must be unique")
            if seen_requirement_ids.intersection(observed_ids):
                raise ValidationError(f"{question_id} repeats an atom or negative requirement ID")
            seen_requirement_ids.update(observed_ids)
            expected_by_id = {row["id"]: row for row in expected_rows}
            for requirement_row in requirement_rows:
                requirement_id = requirement_row["id"]
                exact_keys(
                    requirement_row,
                    {"id", "required_claim_ids"},
                    f"{requirement_id} claim requirement",
                )
                claim_ids = sorted_unique_strings(
                    requirement_row["required_claim_ids"],
                    f"{requirement_id}.required_claim_ids",
                )
                if any(CLAIM_ID.fullmatch(claim_id) is None for claim_id in claim_ids):
                    raise ValidationError(f"{requirement_id} has a noncanonical required claim ID")
                evidence_ids = expected_by_id[requirement_id]["evidence_ids"]
                allowed_signatures = {
                    (evidence_by_id[evidence_id]["paper_id"], evidence_by_id[evidence_id]["text_sha256"])
                    for evidence_id in evidence_ids
                }
                for claim_id in claim_ids:
                    signature = corpus_claims.get(claim_id)
                    if signature is None:
                        raise ValidationError(f"{requirement_id} requires unknown corpus claim {claim_id}")
                    if signature not in allowed_signatures:
                        raise ValidationError(
                            f"{requirement_id} required claim {claim_id} is not bound to any of its evidence IDs"
                        )
                required_claim_bindings += len(claim_ids)
                required_claim_ids.update(claim_ids)
            if section_name == "answer_claims":
                answer_claims += len(requirement_rows)
            else:
                important_negatives += len(requirement_rows)

    corpus_signatures = set(corpus_claims.values())
    evidence_projections = 0
    for record in ground_truth:
        for evidence in record["authoritative_evidence"]:
            signature = (evidence["paper_id"], evidence["text_sha256"])
            if signature not in corpus_signatures:
                raise ValidationError(
                    f"{evidence['id']} has no reviewed corpus-claim projection for its paper/hash signature"
                )
            evidence_projections += 1

    return {
        "hard_claim_requirement_records": len(question_rows),
        "hard_answer_claims": answer_claims,
        "hard_important_negatives": important_negatives,
        "hard_required_claim_bindings": required_claim_bindings,
        "distinct_required_claims": len(required_claim_ids),
        "hard_evidence_claim_projections": evidence_projections,
    }


def validate_authoritative_passages(records: Iterable[Mapping[str, Any]]) -> int:
    checked = 0
    for record in records:
        for evidence in record["authoritative_evidence"]:
            candidate = (REPOSITORY / evidence["path"]).resolve()
            try:
                candidate.relative_to(REPOSITORY.resolve())
            except ValueError as exc:
                raise ValidationError(f"{evidence['id']} path escapes the repository") from exc
            try:
                text = candidate.read_text(encoding="utf-8")
            except OSError as exc:
                raise ValidationError(f"cannot read authoritative evidence for {evidence['id']}: {exc}") from exc
            if "\r" in text:
                raise ValidationError(f"{candidate.as_posix()} must use LF line endings")
            heading = f"## BioC passage {evidence['passage']:04d}"
            pattern = re.compile(
                rf"(?ms)^{re.escape(heading)}\n\n"
                rf"Locator metadata: (?P<metadata>[^\n]+)\n\n"
                rf"(?P<text>.*?)(?=\n\n## BioC passage [0-9]{{4}}\n|\Z)"
            )
            matches = list(pattern.finditer(text))
            if len(matches) != 1:
                raise ValidationError(f"{evidence['id']} locator must resolve exactly once")
            match = matches[0]
            metadata_match = re.search(r"(?:^|;) text_sha256=([0-9a-f]{64})(?:;|$)", match["metadata"])
            if metadata_match is None:
                raise ValidationError(f"{evidence['id']} locator metadata lacks a passage hash")
            passage_text = match["text"]
            if passage_text.endswith("\n"):
                passage_text = passage_text[:-1]
            computed = sha256_bytes(passage_text.encode("utf-8"))
            if metadata_match.group(1) != evidence["text_sha256"] or computed != evidence["text_sha256"]:
                raise ValidationError(
                    f"{evidence['id']} passage hash mismatch: declared={evidence['text_sha256']} "
                    f"metadata={metadata_match.group(1)} computed={computed}"
                )
            checked += 1
    return checked


def validate_benchmark_manifest(
    manifest: Mapping[str, Any],
    questions: list[dict[str, Any]],
    hard_questions: list[dict[str, Any]],
    ground_truth: list[dict[str, Any]],
    hard_claim_requirements: Mapping[str, Any],
    hard_claim_counts: Mapping[str, int],
) -> None:
    exact_keys(manifest, {"contracts", "counts", "files", "schema_version"}, "benchmark manifest")
    if manifest["schema_version"] != "semantic-okf-endocrine-hygiene-benchmark-manifest/1.0":
        raise ValidationError("benchmark manifest schema version is unsupported")
    contracts = manifest["contracts"]
    if not isinstance(contracts, dict):
        raise ValidationError("benchmark manifest contracts must be an object")
    exact_keys(
        contracts,
        {"authority", "evidence_locator", "qrels", "question_prompt"},
        "benchmark manifest contracts",
    )
    for key, value in contracts.items():
        validate_string(value, f"benchmark manifest contracts.{key}", minimum_words=4)
    counts = manifest["counts"]
    if not isinstance(counts, dict):
        raise ValidationError("benchmark manifest counts must be an object")
    exact_keys(
        counts,
        {
            "cross_paper",
            "direct",
            "distinct_required_claims",
            "distinct_authoritative_passages",
            "hard",
            "hard_answer_claims",
            "hard_claim_requirement_records",
            "hard_evidence_bindings",
            "hard_ground_truth",
            "hard_important_negatives",
            "hard_required_claim_bindings",
            "questions",
        },
        "benchmark manifest counts",
    )
    actual_types = Counter(row["question_type"] for row in questions)
    evidence_bindings = [
        evidence
        for record in ground_truth
        for evidence in record["authoritative_evidence"]
    ]
    distinct_passages = {
        (evidence["paper_id"], evidence["locator"], evidence["text_sha256"])
        for evidence in evidence_bindings
    }
    expected_counts = {
        "questions": len(questions),
        "direct": actual_types["direct"],
        "cross_paper": actual_types["cross-paper"],
        "hard": actual_types["hard"],
        "hard_evidence_bindings": len(evidence_bindings),
        "hard_ground_truth": len(ground_truth),
        "distinct_authoritative_passages": len(distinct_passages),
        "hard_claim_requirement_records": hard_claim_counts["hard_claim_requirement_records"],
        "hard_answer_claims": hard_claim_counts["hard_answer_claims"],
        "hard_important_negatives": hard_claim_counts["hard_important_negatives"],
        "hard_required_claim_bindings": hard_claim_counts["hard_required_claim_bindings"],
        "distinct_required_claims": hard_claim_counts["distinct_required_claims"],
    }
    if counts != expected_counts or counts["hard"] != len(hard_questions):
        raise ValidationError(f"benchmark manifest counts are stale: expected {expected_counts}")
    files = manifest["files"]
    if not isinstance(files, dict):
        raise ValidationError("benchmark manifest files must be an object")
    expected_files = {
        "hard-claim-requirements.json": HARD_CLAIM_REQUIREMENTS_PATH,
        "hard-ground-truth.jsonl": GROUND_TRUTH_PATH,
        "hard-questions.jsonl": HARD_QUESTIONS_PATH,
        "retrieval-questions.jsonl": QUESTIONS_PATH,
    }
    exact_keys(files, set(expected_files), "benchmark manifest files")
    row_counts = {
        "hard-claim-requirements.json": len(hard_claim_requirements["questions"]),
        "hard-ground-truth.jsonl": len(ground_truth),
        "hard-questions.jsonl": len(hard_questions),
        "retrieval-questions.jsonl": len(questions),
    }
    for name, path in expected_files.items():
        descriptor = files[name]
        if not isinstance(descriptor, dict):
            raise ValidationError(f"benchmark manifest files.{name} must be an object")
        exact_keys(descriptor, {"path", "row_count", "sha256"}, f"benchmark manifest files.{name}")
        expected_path = path.relative_to(REPOSITORY).as_posix()
        if descriptor["path"] != expected_path:
            raise ValidationError(f"benchmark manifest path for {name} is stale")
        if descriptor["row_count"] != row_counts[name]:
            raise ValidationError(f"benchmark manifest row count for {name} is stale")
        digest = sha256_bytes(path.read_bytes())
        if descriptor["sha256"] != digest:
            raise ValidationError(f"benchmark manifest hash for {name} is stale")


def validate() -> dict[str, Any]:
    corpus_manifest = load_json(CORPUS_MANIFEST_PATH)
    if not isinstance(corpus_manifest, dict) or not isinstance(corpus_manifest.get("sources"), list):
        raise ValidationError("corpus manifest must contain a source array")
    corpus_sources: dict[str, Mapping[str, Any]] = {}
    for number, source in enumerate(corpus_manifest["sources"], start=1):
        if not isinstance(source, dict) or not isinstance(source.get("id"), str):
            raise ValidationError(f"corpus manifest source {number} is invalid")
        if source["id"] in corpus_sources:
            raise ValidationError(f"corpus manifest has duplicate source ID {source['id']}")
        corpus_sources[source["id"]] = source
    corpus_papers = {
        source["id"].removeprefix("paper-").upper()
        for source in corpus_manifest["sources"]
        if isinstance(source, dict) and str(source.get("id", "")).startswith("paper-pmc")
    }
    if not corpus_papers:
        raise ValidationError("corpus manifest does not declare paper-pmc sources")
    corpus_claims = load_corpus_claims(corpus_sources)

    questions = load_jsonl(QUESTIONS_PATH)
    hard_questions = load_jsonl(HARD_QUESTIONS_PATH)
    ground_truth = load_jsonl(GROUND_TRUTH_PATH)
    hard_claim_requirements = load_json(HARD_CLAIM_REQUIREMENTS_PATH)
    if not isinstance(hard_claim_requirements, dict):
        raise ValidationError("hard claim requirements root must be an object")
    question_by_id = validate_questions(questions, hard_questions, corpus_papers)
    expected_ground_truth_ids = [row["id"] for row in hard_questions]
    observed_ground_truth_ids = [row.get("id") for row in ground_truth]
    if observed_ground_truth_ids != expected_ground_truth_ids:
        raise ValidationError("hard ground truth must be ordered one-to-one with hard questions")
    for record in ground_truth:
        validate_ground_truth_record(record, question_by_id[record["id"]], corpus_sources)
    hard_claim_counts = validate_hard_claim_requirements(
        hard_claim_requirements,
        ground_truth,
        corpus_claims,
    )
    passages_checked = validate_authoritative_passages(ground_truth)
    distinct_passages = {
        (evidence["paper_id"], evidence["locator"], evidence["text_sha256"])
        for record in ground_truth
        for evidence in record["authoritative_evidence"]
    }
    manifest = load_json(BENCHMARK_MANIFEST_PATH)
    if not isinstance(manifest, dict):
        raise ValidationError("benchmark manifest root must be an object")
    validate_benchmark_manifest(
        manifest,
        questions,
        hard_questions,
        ground_truth,
        hard_claim_requirements,
        hard_claim_counts,
    )
    return {
        "status": "pass",
        "questions": len(questions),
        "question_types": dict(sorted(Counter(row["question_type"] for row in questions).items())),
        "hard_ground_truth_records": len(ground_truth),
        "hard_evidence_bindings_checked": passages_checked,
        "distinct_authoritative_passages": len(distinct_passages),
        **hard_claim_counts,
        "corpus_papers": len(corpus_papers),
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Print one compact JSON result.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        result = validate()
    except ValidationError as exc:
        if args.json:
            print(json.dumps({"status": "fail", "error": str(exc)}, sort_keys=True))
        else:
            print(f"error: {exc}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    else:
        print(
            "Validated "
            f"{result['questions']} questions, {result['hard_ground_truth_records']} hard ground-truth records, "
            f"{result['hard_evidence_bindings_checked']} question-specific evidence bindings, and "
            f"{result['distinct_authoritative_passages']} distinct authoritative passages; "
            f"{result['hard_required_claim_bindings']} exact reviewed-claim requirements were checked."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
