# MetaTrader 5 Trend Following EA Configuration
# Modify these settings according to your trading preferences

# Account Information (Update with your VPS broker details)
LOGIN = 210715557
PASSWORD = "Johannes@0"
SERVER = "Exness-MT5Trial9"

# Trading Symbol
SYMBOL = "EURUSD"

# Position Sizing
LOT_SIZE = 0.1  # Base lot size
AUTO_LOT_SIZING = True  # Enable automatic position sizing based on risk
RISK_PERCENT = 1.0  # Risk percentage per trade (reduced for VPS stability)

# Magic Number (unique identifier for EA trades)
MAGIC_NUMBER = 98765

# Timeframes for Multi-Timeframe Analysis
PRIMARY_TIMEFRAME = "M1"    # Primary timeframe for signals (1-minute)
SECONDARY_TIMEFRAME = "M5"  # Secondary timeframe for trend confirmation (5-minute)

# VPS Operation Settings
UPDATE_INTERVAL = 60        # Check every 60 seconds (1 minute)
ENABLE_LOGGING = True       # Enable detailed logging for VPS monitoring
LOG_LEVEL = "INFO"         # Logging level
MAX_LOG_SIZE = 50          # Maximum log file size in MB
RESTART_ON_ERROR = True    # Auto-restart on connection errors

# Trend Following Indicators
EMA_FAST = 21           # Fast EMA period
EMA_SLOW = 50           # Slow EMA period  
EMA_FILTER = 200        # Long-term trend filter EMA
ADX_PERIOD = 14         # ADX period for trend strength
ADX_THRESHOLD = 25      # Minimum ADX value for trend confirmation
RSI_PERIOD = 14         # RSI period

# Risk Management
ATR_PERIOD = 14         # ATR period for stop loss calculation
ATR_MULTIPLIER = 2.5    # ATR multiplier for stop loss distance
RISK_REWARD_RATIO = 3.0 # Risk-reward ratio (3:1)

# Position Management
MAX_POSITIONS = 1       # Maximum positions per direction
TRAILING_ENABLED = True # Enable trailing stop
TRAILING_ATR_MULT = 2.5 # ATR multiplier for trailing stop distance

# Signal Filters
MIN_CANDLE_BODY = 0.6   # Minimum candle body ratio for signal confirmation
VOLUME_FILTER = True    # Enable volume confirmation
NEWS_FILTER = False     # Enable news event filter (if available)

# Trading Hours (24-hour format)
TRADING_START_HOUR = 0  # Start trading hour
TRADING_END_HOUR = 24   # End trading hour
AVOID_FRIDAY_CLOSE = True # Avoid opening positions on Friday after 18:00

# Safety Features
MAX_DAILY_TRADES = 2    # Maximum trades per day
MAX_WEEKLY_LOSS = 500   # Maximum weekly loss before EA stops
EMERGENCY_STOP_LOSS = 1000  # Emergency stop loss (account currency)

# Loop Settings
CHECK_INTERVAL = 60    # Seconds between EA iterations (1 minute for M1)
STATUS_UPDATE_INTERVAL = 20  # Iterations between status updates

# Backtesting Settings (for future implementation)
BACKTEST_START_DATE = "2023-01-01"
BACKTEST_END_DATE = "2024-12-31"
BACKTEST_INITIAL_DEPOSIT = 10000
