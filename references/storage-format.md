# Storage Format

## Default cache root

The scripts cache papers under:

```text
.cache/arxiv-skill/papers
```

relative to the skill root.

## Override order

1. `--storage-path`
2. `ARXIV_SKILL_STORAGE_PATH`
3. default cache root

## File naming

For paper ID `2401.12345`:

- markdown:
  `.cache/arxiv-skill/papers/2401.12345.md`
- PDF:
  `.cache/arxiv-skill/papers/2401.12345.pdf`

## Cache behavior

- If markdown already exists, cache operations return success without re-downloading unless `--force` is used.
- PDFs are deleted after markdown conversion by default.
- Use `--keep-pdf` to retain the original PDF.
- Local inventory should work without network access unless metadata lookup is explicitly requested.
