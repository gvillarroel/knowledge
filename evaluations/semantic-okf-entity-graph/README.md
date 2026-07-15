# Semantic OKF Entity-to-Section Graph Evaluation

This evaluation adds a fourth isolated Semantic OKF generation without changing the legacy,
embedding, or classical packages. It builds an entity-first graph whose evidence paths terminate at
exact paper sections, compares twelve retrieval routes on the same forty questions, and evaluates ten
actual hard-question answers in a paired Skill Arena control/treatment run.

For a metric-by-metric explanation, causal interpretation, and deployment recommendation, see
[How to Read the Semantic OKF Evaluation Results](EVALUATION-CONCLUSIONS.md).

## New standalone pair

- `skills/build-semantic-okf-entity-graph`
- `skills/consult-semantic-okf-entity-graph`

The builder creates the ordinary authoritative Semantic OKF core and then adds a derived,
non-authoritative `entity-graph/` directory. The consultant validates and searches that directory
read-only. Neither package imports an existing Semantic OKF skill.

## What the graph contains

The closed projection has 304 exact PDF-page sections, 1,455 entities, 18,830 mentions, and 26,007
edges. Of the entities, 874 are reviewed Semantic OKF identities and 581 are deterministic candidate
phrases. Of the edges, 4,301 project reviewed identities or evidence locators and 21,706 are candidate
mention or co-mention paths.

The useful path is:

```text
reviewed method/dimension -> reviewed claim -> exact evidence section -> reviewed paper
candidate phrase          -> exact mention section             -> reviewed paper
candidate phrase          -> candidate co-mention phrase
```

Candidate phrases, mentions, co-mentions, path weights, and rankings are discovery signals. They are
never added to the authoritative ledger, concepts, or RDF, and they cannot be cited as facts. Reviewed
claim nodes expose the exact authoritative record ID, concept path, claim-source path, paper, PDF page,
section ID, and text hash needed to verify an answer.

## Pinned inputs and reproducibility

The plan selects the same fifteen paper Markdown sources and fifteen reviewed-claim JSONL sources as
the earlier evaluations, plus the separately declared analysis vocabulary required by the core. The
authoritative logical core has 874 records and SHA-256
`331af2f1064463484f64dfaa58bc17d6c6b2f75ef3fca9d371473450deb84424`.

Two final independent builds contained 891 files each and were byte-identical. Their canonical sorted
path-and-byte tree SHA-256 was
`9c4047eb7ee6a52b1a742cc10d9bc1b12529bc355c262fbe8afb1b4753a2d8ba`. The derived graph index SHA-256
was `208e267df72acfc22cc99589e814f4338e3d899ca8ab500db2383ede23a83867`.

Rebuild and validate twice:

```powershell
python skills/build-semantic-okf-entity-graph/scripts/build_semantic_okf_entity_graph.py `
  evaluations/graphrag-cross-paper/manifest.json `
  evaluations/semantic-okf-entity-graph/entity-graph-plan.json `
  tmp/entity-graph-a --output-format json

python skills/build-semantic-okf-entity-graph/scripts/validate_semantic_okf_entity_graph.py `
  tmp/entity-graph-a --output-format json

python skills/build-semantic-okf-entity-graph/scripts/build_semantic_okf_entity_graph.py `
  evaluations/graphrag-cross-paper/manifest.json `
  evaluations/semantic-okf-entity-graph/entity-graph-plan.json `
  tmp/entity-graph-b --output-format json

python skills/build-semantic-okf-entity-graph/scripts/validate_semantic_okf_entity_graph.py `
  tmp/entity-graph-b --output-format json
```

Deep consultation validation rederives every graph artifact in memory:

```powershell
python skills/consult-semantic-okf-entity-graph/scripts/query_semantic_okf_entity_graph.py `
  tmp/entity-graph-a inspect --deep-validation
```

## Query routes

- `lexical` uses persisted section Bag-of-Words statistics and Okapi BM25.
- `entity` resolves reviewed or candidate entity aliases, then follows exact mentions and reviewed
  claim-evidence edges.
- `traversal` performs bounded graph propagation with separate reviewed and candidate edge weights.
- `fusion` combines all three rankings with reciprocal-rank fusion and a per-paper diversity cap.

Example:

```powershell
python skills/consult-semantic-okf-entity-graph/scripts/query_semantic_okf_entity_graph.py `
  tmp/entity-graph-a search `
  --query "compare graph corruption defenses and failure conditions" `
  --mode fusion --top-k 10
```

`manual-query-verification.json` records successful lexical, entity, traversal, and fusion spot checks,
exact section/hash agreement, expected leading papers, and an unchanged bundle tree.

## Retrieval comparison

All values below are direct top-10 paper-level metrics over the same forty questions. “Hard” is the
ten-question evidence-first cohort. Every route completed forty queries with zero errors, 100%
independently valid evidence, and identical authoritative-core hashes.

| Builder / consultant | Route | All recall@10 | All MRR@10 | All nDCG@10 | Hard recall@10 | Hard MRR@10 | Hard nDCG@10 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| legacy Semantic OKF | `legacy_lexical` | 79.31% | 78.96% | 74.22% | 80.67% | 57.50% | 56.81% |
| embedding Semantic OKF | `new_lexical` | 54.75% | 88.83% | 60.92% | 73.50% | 80.33% | 65.78% |
| embedding Semantic OKF | `vector` | 50.40% | 78.75% | 54.77% | 61.00% | 66.67% | 53.05% |
| embedding Semantic OKF | `hybrid` | 48.34% | 88.54% | 56.51% | 65.17% | 87.50% | 64.60% |
| classical Semantic OKF | `classical_fusion` | **83.46%** | 95.83% | **83.23%** | **95.50%** | **95.00%** | **84.98%** |
| entity-graph Semantic OKF | `entity_graph_fusion` | 80.84% | 93.13% | 79.86% | 91.67% | 90.00% | 76.32% |

