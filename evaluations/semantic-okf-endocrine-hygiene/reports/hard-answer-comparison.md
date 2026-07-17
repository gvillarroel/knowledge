# Hard-Question Grounded Answer Comparison

These are actual deterministic extractive answer packs from each compatible consultation route. Generation is ground-truth blind: the same post-retrieval rule selects top reviewed claims, diversifies once by paper, and copies their reviewed interpretations with exact evidence bindings. No MCP or language model participates. The answer metrics below are exact reviewed-claim fidelity and evidence-selection measures; they do not measure free-form semantic answer quality or prose fluency.

| Family | Answer-best route | Retrieval-best route | Atomic claim fidelity | Required papers | Evidence completeness | Negative claim fidelity | Exact-claim precision | Grounding | Ledger evidence valid |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| legacy | legacy_lexical | legacy_lexical | 0.0% | 97.1% | 20.4% | 0.0% | 18.3% | 100.0% | 100.0% |
| embeddings | lexical | lexical | 9.0% | 87.6% | 30.6% | 6.7% | 40.8% | 100.0% | 100.0% |
| classical | fusion | bm25 | 0.0% | 97.1% | 21.5% | 0.0% | 16.7% | 100.0% | 100.0% |
| entity-graph | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| adaptive | fusion | bm25 | 0.0% | 97.1% | 21.5% | 0.0% | 16.7% | 100.0% | 100.0% |
| ensemble | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |

## Showcase: `q030-causal-evidence-map`

### legacy

Build an evidence map covering product content, package air, workplace sampling, human biomonitoring, receptor bioassays, epidemiologic association, and mechanistic review. What minimum additional evidence would be needed for a product-specific causal health claim?

- All 11 tested sanitary-pad brands contained DBP and DEHP. (`PMC6504186`, `claim-pmc6504186-002`, `sources/markdown/PMC6504186.md#BioC-passage-0025`)
- Benzene was detected in 83 percent of the tested feminine-hygiene products and reached 3,604 nanograms per gram in one spray. (`PMC7958867`, `claim-pmc7958867-002`, `sources/markdown/PMC7958867.md#BioC-passage-0034`)
- In children, total product count did not predict higher parabens, although sunscreen and hair-care use had product-specific paraben associations. (`PMC4724203`, `claim-pmc4724203-004`, `sources/markdown/PMC4724203.md#BioC-passage-0040`)
- High product users had higher concentrations of every measured metabolite and paraben, including propyl paraben 219 percent higher and MBP 61 percent higher than low users. (`PMC4016195`, `claim-pmc4016195-005`, `sources/markdown/PMC4016195.md#BioC-passage-0035`)
- Most tested products did not list added hormones on their labels despite measured hormonal activity, while one hair oil listed placenta. (`PMC8812815`, `claim-pmc8812815-005`, `sources/markdown/PMC8812815.md#BioC-passage-0023`)
- BP-3 did not activate the progesterone receptor but acted as a progesterone-receptor antagonist in the cited assay. (`PMC4997468`, `claim-pmc4997468-004`, `sources/markdown/PMC4997468.md#BioC-passage-0016`)
- Daily hair-oil use near 36 weeks was associated with 8.3 fewer gestational days after adjustment for race. (`PMC8316883`, `claim-pmc8316883-003`, `sources/markdown/PMC8316883.md#BioC-passage-0046`)
- The reported DEP maximum is lower than the reported minimum, so that internally inconsistent range must not be reused as valid quantitative evidence. (`PMC9764248`, `claim-pmc9764248-003`, `sources/markdown/PMC9764248.md#BioC-passage-0043`)
- Participants with higher urinary MECPP reported using more total products, with weaker evidence for exposure to more ingredients of concern. (`PMC11764522`, `claim-pmc11764522-003`, `sources/markdown/PMC11764522.md#BioC-passage-0037`)
- Daily mouthwash users had higher MEP, BP3, methyl paraben, and propyl paraben than never-users. (`PMC5376243`, `claim-pmc5376243-002`, `sources/markdown/PMC5376243.md#BioC-passage-0022`)
- Cologne or perfume and deodorant were the strongest MEP predictors, while suntan or sunblock and body lotion were the strongest paraben predictors. (`PMC5783668`, `claim-pmc5783668-002`, `sources/markdown/PMC5783668.md#BioC-passage-0073`)
- Daily makeup users had higher MEP, methyl paraben, propyl paraben, and BP3 than rare or never users, and recent use of at least 20 products predicted higher propyl paraben. (`PMC6037613`, `claim-pmc6037613-002`, `sources/markdown/PMC6037613.md#BioC-passage-0027`)

