import argparse, os, sys
from pathlib import Path
from azure.identity import DefaultAzureCredential
from azure.ai.ml import MLClient, load_job

p = argparse.ArgumentParser()
p.add_argument('--workspace', required=True)
p.add_argument('--resource-group', required=True)
p.add_argument('--subscription', default=os.environ.get('AZURE_SUBSCRIPTION_ID'))
args = p.parse_args()

if not args.subscription:
    print("ERROR: --subscription not provided and AZURE_SUBSCRIPTION_ID not set.",
          file=sys.stderr)
    sys.exit(2)

ml_client = MLClient(
    DefaultAzureCredential(),
    subscription_id=args.subscription,
    resource_group_name=args.resource_group,
    workspace_name=args.workspace,
)

# pipeline.yml sits next to this script
here = Path(__file__).resolve().parent
yaml_path = here / "pipeline.yml"

if not yaml_path.exists():
    print(f"ERROR: pipeline.yml not found at {yaml_path}", file=sys.stderr)
    sys.exit(2)

job = load_job(str(yaml_path))  # positional arg for older azure-ai-ml versions
submitted = ml_client.jobs.create_or_update(job)
print(f"Submitted: {submitted.name}")
