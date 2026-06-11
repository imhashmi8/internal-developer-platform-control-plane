variable "service_name" {
  type = string
}

variable "team" {
  type = string
}

variable "environment" {
  type = string
}

variable "namespace" {
  type = string
}

variable "labels" {
  type    = map(string)
  default = {}
}
