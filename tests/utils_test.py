from tfdocs import utils


def test_count_blocks():
    assert utils.count_blocks("()") is True
    assert utils.count_blocks("()(") is False
    assert utils.count_blocks("()()") is True
    assert utils.count_blocks("()()(") is False
    assert utils.count_blocks("{}") is True
    assert utils.count_blocks("{}{") is False
    assert utils.count_blocks("{}{}") is True
    assert utils.count_blocks("{}{}{") is False
    assert utils.count_blocks("[]") is True
    assert utils.count_blocks("[][") is False
    assert utils.count_blocks("[][]") is True
    assert utils.count_blocks("[][][") is False
    assert utils.count_blocks("<>") is True
    assert utils.count_blocks("<><") is False
    assert utils.count_blocks("<><>") is True
    assert utils.count_blocks("<><><") is False
    assert utils.count_blocks("(){}[]<>") is True
    assert utils.count_blocks("({[]})") is True
    assert utils.count_blocks("({[]})(") is False
    assert utils.count_blocks("({[]})()") is True
    assert utils.count_blocks("({[]})()(") is False
    assert utils.count_blocks("({[]})(){}") is True
    assert utils.count_blocks("({[]})(){}{") is False
    assert utils.count_blocks("({[]})(){}{}") is True
    assert utils.count_blocks(["()"]) is True
    assert utils.count_blocks(["()","("]) is False
    assert utils.count_blocks(["()","()"]) is True
    assert utils.count_blocks(["()","()","("]) is False
    assert utils.count_blocks(["{}"]) is True
    assert utils.count_blocks(["{}","{"]) is False
    assert utils.count_blocks(["{}","{}"]) is True
    assert utils.count_blocks(["{}","{}","{"]) is False


def test_process_line_block():
    assert utils.process_line_block("type = string", "type", "", None) == (
        "string",
        None,
    )
    assert utils.process_line_block("typee = string", "type", "", None) == ("", None)
    assert utils.process_line_block("type = stringg", "type", "", None) == (
        "stringg",
        None,
    )
    assert utils.process_line_block("type = list[]", "type", "", None) == (
        "list[]",
        None,
    )
    assert utils.process_line_block("type = list[", "type", "", None) == (
        "list[",
        "type",
    )
    assert utils.process_line_block("type = list[()", "type", "", None) == (
        "list[()",
        "type",
    )
    assert utils.process_line_block("type = list[()]", "type", "", None) == (
        "list[()]",
        None,
    )
    assert utils.process_line_block(
        'description = "my description"', "description", "", None
    ) == ('"my description"', None)
    assert utils.process_line_block("default = 24", "default", "", None) == ("24", None)
    assert utils.process_line_block("default = [1,2,3]", "default", "", None) == (
        "[1,2,3]",
        None,
    )
    assert utils.process_line_block("default = [1,2,3", "default", "", None) == (
        "[1,2,3",
        "default",
    )
    assert utils.process_line_block(
        "#tfdocs:type=object()", "type_override", "", None
    ) == ("object()", None)
    assert utils.process_line_block(
        "# tfdocs:type=object()", "type_override", "", None
    ) == ("object()", None)
    assert utils.process_line_block(
        "# tfdocs:type = object()", "type_override", "", None
    ) == ("object()", None)
    assert utils.process_line_block(
        "# tfdocs: type=object()", "type_override", "", None
    ) == ("object()", None)
    assert utils.process_line_block(
        "# tfdocs: type=object(", "type_override", "", None
    ) == ("object(", "#\\s*tfdocs:\\s*type")



    assert utils.process_line_block("  )]", "type", "type = list[(", "type") == (
        "type = list[()]",
        None,
    )


