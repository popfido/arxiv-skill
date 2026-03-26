from __future__ import annotations

import argparse

try:
    from scripts.common import cache_paper, print_json, resolve_storage_path
except ModuleNotFoundError:
    from common import cache_paper, print_json, resolve_storage_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Cache an arXiv paper locally.")
    parser.add_argument("--paper-id", required=True)
    parser.add_argument("--storage-path")
    parser.add_argument("--keep-pdf", action="store_true")
    parser.add_argument("--force", action="store_true")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    result = cache_paper(
        paper_id=args.paper_id,
        storage_path=resolve_storage_path(args.storage_path),
        keep_pdf=args.keep_pdf,
        force=args.force,
    )
    print_json(result)


if __name__ == "__main__":
    main()
