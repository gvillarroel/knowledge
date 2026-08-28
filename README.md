# Knowledge CLI

`know` builds local knowledge collections from registered external sources and exports normalized Markdown libraries. A project-local `.know/` store keeps source registrations, synchronized inputs, metadata, and repeatable export workflows together.

Store selection is explicit `--store`, then the nearest project `.know/`, then the global fallback. Source synchronization may access authenticated services; use the source-specific guide first.

## Get started

Requires Python 3.11 or later and uv. Use Python 3.12 for the documented Windows browser-assisted capture workflow.

```sh
uv tool install --python 3.12 .
know --help
```

Run `know init` in the project that should own a collection, not in this source checkout unless that is intentional.

## Documentation

- [Documentation index](docs/README.md)
- [Usage and operations](docs/getting-started.md)
- [Repository layout and validation](docs/repository-guide.md)
- [CLI reference](docs/cli.md)
- [Specification](SPEC.md)
- [Knowledge skill evolution playbook](docs/knowledge-skill-evolution-playbook.md)
- [AGENTS.md](AGENTS.md)
