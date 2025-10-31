#!/usr/bin/env python
# Copyright (c) 2024 Vajeen Karunathilaka <vajeen@gmail.com>
#
# MIT License (see header above)

from __future__ import annotations

import errno
import sys
from pathlib import Path
from typing import Dict, List, Optional

from rich.console import Console

from tfdocs import cli
from tfdocs import readme


def main(argv: Optional[List[str]] = None) -> int:
    if argv is None:
        argv = sys.argv

    options = cli.get_parser(argv[1:])

    if options.version:
        print(f"tfdocs {cli.get_version()}")
        return 0

    module_name: str = options.module_name or Path.cwd().name

    rd = readme.Readme(
        readme_file=options.readme_file,
        variables_file=options.variables_file,
        module_name=module_name,
        module_source=options.source,
        module_source_git=options.git_source,
    )

    if not options.dry_run and options.format:
        rd.write_variables()

    if options.dry_run:
        if options.format:
            rd.print_variables_file()
            if not rd.get_status()["variables"]:
                rd.print_readme()
                return report_and_exit(
                    rd.get_status(),
                    options.readme_file,
                    options.variables_file,
                    options.format,
                    options.dry_run,
                )

        rd.print_readme()
        return report_and_exit(
            rd.get_status(),
            options.readme_file,
            options.variables_file,
            options.format,
            options.dry_run,
        )

    rd.write_readme()
    return report_and_exit(
        rd.get_status(),
        options.readme_file,
        options.variables_file,
        options.format,
        options.dry_run,
    )


def report_and_exit(
    status: Dict[str, bool],
    readme_file: str,
    variables_file: str,
    format_variables: bool,
    dry_run: bool,
) -> int:
    console = Console()
    changed_files: List[str] = []

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
        return -1
    else:
        console.print("[cyan]Nothing to update!!![/]")
        return 0


def _cli_entrypoint() -> None:
    try:
        sys.exit(main(sys.argv))
    except OSError as exc:
        if exc.errno != errno.EPIPE:
            raise
        sys.exit(0)
    except KeyboardInterrupt:
        sys.exit(130)
    except RuntimeError as exc:
        raise SystemExit(exc) from exc


if __name__ == "__main__":
    _cli_entrypoint()
