# Search Syntax

Use concise arXiv queries. Prefer exact phrases and fielded queries over long keyword bags.

## Useful patterns

- Exact phrase:
  `"multi-agent systems"`
- Title-only:
  `ti:"transformer architecture"`
- Author:
  `au:"Hinton"`
- Abstract:
  `abs:"attention mechanism"`
- Exclusion:
  `"deep learning" ANDNOT "survey"`

## Categories

The scripts validate category prefixes. Common categories:

- `cs.AI`
- `cs.MA`
- `cs.LG`
- `cs.CL`
- `cs.CV`
- `cs.RO`
- `stat.ML`
- `math.OC`

## Date filtering

Use `YYYY-MM-DD` for `--date-from` and `--date-to`.

Examples:

- recent work:
  `--date-from 2023-01-01`
- historical work:
  `--date-to 2015-12-31`
- bounded range:
  `--date-from 2018-01-01 --date-to 2020-12-31`

The search script uses the raw arXiv export API for date-filtered searches so the `submittedDate:[...+TO+...]` clause stays valid.
