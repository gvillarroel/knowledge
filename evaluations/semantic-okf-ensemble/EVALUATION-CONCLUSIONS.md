# Semantic OKF Evaluation Conclusions

> **Current versus historical boundary:** the active
> `consult-semantic-okf-ensemble` skill is CLI-only and makes zero MCP calls. All
> MCP v1.5.0 Skill Arena results below are preserved historical experiment evidence
> from commit `3a5df66baf99c6c34ef6ff96d35aa44740b906c6`, not measurements of the current
> transport. ADR 0027 supersedes ADR 0026 for current operation without invalidating
> ADRs 0023–0026 or changing any historical report, hash, or metric.

## Current CLI-only evidence

The difficult `q031-graph-routing-boundary` question was verified through the local
CLI only. Deep validation passed, the `quality` policy materially used adaptive,
BM25, embedding, and entity-graph routes, and the bounded coverage pages contained
`[48, 48, 48, 48, 14]` claims for 206 unique reviewed claims. The run recorded
coverage SHA-256 `881dec7d573003631c7ee5bb6c55ba4568393df1f911c26dbaa7bfa5c0619ac7`
and priority-order SHA-256
`9ec21df4d02d0e1fba2a9dac3555c68e424968d347ff4d48d8df768351e1b25b`.
It covered 4/4 atomic answer groups, 1/1 important-negative group, 3/3 required
papers, and four authoritative evidence bindings with zero MCP calls. End-to-end
validation, coverage, and answer preparation took approximately 66.23 seconds; the
captured final output SHA-256 was
`e052575835024481527ed7f07c80242a2ab414370f8868323861945931e43d50`.

This proves that the active definitive consultant can execute one difficult case
without MCP while retaining its retrieval and evidence gates. It does not transfer
the historical MCP publication guarantees or establish new aggregate CLI-only
answer-quality metrics. The retrieval comparison remains applicable to the same
deterministic algorithms; the 90-answer contract, grounding, correctness, and
completeness table remains explicitly historical.

The [exact q031 consultation comparison](cli-q031-comparison.md) preserves the full
responses from legacy, embedding, classical, entity-graph, adaptive, and current
definitive consultation. Under the five retained mechanical gates, the direct
current CLI finalizer passes 5/5 (`1.0`), embeddings passes 3/5 (`0.6`), and the
other four predecessor rows pass 2/5 (`0.4`). These cross-run rows are descriptive,
not causal.

A fresh, paired, MCP-free Skill Arena diagnostic used the checked
[`cli-q031.yaml`](skill-arena/cli-q031.yaml) configuration. The first attempt is
rejected because the treatment hit the adapter's 240-second limit. With the
adapter limit aligned to the existing 600-second evaluation timeout, the control
scored `0.6` and the treatment scored `0.8`: the treatment passed response format,
response contract, atomic completeness, and the important negative, but failed
evidence validity after the agent changed exactly two authoritative source paths
from `2506.05690v3.jsonl` to the nonexistent `2506-05690v3.jsonl`. The deterministic
CLI output itself retained the correct paths and passed all five gates. The
[compact diagnostic](cli-q031-skill-arena-diagnostic.md) therefore establishes a
sharp boundary: MCP is not required for retrieval, coverage, or deterministic
finalization, but CLI-only skill instructions do not mechanically guarantee that a
host agent will publish the finalizer bytes unchanged.

## Conclusion

The definitive ensemble `quality` policy is the strongest observed direct-ranking option on the frozen 40-question benchmark. It preserves the adaptive incumbent's paper Recall@10 and 100% evidence validity while improving the order of relevant papers: all-40 MRR@10 rises from 95.83% to 100.00% and nDCG@10 from 83.43% to 85.20%; hard-10 MRR@10 rises from 95.00% to 100.00% and nDCG@10 from 84.98% to 88.27%.