def test_match_type_constructors():
    assert utils.match_type_constructors("list") is True
    assert utils.match_type_constructors("set") is True
    assert utils.match_type_constructors("map") is True
    assert utils.match_type_constructors("object") is True
    assert utils.match_type_constructors("tuple") is True
    assert utils.match_type_constructors("list[]") is True
    assert utils.match_type_constructors("set{}") is True
    assert utils.match_type_constructors("map{}") is True
    assert utils.match_type_constructors("object()") is True
    assert utils.match_type_constructors("tuple()") is True
    assert utils.match_type_constructors("list[") is True
    assert utils.match_type_constructors("set{") is True
    assert utils.match_type_constructors("map{") is True
    assert utils.match_type_constructors("object(") is True
    assert utils.match_type_constructors("tuple(") is True
    assert utils.match_type_constructors("list[()") is True
    assert utils.match_type_constructors("set{}(") is True
    assert utils.match_type_constructors("listt") is False
    assert utils.match_type_constructors("listt[()") is False
    assert utils.match_type_constructors("json") is False
    assert utils.match_type_constructors("const") is False
    assert utils.match_type_constructors("const ") is False
    assert utils.match_type_constructors("array") is False
    assert utils.match_type_constructors("dict") is False


def test_format_block():
    assert (
        utils.format_block('  default = "my default string"')
        == '  default = "my default string"'
    )

    var1in = '  default = [{name = "name1",size = 10,directory = "dir1"},{name = "name2",size = 15,directory = "dir2"},{name = "name3",size = 20,directory = "dir3"}]'
    var1out = """  default = [
    {
      name = "name1",
      size = 10,
      directory = "dir1"
    },
    {
      name = "name2",
      size = 15,
      directory = "dir2"
    },
    {
      name = "name3",
      size = 20,
      directory = "dir3"
    }
  ]"""
    assert utils.format_block(var1in) == var1out

    var2in = "list(object({name = string,size = number,directory = string}))"
    var2out = """list(object({
    name = string,
    size = number,
    directory = string
  }))"""
    assert utils.format_block(var2in) == var2out

    assert (
        utils.format_block('  default = "myapp-1.1.1"') == '  default = "myapp-1.1.1"'
    )
    assert utils.format_block("  default = 40") == "  default = 40"


def test_construct_tf_variable():
    var1in = {
        "name": "my_variable",
        "type_override": None,
        "type": "string",
        "description": '"My variable"',
        "default": '"my default"',
    }
    var1out = """variable "my_variable" {
  type = string
  description = "My variable"
  default = "my default"
}

"""
    assert utils.construct_tf_variable(var1in) == var1out

    var2in = {
        "name": "my_variable",
        "type_override": "list(object({}))",
        "type": "list(object({name = string,size = number,directory = string}))",
        "description": '"My variable"',
        "default": '[{name = "name1",size = 10,directory = "dir1"},{name = "name2",size = 15,directory = "dir2"},{name = "name3",size = 20,directory = "dir3"}]',
    }
    var2out = """variable "my_variable" {
  #tfdocs: type=list(object({}))
  type = list(object({
    name = string,
    size = number,
    directory = string
  }))
  description = "My variable"
  default = [
    {
      name = "name1",
      size = 10,
      directory = "dir1"
    },
    {
      name = "name2",
      size = 15,
      directory = "dir2"
    },
    {
      name = "name3",
      size = 20,
      directory = "dir3"
    }
  ]
}

"""
    assert utils.construct_tf_variable(var2in) == var2out

    var3in = {
        "name": "my_variable",
        "type_override": None,
        "type": "string  ",
        "description": '"My variable"',
        "default": '"my default"',
    }
    var3out = """variable "my_variable" {
  type = string
  description = "My variable"
  default = "my default"
}

"""
    assert utils.construct_tf_variable(var3in) == var3out


