import os, sys, datetime as dt
from azure.identity import DefaultAzureCredential
from azure.ai.ml import MLClient, load_job
from azure.ai.ml.entities import Schedule
from azure.ai.ml.constants import TimeZone

sub = os.getenv("AZURE_SUBSCRIPTION_ID")
rg  = os.getenv("AZUREML_RESOURCE_GROUP")
ws  = os.getenv("AZUREML_WORKSPACE_NAME")
if not all([sub, rg, ws]):
    print("Set AZURE_SUBSCRIPTION_ID, AZUREML_RESOURCE_GROUP, AZUREML_WORKSPACE_NAME", file=sys.stderr)
    sys.exit(2)

client = MLClient(DefaultAzureCredential(), sub, rg, ws)

job = load_job("ml/pipelines/monitoring_pipeline.yml")

# Create/update a daily 08:00 schedule
sched = Schedule(
    name="daily-drift-monitor",
    display_name="Daily Drift Monitor",
    description="Runs the drift-only pipeline every morning",
    trigger={"type": "recurrence", "frequency": "day", "interval": 1,
             "schedule": {"hours": [8], "minutes": [0]},
             "time_zone": TimeZone.UTC},
    create_job=job,
)

created = client.schedules.begin_create_or_update(sched).result()
print("Schedule:", created.name, "->", created.status)
