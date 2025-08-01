"""
Grid Trading Test - Test actual order placement functionality
"""

import MetaTrader5 as mt5
import time
from datetime import datetime

def test_grid_orders():
    """Test placing and managing grid orders"""
    
    # Initialize MT5
    if not mt5.initialize():
        print("❌ MT5 initialization failed")
        return False
    
    # Login
    login = 210715557
    password = "Johannes@0"
    server = "Exness-MT5Trial9"
    
    print(f"🔐 Logging in to account {login}...")
    if not mt5.login(login, password=password, server=server):
        print("❌ Login failed:", mt5.last_error())
        return False
    
    print("✅ Login successful!")
    
    # Check account status
    account_info = mt5.account_info()
    print(f"\n📊 Account Status:")
    print(f"   Balance: ${account_info.balance:.2f}")
    print(f"   Free Margin: ${account_info.margin_free:.2f}")
    print(f"   Margin Level: {account_info.margin_level:.2f}%")
    
    if account_info.margin_free < 500:
        print("⚠️  Warning: Low free margin for grid trading")
    
    # Symbol setup
    symbol = "EURUSD"
    symbol_info = mt5.symbol_info(symbol)
    if not symbol_info:
        print(f"❌ Symbol {symbol} not found")
        return False
    
    if not symbol_info.visible:
        mt5.symbol_select(symbol, True)
    
    # Get current price
    tick = mt5.symbol_info_tick(symbol)
    if not tick:
        print(f"❌ Failed to get price for {symbol}")
        return False
    
    current_price = (tick.bid + tick.ask) / 2
    point = symbol_info.point
    
    print(f"\n💰 Current {symbol} Price: {current_price:.5f}")
    print(f"   Spread: {(tick.ask - tick.bid) / point:.1f} points")
    
    # Grid parameters for testing
    lot_size = 0.01  # Very small for testing
    grid_distance = 100  # Larger distance for testing
    magic_number = 54321
    
    print(f"\n🔧 Grid Test Parameters:")
    print(f"   Lot Size: {lot_size}")
    print(f"   Grid Distance: {grid_distance} points")
    print(f"   Magic Number: {magic_number}")
    
    # Calculate test grid levels (only 2 levels each way)
    buy_price = current_price - (grid_distance * point)
    sell_price = current_price + (grid_distance * point)
    
    print(f"\n📋 Test Grid Levels:")
    print(f"   Buy Level: {buy_price:.5f} ({grid_distance} points below)")
    print(f"   Sell Level: {sell_price:.5f} ({grid_distance} points above)")
    
    # Test placing buy limit order
    print(f"\n🧪 Testing BUY LIMIT order...")
    buy_tp = buy_price + (grid_distance * point)
    
    buy_request = {
        "action": mt5.TRADE_ACTION_PENDING,
        "symbol": symbol,
        "volume": lot_size,
        "type": mt5.ORDER_TYPE_BUY_LIMIT,
        "price": buy_price,
        "tp": buy_tp,
        "magic": magic_number,
        "comment": "Grid Test - Buy Limit",
        "type_time": mt5.ORDER_TIME_GTC,
    }
    
    buy_result = mt5.order_send(buy_request)
    print(f"   Buy Order Result: {buy_result.retcode}")
    
    if buy_result.retcode == mt5.TRADE_RETCODE_DONE:
        print(f"   ✅ Buy limit order placed: {buy_result.order}")
        buy_order_id = buy_result.order
    else:
        print(f"   ❌ Buy order failed: {buy_result.comment}")
        buy_order_id = None
    
    # Test placing sell limit order
    print(f"\n🧪 Testing SELL LIMIT order...")
    sell_tp = sell_price - (grid_distance * point)
    
    sell_request = {
        "action": mt5.TRADE_ACTION_PENDING,
        "symbol": symbol,
        "volume": lot_size,
        "type": mt5.ORDER_TYPE_SELL_LIMIT,
        "price": sell_price,
        "tp": sell_tp,
        "magic": magic_number,
        "comment": "Grid Test - Sell Limit",
        "type_time": mt5.ORDER_TIME_GTC,
    }
    
    sell_result = mt5.order_send(sell_request)
    print(f"   Sell Order Result: {sell_result.retcode}")
    
    if sell_result.retcode == mt5.TRADE_RETCODE_DONE:
        print(f"   ✅ Sell limit order placed: {sell_result.order}")
        sell_order_id = sell_result.order
    else:
        print(f"   ❌ Sell order failed: {sell_result.comment}")
        sell_order_id = None
    
    # Check placed orders
    print(f"\n📊 Checking placed orders...")
    orders = mt5.orders_get(symbol=symbol)
    
    if orders:
        grid_orders = [o for o in orders if o.magic == magic_number]
        print(f"   Found {len(grid_orders)} grid test orders:")
        
        for order in grid_orders:
            order_type = "BUY LIMIT" if order.type == mt5.ORDER_TYPE_BUY_LIMIT else "SELL LIMIT"
            print(f"     - {order_type} {order.volume} lots at {order.price_open:.5f}")
            if order.tp > 0:
                print(f"       TP: {order.tp:.5f}")
    else:
        print("   No orders found")
    
    # Wait a moment
    print(f"\n⏱️  Waiting 10 seconds before cleanup...")
    time.sleep(10)
    
    # Clean up test orders
    print(f"\n🧹 Cleaning up test orders...")
    cleanup_orders = [buy_order_id, sell_order_id]
    
    for order_id in cleanup_orders:
        if order_id:
            cancel_request = {
                "action": mt5.TRADE_ACTION_REMOVE,
                "order": order_id,
            }
            
            cancel_result = mt5.order_send(cancel_request)
            if cancel_result.retcode == mt5.TRADE_RETCODE_DONE:
                print(f"   ✅ Order {order_id} cancelled")
            else:
                print(f"   ⚠️  Failed to cancel order {order_id}: {cancel_result.retcode}")
    
    # Final verification
    print(f"\n🔍 Final verification...")
    final_orders = mt5.orders_get(symbol=symbol)
    if final_orders:
        remaining_grid_orders = [o for o in final_orders if o.magic == magic_number]
        if remaining_grid_orders:
            print(f"   ⚠️  {len(remaining_grid_orders)} test orders still active")
        else:
            print(f"   ✅ All test orders cleaned up successfully")
    else:
        print(f"   ✅ No orders remaining")
    
    # Cleanup
    mt5.shutdown()
    
    print(f"\n" + "="*50)
    print("Grid Trading Order Test Results:")
    print("✅ Connection and login successful" if buy_result.retcode == mt5.TRADE_RETCODE_DONE or sell_result.retcode == mt5.TRADE_RETCODE_DONE else "❌ Order placement failed")
    print("✅ Pending orders can be placed" if buy_order_id or sell_order_id else "❌ Pending order placement failed")
    print("✅ Orders can be cancelled" if not remaining_grid_orders else "⚠️  Order cancellation may have issues")
    print("="*50)
    
    return True

