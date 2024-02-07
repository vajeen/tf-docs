from __future__ import annotations

import argparse
from dataclasses import dataclass

from tfdocs import __version__

@dataclass
class Options:
    format: bool = True
    dry_run: bool = False
    version: bool = False
    variables_file: str = "variables.tf"
    readme_file: str = "README.md"
    source: str | None = None
    module_name: str | None = None


def get_parser(arguments: list[str]) -> Options:
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "--name",
        "-n",
        dest="module_name",
        action="store",
        default=None,
        help="Specify a custom name for the module",
    )
    parser.add_argument(
        "--readme",
        dest="readme_file",
        action="store",
        default="README.md",
        help="Specify a custom name for README.md file",
    )
    parser.add_argument(
        "--variables",
        dest="variables_file",
        action="store",
        default="variables.tf",
        help="Specify the name of the file containing variables (default: variables.tf)",
    )
    parser.add_argument(
        "--source",
        dest="source",
        action="store",
        default=None,
        help="Specify a custom source for the module",
    )
    parser.add_argument(
        "-f",
        dest="format",
        default=False,
        action="store_true",
        help="Format and sort variables.tf file",
    )
    parser.add_argument(
        "--dry-run",
        dest="dry_run",
        default=False,
        action="store_true",
        help="Show the output without writing to the file",
    )
    parser.add_argument(
        "--version",
        action="store_true",
    )

    parser.parse_args(arguments)

    options = Options(**vars(parser.parse_args(arguments)))
    return options

def get_version() -> str | None:
    return __version__
