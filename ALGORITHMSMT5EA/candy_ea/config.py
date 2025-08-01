# Candy EA Configuration
# Loads settings from global_config.py for consistency
from global_config import get_account_credentials, get_risk_settings

credentials = get_account_credentials()
account_risk = get_risk_settings()
