"""
MetaTrader 5 High-Frequency Scalping Expert Advisor
Author: Johannes N. Nkosi
Date: July 26, 2025

High-frequency scalping algorithm for MetaTrader 5.

Key Features:
- Centralized configuration and risk management (global_config.py, risk_manager.py)
- Dynamic account login and percentage-based risk controls
- Advanced order flow analysis for signal generation
- Percentage-based stop loss and take profit
- Trailing stop and breakeven logic
- Daily trade and loss limits
- Robust error handling and debug logging
- Centralized position sizing via risk manager
"""

import MetaTrader5 as mt5
import pandas as pd
import numpy as np
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import threading
from collections import deque
import sys
import os
# Add root directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Import global configuration and risk management
from global_config import *
from risk_manager import RiskManager
# Import local config for EA-specific settings (optional overrides)
try:
    from config import *
except ImportError:
    print("Local config not found, using global config only")
# Import common EA utilities
from ALGORITHMSMT5EA.common_ea import initialize_mt5, get_symbol_info, get_current_price, check_pause_flag

# Setup logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('hf_scalping_ea.log'),
        logging.StreamHandler()
    ]
)

class HighFrequencyScalpingEA:
    """
    High-frequency scalping EA with advanced order flow analysis and centralized risk management.

    - Uses global configuration and risk manager for all account, symbol, and risk settings
    - All risk is managed as a percentage of account balance
    - SL/TP, trailing stop, and breakeven are calculated dynamically
    - Daily trade and loss limits enforced
    - Advanced order flow metrics for signal generation
    """
    
    def __init__(self):
        # Use global configuration with local overrides
        self.symbol = getattr(sys.modules.get('config', None), 'SYMBOL', 'BTCUSD')
        self.magic_number = getattr(sys.modules.get('config', None), 'MAGIC_NUMBER', 54321)
        self.lot_size = DEFAULT_LOT_SIZE
        self.is_running = False
        
        # Get global credentials
        credentials = get_account_credentials()
        self.login = credentials['login']
        self.password = credentials['password']
        self.server = credentials['server']
        
        # Initialize risk manager
        self.risk_manager = RiskManager(f"HFScalping_{self.symbol}")
        
        # Scalping parameters (use global config with local overrides)
        self.scalp_target_percent = getattr(sys.modules.get('config', None), 'SCALP_TARGET_PERCENT', SCALP_TARGET_PERCENT)
        self.stop_loss_percent = getattr(sys.modules.get('config', None), 'STOP_LOSS_PERCENT', DEFAULT_STOP_LOSS_PERCENT)
        self.trailing_stop_percent = getattr(sys.modules.get('config', None), 'TRAILING_STOP_PERCENT', TRAILING_STOP_PERCENT)
        self.min_spread = getattr(sys.modules.get('config', None), 'MIN_SPREAD', MIN_SPREAD_POINTS)
        self.max_spread = getattr(sys.modules.get('config', None), 'MAX_SPREAD', MAX_SPREAD_POINTS)
        
        # Breakeven settings (from global config)
        self.breakeven_trigger_percent = BREAKEVEN_TRIGGER_PERCENT
        self.enable_breakeven = ENABLE_BREAKEVEN
        
        # Order flow tracking
        self.tick_data = deque(maxlen=getattr(sys.modules.get('config', None), 'TICK_ANALYSIS_PERIOD', 20))
        self.volume_data = deque(maxlen=getattr(sys.modules.get('config', None), 'VOLUME_THRESHOLD', 100))
        self.bid_ask_data = deque(maxlen=getattr(sys.modules.get('config', None), 'BID_ASK_PRESSURE_PERIOD', 10))
        
        # Daily tracking using global limits
        self.daily_trades = 0
        self.daily_profit_percent = 0.0
        self.today = datetime.now().date()
        
        # Performance tracking
        self.total_trades = 0
        self.winning_trades = 0
        self.total_profit_percent = 0.0
        
        logging.info("High-Frequency Scalping EA initialized with global config")
        
    def initialize_mt5(self) -> bool:
        # Use shared utility
        result = initialize_mt5(self.login, self.password, self.server)
        if result:
            symbol_info = get_symbol_info(self.symbol)
            if symbol_info is None:
                logging.error(f"Symbol {self.symbol} not found")
                return False
            self.symbol_info = symbol_info
            self.point = symbol_info.point
            self.digits = symbol_info.digits
            logging.info(f"Symbol info: {self.symbol}, Point: {self.point}, Digits: {self.digits}")
            return True
        return False
            
    def get_current_prices(self) -> Optional[dict]:
        # Use shared utility
        bid, ask = get_current_price(self.symbol)
        if bid is None or ask is None:
            return None
        spread = (ask - bid) / self.point
        tick = mt5.symbol_info_tick(self.symbol)
        return {
            'time': tick.time if tick else None,
            'bid': bid,
            'ask': ask,
            'spread': spread,
            'volume': tick.volume if tick and hasattr(tick, 'volume') else 0
        }
    
    def get_account_balance(self) -> float:
        """Get current account balance"""
        try:
            account_info = mt5.account_info()
            if account_info is None:
                return 10000.0  # Default fallback
            return account_info.balance
        except Exception as e:
            logging.error(f"Error getting account balance: {e}")
            return 10000.0
    
    def calculate_percentage_amount(self, percentage: float) -> float:
        """Calculate amount based on percentage of account balance"""
        try:
            balance = self.get_account_balance()
            return balance * (percentage / 100.0)
        except Exception as e:
            logging.error(f"Error calculating percentage amount: {e}")
            return 0.0
    
    def calculate_price_from_percentage(self, percentage: float, current_price: float, position_type: str) -> float:
        """Calculate price level from percentage of account balance"""
        try:
            amount = self.calculate_percentage_amount(percentage)
            balance = self.get_account_balance()
            
            # Calculate pip value for position sizing
            lot_size = self.calculate_position_size()
            pip_value = self.symbol_info.trade_tick_value * lot_size
            
            if pip_value <= 0:
                pip_value = 1.0
            
            # Calculate pips needed for the percentage amount
            pips_needed = amount / pip_value
            price_distance = pips_needed * self.point
            
            if position_type == 'BUY':
                return current_price + price_distance  # TP above entry
            else:  # SELL
                return current_price - price_distance  # TP below entry
                
        except Exception as e:
            logging.error(f"Error calculating price from percentage: {e}")
            return current_price
            
    def analyze_order_flow(self) -> Dict:
        """Advanced order flow analysis for scalping signals"""
        try:
            # Get recent tick data
            current_tick = self.get_current_prices()
            if current_tick is None:
                return {'signal': 'NONE', 'strength': 0.0}
                
            self.tick_data.append(current_tick)
            
            if len(self.tick_data) < TICK_ANALYSIS_PERIOD:
                return {'signal': 'NONE', 'strength': 0.0}
                
            # Convert to DataFrame for analysis
            df = pd.DataFrame(list(self.tick_data))
            
            # Calculate order flow metrics
            metrics = self.calculate_flow_metrics(df)
            
            # Generate trading signal
            signal = self.generate_scalping_signal(metrics)
            
            return signal
            
        except Exception as e:
            logging.error(f"Error in order flow analysis: {e}")
            return {'signal': 'NONE', 'strength': 0.0}
            
    def calculate_flow_metrics(self, df: pd.DataFrame) -> Dict:
        """Calculate advanced order flow metrics"""
        try:
            # Price momentum
            price_change = df['bid'].iloc[-1] - df['bid'].iloc[0]
            price_momentum = price_change / self.point
            
            # Bid-Ask pressure
            bid_pressure = df['bid'].diff().sum()
            ask_pressure = df['ask'].diff().sum()
            pressure_ratio = ask_pressure / (bid_pressure + 1e-10)
            
            # Volume analysis (if available)
            if 'volume' in df.columns and df['volume'].sum() > 0:
                volume_weighted_price = (df['bid'] * df['volume']).sum() / df['volume'].sum()
                current_price = df['bid'].iloc[-1]
                volume_bias = (current_price - volume_weighted_price) / self.point
            else:
                volume_bias = 0.0
                
            # Spread analysis
            avg_spread = df['spread'].mean()
            current_spread = df['spread'].iloc[-1]
            spread_pressure = current_spread - avg_spread
            
            # Tick frequency analysis
            time_diffs = df['time'].diff().dropna()
            avg_tick_frequency = time_diffs.mean() if len(time_diffs) > 0 else 1.0
            
            return {
                'price_momentum': price_momentum,
                'pressure_ratio': pressure_ratio,
                'volume_bias': volume_bias,
                'spread_pressure': spread_pressure,
                'tick_frequency': avg_tick_frequency,
                'current_spread': current_spread
            }
            
        except Exception as e:
            logging.error(f"Error calculating flow metrics: {e}")
            return {}
            
    def generate_scalping_signal(self, metrics: Dict) -> Dict:
        """Generate scalping signal based on order flow metrics"""
        try:
            if not metrics:
                return {'signal': 'NONE', 'strength': 0.0}
                
            # Check spread condition
            if metrics['current_spread'] > self.max_spread:
                return {'signal': 'NONE', 'strength': 0.0, 'reason': 'Spread too wide'}
                
            if metrics['current_spread'] < self.min_spread:
                return {'signal': 'NONE', 'strength': 0.0, 'reason': 'Spread too narrow'}
                
            signal_strength = 0.0
            signal_direction = 'NONE'
            
            # Momentum-based signals
            if abs(metrics['price_momentum']) >= 2:  # At least 2 points movement
                if metrics['price_momentum'] > 0:
                    signal_strength += 0.3
                    signal_direction = 'BUY'
                else:
                    signal_strength += 0.3
                    signal_direction = 'SELL'
                    
            # Pressure-based signals
            if metrics['pressure_ratio'] > 1.2:  # Ask pressure dominant
                signal_strength += 0.2
                signal_direction = 'BUY' if signal_direction != 'SELL' else signal_direction
            elif metrics['pressure_ratio'] < 0.8:  # Bid pressure dominant
                signal_strength += 0.2
                signal_direction = 'SELL' if signal_direction != 'BUY' else signal_direction
                
            # Volume bias signals
            if abs(metrics['volume_bias']) >= 1:
                signal_strength += 0.2
                if metrics['volume_bias'] > 0:
                    signal_direction = 'BUY' if signal_direction != 'SELL' else signal_direction
                else:
                    signal_direction = 'SELL' if signal_direction != 'BUY' else signal_direction
                    
            # Spread pressure signals
            if metrics['spread_pressure'] < -0.5:  # Spread tightening
                signal_strength += 0.1
                
            # Minimum signal strength threshold
            if signal_strength < 0.4:
                signal_direction = 'NONE'
                
            return {
                'signal': signal_direction,
                'strength': min(signal_strength, 1.0),
                'metrics': metrics
            }
            
        except Exception as e:
            logging.error(f"Error generating scalping signal: {e}")
            return {'signal': 'NONE', 'strength': 0.0}
            
    def calculate_position_size(self, price: float, sl_price: float) -> float:
        """Calculate position size based on risk using global risk manager"""
        try:
            # Get current account balance
            account_info = mt5.account_info()
            if account_info is None:
                logging.error("Failed to get account info")
                return self.min_lot_size
                
            account_balance = account_info.balance
            
            # Use global risk manager to calculate position size
            position_size = self.risk_manager.calculate_position_size(
                account_balance=account_balance,
                entry_price=price,
                stop_loss_price=sl_price,
                symbol=self.symbol
            )
            
            # Ensure position size is within bounds
            position_size = max(self.min_lot_size, min(position_size, self.max_lot_size))
            
            # Round to lot step
            position_size = round(position_size / self.lot_step) * self.lot_step
            
            logging.info(f"Calculated position size: {position_size} for risk on balance {account_balance}")
            return position_size
        except Exception as e:
            logging.error(f"Error calculating position size: {e}")
            return self.min_lot_size

    def place_scalping_order(self, signal: str, current_prices: Dict) -> bool:
        """Place scalping order with tight stops"""
        try:
            if signal not in ['BUY', 'SELL']:
                return False
            # Check daily limits
            if self.daily_trades >= MAX_DAILY_TRADES:
                logging.info("Daily trade limit reached")
                return False
            # Check daily limits using global risk manager
            if not self.risk_manager.check_daily_limits():
                logging.info("Daily loss limit reached")
                return False
            # Check concurrent positions
            positions = mt5.positions_get(symbol=self.symbol, magic=self.magic_number)
            if positions is not None and len(positions) >= MAX_CONCURRENT_TRADES:
                logging.info("Maximum concurrent trades reached")
                return False
            # Calculate position size using centralized risk manager (percentage-based)
            lot_size = self.calculate_position_size()
            # Set up order parameters with percentage-based calculations
            if signal == 'BUY':
                order_type = mt5.ORDER_TYPE_BUY
                price = current_prices['ask']
                # Calculate SL and TP based on percentage of account balance
                tp = self.calculate_price_from_percentage(self.scalp_target_percent, price, 'BUY')
                sl = self.calculate_price_from_percentage(-self.stop_loss_percent, price, 'BUY')
            else:
                order_type = mt5.ORDER_TYPE_SELL
                price = current_prices['bid']
                # Calculate SL and TP based on percentage of account balance
                tp = self.calculate_price_from_percentage(self.scalp_target_percent, price, 'SELL')
                sl = self.calculate_price_from_percentage(-self.stop_loss_percent, price, 'SELL')
            # Create order request
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": self.symbol,
                "volume": lot_size,
                "type": order_type,
                "price": price,
                "sl": sl,
                "tp": tp,
                "deviation": SLIPPAGE,
                "magic": self.magic_number,
                "comment": f"HF_Scalp_{signal}",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            # Send order
            result = mt5.order_send(request)
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                logging.warning(f"Order failed: {result.retcode} - {result.comment}")
                return False
            self.daily_trades += 1
            self.total_trades += 1
            logging.info(f"Scalping order placed: {signal} {lot_size} lots at {price}")
            logging.info(f"SL: {sl}, TP: {tp}, Spread: {current_prices['spread']}")
            return True
        except Exception as e:
            logging.error(f"Error placing scalping order: {e}")
            return False
            
    def manage_positions(self):
        """Manage open positions with trailing stops"""
        try:
            positions = mt5.positions_get(symbol=self.symbol, magic=self.magic_number)
            
            if positions is not None:
                for position in positions:
                    self.apply_trailing_stop(position)
                
        except Exception as e:
            logging.error(f"Error managing positions: {e}")
            
    def apply_trailing_stop(self, position):
        """Apply trailing stop and breakeven logic to position"""
        try:
            current_prices = self.get_current_prices()
            if current_prices is None:
                return
                
            symbol = position.symbol
            ticket = position.ticket
            position_type = position.type
            open_price = position.price_open
            current_sl = position.sl
            
            if position_type == mt5.POSITION_TYPE_BUY:
                # Calculate current profit in percentage of account balance
                balance = self.get_account_balance()
                lot_size = position.volume
                pip_value = self.symbol_info.trade_tick_value * lot_size
                current_profit_pips = (current_prices['bid'] - open_price) / self.point
                current_profit_amount = current_profit_pips * pip_value
                current_profit_percent = (current_profit_amount / balance) * 100
                
                # Check for breakeven move (when profit reaches breakeven trigger percentage)
                if (hasattr(self, 'breakeven_trigger_percent') and 
                    current_profit_percent >= self.breakeven_trigger_percent and 
                    current_sl < open_price):
                    # Move SL to entry (breakeven)
                    new_sl = open_price
                    self.modify_position(ticket, new_sl, position.tp)
                    logging.info(f"BUY position {ticket} moved to breakeven at {new_sl} (Profit: {current_profit_percent:.2f}%)")
                    return
                
                # Apply percentage-based trailing stop
                trailing_amount = self.calculate_percentage_amount(self.trailing_stop_percent)
                trailing_pips = trailing_amount / pip_value if pip_value > 0 else 1
                new_sl = current_prices['bid'] - (trailing_pips * self.point)
                if new_sl > current_sl + (self.point * 0.5):  # Only move if significant
                    self.modify_position(ticket, new_sl, position.tp)
                    
            elif position_type == mt5.POSITION_TYPE_SELL:
                # Calculate current profit in percentage of account balance
                balance = self.get_account_balance()
                lot_size = position.volume
                pip_value = self.symbol_info.trade_tick_value * lot_size
                current_profit_pips = (open_price - current_prices['ask']) / self.point
                current_profit_amount = current_profit_pips * pip_value
                current_profit_percent = (current_profit_amount / balance) * 100
                
                # Check for breakeven move (when profit reaches breakeven trigger percentage)
                if (hasattr(self, 'breakeven_trigger_percent') and 
                    current_profit_percent >= self.breakeven_trigger_percent and 
                    current_sl > open_price):
                    # Move SL to entry (breakeven)
                    new_sl = open_price
                    self.modify_position(ticket, new_sl, position.tp)
                    logging.info(f"SELL position {ticket} moved to breakeven at {new_sl} (Profit: {current_profit_percent:.2f}%)")
                    return
                
                # Apply percentage-based trailing stop
                trailing_amount = self.calculate_percentage_amount(self.trailing_stop_percent)
                trailing_pips = trailing_amount / pip_value if pip_value > 0 else 1
                new_sl = current_prices['ask'] + (trailing_pips * self.point)
                if new_sl < current_sl - (self.point * 0.5):  # Only move if significant
                    self.modify_position(ticket, new_sl, position.tp)
                    
        except Exception as e:
            logging.error(f"Error applying trailing stop: {e}")
            
    def modify_position(self, ticket: int, sl: float, tp: float):
        """Modify position stop loss and take profit"""
        try:
            request = {
                "action": mt5.TRADE_ACTION_SLTP,
                "symbol": self.symbol,
                "position": ticket,
                "sl": sl,
                "tp": tp
            }
            
            result = mt5.order_send(request)
            if result.retcode == mt5.TRADE_RETCODE_DONE:
                logging.debug(f"Position {ticket} modified - SL: {sl}, TP: {tp}")
            else:
                logging.warning(f"Failed to modify position {ticket}: {result.comment}")
                
        except Exception as e:
            logging.error(f"Error modifying position: {e}")
            
    def is_trading_time(self) -> bool:
        """Check if current time is within trading hours"""
        try:
            current_time = datetime.now()
            current_hour = current_time.hour
            
            # Check trading hours
            if current_hour < START_HOUR or current_hour >= END_HOUR:
                return False
                
            # Avoid weekends
            if current_time.weekday() >= 5:  # Saturday = 5, Sunday = 6
                return False
                
            return True
            
        except Exception as e:
            logging.error(f"Error checking trading time: {e}")
            return False
            
    def update_daily_stats(self):
        """Update daily trading statistics (percentage-based)"""
        try:
            current_date = datetime.now().date()
            balance = self.get_account_balance()
            
            # Reset daily counters if new day
            if current_date != self.today:
                logging.info(f"New trading day - Daily trades: {self.daily_trades}, Daily P&L: {self.daily_profit_percent:.2f}%")
                self.daily_trades = 0
                self.daily_profit_percent = 0.0
                self.today = current_date
                
            # Calculate current daily profit as percentage
            deals = mt5.history_deals_get(
                datetime.combine(self.today, datetime.min.time()),
                datetime.now(),
                group="*"
            )
            
            if deals and balance > 0:
                daily_profit_amount = sum(deal.profit for deal in deals if deal.magic == self.magic_number)
                self.daily_profit_percent = (daily_profit_amount / balance) * 100
                
        except Exception as e:
            logging.error(f"Error updating daily stats: {e}")
            
    def get_performance_stats(self) -> Dict:
        """Get current performance statistics (percentage-based)"""
        try:
            account_info = mt5.account_info()
            if account_info is None:
                return {}
                
            win_rate = (self.winning_trades / max(self.total_trades, 1)) * 100
            
            return {
                'total_trades': self.total_trades,
                'daily_trades': self.daily_trades,
                'daily_profit_percent': self.daily_profit_percent,
                'total_profit_percent': self.total_profit_percent,
                'win_rate': win_rate,
                'account_balance': account_info.balance,
                'account_equity': account_info.equity
            }
            
        except Exception as e:
            logging.error(f"Error getting performance stats: {e}")
            return {}
            
    def run(self):
        """Main trading loop for high-frequency scalping"""
        try:
            if not self.initialize_mt5():
                logging.error("Failed to initialize MT5")
                return
            logging.info("Starting High-Frequency Scalping EA")
            self.is_running = True
            while self.is_running:
                # Pause logic: check for pause.flag in working directory
                check_pause_flag(os.path.dirname(os.path.abspath(__file__)))
                try:
                    # Check if it's trading time
                    if not self.is_trading_time():
                        time.sleep(60)  # Check every minute during off hours
                        continue
                    # Update daily statistics
                    self.update_daily_stats()
                    # Check daily limits
                    if self.daily_trades >= MAX_DAILY_TRADES:
                        logging.info("Daily trade limit reached, waiting...")
                        time.sleep(300)  # Wait 5 minutes
                        continue
                    # Check daily limits using global risk manager  
                    if not self.risk_manager.check_daily_limits():
                        logging.info("Daily loss limit reached, stopping trading")
                        break
                    # Manage existing positions
                    self.manage_positions()
                    # Analyze market for new opportunities
                    signal_data = self.analyze_order_flow()
                    if signal_data['signal'] in ['BUY', 'SELL'] and signal_data['strength'] >= 0.6:
                        current_prices = self.get_current_prices()
                        if current_prices:
                            success = self.place_scalping_order(signal_data['signal'], current_prices)
                            if success:
                                logging.info(f"Signal executed: {signal_data['signal']} (Strength: {signal_data['strength']:.2f})")
                    # Log performance every 100 trades
                    if self.total_trades > 0 and self.total_trades % 100 == 0:
                        stats = self.get_performance_stats()
                        logging.info(f"Performance Update: {stats}")
                    # Short sleep for high-frequency operation
                    time.sleep(UPDATE_INTERVAL)
                except KeyboardInterrupt:
                    logging.info("Received stop signal")
                    break
                except Exception as e:
                    logging.error(f"Error in main loop: {e}")
                    if RESTART_ON_ERROR:
                        time.sleep(5)
                        continue
                    else:
                        break
        except Exception as e:
            logging.error(f"Fatal error in EA: {e}")
        finally:
            self.is_running = False
            mt5.shutdown()
            logging.info("High-Frequency Scalping EA stopped")
            
    def stop(self):
        """Stop the EA"""
        self.is_running = False
        logging.info("Stop signal sent to EA")

def main():
    """Main function to run the High-Frequency Scalping EA"""
    ea = HighFrequencyScalpingEA()
    
    try:
        ea.run()
    except KeyboardInterrupt:
        logging.info("Keyboard interrupt received")
    finally:
        ea.stop()

if __name__ == "__main__":
    print("🚀 High-Frequency Scalping EA Starting...")
    print("📊 Percentage-based risk management: 3% per trade")
    print("⚠️  Press Ctrl+C to stop the EA")
    print()
    main()