def test_construct_tf_file():
    var1in = [
        {
            "name": "my_var",
            "type_override": None,
            "type": "string",
            "description": '"My description 1"',
            "default": '"my-default-1"',
        }
    ]
    var1out = """variable "my_var" {
  type = string
  description = "My description 1"
  default = "my-default-1"
}
"""
    assert utils.construct_tf_file(var1in) == var1out

    var2in = [
        {
            "name": "my_var2",
            "type_override": None,
            "type": "string",
            "description": '"my-default-2"',
        }
    ]
    var2out = """variable "my_var2" {
  type = string
  description = "my-default-2"
}
"""
    assert utils.construct_tf_file(var2in) == var2out

    var3in = [
        {
            "name": "my_var_3",
            "type_override": None,
            "type": "bool",
            "description": '"My description 3"',
            "default": "true",
        }
    ]
    var3out = """variable "my_var_3" {
  type = bool
  description = "My description 3"
  default = true
}
"""
    assert utils.construct_tf_file(var3in) == var3out

    var4in = [
        {
            "name": "my_var_4",
            "type_override": None,
            "type": "number",
            "description": '"My description 4"',
            "default": "45",
        }
    ]
    var4out = """variable "my_var_4" {
  type = number
  description = "My description 4"
  default = 45
}
"""
    assert utils.construct_tf_file(var4in) == var4out

    var5in = [
        {
            "name": "my_var_5",
            "type_override": "list(object({}))",
            "type": "list(object({name = string,size = number,directory = string}))",
            "description": '"Volume size of EBS for Bamboo, Docker and Backup"',
            "default": '[{name = "name1",size = 10,directory = "dir1"},{name = "name2",size = 15,directory = "dir2"},{name = "name3",size = 20,directory = "dir3"}]',
        }
    ]
    var5out = """variable "my_var_5" {
  #tfdocs: type=list(object({}))
  type = list(object({
    name = string,
    size = number,
    directory = string
  }))
  description = "Volume size of EBS for Bamboo, Docker and Backup"
  default = [
    {
      name = "name1",
      size = 10,
      directory = "dir1"
    },
    {
      name = "name2",
      size = 15,
      directory = "dir2"
    },
    {
      name = "name3",
      size = 20,
      directory = "dir3"
    }
  ]
}
"""
    assert utils.construct_tf_file(var5in) == var5out

    var6in = [
        {
            "name": "my_var_6",
            "type_override": None,
            "type": "any",
            "description": '"My description 6"',
            "default": "[]",
        }
    ]
    var6out = """variable "my_var_6" {
  type = any
  description = "My description 6"
  default = []
}
"""
    assert utils.construct_tf_file(var6in) == var6out

    var7in = [
        {
            "name": "my_var",
            "type_override": None,
            "type": "string",
            "description": '"My description 1"',
            "default": '"my-default-1"',
        },
        {
            "name": "my_var2",
            "type_override": None,
            "type": "string",
            "description": '"my-default-2"',
        },
        {
            "name": "my_var_3",
            "type_override": None,
            "type": "bool",
            "description": '"My description 3"',
            "default": "true",
        },
        {
            "name": "my_var_4",
            "type_override": None,
            "type": "number",
            "description": '"My description 4"',
            "default": "45",
        },
        {
            "name": "my_var_5",
            "type_override": "list(object({}))",
            "type": "list(object({name = string,size = number,directory = string}))",
            "description": '"My description 5"',
            "default": '[{name = "name1",size = 10,directory = "dir1"},{name = "name2",size = 15,directory = "dir2"},{name = "name3",size = 20,directory = "dir3"}]',
        },
        {
            "name": "my_var_6",
            "type_override": None,
            "type": "any",
            "description": '"My description 6"',
            "default": "[]",
        },
    ]
    var7out = """variable "my_var" {
  type = string
  description = "My description 1"
  default = "my-default-1"
}

variable "my_var2" {
  type = string
  description = "my-default-2"
}

variable "my_var_3" {
  type = bool
  description = "My description 3"
  default = true
}

variable "my_var_4" {
  type = number
  description = "My description 4"
  default = 45
}

variable "my_var_5" {
  #tfdocs: type=list(object({}))
  type = list(object({
    name = string,
    size = number,
    directory = string
  }))
  description = "My description 5"
  default = [
    {
      name = "name1",
      size = 10,
      directory = "dir1"
    },
    {
      name = "name2",
      size = 15,
      directory = "dir2"
    },
    {
      name = "name3",
      size = 20,
      directory = "dir3"
    }
  ]
}

variable "my_var_6" {
  type = any
  description = "My description 6"
  default = []
}
"""
    assert utils.construct_tf_file(var7in) == var7out

def test_generate_source():
    assert (
        utils.generate_source("modules", "git@git.com:tfdocs", True)
        == "git@git.com:tfdocs//.?ref=<TAG>"
    )
    assert utils.generate_source("modules", "tfdocs", False) == "tfdocs"
