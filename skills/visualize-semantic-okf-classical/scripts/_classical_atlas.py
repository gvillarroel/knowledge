from __future__ import annotations

from collections import Counter, defaultdict
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import re
import shutil
import tempfile
from typing import Any


ATLAS_SCHEMA = "classical-knowledge-atlas/1.2"
RECEIPT_SCHEMA = "classical-knowledge-atlas-receipt/1.2"
CONTRADICTION_SCHEMA = "classical-contradiction-review/2.0"
EXPECTED_CLASSICAL_FILES = {
    "associations.jsonl",
    "build-report.json",
    "documents.jsonl",
    "index.json",
    "lexicon.json",
    "topics.json",
}
EXPECTED_OUTPUT_FILES = {"index.html", "projection.json", "receipt.json"}
REQUIRED_SEMANTIC_FILES = {
    "build-report.json",
    "records.jsonl",
    "semantic-plan.json",
    "source-manifest.json",
}

CONTRADICTION_RELATION_FIELDS = (
    "contradicts",
    "contradicts_record_id",
    "contradicts_record_ids",
    "contradiction_record_id",
    "contradiction_record_ids",
)
CONTRADICTION_STOPWORDS = frozenset(
    """
    a an and are as at author authors be been being by can claim could data dataset datasets
    for from graph graphs has have in into is it its may method methods might model models most
    of on or our paper performance rag reported result results retrieval system systems task tasks
    that the their them they this to use used using was were which while with within would
    approach approaches
    """.split()
)
POSITIVE_CUES = frozenset(
    """
    advantage advantages accurate better cheaper comprehensive effective efficient enable enabled
    enables faster gain gains higher improve improved improvement improvements improves increase
    increased increases outperform outperformed outperforms reliable robust safe scalable strong
    stronger success successful support supported supports
    """.split()
)
NEGATIVE_CUES = frozenset(
    """
    absent cannot costly decrease decreased decreases degrade degraded degrades drop drops expensive
    exclude excluded excludes fail failed failure failures fails fewer hurt hurts inaccurate
    inefficient lack lacked lacking lacks limitation limitations limited lose loses lower neither
    never no noise noisy not poor prevent prevented prevents underperform underperformed
    underperforms unable unsafe weak without worse
    """.split()
)
NEGATION_CUES = frozenset(
    "cannot failed fails lack lacks neither never no not unable without".split()
)
OPPOSITION_FAMILIES = (
    (
        "increase-versus-decrease",
        frozenset("gain gains higher increase increased increases".split()),
        frozenset("decrease decreased decreases drop drops fewer lower".split()),
    ),
    (
        "improvement-versus-degradation",
        frozenset(
            "advantage advantages better improve improved improves outperform outperformed "
            "outperforms strong stronger".split()
        ),
        frozenset(
            "degrade degraded degrades hurt hurts underperform underperformed underperforms weak worse".split()
        ),
    ),
    (
        "support-versus-failure",
        frozenset("enable enabled enables support supported supports".split()),
        frozenset("cannot fail failed fails prevent prevented prevents unable".split()),
    ),
    (
        "quality-versus-risk",
        frozenset("accurate efficient reliable robust safe scalable".split()),
        frozenset("inaccurate inefficient unsafe weak".split()),
    ),
    (
        "speed-versus-cost",
        frozenset("cheaper faster".split()),
        frozenset("costly expensive slower".split()),
    ),
)
POLARITY_CUE_TOKENS = frozenset(
    set(POSITIVE_CUES)
    | set(NEGATIVE_CUES)
    | {term for _family, positive, negative in OPPOSITION_FAMILIES for term in positive | negative}
)
CONTRAST_KIND_PAIRS = frozenset(
    {
        frozenset(("strength", "limitation")),
        frozenset(("strength", "comparison")),
        frozenset(("limitation", "comparison")),
        frozenset(("limitation", "efficiency-update")),
    }
)
MAX_CONTRADICTION_CANDIDATES = 48
STRICT_NEGATION_SIMILARITY_FLOOR = 0.82
STRICT_DIRECTIONAL_SIMILARITY_FLOOR = 0.72
STRICT_NUMERIC_SIMILARITY_FLOOR = 0.9
STRICT_MIN_SHARED_ANCHORS = 3
STRICT_MAX_TOKEN_DIFFERENCE = 4
AMBIGUOUS_NEGATION_PATTERNS = (
    re.compile(r"\bnot\s+(?:all|always|every|merely|necessarily|only|uniformly|yet)\b"),
    re.compile(r"\bno\s+retrieval\b"),
    re.compile(r"\bwithout\s+(?:eliminating|reporting|requiring)\b"),
)
STRICT_NEGATION_PATTERNS = (
    re.compile(
        r"\b(?:are|can|could|did|do|does|had|has|have|is|may|might|must|should|was|were|will|would)\s+not\b"
    ),
    re.compile(r"\bcannot\b"),
    re.compile(r"\bnever\b"),
)
AFFIRMED_POLARITIES = frozenset({"affirmed", "positive", "true", "yes"})
NEGATED_POLARITIES = frozenset({"negated", "negative", "false", "no"})


class AtlasError(RuntimeError):
    """Raised when an input bundle or generated atlas violates its contract."""


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def pretty_json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return sha256(value).hexdigest()


