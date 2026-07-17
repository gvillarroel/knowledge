# Endocrine-Hygiene Evaluation Conclusions

## Conclusion

No executed consultation route is best on every metric in the accepted
`20260715-endocrine-builds-05` run. The results form a Pareto frontier:

- the evaluator-side legacy lexical baseline has the best overall MRR@10
  (`0.967`) and the lowest measured ranking time (`0.6 ms`);
- classical and adaptive BM25 have the best overall nDCG@10 (`0.953`);
- classical and adaptive association have the best overall Recall@10 (`99.5%`);
- embedding lexical is the only route with `100%` hard-question Recall@10; and
- every retained hit from every executable route passed exact ledger evidence
  validation (`100%`).

These are retrieval results, not answer-correctness percentages. The deterministic
hard-answer exercise is deliberately stricter: it requires exact independently
reviewed claim IDs, rather than treating any claim from the same passage as
interchangeable. Embedding lexical is the family winner for that exercise with
`9.0%` complete atomic reviewed-claim fidelity, `6.7%` important-negative fidelity,
`30.6%` authoritative-evidence completeness, and `40.8%` exact-required-claim
precision. Its hybrid route preserves the same `9.0%` atomic fidelity and raises
evidence completeness to `35.9%`, but misses all complete negative groups. None of
these numbers measures free-form prose quality or general semantic correctness.

Entity-graph and ensemble are N/A, not zero-scoring failures. Their unchanged closed
schemas cannot honestly represent BioC passage headings and PMCID identity,
respectively.

## Frozen evaluation contract

All routes use the same 15 papers, 93 reviewed claims, 30 questions, a raw candidate
pool of 100, and first-occurrence paper deduplication before metric cutoffs. The five
hard questions contain:

- 27 atomic answer claims and 15 important negatives;
- 60 question-specific evidence bindings across 34 distinct authoritative
  passages; and
- 128 exact reviewed-claim requirement occurrences across 37 distinct claim IDs.

The exact-claim requirements are joined to ground-truth evidence by
`(paper_id, evidence_text_sha256)`. This evidence-digest join ensures that each
required claim is supported by one of the evidence bindings declared for that
atomic answer or negative. Claim IDs remain necessary because a single passage can
support several distinct reviewed interpretations. All 60 evidence bindings also
have at least one reviewed-claim projection.

## How to read the retrieval metrics

- **Recall@k** is the average fraction of required papers found among the first *k*
  distinct papers. Recall@10 of `99.5%` means nearly all required papers were found;
  it does not mean `99.5%` of answers were correct.
- **MRR@10** scores only the rank of the first required paper. It can be high while
  additional papers needed for a synthesis are absent.
- **nDCG@10** rewards placing all required papers near the top and normalizes against
  an ideal ordering. It measures relevance ordering, not entailment.
- **Hard Recall@10** applies Recall@10 only to the five evidence-first questions that
  require joins, contrasts, exclusions, normalization, or causal-boundary analysis.
- **Evidence valid** is the fraction of retained hits whose source and record
  identity, canonical record digest, concept path, locator, retained text, and text
  digest independently match the authoritative Semantic OKF ledger. Relevance is a
  separate question.
- **Mean and p95 ms** are observed route runtimes in this recorded Windows run. They
  are not hardware-independent service-level guarantees.

## Build portability

Accepted run: `20260715-endocrine-builds-05`.

| Builder/consult family | Expected | Observed | Validation | Two-attempt result | Authoritative core SHA-256 |
| --- | --- | --- | --- | --- | --- |
| legacy | success | success | pass | identical logical tree | `a94509f0580c9cc2e7d917a1b07279adb8b8f5abf13a5b96c73b7f015f015262` |
| embeddings | success | success | pass | identical logical tree | `a94509f0580c9cc2e7d917a1b07279adb8b8f5abf13a5b96c73b7f015f015262` |
| classical | success | success | pass | identical logical tree | `a94509f0580c9cc2e7d917a1b07279adb8b8f5abf13a5b96c73b7f015f015262` |
| entity-graph | incompatible | expected incompatibility | N/A | same bounded diagnostic twice | N/A |
| adaptive | success | success | pass | identical logical tree | `a94509f0580c9cc2e7d917a1b07279adb8b8f5abf13a5b96c73b7f015f015262` |
| ensemble | incompatible | expected incompatibility | N/A | same bounded diagnostic twice | N/A |

