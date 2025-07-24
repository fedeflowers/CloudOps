# terraform-azure-pipeline

This project contains Azure DevOps pipelines and Terraform configurations for managing resources in Azure.

## Project Structure

```
terraform-azure-pipeline
├── azure-pipelines
│   ├── dev-pipeline.yml       # Azure DevOps pipeline for the development environment
│   └── prod-pipeline.yml      # Azure DevOps pipeline for the production environment
├── terraform
│   ├── main.tf                # Main Terraform configuration file
│   ├── variables.tf           # Variables used in the Terraform configuration
│   ├── providers.tf           # Providers required for the Terraform configuration
│   └── environments
│       ├── dev
│       │   └── terraform.tfvars # Variable values for the development environment
│       └── prod
│           └── terraform.tfvars # Variable values for the production environment
├── .gitignore                  # Files and directories to be ignored by Git
└── README.md                   # Documentation for the project
```

## Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd terraform-azure-pipeline
   ```

2. **Configure Azure DevOps Pipelines:**
   - Set up the `dev-pipeline.yml` and `prod-pipeline.yml` in Azure DevOps to automate the build, test, and deployment processes.

3. **Terraform Configuration:**
   - Update the `variables.tf` file with necessary variables.
   - Modify the `main.tf` file to define the Azure resources you want to create.
   - Use the `terraform.tfvars` files in the respective environment folders to set environment-specific values.

4. **Deployment:**
   - Run the Terraform commands to initialize and apply the configuration:
     ```bash
     cd terraform
     terraform init
     terraform apply
     ```

## Usage

- Follow the instructions in the Azure DevOps pipelines to build and deploy your application.
- Use Terraform to manage your Azure resources as defined in the configuration files.

## Contributing

Feel free to submit issues or pull requests for improvements or additional features.