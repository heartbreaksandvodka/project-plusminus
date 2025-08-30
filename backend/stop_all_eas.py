#!/usr/bin/env python
import os
import sys
import django
from datetime import datetime, timezone

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'authproject.settings')
django.setup()

from mt5_integration.models import AlgorithmExecution
from mt5_integration.mt5_service import MT5AlgorithmManager

def stop_all_running_eas():
    """Stop all currently running EAs."""
    print("Stopping all running EAs...")
    
    # Get all running executions
    running_executions = AlgorithmExecution.objects.filter(execution_status='running')
    
    if not running_executions.exists():
        print("No running EAs found.")
        return
    
    total_stopped = 0
    
    for execution in running_executions:
        print(f"\nStopping EA: {execution.algorithm_name} (ID: {execution.id})")
        
        # Try to stop the process if PID exists
        if execution.pid:
            try:
                result = MT5AlgorithmManager.stop_algorithm(execution.pid)
                if result.get('status') == 'success':
                    print(f"  Process stopped successfully (PID: {execution.pid})")
                else:
                    print(f"  Process stop failed, but marking as stopped anyway")
            except Exception as e:
                print(f"  Error stopping process: {e}")
        else:
            print(f"  No PID found, marking as stopped")
        
        # Mark as stopped in database
        execution.execution_status = 'stopped'
        execution.stopped_at = datetime.now(timezone.utc)
        execution.save()
        total_stopped += 1
        print(f"  Marked as stopped in database")
    
    print(f"\nStopped {total_stopped} EA{'s' if total_stopped != 1 else ''}.")
    
    # Show final status
    print("\nFinal status:")
    final_running = AlgorithmExecution.objects.filter(execution_status='running').count()
    final_stopped = AlgorithmExecution.objects.filter(execution_status='stopped').count()
    print(f"  Running EAs: {final_running}")
    print(f"  Stopped EAs: {final_stopped}")

if __name__ == '__main__':
    stop_all_running_eas()
