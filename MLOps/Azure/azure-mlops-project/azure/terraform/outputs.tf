output "workspace_name" { value = azurerm_machine_learning_workspace.aml.name }
output "acr_name" { value = azurerm_container_registry.acr.name }
output "kv_name" {
  value = module.ml_core.kv_name
}

output "storage_account" {
  value = module.ml_core.storage_account_name
}
