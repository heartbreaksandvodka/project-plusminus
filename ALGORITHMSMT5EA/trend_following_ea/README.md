# MetaTrader 5 Trend Following Expert Advisor

A sophisticated Python-based Expert Advisor that implements a long-term trend following strategy for MetaTrader 5. This EA identifies and rides major market trends using multi-timeframe analysis and advanced technical indicators.

## 🎯 Strategy Overview

Trend following is a time-tested approach that:
- **Captures Major Moves**: Designed to catch significant market trends
- **Multi-Timeframe Analysis**: Uses M1 and M5 timeframes for confirmation
- **Long-Term Focus**: Holds positions for days to weeks
- **Risk-Managed**: ATR-based position sizing and stop losses
- **Trend Confirmation**: Multiple indicators confirm trend direction and strength

## 📊 How It Works

### Signal Generation Process:
1. **EMA Crossover**: Fast EMA (21) crosses Slow EMA (50)
2. **Trend Filter**: Price must be above/below long-term EMA (200)
3. **Trend Strength**: ADX must be above threshold (25)
4. **Multi-Timeframe**: Both M1 and M5 must align
5. **Momentum**: RSI confirms directional bias

### Example Long Setup:
```
✅ Fast EMA > Slow EMA (M1 crossover)
✅ Price > 200 EMA (uptrend filter)
✅ ADX > 25 (strong trend)
✅ 5-minute chart bullish (M5 confirmation)
✅ RSI > 50 (bullish momentum)
→ ENTER LONG POSITION
```

## ⚠️ Strategy Characteristics

### **Strengths:**
- Excellent for capturing major trends
- High win rate in trending markets
- Large profit potential per trade
- Well-defined risk management
- Reduces market noise through filters

### **Considerations:**
- Requires patience (positions held days/weeks)
- Can have periods of drawdown
- Not suitable for ranging markets
- Lower trade frequency
- Requires strong trending conditions

## 🚀 Features

### **Advanced Technical Analysis:**
- **EMAs**: 21, 50, 200 period exponential moving averages
- **ADX**: Average Directional Index for trend strength
- **ATR**: Average True Range for volatility-based stops
- **RSI**: Relative Strength Index for momentum
- **Multi-Timeframe**: M1 signals + M5 confirmation

### **Risk Management:**
- **ATR-Based Stops**: Dynamic stop losses based on market volatility
- **Position Sizing**: Risk-based lot size calculation (2% per trade)
- **Risk-Reward**: 3:1 minimum risk-reward ratio
- **Trailing Stops**: Protect profits as trends develop
- **Emergency Controls**: Quick position closure capabilities

### **Professional Features:**
- **Real-time Monitoring**: Comprehensive trend analysis
- **Position Management**: Automated trailing stops
- **Multi-Timeframe Dashboard**: Clear trend overview
- **Comprehensive Testing**: Full validation suite
- **Risk Calculations**: Detailed exposure analysis

## 📁 Files Structure

```
trend_following_ea/
├── mt5_trend_following_ea.py    # Main EA (600+ lines)
├── config.py                    # Strategy configuration
├── test_ea.py                   # Comprehensive tests
├── trading_test.py              # Position management tests
├── launcher.py                  # Interactive launcher
├── start_ea.bat                # Windows batch launcher
└── README.md                   # This documentation
```

## ⚙️ Configuration

Edit `config.py` to customize the strategy:

```python
# Timeframes
PRIMARY_TIMEFRAME = "M1"    # Signal timeframe
SECONDARY_TIMEFRAME = "M5"  # Confirmation timeframe

# Indicators
EMA_FAST = 21              # Fast EMA period
EMA_SLOW = 50              # Slow EMA period
EMA_FILTER = 200           # Trend filter EMA
ADX_THRESHOLD = 25         # Minimum trend strength

# Risk Management
RISK_PERCENT = 2.0         # Risk per trade (% of balance)
ATR_MULTIPLIER = 2.5       # Stop loss distance
RISK_REWARD_RATIO = 3.0    # Minimum R:R ratio
```

## 🚀 How to Use

### Option 1: Interactive Launcher
```bash
cd trend_following_ea
C:/Python313/python.exe launcher.py
```
Or double-click `start_ea.bat`

### Option 2: Direct Commands
```bash
# Test connection and analysis
C:/Python313/python.exe test_ea.py

# Run the EA
C:/Python313/python.exe mt5_trend_following_ea.py
```

## 📊 Launcher Menu Options

1. **Run Trend Following EA**: Start live trend following
2. **Test Connection & Setup**: Verify MT5 connection
3. **Run Comprehensive Tests**: Full functionality testing
4. **Test Trading Functions**: Position management tests
5. **Analyze Current Market**: Real-time trend analysis
6. **View Current Positions**: Monitor active trades
7. **Close All Positions**: Emergency position closure
8. **Exit**: Close launcher

