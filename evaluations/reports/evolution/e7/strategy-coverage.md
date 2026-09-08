# E7 strategy coverage

All eight families belong to the same frozen campaign. Completing Legacy does
not complete the study. Each other family retains its own native baseline,
primary route, mutation channel and sequential three-miss counter.

| Family | Mutation channel | Primary route | Predeclared mechanisms | Catalog variants per round |
| --- | --- | --- | --- | ---: |
| Legacy | Consultation | lexical | BM25 saturation; length normalization; title weight | 11 |
| Embeddings | Construction | hybrid | Semantic segmentation; neighboring-sentence context | 8 |
| Classical | Construction | fusion | Length normalization; BM25 saturation; title weight; expansion strength; relevance versus diversity | 17 |
| Adaptive | Construction | adaptive | Length normalization; BM25 saturation; title weight; expansion strength; relevance versus diversity; query-aspect allocation | 20 |
| Entity Graph | Construction | fusion | Length normalization; BM25 saturation; graph reach; candidate-edge noise; section granularity | 16 |
| Ensemble | Construction | quality | Pinned learned embeddings; length normalization; BM25 saturation; title weight; expansion strength; relevance versus diversity; route allocation | 21 |
| Graphify | Consultation | search | Traversal depth; lexical/graph fusion; reciprocal-rank decay | 13 |
| Turso | Consultation | lexical-sql | BM25 saturation; length normalization; title weight | 11 |

The inventory has 117 variants per catalog round, including 106 across the
seven non-Legacy families. These are declared options, not completed trial
counts: the three-miss rule and duplicate-profile detection can skip variants.
After an improving round, repeat the catalog with the retained configuration.
A complete round without improvement ends that family. A five-round resource
limit, if reached while still improving, must be reported as budget exhaustion.

## Execution and interpretation

Two family lanes execute concurrently, with one trial at a time in each lane.
The next queued family starts when a lane becomes free. Each agent has two CPU
threads and 6 GiB RAM. These resource limits are part of the frozen comparison;
an active long-running trial is neither a completed score nor permission to
change another family's resource allocation.

A qualified strict improvement retains the new profile and resets the miss
count. Native execution errors remain rejected evidence with unavailable
retrieval scores, even when the owner's scheduler objective is zero. A proven
external failure stops affected execution for separate review. There are no
automatic retries or silent model fallbacks.

The all-family release sequence remains unchanged: finish all eight searches,
replay the exact joint selection against the baseline, freeze it, compare both
arms on all 500 public questions, then apply the one private transfer gate.
Every final family report must show qualified quality, execution failures,
stopping evidence and time consumed. Promotion is a decision about the entire
frozen bundle.

See the [campaign status](README.md) and the
[study guide](../../../../docs/enterprise-stratified-evolution.md) for dataset
scope and the [completed Legacy search](legacy-complete-001/README.md) for the
first completed family's evidence. This inventory does not claim a gain for
an unfinished family.
