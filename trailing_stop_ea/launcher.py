"""
EA Launcher
Simple script to run the EA or tests from the root directory
"""

import sys
import os

def show_menu():
    """Display the main menu"""
    print("\n" + "="*50)
    print("  MetaTrader 5 Trailing Stop EA Launcher")
    print("="*50)
    print("1. Run EA (Live Trading)")
    print("2. Test EA Connection")
    print("3. Run Trading Test")
    print("4. Exit")
    print("="*50)

def run_ea():
    """Run the main EA"""
    try:
        from mt5_trailing_stop_ea import main
        print("Starting EA...")
        main()
    except Exception as e:
        print(f"Error running EA: {e}")

def test_connection():
    """Test MT5 connection"""
    try:
        from mt5_trailing_stop_ea import test_connection
        test_connection()
    except Exception as e:
        print(f"Error testing connection: {e}")

def run_test_suite():
    """Run the complete test suite"""
    try:
        from test_ea import run_tests
        run_tests()
    except Exception as e:
        print(f"Error running tests: {e}")

def run_trading_test():
    """Run trading functionality test"""
    try:
        from trading_test import test_trading
        test_trading()
    except Exception as e:
        print(f"Error running trading test: {e}")

def main():
    """Main launcher function"""
    while True:
        show_menu()
        try:
            choice = input("\nEnter your choice (1-4): ").strip()
            
            if choice == "1":
                print("\n⚠️  WARNING: This will start live trading!")
                confirm = input("Are you sure? (yes/no): ").strip().lower()
                if confirm in ['yes', 'y']:
                    run_ea()
                else:
                    print("EA start cancelled.")
            
            elif choice == "2":
                test_connection()
            
            elif choice == "3":
                run_trading_test()
            
            elif choice == "4":
                print("Goodbye!")
                break
            
            else:
                print("Invalid choice. Please enter 1-4.")
                
        except KeyboardInterrupt:
            print("\n\nLauncher stopped by user.")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
