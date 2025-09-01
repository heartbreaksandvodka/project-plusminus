#!/usr/bin/env python3
"""
MT5 Connection Test Script for Exness Demo Account
This script will help diagnose MT5 connection issues
"""

import MetaTrader5 as mt5
import sys
import os

def test_mt5_connection():
    """Test MT5 connection with detailed error reporting"""
    
    # Your Exness demo account details
    account_number = 211047814
    password = "Johannes@0"
    server = "Exness-MT5Trial9"
    
    print("=== MT5 Connection Test for Exness Demo Account ===")
    print(f"Account: {account_number}")
    print(f"Server: {server}")
    print(f"Password: {'*' * len(password)}")
    print()
    
    # Step 1: Check MT5 installation
    print("Step 1: Checking MT5 installation...")
    try:
        print(f"MT5 module version: {mt5.__version__ if hasattr(mt5, '__version__') else 'Unknown'}")
        print(f"MT5 module path: {mt5.__file__}")
    except Exception as e:
        print(f"Error checking MT5 module: {e}")
    print()
    
    # Step 2: Initialize MT5
    print("Step 2: Initializing MT5...")
    if not mt5.initialize():
        error = mt5.last_error()
        print(f"❌ MT5 initialization failed!")
        print(f"Error code: {error[0] if error else 'Unknown'}")
        print(f"Error message: {error[1] if error else 'Unknown'}")
        return False
    else:
        print("✅ MT5 initialized successfully")
    print()
    
    # Step 3: Get terminal info
    print("Step 3: Getting terminal information...")
    try:
        terminal_info = mt5.terminal_info()
        if terminal_info:
            print(f"Terminal path: {terminal_info.path}")
            print(f"Terminal name: {terminal_info.name}")
            print(f"Terminal build: {terminal_info.build}")
            print(f"Terminal connected: {terminal_info.connected}")
            print(f"DLLs allowed: {terminal_info.dlls_allowed}")
            print(f"Trade allowed: {terminal_info.trade_allowed}")
            print(f"Expert advisors enabled: {terminal_info.expert_advisors_enabled}")
        else:
            print("❌ Could not get terminal info")
    except Exception as e:
        print(f"Error getting terminal info: {e}")
    print()
    
    # Step 4: Test login
    print("Step 4: Testing login...")
    try:
        authorized = mt5.login(
            login=account_number,
            password=password,
            server=server
        )
        
        if not authorized:
            error = mt5.last_error()
            print(f"❌ Login failed!")
            print(f"Error code: {error[0] if error else 'Unknown'}")
            print(f"Error message: {error[1] if error else 'Unknown'}")
            
            # Common error codes for Exness
            if error and error[0] == -6:
                print("\n🔍 Error Analysis for Exness:")
                print("- Error -6 usually means 'Authorization failed'")
                print("- Check if account number is correct (no extra characters)")
                print("- Verify password (case-sensitive)")
                print("- Ensure server name is exactly 'Exness-MT5Trial9'")
                print("- Make sure account allows API trading")
                print("- Try logging in manually to MT5 first")
                
            return False
        else:
            print("✅ Login successful!")
            
    except Exception as e:
        print(f"❌ Login exception: {e}")
        return False
    
    # Step 5: Get account info
    print("\nStep 5: Getting account information...")
    try:
        account_info = mt5.account_info()
        if account_info:
            print(f"Account login: {account_info.login}")
            print(f"Account server: {account_info.server}")
            print(f"Account name: {account_info.name}")
            print(f"Account company: {account_info.company}")
            print(f"Account currency: {account_info.currency}")
            print(f"Account balance: {account_info.balance}")
            print(f"Account equity: {account_info.equity}")
            print(f"Account margin: {account_info.margin}")
            print(f"Trade mode: {account_info.trade_mode}")
            print(f"Trade allowed: {account_info.trade_allowed}")
            print(f"Trade expert: {account_info.trade_expert}")
        else:
            print("❌ Could not get account info")
            error = mt5.last_error()
            print(f"Error: {error}")
    except Exception as e:
        print(f"Error getting account info: {e}")
    
    # Step 6: Test market data
    print("\nStep 6: Testing market data access...")
    try:
        symbols = mt5.symbols_get()
        if symbols:
            print(f"✅ Found {len(symbols)} symbols")
            print(f"First few symbols: {[s.name for s in symbols[:5]]}")
        else:
            print("❌ Could not get symbols")
    except Exception as e:
        print(f"Error getting symbols: {e}")
    
    # Cleanup
    print("\nStep 7: Cleanup...")
    mt5.shutdown()
    print("✅ MT5 connection test completed")
    
    return True

if __name__ == "__main__":
    print("Starting MT5 connection diagnostic...")
    print("Make sure MetaTrader 5 is installed and you can log in manually first.\n")
    
    success = test_mt5_connection()
    
    if not success:
        print("\n❌ Connection test failed. Please check the error messages above.")
        print("\n💡 Troubleshooting tips for Exness:")
        print("1. Open MetaTrader 5 manually and log in with the same credentials")
        print("2. Go to Tools → Options → Expert Advisors")
        print("3. Enable 'Allow algorithmic trading'")
        print("4. Enable 'Allow DLL imports'")
        print("5. Make sure the account allows API access")
        print("6. Check if there are any account restrictions")
        sys.exit(1)
    else:
        print("\n✅ Connection test successful!")
