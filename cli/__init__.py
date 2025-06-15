"""Command-line entry point."""

import argparse


def main():
    parser = argparse.ArgumentParser(description="Interact with WriterAgents")
    parser.add_argument('--config', default='config/local.yaml', help='Path to config file')
    args = parser.parse_args()

    print(f"Using configuration: {args.config}")
    # TODO: load config and initialize agents


if __name__ == '__main__':
    main()
