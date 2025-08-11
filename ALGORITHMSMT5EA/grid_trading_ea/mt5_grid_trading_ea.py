"""
MetaTrader 5 Grid Trading Expert Advisor
Author: Johannes N. Nkosi
Date: July 25, 2025

This EA implements a grid trading strategy that profits from market volatility
by placing buy and sell orders at regular intervals above and below current price.
"""

import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from datetime import datetime
import time
import sys
import os
# Add root directory to path for global imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from global_config import get_account_credentials, get_risk_settings
from risk_manager import RiskManager
# Import common EA utilities
from ALGORITHMSMT5EA.common_ea import initialize_mt5, get_symbol_info, get_current_price, check_pause_flag

class GridTradingEA:
    def __init__(self, symbol="EURUSD", grid_distance=50, 
                 max_levels=5, magic_number=54321,
                 max_loss_usd=100, trail_profit_start_usd=100, trail_profit_step_usd=50,
                 max_orders=10):
        """
        Initialize the Grid Trading Expert Advisor
        
        Args:
            symbol (str): Trading symbol (default: EURUSD)
            grid_distance (int): Distance between grid levels in points
            max_levels (int): Maximum number of grid levels above/below price
            magic_number (int): Unique identifier for EA trades
            max_loss_usd (float): Maximum allowed floating loss before closing all positions
            trail_profit_start_usd (float): Start trailing profit when floating profit exceeds this
            trail_profit_step_usd (float): Trail profit by this amount
            max_orders (int): Maximum number of open grid orders (pending + positions)
        """
        self.symbol = symbol
        self.grid_distance = grid_distance
        self.max_levels = max_levels
        self.magic_number = magic_number
        self.max_loss_usd = max_loss_usd
        self.trail_profit_start_usd = trail_profit_start_usd
        self.trail_profit_step_usd = trail_profit_step_usd
        self.trail_profit_max = None  # For trailing logic
        self.max_orders = max_orders
        self.is_running = False
        
        # Get global configuration
        credentials = get_account_credentials()
        self.login = credentials['login']
        self.password = credentials['password']
        self.server = credentials['server']
        
        # Initialize global risk manager
        self.risk_manager = RiskManager()
        
        # Grid tracking
        self.buy_orders = {}  # Track buy orders by price level
        self.sell_orders = {}  # Track sell orders by price level
        self.base_price = None  # Reference price for grid
        
    def initialize_mt5(self):
        # Use shared utility
        return initialize_mt5(self.login, self.password, self.server)
    
    def get_symbol_info(self):
        # Use shared utility
        return get_symbol_info(self.symbol)
    
    def get_current_price(self):
        # Use shared utility
        return get_current_price(self.symbol)
    
    def calculate_grid_levels(self, current_price, point):
        """Calculate grid levels above and below current price"""
        buy_levels = []  # Levels below current price (buy cheaper)
        sell_levels = []  # Levels above current price (sell higher)
        
        for i in range(1, self.max_levels + 1):
            # Buy levels (below current price)
            buy_price = current_price - (i * self.grid_distance * point)
            buy_levels.append(round(buy_price, 5))
            
            # Sell levels (above current price)
            sell_price = current_price + (i * self.grid_distance * point)
            sell_levels.append(round(sell_price, 5))
        
        return buy_levels, sell_levels
    
    def place_pending_order(self, order_type, price, tp=None):
        """Place a pending order using global risk manager for lot size (no per-order SL)"""
        symbol_info = self.get_symbol_info()
        if symbol_info is None:
            return False

        # Determine order type and price
        if order_type == "BUY_LIMIT":
            action_type = mt5.ORDER_TYPE_BUY_LIMIT
        elif order_type == "SELL_LIMIT":
            action_type = mt5.ORDER_TYPE_SELL_LIMIT
        else:
            print(f"Invalid order type: {order_type}")
            return False

        # Use risk manager to calculate lot size (position size)
        lot_size = self.risk_manager.calculate_position_size(self.symbol)
        print(f"[Order Debug] Attempting {order_type} at {price} | lot_size={lot_size} | tp={tp} | type={action_type}")
        symbol_info = self.get_symbol_info()
        if symbol_info:
            print(f"[Order Debug] Symbol info: min_lot={symbol_info.volume_min}, max_lot={symbol_info.volume_max}, step={symbol_info.volume_step}, point={symbol_info.point}, trade_tick_value={symbol_info.trade_tick_value}")

        # Build a safe comment (max 31 chars, ASCII only)
        comment_raw = f"Grid {order_type} {price:.2f}"
        comment = comment_raw[:31]
        comment = ''.join([c if ord(c) < 128 else '_' for c in comment])

        request = {
            "action": mt5.TRADE_ACTION_PENDING,
            "symbol": self.symbol,
            "volume": lot_size,
            "type": action_type,
            "price": price,
            "deviation": 20,
            "magic": self.magic_number,
            "comment": comment,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_RETURN,  # Use RETURN for pending orders
        }
        if tp is not None:
            request["tp"] = tp

        print(f"[Order Debug] Request: {request}")
        result = mt5.order_send(request)
        if result is None:
            print(f"Order send failed for {order_type} at {price}: No result returned")
            print(f"[Order Debug] mt5.last_error(): {mt5.last_error()}")
            return False
        print(f"[Order Debug] Result: retcode={getattr(result, 'retcode', None)}, comment={getattr(result, 'comment', None)}, request_id={getattr(result, 'request_id', None)}")
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print(f"Failed to place {order_type} order at {price}: {result.retcode} | comment: {getattr(result, 'comment', None)}")
            return False
        print(f"{order_type} order placed at {price}: {result.order}")
        return result.order
    def check_global_risk(self):
        """Check global floating P&L for stop loss or trailing take profit"""
        positions = self.get_existing_positions()
        if not positions:
            self.trail_profit_max = None
            return

        total_profit = sum([pos.profit for pos in positions])

        # Global stop loss
        if total_profit <= -abs(self.max_loss_usd):
            print(f"\n🛑 Max loss reached (${total_profit:.2f} <= -${self.max_loss_usd:.2f}), closing all positions and cancelling orders!")
            self.close_all_positions()
            self.cancel_all_orders()
            self.is_running = False
            return

        # Trailing take profit
        if total_profit >= self.trail_profit_start_usd:
            if self.trail_profit_max is None or total_profit > self.trail_profit_max:
                self.trail_profit_max = total_profit
            # If profit falls back by trail_profit_step_usd from max, close all
            if self.trail_profit_max - total_profit >= self.trail_profit_step_usd:
                print(f"\n🏁 Trailing take profit hit! Max profit: ${self.trail_profit_max:.2f}, current: ${total_profit:.2f}. Closing all positions and cancelling orders!")
                self.close_all_positions()
                self.cancel_all_orders()
                self.is_running = False
                return
    
    def get_existing_orders(self):
        """Get all existing pending orders for this EA"""
        orders = mt5.orders_get(symbol=self.symbol)
        if orders is None:
            return []
        
        # Filter orders by magic number
        ea_orders = [order for order in orders if order.magic == self.magic_number]
        return ea_orders
    
    def get_existing_positions(self):
        """Get all existing positions for this EA"""
        positions = mt5.positions_get(symbol=self.symbol)
        if positions is None:
            return []
        
        # Filter positions by magic number
        ea_positions = [pos for pos in positions if pos.magic == self.magic_number]
        return ea_positions
    
    def setup_initial_grid(self):
        """Set up the initial grid of pending orders"""
        bid, ask = self.get_current_price()
        if bid is None or ask is None:
            return False
        
        symbol_info = self.get_symbol_info()
        if symbol_info is None:
            return False
        
        # Use mid price as base
        self.base_price = (bid + ask) / 2
        point = symbol_info.point
        
        # Calculate grid levels
        buy_levels, sell_levels = self.calculate_grid_levels(self.base_price, point)
        
        print(f"Setting up grid around base price: {self.base_price}")
        print(f"Buy levels: {buy_levels}")
        print(f"Sell levels: {sell_levels}")
        
        # Count current orders (pending + open positions)
        current_orders = self.get_existing_orders()
        current_positions = self.get_existing_positions()
        total_active = len(current_orders) + len(current_positions)

        # Place buy limit orders (below current price)
        for price in buy_levels:
            if total_active >= self.max_orders:
                print(f"[Grid] Max orders ({self.max_orders}) reached, not placing more pending orders.")
                break
            tp = price + (self.grid_distance * point)
            order_id = self.place_pending_order("BUY_LIMIT", price, tp=tp)
            if order_id:
                self.buy_orders[price] = order_id
                total_active += 1

        # Place sell limit orders (above current price)
        for price in sell_levels:
            if total_active >= self.max_orders:
                print(f"[Grid] Max orders ({self.max_orders}) reached, not placing more pending orders.")
                break
            tp = price - (self.grid_distance * point)
            order_id = self.place_pending_order("SELL_LIMIT", price, tp=tp)
            if order_id:
                self.sell_orders[price] = order_id
                total_active += 1
        
        return True
    
    def manage_grid(self):
        """Manage the grid - replace filled orders and adjust levels"""
        current_orders = self.get_existing_orders()
        current_positions = self.get_existing_positions()
        
        # Track current order prices
        current_buy_prices = set()
        current_sell_prices = set()
        
        for order in current_orders:
            if order.type == mt5.ORDER_TYPE_BUY_LIMIT:
                current_buy_prices.add(order.price_open)
            elif order.type == mt5.ORDER_TYPE_SELL_LIMIT:
                current_sell_prices.add(order.price_open)
        
        # Check for filled orders and replace them
        bid, ask = self.get_current_price()
        if bid is None or ask is None:
            return
        
        symbol_info = self.get_symbol_info()
        if symbol_info is None:
            return
        
        point = symbol_info.point
        current_price = (bid + ask) / 2
        
        # Recalculate grid levels based on current price
        buy_levels, sell_levels = self.calculate_grid_levels(current_price, point)
        
        # Count current orders (pending + open positions)
        total_active = len(current_orders) + len(current_positions)

        # Replace missing buy orders
        for price in buy_levels:
            if total_active >= self.max_orders:
                print(f"[Grid] Max orders ({self.max_orders}) reached, not placing more pending orders.")
                break
            if price not in current_buy_prices and price < current_price:
                tp = price + (self.grid_distance * point)
                order_id = self.place_pending_order("BUY_LIMIT", price, tp=tp)
                if order_id:
                    self.buy_orders[price] = order_id
                    total_active += 1

        # Replace missing sell orders
        for price in sell_levels:
            if total_active >= self.max_orders:
                print(f"[Grid] Max orders ({self.max_orders}) reached, not placing more pending orders.")
                break
            if price not in current_sell_prices and price > current_price:
                tp = price - (self.grid_distance * point)
                order_id = self.place_pending_order("SELL_LIMIT", price, tp=tp)
                if order_id:
                    self.sell_orders[price] = order_id
                    total_active += 1
    
    def close_all_positions(self):
        """Close all open positions"""
        positions = self.get_existing_positions()
        
        for position in positions:
            bid, ask = self.get_current_price()
            if bid is None or ask is None:
                continue
            
            # Determine close price based on position type
            close_price = bid if position.type == mt5.ORDER_TYPE_BUY else ask
            
            close_request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": self.symbol,
                "volume": position.volume,
                "type": mt5.ORDER_TYPE_SELL if position.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY,
                "position": position.ticket,
                "price": close_price,
                "deviation": 20,
                "magic": self.magic_number,
                "comment": "Grid EA Close",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            result = mt5.order_send(close_request)
            if result.retcode == mt5.TRADE_RETCODE_DONE:
                print(f"Position {position.ticket} closed successfully")
            else:
                print(f"Failed to close position {position.ticket}: {result.retcode}")
    
    def cancel_all_orders(self):
        """Cancel all pending orders"""
        orders = self.get_existing_orders()
        
        for order in orders:
            request = {
                "action": mt5.TRADE_ACTION_REMOVE,
                "order": order.ticket,
            }
            
            result = mt5.order_send(request)
            if result.retcode == mt5.TRADE_RETCODE_DONE:
                print(f"Order {order.ticket} cancelled successfully")
            else:
                print(f"Failed to cancel order {order.ticket}: {result.retcode}")
    
    def get_grid_status(self):
        """Get current grid status"""
        orders = self.get_existing_orders()
        positions = self.get_existing_positions()
        
        print(f"\n📊 Grid Status:")
        print(f"   Active Orders: {len(orders)}")
        print(f"   Open Positions: {len(positions)}")
        
        if positions:
            total_profit = sum([pos.profit for pos in positions])
            print(f"   Total Floating P&L: ${total_profit:.2f}")
        
        # Show order distribution
        buy_orders = [o for o in orders if o.type == mt5.ORDER_TYPE_BUY_LIMIT]
        sell_orders = [o for o in orders if o.type == mt5.ORDER_TYPE_SELL_LIMIT]
        
        print(f"   Buy Orders: {len(buy_orders)}")
        print(f"   Sell Orders: {len(sell_orders)}")
    
    def run(self):
        """Main EA loop"""
        if not self.initialize_mt5():
            return
        print("Grid Trading EA started...")
        # Set up initial grid
        if not self.setup_initial_grid():
            print("Failed to setup initial grid")
            return
        self.is_running = True
        try:
            while self.is_running:
                # Pause logic: check for pause.flag in working directory
                check_pause_flag(os.path.dirname(os.path.abspath(__file__)))
                # Manage grid (replace filled orders)
                self.manage_grid()
                # Check global risk (accumulative SL/TP)
                self.check_global_risk()
                if not self.is_running:
                    break
                # Display status every 10 iterations (50 seconds)
                if hasattr(self, 'iteration_count'):
                    self.iteration_count += 1
                else:
                    self.iteration_count = 0
                if self.iteration_count % 10 == 0:
                    self.get_grid_status()
                # Wait before next iteration
                time.sleep(60)  # Check every 1 minute for grid updates
        except KeyboardInterrupt:
            print("EA stopped by user")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the EA and cleanup"""
        self.is_running = False
        
        # Ask user if they want to close positions and cancel orders
        print("\n🛑 Stopping Grid EA...")
        print("Do you want to:")
        print("1. Keep all positions and orders (recommended)")
        print("2. Close all positions and cancel orders")
        
        try:
            choice = input("Enter choice (1 or 2): ").strip()
            if choice == "2":
                print("Closing all positions and cancelling orders...")
                self.close_all_positions()
                self.cancel_all_orders()
                print("✅ All positions closed and orders cancelled")
            else:
                print("✅ Positions and orders preserved")
        except:
            print("✅ EA stopped - positions and orders preserved")
        
        mt5.shutdown()
        print("EA stopped and MT5 connection closed")

# Example usage and testing functions
def test_connection():
    """Test MT5 connection"""
    ea = GridTradingEA()
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
    """Main function to run the Grid EA"""
    ea = GridTradingEA(symbol="ETHUSD", grid_distance=500, max_loss_usd=100, trail_profit_start_usd=100, trail_profit_step_usd=50, max_orders=10)
    ea.run()

if __name__ == "__main__":
    # Uncomment the line below to test connection first
    # test_connection()
    
    # Run the main EA
    main()
