# Semantic OKF Classical Text Evaluation

This evaluation adds an isolated, model-free Semantic OKF generation without modifying the legacy or embedding packages. It compares eight retrieval routes over the same pinned authoritative corpus and evaluates grounded answer behavior on ten new evidence-first synthesis questions.

## Scope and authority

The authoritative input is exactly:

- 15 pinned paper Markdown files;
- 15 reviewed-claim JSONL files; and
- the separately declared analysis vocabulary required by the Semantic OKF core build.

`input-inventory.json` in the embedding evaluation fixes the 30 paper/claim files. The historical `evaluations/graphrag-cross-paper/manifest.json` fixes all 31 build sources. The resulting authoritative core has 874 records and logical tree SHA-256 `331af2f1064463484f64dfaa58bc17d6c6b2f75ef3fca9d371473450deb84424`.

Everything below `classical/` is derived and non-authoritative. The projection is closed, hash-bound, deterministic, and reproducible offline. It never changes `semantic/records.jsonl`, concept Markdown, RDF, source identity, or source content.

## Classical alternatives

The standalone pair is:

- `skills/build-semantic-okf-classical`
- `skills/consult-semantic-okf-classical`

The builder persists exact authoritative page/record passages and these signals:

- unigram and bigram Bag of Words counts;
- field-aware Okapi BM25 corpus statistics;
- positive-PMI term associations from deterministic co-occurrence windows;
- deterministic weighted label-propagation topic communities; and
- document-topic weights used by topic-aware diversification.

The consultant exposes four independent routes:

- `bm25`: persisted field-aware BM25;
- `topic`: topic expansion, topic similarity, and topic/source-aware MMR;
- `association`: two-step PPMI term-graph expansion and source-aware MMR; and
- `fusion`: reciprocal-rank fusion of BM25, topic, and association rankings.

Every hit retains an exact concept path, source/record identity, authoritative text hash, and a record or character-range locator. Retrieval scores and topics remain discovery signals, never factual evidence.

## Hard-question construction

The original 30 questions are preserved byte-for-byte at the start of `retrieval-questions.jsonl`. Questions `q031` through `q040` were written only after reviewing and hashing their evidence. Each row in `hard-ground-truth.jsonl` contains:

- atomic answer claims and important negatives;
- required paper and source identities;
- exact claim JSONL line/character locators and record hashes;
- exact paper page locators, character ranges, and page-text hashes;
- explicit join, contrast, conditional, classification, or policy derivations; and
- acceptable answer variants.

The task questions contain none of those hidden answers. Regenerate and independently verify them with:

```powershell
python evaluations/semantic-okf-classical/scripts/generate_hard_questions.py --check
python evaluations/semantic-okf-classical/scripts/validate_hard_ground_truth.py
```

## Rebuilding the classical bundle

The following produces two independently validated builds from the pinned manifest:

```powershell
python skills/build-semantic-okf-classical/scripts/build_semantic_okf_classical.py `
  evaluations/graphrag-cross-paper/manifest.json `
  evaluations/semantic-okf-classical/classical-plan.json `
  tmp/classical-a --output-format json

python skills/build-semantic-okf-classical/scripts/validate_semantic_okf_classical.py `
  tmp/classical-a --output-format json

python skills/build-semantic-okf-classical/scripts/build_semantic_okf_classical.py `
  evaluations/graphrag-cross-paper/manifest.json `
  evaluations/semantic-okf-classical/classical-plan.json `
  tmp/classical-b --output-format json

python skills/build-semantic-okf-classical/scripts/validate_semantic_okf_classical.py `
  tmp/classical-b --output-format json
```

The accepted independent builds were byte-identical across all 890 files. The canonical sorted path-and-byte tree hash was `a22947f9ef491369d2785cb85973ff4dd1c0278cfae043b972362a93c866c700`; the authoritative logical core hash was the value above. The derived projection contains 1,135 documents, 96,799 lexical terms, 3,000 association-term rows, and 16 topics.

## Append-only run inputs

Large bundles and raw runs are stored below `evaluations/semantic-okf-classical/results/runs/`, which is ignored. A new run is atomically prepared only at a previously absent ID:

```powershell
python evaluations/semantic-okf-classical/scripts/prepare_evaluation_run.py prepare `
  --run-id MY-UNIQUE-RUN `
  --output-root evaluations/semantic-okf-classical/results/runs `
  --workspace-template evaluations/graphrag-cross-paper/fixtures/workspaces/base `
  --legacy-bundle evaluations/graphrag-cross-paper/bundle `
  --embedding-bundle C:\path\to\validated-embedding-bundle `
  --classical-bundle tmp/classical-a
```

The preparer refuses an existing run ID, validates every core/derived report, independently fingerprints all files, requires three-way authoritative-core parity, and publishes from a private staging directory. `audit-existing` can append a missing input manifest to a manually staged run, but refuses to replace one.

The completed local run is `20260714-classical-final-01`. Its ignored input manifest fixes all three workspaces and verifies core parity before either benchmark.

## Retrieval comparison

`scripts/compare_retrieval.py` extends the embedding evaluator's evidence-valid schema 1.2 contract as schema 1.3. It runs:

