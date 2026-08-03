from __future__ import annotations

import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="know")
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add")
    add_subparsers = add_parser.add_subparsers(dest="add_command", required=True)

    add_key_parser = add_subparsers.add_parser("key")
    add_key_parser.add_argument("name")

    add_confluence_parser = add_subparsers.add_parser("confluence")
    add_confluence_parser.add_argument("--space", required=True)
    add_confluence_parser.add_argument("--key", required=True)

    add_arxiv_parser = add_subparsers.add_parser("arxiv")
    add_arxiv_parser.add_argument("url")
    add_arxiv_parser.add_argument("--key", required=True)

    list_parser = subparsers.add_parser("list")
    list_subparsers = list_parser.add_subparsers(dest="list_command", required=True)
    list_subparsers.add_parser("keys")
    list_sources_parser = list_subparsers.add_parser("sources")
    list_sources_parser.add_argument("--key")

    search_parser = subparsers.add_parser("search")
    search_subparsers = search_parser.add_subparsers(dest="search_command", required=True)
    search_confluence_parser = search_subparsers.add_parser("confluence")
    search_confluence_parser.add_argument("query")

    sync_parser = subparsers.add_parser("sync")
    sync_parser.add_argument("--key")

    export_parser = subparsers.add_parser("export")
    export_parser.add_argument("--key")

    return parser
