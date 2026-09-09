# ADR 0136: Read native trial configurations with authenticated defaults

Date: 2026-09-09

Status: Accepted for preservation, artifact-only reporting and prospective
correction. Replacement execution requires a new independent review and seal.

## Context

E10 completed three native starting measurements: both Legacy roles and the
Embeddings baseline. All three had finite rewards, evidence integrity 1, zero
native errors and no retries. Their primary scores exactly reproduced their
bound historical values. Legacy then failed its mandatory post-evaluation
custody check. Six other families were refused before native dispatch;
Embeddings completed its controller return after its original job finished.
The all-family starting gate remained incomplete and no variants were proposed.

Independent diagnosis reproduced a compatibility defect on the later snapshot
of the still-running Embeddings agent. Harbor 0.18.0 persists `TrialConfig` with
`model_dump_json(indent=4, exclude_defaults=True)`. The frozen guard directly
indexed eight fields omitted at their native defaults. Its first missing-key
lookup was `extra_instruction_paths`. Earlier fixtures used a full START model
dump and did not exercise this durable serialization boundary.

Restoring only the eight source-proven defaults in a diagnostic projection
passed the remaining checks on the captured agent metadata. Eight explicit
non-default counterfactuals still rejected. This establishes a concrete false
rejection; the original generic denial does not preserve enough information to
reconstruct its original snapshot or exclude every other possible condition.

## Decision

Preserve E10's original controls, refusals, completed native outcomes, partial
controller receipts and unopened private portfolio. Bind the independent
diagnosis, maintained native report and settled inventory, then make every
stage truthfully terminal. Do not fabricate the missing Legacy dispatch
receipt, rerun any completed semantic outcome or mark the starting gate passed.

Implement a separately versioned persisted-config reader, authenticated to the
exact native schema and writer. Validate complete supported field names,
nesting and types before reconstructing defaults. Reject duplicate keys,
unknown inputs, missing required identities, invalid numbers, booleans in
numeric settings and schema drift. Preserve explicit values. Restore only
omissions justified by the authenticated native serializer and definitions.
Native parsing must not silently discard unknown fields.

Compare the complete effective inputs against the exact declared job, task and
owner policy, allowing only declared generated identities and staged skill
paths. Keep phase, role, image, resources, package and mount checks. A missing
default timeout cannot satisfy the explicit 10,800-second recalculation
override. A parser or fixture success is not live execution admission.

Test the actual durable representation and its equivalent explicit-default
form. Cover each protected override, malformed inputs, source drift, all three
phases and both native roles. Reuse unchanged access evidence with its original
scope; the correction must not create a claim of previously unobserved runtime
isolation. Preserve actionable sanitized refusal codes and evidence references
prospectively so a later diagnosis need not infer the original failure branch.

Continue under the preservation and import rules of [ADR 0130](0130-continue-interrupted-enterprise-search-prospectively.md)
and [ADR 0131](0131-correct-sealed-enterprise-admission-prospectively.md).
The twelve-role starting allocation has three consumed native measurements and
nine unstarted roles. A prospective native-owner import must revalidate the
exact completed task, package, profile, lock and result bindings and retain
their original costs and incomplete E10 admission disposition. Keep compatible
task paths and native signatures; changing an identity cannot make an
incompatible import valid. Import eligibility and future admission must be
established independently, not assumed from the reported rewards. Do not repeat
the three completed measurements to obtain a preferred outcome or a cleaner
history.

No variant was claimed in E10. Preserve all 81 existing cumulative claims,
pending first-measurement obligations, unavailable originals, seen profiles,
miss counters, finite catalogs and round limits. The zero-tolerance historical
reproduction and fixed-role requirements of [ADR 0134](0134-requalify-versioned-enterprise-profiles-without-resetting-search.md)
remain in force before new proposals. Closed catalogs stay closed. A control
refusal is not a semantic miss or a new source of fitness.

The replacement requires terminal E10 in the complete predecessor inventory,
independent non-consumption/custody review, an exclusive reservation and a new
registered design. Do not modify a previously sealed guard or treat a later
default projection as retroactive custody admission. Keep joint all-eight
replay, exact whole-bundle freezing, paired all-500 recalculation and the single
private acceptance gate unchanged. No private feedback can drive reselection.

## Evidence and limitations

The independent diagnosis contains 12 files and 40 source commitments. Its
maintained directory digest is
`3e4e29d7d7d317f49d8e12258a433383fb98bc6caeff0b0d470c97d434ff2a7a`.
The exact native configuration source digest is
`bcdf4a0e55d2318da0595aa63ee09c0a8c4fdc8aee3e3fd326fc00853832d9c5`;
the writer digest is
`15a40691a5aa03152de4f6878347272503aaa3f976cf3eb22a1ec0e5d62609c9`.
E10 ended at ledger sequence 20 with all four stages stopped and no private
release. The [E10 report](../../evaluations/reports/evolution/e10/README.md)
preserves the measured values and CTA separately from controller completion.
This decision establishes no new skill gain, completed all-family comparison,
promotion or installation.