The accepted answer-preparation route now also covers all 44 reviewed hard-question answer groups, all 13 important-negative groups, all required papers, and 713/713 independently validated evidence bindings. It reached that result with deterministic paper-conditioned semantic-claim diversification: the earlier reviewed candidate covered 43/44 groups, while the accepted reranker covers 44/44 with a smaller mean union, 162.4 rather than 166.4 claims.

The complete v1.5.0 generated-answer experiment adds a third bounded win. Skill Arena run `2026-07-15T15-24-19-159Z-compare` (`eval-RTd-2026-07-15T15:24:26`) produced all 90 planned answers, preparation `live-published-confirmed-01` received 90 blinded reviews, and the independent 90-trace attestation passed. The ensemble treatment reached 100.0% response-contract compliance, evidence validity, and grounding, with 96.7% correctness and 91.1% semantic completeness. Against the matched adaptive control, those results are improvements of 76.7, 17.4, 17.5, 13.7, and 18.4 percentage points, respectively.

These are bounded wins, not a universal win. Direct ranking does not add top-10 paper recall, `quality` has the highest measured ensemble p95 latency, and neither 100% candidate coverage nor one completed generation benchmark proves universal answer quality. Use `quality` when evidence ordering and synthesis readiness matter most, `robust` for the protected adaptive floor, and `fast` when avoiding the pinned embedding route matters; in these measurements, `fast` is faster than `quality` but not faster than `robust`.

## Complete direct-retrieval comparison

All rows below use the same frozen 40-question, direct top-10, canonical paper-identity comparison and evidence-valid schema 1.2 contract. The first 13 routes come from the checked [adaptive retrieval summary](../semantic-okf-adaptive/retrieval-summary.json). The ensemble rows are independently recomputed from the current final release in the checked [`robust`](baselines/ensemble-robust-current-direct.json), [`fast`](baselines/ensemble-fast-current-direct.json), and [`quality`](baselines/ensemble-quality-winner-direct.json) reports.

The six standalone, independently installable pairs map to the evaluated routes as follows:

| Family | Build skill | Consult skill | Evaluated routes / policies |
| --- | --- | --- | --- |
| Legacy | `build-semantic-okf` | `consult-semantic-okf` | `legacy_lexical` |
| Embeddings | `build-semantic-okf-embeddings` | `consult-semantic-okf-embeddings` | `new_lexical`, `vector`, `hybrid` |
| Classical | `build-semantic-okf-classical` | `consult-semantic-okf-classical` | `classical_bm25`, `classical_topic`, `classical_association`, `classical_fusion` |
| Entity graph | `build-semantic-okf-entity-graph` | `consult-semantic-okf-entity-graph` | `entity_graph_lexical`, `entity_graph_entity`, `entity_graph_traversal`, `entity_graph_fusion` |
| Adaptive | `build-semantic-okf-adaptive` | `consult-semantic-okf-adaptive` | `adaptive_fusion` |
| Definitive ensemble | `build-semantic-okf-ensemble` | `consult-semantic-okf-ensemble` | `robust`, `fast`, `quality` |

