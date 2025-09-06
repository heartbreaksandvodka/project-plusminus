# ALGORITHMSMT5EA Architecture Guide
## Expert Advisor Collection & Execution Framework

### 🏗️ **Architecture Overview**
```
┌─────────────────────────────────────────────────┐
│             ALGORITHMSMT5EA                     │
│              (Subprocess Layer)                 │
│  ┌─────────────────────────────────────────┐    │
│  │           EA Collection                 │    │
│  │  10 Expert Advisors + Common Base     │    │
│  └─────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────┐    │
│  │        Common Framework                │    │
│  │   Shared Logic & Utilities            │    │
│  └─────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────┐    │
│  │         MT5 Integration                │    │
│  │     MetaTrader 5 Python API          │    │
│  └─────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────┐    │
│  │       Control Systems                  │    │
│  │  File-based + WebSocket Control       │    │
│  └─────────────────────────────────────────┘    │
└─────────────────────────────────────────────────┘
```

### 📁 **Folder Structure**
```
ALGORITHMSMT5EA/
├── common_ea.py              # Shared EA base classes
├── dynamic_credentials.py    # Credential management
├── websocket_client.py      # WebSocket communication
├── global_config.py         # Global configuration
├── requirements.txt         # Python dependencies
├── start_ea.bat            # Windows EA launcher
├── README.md               # Main documentation
├── test_*.py               # Testing utilities
│
├── trailing_stop_ea/        # Risk-based trailing stop
│   ├── config.py
│   ├── launcher.py
│   └── mt5_trailing_stop_ea.py
│
├── grid_trading_ea/         # Grid trading system
│   ├── config.py
│   ├── launcher.py
│   └── mt5_grid_trading_ea.py
│
├── trend_following_ea/      # Trend following strategy
│   ├── config.py
│   ├── launcher.py
│   └── mt5_trend_following_ea.py
│
├── hf_scalping_ea/         # High-frequency scalping
│   ├── config.py
│   ├── launcher.py
│   └── mt5_hf_scalping_ea.py
│
├── news_ea/                # News-based trading
│   ├── config.py
│   ├── launcher.py
│   ├── mt5_news_ea.py
│   └── news_api.py
│
├── smart_hedging_ea/       # Smart hedging system
│   ├── config.py
│   ├── launcher.py
│   └── mt5_smart_hedging_ea.py
│
├── liquidity_ea/           # Liquidity provision
│   ├── config.py
│   ├── launcher.py
│   └── mt5_liquidity_ea.py
│
├── candy_ea/               # Candy pattern trading
│   ├── config.py
│   ├── launcher.py
│   └── mt5_candy_ea.py
│
├── indices_hedging_ea/     # Index hedging
│   ├── config.py
│   ├── launcher.py
│   └── mt5_indices_hedging_ea.py
│
└── indices_martingale_ea/  # Martingale indices
    ├── config.py
    ├── launcher.py
    └── mt5_indices_martingale_ea.py
```

### 🧬 **Common Framework**

#### **1. Enhanced EA Base Class (common_ea.py)**
```python
class EnhancedEABase:
    """Enhanced base class for EAs with WebSocket integration"""
    
    def __init__(self, algorithm_name: str, config: Dict[str, Any]):
        self.algorithm_name = algorithm_name
        self.config = config
        self.is_running = False
        self.is_paused = False
        self.logger = logging.getLogger(algorithm_name)
        self.status_reporter = None
        self.ws_client = None
    
    def initialize_mt5(self) -> bool:
        # MT5 initialization with error handling
        
    def start_trading(self):
        # Start main trading loop
        
    def pause_trading(self):
        # Pause algorithm execution
        
    def resume_trading(self):
        # Resume algorithm execution
        
    def stop_trading(self):
        # Stop algorithm and cleanup
        
    def check_pause_flag(self):
        # Check for pause.flag file
```

#### **2. Dynamic Credential System (dynamic_credentials.py)**
```python
def get_dynamic_mt5_credentials():
    """Get MT5 credentials from environment variables"""
    try:
        credentials = {
            'login': int(os.environ['MT5_ACCOUNT_NUMBER']),
            'password': os.environ['MT5_PASSWORD'],
            'server': os.environ['MT5_SERVER'],
            'timeout': 60000,
            'portable': False
        }
        return credentials
    except KeyError as e:
        # Fallback to config file
        return get_fallback_credentials()
```

