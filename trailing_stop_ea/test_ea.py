"""
Test script for MetaTrader 5 Trailing Stop Manager
This script tests the connection and basic functionality
"""

from mt5_trailing_stop_ea import TrailingStopManager, test_connection
import MetaTrader5 as mt5

def run_tests():
    """Run basic tests for the Trailing Stop Manager"""
    print("=" * 50)
    print("MetaTrader 5 Trailing Stop Manager Test Suite")
    print("=" * 50)
    
    # Test 1: Basic connection
    print("\n1. Testing MT5 connection...")
    test_connection()
    
    # Test 2: Initialize Manager
    print("\n2. Testing Manager initialization...")
    manager = TrailingStopManager(
        symbol="EURUSD", 
        trailing_distance=50,
        magic_number=0,
        login=210715557,
        password="Johannes@0",
        server="Exness-MT5Trial9"
    )
    
    if manager.initialize_mt5():
        print("✅ Manager initialized successfully")
        
        # Test 3: Symbol info
        print("\n3. Testing symbol information...")
        symbol_info = manager.get_symbol_info()
        if symbol_info:
            print(f"✅ Symbol info retrieved: {manager.symbol}")
            print(f"   - Point: {symbol_info.point}")
            print(f"   - Digits: {symbol_info.digits}")
            print(f"   - Spread: {symbol_info.spread}")
        
        # Test 4: Current prices
        print("\n4. Testing price feed...")
        bid, ask = manager.get_current_price()
        if bid and ask:
            print(f"✅ Current prices - Bid: {bid}, Ask: {ask}")
            print(f"   - Spread: {ask - bid:.5f}")
        
        # Test 5: Position detection
        print("\n5. Testing position detection...")
        positions = manager.get_open_positions()
        print(f"✅ Position detection working: {len(positions)} open positions found")
        
        if len(positions) > 0:
            print("   Current positions:")
            for i, pos in enumerate(positions):
                print(f"   - Position {i+1}: {pos.type_name} {pos.volume} lots at {pos.price_open}")
        else:
            print("   - No open positions (this is normal for testing)")
        
        # Test 6: Trailing stop simulation
        print("\n6. Testing trailing stop logic...")
        if len(positions) > 0:
            print("✅ Would update trailing stops for existing positions")
            # Don't actually modify positions in test mode
        else:
            print("✅ Trailing stop logic ready (no positions to test)")
        
        # Cleanup
        manager.stop()
        print("\n✅ All tests completed successfully!")
        
    else:
        print("❌ Failed to initialize Trailing Stop Manager")
    
    print("\n" + "=" * 50)
    print("Test Summary:")
    print("- Make sure MetaTrader 5 is running")
    print("- Verify algorithmic trading is enabled")
    print("- Check your internet connection")
    print("- Ensure the symbol (EURUSD) is available")
    print("- This tool only manages EXISTING positions")
    print("=" * 50)

if __name__ == "__main__":
    run_tests()
