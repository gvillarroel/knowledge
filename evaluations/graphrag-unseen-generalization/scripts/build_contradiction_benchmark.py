#!/usr/bin/env python3
"""Build a sealed evaluation-only benchmark for cross-source contradiction search."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
from typing import Any, Mapping, Sequence


SCHEMA_VERSION = "graphrag-contradiction-question-extension/1.0"
POLICY_SCHEMA_VERSION = "evaluation-only-dataset-policy/1.0"
DATASET_ID = "graphrag-papers-contradiction-eval-40-v1"
QUESTION_COUNT = 40
REPO_ROOT = Path(__file__).resolve().parents[3]
ANALYSIS_ROOT = REPO_ROOT / "evaluations" / "graphrag-cross-paper" / "analysis"
MARKDOWN_ROOT = REPO_ROOT / "evaluations" / "graphrag-cross-paper" / "sources" / "markdown"
GROUP_FILES = ("group-a.json", "group-b.json", "group-c.json")
TOKEN_RE = re.compile(r"[a-z0-9]+(?:[._/-][a-z0-9]+)*", re.IGNORECASE)
OUTPUT_FILES = (
    "retrieval-questions.jsonl",
    "ground-truth.jsonl",
    "manifest.json",
    "EVALUATION_ONLY.json",
)


class ContradictionBenchmarkError(ValueError):
    """Describe invalid contradiction benchmark input or generated output."""


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
        allow_nan=False,
    ) + "\n"


def _json_line(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _tokens(text: str) -> tuple[str, ...]:
    return tuple(
        token.strip("._/-")
        for token in TOKEN_RE.findall(text.casefold())
        if token.strip("._/-")
    )


def _load_object(path: Path, *, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ContradictionBenchmarkError(f"Cannot read {label} at {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ContradictionBenchmarkError(f"{label} must be a JSON object")
    return value


def _load_papers() -> tuple[dict[str, dict[str, Any]], list[dict[str, Any]]]:
    papers: dict[str, dict[str, Any]] = {}
    inputs = []
    for name in GROUP_FILES:
        path = ANALYSIS_ROOT / name
        payload = _load_object(path, label=name)
        rows = payload.get("papers")
        if not isinstance(rows, list):
            raise ContradictionBenchmarkError(f"{name} has no papers array")
        for row in rows:
            if not isinstance(row, dict):
                raise ContradictionBenchmarkError(f"{name} contains a non-object paper")
            paper_id = row.get("paper_id")
            claims = row.get("claims")
            if (
                not isinstance(paper_id, str)
                or not paper_id
                or paper_id in papers
                or not isinstance(claims, list)
                or len(claims) < 10
            ):
                raise ContradictionBenchmarkError(f"{name} contains an invalid paper")
            papers[paper_id] = row
        inputs.append(
            {
                "path": path.relative_to(REPO_ROOT).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": _sha256_file(path),
            }
        )
    if len(papers) != 15:
        raise ContradictionBenchmarkError(f"Expected 15 papers, found {len(papers)}")
    return papers, inputs


def _side(paper_id: str, *claim_indices: int) -> dict[str, Any]:
    return {"paper_id": paper_id, "claim_indices": list(claim_indices)}


def _spec(
    slug: str,
    category: str,
    verdict: str,
    challenge: str,
    rationale: str,
    scope_dimensions: Sequence[str],
    *sides: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "slug": slug,
        "category": category,
        "verdict": verdict,
        "challenge": challenge,
        "rationale": rationale,
        "scope_dimensions": list(scope_dimensions),
        "sides": list(sides),
    }


def _question_specs() -> list[dict[str, Any]]:
    specs = [
        _spec(
            "local-versus-global-rag",
            "scope conflict",
            "scope-conditioned tension",
            (
                "One line of evidence says ordinary vector retrieval is appropriate for localized "
                "questions but fails at corpus-wide sensemaking. Another says basic RAG is comparable "
                "to or better than graph retrieval for simple facts, while graph methods become useful "
                "for complex reasoning and summarization."
            ),
            (
                "The claims agree once task breadth and reasoning depth are aligned; neither supports "
                "a universal winner across local and global questions."
            ),
            ("task breadth", "reasoning depth", "retrieval unit"),
            _side("2404.16130v2", 0, 14),
            _side("2506.05690v3", 0, 5, 6),
        ),
        _spec(
            "global-summary-versus-local-subgraph",
            "retrieval-unit conflict",
            "complementary claims",
            (
                "A precomputed thematic-summary approach reports strong global coverage, whereas a "
                "connected-subgraph approach is designed to recover compact bridge evidence for a "
                "specific graph question. Decide whether these results disagree about the best "
                "retrieval unit."
            ),
            (
                "The units solve different evidence needs: corpus-wide synthesis versus local connected "
                "support. The cited experiments do not establish a direct contradiction."
            ),
            ("question locality", "retrieval unit", "output objective"),
            _side("2404.16130v2", 7, 14),
            _side("2402.07630v3", 3, 12, 14),
        ),
        _spec(
            "summaries-versus-incremental-graphs",
            "update conflict",
            "design-conditioned tension",
            (
                "One source contrasts incremental associative-edge updates with summary indexes that "
                "must be recomputed, while another graph system claims that new nodes and edges can be "
                "added without reconstructing its existing index. Determine what is actually being "
                "contrasted and whether graph summarization as a class is refuted."
            ),
            (
                "Both sources favor incremental graph updates, but they compare different graph and "
                "summary designs. The evidence challenges a particular update architecture, not every "
                "summary-based system."
            ),
            ("index architecture", "update operation", "summary recomputation"),
            _side("2405.14831v3", 12),
            _side("2410.05779v3", 1, 12),
        ),
        _spec(
            "raw-text-necessity",
            "representation conflict",
            "representation-conditioned tension",
            (
                "A graph retriever reports that removing original text did not consistently lower answer "
                "quality, while a fact-checking retriever argues that natural-language sentences are more "
                "usable by an LLM than raw triples. Determine whether raw text is necessary and identify "
                "the unaligned evidence representations."
            ),
            (
                "The claims concern different representations and tasks. Profiled graph descriptions may "
                "replace excerpts in one generator, while sentence evidence may outperform bare triples "
                "in fact verification."
            ),
            ("task", "graph verbalization", "sentence evidence", "baseline representation"),
            _side("2410.05779v3", 5, 10),
            _side("2408.08535v1", 7, 14),
        ),
        _spec(
            "more-graph-versus-useful-graph",
            "graph-size conflict",
            "measure-conditioned tension",
            (
                "One optimization study associates extracting more nodes and edges with higher accuracy. "
                "A benchmark analysis recommends tightly connected useful graphs rather than simply "
                "larger graphs. Decide whether graph size itself is beneficial or harmful."
            ),
            (
                "The first result is a within-system correlation under an extraction change; the second "
                "warns that raw size is not a sufficient objective. Connectivity and relevance mediate "
                "the apparent conflict."
            ),
            ("graph quality", "graph size", "connectivity", "within-system intervention"),
            _side("2503.06474v2", 8),
            _side("2506.05690v3", 9, 11),
        ),
        _spec(
            "missing-evidence-versus-redundancy",
            "candidate-budget conflict",
            "operating-point tradeoff",
            (
                "A local subgraph retriever warns that too few semantic candidates miss evidence and too "
                "many add distractions. A global path retriever argues that redundant information can be "
                "a more important failure source than insufficient information. Reconcile the two claims "
                "at a fixed retrieval budget."
            ),
            (
                "Both describe different sides of the same precision-recall operating point. The relative "
                "dominant error depends on task and candidate budget."
            ),
            ("candidate budget", "recall", "redundancy", "task locality"),
            _side("2402.07630v3", 11),
            _side("2502.14902v2", 0, 4, 12),
        ),
        _spec(
            "medical-gains-versus-simple-fact-noise",
            "domain conflict",
            "scope-conditioned tension",
            (
                "A medical graph pipeline improves most tested models over standard retrieval and a "
                "general graph baseline, but a broad benchmark finds graph expansion can add noise and "
                "basic retrieval can be as good or better for simple facts. Decide whether the medical "
                "results contradict the benchmark."
            ),
            (
                "The medical evidence covers terminology, linked definitions, and holistic reasoning; "
                "the benchmark warning is conditioned on simple fact access. Domain and task complexity "
                "resolve the tension."
            ),
            ("domain", "task complexity", "evidence linkage", "baseline"),
            _side("2408.04187v2", 0, 7, 10),
            _side("2506.05690v3", 2, 5, 6),
        ),
        _spec(
            "graphrag-corrects-and-corrupts",
            "outcome conflict",
            "conditional bidirectional effect",
            (
                "One study reports that graph augmentation corrects many standalone-model errors but also "
                "turns some initially correct answers into wrong ones. Another finds graphs help most on "
                "complex tasks and can hurt simple retrieval. Determine the conditions under which both "
                "positive and negative effects are supported."
            ),
            (
                "The positive and negative outcomes coexist. Filtering, task complexity, and retrieval "
                "noise determine the direction; an average gain cannot erase the documented regressions."
            ),
            ("initial answer correctness", "task complexity", "retrieval noise", "filtering"),
            _side("2503.13804v1", 0, 1, 5, 10),
            _side("2506.05690v3", 5, 6),
        ),
        _spec(
            "dependency-versus-llm-construction",
            "construction conflict",
            "quality-cost tradeoff",
            (
                "A practical construction study presents dependency and LLM extraction as interchangeable "
                "cost-accuracy modes, with the dependency variant close on one metric but weaker on another. "
                "Assess whether this evidence supports replacing LLM construction without qualification."
            ),
            (
                "The dependency route is cheaper and competitive on selected metrics, but it remains below "
                "the LLM route on reported aggregate measures and can miss implicit relations."
            ),
            ("construction cost", "metric", "implicit relations", "domain"),
            _side("2507.03226v3", 0, 1, 6, 7, 11),
            _side("2405.14831v3", 2, 8),
        ),
        _spec(
            "all-sentences-versus-filtered-paths",
            "evidence-volume conflict",
            "selection-conditioned tension",
            (
                "A community retriever's best setting keeps all sentences from targeted communities even "
                "though sentence inclusion is non-monotonic. A path system reports that a moderate number "
                "of paths helps but additional paths add noise. Determine whether retaining all evidence "
                "is supported."
            ),
            (
                "All sentences is beneficial only after a targeted community gate; it is not equivalent "
                "to retaining all communities or arbitrary paths. Both sources support bounded selection."
            ),
            ("first-stage gate", "evidence unit", "candidate count", "noise"),
            _side("2408.08535v1", 5, 10, 11),
            _side("2503.13804v1", 2, 5),
        ),
        _spec(
            "sentences-versus-path-structure",
            "prompt-organization conflict",
            "complementary claims",
            (
                "One paper argues that sentences are more usable by generators than raw triples. Another "
                "shows that ordered relation-preserving paths outperform flattened graph elements. Decide "
                "whether natural-language evidence and explicit relational organization are competing "
                "requirements."
            ),
            (
                "The requirements are compatible: path structure can be verbalized as ordered text. The "
                "comparison baselines differ and do not force a choice between language and relations."
            ),
            ("surface form", "relational order", "comparison baseline"),
            _side("2408.08535v1", 7, 14),
            _side("2502.14902v2", 1, 5, 10),
        ),
        _spec(
            "ppr-versus-connected-pcst",
            "graph-search conflict",
            "task-conditioned alternatives",
            (
                "An associative retriever reports that personalized propagation outperforms query nodes "
                "and immediate neighbors, while another retriever optimizes a connected prize-cost "
                "subgraph. Determine whether one graph-search result invalidates the other."
            ),
            (
                "The methods optimize different outputs: ranked passages through global propagation versus "
                "a compact connected evidence subgraph. Their experiments are not aligned enough for a "
                "direct contradiction."
            ),
            ("output unit", "graph objective", "reader input", "dataset"),
            _side("2405.14831v3", 3, 4, 7, 10),
            _side("2402.07630v3", 3, 12),
        ),
        _spec(
            "static-versus-agentic-retrieval",
            "adaptivity conflict",
            "capability-cost tradeoff",
            (
                "A connected-subgraph retriever is explicitly static, while an agentic reader reflects "
                "during traversal and a pattern-aware system chooses specialized graph algorithms. Assess "
                "whether adaptivity is demonstrated to be universally superior."
            ),
            (
                "Adaptive policies offer broader behavior but add planning cost and failure modes. The "
                "static method remains evaluated for a different graph-QA contract."
            ),
            ("adaptivity", "planning cost", "task pattern", "graph availability"),
            _side("2402.07630v3", 13, 14),
            _side("2406.14550v2", 2, 4, 13),
            _side("2504.02112v2", 1, 6, 12),
        ),
        _spec(
            "llm-judge-versus-grounded-reject",
            "evaluation conflict",
            "evidence-incommensurable",
            (
                "Global-answer studies rely heavily on LLM judges because straightforward gold answers "
                "are unavailable, whereas another evaluation anonymizes entities and requires abstention "
                "when retrieval cannot support an answer. Determine which conclusions can be compared and "
                "which cannot."
            ),
            (
                "Preference dimensions and retrieval-grounded reject accuracy measure different properties. "
                "Neither can be substituted for the other without a shared task and scoring contract."
            ),
            ("evaluation mode", "ground truth", "parametric knowledge", "abstention"),
            _side("2404.16130v2", 8, 9, 13),
            _side("2502.14902v2", 13),
            _side("2508.19855v3", 7, 8, 10),
        ),
        _spec(
            "graph-only-versus-hybrid-reasoning",
            "solver conflict",
            "accuracy-latency tradeoff",
            (
                "Graph-only logical reasoning is reported faster but less accurate when extracted facts are "
                "incomplete. A second pipeline finds fuzzy retrieval broader and more accurate, while logic "
                "forms are shorter and clearer to experts. Reconcile the proposed solver policies."
            ),
            (
                "Both sources support hybrid or fallback policies: symbolic structure improves density and "
                "clarity, while text or fuzzy retrieval compensates for graph incompleteness."
            ),
            ("latency", "graph completeness", "context density", "accuracy"),
            _side("2409.13731v3", 5, 10),
            _side("2503.06474v2", 5, 6, 11, 15),
        ),
        _spec(
            "fixed-versus-pattern-specific-traversal",
            "traversal conflict",
            "conditional specialization",
            (
                "One benchmark claims fixed graph traversals specialize in narrow question patterns, while "
                "a vertically unified agent selects entity, triple, community, and depth-first routes after "
                "schema-guided decomposition. Determine whether the evidence establishes that per-query "
                "routing is always worth its cost."
            ),
            (
                "The sources motivate routing for diverse complex questions, but they do not compare against "
                "every fixed method under a shared latency and quality contract."
            ),
            ("question pattern", "routing cost", "schema", "comparison coverage"),
            _side("2504.02112v2", 0, 1, 6, 12),
            _side("2508.19855v3", 1, 5, 12),
        ),
        _spec(
            "schemaless-versus-schema-constrained",
            "knowledge-model conflict",
            "domain-conditioned alternatives",
            (
                "A long-term memory system uses a schemaless OpenIE graph, while professional-domain and "
                "unified-agent systems emphasize schema-constrained extraction and schema-valid query "
                "decomposition. Decide whether the schema requirements are contradictory."
            ),
            (
                "Schemaless coverage and schema rigor target different domain constraints. Professional "
                "settings may justify labor and control that open-domain retrieval avoids."
            ),
            ("domain rigor", "schema labor", "coverage", "query execution"),
            _side("2405.14831v3", 1, 13),
            _side("2409.13731v3", 2, 4, 13),
            _side("2508.19855v3", 1, 2, 13),
        ),
        _spec(
            "general-communities-versus-medical-tags",
            "hierarchy conflict",
            "domain-specific refinement",
            (
                "A general system organizes entity graphs with hierarchical communities, whereas a medical "
                "system explicitly replaces general community detection with hierarchical medical tags. "
                "Determine whether this is evidence against community organization or a domain-specific "
                "change in routing semantics."
            ),
            (
                "The medical method changes the hierarchy to preserve domain terminology and source-definition "
                "paths. It is a scoped design alternative, not a shared ablation proving communities inferior."
            ),
            ("domain ontology", "hierarchy semantics", "ablation scope"),
            _side("2404.16130v2", 5, 7),
            _side("2408.04187v2", 1, 4, 5),
        ),
        _spec(
            "extraction-volume-versus-extraction-quality",
            "construction signal conflict",
            "quality-mediated tension",
            (
                "One pipeline associates extracting more nodes and edges with higher accuracy, while another "
                "shows that a weaker OpenIE extractor produces large retrieval drops and a dependency system "
                "warns that surface syntax misses implicit relations. Assess whether extraction quantity is "
                "a sufficient optimization target."
            ),
            (
                "Quantity is not sufficient. Coverage, relation correctness, and implicit semantics mediate "
                "the reported correlation."
            ),
            ("quantity", "relation quality", "implicit semantics", "retrieval accuracy"),
            _side("2503.06474v2", 8),
            _side("2405.14831v3", 8),
            _side("2507.03226v3", 2, 11),
        ),
        _spec(
            "quality-versus-token-cost",
            "efficiency conflict",
            "evidence-incommensurable",
            (
                "Several systems claim lower token cost without large quality loss: path pruning relative to "
                "a dual-level graph retriever, a unified agent relative to its baselines, and pattern-specific "
                "traversal relative to general LLM control. Determine whether the largest percentage establishes "
                "the fastest or most efficient method overall."
            ),
            (
                "The denominators, systems, tasks, models, and quality metrics differ. Relative savings cannot "
                "be ranked as absolute efficiency without a shared runtime contract."
            ),
            ("baseline", "token denominator", "quality metric", "runtime"),
            _side("2502.14902v2", 12),
            _side("2508.19855v3", 11),
            _side("2504.02112v2", 1, 12),
        ),
        _spec(
            "three-retrieval-units",
            "retrieval-unit triangulation",
            "complementary claims",
            (
                "Compare a compact connected subgraph, graph-mediated passage ranking, and precomputed "
                "community summaries. Each source presents its unit as effective. Determine whether any "
                "pair makes mutually exclusive claims once the question type and generator input are aligned."
            ),
            (
                "The units target local graph QA, multi-hop passage recovery, and global summarization. The "
                "evidence supports routing by task rather than one universal retrieval unit."
            ),
            ("task", "retrieval unit", "generator input", "scope"),
            _side("2402.07630v3", 3, 14),
            _side("2405.14831v3", 4, 14),
            _side("2404.16130v2", 7, 14),
        ),
        _spec(
            "text-removal-sentence-and-path-evidence",
            "evidence-form triangulation",
            "representation-conditioned tension",
            (
                "Triangulate three findings: original text can sometimes be removed without consistent loss, "
                "sentences can be more usable than triples, and ordered paths can beat flattened graph elements. "
                "State the narrow conclusion about evidence form that survives all three."
            ),
            (
                "Useful evidence need not be raw source text, but it must preserve task-relevant semantics in "
                "a generator-usable form. The three baselines are different and do not yield one universal format."
            ),
            ("raw text", "verbalization", "relational order", "task"),
            _side("2410.05779v3", 10),
            _side("2408.08535v1", 7),
            _side("2502.14902v2", 5, 10),
        ),
        _spec(
            "planning-benefit-and-planning-failure",
            "planning triangulation",
            "capability-risk tradeoff",
            (
                "Planning improves graph exploration and structured query execution in several studies, yet "
                "planning quality, decomposition errors, and failure without self-correction are prominent "
                "limitations. Decide whether planning is supported as a benefit, a risk, or both."
            ),
            (
                "Planning is both a capability and a failure surface. Gains depend on valid decomposition, "
                "repair, and stopping policies; average improvements do not eliminate planning regressions."
            ),
            ("decomposition correctness", "repair", "planning cost", "task nesting"),
            _side("2406.14550v2", 2, 9, 13),
            _side("2409.13731v3", 5, 11, 13),
            _side("2504.02112v2", 5, 7, 11),
        ),
        _spec(
            "simple-complex-and-dual-level-routing",
            "task-complexity triangulation",
            "scope-conditioned convergence",
            (
                "A benchmark favors basic retrieval for simple facts and graphs for complex tasks. A dual-level "
                "system separately routes entity detail and relation themes, while a global summarizer focuses "
                "on corpus-wide questions. Determine whether these results converge on a workload policy."
            ),
            (
                "The evidence converges on task-aware routing: lexical or entity retrieval for local facts and "
                "broader graph organization for interconnected or global questions."
            ),
            ("task complexity", "query locality", "retrieval level"),
            _side("2506.05690v3", 5, 6),
            _side("2410.05779v3", 3, 6, 9),
            _side("2404.16130v2", 0, 14),
        ),
        _spec(
            "construction-cost-quality-and-rigor",
            "construction triangulation",
            "multi-objective tradeoff",
            (
                "Dependency extraction reduces construction cost but can miss implicit relations; stronger "
                "OpenIE improves retrieval but is expensive; schema-constrained professional construction "
                "improves rigor at greater labor and runtime cost. Determine whether one construction policy "
                "dominates."
            ),
            (
                "No policy dominates on the cited evidence. Cost, coverage, relation quality, and domain rigor "
                "form a multi-objective frontier."
            ),
            ("cost", "coverage", "relation quality", "schema labor"),
            _side("2507.03226v3", 0, 1, 11),
            _side("2405.14831v3", 2, 8),
            _side("2409.13731v3", 4, 12, 13),
        ),
        _spec(
            "domain-transfer-limitations",
            "generalization triangulation",
            "convergent limitation",
            (
                "Three papers report strong results but separately limit transfer because of domain-specific "
                "entity extraction, a single specialized dataset and model, or missing public-benchmark and "
                "cross-domain tests. Determine whether any source supports broad generalization."
            ),
            (
                "The limitations converge: none of the cited results alone supports broad cross-domain "
                "generalization."
            ),
            ("domain", "model", "benchmark", "extraction pipeline"),
            _side("2408.08535v1", 13),
            _side("2503.06474v2", 13),
            _side("2507.03226v3", 12),
        ),
        _spec(
            "evidence-validity-versus-deployment-safety",
            "safety triangulation",
            "evidence-level mismatch",
            (
                "A graph QA system reports manually valid supporting subgraphs, a medical system reports "
                "benchmark and limited human gains, and an anonymized reject benchmark measures retrieval-grounded "
                "abstention. Determine whether any of these establishes deployment safety."
            ),
            (
                "All are useful evidence-integrity signals, but none directly measures deployment outcomes. "
                "Their validity, human-rating, and reject-mode contracts must remain separate."
            ),
            ("evidence validity", "human evaluation", "abstention", "deployment outcome"),
            _side("2402.07630v3", 9),
            _side("2408.04187v2", 8, 14),
            _side("2508.19855v3", 7, 8, 10),
        ),
        _spec(
            "benchmark-contamination-and-anonymization",
            "evaluation-validity triangulation",
            "complementary controls",
            (
                "One paper warns that pretraining overlap can mimic retrieval strength, another anonymizes "
                "entities and requires abstention, and a third generates persona-conditioned global questions "
                "without simple gold answers. Compare which validity threat each evaluation addresses."
            ),
            (
                "The controls address different threats: memorization, unsupported answering, and global-question "
                "coverage. They are complementary rather than contradictory."
            ),
            ("pretraining overlap", "entity memorization", "abstention", "question generation"),
            _side("2503.06474v2", 1),
            _side("2508.19855v3", 7, 8),
            _side("2404.16130v2", 8, 9),
        ),
        _spec(
            "density-volume-and-pruning",
            "graph-budget triangulation",
            "quality-mediated tradeoff",
            (
                "Dense graphs correlate with high recall in one benchmark, extracting more graph elements "
                "correlates with accuracy in one pipeline, and path retrieval improves by pruning low-contribution "
                "regions. Determine whether density, volume, and pruning are empirically inconsistent."
            ),
            (
                "They measure different stages. A sufficiently connected index may aid recall while query-time "
                "pruning removes irrelevant evidence; useful density does not imply an unbounded prompt."
            ),
            ("index density", "extraction coverage", "query-time pruning", "prompt budget"),
            _side("2506.05690v3", 9, 11),
            _side("2503.06474v2", 8),
            _side("2502.14902v2", 0, 3, 4),
        ),
        _spec(
            "comprehensiveness-directness-and-cost",
            "quality-dimension triangulation",
            "metric-conditioned tradeoff",
            (
                "A pattern-aware system is often comprehensive but not always direct or cheap. A global summarizer "
                "improves comprehensiveness and diversity with only small gains over raw map-reduce in some settings, "
                "and a benchmark finds recall or faithfulness can rise while context relevance falls. Determine "
                "whether a single quality score can resolve these claims."
            ),
            (
                "The dimensions conflict and must remain separate. No single average identifies a universal winner "
                "without declared weights and cost limits."
            ),
            ("comprehensiveness", "directness", "diversity", "context relevance", "cost"),
            _side("2504.02112v2", 12),
            _side("2404.16130v2", 10, 11),
            _side("2506.05690v3", 7),
        ),
        _spec(
            "exact-match-versus-semantic-matching",
            "matching-policy triangulation",
            "stage-conditioned tension",
            (
                "One evaluated graph builder reconciles entities by exact string match, while another retrieval "
                "study reports exact query matching degrades accuracy and a practical system combines noun phrases "
                "with semantic vector search. Determine whether exact matching is supported or contradicted."
            ),
            (
                "Exact matching is used at entity reconciliation in one pipeline, while the negative result concerns "
                "query retrieval keys. Matching policy must be aligned by stage before comparison."
            ),
            ("construction stage", "query stage", "entity identity", "semantic recall"),
            _side("2404.16130v2", 4),
            _side("2503.06474v2", 4, 10),
            _side("2507.03226v3", 3, 4),
        ),
        _spec(
            "connected-subgraphs-paths-and-communities",
            "structural-unit triangulation",
            "complementary claims",
            (
                "A prize-cost method retrieves a connected subgraph, a pruning method preserves ordered paths, "
                "and a fact-checker routes through communities before selecting sentences. Identify the claimed "
                "benefit of each structure and decide whether their results are mutually exclusive."
            ),
            (
                "Connectivity, path order, and community routing address different structural requirements. The "
                "evidence is complementary and task-conditioned."
            ),
            ("connectivity", "path order", "community routing", "task"),
            _side("2402.07630v3", 3, 12),
            _side("2502.14902v2", 2, 5, 10),
            _side("2408.08535v1", 5, 14),
        ),
        _spec(
            "full-context-active-selection-and-overhead",
            "context-management triangulation",
            "convergent constraint",
            (
                "An active reader beats a long-context baseline with a small working context, a retrieval pipeline "
                "loses accuracy when maximum context doubles, and a benchmark documents substantial prompt expansion "
                "overhead. Determine the strongest common conclusion and its limits."
            ),
            (
                "All three support selective context management, but they do not establish one optimal context size "
                "across models, tasks, and retrieval architectures."
            ),
            ("context size", "selection", "token overhead", "model"),
            _side("2406.14550v2", 7, 10, 12),
            _side("2503.06474v2", 9),
            _side("2506.05690v3", 10, 11),
        ),
        _spec(
            "internal-and-external-answer-fusion",
            "knowledge-source triangulation",
            "confidence-conditioned policy",
            (
                "One system independently thresholds graph-derived and standalone-model answers before integration, "
                "another separates open evaluation from retrieval-grounded reject evaluation, and a medical system "
                "requires verifiable external evidence. Determine when parametric knowledge may legitimately "
                "contribute to the answer."
            ),
            (
                "Parametric knowledge may contribute under an open or explicitly fused contract, but it must not be "
                "mistaken for retrieved support in reject or evidence-required settings."
            ),
            ("evaluation contract", "confidence", "retrieved support", "parametric knowledge"),
            _side("2503.13804v1", 0, 7),
            _side("2508.19855v3", 7, 10),
            _side("2408.04187v2", 0, 14),
        ),
        _spec(
            "global-graph-method-rankings",
            "cross-benchmark result conflict",
            "evidence-incommensurable",
            (
                "A global summarization system beats vector search on coverage dimensions, a dual-level system "
                "generally beats that summarizer on several larger corpora, and a path system reports majority wins "
                "over both graph and non-graph baselines. Determine whether these papers define a transitive ranking."
            ),
            (
                "They do not. Corpora, questions, models, baselines, metrics, and judge protocols differ, so pairwise "
                "wins cannot be composed into a transitive universal leaderboard."
            ),
            ("corpus", "question set", "model", "metric", "judge"),
            _side("2404.16130v2", 9, 10),
            _side("2410.05779v3", 7, 8, 13),
            _side("2502.14902v2", 8, 13),
        ),
        _spec(
            "local-global-medical-and-professional-reasoning",
            "four-source scope audit",
            "scope-conditioned alternatives",
            (
                "Audit four claims about when graphs help: global sensemaking, compact local graph QA, medically "
                "linked terminology and evidence, and professional numerical or rule-based reasoning. Determine "
                "whether the sources contradict one another or define distinct applicability regions."
            ),
            (
                "They define distinct applicability regions. A correct synthesis retains local/global, domain, "
                "reasoning, and evidence requirements instead of declaring one method universally best."
            ),
            ("locality", "domain", "reasoning type", "evidence contract"),
            _side("2404.16130v2", 0, 14),
            _side("2402.07630v3", 0, 14),
            _side("2408.04187v2", 0, 14),
            _side("2409.13731v3", 0, 7),
        ),
        _spec(
            "four-way-noise-control",
            "four-source noise audit",
            "convergent tradeoff",
            (
                "Compare four noise-control findings: longer chunks can hide early information, too many initial "
                "graph candidates distract, sentence inclusion is non-monotonic, and extra retrieved paths eventually "
                "reduce performance. Determine whether they disagree about adding more context."
            ),
            (
                "They converge on bounded evidence selection. The optimal control differs by chunking, candidate "
                "seeding, community filtering, and path filtering."
            ),
            ("chunk size", "candidate count", "sentence count", "path count"),
            _side("2404.16130v2", 3),
            _side("2402.07630v3", 11),
            _side("2408.08535v1", 10),
            _side("2503.13804v1", 2),
        ),
        _spec(
            "four-way-generalization-audit",
            "four-source generalization audit",
            "convergent limitation",
            (
                "Four strong-result papers separately limit conclusions to tested corpora, one medical benchmark "
                "and limited human review, one specialized dataset and model, or missing cross-domain public tests. "
                "Determine the maximum defensible generalization claim."
            ),
            (
                "The maximum claim is within-study effectiveness under each reported setup. Broad domain, model, "
                "deployment, or corpus transfer remains unestablished."
            ),
            ("corpus", "domain", "model", "deployment"),
            _side("2404.16130v2", 13),
            _side("2408.04187v2", 13, 14),
            _side("2503.06474v2", 13),
            _side("2507.03226v3", 12),
        ),
        _spec(
            "four-way-reasoning-control",
            "four-source reasoning audit",
            "capability-risk tradeoff",
            (
                "Four systems use different reasoning controls: rational plans with reflection, executable logical "
                "forms with hybrid fallback, automatic Cypher repair, and schema-guided iterative agents. Compare "
                "their evidence for reasoning reliability and identify the shared failure boundary."
            ),
            (
                "Structured control improves complex retrieval, but decomposition, extraction, schema, repair, and "
                "planning errors remain shared failure boundaries. The reported gains are not a proof of guaranteed "
                "reasoning correctness."
            ),
            ("decomposition", "verification", "repair", "schema", "planning"),
            _side("2406.14550v2", 2, 4, 13),
            _side("2503.06474v2", 5, 6, 14),
            _side("2504.02112v2", 5, 7, 11),
            _side("2508.19855v3", 1, 5, 6),
        ),
        _spec(
            "four-way-quality-latency-audit",
            "four-source efficiency audit",
            "evidence-incommensurable",
            (
                "Four papers report efficiency using different quantities: prompt tokens and training time, update "
                "recomputation, relative token use against a graph baseline, and lower token cost with higher accuracy. "
                "Determine whether the claims support an overall efficiency ranking."
            ),
            (
                "No overall ranking is valid because build, update, retrieval, training, and generation costs have "
                "different denominators and runtime boundaries."
            ),
            ("build cost", "update cost", "retrieval tokens", "training time", "generation quality"),
            _side("2402.07630v3", 8),
            _side("2405.14831v3", 12),
            _side("2502.14902v2", 12),
            _side("2508.19855v3", 11),
        ),
    ]
    if len(specs) != QUESTION_COUNT:
        raise ContradictionBenchmarkError(
            f"Internal contradiction plan has {len(specs)} questions, expected {QUESTION_COUNT}"
        )
    return specs


def _source_ids(paper_ids: Sequence[str]) -> list[str]:
    result = []
    for paper_id in paper_ids:
        slug = paper_id.replace(".", "-")
        result.extend((f"claims-{slug}", f"paper-{slug}"))
    return sorted(result)


def _validate_pages(paper_id: str, pages: Sequence[int]) -> str:
    path = MARKDOWN_ROOT / f"{paper_id}.md"
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise ContradictionBenchmarkError(f"Cannot read paper Markdown {path}: {exc}") from exc
    for page in pages:
        if f"## PDF page {page}" not in text:
            raise ContradictionBenchmarkError(f"{paper_id} lacks PDF page {page}")
    return path.relative_to(REPO_ROOT).as_posix()


def _materialize(
    specs: Sequence[Mapping[str, Any]],
    papers: Mapping[str, Mapping[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, int]]:
    retrieval_rows = []
    truth_rows = []
    distribution: dict[str, int] = {}
    signatures: set[tuple[tuple[str, tuple[int, ...]], ...]] = set()
    questions: set[str] = set()
    for number, spec in enumerate(specs, start=301):
        question_id = f"q{number:03d}-contradiction-{spec['slug']}"
        sides = spec.get("sides")
        if not isinstance(sides, list) or not 2 <= len(sides) <= 4:
            raise ContradictionBenchmarkError(f"{question_id} must bind two to four sources")
        signature = tuple(
            sorted(
                (
                    str(side["paper_id"]),
                    tuple(int(value) for value in side["claim_indices"]),
                )
                for side in sides
            )
        )
        if signature in signatures:
            raise ContradictionBenchmarkError(f"Duplicate contradiction signature: {question_id}")
        signatures.add(signature)
        evidence = []
        answer_sections = []
        paper_ids = []
        for side in sides:
            paper_id = side.get("paper_id")
            claim_indices = side.get("claim_indices")
            paper = papers.get(paper_id) if isinstance(paper_id, str) else None
            if (
                paper is None
                or not isinstance(claim_indices, list)
                or not claim_indices
                or any(
                    isinstance(value, bool)
                    or not isinstance(value, int)
                    or value < 0
                    or value >= len(paper["claims"])
                    for value in claim_indices
                )
            ):
                raise ContradictionBenchmarkError(f"{question_id} has an invalid evidence side")
            paper_ids.append(paper_id)
            statements = []
            for claim_index in claim_indices:
                claim = paper["claims"][claim_index]
                pages = claim.get("evidence_pages")
                statement = claim.get("statement")
                kind = claim.get("kind")
                if (
                    not isinstance(pages, list)
                    or not pages
                    or any(
                        isinstance(page, bool) or not isinstance(page, int) or page < 1
                        for page in pages
                    )
                    or not isinstance(statement, str)
                    or not statement
                    or not isinstance(kind, str)
                    or not kind
                ):
                    raise ContradictionBenchmarkError(
                        f"{question_id} references an incomplete claim"
                    )
                source_markdown = _validate_pages(paper_id, pages)
                statements.append(statement)
                evidence.append(
                    {
                        "paper_id": paper_id,
                        "paper_title": paper["title"],
                        "method_name": paper["method_name"],
                        "claim_index": claim_index,
                        "claim_kind": kind,
                        "statement": statement,
                        "evidence_pages": pages,
                        "source_markdown": source_markdown,
                        "source_markdown_sha256": _sha256_file(REPO_ROOT / source_markdown),
                    }
                )
            answer_sections.append(
                f"{paper['method_name']} ({paper_id}): " + " ".join(statements)
            )
        unique_paper_ids = sorted(set(paper_ids))
        if len(unique_paper_ids) != len(paper_ids):
            raise ContradictionBenchmarkError(f"{question_id} repeats a source")
        question = (
            f"Contradiction audit: {spec['challenge']} Retrieve and identify every relevant "
            "source. For each side, state the exact claim and evidence boundary. Align the "
            "task, corpus or domain, model, retrieval unit, metric, baseline, and operating "
            "assumptions before deciding whether this is a direct contradiction, a "
            "scope-conditioned tension, an evidence-incommensurable result, or a compatible "
            "trade-off. State what conclusion is supported and what stronger conclusion is not."
        )
        normalized_question = " ".join(_tokens(question))
        if normalized_question in questions:
            raise ContradictionBenchmarkError(f"Duplicate generated question: {question_id}")
        questions.add(normalized_question)
        if len(_tokens(question)) < 75:
            raise ContradictionBenchmarkError(f"{question_id} is not sufficiently complex")
        retrieval_rows.append(
            {
                "id": question_id,
                "question": question,
                "qrels": {
                    "paper_ids": unique_paper_ids,
                    "source_ids": _source_ids(unique_paper_ids),
                },
                "evaluation": {
                    "focus": "cross-source contradiction retrieval",
                    "required_source_count": len(unique_paper_ids),
                },
            }
        )
        truth_rows.append(
            {
                "id": question_id,
                "question": question,
                "category": spec["category"],
                "verdict": spec["verdict"],
                "expected_answer": (
                    f"Verdict: {spec['verdict']}. {spec['rationale']}\n\n"
                    + "\n\n".join(answer_sections)
                ),
                "rationale": spec["rationale"],
                "scope_dimensions": spec["scope_dimensions"],
                "paper_ids": unique_paper_ids,
                "evidence": evidence,
                "review": {
                    "status": "source-derived-claim-bound-contradiction-adjudication",
                    "independent_human_adjudication": False,
                    "mechanical_evidence_validation": True,
                    "answer_scope": (
                        "all cited sides and the authored contradiction verdict are required"
                    ),
                },
            }
        )
        distribution[str(len(unique_paper_ids))] = (
            distribution.get(str(len(unique_paper_ids)), 0) + 1
        )
    return retrieval_rows, truth_rows, distribution


def build() -> dict[str, str]:
    """Build all contradiction evaluation artifacts in memory."""

    papers, claim_inputs = _load_papers()
    specs = _question_specs()
    retrieval, truth, distribution = _materialize(specs, papers)
    retrieval_text = "\n".join(_json_line(row) for row in retrieval) + "\n"
    truth_text = "\n".join(_json_line(row) for row in truth) + "\n"
    retrieval_sha = _sha256_bytes(retrieval_text.encode("utf-8"))
    truth_sha = _sha256_bytes(truth_text.encode("utf-8"))
    forbidden_uses = [
        "knowledge construction",
        "retrieval-profile construction",
        "skill or query-adapter evolution",
        "trace distillation",
        "candidate realization or selection",
        "discovery, development, or validation fitness",
    ]
    policy = {
        "schema_version": POLICY_SCHEMA_VERSION,
        "dataset_id": DATASET_ID,
        "classification": "evaluation-only",
        "allowed_uses": [
            "sealed final evaluation",
            "aggregate comparison reporting",
        ],
        "forbidden_uses": forbidden_uses,
        "questions_sha256": retrieval_sha,
        "ground_truth_sha256": truth_sha,
        "copying_or_reformatting_does_not_change_policy": True,
    }
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "dataset_id": DATASET_ID,
        "classification": "evaluation-only",
        "corpus": {
            "dataset_id": "graphrag-papers-40",
            "paper_count": 15,
            "new_source_groups": False,
            "description": (
                "New contradiction-search questions over the existing frozen GraphRAG papers"
            ),
        },
        "question_count": len(retrieval),
        "question_id_range": [retrieval[0]["id"], retrieval[-1]["id"]],
        "source_count_distribution": distribution,
        "contract": {
            "minimum_sources_per_question": 2,
            "maximum_sources_per_question": 4,
            "top_k": 10,
            "primary_identity": "authoritative-paper",
            "required_adjudication": [
                "retrieve every cited side",
                "align scope and measurement dimensions",
                "classify contradiction status",
                "state supported and unsupported conclusions",
            ],
            "direct_retrieval_metrics": [
                "recall_at_10",
                "full_evidence_set_rate_at_10",
                "mrr_at_10",
                "ndcg_at_10",
                "evidence_validity",
                "query_stability",
                "p95_latency_ms",
            ],
        },
        "review": {
            "answer_source": "previously reviewed claim ledger",
            "verdict_source": "authored cross-source scope adjudication",
            "independent_human_adjudication": False,
            "mechanical_checks": [
                "claim index exists",
                "claim text is preserved exactly",
                "every evidence page exists in pinned Markdown",
                "every Markdown source is SHA-256 bound",
                "every question binds two to four unique papers",
            ],
        },
        "inputs": claim_inputs,
        "artifacts": {
            "retrieval-questions.jsonl": {
                "bytes": len(retrieval_text.encode("utf-8")),
                "sha256": retrieval_sha,
            },
            "ground-truth.jsonl": {
                "bytes": len(truth_text.encode("utf-8")),
                "sha256": truth_sha,
            },
        },
        "policy": policy,
    }
    return {
        "retrieval-questions.jsonl": retrieval_text,
        "ground-truth.jsonl": truth_text,
        "manifest.json": _canonical_json(manifest),
        "EVALUATION_ONLY.json": _canonical_json(policy),
    }


def _write_or_check(output_dir: Path, expected: Mapping[str, str], *, check: bool) -> None:
    if check:
        for name in OUTPUT_FILES:
            path = output_dir / name
            if not path.is_file():
                raise ContradictionBenchmarkError(f"Missing generated artifact: {path}")
            if path.read_bytes() != expected[name].encode("utf-8"):
                raise ContradictionBenchmarkError(f"Generated artifact drifted: {path}")
        unexpected = sorted(
            path.name
            for path in output_dir.iterdir()
            if path.is_file() and path.name not in OUTPUT_FILES
        )
        if unexpected:
            raise ContradictionBenchmarkError(
                "Unexpected files in contradiction benchmark: " + ", ".join(unexpected)
            )
        return
    if output_dir.exists() and any(output_dir.iterdir()):
        exact_existing = all(
            (output_dir / name).is_file()
            and (output_dir / name).read_bytes() == expected[name].encode("utf-8")
            for name in OUTPUT_FILES
        )
        if not exact_existing:
            raise ContradictionBenchmarkError(
                f"Refusing to overwrite non-empty output directory: {output_dir}"
            )
        return
    output_dir.mkdir(parents=True, exist_ok=True)
    for name in OUTPUT_FILES:
        (output_dir / name).write_text(expected[name], encoding="utf-8", newline="\n")


def _task_tree(expected: Mapping[str, str]) -> dict[str, str]:
    rows = [
        json.loads(line)
        for line in expected["retrieval-questions.jsonl"].splitlines()
        if line.strip()
    ]
    result = {}
    for row in rows:
        question_id = row["id"]
        task_root = Path(question_id)
        result[(task_root / "task.toml").as_posix()] = (
            'schema_version = "1.3"\n'
            "\n"
            "[task]\n"
            f'name = "knowledge/{DATASET_ID}__direct-retrieval__{question_id}"\n'
            'description = "Evaluation-only cross-source contradiction retrieval case."\n'
            'keywords = ["semantic-okf", "graphrag", "contradiction", "evaluation-only"]\n'
            "\n"
            "[metadata]\n"
            'difficulty = "hard"\n'
            'category = "cross-source-contradiction-retrieval"\n'
            f'dataset_id = "{DATASET_ID}"\n'
            'mode = "direct-retrieval"\n'
            'cohort = "evaluation-only"\n'
            "\n"
            "[agent]\n"
            "timeout_sec = 180.0\n"
            'network_mode = "none"\n'
            "\n"
            "[verifier]\n"
            "timeout_sec = 60.0\n"
            'environment_mode = "separate"\n'
            'network_mode = "none"\n'
            "\n"
            "[environment]\n"
            'docker_image = "semantic-okf-harbor-runtime:1.0"\n'
            'os = "linux"\n'
            'network_mode = "none"\n'
            "memory_mb = 4096\n"
            "storage_mb = 8192\n"
            'workdir = "/workspace"\n'
        )
        result[(task_root / "instruction.md").as_posix()] = (
            "# Cross-source contradiction retrieval\n\n"
            f"{row['question']}\n\n"
            "Return the relevant authoritative paper identities in ranked order. "
            "Do not assume that an apparent tension is a direct contradiction.\n"
        )
    return result


def _write_or_check_tasks(tasks_dir: Path, expected: Mapping[str, str], *, check: bool) -> None:
    task_files = _task_tree(expected)
    if check:
        actual = {
            path.relative_to(tasks_dir).as_posix()
            for path in tasks_dir.rglob("*")
            if path.is_file()
        }
        if actual != set(task_files):
            raise ContradictionBenchmarkError("Generated contradiction task inventory drifted")
        for relative, text in task_files.items():
            if (tasks_dir / relative).read_bytes() != text.encode("utf-8"):
                raise ContradictionBenchmarkError(
                    f"Generated contradiction task drifted: {relative}"
                )
        return
    if tasks_dir.exists() and any(tasks_dir.iterdir()):
        raise ContradictionBenchmarkError(
            f"Refusing to overwrite non-empty task directory: {tasks_dir}"
        )
    for relative, text in task_files.items():
        path = tasks_dir / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")


def main(argv: Sequence[str] | None = None) -> int:
    """Build or check the contradiction benchmark."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--tasks-dir", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    try:
        expected = build()
        _write_or_check(args.output_dir.resolve(), expected, check=args.check)
        if args.tasks_dir is not None:
            _write_or_check_tasks(args.tasks_dir.resolve(), expected, check=args.check)
    except (ContradictionBenchmarkError, OSError, UnicodeError, ValueError, TypeError) as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, sort_keys=True))
        return 2
    print(
        json.dumps(
            {
                "status": "pass",
                "check": args.check,
                "dataset_id": DATASET_ID,
                "question_count": QUESTION_COUNT,
                "questions_sha256": _sha256_bytes(
                    expected["retrieval-questions.jsonl"].encode("utf-8")
                ),
                "ground_truth_sha256": _sha256_bytes(
                    expected["ground-truth.jsonl"].encode("utf-8")
                ),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
