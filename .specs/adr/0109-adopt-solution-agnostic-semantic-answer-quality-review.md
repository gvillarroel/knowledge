# ADR 0109: Adopt solution-agnostic semantic answer-quality review

## Status

Accepted

## Context

The native Semantic OKF scorer explicitly measures mechanical response
contracts, evidence validity, document focus, and evidence-anchor coverage. It
does not establish semantic correctness. Whole-record evidence locators can
cover every hidden anchor mechanically, so a storage representation may raise
native reward even when the delivered passages omit a target result.

The first independent v27 review compared answers through their selected
evidence and citation assignments. It found two regressions, but that method
could not prove that the result was independent of the files, locators, and
retrieval route used to construct each response.

## Decision

Use `evaluations/semantic-okf-datasets/answer_quality_review.py` for automated
semantic non-regression review of completed answer pairs.

The reviewer-visible packet contains only:

- the question;
- authored required points;
- frozen ground-truth claims;
- authored important negatives; and
- normalized answer summaries and claim statements.

It excludes answer-selected evidence, evidence indices, retrieval traces,
strategy and job identities, paths, hashes, locators, native rewards, and token
usage. Ground-truth claims define the requested semantic target, but do not
prescribe wording, citation order, retrieval method, chunk layout, or storage
format. A true adjacent result cannot replace the concrete experiment, model,
or quantity fixed by the target claim.

Run two independent Pi/GPT-5.6 Luna reviews per case with answer order reversed.
Validate every output against the exact packet digest and a closed status
vocabulary. Derive required-point coverage deterministically from validated
statuses, use conservative consensus across orientations, and compare arms by
Pareto dominance across coverage, important-negative violations, correctness,
and strict case pass. Do not accept a model-authored aggregate score.

The R2 re-adjudication reused the six canonical and six v27 validation answers
without regenerating them, thereby isolating the evaluator change. It found:

- mean required-point coverage of 77.08% for canonical and 75.00% for v27;
- three v27 regressions, two improvements, and one mixed case;
- the original q047 and q048 semantic regressions without exposing solution
  mechanics, plus an additional q049 coverage regression;
- v27 improvements on q050 and q051, and mixed movement on q052; and
- zero strict full-quality cases for either arm under conservative consensus.

The result rejects semantic non-regression and does not change ADR 0108's
non-promotion decision. Native reward and token, cost, and latency measurements
remain valid within their stated mechanical and efficiency scopes.

## Consequences

- Storage and locator changes cannot affect the reviewer-visible quality
  packet when answer prose is unchanged.
- Mechanical reward can no longer be presented as semantic quality.
- The original raw jobs and the first review remain immutable historical
  evidence; R2 is the superseding quality audit.
- The released validation outcomes must not be used to mutate v27. Any repair
  requires a new study and fresh, digest-locked validation data.
