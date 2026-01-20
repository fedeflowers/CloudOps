# =============================================================================
# Terraform Variables
# =============================================================================
# Input variables for Unity Catalog infrastructure provisioning.
# =============================================================================

# -----------------------------------------------------------------------------
# Environment
# -----------------------------------------------------------------------------
variable "environment" {
  description = "Deployment environment (dev, prod)"
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "prod"], var.environment)
    error_message = "Environment must be either 'dev' or 'prod'."
  }
}

# -----------------------------------------------------------------------------
# Databricks Configuration
# -----------------------------------------------------------------------------
variable "databricks_host" {
  description = "Databricks workspace URL"
  type        = string
  sensitive   = true
}

variable "databricks_token" {
  description = "Databricks personal access token"
  type        = string
  sensitive   = true
}

variable "databricks_account_id" {
  description = "Databricks account ID for Unity Catalog"
  type        = string
  default     = ""
}

variable "databricks_workspace_id" {
  description = "Databricks workspace resource ID"
  type        = string
  default     = ""
}

# -----------------------------------------------------------------------------
# Unity Catalog Configuration
# -----------------------------------------------------------------------------
variable "metastore_id" {
  description = "Unity Catalog metastore ID"
  type        = string
}

variable "catalog_owner" {
  description = "Owner principal for catalogs"
  type        = string
  default     = "data-engineers"
}

variable "catalog_names" {
  description = "List of catalogs to create"
  type = list(object({
    name    = string
    comment = string
  }))
  default = [
    { name = "bronze", comment = "Raw data ingestion layer" },
    { name = "silver", comment = "Cleaned and transformed data" },
    { name = "gold", comment = "Business-ready aggregated data" }
  ]
}

# -----------------------------------------------------------------------------
# Storage Configuration
# -----------------------------------------------------------------------------
variable "storage_account_name" {
  description = "Azure Storage account for external locations"
  type        = string
}

variable "storage_container_name" {
  description = "Azure Storage container for Unity Catalog"
  type        = string
  default     = "unity-catalog"
}

# -----------------------------------------------------------------------------
# Access Control
# -----------------------------------------------------------------------------
variable "data_engineers_group" {
  description = "Data Engineers group name for access grants"
  type        = string
  default     = "data-engineers"
}

variable "data_scientists_group" {
  description = "Data Scientists group name for access grants"
  type        = string
  default     = "data-scientists"
}

variable "data_analysts_group" {
  description = "Data Analysts group name for access grants"
  type        = string
  default     = "data-analysts"
}

# -----------------------------------------------------------------------------
# Tags
# -----------------------------------------------------------------------------
variable "tags" {
  description = "Common tags for all resources"
  type        = map(string)
  default = {
    Project     = "Databricks-CICD"
    ManagedBy   = "Terraform"
    Environment = "dev"
  }
}
