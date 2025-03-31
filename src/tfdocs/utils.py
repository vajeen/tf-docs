import copy
import os
import re

import git


def count_blocks(data):
    string = "".join(data) if isinstance(data, list) else data
    stack = []
    
    block_constructors = {"{": "}", "(": ")", "[": "]", "<": ">"}
    closing_brackets = set(block_constructors.values())

    for char in string:
        if char in block_constructors:
            stack.append(char)
        elif char in closing_brackets and stack:
            if char == block_constructors[stack[-1]]:
                stack.pop()

    return len(stack) == 0


def process_line_block(line_block, target_type, content, cont):
    type_match = None

    if target_type == "type_override":
        target_type = r"#\s*tfdocs:\s*type"

    if not cont:
        type_match = (
            line_block if re.match(rf"^\s*{target_type}\s*=\s*", line_block) else None
        )

    if type_match or cont == target_type:
        if cont:
            content += line_block.strip()
        else:
            content = line_block.split("=",1)[1].strip()

        if not count_blocks(content):
            cont = target_type
        else:
            cont = None

    return content, cont


def match_type_constructors(string):
    type_constructors = ["list", "set", "map", "object", "tuple"]

    pattern = r"\b(" + "|".join(type_constructors) + r")\b"

    if re.search(pattern, string):
        return True
    else:
        return False


def format_block(content):
    input_str = content.strip()

    if "{" not in input_str:
        return input_str

    def add_missing_commas(s):
        return re.sub(r'([}\]"\w])(\s+)(\w+\s*=)', r'\1,\2\3', s)

    def smart_split(s):
        result = []
        current = ''
        depth = 0
        for char in s:
            if char in '{[':
                depth += 1
            elif char in '}]':
                depth -= 1
            if char == ',' and depth == 0:
                result.append(current.strip())
                current = ''
            else:
                current += char
        if current.strip():
            result.append(current.strip())
        return result

    def format_object_block(block_content, indent_level=2):
        indent = "  " * indent_level
        items = smart_split(block_content.strip())

        if len(items) == 1 and len(block_content.strip()) < 40:
            return "{ " + block_content.strip() + " }"

        formatted_str = "{\n"
        for i, item in enumerate(items):
            if "=" not in item:
                continue
            key, val = map(str.strip, item.split("=", 1))
            comma = "," if i < len(items) - 1 else ""
            if val.startswith("{") and val.endswith("}"):
                val = format_object_block(val[1:-1], indent_level + 1)
                formatted_str += f"{indent}{key} = {val}{comma}\n"
            else:
                formatted_str += f"{indent}{key} = {val}{comma}\n"
        formatted_str += "  " * (indent_level - 1) + "}"
        return formatted_str

    def add_indent_after_first_line(s):
        lines = s.splitlines()
        if len(lines) <= 1:
            return s
        return lines[0] + "\n" + "\n".join("  " + line for line in lines[1:])

    nested_match = re.match(r'(\w+\s*\(\s*\w+\s*\(\s*){(.*)}(\s*\)\s*\))', input_str)
    if nested_match:
        prefix, body, suffix = nested_match.groups()
        body_fixed = add_missing_commas(body)
        formatted_body = format_object_block(body_fixed)
        return add_indent_after_first_line(f"{prefix}{formatted_body}{suffix}")

    if input_str.startswith("{") and input_str.endswith("}"):
        inner = input_str[1:-1]
        inner_fixed = add_missing_commas(inner)
        formatted = format_object_block(inner_fixed, indent_level=1)
        return add_indent_after_first_line(formatted)

    return input_str


def construct_tf_variable(content):
    lines = [f'variable "{content["name"]}" {{']

    if content["type_override"]:
        lines.append(f'  #tfdocs: type={content["type_override"].strip()}')

    lines.append(f'  type = {format_block(content["type"].strip())}')
    lines.append(f'  description = {content["description"].strip()}')

    if "default" in content:
        lines.append(f'  default = {format_block(content["default"].strip())}')

    lines.append("}")
    return "\n".join(lines)


def construct_tf_file(content):
    content_copy = copy.deepcopy(content)
    file_content = ""
    for content in content_copy:
        file_content += construct_tf_variable(content)
    return file_content.rstrip() + "\n"


def generate_source(module_name, source, source_git):
    if source and not source_git:
        return source
    else:
        try:
            repo = git.Repo(search_parent_directories=True)
            repo_root = repo.git.rev_parse("--show-toplevel")
            current_path = os.path.abspath(os.getcwd())
            rel_path = os.path.relpath(current_path, repo_root)
            if source:
                return f"{source}//{rel_path}?ref=<TAG>"
            return f"{repo.remotes.origin.url}//{rel_path}?ref=<TAG>"
        except git.exc.InvalidGitRepositoryError:
            return f"./modules/{module_name}"
