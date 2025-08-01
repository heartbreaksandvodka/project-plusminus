# MetaTrader 5 Grid Trading Expert Advisor

A sophisticated Python-based Expert Advisor that implements a systematic grid trading strategy for MetaTrader 5. This EA profits from market volatility by placing buy and sell orders at regular intervals above and below the current price.

## 🎯 Strategy Overview

Grid trading is a systematic approach that:
- Places **buy orders below** the current market price
- Places **sell orders above** the current market price  
- Profits when the market oscillates between grid levels
- Works best in **ranging/sideways markets**
- Can be risky in **strong trending markets**

## ⚠️ Risk Warning

**Grid trading involves significant risks:**
- Can open many positions simultaneously
- Requires substantial margin and capital
- Can amplify losses in trending markets
- Best suited for ranging markets
- **Always test on demo account first**
- **Never risk more than you can afford to lose**

## 🚀 Features


## 🚀 Features

- **Automatic Grid Management**: Dynamically places and manages grid levels
- **Smart Accumulative Risk Management**: Global stop loss and trailing take profit based on total floating P&L
- **Max Orders Limit**: Caps the total number of open grid orders (pending + positions)
- **Centralized Position Sizing**: All order sizes are calculated by a risk manager
- **Position Monitoring**: Real-time tracking of grid performance
- **Emergency Stop**: Quick closure of all positions and orders
- **Flexible Configuration**: Easy customization via config file or EA parameters
- **Comprehensive Testing**: Full test suite for validation
- **1-Minute Execution**: Updates grid positions every minute for responsive management

## 📋 Prerequisites

1. **MetaTrader 5 Terminal** installed and running
2. **Python 3.7+** with required packages (already configured in root)
3. **MT5 Trading Account** (demo recommended for testing)
4. **Sufficient Account Balance** (minimum $1000 recommended)
5. **Algorithmic Trading Enabled** in MT5

## 📁 Files Structure

```
grid_trading_ea/
├── mt5_grid_trading_ea.py    # Main EA script

## ⚙️ Configuration & Main Parameters

You can configure the EA via `config.py` or directly via the `GridTradingEA` class parameters:

```python
ea = GridTradingEA(
    symbol="ETHUSD",                # Trading symbol
    grid_distance=500,               # Distance between grid levels (points)
    max_levels=5,                    # Number of grid levels above/below price
    magic_number=54321,              # Unique identifier for EA trades
    max_loss_usd=100,                # Global stop loss (close all if floating loss <= -100 USD)
    trail_profit_start_usd=100,      # Start trailing profit when floating profit >= 100 USD
    trail_profit_step_usd=50,        # Trail profit by 50 USD (close all if profit falls back by this amount)
    max_orders=10                    # Maximum open grid orders (pending + positions)
)
ea.run()
```

**Key Risk Controls:**
- No per-order stop loss: All risk is managed globally.
- Global stop loss: All positions/orders are closed if floating loss exceeds `max_loss_usd`.
- Trailing take profit: If floating profit exceeds `trail_profit_start_usd`, a trailing take profit is activated.
- Max orders: The EA will never have more than `max_orders` open (pending + positions).
├── config.py                 # Configuration settings
├── test_ea.py                # Connection and functionality tests
├── trading_test.py           # Order placement tests
├── launcher.py               # Interactive launcher menu
├── start_ea.bat             # Windows batch launcher
└── README.md                # This documentation
```

### How Profits are Made
1. Market moves down → Buy orders fill
2. Market moves back up → Take profits trigger
3. Market moves up → Sell orders fill
4. Market moves back down → Take profits trigger

### How Risk is Managed
- If total floating loss drops below the global stop loss, all positions and orders are closed.
- If total floating profit exceeds the trailing profit start, a trailing take profit is activated. If profit falls back by the trail step, all positions and orders are closed.
- The number of open grid orders is always capped by `max_orders`.

## ⚙️ Configuration


## 🔧 Customization Options

- **Grid Distance**: Adjust based on average daily range and volatility
- **Max Levels**: More levels = more positions = higher risk
- **Lot Size**: Controlled by the risk manager, scale based on account size
- **Max Orders**: Set a hard cap on total grid exposure
- **Global Risk Controls**: Tune `max_loss_usd`, `trail_profit_start_usd`, and `trail_profit_step_usd` for your risk appetite
# Grid Parameters
**Remember**: Grid trading is a sophisticated strategy that requires understanding and proper risk management. This EA now includes smart, accumulative risk controls and a max orders cap for safer grid trading. Always test thoroughly on a demo account before live trading!
LOT_SIZE = 0.01          # Lot size per grid level
GRID_DISTANCE = 50       # Distance between levels (points)
MAX_LEVELS = 5           # Levels above/below price

# Risk Management
MAX_TOTAL_LOTS = 1.0     # Maximum total exposure
MIN_FREE_MARGIN = 1000   # Minimum margin required
EMERGENCY_STOP_LOSS = 500 # Emergency stop level
```

## 🚀 How to Use

### Option 1: Interactive Launcher
```bash
cd grid_trading_ea
C:/Python313/python.exe launcher.py
```
Or double-click `start_ea.bat`

### Option 2: Direct Commands
```bash
# Test connection first
C:/Python313/python.exe -c "from mt5_grid_trading_ea import test_connection; test_connection()"

