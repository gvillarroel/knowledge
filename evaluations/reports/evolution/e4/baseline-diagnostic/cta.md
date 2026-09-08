# Baseline cost, time and accuracy diagnostics

[Baseline report](README.md) · [CTA CSV](cta.csv) · [All routes](routes.csv)

The native experiment records zero instruction-model tokens and provider charge. Local computing is not priced. Each construction measurement includes two validated builds. Agent time also includes snapshot initialization and all declared routes; native trial time includes setup and verification. These timings describe the full evaluation under a two-CPU container limit and up to two concurrent trials, not one production query. This baseline was excluded from evolution by the controller's identity check.

| Dataset | Family | Default nDCG@10 | Query P95 ms | Double build s | Agent s, all routes | Native trial s | Knowledge MiB |
|---|---|---:|---:|---:|---:|---:|---:|
| architecture | adaptive | 85.61 | 1745.95 | 131.32 | 196.47 | 237.68 | 145.49 |
| architecture | classical | 92.58 | 729.62 | 144.91 | 272.69 | 314.66 | 164.23 |
| architecture | embeddings | 72.38 | 409.04 | 11.84 | 43.39 | 88.30 | 36.53 |
| architecture | ensemble | 85.01 | 5328.75 | 608.50 | 1036.26 | 1081.52 | 437.13 |
| architecture | entity-graph | 83.50 | 2931.74 | 206.18 | 651.48 | 695.59 | 303.62 |
| architecture | graphify | 57.76 | 93.54 | 15.75 | 20.54 | 66.73 | 31.10 |
| architecture | legacy | 81.55 | 0.22 | 5.15 | 6.75 | 50.87 | 24.27 |
| architecture | turso | 58.40 | 352.11 | 14.58 | 27.03 | 69.46 | 73.29 |
| astro | adaptive | 83.34 | 2591.38 | 47.20 | 108.42 | 149.03 | 32.77 |
| astro | classical | 83.34 | 73.61 | 46.64 | 60.34 | 100.65 | 32.77 |
| astro | embeddings | 78.52 | 94.12 | 26.13 | 34.39 | 76.58 | 12.41 |
| astro | ensemble | 82.62 | 3738.00 | 249.32 | 527.78 | 572.05 | 138.36 |
| astro | entity-graph | 69.47 | 1035.23 | 87.09 | 243.47 | 284.00 | 109.50 |
| astro | graphify | 57.79 | 140.27 | 36.34 | 41.77 | 85.93 | 16.96 |
| astro | legacy | 60.52 | 2.55 | 16.97 | 18.03 | 62.78 | 8.37 |
| astro | turso | 47.81 | 138.51 | 19.41 | 23.54 | 64.44 | 31.10 |
| data-science | adaptive | 91.78 | 2684.98 | 245.83 | 350.83 | 393.62 | 253.92 |
| data-science | classical | 80.54 | 1023.25 | 260.32 | 431.24 | 474.44 | 253.92 |
| data-science | embeddings | 60.04 | 803.66 | 21.23 | 83.57 | 126.87 | 75.41 |
| data-science | ensemble | 92.78 | 9928.14 | 1202.02 | 2010.13 | 2051.94 | 874.73 |
| data-science | entity-graph | 85.79 | 6874.66 | 455.14 | 1554.86 | 1597.47 | 645.60 |
| data-science | graphify | 54.41 | 344.84 | 37.10 | 52.61 | 94.78 | 71.21 |
| data-science | legacy | 83.22 | 0.54 | 8.50 | 10.82 | 52.66 | 50.12 |
| data-science | turso | 40.16 | 483.03 | 28.93 | 48.70 | 89.05 | 151.46 |
| enterprise | adaptive | 50.34 | 1344.75 | 60.60 | 94.27 | 135.21 | 7.64 |
| enterprise | classical | 43.42 | 41.38 | 60.24 | 65.97 | 109.95 | 7.64 |
| enterprise | embeddings | 51.64 | 46.07 | 64.40 | 68.79 | 112.22 | 6.84 |
| enterprise | ensemble | 55.35 | 1508.28 | 236.85 | 342.18 | 382.49 | 19.07 |
| enterprise | entity-graph | 46.73 | 49.85 | 62.78 | 70.42 | 112.98 | 13.21 |
| enterprise | graphify | 13.63 | 130.67 | 132.34 | 136.26 | 176.01 | 14.25 |
| enterprise | legacy | 57.50 | 3.26 | 36.05 | 37.00 | 78.93 | 4.71 |
| enterprise | turso | 40.32 | 37.86 | 40.29 | 42.13 | 83.36 | 22.82 |
