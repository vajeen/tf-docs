#!/usr/bin/env python
# Copyright (c) 2024 Vajeen Karunathilaka <vajeen@gmail.com>
#
# MIT License

from __future__ import annotations

import errno
import sys
from pathlib import Path

from rich.console import Console

from tfdocs import cli
from tfdocs import readme


def main(argv: list[str] | None = None) -> None:
    """
    Entry point used by tests. It MUST call sys.exit(..) so tests that
    expect SystemExit behave correctly.
    """
    if argv is None:
        argv = sys.argv

    options = cli.get_parser(argv[1:])

    if options.version:
        print(f"tfdocs {cli.get_version()}")
        sys.exit(0)

    module_name = options.module_name or Path.cwd().name

    rd = readme.Readme(
        options.readme_file,
        options.variables_file,
        module_name,
        options.source,
        options.git_source,
    )

    if not options.dry_run and options.format:
        rd.write_variables()

    if options.dry_run:
        if options.format:
            rd.print_variables_file()
            if not rd.get_status()["variables"]:
                rd.print_readme()
                report_and_exit(
                    rd.get_status(),
                    options.readme_file,
                    options.variables_file,
                    options.format,
                    options.dry_run,
                )

        rd.print_readme()
        report_and_exit(
            rd.get_status(),
            options.readme_file,
            options.variables_file,
            options.format,
            options.dry_run,
        )

    rd.write_readme()
    report_and_exit(
        rd.get_status(),
        options.readme_file,
        options.variables_file,
        options.format,
        options.dry_run,
    )


def report_and_exit(
    status: dict[str, bool],
    readme_file: str,
    variables_file: str,
    format_variables: bool,
    dry_run: bool,
) -> None:
    """
    Print a summary and exit with the expected codes.
    Exits -1 when there are updates/pending updates; 0 otherwise.
    """
    console = Console()
    changed_files: list[str] = []

    if status.get("readme"):
        changed_files.append(readme_file)

    if format_variables and status.get("variables"):
        changed_files.append(variables_file)

    if changed_files:
        changed_list = ", ".join(changed_files)
        console.print(
            f"[green]Updated:[/] {changed_list}"
            if not dry_run
            else f"[yellow]Pending changes:[/] {changed_list}"
        )
        sys.exit(-1)
    else:
        console.print("[cyan]Nothing to update!!![/]")
        sys.exit(0)


def _cli_entrypoint() -> None:
    """
    Console script entrypoint. Mirrors your original signal/errno handling.
    """
    try:
        sys.exit(main(sys.argv))
    except OSError as exc:
        if exc.errno == errno.EPIPE:
            return
        raise
    except KeyboardInterrupt:
        sys.exit(130)
    except RuntimeError as exc:
        raise SystemExit(exc) from exc


if __name__ == "__main__":
    _cli_entrypoint()