| Builder / consultant family | Retrieval route / policy | All-40 Recall@10 | All-40 MRR@10 | All-40 nDCG@10 | Hard-10 Recall@10 | Hard-10 MRR@10 | Hard-10 nDCG@10 | Evidence validity | P95 ms |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Legacy | `legacy_lexical` | 79.31% | 78.96% | 74.22% | 80.67% | 57.50% | 56.81% | 100.00% | 4.79 |
| Embedding | `new_lexical` | 54.75% | 88.83% | 60.92% | 73.50% | 80.33% | 65.78% | 100.00% | 76.20 |
| Embedding | `vector` | 50.40% | 78.75% | 54.77% | 61.00% | 66.67% | 53.05% | 100.00% | 122.82 |
| Embedding | `hybrid` | 48.34% | 88.54% | 56.51% | 65.17% | 87.50% | 64.60% | 100.00% | 228.52 |
| Entity graph | `entity_graph_lexical` | 79.76% | 96.67% | 81.14% | 84.67% | 86.67% | 74.47% | 100.00% | 241.63 |
| Entity graph | `entity_graph_entity` | 79.58% | 86.04% | 76.72% | 85.00% | 71.67% | 66.08% | 100.00% | 237.23 |
| Entity graph | `entity_graph_traversal` | 78.49% | 80.21% | 74.03% | 86.67% | 75.00% | 69.65% | 100.00% | 235.99 |
| Entity graph | `entity_graph_fusion` | 80.84% | 93.12% | 79.86% | 91.67% | 90.00% | 76.32% | 100.00% | 237.15 |
| Classical | `classical_bm25` | 49.72% | 95.83% | 60.94% | 63.17% | 95.00% | 69.31% | 100.00% | 99.46 |
| Classical | `classical_topic` | 82.42% | 93.33% | 82.25% | 93.00% | 95.00% | 83.75% | 100.00% | 107.79 |
| Classical | `classical_association` | 82.56% | 94.58% | 82.58% | 93.00% | 95.00% | 84.76% | 100.00% | 111.94 |
| Classical | `classical_fusion` | 83.46% | 95.83% | 83.23% | 95.50% | 95.00% | 84.98% | 100.00% | 106.76 |
| Adaptive | `adaptive_fusion` | **83.82%** | 95.83% | 83.43% | **95.50%** | 95.00% | 84.98% | 100.00% | 407.56 |
| Definitive ensemble | `robust` | **83.82%** | 95.83% | 83.43% | **95.50%** | 95.00% | 84.98% | 100.00% | 568.20 |
| Definitive ensemble | `fast` | **83.82%** | 97.50% | 84.30% | **95.50%** | 95.00% | 85.62% | 100.00% | 766.57 |
| Definitive ensemble | `quality` | **83.82%** | **100.00%** | **85.20%** | **95.50%** | **100.00%** | **88.27%** | 100.00% | 1,461.92 |

### How to read the numbers

- **Recall@10** is the fraction of expected papers present anywhere in the first ten results. It measures coverage, not order.
- **MRR@10** is the mean reciprocal rank of the first relevant paper. A value of 100% means every question has a relevant paper at rank one.
- **nDCG@10** rewards placing all relevant papers near the top, not just finding the first one.
- **Evidence validity** means every returned hit passed independent record, path, locator, and hash checks. It does not mean that a generated sentence correctly interprets the evidence.
- **P95 ms** is the 95th-percentile query time recorded by each in-process evaluator. It is a diagnostic, not a cross-system service-level benchmark: route initialization, candidate work, and runtime dependencies differ.

A **percentage-point** difference is a direct subtraction. For example, 100.00% minus 95.83% is **4.17 percentage points**, not a 4.17% relative improvement.

For answer-facing results, the columns mean something different:

- **Answer-group coverage** asks whether the candidate pool contains at least one independently acceptable reviewed claim for each required atomic idea. It does not inspect generated prose.
- **Important-negative coverage** asks whether candidates include an approved anchor for each required exclusion, limitation, or failure condition.
- **Claim correctness** judges whether the generated answer's atomic statements are true under the reviewed evidence.
- **Semantic completeness** measures how much of the required answer content the generated answer actually states.
- **Grounding** measures whether statements point to independently valid supporting evidence.
- **Exact atomic evidence** is the stricter identity score: it credits an answer only when it uses an approved reviewed claim ID, so it can be lower than semantic correctness.
- **Response contract** checks the required JSON shape and field types. A well-written answer can still score zero here if it serializes a page as a locator string or changes a path.

These metrics are deliberately non-substitutable. A high MRR cannot compensate for missing answer facets, and a correct sentence cannot compensate for a fabricated evidence path.

## What changed with the winner

