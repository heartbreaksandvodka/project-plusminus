import MetaTrader5 as mt5
from django.conf import settings
import logging
from datetime import datetime
from typing import Dict, Optional, Tuple
from .models import MT5Account
from .mt5_auto_manager import MT5SmartConnection, MT5AutoManager

# Alias for backward compatibility with tests
MT5TerminalManager = MT5AutoManager
import subprocess
import signal
import os
import sys


logger = logging.getLogger(__name__)


class MT5ConnectionManager:
    """Manages MetaTrader 5 connections and operations"""
    
    @staticmethod
    def test_connection(account_number: str, password: str, server: str) -> Tuple[bool, Dict]:
        """
        Test MT5 connection with automated terminal management
        Returns: (success: bool, data: dict)
        """
        try:
            # Use smart connection that handles automation
            success, result = MT5SmartConnection.connect(account_number, password, server)
            
            if success:
                logger.info("MT5 connection test successful")
                return True, result
            else:
                logger.warning("MT5 connection test failed")
                return False, result
                
        except Exception as e:
            logger.error(f"MT5 connection test failed: {str(e)}")
            try:
                mt5.shutdown()
            except:
                pass
            return False, {
                'error': 'Connection test failed',
                'details': str(e),
                'solution': 'Check MT5 installation and try again'
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
    def _get_project_root() -> str:
        # backend/mt5_integration/ -> backend -> project root
        return os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))

    @staticmethod
    def _get_algorithms_dir() -> str:
        # Prefer settings.ALGORITHMS_DIR; fallback to <project_root>/ALGORITHMSMT5EA
        try:
            base = getattr(settings, 'ALGORITHMS_DIR', None)
        except Exception:
            base = None
        if not base:
            base = os.path.join(MT5AlgorithmManager._get_project_root(), 'ALGORITHMSMT5EA')
        return base

    @staticmethod
    def _get_ea_script_path(algorithm_name: str) -> str:
        # EAs follow convention: <algoname>/mt5_<algoname>.py
        ea_dir = os.path.join(MT5AlgorithmManager._get_algorithms_dir(), algorithm_name)
        script = f"mt5_{algorithm_name}.py"
        return os.path.join(ea_dir, script)
    @staticmethod
    def start_algorithm(mt5_account: MT5Account, algorithm_name: str, symbol: str) -> Dict:
        """
        Actually launch the EA script as a subprocess and store its PID.
        Passes the user's MT5 account credentials as environment variables.
        """
        try:
            ea_script_path = MT5AlgorithmManager._get_ea_script_path(algorithm_name)
            if not os.path.isfile(ea_script_path):
                return {
                    'status': 'error',
                    'message': f'EA script not found for {algorithm_name}',
                    'details': ea_script_path
                }

            # Ensure Python can import the ALGORITHMSMT5EA package
            project_root = MT5AlgorithmManager._get_project_root()
            env = os.environ.copy()
            existing_pp = env.get('PYTHONPATH', '')
            env['PYTHONPATH'] = (project_root + (os.pathsep + existing_pp if existing_pp else ''))

            # Pass MT5 account credentials as environment variables for the EA to use
            env['MT5_ACCOUNT_NUMBER'] = str(mt5_account.account_number)
            env['MT5_PASSWORD'] = mt5_account.get_password()
            env['MT5_SERVER'] = mt5_account.server
            env['MT5_BROKER_NAME'] = mt5_account.broker_name
            env['MT5_ACCOUNT_ID'] = str(mt5_account.id)

            # Prefer current interpreter
            python_exec = sys.executable or 'python'

            # Start the EA
            cmd = [python_exec, ea_script_path]
            if symbol:
                cmd.append(symbol)
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=project_root,
                env=env,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if hasattr(subprocess, 'CREATE_NEW_PROCESS_GROUP') else 0
            )
            pid = process.pid
            return {
                'status': 'success',
                'message': f'Algorithm {algorithm_name} started successfully',
                'pid': pid,
                'algorithm_id': f"{algorithm_name}_{symbol}_{mt5_account.id}_{datetime.now().timestamp()}"
            }
        except Exception as e:
            logger.error(f"Failed to start algorithm: {str(e)}")
            return {
                'status': 'error',
                'message': 'Failed to start algorithm',
                'details': str(e)
            }

    

    @staticmethod
    def pause_algorithm(pid: int, algorithm_name: str = None) -> dict:
        """
        Pause a running EA subprocess by creating a pause.flag file in the EA directory.
        """
        try:
            if algorithm_name:
                # Use the EA folder name (e.g., candy_ea, grid_trading_ea)
                ea_dir = os.path.join(MT5AlgorithmManager._get_algorithms_dir(), algorithm_name)
                pause_flag_path = os.path.join(ea_dir, "pause.flag")
                with open(pause_flag_path, 'w') as f:
                    f.write('paused')
                return {
                    'status': 'success',
                    'message': 'Algorithm paused successfully (pause.flag created)'
                }
            else:
                return {
                    'status': 'error',
                    'message': 'Algorithm name required for pause on Windows.'
                }
        except Exception as e:
            logger.error(f"Failed to pause algorithm: {str(e)}")
            return {
                'status': 'error',
                'message': 'Failed to pause algorithm',
                'details': str(e)
            }

    @staticmethod
    def resume_algorithm(pid: int, algorithm_name: str = None) -> Dict:
        """
        Resume a paused EA subprocess by deleting the pause.flag file in the EA directory.
        """
        try:
            if algorithm_name:
                ea_dir = os.path.join(MT5AlgorithmManager._get_algorithms_dir(), algorithm_name)
                pause_flag_path = os.path.join(ea_dir, "pause.flag")
                if os.path.exists(pause_flag_path):
                    os.remove(pause_flag_path)
                return {
                    'status': 'success',
                    'message': 'Algorithm resumed successfully (pause.flag removed)'
                }
            else:
                return {
                    'status': 'error',
                    'message': 'Algorithm name required for resume on Windows.'
                }
        except Exception as e:
            logger.error(f"Failed to resume algorithm: {str(e)}")
            return {
                'status': 'error',
                'message': 'Failed to resume algorithm',
                'details': str(e)
            }

    @staticmethod
    def stop_algorithm(pid: int) -> Dict:
        """
        Stop a running EA subprocess by terminating the process. Windows-friendly.
        """
        try:
            if os.name == 'nt':
                try:
                    # Attempt graceful termination
                    os.kill(pid, signal.SIGTERM)
                except Exception:
                    # Fallback to taskkill if needed
                    subprocess.run(['taskkill', '/PID', str(pid), '/F', '/T'], check=False,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            else:
                # POSIX: try SIGTERM, then SIGKILL
                try:
                    os.kill(pid, signal.SIGTERM)
                except Exception:
                    os.kill(pid, signal.SIGKILL)
            return {
                'status': 'success',
                'message': 'Algorithm stopped successfully'
            }
        except Exception as e:
            logger.error(f"Failed to stop algorithm PID {pid}: {str(e)}")
            return {
                'status': 'error',
                'message': 'Failed to stop algorithm',
                'details': str(e)
            }
