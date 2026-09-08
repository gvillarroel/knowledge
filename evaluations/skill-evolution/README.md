# Native retrieval-profile evolution

This workspace owns the bounded construction-profile experiment described in
[ADR 0117](../../.specs/adr/0117-evolve-retrieval-construction-profiles-with-native-harbor.md).
Follow the [operating guide](../../docs/retrieval-profile-evolution.md) and the
[knowledge-skill evolution playbook](../../docs/knowledge-skill-evolution-playbook.md)
before authoring tasks, realizing candidates, or opening an independent gate.

The current proposal covers eight families and 18 existing retrieval routes on
four exposed internal development workloads. Four initial profile mutations
change learned embeddings, expansion weights, BM25 length normalization, and
title weighting. They preserve vendored builder and consultant implementations.
Native Harbor executes the exact staged package; the independent verifier runs
in a separate, physically offline container. No instruction-model calls occur.

Code and the hypothesis grid belong in Git. `generated/`, `results/`, model
weights, private source corpora, questions, reference labels, seeds, native jobs,
candidate copies, and case diagnostics remain local and ignored. Reviewed
aggregate reports belong in `evaluations/reports/evolution/`.

The [exact campaign helper source archive](campaign-tools/README.md) retains the
reviewed workspace scripts and their hashes in Git. Their runtime location is
the ignored registered study workspace; see the operating guide before replay.

`aggregate_development.py` publishes per-skill, per-profile, per-dataset and CTA
views from completed native reports. `report_selection.py` records the frozen
final-archive tie-breaks and development-gain requirement using the owner's
scores; the installed owner must verify its seal and exact finalist binding.
This reporter cannot start evaluations, release validation or promote a package.
`aggregate_campaign.py` joins both registered e5 development reports into one
catalog by dataset, skill, measured run and CTA before private release. It keeps
the two baseline runs separate and publishes descriptive maxima without creating
a combined native archive or changing the final-generation selection rule.
`aggregate_interruption.py` provides a separate descriptive endpoint when a
native generation cannot finish. It binds native complete and explicitly partial
reports, preserves all missing denominators, and creates no archive or selection.
The [e5 observed comparison](../reports/evolution/e5/interrupted-development-001/README.md)
contains 319 / 320 native results and 717 route measurements. Its last profile is
unavailable for ranking; private validation remains sealed.
`aggregate_validation.py` publishes only
the terminal controller decision and allowed aggregate fields after evolution
and independent validation are completed. It preserves rejected and incomplete
outcomes without exporting private task identities or case-level feedback.

These are deterministic construction/retrieval experiments. They do not measure
generated-answer correctness, instruction following, or official EnterpriseRAG
or BEIR leaderboard performance. Canonical defaults require the declared
terminal validation decision before any promotion claim.
