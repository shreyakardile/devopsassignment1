variable "aws_region" {
  description = "AWS region in which resources will be created."
  type        = string
  default     = "ap-south-1"
}
variable "project_name" {
  description = "Short lowercase prefix used in resource names."
  type        = string
  default     = "student-record-devops"
  validation {
    condition     = can(regex("^[a-z0-9-]{3,25}$", var.project_name))
    error_message = "project_name must be 3-25 lowercase letters, numbers, or hyphens."
  }
}
variable "key_name" {
  description = "Name of an existing EC2 key pair in the selected region."
  type        = string
}
variable "admin_cidr" {
  description = "Administrator public IPv4 address in CIDR notation, e.g. x.x.x.x/32."
  type        = string
  validation {
    condition     = can(cidrhost(var.admin_cidr, 0))
    error_message = "admin_cidr must be a valid CIDR block."
  }
}
variable "instance_type" {
  description = "EC2 instance type; assignment specifies t2.micro."
  type        = string
  default     = "t2.micro"
}
variable "root_volume_size" {
  description = "EC2 root volume size in GiB."
  type        = number
  default     = 20
}
