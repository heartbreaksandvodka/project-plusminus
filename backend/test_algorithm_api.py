#!/usr/bin/env python
"""
Test script for MT5 Algorithm API endpoints
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'authproject.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from mt5_integration.mt5_service import MT5AlgorithmManager
from mt5_integration.models import MT5Account
from authentication.models import User

def test_algorithm_path_resolution():
    """Test algorithm path resolution"""
    print("=== Testing Algorithm Path Resolution ===")
    
    # Test trailing_stop_ea (correct name)
    trailing_stop_path = MT5AlgorithmManager._get_ea_script_path("trailing_stop_ea")
    print(f"trailing_stop_ea path: {trailing_stop_path}")
    print(f"trailing_stop_ea exists: {os.path.isfile(trailing_stop_path)}")
    
    # Test trend_following_ea
    trend_following_path = MT5AlgorithmManager._get_ea_script_path("trend_following_ea")
    print(f"trend_following_ea path: {trend_following_path}")
    print(f"trend_following_ea exists: {os.path.isfile(trend_following_path)}")
    
    # Test with wrong name (mt5_trailing_stop_ea)
    wrong_path = MT5AlgorithmManager._get_ea_script_path("mt5_trailing_stop_ea")
    print(f"mt5_trailing_stop_ea path: {wrong_path}")
    print(f"mt5_trailing_stop_ea exists: {os.path.isfile(wrong_path)}")
    
    print("\n=== Available EAs ===")
    algorithms_dir = MT5AlgorithmManager._get_algorithms_dir()
    print(f"Algorithms directory: {algorithms_dir}")
    
    for item in os.listdir(algorithms_dir):
        item_path = os.path.join(algorithms_dir, item)
        if os.path.isdir(item_path) and not item.startswith('.') and not item.startswith('__'):
            ea_script = os.path.join(item_path, f"mt5_{item}.py")
            print(f"  {item} -> {os.path.isfile(ea_script)}")

def test_start_algorithm():
    """Test starting an algorithm"""
    print("\n=== Testing Start Algorithm ===")
    
    # Create a dummy MT5Account for testing
    try:
        user = User.objects.first()
        if not user:
            print("No users found in database")
            return
            
        mt5_account = MT5Account.objects.filter(user=user).first()
        if not mt5_account:
            print("No MT5 account found")
            return
            
        # Test starting trailing_stop_ea
        result = MT5AlgorithmManager.start_algorithm(mt5_account, "trailing_stop_ea", "EURUSD")
        print(f"Start result: {result}")
        
    except Exception as e:
        print(f"Error testing start algorithm: {e}")

if __name__ == "__main__":
    test_algorithm_path_resolution()
    test_start_algorithm()
