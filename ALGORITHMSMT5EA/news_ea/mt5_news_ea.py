"""
MetaTrader 5 News Trading Expert Advisor
Author: Johannes N. Nkosi
Date: July 28, 2025

This EA trades news events using a global economic calendar API (news_api.py).
It places buy/sell stop orders before critical news and manages risk dynamically.
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
from news_api import get_upcoming_events, filter_critical_events

class NewsEA:
    def __init__(self, symbol="EURUSD", base_lot=0.1, magic_number=67890):
        credentials = get_account_credentials()
        self.symbol = credentials.get('symbol', symbol)
        self.base_lot = base_lot
        self.magic_number = magic_number
        self.is_running = False
        self.risk_manager = RiskManager()
        self.login = credentials['login']
        self.password = credentials['password']
        self.server = credentials['server']
        self.country = credentials.get('country', 'united states')
        self.days_ahead = 1
        self.log_file = "news_ea.log"

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

    def get_current_price(self):
        tick = mt5.symbol_info_tick(self.symbol)
        if tick is None:
            return None, None
        return tick.bid, tick.ask

    def place_news_orders(self, event):
        bid, ask = self.get_current_price()
        if bid is None or ask is None:
            print("No price available.")
            return
        # Place buy stop and sell stop above/below price
        stop_distance = 50  # points above/below
        symbol_info = mt5.symbol_info(self.symbol)
        point = symbol_info.point if symbol_info else 0.0001
        buy_stop = ask + stop_distance * point
        sell_stop = bid - stop_distance * point
        lot = self.base_lot
        # Buy stop order
        buy_request = {
            "action": mt5.TRADE_ACTION_PENDING,
            "symbol": self.symbol,
            "volume": lot,
            "type": mt5.ORDER_TYPE_BUY_STOP,
            "price": buy_stop,
            "deviation": 20,
            "magic": self.magic_number,
            "comment": f"NewsEA BuyStop {event['event']}",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        # Sell stop order
        sell_request = {
            "action": mt5.TRADE_ACTION_PENDING,
            "symbol": self.symbol,
            "volume": lot,
            "type": mt5.ORDER_TYPE_SELL_STOP,
            "price": sell_stop,
            "deviation": 20,
            "magic": self.magic_number,
            "comment": f"NewsEA SellStop {event['event']}",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        mt5.order_send(buy_request)
        mt5.order_send(sell_request)
        print(f"Placed buy stop at {buy_stop:.5f} and sell stop at {sell_stop:.5f} for event: {event['event']}")

    def run(self):
        if not self.initialize_mt5():
            return
        self.is_running = True
        print("News EA started...")
        try:
            self.send_daily_news_events()  # Log daily news events on start
            while self.is_running:
                # Get upcoming news events
                events = get_upcoming_events(self.country, self.days_ahead)
                critical_events = filter_critical_events(events)
                for idx, event in critical_events.iterrows():
                    print(f"Critical event: {event['date']} {event['time']} {event['event']}")
                    self.place_news_orders(event)
                time.sleep(300)  # Check every 5 minutes
        except KeyboardInterrupt:
            print("EA stopped by user")
        finally:
            self.stop()

    def send_daily_news_events(self):
        events = get_upcoming_events(self.country, self.days_ahead)
        if events.empty:
            message = f"No news events found for {self.country} in next {self.days_ahead} day(s)."
        else:
            message = f"Upcoming news events for {self.country} (next {self.days_ahead} day(s)):\n"
            for idx, event in events.iterrows():
                message += f"{event['date']} {event['time']} {event['event']} [{event['importance']}]\n"
        try:
            with open('news_events.log', 'a', encoding='utf-8') as log_file:
                log_file.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}]\n{message}\n\n")
            print("News events logged to news_events.log.")
        except Exception as e:
            print(f"Error logging news events: {e}")

    def stop(self):
        self.is_running = False
        print("Stopping News EA...")
        mt5.shutdown()
        print("EA stopped and MT5 connection closed")

if __name__ == "__main__":
    ea = NewsEA()
    ea.run()
