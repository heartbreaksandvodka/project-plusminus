#!/usr/bin/env python
"""
Quick verification that the new account credentials work
"""

import os
import sys
import django
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'authproject.settings')
django.setup()

from mt5_integration.mt5_service import MT5ConnectionManager

def quick_test():
    print("🔍 Quick verification of new account credentials...")
    
    # New account details
    account_number = "211047814"
    password = "Johannes@0"
    server = "Exness-MT5Trial9"
    
    # Test connection
    success, result = MT5ConnectionManager.test_connection(account_number, password, server)
    
    if success:
        print("✅ New account credentials working perfectly!")
        print(f"   Account: {result['account_info']['login']}")
        print(f"   Balance: ${result['account_info']['balance']:,.2f}")
        print(f"   Server: {result['account_info']['server']}")
    else:
        print("❌ Connection failed:")
        print(f"   Error: {result['error']}")
    
    return success

if __name__ == "__main__":
    quick_test()
