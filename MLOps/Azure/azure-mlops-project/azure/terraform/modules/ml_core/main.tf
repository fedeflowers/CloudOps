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
}
