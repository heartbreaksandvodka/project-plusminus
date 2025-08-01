"""
Trend Following EA Launcher
Interactive menu to run the EA or tests
"""

import sys
import os

def show_menu():
    """Display the main menu"""
    print("\n" + "="*65)
    print("  MetaTrader 5 Trend Following EA Launcher")
    print("="*65)
    print("1. Run Trend Following EA (Live Trading)")
    print("2. Test EA Connection & Setup")
    print("3. Run Comprehensive Tests")
    print("4. Test Trading Functions")
    print("5. Analyze Current Market Trends")
    print("6. View Current Positions")
    print("7. Close All Positions")
    print("8. Exit")
    print("="*65)

def run_ea():
    """Run the main Trend Following EA"""
    try:
        print("\n🚀 Starting Trend Following EA...")
        print("⚠️  WARNING: This EA is designed for long-term trend following!")
        print("⚠️  It uses H4 and D1 timeframes - positions may be held for days/weeks!")
        print("⚠️  Make sure you understand the strategy before starting!")
        
        confirm = input("\nType 'START' to confirm: ").strip().upper()
        if confirm != 'START':
            print("❌ Trend Following EA start cancelled.")
            return
        
        from mt5_trend_following_ea import main
        main()
    except Exception as e:
        print(f"❌ Error running Trend Following EA: {e}")

def test_connection():
    """Test MT5 connection"""
    try:
        print("\n🔍 Testing connection...")
        from mt5_trend_following_ea import test_connection
        test_connection()
    except Exception as e:
        print(f"❌ Error testing connection: {e}")

def run_full_tests():
    """Run the complete test suite"""
    try:
        print("\n🧪 Running Trend Following EA comprehensive tests...")
        from test_ea import run_tests
        run_tests()
    except Exception as e:
        print(f"❌ Error running tests: {e}")

def run_trading_tests():
    """Run trading functionality tests"""
    try:
        print("\n📊 Running trading functionality tests...")
        from trading_test import test_trend_trading
        test_trend_trading()
    except Exception as e:
        print(f"❌ Error running trading tests: {e}")

def analyze_trends():
    """Analyze current market trends"""
    try:
        print("\n📈 Analyzing current market trends...")
        from test_ea import test_trend_scenarios
        test_trend_scenarios()
    except Exception as e:
        print(f"❌ Error analyzing trends: {e}")

def view_positions():
    """View current positions"""
    try:
        print("\n📊 Checking current positions...")
        
        from mt5_trend_following_ea import TrendFollowingEA
        import MetaTrader5 as mt5
        
        ea = TrendFollowingEA(
            login=210715557,
            password="Johannes@0",
            server="Exness-MT5Trial9"
        )
        
        if ea.initialize_mt5():
            positions = ea.get_open_positions()
            
            print(f"\n📋 Current Trend Following Positions:")
            print(f"   Open Positions: {len(positions)}")
            
            if positions:
                total_profit = sum([pos.profit for pos in positions])
                total_volume = sum([pos.volume for pos in positions])
                
                print(f"\n   💰 Position Summary:")
                print(f"     Total Volume: {total_volume} lots")
                print(f"     Total P&L: ${total_profit:.2f}")
                
                print(f"\n   📍 Individual Positions:")
                for i, pos in enumerate(positions, 1):
                    pos_type = "BUY" if pos.type == mt5.ORDER_TYPE_BUY else "SELL"
                    days_open = (mt5.symbol_info_tick(ea.symbol).time - pos.time) / 86400
                    
                    print(f"     {i}. {pos_type} {pos.volume} lots")
                    print(f"        Entry: {pos.price_open:.5f}")
                    print(f"        Current: {pos.price_current:.5f}")
                    print(f"        P&L: ${pos.profit:.2f}")
                    print(f"        Stop Loss: {pos.sl:.5f}")
                    print(f"        Take Profit: {pos.tp:.5f}")
                    print(f"        Days Open: {days_open:.1f}")
                    print()
                
                # Show trend analysis for current positions
                print(f"   📊 Current Market Analysis:")
                signal_data = ea.generate_signal()
                if signal_data:
                    primary = signal_data['primary_analysis']
                    print(f"     Current Signal: {signal_data['signal'] if signal_data['signal'] else 'No new signal'}")
                    print(f"     Trend Strength: {'Strong' if primary['strong_trend'] else 'Weak'} (ADX: {primary['adx']:.2f})")
                    print(f"     Market Bias: {'Bullish' if primary['above_filter'] else 'Bearish'}")
            else:
                print("   ✅ No active trend following positions")
                
                # Show current market opportunities
                signal_data = ea.generate_signal()
                if signal_data:
                    if signal_data['signal']:
                        print(f"\n   🎯 Current Market Opportunity:")
                        print(f"     Signal: {signal_data['signal']}")
                        print(f"     Strength: High (multi-timeframe confirmation)")
                    else:
                        print(f"\n   ⏱️  Waiting for trend setup...")
                        primary = signal_data['primary_analysis']
                        print(f"     ADX: {primary['adx']:.2f} (need >{ea.adx_threshold})")
                        print(f"     Price vs Filter: {'Above' if primary['above_filter'] else 'Below'} long-term EMA")
            
            ea.stop()
        else:
            print("❌ Failed to connect to MT5")
            
    except Exception as e:
        print(f"❌ Error checking positions: {e}")

