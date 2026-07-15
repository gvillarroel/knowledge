#!/usr/bin/env python3
"""Pure deterministic derivation for the Semantic OKF entity-section graph."""

from __future__ import annotations

import hashlib
import json
import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Mapping, Sequence


SCHEMA_VERSION = "1.0"
TOKENIZER_ID = "ascii-alphanumeric-v1"
STOPWORDS_ID = "english-v1"
TOKEN_RE = re.compile(r"[a-z0-9]+", re.IGNORECASE)
PAGE_RE = re.compile(r"(?m)^## PDF page (?P<page>\d+)\s*$")
HEX_64 = re.compile(r"[0-9a-f]{64}")

STOPWORDS = frozenset(
    "a about above after again against all am an and any are as at be because been before being below "
    "between both but by can could did do does doing down during each few for from further had has have "
    "having he her here hers herself him himself his how i if in into is it its itself just me more most "
    "my myself no nor not now of off on once only or other our ours ourselves out over own same she should "
    "so some such than that the their theirs them themselves then there these they this those through to too "
    "under until up very was we were what when where which while who whom why will with you your yours "
    "yourself yourselves".split()
)

PLAN_KEYS = {
    "schema_version",
    "selection",
    "sectioning",
    "tokenization",
    "extraction",
    "bm25",
    "graph",
    "query",
}
ENTITY_KEYS = {
    "entity_id",
    "entity_type",
    "canonical_label",
    "aliases",
    "review_state",
    "authoritative_identity",
    "extraction",
}
IDENTITY_KEYS = {
    "source_id",
    "record_id",
    "record_sha256",
    "concept_id",
    "concept_path",
    "subject_iri",
}
EXTRACTION_KEYS = {
    "algorithm",
    "section_frequency",
    "total_occurrences",
    "score",
}
SECTION_KEYS = {
    "section_id",
    "paper_entity_id",
    "paper_id",
    "source_id",
    "record_id",
    "record_sha256",
    "concept_id",
    "concept_path",
    "source_path",
    "ordinal",
    "heading",
    "locator",
    "text",
    "text_sha256",
    "terms",
    "length",
}
LOCATOR_KEYS = {"kind", "start", "end", "fragment"}
MENTION_KEYS = {
    "mention_id",
    "entity_id",
    "section_id",
    "count",
    "matched_aliases",
    "review_state",
    "semantic_source",
}
EDGE_KEYS = {
    "edge_id",
    "source_node",
    "predicate",
    "target_node",
    "review_state",
    "semantic_source",
    "claim_record_id",
    "evidence_section_ids",
    "weight",
}
LEXICON_KEYS = {
    "schema_version",
    "tokenizer",
    "stopwords",
    "document_count",
    "average_length",
    "terms",
}

ALGORITHMS = {
    "sectioning": "pdf-page-heading-character-range-v1",
    "entity_extraction": "bounded-corpus-salient-ngram-v1",
    "mention_matching": "normalized-longest-phrase-match-v1",
    "reviewed_relations": "semantic-okf-reviewed-claim-projection-v1",
    "candidate_relations": "section-co-mention-v1",
    "lexical_scoring": "okapi-bm25-v1",
    "entity_scoring": "alias-overlap-plus-mention-evidence-v1",
    "graph_scoring": "bounded-provenance-aware-traversal-v1",
    "fusion": "reciprocal-rank-fusion-v1",
    "reranking": "source-diversified-ranking-v1",
}
DERIVED_ROOTS = frozenset({"adaptive", "entity-graph", "retrieval", "ensemble"})

PREDICATES = {
    "hasReviewedClaim",
    "objectTerm",
    "aboutPaper",
    "supportedBySection",
    "partOfPaper",
    "mentionedInSection",
    "coMentionedWith",
}


class EntityGraphError(RuntimeError):
    """Describe an invalid plan, core binding, or derived entity graph."""


@dataclass(frozen=True)
class EntityGraphPlan:
    """Hold one validated closed entity-graph plan."""

    raw: dict[str, Any]
    sha256: str
    paper_source_ids: tuple[str, ...]
    claim_source_ids: tuple[str, ...]
    vocabulary_source_id: str

    @property
    def source_ids(self) -> tuple[str, ...]:
        """Return every selected source ID in deterministic order."""

        return tuple(sorted((*self.paper_source_ids, *self.claim_source_ids, self.vocabulary_source_id)))


def canonical_json(value: Any) -> str:
    """Serialize JSON deterministically and reject non-finite numbers."""

    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sha256_bytes(value: bytes) -> str:
    """Return a lowercase SHA-256 digest for bytes."""

    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    """Return a lowercase SHA-256 digest for one file."""

    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_canonical(value: Any) -> str:
    """Hash deterministic UTF-8 JSON."""

    return sha256_bytes(canonical_json(value).encode("utf-8"))


def strict_json_loads(payload: str, *, label: str) -> Any:
    """Load JSON while rejecting duplicate keys and non-standard numbers."""

    def reject_constant(value: str) -> Any:
        raise EntityGraphError(f"{label} contains non-standard number {value!r}")

    def reject_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise EntityGraphError(f"{label} contains duplicate member {key!r}")
            result[key] = value
        return result

    try:
        return json.loads(payload, object_pairs_hook=reject_duplicates, parse_constant=reject_constant)
    except json.JSONDecodeError as exc:
        raise EntityGraphError(f"{label} is invalid JSON: {exc}") from exc