Relative to the adaptive incumbent, `quality` changes ordering while protecting coverage:

| Cohort | Recall@10 change | MRR@10 change | nDCG@10 change |
| --- | ---: | ---: | ---: |
| All 40 | 0.00 percentage points | +4.17 percentage points | +1.77 percentage points |
| Hard 10 | 0.00 percentage points | +5.00 percentage points | +3.29 percentage points |

Relative to `fast`, `quality` adds 2.50 points of all-40 MRR and 0.90 points of all-40 nDCG; on the hard 10 it adds 5.00 MRR points and 2.65 nDCG points. The trade-off in the accepted final-03 replay is p95 latency: about 1,462 ms for `quality`, 767 ms for `fast`, and 568 ms for `robust`.

The population result explains why a real ensemble was useful. The completed [four-generation search](population-search-results.md) evaluated 40 policies with three deterministic replays each. Route and promotion ablations, single-signal emphasis, nearby weight changes, and larger RRF smoothing constants either failed a hard gate or scored below the accepted `4:1:5:1`, `k=7` policy. A ratio-equivalent doubled-weight policy produced the same ranking, so the smaller representation won the deterministic simplicity tie. Two later generations did not improve fitness. The reviewed semantic-claim gate and its later paper-conditioned diversification were added after this selection as non-ranking answer preparation: neither changes direct paper routes, weights, protected sets, or order, so the population ranking metrics remain applicable to final-03.

The family-level pattern is also informative:

- Legacy lexical retrieval is extremely fast and reaches many papers, but its ordering is substantially weaker on the hard synthesis questions.
- The embedding routes are sensitive to the candidate budget because direct chunk retrieval can spend top-10 positions on duplicate papers. A separate pool-100 sensitivity run raises hard Recall@10 to 93.0% for its lexical route, 78.0% for vector, and 90.5% for hybrid; those different-budget figures are intentionally excluded from the direct table.
- Entity-graph lexical retrieval has strong first-hit ordering, while graph fusion improves hard-question coverage. Entity and traversal signals alone are not sufficient.
- Classical topic and association routes provide most of the recall and hard-question nDCG gain. BM25 alone often places one relevant paper first but misses too many expected papers, which is why its MRR is high while Recall@10 and nDCG are low.
- Adaptive fusion is the best pre-ensemble coverage anchor. The final policy protects that set, then uses BM25, graph, and embedding votes to improve ordering rather than allowing a semantic route to erase lexical coverage.

## Retrieval quality versus answer quality

The direct table does **not** score generated answers. Retrieval, evidence readiness, and answer behavior are separate stages:

| Stage | Current evidence | What it establishes | What it does not establish |
| --- | --- | --- | --- |
| Direct retrieval | One accepted 40-question comparison for the 13 predecessor routes; three deterministic replays per ensemble policy and one extra fresh-process `quality` replay | Coverage, first-relevant rank, multi-relevant ordering, evidence identity, and latency | Correct synthesis, completeness, qualifications, or response format |
| Reviewed hard-10 diversified coverage pack | 44/44 answer groups, 13/13 important-negative groups, all required papers, 713/713 validated bindings | Candidate evidence available before drafting under the current reranker | That the eventual answer selects or interprets every candidate correctly |
| Historical manual finalizer | One pre-diversification q031 end-to-end case, all 4 answer groups covered | Read-only behavior, exact binding reconstruction, and explicit facet status for that runtime | Current host-publication integrity or aggregate correctness/completeness |
| Prior adaptive Skill Arena | Paired hard-10 control/treatment generated answers | Answer-output behavior for that earlier adaptive candidate | Final-ensemble answer behavior |
| Final-ensemble Skill Arena | Accepted 90-answer experiment with 90 blinded reviews and a passing independent 90-trace attestation | The full treatment capability: ensemble consultation skill, digest-bound bootstrap, profile-gated MCP workflow, treatment shell isolation, and confirmed-output host publication | Universal quality, out-of-benchmark generalization, or the effect of skill text in isolation |

