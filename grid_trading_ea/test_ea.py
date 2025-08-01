"""
Test script for MetaTrader 5 Grid Trading Expert Advisor
This script tests the connection and basic functionality
"""

from mt5_grid_trading_ea import GridTradingEA, test_connection
import MetaTrader5 as mt5
from datetime import datetime

def run_tests():
    """Run basic tests for the Grid Trading EA"""
    print("=" * 60)
    print("  MetaTrader 5 Grid Trading EA Test Suite")
    print("=" * 60)
    
    # Test 1: Basic connection
    print("\n1. Testing MT5 connection...")
    test_connection()
    
    # Test 2: Initialize EA
    print("\n2. Testing Grid EA initialization...")
    ea = GridTradingEA(
        symbol="EURUSD", 
        lot_size=0.01,  # Very small lot size for testing
        grid_distance=50,
        max_levels=3,  # Fewer levels for testing
        login=210715557,
        password="Johannes@0",
        server="Exness-MT5Trial9"
    )
    
    if ea.initialize_mt5():
        print("✅ Grid EA initialized successfully")
        
        # Test 3: Symbol info
        print("\n3. Testing symbol information...")
        symbol_info = ea.get_symbol_info()
        if symbol_info:
            print(f"✅ Symbol info retrieved: {ea.symbol}")
            print(f"   - Point: {symbol_info.point}")
            print(f"   - Digits: {symbol_info.digits}")
            print(f"   - Spread: {symbol_info.spread}")
            print(f"   - Min Volume: {symbol_info.volume_min}")
            print(f"   - Max Volume: {symbol_info.volume_max}")
        
        # Test 4: Current prices
        print("\n4. Testing price feed...")
        bid, ask = ea.get_current_price()
        if bid and ask:
            print(f"✅ Current prices - Bid: {bid}, Ask: {ask}")
            print(f"   - Spread: {ask - bid:.5f}")
            print(f"   - Mid Price: {(bid + ask) / 2:.5f}")
        
        # Test 5: Grid level calculation
        print("\n5. Testing grid level calculation...")
        if symbol_info and bid and ask:
            current_price = (bid + ask) / 2
            point = symbol_info.point
            buy_levels, sell_levels = ea.calculate_grid_levels(current_price, point)
            
            print(f"✅ Grid levels calculated around {current_price:.5f}")
            print(f"   - Buy levels (below): {buy_levels}")
            print(f"   - Sell levels (above): {sell_levels}")
            print(f"   - Grid distance: {ea.grid_distance} points")
        
        # Test 6: Check existing orders and positions
        print("\n6. Testing order and position queries...")
        existing_orders = ea.get_existing_orders()
        existing_positions = ea.get_existing_positions()
        
        print(f"✅ Existing orders: {len(existing_orders)}")
        print(f"✅ Existing positions: {len(existing_positions)}")
        
        if existing_orders:
            print("   Current orders:")
            for order in existing_orders[:3]:  # Show first 3
                print(f"     - {order.type} at {order.price_open} (Ticket: {order.ticket})")
        
        if existing_positions:
            print("   Current positions:")
            for pos in existing_positions[:3]:  # Show first 3
                print(f"     - {pos.type} {pos.volume} lots, P&L: ${pos.profit:.2f}")
        
        # Test 7: Account info for grid trading
        print("\n7. Testing account suitability for grid trading...")
        account_info = mt5.account_info()
        if account_info:
            print(f"✅ Account info retrieved:")
            print(f"   - Balance: ${account_info.balance:.2f}")
            print(f"   - Equity: ${account_info.equity:.2f}")
            print(f"   - Free Margin: ${account_info.margin_free:.2f}")
            print(f"   - Margin Level: {account_info.margin_level:.2f}%")
            print(f"   - Trade Allowed: {account_info.trade_allowed}")
            
            # Check if account is suitable for grid trading
            if account_info.margin_free > 1000:
                print("   ✅ Sufficient free margin for grid trading")
            else:
                print("   ⚠️  Low free margin - use smaller lot sizes")
        
        # Test 8: Spread check
        print("\n8. Testing spread conditions...")
        if symbol_info:
            current_spread = symbol_info.spread
            print(f"✅ Current spread: {current_spread} points")
            
            if current_spread <= 5:
                print("   ✅ Good spread for grid trading")
            elif current_spread <= 10:
                print("   ⚠️  Moderate spread - adjust grid distance")
            else:
                print("   ❌ High spread - not recommended for grid trading")
        
        # Test 9: Market hours check
        print("\n9. Testing market conditions...")
        tick = mt5.symbol_info_tick(ea.symbol)
        if tick:
            print(f"✅ Market is active (last tick: {tick.time})")
            print(f"   - Volume: {tick.volume}")
            print(f"   - Time: {datetime.fromtimestamp(tick.time)}")
        else:
            print("❌ Market appears to be closed or inactive")
        
        # Cleanup
        ea.stop()
        print("\n✅ All Grid Trading EA tests completed!")
        
    else:
        print("❌ Failed to initialize Grid EA")
    
    print("\n" + "=" * 60)
    print("Grid Trading EA Test Summary:")
    print("- Make sure MetaTrader 5 is running")
    print("- Verify algorithmic trading is enabled")
    print("- Check your internet connection")
    print("- Ensure sufficient free margin (>$1000 recommended)")
    print("- Monitor spread conditions before live trading")
    print("- Start with small lot sizes (0.01) for testing")
    print("=" * 60)

