# =============================================================================
# Main Terraform Configuration
# =============================================================================
# Root module that orchestrates Unity Catalog resource creation.
# =============================================================================

# -----------------------------------------------------------------------------
# Local Values
# -----------------------------------------------------------------------------
locals {
  # Environment-specific naming prefix
  prefix = var.environment == "prod" ? "" : "${var.environment}_"
  
  # Storage URL for external locations
  storage_url = "abfss://${var.storage_container_name}@${var.storage_account_name}.dfs.core.windows.net"
  
  # Flatten schemas for creation
  schemas = flatten([
    for catalog in var.catalog_names : [
      for schema in lookup(local.schema_definitions, catalog.name, []) : {
        catalog = catalog.name
        schema  = schema
        key     = "${catalog.name}_${schema}"
      }
    ]
  ])
  
  # Schema definitions per catalog
  schema_definitions = {
    bronze = ["raw_sales", "raw_inventory", "raw_customers", "raw_events"]
    silver = ["cleaned_sales", "cleaned_inventory", "cleaned_customers", "cleaned_events"]
    gold   = ["analytics", "reporting", "ml_features", "aggregates"]
  }
}

# -----------------------------------------------------------------------------
# Data Sources
# -----------------------------------------------------------------------------
data "databricks_current_user" "me" {}

data "databricks_spark_version" "latest_lts" {
  long_term_support = true
}
