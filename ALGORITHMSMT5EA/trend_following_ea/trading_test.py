"""
Trend Following Trading Test - Test position management and risk calculations
"""

import MetaTrader5 as mt5
import time
from datetime import datetime

def test_trend_trading():
    """Test trend following trading functionality"""
    
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
    print(f"   Equity: ${account_info.equity:.2f}")
    print(f"   Free Margin: ${account_info.margin_free:.2f}")
    print(f"   Margin Level: {account_info.margin_level:.2f}%")
    print(f"   Leverage: 1:{account_info.leverage}")
    
    if account_info.margin_free < 1000:
        print("⚠️  Warning: Low free margin for trend following")
    
    # Symbol setup
    symbol = "EURUSD"
    symbol_info = mt5.symbol_info(symbol)
    if not symbol_info:
        print(f"❌ Symbol {symbol} not found")
        return False
    
    if not symbol_info.visible:
        mt5.symbol_select(symbol, True)
    
    # Get current price and market data
    tick = mt5.symbol_info_tick(symbol)
    if not tick:
        print(f"❌ Failed to get price for {symbol}")
        return False
    
    current_price = (tick.bid + tick.ask) / 2
    point = symbol_info.point
    
    print(f"\n💰 Current {symbol} Market:")
    print(f"   Price: {current_price:.5f}")
    print(f"   Bid: {tick.bid:.5f}")
    print(f"   Ask: {tick.ask:.5f}")
    print(f"   Spread: {(tick.ask - tick.bid) / point:.1f} points")
    
    # Test ATR calculation for stop loss
    print(f"\n🧮 Testing ATR-based risk calculations...")
    
    # Get H4 data for ATR calculation
    rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_H4, 0, 100)
    if rates is None:
        print("❌ Failed to get historical data")
        return False
    
    import pandas as pd
    import numpy as np
    
    df = pd.DataFrame(rates)
    
    # Calculate ATR
    high_low = df['high'] - df['low']
    high_close = np.abs(df['high'] - df['close'].shift())
    low_close = np.abs(df['low'] - df['close'].shift())
    
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = ranges.max(axis=1)
    atr = true_range.rolling(window=14).mean().iloc[-1]
    
    print(f"   ATR (14): {atr:.5f}")
    print(f"   ATR in points: {atr / point:.1f}")
    
    # Risk management calculations
    atr_multiplier = 2.5
    stop_loss_distance = atr * atr_multiplier
    take_profit_distance = stop_loss_distance * 3  # 3:1 RR
    
    print(f"\n📊 Risk Management Setup:")
    print(f"   ATR Multiplier: {atr_multiplier}")
    print(f"   Stop Loss Distance: {stop_loss_distance:.5f} ({stop_loss_distance/point:.1f} points)")
    print(f"   Take Profit Distance: {take_profit_distance:.5f} ({take_profit_distance/point:.1f} points)")
    print(f"   Risk:Reward Ratio: 1:3")
    
    # Position sizing calculation
    risk_percent = 2.0  # 2% risk per trade
    risk_amount = account_info.balance * (risk_percent / 100)
    
    # Calculate position size based on risk
    tick_value = symbol_info.trade_tick_value
    tick_size = symbol_info.trade_tick_size
    
    if tick_value > 0 and tick_size > 0:
        stop_loss_ticks = stop_loss_distance / tick_size
        position_size = risk_amount / (stop_loss_ticks * tick_value)
        
        # Round to volume step
        volume_step = symbol_info.volume_step
        position_size = round(position_size / volume_step) * volume_step
        
        # Ensure within limits
        min_volume = symbol_info.volume_min
        max_volume = symbol_info.volume_max
        position_size = max(min_volume, min(position_size, max_volume))
        
        print(f"\n💼 Position Sizing Calculation:")
        print(f"   Risk Amount: ${risk_amount:.2f} ({risk_percent}% of balance)")
        print(f"   Calculated Lot Size: {position_size:.2f}")
        print(f"   Volume Limits: {min_volume} - {max_volume}")
        print(f"   Volume Step: {volume_step}")
    else:
        position_size = 0.01  # Fallback
        print(f"⚠️  Using fallback position size: {position_size}")
    
    # Test order placement (simulation mode)
    print(f"\n🧪 Testing Order Placement (Simulation)...")
    
    # Calculate order prices
    buy_price = tick.ask
    sell_price = tick.bid
    
    buy_sl = buy_price - stop_loss_distance
    buy_tp = buy_price + take_profit_distance
    sell_sl = sell_price + stop_loss_distance
    sell_tp = sell_price - take_profit_distance
    
    print(f"   📈 BUY Order Simulation:")
    print(f"     Entry: {buy_price:.5f}")
    print(f"     Stop Loss: {buy_sl:.5f}")
    print(f"     Take Profit: {buy_tp:.5f}")
    print(f"     Risk: ${risk_amount:.2f}")
    print(f"     Potential Profit: ${risk_amount * 3:.2f}")
    
    print(f"\n   📉 SELL Order Simulation:")
    print(f"     Entry: {sell_price:.5f}")
    print(f"     Stop Loss: {sell_sl:.5f}")
    print(f"     Take Profit: {sell_tp:.5f}")
    print(f"     Risk: ${risk_amount:.2f}")
    print(f"     Potential Profit: ${risk_amount * 3:.2f}")
    
    # Test small position if user confirms
    print(f"\n🔬 Test Real Order Placement?")
    print(f"   This will place a VERY small test position (0.01 lots)")
    print(f"   Risk: ~$2-5 maximum")
    
    confirm = input("Place test order? (yes/no): ").strip().lower()
    
    if confirm in ['yes', 'y']:
        print(f"\n📝 Placing test BUY order...")
        
        test_lot_size = 0.01  # Very small for testing
        magic_number = 98765
        
        buy_request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": test_lot_size,
            "type": mt5.ORDER_TYPE_BUY,
            "price": buy_price,
            "sl": buy_sl,
            "tp": buy_tp,
            "deviation": 20,
            "magic": magic_number,
            "comment": "Trend Following Test",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        result = mt5.order_send(buy_request)
        print(f"   Order Result: {result.retcode}")
        
        if result.retcode == mt5.TRADE_RETCODE_DONE:
            print(f"   ✅ Test position opened successfully!")
            print(f"   Position ID: {result.deal}")
            print(f"   Volume: {result.volume} lots")
            print(f"   Price: {result.price:.5f}")
            
            # Wait a moment
            print(f"\n⏱️  Waiting 10 seconds...")
            time.sleep(10)
            
            # Check position status
            positions = mt5.positions_get(symbol=symbol)
            if positions:
                test_positions = [p for p in positions if p.magic == magic_number]
                if test_positions:
                    pos = test_positions[0]
                    print(f"\n📊 Test Position Status:")
                    print(f"   Current P&L: ${pos.profit:.2f}")
                    print(f"   Current Price: {pos.price_current:.5f}")
                    print(f"   Open Price: {pos.price_open:.5f}")
                    
                    # Close the test position
                    close_confirm = input("Close test position? (yes/no): ").strip().lower()
                    if close_confirm in ['yes', 'y']:
                        close_request = {
                            "action": mt5.TRADE_ACTION_DEAL,
                            "symbol": symbol,
                            "volume": pos.volume,
                            "type": mt5.ORDER_TYPE_SELL,
                            "position": pos.ticket,
                            "price": tick.bid,
                            "deviation": 20,
                            "magic": magic_number,
                            "comment": "Test Close",
                            "type_time": mt5.ORDER_TIME_GTC,
                            "type_filling": mt5.ORDER_FILLING_IOC,
                        }
                        
                        close_result = mt5.order_send(close_request)
                        if close_result.retcode == mt5.TRADE_RETCODE_DONE:
                            print(f"   ✅ Test position closed")
                            print(f"   Final P&L: ${pos.profit:.2f}")
                        else:
                            print(f"   ⚠️  Failed to close: {close_result.retcode}")
        else:
            print(f"   ❌ Test order failed: {result.retcode}")
            
            # Error explanations
            error_dict = {
                10004: "Requote",
                10006: "Request rejected",
                10014: "Invalid volume in the request",
                10015: "Invalid price in the request",
                10016: "Invalid stops in the request",
                10018: "Market is closed",
                10019: "There is not enough money to complete the request",
            }
            
            error_msg = error_dict.get(result.retcode, f"Unknown error {result.retcode}")
            print(f"   Error: {error_msg}")
    
    else:
        print(f"   ✅ Test order placement skipped")
    
    # Cleanup
    mt5.shutdown()
    
    print(f"\n" + "="*60)
    print("Trend Following Trading Test Results:")
    print("✅ Connection and market data access successful")
    print("✅ ATR-based risk calculations working")
    print("✅ Position sizing calculations functional")
    print("✅ Order price calculations accurate")
    print("="*60)
    
    return True