#### **3. WebSocket Communication (websocket_client.py)**
```python
def setup_ea_websocket_integration(ea_instance, backend_url: str, algorithm_id: str, auth_token: str):
    """Setup WebSocket communication with backend"""
    
    def on_message(message):
        # Handle WebSocket messages
        if message['type'] == 'pause':
            ea_instance.pause_trading()
        elif message['type'] == 'resume':
            ea_instance.resume_trading()
        elif message['type'] == 'stop':
            ea_instance.stop_trading()
    
    def on_connect():
        # Report EA status on connection
        status_reporter.report_status_update('running', 'EA connected')
    
    # Start WebSocket client
    ws_client = WebSocketClient(backend_url, algorithm_id, auth_token)
    ws_client.on_message = on_message
    ws_client.on_connect = on_connect
    return ws_client
```

### 🤖 **Expert Advisor Collection**

#### **1. Trailing Stop EA**
```python
# Strategy: Risk-based position management
class TrailingStopManager:
    def __init__(self):
        self.risk_percentage = 10.0  # 10% account risk
        self.symbol = "EURUSD"
        self.magic_number = 12345
    
    def calculate_stop_loss(self, position_size, account_balance):
        # Dynamic stop loss based on account balance
        
    def update_trailing_stops(self):
        # Update existing position stop losses
```

#### **2. Grid Trading EA**
```python
# Strategy: Systematic grid placement
class GridTradingEA:
    def __init__(self):
        self.grid_spacing = 50  # pips
        self.max_levels = 10
        self.base_lot_size = 0.01
    
    def place_grid_orders(self):
        # Place buy/sell orders at grid levels
        
    def manage_grid(self):
        # Manage existing grid positions
```

#### **3. High-Frequency Scalping EA**
```python
# Strategy: Sub-minute scalping
class HighFrequencyScalpingEA:
    def __init__(self):
        self.timeframe = mt5.TIMEFRAME_M1
        self.spread_filter = 2.0
        self.profit_target = 5  # pips
    
    def analyze_tick_data(self):
        # Real-time tick analysis
        
    def execute_scalp_trade(self):
        # High-speed trade execution
```

#### **4. News Trading EA**
```python
# Strategy: Economic news impact trading
class NewsEA:
    def __init__(self):
        self.news_api = NewsAPI()
        self.impact_threshold = "high"
    
    def fetch_news_events(self):
        # Get upcoming news events
        
    def trade_news_event(self, event):
        # Execute trades around news releases
```

### 🔄 **Control Systems**

#### **1. File-based Control**
```python
def check_pause_flag(ea_directory: str):
    """Check for pause.flag file in EA directory"""
    pause_flag_path = os.path.join(ea_directory, "pause.flag")
    
    while os.path.exists(pause_flag_path):
        print("⏸️  Algorithm paused (pause.flag detected)")
        time.sleep(1)  # Check every second
        
    return True  # Continue execution
```

#### **2. Process Management**
```python
def signal_handler(signum, frame):
    """Handle termination signals gracefully"""
    global is_running
    print(f"\n🛑 Received signal {signum}, stopping EA...")
    is_running = False
    
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)
```

### 🔌 **MT5 Integration**

#### **1. Connection Management**
```python
def initialize_mt5():
    """Initialize MT5 connection with dynamic credentials"""
    if not mt5.initialize():
        return False
    
    credentials = get_dynamic_mt5_credentials()
    if not mt5.login(**credentials):
        return False
    
    return True
```

#### **2. Trading Operations**
```python
def place_order(symbol: str, order_type: int, volume: float, price: float):
    """Place MT5 order with error handling"""
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": order_type,
        "price": price,
        "magic": MAGIC_NUMBER,
        "comment": f"EA_{algorithm_name}",
    }
    
    result = mt5.order_send(request)
    return result
```

### 🚀 **EA Execution Flow**

#### **1. Standard EA Startup**
```python
def main():
    """Standard EA main function"""
    ea = AlgorithmEA()
    
    if not ea.initialize_mt5():
        print("❌ MT5 initialization failed")
        return
    
    # Setup WebSocket integration
    ws_client = setup_ea_websocket_integration(ea, backend_url, algorithm_id, token)
    
    # Start trading loop
    ea.is_running = True
    try:
        while ea.is_running:
            # Check for pause flag
            check_pause_flag(os.path.dirname(__file__))
            
            # Execute trading logic
            ea.execute_trading_logic()
            
            # Wait before next iteration
            time.sleep(ea.loop_delay)
            
    except KeyboardInterrupt:
        print("EA stopped by user")
    finally:
        ea.stop_trading()
        mt5.shutdown()
```

