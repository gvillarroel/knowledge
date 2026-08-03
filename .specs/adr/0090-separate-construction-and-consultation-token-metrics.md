# ADR 0090: Separate construction and consultation token metrics

## Status

Accepted on 2026-07-30.

## Context

Harbor result artifacts preserve `n_input_tokens`, `n_cache_tokens`, and
`n_output_tokens`, but current evaluation tables either retained those values
only in raw JSON or reported aggregate totals without a stable denominator.
That made it difficult to compare knowledge-construction workflows with one
another or consultation workflows with one another.

Construction and consultation are separate causal stages. A `build-consult`
trial combines both and cannot identify construction cost. Token values also
depend on the model, tokenizer, prompt contract, corpus, and task, so a
cross-model average is not a fair methodology comparison.

Harbor's `n_input_tokens` already includes cached input. Adding
`n_cache_tokens` to it would count cached tokens twice.

## Decision

Use two distinct efficiency metrics:

1. **Tokens per generated knowledge folder.** Source this only from
   builder-direct trials that declare how many primary and replay folders they
   generated. Report trial count, folder count, qualification state, model,
   mean input including cache, mean cache, mean output, and mean total per
   folder. Exclude combined `build-consult` usage from this metric.
2. **Tokens per consultation query.** Source this from `consult-only` trials.
   Report submitted-query cost so provider and runtime failures do not
   disappear, and report complete-response cost separately when the available
   artifacts support that denominator.

For both metrics:

- define total tokens as `n_input_tokens + n_output_tokens`;
- report `n_cache_tokens` separately as a subset of input and never add it to
  total;
- omit incomplete input/output observations from token means rather than
  converting them to zero;
- keep methodology comparison rows split by model and runtime contract;
- state the dataset, cohort, trial count, unit, and failure count; and
- keep token efficiency in a diagnostic table without a position unless all
  ranking inputs share the same model, corpus, cohort, and task contract.

Compact checked evidence may preserve exact token observations, result paths,
and result SHA-256 values when large raw Harbor directories remain ignored.
When the raw result is locally available, regeneration must verify its digest,
model, task identity, gate values, and usage against the compact evidence.

Historical digest-bound reports remain immutable. Future consultation campaign
summaries and current-metrics reports add token sections under this contract.
Artifact-only recalculation is preferred when complete native traces already
exist; it must not make new model calls merely to reproduce stored usage.

## Consequences

- Construction and consultation costs are visible without conflating stages.
- Cache accounting is consistent and cannot inflate totals through double
  counting.
- Failed submitted consultations remain part of the operational cost estimate.
- Existing immutable traces can populate current tables without consuming
  additional model quota.
- Builder coverage remains incomplete until every registered methodology has
  comparable builder-direct evidence.
- Cross-model and cross-corpus token values remain useful diagnostics, but not
  a methodology ranking.
