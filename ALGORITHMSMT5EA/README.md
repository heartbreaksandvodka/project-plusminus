# ALGORITHMS

Professional MetaTrader 5 Expert Advisors Collection
Author: Johannes N. Nkosi
Date: July 25, 2025

This is the main algorithms development workspace with a centralized Python environment for developing and running sophisticated trading strategies.

## Python Environment

- **Python Version**: 3.13.3
- **Installed Packages**:
  - MetaTrader5 (5.0.5120)
  - pandas (2.3.1)
  - numpy (2.3.2)
  - All other required dependencies

## Expert Advisors Collection

Each Expert Advisor (EA) has its own dedicated folder containing:
- Main EA script with complete strategy implementation
- Configuration files for easy customization
- Comprehensive test scripts for validation
- Interactive launcher scripts for user-friendly operation
- Detailed documentation and usage guides
- Windows batch files for quick startup

### Code Reuse & Shared Utilities

All EA scripts now use shared utility functions from `common_ea.py` for:
- MetaTrader 5 initialization and login
- Symbol information and price retrieval
- Pause/resume logic via file-based flags (Windows compatible)

This ensures consistent, maintainable, and robust code across all EAs. To use these utilities, simply import from:

```python
from ALGORITHMSMT5EA.common_ea import initialize_mt5, get_symbol_info, get_current_price, check_pause_flag
```

Refer to `common_ea.py` for details and usage examples.

## Current Expert Advisors

### 1. `trailing_stop_ea/` - Risk-Based Trailing Stop Manager
**Strategy**: Professional risk management with account balance-based stop losses
- **Features**: 10% account balance risk calculation, dynamic trailing stops
- **Timeframe**: Real-time monitoring with 3-second updates
- **Best For**: Protecting existing positions with precise risk management

### 2. `grid_trading_ea/` - Grid Trading Expert Advisor  
**Strategy**: Systematic grid trading that profits from market volatility
- **Features**: Automatic grid placement, volatility-based spacing, risk controls
- **Timeframe**: 1-minute execution for responsive grid management
- **Best For**: Ranging markets and volatile conditions

### 3. `trend_following_ea/` - Fast Trend Following Expert Advisor
**Strategy**: Multi-timeframe trend analysis for capturing quick market moves
- **Features**: M1+M5 analysis, ADX trend strength, ATR-based risk management
- **Timeframe**: 1-minute primary with 5-minute confirmation
- **Best For**: Fast trend capture and scalping opportunities

## AWS VPS Deployment

For 24/7 automated trading, you can deploy any EA to Amazon Web Services:

📖 **[Complete AWS VPS Deployment Guide](aws_vps_deployment_guide.md)**

### Quick VPS Setup:
1. Launch Windows Server 2022 EC2 instance
2. Install Python 3.13 + MetaTrader 5
3. Upload your chosen EA folder
4. Configure for 24/7 operation
5. Monitor remotely via RDP

**Recommended**: Start with `t3.small` instance (~$15-20/month) for 2-3 EAs

## Local Development & Testing

Navigate to any EA folder and run the interactive launcher:

```bash
cd trailing_stop_ea
C:/Python313/python.exe launcher.py
```

Or use the Windows batch files:
```bash
cd trailing_stop_ea
start_ea.bat
```

## Creating New Expert Advisors
2. Develop your EA using the centralized Python environment
3. Follow the established structure:
   - `mt5_[name]_ea.py` - Main EA script
   - `config.py` - Configuration settings
   - `test_ea.py` - Comprehensive tests
   - `trading_test.py` - Trading functionality tests
   - `launcher.py` - Interactive menu
   - `start_ea.bat` - Windows launcher
   - `README.md` - Documentation
4. Keep all EA-specific files in their respective folders

## Python Environment Commands

To run Python scripts from any EA folder:
```bash
C:/Python313/python.exe your_script.py
```

To install additional packages (if needed):
```bash
C:/Python313/python.exe -m pip install package_name
```

## Development Guidelines

- **Modularity**: Keep each EA self-contained
- **Documentation**: Include comprehensive README files
- **Testing**: Implement thorough test suites
- **Risk Management**: Always include safety features
- **User Experience**: Provide intuitive launchers and clear instructions

## Author Information

**Developer**: Johannes N. Nkosi  
**Specialization**: Algorithmic Trading Systems  
**Platform**: MetaTrader 5  
**Language**: Python  
**Date Created**: July 25, 2025

## Support & Maintenance

Each EA includes:
- Comprehensive error handling
- Detailed logging and status updates
- Emergency stop procedures
- Risk management controls
- Performance monitoring tools

For questions or issues:
1. Check the individual EA README files
2. Run the built-in test suites
3. Review the configuration settings
4. Test on demo accounts before live trading

---

**Disclaimer**: All Expert Advisors are for educational and research purposes. Trading involves significant risk of loss. Always test on demo accounts and never risk more than you can afford to lose.