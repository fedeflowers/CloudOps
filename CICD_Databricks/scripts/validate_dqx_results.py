#!/usr/bin/env python3
# =============================================================================
# Validate DQx Results Script
# =============================================================================
"""
Validates DQx data quality results and fails the pipeline if quality gates are not met.
Used by Azure DevOps pipeline for post-deployment validation.
"""

import argparse
import sys
from databricks.sdk import WorkspaceClient


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Validate DQx quality results")
    parser.add_argument("--host", required=True, help="Databricks workspace URL")
    parser.add_argument("--token", required=True, help="Databricks access token")
    parser.add_argument("--results-table", required=True, help="Table containing DQx results")
    parser.add_argument("--fail-on-error", action="store_true", help="Fail if any critical checks failed")
    parser.add_argument("--fail-on-warning", action="store_true", help="Fail if any warnings exist")
    return parser.parse_args()


def get_quality_results(client: WorkspaceClient, results_table: str) -> dict:
    """
    Retrieve quality check results from the results table.
    
    Returns:
        dict: Summary of quality check results
    """
    # Query for latest results
    query = f"""
    WITH latest_run AS (
        SELECT MAX(run_timestamp) as max_ts
        FROM {results_table}
    )
    SELECT 
        r.rule_name,
        r.severity,
        r.status,
        r.violation_count,
        r.message
    FROM {results_table} r
    JOIN latest_run l ON r.run_timestamp = l.max_ts
    ORDER BY 
        CASE r.severity 
            WHEN 'critical' THEN 1 
            WHEN 'warning' THEN 2 
            ELSE 3 
        END,
        r.rule_name
    """
    
    # Execute using statement execution API
    result = client.statement_execution.execute_statement(
        warehouse_id=get_default_warehouse_id(client),
        statement=query,
        wait_timeout="60s"
    )
    
    # Parse results
    results = {
        "critical_failures": [],
        "warnings": [],
        "passed": [],
        "total_checks": 0
    }
    
    if result.result and result.result.data_array:
        for row in result.result.data_array:
            rule_name, severity, status, violation_count, message = row
            results["total_checks"] += 1
            
            if status == "FAILED":
                if severity == "critical":
                    results["critical_failures"].append({
                        "rule": rule_name,
                        "violations": violation_count,
                        "message": message
                    })
                elif severity == "warning":
                    results["warnings"].append({
                        "rule": rule_name,
                        "violations": violation_count,
                        "message": message
                    })
            else:
                results["passed"].append(rule_name)
    
    return results


def get_default_warehouse_id(client: WorkspaceClient) -> str:
    """Get the first available SQL warehouse ID."""
    warehouses = client.warehouses.list()
    for wh in warehouses:
        if wh.state.value == "RUNNING":
            return wh.id
    raise ValueError("No running SQL warehouse found")


def print_results(results: dict) -> None:
    """Print formatted quality check results."""
    print("\n" + "=" * 60)
    print("DATA QUALITY RESULTS")
    print("=" * 60)
    
    print(f"\n📊 Total checks: {results['total_checks']}")
    print(f"✅ Passed: {len(results['passed'])}")
    print(f"⚠️  Warnings: {len(results['warnings'])}")
    print(f"❌ Critical failures: {len(results['critical_failures'])}")
    
    if results["critical_failures"]:
        print("\n" + "-" * 40)
        print("❌ CRITICAL FAILURES:")
        print("-" * 40)
        for failure in results["critical_failures"]:
            print(f"  • {failure['rule']}")
            print(f"    Violations: {failure['violations']}")
            print(f"    Message: {failure['message']}")
    
    if results["warnings"]:
        print("\n" + "-" * 40)
        print("⚠️  WARNINGS:")
        print("-" * 40)
        for warning in results["warnings"]:
            print(f"  • {warning['rule']}")
            print(f"    Violations: {warning['violations']}")
            print(f"    Message: {warning['message']}")
    
    if results["passed"]:
        print("\n" + "-" * 40)
        print("✅ PASSED CHECKS:")
        print("-" * 40)
        for check in results["passed"]:
            print(f"  • {check}")
    
    print("\n" + "=" * 60)


def main():
    """Main entry point."""
    args = parse_args()
    
    print("=" * 60)
    print("DQx Results Validation")
    print("=" * 60)
    print(f"Host: {args.host}")
    print(f"Results table: {args.results_table}")
    print("=" * 60)
    
    # Initialize client
    client = WorkspaceClient(
        host=args.host,
        token=args.token
    )
    
    try:
        # Get results
        results = get_quality_results(client, args.results_table)
        
        # Print results
        print_results(results)
        
        # Determine exit status
        if args.fail_on_error and results["critical_failures"]:
            print("\n❌ QUALITY GATE FAILED: Critical checks failed")
            sys.exit(1)
        
        if args.fail_on_warning and results["warnings"]:
            print("\n❌ QUALITY GATE FAILED: Warnings detected (fail-on-warning enabled)")
            sys.exit(1)
        
        if results["critical_failures"]:
            print("\n⚠️  Quality gate passed with critical failures (not blocking)")
        
        print("\n✅ QUALITY GATE PASSED")
        sys.exit(0)
            
    except Exception as e:
        print(f"\n❌ Error validating results: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
