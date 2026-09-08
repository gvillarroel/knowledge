# Full-corpus EnterpriseRAG with Classical

This workflow measures the shipped Classical BM25 route against every document
in EnterpriseRAG-Bench release v1.0.0, then prepares the official 500-answer
evaluation. It is separate from the [985-document generator comparison](enterprise-generator-comparison.md).

## What is measured

- Corpus: 511,962 physical documents, 511,958 original IDs, and nine source types.
- Questions: all 500 public questions at upstream commit
  `d36685e273713975ee20299bbf1ab64165575b3c`.
- Retrieval: native Classical fielded BM25, k1 1.2, b 0.75, title weight 2,
  body weight 1, English stopwords, unigrams and adjacent bigrams, Top-10.
- Retrieval means: 470 questions with qrels. The other 30 remain part of the
  answer-quality evaluation and have unavailable retrieval metrics.
- Answering: the unchanged upstream baseline answer prompt, complete retrieved
  source text, GPT-5.4, medium reasoning, one answer per question.
- Judging: the pinned upstream `metrics_based_eval.py`, including citation
  stripping and its document-correction, gold-update, fact and correctness flow.
- Public comparison: Overall is the mean of each question's correctness times
  completeness. It is not nDCG or the product of separately averaged metrics.

The [official repository](https://github.com/onyx-dot-app/EnterpriseRAG-Bench)
defines the submission requirements. The [public leaderboard](https://huggingface.co/spaces/onyx-dot-app/EnterpriseRAG-Bench-Leaderboard)
requires a reproducible submission verified by its maintainers. A locally
calculated relative position does not add a system to that table.

## Execution boundary

The [bounded-memory adapter](../evaluations/enterprise-rag-bench/full_corpus_classical.py)
imports the frozen native source normalizer, tokenizer, record identities,
scalar BM25 scorer and tie ordering. It persists all terms and their postings
before seeing a question, with one global corpus-frequency/length contract.
The index is read-only during consultation. Every returned hit carries the
complete original body, exact native retrieval text, a physical source path,
and their hashes.

This is an execution adapter for Classical/BM25. It does not generate a complete
Semantic OKF/RDF expert or measure autonomous skill selection. The canonical
Classical builder and consultant are identical to the corresponding packages
embedded in G2. No skill content or ranking parameter changes in this run.

The adapter preserves all physical records with colliding upstream IDs. If a
retrieved or reference ID is ambiguous, answer preparation requires an explicit
canonical-citation proof. Every first occurrence must exactly match the pinned
upstream JSON path and complete export text. Later duplicate public IDs are
removed without reordering or refill. A first-occurrence mismatch fails. The
2026-09-08 run keeps its original physical rankings and binds this projection
separately; one question has nine unique answer-context documents.

Before full retrieval, require parity against the native scorer with ordinary
queries, repeated terms, length variation, Unicode, ties, absent terms, multiple
posting blocks, and empty token bags. The initial real-corpus parity check used
53 non-benchmark queries against the validated 985-document snapshot and found
exact ordered document and score equality.

## Reproduction

Keep the source archive, question bank, original JSON documents, indexes,
credentials, model responses and per-question scores under ignored local
directories. Pin the archive with the existing
[acquisition descriptor](../evaluations/enterprise-rag-bench/descriptor.json).
Freeze a source manifest with an explicit `body` field mapping, the Classical
plan, copied builder/consultant packages, execution adapter, and runtime before
index construction. The 2026-09-08 run binds these in its local
`index-binding.json` and uses the recorded offline Python 3.12 container.

The reviewed [frozen configuration](../evaluations/reports/enterprise-classical-full/reproduction.json)
contains the exact `manifest`, `plan` and `index_binding` objects. Materialize
them as `manifest.json`, `plan.json` and `index-binding.json` in a fresh ignored
input directory. Obtain the archive and question bank with the existing
acquisition workflow and verify their recorded hashes. Copy the canonical
builder and consultant and verify every file against `frozen_files` before
using the commands below. The configuration contains no source documents or
question-level data.

The frozen manifest retains the older descriptive title `EnterpriseRAG reduced
enterprise corpus`. That label does not select or exclude records. This run's
archive iterator consumes every document member, and its independent inventory
gate requires all 511,962 physical records and every source count before queries
can start. Preserve the frozen bytes when reproducing this measurement.

From a copied runtime with those explicit inputs:

```sh
python -B full_corpus_classical.py --consultant CONSULTANT build \
  --archive all_documents.zip --manifest manifest.json \
  --builder BUILDER --plan plan.json --output NEW_INDEX

python -B run_full_classical_retrieval.py \
  --index NEW_INDEX --consultant CONSULTANT --questions questions.jsonl \
  --binding index-binding.json --output NEW_RETRIEVAL_DIRECTORY
```

The index and result destinations must be absent. All 500 retrieval queries run
once. No scored outcome is repeated to improve a result.

The [official answer runner](../evaluations/enterprise-rag-bench/run_official_classical_answers.py)
expects a local work directory containing the pinned `upstream-code/`,
`upstream-revision.json`, `uuid_index.json`, `index-binding.json` and completed
`retrieval/` artifacts. It acquires original source JSON only for IDs needed by
the answer and judge stages. Its `seal` command binds all code, source files,
retrieval inputs, provider, model parameters and cost cap before answering.

```sh
python -B evaluations/enterprise-rag-bench/run_official_classical_answers.py \
  --work WORK acquire-documents

python -B evaluations/enterprise-rag-bench/run_official_classical_answers.py \
  --work WORK resolve-citations

python -B evaluations/enterprise-rag-bench/run_official_classical_answers.py \
  --work WORK seal --provider openai --budget-usd 50

python -B WORK/answer-tools/run_official_classical_answers.py --work WORK answer

python -B WORK/answer-tools/run_official_classical_answers.py \
  --work WORK judge --questions questions.jsonl
```

Use `LLM_API_KEY` for the explicit OpenAI provider. The optional
`--provider openrouter` uses `OPENROUTER_API_KEY`, the same GPT-5.4 model and
medium reasoning, and an OpenAI-only provider route with no fallback. Keep
credentials in the local environment, never in commands, reports or Git.
The declared cost cap is an execution ceiling, not an assertion that the whole
benchmark will fit within that amount. Native OpenAI costs use the published
token-rate estimate; OpenRouter costs use provider-reported usage.

The 2026-09-08 execution also supports `--provider github-copilot` through the
already configured local account. `ENTERPRISE_COPILOT_CONFIG` points to a private
JSON object declaring `authPath`, `modelsStorePath`, `piPackageRoot` and
`node_executable`, all inside the ignored work directory. Copy Pi 0.84.2 and its
dependencies plus Node 24.18.0 there, and retain `runtime-lock.json` with the
runtime file hashes and Node digest. The answer binding verifies that lock;
refreshable authentication content is excluded. The bridge captures the actual
provider response model, usage and request parameters. It does not enable Auto
selection or fall back to another model. Report its token-rate cost as an
OpenAI-equivalent estimate, separately from a Copilot invoice.

The generator process receives question-only rows and retrieved documents. The
judge starts only after the complete answer submission exists. It receives the
gold question bank in a separate phase. Preserve the upstream evaluator's
bounded parsing attempts, but never introduce HTTP retries, model substitution,
or a new semantic answer attempt after looking at a result.

## Completion and unavailable work

Verify the full corpus count, all 500 question identities, all 470 qrel-bearing
cases, original text fidelity, unchanged index hashes, finite metrics, complete
answer/judge coverage and absence of transport errors. Model failures must not
be converted to wrong answers or included in a public ranking. Keep the completed
retrieval result available even when answering is unavailable.

The 2026-09-08 availability checks found that GPT-5.4 was rejected by the Codex
ChatGPT route, and OpenRouter returned HTTP 402 because its account had no
available credit. A subsequent check of the already configured GitHub Copilot
account succeeded and returned `gpt-5.4-2026-03-05` at medium reasoning. Copilot
was selected explicitly before sealing the answer stage. Earlier checks did
not produce benchmark answers or judgments. The model and question workload
remain unchanged.

Copilot later returned HTTP 429 quota errors during the full answer run, so that
GPT-5.4 workload is incomplete and has no valid Overall score or public rank.
Its existing answer files and call receipts are preserved without semantic
retries. A separate user-requested Luna treatment uses all 500 inputs through
the available Codex connection.

## Internal Luna measurement

Use a fresh ignored work directory with the same immutable retrieval inputs,
source-document manifest, source bytes and upstream code. Separate all mutable
authentication, answer and judge files. `--provider openai-codex --model
gpt-5.6-luna` explicitly binds Luna for both generation and evaluation.
`ENTERPRISE_CODEX_CONFIG` has the same private runtime-path shape described
above; all paths must remain inside this new work directory.

```sh
python -B evaluations/enterprise-rag-bench/run_official_classical_answers.py \
  --work LUNA_WORK seal --provider openai-codex --model gpt-5.6-luna \
  --budget-usd 75 --question-concurrency 4 --model-concurrency 8

python -B LUNA_WORK/answer-tools/run_official_classical_answers.py --work LUNA_WORK answer

python -B LUNA_WORK/answer-tools/run_official_classical_answers.py \
  --work LUNA_WORK judge --questions questions.jsonl
```

This internal arm preserves the upstream user prompts and evaluation functions.
The Codex subscription protocol adds its default system instruction, `You are a
helpful assistant.`, and uses low text verbosity. It does not accept an API
output-token cap; the host rejects outputs above 8,192 tokens and reserves cost
at the model's full 128,000-token maximum. Rates come from the frozen runtime
catalog and are an accounting equivalent, not an actual Codex invoice.

The bridge checks the actual provider model, medium reasoning, completed output,
and exact agreement between final SSE message items and SDK text. It uses no
tools, model fallback, provider fallback, or HTTP retries. Both model identities
and the subscription protocol are visible in the binding and aggregate report.
Luna's answer-quality metrics are internal because its judge also uses Luna;
they cannot establish a public-table position or a controlled quality difference
from results judged by GPT-5.4.

## Recovering a completed reply after a local process-exit failure

The Luna judge encountered one local bridge exit error after the provider had
already returned a complete, verified response. The initial interrupted score
contains unavailable fallback judgments and is excluded from publication.
The [recovery runner](../evaluations/enterprise-rag-bench/recover_classical_judge.py)
first performs a network-free replay of literal requests and original document
permutations. It preserves separate occurrences of repeated requests and rejects
ambiguous response ownership. The 2026-09-08 audit recovered 233 complete
questions from all 1,449 original replies; 232 results match exactly and one
incorporates the reply misclassified by the host.

The continuation retains those question results and replays existing component
replies for the remaining questions before issuing any missing requests. It
does not regenerate answers, resample an available judgment or select a better
response. Its frozen binding covers the original receipt tree, offline audit,
recovery code, unchanged model parameters and remaining portion of the original
$75 token-rate-equivalent budget. Unissued document permutations use the
declared seed. The final aggregate must cover 500 first-evaluable question
records, consume every original response, pass the upstream aggregate checks,
and disclose the recovered process failure separately from unresolved errors.

The first live continuation retained 439 valid question evaluations before a
second local bridge failure left no decodable provider reply for one attempt.
Its response and usage are unavailable; it is not a negative semantic verdict.
A second offline audit exactly reproduced all 439 complete results from 3,634
available component responses, including the original recovered reply. The
second continuation retains those results and completes the remaining 61
questions. Its cache is checked against every original physical receipt by
digest and content before execution.

The bridge now atomically saves the completed provider reply to a fresh private
file before stdout delivery and shutdown. The host retains stdout, stderr and
the exit status separately and prefers the bound durable reply. Raw process
logs remain ignored. Account for the one historical attempt with unknown usage
as a separate uncertainty interval, with a conservative $0.2317224 token-rate
cost reserve; do not report its missing usage as zero. Publish all executed
phase time and every interrupted history and recovery binding.

The second continuation preserved three more component replies, then exposed
the repeated cause through its process log: the bridge rejected a completed
empty citation-stripping response. The official helper already handles this
case by falling back to the original answer. The host must deliver completed
empty judge replies to that unchanged helper instead of imposing a nonempty
answer-generation rule. It still rejects empty generated answers and truncated
or mismatched provider responses.

The final continuation restores all 3,637 available replies after a third
offline audit, retaining the same 439 complete evaluations. A captured reply
for the missing request confirms that SDK and stream text are both empty and
completed; the upstream helper applies its existing fallback. The two prior
attempts did not preserve a response or usage, so both remain explicitly
unevaluable, with a combined $0.4634448 conservative cost reserve. All 500
generated answers remain unchanged.

Run the relevant unit tests and the repository coverage gate before publishing
reviewed aggregates. Index the publication by dataset, Classical skill and CTA.
See [ADR 0128](../.specs/adr/0128-run-full-enterprise-classical-with-native-bm25-and-official-answer-scoring.md).
