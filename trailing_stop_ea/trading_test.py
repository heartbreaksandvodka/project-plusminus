"""
Simple EA Test - Check if trades can be placed
"""

import MetaTrader5 as mt5
import time

def test_trading():
    """Test if we can actually place trades"""
    
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
    
    # Check account and terminal info
    account_info = mt5.account_info()
    terminal_info = mt5.terminal_info()
    
    print(f"\n📊 Account Status:")
    print(f"   Balance: ${account_info.balance}")
    print(f"   Equity: ${account_info.equity}")
    print(f"   Free Margin: ${account_info.margin_free}")
    print(f"   Trade Allowed: {account_info.trade_allowed}")
    print(f"   Expert Allowed: {account_info.trade_expert}")
    
    print(f"\n🖥️ Terminal Status:")
    print(f"   Trade Allowed: {terminal_info.trade_allowed}")
    print(f"   Connected: {terminal_info.connected}")
    print(f"   DLLs Allowed: {terminal_info.dlls_allowed}")
    
    # Check symbol
    symbol = "EURUSD"
    symbol_info = mt5.symbol_info(symbol)
    if not symbol_info:
        print(f"❌ Symbol {symbol} not found")
        return False
    
    if not symbol_info.visible:
        print(f"🔄 Making {symbol} visible...")
        if not mt5.symbol_select(symbol, True):
            print(f"❌ Failed to select {symbol}")
            return False
    
    # Get current price
    tick = mt5.symbol_info_tick(symbol)
    if not tick:
        print(f"❌ Failed to get price for {symbol}")
        return False
    
    print(f"\n💰 Current {symbol} Prices:")
    print(f"   Bid: {tick.bid}")
    print(f"   Ask: {tick.ask}")
    print(f"   Spread: {(tick.ask - tick.bid) / symbol_info.point} points")
    
    # Try to place a very small test order
    print(f"\n🧪 Testing order placement...")
    
    lot_size = 0.01  # Very small size for testing
    point = symbol_info.point
    price = tick.ask
    sl = price - (50 * point)  # 50 point stop loss
    tp = price + (100 * point)  # 100 point take profit
    
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot_size,
        "type": mt5.ORDER_TYPE_BUY,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": 20,
        "magic": 123456,
        "comment": "EA Test Order",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    
    print(f"📋 Order Request:")
    print(f"   Symbol: {symbol}")
    print(f"   Volume: {lot_size}")
    print(f"   Type: BUY")
    print(f"   Price: {price}")
    print(f"   Stop Loss: {sl}")
    print(f"   Take Profit: {tp}")
    
    result = mt5.order_send(request)
    print(f"\n📤 Order Result:")
    print(f"   Return Code: {result.retcode}")
    print(f"   Deal: {result.deal}")
    print(f"   Order: {result.order}")
    print(f"   Volume: {result.volume}")
    print(f"   Price: {result.price}")
    print(f"   Comment: {result.comment}")
    
    if result.retcode == mt5.TRADE_RETCODE_DONE:
        print("✅ TEST ORDER PLACED SUCCESSFULLY!")
        
        # Wait a moment then close the position
        time.sleep(2)
        
        # Get the position to close it
        positions = mt5.positions_get(symbol=symbol)
        if positions:
            position = positions[-1]  # Get the last position
            
            close_request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": position.volume,
                "type": mt5.ORDER_TYPE_SELL if position.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY,
                "position": position.ticket,
                "price": tick.bid if position.type == mt5.ORDER_TYPE_BUY else tick.ask,
                "deviation": 20,
                "magic": 123456,
                "comment": "EA Test Close",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            close_result = mt5.order_send(close_request)
            if close_result.retcode == mt5.TRADE_RETCODE_DONE:
                print("✅ Test position closed successfully!")
            else:
                print(f"⚠️ Failed to close test position: {close_result.retcode}")
        
        return True
    else:
        print(f"❌ ORDER FAILED!")
        
        # Print detailed error information
        error_dict = {
            10004: "Requote",
            10006: "Request rejected",
            10007: "Request canceled by trader", 
            10008: "Order placed",
            10009: "Request completed",
            10010: "Only part of the request was completed",
            10011: "Request processing error",
            10012: "Request canceled by timeout",
            10013: "Invalid request",
            10014: "Invalid volume in the request",
            10015: "Invalid price in the request",
            10016: "Invalid stops in the request",
            10017: "Trade is disabled",
            10018: "Market is closed",
            10019: "There is not enough money to complete the request",
            10020: "Prices changed",
            10021: "There are no quotes to process the request",
            10022: "Invalid order expiration date in the request",
            10023: "Order state changed",
            10024: "Too frequent requests",
            10025: "No changes in request",
            10026: "Autotrading disabled by server",
            10027: "Autotrading disabled by client terminal",
            10028: "Request locked for processing",
            10029: "Order or position frozen",
            10030: "Invalid order filling type",
            10031: "No connection with the trade server"
        }
        
        error_msg = error_dict.get(result.retcode, f"Unknown error {result.retcode}")
        print(f"   Error: {error_msg}")
        
        return False
    
    # Cleanup
    mt5.shutdown()

if __name__ == "__main__":
    test_trading()
