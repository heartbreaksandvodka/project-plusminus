"""
MetaTrader 5 Risk-Based Trailing Stop Manager
Author: Johannes N. Nkosi
Date: July 23, 2025

This EA manages trailing stops based on account balance risk.
It calculates stop loss distances so that if hit, you only lose a specified % of your balance.
It does not open new trades - it only trails stop losses for existing trades.
"""

import MetaTrader5 as mt5
from datetime import datetime
import time
import sys
import os
# Add root directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Import global configuration and risk management
from global_config import *
from risk_manager import RiskManager
# Import common EA utilities
from ALGORITHMSMT5EA.common_ea import initialize_mt5, get_symbol_info, get_current_price, check_pause_flag

class TrailingStopManager:
    def __init__(self, symbol="EURUSD", risk_percentage=None, 
                 magic_number=0):
        """
        Initialize the Trailing Stop Manager
        
        Args:
            symbol (str): Trading symbol (default: EURUSD)
            risk_percentage (float): Percentage of balance to risk (uses global config if None)
            magic_number (int): Unique identifier for EA trades (0 = all trades)
        """
        self.symbol = symbol
        self.risk_percentage = risk_percentage or TRAILING_STEP_PERCENT
        self.magic_number = magic_number
        self.is_running = False
        
        # Use global credentials
        credentials = get_account_credentials()
        self.login = credentials['login']
        self.password = credentials['password'] 
        self.server = credentials['server']
        
        # Initialize risk manager
        self.risk_manager = RiskManager(f"TrailingStop_{symbol}")
        
    def initialize_mt5(self):
        # Use shared utility
        return initialize_mt5(self.login, self.password, self.server)
    
    def get_symbol_info(self):
        # Use shared utility
        return get_symbol_info(self.symbol)
    
    def get_current_price(self):
        # Use shared utility
        return get_current_price(self.symbol)
    
    def calculate_risk_based_sl(self, position):
        """Calculate stop loss based on percentage of account balance"""
        # Use risk manager to calculate
        balance = self.risk_manager.get_account_balance()
        risk_amount = balance * (self.risk_percentage / 100)
        
        # Get symbol info for pip value calculation
        symbol_info = self.get_symbol_info()
        if symbol_info is None:
            return None
            
        # Calculate pip value for this position
        point = symbol_info.point
        tick_value = symbol_info.trade_tick_value
        lot_size = position.volume
        
        # For most forex pairs, 1 pip = 10 * point
        pip_value = tick_value * 10 * lot_size
        
        # Calculate how many pips we can risk
        max_pips_risk = risk_amount / pip_value if pip_value > 0 else 10
        
        # Get current price
        bid, ask = self.get_current_price()
        if bid is None or ask is None:
            return None
            
        # Calculate stop loss based on position type
        if position.type == mt5.ORDER_TYPE_BUY:
            sl_price = bid - (max_pips_risk * point * 10)
        else:
            sl_price = ask + (max_pips_risk * point * 10)
            
        print(f"Risk Calculation for Position #{position.ticket}:")
        print(f"  Balance: ${balance:.2f}")
        print(f"  Risk Amount ({self.risk_percentage}%): ${risk_amount:.2f}")
        print(f"  Lot Size: {lot_size}")
        print(f"  Pip Value: ${pip_value:.2f}")
        print(f"  Max Pips Risk: {max_pips_risk:.1f}")
        print(f"  Calculated SL: {sl_price:.5f}")
        
        return sl_price

    def get_open_positions(self):
        """Get all open positions for the symbol"""
        if self.magic_number == 0:
            # Get all positions for the symbol regardless of magic number
            positions = mt5.positions_get(symbol=self.symbol)
        else:
            # Get positions with specific magic number
            positions = mt5.positions_get(symbol=self.symbol, magic=self.magic_number)
        
        if positions is None:
            return []
        return list(positions)
    
    def modify_position_sl(self, position, new_sl):
        """Modify the stop loss of a position"""
        request = {
            "action": mt5.TRADE_ACTION_SLTP,
            "symbol": position.symbol,
            "position": position.ticket,
            "sl": new_sl,
            "tp": position.tp,
        }
        
        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print(f"Failed to modify SL: {result.retcode}")
            return False
        
        print(f"Stop loss modified to {new_sl} for position {position.ticket}")
        return True
    
    def update_trailing_stops(self):
        """Update trailing stops based on 10% account balance risk"""
        positions = self.get_open_positions()
        
        if not positions:
            return
        
        for position in positions:
            # Calculate risk-based stop loss
            new_sl = self.calculate_risk_based_sl(position)
            
            if new_sl is None:
                continue
                
            # Only update if this would be a better stop loss (trailing)
            if position.type == mt5.ORDER_TYPE_BUY:
                # For buy positions, only move SL up (higher)
                if position.sl == 0 or new_sl > position.sl:
                    print(f"BUY Position #{position.ticket}: Old SL={position.sl:.5f}, New SL={new_sl:.5f}")
                    self.modify_position_sl(position, new_sl)
                else:
                    print(f"BUY Position #{position.ticket}: SL {position.sl:.5f} already better than calculated {new_sl:.5f}")
            
            elif position.type == mt5.ORDER_TYPE_SELL:
                # For sell positions, only move SL down (lower) 
                if position.sl == 0 or new_sl < position.sl:
                    print(f"SELL Position #{position.ticket}: Old SL={position.sl:.5f}, New SL={new_sl:.5f}")
                    self.modify_position_sl(position, new_sl)
                else:
                    print(f"SELL Position #{position.ticket}: SL {position.sl:.5f} already better than calculated {new_sl:.5f}")
    
    def run(self):
        """Main trailing stop manager loop"""
        if not self.initialize_mt5():
            return
        self.is_running = True
        print("Risk-Based Trailing Stop Manager started...")
        print(f"Managing positions for symbol: {self.symbol}")
        print(f"Risk per trade: {self.risk_percentage}% of account balance")
        print(f"Magic number filter: {'All trades' if self.magic_number == 0 else self.magic_number}")
        print("Will calculate stop loss based on risking 10% of balance!")
        try:
            while self.is_running:
                # Pause logic: check for pause.flag in working directory
                check_pause_flag(os.path.dirname(os.path.abspath(__file__)))
                # Update trailing stops for existing positions
                positions = self.get_open_positions()
                if len(positions) > 0:
                    print(f"\nManaging {len(positions)} open position(s)...")
                    self.update_trailing_stops()
                else:
                    print("No open positions to manage.")
                # Wait before next iteration
                time.sleep(3)  # Check every 3 seconds for more responsive trailing
        except KeyboardInterrupt:
            print("Trailing Stop Manager stopped by user")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the trailing stop manager and cleanup"""
        self.is_running = False
        mt5.shutdown()
        print("Trailing Stop Manager stopped and MT5 connection closed")

# Example usage and testing functions
def test_connection():
    """Test MT5 connection"""
    manager = TrailingStopManager(
        symbol="EURUSD",
        risk_percentage=10.0,
        magic_number=0,
        login=210715557,
        password="Johannes@0",
        server="Exness-MT5Trial9"
    )
    if manager.initialize_mt5():
        print("Connection test successful!")
        symbol_info = manager.get_symbol_info()
        if symbol_info:
            print(f"Symbol info: {symbol_info}")
        
        bid, ask = manager.get_current_price()
        print(f"Current prices - Bid: {bid}, Ask: {ask}")
        
        positions = manager.get_open_positions()
        print(f"Open positions: {len(positions)}")
        
        manager.stop()
    else:
        print("Connection test failed!")

def main():
    """Main function to run the Risk-Based Trailing Stop Manager"""
    # Use global configuration
    SYMBOL = "BTCUSD"
    RISK_PERCENTAGE = TRAILING_STEP_PERCENT  # From global config
    MAGIC_NUMBER = 0  # 0 = manage all trades, or specific number for EA trades only
    
    print(f"🔧 Using Global Configuration:")
    print(f"  Account: {MT5_LOGIN} on {MT5_SERVER}")
    print(f"  Risk per adjustment: {RISK_PERCENTAGE}%")
    
    # Create and run Risk-Based Trailing Stop Manager
    manager = TrailingStopManager(
        symbol=SYMBOL,
        risk_percentage=RISK_PERCENTAGE,
        magic_number=MAGIC_NUMBER
    )
    
    # Run the manager
    manager.run()

if __name__ == "__main__":
    # Uncomment the line below to test connection first
    # test_connection()
    
    # Run the main EA
    main()
