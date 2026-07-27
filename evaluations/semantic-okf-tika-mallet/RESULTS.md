# Tika and MALLET Real-Tool Results

The real-tool smoke passed on Windows on 2026-07-22 with Eclipse Temurin
`17.0.19+10`, the official Apache Tika `4.0.0-beta-1` application ZIP, and the
official MALLET `2.1.0` binary ZIP. The machine-readable receipt is
[`reports/real-tool-smoke-20260722-hardened.json`](reports/real-tool-smoke-20260722-hardened.json).
The final pair-level run used an isolated CPython `3.12.13` environment installed
from the package-local lock. The earlier receipt remains preserved as historical
pre-hardening evidence.

## Result

- Tika's default output matched explicit `--md` for both the PDF and XLSX inputs.
- Tika `--json` metadata, raw input hashes, generated Markdown, and Semantic OKF
  ledger attributes had exact hash parity.
- The generated `ExtractedDocument` ontology, RDF, provenance, and SHACL validation
  passed.
- Java MALLET trained two topics with seed `42`, one thread, and 100 iterations.
- Independent builder validation and consultant deep retraining passed.
- A fusion query returned both exact authoritative record locators.
- Two clean builds contained the same 24 files and had the same canonical inventory
  digest: `fd566c7b53aac3a1680fe6de11bc7908767ba8d943ae181728444e299555c911`.
- The builder-only runner independently repeated two builds and two validations
  without importing or invoking the consultant.

The Tika archive SHA-512 matched the Apache release checksum. The MALLET archive
SHA-256 matched the GitHub release asset digest. The bundle binds the full Tika and
MALLET JAR inventories, not only the archive names. The hardened receipt also binds
the complete generated bundle inventory, both plans, the source-combination
decision, both Python locks, the full Python runtime string, and both final skill
trees.

## Canonical extraction and retrieval

The candidate subsequently completed two clean builds from the 15 PDF sources in
`graphrag-papers-40`. Both builds produced the same authoritative record digest,
`faac75af34f1a3bd67c10354fbf217850cd1b4d0468a93b1a90416e236e9286c`,
and the same bundle inventory digest,
`bc7db567bb8dfbbe3f3e80c2279f002bdc1e1af57d143bfc1c70707ab029d993`.

The extraction-fidelity audit passed all 75 exact gates across the 15 papers and
reproduced every metric in the independent build:

| Token recall | Token precision | Five-gram recall | Hard-anchor pass | Hard-anchor five-gram recall |
|---:|---:|---:|---:|---:|
| 98.79% | 93.69% | 95.55% | 98.31% | 96.32% |

The deterministic evaluator then ran all 40 frozen questions against both builds
at Top 10 and pool 100. Rankings, scores, evidence, aggregate metrics, and
pool-prefix comparisons were exact across replicas. The prospectively selected
attempt-10 Top-10 row is:

| Route | Recall@10 | Hard Recall@10 | MRR@10 | nDCG@10 | Evidence valid | Mean ms | P95 ms |
|---|---:|---:|---:|---:|---:|---:|---:|
| `tika_mallet_fusion` | 74.82% | 71.83% | 87.50% | 75.44% | 400/400 | 77.13 | 86.36 |

Hard-question MRR@10 was 71.67% and hard-question nDCG@10 was 61.80%. Latency
excludes the separately reported 8,641.89 ms deep-validation and loading setup.
The tracked
[retrieval audit](reports/canonical-retrieval-20260723.md) binds all four Top-10
and pool-100 reports. This result is ranking-eligible for the canonical direct
retrieval comparison.

## Grounded Harbor status

Grounded answer construction remains unranked. The v2 and v3 treatments each
encountered a provider context-limit failure, so their successful cells cannot be
merged into a complete treatment. The separately frozen v4 bounded consultation
skill was rejected on its first model call with `usage_limit_reached`: zero input
tokens, zero output tokens, no assistant output, and no agent tool calls.

The provider reported a reset at `2026-07-29T17:08:54-04:00`. The quota result is
an external pre-agent failure; its numeric verifier placeholders are not semantic
scores. A grounded ranking requires a new append-only v4 campaign that completes
all 40 questions exactly once after provider access returns. The
[campaign status](reports/harbor-campaign-status-20260723.md) binds the preserved
receipts and explains the admission rule.

## Operational findings

MALLET can emit a missing-option error with process exit code zero. The wrappers
therefore require clean diagnostics plus every expected non-empty output and parse
their contents before accepting success.

One MALLET import attempt on Windows encountered a transient JShell/JDI local
connection timeout; the identical next attempt passed. Both build and deep-consult
wrappers now retry once only when that exact transient signature appears. Other
non-zero exits and runtime markers still fail immediately.

The adversarial pass additionally required one-read raw snapshots before Tika,
lexical symlink/reparse rejection, an explicit hash-bound MALLET classpath checked
around every Java invocation, deep-validation scratch disjoint from the bundle and
runtime, closed authoritative concept and Semantic trees, and atomic no-replace
publication. The negative-case matrix records each corresponding automated test.

## Interpretation

The original two-fixture smoke alone was not evidence that MALLET improves
retrieval quality. The later 40-question result is valid comparative evidence for
the direct-retrieval scope: it is deterministic and evidence-valid, but its 74.82%
Recall@10 is below the strongest accepted and experimental fusion rows.

This reporting decision does not promote the Tika beta to production use, register
a ninth Harbor family, or claim grounded answer quality. The format study covers
15 canonical PDFs plus the earlier XLSX smoke fixture, not Tika's full format
surface. Cross-platform build and retrieval replication and a clean grounded
Harbor campaign remain promotion requirements.

## Canonical evaluation intake

The candidate now has a machine-readable
[canonical evaluation intake](canonical-evaluation-intake.json). It records the
passing mechanical, extraction, and 40-question retrieval evidence. Direct
retrieval is explicitly ranking-eligible; grounded Harbor rewards remain null
because no single frozen treatment completed the exact 40-cell matrix. This adds
the candidate to the canonical direct-retrieval table without changing
`families.json` or the historical eight-family campaign.

## Reproduce

The runner never downloads tools and refuses to overwrite its output root:

```bash
python run_experiment.py --java JAVA --tika-home TIKA_HOME --mallet-home MALLET_HOME --output-root NEW_OUTPUT_ROOT
```

It builds two bundles, validates each, runs consultant deep validation and a fusion
query, compares all path-and-byte hashes, and writes `report.json` under the new
output root.

For a builder-only acceptance run, use:

```bash
python run_builder_experiment.py --java JAVA --tika-home TIKA_HOME --mallet-home MALLET_HOME --output-root NEW_OUTPUT_ROOT
```
