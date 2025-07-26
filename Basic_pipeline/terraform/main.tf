terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.37.0"
    }
  }

  backend "azurerm" {}
}

resource "azurerm_resource_group" "example" {
  name     = var.resource_group_name
  location = var.location
}