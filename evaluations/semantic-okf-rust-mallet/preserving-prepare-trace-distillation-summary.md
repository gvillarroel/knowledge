# RustMallet Preserving-Prepare Trace Distillation

## Outcome

Retain the live reference-aware RustMallet consultant. The trace-backed
preserving-prepare candidate passed candidate development, but its untouched
q005/q020 holdout was not evaluable under the frozen promotion rules. One q020
candidate trial exited with code 137, and q005 failed the required mechanical
qualification gate for both baseline and candidate.

## Candidate

Two successful discovery traces supported a narrow change that combines the
existing compact search with opening the selected authoritative text. It keeps
all recommended rows, retrieval interpretations, the minimum-through-minimum-
plus-two breadth buffer, and the original `search`, `show`, and `finalize`
commands. The isolated candidate digest is
`sha256:7e145adb6c8a0ada14a43fe73fef257c24656aa9b00653e0d3d5f7ea61358f0f`.

Local quick validation, Python compilation, and a real q007 preparation passed.
The preparation returned six recommendations and six matching selected texts
for a minimum of four in 76.6 seconds, including PowerShell, WSL launch, and
two snapshot loads.

## Harbor result

Harbor 0.18.0 used Pi 0.73.1,
`github-copilot/gpt-5.3-codex`, `thinking: high`, and zero retries.
Development reused q007 and q019 with the exact discovery task checksums. Both
trials were evaluable and qualified:

| Task | Reward | Trial wall time |
| --- | ---: | ---: |
| q007 | 0.840638 | 153.68 s |
| q019 | 0.853419 | 162.61 s |
| Mean | 0.847029 | 158.15 s |

The passed development gate opened the untouched q005/q020 holdout with two
attempts per task:

| Cell | Baseline mean | Candidate mean | Result |
| --- | ---: | ---: | --- |
| q005 | 0.000000 | 0.000000 | mechanical gate was 0 on both sides |
| q020 | 0.792797 | not evaluable | one reward 0.780397; one exit 137 |
| Overall | 0.396399 | not evaluable | candidate had one error |

Baseline holdout trials took 168.58–181.29 seconds each, 695.13 seconds summed.
Candidate trials took 150.46–212.46 seconds each, 704.89 seconds summed. Timing
cannot compensate for a missing semantic reward or a failed required gate.

## Decision

Do not copy the candidate into
`skills/consult-semantic-okf-rust-mallet-evolved`. The strict gate required a
mean gain of at least 0.01, no per-task regression, no candidate errors, and
both non-compensating gates at 1.0. The holdout satisfied none of the conditions
needed to turn its partial candidate evidence into a promotion decision.
