# ADR 0111: Adopt isolated replicated semantic answer audits

## Status

Accepted

## Context

ADR 0110 re-adjudicated the Classical chunking population with two answers in
each reviewer call and reversed their order in a second call. A methodology
audit found that this design could leak one answer into the judgment of the
other, synthesize a false regression by taking the worst cell across two
orientations, and hide required-point swaps inside an aggregate score. The
population preparation path also validated only the first two arms even when a
larger population was declared.

The historical q019-q024 and q041-q046 tasks have semantic rubrics and qrel
document identities but no separately authored hard ground truth. The consumed
q047-q052 validation tasks have semantic rubrics and hard ground truth. Their
answers, validation outcomes, and earlier reviewer outputs are all exposed and
therefore can support only a retrospective correction, never a fresh
promotion gate.

Early correction attempts exposed two additional evaluator defects. A positive
control derived only from summarized ground-truth claims did not necessarily
cover every authored rubric point. Separately, Luna repeatedly mistyped one
character while echoing a packet SHA-256 even though the runner already had the
authoritative prompt-to-process binding.

## Decision

Use `isolated_answer_quality_review.py` for superseding retrospective semantic
audits. The protocol must:

- validate every declared arm against its complete frozen question set, task
  checksums, job lock, raw-answer digest, projected-answer digest, and native
  Harbor report;
- distinguish `qrel-grounded-rubric` contracts from `hard-ground-truth`
  contracts and never invent retrospective truth;
- show exactly one anonymized answer per reviewer call;
- obtain three independent judgments with forward, reverse, and deterministic
  rotated criterion orders while retaining stable criterion identifiers;
- derive per-cell majority consensus and emit an unresolved state when three
  judgments disagree;
- compare answers by criterion identity without within-case compensation, so a
  simultaneous gain and loss is `mixed` rather than improved;
- run an empty-answer negative control for every task and a complete
  contract-derived positive control only where hard ground truth exists;
- bind the accepted result to the packet in the runner, treat the model's
  digest echo as diagnostic only, and record rather than semantically interpret
  echo mismatches;
- capture invalid outputs privately, cap attempts at three per prompt, bind the
  evaluator implementation hash in the manifest, and reuse a valid result only
  when packet and prompt digests are identical; and
- publish only reviewed aggregates, never answer text, task text, rationales,
  job paths, or private recovery artifacts.

Validate the reused frozen answer jobs first with native `harbor-run-results`
reports. The q019-q024 and q047-q052 populations are lock-and-trial comparable.
The q041-q046 v27 job has matching tasks, model, Pi version, checksums, and
completed results but a documented recovery environment-wrapper drift; report
that arm as trial-result comparable rather than fully lock comparable.

The final Luna/high audit contains 468 validated judgments across 22 strategy
rows. Calibration passes 6/6 for q019-q024, 6/6 for q041-q046, and 12/12 for
q047-q052. Every non-canonical strategy remains rejected by the component-wise
non-regression gate. For q047-q052, v27 reduces mean agent tokens by 82.30% but
has three regressed cases, two mixed cases, and one tie. The earlier two claimed
improvements are not retained because each compensated for a lost component.

## Consequences

- The top-level conclusion from ADR 0110 remains stable: no evaluated chunked
  strategy is promotion eligible.
- Per-case and aggregate semantic counts from ADR 0110 are superseded; they are
  retained only as historical methodology evidence.
- Quality deltas between the old and new reports are measurement corrections
  over identical answer generations, not changes in the generated answers.
- Native mechanical reward, evidence validity, token efficiency, and semantic
  correctness remain separate axes.
- Any candidate repair requires a new study with a fresh sealed validation
  dataset. None of these exposed retrospective results may guide mutation and
  then serve as its acceptance gate.
