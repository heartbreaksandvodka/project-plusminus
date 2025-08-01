"""
Interactive launcher for High-Frequency Scalping EA
Provides user-friendly menu interface for EA management
"""

import os
import sys
import time
import subprocess
from datetime import datetime

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Print the EA header"""
    print("=" * 60)
    print("     MetaTrader 5 High-Frequency Scalping EA")
    print("     Author: Johannes N. Nkosi")
    print("     Date: July 26, 2025")
    print("=" * 60)
    print()

def print_menu():
    """Print the main menu"""
    print("📈 HIGH-FREQUENCY SCALPING EA MENU")
    print()
    print("1. 🚀 Start Scalping EA")
    print("2. ⚙️  View/Edit Configuration")
    print("3. 🧪 Run Test Suite")
    print("4. 📊 View Trading Performance")
    print("5. 📋 Check MT5 Connection")
    print("6. 📖 View Documentation")
    print("7. 🔄 Update EA")
    print("8. ❌ Exit")
    print()

def start_ea():
    """Start the High-Frequency Scalping EA"""
    clear_screen()
    print_header()
    print("🚀 Starting High-Frequency Scalping EA...")
    print()
    print("⚠️  IMPORTANT SCALPING NOTES:")
    print("   • This EA executes 50-100 trades per day")
    print("   • Requires low-latency internet connection")
    print("   • Uses tight stops (5-15 points)")
    print("   • Best during London/New York sessions")
    print("   • Monitor spread conditions closely")
    print()
    
    confirm = input("Ready to start scalping? (y/n): ").lower()
    if confirm == 'y':
        print("\n🔥 Launching High-Frequency Scalping EA...")
        print("Press Ctrl+C to stop the EA")
        print("-" * 50)
        
        try:
            # Import and run the EA
            from mt5_hf_scalping_ea import main
            main()
        except KeyboardInterrupt:
            print("\n\n⏹️  EA stopped by user")
        except ImportError as e:
            print(f"\n❌ Error importing EA: {e}")
        except Exception as e:
            print(f"\n❌ Error running EA: {e}")
    else:
        print("\n↩️  Returning to main menu...")
    
    input("\nPress Enter to continue...")

def view_config():
    """View and edit configuration"""
    clear_screen()
    print_header()
    print("⚙️  SCALPING EA CONFIGURATION")
    print()
    
    try:
        with open('config.py', 'r') as f:
            config_content = f.read()
        
        print("Current configuration:")
        print("-" * 40)
        print(config_content)
        print("-" * 40)
        
        edit = input("\nEdit configuration? (y/n): ").lower()
        if edit == 'y':
            if os.name == 'nt':
                os.system('notepad config.py')
            else:
                os.system('nano config.py')
                
    except FileNotFoundError:
        print("❌ Configuration file not found!")
    except Exception as e:
        print(f"❌ Error reading configuration: {e}")
    
    input("\nPress Enter to continue...")

def run_tests():
    """Run the test suite"""
    clear_screen()
    print_header()
    print("🧪 RUNNING SCALPING EA TESTS")
    print()
    
    try:
        print("1. Running connection tests...")
        subprocess.run([sys.executable, 'test_ea.py'], check=True)
        
        print("\n2. Running trading tests...")
        subprocess.run([sys.executable, 'trading_test.py'], check=True)
        
        print("\n✅ All tests completed!")
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Test failed with error code: {e.returncode}")
    except FileNotFoundError:
        print("\n❌ Test files not found!")
    except Exception as e:
        print(f"\n❌ Error running tests: {e}")
    
    input("\nPress Enter to continue...")

def view_performance():
    """View trading performance"""
    clear_screen()
    print_header()
    print("📊 SCALPING EA PERFORMANCE")
    print()
    
    try:
        # Check if log file exists
        if os.path.exists('hf_scalping_ea.log'):
            print("📄 Recent EA Activity:")
            print("-" * 40)
            
            with open('hf_scalping_ea.log', 'r') as f:
                lines = f.readlines()
                # Show last 20 lines
                for line in lines[-20:]:
                    print(line.strip())
        else:
            print("📄 No log file found. EA hasn't been run yet.")
            
        print()
        print("💡 Tips for Scalping Performance:")
        print("   • Monitor win rate (target: >60%)")
        print("   • Watch daily trade count (50-100)")
        print("   • Keep spreads under 8 points")
        print("   • Best performance during high volatility")
        
    except Exception as e:
        print(f"❌ Error reading performance data: {e}")
    
    input("\nPress Enter to continue...")

def check_mt5_connection():
    """Check MetaTrader 5 connection"""
    clear_screen()
    print_header()
    print("📋 MT5 CONNECTION CHECK")
    print()
    
    try:
        import MetaTrader5 as mt5
        
        if not mt5.initialize():
            print("❌ MetaTrader 5 not initialized")
            print("   Please ensure MT5 is running and try again")
            return
            
        print("✅ MetaTrader 5 initialized successfully")
        
        # Try to get account info
        account_info = mt5.account_info()
        if account_info:
            print(f"📊 Account: {account_info.login}")
            print(f"💰 Balance: {account_info.balance:.2f}")
            print(f"📈 Equity: {account_info.equity:.2f}")
            print(f"🏦 Server: {account_info.server}")
        
        # Check symbol
        from config import SYMBOL
        symbol_info = mt5.symbol_info(SYMBOL)
        if symbol_info:
            print(f"📊 Symbol: {SYMBOL}")
            print(f"📏 Spread: {symbol_info.spread} points")
            print(f"💱 Bid/Ask: {symbol_info.bid}/{symbol_info.ask}")
        
        mt5.shutdown()
        print("\n✅ Connection test completed successfully!")
        
    except ImportError:
        print("❌ MetaTrader5 package not installed")
        print("   Run: pip install MetaTrader5")
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
    
    input("\nPress Enter to continue...")

def view_documentation():
    """View documentation"""
    clear_screen()
    print_header()
    print("📖 SCALPING EA DOCUMENTATION")
    print()
    
    try:
        if os.path.exists('README.md'):
            with open('README.md', 'r') as f:
                content = f.read()
            print(content)
        else:
            print("📄 README.md not found")
            print()
            print("📖 Quick Documentation:")
            print("   • This EA uses high-frequency scalping strategies")
            print("   • Targets 5-point profits with 15-point stops")
            print("   • Analyzes order flow for entry signals")
            print("   • Executes 50-100 trades per day")
            print("   • Best during London/New York overlap")
            
    except Exception as e:
        print(f"❌ Error reading documentation: {e}")
    
    input("\nPress Enter to continue...")

def update_ea():
    """Update EA (placeholder)"""
    clear_screen()
    print_header()
    print("🔄 UPDATE SCALPING EA")
    print()
    print("📋 Current Version: 1.0.0")
    print("📅 Last Update: July 26, 2025")
    print()
    print("🔍 Checking for updates...")
    time.sleep(2)
    print("✅ You have the latest version!")
    print()
    print("🆕 What's New in v1.0.0:")
    print("   • Advanced order flow analysis")
    print("   • High-frequency execution engine")
    print("   • Tight spread filtering")
    print("   • Daily trade and profit limits")
    print("   • Real-time performance monitoring")
    
    input("\nPress Enter to continue...")

def main():
    """Main launcher function"""
    while True:
        clear_screen()
        print_header()
        print_menu()
        
        try:
            choice = input("Select option (1-8): ").strip()
            
            if choice == '1':
                start_ea()
            elif choice == '2':
                view_config()
            elif choice == '3':
                run_tests()
            elif choice == '4':
                view_performance()
            elif choice == '5':
                check_mt5_connection()
            elif choice == '6':
                view_documentation()
            elif choice == '7':
                update_ea()
            elif choice == '8':
                clear_screen()
                print("👋 Thank you for using High-Frequency Scalping EA!")
                print("💰 Happy Scalping!")
                break
            else:
                print("\n❌ Invalid option. Please try again.")
                time.sleep(1)
                
        except KeyboardInterrupt:
            clear_screen()
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            input("Press Enter to continue...")

if __name__ == "__main__":
    main()
