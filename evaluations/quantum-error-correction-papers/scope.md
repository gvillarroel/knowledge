# Quantum Error Correction Paper Corpus Scope

## Purpose

Build a new, version-pinned arXiv corpus that tests whether the specialized
expert builder can reproduce the fixed-workload retrieval quality achieved on
GraphRAG and Astro without reusing either source collection.

## Competency questions

The corpus must support exact-evidence comparison across:

- surface-code architecture, noise bias, XZZX variants, distance scaling, and
  below-threshold experiments;
- belief-propagation decoder failures and neural, ordered-statistics,
  guided-decimation, and ensemble remedies;
- lifted-product, asymptotically good, and quantum Tanner qLDPC constructions;
  and
- binomial, cat, and GKP bosonic-code mechanisms and applications.

## Authority and limits

Only the fifteen exact versioned arXiv records and PDFs in
`paper-selection.json` are authoritative. PDF-page headings in the extracted
Markdown are evidence locators. The derived retrieval profile is
non-authoritative, uses every exposed qrel, and cannot establish unseen-query
generalization or promotion eligibility.