#### **2. Launcher Scripts**
```python
# launcher.py - Consistent launcher for all EAs
import subprocess
import sys
import os

def launch_ea():
    """Launch EA with proper environment setup"""
    script_path = f"mt5_{os.path.basename(os.getcwd())}.py"
    
    if not os.path.exists(script_path):
        print(f"❌ EA script not found: {script_path}")
        return
    
    print(f"🚀 Starting {script_path}...")
    subprocess.run([sys.executable, script_path])

if __name__ == "__main__":
    launch_ea()
```

### 📊 **Configuration Management**

#### **1. Individual EA Configs**
```python
# config.py - Per-EA configuration
EA_CONFIG = {
    'SYMBOL': 'EURUSD',
    'TIMEFRAME': 'M15',
    'MAGIC_NUMBER': 12345,
    'RISK_PERCENTAGE': 2.0,
    'MAX_POSITIONS': 5,
    'STOP_LOSS_PIPS': 20,
    'TAKE_PROFIT_PIPS': 40
}
```

#### **2. Global Configuration**
```python
# global_config.py - Shared settings
GLOBAL_CONFIG = {
    'DEFAULT_TIMEOUT': 60000,
    'WEBSOCKET_ENABLED': True,
    'LOGGING_LEVEL': 'INFO',
    'BACKEND_URL': 'ws://localhost:8000',
    'STATUS_UPDATE_INTERVAL': 30
}
```

### 🔗 **Integration Points**

#### **With EA Service**
1. **Process Launch**: Started as subprocesses
2. **Environment Variables**: Receive credentials
3. **File Control**: pause.flag system
4. **Process Monitoring**: PID tracking

#### **With Django Backend**
1. **WebSocket**: Real-time communication
2. **Status Updates**: Execution status reporting
3. **Trade Data**: Send trade information
4. **Configuration**: Receive parameter updates

#### **With MT5 Terminal**
1. **API Connection**: Python-MT5 integration
2. **Trade Execution**: Order placement and management
3. **Market Data**: Real-time price feeds
4. **Account Info**: Balance and position data

### 📊 **Data Flow**

#### **Credential Flow**
```
EA Service → Environment Variables → EA Process → MT5 Connection
```

#### **Control Flow**
```
EA Service → pause.flag → EA Process → Pause/Resume
```

#### **Status Flow**
```
EA Process → WebSocket → Django Backend → Frontend
```

### 🛡️ **Error Handling & Recovery**

#### **Connection Recovery**
```python
def ensure_mt5_connection():
    """Ensure MT5 connection is active"""
    if not mt5.terminal_info():
        print("⚠️  MT5 connection lost, reconnecting...")
        if not initialize_mt5():
            return False
    return True
```

#### **Graceful Shutdown**
```python
def cleanup_on_exit():
    """Cleanup resources on EA shutdown"""
    # Close open positions if configured
    # Cancel pending orders
    # Save state data
    # Close WebSocket connection
    # Shutdown MT5 connection
```

### 🎯 **Current Status**

#### **✅ Available EAs (10 Total)**
1. **trailing_stop_ea** - Risk-based position management
2. **grid_trading_ea** - Systematic grid trading
3. **trend_following_ea** - Trend momentum trading
4. **hf_scalping_ea** - High-frequency scalping
5. **news_ea** - Economic news trading
6. **smart_hedging_ea** - Intelligent hedging
7. **liquidity_ea** - Liquidity provision
8. **candy_ea** - Candy pattern recognition
9. **indices_hedging_ea** - Index hedging strategies
10. **indices_martingale_ea** - Martingale on indices

#### **✅ Framework Features**
- Dynamic credential injection
- WebSocket real-time communication
- File-based pause/resume control
- Consistent EA structure
- Error handling and recovery
- Logging and monitoring

#### **🔄 Integration Status**
- EA Service process management ✅
- Django backend communication ✅
- Frontend status display ✅
- Real-time updates ✅

### 🚀 **Advantages**

#### **Modular Design**
- Independent EA development
- Shared common functionality
- Consistent interfaces
- Easy testing and debugging

#### **Production Ready**
- Robust error handling
- Graceful shutdown procedures
- Real-time monitoring
- Flexible configuration

#### **Scalable Architecture**
- Multi-EA execution
- Resource isolation
- Independent failures
- Horizontal scaling potential