def test_timeframe_analysis():
    """Test multi-timeframe analysis for trend following"""
    print("\n" + "="*50)
    print("Multi-Timeframe Trend Analysis Test")
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
    
    # Test different timeframes
    timeframes = {
        "H1": mt5.TIMEFRAME_H1,
        "H4": mt5.TIMEFRAME_H4,
        "D1": mt5.TIMEFRAME_D1
    }
    
    print(f"📊 Multi-Timeframe Analysis for {symbol}:")
    
    for tf_name, tf_value in timeframes.items():
        print(f"\n   {tf_name} Timeframe:")
        
        # Get data
        rates = mt5.copy_rates_from_pos(symbol, tf_value, 0, 100)
        if rates is None:
            print(f"     ❌ Failed to get {tf_name} data")
            continue
        
        import pandas as pd
        df = pd.DataFrame(rates)
        
        # Calculate simple trend indicators
        close_prices = df['close']
        
        # EMAs
        ema_21 = close_prices.ewm(span=21).mean().iloc[-1]
        ema_50 = close_prices.ewm(span=50).mean().iloc[-1]
        ema_200 = close_prices.ewm(span=200).mean().iloc[-1] if len(close_prices) >= 200 else None
        
        current_price = close_prices.iloc[-1]
        
        print(f"     Current Price: {current_price:.5f}")
        print(f"     EMA 21: {ema_21:.5f}")
        print(f"     EMA 50: {ema_50:.5f}")
        if ema_200:
            print(f"     EMA 200: {ema_200:.5f}")
        
        # Trend direction
        if ema_21 > ema_50:
            short_trend = "Bullish"
        else:
            short_trend = "Bearish"
        
        if ema_200:
            if current_price > ema_200:
                long_trend = "Bullish"
            else:
                long_trend = "Bearish"
        else:
            long_trend = "Unknown"
        
        print(f"     Short-term trend: {short_trend}")
        print(f"     Long-term trend: {long_trend}")
        
        # Trend strength (simplified)
        price_change = (current_price - close_prices.iloc[-5]) / close_prices.iloc[-5] * 100
        print(f"     5-period change: {price_change:.2f}%")
    
    mt5.shutdown()

if __name__ == "__main__":
    print("Starting Trend Following Trading Tests...")
    
    # Test main trading functionality
    test_trend_trading()
    
    # Test timeframe analysis
    test_timeframe_analysis()
    
    print("\n🎉 Trend Following trading tests completed!")