### embeddings

Build an evidence map covering product content, package air, workplace sampling, human biomonitoring, receptor bioassays, epidemiologic association, and mechanistic review. What minimum additional evidence would be needed for a product-specific causal health claim?

- The reported DEP maximum is lower than the reported minimum, so that internally inconsistent range must not be reused as valid quantitative evidence. (`PMC9764248`, `claim-pmc9764248-003`, `sources/markdown/PMC9764248.md#BioC-passage-0043`)
- Sanitary pads and diapers were collected in six countries, and package air was sampled and analyzed by gas chromatography for volatile compounds. (`PMC6504186`, `claim-pmc6504186-001`, `sources/markdown/PMC6504186.md#BioC-passage-0009`)
- This review synthesizes endocrine evidence for benzophenones, camphor derivatives, and cinnamate ultraviolet filters rather than reporting a new human-exposure study. (`PMC4997468`, `claim-pmc4997468-001`, `sources/markdown/PMC4997468.md#BioC-passage-0002`)
- Participants with higher urinary MECPP reported using more total products, with weaker evidence for exposure to more ingredients of concern. (`PMC11764522`, `claim-pmc11764522-003`, `sources/markdown/PMC11764522.md#BioC-passage-0037`)
- Benzene was detected in 83 percent of the tested feminine-hygiene products and reached 3,604 nanograms per gram in one spray. (`PMC7958867`, `claim-pmc7958867-002`, `sources/markdown/PMC7958867.md#BioC-passage-0034`)
- Most tested products did not list added hormones on their labels despite measured hormonal activity, while one hair oil listed placenta. (`PMC8812815`, `claim-pmc8812815-005`, `sources/markdown/PMC8812815.md#BioC-passage-0023`)
- High product users had higher concentrations of every measured metabolite and paraben, including propyl paraben 219 percent higher and MBP 61 percent higher than low users. (`PMC4016195`, `claim-pmc4016195-005`, `sources/markdown/PMC4016195.md#BioC-passage-0035`)
- All four tested diaper brands contained DBP and DEHP. (`PMC6504186`, `claim-pmc6504186-004`, `sources/markdown/PMC6504186.md#BioC-passage-0027`)
- All 11 tested sanitary-pad brands contained DBP and DEHP. (`PMC6504186`, `claim-pmc6504186-002`, `sources/markdown/PMC6504186.md#BioC-passage-0025`)
- DEP was detected in two of four diaper brands, while BBP was not detected in any tested diaper. (`PMC6504186`, `claim-pmc6504186-009`, `sources/markdown/PMC6504186.md#BioC-passage-0027`)
- DEP was detected in eight of eleven sanitary-pad brands, while BBP was not detected in any tested sanitary pad. (`PMC6504186`, `claim-pmc6504186-008`, `sources/markdown/PMC6504186.md#BioC-passage-0025`)
- BP-3 did not activate the progesterone receptor but acted as a progesterone-receptor antagonist in the cited assay. (`PMC4997468`, `claim-pmc4997468-004`, `sources/markdown/PMC4997468.md#BioC-passage-0016`)

### classical

Build an evidence map covering product content, package air, workplace sampling, human biomonitoring, receptor bioassays, epidemiologic association, and mechanistic review. What minimum additional evidence would be needed for a product-specific causal health claim?

