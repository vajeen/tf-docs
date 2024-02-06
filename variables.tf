variable "my_string" {
  type  = string
  description = "Description of the string"
  default = "default"
}

variable "my_list" {
  type  = List(string)
  description = "Description of the list"
  default = ["default"]
}
