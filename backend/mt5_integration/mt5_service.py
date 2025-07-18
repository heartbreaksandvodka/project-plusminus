import MetaTrader5 as mt5
import logging
from datetime import datetime
from typing import Dict, Optional, Tuple
from .models import MT5Account


logger = logging.getLogger(__name__)


class MT5ConnectionManager:
    """Manages MetaTrader 5 connections and operations"""
    
    @staticmethod
    def test_connection(account_number: str, password: str, server: str) -> Tuple[bool, Dict]:
        """
        Test MT5 connection with provided credentials
        Returns: (success: bool, data: dict)
        """
        try:
            # Initialize MT5
            if not mt5.initialize():
                error = mt5.last_error()
                logger.error(f"MT5 initialization failed: {error}")
                return False, {
                    'error': 'Failed to initialize MetaTrader 5',
                    'details': f"Error code: {error[0]}, Description: {error[1]}" if error else "Unknown error"
                }
            
            # Attempt login
            authorized = mt5.login(
                login=int(account_number),
                password=password,
                server=server
            )
            
            if not authorized:
                error = mt5.last_error()
                mt5.shutdown()
                logger.error(f"MT5 login failed for account {account_number}: {error}")
                return False, {
                    'error': 'Login failed',
                    'details': f"Error code: {error[0]}, Description: {error[1]}" if error else "Invalid credentials"
                }
            
            # Get account info
            account_info = mt5.account_info()
            if account_info is None:
                mt5.shutdown()
                return False, {'error': 'Failed to retrieve account information'}
            
            # Get terminal info
            terminal_info = mt5.terminal_info()
            
            # Logout and shutdown
            mt5.shutdown()
            
            return True, {
                'account_info': {
                    'login': account_info.login,
                    'trade_mode': account_info.trade_mode,
                    'balance': account_info.balance,
                    'equity': account_info.equity,
                    'margin': account_info.margin,
                    'currency': account_info.currency,
                    'company': account_info.company,
                    'server': account_info.server,
                },
                'terminal_info': {
                    'build': terminal_info.build if terminal_info else None,
                    'name': terminal_info.name if terminal_info else None,
                } if terminal_info else None,
                'connection_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"MT5 connection test failed: {str(e)}")
            try:
                mt5.shutdown()
            except:
                pass
            return False, {
                'error': 'Connection test failed',
                'details': str(e)
            }
    
    @staticmethod
    def update_account_status(mt5_account: MT5Account) -> Dict:
        """
        Update MT5 account status and balance information
        Returns: dict with updated information
        """
        try:
            password = mt5_account.get_password()
            success, data = MT5ConnectionManager.test_connection(
                mt5_account.account_number,
                password,
                mt5_account.server
            )
            
            if success:
                account_info = data.get('account_info', {})
                mt5_account.connection_status = 'connected'
                mt5_account.last_connected = datetime.now()
                mt5_account.balance = account_info.get('balance')
                mt5_account.equity = account_info.get('equity')
                mt5_account.margin = account_info.get('margin')
                mt5_account.currency = account_info.get('currency', mt5_account.currency)
                mt5_account.save()
                
                return {
                    'status': 'connected',
                    'message': 'Account connected successfully',
                    'data': account_info
                }
            else:
                mt5_account.connection_status = 'error'
                mt5_account.save()
                
                return {
                    'status': 'error',
                    'message': data.get('error', 'Connection failed'),
                    'details': data.get('details')
                }
                
        except Exception as e:
            logger.error(f"Failed to update account status: {str(e)}")
            mt5_account.connection_status = 'error'
            mt5_account.save()
            
            return {
                'status': 'error',
                'message': 'Failed to check account status',
                'details': str(e)
            }
    
    @staticmethod
    def get_market_data(symbol: str, timeframe: int = mt5.TIMEFRAME_M1, count: int = 100) -> Optional[Dict]:
        """
        Get market data for a specific symbol
        """
        try:
            if not mt5.initialize():
                return None
            
            rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, count)
            mt5.shutdown()
            
            if rates is not None:
                return {
                    'symbol': symbol,
                    'timeframe': timeframe,
                    'rates': rates.tolist() if hasattr(rates, 'tolist') else list(rates)
                }
            return None
            
        except Exception as e:
            logger.error(f"Failed to get market data: {str(e)}")
            try:
                mt5.shutdown()
            except:
                pass
            return None


class MT5AlgorithmManager:
    """Manages algorithm execution on MT5 accounts"""
    
    @staticmethod
    def start_algorithm(mt5_account: MT5Account, algorithm_name: str) -> Dict:
        """
        Start an algorithm on the MT5 account
        """
        try:
            # This would typically involve:
            # 1. Connecting to MT5
            # 2. Loading the EA/algorithm
            # 3. Starting execution
            # 4. Monitoring the process
            
            # For now, we'll simulate the process
            return {
                'status': 'success',
                'message': f'Algorithm {algorithm_name} started successfully',
                'algorithm_id': f"{algorithm_name}_{mt5_account.id}_{datetime.now().timestamp()}"
            }
            
        except Exception as e:
            logger.error(f"Failed to start algorithm: {str(e)}")
            return {
                'status': 'error',
                'message': 'Failed to start algorithm',
                'details': str(e)
            }
    
    @staticmethod
    def stop_algorithm(algorithm_execution_id: str) -> Dict:
        """
        Stop a running algorithm
        """
        try:
            # Implementation for stopping algorithm
            return {
                'status': 'success',
                'message': 'Algorithm stopped successfully'
            }
            
        except Exception as e:
            logger.error(f"Failed to stop algorithm: {str(e)}")
            return {
                'status': 'error',
                'message': 'Failed to stop algorithm',
                'details': str(e)
            }