- All four tested diaper brands contained DBP and DEHP. (`PMC6504186`, `claim-pmc6504186-004`, `sources/markdown/PMC6504186.md#BioC-passage-0027`)
- Benzene was detected in 83 percent of the tested feminine-hygiene products and reached 3,604 nanograms per gram in one spray. (`PMC7958867`, `claim-pmc7958867-002`, `sources/markdown/PMC7958867.md#BioC-passage-0034`)
- Most tested products did not list added hormones on their labels despite measured hormonal activity, while one hair oil listed placenta. (`PMC8812815`, `claim-pmc8812815-005`, `sources/markdown/PMC8812815.md#BioC-passage-0023`)
- In children, total product count did not predict higher parabens, although sunscreen and hair-care use had product-specific paraben associations. (`PMC4724203`, `claim-pmc4724203-004`, `sources/markdown/PMC4724203.md#BioC-passage-0040`)
- High product users had higher concentrations of every measured metabolite and paraben, including propyl paraben 219 percent higher and MBP 61 percent higher than low users. (`PMC4016195`, `claim-pmc4016195-005`, `sources/markdown/PMC4016195.md#BioC-passage-0035`)
- Daily hair-oil use near 36 weeks was associated with 8.3 fewer gestational days after adjustment for race. (`PMC8316883`, `claim-pmc8316883-003`, `sources/markdown/PMC8316883.md#BioC-passage-0046`)
- Salons providing acrylic services had significantly higher EMA concentrations than salons without acrylic services. (`PMC9566193`, `claim-pmc9566193-004`, `sources/markdown/PMC9566193.md#BioC-passage-0029`)
- Participants with higher urinary methylparaben reported using more supplements. (`PMC11764522`, `claim-pmc11764522-004`, `sources/markdown/PMC11764522.md#BioC-passage-0037`)
- Colgate Total use was associated with 86.7 percent higher urinary triclosan. (`PMC6037613`, `claim-pmc6037613-004`, `sources/markdown/PMC6037613.md#BioC-passage-0030`)
- Daily mouthwash users had higher MEP, BP3, methyl paraben, and propyl paraben than never-users. (`PMC5376243`, `claim-pmc5376243-002`, `sources/markdown/PMC5376243.md#BioC-passage-0022`)
- Cologne or perfume and deodorant were the strongest MEP predictors, while suntan or sunblock and body lotion were the strongest paraben predictors. (`PMC5783668`, `claim-pmc5783668-002`, `sources/markdown/PMC5783668.md#BioC-passage-0073`)
- DEP, DBP, and DEHP were detected in all 20 menstrual-blood samples, while BPA was detected in 13 samples. (`PMC9764248`, `claim-pmc9764248-002`, `sources/markdown/PMC9764248.md#BioC-passage-0032`)

### entity-graph

N/A — paper record sources/markdown/PMC11764522 has no PDF page headings

### adaptive

Build an evidence map covering product content, package air, workplace sampling, human biomonitoring, receptor bioassays, epidemiologic association, and mechanistic review. What minimum additional evidence would be needed for a product-specific causal health claim?

- All four tested diaper brands contained DBP and DEHP. (`PMC6504186`, `claim-pmc6504186-004`, `sources/markdown/PMC6504186.md#BioC-passage-0027`)
- Benzene was detected in 83 percent of the tested feminine-hygiene products and reached 3,604 nanograms per gram in one spray. (`PMC7958867`, `claim-pmc7958867-002`, `sources/markdown/PMC7958867.md#BioC-passage-0034`)
- Most tested products did not list added hormones on their labels despite measured hormonal activity, while one hair oil listed placenta. (`PMC8812815`, `claim-pmc8812815-005`, `sources/markdown/PMC8812815.md#BioC-passage-0023`)
- In children, total product count did not predict higher parabens, although sunscreen and hair-care use had product-specific paraben associations. (`PMC4724203`, `claim-pmc4724203-004`, `sources/markdown/PMC4724203.md#BioC-passage-0040`)
- High product users had higher concentrations of every measured metabolite and paraben, including propyl paraben 219 percent higher and MBP 61 percent higher than low users. (`PMC4016195`, `claim-pmc4016195-005`, `sources/markdown/PMC4016195.md#BioC-passage-0035`)
- Daily hair-oil use near 36 weeks was associated with 8.3 fewer gestational days after adjustment for race. (`PMC8316883`, `claim-pmc8316883-003`, `sources/markdown/PMC8316883.md#BioC-passage-0046`)
- Salons providing acrylic services had significantly higher EMA concentrations than salons without acrylic services. (`PMC9566193`, `claim-pmc9566193-004`, `sources/markdown/PMC9566193.md#BioC-passage-0029`)
- Participants with higher urinary methylparaben reported using more supplements. (`PMC11764522`, `claim-pmc11764522-004`, `sources/markdown/PMC11764522.md#BioC-passage-0037`)
- Colgate Total use was associated with 86.7 percent higher urinary triclosan. (`PMC6037613`, `claim-pmc6037613-004`, `sources/markdown/PMC6037613.md#BioC-passage-0030`)
- Daily mouthwash users had higher MEP, BP3, methyl paraben, and propyl paraben than never-users. (`PMC5376243`, `claim-pmc5376243-002`, `sources/markdown/PMC5376243.md#BioC-passage-0022`)
- Cologne or perfume and deodorant were the strongest MEP predictors, while suntan or sunblock and body lotion were the strongest paraben predictors. (`PMC5783668`, `claim-pmc5783668-002`, `sources/markdown/PMC5783668.md#BioC-passage-0073`)
- DEP, DBP, and DEHP were detected in all 20 menstrual-blood samples, while BPA was detected in 13 samples. (`PMC9764248`, `claim-pmc9764248-002`, `sources/markdown/PMC9764248.md#BioC-passage-0032`)

### ensemble

N/A — ensemble component plan adaptive is invalid: paper identity mappings must contain canonical versioned arXiv IDs
