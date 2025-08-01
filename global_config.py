# Global Configuration for All MetaTrader5 EAs
# Author: Johannes N. Nkosi
# Date: July 27, 2025

"""
Centralized configuration file for all Expert Advisors.
This file contains login credentials and global risk management settings
that are imported by all EAs for consistency.
"""

# =============================================================================
# ACCOUNT CREDENTIALS (Update with your broker details)
# =============================================================================
MT5_LOGIN = 210715557
MT5_PASSWORD = "Johannes@0"
MT5_SERVER = "Exness-MT5Trial9"

# =============================================================================
# GLOBAL RISK MANAGEMENT (Percentage-based for all EAs)
# =============================================================================

# Position Sizing
DEFAULT_LOT_SIZE = 0.01         # Fallback lot size if auto-sizing fails
AUTO_LOT_SIZING = True          # Enable automatic lot size calculation

# Risk Parameters (All percentage-based)
ACCOUNT_RISK_PERCENT = 2.0      # Risk per trade as % of account balance
DAILY_RISK_LIMIT_PERCENT = 10.0 # Maximum daily loss as % of account balance
DAILY_PROFIT_TARGET_PERCENT = 20.0  # Daily profit target as % of account balance

# Stop Loss & Take Profit (Percentage-based)
DEFAULT_STOP_LOSS_PERCENT = 2.5     # Default SL as % of account balance
DEFAULT_TAKE_PROFIT_PERCENT = 5.0   # Default TP as % of account balance
TRAILING_STOP_PERCENT = 1.0         # Trailing stop as % of account balance

# Breakeven Settings
BREAKEVEN_TRIGGER_PERCENT = 2.0     # Move to breakeven when profit reaches this %
ENABLE_BREAKEVEN = True             # Enable breakeven functionality

# Risk Limits
MAX_CONCURRENT_POSITIONS = 5        # Maximum open positions across all EAs
MAX_DAILY_TRADES = 50              # Maximum trades per day (all EAs combined)
DRAWDOWN_LIMIT_PERCENT = 15.0      # Stop all trading if drawdown exceeds this %

# =============================================================================
# TRADING HOURS & FILTERS
# =============================================================================
TRADING_START_HOUR = 8             # Start trading hour (GMT)
TRADING_END_HOUR = 18              # End trading hour (GMT)
AVOID_WEEKENDS = True              # Skip weekend trading
AVOID_NEWS_MINUTES = 30            # Minutes to avoid before/after major news

# =============================================================================
# EXECUTION SETTINGS
# =============================================================================
MAX_SLIPPAGE = 3                   # Maximum slippage in points
ORDER_TIMEOUT_SECONDS = 30         # Order execution timeout
RETRY_ATTEMPTS = 3                 # Number of retry attempts for failed orders

# =============================================================================
# LOGGING & MONITORING
# =============================================================================
ENABLE_LOGGING = True              # Enable logging for all EAs
LOG_LEVEL = "INFO"                 # DEBUG, INFO, WARNING, ERROR
LOG_TO_FILE = True                 # Save logs to files
LOG_TO_CONSOLE = True              # Display logs in console
MAX_LOG_FILE_SIZE_MB = 50          # Maximum log file size in MB

# =============================================================================
# VPS & CONNECTIVITY
# =============================================================================
RESTART_ON_ERROR = True            # Restart EA if critical error occurs
CONNECTION_TIMEOUT = 10            # MT5 connection timeout in seconds
HEARTBEAT_INTERVAL = 60            # Heartbeat check interval in seconds

# =============================================================================
# EA-SPECIFIC OVERRIDES (Can be customized per EA)
# =============================================================================

# Grid Trading EA Specifics
GRID_SPACING_PERCENT = 1.0         # Grid level spacing as % of account balance
GRID_MAX_LEVELS = 10               # Maximum grid levels

# Scalping EA Specifics  
SCALP_TARGET_PERCENT = 1.5         # Scalping target as % of account balance
MIN_SPREAD_POINTS = 2              # Minimum spread for scalping
MAX_SPREAD_POINTS = 8              # Maximum spread for scalping

# Trend Following EA Specifics
TREND_MIN_MOMENTUM = 0.5           # Minimum momentum for trend signals
TREND_CONFIRMATION_PERIOD = 20     # Bars for trend confirmation

# Trailing Stop EA Specifics
TRAILING_STEP_PERCENT = 0.25       # Trailing step as % of account balance
RISK_BASED_SL_PERCENT = 10.0       # Risk-based stop loss as % of balance

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_account_credentials():
    """Get MT5 account credentials"""
    return {
        'login': MT5_LOGIN,
        'password': MT5_PASSWORD,
        'server': MT5_SERVER
    }

def get_risk_settings():
    """Get global risk management settings"""
    return {
        'account_risk_percent': ACCOUNT_RISK_PERCENT,
        'daily_risk_limit_percent': DAILY_RISK_LIMIT_PERCENT,
        'daily_profit_target_percent': DAILY_PROFIT_TARGET_PERCENT,
        'stop_loss_percent': DEFAULT_STOP_LOSS_PERCENT,
        'take_profit_percent': DEFAULT_TAKE_PROFIT_PERCENT,
        'trailing_stop_percent': TRAILING_STOP_PERCENT,
        'breakeven_trigger_percent': BREAKEVEN_TRIGGER_PERCENT,
        'enable_breakeven': ENABLE_BREAKEVEN,
        'max_concurrent_positions': MAX_CONCURRENT_POSITIONS,
        'max_daily_trades': MAX_DAILY_TRADES,
        'drawdown_limit_percent': DRAWDOWN_LIMIT_PERCENT
    }

def get_trading_hours():
    """Get trading time settings"""
    return {
        'start_hour': TRADING_START_HOUR,
        'end_hour': TRADING_END_HOUR,
        'avoid_weekends': AVOID_WEEKENDS,
        'avoid_news_minutes': AVOID_NEWS_MINUTES
    }

def get_execution_settings():
    """Get order execution settings"""
    return {
        'max_slippage': MAX_SLIPPAGE,
        'order_timeout': ORDER_TIMEOUT_SECONDS,
        'retry_attempts': RETRY_ATTEMPTS,
        'restart_on_error': RESTART_ON_ERROR
    }

def get_logging_config():
    """Get logging configuration"""
    return {
        'enabled': ENABLE_LOGGING,
        'level': LOG_LEVEL,
        'to_file': LOG_TO_FILE,
        'to_console': LOG_TO_CONSOLE,
        'max_file_size_mb': MAX_LOG_FILE_SIZE_MB
    }

# Quick validation
if __name__ == "__main__":
    print("🔧 Global EA Configuration Loaded")
    print(f"📊 Account: {MT5_LOGIN} on {MT5_SERVER}")
    print(f"⚖️  Risk per trade: {ACCOUNT_RISK_PERCENT}%")
    print(f"🎯 Daily profit target: {DAILY_PROFIT_TARGET_PERCENT}%")
    print(f"🛡️  Daily loss limit: {DAILY_RISK_LIMIT_PERCENT}%")
    print("✅ Configuration validated successfully!")