## 📈 Best Market Conditions

### **Ideal Conditions:**
- ✅ **Strong trending markets** (ADX > 30)
- ✅ **Clear directional bias** (minimal consolidation)
- ✅ **Major currency pairs** (EURUSD, GBPUSD, etc.)
- ✅ **Normal volatility** (not crisis periods)
- ✅ **Liquid market hours** (London/NY overlap)

### **Avoid:**
- ❌ **Ranging/sideways markets**
- ❌ **High impact news events**
- ❌ **Extremely low volatility**
- ❌ **Market holidays/closures**
- ❌ **Crisis/panic conditions**

## 🧪 Testing & Validation

### 1. Connection Test
```bash
C:/Python313/python.exe -c "from mt5_trend_following_ea import test_connection; test_connection()"
```

### 2. Comprehensive Analysis
```bash
C:/Python313/python.exe test_ea.py
```

### 3. Market Trend Analysis
```bash
C:/Python313/python.exe -c "from test_ea import test_trend_scenarios; test_trend_scenarios()"
```

### 4. Trading Function Test
```bash
C:/Python313/python.exe trading_test.py
```

## 📊 Real-Time Monitoring

The EA provides detailed monitoring:

```
📊 Trend Following Status:
   Current Signal: BUY / SELL / No signal
   Open Positions: X positions
   
📈 Primary Timeframe (M1):
   Price: 1.1234
   Fast EMA: 1.1220
   Slow EMA: 1.1200
   ADX: 32.5 (Strong trend)
   
💰 Position Summary:
   Total P&L: $XXX.XX
   Position details...
```

## 🛡️ Risk Management

### **Position Sizing:**
- **Risk per Trade**: 2% of account balance
- **ATR-Based Calculation**: Stop loss = 2.5 × ATR
- **Dynamic Adjustment**: Lot size adapts to volatility

### **Stop Loss Management:**
- **Initial Stop**: 2.5 × ATR from entry
- **Trailing Stop**: Moves with favorable price action
- **Take Profit**: 3:1 risk-reward minimum

### **Account Protection:**
- **Maximum Positions**: 1 per direction
- **Daily/Weekly Limits**: Configurable loss limits
- **Emergency Stop**: Instant position closure

## 📋 Account Requirements

### **Recommended Minimum:**
- **Account Balance**: $5,000+
- **Leverage**: 1:100 or higher
- **Spread**: <2 points average
- **Execution**: Fast execution broker
- **Timeframe**: Available 24/5 market access

### **Optimal Setup:**
- **Account Type**: Standard/ECN
- **Base Currency**: USD/EUR
- **Platform**: MetaTrader 5
- **VPS**: Recommended for 24/7 operation

## 🔧 Advanced Features

### **Multi-Timeframe Dashboard:**
- M1 signals with M5 confirmation
- Real-time trend strength monitoring
- Market condition assessment
- Signal quality scoring

### **Adaptive Risk Management:**
- Volatility-adjusted position sizing
- Dynamic stop loss placement
- Trend-strength based exposure
- Market condition filters

### **Performance Analytics:**
- Win rate tracking
- Average holding period
- Risk-reward analysis
- Drawdown monitoring

## 🚨 Important Notes

### **Strategy Characteristics:**
- **Holding Period**: Days to weeks
- **Trade Frequency**: Low (quality over quantity)
- **Market Dependency**: Requires trending conditions
- **Patience Required**: Long-term perspective essential

### **Risk Considerations:**
- **Drawdown Potential**: Can experience extended losing periods
- **Market Dependency**: Performance varies with market conditions
- **Emotional Challenge**: Requires discipline during drawdowns
- **Capital Requirements**: Needs adequate margin for long holds

## 🎓 Educational Resources

### **Trend Following Concepts:**
- Market structure analysis
- Trend identification techniques
- Multi-timeframe alignment
- Risk-reward optimization

### **Technical Indicators:**
- EMA crossover strategies
- ADX trend strength measurement
- ATR volatility analysis
- RSI momentum confirmation

## 📞 Support & Optimization

### **Performance Optimization:**
- Adjust timeframes for different markets
- Optimize indicator parameters for symbols
- Fine-tune risk management settings
- Adapt to changing market conditions

### **Troubleshooting:**
- Check trend strength requirements
- Verify multi-timeframe alignment
- Review position sizing calculations
- Monitor market condition filters

## 👨‍💻 Author

**Developer**: Johannes N. Nkosi  
**Date**: July 25, 2025  
**Platform**: MetaTrader 5  
**Language**: Python  
**Strategy**: Long-Term Trend Following  

---

**Remember**: Trend following requires patience and discipline. This strategy is designed for traders who understand the importance of riding major market trends while managing risk effectively. Always test thoroughly on demo accounts and ensure you understand the long-term nature of this approach!
