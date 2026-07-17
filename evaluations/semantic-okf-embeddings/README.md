# Semantic OKF Embedding Evaluation

This evaluation compares the legacy record-level lexical route with the embedding-enabled
lexical, vector, and hybrid routes over the same pinned corpus. The requested corpus is the 15
paper Markdown files plus the 15 reviewed-claim JSONL files in `input-inventory.json`. The
historical vocabulary JSONL remains the required thirty-first authoritative build input and is
excluded only from the derived retrieval projection.

## Evidence-validity contract

`scripts/compare_retrieval.py` scores retrieval quality and evidence validity independently. It
loads `semantic/records.jsonl` once for the legacy bundle and once for the embedding bundle, then
retains the following values for every ranked hit:

- source ID and source path;
- chunk ID and ordinal when the route uses derived chunks;
- record ID and optional record digest;
- concept ID and concept path;
- exact evidence text and its SHA-256 during in-memory validation; and
- either a complete-record locator or an exact character range.

A hit is evidence-valid only when its concept path is a safe relative path below `concepts/`, the
concept file exists, one authoritative ledger record matches its source and record IDs, every
retained identity matches that record, the text hash is correct, and the locator resolves to the
exact retained text in the authoritative record body. Aggregate validity appears at
`routes[].evidence_validity`; per-query validity and complete retained hits appear at
`routes[].queries[].evidence_validity` and `routes[].queries[].hits`.

Fresh schema 1.2 reports use a compact hit representation. Raw evidence text is never serialized
into the report. Each emitted hit retains `text_sha256`, UTF-8 `text_bytes`, Unicode
`text_characters`, and the exact locator. An auditor can reconstruct the evidence text from the
authoritative ledger body and locator, verify both lengths, and recompute the retained hash. This
avoids repeating complete paper bodies for legacy record-level hits while preserving the evidence
audit.

The checked-in comparison reports were recomputed with this stronger contract on July 13, 2026.
Every retained hit in both the top-10 and top-100 reports passed the ledger, identity, text-hash,
concept-path, and exact-locator checks. The append-only local run manifest for that recomputation
is `results/runs/20260713-compact-final/run-manifest.json`.

## Append-only orchestration

Run the complete evaluation with a Python environment containing the package-local locked
requirements and the explicitly preloaded model revision:

```powershell
python evaluations/semantic-okf-embeddings/scripts/run_evaluation.py `
  --python-executable C:\path\to\venv\Scripts\python.exe
```

The orchestrator forces Hugging Face and Transformers offline mode. It never downloads weights.
The model declared in `retrieval-plan.json` must already be available to the selected Python
environment.

Every invocation creates a previously absent directory under
`evaluations/semantic-okf-embeddings/results/runs/`. The repository ignores `results`, so the
large bundles remain local. A caller-supplied `--run-id` is accepted only when that directory does
not exist. The orchestrator never deletes a prior run and refuses to replace any run directory,
command log, report, or manifest.

One complete run performs these stages:

1. validate the historical legacy bundle and both package runtimes;
2. build and independently validate two embedding-enabled bundles;
3. require byte-identical sorted file trees from those independent builds;
4. run the four-route comparison with candidate pools of 10 and 100; and
5. write `run-manifest.json` exactly once.

The manifest records portable command arguments, timings and exit codes, stdout/stderr hashes,
tool and requirement fingerprints, plan/inventory/question/manifest hashes, historical input
bundle hash, Python/platform/package identity, the exact embedding model and revision,
deterministic-rebuild hashes, and every final report hash. On a failed run, the script writes a
new `run-manifest.failed.json` instead. `--dry-run` creates an append-only planned manifest without
starting a build.

Fresh comparator reports use schema version 1.2. Input fingerprints contain portable POSIX paths,
byte counts, and SHA-256 values, including a fingerprint of the comparator itself.
