#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'authproject.settings')
django.setup()

from mt5_integration.models import AlgorithmExecution

def check_ea_status():
    execs = AlgorithmExecution.objects.all()
    print(f'Total executions: {execs.count()}')
    print('By status:')
    
    statuses = ['running', 'stopped', 'paused', 'error']
    for status in statuses:
        count = execs.filter(execution_status=status).count()
        print(f'  {status}: {count}')
    
    # Get all unique statuses
    all_statuses = set(exec.execution_status for exec in execs)
    print(f'All statuses found: {all_statuses}')
    
    # Show some example records
    print('\nExample records:')
    for exec in execs[:5]:
        print(f'  {exec.algorithm_name}: {exec.execution_status} (Started: {exec.started_at})')

if __name__ == '__main__':
    check_ea_status()