def exact_keys(value: Mapping[str, Any], expected: set[str], label: str) -> None:
    """Require an exact closed object schema."""

    actual = set(value)
    if actual != expected:
        raise EntityGraphError(
            f"{label} has a closed schema; missing={sorted(expected - actual)}, "
            f"unknown={sorted(actual - expected)}"
        )


def _plain_int(value: Any, label: str, minimum: int, maximum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not minimum <= value <= maximum:
        raise EntityGraphError(f"{label} must be an integer from {minimum} through {maximum}")
    return value


def _finite(value: Any, label: str, minimum: float, maximum: float) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise EntityGraphError(f"{label} must be numeric")
    result = float(value)
    if not math.isfinite(result) or not minimum <= result <= maximum:
        raise EntityGraphError(f"{label} must be finite from {minimum} through {maximum}")
    return result


def _source_id_list(value: Any, label: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not value or any(not isinstance(item, str) or not item for item in value):
        raise EntityGraphError(f"{label} must be a nonempty string array")
    if len(set(value)) != len(value) or value != sorted(value):
        raise EntityGraphError(f"{label} must be unique and sorted")
    return tuple(value)


def parse_plan(value: Any) -> EntityGraphPlan:
    """Validate one closed plan object."""

    if not isinstance(value, dict):
        raise EntityGraphError("entity-graph plan root must be an object")
    exact_keys(value, PLAN_KEYS, "entity-graph plan")
    if value["schema_version"] != SCHEMA_VERSION:
        raise EntityGraphError(f"entity-graph plan schema_version must be {SCHEMA_VERSION}")

    selection = value["selection"]
    if not isinstance(selection, dict):
        raise EntityGraphError("selection must be an object")
    exact_keys(selection, {"paper_source_ids", "claim_source_ids", "vocabulary_source_id"}, "selection")
    papers = _source_id_list(selection["paper_source_ids"], "selection.paper_source_ids")
    claims = _source_id_list(selection["claim_source_ids"], "selection.claim_source_ids")
    vocabulary = selection["vocabulary_source_id"]
    if not isinstance(vocabulary, str) or not vocabulary:
        raise EntityGraphError("selection.vocabulary_source_id must be nonempty")
    all_sources = [*papers, *claims, vocabulary]
    if len(set(all_sources)) != len(all_sources):
        raise EntityGraphError("selected paper, claim, and vocabulary source IDs must not overlap")

    sectioning = value["sectioning"]
    if not isinstance(sectioning, dict):
        raise EntityGraphError("sectioning must be an object")
    exact_keys(sectioning, {"strategy", "minimum_characters"}, "sectioning")
    if sectioning["strategy"] != "pdf-page-headings-v1":
        raise EntityGraphError("sectioning.strategy must be pdf-page-headings-v1")
    _plain_int(sectioning["minimum_characters"], "sectioning.minimum_characters", 1, 10000)

    tokenization = value["tokenization"]
    if not isinstance(tokenization, dict):
        raise EntityGraphError("tokenization must be an object")
    exact_keys(tokenization, {"tokenizer", "stopwords", "min_token_length"}, "tokenization")
    if tokenization["tokenizer"] != TOKENIZER_ID or tokenization["stopwords"] != STOPWORDS_ID:
        raise EntityGraphError("tokenization identifiers are unsupported")
    _plain_int(tokenization["min_token_length"], "tokenization.min_token_length", 1, 20)

    extraction = value["extraction"]
    if not isinstance(extraction, dict):
        raise EntityGraphError("extraction must be an object")
    exact_keys(
        extraction,
        {
            "ngram_range",
            "minimum_section_frequency",
            "maximum_section_fraction",
            "maximum_candidates",
            "top_candidates_per_section",
        },
        "extraction",
    )
    ngram_range = extraction["ngram_range"]
    if (
        not isinstance(ngram_range, list)
        or len(ngram_range) != 2
        or any(isinstance(item, bool) or not isinstance(item, int) for item in ngram_range)
        or not 1 <= ngram_range[0] <= ngram_range[1] <= 5
    ):
        raise EntityGraphError("extraction.ngram_range must be two ordered integers from 1 through 5")
    _plain_int(extraction["minimum_section_frequency"], "extraction.minimum_section_frequency", 1, 1000)
    _finite(extraction["maximum_section_fraction"], "extraction.maximum_section_fraction", 0.01, 1.0)
    _plain_int(extraction["maximum_candidates"], "extraction.maximum_candidates", 1, 100000)
    _plain_int(extraction["top_candidates_per_section"], "extraction.top_candidates_per_section", 1, 1000)

    bm25 = value["bm25"]
    if not isinstance(bm25, dict):
        raise EntityGraphError("bm25 must be an object")
    exact_keys(bm25, {"k1", "b"}, "bm25")
    _finite(bm25["k1"], "bm25.k1", 0.01, 10.0)
    _finite(bm25["b"], "bm25.b", 0.0, 1.0)

    graph = value["graph"]
    if not isinstance(graph, dict):
        raise EntityGraphError("graph must be an object")
    exact_keys(
        graph,
        {
            "max_co_mentions_per_section",
            "minimum_co_mention_sections",
            "max_co_mention_neighbors",
            "max_edge_evidence_sections",
        },
        "graph",
    )
    _plain_int(graph["max_co_mentions_per_section"], "graph.max_co_mentions_per_section", 2, 100)
    _plain_int(graph["minimum_co_mention_sections"], "graph.minimum_co_mention_sections", 1, 1000)
    _plain_int(graph["max_co_mention_neighbors"], "graph.max_co_mention_neighbors", 1, 1000)
    _plain_int(graph["max_edge_evidence_sections"], "graph.max_edge_evidence_sections", 1, 1000)

    query = value["query"]
    if not isinstance(query, dict):
        raise EntityGraphError("query must be an object")
    exact_keys(
        query,
        {
            "resolved_entities",
            "max_hops",
            "hop_decay",
            "reviewed_edge_weight",
            "candidate_edge_weight",
            "mention_weight",
            "candidate_pool",
            "max_per_paper",
            "rrf_k",
        },
        "query",
    )
    _plain_int(query["resolved_entities"], "query.resolved_entities", 1, 1000)
    _plain_int(query["max_hops"], "query.max_hops", 1, 6)
    _finite(query["hop_decay"], "query.hop_decay", 0.01, 1.0)
    _finite(query["reviewed_edge_weight"], "query.reviewed_edge_weight", 0.01, 10.0)
    _finite(query["candidate_edge_weight"], "query.candidate_edge_weight", 0.0, 10.0)
    _finite(query["mention_weight"], "query.mention_weight", 0.01, 10.0)
    _plain_int(query["candidate_pool"], "query.candidate_pool", 1, 10000)
    _plain_int(query["max_per_paper"], "query.max_per_paper", 1, 1000)
    _plain_int(query["rrf_k"], "query.rrf_k", 1, 10000)

    normalized = json.loads(canonical_json(value))
    return EntityGraphPlan(normalized, sha256_canonical(normalized), papers, claims, vocabulary)


def load_plan(path: Path) -> EntityGraphPlan:
    """Read and validate one closed plan file."""

    try:
        value = strict_json_loads(path.read_text(encoding="utf-8"), label=str(path))
    except (OSError, UnicodeError) as exc:
        raise EntityGraphError(f"cannot read entity-graph plan at {path}: {exc}") from exc
    return parse_plan(value)


def safe_relative(value: str, label: str) -> PurePosixPath:
    """Validate and normalize one safe relative path."""

    candidate = PurePosixPath(value.replace("\\", "/"))
    if candidate.is_absolute() or not candidate.parts or any(part in {"", ".", ".."} for part in candidate.parts):
        raise EntityGraphError(f"{label} is not a safe relative path: {value!r}")
    return candidate


def read_json(path: Path, label: str) -> Any:
    """Read strict JSON from a local file."""

    try:
        return strict_json_loads(path.read_text(encoding="utf-8"), label=label)
    except (OSError, UnicodeError) as exc:
        raise EntityGraphError(f"cannot read {label}: {exc}") from exc


def read_jsonl(path: Path, *, label: str) -> list[dict[str, Any]]:
    """Read a strict nonblank JSONL object sequence."""

    rows: list[dict[str, Any]] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        raise EntityGraphError(f"cannot read {label}: {exc}") from exc
    for number, line in enumerate(lines, start=1):
        if not line:
            raise EntityGraphError(f"{label}:{number} is blank")
        value = strict_json_loads(line, label=f"{label}:{number}")
        if not isinstance(value, dict):
            raise EntityGraphError(f"{label}:{number} must be an object")
        rows.append(value)
    return rows


def core_inventory(root: Path) -> list[dict[str, str]]:
    """Hash the authoritative core while excluding the derived projection."""

    rows: list[dict[str, str]] = []
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        relative = path.relative_to(root)
        if relative.parts and relative.parts[0] in DERIVED_ROOTS:
            continue
        rows.append({"path": relative.as_posix(), "sha256": sha256_file(path)})
    return rows


def core_tree_sha256(root: Path) -> str:
    """Hash the complete authoritative core inventory."""

    return sha256_canonical(core_inventory(root))


def load_core(root: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Load the authoritative record ledger and generated source manifest."""

    records = read_jsonl(root / "semantic" / "records.jsonl", label="semantic/records.jsonl")
    source_manifest = read_json(root / "semantic" / "source-manifest.json", "semantic/source-manifest.json")
    sources = source_manifest.get("sources") if isinstance(source_manifest, dict) else None
    if not isinstance(sources, list) or any(not isinstance(item, dict) for item in sources):
        raise EntityGraphError("semantic/source-manifest.json must contain an object source array")
    return records, sources


def select_records(
    records: Sequence[dict[str, Any]], sources: Sequence[dict[str, Any]], plan: EntityGraphPlan
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Select and hash the exact plan-bound sources."""

    source_by_id = {
        str(source["id"]): source
        for source in sources
        if isinstance(source.get("id"), str) and source["id"]
    }
    missing = sorted(set(plan.source_ids) - set(source_by_id))
    if missing:
        raise EntityGraphError(f"entity-graph plan selects unknown source IDs: {missing}")
    selected = [record for record in records if record.get("source_id") in set(plan.source_ids)]
    eligible = sorted({str(record.get("source_id")) for record in selected})
    if eligible != list(plan.source_ids):
        raise EntityGraphError(f"selected source IDs produced no records: {sorted(set(plan.source_ids) - set(eligible))}")
    inventory = [
        {"source_id": source_id, "content_sha256": source_by_id[source_id].get("content_sha256")}
        for source_id in eligible
    ]
    if any(not HEX_64.fullmatch(str(row["content_sha256"])) for row in inventory):
        raise EntityGraphError("selected source inventory contains an invalid content digest")
    selection = {
        "paper_source_ids": list(plan.paper_source_ids),
        "claim_source_ids": list(plan.claim_source_ids),
        "vocabulary_source_id": plan.vocabulary_source_id,
        "eligible_source_ids": eligible,
        "excluded_source_ids": sorted(set(source_by_id) - set(plan.source_ids)),
        "input_count": len(inventory),
        "input_sha256": sha256_canonical(inventory),
    }
    return sorted(selected, key=lambda row: (str(row.get("source_id")), str(row.get("record_id")))), selection


def tokens(value: str, plan: EntityGraphPlan) -> list[str]:
    """Tokenize text with the closed portable contract."""

    minimum = int(plan.raw["tokenization"]["min_token_length"])
    return [token for token in TOKEN_RE.findall(value.casefold()) if len(token) >= minimum]


def content_tokens(value: str, plan: EntityGraphPlan) -> list[str]:
    """Tokenize text and remove closed English stopwords."""

    return [token for token in tokens(value, plan) if token not in STOPWORDS and not token.isdigit()]


def _counter_object(items: Iterable[str]) -> dict[str, int]:
    return {key: value for key, value in sorted(Counter(items).items())}


def _stable_id(prefix: str, *parts: Any) -> str:
    return f"{prefix}-{sha256_canonical(list(parts))[:24]}"


def _record_identity(record: Mapping[str, Any]) -> dict[str, str]:
    identity = {
        "source_id": record.get("source_id"),
        "record_id": record.get("record_id"),
        "record_sha256": record.get("record_sha256"),
        "concept_id": record.get("concept_id"),
        "concept_path": record.get("concept_path"),
        "subject_iri": record.get("subject_iri"),
    }
    if any(not isinstance(value, str) or not value for value in identity.values()):
        raise EntityGraphError(f"record {record.get('source_id')}/{record.get('record_id')} lacks entity identity")
    if not HEX_64.fullmatch(identity["record_sha256"]):
        raise EntityGraphError("record identity contains an invalid digest")
    safe_relative(identity["concept_path"], "concept_path")
    return identity  # type: ignore[return-value]


def _aliases(*values: Any) -> list[str]:
    result: dict[str, str] = {}
    for value in values:
        if not isinstance(value, str) or not value.strip():
            continue
        clean = " ".join(value.split())
        result.setdefault(clean.casefold(), clean)
    return [result[key] for key in sorted(result)]


def _paper_records(records: Sequence[dict[str, Any]], plan: EntityGraphPlan) -> list[dict[str, Any]]:
    result = [record for record in records if record.get("source_id") in set(plan.paper_source_ids)]
    by_source = Counter(str(record.get("source_id")) for record in result)
    if any(by_source[source_id] != 1 for source_id in plan.paper_source_ids):
        raise EntityGraphError("each selected paper source must produce exactly one record")
    return result


def derive_sections(
    records: Sequence[dict[str, Any]], plan: EntityGraphPlan, paper_entities: Mapping[str, str]
) -> list[dict[str, Any]]:
    """Derive exact PDF-page sections from authoritative paper record bodies."""

    result: list[dict[str, Any]] = []
    minimum = int(plan.raw["sectioning"]["minimum_characters"])
    for record in _paper_records(records, plan):
        body = record.get("body")
        attributes = record.get("attributes")
        if not isinstance(body, str) or not isinstance(attributes, dict):
            raise EntityGraphError("paper record body and attributes must be present")
        matches = list(PAGE_RE.finditer(body))
        if not matches:
            raise EntityGraphError(f"paper record {record.get('record_id')} has no PDF page headings")
        paper_id = attributes.get("paper_id")
        subject_iri = record.get("subject_iri")
        if not isinstance(paper_id, str) or not paper_id or subject_iri not in paper_entities:
            raise EntityGraphError("paper record has no bound paper entity")
        seen_pages: set[int] = set()
        for index, match in enumerate(matches):
            page = int(match.group("page"))
            if page in seen_pages:
                raise EntityGraphError(f"paper {paper_id} repeats PDF page {page}")
            seen_pages.add(page)
            start = match.start()
            end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
            while end > start and body[end - 1].isspace():
                end -= 1
            text = body[start:end]
            if len(text) < minimum:
                continue
            fragment = f"PDF-page-{page}"
            section_id = _stable_id("section", record["source_id"], record["record_id"], start, end, fragment)
            section_terms = content_tokens(text, plan)
            result.append(
                {
                    "section_id": section_id,
                    "paper_entity_id": paper_entities[str(subject_iri)],
                    "paper_id": paper_id,
                    "source_id": record["source_id"],
                    "record_id": record["record_id"],
                    "record_sha256": record["record_sha256"],
                    "concept_id": record["concept_id"],
                    "concept_path": record["concept_path"],
                    "source_path": record["source_path"],
                    "ordinal": page,
                    "heading": match.group(0).strip().removeprefix("## "),
                    "locator": {"kind": "character-range", "start": start, "end": end, "fragment": fragment},
                    "text": text,
                    "text_sha256": sha256_bytes(text.encode("utf-8")),
                    "terms": _counter_object(section_terms),
                    "length": len(section_terms),
                }
            )
    result.sort(key=lambda row: (row["source_id"], row["ordinal"], row["section_id"]))
    if not result:
        raise EntityGraphError("section derivation produced no eligible sections")
    return result


def derive_reviewed_entities(
    records: Sequence[dict[str, Any]], plan: EntityGraphPlan
) -> tuple[list[dict[str, Any]], dict[str, str]]:
    """Project reviewed terms, papers, and claims as graph entities."""

    entities: list[dict[str, Any]] = []
    by_iri: dict[str, str] = {}
    for record in records:
        source_id = record.get("source_id")
        attributes = record.get("attributes")
        if not isinstance(attributes, dict):
            raise EntityGraphError("selected record attributes must be an object")
        entity_type: str
        label: Any
        aliases: list[str]
        if source_id == plan.vocabulary_source_id:
            kind = attributes.get("term_kind")
            if kind == "paper-specific-method":
                entity_type = "method"
            elif kind == "analysis-dimension":
                entity_type = "dimension"
            else:
                raise EntityGraphError(f"unsupported analysis term kind: {kind!r}")
            label = attributes.get("label") or record.get("title")
            aliases = _aliases(label)
        elif source_id in set(plan.paper_source_ids):
            entity_type = "paper"
            label = attributes.get("title") or record.get("title")
            aliases = _aliases(label, attributes.get("paper_id"), attributes.get("arxiv_id"))
        elif source_id in set(plan.claim_source_ids):
            if attributes.get("review_state") != "reviewed":
                raise EntityGraphError(f"claim {record.get('record_id')} is not reviewed")
            entity_type = "claim"
            label = attributes.get("interpretation") or record.get("title")
            aliases = _aliases(record.get("record_id"))
        else:
            continue
        if not isinstance(label, str) or not label.strip() or not aliases:
            raise EntityGraphError("reviewed entity must have a label and alias")
        identity = _record_identity(record)
        entity_id = _stable_id("entity", entity_type, identity["subject_iri"])
        if identity["subject_iri"] in by_iri:
            raise EntityGraphError(f"duplicate reviewed entity IRI: {identity['subject_iri']}")
        by_iri[identity["subject_iri"]] = entity_id
        entities.append(
            {
                "entity_id": entity_id,
                "entity_type": entity_type,
                "canonical_label": " ".join(label.split()),
                "aliases": aliases,
                "review_state": "reviewed",
                "authoritative_identity": identity,
                "extraction": None,
            }
        )
    entities.sort(key=lambda row: row["entity_id"])
    return entities, by_iri


def _candidate_statistics(
    sections: Sequence[dict[str, Any]], plan: EntityGraphPlan, excluded_aliases: set[tuple[str, ...]]
) -> list[tuple[str, int, int, float]]:
    extraction = plan.raw["extraction"]
    low, high = extraction["ngram_range"]
    section_counts: dict[str, Counter[str]] = {}
    total = Counter()
    document_frequency = Counter()
    for section in sections:
        raw_tokens = tokens(section["text"], plan)
        counts: Counter[str] = Counter()
        for size in range(low, high + 1):
            for start in range(0, len(raw_tokens) - size + 1):
                phrase_tokens = tuple(raw_tokens[start : start + size])
                if phrase_tokens in excluded_aliases:
                    continue
                if any(token in STOPWORDS or token.isdigit() for token in phrase_tokens):
                    continue
                phrase = " ".join(phrase_tokens)
                counts[phrase] += 1
        section_counts[section["section_id"]] = counts
        total.update(counts)
        document_frequency.update(counts.keys())
    count = len(sections)
    minimum_df = int(extraction["minimum_section_frequency"])
    maximum_fraction = float(extraction["maximum_section_fraction"])
    scores: dict[str, float] = {}
    for phrase, frequency in total.items():
        df = document_frequency[phrase]
        if df < minimum_df or df / count > maximum_fraction:
            continue
        phrase_length = len(phrase.split())
        idf = math.log(1.0 + (count - df + 0.5) / (df + 0.5))
        scores[phrase] = frequency * idf * (1.0 + 0.35 * (phrase_length - 1))
    locally_selected: set[str] = set()
    top_per_section = int(extraction["top_candidates_per_section"])
    for counts in section_counts.values():
        ranked = sorted(
            (phrase for phrase in counts if phrase in scores),
            key=lambda phrase: (-counts[phrase] * scores[phrase], -len(phrase.split()), phrase),
        )
        locally_selected.update(ranked[:top_per_section])
    ranked_global = sorted(
        locally_selected,
        key=lambda phrase: (-scores[phrase], -document_frequency[phrase], -len(phrase.split()), phrase),
    )[: int(extraction["maximum_candidates"])]
    return [
        (phrase, document_frequency[phrase], total[phrase], round(scores[phrase], 8))
        for phrase in ranked_global
    ]


def derive_candidate_entities(
    sections: Sequence[dict[str, Any]], reviewed: Sequence[dict[str, Any]], plan: EntityGraphPlan
) -> list[dict[str, Any]]:
    """Extract deterministic candidate entity phrases from paper sections."""

    excluded: set[tuple[str, ...]] = set()
    for entity in reviewed:
        for alias in entity["aliases"]:
            alias_tokens = tuple(tokens(alias, plan))
            if alias_tokens:
                excluded.add(alias_tokens)
    result = []
    for phrase, section_frequency, total_occurrences, score in _candidate_statistics(sections, plan, excluded):
        result.append(
            {
                "entity_id": _stable_id("entity-candidate", phrase),
                "entity_type": "candidate-phrase",
                "canonical_label": phrase,
                "aliases": [phrase],
                "review_state": "candidate",
                "authoritative_identity": None,
                "extraction": {
                    "algorithm": ALGORITHMS["entity_extraction"],
                    "section_frequency": section_frequency,
                    "total_occurrences": total_occurrences,
                    "score": score,
                },
            }
        )
    return sorted(result, key=lambda row: row["entity_id"])


def derive_mentions(
    sections: Sequence[dict[str, Any]], entities: Sequence[dict[str, Any]], plan: EntityGraphPlan
) -> list[dict[str, Any]]:
    """Bind normalized entity aliases to exact source sections."""

    alias_map: dict[tuple[str, ...], list[tuple[str, str]]] = defaultdict(list)
    for entity in entities:
        if entity["entity_type"] == "claim":
            continue
        for alias in entity["aliases"]:
            alias_tokens = tuple(tokens(alias, plan))
            if alias_tokens:
                alias_map[alias_tokens].append((entity["entity_id"], alias))
    lengths = sorted({len(alias) for alias in alias_map})
    result: list[dict[str, Any]] = []
    for section in sections:
        section_tokens = tokens(section["text"], plan)
        matches: dict[str, Counter[str]] = defaultdict(Counter)
        for size in lengths:
            for start in range(0, len(section_tokens) - size + 1):
                phrase = tuple(section_tokens[start : start + size])
                for entity_id, alias in alias_map.get(phrase, []):
                    matches[entity_id][alias] += 1
        for entity_id, aliases in sorted(matches.items()):
            count = sum(aliases.values())
            result.append(
                {
                    "mention_id": _stable_id("mention", entity_id, section["section_id"]),
                    "entity_id": entity_id,
                    "section_id": section["section_id"],
                    "count": count,
                    "matched_aliases": sorted(aliases),
                    "review_state": "candidate",
                    "semantic_source": ALGORITHMS["mention_matching"],
                }
            )
    return sorted(result, key=lambda row: (row["section_id"], row["entity_id"]))


def _edge(
    source: str,
    predicate: str,
    target: str,
    review_state: str,
    semantic_source: str,
    evidence: Sequence[str],
    *,
    claim_record_id: str | None = None,
    weight: float = 1.0,
) -> dict[str, Any]:
    if predicate not in PREDICATES:
        raise EntityGraphError(f"unsupported graph predicate: {predicate}")
    evidence_ids = sorted(set(evidence))
    return {
        "edge_id": _stable_id("edge", source, predicate, target, claim_record_id, evidence_ids),
        "source_node": source,
        "predicate": predicate,
        "target_node": target,
        "review_state": review_state,
        "semantic_source": semantic_source,
        "claim_record_id": claim_record_id,
        "evidence_section_ids": evidence_ids,
        "weight": round(float(weight), 8),
    }


def derive_edges(
    records: Sequence[dict[str, Any]],
    sections: Sequence[dict[str, Any]],
    entities: Sequence[dict[str, Any]],
    iri_entities: Mapping[str, str],
    mentions: Sequence[dict[str, Any]],
    plan: EntityGraphPlan,
) -> list[dict[str, Any]]:
    """Derive reviewed claim paths, exact provenance edges, and candidate co-mentions."""

    result: list[dict[str, Any]] = []
    entity_by_id = {entity["entity_id"]: entity for entity in entities}
    section_by_path_fragment = {
        (section["source_path"], section["locator"]["fragment"]): section["section_id"] for section in sections
    }
    section_by_id = {section["section_id"]: section for section in sections}
    for section in sections:
        result.append(
            _edge(
                section["section_id"],
                "partOfPaper",
                section["paper_entity_id"],
                "reviewed",
                ALGORITHMS["reviewed_relations"],
                [section["section_id"]],
            )
        )
    for mention in mentions:
        result.append(
            _edge(
                mention["entity_id"],
                "mentionedInSection",
                mention["section_id"],
                "candidate",
                ALGORITHMS["mention_matching"],
                [mention["section_id"]],
                weight=1.0 + math.log1p(mention["count"]),
            )
        )
    claim_ids = set(plan.claim_source_ids)
    claim_entity_by_record: dict[str, str] = {}
    for entity in entities:
        identity = entity["authoritative_identity"]
        if entity["entity_type"] == "claim" and identity is not None:
            claim_entity_by_record[identity["record_id"]] = entity["entity_id"]
    for record in records:
        if record.get("source_id") not in claim_ids:
            continue
        attributes = record.get("attributes")
        if not isinstance(attributes, dict) or attributes.get("review_state") != "reviewed":
            raise EntityGraphError(f"claim {record.get('record_id')} is not reviewed")
        claim_record_id = str(record.get("record_id"))
        claim_entity = claim_entity_by_record.get(claim_record_id)
        subject = iri_entities.get(str(attributes.get("subject_term_iri")))
        object_entity = iri_entities.get(str(attributes.get("object_term_iri")))
        paper = iri_entities.get(str(attributes.get("paper_iri")))
        locator = attributes.get("evidence_locator")
        if not isinstance(locator, str) or "#" not in locator:
            raise EntityGraphError(f"claim {claim_record_id} has no exact page evidence locator")
        evidence_sections: list[str] = []
        for item in locator.split(";"):
            if "#" not in item:
                raise EntityGraphError(f"claim {claim_record_id} contains an invalid evidence locator")
            path, fragment = item.split("#", 1)
            section = section_by_path_fragment.get((path, fragment))
            if section is None:
                raise EntityGraphError(f"claim {claim_record_id} cannot bind evidence locator {item!r}")
            evidence_sections.append(section)
        evidence_sections = sorted(set(evidence_sections))
        if not all((claim_entity, subject, object_entity, paper)) or not evidence_sections:
            raise EntityGraphError(f"claim {claim_record_id} cannot bind every graph node and evidence section")
        evidence = evidence_sections
        source = ALGORITHMS["reviewed_relations"]
        result.extend(
            [
                _edge(str(subject), "hasReviewedClaim", str(claim_entity), "reviewed", source, evidence, claim_record_id=claim_record_id),
                _edge(str(claim_entity), "objectTerm", str(object_entity), "reviewed", source, evidence, claim_record_id=claim_record_id),
                _edge(str(claim_entity), "aboutPaper", str(paper), "reviewed", source, evidence, claim_record_id=claim_record_id),
            ]
        )
        result.extend(
            _edge(
                str(claim_entity),
                "supportedBySection",
                section_id,
                "reviewed",
                source,
                [section_id],
                claim_record_id=claim_record_id,
            )
            for section_id in evidence_sections
        )

    mention_by_section: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for mention in mentions:
        mention_by_section[mention["section_id"]].append(mention)
    pair_sections: dict[tuple[str, str], list[str]] = defaultdict(list)
    max_per_section = int(plan.raw["graph"]["max_co_mentions_per_section"])
    for section_id, rows in mention_by_section.items():
        ranked = sorted(
            rows,
            key=lambda row: (
                entity_by_id[row["entity_id"]]["review_state"] != "reviewed",
                -row["count"],
                row["entity_id"],
            ),
        )[:max_per_section]
        ids = sorted(row["entity_id"] for row in ranked)
        for left_index, left in enumerate(ids):
            for right in ids[left_index + 1 :]:
                pair_sections[(left, right)].append(section_id)
    minimum = int(plan.raw["graph"]["minimum_co_mention_sections"])
    max_neighbors = int(plan.raw["graph"]["max_co_mention_neighbors"])
    max_evidence = int(plan.raw["graph"]["max_edge_evidence_sections"])
    eligible_pairs = {pair: sorted(set(values)) for pair, values in pair_sections.items() if len(set(values)) >= minimum}
    neighbor_rank: dict[str, list[tuple[int, str]]] = defaultdict(list)
    for (left, right), evidence in eligible_pairs.items():
        neighbor_rank[left].append((len(evidence), right))
        neighbor_rank[right].append((len(evidence), left))
    allowed = {
        (node, neighbor)
        for node, values in neighbor_rank.items()
        for _, neighbor in sorted(values, key=lambda item: (-item[0], item[1]))[:max_neighbors]
    }
    for (left, right), evidence in sorted(eligible_pairs.items()):
        if (left, right) not in allowed and (right, left) not in allowed:
            continue
        result.append(
            _edge(
                left,
                "coMentionedWith",
                right,
                "candidate",
                ALGORITHMS["candidate_relations"],
                evidence[:max_evidence],
                weight=math.log1p(len(evidence)),
            )
        )
    result.sort(key=lambda row: row["edge_id"])
    if len({row["edge_id"] for row in result}) != len(result):
        raise EntityGraphError("derived graph contains duplicate edge IDs")
    if any(section_id not in section_by_id for row in result for section_id in row["evidence_section_ids"]):
        raise EntityGraphError("derived graph edge cites an unknown section")
    return result


def derive_lexicon(sections: Sequence[dict[str, Any]]) -> dict[str, Any]:
    """Derive persisted section-level BM25 statistics."""

    document_count = len(sections)
    document_frequency = Counter()
    for section in sections:
        document_frequency.update(section["terms"].keys())
    terms = {
        term: {
            "document_frequency": frequency,
            "idf": round(math.log(1.0 + (document_count - frequency + 0.5) / (frequency + 0.5)), 12),
        }
        for term, frequency in sorted(document_frequency.items())
    }
    return {
        "schema_version": SCHEMA_VERSION,
        "tokenizer": TOKENIZER_ID,
        "stopwords": STOPWORDS_ID,
        "document_count": document_count,
        "average_length": round(sum(section["length"] for section in sections) / document_count, 12),
        "terms": terms,
    }


def validate_rows(
    entities: Sequence[dict[str, Any]],
    sections: Sequence[dict[str, Any]],
    mentions: Sequence[dict[str, Any]],
    edges: Sequence[dict[str, Any]],
    lexicon: Mapping[str, Any],
) -> None:
    """Validate closed row schemas and graph referential integrity."""

    entity_ids: set[str] = set()
    for number, entity in enumerate(entities, start=1):
        exact_keys(entity, ENTITY_KEYS, f"entities.jsonl:{number}")
        if entity["entity_id"] in entity_ids:
            raise EntityGraphError("entity IDs must be unique")
        entity_ids.add(entity["entity_id"])
        if entity["entity_type"] not in {"method", "dimension", "paper", "claim", "candidate-phrase"}:
            raise EntityGraphError("entity type is invalid")
        if entity["review_state"] not in {"reviewed", "candidate"}:
            raise EntityGraphError("entity review state is invalid")
        if not isinstance(entity["aliases"], list) or not entity["aliases"]:
            raise EntityGraphError("entity aliases must be nonempty")
        if entity["authoritative_identity"] is None:
            if entity["review_state"] != "candidate" or not isinstance(entity["extraction"], dict):
                raise EntityGraphError("only extracted candidates may omit authoritative identity")
            exact_keys(entity["extraction"], EXTRACTION_KEYS, "candidate extraction")
        else:
            if entity["review_state"] != "reviewed" or entity["extraction"] is not None:
                raise EntityGraphError("reviewed entities require identity and no extraction metadata")
            exact_keys(entity["authoritative_identity"], IDENTITY_KEYS, "authoritative entity identity")

    section_ids: set[str] = set()
    for number, section in enumerate(sections, start=1):
        exact_keys(section, SECTION_KEYS, f"sections.jsonl:{number}")
        exact_keys(section["locator"], LOCATOR_KEYS, f"sections.jsonl:{number}.locator")
        if section["section_id"] in section_ids:
            raise EntityGraphError("section IDs must be unique")
        section_ids.add(section["section_id"])
        if section["paper_entity_id"] not in entity_ids:
            raise EntityGraphError("section paper entity does not exist")
        if sha256_bytes(section["text"].encode("utf-8")) != section["text_sha256"]:
            raise EntityGraphError("section text digest is invalid")
        safe_relative(section["concept_path"], "section concept_path")
        safe_relative(section["source_path"], "section source_path")

    mention_ids: set[str] = set()
    for number, mention in enumerate(mentions, start=1):
        exact_keys(mention, MENTION_KEYS, f"mentions.jsonl:{number}")
        if mention["mention_id"] in mention_ids:
            raise EntityGraphError("mention IDs must be unique")
        mention_ids.add(mention["mention_id"])
        if mention["entity_id"] not in entity_ids or mention["section_id"] not in section_ids:
            raise EntityGraphError("mention refers to an unknown entity or section")
        _plain_int(mention["count"], "mention count", 1, 100000000)

    node_ids = entity_ids | section_ids
    edge_ids: set[str] = set()
    for number, edge in enumerate(edges, start=1):
        exact_keys(edge, EDGE_KEYS, f"edges.jsonl:{number}")
        if edge["edge_id"] in edge_ids:
            raise EntityGraphError("edge IDs must be unique")
        edge_ids.add(edge["edge_id"])
        if edge["source_node"] not in node_ids or edge["target_node"] not in node_ids:
            raise EntityGraphError("edge refers to an unknown graph node")
        if edge["predicate"] not in PREDICATES or edge["review_state"] not in {"reviewed", "candidate"}:
            raise EntityGraphError("edge predicate or review state is invalid")
        if any(section_id not in section_ids for section_id in edge["evidence_section_ids"]):
            raise EntityGraphError("edge evidence refers to an unknown section")
        _finite(edge["weight"], "edge weight", 0.0, 1000000000.0)

    exact_keys(lexicon, LEXICON_KEYS, "lexicon")
    if lexicon["schema_version"] != SCHEMA_VERSION or lexicon["document_count"] != len(sections):
        raise EntityGraphError("lexicon version or document count is invalid")
    if lexicon["tokenizer"] != TOKENIZER_ID or lexicon["stopwords"] != STOPWORDS_ID:
        raise EntityGraphError("lexicon tokenizer contract is invalid")


def derive_projection(root: Path, plan: EntityGraphPlan) -> dict[str, Any]:
    """Rederive the complete entity graph in memory from the authoritative core."""

    records, sources = load_core(root)
    selected, selection = select_records(records, sources, plan)
    reviewed, iri_entities = derive_reviewed_entities(selected, plan)
    paper_entities = {
        entity["authoritative_identity"]["subject_iri"]: entity["entity_id"]
        for entity in reviewed
        if entity["entity_type"] == "paper"
    }
    sections = derive_sections(selected, plan, paper_entities)
    candidates = derive_candidate_entities(sections, reviewed, plan)
    entities = sorted([*reviewed, *candidates], key=lambda row: row["entity_id"])
    mentions = derive_mentions(sections, entities, plan)
    edges = derive_edges(selected, sections, entities, iri_entities, mentions, plan)
    lexicon = derive_lexicon(sections)
    validate_rows(entities, sections, mentions, edges, lexicon)
    summary = {
        "inputs": selection["input_count"],
        "selected_records": len(selected),
        "sections": len(sections),
        "entities": len(entities),
        "reviewed_entities": sum(entity["review_state"] == "reviewed" for entity in entities),
        "candidate_entities": sum(entity["review_state"] == "candidate" for entity in entities),
        "mentions": len(mentions),
        "edges": len(edges),
        "reviewed_edges": sum(edge["review_state"] == "reviewed" for edge in edges),
        "candidate_edges": sum(edge["review_state"] == "candidate" for edge in edges),
        "lexicon_terms": len(lexicon["terms"]),
    }
    return {
        "selection": selection,
        "summary": summary,
        "entities": entities,
        "sections": sections,
        "mentions": mentions,
        "edges": edges,
        "lexicon": lexicon,
    }
