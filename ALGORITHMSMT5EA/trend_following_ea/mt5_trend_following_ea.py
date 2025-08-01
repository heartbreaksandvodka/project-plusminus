"""
MetaTrader 5 Trend Following Expert Advisor
Author: Johannes N. Nkosi
Date: July 25, 2025

This EA implements a long-term trend following strategy that identifies and rides
major market trends using multiple timeframe analysis and trend confirmation indicators.
"""


import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import sys
import os

# Add root directory to path for global imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from global_config import get_account_credentials, get_risk_settings
from risk_manager import RiskManager

class TrendFollowingEA:
    def __init__(self, symbol="EURUSD", lot_size=0.1, magic_number=98765,
                 primary_timeframe=mt5.TIMEFRAME_M1, secondary_timeframe=mt5.TIMEFRAME_M5,
                 login=None, password=None, server=None):
        """
        Initialize the Trend Following Expert Advisor
        
        Args:
            symbol (str): Trading symbol (default: EURUSD)
            lot_size (float): Position size in lots
            magic_number (int): Unique identifier for EA trades
            primary_timeframe: Primary timeframe for signals (M1)
            secondary_timeframe: Secondary timeframe for trend confirmation (M5)
            login (int): MT5 account login number
            password (str): MT5 account password
            server (str): MT5 server name
        """
        self.symbol = symbol
        self.magic_number = magic_number
        self.primary_timeframe = primary_timeframe
        self.secondary_timeframe = secondary_timeframe
        self.is_running = False
        
        # Account credentials
        # Get global configuration
        credentials = get_account_credentials()
        self.login = credentials['login']
        self.password = credentials['password']
        self.server = credentials['server']

        # Initialize global risk manager
        self.risk_manager = RiskManager()
        
        # Trend following parameters
        self.ema_fast = 21       # Fast EMA period
        self.ema_slow = 50       # Slow EMA period
        self.ema_filter = 200    # Long-term trend filter
        self.atr_period = 14     # ATR period for stop loss
        self.atr_multiplier = 2.5 # ATR multiplier for stop loss
        self.adx_period = 14     # ADX period for trend strength
        self.adx_threshold = 25  # Minimum ADX for trend confirmation
        
        # Position management
        self.max_positions = 1   # Maximum positions per direction
        self.trailing_enabled = True
        self.trailing_distance = 100  # Trailing stop distance in points
        
    def initialize_mt5(self):
        """Initialize connection to MetaTrader 5"""
        if not mt5.initialize():
            print("MetaTrader 5 initialization failed")
            print("Error code:", mt5.last_error())
            return False
        
        print("MetaTrader 5 initialized successfully")
        
        # Login to account if credentials provided
        if self.login and self.password and self.server:
            print(f"Attempting to login to account {self.login} on server {self.server}...")
            authorized = mt5.login(self.login, password=self.password, server=self.server)
            if not authorized:
                print("Login failed")
                print("Error code:", mt5.last_error())
                return False
            print("Login successful!")
        
        print("Terminal info:", mt5.terminal_info())
        print("Account info:", mt5.account_info())
        return True
    
    def get_symbol_info(self):
        """Get symbol information and verify it's available"""
        symbol_info = mt5.symbol_info(self.symbol)
        if symbol_info is None:
            print(f"Symbol {self.symbol} not found")
            return None
        
        # Enable symbol in Market Watch if not visible
        if not symbol_info.visible:
            print(f"Symbol {self.symbol} is not visible, trying to switch on")
            if not mt5.symbol_select(self.symbol, True):
                print(f"symbol_select({self.symbol}) failed, exit")
                return None
        
        return symbol_info
    
    def get_current_price(self):
        """Get current bid and ask prices"""
        tick = mt5.symbol_info_tick(self.symbol)
        if tick is None:
            print(f"Failed to get tick for {self.symbol}")
            return None, None
        return tick.bid, tick.ask
    
    def get_market_data(self, timeframe, num_bars=500):
        """Get historical market data for analysis"""
        rates = mt5.copy_rates_from_pos(self.symbol, timeframe, 0, num_bars)
        if rates is None:
            print(f"Failed to get market data for {self.symbol}")
            return None
        
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        return df
    
    def calculate_ema(self, data, period):
        """Calculate Exponential Moving Average"""
        return data['close'].ewm(span=period, adjust=False).mean()
    
    def calculate_atr(self, data, period=14):
        """Calculate Average True Range"""
        high_low = data['high'] - data['low']
        high_close = np.abs(data['high'] - data['close'].shift())
        low_close = np.abs(data['low'] - data['close'].shift())
        
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        atr = true_range.rolling(window=period).mean()
        return atr
    
    def calculate_adx(self, data, period=14):
        """Calculate Average Directional Index (ADX)"""
        high = data['high']
        low = data['low']
        close = data['close']
        
        # Calculate directional movement
        plus_dm = high.diff()
        minus_dm = low.diff()
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm > 0] = 0
        minus_dm = minus_dm.abs()
        
        # Calculate True Range
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        # Calculate smoothed averages
        atr = tr.rolling(window=period).mean()
        plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr)
        minus_di = 100 * (minus_dm.rolling(window=period).mean() / atr)
        
        # Calculate ADX
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(window=period).mean()
        
        return adx, plus_di, minus_di
    
    def calculate_rsi(self, data, period=14):
        """Calculate RSI indicator"""
        delta = data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def analyze_trend(self, timeframe):
        """Comprehensive trend analysis"""
        data = self.get_market_data(timeframe, 500)
        if data is None or len(data) < 250:
            return None
        
        # Calculate indicators
        ema_fast = self.calculate_ema(data, self.ema_fast)
        ema_slow = self.calculate_ema(data, self.ema_slow)
        ema_filter = self.calculate_ema(data, self.ema_filter)
        atr = self.calculate_atr(data, self.atr_period)
        adx, plus_di, minus_di = self.calculate_adx(data, self.adx_period)
        rsi = self.calculate_rsi(data)
        
        # Current values
        current_price = data['close'].iloc[-1]
        current_ema_fast = ema_fast.iloc[-1]
        current_ema_slow = ema_slow.iloc[-1]
        current_ema_filter = ema_filter.iloc[-1]
        current_atr = atr.iloc[-1]
        current_adx = adx.iloc[-1]
        current_plus_di = plus_di.iloc[-1]
        current_minus_di = minus_di.iloc[-1]
        current_rsi = rsi.iloc[-1]
        
        # Previous values for crossover detection
        prev_ema_fast = ema_fast.iloc[-2]
        prev_ema_slow = ema_slow.iloc[-2]
        
        analysis = {
            'price': current_price,
            'ema_fast': current_ema_fast,
            'ema_slow': current_ema_slow,
            'ema_filter': current_ema_filter,
            'atr': current_atr,
            'adx': current_adx,
            'plus_di': current_plus_di,
            'minus_di': current_minus_di,
            'rsi': current_rsi,
            'ema_cross_up': current_ema_fast > current_ema_slow and prev_ema_fast <= prev_ema_slow,
            'ema_cross_down': current_ema_fast < current_ema_slow and prev_ema_fast >= prev_ema_slow,
            'above_filter': current_price > current_ema_filter,
            'below_filter': current_price < current_ema_filter,
            'strong_trend': current_adx > self.adx_threshold,
            'uptrend_strength': current_plus_di > current_minus_di,
            'downtrend_strength': current_minus_di > current_plus_di
        }
        
        return analysis
    
    def generate_signal(self):
        """Generate trading signals based on multi-timeframe analysis"""
        # Primary timeframe analysis
        primary_analysis = self.analyze_trend(self.primary_timeframe)
        if primary_analysis is None:
            return None
        
        # Secondary timeframe analysis (for trend confirmation)
        secondary_analysis = self.analyze_trend(self.secondary_timeframe)
        if secondary_analysis is None:
            return None
        
        # Signal conditions
        signal = None
        
        # Long signal conditions
        if (primary_analysis['ema_cross_up'] and
            primary_analysis['above_filter'] and
            secondary_analysis['above_filter'] and
            primary_analysis['strong_trend'] and
            primary_analysis['uptrend_strength'] and
            secondary_analysis['uptrend_strength'] and
            primary_analysis['rsi'] > 50):
            signal = "BUY"
        
        # Short signal conditions
        elif (primary_analysis['ema_cross_down'] and
              primary_analysis['below_filter'] and
              secondary_analysis['below_filter'] and
              primary_analysis['strong_trend'] and
              primary_analysis['downtrend_strength'] and
              secondary_analysis['downtrend_strength'] and
              primary_analysis['rsi'] < 50):
            signal = "SELL"
        
        return {
            'signal': signal,
            'primary_analysis': primary_analysis,
            'secondary_analysis': secondary_analysis
        }
    
    def calculate_position_size(self, atr_value, account_balance, risk_percent=2.0):
        """Calculate position size using global risk manager"""
        symbol_info = self.get_symbol_info()
        if symbol_info is None:
            return 0.01  # fallback minimum lot size
        # Use ATR-based stop loss for risk manager
        bid, ask = self.get_current_price()
        entry_price = ask if bid is None else bid
        stop_loss_price = entry_price - (atr_value * self.atr_multiplier) if entry_price else None
        if stop_loss_price is None:
            return 0.01
        return self.risk_manager.calculate_position_size(
            account_balance=account_balance,
            entry_price=entry_price,
            stop_loss_price=stop_loss_price,
            symbol=self.symbol
        )
    
    def open_position(self, direction, analysis):
        """Open a new position"""
        symbol_info = self.get_symbol_info()
        if symbol_info is None:
            return False
        
        bid, ask = self.get_current_price()
        if bid is None or ask is None:
            return False
        
        # Calculate position size
        account_info = mt5.account_info()
        if account_info:
            position_size = self.calculate_position_size(
                analysis['atr'], 
                account_info.balance
            )
        else:
            position_size = 0.01
        
        point = symbol_info.point
        
        if direction == "BUY":
            price = ask
            # Stop loss based on ATR
            sl = price - (analysis['atr'] * self.atr_multiplier)
            # Take profit at 3:1 risk-reward ratio
            tp = price + (analysis['atr'] * self.atr_multiplier * 3)
            order_type = mt5.ORDER_TYPE_BUY
            
        else:  # SELL
            price = bid
            # Stop loss based on ATR
            sl = price + (analysis['atr'] * self.atr_multiplier)
            # Take profit at 3:1 risk-reward ratio
            tp = price - (analysis['atr'] * self.atr_multiplier * 3)
            order_type = mt5.ORDER_TYPE_SELL
        
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.symbol,
            "volume": position_size,
            "type": order_type,
            "price": price,
            "sl": sl,
            "tp": tp,
            "deviation": 20,
            "magic": self.magic_number,
            "comment": f"Trend Following EA - {direction}",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print(f"Failed to open {direction} position: {result.retcode}")
            return False
        
        print(f"{direction} position opened: Volume={position_size}, Price={price:.5f}, SL={sl:.5f}, TP={tp:.5f}")
        return True
    
    def get_open_positions(self):
        """Get all open positions for this EA"""
        positions = mt5.positions_get(symbol=self.symbol)
        if positions is None:
            return []
        
        # Filter positions by magic number
        ea_positions = [pos for pos in positions if pos.magic == self.magic_number]
        return ea_positions
    
    def update_trailing_stop(self, position, current_price, atr_value):
        """Update trailing stop for a position"""
        if not self.trailing_enabled:
            return False
        
        symbol_info = self.get_symbol_info()
        if symbol_info is None:
            return False
        
        point = symbol_info.point
        trailing_distance = atr_value * self.atr_multiplier
        
        new_sl = None
        
        if position.type == mt5.ORDER_TYPE_BUY:
            # For buy positions, trail stop loss upward
            new_sl = current_price - trailing_distance
            if new_sl > position.sl + (10 * point):  # Only move if significant improvement
                new_sl = round(new_sl, 5)
            else:
                return False
        
        elif position.type == mt5.ORDER_TYPE_SELL:
            # For sell positions, trail stop loss downward
            new_sl = current_price + trailing_distance
            if new_sl < position.sl - (10 * point):  # Only move if significant improvement
                new_sl = round(new_sl, 5)
            else:
                return False
        
        # Modify position
        request = {
            "action": mt5.TRADE_ACTION_SLTP,
            "symbol": position.symbol,
            "position": position.ticket,
            "sl": new_sl,
            "tp": position.tp,
        }
        
        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print(f"Failed to update trailing stop: {result.retcode}")
            return False
        
        print(f"Trailing stop updated to {new_sl:.5f} for position {position.ticket}")
        return True
    
    def manage_positions(self):
        """Manage existing positions with trailing stops"""
        positions = self.get_open_positions()
        if not positions:
            return
        
        # Get current market analysis for trailing stops
        analysis = self.analyze_trend(self.primary_timeframe)
        if analysis is None:
            return
        
        bid, ask = self.get_current_price()
        if bid is None or ask is None:
            return
        
        for position in positions:
            if position.type == mt5.ORDER_TYPE_BUY:
                current_price = bid
            else:
                current_price = ask
            
            # Update trailing stop
            self.update_trailing_stop(position, current_price, analysis['atr'])
    
    def close_position(self, position, reason="Manual close"):
        """Close a specific position"""
        bid, ask = self.get_current_price()
        if bid is None or ask is None:
            return False
        
        if position.type == mt5.ORDER_TYPE_BUY:
            price = bid
            order_type = mt5.ORDER_TYPE_SELL
        else:
            price = ask
            order_type = mt5.ORDER_TYPE_BUY
        
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.symbol,
            "volume": position.volume,
            "type": order_type,
            "position": position.ticket,
            "price": price,
            "deviation": 20,
            "magic": self.magic_number,
            "comment": f"Trend EA Close - {reason}",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print(f"Failed to close position {position.ticket}: {result.retcode}")
            return False
        
        print(f"Position {position.ticket} closed: {reason}")
        return True
    
    def close_all_positions(self):
        """Close all open positions"""
        positions = self.get_open_positions()
        closed_count = 0
        
        for position in positions:
            if self.close_position(position, "EA Stop"):
                closed_count += 1
        
        print(f"Closed {closed_count} positions")
        return closed_count
    
    def get_trend_status(self):
        """Get current trend status and analysis"""
        signal_data = self.generate_signal()
        if signal_data is None:
            return
        
        primary = signal_data['primary_analysis']
        secondary = signal_data['secondary_analysis']
        positions = self.get_open_positions()
        
        print(f"\n📊 Trend Following Status:")
        print(f"   Current Signal: {signal_data['signal'] if signal_data['signal'] else 'No signal'}")
        print(f"   Open Positions: {len(positions)}")
        
        print(f"\n📈 Primary Timeframe Analysis:")
        print(f"   Price: {primary['price']:.5f}")
        print(f"   Fast EMA: {primary['ema_fast']:.5f}")
        print(f"   Slow EMA: {primary['ema_slow']:.5f}")
        print(f"   Filter EMA: {primary['ema_filter']:.5f}")
        print(f"   ADX: {primary['adx']:.2f}")
        print(f"   RSI: {primary['rsi']:.2f}")
        print(f"   Strong Trend: {'Yes' if primary['strong_trend'] else 'No'}")
        
        print(f"\n📊 Secondary Timeframe Trend:")
        print(f"   Above Filter: {'Yes' if secondary['above_filter'] else 'No'}")
        print(f"   Trend Direction: {'Up' if secondary['uptrend_strength'] else 'Down'}")
        
        if positions:
            total_profit = sum([pos.profit for pos in positions])
            print(f"\n💰 Position Summary:")
            print(f"   Total P&L: ${total_profit:.2f}")
            
            for pos in positions:
                pos_type = "BUY" if pos.type == mt5.ORDER_TYPE_BUY else "SELL"
                print(f"   {pos_type} {pos.volume} lots at {pos.price_open:.5f}, P&L: ${pos.profit:.2f}")
    
    def run(self):
        """Main EA loop"""
        if not self.initialize_mt5():
            return
        
        self.is_running = True
        print("Trend Following EA started...")
        print("Monitoring for long-term trend signals...")
        
        try:
            iteration_count = 0
            while self.is_running:
                # Manage existing positions
                self.manage_positions()
                
                # Check for new signals
                signal_data = self.generate_signal()
                if signal_data and signal_data['signal']:
                    positions = self.get_open_positions()
                    
                    # Check if we can open new positions
                    if len(positions) < self.max_positions:
                        if signal_data['signal'] == "BUY":
                            # Check if we don't already have a buy position
                            buy_positions = [p for p in positions if p.type == mt5.ORDER_TYPE_BUY]
                            if len(buy_positions) == 0:
                                print("🚀 Strong uptrend signal detected!")
                                self.open_position("BUY", signal_data['primary_analysis'])
                        
                        elif signal_data['signal'] == "SELL":
                            # Check if we don't already have a sell position
                            sell_positions = [p for p in positions if p.type == mt5.ORDER_TYPE_SELL]
                            if len(sell_positions) == 0:
                                print("🔻 Strong downtrend signal detected!")
                                self.open_position("SELL", signal_data['primary_analysis'])
                
                # Display status every 20 iterations (for M1 timeframe = ~20 minutes)
                iteration_count += 1
                if iteration_count % 20 == 0:
                    self.get_trend_status()
                
                # Wait before next iteration (M1 timeframe = check every 1 minute)
                time.sleep(60)  # 1 minute
                
        except KeyboardInterrupt:
            print("EA stopped by user")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the EA and cleanup"""
        self.is_running = False
        
        print("\n🛑 Stopping Trend Following EA...")
        print("Do you want to:")
        print("1. Keep all positions open (recommended for trend following)")
        print("2. Close all positions")
        
        try:
            choice = input("Enter choice (1 or 2): ").strip()
            if choice == "2":
                print("Closing all positions...")
                self.close_all_positions()
                print("✅ All positions closed")
            else:
                print("✅ Positions preserved for trend continuation")
        except:
            print("✅ EA stopped - positions preserved")
        
        mt5.shutdown()
        print("EA stopped and MT5 connection closed")

# Example usage and testing functions
def test_connection():
    """Test MT5 connection"""
    ea = TrendFollowingEA()
    if ea.initialize_mt5():
        print("Connection test successful!")
        symbol_info = ea.get_symbol_info()
        if symbol_info:
            print(f"Symbol info: {symbol_info}")
        
        bid, ask = ea.get_current_price()
        print(f"Current prices - Bid: {bid}, Ask: {ask}")
        
        ea.stop()
    else:
        print("Connection test failed!")

def main():
    """Main function to run the Trend Following EA"""
    ea = TrendFollowingEA()
    ea.run()

if __name__ == "__main__":
    # Uncomment the line below to test connection first
    # test_connection()
    
    # Run the main EA
    main()
