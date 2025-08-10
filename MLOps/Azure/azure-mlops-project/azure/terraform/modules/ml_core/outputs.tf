output "workspace_name" {
  value = azurerm_machine_learning_workspace.aml.name
}

output "acr_name" {
  value = azurerm_container_registry.acr.name
}

output "kv_name" {
  value = azurerm_key_vault.kv.name
}

output "storage_account_name" {
  value = azurerm_storage_account.sa.name
}

output "sklearn_env_name" {
  value = azurerm_machine_learning_environment.sklearn_env.name
}