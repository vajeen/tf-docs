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

    if target_type == "type_override":
        target_type = "#\s*tfdocs:\s*type"

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
    start_braces = ["{", "[", "("]
    end_braces = ["}", "]", ")"]
    
    if match_type_constructors(content):
        content_str = content.rstrip()
        indent = 4
        tokens = []
        current_token = []
        
        # Tokenize the input
        for char in content_str:
            if char in start_braces + end_braces + [","]:
                if current_token:
                    tokens.append("".join(current_token).strip())
                    current_token = []
                tokens.append(char)
            else:
                current_token.append(char)
        if current_token:
            tokens.append("".join(current_token).strip())

        # Format the tokens
        result = []
        prev_item = None
        
        for item in tokens:
            if item in start_braces:
                if match_type_constructors(prev_item):
                    result.append(item)
                else:
                    result.append(item)
                    indent += 2
                    result.append("\n" + " " * indent)
            elif item == ",":
                result.append(item)
            elif item in end_braces:
                if prev_item in end_braces:
                    result.append(item)
                else:
                    indent -= 2
                    result.append("\n" + " " * indent + item)
            else:
                if prev_item:
                    if match_type_constructors(prev_item) and match_type_constructors(item):
                        result.append(item)
                    else:
                        result.append("\n" + " " * indent + item)
                else:
                    result.append(item)
            
            if item not in start_braces + [","]:
                prev_item = item
                
        return "".join(result)
    
    # Handle non-type constructor case
    content_str = content.rstrip()
    indent = 2
    result = []
    brace_flag = False
    content_flag = 0

    for char in content_str:
        if char in start_braces + end_braces:
            brace_flag = True
            char = char.strip()
            if char in end_braces:
                indent -= 2
                result.extend(["\n", " " * indent, char])
            else:
                result.append(char)
                if char in start_braces:
                    indent += 2
                    result.extend(["\n", " " * indent])
        elif char == "," and brace_flag:
            result.extend([char, "\n", " " * indent])
        else:
            if content_flag >= 1 and char.strip():
                content_flag = 2
            elif char == "=":
                content_flag = 1
            result.append(char)

    formatted = "".join(result)
    
    # Handle special case for assignments
    if content_flag == 1:
        left, right = formatted.split("=", 1)
        right = right.replace("\n", "").replace("\r", "").replace(" ", "")
        return f"{left}= {right}"
        
    return formatted


def construct_tf_variable(content):
    default_str = (
        f'  default = {content.pop("default")}\n' if "default" in content else ""
    )

    type_override = (
        f"  #tfdocs: type={content['type_override']}" + "\n"
        if content["type_override"]
        else ""
    )

    formatted_default_str = format_block(default_str)
    default_str = formatted_default_str + "\n" if formatted_default_str else ""

    type_str = format_block(content["type"])

    template = (
        'variable "{name}" {{\n'
        "{type_override}"
        "  type = {type}\n"
        "  description = {description}\n"
        "{default}"
        "}}\n\n"
    )

    return template.format(
        name=content["name"],
        type_override=type_override,
        type=type_str,
        description=content["description"],
        default=default_str,
    )


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
