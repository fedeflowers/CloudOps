# =============================================================================
# Terraform Outputs
# =============================================================================
# Output values from Unity Catalog infrastructure provisioning.
# =============================================================================

# -----------------------------------------------------------------------------
# Catalog Outputs
# -----------------------------------------------------------------------------
output "catalog_ids" {
  description = "Map of catalog names to their IDs"
  value = {
    for k, v in databricks_catalog.catalogs : k => v.id
  }
}

output "catalog_names" {
  description = "List of created catalog names"
  value       = [for c in databricks_catalog.catalogs : c.name]
}

# -----------------------------------------------------------------------------
# Schema Outputs
# -----------------------------------------------------------------------------
output "schema_full_names" {
  description = "List of schema full names (catalog.schema)"
  value       = [for s in databricks_schema.schemas : s.id]
}

# -----------------------------------------------------------------------------
# External Location Outputs
# -----------------------------------------------------------------------------
output "external_location_urls" {
  description = "Map of external location names to their URLs"
  value = {
    for k, v in databricks_external_location.locations : k => v.url
  }
}

# -----------------------------------------------------------------------------
# Volume Outputs
# -----------------------------------------------------------------------------
output "volume_paths" {
  description = "Map of volume names to their paths"
  value = {
    for k, v in databricks_volume.volumes : k => "/Volumes/${v.catalog_name}/${v.schema_name}/${v.name}"
  }
}

# -----------------------------------------------------------------------------
# Summary Output
# -----------------------------------------------------------------------------
output "deployment_summary" {
  description = "Summary of deployed Unity Catalog resources"
  value = {
    environment        = var.environment
    catalogs_created   = length(databricks_catalog.catalogs)
    schemas_created    = length(databricks_schema.schemas)
    external_locations = length(databricks_external_location.locations)
    volumes_created    = length(databricks_volume.volumes)
  }
}
