#!/usr/bin/env python
# Copyright (c) 2024 Vajeen Karunathilaka <vajeen@gmail.comu>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
from __future__ import annotations

import errno
import os
import sys

from rich.console import Console

from tfdocs import cli
from tfdocs import readme


def main(argv: list[str] | None = None):
    if argv is None:
        argv = sys.argv

    options = cli.get_parser(argv[1:])

    for k, v in options.__dict__.items():
        setattr(options, k, v)

    if options.version:
        print(f"tfdocs {cli.get_version()}")
        sys.exit(0)

    module_name = (
        options.module_name if options.module_name else os.getcwd().split("/")[-1]
    )

    rd = readme.Readme(options.readme_file, options.variables_file, module_name)
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


def report_and_exit(status: [], readme_file, variables_file, format_variables, dry_run):
    console = Console()
    changed_files = []

    if status["readme"]:
        changed_files.append(readme_file)

    if format_variables and status["variables"]:
        changed_files.append(variables_file)

    changed_list = f"{', '.join([f'{file}' for file in changed_files])}" if changed_files else "0"
    console.print(f"[green]Updated:[/] {changed_list}" if dry_run else f"[yellow]Pending changes:[/] {changed_list}")

    if changed_files:
        sys.exit(-1)
    else:
        sys.exit(0)


def _cli_entrypoint() -> None:
    try:
        sys.exit(main(sys.argv))
    except OSError as exc:
        if exc.errno != errno.EPIPE:
            raise
    except KeyboardInterrupt:
        sys.exit(130)
    except RuntimeError as exc:
        raise SystemExit(exc) from exc


if __name__ == "__main__":
    _cli_entrypoint()
