import MetaTrader5 as mt5
import os
import time
import logging

def initialize_mt5(login, password, server):
    if not mt5.initialize():
        logging.error("MetaTrader 5 initialization failed")
        print("MetaTrader 5 initialization failed")
        print("Error code:", mt5.last_error())
        return False
    if login and password and server:
        authorized = mt5.login(login, password=password, server=server)
        if not authorized:
            logging.error("Login failed")
            print("Login failed")
            print("Error code:", mt5.last_error())
            return False
    logging.info("MetaTrader 5 initialized and logged in.")
    print("MetaTrader 5 initialized and logged in.")
    return True

def get_symbol_info(symbol):
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        print(f"Symbol {symbol} not found")
        return None
    if not symbol_info.visible:
        mt5.symbol_select(symbol, True)
    return symbol_info

def get_current_price(symbol):
    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        return None, None
    return tick.bid, tick.ask

def check_pause_flag(ea_dir):
    pause_flag_path = os.path.join(ea_dir, 'pause.flag')
    if os.path.exists(pause_flag_path):
        print("EA paused. Waiting for resume...")
        logging.info("EA paused. Waiting for resume...")
        while os.path.exists(pause_flag_path):
            time.sleep(5)
        print("EA resumed.")
        logging.info("EA resumed.")
