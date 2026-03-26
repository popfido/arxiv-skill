# Workflow Guide

## Search a topic

```bash
python scripts/search_arxiv.py --query '"transformer architecture"' --max-results 5
```

## Search with categories

```bash
python scripts/search_arxiv.py --query '"multi-agent systems"' --categories cs.AI cs.MA --max-results 10
```

## Search a historical date range

```bash
python scripts/search_arxiv.py \
  --query 'ti:"belief desire intention"' \
  --date-from 1995-01-01 \
  --date-to 2010-12-31 \
  --max-results 10
```

## Cache a paper locally

```bash
python scripts/cache_paper.py --paper-id 2401.12345
```

## Cache a paper and keep the PDF

```bash
python scripts/cache_paper.py --paper-id 2401.12345 --keep-pdf
```

## List cached papers only

```bash
python scripts/list_cached_papers.py
```

## List cached papers with metadata lookup

```bash
python scripts/list_cached_papers.py --include-metadata
```

## Read cached markdown as raw text

```bash
python scripts/read_cached_paper.py --paper-id 2401.12345 --format raw
```

## Read cached markdown as JSON

```bash
python scripts/read_cached_paper.py --paper-id 2401.12345 --format json
```

## Analyze a paper

1. Search or confirm the paper ID.
2. Cache the paper if it is not already available.
3. Read the cached markdown.
4. If the answer would benefit from comparison, search for related work.
5. Use [analysis-framework.md](analysis-framework.md) for the final structure.
