#!/usr/bin/env python3
# =============================================================================
# Trigger DQx Workflow Script
# =============================================================================
"""
Triggers a DQx data quality workflow in Databricks and waits for completion.
Used by Azure DevOps pipeline for post-deployment validation.
"""

import argparse
import sys
import time
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.jobs import RunLifeCycleState


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Trigger DQx workflow in Databricks")
    parser.add_argument("--host", required=True, help="Databricks workspace URL")
    parser.add_argument("--token", required=True, help="Databricks access token")
    parser.add_argument("--workflow-name", required=True, help="Name of the workflow to trigger")
    parser.add_argument("--timeout", type=int, default=1800, help="Timeout in seconds (default: 1800)")
    return parser.parse_args()


def get_job_id_by_name(client: WorkspaceClient, job_name: str) -> int:
    """Find job ID by name."""
    jobs = client.jobs.list(name=job_name)
    for job in jobs:
        if job.settings.name == job_name:
            return job.job_id
    raise ValueError(f"Job '{job_name}' not found in workspace")


def trigger_and_wait(client: WorkspaceClient, job_id: int, timeout: int) -> bool:
    """
    Trigger a job run and wait for completion.
    
    Returns:
        bool: True if job succeeded, False otherwise
    """
    print(f"Triggering job {job_id}...")
    run = client.jobs.run_now(job_id=job_id)
    run_id = run.run_id
    print(f"Run started with ID: {run_id}")
    
    start_time = time.time()
    terminal_states = {
        RunLifeCycleState.TERMINATED,
        RunLifeCycleState.SKIPPED,
        RunLifeCycleState.INTERNAL_ERROR
    }
    
    while True:
        elapsed = time.time() - start_time
        if elapsed > timeout:
            print(f"ERROR: Timeout after {timeout} seconds")
            return False
        
        run_status = client.jobs.get_run(run_id=run_id)
        state = run_status.state.life_cycle_state
        
        print(f"Run status: {state.value} (elapsed: {int(elapsed)}s)")
        
        if state in terminal_states:
            result_state = run_status.state.result_state
            if result_state and result_state.value == "SUCCESS":
                print(f"✅ Job completed successfully!")
                return True
            else:
                print(f"❌ Job failed with state: {result_state}")
                return False
        
        time.sleep(30)  # Poll every 30 seconds


def main():
    """Main entry point."""
    args = parse_args()
    
    print("=" * 60)
    print("DQx Workflow Trigger")
    print("=" * 60)
    print(f"Host: {args.host}")
    print(f"Workflow: {args.workflow_name}")
    print(f"Timeout: {args.timeout}s")
    print("=" * 60)
    
    # Initialize client
    client = WorkspaceClient(
        host=args.host,
        token=args.token
    )
    
    try:
        # Find job by name
        job_id = get_job_id_by_name(client, args.workflow_name)
        print(f"Found job ID: {job_id}")
        
        # Trigger and wait
        success = trigger_and_wait(client, job_id, args.timeout)
        
        if success:
            print("\n✅ DQx workflow completed successfully")
            sys.exit(0)
        else:
            print("\n❌ DQx workflow failed")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
