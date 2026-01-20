# =============================================================================
# Unity Catalog - Volumes
# =============================================================================
# Creates managed and external volumes for file storage.
# =============================================================================

# -----------------------------------------------------------------------------
# Local Volume Definitions
# -----------------------------------------------------------------------------
locals {
  volumes = flatten([
    for catalog in var.catalog_names : [
      # Managed volume for each catalog
      {
        catalog     = catalog.name
        schema      = "${catalog.name == "bronze" ? "raw_events" : catalog.name == "silver" ? "cleaned_events" : "analytics"}"
        name        = "files"
        volume_type = "MANAGED"
        key         = "${catalog.name}_files"
      },
      # External volume for each catalog (landing zone)
      {
        catalog     = catalog.name
        schema      = "${catalog.name == "bronze" ? "raw_events" : catalog.name == "silver" ? "cleaned_events" : "analytics"}"
        name        = "landing"
        volume_type = "EXTERNAL"
        key         = "${catalog.name}_landing"
      }
    ]
  ])
}

# -----------------------------------------------------------------------------
# Managed Volumes
# -----------------------------------------------------------------------------
resource "databricks_volume" "managed_volumes" {
  for_each = { for v in local.volumes : v.key => v if v.volume_type == "MANAGED" }

  catalog_name = databricks_catalog.catalogs[each.value.catalog].name
  schema_name  = each.value.schema
  name         = each.value.name
  volume_type  = "MANAGED"
  comment      = "Managed volume for ${each.value.catalog} layer files"
  owner        = var.catalog_owner

  depends_on = [databricks_schema.schemas]
}

# -----------------------------------------------------------------------------
# External Volumes
# -----------------------------------------------------------------------------
resource "databricks_volume" "external_volumes" {
  for_each = { for v in local.volumes : v.key => v if v.volume_type == "EXTERNAL" }

  catalog_name     = databricks_catalog.catalogs[each.value.catalog].name
  schema_name      = each.value.schema
  name             = each.value.name
  volume_type      = "EXTERNAL"
  storage_location = "${local.storage_url}/${each.value.catalog}/volumes/${each.value.name}"
  comment          = "External volume for ${each.value.catalog} layer landing zone"
  owner            = var.catalog_owner

  depends_on = [
    databricks_schema.schemas,
    databricks_external_location.locations
  ]
}

# -----------------------------------------------------------------------------
# Combined Volume Output
# -----------------------------------------------------------------------------
resource "databricks_volume" "volumes" {
  for_each = { for v in local.volumes : v.key => v }

  catalog_name     = databricks_catalog.catalogs[each.value.catalog].name
  schema_name      = each.value.schema
  name             = each.value.name
  volume_type      = each.value.volume_type
  storage_location = each.value.volume_type == "EXTERNAL" ? "${local.storage_url}/${each.value.catalog}/volumes/${each.value.name}" : null
  comment          = "${each.value.volume_type} volume for ${each.value.catalog} layer"
  owner            = var.catalog_owner

  depends_on = [
    databricks_schema.schemas,
    databricks_external_location.locations
  ]
}
