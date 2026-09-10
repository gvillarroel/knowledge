# Ensemble semantic-return correction: public correctness evidence

The second Ensemble construction proposal passed its sealed local checks and
an exact parent/child comparison in the pinned Python 3.12.13 runtime. Both
versions produced **35 byte-identical files**, the same nonempty search results
under all three policies, and the same rejection JSON for the declared corrupt
input. **No EnterpriseRAG retrieval score changed.** The full native workload
has been prepared for this exact candidate but has not been dispatched at this
checkpoint. The [aggregate](aggregate.json) binds the reviewed evidence.

## What changed and why

The [previous full-workload execution](../construction-native-terminal-001/README.md)
completed its first build, then failed during standalone validation with a
container OOM event. A subsequent public observation found five parsed RDF
graphs and one SHACL report still alive after the unchanged semantic validator
returned. Their later reclamation was observed, but automatic collection
remained enabled: that observation did not isolate manual collection as the
exclusive cause or identify the original OOM allocation site.

The new candidate changes one Ensemble builder file. It keeps the original
validation body byte-for-byte under a private function name. The public
wrapper calls it once, collects unreachable objects after its frame returns,
and returns the same result. It preserves invalid results and propagated inner
exceptions. All **251 other package files**, including consultation, remain
unchanged. See the [decision record](../../../../../.specs/adr/0140-collect-semantic-validation-state-after-frame-return.md).

The sealed candidate is
`sha256:3adc772b29c0175023b48875e4592a85499394d322f09a8d6e837c460025014c`.
Its parent is the previous Ensemble correction,
`sha256:d41f9aa819ff9e6154d5d3eea08e7963e060d86f67e7ab1a104225c828180eef`.

## Evidence by runtime

Five sealed Windows Python 3.14 commands passed: syntax, skill format,
complete artifact/query and rejection checks in each of two storage layouts,
and a graph-lifetime comparison. The lifetime assertions observed five parsed
graphs plus one SHACL report alive in the parent and zero in the child, with
equal validation reports and core artifacts. The sealed command receipts and
source-bound assertions are retained; their disposable raw output trees are
not. Those earlier corruption checks compare rejection status and exit code.

The subsequent native-image fixture retained every command output. It uses
four public records, source-packed storage, hashing embeddings of dimension
384 and native record chunking. Its **12 child commands** comprise two complete
builds, two independent post-build validations, six queries and two deliberately
invalid validations. All returned their declared exit codes. Independent
comparison confirmed identical build/validation reports, all 35 artifact files,
and the complete fast, quality and robust query JSON. Increasing the semantic
processor record count by one was the sole parsed corruption; both versions
rejected it with byte-identical diagnostic JSON.

The container completed in **48.42 seconds**, with two CPUs, 6 GiB, network
disabled and zero retries or OOM events. Seven exact mounts were checked,
including an empty read-only mask over the image's baked dataset. No benchmark
questions, corpus, model cache, optimizer history or private task input was
mounted. The [CTA report](cta.md) separates this finite check from native
EnterpriseRAG evaluation.

## Opportunity accounting and remaining work

This is one new nonrefundable proposal: cumulative claims increase from **83
to 84 of 585**, and Ensemble advances to **2 of 105**, leaving 103. Both previous
construction first measurements remain consumed. Local checks and the public
runtime fixture add no proposal, quality miss or native retry. Closed catalogs,
five-round limits and the two historical pending first measurements remain
unchanged.

The prepared full task preserves the original **6,000 documents and 120
questions**, all validators, both constructions, all policies and resource
limits. Only the changed builder file's expected digest is updated. Harbor
parsed the configuration and bound its task/package identities without creating
a job. The exact caller, registered design and current admission still require
their execution checks. Its one prospective measurement is separate from the
two consumed construction attempts.

This fixture establishes bounded correctness compatibility. It does not show
full-corpus fit, peak-memory reduction, learned-provider compatibility, a
retrieval gain or independent acceptance. Collection after a frame returns
cannot reduce a peak inside that frame and may add runtime overhead. Canonical
skills remain unchanged. The [retained eight-family comparison](../construction-native-terminal-001/README.md)
still leads with Legacy at 72.38 and Turso at 72.08 on the internal weighted
nDCG@10 scale. Five searches, joint replay, the paired all-500 comparison and
independent whole-bundle acceptance remain unfinished.

[E11 overview](../README.md) · [Results by family](../../../../../docs/enterprise-family-report-index.md)