# Run tests
C:/Python313/python.exe test_ea.py

# Run the EA
C:/Python313/python.exe mt5_grid_trading_ea.py
```

## 📊 Grid Strategy Details

### Grid Placement
- **Buy Levels**: Placed below current price at regular intervals
- **Sell Levels**: Placed above current price at regular intervals
- **Take Profit**: Set at the next grid level (automatic profit taking)

### Example Grid (50-point distance):
```
Current Price: 1.1000

Sell Levels (above):
├── 1.1050 (TP: 1.1000)
├── 1.1100 (TP: 1.1050)
└── 1.1150 (TP: 1.1100)

Buy Levels (below):
├── 1.0950 (TP: 1.1000)
├── 1.0900 (TP: 1.0950)
└── 1.0850 (TP: 1.0900)
```

### How Profits are Made
1. Market moves down → Buy orders fill
2. Market moves back up → Take profits trigger
3. Market moves up → Sell orders fill  
4. Market moves back down → Take profits trigger

## 🧪 Testing

### 1. Connection Test
```bash
C:/Python313/python.exe -c "from mt5_grid_trading_ea import test_connection; test_connection()"
```

### 2. Full Test Suite
```bash
C:/Python313/python.exe test_ea.py
```

### 3. Order Placement Test
```bash
C:/Python313/python.exe trading_test.py
```

### 4. Grid Simulation (No Real Orders)
```bash
C:/Python313/python.exe -c "from test_ea import test_grid_simulation; test_grid_simulation()"
```

## 📈 Best Practices

### Market Conditions
- ✅ **Good**: Ranging/sideways markets with regular oscillations
- ⚠️ **Caution**: Low volatility or very high volatility periods  
- ❌ **Avoid**: Strong trending markets (up or down)

### Risk Management
- Start with **small lot sizes** (0.01)
- Ensure **adequate free margin** (>$1000)
- Monitor **spread conditions** (<5 points preferred)
- Set **conservative grid distances** (50+ points)
- Use **maximum level limits** (5-10 levels)

### Account Requirements
- **Minimum Balance**: $1000+ recommended
- **Leverage**: 1:100 or higher
- **Spread**: Low spread pairs (EURUSD, GBPUSD)
- **Execution**: Fast execution environment

## 🛠️ Launcher Menu Options

1. **Run Grid Trading EA**: Start live grid trading
2. **Test Connection**: Verify MT5 connection and login
3. **Run Grid Tests**: Complete functionality testing
4. **Simulate Grid**: Preview grid behavior without orders
5. **View Grid Status**: Check current orders and positions
6. **Emergency Stop**: Close all positions and cancel orders
7. **Exit**: Close the launcher

## 🚨 Emergency Procedures

### If Something Goes Wrong:
1. **Use Emergency Stop** in launcher menu
2. **Or run**: `C:/Python313/python.exe -c "from mt5_grid_trading_ea import GridTradingEA; ea = GridTradingEA(login=YOUR_LOGIN, password='YOUR_PASSWORD', server='YOUR_SERVER'); ea.initialize_mt5(); ea.close_all_positions(); ea.cancel_all_orders()"`
3. **Or manually** close positions in MT5 terminal

### Market Crisis Response:
- **Strong Trend**: Close all positions immediately
- **High Volatility**: Reduce grid levels or stop trading
- **News Events**: Consider pausing the EA temporarily

## 📊 Monitoring Your Grid

The EA provides real-time monitoring:
- **Active Orders**: Number of pending buy/sell orders
- **Open Positions**: Current filled positions
- **Total P&L**: Combined profit/loss across all positions
- **Grid Status**: Visual representation of current grid

## 🔧 Customization Options

### Grid Parameters
- **Distance**: Adjust based on average daily range
- **Levels**: More levels = more positions = higher risk
- **Lot Size**: Scale based on account size

### Advanced Features
- **Auto-adjust**: Grid adapts to volatility
- **Time filters**: Trade only during specific hours
- **Spread filters**: Pause during high spread periods
- **Profit targets**: Close all positions at target profit

## 📞 Support & Troubleshooting

### Common Issues

1. **"Failed to place order"**
   - Check free margin
   - Verify lot size is within broker limits
   - Ensure market is open

2. **"High margin usage"**
   - Reduce lot size
   - Decrease maximum levels
   - Increase grid distance

3. **"Grid not profitable"**
   - Check if market is trending strongly
   - Consider wider grid spacing
   - Review market conditions

### Debug Mode
Enable detailed logging by setting `DEBUG = True` in config.py

## 📚 Educational Resources

- **Grid Trading Basics**: Research grid trading strategies
- **Risk Management**: Learn position sizing techniques
- **Market Analysis**: Understand ranging vs trending markets
- **MetaTrader 5**: Familiarize yourself with MT5 platform

## 👨‍💻 Author

**Developer**: Johannes N. Nkosi  
**Date**: July 25, 2025  
**Platform**: MetaTrader 5  
**Language**: Python  
**Strategy**: Grid Trading System  

---

**Remember**: Grid trading is a sophisticated strategy that requires understanding and proper risk management. Always test thoroughly on a demo account before live trading!
