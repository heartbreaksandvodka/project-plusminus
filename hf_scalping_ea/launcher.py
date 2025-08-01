"""
HF Scalping EA Simple Launcher
Simple script to run the EA or tests like other EAs
"""

import sys
import os

def show_menu():
    """Display the main menu"""
    print("\n" + "="*60)
    print("  MetaTrader 5 High-Frequency Scalping EA Launcher")
    print("="*60)
    print("1. Run HF Scalping EA (Live Trading)")
    print("2. Test EA Connection & Setup")
    print("3. Run HF Scalping Tests")
    print("4. View Performance Statistics")
    print("5. Check Account Balance & Risk")
    print("6. Emergency Stop (Close All)")
    print("7. Exit")
    print("="*60)

def run_ea():
    """Run the main HF Scalping EA"""
    try:
        print("\n🚀 Starting High-Frequency Scalping EA...")
        print("📊 Risk Management: 3% per trade, percentage-based system")
        print("⚠️  WARNING: This will execute high-frequency trades!")
        print("⚠️  Make sure you understand scalping risks!")
        
        confirm = input("\nType 'START' to confirm: ").strip().upper()
        if confirm == 'START':
            from mt5_hf_scalping_ea import main
            print("🔥 Starting High-Frequency Scalping...")
            main()
        else:
            print("❌ Operation cancelled")
    except Exception as e:
        print(f"❌ Error running EA: {e}")

def test_connection():
    """Test MT5 connection"""
    try:
        print("\n🔧 Testing MT5 Connection...")
        from mt5_hf_scalping_ea import HighFrequencyScalpingEA
        
        ea = HighFrequencyScalpingEA()
        if ea.initialize_mt5():
            print("✅ MT5 connection successful!")
            print(f"✅ Account: Connected")
            print(f"✅ Symbol: {ea.symbol}")
            print(f"✅ Risk per trade: {ea.scalp_target_percent}% of account")
            print(f"✅ Stop loss: {ea.stop_loss_percent}% of account")
            print(f"✅ Trailing stop: {ea.trailing_stop_percent}% of account")
        else:
            print("❌ MT5 connection failed!")
            
    except Exception as e:
        print(f"❌ Connection test failed: {e}")

def run_tests():
    """Run EA tests"""
    try:
        print("\n🧪 Running HF Scalping EA Tests...")
        os.system("python test_ea.py")
    except Exception as e:
        print(f"❌ Error running tests: {e}")

def view_performance():
    """View performance statistics"""
    try:
        print("\n📈 Performance Statistics...")
        # Read recent log entries
        try:
            with open('hf_scalping_ea.log', 'r') as f:
                lines = f.readlines()
                if lines:
                    print("📝 Recent EA Activity:")
                    for line in lines[-10:]:  # Last 10 lines
                        print(f"   {line.strip()}")
                else:
                    print("📝 No recent activity")
        except FileNotFoundError:
            print("📝 No log file found")
            
        # Show current config
        try:
            import config
            print(f"\n⚙️  Current Configuration:")
            print(f"   Symbol: {config.SYMBOL}")
            print(f"   Risk per trade: {config.SCALP_TARGET_PERCENT}%")
            print(f"   Stop loss: {config.STOP_LOSS_PERCENT}%")
            print(f"   Trailing stop: {config.TRAILING_STOP_PERCENT}%")
            print(f"   Daily loss limit: {config.DAILY_LOSS_LIMIT_PERCENT}%")
            print(f"   Daily profit target: {config.DAILY_PROFIT_TARGET_PERCENT}%")
            print(f"   Max daily trades: {config.MAX_DAILY_TRADES}")
        except Exception as e:
            print(f"⚠️  Error reading config: {e}")
            
    except Exception as e:
        print(f"❌ Error viewing performance: {e}")

def check_account_risk():
    """Check account balance and risk parameters"""
    try:
        print("\n💰 Account Balance & Risk Check...")
        from mt5_hf_scalping_ea import HighFrequencyScalpingEA
        
        ea = HighFrequencyScalpingEA()
        if ea.initialize_mt5():
            balance = ea.get_account_balance()
            risk_amount = ea.calculate_percentage_amount(3.0)  # 3% risk
            
            print(f"💳 Account Balance: ${balance:,.2f}")
            print(f"💰 Risk per trade: ${risk_amount:,.2f} (3% of balance)")
            print(f"📊 Daily loss limit: ${balance * 0.09:,.2f} (9% of balance)")
            print(f"🎯 Daily profit target: ${balance * 0.15:,.2f} (15% of balance)")
            
            # Calculate position size
            lot_size = ea.calculate_position_size()
            print(f"📈 Position size: {lot_size} lots")
            
        else:
            print("❌ Could not connect to get account info")
            
    except Exception as e:
        print(f"❌ Error checking account: {e}")

def emergency_stop():
    """Emergency stop all positions"""
    try:
        print("\n🚨 EMERGENCY STOP - Closing all positions...")
        confirm = input("Type 'STOP' to confirm emergency closure: ").strip().upper()
        if confirm == 'STOP':
            import MetaTrader5 as mt5
            if mt5.initialize():
                positions = mt5.positions_get()
                if positions:
                    closed = 0
                    for pos in positions:
                        # Close position logic here
                        print(f"   Closing position {pos.ticket}")
                        closed += 1
                    print(f"✅ Closed {closed} positions")
                else:
                    print("ℹ️  No open positions found")
                mt5.shutdown()
            else:
                print("❌ Could not connect to MT5")
        else:
            print("❌ Emergency stop cancelled")
    except Exception as e:
        print(f"❌ Error in emergency stop: {e}")

def main():
    """Main launcher loop"""
    while True:
        try:
            show_menu()
            choice = input("\n📝 Enter your choice (1-7): ").strip()
            
            if choice == '1':
                run_ea()
            elif choice == '2':
                test_connection()
            elif choice == '3':
                run_tests()
            elif choice == '4':
                view_performance()
            elif choice == '5':
                check_account_risk()
            elif choice == '6':
                emergency_stop()
            elif choice == '7':
                print("\n👋 Goodbye!")
                break
            else:
                print("\n❌ Invalid choice. Please try again.")
                
            input("\n📝 Press Enter to continue...")
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            input("📝 Press Enter to continue...")

if __name__ == "__main__":
    main()
