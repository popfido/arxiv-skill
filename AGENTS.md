# AGENTS.md

This repository contains the `arxiv-skill` Agent Skill for arXiv search, local paper caching, and structured paper analysis.

## Working model

The repository is organized around:

- `SKILL.md`
  Root skill metadata and workflow guidance.
- `scripts/`
  Direct entrypoints for search, caching, listing, and reading.
- `references/`
  On-demand documentation for search syntax, storage behavior, workflow, and analysis structure.
- `tests/`
  Structure and script-level tests.

## Development commands

Environment setup:

```bash
uv sync --all-extras --dev
```

Run tests:

```bash
./.venv/bin/python -m pytest
```

Check formatting:

```bash
./.venv/bin/black --check scripts tests
```

Validate the skill:

```bash
./.venv/bin/agentskills validate "$(pwd)"
```

## Script surface

- `scripts/search_arxiv.py`
  Search arXiv with query, category, and optional date filters.
- `scripts/cache_paper.py`
  Download a paper by arXiv ID and convert it to cached markdown.
- `scripts/list_cached_papers.py`
  List cached markdown files, with optional metadata lookup.
- `scripts/read_cached_paper.py`
  Read cached markdown as JSON or raw text.

Shared logic lives in `scripts/common.py`.

## Repository expectations

- Keep `SKILL.md` concise.
- Put detailed procedural material in `references/`.
- Keep script outputs deterministic and JSON-friendly where appropriate.
- Keep the default cache path workspace-local.
- Use tests to validate script behavior, not just helper functions.
