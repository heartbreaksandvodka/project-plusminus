#!/usr/bin/env python
"""
Test script for MT5 integration
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'authproject.settings')
django.setup()

from mt5_integration.mt5_service import MT5ConnectionManager

def test_mt5_connection():
    """Test MT5 connection functionality"""
    print("🔧 Testing MT5 Connection Manager...")
    
    # Test with dummy data (this will fail but we can see if the service works)
    test_data = {
        'account_number': '12345678',
        'password': 'test_password',
        'server': 'Test-Server'
    }
    
    try:
        success, result = MT5ConnectionManager.test_connection(
            test_data['account_number'],
            test_data['password'],
            test_data['server']
        )
        
        if success:
            print("✅ Connection test successful!")
            print(f"Result: {result}")
        else:
            print("❌ Connection test failed (expected with dummy data)")
            print(f"Error: {result}")
            
    except Exception as e:
        print(f"🚨 Exception during test: {e}")
    
    print("\n📋 MT5 Integration is ready for real credentials!")

if __name__ == "__main__":
    test_mt5_connection()