All four compatible families also publish byte-identical `semantic/records.jsonl`
with SHA-256
`5bb09f5b4a7eb86c9f9e69c2e78c77d04a9530c5b305f3725c7ec3ef859913f5`.
The exact entity-graph diagnostic is `paper record
sources/markdown/PMC11764522 has no PDF page headings`. The exact ensemble diagnostic
is `ensemble component plan adaptive is invalid: paper identity mappings must
contain canonical versioned arXiv IDs`.

The preceding append-only run, `20260715-endocrine-builds-04`, is historical and
rejected. Its second embeddings attempt failed with a Windows missing staging-path
error, so its core-parity gate failed and no retrieval report was accepted. Run
`-05` rebuilt every family from the same frozen inputs and passed both attempts; it
supersedes `-04` without deleting it.

## Retrieval results: best route per family

The evaluator chooses a family winner by hard Recall@10, then overall nDCG@10, then
overall MRR@10. Latency is reported but is not a tie-breaker.

| Family | Status | Best route | Recall@10 overall | Recall@10 hard | MRR@10 | nDCG@10 | Evidence valid | Mean ms | p95 ms |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| legacy | pass | `legacy_lexical` | 98.9% | 97.1% | 0.967 | 0.947 | 100.0% | 0.6 | 0.8 |
| embeddings | pass | `lexical` | 98.7% | 100.0% | 0.933 | 0.928 | 100.0% | 33.4 | 36.0 |
| classical | pass | `bm25` | 98.9% | 97.1% | 0.950 | 0.953 | 100.0% | 19.0 | 20.6 |
| entity-graph | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| adaptive | pass | `bm25` | 98.9% | 97.1% | 0.950 | 0.953 | 100.0% | 24.0 | 26.3 |
| ensemble | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |

## Retrieval results: every route

| Family | Route | Status | Recall@1 | Recall@3 | Recall@5 | Recall@10 | Hard Recall@10 | MRR@10 | nDCG@10 | Evidence valid | Mean ms |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| legacy | `legacy_lexical` | pass | 63.4% | 80.0% | 91.1% | 98.9% | 97.1% | 0.967 | 0.947 | 100.0% | 0.6 |
| embeddings | `lexical` | pass | 60.9% | 81.2% | 87.4% | 98.7% | 100.0% | 0.933 | 0.928 | 100.0% | 33.4 |
| embeddings | `vector` | pass | 50.4% | 65.6% | 75.0% | 94.2% | 79.8% | 0.805 | 0.805 | 100.0% | 45.1 |
| embeddings | `hybrid` | pass | 54.4% | 69.9% | 82.5% | 95.9% | 94.3% | 0.875 | 0.858 | 100.0% | 92.1 |
| classical | `bm25` | pass | 62.2% | 84.0% | 92.9% | 98.9% | 97.1% | 0.950 | 0.953 | 100.0% | 19.0 |
| classical | `topic` | pass | 61.5% | 84.0% | 92.9% | 98.2% | 97.1% | 0.928 | 0.940 | 100.0% | 82.5 |
| classical | `association` | pass | 62.2% | 84.0% | 92.9% | 99.5% | 97.1% | 0.944 | 0.952 | 100.0% | 71.1 |
| classical | `fusion` | pass | 62.2% | 84.8% | 92.9% | 98.9% | 97.1% | 0.944 | 0.949 | 100.0% | 82.4 |
| entity-graph | `lexical` | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| entity-graph | `entity` | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| entity-graph | `traversal` | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| entity-graph | `fusion` | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| adaptive | `bm25` | pass | 62.2% | 84.0% | 92.9% | 98.9% | 97.1% | 0.950 | 0.953 | 100.0% | 24.0 |
| adaptive | `topic` | pass | 61.5% | 84.0% | 92.9% | 98.2% | 97.1% | 0.928 | 0.940 | 100.0% | 508.6 |
| adaptive | `association` | pass | 62.2% | 84.0% | 92.9% | 99.5% | 97.1% | 0.944 | 0.952 | 100.0% | 339.6 |
| adaptive | `fusion` | pass | 62.2% | 84.8% | 92.9% | 98.9% | 97.1% | 0.944 | 0.949 | 100.0% | 510.9 |
| adaptive | `adaptive` | pass | 62.2% | 84.8% | 92.9% | 98.9% | 97.1% | 0.944 | 0.949 | 100.0% | 1671.6 |
| ensemble | `quality` | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| ensemble | `fast` | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| ensemble | `robust` | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |

