# Contributor Workflow

This document explains the working conventions for contributors and agents who modify the `know` CLI.

It is not a command reference. Use the rest of `docs/` as the product contract:

- [README.md](README.md): documentation map
- [cli.md](cli.md): primary behavior and workflow guide
- [COMMANDS.md](COMMANDS.md): compact command reference
- [TVs.md](TVs.md): Television-specific usage
- [site-spikes.md](site-spikes.md): site capture benchmarking

## Scope

When you change this project, keep the work aligned with the documented behavior of:

- the `know` command family
- the local knowledge store layout
- sync, export, and browse workflows
- Television integration patterns
- site capture strategy selection and documentation

## Working Rules

- Keep all human-facing documentation in English.
- Prefer small, explicit command shapes over implicit behavior.
- Preserve stable command naming and argument patterns when extending the CLI.
- Update tests for every user-visible behavior change.
- Update documentation in the same change when command shape, defaults, or workflows change.
- Keep examples realistic and runnable.
- Preserve Open Knowledge Format compatibility for exported Markdown concept documents.
- Keep native skill frontmatter limited to `name` and `description`; regenerate the strict project-and-skills projection under `okf/` after changing any skill.

## Validation Expectations

Before closing work:

- run the relevant test suite
- run the repository coverage gate
- confirm the documentation still matches the implemented behavior
- validate OKF-sensitive changes with tests that inspect generated frontmatter
- run the project bundle drift check and strict validator after project or skill documentation changes

The default validation gate used in routine work is:

```bash
python scripts/check_coverage.py --threshold 80
python skills/open-knowledge-format/scripts/build_project_okf_bundle.py . --output okf --check
python skills/open-knowledge-format/scripts/validate_okf_bundle.py okf
```

## Documentation Maintenance Rules

- Keep cross-links inside `docs/`.
- Do not make `docs/` depend on reading repository-level documents first.
- Put narrative workflows in [cli.md](cli.md).
- Put terse lookup material in [COMMANDS.md](COMMANDS.md).
- Put `tv` usage in [TVs.md](TVs.md).
- Put site strategy comparison material in [site-spikes.md](site-spikes.md).

## Television Documentation Patterns

When documenting Television usage, prefer the existing command shapes:

- `know add tv ... --source-command ... --preview-command ...`
- `know list keys --format television`
- `know list sources --format television`
- `know search arxiv ... --format television`
- `know browse ... --format television`
