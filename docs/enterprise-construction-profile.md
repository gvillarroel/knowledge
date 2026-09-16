# EnterpriseRAG construction feasibility and phase costs

This prospective ordinary evaluation diagnoses the unchanged Entity Graph and
Ensemble constructors. [ADR 0168](../.specs/adr/0168-profile-construction-before-further-enterprise-mutations.md)
records the decision. The [six-strategy retrieval catalog](../evaluations/reports/datasets/enterprise-all500-first-executions-001/README.md)
retains its separate metric and source studies.

## Frozen workload and budget

| Field | Declared value |
| --- | --- |
| Study | `enterprise-build-profile-001` |
| Owner and stages | `harbor-run-results`; ordinary evaluation, then publication |
| Cell order | Entity Graph 256; Ensemble 256; Entity Graph 1,024; Ensemble 1,024 |
| Input | Complete records from the identified 6,000-document public parent; nine applications |
| Input size | 256 records / 1,629,264 UTF-8 body bytes; 1,024 records / 6,797,341 bytes |
| Skill | Complete, unchanged E16 reference composition |
| Provider and layout | Ensemble hashing, revision 1, 384 dimensions; `source-packed-v1` |
| Original allocation | Four trials in one job, one attempt each, zero retries |
| Concurrency and resources | Two trials; two CPUs and 6 GiB per agent and separate verifier |
| Agent budget | 1,800 seconds for the whole sequence; 1,750 useful seconds and bounded finalization |
| Verifier budget | 600 seconds total; 570 useful seconds and bounded finalization |
| Work per cell | Two constructions, two additional validator commands, full output hashing and equality |
| Outcomes | Construction integrity, phase wall time, output bytes, bounded code-location samples |
| Queries, retrieval scores, answer quality, mutation, selection, promotion | None |

Within each application, order records by SHA256 of compact UTF-8 JSON
`[source_id, record_id]`, followed by exact record ID. Interleave sorted application
IDs round-robin, skipping exhausted groups. Use the first 256 and 1,024 identities
of that single order. Preserve original complete record lines and all fields;
adapt only declared manifest descriptions and source ordering. The smaller
membership is a prefix of the larger. This balances application record counts,
not corpus proportions or body bytes. No question, relevance label or answer
influences input selection.

## Execution and evidence

Bind the actual original image's helper bytes, complete input inventory, effective
adjusted plans, constructor and validator argv, interpreter, model cache and full
skill. The derived agent image removes the inherited dataset; each task receives
only its declared input through a read-only mount. Keep networking disabled,
privileges restricted, skill and model mounts read-only, and workspaces fresh.
The separate verifier uses the same dependency image with its own trusted source,
skill and contract. No development history or private evaluation material is an
executor input.

Record initial attestation, plan generation, plan adjustment, build 1, additional
validation 1, build 2, additional validation 2, and final integrity as separate
phases. Builder-command time already includes its internal validations. Do not
sum inclusive stack observations into elapsed time or treat an unfinished phase
as complete. Sample stacks every five seconds, with fixed thread/frame/count and
byte caps; retain code locations without arguments, locals or source text.

Each child receives the remaining whole-sequence time. Bind process groups to
their leader's start identity and verify bounded descendant cleanup. Native
exceptions remain execution errors. A completed construction requires actual
transported trees, complete source/body coverage, expected family artifacts,
matching plans and skills, byte equality, valid phase/sample evidence, and one
additional trusted family validation outside the measured agent.

Preserve both `/workspace/construction-profile` and
`/logs/agent/construction-profile` through explicit native artifact routes.
Provide the verifier's writable `/logs/agent` mount because artifact restoration
uses the original source path. Preserve partial artifacts after a deadline.

## Finite rehearsal and admission

Before measured execution, use one separately authored nine-record fictional
fixture. For each family, compare one direct construction with two instrumented
constructions and their matched validators within one 180-second family sequence.
The total fixture cap is six constructions, with no retries.

Use exactly two no-constructor native transport originals, each with a 30-second
agent limit, one attempt and zero retries. The successful case must retain both
artifact routes, observe a real five-second sample and exclude dynamic-name/local
canaries. The forced native timeout must first prove cleanup when a leader exits
before a descendant that ignores SIGTERM, then preserve incomplete evidence and
finish native container/volume cleanup. A substantive rehearsal failure prevents
measurement admission; it does not replenish the allocation.

Register all four related cells in one public development-role dataset. Bind the
native task/configuration, runtime, image, inputs, model cache, baseline and
protocol, then require all six independent organizer checks and an exact design
seal. The one-use launcher holds the repository's exclusive execution authority.
Drift prevents further admission; consumed cells remain consumed.

## Interpretation and publication

Report every cell, including execution errors and missing construction outcomes.
Use the native Harbor report first, followed by independently reviewed aggregate
phase and sample summaries. Keep builder work, additional validators and verifier
costs separate. Nested inputs, one attempt, observer overhead, warm effects and
concurrent neighbors support descriptive observations only; they do not establish
an asymptotic scaling law or causal comparison to the old interrupted runs.

Publish reviewed aggregate construction reports and link them from the existing
skill, dataset and CTA catalogs. Retain unavailable all-500 retrieval entries.
Keep raw inputs, questions, indexed knowledge, native records, sampled stacks and
per-record evidence ignored. A later mutation needs its own prospective evolution
study and fresh independent validation; this study supplies no promotion gate.

[Back to the documentation index](README.md).
