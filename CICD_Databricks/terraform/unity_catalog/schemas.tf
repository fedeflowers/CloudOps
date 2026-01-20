# =============================================================================
# Unity Catalog - Schemas
# =============================================================================
# Creates schemas within catalogs for organizing tables.
# =============================================================================

# -----------------------------------------------------------------------------
# Schemas
# -----------------------------------------------------------------------------
resource "databricks_schema" "schemas" {
  for_each = { for s in local.schemas : s.key => s }

  catalog_name = databricks_catalog.catalogs[each.value.catalog].name
  name         = each.value.schema
  comment      = "Schema for ${each.value.schema} data in ${each.value.catalog} layer"
  owner        = var.catalog_owner

  properties = {
    environment = var.environment
    layer       = each.value.catalog
    managed_by  = "terraform"
  }

  depends_on = [databricks_catalog.catalogs]
}

# -----------------------------------------------------------------------------
# Schema Output for Reference
# -----------------------------------------------------------------------------
locals {
  schema_map = {
    for s in local.schemas : s.key => {
      catalog     = s.catalog
      schema_name = s.schema
      full_name   = "${databricks_catalog.catalogs[s.catalog].name}.${s.schema}"
    }
  }
}
