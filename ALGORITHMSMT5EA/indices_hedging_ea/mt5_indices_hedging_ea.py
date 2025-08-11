"""
MetaTrader 5 Indices Smart Hedging Expert Advisor
Author: Johannes N. Nkosi
Date: July 28, 2025

This EA implements a smart hedging strategy for indices (e.g., US500, DE30).
It uses dynamic partial hedging, volatility and trend filters, and robust risk controls.
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

class IndicesHedgingEA:
    def __init__(self, symbol="US500", base_lot=0.1, hedge_ratio=0.5, magic_number=54321):
        credentials = get_account_credentials()
        self.symbol = credentials.get('symbol', symbol)
        self.base_lot = base_lot
        self.hedge_ratio = hedge_ratio
        self.magic_number = magic_number
        self.is_running = False
        self.risk_manager = RiskManager()
        self.login = credentials['login']
        self.password = credentials['password']
        self.server = credentials['server']
        self.trailing_enabled = True
        self.trailing_distance_points = 100
        self.max_drawdown_percent = 20.0
        self.log_file = "hedging_ea.log"

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
        # Use volatility spike or trend reversal to trigger hedge
        data = self.get_market_data()
        if data is None or len(data) < 50:
            return None
        atr = data['high'].rolling(window=14).max() - data['low'].rolling(window=14).min()
        fast_ma = data['close'].rolling(window=10).mean()
        slow_ma = data['close'].rolling(window=30).mean()
        if atr.iloc[-1] > atr.mean() * 1.5:
            return "HEDGE"
        if fast_ma.iloc[-1] < slow_ma.iloc[-1]:
            return "HEDGE"
        return None

    def open_main_position(self, direction):
        bid, ask = self.get_current_price()
        price = ask if direction == "BUY" else bid
        lot = self.base_lot
        order_type = mt5.ORDER_TYPE_BUY if direction == "BUY" else mt5.ORDER_TYPE_SELL
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.symbol,
            "volume": lot,
            "type": order_type,
            "price": price,
            "deviation": 20,
            "magic": self.magic_number,
            "comment": f"Main {direction}",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            self.log(f"Failed to open main {direction} position: {result.retcode}")
            return None
        self.log(f"Main {direction} position opened: Volume={lot}, Price={price:.2f}")
        return result

    def open_hedge_position(self, main_direction):
        bid, ask = self.get_current_price()
        price = bid if main_direction == "BUY" else ask
        lot = self.base_lot * self.hedge_ratio
        order_type = mt5.ORDER_TYPE_SELL if main_direction == "BUY" else mt5.ORDER_TYPE_BUY
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.symbol,
            "volume": lot,
            "type": order_type,
            "price": price,
            "deviation": 20,
            "magic": self.magic_number,
            "comment": f"Hedge {order_type}",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            self.log(f"Failed to open hedge position: {result.retcode}")
            return None
        self.log(f"Hedge position opened: Volume={lot}, Price={price:.2f}")
        return result

    def manage_positions(self):
        # Trailing stop, partial close, global stop loss, drawdown check
        account_info = mt5.account_info()
        if not account_info:
            return
        balance = account_info.balance
        equity = account_info.equity
        drawdown = (balance - equity) / balance * 100 if balance > 0 else 0
        if drawdown > self.max_drawdown_percent:
            self.log("Max drawdown reached! Closing all positions.")
            self.close_all_positions()
        # Trailing stop logic for all positions
        positions = mt5.positions_get(symbol=self.symbol)
        if positions:
            for pos in positions:
                self.update_trailing_stop(pos, pos.price_current)
                if pos.profit > 50:  # Example profit threshold
                    self.partial_close(pos)

    def update_trailing_stop(self, position, current_price):
        if not self.trailing_enabled:
            return False
        symbol_info = self.get_symbol_info()
        if symbol_info is None:
            return False
        point = symbol_info.point
        trailing_distance = self.trailing_distance_points * point
        new_sl = None
        if position.type == mt5.ORDER_TYPE_BUY:
            new_sl = current_price - trailing_distance
        elif position.type == mt5.ORDER_TYPE_SELL:
            new_sl = current_price + trailing_distance
        else:
            return False
        request = {
            "action": mt5.TRADE_ACTION_SLTP,
            "symbol": self.symbol,
            "position": position.ticket,
            "sl": new_sl,
            "tp": position.tp,
        }
        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            self.log(f"Failed to update trailing stop: {result.retcode}")
            return False
        self.log(f"Trailing stop updated to {new_sl:.2f} for position {position.ticket}")
        return True

    def partial_close(self, position):
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
                "comment": "Hedging EA Close",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            result = mt5.order_send(request)
            if result.retcode == mt5.TRADE_RETCODE_DONE:
                self.log(f"Closed position {pos.ticket}")

    def log(self, message):
        with open(self.log_file, "a") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")
        print(message)

    def run(self):
        if not self.initialize_mt5():
            return
        self.is_running = True
        print("Indices Hedging EA started...")
        try:
            while self.is_running:
                # Pause logic: check for pause.flag in working directory
                check_pause_flag(os.path.dirname(os.path.abspath(__file__)))
                self.manage_positions()
                signal = self.get_signal()
                if signal == "HEDGE":
                    print("Hedge signal detected. Opening hedge position.")
                    self.open_hedge_position("BUY")  # Example: always hedge against BUY
                time.sleep(60)
        except KeyboardInterrupt:
            print("EA stopped by user")
        finally:
            self.stop()

    def stop(self):
        self.is_running = False
        print("Stopping Indices Hedging EA...")
        self.close_all_positions()
        mt5.shutdown()
        print("EA stopped and MT5 connection closed")

if __name__ == "__main__":
    ea = IndicesHedgingEA()
    ea.run()