The historical five-family answer portfolio remains useful descriptive context. Its checked [machine-readable summary](../semantic-okf-adaptive/grounded-answer-summary.json) contains one answer per hard question for each treatment, or ten outputs per row. It used an earlier answer protocol, so it must remain separate from the accepted three-repetition experiment:

| Historical consult treatment | Response contract | Evidence validity | Grounding | Claim correctness | Semantic completeness | Exact atomic evidence | Required papers | Required sources | Important negatives |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Legacy | 10.0% | 84.3% | 83.5% | 88.8% | 75.0% | 50.5% | 75.0% | 74.0% | 90.0% |
| Embeddings | 40.0% | 83.6% | 83.4% | 96.2% | 82.8% | 48.5% | 89.2% | 85.4% | 100.0% |
| Classical | 30.0% | 80.4% | 79.7% | 91.5% | 82.2% | 37.0% | 86.7% | 79.2% | 95.0% |
| Entity graph | 40.0% | 60.0% | 60.0% | 78.8% | 70.2% | 31.5% | 67.7% | 57.6% | 90.0% |
| Adaptive, first release | 20.0% | 59.3% | 60.0% | 93.6% | 57.2% | 19.5% | 69.7% | 56.9% | 100.0% |

The later adaptive generated-answer experiment is a stronger historical comparator, but it still must not be attributed to the definitive ensemble. Its checked [generation-002 report](../semantic-okf-adaptive-evolution/generation-002-summary.json) found:

| Hard-10 generated-answer variant | Response contract | Evidence validity | Grounding | Claim correctness | Semantic completeness | Exact atomic evidence | Required papers | Required sources | Important negatives |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Knowledge-only control | 10.00% | 73.54% | 72.57% | 98.75% | 89.00% | 49.50% | 89.17% | 79.17% | 100.00% |
| Adaptive candidate 11 treatment | 100.00% | 94.40% | 93.68% | 98.00% | 84.75% | 53.50% | 93.00% | 91.33% | 100.00% |

That paired treatment improved response-contract compliance, evidence validity, grounding, exact evidence coverage, and source coverage, but reduced completeness by 4.25 percentage points and correctness by 0.75 points. It demonstrates why multiple gates are necessary: a more grounded answer can still omit useful content.

## Coverage, ground truth, and expected IDs

The answer evaluation now uses the append-only reviewed benchmark `semantic-okf-ensemble-reviewed-answer-40-plus-hard10-v1`. It leaves the parent retrieval and question bytes unchanged and preserves every statement, qrel, required paper/source, derivation, acceptable textual variant, important negative, and parent evidence option. A closed amendments file appends only independently sufficient reviewed alternatives to existing OR groups. The parent had 72 expected-ID links and 42 unique IDs; the reviewed version has 113 links, 68 unique IDs, and 71 exact authoritative evidence objects. The review rejected 38 close alternatives that were partial, changed a condition, or otherwise did not independently satisfy the complete group. This broadens valid evidence scoring without changing the answer key.

The accepted [paper-diversified hard-10 coverage report](hard10-coverage-pack-multisignal-diversified-publication-gate-final.md) and [machine-readable report](hard10-coverage-pack-multisignal-diversified-publication-gate-final.json) have SHA-256 values `25720899f87efedf4f9c901d91df19dbe97d2ffba53fec7c61e8dff0576ad0a1` and `f96ab9356a99ca5b3798e4de6912e0a6b5fc010c3abb5711360b85257374deec`, respectively. They are bound to reviewed manifest SHA-256 `257997cc2da3d9afae596ac8b46551a1b1fa73480f15861a25f262bb85a91f62` and ground-truth SHA-256 `c656fc575b0c7e06cd386093d975cd74ef9c9aead743312e3aadec1cbdc08451`.

