# =============================================================================
# Unity Catalog - External Locations
# =============================================================================
# Creates external locations pointing to Azure Storage.
# =============================================================================

# -----------------------------------------------------------------------------
# Storage Credential
# -----------------------------------------------------------------------------
resource "databricks_storage_credential" "storage_cred" {
  name    = "${var.environment}_storage_credential"
  comment = "Storage credential for ${var.environment} environment"

  azure_managed_identity {
    access_connector_id = var.access_connector_id
  }

  # Alternative: Service Principal
  # azure_service_principal {
  #   directory_id   = var.azure_tenant_id
  #   application_id = var.azure_client_id
  #   client_secret  = var.azure_client_secret
  # }
}

# -----------------------------------------------------------------------------
# External Locations
# -----------------------------------------------------------------------------
resource "databricks_external_location" "locations" {
  for_each = { for c in var.catalog_names : c.name => c }

  name            = "${var.environment}_${each.value.name}_location"
  url             = "${local.storage_url}/${each.value.name}"
  credential_name = databricks_storage_credential.storage_cred.name
  comment         = "External location for ${each.value.name} layer data"
  owner           = var.catalog_owner

  depends_on = [databricks_storage_credential.storage_cred]
}

# -----------------------------------------------------------------------------
# Additional Variable for Storage Credential
# -----------------------------------------------------------------------------
variable "access_connector_id" {
  description = "Azure Databricks Access Connector ID for managed identity"
  type        = string
  default     = ""
}
