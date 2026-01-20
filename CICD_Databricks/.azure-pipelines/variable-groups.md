# Azure DevOps Variable Groups Configuration

This document describes how to set up the required Variable Groups in Azure DevOps for the CI/CD pipeline.

## Prerequisites

1. Azure Key Vault with required secrets
2. Azure DevOps project with appropriate permissions
3. Service Connection to Azure subscription

---

## Variable Groups

### 1. `databricks-credentials`

**Purpose**: Databricks workspace authentication

| Variable | Key Vault Secret Name | Description |
|----------|----------------------|-------------|
| `DATABRICKS_HOST` | `databricks-host` | Workspace URL (e.g., `https://adb-xxx.azuredatabricks.net`) |
| `DATABRICKS_TOKEN` | `databricks-token` | Personal Access Token or Service Principal token |

**Setup Steps**:
1. Go to **Pipelines** → **Library** → **+ Variable group**
2. Name: `databricks-credentials`
3. Enable **Link secrets from an Azure key vault**
4. Select your Azure subscription and Key Vault
5. Add the secrets listed above

---

### 2. `azure-credentials`

**Purpose**: Azure authentication for Terraform

| Variable | Key Vault Secret Name | Description |
|----------|----------------------|-------------|
| `ARM_CLIENT_ID` | `arm-client-id` | Service Principal Application ID |
| `ARM_CLIENT_SECRET` | `arm-client-secret` | Service Principal Secret |
| `ARM_TENANT_ID` | `arm-tenant-id` | Azure AD Tenant ID |
| `ARM_SUBSCRIPTION_ID` | `arm-subscription-id` | Azure Subscription ID |

**Setup Steps**:
1. Go to **Pipelines** → **Library** → **+ Variable group**
2. Name: `azure-credentials`
3. Enable **Link secrets from an Azure key vault**
4. Select your Azure subscription and Key Vault
5. Add the secrets listed above

---

### 3. `terraform-backend`

**Purpose**: Terraform remote state storage

| Variable | Key Vault Secret Name | Description |
|----------|----------------------|-------------|
| `TF_BACKEND_RESOURCE_GROUP` | `tf-backend-rg` | Resource group containing storage account |
| `TF_BACKEND_STORAGE_ACCOUNT` | `tf-backend-storage` | Storage account name |
| `TF_BACKEND_CONTAINER` | `tf-backend-container` | Container name (e.g., `tfstate`) |
| `TF_BACKEND_KEY` | `tf-backend-key` | State file name (e.g., `databricks.tfstate`) |
| `TF_BACKEND_ACCESS_KEY` | `tf-backend-access-key` | Storage account access key |

**Setup Steps**:
1. Go to **Pipelines** → **Library** → **+ Variable group**
2. Name: `terraform-backend`
3. Enable **Link secrets from an Azure key vault**
4. Select your Azure subscription and Key Vault
5. Add the secrets listed above

---

## Key Vault Secrets Setup

### Azure CLI Commands

```bash
# Set variables
KEY_VAULT_NAME="kv-databricks-cicd"
RESOURCE_GROUP="rg-databricks-cicd"

# Create Key Vault (if not exists)
az keyvault create \
  --name $KEY_VAULT_NAME \
  --resource-group $RESOURCE_GROUP \
  --location westeurope

# Add Databricks secrets
az keyvault secret set --vault-name $KEY_VAULT_NAME \
  --name "databricks-host" \
  --value "https://adb-1234567890123456.16.azuredatabricks.net"

az keyvault secret set --vault-name $KEY_VAULT_NAME \
  --name "databricks-token" \
  --value "dapi_your_token_here"

# Add Azure credentials
az keyvault secret set --vault-name $KEY_VAULT_NAME \
  --name "arm-client-id" \
  --value "your-client-id"

az keyvault secret set --vault-name $KEY_VAULT_NAME \
  --name "arm-client-secret" \
  --value "your-client-secret"

az keyvault secret set --vault-name $KEY_VAULT_NAME \
  --name "arm-tenant-id" \
  --value "your-tenant-id"

az keyvault secret set --vault-name $KEY_VAULT_NAME \
  --name "arm-subscription-id" \
  --value "your-subscription-id"

# Add Terraform backend secrets
az keyvault secret set --vault-name $KEY_VAULT_NAME \
  --name "tf-backend-rg" \
  --value "rg-databricks-cicd"

az keyvault secret set --vault-name $KEY_VAULT_NAME \
  --name "tf-backend-storage" \
  --value "stterraformstate"

az keyvault secret set --vault-name $KEY_VAULT_NAME \
  --name "tf-backend-container" \
  --value "tfstate"

az keyvault secret set --vault-name $KEY_VAULT_NAME \
  --name "tf-backend-key" \
  --value "databricks-cicd.tfstate"

# Get storage account key and store it
STORAGE_KEY=$(az storage account keys list \
  --resource-group $RESOURCE_GROUP \
  --account-name stterraformstate \
  --query '[0].value' -o tsv)

az keyvault secret set --vault-name $KEY_VAULT_NAME \
  --name "tf-backend-access-key" \
  --value "$STORAGE_KEY"
```

---

## Service Principal Setup

### Create Service Principal

```bash
# Create service principal for Databricks CI/CD
az ad sp create-for-rbac \
  --name "sp-databricks-cicd" \
  --role "Contributor" \
  --scopes "/subscriptions/YOUR_SUBSCRIPTION_ID" \
  --sdk-auth

# Grant additional permissions for Unity Catalog
az role assignment create \
  --assignee "SP_CLIENT_ID" \
  --role "Storage Blob Data Contributor" \
  --scope "/subscriptions/YOUR_SUBSCRIPTION_ID/resourceGroups/rg-databricks-data/providers/Microsoft.Storage/storageAccounts/YOUR_STORAGE_ACCOUNT"
```

### Databricks Workspace Permissions

The service principal needs the following permissions in Databricks:
- Workspace access
- Unity Catalog admin (for catalog/schema creation)
- Job creation and execution rights

```bash
# Add service principal to Databricks workspace using SCIM API or UI
# Navigate to: Admin Console → Service Principals → Add
```

---

## Pipeline Authorization

After creating variable groups, authorize the pipeline to use them:

1. Go to **Pipelines** → **Library**
2. Click on each variable group
3. Go to **Pipeline permissions**
4. Click **+** and add your pipeline
5. Or enable **Allow access to all pipelines**

---

## Verification

### Test Variable Group Access

Create a simple test pipeline to verify access:

```yaml
trigger: none

variables:
  - group: databricks-credentials
  - group: azure-credentials
  - group: terraform-backend

pool:
  vmImage: 'ubuntu-latest'

steps:
  - script: |
      echo "Testing variable group access..."
      echo "DATABRICKS_HOST is set: $([ -n '$DATABRICKS_HOST' ] && echo 'YES' || echo 'NO')"
      echo "ARM_CLIENT_ID is set: $([ -n '$ARM_CLIENT_ID' ] && echo 'YES' || echo 'NO')"
    displayName: 'Verify Variable Groups'
    env:
      DATABRICKS_HOST: $(DATABRICKS_HOST)
      ARM_CLIENT_ID: $(ARM_CLIENT_ID)
```

---

## Security Best Practices

1. **Rotate secrets regularly** - Set up Key Vault secret rotation
2. **Use managed identities** when possible instead of service principal secrets
3. **Limit permissions** - Service principal should have minimum required permissions
4. **Audit access** - Enable Key Vault diagnostic logging
5. **Separate environments** - Use different Key Vaults/Service Principals for dev and prod
