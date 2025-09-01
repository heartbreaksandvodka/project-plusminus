#!/usr/bin/env python
"""
Test script for MT5 automation with fresh account credentials
Account: 211047814
Password: Johannes@0  
Server: Exness-MT5Trial9

This script tests the complete automation flow with new account details.
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

from mt5_integration.mt5_auto_manager import MT5AutoManager, MT5SmartConnection
from mt5_integration.mt5_service import MT5ConnectionManager
import time


def test_fresh_account_automation():
    """Test complete automation flow with fresh account"""
    
    print("=" * 60)
    print("🧪 TESTING MT5 AUTOMATION WITH FRESH ACCOUNT")
    print("=" * 60)
    
    # New account credentials
    account_number = "211047814"
    password = "Johannes@0"
    server = "Exness-MT5Trial9"
    
    print(f"📋 Test Account Details:")
    print(f"   Account: {account_number}")
    print(f"   Server: {server}")
    print(f"   Password: {'*' * len(password)}")
    print()
    
    # Test 1: Check MT5 Status
    print("🔍 STEP 1: Checking MT5 System Status")
    print("-" * 40)
    
    status = MT5AutoManager.get_status()
    print(f"   MT5 Terminal Running: {status['mt5_terminal_running']}")
    print(f"   MT5 Executable Found: {status['mt5_executable_found']}")
    print(f"   MT5 API Initialized: {status['mt5_api_initialized']}")
    print(f"   Currently Logged In: {status['logged_in']}")
    
    if status['account_info']:
        print(f"   Current Account: {status['account_info']['login']}")
    print()
    
    # Test 2: Smart Connection Attempt
    print("🚀 STEP 2: Testing Smart Connection")
    print("-" * 40)
    
    try:
        success, result = MT5SmartConnection.connect(account_number, password, server)
        
        if success:
            print("✅ Smart Connection SUCCESSFUL!")
            print(f"   Account Login: {result['account_info']['login']}")
            print(f"   Balance: ${result['account_info']['balance']:,.2f}")
            print(f"   Equity: ${result['account_info']['equity']:,.2f}")
            print(f"   Currency: {result['account_info']['currency']}")
            print(f"   Company: {result['account_info']['company']}")
            print(f"   Server: {result['account_info']['server']}")
            print(f"   Terminal Build: {result['terminal_info']['build']}")
            print(f"   Automation Used: {result.get('automation_used', False)}")
        else:
            print("❌ Smart Connection FAILED!")
            print(f"   Error: {result['error']}")
            if 'details' in result:
                print(f"   Details: {result['details']}")
            if 'solution' in result:
                print(f"   Solution: {result['solution']}")
            if 'manual_steps' in result:
                print("   Manual Steps Required:")
                for step in result['manual_steps']:
                    print(f"     {step['step']}. {step['action']}: {step['description']}")
    except Exception as e:
        print(f"❌ Smart Connection EXCEPTION: {e}")
    
    print()
    
    # Test 3: Direct Connection Manager Test
    print("🔧 STEP 3: Testing Connection Manager")
    print("-" * 40)
    
    try:
        connection_manager = MT5ConnectionManager()
        success, result = connection_manager.test_connection(account_number, password, server)
        
        if success:
            print("✅ Connection Manager SUCCESSFUL!")
            print(f"   Account: {result['account_info']['login']}")
            print(f"   Balance: ${result['account_info']['balance']:,.2f}")
            print(f"   Server: {result['account_info']['server']}")
        else:
            print("❌ Connection Manager FAILED!")
            print(f"   Error: {result['error']}")
            if 'details' in result:
                print(f"   Details: {result['details']}")
    except Exception as e:
        print(f"❌ Connection Manager EXCEPTION: {e}")
    
    print()
    
    # Test 4: Terminal Management
    print("🖥️  STEP 4: Testing Terminal Management")
    print("-" * 40)
    
    exe_path = MT5AutoManager.find_mt5_executable()
    if exe_path:
        print(f"   MT5 Executable: {exe_path}")
        
        terminal_running = MT5AutoManager.is_mt5_running()
        print(f"   Terminal Running: {terminal_running}")
        
        if not terminal_running:
            print("   Attempting to start terminal...")
            start_result = MT5AutoManager.start_mt5_terminal(exe_path)
            print(f"   Start Result: {start_result}")
            
            if start_result:
                print("   Waiting for terminal to initialize...")
                time.sleep(3)
                
                terminal_running = MT5AutoManager.is_mt5_running()
                print(f"   Terminal Running After Start: {terminal_running}")
    else:
        print("   ❌ MT5 Executable not found!")
    
    print()
    
    # Test 5: Final Status Check
    print("📊 STEP 5: Final System Status")
    print("-" * 40)
    
    final_status = MT5AutoManager.get_status()
    print(f"   System Ready: {final_status['mt5_terminal_running'] and final_status['mt5_api_initialized']}")
    print(f"   Account Connected: {final_status['logged_in']}")
    
    if final_status['account_info']:
        account_info = final_status['account_info']
        print(f"   Connected Account: {account_info['login']}")
        print(f"   Server: {account_info['server']}")
        print(f"   Company: {account_info['company']}")
    
    print()
    print("=" * 60)
    print("🏁 TEST COMPLETE")
    print("=" * 60)


def test_automation_components():
    """Test individual automation components"""
    
    print("\n🔬 COMPONENT TESTS")
    print("=" * 40)
    
    # Test terminal detection
    print("1. Terminal Detection:")
    running = MT5AutoManager.is_mt5_running()
    print(f"   Is MT5 Running: {running}")
    
    # Test executable finding
    print("\n2. Executable Detection:")
    exe_path = MT5AutoManager.find_mt5_executable()
    print(f"   Executable Path: {exe_path}")
    
    # Test status reporting
    print("\n3. Status Reporting:")
    status = MT5AutoManager.get_status()
    for key, value in status.items():
        if key != 'account_info':  # Skip detailed account info for brevity
            print(f"   {key}: {value}")


if __name__ == "__main__":
    try:
        test_fresh_account_automation()
        test_automation_components()
    except KeyboardInterrupt:
        print("\n\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n\n💥 Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
