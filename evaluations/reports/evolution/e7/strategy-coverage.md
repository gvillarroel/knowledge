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

The [configuration audit](catalog-audit-001/README.md) checks all 117 variants:
82 against the native builder plan parsers and 35 through the frozen
consultation bridge with fixture dependencies. These checks do not count as
native dataset trials. It also identifies a conditional Adaptive limitation:
when the full query supplies ten identities, protecting all ten prevents
aspect-weight changes from changing the top ten. Other Adaptive construction
mechanisms remain able to change that full-query ranking.

The later [Classical source-group audit](classical-source-cap-001/README.md)
finds another limitation: diversity uses an application-level fallback identity
with a cap of one, so three Classical routes cannot return multiple independent
documents from the same application. The E7 catalog does not vary that cap or
identity policy. The verified follow-up plan is untested and belongs to a new
study; it is not an additional completed opportunity in this table. Exhausting
the frozen catalog must not be reported as exhausting every possible operator.

The [Ensemble protected-set audit](ensemble-protection-001/README.md) exercises
the exact generic fusion function with synthetic component payloads. All three
declared quality-weight variants can affect rank order in the full-set fixture,
but every variant preserves Adaptive's document set. A short protected set is
not refilled from auxiliary routes. Allocation therefore has a ranking
opportunity; Adaptive construction can separately change coverage. These eight
fixture cases are not native Enterprise trials or completed family opportunities.

## Execution and interpretation

The [Entity Graph function audit](entity-graph-opportunity-001/README.md)
exercises graph reach and candidate-edge weights with synthetic sections,
native edge construction and exact query functions. Increasing reach changes
the returned document set in the fixture. Positive edge-weight changes with
identical component order leave rank fusion unchanged; zero candidate-edge
weight still permits direct-entity and mention contributions. Document grouping
allows multiple records from one application. These eight cases do not replace
any native Entity Graph trial or establish Enterprise performance.

The [Graphify function audit](graphify-opportunity-001/README.md) verifies depth
and fusion sensitivity with synthetic graphs and lists. Changing depth can
change the returned set, while a larger visited set can leave the top ten
unchanged. First enabling lexical fusion also expands graph and lexical pools
to at most 100 each. Rank-decay variants set lexical weight to one as well as
changing decay, so exact parent and child profiles determine attribution. These
fixtures use pinned local query functions and consume no native opportunities
or controller misses.

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
scope. The [completed Legacy search](legacy-complete-001/README.md) records a
measured gain and a later plateau; the
[completed Embeddings search](embeddings-complete-001/README.md) records six
construction timeouts and retention of its baseline. Both terminal histories
were replayed. This inventory does not claim a gain for an unfinished family.
