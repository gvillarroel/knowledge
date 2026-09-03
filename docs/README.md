# Documentation Index

## Start here

- [Usage and setup](getting-started.md)
- [Repository layout, maintenance, and validation](repository-guide.md)
- [Agent instructions](../AGENTS.md)
- [CLI reference](cli.md)
- [ServiceNow tickets and knowledge-base synchronization](servicenow.md)
- [Reliable Confluence synchronization](confluence-sync.md)
- [Specification](../SPEC.md)
- [Knowledge skill evolution playbook](knowledge-skill-evolution-playbook.md)


This directory is the canonical documentation set for the `know` CLI.

Everything in this folder is intended to be readable on its own, with links that stay inside `docs/`.

## Start Here

- [cli.md](cli.md): main user guide, workflows, store layout, source behavior, and operational examples
- [COMMANDS.md](COMMANDS.md): compact command reference
- [TVs.md](TVs.md): Television integration guide and `tv` workflows
- [site-spikes.md](site-spikes.md): benchmark and strategy-comparison guide for site capture experiments
- [know-skill.md](know-skill.md): contributor and agent working conventions for this project
- [knowledge-skill-evolution-playbook.md](knowledge-skill-evolution-playbook.md): ordered strategy for building, evaluating, evolving, and promoting evidence-bound knowledge skills

## Suggested Reading Paths

### I want to use the CLI

1. Read [cli.md](cli.md)
2. Keep [COMMANDS.md](COMMANDS.md) open as a quick reference

### I want to use Television

1. Read the Television sections in [cli.md](cli.md)
2. Read [TVs.md](TVs.md) for bundled channels, inline usage, and custom channel registration

### I want browser-assisted site capture

1. Read the site capture sections in [cli.md](cli.md)
2. Read [site-spikes.md](site-spikes.md) only if you need strategy comparison or benchmarking

### I want to modify the project safely

1. Read [know-skill.md](know-skill.md)
2. Use [cli.md](cli.md) and [COMMANDS.md](COMMANDS.md) as the behavior contract for user-facing command shape

### I want to create or improve a knowledge skill

1. Read [knowledge-skill-evolution-playbook.md](knowledge-skill-evolution-playbook.md)
2. Author disjoint task families and replayable adapter variations with the
   [`harbor-author-evaluation-datasets` skill](../skills/harbor-author-evaluation-datasets/SKILL.md)
3. Select the knowledge builder and artifact boundary before choosing an evolution strategy
4. Keep only development optimizer-visible; release sealed validation once for
   the frozen winner, then use optional holdout only when the study declares it

## Documentation Conventions

- `cli.md` is the primary narrative guide.
- `COMMANDS.md` is the terse lookup reference.
- `TVs.md` is focused only on Television usage.
- `site-spikes.md` is focused only on site capture experiments.
- `know-skill.md` explains contributor expectations and documentation maintenance rules.
- `knowledge-skill-evolution-playbook.md` defines the evidence and skill order for knowledge-skill creation, evaluation, evolution, and promotion.