def test_grid_simulation():
    """Simulate grid behavior without placing actual orders"""
    print("\n" + "=" * 50)
    print("  Grid Trading Simulation")
    print("=" * 50)
    
    # Create EA instance
    ea = GridTradingEA(
        symbol="EURUSD",
        lot_size=0.01,
        grid_distance=50,
        max_levels=5
    )
    
    if not ea.initialize_mt5():
        print("❌ Failed to initialize MT5")
        return
    
    # Get current price
    bid, ask = ea.get_current_price()
    symbol_info = ea.get_symbol_info()
    
    if not (bid and ask and symbol_info):
        print("❌ Failed to get market data")
        return
    
    current_price = (bid + ask) / 2
    point = symbol_info.point
    
    print(f"📊 Simulating grid around price: {current_price:.5f}")
    print(f"   Grid distance: {ea.grid_distance} points")
    print(f"   Max levels: {ea.max_levels}")
    print(f"   Lot size per level: {ea.lot_size}")
    
    # Calculate and display grid
    buy_levels, sell_levels = ea.calculate_grid_levels(current_price, point)
    
    print(f"\n📈 BUY LEVELS (below current price):")
    for i, price in enumerate(buy_levels, 1):
        tp = price + (ea.grid_distance * point)
        distance = (current_price - price) / point
        print(f"   Level {i}: Buy at {price:.5f} (TP: {tp:.5f}) - {distance:.0f} points below")
    
    print(f"\n📉 SELL LEVELS (above current price):")
    for i, price in enumerate(sell_levels, 1):
        tp = price - (ea.grid_distance * point)
        distance = (price - current_price) / point
        print(f"   Level {i}: Sell at {price:.5f} (TP: {tp:.5f}) - {distance:.0f} points above")
    
    # Calculate potential exposure
    total_lots = len(buy_levels + sell_levels) * ea.lot_size
    print(f"\n💰 Potential Exposure:")
    print(f"   Total grid levels: {len(buy_levels + sell_levels)}")
    print(f"   Max lot exposure: {total_lots} lots")
    print(f"   Estimated margin per lot: ${symbol_info.margin_initial:.2f}")
    print(f"   Total margin requirement: ${total_lots * symbol_info.margin_initial:.2f}")
    
    ea.stop()

if __name__ == "__main__":
    # Run main tests
    run_tests()
    
    # Run simulation
    print("\n" + "="*20 + " SIMULATION " + "="*20)
    test_grid_simulation()
