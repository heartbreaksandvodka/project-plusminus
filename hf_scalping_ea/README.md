# 🚀 High-Frequency Scalping EA

An advanced MetaTrader 5 Expert Advisor designed for high-frequency scalping on major forex pairs using sophisticated order flow analysis and tick-by-tick execution.

## 📊 **Trading Strategy**

### **Core Algorithm**
- **Execution**: Tick-based high-frequency trading
- **Target**: 50-100 trades per day
- **Analysis**: Advanced order flow momentum detection
- **Timeframe**: Real-time tick processing with 1-second updates

### **Updated Risk Parameters**
- **Target Profit**: **15 pips** (improved profit locking)
- **Stop Loss**: 15 pips (1:1 risk-reward ratio)
- **Trailing Stop**: **2 pips** (tight profit protection)
- **Spread Filter**: 2-8 points maximum
- **Position Size**: 0.01 lots (auto-sizing available)

## 🎯 **Key Features**

### **Order Flow Analysis**
- Real-time bid/ask pressure monitoring
- Volume-weighted price momentum detection
- Tick-by-tick market microstructure analysis
- Advanced signal generation based on order flow

### **Risk Management**
- Daily trade limits (100 maximum)
- Maximum 3 concurrent positions
- Dynamic position sizing based on account balance
- Automatic daily profit/loss tracking
- 5% maximum drawdown protection

### **Trading Hours**
- **Active**: 8:00 AM - 6:00 PM GMT
- **News Avoidance**: 30 minutes before/after major events
- **Optimal Pairs**: EURUSD, GBPUSD, USDJPY (high liquidity)

## 🛠️ **Installation & Setup**

### **Prerequisites**
```bash
# Required software
- MetaTrader 5 terminal
- Python 3.7+
- Required packages: MetaTrader5, pandas, numpy
```

### **Quick Start**
1. **Configure Account**: Update `config.py` with your MT5 credentials
2. **Run Setup**: Double-click `start_ea.bat` 
3. **Monitor**: Use launcher menu for real-time monitoring

### **Configuration Files**
- `config.py` - Main EA settings and parameters
- `launcher.py` - Interactive menu system
- `start_ea.bat` - Automated startup script

## 📈 **Performance Expectations**

### **Daily Targets**
- **Trades**: 50-100 per day
- **Win Rate**: 65-70% (typical for scalping)
- **Daily Profit**: $50 target (customizable)
- **Max Loss**: $100 daily limit

### **Scalping Advantages**
- **Quick Profits**: 15-pip targets captured rapidly
- **Tight Stops**: 2-pip trailing minimizes losses
- **High Frequency**: Multiple opportunities per hour
- **Low Drawdown**: Small position sizes reduce risk

## 🚨 **Important Settings Update**

### **Profit Optimization Changes**
```python
SCALP_TARGET = 15       # Increased from 5 pips
TRAILING_STOP = 2       # Tightened from 3 pips
```

These changes provide:
- **Better Profit Lock**: 15 pips allows stronger trend capture
- **Tighter Protection**: 2-pip trailing keeps more profits
- **Improved R:R**: Better risk-reward ratio per trade

## 🔧 **Usage Instructions**

### **Starting the EA**
```bash
# Method 1: Batch file (Recommended)
start_ea.bat

# Method 2: Python launcher
python launcher.py

# Method 3: Direct execution
python mt5_hf_scalping_ea.py
```

### **Menu Options**
1. **Start EA** - Begin automated trading
2. **Monitor Performance** - View real-time statistics
3. **Check Positions** - Review open trades
4. **View Logs** - Debug and analysis
5. **Stop EA** - Safe shutdown

## 📊 **Monitoring & Analysis**

### **Real-Time Statistics**
- Current spread conditions
- Active positions count
- Daily trade progress
- Profit/loss tracking
- Win rate monitoring

### **Log Files**
- `hf_scalping_ea.log` - Detailed trading activity
- Error handling and debugging information
- Performance metrics and statistics

## ⚡ **High-Frequency Features**

### **Advanced Order Flow**
- **Tick Analysis**: 20-tick momentum calculation
- **Pressure Detection**: 10-period bid/ask analysis  
- **Volume Filtering**: Minimum 100 volume threshold
- **Microstructure**: Real-time market depth analysis

### **Execution Speed**
- **Latency**: Sub-second order placement
- **Slippage**: Maximum 3 points tolerance
- **Fill Rate**: IOC (Immediate or Cancel) orders
- **Frequency**: 1-second update intervals

## 🛡️ **Risk Controls**

### **Daily Limits**
- **Max Trades**: 100 per day
- **Profit Target**: $50 daily goal
- **Loss Limit**: $100 maximum loss
- **Concurrent**: 3 positions maximum

### **Account Protection**
- **Drawdown**: 5% maximum
- **Auto-Stop**: Trading halts on limits
- **Balance Check**: Regular account monitoring
- **Error Recovery**: Automatic restart capability

## 🔍 **Testing & Validation**

### **Test Suite**
```bash
# Run comprehensive tests
python test_ea.py          # Basic functionality
python trading_test.py     # Trading operations
```

### **Validation Areas**
- Order placement accuracy
- Risk management compliance
- Performance calculation
- Error handling robustness

## 📞 **Support & Troubleshooting**

### **Common Issues**
- **Connection**: Verify MT5 terminal is running
- **Credentials**: Check account details in config.py
- **Spread**: Ensure spreads are within 2-8 point range
- **Balance**: Minimum $1000 recommended for scalping

### **Optimization Tips**
- **VPS Hosting**: Recommended for consistent execution
- **Low Latency**: Choose broker with fast execution
- **Spread Monitoring**: Avoid high-spread periods
- **News Events**: Use built-in news avoidance

## 📋 **Version History**

### **v1.2** (Current)
- ✅ Increased target to 15 pips for better profit lock
- ✅ Tightened trailing stop to 2 pips
- ✅ Enhanced order flow analysis
- ✅ Improved risk management

### **v1.1**
- Advanced tick processing
- Order flow momentum detection
- Real-time spread filtering

### **v1.0**
- Initial high-frequency scalping implementation
- Basic order flow analysis
- Standard risk management

---

**⚠️ Risk Warning**: High-frequency trading involves substantial risk. Only trade with capital you can afford to lose. Past performance does not guarantee future results.

**📧 Support**: For technical support or customization requests, contact the development team.
