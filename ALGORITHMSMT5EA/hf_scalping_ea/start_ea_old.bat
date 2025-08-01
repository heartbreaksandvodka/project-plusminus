@echo off
echo.
echo ========================================
echo  High-Frequency Scalping EA Launcher
echo ========================================
echo.
echo Starting MT5 High-Frequency Scalping EA...
echo.
echo Configuration:
echo - Target Profit: 15 pips
echo - Stop Loss: 15 pips  
echo - Trailing Stop: 2 pips
echo - Symbol: EURUSD
echo - Lot Size: 0.01 (Auto-sizing enabled)
echo - Max Daily Trades: 100
echo.

cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Python not found in PATH
    echo Please install Python or add it to your PATH
    pause
    exit /b 1
)

REM Check if required packages are installed
python -c "import MetaTrader5, pandas, numpy" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Installing required packages...
    python -m pip install MetaTrader5 pandas numpy
    if errorlevel 1 (
        echo ❌ Failed to install packages
        pause
        exit /b 1
    )
)

echo ✅ Environment check passed
echo.
echo 🚀 Launching High-Frequency Scalping EA...
echo.
echo ⚠️  IMPORTANT REMINDERS:
echo - Ensure MT5 terminal is running
echo - Check internet connection
echo - Verify account credentials in config.py
echo - Monitor the EA during initial run
echo.

REM Start the EA
python launcher.py

if errorlevel 1 (
    echo.
    echo ❌ EA stopped with error
    echo Check the log files for details
) else (
    echo.
    echo ✅ EA stopped normally
)

echo.
pause
