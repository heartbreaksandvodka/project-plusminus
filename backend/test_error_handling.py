#!/usr/bin/env python
"""
Test MT5 automation with intentionally wrong credentials to verify error handling
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

from mt5_integration.mt5_auto_manager import MT5SmartConnection
from mt5_integration.mt5_service import MT5ConnectionManager


def test_wrong_credentials():
    """Test error handling with wrong credentials"""
    
    print("🚫 TESTING ERROR HANDLING WITH WRONG CREDENTIALS")
    print("=" * 50)
    
    # Test with wrong password
    print("\n📋 Test 1: Wrong Password")
    print("-" * 30)
    success, result = MT5SmartConnection.connect("211047814", "WrongPassword123", "Exness-MT5Trial9")
    
    if not success:
        print("✅ Correctly failed with wrong password")
        print(f"   Error: {result['error']}")
        if 'details' in result:
            print(f"   Details: {result['details']}")
    else:
        print("❌ Should have failed with wrong password!")
    
    # Test with wrong account
    print("\n📋 Test 2: Wrong Account Number")
    print("-" * 30)
    success, result = MT5SmartConnection.connect("999999999", "Johannes@0", "Exness-MT5Trial9")
    
    if not success:
        print("✅ Correctly failed with wrong account")
        print(f"   Error: {result['error']}")
        if 'details' in result:
            print(f"   Details: {result['details']}")
    else:
        print("❌ Should have failed with wrong account!")
    
    # Test with wrong server
    print("\n📋 Test 3: Wrong Server")
    print("-" * 30)
    success, result = MT5SmartConnection.connect("211047814", "Johannes@0", "WrongServer-MT5")
    
    if not success:
        print("✅ Correctly failed with wrong server")
        print(f"   Error: {result['error']}")
        if 'details' in result:
            print(f"   Details: {result['details']}")
    else:
        print("❌ Should have failed with wrong server!")
    
    print("\n🏁 ERROR HANDLING TEST COMPLETE")


if __name__ == "__main__":
    try:
        test_wrong_credentials()
    except Exception as e:
        print(f"\n💥 Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
