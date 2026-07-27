# Semantic OKF Tika and MALLET Experiment

This experiment exercises the standalone Tika and Java MALLET skill pair on two
small, immutable binary fixtures: one PDF and one XLSX workbook. It remains outside
the canonical eight-family Harbor registry.

The build must prove all of the following:

- Apache Tika 4.0.0-beta-1 default output equals explicit `--md` output;
- canonical Tika metadata and raw input hashes bind each generated Markdown source;
- the generated `ExtractedDocument` ontology and SHACL rules produce a valid
  Semantic OKF core;
- Java MALLET 2.1.0 trains with a fixed seed and one thread;
- every MALLET document and topic remains a non-authoritative retrieval signal; and
- two complete builds have identical sorted path-and-byte inventories.

The fixture hashes are:

| Path | SHA-256 |
| --- | --- |
| `fixtures/documents/integration-preview.pdf` | `c78b908d8dd8490e48abd7c970b5a59993a68477cfbcbb87c45d4a8a3d575a84` |
| `fixtures/documents/office-excel-fixture.xlsx` | `1d2a9fd643b3ad20d249c6f371b23e436798744a9439d227ca3e59000e8c1ac2` |

`source-combination-decision.json` records why the format-diverse members remain
separate logical sources in one atomic bundle. `NEGATIVE-CASES.md` is the blocking
failure-path matrix.

Run the builder and validator with explicit paths to a Java 17 executable, an
unpacked official Tika application distribution, and an unpacked official MALLET
2.1.0 binary distribution. The skills never download those prerequisites.

Use `run_builder_experiment.py` for the builder-only acceptance path: two builds,
both builder-owned validations, and a complete inventory comparison. It has no
consultant dependency:

```bash
python run_builder_experiment.py --java JAVA --tika-home TIKA_HOME --mallet-home MALLET_HOME --output-root NEW_OUTPUT_ROOT
```

Use the explicitly pair-level `run_experiment.py` only for integration acceptance.
It additionally runs consultant deep validation and a fusion query. The output root
must not exist:

```bash
python run_experiment.py --java JAVA --tika-home TIKA_HOME --mallet-home MALLET_HOME --output-root NEW_OUTPUT_ROOT
```

See [RESULTS.md](RESULTS.md) for the checked real-tool smoke and its limitations.
The
[canonical evaluation intake](canonical-evaluation-intake.json)
maps that evidence to the canonical table without treating unmeasured retrieval or
Harbor fields as zero. The candidate remains outside `families.json` until every
required admission gate in that record passes.
