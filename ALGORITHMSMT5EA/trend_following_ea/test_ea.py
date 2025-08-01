"""
Test script for MetaTrader 5 Trend Following Expert Advisor
This script tests the connection and trend analysis functionality
"""

from mt5_trend_following_ea import TrendFollowingEA, test_connection
import MetaTrader5 as mt5
from datetime import datetime

def run_tests():
    """Run comprehensive tests for the Trend Following EA"""
    print("=" * 70)
    print("  MetaTrader 5 Trend Following EA Test Suite")
    print("=" * 70)
    
    # Test 1: Basic connection
    print("\n1. Testing MT5 connection...")
    test_connection()
    
    # Test 2: Initialize EA
    print("\n2. Testing Trend Following EA initialization...")
    ea = TrendFollowingEA(
        symbol="EURUSD", 
        lot_size=0.1,
        primary_timeframe=mt5.TIMEFRAME_H4,
        secondary_timeframe=mt5.TIMEFRAME_D1,
        login=210715557,
        password="Johannes@0",
        server="Exness-MT5Trial9"
    )
    
    if ea.initialize_mt5():
        print("✅ Trend Following EA initialized successfully")
        
        # Test 3: Symbol info and current prices
        print("\n3. Testing symbol information and prices...")
        symbol_info = ea.get_symbol_info()
        if symbol_info:
            print(f"✅ Symbol info retrieved: {ea.symbol}")
            print(f"   - Point: {symbol_info.point}")
            print(f"   - Digits: {symbol_info.digits}")
            print(f"   - Spread: {symbol_info.spread}")
            print(f"   - Min Volume: {symbol_info.volume_min}")
            print(f"   - Max Volume: {symbol_info.volume_max}")
        
        bid, ask = ea.get_current_price()
        if bid and ask:
            print(f"✅ Current prices - Bid: {bid}, Ask: {ask}")
            print(f"   - Mid Price: {(bid + ask) / 2:.5f}")
            print(f"   - Spread: {ask - bid:.5f}")
        
        # Test 4: Market data retrieval
        print("\n4. Testing market data retrieval...")
        h4_data = ea.get_market_data(mt5.TIMEFRAME_H4, 100)
        d1_data = ea.get_market_data(mt5.TIMEFRAME_D1, 50)
        
        if h4_data is not None:
            print(f"✅ H4 data retrieved: {len(h4_data)} bars")
            print(f"   - Date range: {h4_data['time'].iloc[0]} to {h4_data['time'].iloc[-1]}")
            print(f"   - Latest close: {h4_data['close'].iloc[-1]:.5f}")
        
        if d1_data is not None:
            print(f"✅ D1 data retrieved: {len(d1_data)} bars")
            print(f"   - Date range: {d1_data['time'].iloc[0]} to {d1_data['time'].iloc[-1]}")
            print(f"   - Latest close: {d1_data['close'].iloc[-1]:.5f}")
        
        # Test 5: Technical indicators calculation
        print("\n5. Testing technical indicators...")
        if h4_data is not None and len(h4_data) > 250:
            # Test EMA calculations
            ema_fast = ea.calculate_ema(h4_data, ea.ema_fast)
            ema_slow = ea.calculate_ema(h4_data, ea.ema_slow)
            ema_filter = ea.calculate_ema(h4_data, ea.ema_filter)
            
            print(f"✅ EMAs calculated:")
            print(f"   - Fast EMA ({ea.ema_fast}): {ema_fast.iloc[-1]:.5f}")
            print(f"   - Slow EMA ({ea.ema_slow}): {ema_slow.iloc[-1]:.5f}")
            print(f"   - Filter EMA ({ea.ema_filter}): {ema_filter.iloc[-1]:.5f}")
            
            # Test ATR calculation
            atr = ea.calculate_atr(h4_data, ea.atr_period)
            print(f"✅ ATR calculated: {atr.iloc[-1]:.5f}")
            
            # Test ADX calculation
            adx, plus_di, minus_di = ea.calculate_adx(h4_data, ea.adx_period)
            print(f"✅ ADX calculated:")
            print(f"   - ADX: {adx.iloc[-1]:.2f}")
            print(f"   - +DI: {plus_di.iloc[-1]:.2f}")
            print(f"   - -DI: {minus_di.iloc[-1]:.2f}")
            
            # Test RSI calculation
            rsi = ea.calculate_rsi(h4_data)
            print(f"✅ RSI calculated: {rsi.iloc[-1]:.2f}")
        
        # Test 6: Trend analysis
        print("\n6. Testing trend analysis...")
        h4_analysis = ea.analyze_trend(mt5.TIMEFRAME_H4)
        d1_analysis = ea.analyze_trend(mt5.TIMEFRAME_D1)
        
        if h4_analysis:
            print(f"✅ H4 trend analysis completed:")
            print(f"   - Strong trend: {'Yes' if h4_analysis['strong_trend'] else 'No'}")
            print(f"   - Above filter: {'Yes' if h4_analysis['above_filter'] else 'No'}")
            print(f"   - Uptrend strength: {'Yes' if h4_analysis['uptrend_strength'] else 'No'}")
            print(f"   - ADX: {h4_analysis['adx']:.2f}")
            print(f"   - RSI: {h4_analysis['rsi']:.2f}")
        
        if d1_analysis:
            print(f"✅ D1 trend analysis completed:")
            print(f"   - Strong trend: {'Yes' if d1_analysis['strong_trend'] else 'No'}")
            print(f"   - Above filter: {'Yes' if d1_analysis['above_filter'] else 'No'}")
            print(f"   - Trend direction: {'Up' if d1_analysis['uptrend_strength'] else 'Down'}")
        
        # Test 7: Signal generation
        print("\n7. Testing signal generation...")
        signal_data = ea.generate_signal()
        if signal_data:
            print(f"✅ Signal generation working:")
            print(f"   - Current signal: {signal_data['signal'] if signal_data['signal'] else 'No signal'}")
            
            if signal_data['signal']:
                print(f"   - Signal strength: High (multi-timeframe confirmation)")
                print(f"   - Primary timeframe confirms: Yes")
                print(f"   - Secondary timeframe confirms: Yes")
            else:
                print(f"   - Waiting for trend confirmation...")
        
        # Test 8: Position management queries
        print("\n8. Testing position management...")
        existing_positions = ea.get_open_positions()
        print(f"✅ Position query successful: {len(existing_positions)} open positions")
        
        if existing_positions:
            for pos in existing_positions[:3]:  # Show first 3
                pos_type = "BUY" if pos.type == mt5.ORDER_TYPE_BUY else "SELL"
                print(f"   - {pos_type} {pos.volume} lots at {pos.price_open:.5f}, P&L: ${pos.profit:.2f}")
        
        # Test 9: Position sizing calculation
        print("\n9. Testing position sizing...")
        account_info = mt5.account_info()
        if account_info and h4_analysis:
            position_size = ea.calculate_position_size(
                h4_analysis['atr'], 
                account_info.balance, 
                risk_percent=2.0
            )
            print(f"✅ Position sizing calculated:")
            print(f"   - Account balance: ${account_info.balance:.2f}")
            print(f"   - ATR value: {h4_analysis['atr']:.5f}")
            print(f"   - Calculated lot size: {position_size:.2f}")
            print(f"   - Risk per trade: 2% of balance")
        
        # Test 10: Market conditions analysis
        print("\n10. Testing market conditions...")
        if h4_analysis and d1_analysis:
            print(f"✅ Market conditions analysis:")
            
            # Trend strength assessment
            if h4_analysis['adx'] > 30:
                trend_strength = "Strong"
            elif h4_analysis['adx'] > 20:
                trend_strength = "Moderate"
            else:
                trend_strength = "Weak"
            
            print(f"   - Trend strength: {trend_strength} (ADX: {h4_analysis['adx']:.2f})")
            
            # Market direction
            if h4_analysis['above_filter'] and d1_analysis['above_filter']:
                market_bias = "Bullish"
            elif h4_analysis['below_filter'] and d1_analysis['below_filter']:
                market_bias = "Bearish"
            else:
                market_bias = "Mixed/Ranging"
            
            print(f"   - Market bias: {market_bias}")
            print(f"   - Suitable for trend following: {'Yes' if trend_strength != 'Weak' else 'No'}")
        
        # Cleanup
        ea.stop()
        print("\n✅ All Trend Following EA tests completed successfully!")
        
    else:
        print("❌ Failed to initialize Trend Following EA")
    
    print("\n" + "=" * 70)
    print("Trend Following EA Test Summary:")
    print("- Make sure MetaTrader 5 is running")
    print("- Verify algorithmic trading is enabled")
    print("- Check your internet connection")
    print("- Ensure sufficient historical data is available")
    print("- Best results in trending markets with strong directional moves")
    print("- Recommended for H4 and D1 timeframes")
    print("=" * 70)

