"""
Dynamic MT5 credential management for EAs
This module provides functions to get MT5 credentials from the database
instead of using hardcoded values in config files.
"""

import os
import sys
from pathlib import Path

def get_mt5_credentials_from_db():
    """
    Get MT5 credentials from the database or environment variables
    Returns the most recently connected/active MT5 account
    Priority: 1. Environment variables (from backend), 2. Database, 3. Global config
    """
    try:
        # First, check if credentials are passed via environment variables (from backend)
        if all(key in os.environ for key in ['MT5_ACCOUNT_NUMBER', 'MT5_PASSWORD', 'MT5_SERVER']):
            print("Using MT5 credentials from environment variables (backend)")
            return {
                'login': int(os.environ['MT5_ACCOUNT_NUMBER']),
                'password': os.environ['MT5_PASSWORD'],
                'server': os.environ['MT5_SERVER'],
                'account_id': int(os.environ.get('MT5_ACCOUNT_ID', 0)),
                'broker_name': os.environ.get('MT5_BROKER_NAME', 'Unknown')
            }
    
    except (ValueError, KeyError) as e:
        print(f"Environment variables invalid: {e}, trying database...")
    
    try:
        # Setup Django dynamically
        backend_dir = Path(__file__).resolve().parent.parent / 'backend'
        sys.path.insert(0, str(backend_dir))
        
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'authproject.settings')
        
        import django
        django.setup()
        
        from mt5_integration.models import MT5Account
        
        # Get the most recent active account, preferring connected ones
        account = MT5Account.objects.filter(
            is_active=True
        ).order_by(
            # Prefer connected accounts, then by last_connected, then by updated_at
            '-connection_status',  # 'connected' comes before 'disconnected' alphabetically
            '-last_connected',
            '-updated_at'
        ).first()
        
        if not account:
            raise Exception("No active MT5 account found in database")
        
        print(f"Using MT5 credentials from database for account {account.account_number}")
        return {
            'login': int(account.account_number),
            'password': account.get_password(),
            'server': account.server,
            'account_id': account.id,
            'broker_name': account.broker_name
        }
    
    except Exception as e:
        # Fallback to global config if database access fails
        print(f"Warning: Could not get credentials from database: {e}")
        print("Falling back to global config...")
        
        try:
            from global_config import MT5_LOGIN, MT5_PASSWORD, MT5_SERVER
            return {
                'login': MT5_LOGIN,
                'password': MT5_PASSWORD,
                'server': MT5_SERVER,
                'account_id': None,
                'broker_name': 'Exness'
            }
        except ImportError:
            raise Exception("Could not get MT5 credentials from database or global config")

def get_account_credentials():
    """
    Wrapper function that maintains compatibility with existing EA code
    """
    creds = get_mt5_credentials_from_db()
    return {
        'login': creds['login'],
        'password': creds['password'],
        'server': creds['server']
    }

# For backward compatibility, also provide individual functions
def get_mt5_login():
    """Get MT5 login from database"""
    return get_mt5_credentials_from_db()['login']

def get_mt5_password():
    """Get MT5 password from database"""
    return get_mt5_credentials_from_db()['password']

def get_mt5_server():
    """Get MT5 server from database"""
    return get_mt5_credentials_from_db()['server']

# Update EA initialization to use dynamic credentials
def initialize_mt5_dynamic():
    """
    Initialize MT5 with credentials from database
    """
    import MetaTrader5 as mt5
    import logging
    
    creds = get_mt5_credentials_from_db()
    
    if not mt5.initialize():
        logging.error("MetaTrader 5 initialization failed")
        print("MetaTrader 5 initialization failed")
        print("Error code:", mt5.last_error())
        return False
    
    authorized = mt5.login(creds['login'], password=creds['password'], server=creds['server'])
    if not authorized:
        logging.error("Login failed")
        print("Login failed")
        print("Error code:", mt5.last_error())
        return False
    
    logging.info(f"MetaTrader 5 initialized and logged in to account {creds['login']}")
    print(f"MetaTrader 5 initialized and logged in to account {creds['login']}")
    return True

if __name__ == "__main__":
    # Test the credential system
    try:
        creds = get_mt5_credentials_from_db()
        print("✅ Dynamic MT5 Credentials:")
        print(f"   Account: {creds['login']}")
        print(f"   Server: {creds['server']}")
        print(f"   Broker: {creds['broker_name']}")
        print(f"   Database ID: {creds['account_id']}")
    except Exception as e:
        print(f"❌ Error: {e}")
