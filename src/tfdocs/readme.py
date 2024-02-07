import os
import re
import sys

from rich.console import Console

from tfdocs.utils import (
    count_blocks,
    match_type_constructors,
    construct_tf_file,
    get_module_url,
)


class Readme:
    def __init__(
        self, readme_file, variables_file, module_name=None, module_source=None
    ):
        self.module_name = module_name
        self.module_source = module_source
        self.readme_content: str
        self.variables_content = []
        self.readme_changed = True
        self.variables_changed = True
        self.readme_file = readme_file
        self.variables_file = variables_file
        self.str_len = 0
        self.console = Console()

        try:
            with open(self.variables_file, "r") as file:
                file_content = file.read()

            self.variables_content = file_content.split("\n")

            pattern = r'variable\s+"?(\w+)"?\s*{(.*?)\n}'

            matches = re.findall(pattern, file_content, re.DOTALL)

            self.variables = []

            for match in matches:
                name = match[0]
                content = match[1]
                type_content, default_content, description_content, cont = (
                    "",
                    "",
                    "",
                    None,
                )
                for line in content.split("\n"):
                    stripped_line = line.strip()

                    type_match = stripped_line if "type" in stripped_line else None
                    if type_match or cont == "type":
                        if (
                            len(f'  {name} = <{type_match.split("=")[1].strip()}>')
                            > self.str_len
                        ):
                            self.str_len = len(
                                f'  {name} = <{type_match.split("=")[1].strip()}>'
                            )
                        type_content += (
                            stripped_line if cont else type_match.split("=")[1].strip()
                        )
                        cont = "type" if count_blocks(type_content) else None

                    default_match = (
                        stripped_line if "default" in stripped_line else None
                    )
                    if default_match or cont == "default":
                        default_content += (
                            stripped_line
                            if cont
                            else default_match.split("=")[1].strip()
                        )
                        if match_type_constructors(default_content):
                            cont = "default" if count_blocks(default_content) else None

                    description_match = (
                        stripped_line if "description" in stripped_line else None
                    )
                    if description_match or cont == "description":
                        description_content += (
                            stripped_line
                            if cont
                            else description_match.split("=")[1].strip()
                        )
                        cont = (
                            "description" if count_blocks(description_content) else None
                        )

                attributes = {
                    "name": name,
                    "type": type_content if type_content else "unknown",
                    "description": description_content
                    if description_content
                    else "No description provided",
                }

                if default_content:
                    attributes["default"] = default_content

                self.variables.append(attributes)

            self.sorted_variables = sorted(self.variables, key=lambda k: k["name"])

            if construct_tf_file(self.sorted_variables) == file_content:
                self.variables_changed = False
        except FileNotFoundError:
            self.console.print(f"[red]ERROR:[/] Cannot find {self.variables_file} in current directory")
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
            f"module {self.module_name} {{",
            f'  source = "{get_module_url(self.module_name) if self.module_source is None else self.module_source}"',
        ]

        for item in self.sorted_variables:
            spaces = " " * (
                self.str_len - len(f'  {item["name"]} = <{item["type"]}>') + 2
            )
            description = (
                item["description"][1:-1]
                if item["description"].startswith('"')
                and item["description"].endswith('"')
                else item["description"]
            )

            readme_content.append(
                f'  {item["name"]} = <{item["type"].upper()}> {spaces} # {description}'
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
