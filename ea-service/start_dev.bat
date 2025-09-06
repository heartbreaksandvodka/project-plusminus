@echo off
REM Windows batch script for EA Service startup

echo 🚀 Starting EA Management Service (Development)
echo ================================================

REM Check if virtual environment exists
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo 📋 Installing dependencies...
pip install -r requirements.txt

REM Check if .env exists
if not exist ".env" (
    echo ⚙️  Creating .env file from example...
    copy .env.example .env
    echo ⚠️  Please update .env with your configuration!
)

REM Start the service
echo 🚀 Starting EA Service on port 8001...
python main.py

pause