def test_grid_risk_management():
    """Test risk management calculations for grid trading"""
    print("\n" + "="*50)
    print("Grid Trading Risk Management Test")
    print("="*50)
    
    # Initialize MT5
    if not mt5.initialize():
        print("❌ MT5 initialization failed")
        return
    
    # Login
    login = 210715557
    password = "Johannes@0"
    server = "Exness-MT5Trial9"
    
    if not mt5.login(login, password=password, server=server):
        print("❌ Login failed")
        return
    
    symbol = "EURUSD"
    symbol_info = mt5.symbol_info(symbol)
    account_info = mt5.account_info()
    
    if not (symbol_info and account_info):
        print("❌ Failed to get symbol or account info")
        return
    
    # Risk calculations
    print(f"📊 Risk Management Analysis:")
    print(f"   Account Balance: ${account_info.balance:.2f}")
    print(f"   Free Margin: ${account_info.margin_free:.2f}")
    print(f"   Leverage: 1:{account_info.leverage}")
    
    # Grid scenarios
    scenarios = [
        {"levels": 5, "lot_size": 0.01, "distance": 50},
        {"levels": 10, "lot_size": 0.01, "distance": 50},
        {"levels": 5, "lot_size": 0.1, "distance": 100},
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        levels = scenario["levels"]
        lot_size = scenario["lot_size"]
        distance = scenario["distance"]
        
        total_lots = levels * 2 * lot_size  # Buy and sell sides
        margin_per_lot = symbol_info.margin_initial
        total_margin = total_lots * margin_per_lot
        margin_usage = (total_margin / account_info.margin_free) * 100
        
        print(f"\n   Scenario {i}: {levels} levels, {lot_size} lots, {distance} points")
        print(f"     Total lots exposure: {total_lots}")
        print(f"     Margin requirement: ${total_margin:.2f}")
        print(f"     Margin usage: {margin_usage:.1f}%")
        
        if margin_usage < 30:
            print(f"     ✅ Safe margin usage")
        elif margin_usage < 50:
            print(f"     ⚠️  Moderate margin usage")
        else:
            print(f"     ❌ High margin usage - risky!")
    
    mt5.shutdown()

if __name__ == "__main__":
    print("Starting Grid Trading Tests...")
    
    # Test order placement
    test_grid_orders()
    
    # Test risk management
    test_grid_risk_management()
    
    print("\n🎉 Grid Trading tests completed!")
