#!/usr/bin/env python
"""
Test dynamic MT5 credentials system
"""

import sys
import os

# Add the current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_dynamic_credentials():
    print("🧪 Testing Dynamic MT5 Credentials System")
    print("=" * 50)
    
    try:
        from dynamic_credentials import get_mt5_credentials_from_db, initialize_mt5_dynamic
        
        print("✅ Dynamic credentials module imported successfully")
        
        # Test getting credentials
        creds = get_mt5_credentials_from_db()
        print(f"✅ Retrieved credentials for account: {creds['login']}")
        print(f"   Server: {creds['server']}")
        print(f"   Broker: {creds['broker_name']}")
        print(f"   Database ID: {creds['account_id']}")
        
        # Test initialization
        print("\n🔌 Testing MT5 initialization...")
        success = initialize_mt5_dynamic()
        
        if success:
            print("✅ MT5 initialization successful!")
            
            # Quick test to verify we're connected
            import MetaTrader5 as mt5
            account_info = mt5.account_info()
            if account_info:
                print(f"✅ Connected to account: {account_info.login}")
                print(f"   Balance: ${account_info.balance:,.2f}")
                print(f"   Company: {account_info.company}")
            mt5.shutdown()
        else:
            print("❌ MT5 initialization failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    test_dynamic_credentials()
