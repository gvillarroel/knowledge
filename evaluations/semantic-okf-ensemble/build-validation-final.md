# Definitive Ensemble Build Validation

Status: **pass**.

The final standalone builder processed the same pinned 31-source input: 15 Markdown papers, 15 reviewed claim JSONL files, and the separately declared analysis vocabulary. It published only derived, non-authoritative discovery artifacts and preserved the authoritative Semantic OKF core.

| Gate | Result |
| --- | --- |
| Exact source selection | 31/31 declared sources |
| Authoritative records | 874 |
| Authoritative core tree SHA-256 | `331af2f1064463484f64dfaa58bc17d6c6b2f75ef3fca9d371473450deb84424` |
| Ensemble index SHA-256 | `9ce8bac88df8621fd870d718d1166e706516f4c4d56497eecc080d454453e939` |
| Canonical plan SHA-256 | `cbbc28d140667670621260513d08998a740227f2bdf93f4dce754f4c996dd8eb` |
| Independent validation | pass for both builds |
| Deterministic rebuild | 904 files versus 904 files; zero path or digest differences |
| Publication boundary | one validated private candidate followed by one atomic publication |

The raw build directories remain append-only and ignored under run `20260715-ensemble-final-03`. The compact machine-readable binding is [build-validation-final.json](build-validation-final.json).