def file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise AtlasError(f"cannot read JSON object {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise AtlasError(f"expected a JSON object: {path}")
    return value


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        raise AtlasError(f"cannot read JSON Lines file {path}: {exc}") from exc
    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise AtlasError(f"invalid JSON at {path}:{line_number}: {exc}") from exc
        if not isinstance(value, dict):
            raise AtlasError(f"expected an object at {path}:{line_number}")
        rows.append(value)
    return rows


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def require_disjoint_paths(knowledge: Path, output: Path) -> tuple[Path, Path]:
    knowledge = knowledge.resolve()
    output = output.resolve()
    if knowledge == output or _is_relative_to(output, knowledge) or _is_relative_to(knowledge, output):
        raise AtlasError("knowledge and atlas paths must be disjoint")
    return knowledge, output


def tree_receipt(root: Path) -> dict[str, Any]:
    entries: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise AtlasError(f"knowledge bundle contains a symlink: {path}")
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        entries.append(
            {
                "path": relative,
                "bytes": path.stat().st_size,
                "sha256": file_sha256(path),
            }
        )
    return {
        "schema": "path-and-byte-tree/1.0",
        "file_count": len(entries),
        "byte_count": sum(entry["bytes"] for entry in entries),
        "sha256": sha256_bytes(canonical_json(entries).encode("utf-8")),
    }


def _require_file(root: Path, relative: str) -> Path:
    path = root / relative
    if not path.is_file() or path.is_symlink():
        raise AtlasError(f"required regular file is missing: {relative}")
    return path


def _verify_artifact(root: Path, entry: dict[str, Any], expected_path: str) -> None:
    if entry.get("path") != expected_path:
        raise AtlasError(f"artifact path mismatch for {expected_path}")
    path = _require_file(root, expected_path)
    if entry.get("sha256") != file_sha256(path):
        raise AtlasError(f"artifact hash mismatch: {expected_path}")
    if "bytes" in entry and entry.get("bytes") != path.stat().st_size:
        raise AtlasError(f"artifact byte count mismatch: {expected_path}")


def validate_bundle(root: Path) -> dict[str, Any]:
    root = root.resolve()
    if not root.is_dir():
        raise AtlasError(f"knowledge bundle does not exist: {root}")
    _require_file(root, "index.md")
    if not (root / "concepts").is_dir():
        raise AtlasError("concepts directory is missing")
    if not (root / "semantic").is_dir():
        raise AtlasError("semantic directory is missing")
    if not (root / "classical").is_dir():
        raise AtlasError("classical directory is missing")

    classical_entries = {path.name for path in (root / "classical").iterdir()}
    if classical_entries != EXPECTED_CLASSICAL_FILES:
        missing = sorted(EXPECTED_CLASSICAL_FILES - classical_entries)
        unknown = sorted(classical_entries - EXPECTED_CLASSICAL_FILES)
        raise AtlasError(f"classical closed-file mismatch; missing={missing}, unknown={unknown}")
    for name in EXPECTED_CLASSICAL_FILES:
        _require_file(root, f"classical/{name}")
    for name in REQUIRED_SEMANTIC_FILES:
        _require_file(root, f"semantic/{name}")

    classical_index = read_json(root / "classical" / "index.json")
    classical_report = read_json(root / "classical" / "build-report.json")
    semantic_report = read_json(root / "semantic" / "build-report.json")
    source_manifest = read_json(root / "semantic" / "source-manifest.json")
    semantic_plan = read_json(root / "semantic" / "semantic-plan.json")

    for label, report in (("classical", classical_report), ("semantic", semantic_report)):
        if report.get("status") != "pass" or report.get("valid") is not True:
            raise AtlasError(f"{label} build report is not passing")
        if report.get("errors"):
            raise AtlasError(f"{label} build report contains errors")

    artifact_paths = {
        "documents": "classical/documents.jsonl",
        "lexicon": "classical/lexicon.json",
        "associations": "classical/associations.jsonl",
        "topics": "classical/topics.json",
    }
    indexed_artifacts = classical_index.get("artifacts") or {}
    for name, relative in artifact_paths.items():
        entry = indexed_artifacts.get(name)
        if not isinstance(entry, dict):
            raise AtlasError(f"classical index is missing artifact metadata: {name}")
        _verify_artifact(root, entry, relative)

    reported_artifacts = classical_report.get("artifacts") or {}
    for name, relative in {**artifact_paths, "index": "classical/index.json"}.items():
        entry = reported_artifacts.get(name)
        if not isinstance(entry, dict):
            raise AtlasError(f"classical report is missing artifact metadata: {name}")
        _verify_artifact(root, entry, relative)

    semantic_artifacts = source_manifest.get("artifacts") or {}
    for name, entry in semantic_artifacts.items():
        if not isinstance(entry, dict) or not isinstance(entry.get("path"), str):
            raise AtlasError(f"invalid semantic artifact metadata: {name}")
        _verify_artifact(root, entry, entry["path"])

    records_path = root / "semantic" / "records.jsonl"
    records_sha = file_sha256(records_path)
    core = classical_index.get("core") or {}
    if core.get("records_sha256") != records_sha:
        raise AtlasError("classical core records hash does not match semantic records")

    records = read_jsonl(records_path)
    documents = read_jsonl(root / "classical" / "documents.jsonl")
    associations = read_jsonl(root / "classical" / "associations.jsonl")
    lexicon = read_json(root / "classical" / "lexicon.json")
    topics = read_json(root / "classical" / "topics.json")

    expected_counts = {
        "documents": len(documents),
        "associations": len(associations),
        "lexicon": len(lexicon.get("terms") or []),
        "topics": len(topics.get("topics") or []),
    }
    for name, actual in expected_counts.items():
        declared = (indexed_artifacts.get(name) or {}).get("count")
        if declared != actual:
            raise AtlasError(f"{name} count mismatch: declared={declared}, actual={actual}")
    if core.get("record_count") != len(records):
        raise AtlasError("classical core record count does not match semantic records")

    selected = set((classical_index.get("selection") or {}).get("eligible_source_ids") or [])
    source_ids = {str(row.get("id")) for row in source_manifest.get("sources") or []}
    if not selected or not selected.issubset(source_ids):
        raise AtlasError("eligible classical sources are missing from the semantic source manifest")

    return {
        "classical_index": classical_index,
        "classical_report": classical_report,
        "semantic_report": semantic_report,
        "source_manifest": source_manifest,
        "semantic_plan": semantic_plan,
        "records": records,
        "documents": documents,
        "associations": associations,
        "lexicon": lexicon,
        "topics": topics,
        "source_tree": tree_receipt(root),
    }


def _short_text(value: Any, limit: int = 220) -> str:
    compact = " ".join(str(value or "").split())
    if len(compact) <= limit:
        return compact
    return compact[: limit - 1].rstrip() + "…"


def _record_year(record: dict[str, Any]) -> int | None:
    attributes = record.get("attributes") or {}
    for key in ("publication_year", "year"):
        value = attributes.get(key)
        if isinstance(value, int):
            return value
        if isinstance(value, str) and value.isdigit():
            return int(value)
    return None


def _bucket_document_frequency(value: int) -> str:
    if value <= 1:
        return "1"
    if value <= 4:
        return "2–4"
    if value <= 19:
        return "5–19"
    if value <= 99:
        return "20–99"
    return "100+"


def _round(value: float, digits: int = 6) -> float:
    return round(float(value), digits)


def _topic_graph(
    topic: dict[str, Any],
    association_map: dict[str, dict[str, Any]],
    term_metrics: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    weighted_terms = topic.get("terms") or []
    core_terms = [str(row.get("term")) for row in weighted_terms[:12] if row.get("term")]
    core = set(core_terms)
    nodes = set(core_terms)
    edge_map: dict[tuple[str, str], dict[str, Any]] = {}

    def add_edge(source: str, target: str, neighbor: dict[str, Any]) -> None:
        if source == target:
            return
        key = tuple(sorted((source, target)))
        candidate = {
            "source": key[0],
            "target": key[1],
            "ppmi": _round(neighbor.get("ppmi") or 0.0, 8),
            "cooccurrence": int(neighbor.get("cooccurrence") or 0),
        }
        previous = edge_map.get(key)
        if previous is None or candidate["ppmi"] > previous["ppmi"]:
            edge_map[key] = candidate

    for term in core_terms:
        row = association_map.get(term) or {}
        for neighbor in row.get("neighbors") or []:
            target = str(neighbor.get("term") or "")
            if target in core:
                add_edge(term, target, neighbor)

    bridge_candidates: list[tuple[float, int, str, str, dict[str, Any]]] = []
    for term in core_terms:
        row = association_map.get(term) or {}
        for neighbor in row.get("neighbors") or []:
            target = str(neighbor.get("term") or "")
            if not target or target in core:
                continue
            bridge_candidates.append(
                (
                    -float(neighbor.get("ppmi") or 0.0),
                    -int(neighbor.get("cooccurrence") or 0),
                    term,
                    target,
                    neighbor,
                )
            )
    for _negative_ppmi, _negative_count, term, target, neighbor in sorted(bridge_candidates):
        if len(nodes) >= 18 or len(edge_map) >= 30:
            break
        nodes.add(target)
        add_edge(term, target, neighbor)

    topic_weights = {str(row.get("term")): float(row.get("weight") or 0.0) for row in weighted_terms}
    node_rows = []
    for term in sorted(nodes, key=lambda item: (item not in core, -topic_weights.get(item, 0.0), item)):
        metrics = term_metrics.get(term) or {}
        node_rows.append(
            {
                "id": term,
                "role": "topic-term" if term in core else "association-bridge",
                "topic_weight": _round(topic_weights.get(term, 0.0), 8),
                "document_frequency": int(metrics.get("document_frequency") or 0),
                "corpus_frequency": int(metrics.get("corpus_frequency") or 0),
                "idf": _round(metrics.get("idf") or 0.0, 8),
            }
        )
    return {
        "nodes": node_rows,
        "edges": sorted(edge_map.values(), key=lambda row: (-row["ppmi"], row["source"], row["target"])),
    }


def _word_tokens(value: Any) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", str(value or "").lower()))


def _claim_text(record: dict[str, Any]) -> str:
    attributes = record.get("attributes") or {}
    return str(attributes.get("interpretation") or attributes.get("description") or record.get("body") or "")


def _claim_payload(record: dict[str, Any]) -> dict[str, Any]:
    attributes = record.get("attributes") or {}
    return {
        "record_id": record.get("record_id"),
        "title": record.get("title"),
        "concept_id": record.get("concept_id"),
        "concept_path": record.get("concept_path"),
        "concept_type": record.get("concept_type"),
        "source_id": record.get("source_id"),
        "source_path": record.get("source_path"),
        "subject_iri": record.get("subject_iri"),
        "claim_kind": attributes.get("claim_kind"),
        "interpretation": _short_text(_claim_text(record), 420),
        "evidence_locator": attributes.get("evidence_locator"),
        "paper_iri": attributes.get("paper_iri"),
        "subject_term_iri": attributes.get("subject_term_iri"),
        "object_term_iri": attributes.get("object_term_iri"),
        "confidence": attributes.get("confidence"),
        "review_state": attributes.get("review_state"),
        "record_sha256": record.get("record_sha256"),
    }


def _target_values(value: Any) -> list[str]:
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    if isinstance(value, list):
        return [str(item).strip() for item in value if isinstance(item, str) and item.strip()]
    return []


def _explicit_contradiction_pairs(
    records: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], set[tuple[str, str]], int]:
    reference_map: dict[str, dict[str, Any]] = {}
    for record in records:
        for key in ("record_id", "concept_id", "subject_iri"):
            value = record.get(key)
            if isinstance(value, str) and value:
                reference_map[value] = record

    relations: list[tuple[dict[str, Any], dict[str, Any], str]] = []
    declared_relation_count = 0
    for record in records:
        attributes = record.get("attributes") or {}
        containers = (record, attributes)
        for container in containers:
            for field in CONTRADICTION_RELATION_FIELDS:
                if field not in container:
                    continue
                targets = _target_values(container.get(field))
                declared_relation_count += len(targets)
                for target in targets:
                    if target in reference_map and reference_map[target] is not record:
                        relations.append((record, reference_map[target], field))
        relationships = attributes.get("relationships")
        if isinstance(relationships, list):
            for relationship in relationships:
                if not isinstance(relationship, dict):
                    continue
                predicate = str(
                    relationship.get("predicate")
                    or relationship.get("type")
                    or relationship.get("relation")
                    or ""
                ).lower()
                if predicate not in {"contradicts", "contradiction"}:
                    continue
                declared_relation_count += 1
                target = str(
                    relationship.get("target")
                    or relationship.get("record_id")
                    or relationship.get("object")
                    or ""
                )
                if target in reference_map and reference_map[target] is not record:
                    relations.append((record, reference_map[target], "relationships"))

    confirmed: list[dict[str, Any]] = []
    confirmed_pairs: set[tuple[str, str]] = set()
    for left, right, field in sorted(
        relations,
        key=lambda row: (
            str(row[0].get("record_id") or ""),
            str(row[1].get("record_id") or ""),
            row[2],
        ),
    ):
        left_id = str(left.get("record_id") or left.get("concept_id") or "")
        right_id = str(right.get("record_id") or right.get("concept_id") or "")
        pair = tuple(sorted((left_id, right_id)))
        if not all(pair) or pair in confirmed_pairs:
            continue
        confirmed_pairs.add(pair)
        confirmed.append(
            {
                "contradiction_id": f"declared-{sha256_bytes(canonical_json(pair).encode('utf-8'))[:16]}",
                "status": "source-declared",
                "basis": {
                    "kind": "explicit-contradiction-relation",
                    "field": field,
                    "message": "The source metadata explicitly links these records as contradictory.",
                },
                "claim_a": _claim_payload(left),
                "claim_b": _claim_payload(right),
            }
        )
    return confirmed, confirmed_pairs, declared_relation_count


def _token_jaccard(left: set[str], right: set[str]) -> float:
    return len(left & right) / max(1, len(left | right))


def _rare_shared_terms(
    left: set[str], right: set[str], term_metrics: dict[str, dict[str, Any]]
) -> list[dict[str, Any]]:
    rare_terms = []
    for term in left & right:
        if term in POLARITY_CUE_TOKENS or term in NEGATION_CUES or term.isdigit():
            continue
        idf = float((term_metrics.get(term) or {}).get("idf") or 0.0)
        if idf >= 1.5:
            rare_terms.append({"term": term, "idf": _round(idf, 6)})
    return sorted(rare_terms, key=lambda row: (-row["idf"], row["term"]))


def _strict_negation_state(value: Any) -> bool | None:
    text = str(value or "").lower()
    if any(pattern.search(text) for pattern in AMBIGUOUS_NEGATION_PATTERNS):
        return None
    return any(pattern.search(text) for pattern in STRICT_NEGATION_PATTERNS)


def _numeric_values(value: Any) -> tuple[str, ...]:
    return tuple(re.findall(r"(?<![\w.])\d+(?:\.\d+)?%?(?![\w.])", str(value or "").lower()))


def _normalized_polarity(value: Any) -> str | None:
    normalized = str(value or "").strip().lower()
    if normalized in AFFIRMED_POLARITIES:
        return "affirmed"
    if normalized in NEGATED_POLARITIES:
        return "negated"
    return None


def _structured_proposition(record: dict[str, Any]) -> tuple[str, str] | None:
    attributes = record.get("attributes") or {}
    proposition_key = attributes.get("proposition_key") or attributes.get("assertion_key")
    polarity = _normalized_polarity(
        attributes.get("proposition_polarity") or attributes.get("assertion_polarity")
    )
    if isinstance(proposition_key, str) and proposition_key.strip() and polarity:
        return proposition_key.strip(), polarity

    proposition = attributes.get("proposition")
    if not isinstance(proposition, dict):
        return None
    polarity = _normalized_polarity(proposition.get("polarity"))
    subject = proposition.get("subject_iri") or proposition.get("subject")
    predicate = proposition.get("predicate_iri") or proposition.get("predicate")
    object_value = proposition.get("object_iri") or proposition.get("object")
    if not polarity or not subject or not predicate or object_value in (None, ""):
        return None
    signature = {
        "subject": subject,
        "predicate": predicate,
        "object": object_value,
        "qualifiers": proposition.get("qualifiers") or {},
    }
    return canonical_json(signature), polarity


def _comparison_subject(record: dict[str, Any]) -> str | None:
    attributes = record.get("attributes") or {}
    subject = attributes.get("subject_term_iri")
    if subject:
        return str(subject)
    proposition = attributes.get("proposition")
    if isinstance(proposition, dict):
        subject = proposition.get("subject_iri") or proposition.get("subject")
        if subject:
            return str(subject)
    proposition_key = attributes.get("proposition_key") or attributes.get("assertion_key")
    if isinstance(proposition_key, str) and proposition_key.strip():
        return f"proposition-key:{proposition_key.strip()}"
    return None


def _directional_opposition_signals(
    left_tokens: set[str], right_tokens: set[str]
) -> list[dict[str, Any]]:
    signals = []
    for family, positive, negative in OPPOSITION_FAMILIES:
        left_positive = sorted(left_tokens & positive)
        left_negative = sorted(left_tokens & negative)
        right_positive = sorted(right_tokens & positive)
        right_negative = sorted(right_tokens & negative)
        left_direction = (
            "positive" if left_positive and not left_negative else "negative" if left_negative and not left_positive else None
        )
        right_direction = (
            "positive" if right_positive and not right_negative else "negative" if right_negative and not right_positive else None
        )
        if left_direction and right_direction and left_direction != right_direction:
            signals.append(
                {
                    "kind": "strict-directional-opposition",
                    "family": family,
                    "left": left_positive or left_negative,
                    "right": right_positive or right_negative,
                    "label": f"Unambiguous opposite directions in {family}",
                }
            )
    return signals


def _legacy_loose_signal(
    kind_pair: frozenset[str],
    left_tokens: set[str],
    right_tokens: set[str],
    rare_score: float,
    jaccard: float,
) -> bool:
    if kind_pair not in CONTRAST_KIND_PAIRS or rare_score < 3.5:
        return False
    negation_mismatch = bool(left_tokens & NEGATION_CUES) != bool(right_tokens & NEGATION_CUES)
    polarity_mismatch = bool(
        (left_tokens & POSITIVE_CUES and right_tokens & NEGATIVE_CUES)
        or (right_tokens & POSITIVE_CUES and left_tokens & NEGATIVE_CUES)
    )
    opposition_count = sum(
        1
        for _family, positive, negative in OPPOSITION_FAMILIES
        if (left_tokens & positive and right_tokens & negative)
        or (left_tokens & negative and right_tokens & positive)
    )
    strength_limitation = kind_pair == frozenset(("strength", "limitation"))
    lexical_signal = (
        polarity_mismatch
        or opposition_count > 0
        or (strength_limitation and negation_mismatch)
    )
    return lexical_signal and not (
        jaccard > 0.58 and not (negation_mismatch or opposition_count > 0)
    )


def _strict_lexical_conflict(
    left: dict[str, Any],
    right: dict[str, Any],
    term_metrics: dict[str, dict[str, Any]],
) -> tuple[dict[str, Any] | None, str]:
    left_attributes = left.get("attributes") or {}
    right_attributes = right.get("attributes") or {}
    left_proposition = _structured_proposition(left)
    right_proposition = _structured_proposition(right)
    if (
        left_proposition
        and right_proposition
        and left_proposition[0] == right_proposition[0]
        and left_proposition[1] != right_proposition[1]
    ):
        return (
            {
                "detection_kind": "structured-polarity",
                "minimum_similarity": None,
                "proposition_similarity": 1.0,
                "token_difference": 0,
                "shared_anchors": [],
                "signals": [
                    {
                        "kind": "structured-polarity-conflict",
                        "label": "The same structured proposition has opposite declared polarity",
                    }
                ],
            },
            "qualified",
        )

    left_dimension = left_attributes.get("object_term_iri")
    right_dimension = right_attributes.get("object_term_iri")
    if not left_dimension or left_dimension != right_dimension:
        return None, "different-analysis-dimension"

    left_text = left_attributes.get("interpretation")
    right_text = right_attributes.get("interpretation")
    left_tokens = _word_tokens(left_text)
    right_tokens = _word_tokens(right_text)
    numeric_left = _numeric_values(left_text)
    numeric_right = _numeric_values(right_text)
    ignored = set(CONTRADICTION_STOPWORDS | POLARITY_CUE_TOKENS | NEGATION_CUES)
    ignored.update(value.rstrip("%") for value in (*numeric_left, *numeric_right))
    left_proposition_tokens = left_tokens - ignored
    right_proposition_tokens = right_tokens - ignored
    similarity = _token_jaccard(left_proposition_tokens, right_proposition_tokens)
    token_difference = len(left_proposition_tokens ^ right_proposition_tokens)
    shared_anchors = _rare_shared_terms(
        left_proposition_tokens, right_proposition_tokens, term_metrics
    )
    rare_score = sum(row["idf"] for row in shared_anchors[:4])
    if len(shared_anchors) < STRICT_MIN_SHARED_ANCHORS or rare_score < 3.5:
        return None, "insufficient-shared-proposition-anchors"

    left_negated = _strict_negation_state(left_text)
    right_negated = _strict_negation_state(right_text)
    if left_negated is None or right_negated is None:
        return None, "ambiguous-negation-scope"
    if (
        left_negated != right_negated
        and similarity >= STRICT_NEGATION_SIMILARITY_FLOOR
        and token_difference <= STRICT_MAX_TOKEN_DIFFERENCE
    ):
        return (
            {
                "detection_kind": "exact-negation",
                "minimum_similarity": STRICT_NEGATION_SIMILARITY_FLOOR,
                "proposition_similarity": _round(similarity, 6),
                "token_difference": token_difference,
                "shared_anchors": shared_anchors[:8],
                "signals": [
                    {
                        "kind": "strict-negation-conflict",
                        "label": "Near-identical proposition wording has opposite explicit negation",
                    }
                ],
            },
            "qualified",
        )

    directional_signals = _directional_opposition_signals(left_tokens, right_tokens)
    if (
        directional_signals
        and similarity >= STRICT_DIRECTIONAL_SIMILARITY_FLOOR
        and token_difference <= STRICT_MAX_TOKEN_DIFFERENCE
    ):
        return (
            {
                "detection_kind": "directional-opposition",
                "minimum_similarity": STRICT_DIRECTIONAL_SIMILARITY_FLOOR,
                "proposition_similarity": _round(similarity, 6),
                "token_difference": token_difference,
                "shared_anchors": shared_anchors[:8],
                "signals": directional_signals,
            },
            "qualified",
        )

    if (
        len(numeric_left) == len(numeric_right) == 1
        and numeric_left != numeric_right
        and similarity >= STRICT_NUMERIC_SIMILARITY_FLOOR
        and token_difference <= 2
    ):
        return (
            {
                "detection_kind": "numeric-disagreement",
                "minimum_similarity": STRICT_NUMERIC_SIMILARITY_FLOOR,
                "proposition_similarity": _round(similarity, 6),
                "token_difference": token_difference,
                "shared_anchors": shared_anchors[:8],
                "signals": [
                    {
                        "kind": "strict-numeric-disagreement",
                        "left": list(numeric_left),
                        "right": list(numeric_right),
                        "label": "Near-identical proposition context declares different numeric values",
                    }
                ],
            },
            "qualified",
        )

    if similarity < STRICT_DIRECTIONAL_SIMILARITY_FLOOR:
        return None, "insufficient-proposition-alignment"
    return None, "compatible-or-unresolved-polarity"


def _heuristic_contradiction_candidates(
    records: list[dict[str, Any]],
    term_metrics: dict[str, dict[str, Any]],
    excluded_pairs: set[tuple[str, str]],
) -> tuple[list[dict[str, Any]], int, int, dict[str, Any]]:
    claims = []
    for record in records:
        attributes = record.get("attributes") or {}
        interpretation = attributes.get("interpretation")
        subject = _comparison_subject(record)
        if not isinstance(interpretation, str) or not interpretation.strip() or not subject:
            continue
        review_state = attributes.get("review_state")
        if review_state not in (None, "", "reviewed"):
            continue
        claims.append(record)

    by_subject: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for claim in claims:
        subject = _comparison_subject(claim)
        if subject:
            by_subject[subject].append(claim)

    candidates: list[dict[str, Any]] = []
    rejection_counts: Counter[str] = Counter()
    loose_signal_count = 0
    qualified_loose_signals = 0
    evaluated_pairs = 0
    for subject, subject_claims in sorted(by_subject.items()):
        for left, right in combinations(
            sorted(subject_claims, key=lambda row: str(row.get("record_id") or "")), 2
        ):
            evaluated_pairs += 1
            left_id = str(left.get("record_id") or left.get("concept_id") or "")
            right_id = str(right.get("record_id") or right.get("concept_id") or "")
            pair = tuple(sorted((left_id, right_id)))
            if not all(pair) or pair in excluded_pairs:
                continue

            left_attributes = left.get("attributes") or {}
            right_attributes = right.get("attributes") or {}
            left_tokens = _word_tokens(left_attributes.get("interpretation"))
            right_tokens = _word_tokens(right_attributes.get("interpretation"))
            left_content = left_tokens - CONTRADICTION_STOPWORDS
            right_content = right_tokens - CONTRADICTION_STOPWORDS
            rare_terms = _rare_shared_terms(left_content, right_content, term_metrics)
            rare_score = sum(row["idf"] for row in rare_terms[:4])
            kind_pair = frozenset(
                (
                    str(left_attributes.get("claim_kind") or ""),
                    str(right_attributes.get("claim_kind") or ""),
                )
            )
            loose_signal = _legacy_loose_signal(
                kind_pair,
                left_tokens,
                right_tokens,
                rare_score,
                _token_jaccard(left_content, right_content),
            )
            if loose_signal:
                loose_signal_count += 1

            strict, rejection_reason = _strict_lexical_conflict(left, right, term_metrics)
            if strict is None:
                if loose_signal:
                    rejection_counts[rejection_reason] += 1
                continue
            if loose_signal:
                qualified_loose_signals += 1

            same_dimension = bool(left_attributes.get("object_term_iri")) and (
                left_attributes.get("object_term_iri") == right_attributes.get("object_term_iri")
            )
            source_scope = (
                "same-source"
                if left.get("source_id") and left.get("source_id") == right.get("source_id")
                else "cross-source"
            )
            candidates.append(
                {
                    "candidate_id": f"candidate-{sha256_bytes(canonical_json(pair).encode('utf-8'))[:16]}",
                    "status": "strict-review-required",
                    "detection_kind": strict["detection_kind"],
                    "alignment_score": strict["proposition_similarity"],
                    "alignment": {
                        "same_structured_subject": True,
                        "same_analysis_dimension": same_dimension,
                        "subject_term_iri": subject,
                        "left_object_term_iri": left_attributes.get("object_term_iri"),
                        "right_object_term_iri": right_attributes.get("object_term_iri"),
                        "proposition_similarity": strict["proposition_similarity"],
                        "minimum_similarity": strict["minimum_similarity"],
                        "token_difference": strict["token_difference"],
                    },
                    "source_scope": source_scope,
                    "shared_anchors": strict["shared_anchors"],
                    "signals": strict["signals"],
                    "scope_warning": (
                        "The pair passed a precision-first surface or structured alignment gate, but hidden "
                        "conditions, baselines, time periods, or definitions may still reconcile it. Review "
                        "both cited evidence locations before accepting a contradiction."
                    ),
                    "claim_a": _claim_payload(left),
                    "claim_b": _claim_payload(right),
                }
            )

    detection_order = {
        "structured-polarity": 0,
        "exact-negation": 1,
        "directional-opposition": 2,
        "numeric-disagreement": 3,
    }
    candidates.sort(
        key=lambda row: (
            detection_order[row["detection_kind"]],
            -float(row["alignment_score"] or 0.0),
            row["candidate_id"],
        )
    )
    return (
        candidates,
        evaluated_pairs,
        len(claims),
        {
            "loose_signal_count": loose_signal_count,
            "filtered_loose_signal_count": loose_signal_count - qualified_loose_signals,
            "rejection_reasons": dict(sorted(rejection_counts.items())),
        },
    )


def detect_contradictions(
    records: list[dict[str, Any]], term_metrics: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    declared, declared_pairs, declared_relations = _explicit_contradiction_pairs(records)
    candidates, evaluated_pairs, eligible_claims, audit = _heuristic_contradiction_candidates(
        records, term_metrics, declared_pairs
    )
    displayed = candidates[:MAX_CONTRADICTION_CANDIDATES]
    detection_counts = Counter(row["detection_kind"] for row in candidates)
    return {
        "schema": CONTRADICTION_SCHEMA,
        "status": (
            "source-declared-and-strict-candidates"
            if declared and candidates
            else "source-declared-only"
            if declared
            else "strict-candidates-only"
            if candidates
            else "no-qualified-conflicts"
        ),
        "summary": {
            "eligible_claims": eligible_claims,
            "evaluated_pairs": evaluated_pairs,
            "declared_relation_count": declared_relations,
            "declared_count": len(declared),
            "strict_candidate_count": len(candidates),
            "displayed_strict_candidate_count": len(displayed),
            "loose_signal_count": audit["loose_signal_count"],
            "filtered_loose_signal_count": audit["filtered_loose_signal_count"],
            "rejection_reasons": audit["rejection_reasons"],
            "by_detection_kind": {
                kind: detection_counts.get(kind, 0)
                for kind in (
                    "structured-polarity",
                    "exact-negation",
                    "directional-opposition",
                    "numeric-disagreement",
                )
            },
        },
        "method": {
            "source_declared_definition": (
                "Only an explicit source-metadata contradiction relation is shown as source-declared."
            ),
            "strict_candidate_definition": (
                "A strict candidate must align the same structured subject and analysis dimension, share "
                "at least three rare proposition anchors, and express near-identical context with exact "
                "negation, one unambiguous directional opposition, or one conflicting numeric value. An "
                "exact structured proposition key with opposite declared polarity also qualifies."
            ),
            "loose_signal_definition": (
                "Broad strength-versus-limitation and polarity matches are counted for quality auditing, "
                "then excluded unless they pass the strict proposition gate."
            ),
            "ranking_is_probability": False,
            "lexical_idf_floor": 1.5,
            "minimum_shared_anchors": STRICT_MIN_SHARED_ANCHORS,
            "similarity_floors": {
                "exact_negation": STRICT_NEGATION_SIMILARITY_FLOOR,
                "directional_opposition": STRICT_DIRECTIONAL_SIMILARITY_FLOOR,
                "numeric_disagreement": STRICT_NUMERIC_SIMILARITY_FLOOR,
            },
            "candidate_display_limit": MAX_CONTRADICTION_CANDIDATES,
            "limitations": [
                "A strict lexical candidate is still a review item, not a factual adjudication.",
                "Conditions omitted from a short interpretation may reconcile apparently incompatible claims.",
                "Cross-source detection requires a shared structured subject; paper-local identifiers cannot be guessed safely.",
                "No qualified conflict does not prove that the knowledge base is consistent.",
                "Every candidate requires review of both authoritative evidence locators.",
            ],
        },
        "declared": declared,
        "strict_candidates": displayed,
    }


def build_projection(root: Path, bundle: dict[str, Any]) -> dict[str, Any]:
    classical_index = bundle["classical_index"]
    classical_report = bundle["classical_report"]
    semantic_report = bundle["semantic_report"]
    source_manifest = bundle["source_manifest"]
    semantic_plan = bundle["semantic_plan"]
    records = bundle["records"]
    documents = bundle["documents"]
    associations = bundle["associations"]
    lexicon = bundle["lexicon"]
    topics_document = bundle["topics"]

    type_counts = Counter(str(record.get("concept_type") or "Unknown") for record in records)
    year_counts = Counter(year for record in records if (year := _record_year(record)) is not None)
    attribute_counts: Counter[str] = Counter()
    for record in records:
        attribute_counts.update(str(key) for key in (record.get("attributes") or {}))

    compact_records = []
    for record in records:
        compact_records.append(
            {
                "concept_id": record.get("concept_id"),
                "concept_path": record.get("concept_path"),
                "concept_type": record.get("concept_type"),
                "record_id": record.get("record_id"),
                "source_id": record.get("source_id"),
                "source_kind": record.get("source_kind"),
                "source_path": record.get("source_path"),
                "subject_iri": record.get("subject_iri"),
                "title": record.get("title"),
                "year": _record_year(record),
                "attributes": record.get("attributes") or {},
                "body_characters": len(str(record.get("body") or "")),
                "description": _short_text((record.get("attributes") or {}).get("description") or record.get("body")),
            }
        )

    term_rows = lexicon.get("terms") or []
    term_metrics = {str(row.get("term")): row for row in term_rows}
    contradictions = detect_contradictions(records, term_metrics)
    df_buckets = Counter(_bucket_document_frequency(int(row.get("document_frequency") or 0)) for row in term_rows)
    idf_values = [float(row.get("idf") or 0.0) for row in term_rows]
    top_by_df = sorted(
        term_rows,
        key=lambda row: (
            -int(row.get("document_frequency") or 0),
            -int(row.get("corpus_frequency") or 0),
            str(row.get("term") or ""),
        ),
    )[:24]

    association_map = {str(row.get("term")): row for row in associations}
    association_ppmi: list[float] = []
    association_edges = 0
    association_cooccurrence = 0
    for row in associations:
        for neighbor in row.get("neighbors") or []:
            association_edges += 1
            association_ppmi.append(float(neighbor.get("ppmi") or 0.0))
            association_cooccurrence += int(neighbor.get("cooccurrence") or 0)

    document_topics: dict[str, list[tuple[float, dict[str, Any]]]] = defaultdict(list)
    dominant_topic_counts: Counter[str] = Counter()
    compact_documents = []
    for document in documents:
        weights = [row for row in document.get("topic_weights") or [] if row.get("topic_id")]
        dominant = max(weights, key=lambda row: (float(row.get("weight") or 0.0), str(row.get("topic_id"))), default=None)
        if dominant:
            dominant_topic_counts[str(dominant["topic_id"])] += 1
        for weight in weights:
            document_topics[str(weight["topic_id"])].append((float(weight.get("weight") or 0.0), document))
        locator = document.get("locator") or {}
        compact_documents.append(
            {
                "document_id": document.get("document_id"),
                "title": document.get("title"),
                "concept_type": document.get("concept_type"),
                "concept_id": document.get("concept_id"),
                "concept_path": document.get("concept_path"),
                "record_id": document.get("record_id"),
                "source_id": document.get("source_id"),
                "source_path": document.get("source_path"),
                "paper_id": document.get("paper_id"),
                "ordinal": document.get("ordinal"),
                "locator": locator,
                "body_length": document.get("body_length"),
                "title_length": document.get("title_length"),
                "text_sha256": document.get("text_sha256"),
                "text_preview": _short_text(document.get("text"), 260),
                "dominant_topic": dominant.get("topic_id") if dominant else None,
                "dominant_weight": _round(dominant.get("weight") or 0.0, 8) if dominant else 0.0,
                "topic_weights": weights,
            }
        )

    topics = []
    for topic in topics_document.get("topics") or []:
        topic_id = str(topic.get("topic_id"))
        weighted_documents = sorted(
            document_topics.get(topic_id) or [],
            key=lambda pair: (-pair[0], str(pair[1].get("document_id") or "")),
        )
        representative = []
        seen_sources: set[str] = set()
        for weight, document in weighted_documents:
            source_id = str(document.get("source_id") or "")
            if source_id in seen_sources and len(representative) < 3:
                continue
            representative.append(
                {
                    "document_id": document.get("document_id"),
                    "title": document.get("title"),
                    "concept_type": document.get("concept_type"),
                    "concept_path": document.get("concept_path"),
                    "source_id": source_id,
                    "paper_id": document.get("paper_id"),
                    "locator": document.get("locator") or {},
                    "text_preview": _short_text(document.get("text"), 240),
                    "weight": _round(weight, 8),
                }
            )
            seen_sources.add(source_id)
            if len(representative) >= 6:
                break
        topic_terms = []
        for row in topic.get("terms") or []:
            term = str(row.get("term") or "")
            metrics = term_metrics.get(term) or {}
            topic_terms.append(
                {
                    "term": term,
                    "weight": _round(row.get("weight") or 0.0, 8),
                    "document_frequency": int(metrics.get("document_frequency") or 0),
                    "corpus_frequency": int(metrics.get("corpus_frequency") or 0),
                    "idf": _round(metrics.get("idf") or 0.0, 8),
                }
            )
        topics.append(
            {
                "topic_id": topic_id,
                "seed": topic.get("seed"),
                "term_count": int(topic.get("term_count") or 0),
                "terms": topic_terms,
                "primary_document_count": dominant_topic_counts.get(topic_id, 0),
                "weighted_document_count": len(weighted_documents),
                "total_document_weight": _round(sum(weight for weight, _document in weighted_documents), 8),
                "source_count": len({str(document.get("source_id") or "") for _weight, document in weighted_documents}),
                "representative_documents": representative,
                "association_graph": _topic_graph(topic, association_map, term_metrics),
            }
        )

    selected_sources = set((classical_index.get("selection") or {}).get("eligible_source_ids") or [])
    excluded_sources = set((classical_index.get("selection") or {}).get("excluded_source_ids") or [])
    source_plan_by_id = {str(row.get("id")): row for row in semantic_plan.get("sources") or []}
    compact_sources = []
    for source in source_manifest.get("sources") or []:
        source_id = str(source.get("id") or "")
        plan_source = source_plan_by_id.get(source_id) or {}
        compact_sources.append(
            {
                **source,
                "concept_type": plan_source.get("concept_type"),
                "ontology_class": plan_source.get("ontology_class"),
                "classical_status": (
                    "selected" if source_id in selected_sources else "excluded" if source_id in excluded_sources else "core-only"
                ),
            }
        )

    bundle_metadata = semantic_plan.get("bundle") or {}
    ontology = semantic_plan.get("ontology") or {}
    inventory = {
        "records": len(records),
        "passages": len(documents),
        "terms": len(term_rows),
        "topics": len(topics),
        "association_terms": len(associations),
        "association_edges": association_edges,
        "semantic_sources": len(compact_sources),
        "classical_sources": len(selected_sources),
        "concept_types": len(type_counts),
        "ontology_classes": len(ontology.get("classes") or []),
        "ontology_properties": len(ontology.get("properties") or []),
        "validation_rules": len(semantic_plan.get("rules") or []),
        "source_declared_contradictions": contradictions["summary"]["declared_count"],
        "strict_contradiction_candidates": contradictions["summary"]["strict_candidate_count"],
        "filtered_loose_contradiction_signals": contradictions["summary"][
            "filtered_loose_signal_count"
        ],
    }

    return {
        "schema": ATLAS_SCHEMA,
        "generator": "visualize-semantic-okf-classical",
        "bundle": bundle_metadata,
        "inventory": inventory,
        "record_types": [
            {"label": label, "count": count}
            for label, count in sorted(type_counts.items(), key=lambda item: (-item[1], item[0]))
        ],
        "publication_years": [
            {"year": year, "count": count} for year, count in sorted(year_counts.items())
        ],
        "attribute_coverage": [
            {"attribute": attribute, "records": count}
            for attribute, count in sorted(attribute_counts.items(), key=lambda item: (-item[1], item[0]))
        ],
        "records": compact_records,
        "documents": compact_documents,
        "sources": sorted(compact_sources, key=lambda row: str(row.get("id") or "")),
        "topics": topics,
        "contradictions": contradictions,
        "lexical": {
            "document_count": lexicon.get("document_count"),
            "tokenization": lexicon.get("tokenization") or {},
            "bm25": lexicon.get("bm25") or {},
            "average_field_lengths": lexicon.get("average_field_lengths") or {},
            "unigram_count": sum(1 for row in term_rows if " " not in str(row.get("term") or "")),
            "bigram_count": sum(1 for row in term_rows if " " in str(row.get("term") or "")),
            "corpus_frequency_total": sum(int(row.get("corpus_frequency") or 0) for row in term_rows),
            "idf": {
                "minimum": _round(min(idf_values) if idf_values else 0.0),
                "maximum": _round(max(idf_values) if idf_values else 0.0),
                "mean": _round(sum(idf_values) / len(idf_values) if idf_values else 0.0),
            },
            "document_frequency_buckets": [
                {"label": label, "count": df_buckets.get(label, 0)}
                for label in ("1", "2–4", "5–19", "20–99", "100+")
            ],
            "top_by_document_frequency": top_by_df,
        },
        "associations": {
            "term_count": len(associations),
            "directed_edge_count": association_edges,
            "cooccurrence_total": association_cooccurrence,
            "ppmi": {
                "minimum": _round(min(association_ppmi) if association_ppmi else 0.0, 8),
                "maximum": _round(max(association_ppmi) if association_ppmi else 0.0, 8),
                "mean": _round(sum(association_ppmi) / len(association_ppmi) if association_ppmi else 0.0, 8),
            },
        },
        "ontology": {
            "classes": ontology.get("classes") or [],
            "properties": ontology.get("properties") or [],
            "rules": semantic_plan.get("rules") or [],
        },
        "integrity": {
            "source_tree": bundle["source_tree"],
            "core": classical_index.get("core") or {},
            "selection": classical_index.get("selection") or {},
            "classical_status": classical_report.get("status"),
            "classical_valid": classical_report.get("valid"),
            "semantic_status": semantic_report.get("status"),
            "semantic_valid": semantic_report.get("valid"),
            "semantic_summary": semantic_report.get("summary") or {},
            "validation": source_manifest.get("validation") or {},
            "artifacts": classical_report.get("artifacts") or {},
            "algorithms": classical_index.get("algorithms") or {},
            "plan_sha256": classical_index.get("classical_plan_sha256"),
        },
        "contracts": {
            "classical_index": classical_index,
            "classical_build_report": classical_report,
            "semantic_build_report": semantic_report,
            "semantic_source_manifest": source_manifest,
            "semantic_plan": semantic_plan,
        },
    }


def render_html(template_path: Path, projection: dict[str, Any]) -> bytes:
    try:
        template = template_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise AtlasError(f"cannot read atlas template: {exc}") from exc
    placeholder = "__CLASSICAL_ATLAS_DATA__"
    if template.count(placeholder) != 1:
        raise AtlasError("atlas template must contain exactly one data placeholder")
    embedded = canonical_json(projection).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    return template.replace(placeholder, embedded).encode("utf-8")


def build_expected_files(root: Path, template_path: Path) -> dict[str, bytes]:
    bundle = validate_bundle(root)
    projection = build_projection(root, bundle)
    projection_bytes = pretty_json_bytes(projection)
    html_bytes = render_html(template_path, projection)
    receipt = {
        "schema": RECEIPT_SCHEMA,
        "generator": "visualize-semantic-okf-classical",
        "source": bundle["source_tree"],
        "bindings": {
            "core_tree_sha256": (bundle["classical_index"].get("core") or {}).get("tree_sha256"),
            "records_sha256": (bundle["classical_index"].get("core") or {}).get("records_sha256"),
            "classical_plan_sha256": bundle["classical_index"].get("classical_plan_sha256"),
        },
        "projection": {
            "schema": projection["schema"],
            "records": projection["inventory"]["records"],
            "passages": projection["inventory"]["passages"],
            "terms": projection["inventory"]["terms"],
            "topics": projection["inventory"]["topics"],
            "association_terms": projection["inventory"]["association_terms"],
            "source_declared_contradictions": projection["inventory"][
                "source_declared_contradictions"
            ],
            "strict_contradiction_candidates": projection["inventory"][
                "strict_contradiction_candidates"
            ],
            "filtered_loose_contradiction_signals": projection["inventory"][
                "filtered_loose_contradiction_signals"
            ],
        },
        "artifacts": {
            "index.html": {"bytes": len(html_bytes), "sha256": sha256_bytes(html_bytes)},
            "projection.json": {"bytes": len(projection_bytes), "sha256": sha256_bytes(projection_bytes)},
        },
    }
    return {
        "index.html": html_bytes,
        "projection.json": projection_bytes,
        "receipt.json": pretty_json_bytes(receipt),
    }


def write_atlas(root: Path, output: Path, template_path: Path, check: bool = False) -> dict[str, Any]:
    root, output = require_disjoint_paths(root, output)
    expected = build_expected_files(root, template_path)
    if check:
        if not output.is_dir():
            raise AtlasError(f"atlas output does not exist: {output}")
        actual_names = {path.name for path in output.iterdir()}
        if actual_names != EXPECTED_OUTPUT_FILES:
            raise AtlasError("atlas output closed-file set does not match")
        for name, expected_bytes in expected.items():
            path = output / name
            if not path.is_file() or path.is_symlink() or path.read_bytes() != expected_bytes:
                raise AtlasError(f"atlas drift detected: {name}")
        return {"status": "pass", "check": True, "output": str(output), "source_unchanged": True}

    if output.exists():
        raise AtlasError(f"atlas output already exists: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    candidate = Path(tempfile.mkdtemp(prefix=f".{output.name}.candidate-", dir=output.parent))
    try:
        for name, value in expected.items():
            (candidate / name).write_bytes(value)
        candidate.replace(output)
    except Exception:
        if candidate.exists() and _is_relative_to(candidate.resolve(), output.parent.resolve()):
            shutil.rmtree(candidate)
        raise
    return {"status": "pass", "check": False, "output": str(output), "source_unchanged": True}


def validate_atlas(root: Path, output: Path, template_path: Path) -> dict[str, Any]:
    root, output = require_disjoint_paths(root, output)
    if not output.is_dir():
        raise AtlasError(f"atlas output does not exist: {output}")
    for path in output.rglob("*"):
        if path.is_symlink():
            raise AtlasError(f"atlas contains a symlink: {path}")
    actual_names = {path.name for path in output.iterdir()}
    if actual_names != EXPECTED_OUTPUT_FILES:
        raise AtlasError("atlas output must contain exactly index.html, projection.json, and receipt.json")

    projection = read_json(output / "projection.json")
    receipt = read_json(output / "receipt.json")
    if projection.get("schema") != ATLAS_SCHEMA or receipt.get("schema") != RECEIPT_SCHEMA:
        raise AtlasError("atlas schema mismatch")

    contradictions = projection.get("contradictions") or {}
    contradiction_summary = contradictions.get("summary") or {}
    declared = contradictions.get("declared") or []
    candidates = contradictions.get("strict_candidates") or []
    if contradictions.get("schema") != CONTRADICTION_SCHEMA:
        raise AtlasError("contradiction review schema mismatch")
    if contradiction_summary.get("declared_count") != len(declared):
        raise AtlasError("source-declared contradiction count mismatch")
    if contradiction_summary.get("displayed_strict_candidate_count") != len(candidates):
        raise AtlasError("displayed strict contradiction candidate count mismatch")
    if contradiction_summary.get("strict_candidate_count", 0) < len(candidates):
        raise AtlasError("strict contradiction candidate count is smaller than its display projection")
    loose_count = int(contradiction_summary.get("loose_signal_count") or 0)
    filtered_count = int(contradiction_summary.get("filtered_loose_signal_count") or 0)
    if filtered_count > loose_count:
        raise AtlasError("filtered loose contradiction signals exceed detected loose signals")
    if any(row.get("status") != "source-declared" for row in declared):
        raise AtlasError("declared contradictions must come from source metadata")
    allowed_detection_kinds = {
        "structured-polarity",
        "exact-negation",
        "directional-opposition",
        "numeric-disagreement",
    }
    if any(row.get("status") != "strict-review-required" for row in candidates):
        raise AtlasError("strict contradiction candidates must require review")
    if any(row.get("detection_kind") not in allowed_detection_kinds for row in candidates):
        raise AtlasError("strict contradiction candidate has an unknown detection kind")
    for row in candidates:
        alignment = row.get("alignment") or {}
        if not alignment.get("same_structured_subject"):
            raise AtlasError("strict contradiction candidates must share a structured subject")
        if row.get("detection_kind") != "structured-polarity" and not alignment.get(
            "same_analysis_dimension"
        ):
            raise AtlasError("strict lexical candidates must share an analysis dimension")
    for row in [*declared, *candidates]:
        for side in ("claim_a", "claim_b"):
            claim = row.get(side) or {}
            if not claim.get("record_id") or not claim.get("concept_path"):
                raise AtlasError("contradiction entries must preserve record and concept identity")

    current_source = tree_receipt(root)
    if receipt.get("source") != current_source:
        raise AtlasError("knowledge source tree changed after atlas generation")

    artifacts = receipt.get("artifacts") or {}
    for name in ("index.html", "projection.json"):
        path = output / name
        entry = artifacts.get(name) or {}
        if entry.get("sha256") != file_sha256(path) or entry.get("bytes") != path.stat().st_size:
            raise AtlasError(f"generated artifact receipt mismatch: {name}")

    html = (output / "index.html").read_text(encoding="utf-8")
    opening = '<script id="atlas-data" type="application/json">'
    closing = "</script>"
    start = html.find(opening)
    if start < 0:
        raise AtlasError("embedded atlas data element is missing")
    start += len(opening)
    end = html.find(closing, start)
    if end < 0:
        raise AtlasError("embedded atlas data element is not closed")
    try:
        embedded = json.loads(html[start:end])
    except json.JSONDecodeError as exc:
        raise AtlasError(f"embedded atlas data is invalid: {exc}") from exc
    if embedded != projection:
        raise AtlasError("embedded atlas data differs from projection.json")
    external_resource_markers = (
        '<script src="http',
        "<script src='http",
        '<link href="http',
        "<link href='http",
        '<img src="http',
        "<img src='http",
        'fetch("http',
        "fetch('http",
        "xmlhttprequest",
        "new websocket",
    )
    lowered_html = html.lower()
    if any(marker in lowered_html for marker in external_resource_markers):
        raise AtlasError("atlas must not load external network resources")

    expected = build_expected_files(root, template_path)
    for name, expected_bytes in expected.items():
        if (output / name).read_bytes() != expected_bytes:
            raise AtlasError(f"atlas does not reproduce deterministically: {name}")

    inventory = projection.get("inventory") or {}
    return {
        "status": "pass",
        "source_unchanged": True,
        "records": inventory.get("records"),
        "passages": inventory.get("passages"),
        "terms": inventory.get("terms"),
        "topics": inventory.get("topics"),
        "association_terms": inventory.get("association_terms"),
        "source_declared_contradictions": inventory.get("source_declared_contradictions"),
        "strict_contradiction_candidates": inventory.get("strict_contradiction_candidates"),
        "filtered_loose_contradiction_signals": inventory.get(
            "filtered_loose_contradiction_signals"
        ),
        "output": str(output),
    }


def format_result(result: dict[str, Any], output_format: str) -> str:
    if output_format == "json":
        return canonical_json(result)
    details = ", ".join(f"{key}={value}" for key, value in result.items() if key != "status")
    return f"PASS: {details}"
