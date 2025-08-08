terraform {
  required_version = ">= 1.6.0"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = ">= 3.114.0"
    }
  }
}

provider "azurerm" {
  features {}
}

variable "prefix" { type = string }
variable "location" { type = string }
variable "environment" { type = string }

resource "azurerm_resource_group" "rg" {
  name     = "${var.prefix}-${var.environment}-rg"
  location = var.location
}

module "ml_core" {
  source      = "./modules/ml_core"
  prefix      = var.prefix
  environment = var.environment
  location    = var.location
  rg_name     = azurerm_resource_group.rg.name
}

output "ml_workspace_name" { value = module.ml_core.workspace_name }
output "acr_name" { value = module.ml_core.acr_name }
output "kv_name" { value = module.ml_core.kv_name }
output "storage_account" { value = module.ml_core.storage_account }









