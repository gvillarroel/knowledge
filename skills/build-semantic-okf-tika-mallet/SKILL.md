---
name: build-semantic-okf-tika-mallet
description: Build and independently validate an atomic Semantic OKF snapshot from local PDF, Office, archive, media, or other files extracted by Apache Tika 4.0.0-beta-1, then add a non-authoritative Java MALLET 2.1.0 topic, BM25, PPMI, and fusion retrieval projection. Use when Codex needs to experiment with Tika's new default Markdown output, test heterogeneous document ingestion, or compare fixed-seed MALLET topics while preserving OKF authority and provenance. This standalone experimental skill builds only; it never consults or answers from published knowledge.
---

# Build Semantic OKF with Tika and MALLET

Build one format-diverse Semantic OKF release whose extraction receipts and topic
projection can be reproduced independently. Treat Tika `4.0.0-beta-1` as preview
software and MALLET topics as discovery signals, never ontology truth.

## Standalone and authority boundary

- Use only this directory's instructions, references, scripts, and requirements.
- Treat both plans, local sources, three runtime paths, and the absent destination as
  explicit user inputs.
- Do not import a sibling skill, repository helper, evaluation fixture, or root file.
- Do not download Java, Tika, MALLET, models, or source documents.
- Own extraction, Semantic OKF materialization, MALLET derivation, validation, and
  one final atomic publication.
- Do not search, answer, cite, or synthesize from the published bundle.
- Keep `concepts/`, `semantic/records.jsonl`, and purpose-selected RDF graphs
  authoritative. Keep Tika metadata as provenance and `classical/` as replaceable
  discovery data.

## Read the relevant references

- Always read [tika-mallet-contract.md](references/tika-mallet-contract.md) before
  writing plans or running external tools.
- Read [python-runtime.md](references/python-runtime.md) before installing or
  preflighting the isolated environment.
- Read [tika-mallet-format.md](references/tika-mallet-format.md) before diagnosing a
  receipt, projection, reproducibility failure, or tampered bundle.
- Read [source-combination.md](references/source-combination.md) when combining
  physical sources or defining evidence identity.
- Read [manifest.md](references/manifest.md) and
  [coherence-contract.md](references/coherence-contract.md) only when changing the
  fixed generated `ExtractedDocument` ontology or Semantic OKF mappings.

## Workflow

1. Confirm that the experiment may use preview Tika `4.0.0-beta-1`. Inventory exact
   local files and assign stable source IDs and concept types.
2. Write a closed ingestion plan with plan-relative glob paths, size and timeout
   limits, and `verify_default_markdown: true`. The default body mode is
   Tika-produced Markdown. Use
   `body_mode: utf8-verbatim-tika-verified` only for a pinned UTF-8 textual
   source whose exact bytes are already the authoritative representation.
3. Write a closed retrieval plan. Select every intended source ID explicitly and pin
   tokenizer, BM25, PPMI, fixed-seed one-thread MALLET, expansion, and reranking.
4. Establish the CPython 3.12 dependency contract. If dependency installation is
   allowed, create one isolated environment and install only
   `scripts/requirements.txt`. If downloads or installation are forbidden, verify
   that the current interpreter already provides every pinned requirement and use
   it directly; never create an empty virtual environment or invoke an installer.
   Preflight the explicit Java, Tika, and MALLET paths.
5. Build into an absent output path. Each raw file is read once into a private,
   hash-bound snapshot before Tika opens it. Any extraction, schema, SHACL, hash,
   MALLET, path-safety, or validation failure must leave no destination.
6. Run the independent published-bundle validator with the same hash-bound Java and
   MALLET runtime.
7. Repeat the full build into a second absent path and require identical sorted
   relative-path and SHA-256 inventories.
8. Open at least one generated Markdown source per physical format and confirm that
   its ledger body, media type, raw hash, metadata hash, and concept path agree.

## Build and validate

