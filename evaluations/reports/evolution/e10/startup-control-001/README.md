# E10 startup: completed measurements and control refusal

E10 stopped on September 9, 2026 after three completed native jobs. All three reproduced their bound historical primary scores and had evidence integrity 1, no native errors and zero retries. The all-family starting gate remained incomplete because seven controller lanes were refused.

| Family | Native role | nDCG@10 | Recall@10 | MRR@10 | Full evidence@10 | Controller return |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| embeddings | baseline | 63.51 | 80.82 | 61.59 | 75.61 | Completed |
| legacy | baseline | 61.11 | 71.60 | 61.01 | 66.60 | Post-check refused |
| legacy | retained-start | 72.38 | 81.99 | 71.51 | 76.43 | Post-check refused |

Quality values are percentages. These measurements use 120 exposed development questions, 112 eligible questions and population weights totaling 470, on 6,000 reference-enriched complete documents. They confirm starting references; no new mutation was measured and no new gain is claimed.

Legacy's native owner completed both jobs and its archive, then the mandatory post-evaluation custody check refused. Its settled controller receipt is absent. Classical, Adaptive, Entity Graph, Ensemble, Graphify and Turso were refused before any E10 native trial. Embeddings completed its controller return. A native measurement and completion of the guarded starting stage are separate facts.

## Demonstrated control defect

Harbor persists trial configuration with `exclude_defaults=True`. The frozen checker instead expected a complete model dump. On the captured live agent, the first absent default, `extra_instruction_paths`, raised a missing-key error and became a generic custody refusal. Eight directly indexed defaults were affected. The earlier fixtures used a full START dump and missed this serialization boundary.

A source-derived projection of only those defaults passed the remaining checks on the later captured agent metadata; eight explicit non-default counterfactuals still rejected. The independent review establishes a concrete compatibility defect. It does not reconstruct the original refusal snapshot or prove that no other condition could have failed at that earlier time.

The sealed checker was preserved. No later projection replaced the original refusal or supplied a missing receipt. A separately reviewed correction must validate the complete native schema, preserve explicit overrides and retain effective-policy checks. See [ADR 0136](../../../../../.specs/adr/0136-read-native-trial-configurations-with-authenticated-defaults.md).

## Preserved opportunities

Three of the twelve allocated starting roles were consumed; nine never ran. None of the 81 cumulative variant claims changed, and both pending first-measurement obligations remain pending. The three closed catalogs stay closed. A future continuation must revalidate compatible completed native imports without repeating these semantic outcomes, then complete the unstarted roles before remaining proposals.

All four E10 stages are stopped, with no private release, all-500 recalculation, joint selection or installation. The eight-family comparison and improvement objective remain incomplete. This report supplies no Luna answer Overall or official public leaderboard position.

[CTA](cta.md) · [Exact native report](native-final-report.md) · [Aggregate and source bindings](aggregate.json) · [E10 overview](../README.md)