The non-runtime projection was identical across accepted detailed executions `v2`
and `v3`. Both have SHA-256
`5d210c8c5ee49fdb5943032bcab66b8723bee47dacbf1d75267367cbc68f5d1e`
after timing and floating runtime scores are excluded.

## Deterministic hard-answer metrics

For each compatible route, the ground-truth-blind generator selects at most 12
retrieved reviewed claims, takes one per paper before rank fill, and copies the
reviewed interpretations with exact evidence bindings. The family-level report picks
an answer route only after all routes have been scored, so these are development-set
diagnostics rather than untouched holdout estimates.

| Family | Route | Atomic claim fidelity | Required papers | Evidence completeness | Negative claim fidelity | Exact-claim precision | Grounding | Ledger evidence valid | Contract |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| legacy | `legacy_lexical` | 0.0% | 97.1% | 20.4% | 0.0% | 18.3% | 100.0% | 100.0% | 100.0% |
| embeddings | `lexical` | 9.0% | 87.6% | 30.6% | 6.7% | 40.8% | 100.0% | 100.0% | 100.0% |
| embeddings | `vector` | 4.0% | 79.8% | 30.1% | 0.0% | 32.7% | 100.0% | 100.0% | 100.0% |
| embeddings | `hybrid` | 9.0% | 97.1% | 35.9% | 0.0% | 40.3% | 100.0% | 100.0% | 100.0% |
| classical | `bm25` | 0.0% | 97.1% | 17.9% | 0.0% | 16.7% | 100.0% | 100.0% | 100.0% |
| classical | `topic` | 0.0% | 97.1% | 18.5% | 0.0% | 13.3% | 100.0% | 100.0% | 100.0% |
| classical | `association` | 0.0% | 97.1% | 19.0% | 0.0% | 15.0% | 100.0% | 100.0% | 100.0% |
| classical | `fusion` | 0.0% | 97.1% | 21.5% | 0.0% | 16.7% | 100.0% | 100.0% | 100.0% |
| adaptive | `bm25` | 0.0% | 97.1% | 17.9% | 0.0% | 16.7% | 100.0% | 100.0% | 100.0% |
| adaptive | `topic` | 0.0% | 97.1% | 18.5% | 0.0% | 13.3% | 100.0% | 100.0% | 100.0% |
| adaptive | `association` | 0.0% | 97.1% | 19.0% | 0.0% | 15.0% | 100.0% | 100.0% | 100.0% |
| adaptive | `fusion` | 0.0% | 97.1% | 21.5% | 0.0% | 16.7% | 100.0% | 100.0% | 100.0% |
| adaptive | `adaptive` | 0.0% | 97.1% | 21.5% | 0.0% | 16.7% | 100.0% | 100.0% | 100.0% |
| entity-graph | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| ensemble | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |

### What the hard-answer numbers mean

- **Atomic claim fidelity** requires every exact reviewed claim ID declared for one
  atomic answer group. Partial support receives no credit for that group.
- **Required papers** asks whether at least one selected claim came from each paper
  required by a question; it does not require the right claim from that paper.
- **Evidence completeness** is the average fraction of the question's exact
  authoritative evidence bindings covered by selected claims through the paper/text
  digest join.
- **Negative claim fidelity** requires every exact reviewed claim ID for an explicit
  caveat, exclusion, null result, or failure condition.
- **Exact-claim precision** is the fraction of selected claim IDs that appear in the
  question's independently declared exact requirements.
- **Grounding**, **ledger evidence valid**, and **contract** are structural gates.
  Their `100%` values confirm non-empty grounded outputs, valid ledger bindings, and
  the fixed response shape; they do not imply completeness or correctness.

## Insights

1. **There is no justified universal winner.** Legacy leads MRR, BM25 leads nDCG,
   association leads overall breadth, and embedding lexical leads hard Recall@10.
   Choosing a default requires an explicit priority rather than a single blended
   claim of superiority.
2. **Classical BM25 is the fastest packaged route tied for the top observed
   nDCG@10.** It combines `0.953` nDCG@10 with a `19.0 ms` mean. The `0.6 ms` legacy
   result is faster but belongs to an evaluator-side in-memory baseline, not a
   ranked search command in the legacy consult package.
