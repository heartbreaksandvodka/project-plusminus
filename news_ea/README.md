# News EA

This folder contains a News Trading Expert Advisor for MetaTrader 5.
It uses a global economic calendar API (news_api.py) to trade critical news events with dynamic risk management.

## Features
- Fetches and filters critical news events
- Places buy/sell stop orders before news
- Dynamic risk management and order handling
- Centralized configuration and risk management
- Easy to use launcher script

## Files
- `mt5_news_ea.py`: Main EA logic
- `config.py`: EA settings (loads from global_config.py)
- `launcher.py`: Run the EA
- `news_api.py`: Global news API (in root folder)

## Usage
1. Edit `global_config.py` to set your symbol and risk parameters.
2. Run `launcher.py` to start the EA.

---
**Author:** Johannes N. Nkosi
**Date:** July 28, 2025
