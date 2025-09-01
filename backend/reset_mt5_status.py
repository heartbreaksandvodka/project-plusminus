#!/usr/bin/env python
"""
Check MT5 terminal status and reset if needed
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

from mt5_integration.mt5_auto_manager import MT5AutoManager
import time

def reset_mt5_terminal():
    print("🔍 Checking MT5 terminal status...")
    
    # Check current status
    status = MT5AutoManager.get_status()
    print(f"   Terminal Running: {status['mt5_terminal_running']}")
    print(f"   API Initialized: {status['mt5_api_initialized']}")
    print(f"   Currently Logged In: {status['logged_in']}")
    
    if status['account_info']:
        print(f"   Current Account: {status['account_info']['login']}")
    
    # If MT5 is running but not responding properly, restart it
    if status['mt5_terminal_running'] and not status['mt5_api_initialized']:
        print("\n🔄 MT5 terminal appears to be in bad state, attempting restart...")
        
        # Try to shutdown API first
        try:
            import MetaTrader5 as mt5
            mt5.shutdown()
            print("   API shutdown completed")
        except:
            print("   API shutdown failed (expected)")
        
        # Wait a moment
        time.sleep(2)
        
        # Check if we can now connect with new credentials
        from mt5_integration.mt5_service import MT5ConnectionManager
        success, result = MT5ConnectionManager.test_connection("211047814", "Johannes@0", "Exness-MT5Trial9")
        
        if success:
            print("✅ Connection successful after reset!")
            print(f"   Account: {result['account_info']['login']}")
            print(f"   Balance: ${result['account_info']['balance']:,.2f}")
        else:
            print("❌ Still having connection issues:")
            print(f"   Error: {result['error']}")
    
    elif not status['mt5_terminal_running']:
        print("\n🚀 Starting MT5 terminal...")
        exe_path = MT5AutoManager.find_mt5_executable()
        if exe_path:
            success = MT5AutoManager.start_mt5_terminal(exe_path)
            if success:
                print("   Terminal started successfully")
                time.sleep(3)
                
                # Try connection
                from mt5_integration.mt5_service import MT5ConnectionManager
                success, result = MT5ConnectionManager.test_connection("211047814", "Johannes@0", "Exness-MT5Trial9")
                
                if success:
                    print("✅ Connection successful!")
                    print(f"   Account: {result['account_info']['login']}")
                    print(f"   Balance: ${result['account_info']['balance']:,.2f}")
                else:
                    print("❌ Connection failed:")
                    print(f"   Error: {result['error']}")
        else:
            print("❌ MT5 executable not found")
    
    else:
        print("\n✅ MT5 terminal looks healthy, testing direct connection...")
        from mt5_integration.mt5_service import MT5ConnectionManager
        success, result = MT5ConnectionManager.test_connection("211047814", "Johannes@0", "Exness-MT5Trial9")
        
        if success:
            print("✅ Connection successful!")
            print(f"   Account: {result['account_info']['login']}")
            print(f"   Balance: ${result['account_info']['balance']:,.2f}")
        else:
            print("❌ Connection failed:")
            print(f"   Error: {result['error']}")

if __name__ == "__main__":
    reset_mt5_terminal()