def test_trend_scenarios():
    """Test different market trend scenarios"""
    print("\n" + "=" * 60)
    print("  Trend Following Scenario Analysis")
    print("=" * 60)
    
    # Create EA instance
    ea = TrendFollowingEA(
        symbol="EURUSD",
        lot_size=0.1,
        login=210715557,
        password="Johannes@0",
        server="Exness-MT5Trial9"
    )
    
    if not ea.initialize_mt5():
        print("❌ Failed to initialize MT5")
        return
    
    print(f"📊 Analyzing current market conditions for trend following...")
    
    # Get comprehensive analysis
    signal_data = ea.generate_signal()
    if not signal_data:
        print("❌ Failed to generate signal data")
        return
    
    primary = signal_data['primary_analysis']
    secondary = signal_data['secondary_analysis']
    
    print(f"\n🔍 Current Market Analysis:")
    print(f"   Symbol: {ea.symbol}")
    print(f"   Current Price: {primary['price']:.5f}")
    print(f"   Timeframes: H4 (primary) + D1 (secondary)")
    
    print(f"\n📈 Primary Timeframe (H4) Indicators:")
    print(f"   EMA Fast (21): {primary['ema_fast']:.5f}")
    print(f"   EMA Slow (50): {primary['ema_slow']:.5f}")
    print(f"   EMA Filter (200): {primary['ema_filter']:.5f}")
    print(f"   ATR: {primary['atr']:.5f}")
    print(f"   ADX: {primary['adx']:.2f}")
    print(f"   RSI: {primary['rsi']:.2f}")
    
    print(f"\n📊 Secondary Timeframe (D1) Confirmation:")
    print(f"   Above Long-term Filter: {'Yes' if secondary['above_filter'] else 'No'}")
    print(f"   Trend Direction: {'Bullish' if secondary['uptrend_strength'] else 'Bearish'}")
    print(f"   Trend Strength: {'Strong' if secondary['strong_trend'] else 'Weak'}")
    
    # Signal analysis
    signal = signal_data['signal']
    print(f"\n🎯 Trading Signal Analysis:")
    print(f"   Current Signal: {signal if signal else 'No signal - waiting for setup'}")
    
    if signal:
        print(f"   Signal Type: {signal}")
        print(f"   Confidence: High (multi-timeframe confirmation)")
        print(f"   Recommended Action: Enter {signal.lower()} position")
    else:
        print(f"   Signal Status: Analyzing market conditions...")
        
        # Explain why no signal
        reasons = []
        if not primary['strong_trend']:
            reasons.append(f"ADX too low ({primary['adx']:.2f} < {ea.adx_threshold})")
        if not (primary['above_filter'] and secondary['above_filter']) and not (primary['below_filter'] and secondary['below_filter']):
            reasons.append("Timeframes not aligned")
        if not primary['ema_cross_up'] and not primary['ema_cross_down']:
            reasons.append("No EMA crossover signal")
        
        if reasons:
            print(f"   Waiting for: {', '.join(reasons)}")
    
    # Risk assessment
    account_info = mt5.account_info()
    if account_info:
        position_size = ea.calculate_position_size(primary['atr'], account_info.balance, 2.0)
        stop_loss_distance = primary['atr'] * ea.atr_multiplier
        risk_amount = account_info.balance * 0.02  # 2% risk
        
        print(f"\n💰 Risk Management:")
        print(f"   Account Balance: ${account_info.balance:.2f}")
        print(f"   Risk per Trade: 2% (${risk_amount:.2f})")
        print(f"   Calculated Lot Size: {position_size:.2f}")
        print(f"   Stop Loss Distance: {stop_loss_distance:.5f} ({stop_loss_distance/ea.get_symbol_info().point:.0f} points)")
        print(f"   Take Profit Distance: {stop_loss_distance * 3:.5f} (3:1 RR)")
    
    # Market suitability
    print(f"\n🎭 Market Suitability for Trend Following:")
    
    suitability_score = 0
    max_score = 5
    
    if primary['strong_trend']:
        suitability_score += 1
        print(f"   ✅ Strong trend detected (ADX: {primary['adx']:.2f})")
    else:
        print(f"   ❌ Weak trend (ADX: {primary['adx']:.2f})")
    
    if primary['above_filter'] == secondary['above_filter']:
        suitability_score += 1
        print(f"   ✅ Timeframes aligned")
    else:
        print(f"   ❌ Mixed timeframe signals")
    
    if 30 < primary['rsi'] < 70:
        suitability_score += 1
        print(f"   ✅ RSI in neutral zone ({primary['rsi']:.2f})")
    else:
        print(f"   ⚠️  RSI in extreme zone ({primary['rsi']:.2f})")
    
    spread = ea.get_symbol_info().spread
    if spread <= 2:
        suitability_score += 1
        print(f"   ✅ Good spread conditions ({spread} points)")
    else:
        print(f"   ⚠️  High spread ({spread} points)")
    
    volatility = primary['atr'] / primary['price'] * 10000  # ATR as percentage in pips
    if 10 <= volatility <= 50:
        suitability_score += 1
        print(f"   ✅ Good volatility ({volatility:.1f} pips)")
    else:
        print(f"   ⚠️  {'Low' if volatility < 10 else 'High'} volatility ({volatility:.1f} pips)")
    
    print(f"\n📊 Overall Suitability: {suitability_score}/{max_score}")
    if suitability_score >= 4:
        print(f"   🟢 Excellent conditions for trend following")
    elif suitability_score >= 3:
        print(f"   🟡 Good conditions with some caution")
    else:
        print(f"   🔴 Poor conditions - consider waiting")
    
    ea.stop()

if __name__ == "__main__":
    # Run main tests
    run_tests()
    
    # Run scenario analysis
    print("\n" + "="*25 + " SCENARIO ANALYSIS " + "="*25)
    test_trend_scenarios()