3. **Fusion and orchestration do not dominate their components here.** Association
   improves overall Recall@10 to `99.5%`, while fusion falls back to `98.9%` and
   slightly lower ordering. Adaptive counterparts preserve the same quality with
   higher measured latency.
4. **The pinned embedding vector signal is not the leading retrieval signal on this
   corpus.** Vector hard Recall@10 is `79.8%`; embedding lexical reaches `100%`.
   This is corpus- and model-specific evidence, not a general rejection of semantic
   retrieval.
5. **Paper discovery is substantially easier than complete answer assembly.** Every
   compatible family reaches at least `87.6%` required-paper coverage in its selected
   answer route, yet complete atomic claim fidelity never exceeds `9.0%`.
6. **Exact claim identity materially changes the conclusion.** Passage-only scoring
   can credit the wrong interpretation when several claims share a passage. The
   37-claim, 128-binding requirement ledger removes that ambiguity.
7. **Portability gates prevented false success.** Preserving real PMCIDs and BioC
   locators exposes two schema assumptions. Fabricating PDF pages or arXiv IDs would
   make the table look fuller while invalidating provenance.

## Skill Arena hard5 paired diagnostic

The accepted live run is `eval-v8v-2026-07-15T23:49:40`. All `10/10` unique cells
completed with `0` runtime errors after being bound to the exact source config,
compiled config, immutable bundle, five prompt IDs, two profiles, variant, and model.

| Profile | Compound pass | Mean score | Mean latency |
| --- | ---: | ---: | ---: |
| `knowledge-only-control` | 0/5 | 0.657 | 72.6 s |
| `classical-cli-consult-treatment` | 0/5 | 0.543 | 117.6 s |

| Component gate | Control | Treatment | Treatment minus control |
| --- | ---: | ---: | ---: |
| Response format | 100% | 100% | 0% |
| Response contract | 100% | 80% | -20% |
| Evidence validity | 40% | 20% | -20% |
| Exact reviewed-claim fidelity | 100% | 100% | 0% |
| Atomic answer completeness | 20% | 0% | -20% |
| Important-negative coverage | 20% | 0% | -20% |
| Required-paper coverage | 80% | 80% | 0% |

Treatment minus control was `-0.114` mean score and `+45.0 s` mean latency. Both
profiles passed zero compound cells. On this run there is no evidence that adding
the classical consultation skill improved the measured outcome; the treatment was
descriptively slower and lower-scoring. Exact reviewed-claim fidelity passed in all
cells, but strict evidence validity, complete atomic claim sets, important negatives,
and, for one treatment cell, the response contract remained the binding failures.
That distinction matters: copying a reviewed interpretation exactly does not make
its locator, source path, concept path, or digest valid, and it does not make the
answer complete.

The design varies only the skill surface, uses a remote PI model with network access,
and uses no MCP. With five prompts and one request per cell, these findings are
descriptive only; they are neither a stable population effect nor an all-skills
portfolio ranking. See the
[compact accepted report](reports/skill-arena-hard5-diagnostic.md) and
[machine-readable result](reports/skill-arena-hard5-diagnostic.json) for
per-question cells and actual Q030 control/treatment answers.

## Limitations and unsupported claims

- The 30 questions and five hard-answer cases are a frozen development benchmark,
  not a representative sample of all biomedical questions.
- The deterministic direct comparison is an algorithm comparison, not a causal
  estimate of how a skill changes an agent. The separate Skill Arena diagnostic has
  a paired causal structure but only five prompts and one request per cell; its
  observed negative treatment delta is descriptive rather than a stable population
  estimate.
- The extractive packs use no language model and do not perform free-form synthesis.
  Their exact reviewed-claim fidelity is not a semantic answer-correctness score.
- The adaptive search build has an empty PMCID answer-identity map. Evaluator-side
  source-to-PMCID mapping does not prove that its packaged answer finalizer supports
  this corpus.
- N/A alternatives were not executed for retrieval and cannot be ranked below an
  executed route.
- Timing comes from one Windows/Python environment with a cached offline embedding
  model and should be reproduced before setting operational latency expectations.
- Product content, external sampling, biomonitoring, receptor assays, modeled risk,
  observational association, and health outcomes have different causal force.
  Retrieval relevance must not collapse them into a product-specific causal claim.

The machine-readable reports are authoritative for unrounded metrics, hashes,
routes, diagnostics, and answer bindings.