The accepted route keeps the first six global semantic claims, then reserves up to six semantic claims for each of the first three distinct papers independently selected by adaptive retrieval, and finally fills from global semantic order. It retrieves a larger internal pool but retains the existing cap of 20 semantic claims per facet and 240 overall. It receives no question ID, expected claim, qrel, or answer label, cannot introduce a paper, and still intersects every result with a reviewed exact answer binding.

| Reviewed hard-10 experiment | Adaptive groups | Graph groups | Semantic groups | Union groups | Negative groups | Required papers | Mean semantic candidates | Mean union candidates | Valid bindings |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Global semantic order, retained diagnostic | 39/44 | 24/44 | 42/44 | 43/44 | 13/13 | 100.0% | 126.1 | 166.4 | 713/713 |
| Paper-conditioned semantic diversity, accepted | 39/44 | 24/44 | 39/44 | **44/44** | **13/13** | **100.0%** | 104.4 | 162.4 | **713/713** |

The accepted semantic route has lower standalone group coverage than the earlier route, yet it is more complementary to adaptive and graph candidates and recovers the previously missing q033 alternative. The union therefore reaches 100% while becoming slightly smaller. That is the intended ensemble behavior: optimize the gated union's marginal coverage rather than maximizing one component's duplicate-heavy count. The variable-budget union is not Recall@30. Its 100% coverage means at least one reviewed option is available for every group; it does not mean a generated answer will select, interpret, or state every option correctly.

The [pre-diversification report](hard10-coverage-pack-multisignal-publication-gate-final.md), SHA-256 `fdf3f6a96b242dec2b1534746648589597871de65afcadd736628e44352b1e96`, and [machine-readable companion](hard10-coverage-pack-multisignal-publication-gate-final.json), SHA-256 `b477a5a51f7ccaef9695d496c57f79ae8c515b365745f26ded987c12b2637c60`, remain append-only diagnostic evidence. Earlier 41/44 and 198-claim MCP reports used the parent expected-ID interpretation and an older runtime; they remain historical and are not the accepted reviewed-coverage result.

The historical [manual q031 verification](manual-query-verification-final.md), [machine-readable report](manual-query-verification-final.json), and [checked draft](manual-query-q031-draft.json) still prove one earlier finalizer path could reconstruct exact bindings and cover all four q031 groups without mutating the bundle. The later q031 MCP v1.3.1 publication preflight used the 206-claim, five-page diversified pack and established the recoverable four-tool transaction shape: any failed prepare or confirm published nothing, the final clean suffix began with a fresh successful prepare, and exactly one successful confirm was terminal. That intermediate protocol still required copying the complete candidate into confirmation. It is historical runtime preflight evidence, not the later historical v1.5.0 protocol or an aggregate answer-quality result.

The original [expected-ID audit](EXPECTED-ID-AUDIT.md) found all 44 parent atomic mappings and 13 important-negative sets coherent. The reviewed benchmark does not declare those mappings wrong: it preserves them and adds independently sufficient alternatives. The reviewed manifest records 113 total option links, 68 unique reviewed IDs, 71 evidence objects, and 38 explicitly rejected close alternatives. Two qualifications matter:

- a correct answer that uses different valid evidence can lose exact-ID credit; and
- citing an expected ID does not by itself prove that the answer made the required inference or stated the important negative.

Exact-ID metrics are diagnostics. Blinded semantic review remains authoritative for entailment and completeness.

## Confirmed-output publication diagnostics

Four rejected or interrupted live diagnostics are deliberately excluded from answer-quality metrics:

