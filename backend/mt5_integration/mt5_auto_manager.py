import MetaTrader5 as mt5
import subprocess
import time
import os
import psutil
import logging
from typing import Dict, Tuple, Optional
from pathlib import Path
import winreg


logger = logging.getLogger(__name__)


class MT5AutoManager:
    """Automated MT5 Terminal Management"""
    
    @staticmethod
    def find_mt5_executable() -> Optional[str]:
        """Find MT5 terminal executable path"""
        common_paths = [
            "C:\\Program Files\\MetaTrader 5\\terminal64.exe",
            "C:\\Program Files (x86)\\MetaTrader 5\\terminal64.exe",
            "C:\\Users\\{}\\AppData\\Roaming\\MetaQuotes\\Terminal\\*\\terminal64.exe".format(os.getenv('USERNAME')),
        ]
        
        # Check registry for MT5 installation
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                               "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall") as key:
                for i in range(winreg.QueryInfoKey(key)[0]):
                    subkey_name = winreg.EnumKey(key, i)
                    try:
                        with winreg.OpenKey(key, subkey_name) as subkey:
                            try:
                                display_name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                                if "MetaTrader 5" in display_name:
                                    install_location = winreg.QueryValueEx(subkey, "InstallLocation")[0]
                                    exe_path = os.path.join(install_location, "terminal64.exe")
                                    if os.path.exists(exe_path):
                                        return exe_path
                            except FileNotFoundError:
                                continue
                    except Exception:
                        continue
        except Exception as e:
            logger.warning(f"Could not check registry for MT5: {e}")
        
        # Check common paths
        for path in common_paths:
            if "*" in path:
                # Handle wildcard paths
                from glob import glob
                matches = glob(path)
                for match in matches:
                    if os.path.exists(match):
                        return match
            else:
                if os.path.exists(path):
                    return path
        
        return None
    
    @staticmethod
    def is_mt5_running() -> bool:
        """Check if MT5 terminal is already running"""
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if proc.info['name'].lower() in ['terminal64.exe', 'terminal.exe', 'metatrader.exe']:
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return False
    
    @staticmethod
    def start_mt5_terminal(exe_path: str) -> bool:
        """Start MT5 terminal if not running"""
        try:
            if MT5AutoManager.is_mt5_running():
                logger.info("MT5 terminal already running")
                return True
            
            logger.info(f"Starting MT5 terminal: {exe_path}")
            subprocess.Popen([exe_path], 
                           creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
            
            # Wait for terminal to start
            for _ in range(30):  # Wait up to 30 seconds
                time.sleep(1)
                if MT5AutoManager.is_mt5_running():
                    logger.info("MT5 terminal started successfully")
                    # Give it extra time to fully initialize
                    time.sleep(3)
                    return True
            
            logger.error("MT5 terminal failed to start within timeout")
            return False
            
        except Exception as e:
            logger.error(f"Failed to start MT5 terminal: {e}")
            return False
    
    @staticmethod
    def auto_login(account_number: str, password: str, server: str, max_retries: int = 3) -> Tuple[bool, Dict]:
        """
        Automated MT5 login process with terminal management
        """
        try:
            # Step 1: Find MT5 executable
            exe_path = MT5AutoManager.find_mt5_executable()
            if not exe_path:
                return False, {
                    'error': 'MT5 terminal not found',
                    'details': 'Please install MetaTrader 5 terminal',
                    'solution': 'Download and install MT5 from your broker'
                }
            
            # Step 2: Start MT5 terminal if needed
            if not MT5AutoManager.start_mt5_terminal(exe_path):
                return False, {
                    'error': 'Failed to start MT5 terminal',
                    'details': 'Terminal executable found but failed to start',
                    'solution': 'Try running MT5 manually first'
                }
            
            # Step 3: Attempt connection with retries
            for attempt in range(max_retries):
                logger.info(f"Connection attempt {attempt + 1}/{max_retries}")
                
                # Initialize MT5 API
                if not mt5.initialize():
                    error = mt5.last_error()
                    logger.warning(f"MT5 initialize failed on attempt {attempt + 1}: {error}")
                    
                    if attempt < max_retries - 1:
                        time.sleep(2)  # Wait before retry
                        continue
                    else:
                        return False, {
                            'error': 'MT5 API initialization failed',
                            'details': f"Error: {error}",
                            'solution': 'Check if MT5 terminal is properly installed and running'
                        }
                
                # Attempt login
                authorized = mt5.login(
                    login=int(account_number),
                    password=password,
                    server=server
                )
                
                if authorized:
                    # Success! Get account info
                    account_info = mt5.account_info()
                    terminal_info = mt5.terminal_info()
                    
                    return True, {
                        'status': 'success',
                        'message': 'Automated login successful',
                        'account_info': {
                            'login': account_info.login,
                            'trade_mode': account_info.trade_mode,
                            'balance': account_info.balance,
                            'equity': account_info.equity,
                            'margin': account_info.margin,
                            'currency': account_info.currency,
                            'company': account_info.company,
                            'server': account_info.server,
                        } if account_info else None,
                        'terminal_info': {
                            'build': terminal_info.build,
                            'name': terminal_info.name,
                        } if terminal_info else None,
                        'automation_used': True
                    }
                else:
                    error = mt5.last_error()
                    logger.warning(f"MT5 login failed on attempt {attempt + 1}: {error}")
                    
                    if attempt < max_retries - 1:
                        time.sleep(2)  # Wait before retry
                        continue
                    else:
                        mt5.shutdown()
                        return False, {
                            'error': 'Login failed after retries',
                            'details': f"Error: {error}",
                            'solution': 'Check credentials and server name. Try logging in manually first.'
                        }
            
        except Exception as e:
            logger.error(f"Auto-login process failed: {e}")
            try:
                mt5.shutdown()
            except:
                pass
            return False, {
                'error': 'Automated login process failed',
                'details': str(e),
                'solution': 'Try manual login or check system requirements'
            }
    
    @staticmethod
    def get_status() -> Dict:
        """Get current status of MT5 terminal and API"""
        status = {
            'mt5_terminal_running': MT5AutoManager.is_mt5_running(),
            'mt5_executable_found': MT5AutoManager.find_mt5_executable() is not None,
            'mt5_api_initialized': False,
            'logged_in': False,
            'account_info': None
        }
        
        try:
            # Test MT5 API
            if mt5.initialize():
                status['mt5_api_initialized'] = True
                
                # Check if logged in
                account_info = mt5.account_info()
                if account_info:
                    status['logged_in'] = True
                    status['account_info'] = {
                        'login': account_info.login,
                        'server': account_info.server,
                        'company': account_info.company
                    }
                
                mt5.shutdown()
        except Exception as e:
            logger.error(f"Status check failed: {e}")
        
        return status


class MT5SmartConnection:
    """Smart MT5 connection that tries automation first, falls back to manual"""
    
    @staticmethod
    def connect(account_number: str, password: str, server: str) -> Tuple[bool, Dict]:
        """
        Smart connection strategy:
        1. Try automated login (start terminal + login)
        2. If that fails, provide helpful guidance for manual setup
        """
        
        # First, try automated approach
        logger.info("Attempting automated MT5 connection...")
        success, result = MT5AutoManager.auto_login(account_number, password, server)
        
        if success:
            logger.info("Automated connection successful!")
            return True, result
        
        # If automation failed, check what's needed for manual setup
        logger.info("Automated connection failed, checking manual setup requirements...")
        status = MT5AutoManager.get_status()
        
        guidance = {
            'status': 'requires_manual_setup',
            'error': result.get('error'),
            'automation_failed': True,
            'manual_steps': []
        }
        
        if not status['mt5_executable_found']:
            guidance['manual_steps'].append({
                'step': 1,
                'action': 'Install MetaTrader 5',
                'description': 'Download and install MT5 from your broker (Exness)',
                'url': 'https://www.exness.com/trading-platforms/metatrader5/'
            })
        
        if not status['mt5_terminal_running']:
            guidance['manual_steps'].append({
                'step': 2,
                'action': 'Start MT5 Terminal',
                'description': 'Open MetaTrader 5 application manually'
            })
        
        if not status['logged_in']:
            guidance['manual_steps'].append({
                'step': 3,
                'action': 'Login to MT5',
                'description': f'Login manually with: Account: {account_number}, Server: {server}',
                'note': 'After manual login, try connecting again in the web app'
            })
        
        guidance['manual_steps'].append({
            'step': 4,
            'action': 'Enable Algo Trading',
            'description': 'In MT5: Tools → Options → Expert Advisors → Enable "Allow algorithmic trading"'
        })
        
        return False, guidance
