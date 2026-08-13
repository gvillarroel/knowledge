---
adr: "0104"
title: "ADR 0104: Normalize Historical and Current arXiv Identities"
summary: "Treat both four- and five-digit new-style arXiv sequence numbers as canonical versioned paper identities across construction, consultation, and evaluation."
status: "Accepted"
date: "2026-08-13"
product: "knowledge"
owner: "Platform Architecture"
area: "Evidence Identity"
tags: [arxiv, identity, semantic-okf, evaluation]
---

# ADR 0104: Normalize Historical and Current arXiv Identities

## Status

Accepted.

## Context

Several canonical retrieval families validated only new-style arXiv IDs with a
five-digit sequence number. The frozen quantum-error-correction dataset also
contains `1208.0928v2`, whose historical sequence has four digits. Dataset
staging and the evaluator already treated that identifier as canonical, but
adaptive, classical, ensemble, and Graphify construction or consultation
could reject or fail to derive it. This split identity contract prevented the
same accepted dataset from running across every registered family.

The official
[arXiv identifier specification](https://info.arxiv.org/help/arxiv_identifier_for_services.html)
documents the January 2015 expansion from four to five sequence digits and
states that existing identifiers retain their original form.

The version suffix remains essential evidence identity. Accepting arbitrary
paper-like strings or unversioned IDs would weaken rather than fix the
contract.

## Decision

- Define a canonical new-style versioned arXiv identity as four year/month
  digits, a dot, four or five sequence digits, and a nonempty numeric version
  suffix, for example `1208.0928v2` or `2508.05095v3`.
- Permit the source-ID separator form `paper-YYYY-NNNNvN` or
  `paper-YYYY-NNNNNvN` only where an existing source-ID normalization step is
  already defined. Normalize that separator to the canonical dot.
- Apply the same width contract to the canonical adaptive, classical,
  ensemble, and Graphify builders and consultants, the direct classical
  generator, the universal generator's exact vendored copies, byte-identical
  Harbor consultation derivatives, and Harbor task identity normalization.
- Continue to require an exact full match for plan-declared identities. Do not
  accept prefixes, surrounding prose, missing versions, more than five
  sequence digits, or unrelated legacy identifier forms.
- Test both widths in builder, consultant, Graphify, ensemble, and dataset
  generation paths. Keep vendor-to-canonical byte-parity tests as the release
  binding.

## Consequences

Historical papers now retain one exact identity throughout build, retrieval,
citation, and grading, and every canonical family can consume the QEC dataset.
The accepted language remains deliberately narrow and versioned, so this does
not introduce heuristic paper matching.