- The [finalizer copy-integrity diagnostic](finalizer-copy-integrity-diagnostic-20260715.md) stopped after 46/90 planned rows. All 15 treatment rows used the superseded single-tool prototype, but only 5/15 visible outputs exactly copied its bytes; q031 was 0/3. This proved that an instruction to copy JSON verbatim is not a publication guarantee.
- The [host-publication mutation diagnostic](host-publication-mutation-diagnostic-20260715.md) examined three q031 treatment rows from the superseded two-mode prototype. All three produced canonical candidates and valid confirmation receipts, but the plain host command published a re-authored message in 3/3 cases and changed six evidence fields. This proved that server confirmation alone is insufficient.
- The [long-candidate confirmation diagnostic](long-candidate-confirmation-diagnostic-20260715.md) records frozen full-run attempt `2026-07-15T13-50-35-550Z-compare` (`eval-d9Z-2026-07-15T13:50:43`). It exercised the historical v1.3.1 protocol; its first treatment prepared successfully, failed to copy the long candidate into confirmation, and did not recover. Execution stopped at that first treatment protocol failure, so the attempt is rejected and contributes no benchmark row or metric.
- The [skill-bootstrap isolation diagnostic](skill-bootstrap-isolation-diagnostic-20260715.md) records partial v1.4.0 run `2026-07-15T14-29-07-959Z-compare` (`eval-T27-2026-07-15T14:29:15`). It persisted 17/90 rows before the stop. One treatment used a faithful but uncontracted shell read of the mounted skill, so none of its rows or metrics are eligible for the accepted comparison.

The historical definitive treatment therefore used the five-tool MCP v1.5.0 server and a hash-bound host wrapper. A no-argument, one-shot bootstrap returned the exact frozen `SKILL.md` body through `semantic-okf-skill-bootstrap/1.0` before inspect; every later treatment tool was gated on that success, and the treatment host disabled the general shell tool. Prepare returned the canonical closed `semantic-okf-prepared-answer/1.0` envelope with exactly `schema`, `candidate_json`, `response_sha256`, and `byte_count`; confirm accepted only the envelope's 64-character lowercase hexadecimal `response_sha256`, never the long candidate. For treatment rows the wrapper parsed and verified the strict envelope, candidate canonicality, digest, UTF-8 length, final clean suffix, and receipt binding, then atomically published the exact `candidate_json` bytes; controls remained transparent pass-throughs. Any bootstrap binding failure or replay, tool before bootstrap, failed prepare or confirm, earlier successful confirm, confirm without a fresh prepare after failure, stale or mismatched digest, repeated confirm, non-canonical candidate, trailing tool call, or envelope, length, hash, or receipt mismatch failed closed. These diagnostics motivated the gate but contribute no benchmark row. The complete v1.5.0 generation, review, aggregation, and independent trace-attestation stages all passed.

## Selection and interpretation limits

The winning weights and RRF constant were optimized on the same frozen 40-question benchmark reported here. The repeated rankings establish determinism and the gates establish non-regression on this target, but they do not create an independent holdout estimate. The winner may be partly adapted to this corpus and question set. Claims should therefore use “best observed on the frozen benchmark,” not “universally best.”

Likewise, this portfolio table is descriptive. The isolated Skill Arena comparison estimates the full definitive consultation capability—skill instructions, digest-bound bootstrap, profile-gated MCP transport, treatment runtime policy, and confirmed-output host publication—not the effect of skill text alone. Its knowledge-only and adaptive controls expose no Semantic OKF MCP tools, and its treatment exposes the bootstrap, inspect, coverage, prepare, and confirm workflow through five public tools. Only the completed, independently evaluated comparison may support that bounded causal claim.

## Final live answer-output result

Skill Arena compare `2026-07-15T15-24-19-159Z-compare`, Promptfoo evaluation `eval-RTd-2026-07-15T15:24:26`, completed 90/90 planned rows: three profiles, ten hard questions, and three repetitions per profile-question cell. Preparation `live-published-confirmed-01` produced 90 blinded review tasks and 90 completed reviews. The checked compact reports are [answer-output-comparison-final.json](answer-output-comparison-final.json), SHA-256 `6f48c963e8c1f85f9c1355a2d1d796ff8821239c05fb19ad72f78488a6acd5ae`, and [answer-output-comparison-final.md](answer-output-comparison-final.md), SHA-256 `2e37ec6602839d89ee27e1eb6fe6b8a8f1a8b3da24dbd5576ecaef08dad10178`.

