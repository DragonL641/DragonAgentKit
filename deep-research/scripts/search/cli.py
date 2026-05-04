#!/usr/bin/env python3
"""CLI entry point for the built-in search engine. Output compatible with search-cli."""
from __future__ import annotations
import sys
import json
import argparse
import asyncio
from dataclasses import asdict
from . import search as do_search

def main() -> None:
    parser = argparse.ArgumentParser(description="Built-in multi-provider search engine")
    parser.add_argument("query", help="Search query")
    parser.add_argument("-m", "--mode", default="auto",
                        help="Search mode (auto/general/news/academic/deep/people)")
    parser.add_argument("-p", "--providers", nargs="+", help="Specific providers to use")
    parser.add_argument("-c", "--count", type=int, default=10, help="Number of results")
    parser.add_argument("--json", action="store_true", default=True, help="JSON output (always on)")
    args = parser.parse_args()

    resp = asyncio.run(do_search(args.query, args.mode, args.providers, args.count))
    print(json.dumps(asdict(resp), indent=2, ensure_ascii=False))

    if resp.status == "error":
        if "no providers" in resp.metadata.get("error", ""):
            sys.exit(3)  # auth_missing
        sys.exit(1)  # runtime error
    sys.exit(0)

if __name__ == "__main__":
    main()
