"""Command-line entry point."""

import argparse
import os
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import yaml

from writeragents.storage.long_term import DatabaseMemory
from writeragents.storage.short_term import RedisMemory
from importlib import resources
import os


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

    archive_parser = subparsers.add_parser("archive", help="Archive text using WBA")
    archive_parser.add_argument("text", help="Text to archive")

    write_parser = subparsers.add_parser("write", help="Generate text with WriterAgent")
    write_parser.add_argument("prompt", help="Prompt for WriterAgent")

    args = parser.parse_args(argv)

    config_path = args.config
    config = load_config(config_path)

    storage_cfg = config.get("storage", {})

    long_term = DatabaseMemory(
        url=storage_cfg.get("database_url", "sqlite:///memory.db")
    )
    short_term = RedisMemory(host=storage_cfg.get("redis_host", "localhost"))

    if args.command == "archive":
        from agents.wba.agent import WorldBuildingArchivist

        agent = WorldBuildingArchivist()
        agent.archive_text(args.text)
    elif args.command == "write":
        from agents.writer_agent.agent import WriterAgent

        agent = WriterAgent()
        agent.run(args.prompt)

    print(f"Using configuration: {args.config}")
    return config, long_term, short_term


if __name__ == '__main__':
    main()
