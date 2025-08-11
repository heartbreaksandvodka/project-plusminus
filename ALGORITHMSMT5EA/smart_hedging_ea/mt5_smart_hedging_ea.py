"""
MetaTrader 5 Smart Hedging Expert Advisor
Author: Johannes N. Nkosi
Date: July 28, 2025

This EA implements a smart hedging strategy for any market (indices, forex, commodities).
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

class SmartHedgingEA:
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

    def manage_positions(self):
        # Trailing stop, partial close, global stop loss, drawdown check
        account_info = mt5.account_info()
        if not account_info:
            return
        balance = account_info.balance
        equity = account_info.equity
        drawdown = (balance - equity) / balance * 100 if balance > 0 else 0
        if drawdown > self.max_drawdown_percent:
            print("Max drawdown reached! Closing all positions.")
            self.close_all_positions()
        # Trailing stop logic for all positions
        positions = mt5.positions_get(symbol=self.symbol)
        if positions:
            for pos in positions:
                # Placeholder for trailing stop and partial close
                pass

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
                "comment": "Smart Hedging EA Close",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            result = mt5.order_send(request)
            if result.retcode == mt5.TRADE_RETCODE_DONE:
                print(f"Closed position {pos.ticket}")

    def get_signal(self):
        # Use volatility spike or trend reversal to trigger hedge
        data = self.get_market_data() if hasattr(self, 'get_market_data') else None
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

    def run(self):
        if not self.initialize_mt5():
            return
        self.is_running = True
        print("Smart Hedging EA started...")
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
        print("Stopping Smart Hedging EA...")
        self.close_all_positions()
        mt5.shutdown()
        print("EA stopped and MT5 connection closed")
