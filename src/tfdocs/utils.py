import os

import git


def count_blocks(string):
    stack = []

    for char in string:
        if char == "(":
            stack.append(char)
        elif char == ")":
            if stack:
                stack.pop()

    return len(stack)


def match_type_constructors(string):
    type_constructors = ["list", "set", "map", "object", "tuple"]

    for sub in type_constructors:
        if sub in string:
            return True

    return False


def construct_tf_variable(content):
    default_str = (
        f'  default = {content.pop("default")}\n' if "default" in content else ""
    )
    if match_type_constructors(default_str):
        default_str = default_str.rstrip()
        indent = 2
        tmp_default = ""
        start_braces = ["{", "[", "("]
        end_braces = ["}", "]", ")"]
        for index, char in enumerate(default_str):
            tmp_default += char
            if char in start_braces:
                indent += 2
                tmp_default += "\n" + " " * indent
            elif char in end_braces:
                indent -= 2
                if len(default_str) == index + 1:
                    tmp_default = (
                        tmp_default[:-1] + "\n" + " " * indent + tmp_default[-1]
                    )
                    indent -= 2
                tmp_default += "\n" + " " * indent
            elif char == ",":
                tmp_default += "\n" + " " * indent
        default_str = tmp_default

    template = (
        'variable "{name}" {{\n'
        "  type = {type}\n"
        "  description = {description}\n"
        "{default}"
        "}}\n\n"
    )

    return template.format(default=default_str, **content)


def construct_tf_file(content):
    file_content = ""
    for content in content:
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
