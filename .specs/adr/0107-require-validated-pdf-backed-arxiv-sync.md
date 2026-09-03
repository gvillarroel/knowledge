---
adr: "0107"
title: "ADR 0107: Require Validated PDF-Backed arXiv Synchronization"
summary: "Treat an arXiv sync as successful only after the official PDF is validated and extracted into page-addressable Markdown."
status: "Accepted"
date: "2026-08-14"
product: "knowledge"
owner: "Platform Architecture"
area: "Research Acquisition"
tags: [arxiv, pdf, acquisition, extraction, provenance]
---

# ADR 0107: Require Validated PDF-Backed arXiv Synchronization

## Status

Accepted.

## Context

The arXiv adapter queried the Atom API, with the official abstract page as a
metadata fallback, and then wrote only the abstract to `paper.md`. It never
requested the PDF exposed by that metadata. A synchronization could therefore
report success while materializing approximately the same content as an arXiv
search preview rather than the paper itself.

This repository's evaluated paper corpora already use a stronger convention:
download exact-version PDF bytes, validate the PDF signature, extract text with
pypdf, retain page boundaries as `## PDF page N`, and bind the projection to the
downloaded bytes with SHA-256. The normal CLI must not silently provide a weaker
paper-acquisition contract.

## Decision

- After acquiring metadata, every arXiv sync must download the corresponding
  official PDF. Prefer `arxiv.org` and retry through `export.arxiv.org` when the
  primary endpoint fails or returns a non-PDF body.
- Accept a download only after successful HTTP handling, a `%PDF-` signature, a
  100 MiB maximum, successful pypdf parsing, at least one page, and at least 256
  extracted non-whitespace characters across the document.
- Reject metadata that resolves an explicitly requested version to a different
  arXiv version. When an unversioned registration receives a versioned API
  entry, record the resolved version in the synchronized document and source
  statistics.
- Render the abstract as metadata context and the complete extracted paper as
  page-addressable Markdown. Record the PDF URL, SHA-256, byte count, page
  count, nonempty-page count, extracted-character count, and pypdf version.
- Keep the processed-source layout from ADR 0002: persist `paper.md` and
  `source-metadata.yaml`, not an additional PDF or transient extraction tree.
  The digest binds the Markdown projection to the downloaded bytes.
- Perform download, validation, and extraction before replacing source output.
  A blocked HTML response, corrupt PDF, oversized file, extraction failure, or
  suspiciously empty result must fail the sync and preserve the last successful
  document.
- Make pypdf a base runtime dependency because arXiv is a base source adapter;
  a successful installation must be able to fulfill the advertised sync
  behavior without an undeclared optional package.

## Consequences

Positive:

- a successful arXiv sync now means the paper body, rather than only its
  abstract, is locally searchable and exportable;
- page headings provide stable evidence locators for retrieval and citation;
- PDF digests and extraction statistics expose incomplete or drifting inputs;
- HTML rate-limit and anti-bot responses cannot be mistaken for papers;
- failed refreshes do not destroy the last known-good paper projection.

Negative:

- synchronization downloads and parses substantially more data;
- pypdf becomes part of the base installation;
- image-only or otherwise non-extractable papers fail closed until a separately
  reviewed OCR workflow is introduced;
- the processed source does not retain the PDF bytes, so byte-for-byte offline
  regeneration requires reacquisition of the digest-bound upstream PDF.
