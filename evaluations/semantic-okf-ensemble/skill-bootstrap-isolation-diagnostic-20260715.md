# Skill-Bootstrap Isolation Diagnostic

Status: **rejected diagnostic; zero accepted benchmark rows**.

The MCP v1.4.0 comparison `2026-07-15T14-29-07-959Z-compare`
(`eval-T27-2026-07-15T14:29:15`) was stopped after 17 of 90 planned answers had
persisted: six knowledge-only control rows, six adaptive-control rows, and five
ensemble-treatment rows. None of those rows contributes to the definitive answer
comparison.

The stopping row was treatment q032, repetition index 4. Before the governed MCP
sequence, Codex successfully executed one read-only command equivalent to:

```powershell
Get-Content -LiteralPath '<isolated CODEX_HOME>/skills/consult-semantic-okf-ensemble/SKILL.md' -Raw
```

The command read the exact mounted skill body; PowerShell added one terminal CRLF to
its captured output. Inspect, coverage, preparation, digest confirmation, and exact
host publication then completed. The row also passed response-contract, evidence-
validity, and important-negative assertions, but missed one exact atomic evidence
option. Those assertion outcomes are diagnostic details, not accepted answer scores.

## Why the run was rejected

Skill Arena installs the selected skill and exposes its identity and path, but does
not place the complete `SKILL.md` body in model context. Codex therefore used the
ordinary shell to load the instructions. The frozen v1.4.0 trace contract required
zero treatment command-execution events. Post-hoc classification of this command as
harmless would weaken that predeclared isolation gate, so the runner stopped and the
entire partial execution was rejected.

## Replacement design

MCP v1.5.0 adds the no-argument `semantic_okf_bootstrap_skill` operation. It resolves
only the installed ensemble skill under `CODEX_HOME`, rejects path escape and links,
verifies the frozen raw-byte SHA-256 and length, and returns the strict UTF-8 body in
the closed `semantic-okf-skill-bootstrap/1.0` envelope. It can succeed only once and
must precede inspect. The treatment host disables the general shell tool before
Codex starts; controls retain the baseline command behavior. The independent attestor
requires the five-tool sequence and zero treatment command-execution events.

This is a change to the complete definitive consultation capability, not a pure
skill-text ablation. Only a fresh 90-answer run under the new frozen contract can
supply causal or answer-quality results.
