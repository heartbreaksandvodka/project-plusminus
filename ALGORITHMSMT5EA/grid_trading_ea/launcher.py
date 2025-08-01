"""
Grid Trading EA Launcher
Interactive menu to run the EA or tests
"""

import sys
import os

def show_menu():
    """Display the main menu"""
    print("\n" + "="*60)
    print("  MetaTrader 5 Grid Trading EA Launcher")
    print("="*60)
    print("1. Run Grid Trading EA (Live Trading)")
    print("2. Test EA Connection & Setup")
    print("3. Run Grid Trading Tests")
    print("4. Simulate Grid Behavior (No Orders)")
    print("5. View Current Grid Status")
    print("6. Emergency Stop (Close All)")
    print("7. Exit")
    print("="*60)

def run_ea():
    """Run the main Grid Trading EA"""
    try:
        print("\n🚀 Starting Grid Trading EA...")
        print("⚠️  WARNING: This will place real pending orders!")
        print("⚠️  Make sure you understand grid trading risks!")
        
        confirm = input("\nType 'START' to confirm: ").strip().upper()
        if confirm != 'START':
            print("❌ Grid EA start cancelled.")
            return
        
        from mt5_grid_trading_ea import main
        main()
    except Exception as e:
        print(f"❌ Error running Grid EA: {e}")

def test_connection():
    """Test MT5 connection"""
    try:
        print("\n🔍 Testing connection...")
        from mt5_grid_trading_ea import test_connection
        test_connection()
    except Exception as e:
        print(f"❌ Error testing connection: {e}")

def run_full_tests():
    """Run the complete test suite"""
    try:
        print("\n🧪 Running Grid Trading EA tests...")
        from test_ea import run_tests
        run_tests()
    except Exception as e:
        print(f"❌ Error running tests: {e}")

def run_trading_tests():
    """Run trading functionality tests"""
    try:
        print("\n📊 Running trading tests...")
        from trading_test import test_grid_orders
        test_grid_orders()
    except Exception as e:
        print(f"❌ Error running trading tests: {e}")

def simulate_grid():
    """Run grid simulation without placing orders"""
    try:
        print("\n📈 Running grid simulation...")
        from test_ea import test_grid_simulation
        test_grid_simulation()
    except Exception as e:
        print(f"❌ Error running simulation: {e}")

def view_grid_status():
    """View current grid status"""
    try:
        print("\n📊 Checking current grid status...")
        
        from mt5_grid_trading_ea import GridTradingEA
        import MetaTrader5 as mt5
        
        ea = GridTradingEA(
            login=210715557,
            password="Johannes@0",
            server="Exness-MT5Trial9"
        )
        
        if ea.initialize_mt5():
            orders = ea.get_existing_orders()
            positions = ea.get_existing_positions()
            
            print(f"\n📋 Current Grid Status:")
            print(f"   Active Pending Orders: {len(orders)}")
            print(f"   Open Positions: {len(positions)}")
            
            if orders:
                buy_orders = [o for o in orders if o.type == mt5.ORDER_TYPE_BUY_LIMIT]
                sell_orders = [o for o in orders if o.type == mt5.ORDER_TYPE_SELL_LIMIT]
                
                print(f"\n   📈 Buy Orders ({len(buy_orders)}):")
                for order in buy_orders[:5]:  # Show first 5
                    print(f"     {order.volume} lots at {order.price_open:.5f}")
                
                print(f"\n   📉 Sell Orders ({len(sell_orders)}):")
                for order in sell_orders[:5]:  # Show first 5
                    print(f"     {order.volume} lots at {order.price_open:.5f}")
            
            if positions:
                total_profit = sum([pos.profit for pos in positions])
                total_volume = sum([pos.volume for pos in positions])
                
                print(f"\n   💰 Position Summary:")
                print(f"     Total Volume: {total_volume} lots")
                print(f"     Total P&L: ${total_profit:.2f}")
                
                print(f"\n   📍 Active Positions:")
                for pos in positions[:5]:  # Show first 5
                    pos_type = "BUY" if pos.type == mt5.ORDER_TYPE_BUY else "SELL"
                    print(f"     {pos_type} {pos.volume} lots at {pos.price_open:.5f}, P&L: ${pos.profit:.2f}")
            
            if not orders and not positions:
                print("   ✅ No active grid orders or positions")
            
            ea.stop()
        else:
            print("❌ Failed to connect to MT5")
            
    except Exception as e:
        print(f"❌ Error checking grid status: {e}")

def emergency_stop():
    """Emergency stop - close all positions and cancel orders"""
    try:
        print("\n🚨 EMERGENCY STOP INITIATED")
        print("⚠️  This will close ALL positions and cancel ALL orders!")
        
        confirm = input("Type 'STOP' to confirm emergency stop: ").strip().upper()
        if confirm != 'STOP':
            print("❌ Emergency stop cancelled.")
            return
        
        from mt5_grid_trading_ea import GridTradingEA
        
        ea = GridTradingEA(
            login=210715557,
            password="Johannes@0",
            server="Exness-MT5Trial9"
        )
        
        if ea.initialize_mt5():
            print("🔄 Closing all positions...")
            ea.close_all_positions()
            
            print("🔄 Cancelling all orders...")
            ea.cancel_all_orders()
            
            print("✅ Emergency stop completed!")
            ea.stop()
        else:
            print("❌ Failed to connect to MT5")
            
    except Exception as e:
        print(f"❌ Error during emergency stop: {e}")

def show_risk_warning():
    """Show risk warning for grid trading"""
    print("\n" + "="*60)
    print("  ⚠️  GRID TRADING RISK WARNING ⚠️")
    print("="*60)
    print("Grid Trading involves significant risks:")
    print("• Can open many positions simultaneously")
    print("• Requires substantial margin/capital")
    print("• Can amplify losses in trending markets")
    print("• Best suited for ranging/sideways markets")
    print("• Always test on demo account first")
    print("• Never risk more than you can afford to lose")
    print("="*60)

def main():
    """Main launcher function"""
    show_risk_warning()
    
    while True:
        show_menu()
        try:
            choice = input("\nEnter your choice (1-7): ").strip()
            
            if choice == "1":
                run_ea()
            
            elif choice == "2":
                test_connection()
            
            elif choice == "3":
                run_full_tests()
            
            elif choice == "4":
                simulate_grid()
            
            elif choice == "5":
                view_grid_status()
            
            elif choice == "6":
                emergency_stop()
            
            elif choice == "7":
                print("👋 Goodbye!")
                break
            
            else:
                print("❌ Invalid choice. Please enter 1-7.")
                
        except KeyboardInterrupt:
            print("\n\n🛑 Launcher stopped by user.")
            break
        except Exception as e:
            print(f"❌ An error occurred: {e}")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
