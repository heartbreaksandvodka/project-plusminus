"""
Indices Martingale EA Configuration
All settings are now loaded from global_config.py for consistency.
"""

from global_config import get_account_credentials, get_risk_settings

# Example usage:
credentials = get_account_credentials()
account_risk = get_risk_settings()

# You can access settings like:
# symbol = credentials.get('symbol', 'US500')
# base_lot = account_risk.get('base_lot', 0.1)
# grid_step_points = account_risk.get('grid_step_points', 100)
# max_trades = account_risk.get('max_trades', 6)
# max_drawdown_percent = account_risk.get('max_drawdown_percent', 20.0)
