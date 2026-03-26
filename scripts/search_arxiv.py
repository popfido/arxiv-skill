from __future__ import annotations

import argparse

try:
    from scripts.common import print_json, search_papers
except ModuleNotFoundError:
    from common import print_json, search_papers


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Search arXiv papers.")
    parser.add_argument("--query", required=True)
    parser.add_argument("--max-results", type=int, default=10)
    parser.add_argument("--date-from")
    parser.add_argument("--date-to")
    parser.add_argument("--categories", nargs="*", default=[])
    parser.add_argument("--sort-by", choices=["relevance", "date"], default="relevance")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    result = search_papers(
        query=args.query,
        max_results=args.max_results,
        date_from=args.date_from,
        date_to=args.date_to,
        categories=args.categories,
        sort_by=args.sort_by,
    )
    print_json(result)


if __name__ == "__main__":
    main()
