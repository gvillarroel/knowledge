# Isolated Skill Arena hard-question diagnostic

This is a live, no-MCP, paired control/treatment diagnostic over 5 prompts. Every raw cell was bound to the exact benchmark, prompt, profile, variant, model, source config, generated config manifest, compiled Promptfoo config, and immutable bundle before aggregation. With one request per cell, results are descriptive and do not establish a stable population effect.

Accepted eval ID: `eval-v8v-2026-07-15T23:49:40`. All 10 cells completed with 0 runtime errors.

| Profile | Compound pass | Mean score | Mean latency |
| --- | ---: | ---: | ---: |
| knowledge-only-control | 0/5 | 0.657 | 72.6 s |
| classical-cli-consult-treatment | 0/5 | 0.543 | 117.6 s |

## Metric pass rates

| Metric | knowledge-only-control | classical-cli-consult-treatment |
| --- | ---: | ---: |
| response-format | 100% | 100% |
| response-contract | 100% | 80% |
| evidence-validity | 40% | 20% |
| claim-fidelity | 100% | 100% |
| atomic-answer-completeness | 20% | 0% |
| important-negative-coverage | 20% | 0% |
| required-paper-coverage | 80% | 80% |

## Interpretation

The treatment-minus-control mean-score difference was -0.114; mean latency changed by +45.0 seconds. Component gates are more informative than compound pass because a single failed strict gate fails a cell.

| Metric | Treatment minus control |
| --- | ---: |
| response-format | +0% |
| response-contract | -20% |
| evidence-validity | -20% |
| claim-fidelity | +0% |
| atomic-answer-completeness | -20% |
| important-negative-coverage | -20% |
| required-paper-coverage | +0% |

Evidence validity was independently recomputed from all 93 reviewed ledger claims. Reviewed-claim fidelity was also independently checked by requiring each answer statement to equal the bound claim's reviewed interpretation and to have a one-to-one evidence row.

## Per-question cells

| Prompt | Profile | Variant | Pass | Score | Evidence valid | Claim fidelity | Latency |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: |
| `q026-receptor-to-gestation-boundary` | knowledge-only-control | pi-luna-only | no | 0.857 | 0 | 1 | 91.9 s |
| `q026-receptor-to-gestation-boundary` | classical-cli-consult-treatment | pi-luna-only | no | 0.571 | 0 | 1 | 99.1 s |
| `q027-feminine-risk-reconciliation` | knowledge-only-control | pi-luna-only | no | 0.714 | 1 | 1 | 62.5 s |
| `q027-feminine-risk-reconciliation` | classical-cli-consult-treatment | pi-luna-only | no | 0.571 | 0 | 1 | 136.7 s |
| `q028-phthalate-name-normalization` | knowledge-only-control | pi-luna-only | no | 0.571 | 0 | 1 | 73.9 s |
| `q028-phthalate-name-normalization` | classical-cli-consult-treatment | pi-luna-only | no | 0.571 | 0 | 1 | 108.4 s |
| `q029-label-gate-validity` | knowledge-only-control | pi-luna-only | no | 0.571 | 0 | 1 | 64.9 s |
| `q029-label-gate-validity` | classical-cli-consult-treatment | pi-luna-only | no | 0.571 | 1 | 1 | 127.7 s |
| `q030-causal-evidence-map` | knowledge-only-control | pi-luna-only | no | 0.571 | 1 | 1 | 69.8 s |
| `q030-causal-evidence-map` | classical-cli-consult-treatment | pi-luna-only | no | 0.429 | 0 | 1 | 116.2 s |

## Actual answers for `q030-causal-evidence-map`

### knowledge-only-control / pi-luna-only

The snapshot provides a layered but incomplete evidence map. Product testing found DBP and DEHP in all 11 tested sanitary-pad brands, while package air was sampled for volatile compounds. Workplace sampling found six phthalates in every tested nail salon, with DEHP highest on silicone wristbands. Human biomonitoring detected DEP, DBP, and DEHP in all 20 menstrual-blood samples and BPA in 13. Receptor bioassays showed estrogen agonism in three tested hair-product samples. Epidemiologically, daily hair-oil use near 36 weeks was associated with 8.3 fewer gestational days after adjustment for race. A mechanistic review found anti-androgenic activity for BP-1, BP-2, and BP-3 in cited assays. Together, these findings support product presence, environmental and biological exposure, biological activity, and an association with a health outcome, but they do not establish that one specific product caused that outcome. The evidence remains limited by small or selected samples, self-reported or incompletely characterized product use, unknown formulations and doses, possible exposure from non-product sources, and assay or sampling limitations. Minimum additional evidence would be a chemically verified, product-specific exposure assessment linking the product to internal dose; a replicated prospective epidemiologic design with temporally appropriate repeated biomarkers, a defined health outcome, adequate size, and control of major confounding; and convergent experimental evidence showing that exposure levels plausibly reached by users produce the relevant receptor or mechanistic effect and outcome. Ideally, product removal or replacement would reduce exposure and risk. Without that chain from verified product composition to dose, mechanism, temporality, and replicated outcome, a product-specific causal health claim is unsupported.

Claims: 7; evidence rows: 7; summary words: 253; exact ledger evidence valid: yes; exact reviewed-claim fidelity: yes.

### classical-cli-consult-treatment / pi-luna-only

The snapshot supplies a partial evidence chain, not a product-specific causal case. Product-content testing found DBP and DEHP in all 11 tested sanitary-pad brands, while package air was sampled by gas chromatography for volatile compounds. Workplace sampling documented volatile-organic-compound badges and silicone-wristband phthalate assessment in nail salons. Human biomonitoring linked recent product use and label-derived ingredients to urinary endocrine-disrupting-chemical biomarkers, but this was a pilot. Receptor bioassays showed estrogen agonism in three tested hair-product samples, and a mechanistic review synthesized endocrine evidence for several ultraviolet-filter and related chemical classes. Epidemiologic evidence was associative: daily hair-oil use near 36 weeks corresponded to fewer gestational days after adjustment for race.

Important limitations remain. The product and workplace results do not demonstrate absorbed dose from one named product, the biomonitoring study was exploratory, and the epidemiologic result involved self-reported exposure without brands, dose, or chemical composition in a small, incompletely adjusted pilot. The review also states that molecular initiating events and atomic-level mechanisms remain insufficiently characterized. Thus, the minimum additional evidence is a product-specific package: validated chemical and emission characterization of the exact formulation and normal-use scenario; repeated, temporally aligned internal-dose biomarkers in exposed users; receptor and cellular effects at achieved human-relevant concentrations with identified active constituents; and a prospective, adequately powered epidemiologic study linking measured product-specific exposure to a prespecified health outcome while controlling alternative sources and confounding. Stronger causal support would additionally require reproducible dose-response and temporal ordering, triangulated across cohorts or a credible intervention/dechallenge design.

Claims: 9; evidence rows: 9; summary words: 245; exact ledger evidence valid: no; exact reviewed-claim fidelity: yes.

## Superseded evaluator run

Eval `eval-yHh-2026-07-15T23:05:59` is excluded from causal interpretation because it predates the final exact reviewed-claim evaluator contract. Its raw artifact hash remains recorded in the compact JSON report.
