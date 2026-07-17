# Bootstrap and Shell-Isolation Technical Preflight

Status: **pass as a non-causal technical preflight**.

The treatment-only q031 run `2026-07-15T15-19-09-193Z-compare`
(`eval-jpH-2026-07-15T15:19:14`) completed one requested answer with no provider
error. It is not a control/treatment comparison and contributes no causal or
portfolio metric.

The retained trace proves the new runtime boundary:

- zero command- or shell-execution events;
- one first `semantic_okf_bootstrap_skill` call bound to the frozen
  `SKILL.md` SHA-256 `ec80687b…` and 15,699 UTF-8 bytes;
- the canonical `semantic-okf-shell-isolation-receipt/1.0` with
  `shell_tool_disabled: true`;
- one successful inspect, all five deterministic q031 coverage pages, one
  preparation, and one terminal digest confirmation; and
- exact publication of the prepared 8,872-byte candidate at SHA-256
  `a6bf8dfd…`.

The raw agent message differed from the prepared candidate, so the host publication
gate applied a real correction. The visible Promptfoo output nevertheless matched the
prepared envelope digest, confirmation receipt, and candidate bytes exactly. All five
Promptfoo assertions passed: response format, response contract, evidence validity,
atomic answer completeness, and important-negative coverage.

This preflight establishes that MCP v1.5.0 can load the frozen skill without general
shell access and can preserve confirmed answer bytes in the real provider. Only the
fresh complete three-arm 90-answer execution and its independent attestation can
establish comparative answer results.
