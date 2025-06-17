"""Command-line entry point."""

import argparse
import os
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import yaml

from writeragents.storage.long_term import DatabaseMemory
from writeragents.storage.short_term import RedisMemory
from importlib import resources


def load_config(path: str) -> Dict[str, Any]:
    """Load YAML configuration from ``path``.

    If ``path`` is relative and does not exist on disk, look for the file
    within the installed ``writeragents`` package.
    """
    if not os.path.isabs(path) and not os.path.exists(path):
        try:
            pkg_path = resources.files("writeragents").joinpath(path)
            with pkg_path.open("r", encoding="utf-8") as fh:
                return yaml.safe_load(fh) or {}
        except FileNotFoundError:
            pass

    with open(path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def main(
    argv: Optional[list[str]] | None = None,
) -> Tuple[Dict[str, Any], DatabaseMemory, RedisMemory]:
    """Entry point for the CLI."""
    default_cfg = Path(__file__).resolve().parent.parent / "config" / "local.yaml"

    parser = argparse.ArgumentParser(description="Interact with WriterAgents")
    parser.add_argument(
        "--config",
        default=os.environ.get("WRITERAG_CONFIG", str(default_cfg)),
        help="Path to config file",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    archive_parser = subparsers.add_parser(
        "archive", help="Archive text using WBA"
    )
    archive_parser.add_argument("text", help="Text to archive")

    load_parser = subparsers.add_parser(
        "load", help="Load a directory of markdown files"
    )
    load_parser.add_argument("directory", help="Path to directory with .md files")

    search_parser = subparsers.add_parser("search", help="Search the archive")
    search_parser.add_argument("query", help="Query text")
    search_parser.add_argument(
        "--mode", choices=["keyword", "semantic"], default="keyword"
    )

    write_parser = subparsers.add_parser(
        "write", help="Send a request through the agent orchestrator"
    )
    write_parser.add_argument("prompt", help="User request")

    menu_parser = subparsers.add_parser(
        "wba-menu", help="Interactive WorldBuildingArchivist menu"
    )

    args = parser.parse_args(argv)

    config_path = args.config
    config = load_config(config_path)

    storage_cfg = config.get("storage", {})
    wba_cfg = config.get("wba", {})

    long_term = DatabaseMemory(
        url=storage_cfg.get("database_url", "sqlite:///memory.db")
    )
    short_term = RedisMemory(host=storage_cfg.get("redis_host", "localhost"))
    candidate_limit = int(wba_cfg.get("candidate_limit", 3))

    if args.command == "archive":
        from writeragents.agents.wba.agent import WorldBuildingArchivist

        agent = WorldBuildingArchivist(candidate_limit=candidate_limit)
        agent.archive_text(args.text)
    elif args.command == "load":
        from writeragents.agents.wba.agent import WorldBuildingArchivist

        agent = WorldBuildingArchivist(candidate_limit=candidate_limit)
        agent.load_markdown_directory(args.directory)
    elif args.command == "search":
        from writeragents.agents.wba.agent import WorldBuildingArchivist

        agent = WorldBuildingArchivist(candidate_limit=candidate_limit)
        if args.mode == "keyword":
            results = agent.search_keyword(args.query)
        else:
            res, score = agent.search_semantic(args.query)
            results = [res] if res else []
        for r in results:
            print(r["text"])
    elif args.command == "wba-menu":
        from writeragents.agents.wba.agent import WorldBuildingArchivist

        agent = WorldBuildingArchivist(candidate_limit=candidate_limit)
        while True:
            choice = input(
                "1) Load Markdown directory\n"
                "2) Keyword search\n"
                "3) Semantic search\n"
                "4) Show type stats\n"
                "5) Clear RAG store\n"
                "0) Exit\n"
                "Select option: "
            ).strip()
            if choice == "1":
                sample_dir = os.environ.get(
                    "WBA_DOCS",
                    str(
                        Path(__file__).resolve().parent.parent.parent
                        / "docs"
                        / "wba_samples"
                    ),
                )
                print(f"Loading sample markdown from {sample_dir}")
                agent.load_markdown_directory(sample_dir)
            elif choice == "2":
                term = input("Keyword: ")
                results = agent.search_keyword(term)
                for r in results:
                    print(r["text"])
            elif choice == "3":
                text = input("Search text: ")
                res, _ = agent.search_semantic(text)
                if res:
                    print(res["text"])
            elif choice == "4":
                type_counts = agent.get_type_statistics()
                candidate_counts = agent.get_candidate_counts()
                print("Content types:")
                for name, count in type_counts.items():
                    print(f"  {name}: {count}")
                print("Unresolved candidates:")
                for name, count in candidate_counts.items():
                    print(f"  {name}: {count}")
            elif choice == "5":
                agent.clear_rag_store()
                print("RAG store cleared")
            elif choice == "0":
                break
    elif args.command == "write":
        from writeragents.agents.orchestrator.agent import Orchestrator

        agent = Orchestrator(candidate_limit=candidate_limit)
        agent.run(args.prompt)

    print(f"Using configuration: {args.config}")
    return config, long_term, short_term


if __name__ == '__main__':
    main()
