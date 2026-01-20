# Databricks CI/CD Automation

End-to-end CI/CD pipeline implementation for Databricks, enforcing infrastructure-as-code (IaC), automated testing, and strict data quality gates.

![Pipeline Overview](https://img.shields.io/badge/Pipeline-Azure%20DevOps-blue)
![IaC](https://img.shields.io/badge/IaC-Terraform-purple)
![Deployment](https://img.shields.io/badge/Deployment-DABs-orange)
![Testing](https://img.shields.io/badge/Testing-Pytest-green)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Pipeline Stages](#pipeline-stages)
- [Configuration](#configuration)
- [Local Development](#local-development)
- [Deployment Commands](#deployment-commands)
- [Troubleshooting](#troubleshooting)

---

## Overview

This project provides a complete CI/CD solution for Databricks workloads with:

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Orchestrator** | Azure DevOps | Pipeline automation |
| **Compute** | Azure Databricks | Data processing platform |
| **Infrastructure** | Terraform | Unity Catalog governance |
| **Deployment** | DABs | Job and artifact deployment |
| **Testing** | Pytest | Unit test execution |
| **Data Quality** | DQx | Post-deployment validation |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Azure DevOps Pipeline                              │
├─────────────────┬─────────────────┬─────────────────┬─────────────────────────┤
│   Stage 1: CI   │  Stage 2: IaC   │   Stage 3: CD   │  Stage 4: Data Quality  │
│                 │                 │                 │                         │
│  ┌───────────┐  │  ┌───────────┐  │  ┌───────────┐  │  ┌───────────────────┐  │
│  │  Pytest   │  │  │ Terraform │  │  │   DABs    │  │  │       DQx         │  │
│  │  Unit     │──│──│   Plan    │──│──│  Validate │──│──│  Quality Checks   │  │
│  │  Tests    │  │  │   Apply   │  │  │   Deploy  │  │  │  Quality Gates    │  │
│  └───────────┘  │  └───────────┘  │  └───────────┘  │  └───────────────────┘  │
└─────────────────┴─────────────────┴─────────────────┴─────────────────────────┘
                                        │
                                        ▼
                    ┌─────────────────────────────────────┐
                    │        Azure Databricks             │
                    │  ┌─────────┐ ┌─────────┐ ┌───────┐  │
                    │  │ Bronze  │ │ Silver  │ │ Gold  │  │
                    │  │ Catalog │ │ Catalog │ │Catalog│  │
                    │  └─────────┘ └─────────┘ └───────┘  │
                    └─────────────────────────────────────┘
```

---

## Prerequisites

### Required Tools

```bash
# Terraform (>= 1.5.0)
terraform --version

# Databricks CLI
databricks --version

# Python (>= 3.10)
python --version

# Azure CLI (for authentication)
az --version
```

### Azure DevOps Setup

1. **Create Variable Groups** linked to Azure Key Vault:
   - `databricks-credentials`
   - `azure-credentials`
   - `terraform-backend`

2. **Create Service Connection** for Azure subscription

3. **Install Pipeline Extensions**:
   - Terraform Tasks
   - Python Tasks

---

## Quick Start

### 1. Clone and Configure

```bash
# Clone the repository
git clone https://github.com/your-org/CICD_Databricks.git
cd CICD_Databricks

# Update configuration
# Edit config/environments.yml with your values
```

### 2. Install Dependencies

```bash
# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (Linux/macOS)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Run Tests Locally

```bash
# Run all unit tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=databricks_bundles/src --cov-report=html
```

### 4. Validate Terraform

```bash
cd terraform

# Initialize Terraform
terraform init -backend=false

# Validate configuration
terraform validate

# Preview changes (dev)
terraform plan -var-file=environments/dev.tfvars
```

### 5. Validate DABs

```bash
cd databricks_bundles

# Configure Databricks CLI
databricks configure --token

# Validate bundle
databricks bundle validate --target dev
```

---

## Project Structure

```
CICD_Databricks/
├── .azure-pipelines/           # Azure DevOps pipeline definitions
│   ├── azure-pipelines.yml     # Main pipeline
│   └── templates/              # Stage templates
│       ├── ci-stage.yml
│       ├── terraform-stage.yml
│       ├── dabs-stage.yml
│       └── dqx-stage.yml
│
├── config/                     # Configuration files
│   └── environments.yml        # Environment-specific settings
│
├── terraform/                  # Infrastructure as Code
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   ├── providers.tf
│   ├── unity_catalog/          # Unity Catalog resources
│   │   ├── catalogs.tf
│   │   ├── schemas.tf
│   │   ├── external_locations.tf
│   │   ├── volumes.tf
│   │   └── grants.tf
│   └── environments/           # Environment variables
│       ├── dev.tfvars
│       └── prod.tfvars
│
├── databricks_bundles/         # Databricks Asset Bundles
│   ├── databricks.yml          # Bundle configuration
│   ├── resources/
│   │   └── jobs.yml            # Workflow definitions
│   └── src/
│       └── notebooks/          # Databricks notebooks
│           ├── bronze/
│           ├── silver/
│           └── gold/
│
├── tests/                      # Unit tests
│   ├── pytest.ini
│   ├── conftest.py
│   └── unit/
│       └── test_sample.py
│
├── dqx/                        # Data Quality configuration
│   └── dqx_config.yml
│
├── scripts/                    # Utility scripts
│   ├── trigger_dqx_workflow.py
│   └── validate_dqx_results.py
│
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

---

## Pipeline Stages

### Stage 1: Continuous Integration (CI)

**Objective**: Validate code logic with unit tests.

```bash
# Manual execution
pytest tests/ --junitxml=test-results/junit.xml -v
```

**Gate**: Pipeline fails if tests fail.

---

### Stage 2: Infrastructure Provisioning

**Objective**: Manage Unity Catalog governance objects.

```bash
# Initialize
terraform init

# Plan changes
terraform plan -var-file=environments/dev.tfvars -out=tfplan

# Apply changes
terraform apply tfplan
```

**Resources Created**:
- Catalogs (bronze, silver, gold)
- Schemas per catalog
- External locations
- Volumes
- Access grants

**Gate**: Auto-approved on `main`, manual approval on feature branches.

---

### Stage 3: Continuous Deployment (CD)

**Objective**: Deploy jobs and artifacts to Databricks.

```bash
# Validate bundle
databricks bundle validate --target dev

# Deploy bundle
databricks bundle deploy --target dev

# Deploy to production
databricks bundle deploy --target prod
```

**Resources Deployed**:
- Workflows/Jobs
- Python libraries
- Notebooks

---

### Stage 4: Data Quality (DQx)

**Objective**: Verify end-to-end data integrity.

```bash
# Trigger DQx workflow
python scripts/trigger_dqx_workflow.py \
  --host $DATABRICKS_HOST \
  --token $DATABRICKS_TOKEN \
  --workflow-name "dqx_post_deployment_checks"

# Validate results
python scripts/validate_dqx_results.py \
  --host $DATABRICKS_HOST \
  --token $DATABRICKS_TOKEN \
  --results-table "gold.dqx.quality_results" \
  --fail-on-error
```

**Gate**: Pipeline fails if critical quality checks fail.

---

## Configuration

### Environment Configuration (`config/environments.yml`)

Update the following values for your environment:

| Section | Key | Description |
|---------|-----|-------------|
| `azure.subscription_id` | Your Azure subscription ID |
| `databricks.dev.workspace_url` | Dev workspace URL |
| `databricks.prod.workspace_url` | Prod workspace URL |
| `unity_catalog.storage.account_name` | Storage account for Unity Catalog |

### Azure DevOps Variable Groups

Create the following variable groups in Azure DevOps:

#### `databricks-credentials`
| Variable | Source |
|----------|--------|
| `DATABRICKS_HOST` | Key Vault |
| `DATABRICKS_TOKEN` | Key Vault |

#### `azure-credentials`
| Variable | Source |
|----------|--------|
| `ARM_CLIENT_ID` | Key Vault |
| `ARM_CLIENT_SECRET` | Key Vault |
| `ARM_TENANT_ID` | Key Vault |
| `ARM_SUBSCRIPTION_ID` | Key Vault |

#### `terraform-backend`
| Variable | Source |
|----------|--------|
| `TF_BACKEND_STORAGE_ACCOUNT` | Key Vault |
| `TF_BACKEND_CONTAINER` | Key Vault |
| `TF_BACKEND_KEY` | Key Vault |
| `TF_BACKEND_ACCESS_KEY` | Key Vault |

---

## Local Development

### Setup

```bash
# Clone repository
git clone <repository-url>
cd CICD_Databricks

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/macOS

# Install dependencies
pip install -r requirements.txt
```

### Configure Databricks CLI

```bash
# Interactive configuration
databricks configure --token

# Or set environment variables
export DATABRICKS_HOST="https://adb-xxx.azuredatabricks.net"
export DATABRICKS_TOKEN="dapi..."
```

### Configure Terraform

```bash
# Set Azure credentials
export ARM_CLIENT_ID="..."
export ARM_CLIENT_SECRET="..."
export ARM_TENANT_ID="..."
export ARM_SUBSCRIPTION_ID="..."

# Initialize with local backend (for testing)
cd terraform
terraform init -backend=false
```

---

## Deployment Commands

### Complete Command Reference

```bash
# =============================================================================
# TESTING
# =============================================================================

# Run all tests
pytest tests/ -v

# Run unit tests only
pytest tests/unit/ -v -m unit

# Run with coverage report
pytest tests/ --cov=databricks_bundles/src --cov-report=html

# Run specific test file
pytest tests/unit/test_sample.py -v

# Run tests in parallel
pytest tests/ -n auto

# =============================================================================
# TERRAFORM
# =============================================================================

# Initialize Terraform
cd terraform
terraform init

# Format configuration files
terraform fmt -recursive

# Validate configuration
terraform validate

# Plan for dev environment
terraform plan -var-file=environments/dev.tfvars -out=tfplan

# Plan for prod environment
terraform plan -var-file=environments/prod.tfvars -out=tfplan

# Apply changes
terraform apply tfplan

# Destroy resources (CAUTION!)
terraform destroy -var-file=environments/dev.tfvars

# Show current state
terraform show

# List resources
terraform state list

# =============================================================================
# DATABRICKS ASSET BUNDLES
# =============================================================================

# Validate bundle (dev)
cd databricks_bundles
databricks bundle validate --target dev

# Validate bundle (prod)
databricks bundle validate --target prod

# Deploy to dev
databricks bundle deploy --target dev

# Deploy to prod
databricks bundle deploy --target prod

# Destroy bundle resources
databricks bundle destroy --target dev

# Show bundle summary
databricks bundle summary --target dev

# Run a job from the bundle
databricks bundle run sales_ingestion_job --target dev

# =============================================================================
# DATA QUALITY (DQx)
# =============================================================================

# Trigger DQx workflow
python scripts/trigger_dqx_workflow.py \
  --host $DATABRICKS_HOST \
  --token $DATABRICKS_TOKEN \
  --workflow-name "dqx_post_deployment_checks" \
  --timeout 1800

# Validate DQx results
python scripts/validate_dqx_results.py \
  --host $DATABRICKS_HOST \
  --token $DATABRICKS_TOKEN \
  --results-table "gold.dqx.quality_results" \
  --fail-on-error

# =============================================================================
# CODE QUALITY
# =============================================================================

# Format code with Black
black databricks_bundles/ tests/

# Sort imports
isort databricks_bundles/ tests/

# Lint with flake8
flake8 databricks_bundles/ tests/

# Type checking
mypy databricks_bundles/

# =============================================================================
# UTILITY COMMANDS
# =============================================================================

# List Databricks jobs
databricks jobs list

# Get job details
databricks jobs get --job-id <JOB_ID>

# List catalogs
databricks unity-catalog catalogs list

# List schemas in a catalog
databricks unity-catalog schemas list --catalog-name bronze
```

---

## Environment Strategy

| Environment | Trigger | Terraform | DABs Target | DQx |
|-------------|---------|-----------|-------------|-----|
| **Dev** | Feature branches | Manual approval | `dev` | Optional |
| **Prod** | `main` branch | Auto-approved | `prod` | Required |

### Branch Strategy

```
main           ──●────────●────────●─────────────► (Production)
                 │        ↑        │
develop        ──●────────●────────●─────────────► (Integration)
                 │        │        ↑
feature/xyz    ──●────────●────────┘               (Development)
```

---

## Troubleshooting

### Common Issues

#### Terraform State Lock

```bash
# Force unlock (use with caution)
terraform force-unlock <LOCK_ID>
```

#### DABs Deployment Fails

```bash
# Check bundle validation
databricks bundle validate --target dev

# Check workspace connectivity
databricks workspace list /Users
```

#### DQx Workflow Not Found

```bash
# List available jobs
databricks jobs list --output json | jq '.jobs[] | select(.settings.name | contains("dqx"))'
```

### Logs and Debugging

```bash
# Enable Terraform debug logging
export TF_LOG=DEBUG
terraform plan -var-file=environments/dev.tfvars

# Enable Databricks CLI debug
export DATABRICKS_DEBUG=true
databricks bundle deploy --target dev
```

---

## Contributing

1. Create a feature branch from `develop`
2. Make changes and add tests
3. Run `pytest` and ensure all tests pass
4. Submit a pull request to `develop`

---

## License

This project is licensed under the MIT License.

---

## Support

For issues and questions:
- Create a GitHub issue
- Contact: data-platform-team@company.com
