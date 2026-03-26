from __future__ import annotations

import argparse

try:
    from scripts.common import list_cached_papers, print_json, resolve_storage_path
except ModuleNotFoundError:
    from common import list_cached_papers, print_json, resolve_storage_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="List cached arXiv papers.")
    parser.add_argument("--storage-path")
    parser.add_argument("--include-metadata", action="store_true")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    result = list_cached_papers(
        storage_path=resolve_storage_path(args.storage_path),
        include_metadata=args.include_metadata,
    )
    print_json(result)


if __name__ == "__main__":
    main()
