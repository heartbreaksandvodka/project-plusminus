import MetaTrader5 as mt5
import os
import time
import logging
import threading
import queue
from datetime import datetime
from typing import Optional, Dict, Any, Callable
from websocket_client import create_algorithm_websocket_client

# Import dynamic credentials
try:
    from dynamic_credentials import get_mt5_credentials_from_db, initialize_mt5_dynamic
    DYNAMIC_CREDENTIALS_AVAILABLE = True
except ImportError:
    DYNAMIC_CREDENTIALS_AVAILABLE = False
    print("Warning: Dynamic credentials not available, falling back to global config")

# Fallback to global config if dynamic credentials are not available
try:
    from global_config import get_account_credentials
except ImportError:
    print("Warning: Global config not available")


class EnhancedEABase:
    """Enhanced base class for EAs with WebSocket integration"""
    
    def __init__(self, algorithm_name: str, config: Dict[str, Any]):
        self.algorithm_name = algorithm_name
        self.config = config
        self.is_running = False
        self.is_paused = False
        self.trade_count = 0
        self.total_profit = 0.0
        self.positions = {}
        self.logger = logging.getLogger(algorithm_name)
        
        # WebSocket components
        self.ws_client = None
        self.status_reporter = None
        self.command_handler = None
        self.websocket_enabled = config.get('websocket_enabled', True)
        
        # Performance tracking
        self.performance_data = {
            'start_time': None,
            'trades_opened': 0,
            'trades_closed': 0,
            'total_profit': 0.0,
            'current_drawdown': 0.0,
            'max_drawdown': 0.0,
            'peak_balance': 0.0
        }
        
        # Setup logging
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup enhanced logging"""
        log_filename = f"{self.algorithm_name}.log"
        log_path = os.path.join(os.path.dirname(__file__), log_filename)
        
        handler = logging.FileHandler(log_path)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def initialize_websocket(self, backend_url: str, algorithm_id: str, auth_token: str):
        """Initialize WebSocket connection to backend"""
        if not self.websocket_enabled:
            self.logger.info("WebSocket integration disabled")
            return
        
        try:
            self.ws_client, self.status_reporter, self.command_handler = create_algorithm_websocket_client(
                backend_url, algorithm_id, auth_token
            )
            
            # Register command handlers
            self._setup_command_handlers()
            
            # Set connection callbacks
            self.ws_client.set_callbacks(
                on_connect=self._on_websocket_connect,
                on_disconnect=self._on_websocket_disconnect,
                on_error=self._on_websocket_error
            )
            
            # Start WebSocket client
            self.ws_client.start()
            self.logger.info("WebSocket integration initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize WebSocket: {e}")
            self.websocket_enabled = False
    
    def _setup_command_handlers(self):
        """Setup command handlers for WebSocket"""
        if not self.command_handler:
            return
            
        self.command_handler.register_command_handler('pause', self._handle_pause_command)
        self.command_handler.register_command_handler('resume', self._handle_resume_command)
        self.command_handler.register_command_handler('stop', self._handle_stop_command)
        self.command_handler.register_command_handler('update_config', self._handle_config_update)
        self.command_handler.register_command_handler('get_status', self._handle_status_request)
    
    def _handle_pause_command(self, data):
        """Handle pause command from backend"""
        self.pause_trading()
        if self.status_reporter:
            self.status_reporter.report_status_update('paused', 'Algorithm paused by user command')
    
    def _handle_resume_command(self, data):
        """Handle resume command from backend"""
        self.resume_trading()
        if self.status_reporter:
            self.status_reporter.report_status_update('running', 'Algorithm resumed by user command')
    
    def _handle_stop_command(self, data):
        """Handle stop command from backend"""
        self.stop_trading()
        if self.status_reporter:
            self.status_reporter.report_status_update('stopped', 'Algorithm stopped by user command')
    
    def _handle_config_update(self, data):
        """Handle configuration update from backend"""
        config_updates = data.get('config_updates', {})
        self.update_configuration(config_updates)
        if self.status_reporter:
            self.status_reporter.report_status_update('running', 'Configuration updated')
    
    def _handle_status_request(self, data):
        """Handle status request from backend"""
        if self.status_reporter:
            status = 'running' if self.is_running and not self.is_paused else 'paused' if self.is_paused else 'stopped'
            self.status_reporter.report_status_update(status, 'Status requested', self.get_performance_data())
    
    def _on_websocket_connect(self):
        """WebSocket connection established"""
        self.logger.info("WebSocket connected to backend")
        if self.status_reporter:
            status = 'running' if self.is_running and not self.is_paused else 'paused' if self.is_paused else 'stopped'
            self.status_reporter.report_status_update(status, 'WebSocket connected')
    
    def _on_websocket_disconnect(self):
        """WebSocket connection lost"""
        self.logger.warning("WebSocket disconnected from backend")
    
    def _on_websocket_error(self, error):
        """WebSocket error occurred"""
        self.logger.error(f"WebSocket error: {error}")
    
    def start_trading(self):
        """Start the trading algorithm"""
        self.is_running = True
        self.is_paused = False
        self.performance_data['start_time'] = datetime.now()
        self.logger.info(f"{self.algorithm_name} started")
        
        if self.status_reporter:
            self.status_reporter.report_status_update('running', 'Algorithm started')
    
    def pause_trading(self):
        """Pause the trading algorithm"""
        self.is_paused = True
        self.logger.info(f"{self.algorithm_name} paused")
        
        if self.status_reporter:
            self.status_reporter.report_status_update('paused', 'Algorithm paused')
    
    def resume_trading(self):
        """Resume the trading algorithm"""
        self.is_paused = False
        self.logger.info(f"{self.algorithm_name} resumed")
        
        if self.status_reporter:
            self.status_reporter.report_status_update('running', 'Algorithm resumed')
    
    def stop_trading(self):
        """Stop the trading algorithm"""
        self.is_running = False
        self.is_paused = False
        self.logger.info(f"{self.algorithm_name} stopped")
        
        if self.status_reporter:
            self.status_reporter.report_status_update('stopped', 'Algorithm stopped')
        
        # Close WebSocket connection
        if self.ws_client:
            self.ws_client.stop()
    
    def update_configuration(self, config_updates: Dict[str, Any]):
        """Update algorithm configuration"""
        self.config.update(config_updates)
        self.logger.info(f"Configuration updated: {config_updates}")
    
    def report_trade_opened(self, trade_data: Dict[str, Any]):
        """Report trade opened to backend"""
        self.performance_data['trades_opened'] += 1
        self.trade_count += 1
        
        # Store position info
        ticket = trade_data.get('ticket')
        if ticket:
            self.positions[ticket] = trade_data
        
        self.logger.info(f"Trade opened: {trade_data}")
        
        if self.status_reporter:
            self.status_reporter.report_trade_opened(trade_data)
    
    def report_trade_closed(self, trade_data: Dict[str, Any]):
        """Report trade closed to backend"""
        self.performance_data['trades_closed'] += 1
        profit = trade_data.get('profit', 0.0)
        self.total_profit += profit
        self.performance_data['total_profit'] = self.total_profit
        
        # Update drawdown tracking
        self._update_drawdown_tracking(profit)
        
        # Remove from positions
        ticket = trade_data.get('ticket')
        if ticket and ticket in self.positions:
            del self.positions[ticket]
        
        self.logger.info(f"Trade closed: {trade_data}")
        
        if self.status_reporter:
            self.status_reporter.report_trade_closed(trade_data)
    
    def report_signal_generated(self, signal_data: Dict[str, Any]):
        """Report trading signal generated"""
        self.logger.info(f"Signal generated: {signal_data}")
        
        if self.status_reporter:
            self.status_reporter.report_signal_generated(signal_data)
    
    def report_error(self, error_message: str, error_data: Dict[str, Any] = None):
        """Report error to backend"""
        self.logger.error(f"Error: {error_message}")
        
        if self.status_reporter:
            self.status_reporter.report_error(error_message, error_data)
    
    def send_heartbeat(self):
        """Send heartbeat with performance data"""
        if self.status_reporter:
            self.status_reporter.report_heartbeat(self.get_performance_data())
    
    def get_performance_data(self) -> Dict[str, Any]:
        """Get current performance data"""
        runtime = 0
        if self.performance_data['start_time']:
            runtime = (datetime.now() - self.performance_data['start_time']).total_seconds()
        
        return {
            **self.performance_data,
            'runtime_seconds': runtime,
            'current_positions': len(self.positions),
            'is_running': self.is_running,
            'is_paused': self.is_paused
        }
    
    def _update_drawdown_tracking(self, profit: float):
        """Update drawdown tracking with new profit/loss"""
        self.performance_data['peak_balance'] = max(
            self.performance_data['peak_balance'], 
            self.performance_data['total_profit']
        )
        
        current_drawdown = self.performance_data['peak_balance'] - self.performance_data['total_profit']
        self.performance_data['current_drawdown'] = current_drawdown
        self.performance_data['max_drawdown'] = max(
            self.performance_data['max_drawdown'], 
            current_drawdown
        )
    
    def check_pause_status(self):
        """Check if algorithm should pause (WebSocket-aware)"""
        if self.websocket_enabled:
            # With WebSocket, pause status is managed by command handlers
            return self.is_paused
        else:
            # Fallback to file-based pause checking
            return self._check_file_pause()
    
    def _check_file_pause(self) -> bool:
        """Legacy file-based pause checking"""
        ea_dir = os.path.dirname(os.path.abspath(__file__))
        pause_flag_path = os.path.join(ea_dir, 'pause.flag')
        
        if os.path.exists(pause_flag_path):
            if not self.is_paused:
                self.logger.info("Pause flag detected - pausing EA")
                self.is_paused = True
            return True
        else:
            if self.is_paused:
                self.logger.info("Pause flag removed - resuming EA")
                self.is_paused = False
            return False


# Legacy functions for backward compatibility

# Enhanced initialization functions

def initialize_mt5_dynamic():
    """
    Initialize MT5 with dynamic credentials from database or environment variables
    This is the preferred method for EAs started through the web interface
    """
    if DYNAMIC_CREDENTIALS_AVAILABLE:
        try:
            from dynamic_credentials import get_mt5_credentials_from_db
            
            # Get credentials with priority: Environment Variables > Database > Global Config
            credentials = get_mt5_credentials_from_db()
            
            print(f"Attempting to connect to MT5 with account: {credentials['login']} on server: {credentials['server']}")
            
            # Initialize MT5
            if not mt5.initialize():
                error_msg = f"Failed to initialize MT5: {mt5.last_error()}"
                print(error_msg)
                return False
            
            # Login to account
            if not mt5.login(
                login=credentials['login'],
                password=credentials['password'],
                server=credentials['server']
            ):
                error_msg = f"Failed to login to MT5 account {credentials['login']}: {mt5.last_error()}"
                print(error_msg)
                mt5.shutdown()
                return False
            
            # Get account info to verify connection
            account_info = mt5.account_info()
            if account_info is None:
                error_msg = "Connected but could not retrieve account info"
                print(error_msg)
                mt5.shutdown()
                return False
            
            print(f"✅ Successfully connected to MT5")
            print(f"Account: {account_info.login}")
            print(f"Balance: {account_info.balance}")
            print(f"Server: {account_info.server}")
            print(f"Broker: {credentials.get('broker_name', 'Unknown')}")
            
            return True
            
        except Exception as e:
            print(f"Dynamic initialization failed: {e}")
            print("Falling back to legacy method...")
    
    # Fallback to global config
    try:
        creds = get_account_credentials()
        return initialize_mt5(creds['login'], creds['password'], creds['server'])
    except Exception as e:
        print(f"Failed to initialize MT5: {e}")
        return False

def initialize_mt5(login, password, server):
    """
    Legacy MT5 initialization function with explicit parameters
    """
    if not mt5.initialize():
        logging.error("MetaTrader 5 initialization failed")
        print("MetaTrader 5 initialization failed")
        print("Error code:", mt5.last_error())
        return False
    if login and password and server:
        authorized = mt5.login(login, password=password, server=server)
        if not authorized:
            logging.error("Login failed")
            print("Login failed")
            print("Error code:", mt5.last_error())
            return False
    logging.info("MetaTrader 5 initialized and logged in.")
    print("MetaTrader 5 initialized and logged in.")
    return True

def get_symbol_info(symbol):
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        print(f"Symbol {symbol} not found")
        return None
    if not symbol_info.visible:
        mt5.symbol_select(symbol, True)
    return symbol_info

def get_current_price(symbol):
    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        return None, None
    return tick.bid, tick.ask

def check_pause_flag(ea_dir):
    """Legacy pause flag checking - deprecated, use EA.check_pause_status() instead"""
    pause_flag_path = os.path.join(ea_dir, 'pause.flag')
    if os.path.exists(pause_flag_path):
        print("EA paused. Waiting for resume...")
        logging.info("EA paused. Waiting for resume...")
        while os.path.exists(pause_flag_path):
            time.sleep(5)
        print("EA resumed.")
        logging.info("EA resumed.")
