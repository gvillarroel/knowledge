# Knowledge Methodology Reviewer

This project-scoped agent contract defines a read-only methodology reviewer whose complete default and allowed skill set is `review-knowledge-methodology`.

The contract is intentionally local and product-neutral. A compatible runner should load [agent.json](agent.json), apply [AGENTS.md](AGENTS.md), and expose only the listed skill. The reviewer cannot modify the repository or acquire new sources; corpus refresh and implementation remain separate workflows.
