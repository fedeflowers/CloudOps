terraform {
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
}


locals {
  name = "${var.prefix}-${var.environment}"
}

resource "azurerm_storage_account" "sa" {
  name                     = replace(lower("${local.name}sa"), "-", "")
  resource_group_name      = var.rg_name
  location                 = var.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

resource "azurerm_container_registry" "acr" {
  name                = replace(lower("${local.name}acr"), "-", "")
  resource_group_name = var.rg_name
  location            = var.location
  sku                 = "Basic"
  admin_enabled       = false
}

resource "azurerm_key_vault" "kv" {
  name                = replace(lower("${local.name}kv"), "-", "")
  resource_group_name = var.rg_name
  location            = var.location
  tenant_id           = data.azurerm_client_config.current.tenant_id
  sku_name            = "standard"
}

data "azurerm_client_config" "current" {}

resource "azurerm_application_insights" "appi" {
  name                = "${local.name}-appi"
  location            = var.location
  resource_group_name = var.rg_name
  application_type    = "web"
}

resource "azurerm_log_analytics_workspace" "law" {
  name                = "${local.name}-law"
  location            = var.location
  resource_group_name = var.rg_name
  sku                 = "PerGB2018"
}

resource "azurerm_machine_learning_workspace" "aml" {
  name                    = "${local.name}-aml"
  location                = var.location
  resource_group_name     = var.rg_name
  application_insights_id = azurerm_application_insights.appi.id
  key_vault_id            = azurerm_key_vault.kv.id
  storage_account_id      = azurerm_storage_account.sa.id
  container_registry_id   = azurerm_container_registry.acr.id
  identity {
    type = "SystemAssigned"
  }
  
}

resource "azurerm_machine_learning_compute_cluster" "cpu_cluster" {
  name                             = "${local.name}-cpu-cluster"
  location                         = var.location
  machine_learning_workspace_id     = azurerm_machine_learning_workspace.aml.id
  vm_size                          = "STANDARD_D2_V2"
  vm_priority                      = "Dedicated"

  scale_settings {
    min_node_count = 0
    max_node_count = 2
    scale_down_nodes_after_idle_duration = "PT5M"
  }
}

resource "azurerm_storage_data_lake_gen2_filesystem" "ml_data" {
  name               = "ml-data"
  storage_account_id = azurerm_storage_account.sa.id
}

# 1) Environment container (the named environment)
resource "azapi_resource" "sklearn_env" {
  type      = "Microsoft.MachineLearningServices/workspaces/environments@2024-04-01"
  name      = "sklearn-env"  # environment name
  parent_id = azurerm_machine_learning_workspace.aml.id

  body = jsonencode({
    properties = {
      description = "Environment for sklearn models"
      isArchived  = false
      # optional: properties/tags here
    }
  })
}

# 2) Environment version (where image/conda are set)
resource "azapi_resource" "sklearn_env_v1" {
  type      = "Microsoft.MachineLearningServices/workspaces/environments/versions@2024-04-01"
  name      = "1"  # version string
  parent_id = azapi_resource.sklearn_env.id

  body = jsonencode({
    properties = {
      osType     = "Linux"
      # Use either image, or build, or condaFile (any combo AML supports)
      image      = "mcr.microsoft.com/azureml/openmpi4.1.0-ubuntu20.04:202406"
      condaFile  = file("${path.module}/../../../../ml/environments/sklearn-env.yml")
      description = "v1 of sklearn env"
      isArchived  = false
    }
  })

  # Make the dependency explicit (optional but nice)
  depends_on = [azapi_resource.sklearn_env]
}