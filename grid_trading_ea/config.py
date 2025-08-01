# MetaTrader 5 Grid Trading EA Configuration
# Modify these settings according to your trading preferences

# Account Information (Exness Demo Account)
LOGIN = 210715557
PASSWORD = "Johannes@0"
SERVER = "Exness-MT5Trial9"

# Trading Symbol
SYMBOL = "EURUSD"

# Grid Trading Parameters
LOT_SIZE = 0.01  # Position size per grid level (small for safety)
GRID_DISTANCE = 50  # Distance between grid levels in points
MAX_LEVELS = 5  # Maximum levels above and below current price

# Magic Number (unique identifier for EA trades)
MAGIC_NUMBER = 54321

# Risk Management
MAX_TOTAL_LOTS = 1.0  # Maximum total lot size across all positions
MAX_SPREAD = 3  # Maximum spread in points to allow trading
MIN_FREE_MARGIN = 1000  # Minimum free margin required

# Grid Management
AUTO_ADJUST_GRID = True  # Automatically adjust grid based on volatility
GRID_RECALC_INTERVAL = 300  # Seconds between grid recalculation
PROFIT_TARGET = 100  # Target profit in account currency to close all

# Loop Settings
SLEEP_INTERVAL = 60  # Seconds to wait between EA iterations (1 minute)
STATUS_UPDATE_INTERVAL = 10  # Iterations between status updates

# Safety Features
EMERGENCY_STOP_LOSS = 500  # Maximum total loss before emergency stop
MAX_OPEN_POSITIONS = 10  # Maximum number of open positions
TRADING_HOURS_START = 0  # Start trading hour (24h format)
TRADING_HOURS_END = 24   # End trading hour (24h format)
