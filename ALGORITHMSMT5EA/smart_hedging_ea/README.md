# Smart Hedging EA

This folder contains a smart Hedging Expert Advisor for trading any market (indices, forex, commodities) on MetaTrader 5.

## Features
- Dynamic partial hedging based on volatility and trend
- Trailing stop and partial close for all positions
- Global stop loss and drawdown protection
- Centralized configuration and risk management
- Easy to use launcher script

## Files
- `mt5_smart_hedging_ea.py`: Main EA logic
- `config.py`: EA settings (loads from global_config.py)
- `launcher.py`: Run the EA

## Usage
1. Edit `global_config.py` to set your symbol and risk parameters.
2. Run `launcher.py` to start the EA.

---
**Author:** Johannes N. Nkosi
**Date:** July 28, 2025
