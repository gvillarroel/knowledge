# Semantic verifier checks

Each of the four cells declares one complete positive and six independently cloned negatives. A passing negative requires its exact semantic rejection before trusted-validator entry. Any other result stops the cell; remaining checks are unattempted.

| Strategy / records | Check | Observed status | Fixed diagnostic |
| --- | --- | --- | --- |
| Entity Graph / 9 | omitted-record | pass | record-omission-rejected |
| Entity Graph / 9 | altered-row-body | pass | authoritative-body-change-rejected |
| Entity Graph / 9 | wrong-logical-path | pass | logical-path-change-rejected |
| Entity Graph / 9 | missing-physical-document | pass | physical-document-omission-rejected |
| Entity Graph / 9 | missing-anchor-or-body | pass | anchor-or-body-omission-rejected |
| Entity Graph / 9 | unrelated-physical-body | pass | unrelated-physical-body-rejected |
| Ensemble / 9 | omitted-record | pass | record-omission-rejected |
| Ensemble / 9 | altered-row-body | pass | authoritative-body-change-rejected |
| Ensemble / 9 | wrong-logical-path | pass | logical-path-change-rejected |
| Ensemble / 9 | missing-physical-document | pass | physical-document-omission-rejected |
| Ensemble / 9 | missing-anchor-or-body | pass | anchor-or-body-omission-rejected |
| Ensemble / 9 | unrelated-physical-body | pass | unrelated-physical-body-rejected |
| Entity Graph / 18 | omitted-record | pass | record-omission-rejected |
| Entity Graph / 18 | altered-row-body | pass | authoritative-body-change-rejected |
| Entity Graph / 18 | wrong-logical-path | pass | logical-path-change-rejected |
| Entity Graph / 18 | missing-physical-document | pass | physical-document-omission-rejected |
| Entity Graph / 18 | missing-anchor-or-body | pass | anchor-or-body-omission-rejected |
| Entity Graph / 18 | unrelated-physical-body | pass | unrelated-physical-body-rejected |
| Ensemble / 18 | omitted-record | pass | record-omission-rejected |
| Ensemble / 18 | altered-row-body | pass | authoritative-body-change-rejected |
| Ensemble / 18 | wrong-logical-path | pass | logical-path-change-rejected |
| Ensemble / 18 | missing-physical-document | pass | physical-document-omission-rejected |
| Ensemble / 18 | missing-anchor-or-body | pass | anchor-or-body-omission-rejected |
| Ensemble / 18 | unrelated-physical-body | pass | unrelated-physical-body-rejected |

The anchor case removes a packed record anchor in the mixed fixture; in the single fixture it removes the physical body. The unrelated decoy retains frontmatter and packed anchors while replacing the body at the required physical path.

Twenty-nine owner pure-preparation checks, fourteen independent record/document prefix checks, and twenty-six independent mutation/control checks preceded admission. They exercised handwritten or independently assembled parser specimens and fake-evaluator control. The complete native evaluator and trusted validator had not run before the one-use study; this report supplies the later native outcome.

[General report](README.md) · [CTA](cta.md)
