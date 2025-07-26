variable "resource_group_name" {
  description = "first_resource_group"
  type        = string
}

variable "location" {
  description = "The Azure region where resources will be created"
  type        = string
  default     = "westeurope"
}
