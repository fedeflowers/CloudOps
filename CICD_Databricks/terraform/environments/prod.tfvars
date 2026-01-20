# =============================================================================
# Production Environment Variables
# =============================================================================
# Terraform variable values for the prod environment.
# Usage: terraform plan -var-file=environments/prod.tfvars
# =============================================================================

environment = "prod"

# -----------------------------------------------------------------------------
# Databricks Configuration
# -----------------------------------------------------------------------------
databricks_host         = "https://adb-9876543210987654.16.azuredatabricks.net"
databricks_workspace_id = "9876543210987654"
databricks_account_id   = "your-databricks-account-id"

# -----------------------------------------------------------------------------
# Unity Catalog Configuration
# -----------------------------------------------------------------------------
metastore_id = "your-metastore-id"

catalog_names = [
  { name = "bronze", comment = "Raw data ingestion layer - PRODUCTION" },
  { name = "silver", comment = "Cleaned and transformed data - PRODUCTION" },
  { name = "gold", comment = "Business-ready aggregated data - PRODUCTION" }
]

catalog_owner = "data-engineers"

# -----------------------------------------------------------------------------
# Storage Configuration
# -----------------------------------------------------------------------------
storage_account_name   = "stadatabricksprod"
storage_container_name = "unity-catalog"
access_connector_id    = "/subscriptions/12345678-1234-1234-1234-123456789abc/resourceGroups/rg-databricks-prod/providers/Microsoft.Databricks/accessConnectors/databricks-access-connector"

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
  Environment = "prod"
  ManagedBy   = "Terraform"
  CostCenter  = "DataPlatform"
  Criticality = "High"
}
