# =============================================================================
# Terraform Providers Configuration
# =============================================================================
# Configures Azure and Databricks providers for Unity Catalog management.
# =============================================================================

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.80"
    }
    databricks = {
      source  = "databricks/databricks"
      version = "~> 1.30"
    }
  }

  # Azure Backend for State Storage
  backend "azurerm" {
    # These values are provided via -backend-config or environment variables
    # resource_group_name  = "rg-databricks-cicd"
    # storage_account_name = "stterraformstate"
    # container_name       = "tfstate"
    # key                  = "databricks-cicd.tfstate"
  }
}

# -----------------------------------------------------------------------------
# Azure Provider
# -----------------------------------------------------------------------------
provider "azurerm" {
  features {}
  
  # Authentication via environment variables:
  # ARM_CLIENT_ID, ARM_CLIENT_SECRET, ARM_TENANT_ID, ARM_SUBSCRIPTION_ID
}

# -----------------------------------------------------------------------------
# Databricks Provider
# -----------------------------------------------------------------------------
provider "databricks" {
  host  = var.databricks_host
  token = var.databricks_token
  
  # Alternative: Use Azure AD authentication
  # azure_workspace_resource_id = var.databricks_workspace_id
}

# -----------------------------------------------------------------------------
# Databricks Provider for Account-Level Operations (Unity Catalog)
# -----------------------------------------------------------------------------
provider "databricks" {
  alias      = "account"
  host       = "https://accounts.azuredatabricks.net"
  account_id = var.databricks_account_id
  
  # Authentication for account-level operations
  # Uses same credentials as workspace provider
}