| Profile | Strict full pass | Contract | Evidence validity | Grounding | Correctness | Completeness | Exact atomic IDs | Papers | Sources | Negatives | Exact negative IDs |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Knowledge-only control | 0.0% | 13.3% | 5.6% | 5.4% | 90.6% | 75.1% | 3.7% | 75.3% | 39.8% | 94.2% | 5.0% |
| Adaptive consult control | 3.3% | 23.3% | 82.6% | 82.5% | 83.0% | 72.7% | 55.3% | 76.0% | 74.8% | 86.7% | 78.3% |
| Definitive ensemble treatment | **53.3%** | **100.0%** | **100.0%** | **100.0%** | **96.7%** | **91.1%** | **86.0%** | **98.5%** | **98.5%** | **99.2%** | **100.0%** |

The strict full-pass rate is intentionally unforgiving: one answer passes only when every independent contract, mechanical evidence, and semantic review gate passes. The ensemble therefore passed all gates on 16/30 outputs, versus 1/30 for adaptive and 0/30 for knowledge-only, even though its individual metric means are much higher. A strict failure can still be a useful partially correct answer; it is not equivalent to zero on every component metric.

The ensemble's worst-question means, computed as the minimum of the ten three-repetition question means, were 100.0% for contract, evidence validity, and grounding; 87.5% for correctness; 79.2% for completeness; 66.7% for exact atomic IDs; 91.7% for required papers and sources; 91.7% for important negatives; and 100.0% for exact negative IDs. These bounds are more informative than the overall average alone because they show that the treatment's perfect mechanical guarantees persisted on every question while semantic and exact-coverage performance still varied.

| Matched ensemble minus adaptive delta | Strict full pass | Contract | Evidence validity | Grounding | Correctness | Completeness | Exact atomic IDs | Papers | Sources | Negatives | Exact negative IDs |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Ten matched questions | +50.0 pp | +76.7 pp | +17.4 pp | +17.5 pp | +13.7 pp | +18.4 pp | +30.7 pp | +22.5 pp | +23.8 pp | +12.5 pp | +21.7 pp |

Correctness, completeness, and important-negative coverage are model-judged under a fixed blinded rubric; they are strong comparative evidence, not mechanical truth. Contract, evidence validity, grounding, exact identities, papers, and sources are recomputed mechanically against the frozen final-03 bundle. Retrieval metrics remain separate: Recall@10, MRR@10, and nDCG@10 measure which papers were found and ordered, while this table measures the actual generated synthesis.

These are the final accepted answer-output results. The independent [MCP runtime trace attestation](skill-arena-mcp-runtime-attestation-final.json), SHA-256 `8085e666cced0d8b6d5a0b32095c29d836756bf67d1a515412c3ce7d9df5d77d`, binds all 90 published outputs to unique raw traces. The treatment passed 30/30 exact digest-bound bootstrap/terminal-confirm sequences with zero general-shell execution; the host gate corrected 16 free-form raw messages to the confirmed bytes, and three failed protocol attempts recovered only through fresh clean transactions. One adaptive-control q040 trace contains a superseded command start followed by an exact successful retry. The attestor records it transparently as one bounded control-runtime diagnostic and forbids the same condition in treatment traces.

Finally, the legacy route is not a `grep` evaluator. The separate [legacy `grep` / `rg` investigation](../semantic-okf-classical/legacy-grep-investigation.md) verified that the reader instructions offer optional `rg` fixed-string navigation, while `legacy_lexical` is an in-memory deterministic TF-IDF-like scorer with no `grep`, `rg`, or subprocess call. The legacy baseline remains unchanged.
