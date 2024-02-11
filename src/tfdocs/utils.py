import copy
import os
import re

import git


def count_blocks(data):
    if isinstance(data, list):
        string = "".join(data)
    else:
        string = data
    stack = []

    block_constructors = {"(": ")", "{": "}", "[": "]", "<": ">"}

    for char in string:
        if char in block_constructors:
            stack.append(char)
        elif stack:
            if (
                char in block_constructors.values()
                and char == block_constructors[stack[-1]]
            ):
                stack.pop()

    if len(stack) == 0:
        return True
    else:
        return False


def process_line_block(line_block, target_type, content, cont):
    type_match = None
    if not cont:
        type_match = (
            line_block if re.match(rf"^\s*{target_type}\s*=\s*", line_block) else None
        )

    if type_match or cont == target_type:
        if cont:
            content += line_block.strip()
        else:
            content = line_block.split("=")[1].strip()

        if not count_blocks(content):
            cont = target_type
        else:
            cont = None

    return content, cont


def match_type_constructors(string):
    type_constructors = ["list", "set", "map", "object", "tuple"]

    for sub in type_constructors:
        if sub in string:
            return True

    return False


def format_block(content):
    start_braces = ["{", "[", "("]
    end_braces = ["}", "]", ")"]
    prev_item = None
    tmp_content = ""
    if match_type_constructors(content):
        content_str = content.rstrip()
        indent = 4
        tmp_str = ""
        content_list = []
        for index, char in enumerate(content_str):
            if char in start_braces + end_braces + [","]:
                tmp_str = tmp_str.strip()
                if tmp_str != "":
                    content_list.append(tmp_str.strip())
                content_list.append(char)
                tmp_str = ""
            else:
                tmp_str += char

        for item in content_list:
            if item not in start_braces:
                if prev_item:
                    if match_type_constructors(prev_item) and match_type_constructors(
                        item
                    ):
                        tmp_content += item
                    elif item == ",":
                        tmp_content += item
                    else:
                        if item in end_braces:
                            if prev_item in end_braces:
                                tmp_content += item
                            else:
                                indent -= 2
                                tmp_content += "\n" + " " * indent + item
                        else:
                            tmp_content += "\n" + " " * indent + item
                else:
                    tmp_content += item
            else:
                if match_type_constructors(prev_item):
                    tmp_content += item
                else:
                    indent += 2
                    tmp_content += item + "\n" + " " * indent

            if item not in start_braces + [","]:
                prev_item = item
    else:
        content_str = content.rstrip()
        indent = 2

        for char in content_str:
            if char in start_braces or char in end_braces:
                char = char.strip()
                if char in end_braces:
                    indent -= 2
                    tmp_content += "\n" + " " * indent + char
                else:
                    tmp_content += char
                    if char in start_braces:
                        indent += 2
                        tmp_content += "\n" + " " * indent
            elif char == ",":
                tmp_content += char + "\n" + " " * indent
            else:
                tmp_content += char
    return tmp_content


def construct_tf_variable(content):
    default_str = (
        f'  default = {content.pop("default")}\n' if "default" in content else ""
    )

    default_str = format_block(default_str) + "\n"
    type_str = format_block(content["type"])

    template = (
        'variable "{name}" {{\n'
        "  type = {type}\n"
        "  description = {description}\n"
        "{default}"
        "}}\n\n"
    )

    return template.format(
        default=default_str,
        type=type_str,
        description=content["description"],
        name=content["name"],
    )


def construct_tf_file(content):
    content_copy = copy.deepcopy(content)
    file_content = ""
    for content in content_copy:
        file_content += construct_tf_variable(content)
    return file_content.rstrip() + "\n"


def get_module_url(module_name):
    try:
        repo = git.Repo(search_parent_directories=True)
        repo_root = repo.git.rev_parse("--show-toplevel")
        current_path = os.path.abspath(os.getcwd())
        rel_path = os.path.relpath(current_path, repo_root)
        return f"{repo.remotes.origin.url}//{rel_path}?ref=<TAG>"
    except git.exc.InvalidGitRepositoryError:
        return f"./modules/{module_name}"
