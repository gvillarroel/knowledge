# Enterprise skills selected by the task agent

This fixed comparison evaluates one unified expert and nine application-specific
experts, all available to the agent. Both use the corrected full-document source
projection and the same Embeddings family, Luna model, tools, and execution limits.

- [Completed experiment and retained lessons](../../../docs/enterprise-source-skills.md)
- [Completed full-text comparison: results and limitations](s2/README.md)
- [Application skills and source-required question cohorts](s2/sources/README.md)
- [Cost, time, and answer quality](s2/CTA.md)
- [Question categories](s2/categories.md)
- [Verification receipt: native parity, isolation, tests, and coverage](s2/verification.json)
- [Historical title-only ingestion correction](ingestion-scope-20260907.md)
- [Historical audit bindings](ingestion-scope-20260907.json)
- [Cross-dataset report hub](../README.md)

Completed on **2026-09-07**: 80 native trials, forty per arm, with no execution
errors. The source-skill treatment did not improve the observed retrieval metrics:
raw final-evidence nDCG@10 was **82.37**, compared with **84.26** for the unified
expert, on a scale of 100. It used **2.13 times the tokens** and **1.43 times the
agent latency** per question. Both treatments had citation-format failures.

All eighty semantic review calls were attempted once. Eight invalid outputs left
**33 complete paired questions**. Their conservative required-fact coverage was
**90.15% unified versus 78.12% source skills**; full-quality counts were 20/33 and
16/33. Seven unavailable pairs remain unknown. The general report gives explicit
full-cohort bounds, which overlap; the conditional semantic means do not certify
the winner across all forty questions. The [availability decision](../../../.specs/adr/0124-report-unavailable-semantic-review-pairs.md)
preserves the failed reviews without selective retries or fabricated statuses.

The model selected two skills for one question, three for fifteen, and four for
twenty-four. All nine application skills were mounted in every treatment task.
Historical e6 scores remain available with the corrected title-only scope and
are not a full-text baseline. No installation or promotion is implied by this pilot.

At the user's request, the unsuccessful application-split runtime has been
retired from active tracked code. Its exact implementation and evidence remain
in the ignored local archive. The full-text ingestion fix, fidelity checks,
historical audit, reports, and useful failure diagnoses are retained under
[ADR 0125](../../../.specs/adr/0125-retire-enterprise-application-skill-experiment.md).