def close_all_positions():
    """Close all positions"""
    try:
        print("\n🚨 CLOSE ALL POSITIONS")
        print("⚠️  This will close ALL trend following positions!")
        print("⚠️  This may interrupt long-term trend trades!")
        
        confirm = input("Type 'CLOSE' to confirm: ").strip().upper()
        if confirm != 'CLOSE':
            print("❌ Position closure cancelled.")
            return
        
        from mt5_trend_following_ea import TrendFollowingEA
        
        ea = TrendFollowingEA(
            login=210715557,
            password="Johannes@0",
            server="Exness-MT5Trial9"
        )
        
        if ea.initialize_mt5():
            positions = ea.get_open_positions()
            if positions:
                print(f"🔄 Closing {len(positions)} positions...")
                closed_count = ea.close_all_positions()
                print(f"✅ Successfully closed {closed_count} positions!")
            else:
                print("✅ No positions to close")
            
            ea.stop()
        else:
            print("❌ Failed to connect to MT5")
            
    except Exception as e:
        print(f"❌ Error closing positions: {e}")

def show_strategy_info():
    """Show strategy information"""
    print("\n" + "="*65)
    print("  📚 TREND FOLLOWING STRATEGY INFO")
    print("="*65)
    print("Strategy Overview:")
    print("• Designed for capturing major market trends")
    print("• Uses multi-timeframe analysis (H4 + D1)")
    print("• Employs EMA crossovers and trend strength filters")
    print("• Positions held for days to weeks")
    print("• Risk managed with ATR-based stops")
    print("")
    print("Best Market Conditions:")
    print("• Strong trending markets (ADX > 25)")
    print("• Clear directional moves")
    print("• Low to moderate volatility")
    print("• Major currency pairs")
    print("")
    print("Risk Considerations:")
    print("• Long holding periods")
    print("• Potential for significant drawdowns")
    print("• Requires patience and discipline")
    print("• Not suitable for scalping or day trading")
    print("="*65)

def main():
    """Main launcher function"""
    show_strategy_info()
    
    while True:
        show_menu()
        try:
            choice = input("\nEnter your choice (1-8): ").strip()
            
            if choice == "1":
                run_ea()
            
            elif choice == "2":
                test_connection()
            
            elif choice == "3":
                run_full_tests()
            
            elif choice == "4":
                run_trading_tests()
            
            elif choice == "5":
                analyze_trends()
            
            elif choice == "6":
                view_positions()
            
            elif choice == "7":
                close_all_positions()
            
            elif choice == "8":
                print("👋 Goodbye!")
                break
            
            else:
                print("❌ Invalid choice. Please enter 1-8.")
                
        except KeyboardInterrupt:
            print("\n\n🛑 Launcher stopped by user.")
            break
        except Exception as e:
            print(f"❌ An error occurred: {e}")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
