# Data Science, AI, and Machine Learning Book Corpus

This local-only corpus binds the two user-provided Google Drive folders to 38
English EPUB books:

| Partition | Drive folder | Books | Source bytes |
|---|---|---:|---:|
| `ds` | `1h_RJalpoYrGWIj-gWs4GHE5KzzoeMAH-` | 20 | 163,111,969 |
| `ai-ml` | `1XtIbBz96jm5cTJMrbxqcWtg7EJNa7Ntz` | 18 | 323,858,855 |
| Total | Two separate logical sources | 38 | 486,970,824 |

The tracked source catalog preserves Google Drive identities and metadata. The
tracked inventory binds every accepted EPUB to its exact byte size, SHA-256
digest, OPF metadata, and ordered readable spine. The two folder partitions
remain distinct sources in the Semantic OKF bundle; records are not fused.

## Privacy and repository boundary

The EPUB files and extracted full text are copyrighted private data. Keep them
only under the ignored `raw/` and `processed/` directories. Do not commit,
publish, attach, or copy their contents into questions, reports, or test
fixtures. Tests use synthetic EPUB files.

Tracked files contain only compact metadata, content hashes, deterministic
processing code, paraphrased benchmark questions, and the Semantic OKF
structure. This corpus remains outside the public Harbor dataset registry
because the source material and full per-question rankings are private.

## Local layout

Stage exact source files at:

```text
raw/epub/
  ai-ml/*.epub
  ds/*.epub
```

The archive copies under `raw/archives/` are optional provenance aids. The
preparation command writes one deterministic Markdown record per EPUB plus a
receipt under `processed/`. A locally built Semantic OKF snapshot belongs at
`processed/semantic-okf/`.

## Reproduce and validate

Run these commands from the repository root after staging all 38 exact EPUB
files:

```powershell
python evaluations/data-science-ai-ml-books/scripts/prepare_dataset.py inventory --check
python evaluations/data-science-ai-ml-books/scripts/prepare_dataset.py prepare --replace
python evaluations/data-science-ai-ml-books/scripts/prepare_dataset.py check
```

`prepare --replace` builds a complete candidate before atomically replacing an
existing extracted corpus. If source membership, Drive metadata, EPUB package
structure, language, byte sizes, or hashes drift, validation fails closed.

Build and validate the local Semantic OKF snapshot after preparing Markdown:

```powershell
python skills/build-semantic-okf/scripts/build_semantic_okf.py `
  evaluations/data-science-ai-ml-books/manifest.json `
  evaluations/data-science-ai-ml-books/processed/semantic-okf `
  --output-format json
python skills/build-semantic-okf/scripts/validate_okf_bundle.py `
  evaluations/data-science-ai-ml-books/processed/semantic-okf
python skills/build-semantic-okf/scripts/validate_semantic_okf.py `
  evaluations/data-science-ai-ml-books/processed/semantic-okf `
  --output-format json
python evaluations/data-science-ai-ml-books/scripts/prepare_dataset.py check
```

The final extraction check intentionally ignores only the independently
validated `processed/semantic-okf/` subtree. It still requires every Markdown
record and the preparation receipt to be byte-identical to a fresh rebuild.

Confirm the privacy boundary before committing:

```powershell
git check-ignore -v evaluations/data-science-ai-ml-books/raw/archives/ds.zip
git check-ignore -v evaluations/data-science-ai-ml-books/processed/receipt.json
```

See [`scope.md`](scope.md) for competency questions and
[ADR 0089](../../.specs/adr/0089-register-private-drive-epub-corpus.md) for the
durable storage and registration decision.

## Retrieval benchmark

[`retrieval-questions.jsonl`](benchmark/retrieval-questions.jsonl) freezes 30
development and 10 hard cross-book questions. Its reviewed, non-exhaustive
focus sets cover all 38 authoritative book records. The questions are
paraphrased and contain no source excerpts.

[`evaluation-contract.json`](benchmark/evaluation-contract.json) fixes the
Top-10 cutoff, three repetitions, qrel-blind route policy, metric set, and
privacy boundary before results are ranked. The exhaustive comparison covers
18 compatible routes across all eight registered retrieval families. See the
[shared workflow](../private-book-strategy-comparison/README.md) and the
[aggregate comparison](reports/all-route-comparison.md). It evaluates
retrieval, not generated-answer quality.
