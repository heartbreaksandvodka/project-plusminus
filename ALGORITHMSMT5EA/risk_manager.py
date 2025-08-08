# Risk Management Utilities for All EAs
# Author: Johannes N. Nkosi  
# Date: July 27, 2025

"""
Centralized risk management utilities used by all Expert Advisors.
Provides percentage-based position sizing, risk calculations, and safety checks.
"""

import MetaTrader5 as mt5
from global_config import *

class RiskManager:
    """Centralized risk management for all EAs"""
    
    def __init__(self, ea_name="Unknown"):
        self.ea_name = ea_name
        self.daily_trades_count = 0
        self.daily_pnl_percent = 0.0
        self.max_risk_percent = 2.0  # Default maximum risk percentage
        
    def get_account_balance(self):
        """Get current account balance"""
        try:
            account_info = mt5.account_info()
            if account_info is None:
                return 10000.0  # Fallback default
            return account_info.balance
        except Exception as e:
            print(f"Error getting account balance: {e}")
            return 10000.0
    
    def calculate_amount_from_percent(self, percentage):
        """Calculate dollar amount from percentage of account balance"""
        balance = self.get_account_balance()
        return balance * (percentage / 100.0)
    
    def calculate_position_size(self, symbol, risk_percent=None):
        """Calculate optimal position size based on risk percentage"""
        if risk_percent is None:
            risk_percent = ACCOUNT_RISK_PERCENT
            
        try:
            # Get account info
            account_info = mt5.account_info()
            if account_info is None:
                return DEFAULT_LOT_SIZE
                
            balance = account_info.balance
            risk_amount = balance * (risk_percent / 100)
            
            # Get symbol info
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                return DEFAULT_LOT_SIZE
                
            # Calculate lot size based on risk
            if AUTO_LOT_SIZING:
                # Use tick value for calculation
                tick_value = symbol_info.trade_tick_value
                if tick_value > 0:
                    # Calculate lots needed for risk amount
                    stop_loss_points = self.calculate_amount_from_percent(DEFAULT_STOP_LOSS_PERCENT) / tick_value
                    lot_size = risk_amount / (stop_loss_points * tick_value)
                    
                    # Apply min/max limits
                    min_lot = symbol_info.volume_min
                    max_lot = symbol_info.volume_max
                    step = symbol_info.volume_step
                    
                    lot_size = max(min_lot, min(max_lot, lot_size))
                    lot_size = round(lot_size / step) * step
                    
                    return lot_size
                    
            return DEFAULT_LOT_SIZE
            
        except Exception as e:
            print(f"Error calculating position size: {e}")
            return DEFAULT_LOT_SIZE
    
    def calculate_price_levels(self, entry_price, direction, symbol, 
                             sl_percent=None, tp_percent=None):
        """Calculate SL and TP price levels from percentage risk"""
        if sl_percent is None:
            sl_percent = DEFAULT_STOP_LOSS_PERCENT
        if tp_percent is None:
            tp_percent = DEFAULT_TAKE_PROFIT_PERCENT
            
        try:
            # Get symbol info for pip calculation
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                return entry_price, entry_price
                
            balance = self.get_account_balance()
            
            # Calculate risk amounts
            sl_amount = balance * (sl_percent / 100)
            tp_amount = balance * (tp_percent / 100)
            
            # Get tick value for conversion
            tick_value = symbol_info.trade_tick_value
            lot_size = self.calculate_position_size(symbol)
            
            if tick_value > 0 and lot_size > 0:
                # Calculate pip distances
                sl_pips = sl_amount / (tick_value * lot_size)
                tp_pips = tp_amount / (tick_value * lot_size)
                
                # Convert to price distances
                point = symbol_info.point
                sl_distance = sl_pips * point
                tp_distance = tp_pips * point
                
                if direction.upper() == 'BUY':
                    sl_price = entry_price - sl_distance
                    tp_price = entry_price + tp_distance
                else:  # SELL
                    sl_price = entry_price + sl_distance
                    tp_price = entry_price - tp_distance
                    
                return sl_price, tp_price
                
            # Fallback to percentage of price
            price_sl_percent = sl_percent / 10  # Convert to price percentage
            price_tp_percent = tp_percent / 10
            
            if direction.upper() == 'BUY':
                sl_price = entry_price * (1 - price_sl_percent / 100)
                tp_price = entry_price * (1 + price_tp_percent / 100)
            else:
                sl_price = entry_price * (1 + price_sl_percent / 100)
                tp_price = entry_price * (1 - price_tp_percent / 100)
                
            return sl_price, tp_price
            
        except Exception as e:
            print(f"Error calculating price levels: {e}")
            return entry_price, entry_price
    
    def check_daily_limits(self):
        """Check if daily trading limits are reached"""
        try:
            # Check trade count limit
            if self.daily_trades_count >= MAX_DAILY_TRADES:
                return False, "Daily trade limit reached"
                
            # Check daily loss limit
            if self.daily_pnl_percent <= -DAILY_RISK_LIMIT_PERCENT:
                return False, "Daily loss limit reached"
                
            # Check if profit target reached (optional stop)
            if self.daily_pnl_percent >= DAILY_PROFIT_TARGET_PERCENT:
                return False, "Daily profit target achieved"
                
            return True, "OK"
            
        except Exception as e:
            print(f"Error checking daily limits: {e}")
            return True, "OK"
    
    def check_concurrent_positions(self, symbol, magic_number=None):
        """Check if maximum concurrent positions reached"""
        try:
            if magic_number:
                positions = mt5.positions_get(symbol=symbol, magic=magic_number)
            else:
                positions = mt5.positions_get(symbol=symbol)
                
            position_count = len(positions) if positions else 0
            
            if position_count >= MAX_CONCURRENT_POSITIONS:
                return False, f"Max concurrent positions reached ({position_count})"
                
            return True, "OK"
            
        except Exception as e:
            print(f"Error checking concurrent positions: {e}")
            return True, "OK"
    
    def update_daily_stats(self, magic_number=None):
        """Update daily trading statistics"""
        try:
            from datetime import datetime, timedelta
            
            # Get today's deals
            today = datetime.now().date()
            start_time = datetime.combine(today, datetime.min.time())
            end_time = datetime.now()
            
            deals = mt5.history_deals_get(start_time, end_time)
            
            if deals:
                # Filter by magic number if specified
                if magic_number:
                    deals = [deal for deal in deals if deal.magic == magic_number]
                
                # Count trades and calculate P&L
                self.daily_trades_count = len(deals)
                daily_profit = sum(deal.profit for deal in deals)
                
                # Convert to percentage
                balance = self.get_account_balance()
                self.daily_pnl_percent = (daily_profit / balance) * 100
                
        except Exception as e:
            print(f"Error updating daily stats: {e}")
    
    def get_risk_summary(self):
        """Get current risk summary"""
        balance = self.get_account_balance()
        
        return {
            'ea_name': self.ea_name,
            'account_balance': balance,
            'daily_trades': self.daily_trades_count,
            'daily_pnl_percent': self.daily_pnl_percent,
            'risk_per_trade_percent': ACCOUNT_RISK_PERCENT,
            'daily_limit_percent': DAILY_RISK_LIMIT_PERCENT,
            'profit_target_percent': DAILY_PROFIT_TARGET_PERCENT,
            'risk_amount_per_trade': self.calculate_amount_from_percent(ACCOUNT_RISK_PERCENT)
        }
    
    def calculate_current_risk(self, account):
        """Calculate the current risk dynamically based on the MT5 account setup."""
        try:
            # Fetch account balance
            balance = self.get_account_balance()

            # Fetch open positions for the account
            positions = mt5.positions_get()
            if positions is None:
                return 0.0  # No open positions, no risk

            # Calculate total risk from open positions
            total_risk = 0.0
            for position in positions:
                if position.symbol in account.allowed_symbols:
                    # Risk is calculated as volume * price * tick value
                    symbol_info = mt5.symbol_info(position.symbol)
                    if symbol_info:
                        tick_value = symbol_info.trade_tick_value
                        total_risk += position.volume * position.price * tick_value

            # Convert total risk to percentage of account balance
            current_risk_percent = (total_risk / balance) * 100
            return current_risk_percent

        except Exception as e:
            print(f"Error calculating current risk: {e}")
            return 0.0

# Global risk manager instance
risk_manager = RiskManager("Global")

# Convenience functions for easy import
def get_position_size(symbol, risk_percent=None):
    """Quick function to get position size"""
    return risk_manager.calculate_position_size(symbol, risk_percent)

def get_price_levels(entry_price, direction, symbol, sl_percent=None, tp_percent=None):
    """Quick function to get SL/TP levels"""
    return risk_manager.calculate_price_levels(entry_price, direction, symbol, sl_percent, tp_percent)

def check_trading_allowed(symbol, magic_number=None):
    """Quick function to check if trading is allowed"""
    # Check daily limits
    daily_ok, daily_msg = risk_manager.check_daily_limits()
    if not daily_ok:
        return False, daily_msg
        
    # Check concurrent positions
    position_ok, position_msg = risk_manager.check_concurrent_positions(symbol, magic_number)
    if not position_ok:
        return False, position_msg
        
    return True, "Trading allowed"

# Quick test
if __name__ == "__main__":
    print("🛡️  Risk Management System Loaded")
    summary = risk_manager.get_risk_summary()
    for key, value in summary.items():
        print(f"  {key}: {value}")
    print("✅ Risk manager validated successfully!")