1. legacy in-memory TF-IDF-like record ranking;
2. embedding-index lexical retrieval;
3. exact vector retrieval;
4. embedding hybrid retrieval;
5. classical BM25;
6. classical topic retrieval;
7. classical PPMI association retrieval; and
8. classical fusion.

Both top-10 and pool-100 runs process all 40 questions. The pool-100 run is important for chunk-based routes because repeated chunks from one paper are deduplicated before paper-level top-10 scoring. The compact checked outputs are `retrieval-summary.json` and `retrieval-summary.md`; the raw reports remain append-only and ignored.

## Grounded answers and causal controls

`scripts/generate_skill_arena_configs.py` creates three separate paired comparisons instead of an all-skills portfolio:

- legacy bundle: knowledge-only control vs `consult-semantic-okf`;
- embedding bundle: knowledge-only control vs `consult-semantic-okf-embeddings`; and
- classical bundle: knowledge-only control vs `consult-semantic-okf-classical`.

Within each pair, the questions, bundle, model route, sandbox, and concurrency are identical. Only the declared consult skill changes. Prompts contain the real question and observable JSON/evidence contract; hidden assertions contain the reviewed paper/claim identities. Generate and validate with:

```powershell
python evaluations/semantic-okf-classical/scripts/generate_skill_arena_configs.py `
  --ground-truth evaluations/semantic-okf-classical/hard-ground-truth.jsonl `
  --bundle tmp/classical-a `
  --run-id MY-UNIQUE-RUN `
  --output-dir evaluations/semantic-okf-classical/skill-arena

$ValidateDesign = Join-Path $HOME '.agents/skills/skill-arena-config-author/scripts/validate-evaluation-design.js'
node $ValidateDesign `
  evaluations/semantic-okf-classical/skill-arena/classical-hard10.yaml `
  --coverage evaluations/semantic-okf-classical/skill-arena/prompt-coverage.json

skill-arena val-conf evaluations/semantic-okf-classical/skill-arena/classical-hard10.yaml
skill-arena evaluate evaluations/semantic-okf-classical/skill-arena/classical-hard10.yaml --dry-run
skill-arena evaluate evaluations/semantic-okf-classical/skill-arena/classical-hard10.yaml
```

The answer report separates strict all-contract success, response-contract compliance, evidence validity, grounding, exact atomic-identity coverage, required paper/source coverage, important-negative coverage, and blinded semantic correctness/completeness. Raw agent outputs stay in ignored Skill Arena results; the compact checked summary contains no copied paper text.

The three live comparisons produced 60 usable answers: ten control and ten treatment answers for each method. Four initial cells timed out at the model boundary (one legacy treatment, two embedding controls, and one embedding treatment). Narrow retry configs reran only the affected questions. `scripts/merge_skill_arena_retries.py` then replaced only missing provider/question cells in new result copies, recording primary/retry hashes and row-level provenance; it never altered a raw run.

`scripts/review_grounded_answers.py` shuffled and blinded the 60 answers behind opaque IDs. A fixed-rubric reviewer saw the hidden atomic ground truth and authoritative interpretations of cited reviewed records, but not method or treatment labels. `scripts/evaluate_grounded_answers.py` independently revalidated every cited claim, concept path, source path, paper identity, page locator, and citation binding. The checked outputs are `grounded-answer-summary.json` and `grounded-answer-summary.md`.

## Observed results

On the ten hard questions, classical fusion achieved paper recall@10 of **95.5%**, MRR@10 of **95.0%**, and nDCG@10 of **85.0%** from the direct top-10 candidate run. Legacy lexical recall@10 was 80.7%; embedding lexical, vector, and hybrid were 73.5%, 61.0%, and 65.2%. With a 100-candidate chunk pool before paper deduplication, those embedding routes rose to 93.0%, 78.0%, and 90.5%, while classical fusion remained 95.5%. This pool sensitivity is why both candidate budgets are reported.

Retrieval quality did not automatically become answer quality. Relative to each same-bundle control:

- the embedding consult treatment improved independently validated evidence validity by 12.7 points, grounding by 12.4, semantic completeness by 2.0, and claim correctness by 1.0;
- the classical consult treatment improved required-paper coverage by 7.0 points and response-contract compliance by 10.0, but changed completeness by 0.0 and reduced evidence validity by 3.5 and correctness by 4.0; and
- the legacy consult treatment improved evidence validity by 1.7 points but reduced completeness by 8.2 and correctness by 5.2; one treatment answer abstained and therefore scored zero against an answerable case.

These are ten-question, single-model paired estimates, not confidence-bounded population effects. The semantic reviewer used the same model family as the answer generator but had no tools, skill, method label, or prior answer context. Strict Skill Arena full-pass remained 0% because its assertion deliberately requires the curated evidence identities and exact literal path/locator forms; the independent scorer separately accepts authoritative alternative reviewed evidence and normalized `knowledge/` prefixes or integer page locators. The answer-level treatments evaluate the three consultant packages, not each low-level retrieval route in isolation; route-level causal claims are therefore limited to the 40-question retrieval benchmark.

## Legacy `rg` note

See `legacy-grep-investigation.md`. In brief, the legacy reader documentation offers ripgrep for one exact-phrase workflow, while the frozen `legacy_lexical` evaluator is an in-memory TF-IDF-like algorithm and executes neither `rg` nor `grep`. The baseline was not altered to change that finding.
