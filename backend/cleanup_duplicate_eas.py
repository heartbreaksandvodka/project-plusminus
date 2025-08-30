#!/usr/bin/env python
import os
import sys
import django
from datetime import datetime, timezone

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'authproject.settings')
django.setup()

from mt5_integration.models import AlgorithmExecution

def cleanup_duplicate_eas():
    """
    Clean up duplicate EA instances by keeping only the most recent one per EA name
    and marking older instances as 'stopped'.
    """
    print("Starting EA cleanup...")
    
    # Get all running executions
    running_executions = AlgorithmExecution.objects.filter(execution_status='running').order_by('algorithm_name', '-started_at')
    
    # Group by EA name
    ea_groups = {}
    for exec in running_executions:
        if exec.algorithm_name not in ea_groups:
            ea_groups[exec.algorithm_name] = []
        ea_groups[exec.algorithm_name].append(exec)
    
    total_stopped = 0
    
    for ea_name, executions in ea_groups.items():
        if len(executions) > 1:
            print(f"\nFound {len(executions)} instances of '{ea_name}':")
            
            # Keep the most recent one (first in the list due to ordering)
            most_recent = executions[0]
            print(f"  Keeping: ID {most_recent.id} (started: {most_recent.started_at})")
            
            # Stop the older ones
            for old_exec in executions[1:]:
                old_exec.execution_status = 'stopped'
                old_exec.stopped_at = datetime.now(timezone.utc)
                old_exec.save()
                print(f"  Stopped: ID {old_exec.id} (started: {old_exec.started_at})")
                total_stopped += 1
        else:
            print(f"\n'{ea_name}': Only 1 instance found (OK)")
    
    print(f"\nCleanup complete! Stopped {total_stopped} duplicate EA instances.")
    
    # Show final status
    print("\nFinal status:")
    final_running = AlgorithmExecution.objects.filter(execution_status='running').count()
    final_stopped = AlgorithmExecution.objects.filter(execution_status='stopped').count()
    print(f"  Running EAs: {final_running}")
    print(f"  Stopped EAs: {final_stopped}")

if __name__ == '__main__':
    cleanup_duplicate_eas()
