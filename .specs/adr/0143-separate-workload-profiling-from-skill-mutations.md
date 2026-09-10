# Separate workload profiling from skill mutations

Status: Accepted for development diagnostics; native qualification and skill
promotion retain their existing gates.

Date: 2026-09-10

## Context

The Entity builder and consultant matching corrections passed small public
software checks, but the complete EnterpriseRAG construction attempt still
timed out. The previous profiling input used Markdown, 160-character sections
and at most 200 candidate entities. The exposed native workload uses JSON body
fields mapped to RDF literals, 12,000-character sections and up to 1,200
candidate entities. A small profile with different processing paths cannot
identify the complete workload's dominant cost.

A metadata-only audit of the already bound development documents measured
37,183,736 raw body characters across 6,000 records, with a median of 5,869 and
a maximum of 33,976. It exported no document text, identity, question or answer.
New public synthetic JSON cells preserve the relevant plan values while using
deterministic 8,192-character bodies and one declared source family.

The first diagnostic passed construction, independent validation and deep
consultation on 256 records. Its 1,024-record build ended with signal 11 during
a partial asynchronous traceback dump. A separately declared instrumentation
control preserved the exact input, package, image and per-command resources,
disabled asynchronous traceback collection, and completed all three operations.
The successful 256-record cell was not repeated. This evidence does not prove
the crash cause or the phase of the original native timeout.

## Decision

Before using a software profile to choose a resource optimization, record the
source adapter, mapped content, document size range, sectioning, extraction
limits, storage placement and complete validation path. Keep differences from
the target workload explicit. Synthetic sizes or renamed cells do not create
independent source families.

Declare profiling and instrumentation controls before executing them. Keep the
candidate, inputs and resource limits frozen, preserve every consumed attempt,
and retain valid cells when a later cell fails. Asynchronous traceback sampling
is a separate diagnostic treatment; do not insert it silently into qualifying
measurements or attribute its failures to a skill without evidence.

Use successful profiles to formulate bounded hypotheses. Reserve and realize
any skill mutation separately under the existing
[construction accounting policy](0137-charge-construction-corrections-within-enterprise-search-caps.md).
Keep builder and consultant changes in separate treatments and preserve complete
construction, independent rederivation, byte parity and corruption rejection.
Profiling does not reopen a stopped study or replace any acceptance gate.

## Evidence and consequences

The [public JSON diagnostic](../../evaluations/reports/evolution/e11/entity-json-scaling-001/README.md)
binds both original and control outcomes. In the successful 1,024-record
control, candidate extraction accounts for 32.10% of profiled build time and
48.39% of profiled deep-consult time. Nested function timings include profiling
overhead and must not be summed or extrapolated into a native speedup.

The exact package remains
`sha256:15d7fd9ffc0e83a1585a901bf6a2ee8133d2c58407130e3c0918cb7acdf39cbc`.
The public diagnostic aggregate is
`488c5cce7bef3cb89fe2db4ffeb424420e1be901ac8859b3c05f03490069b9a3`.
The next source-only hypothesis concerns repeated n-gram eligibility checks;
it has no candidate, reservation, new native attempt or measured quality gain.
Cumulative claims remain 86, all retained EnterpriseRAG scores are unchanged,
and the final all-500 comparison and independent acceptance remain unfinished.
