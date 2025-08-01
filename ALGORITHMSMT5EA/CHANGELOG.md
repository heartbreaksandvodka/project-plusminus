# Project Changelog

## July 2025

### Major Updates
- Centralized configuration and risk management for all EAs (`global_config.py`, `risk_manager.py`)
- All EAs now use dynamic account login and percentage-based risk controls
- Robust error handling and detailed debug logging added throughout
- **Grid Trading EA**:
  - Smart accumulative risk management: global stop loss and trailing take profit
  - Maximum open orders cap (`max_orders`)
  - No per-order stop loss; all risk managed globally
- **High-Frequency Scalping EA**:
  - Percentage-based stop loss and take profit
  - Trailing stop and breakeven logic
  - Daily trade and loss limits
  - Advanced order flow analysis for signal generation
  - Centralized position sizing via risk manager
- All EAs updated to use centralized modules and dynamic imports
- README.md updated to reflect all new features and risk controls

---
**Note:** Always test thoroughly on a demo account before live trading. Grid and scalping strategies require careful risk management.
