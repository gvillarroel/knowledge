# Knowledge CLI: repository guide

`know` builds local knowledge collections from registered external sources and exports normalized Markdown libraries. A project-local `.know/` store keeps source registrations, synchronized inputs, metadata, and repeatable export workflows together.

## Layout

| Path | Responsibility |
| --- | --- |
| `src/knowledge/` | CLI, store model, source adapters, and export implementation. |
| `tests/` | Unit and integration coverage. |
| `scripts/` | Coverage gate and maintenance helpers. |
| `docs/` | CLI reference, source workflows, and engineering guides. |
| `skills/` | Self-contained knowledge builder and consultation bundles. |
| `evaluations/` | Governed datasets, study contracts, and reviewed evidence. |
| `.specs/adr/` | Architecture and evidence decisions. |

## Documentation policy

- Keep the root `README.md` focused on purpose, critical constraints, and the first useful action. Put detailed procedures in `docs/`.
- Maintain `docs/README.md` as the navigation index whenever a guide is added or moved.
- Preserve existing specification, ADR, skill-contract, and evidence locations. Link to their owners instead of copying authoritative content.
- Keep implementation, configuration, source data, and generated output separate. Do not create empty folder hierarchies without a concrete need.
- Use portable relative links. Update both outgoing links and inbound references when moving a document.
- Document prerequisites, commands, expected outcomes, and limitations. Never describe an unrun check as verified.

## Change workflow

1. Read `AGENTS.md`, this index, and the relevant source contract.
2. Inspect `git status` and preserve pre-existing changes and staged files.
3. Make a focused change and update affected documentation in the same change.
4. Run the applicable checks below, inspect the diff, and record any unavailable prerequisite.
5. Stage explicit paths. Publish only when authorized; do not force-push or merge unrelated work.

## Validation

```sh
python scripts/check_coverage.py --threshold 80
```

For a clean checkout with `uv`, keep the application lock unchanged and provide the test-only dependencies explicitly:

```sh
uv run --locked --python 3.12 --with pytest --with pypdf python scripts/check_coverage.py --threshold 80
```

Review both the pytest summary and the coverage total. The existing `trace` wrapper can print a successful coverage gate even when the pytest summary contains failures; coverage alone is not a passing test suite. Some repository study tests require private, ignored fixtures or external runtimes that a clean clone does not contain. Do not copy private evidence into Git or weaken a test to make a documentation change pass. Record unavailable inputs and report test failures separately from the coverage percentage.

Use the project environment with test dependencies installed. The repository requires at least 80% total application coverage before task closure; preserve any stricter requirement in `SPEC.md` for broader implementation work.

## Data and operating boundaries

Keep corpus contents, credentials, raw provider responses, and native evaluation traces out of general documentation. Preserve sealed evidence and independent validation boundaries; this repository organization work does not authorize new model runs or study promotion.

[Back to the documentation index](README.md).
