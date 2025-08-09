import argparse, os
from azure.identity import DefaultAzureCredential
from azure.ai.ml import MLClient, load_job

p = argparse.ArgumentParser()
p.add_argument('--workspace', required=True)
p.add_argument('--resource-group', required=True)
p.add_argument('--subscription', default=os.environ.get('AZURE_SUBSCRIPTION_ID'))
args = p.parse_args()

ml_client = MLClient(
    DefaultAzureCredential(),
    subscription_id=args.subscription,
    resource_group_name=args.resource_group,
    workspace_name=args.workspace,
)

# Resolve YAML path relative to this script so it works in CI
here = os.path.dirname(os.path.abspath(__file__))
yaml_path = os.path.join(here, "MLOps", "Azure", "azure-mlops-project", "ml", "pipeline", "pipeline.yml")

job = load_job(path=yaml_path)
submitted = ml_client.jobs.create_or_update(job)
print(f"Submitted: {submitted.name}")
