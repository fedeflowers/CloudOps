terraform {
  required_version = ">= 1.5.5"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = ">= 3.114.0"
    }
    azapi = {
      source  = "azure/azapi"
      version = "~> 2.0"
    }
  }

  backend "azurerm" {}
}

provider "azurerm" {
  features {}
}

provider "azapi" {}

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








