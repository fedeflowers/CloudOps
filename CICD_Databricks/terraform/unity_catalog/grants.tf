# =============================================================================
# Unity Catalog - Access Grants
# =============================================================================
# Configures access grants for principals (users, groups, service principals).
# =============================================================================

# -----------------------------------------------------------------------------
# Catalog-Level Grants
# -----------------------------------------------------------------------------

# Data Engineers - Full access to all catalogs
resource "databricks_grants" "catalog_engineers" {
  for_each = databricks_catalog.catalogs

  catalog = each.value.name

  grant {
    principal  = var.data_engineers_group
    privileges = ["ALL_PRIVILEGES"]
  }
}

# Data Scientists - Read access to silver and gold, write to gold
resource "databricks_grants" "catalog_scientists" {
  for_each = { for c in var.catalog_names : c.name => c if c.name != "bronze" }

  catalog = databricks_catalog.catalogs[each.key].name

  grant {
    principal  = var.data_scientists_group
    privileges = each.key == "gold" ? ["USE_CATALOG", "USE_SCHEMA", "SELECT", "MODIFY"] : ["USE_CATALOG", "USE_SCHEMA", "SELECT"]
  }

  depends_on = [databricks_grants.catalog_engineers]
}

# Data Analysts - Read-only access to gold catalog
resource "databricks_grants" "catalog_analysts" {
  catalog = databricks_catalog.catalogs["gold"].name

  grant {
    principal  = var.data_analysts_group
    privileges = ["USE_CATALOG", "USE_SCHEMA", "SELECT"]
  }

  depends_on = [databricks_grants.catalog_engineers]
}

# -----------------------------------------------------------------------------
# Schema-Level Grants
# -----------------------------------------------------------------------------

# Grant schema usage to all relevant groups
resource "databricks_grants" "schema_grants" {
  for_each = { for s in local.schemas : s.key => s }

  schema = "${databricks_catalog.catalogs[each.value.catalog].name}.${each.value.schema}"

  grant {
    principal  = var.data_engineers_group
    privileges = ["ALL_PRIVILEGES"]
  }

  dynamic "grant" {
    for_each = each.value.catalog != "bronze" ? [1] : []
    content {
      principal  = var.data_scientists_group
      privileges = each.value.catalog == "gold" ? ["USE_SCHEMA", "SELECT", "MODIFY", "CREATE_TABLE"] : ["USE_SCHEMA", "SELECT"]
    }
  }

  dynamic "grant" {
    for_each = each.value.catalog == "gold" ? [1] : []
    content {
      principal  = var.data_analysts_group
      privileges = ["USE_SCHEMA", "SELECT"]
    }
  }

  depends_on = [databricks_schema.schemas]
}

# -----------------------------------------------------------------------------
# External Location Grants
# -----------------------------------------------------------------------------
resource "databricks_grants" "external_location_grants" {
  for_each = databricks_external_location.locations

  external_location = each.value.name

  grant {
    principal  = var.data_engineers_group
    privileges = ["ALL_PRIVILEGES"]
  }

  depends_on = [databricks_external_location.locations]
}

# -----------------------------------------------------------------------------
# Volume Grants
# -----------------------------------------------------------------------------
resource "databricks_grants" "volume_grants" {
  for_each = databricks_volume.volumes

  volume = "${each.value.catalog_name}.${each.value.schema_name}.${each.value.name}"

  grant {
    principal  = var.data_engineers_group
    privileges = ["ALL_PRIVILEGES"]
  }

  grant {
    principal  = var.data_scientists_group
    privileges = ["READ_VOLUME", "WRITE_VOLUME"]
  }

  depends_on = [databricks_volume.volumes]
}
