# MetaTrader 5 High-Frequency Scalping EA Configuration
# Modify these settings according to your trading preferences

# Account Information (Update with your broker details)
LOGIN = 210715557
PASSWORD = "Johannes@0"
SERVER = "Exness-MT5Trial9"

# Trading Symbol
SYMBOL = "BTCUSD"

# Position Sizing
LOT_SIZE = 0.01  # Small lot size for scalping
AUTO_LOT_SIZING = True
RISK_PERCENT = 0.5  # Lower risk per trade for high frequency

# Magic Number (unique identifier for EA trades)
MAGIC_NUMBER = 54321

# Scalping Parameters (Percentage-based)
MIN_SPREAD = 2          # Maximum spread to trade (points)
MAX_SPREAD = 8          # Skip trades if spread too wide
SCALP_TARGET_PERCENT = 3.0    # Target profit as % of account balance
STOP_LOSS_PERCENT = 3.0       # Stop loss as % of account balance  
TRAILING_STOP_PERCENT = 0.5   # Trailing stop as % of account balance per move

# Breakeven Settings (Percentage-based)
BREAKEVEN_TRIGGER_PERCENT = 1.5  # Move SL to entry when trade reaches 1.5% (halfway to 3%)
ENABLE_BREAKEVEN = True          # Enable breakeven functionality

# Order Flow Analysis
VOLUME_THRESHOLD = 100  # Minimum volume for signal
TICK_ANALYSIS_PERIOD = 20  # Number of ticks to analyze
BID_ASK_PRESSURE_PERIOD = 10  # Period for bid/ask pressure analysis

# Time Filters
START_HOUR = 8          # Start trading hour (GMT)
END_HOUR = 18           # End trading hour (GMT)
AVOID_NEWS_MINUTES = 30 # Minutes to avoid before/after major news

# Advanced Settings
MAX_DAILY_TRADES = 100  # Maximum trades per day
MAX_CONCURRENT_TRADES = 3  # Maximum open positions
SLIPPAGE = 3           # Maximum slippage in points
UPDATE_INTERVAL = 1    # Check every 1 second for scalping

# VPS-specific settings for high-frequency trading
ENABLE_LOGGING = True
LOG_LEVEL = "DEBUG"
MAX_LOG_SIZE = 100     # MB
RESTART_ON_ERROR = True

# Performance Monitoring (Percentage-based)
DAILY_PROFIT_TARGET_PERCENT = 15.0  # Daily profit target as % of account balance
DAILY_LOSS_LIMIT_PERCENT = 9.0      # Daily loss limit as % of account balance
DRAWDOWN_LIMIT = 5                   # Maximum drawdown percentage
