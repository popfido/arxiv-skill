from __future__ import annotations

import argparse

try:
    from scripts.common import print_json, read_cached_paper, resolve_storage_path
except ModuleNotFoundError:
    from common import print_json, read_cached_paper, resolve_storage_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Read cached arXiv markdown.")
    parser.add_argument("--paper-id", required=True)
    parser.add_argument("--storage-path")
    parser.add_argument("--format", choices=["json", "raw"], default="json")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    result = read_cached_paper(
        paper_id=args.paper_id,
        storage_path=resolve_storage_path(args.storage_path),
    )
    if args.format == "raw":
        print(result["content"])
        return
    print_json(result)


if __name__ == "__main__":
    main()
