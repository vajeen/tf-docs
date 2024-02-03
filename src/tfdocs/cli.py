from __future__ import annotations

import argparse
from dataclasses import dataclass, field

from tfdocs import __version__


@dataclass
class Options:
    configured: bool = False
    format: bool = True
    dry_run: bool = False
    strict: bool = False
    exclude: list[str] = field(default_factory=list)
    version: bool = False
    filename: str | None = None
    variables_file: str = "variables.tf"
    readme_file: str = "README.md"


def get_parser(arguments: list[str]) -> Options:
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "-f",
        dest="format",
        default=False,
        action="store_true",
        help="Auto format variables.tf and outputs.tf files",
    )
    parser.add_argument(
        "--dry-run",
        dest="dry_run",
        default=False,
        action="store_true",
        help="Show generated README.md file",
    )
    parser.add_argument(
        "-s",
        "--strict",
        action="store_true",
        default=False,
        dest="strict",
        help="Return non-zero exit code on warnings as well as errors",
    )
    parser.add_argument(
        "--readme",
        dest="readme_file",
        action="store_true",
        default="README.md",
        help="Specify a custom name for README.md file",
    )
    parser.add_argument(
        "--variables",
        dest="variables_file",
        action="store_true",
        default="variables.tf",
        help="Specify a custom name for variables.tf file",
    )
    parser.add_argument(
        "--version",
        action="store_true",
    )
    parser.add_argument(
        nargs="?",
        default=None,
        dest="filename",
        help="Filename to format",
    )

    parser.parse_args(arguments)

    options = Options(**vars(parser.parse_args(arguments)))
    return options


def get_version() -> str | None:
    return __version__
