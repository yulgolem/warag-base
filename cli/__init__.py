"""Command-line entry point."""

import argparse
import os
from typing import Any, Dict, Optional, Tuple

import yaml

from storage.long_term import DatabaseMemory
from storage.short_term import RedisMemory


def load_config(path: str) -> Dict[str, Any]:
    """Load YAML configuration from ``path``."""
    with open(path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def main(argv: Optional[list[str]] | None = None) -> Tuple[Dict[str, Any], DatabaseMemory, RedisMemory]:
    """Entry point for the CLI."""
    parser = argparse.ArgumentParser(description="Interact with WriterAgents")
    parser.add_argument(
        "--config",
        help="Path to config file",
    )
    args = parser.parse_args(argv)

    config_path = args.config or os.environ.get("WRITERAGENTS_CONFIG", "config/local.yaml")
    config = load_config(config_path)

    storage_cfg = config.get("storage", {})
    db_url = os.environ.get("DATABASE_URL", storage_cfg.get("database_url", "sqlite:///memory.db"))
    redis_host = os.environ.get("REDIS_HOST", storage_cfg.get("redis_host", "localhost"))
    long_term = DatabaseMemory(url=db_url)
    short_term = RedisMemory(host=redis_host)

    print(f"Using configuration: {config_path}")
    return config, long_term, short_term


if __name__ == '__main__':
    main()
