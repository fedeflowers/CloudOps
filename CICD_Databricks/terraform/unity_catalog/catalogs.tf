# =============================================================================
# Unity Catalog - Catalogs
# =============================================================================
# Creates catalogs for the data lakehouse layers (bronze, silver, gold).
# =============================================================================

# -----------------------------------------------------------------------------
# Catalogs
# -----------------------------------------------------------------------------
resource "databricks_catalog" "catalogs" {
  for_each = { for c in var.catalog_names : c.name => c }

  name         = "${local.prefix}${each.value.name}"
  comment      = each.value.comment
  owner        = var.catalog_owner
  
  # Isolation mode for the catalog
  isolation_mode = "ISOLATED"
  
  # Properties for the catalog
  properties = {
    environment = var.environment
    managed_by  = "terraform"
    created_at  = timestamp()
  }
}

# -----------------------------------------------------------------------------
# Catalog Workspace Bindings
# -----------------------------------------------------------------------------
resource "databricks_catalog_workspace_binding" "bindings" {
  for_each = databricks_catalog.catalogs

  catalog_name = each.value.name
  workspace_id = var.databricks_workspace_id
  binding_type = "BINDING_TYPE_READ_WRITE"
}
