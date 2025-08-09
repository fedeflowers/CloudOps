import argparse, os
from azure.identity import DefaultAzureCredential
from azure.ai.ml import MLClient
from azure.ai.ml.entities import Job

p = argparse.ArgumentParser()
p.add_argument('--workspace', required=True)
p.add_argument('--resource-group', required=True)
p.add_argument('--subscription', default=os.environ.get('AZURE_SUBSCRIPTION_ID'))
args = p.parse_args()

ml_client = MLClient(DefaultAzureCredential(), args.subscription, args.resource_group, args.workspace)
job = ml_client.jobs.create_or_update(Job.load('MLOps/Azure/azure-mlops-project/ml/pipeline/pipeline.yml'))
print(f"Submitted: {job.name}")