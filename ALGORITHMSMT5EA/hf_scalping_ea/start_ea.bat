@echo off
echo.
echo ========================================
echo  High-Frequency Scalping EA Launcher
echo ========================================
echo.
echo Starting MT5 High-Frequency Scalping EA...
echo.
echo Configuration:
echo - Risk Management: 3%% per trade (percentage-based)
echo - Stop Loss: 3%% of account balance
echo - Take Profit: 3%% of account balance  
echo - Trailing Stop: 0.5%% of account balance
echo - Breakeven Trigger: 1.5%% of account balance
echo - Daily Loss Limit: 9%% of account balance
echo - Daily Profit Target: 15%% of account balance
echo - Symbol: BTCUSD
echo - Max Daily Trades: 100
echo.
echo WARNING: This EA executes high-frequency trades!
echo Make sure you understand the risks involved.
echo.
pause

python launcher.py
pause
