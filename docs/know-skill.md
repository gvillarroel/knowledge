# Know Skill

The repository includes a Codex skill at `skills/know/SKILL.md` to guide work on the `know` CLI.

Use this skill when changing the Python CLI, aligning behavior with `SPEC.md`, updating the local knowledge store structure, or extending tests and documentation for command behavior.

The skill instructs agents to:

- read `SPEC.md` first;
- keep all documentation in English;
- focus changes on the `know` command family and store semantics;
- update tests for every CLI or metadata change;
- run `pytest` after implementation.

The skill is also the right place to check expected patterns for Television-oriented documentation and examples, including:

- `know add television ... --source-command ... --preview-command ...`
- `know list keys --format television`
- `know list sources --format television`
- `know search arxiv ... --format television`

This document exists for human discoverability. The executable instructions for Codex live in `skills/know/SKILL.md`.
