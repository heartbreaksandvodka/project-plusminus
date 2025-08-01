"""
Liquidity Detector EA for MetaTrader 5
Author: Johannes N. Nkosi
Date: July 31, 2025

- Detects fair value gaps (FVG), liquidity sweeps, and executes institutional-style entries
- Uses higher time frame trend, volume confirmation, and advanced risk management
"""
import MetaTrader5 as mt5
import pandas as pd
import numpy as np
import time
import sys
import os
import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from global_config import get_account_credentials, get_risk_settings
from risk_manager import RiskManager
from liquidity_ea.utils import detect_fvg, detect_liquidity_pools, get_session

class LiquidityEA:
    def __init__(self, symbol="EURUSD", base_lot=0.1, magic_number=88888):
        credentials = get_account_credentials()
        self.symbol = credentials.get('symbol', symbol)
        self.base_lot = base_lot
        self.magic_number = magic_number
        self.is_running = False
        self.risk_manager = RiskManager()
        self.login = credentials['login']
        self.password = credentials['password']
        self.server = credentials['server']
        self.trailing_enabled = True
        self.trailing_distance_points = 50
        self.max_risk_percent = 5.0
        self.log_file = "liquidity_ea.log"

    def initialize_mt5(self):
        if not mt5.initialize():
            print("MetaTrader 5 initialization failed")
            print("Error code:", mt5.last_error())
            return False
        if self.login and self.password and self.server:
            authorized = mt5.login(self.login, password=self.password, server=self.server)
            if not authorized:
                print("Login failed")
                print("Error code:", mt5.last_error())
                return False
        print("MetaTrader 5 initialized and logged in.")
        return True

    def get_symbol_info(self):
        symbol_info = mt5.symbol_info(self.symbol)
        if symbol_info is None:
            print(f"Symbol {self.symbol} not found")
            return None
        if not symbol_info.visible:
            mt5.symbol_select(self.symbol, True)
        return symbol_info

    def get_current_price(self):
        tick = mt5.symbol_info_tick(self.symbol)
        if tick is None:
            return None, None
        return tick.bid, tick.ask

    def get_market_data(self, timeframe, num_bars=200):
        rates = mt5.copy_rates_from_pos(self.symbol, timeframe, 0, num_bars)
        if rates is None:
            return None
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        return df

    def get_trend(self):
        # Use H1 and H4 for trend context
        h1 = self.get_market_data(mt5.TIMEFRAME_H1, 100)
        h4 = self.get_market_data(mt5.TIMEFRAME_H4, 100)
        if h1 is None or h4 is None:
            return None
        h1_ma = h1['close'].rolling(window=20).mean().iloc[-1]
        h4_ma = h4['close'].rolling(window=20).mean().iloc[-1]
        h1_last = h1['close'].iloc[-1]
        h4_last = h4['close'].iloc[-1]
        if h1_last > h1_ma and h4_last > h4_ma:
            return "BULLISH"
        elif h1_last < h1_ma and h4_last < h4_ma:
            return "BEARISH"
        else:
            return None

    def get_signal(self):
        m5 = self.get_market_data(mt5.TIMEFRAME_M5, 100)
        if m5 is None or len(m5) < 30:
            return None
        # --- Session filter ---
        now_utc = datetime.datetime.utcnow()
        session = get_session(now_utc)
        if session not in ("Europe", "New York"):
            return None
        fvg_list = detect_fvg(m5)
        swing_highs, swing_lows = detect_liquidity_pools(m5)
        trend = self.get_trend()
        # Example: Look for sweep of swing low, then bullish engulfing
        if trend == "BULLISH" and swing_lows:
            last_low_idx, last_low = swing_lows[-1]
            if m5['low'].iloc[-1] < last_low:
                # Price swept liquidity, now look for reversal
                if m5['close'].iloc[-1] > m5['open'].iloc[-1]:
                    return "BUY"
        if trend == "BEARISH" and swing_highs:
            last_high_idx, last_high = swing_highs[-1]
            if m5['high'].iloc[-1] > last_high:
                if m5['close'].iloc[-1] < m5['open'].iloc[-1]:
                    return "SELL"
        return None

    def get_account_risk(self):
        account_info = mt5.account_info()
        if not account_info:
            return 0
        balance = account_info.balance
        equity = account_info.equity
        risk = (balance - equity) / balance * 100 if balance > 0 else 0
        return risk

    def open_position(self, direction):
        bid, ask = self.get_current_price()
        price = ask if direction == "BUY" else bid
        lot = self.base_lot
        order_type = mt5.ORDER_TYPE_BUY if direction == "BUY" else mt5.ORDER_TYPE_SELL
        sl_points = 100  # Example: 100 points stop loss
        symbol_info = self.get_symbol_info()
        point = symbol_info.point if symbol_info else 0.0001
        sl = price - sl_points * point if direction == "BUY" else price + sl_points * point
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.symbol,
            "volume": lot,
            "type": order_type,
            "price": price,
            "sl": sl,
            "deviation": 20,
            "magic": self.magic_number,
            "comment": f"LiquidityEA {direction}",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            self.log(f"Failed to open {direction} position: {result.retcode}")
            return None
        self.log(f"{direction} position opened: Volume={lot}, Price={price:.5f}, SL={sl:.5f}")
        return result

    def manage_positions(self):
        # Trailing stop, dynamic SL, risk check
        account_risk = self.get_account_risk()
        if account_risk > self.max_risk_percent:
            self.log("Max risk reached! No new trades.")
            return
        positions = mt5.positions_get(symbol=self.symbol)
        if positions:
            for pos in positions:
                self.update_trailing_stop(pos, pos.price_current)
                # Dynamic SL: tighten SL if multiple positions open
                if len(positions) > 1:
                    self.tighten_stop_loss(pos)

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
        self.log(f"Trailing stop updated to {new_sl:.5f} for position {position.ticket}")
        return True

    def tighten_stop_loss(self, position):
        # Tighten SL if multiple positions are open
        symbol_info = self.get_symbol_info()
        if symbol_info is None:
            return False
        point = symbol_info.point
        tighter_sl = position.price_current - 30 * point if position.type == mt5.ORDER_TYPE_BUY else position.price_current + 30 * point
        request = {
            "action": mt5.TRADE_ACTION_SLTP,
            "symbol": self.symbol,
            "position": position.ticket,
            "sl": tighter_sl,
            "tp": position.tp,
        }
        result = mt5.order_send(request)
        if result.retcode == mt5.TRADE_RETCODE_DONE:
            self.log(f"Stop loss tightened to {tighter_sl:.5f} for position {position.ticket}")
        return True

    def log(self, message):
        with open(self.log_file, "a") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")
        print(message)

    def run(self):
        if not self.initialize_mt5():
            return
        self.is_running = True
        print("Liquidity EA started...")
        try:
            while self.is_running:
                self.manage_positions()
                signal = self.get_signal()
                if signal:
                    self.open_position(signal)
                time.sleep(60)
        except KeyboardInterrupt:
            print("EA stopped by user")
        finally:
            self.stop()

    def stop(self):
        self.is_running = False
        print("Stopping Liquidity EA...")
        mt5.shutdown()
        print("EA stopped and MT5 connection closed")

if __name__ == "__main__":
    ea = LiquidityEA()
    ea.run()
