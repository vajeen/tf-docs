import os
import re
import sys

from rich.console import Console

from tfdocs.utils import (
    count_blocks,
    construct_tf_file,
    generate_source,
    process_line_block,
)


class Readme:
    def __init__(
        self, readme_file, variables_file, module_name=None, module_source=None, module_source_git=False
    ):
        self.module_name = module_name
        self.module_source = module_source
        self.module_source_git = module_source_git
        self.readme_content: str
        self.readme_changed = True
        self.variables_changed = True
        self.readme_file = readme_file
        self.variables_file = variables_file
        self.str_len = 0
        self.console = Console()
        self.variables = []

        try:
            with open(self.variables_file, "r") as file:
                file_content = file.read().strip()

            block = []
            match_flag = False
            for line in file_content.split("\n"):
                block.append(line)
                match = re.match(r'\s*variable\s+"?(\w+)"?\s*{\s*', line, re.DOTALL)
                if match and not match_flag:
                    name = match.group(1)
                    match_flag = True
                if count_blocks(block) and match_flag:
                    match_flag = False
                    (
                        type_content,
                        default_content,
                        description_content,
                        type_override,
                        cont,
                    ) = (
                        "",
                        "",
                        "",
                        None,
                        None,
                    )
                    for line_block in block:
                        type_content, cont = process_line_block(
                            line_block, "type", type_content, cont
                        )

                        type_override, cont = process_line_block(
                            line_block, "type_override", type_override, cont
                        )

                        type_len_content = (
                            type_override if type_override else type_content
                        )

                        if type_len_content:
                            if len(f"  {name} = <{type_len_content}>") > self.str_len:
                                self.str_len = len(f"  {name} = <{type_len_content}>")
                        default_content, cont = process_line_block(
                            line_block, "default", default_content, cont
                        )
                        description_content, cont = process_line_block(
                            line_block, "description", description_content, cont
                        )

                    block = []
                    attributes = {
                        "name": name,
                        "type_override": type_override,
                        "type": type_content if type_content else "unknown",
                        "description": description_content
                        if description_content
                        else "No description provided",
                    }

                    if default_content:
                        attributes["default"] = default_content

                    self.variables.append(attributes)

            self.sorted_variables = sorted(self.variables, key=lambda k: k["name"])

            if construct_tf_file(self.sorted_variables).strip() == file_content.strip():
                self.variables_changed = False

        except FileNotFoundError:
            self.console.print(
                f"[red]ERROR:[/] Cannot find {self.variables_file} in current directory"
            )
            sys.exit(-1)

    def write_variables(self):
        with open(self.variables_file, "w") as file:
            file.writelines(construct_tf_file(self.sorted_variables))

    def print_variables_file(self):
        self.console.print("[purple]--- variables.tf ---[/]")
        print(construct_tf_file(self.sorted_variables))

    def get_status(self):
        return {
            "readme": self.readme_changed,
            "variables": self.variables_changed,
        }

    def construct_readme(self):
        readme_content = [
            "```",
            f"module <{self.module_name}> {{",
            f'  source = "{generate_source(self.module_name, self.module_source, self.module_source_git)}"',
        ]

        for item in self.sorted_variables:
            type_str = item["type_override"] if item["type_override"] else item["type"]
            spaces = " " * (self.str_len - len(f'  {item["name"]} = <{type_str}>') + 2)
            description = (
                item["description"][1:-1]
                if (
                    item["description"].startswith('"')
                    or item["description"].startswith("'")
                )
                and (
                    item["description"].endswith('"')
                    or item["description"].endswith("'")
                )
                else item["description"]
            )

            readme_content.append(
                f'  {item["name"]} = <{type_str.upper()}> {spaces} # {description}'
            )

        readme_content.append("}")
        readme_content.append("```")

        if os.path.exists(self.readme_file):
            with open(self.readme_file, "r") as file:
                content = file.read()

            lines = content.split("\n")
            start_index = None
            end_index = None

            for i, line in enumerate(lines):
                if "<!-- TFDOCS START -->" in line:
                    start_index = i
                elif "<!-- TFDOCS END -->" in line:
                    end_index = i

            # Insert between TFDOCS markers
            lines_constructed = lines.copy()
            if start_index is not None and end_index is not None:
                del lines_constructed[start_index + 1 : end_index]
                lines_constructed[start_index + 1 : start_index + 1] = readme_content

                # Check if the README.md file has changed
                if lines_constructed == lines:
                    self.readme_changed = False

                return lines_constructed
        return (
            [f"# {self.module_name} module", "", "<!-- TFDOCS START -->"]
            + readme_content
            + ["<!-- TFDOCS END -->", ""]
        )

    def print_readme(self):
        self.console.print("[purple]--- README.md ---[/]")
        for line in self.construct_readme():
            print(line)

    def write_readme(self):
        readme_content = self.construct_readme()

        # Remove extra empty line
        if readme_content[-1] == "":
            readme_content.pop()

        with open(self.readme_file, "w") as file:
            file.writelines("%s\n" % item for item in readme_content)
        return True