The complete twelve-route direct and pool-100 tables are in `retrieval-summary.md`. The extra graph
routes establish material graph participation: on the hard cohort, entity-only recall was 85.0% and
traversal-only recall was 86.67%, both above legacy lexical at 80.67%. Graph fusion added the broadest
graph coverage but remained 3.83 points behind classical fusion.

Pool-100 scoring matters mainly for the chunk-based embedding bundle. Its lexical and hybrid hard
recall rose to 93.0% and 90.5% after paper deduplication, while entity-graph fusion remained 91.67% and
classical fusion remained 95.5%.

## Actual grounded answers

The ten new questions retain evidence-first hidden ground truth with atomic claims, required papers
and source identities, exact claim lines and paper-page hashes, derivation logic, acceptable variants,
and important negatives. `validate_hard_ground_truth.py` independently rechecks all of those bindings
and the exact 30+10 benchmark composition.

The live Skill Arena run used one model route and identical questions and graph workspace for:

- `knowledge-only-control`; and
- `entity-graph-consult-treatment`, with only the new consult skill added.

All twenty cells returned usable JSON and there were no transport errors. A blinded fixed-rubric
review scored correctness, semantic completeness, and important negatives. A separate deterministic
scorer recomputed evidence validity and grounding against the authoritative ledger and concepts. The
compact four-method, eight-profile report is `grounded-answer-summary.md`.

| Consult treatment | Contract | Evidence validity | Grounding | Correctness | Completeness | Required papers | Negatives |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| legacy | 10.0% | 84.3% | 83.5% | 88.8% | 75.0% | 75.0% | 90.0% |
| embedding | 40.0% | **83.6%** | **83.4%** | **96.2%** | **82.8%** | **89.2%** | **100.0%** |
| classical | 30.0% | 80.4% | 79.7% | 91.5% | 82.2% | 86.7% | 95.0% |
| entity graph | 40.0% | 60.0% | 60.0% | 78.8% | 70.2% | 67.7% | 90.0% |

Paired treatment-minus-control deltas were:

| Method | Correctness | Completeness | Evidence validity | Grounding | Required papers | Negatives |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| legacy | -5.2 points | -8.2 | +1.7 | +0.6 | -7.2 | -10.0 |
| embedding | +1.0 | +2.0 | +12.7 | +12.4 | +11.7 | +2.5 |
| classical | -4.0 | 0.0 | -3.5 | -3.6 | +7.0 | -5.0 |
| entity graph | -21.2 | -11.8 | -15.6 | -16.0 | -16.5 | -10.0 |

Strict all-contract pass was 0% for every method because one literal sub-contract failure fails the
entire cell. It is reported separately from graded answer quality.

## Interpretation

1. The graph strategy works as a retriever. Entity and traversal routes independently beat legacy
   hard-question recall, and fusion reached 91.67% with fully valid exact-section evidence.
2. Classical topic/association fusion is still the best retrieval choice for this corpus: 95.5% hard
   recall and the best hard nDCG, without model dependencies.
3. The entity graph is most valuable as an auditable index and complementary retrieval route, not as
   a replacement for the classical route.
4. Better retrieval did not translate into a better answer agent. The graph treatment sometimes
   reconstructed claim IDs from concept filenames, changed paper-ID punctuation, or emitted full
   source fragments where integer pages were required. Those serialization errors reduced otherwise
   plausible answers to invalid evidence.
5. The next promising experiment is graph retrieval followed by a deterministic evidence adapter that
   copies contract-ready claim IDs, paths, paper IDs, and pages directly from reviewed graph nodes.
   That should be evaluated on a fresh holdout rather than retrofitted to these ten frozen questions.

These answer estimates cover ten questions and one model route; they are causal within each paired
run but are not confidence-bounded population estimates.

## Skill Arena reproduction

The checked config was authored and validated through the Skill Arena config workflow. Its ten prompts
cover nine task families and all three required case kinds. Revalidate and run with:

```powershell
$ValidateDesign = Join-Path $HOME '.agents/skills/skill-arena-config-author/scripts/validate-evaluation-design.js'
node $ValidateDesign `
  evaluations/semantic-okf-entity-graph/skill-arena/entity-graph-hard10.yaml `
  --coverage evaluations/semantic-okf-entity-graph/skill-arena/prompt-coverage.json

skill-arena val-conf evaluations/semantic-okf-entity-graph/skill-arena/entity-graph-hard10.yaml
skill-arena evaluate evaluations/semantic-okf-entity-graph/skill-arena/entity-graph-hard10.yaml --dry-run
skill-arena evaluate evaluations/semantic-okf-entity-graph/skill-arena/entity-graph-hard10.yaml
```

The accepted live evaluation ID was `eval-wxC-2026-07-14T13:24:38`: 20 completed cells, zero
transport errors. Raw bundles, answer text, reviewer batches, and run outputs remain append-only and
ignored below `results/runs/20260714-entity-graph-final-01`. Compact plans, configs, manifests,
questions, ground truth, and metric summaries are checked in.

`scripts/prepare_evaluation_run.py` atomically prepares a previously absent run ID, or audits a
manually staged run before execution. `finalize` refuses changed workspaces, requires both retrieval
runs, the entity-graph Skill Arena result, and blinded reviews, then publishes a hash inventory once.
