# =============================================================================
# Development Environment Variables
# =============================================================================
# Terraform variable values for the dev environment.
# Usage: terraform plan -var-file=environments/dev.tfvars
# =============================================================================

environment = "dev"

# -----------------------------------------------------------------------------
# Databricks Configuration
# -----------------------------------------------------------------------------
databricks_host         = "https://adb-1234567890123456.16.azuredatabricks.net"
databricks_workspace_id = "1234567890123456"
databricks_account_id   = "your-databricks-account-id"

# -----------------------------------------------------------------------------
# Unity Catalog Configuration
# -----------------------------------------------------------------------------
metastore_id = "your-metastore-id"

catalog_names = [
  { name = "bronze", comment = "Raw data ingestion layer - DEV" },
  { name = "silver", comment = "Cleaned and transformed data - DEV" },
  { name = "gold", comment = "Business-ready aggregated data - DEV" }
]

catalog_owner = "data-engineers"

# -----------------------------------------------------------------------------
# Storage Configuration
# -----------------------------------------------------------------------------
storage_account_name   = "stadatabricksdev"
storage_container_name = "unity-catalog"
access_connector_id    = "/subscriptions/12345678-1234-1234-1234-123456789abc/resourceGroups/rg-databricks-dev/providers/Microsoft.Databricks/accessConnectors/databricks-access-connector"

# -----------------------------------------------------------------------------
# Access Control Groups
# -----------------------------------------------------------------------------
data_engineers_group  = "data-engineers"
data_scientists_group = "data-scientists"
data_analysts_group   = "data-analysts"

# -----------------------------------------------------------------------------
# Tags
# -----------------------------------------------------------------------------
tags = {
  Project     = "Databricks-CICD"
  Environment = "dev"
  ManagedBy   = "Terraform"
  CostCenter  = "DataPlatform"
}
