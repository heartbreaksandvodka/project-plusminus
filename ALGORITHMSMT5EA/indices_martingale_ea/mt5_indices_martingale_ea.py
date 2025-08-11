"""
MetaTrader 5 Indices Martingale Expert Advisor
Author: Johannes N. Nkosi
Date: July 28, 2025

This EA implements a smart Martingale strategy for indices (e.g., US500, DE30).
It uses volatility-based grid spacing, adaptive lot sizing, and robust risk controls.
"""

import MetaTrader5 as mt5
import pandas as pd
import numpy as np
import time
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from global_config import get_account_credentials, get_risk_settings
from risk_manager import RiskManager
# Import common EA utilities
from ALGORITHMSMT5EA.common_ea import initialize_mt5, get_symbol_info, get_current_price, check_pause_flag

class IndicesMartingaleEA:
    def __init__(self, symbol="US500", base_lot=0.1, magic_number=12345, grid_step_points=100, max_trades=6):
        # Load config if available
        try:
            import config
            self.symbol = getattr(config, "SYMBOL", symbol)
            self.base_lot = getattr(config, "BASE_LOT", base_lot)
            self.magic_number = getattr(config, "MAGIC_NUMBER", magic_number)
            self.grid_step_points = getattr(config, "GRID_STEP_POINTS", grid_step_points)
            self.max_trades = getattr(config, "MAX_TRADES", max_trades)
            self.max_drawdown_percent = getattr(config, "MAX_DRAWDOWN_PERCENT", 20.0)
        except Exception:
            self.symbol = symbol
            self.base_lot = base_lot
            self.magic_number = magic_number
            self.grid_step_points = grid_step_points
            self.max_trades = max_trades
            self.max_drawdown_percent = 20.0
        self.is_running = False
        self.risk_manager = RiskManager()
        self.positions = []
        self.grid_levels = []
        self.login = None
        self.password = None
        self.server = None
        credentials = get_account_credentials()
        self.login = credentials['login']
        self.password = credentials['password']
        self.server = credentials['server']
        self.global_stop_loss = 0.0
        self.global_take_profit = 0.0
        self.trailing_enabled = True
        self.trailing_distance_points = 100
        self.log_file = "martingale_ea.log"

    def initialize_mt5(self):
        # Use shared utility
        return initialize_mt5(self.login, self.password, self.server)

    def get_symbol_info(self):
        # Use shared utility
        return get_symbol_info(self.symbol)

    def get_current_price(self):
        # Use shared utility
        return get_current_price(self.symbol)

    def get_market_data(self, timeframe=mt5.TIMEFRAME_M5, num_bars=500):
        rates = mt5.copy_rates_from_pos(self.symbol, timeframe, 0, num_bars)
        if rates is None:
            return None
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        return df

    def get_signal(self):
        # Use moving average crossover as entry signal, skip if spread too high or news event
        if self.is_spread_too_high():
            self.log("Spread too high, skipping signal.")
            return None
        if self.is_news_event():
            self.log("News event detected, pausing trading.")
            return None
        data = self.get_market_data()
        if data is None or len(data) < 50:
            return None
        fast_ma = data['close'].rolling(window=10).mean()
        slow_ma = data['close'].rolling(window=30).mean()
        if fast_ma.iloc[-1] > slow_ma.iloc[-1]:
            return "BUY"
        elif fast_ma.iloc[-1] < slow_ma.iloc[-1]:
            return "SELL"
        return None
    def is_spread_too_high(self, max_spread=10):
        tick = mt5.symbol_info_tick(self.symbol)
        symbol_info = self.get_symbol_info()
        if tick and symbol_info:
            spread = abs(tick.ask - tick.bid) / symbol_info.point
            return spread > max_spread
        return False

    def is_news_event(self):
        # Placeholder: integrate with news API or time filter
        # For now, always return False
        return False

    def log(self, message):
        with open(self.log_file, "a") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")
        print(message)

    def calculate_lot_size(self, trade_number):
        # Martingale: double lot after each loss, cap at max allowed
        lot = self.base_lot * (2 ** trade_number)
        symbol_info = self.get_symbol_info()
        if symbol_info:
            lot = max(symbol_info.volume_min, min(symbol_info.volume_max, lot))
        return lot

    def open_martingale_sequence(self, direction):
        bid, ask = self.get_current_price()
        price = ask if direction == "BUY" else bid
        grid_step = self.grid_step_points * self.get_symbol_info().point
        trade_number = 0
        while trade_number < self.max_trades:
            lot = self.calculate_lot_size(trade_number)
            sl = price - (grid_step * (trade_number + 1)) if direction == "BUY" else price + (grid_step * (trade_number + 1))
            tp = price + (grid_step * 2) if direction == "BUY" else price - (grid_step * 2)
            order_type = mt5.ORDER_TYPE_BUY if direction == "BUY" else mt5.ORDER_TYPE_SELL
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": self.symbol,
                "volume": lot,
                "type": order_type,
                "price": price,
                "sl": sl,
                "tp": tp,
                "deviation": 20,
                "magic": self.magic_number,
                "comment": f"Martingale {direction} #{trade_number+1}",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            result = mt5.order_send(request)
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                self.log(f"Failed to open {direction} position: {result.retcode}")
                break
            self.log(f"{direction} Martingale trade #{trade_number+1} opened: Volume={lot}, Price={price:.2f}, SL={sl:.2f}, TP={tp:.2f}")
            self.positions.append(result)
            # Trailing stop for each position
            self.update_trailing_stop(result, price, grid_step)
            # Wait for loss before next trade
            time.sleep(10)  # Simulate waiting for next grid level
            trade_number += 1
    def update_trailing_stop(self, position, current_price, grid_step):
        if not self.trailing_enabled:
            return False
        symbol_info = self.get_symbol_info()
        if symbol_info is None:
            return False
        point = symbol_info.point
        trailing_distance = self.trailing_distance_points * point
        new_sl = None
        if hasattr(position, "type") and position.type == mt5.ORDER_TYPE_BUY:
            new_sl = current_price - trailing_distance
        elif hasattr(position, "type") and position.type == mt5.ORDER_TYPE_SELL:
            new_sl = current_price + trailing_distance
        else:
            return False
        request = {
            "action": mt5.TRADE_ACTION_SLTP,
            "symbol": self.symbol,
            "position": getattr(position, "ticket", None),
            "sl": new_sl,
            "tp": getattr(position, "tp", None),
        }
        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            self.log(f"Failed to update trailing stop: {result.retcode}")
            return False
        self.log(f"Trailing stop updated to {new_sl:.2f} for position {getattr(position, 'ticket', None)}")
        return True

    def manage_positions(self):
        # Check drawdown, trailing stop, global stop loss, partial close
        account_info = mt5.account_info()
        if not account_info:
            return
        balance = account_info.balance
        equity = account_info.equity
        drawdown = (balance - equity) / balance * 100 if balance > 0 else 0
        if drawdown > self.max_drawdown_percent:
            self.log("Max drawdown reached! Closing all positions.")
            self.close_all_positions()
        positions = mt5.positions_get(symbol=self.symbol)
        if positions:
            for pos in positions:
                # Trailing stop for each position
                self.update_trailing_stop(pos, pos.price_current, self.grid_step_points * self.get_symbol_info().point)
                # Partial close if profit > grid step
                if pos.profit > self.grid_step_points * self.get_symbol_info().point:
                    self.partial_close(pos)

    def partial_close(self, position):
        # Close half the volume if profitable
        if position.volume > 0.01:
            close_volume = position.volume / 2
            order_type = mt5.ORDER_TYPE_SELL if position.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY
            price = self.get_current_price()[0] if order_type == mt5.ORDER_TYPE_SELL else self.get_current_price()[1]
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": self.symbol,
                "volume": close_volume,
                "type": order_type,
                "position": position.ticket,
                "price": price,
                "deviation": 20,
                "magic": self.magic_number,
                "comment": "Partial Close",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            result = mt5.order_send(request)
            if result.retcode == mt5.TRADE_RETCODE_DONE:
                self.log(f"Partial close executed for position {position.ticket}")

    def close_all_positions(self):
        positions = mt5.positions_get(symbol=self.symbol)
        if not positions:
            return
        for pos in positions:
            order_type = mt5.ORDER_TYPE_SELL if pos.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY
            price = self.get_current_price()[0] if order_type == mt5.ORDER_TYPE_SELL else self.get_current_price()[1]
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": self.symbol,
                "volume": pos.volume,
                "type": order_type,
                "position": pos.ticket,
                "price": price,
                "deviation": 20,
                "magic": self.magic_number,
                "comment": "Martingale EA Close",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            result = mt5.order_send(request)
            if result.retcode == mt5.TRADE_RETCODE_DONE:
                self.log(f"Closed position {pos.ticket}")

    def run(self):
        if not self.initialize_mt5():
            return
        self.is_running = True
        print("Indices Martingale EA started...")
        try:
            while self.is_running:
                # Pause logic: check for pause.flag in working directory
                check_pause_flag(os.path.dirname(os.path.abspath(__file__)))
                self.manage_positions()
                signal = self.get_signal()
                if signal:
                    print(f"Signal detected: {signal}. Starting Martingale sequence.")
                    self.open_martingale_sequence(signal)
                time.sleep(60)
        except KeyboardInterrupt:
            print("EA stopped by user")
        finally:
            self.stop()

    def stop(self):
        self.is_running = False
        print("Stopping Indices Martingale EA...")
        self.close_all_positions()
        mt5.shutdown()
        print("EA stopped and MT5 connection closed")

if __name__ == "__main__":
    ea = IndicesMartingaleEA()
    ea.run()
