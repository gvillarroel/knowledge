---
adr: "0005"
title: "ADR 0005: Scale Semantic OKF Spark Adapters by Contract"
summary: "Match CSV fields by physical header name, batch whole-text adapters into one PythonRDD, and warm reusable workers before large local plans."
status: "Superseded"
date: "2026-07-11"
product: "knowledge"
owner: "Platform Architecture"
area: "Semantic Knowledge Processing"
tags:
  - knowledge
  - spark
  - csv
  - rdf
  - windows
---

# ADR 0005: Scale Semantic OKF Spark Adapters by Contract

## Status

Superseded by ADR 0008.

## Context

A forty-source exercise exposed two assumptions that passed the original four-source fixture but were not valid at scale.

First, the CSV adapter built a Spark schema in JSON object order. JSON member order is not semantic, so a manifest serialized with sorted keys could attach the wrong declared type to a physical column. Reading every CSV as strings and casting later fixed the order problem but lost native Spark CSV behavior for locale-sensitive dates, strict booleans, and `FAILFAST` conversion.

Second, each Markdown or RDF source created a separate PythonRDD. Spark 4.1.2 on Windows uses a fixed ten-second connection window for each simple Python worker. A large union could therefore start more worker factories midway through a stage and fail nondeterministically even after the JVM-only Pi smoke test passed.

## Decision

CSV ingestion will use a two-part contract:

- parse each physical header before Spark can rewrite duplicate names;
- reject duplicate, missing, extra, and case-mismatched names;
- treat manifest schema object order as irrelevant;
- build an explicit `StructType` in observed header order and use Spark's native typed `FAILFAST` reader;
- preserve supported Spark date, timestamp, locale, null, and boolean semantics;
- reject non-finite doubles explicitly;
- quote top-level Spark identifiers so legal dots are literal rather than nested paths;
- reserve adapter-internal column names in manifest validation.

Whole-text ingestion will:

- read all declared Markdown and RDF paths with one `wholetext=True` DataFrame;
- route each file to one or more reviewed source mappings by its normalized local path;
- parse all whole-text sources through one PythonRDD rather than one PythonRDD per manifest entry;
- start a small Python-worker job immediately after session creation and require worker reuse;
- use an extended authenticated result-socket timeout and one final ordered `collect()` because the atomic driver materializer retains the complete normalized record set anyway.

Source content hashes remain deterministic driver-side snapshots taken before and after normalization. Spark still performs every declared source adapter read and normalization; the driver hash passes avoid one auxiliary Spark job and one result socket per source.

SHACL build failures will summarize the owning named shape, constraint component, focus node, result path, and message before deleting the atomic staging tree.

## Consequences

Positive:

- CSV semantics no longer depend on JSON serialization order;
- native Spark CSV behavior remains available without silent null conversion;
- duplicate physical headers and dotted field names have explicit behavior;
- a forty-source local plan uses one reusable whole-text worker pipeline and starts reliably on Windows;
- invalid rule fixtures are attributable without retaining partial output;
- source-race detection still compares complete pre/post snapshots.

Negative:

- each CSV file receives a lightweight driver-side header parse before Spark reads its records;
- whole-text mappings and path routing are serialized together to workers, so very large manifests should be split into independently versioned bundles;
- the driver must hold normalized records for atomic cross-artifact validation;
- Spark 4.1.2-specific Windows safeguards must be reviewed when the pinned Spark version changes.