Resolve the three runtime inputs before creating the destination. When
`SEMANTIC_OKF_JAVA`, `SEMANTIC_OKF_TIKA_HOME`, and
`SEMANTIC_OKF_MALLET_HOME` are present, treat their values as the caller's exact
closed runtime contract: use them directly and do not scan `/`, search the PATH,
or substitute `/usr/bin/java`. The Java argument must name the regular canonical
JDK file, never a symlink. If any variable is absent, require the caller's explicit
absolute path instead of guessing or downloading a replacement.

Honor the caller's dependency boundary before preflight. When installation is
allowed, create one isolated build environment and install
`scripts/requirements.txt`. When the caller forbids downloads or dependency
installation, use the supplied CPython 3.12 interpreter directly after verifying
the installed distributions and versions against every non-comment requirement in
`scripts/requirements.txt`; fail closed on any missing or mismatched dependency.
Do not create a virtual environment, run `pip install`, or access the network in
that qualified-runtime branch.

Run `runtime_smoke.py` exactly once before any build. Require every output path to
be absent; never delete or overwrite a destination to recover from a preflight or
build error. A failed private candidate is the builder's responsibility to clean
up. When two reproducibility destinations are requested, use this exact sequence:
one runtime smoke, first build, first independent validation, second build, second
independent validation, then one sorted relative-path/SHA-256 inventory comparison.
Do not run script `--help` probes or repeat a successful build or validation.

Run from this skill directory, or prefix each script with the copied skill root:

```bash
python scripts/runtime_smoke.py --java "$SEMANTIC_OKF_JAVA" --tika-home "$SEMANTIC_OKF_TIKA_HOME" --mallet-home "$SEMANTIC_OKF_MALLET_HOME"
python scripts/build_semantic_okf_tika_mallet.py ingestion-plan.json retrieval-plan.json OUTPUT --java "$SEMANTIC_OKF_JAVA" --tika-home "$SEMANTIC_OKF_TIKA_HOME" --mallet-home "$SEMANTIC_OKF_MALLET_HOME" --concept-layout source-packed-v1 --output-format json
python scripts/validate_semantic_okf_tika_mallet.py OUTPUT --java "$SEMANTIC_OKF_JAVA" --mallet-home "$SEMANTIC_OKF_MALLET_HOME" --output-format json
```

The destination must not exist. The Tika application directory must contain
`tika-app-4.0.0-beta-1.jar`; the MALLET directory must contain
`lib/mallet-2.1.0.jar`; Java must be version 17 or later.
The recommended source-packed layout affects only repeated structured CSV,
JSON, or RDF records. Tika-extracted Markdown documents remain one file per
source, and all ledger identities, exact bodies, extraction receipts, locators,
and MALLET ranking content remain unchanged. Core-bound indexes and reports are
regenerated for the new physical tree.

The builder verifies that Tika's no-flag output equals explicit `--md`, stores
canonical `--json` metadata, generates the fixed OKF ontology and SHACL rules,
builds the authoritative core, and runs MALLET with one thread and the exact seed.
For an explicitly declared `utf8-verbatim-tika-verified` source, it still performs
both Markdown calls and the metadata call, requires Tika to detect a textual media
type, and then stores strict UTF-8 source text with only CRLF/CR converted to LF.
It rejects a BOM, invalid UTF-8, leading or trailing whitespace, and non-textual
suffixes or media types. This mode verifies Tika metadata and type; it does not
claim that Tika produced the authoritative body.
All files are built privately and published together with one atomic no-replace
rename; a destination that appears concurrently is a hard failure.

## Completion gate

Before delivery, confirm:

- runtime preflight, build, core validation, Tika validation, and independent MALLET
  rederivation all pass;
- every requested source matched at least one regular non-symlink file and no source
  was selected implicitly;
- the default and explicit Tika Markdown handlers agreed for every input, and any
  verbatim textual body was explicitly declared and passed strict UTF-8 and
  Tika-detected-media checks;
- raw inputs, metadata, Markdown bodies, generated concepts, ledger records, SHACL,
  RDF, and build reports are hash-bound and mutually coherent;
- MALLET created every required output, probability and vocabulary checks passed,
  and topics remain marked non-authoritative;
- failure-path tests leave no destination or candidate tree;
- two clean builds are byte-identical; and
- the experiment is not represented as production approval of the Tika beta.
