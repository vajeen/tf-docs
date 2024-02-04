import re
import os
import sys
from tfdocs.utils import (
    count_blocks,
    match_type_constructors,
    construct_tf_file,
    get_module_url,
)


class Readme:
    def __init__(self, readme_file, variables_file):
        self.readme_content: str
        self.variables_content = []
        self.readme_changed = True
        self.variables_changed = True
        self.readme_file = readme_file
        self.variables_file = variables_file
        self.str_len = 0

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
            print("variables.tf file not found")
            sys.exit(-1)

    def write_variables(self):
        with open(self.variables_file, "w") as file:
            file.writelines(construct_tf_file(self.sorted_variables))

    def print_variables_file(self):
        print(construct_tf_file(self.sorted_variables))

    def get_variables_changed(self):
        return self.variables_changed

    def get_readme_changed(self):
        return self.readme_changed

    def construct_readme(self):
        directory = os.path.basename(
            os.path.dirname(os.path.abspath(self.variables_file))
        )
        readme_template = [
            f"module {directory} {{",
            f'  source = "{get_module_url()}/{directory}"',
        ]

        for item in self.sorted_variables:
            spaces = " " * (
                self.str_len - len(f'  {item["name"]} = <{item["type"]}>') + 2
            )
            readme_template.append(
                f'  {item["name"]} = <{item["type"].upper()}> {spaces} # {item["description"]}'
            )

        readme_template.append("}")

        if os.path.exists(self.readme_file):
            with open(self.readme_file, "r") as file:
                content = file.read()

            lines = content.split("\n")
            start_index = None
            end_index = None

            for i, line in enumerate(lines):
                if "<!-- TFDOC START -->" in line:
                    start_index = i
                elif "<!-- TFDOC END -->" in line:
                    end_index = i

            # Insert between TFDOC markers
            lines_constructed = lines.copy()
            if start_index is not None and end_index is not None:
                del lines_constructed[start_index + 1 : end_index]
                lines_constructed[start_index + 1 : start_index + 1] = readme_template

                # Check if the README.md file has changed
                if lines_constructed == lines:
                    self.readme_changed = False

            return lines_constructed

        return readme_template

    def print_readme(self):
        for line in self.construct_readme():
            print(line)

    def write_readme(self):
        readme_template = self.construct_readme()

        # Remove extra empty line
        if readme_template[-1] == "":
            readme_template.pop()

        with open(self.readme_file, "w") as file:
            file.writelines("%s\n" % item for item in readme_template)
        return True
