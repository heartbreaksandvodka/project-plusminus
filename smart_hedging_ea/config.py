# Smart Hedging EA Configuration
# All settings are loaded from global_config.py for consistency

from global_config import get_account_credentials, get_risk_settings

credentials = get_account_credentials()
account_risk = get_risk_settings()

# Example usage:
# symbol = credentials.get('symbol', 'US500')
# base_lot = account_risk.get('base_lot', 0.1)
# hedge_ratio = account_risk.get('hedge_ratio', 0.5)
# max_drawdown_percent = account_risk.get('max_drawdown_percent', 20.0)
