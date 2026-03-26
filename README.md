# arxiv-skill

`arxiv-skill` is a pure Agent Skill for arXiv discovery and paper analysis.

This skill is descended from the original MCP-based implementation in
[`blazickjp/arxiv-mcp-server`](https://github.com/blazickjp/arxiv-mcp-server),
adapted into a standalone Agent Skill workflow.

It provides:

- `SKILL.md` as the root instruction surface
- direct scripts for search, caching, listing, and reading
- reference material for search syntax, storage behavior, workflows, and analysis structure

## Use cases

Use this repository when an agent needs to:

- search arXiv with topic, category, and date filters
- cache a paper locally as markdown
- inspect or read cached papers
- perform structured paper analysis or literature review

## Structure

```text
arxiv-skill/
├── SKILL.md
├── scripts/
├── references/
├── assets/
└── tests/
```

## Setup

```bash
uv sync --all-extras --dev
```

## Core commands

Search:

```bash
python scripts/search_arxiv.py --query '"transformer architecture"' --max-results 5
```

Cache a paper:

```bash
python scripts/cache_paper.py --paper-id 2401.12345
```

List cached papers:

```bash
python scripts/list_cached_papers.py
```

Read cached markdown:

```bash
python scripts/read_cached_paper.py --paper-id 2401.12345 --format raw
```

## Validation

Run the test suite:

```bash
./.venv/bin/python -m pytest
```

Validate the skill structure:

```bash
./.venv/bin/agentskills validate "$(pwd)"
```

## Skill entrypoint

The canonical skill instructions live in `SKILL.md`. Supporting details live in:

- `references/workflow.md`
- `references/search-syntax.md`
- `references/storage-format.md`
- `references/analysis-framework.md`

## License

Apache License 2.0. See `LICENSE`.
