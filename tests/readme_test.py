from tfdocs import readme
from tfdocs import utils
import os
import pytest
import tempfile

mock_variables_tf = """
variable "var1" {
  type        = string
  description = "This is variable 1"
}

variable "var2" {
  type        = number
  default     = 42
  description = "This is variable 2"
}

variable "var3" {
  type        = number
  default     = 54
}
"""

# Mock data for README.md
mock_readme_md = """
# Example module

<!-- TFDOCS START -->
<!-- TFDOCS END -->
"""

@pytest.fixture
def temp_files():
    # Create temporary files for variables.tf and README.md
    temp_dir = tempfile.TemporaryDirectory()
    variables_file = os.path.join(temp_dir.name, "variables.tf")
    readme_file = os.path.join(temp_dir.name, "README.md")

    # Write mock data to these files
    with open(variables_file, "w") as f:
        f.write(mock_variables_tf)

    with open(readme_file, "w") as f:
        f.write(mock_readme_md)

    yield variables_file, readme_file

    # Cleanup
    temp_dir.cleanup()

def test_initialization(temp_files):
    variables_file, readme_file = temp_files
    rd = readme.Readme(readme_file, variables_file, module_name="example")

    assert rd.module_name == "example"
    assert rd.variables_file == variables_file
    assert rd.readme_file == readme_file
    assert len(rd.variables) == 3

def test_variable_parsing(temp_files):
    variables_file, readme_file = temp_files
    rd = readme.Readme(readme_file, variables_file)

    expected_variables = [
        {
            "name": "var1",
            "type_override": None,
            "type": "string",
            "description": '"This is variable 1"',
        },
        {
            "name": "var2",
            "type_override": None,
            "type": "number",
            "description": '"This is variable 2"',
            "default": "42",
        },
        {
            "name": "var3",
            "type_override": None,
            "type": "number",
            "description": '"No description provided"',
            "default": "54",
        },
    ]

    assert rd.variables == expected_variables

def test_write_variables(temp_files):
    variables_file, readme_file = temp_files
    rd = readme.Readme(readme_file, variables_file)

    rd.write_variables()

    with open(variables_file, "r") as f:
        content = f.read()

    assert content.strip() == utils.construct_tf_file(rd.sorted_variables).strip()

def test_construct_readme(temp_files):
    variables_file, readme_file = temp_files
    rd = readme.Readme(readme_file, variables_file, module_name="example", module_source="git@git.com:tfdocs")

    constructed_readme = rd.construct_readme()

    expected_readme_content = [
        "```",
        "module <example> {",
        '  source = "git@git.com:tfdocs"',
        '  var1 = <STRING>    # This is variable 1',
        '  var2 = <NUMBER>    # This is variable 2',
        '  var3 = <NUMBER>    # No description provided',
        "}",
        "```",
    ]

    assert all(line in constructed_readme for line in expected_readme_content)

def test_write_readme(temp_files):
    variables_file, readme_file = temp_files
    rd = readme.Readme(readme_file, variables_file, module_name="example", module_source="git@git.com:tfdocs")

    rd.write_readme()

    with open(readme_file, "r") as f:
        content = f.read()

    expected_readme_content = (
        "# Example module\n\n<!-- TFDOCS START -->\n```\nmodule <example> {\n  source = \"git@git.com:tfdocs\"\n  var1 = <STRING>    # This is variable 1\n  var2 = <NUMBER>    # This is variable 2\n  var3 = <NUMBER>    # No description provided\n}\n```\n<!-- TFDOCS END -->\n"
    )

    assert content.strip() == expected_readme_content.strip()
