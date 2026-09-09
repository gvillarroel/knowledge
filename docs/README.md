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
- [Skill evolution roadmap: current rankings, candidate priorities, and independent validation](knowledge-skill-evolution-roadmap.md)
- [Native retrieval-profile evolution: execution, isolation, and one-way validation](retrieval-profile-evolution.md)
- [Combined development comparisons across generations](retrieval-profile-evolution.md#compare-both-generations)
- [Exact source copies of the native campaign helpers](../evaluations/skill-evolution/campaign-tools/README.md)
- [Native generation preflight and complete merge lineage](../.specs/adr/0120-preflight-native-profile-and-complete-merge-lineage.md)
- [Interrupted evolution: evidence preservation and terminal closure](../.specs/adr/0121-preserve-interrupted-evolution-without-manufacturing-completion.md)
- [Enterprise evolution: three consecutive misses per strategy and all eight knowledge families](enterprise-evolution-sweep.md)
- [Enterprise evolution campaign status and reports](../evaluations/reports/evolution/e6/README.md)
- [Stratified Enterprise evolution across eight families and the all-500 internal comparison](enterprise-stratified-evolution.md)
- [Classical application-group diversity limit and an untested document-identity follow-up](../evaluations/reports/evolution/e7/classical-source-cap-001/README.md)
- [Ensemble protected-set audit: ranking changes and the coverage boundary](../evaluations/reports/evolution/e7/ensemble-protection-001/README.md)
- [Graphify function audit: traversal reach, ranking changes, and exact fusion treatments](../evaluations/reports/evolution/e7/graphify-opportunity-001/README.md)
- [Entity Graph function audit: graph reach, rank-based fusion, and document grouping](../evaluations/reports/evolution/e7/entity-graph-opportunity-001/README.md)
- [Stratified Enterprise development CTA: completed-job time, failures, and missing usage](../evaluations/reports/evolution/e7/development-cta-001/README.md)
- [Completed Enterprise application-skill experiment: findings and retained ingestion checks](enterprise-source-skills.md)
- [Generator evolution: explicit source selection and independent construction acceptance](../.specs/adr/0126-evolve-generator-explicit-source-selection.md)
- [Using and evaluating the evolved knowledge-skill generator](knowledge-generator-evolution.md)
- [EnterpriseRAG comparison of the incoming and G2 generators](enterprise-generator-comparison.md)
- [Enterprise historical title-only ingestion scope correction](../evaluations/reports/enterprise-source-skills/ingestion-scope-20260907.md)
- [Unavailable semantic review pairs: paired exclusion and full-cohort bounds](../.specs/adr/0124-report-unavailable-semantic-review-pairs.md)
- [Local evaluation datasets, EnterpriseRAG-Bench, and reports by skill](evaluation-datasets-and-reports.md)
- [EnterpriseRAG public leaderboard and external strategy results](../evaluations/enterprise-rag-bench/reports/public-results-20260906.md)
- [Full-corpus EnterpriseRAG with Classical and official answer scoring](enterprise-classical-full-corpus.md)


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
2. Review the [current evolution roadmap and readiness audit](knowledge-skill-evolution-roadmap.md)
3. Author disjoint task families and replayable adapter variations with the
   [`harbor-author-evaluation-datasets` skill](../skills/harbor-author-evaluation-datasets/SKILL.md)
4. Select the knowledge builder and artifact boundary before choosing an evolution strategy
5. Keep only development optimizer-visible; release sealed validation once for
   the frozen winner, then use optional holdout only when the study declares it

## Documentation Conventions

- `cli.md` is the primary narrative guide.
- `COMMANDS.md` is the terse lookup reference.
- `TVs.md` is focused only on Television usage.
- `site-spikes.md` is focused only on site capture experiments.
- `know-skill.md` explains contributor expectations and documentation maintenance rules.
- `knowledge-skill-evolution-playbook.md` defines the evidence and skill order for knowledge-skill creation, evaluation, evolution, and promotion.
