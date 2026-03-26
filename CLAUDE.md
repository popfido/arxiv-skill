# CLAUDE.md

`arxiv-skill` is a repository-root Agent Skill for working with arXiv papers.

## Repository layout

- `SKILL.md`
  Canonical skill instructions and metadata.
- `scripts/common.py`
  Shared storage, search, parsing, and cache helpers.
- `scripts/search_arxiv.py`
  Search entrypoint.
- `scripts/cache_paper.py`
  Cache-and-convert entrypoint.
- `scripts/list_cached_papers.py`
  Local inventory entrypoint.
- `scripts/read_cached_paper.py`
  Cached markdown reader.
- `references/`
  Supporting documentation used by the skill when deeper context is needed.
- `assets/examples/`
  Small example artifacts.

## Development commands

Install dependencies:

```bash
uv sync --all-extras --dev
```

Run tests:

```bash
./.venv/bin/python -m pytest
```

Run formatting check:

```bash
./.venv/bin/black --check scripts tests
```

Validate the skill:

```bash
./.venv/bin/agentskills validate "$(pwd)"
```

## Editing expectations

- Keep the skill structure compliant.
- Prefer direct, testable script behavior.
- Keep documentation aligned across `SKILL.md`, `README.md`, `AGENTS.md`, and `CLAUDE.md`.
- Preserve the repo-local cache default unless there is a strong reason to change it.
- Add depth in `references/` rather than bloating `SKILL.md`.
