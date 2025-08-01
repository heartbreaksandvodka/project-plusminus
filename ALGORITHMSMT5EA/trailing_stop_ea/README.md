# MetaTrader 5 Trailing Stop Manager

This is a Python-based utility for MetaTrader 5 that manages trailing stops for existing positions. **This tool does not open new trades** - it only manages stop losses for positions that are already open.

## Features

- **Trailing Stop Management**: Automatically adjusts stop losses to protect profits
- **No Trading Signals**: Does not generate buy/sell signals or open new positions
- **Flexible Filtering**: Can manage all positions or only specific EA positions
- **Real-time Monitoring**: Continuously monitors and updates existing positions
- **Simple Configuration**: Easy setup with minimal parameters

## Prerequisites

1. **MetaTrader 5 Terminal**: Download and install from MetaQuotes
2. **Python 3.7+**: Ensure Python is installed on your system
3. **MT5 Account**: Demo or live trading account

## Installation

1. Clone or download this project
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

Edit `config.py` to customize the trailing stop settings:

- `SYMBOL`: Trading pair (e.g., "EURUSD", "GBPUSD") 
- `TRAILING_DISTANCE`: Distance for trailing stop in points
- `MAGIC_NUMBER`: Filter by EA magic number (0 = all positions)
- `UPDATE_INTERVAL`: How often to check and update trailing stops

## Usage

### Method 1: Test Connection First
```python
from mt5_trailing_stop_ea import test_connection
test_connection()
```

### Method 2: Run the Trailing Stop Manager
```python
python mt5_trailing_stop_ea.py
```

### Method 3: Custom Configuration
```python
from mt5_trailing_stop_ea import TrailingStopManager

manager = TrailingStopManager(
    symbol="EURUSD",
    trailing_distance=50,
    magic_number=0  # 0 = all positions, or specific magic number
)
manager.run()
```

## How It Works

1. **Initialization**: Connects to MT5 and verifies symbol availability
2. **Position Detection**: Finds all open positions for the specified symbol
3. **Trailing Stop Updates**: Continuously adjusts stop losses as price moves favorably
4. **Magic Number Filtering**: Can manage all positions or only specific EA positions

**Important**: This tool does NOT open new positions. It only manages existing ones.

## Trading Strategy

The manager uses simple trailing stop logic:

### For Buy Positions
- **Trailing Logic**: As price moves up, stop loss follows at fixed distance below
- **Protection**: Stop loss never moves down, only up to protect profits

### For Sell Positions  
- **Trailing Logic**: As price moves down, stop loss follows at fixed distance above
- **Protection**: Stop loss never moves up, only down to protect profits

## Risk Warning

⚠️ **This tool only manages existing positions and does not open new trades. It's designed to protect profits on positions that you have already opened manually or through other EAs. Always test on a demo account first.**

## Troubleshooting

### Common Issues

1. **"MetaTrader 5 initialization failed"**
   - Ensure MT5 terminal is running
   - Check if algorithmic trading is enabled in MT5
   - Verify your account credentials

2. **"Symbol not found"**
   - Make sure the symbol is available in your broker's Market Watch
   - Check symbol spelling in config.py

3. **"No positions to manage"**
   - This is normal if no positions are open
   - Open positions manually or through another EA first
   - Check magic number filter settings

## Customization

You can extend the trailing stop manager by:

- Adding email/telegram notifications when stops are moved
- Implementing different trailing algorithms (percentage-based, ATR-based)
- Creating a GUI interface for real-time monitoring
- Adding position filtering by comment or other criteria
- Implementing time-based trailing stop activation

## Author

**Developer**: Johannes N. Nkosi  
**Date**: July 23, 2025  
**Platform**: MetaTrader 5  
**Language**: Python  

## Support

For issues or questions, please check the MT5 documentation or Python MetaTrader5 package documentation.
