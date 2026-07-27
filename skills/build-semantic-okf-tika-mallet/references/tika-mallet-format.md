# Tika and MALLET Bundle Format

## Closed tree

A passing release adds two closed derived areas to the ordinary Semantic OKF core:

```text
BUNDLE/
  index.md
  concepts/
  semantic/
    records.jsonl
    semantic-plan.json
    source-manifest.json
    ontology.ttl
    data.ttl
    provenance.ttl
    shapes.ttl
    validation-report.ttl
    build-report.json
  tika/
    index.json
    documents.jsonl
    extracted/SOURCE_ID/*.md
    metadata/SOURCE_ID/*.json
  classical/
    index.json
    documents.jsonl
    lexicon.json
    associations.jsonl
    topics.json
    build-report.json
```

Unknown files in `tika/` or `classical/`, symbolic links, reparse points, unsafe
relative paths, or missing files are validation failures. Final publication uses
an atomic no-replace rename: a destination that exists or appears concurrently is
never overwritten.

## Tika receipt

`tika/index.json` persists the closed ingestion plan, plan digest, exact Tika and
Java toolchain identity, sorted JAR inventory, artifact hashes, inventory hashes,
and counts. `tika/documents.jsonl` binds each raw source locator and hash to one
canonical metadata object and one generated Markdown source.

Each raw file is first copied and hashed through one read into private storage; all
three Tika invocations consume that same snapshot. Each Markdown file contains
generated YAML provenance followed by the persisted body. By default, that body is
the exact normalized Tika Markdown output after the implicit and explicit Markdown
handlers agree. A source may instead declare
`body_mode: utf8-verbatim-tika-verified` when a pinned `.csv`, `.json`, `.jsonl`,
`.md`, `.markdown`, or `.txt` file is itself authoritative. That mode still runs
all three Tika calls and requires a Tika-detected textual media type, but persists
strict UTF-8 source text after line-ending normalization only. The receipt records
handler `utf8-verbatim-tika-metadata-verified-v1`, and the generated Semantic
source mapping records `body_normalization: line-endings-only`.

The verbatim mode rejects a UTF-8 BOM, malformed UTF-8, leading or trailing
whitespace, and non-textual types. Its trust boundary is narrow: Tika verifies the
media type and supplies metadata, while the raw text—not Tika's rendered
Markdown—is the authoritative body. Every frontmatter value, body hash, file hash,
metadata hash, source
partition, and authoritative ledger record must all agree. Raw binary inputs are
not copied into the bundle.

## Semantic OKF core

The fixed generated manifest maps every extraction to one `ExtractedDocument`.
SHACL checks all provenance properties. Tika documents and ledger records have
one-to-one path parity; the record body and source identity must match the receipt.
The normal core build report, source manifest, concepts, RDF graphs, and validation
report retain their standard authority.

## MALLET projection

`classical/index.json` binds the projection to the authoritative core tree, selected
source hashes, full closed retrieval plan, Java version, MALLET version, sorted JAR
inventory, and all artifact hashes.

- `documents.jsonl` stores exact record or character-range passages, term counts,
  topic weights, text hashes, and authoritative concept paths.
- `lexicon.json` stores tokenization, BM25 field statistics, and term frequencies.
- `associations.jsonl` stores bounded positive-PMI neighbors.
- `topics.json` stores MALLET topic terms, the deterministic strongest-topic mapping
  for each unigram, and the requested iteration count.
- `build-report.json` repeats the live bindings and must equal independent validation.

The validator rederives every passage and lexical artifact, reruns fixed-seed
one-thread MALLET in temporary storage, and compares canonical values exactly.

## Reproducibility check

Build unchanged plans and inputs into two absent directories. Compare a sorted list
of every relative file path and SHA-256 digest. A difference is a failed experiment,
even if both individual validators pass. Preserve both toolchain tree digests with
the result so later runtime changes cannot be mistaken for source changes.
