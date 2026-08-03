# ADR 0089: Register a Private Drive EPUB Corpus Without Publishing Its Text

- Status: Accepted
- Date: 2026-07-30

## Context

The user supplied two private Google Drive folders containing 38 commercial
English EPUB books about data science, data engineering, machine learning, and
AI. Reproducible local knowledge construction requires exact source identity,
content binding, deterministic text extraction, and source-level evidence
identity. Committing either the EPUB bytes or extracted prose would
redistribute copyrighted material.

The canonical Semantic OKF Harbor dataset registry also requires a reviewed
question set, evidence-bound ground truth, cohorts, and an evaluation policy.
Those evaluation assets do not exist for this corpus, so registering it as a
benchmark would misrepresent its current readiness.

## Decision

Create `data-science-ai-ml-books-38` under
`evaluations/data-science-ai-ml-books/` as a private, content-bound knowledge
corpus.

- Keep source EPUBs, archives, extracted Markdown, and Semantic OKF snapshots
  under ignored `raw/` and `processed/` paths.
- Track the closed Drive folder and file catalog, a SHA-256 inventory of all 38
  source files, a deterministic standard-library EPUB extractor, a Semantic
  OKF manifest, corpus scope, and source-combination policy.
- Preserve `ds` and `ai-ml` as separate logical sources in one bundle. Retain
  source and record identity and do not fuse records.
- Require portable archive paths, an EPUB-compliant first uncompressed
  `mimetype` member, bounded control and spine documents, a unique readable
  spine, valid OPF metadata, English language, exact catalog membership, byte
  sizes, and hashes.
- Publish extracted Markdown atomically and verify it by rebuilding a
  byte-identical candidate.
- Do not add the corpus to the canonical Harbor evaluation registry until a
  separate reviewed evaluation contract is authored and passes the registry's
  leakage and quality gates.

## Consequences

An authorized local user can reproduce the same 38-book corpus and validate
that its source and extracted bytes have not drifted. A clean checkout retains
the workflow and compact provenance but cannot reconstruct or expose protected
book text without separately authorized Drive access.

The corpus can support local evidence-grounded consultation and a validated
Semantic OKF snapshot now. It cannot support comparative benchmark claims,
model ranking, or skill promotion until the missing evaluation contract is
created under a separate decision.
