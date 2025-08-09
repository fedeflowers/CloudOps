import os, sys
from azure.identity import DefaultAzureCredential
from azure.ai.ml import MLClient, load_job

sub = os.getenv("AZURE_SUBSCRIPTION_ID")
rg  = os.getenv("AZUREML_RESOURCE_GROUP")
ws  = os.getenv("AZUREML_WORKSPACE_NAME")
if not all([sub, rg, ws]):
    print("Set AZURE_SUBSCRIPTION_ID, AZUREML_RESOURCE_GROUP, AZUREML_WORKSPACE_NAME", file=sys.stderr)
    sys.exit(2)

client = MLClient(DefaultAzureCredential(), sub, rg, ws)
job = load_job("ml/pipelines/monitoring_pipeline.yml")
submitted = client.jobs.create_or_update(job)
print("Submitted monitoring:", submitted.name)
