# AWS VPS Deployment Guide for Trading EAs

## Overview
This guide walks you through deploying any Expert Advisor (EA) from this collection on an Amazon EC2 instance (VPS) for 24/7 automated trading.

## Prerequisites
- AWS Account with billing setup
- MetaTrader 5 trading account credentials
- Basic understanding of remote desktop connections
- One or more EAs from this collection ready for deployment

## Step 1: Create AWS EC2 Instance

### 1.1 Launch EC2 Instance
1. Login to AWS Console → EC2 Dashboard
2. Click "Launch Instance"
3. **Name**: `TradingEA-VPS` (or specific EA name)
4. **OS**: Windows Server 2022 Base (recommended for MT5)
5. **Instance Type**: `t3.micro` (free tier) or `t3.small` for better performance
6. **Key Pair**: Create new or use existing for RDP access
7. **Security Group**: Allow RDP (port 3389) from your IP
8. **Storage**: 30 GB gp3 (default is sufficient)

### 1.2 Configure Security Group
- **Type**: RDP
- **Protocol**: TCP
- **Port**: 3389
- **Source**: Your IP address (for security)

## Step 2: Connect to Your VPS

### 2.1 Get Connection Details
1. Select your instance in EC2 console
2. Click "Connect" → "RDP client"
3. Download the RDP file
4. Get password using your key pair

### 2.2 Remote Desktop Connection
1. Open the downloaded RDP file
2. Enter the administrator password
3. You're now connected to your Windows VPS!

## Step 3: Setup Trading Environment

### 3.1 Install Python 3.13
1. Download Python 3.13 from python.org
2. Install with "Add to PATH" checked
3. Verify: Open Command Prompt → `python --version`

### 3.2 Install MetaTrader 5
1. Download MT5 from your broker's website
2. Install and login with your trading credentials
3. Enable algorithmic trading: Tools → Options → Expert Advisors → "Allow algorithmic trading"

### 3.3 Setup Project Files
1. Create folder: `C:\TradingEA\`
2. Upload your chosen EA folder to the VPS (e.g., `trend_following_ea`, `grid_trading_ea`)
3. Install dependencies:
   ```cmd
   cd C:\TradingEA\[your_ea_folder]
   python -m pip install MetaTrader5 pandas numpy
   ```

## Step 4: Configure for VPS Operation

### 4.1 Update config.py for VPS
Edit the `config.py` file in your EA folder with VPS-optimized settings:

**For any EA, ensure these VPS settings are added:**
```python
# VPS-specific settings
ENABLE_LOGGING = True
LOG_LEVEL = "INFO"
MAX_LOG_SIZE = 50  # MB
RESTART_ON_ERROR = True
UPDATE_INTERVAL = 60  # 1-minute updates for most EAs
```

**EA-Specific Configurations:**

**Trend Following EA:**
```python
SYMBOL = "EURUSD"
TIMEFRAME_PRIMARY = "M1"  # 1-minute primary
TIMEFRAME_SECONDARY = "M5"  # 5-minute confirmation
RISK_PERCENT = 1.0  # Conservative risk for VPS
```

**Grid Trading EA:**
```python
SYMBOL = "EURUSD"
GRID_SIZE = 20  # Points between grid levels
GRID_LEVELS = 5  # Number of grid levels
RISK_PERCENT = 0.5  # Lower risk for grid trading
```

**Trailing Stop EA:**
```python
SYMBOL = "EURUSD"
TRAILING_DISTANCE = 50  # Points for trailing stop
RISK_PERCENT_PER_TRADE = 10.0  # Account balance risk
```

### 4.2 Create Windows Service Script
Save as `vps_service.py` in your EA folder:
```python
import subprocess
import time
import logging
import os
from datetime import datetime

# Setup logging
logging.basicConfig(
    filename='C:\\TradingEA\\ea_service.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def run_ea(ea_script_name):
    """Run the specified EA"""
    try:
        result = subprocess.run([
            'python', ea_script_name
        ], capture_output=True, text=True, timeout=3600)  # 1 hour timeout
        
        if result.returncode != 0:
            logging.error(f"EA exited with error: {result.stderr}")
        else:
            logging.info("EA completed successfully")
            
    except subprocess.TimeoutExpired:
        logging.warning("EA timeout - restarting")
    except Exception as e:
        logging.error(f"Error running EA: {e}")

def main():
    """Main service loop"""
    # CONFIGURE THIS: Set your EA script name
    EA_SCRIPT = "mt5_trend_following_ea.py"  # Change to your EA script
    # Examples:
    # EA_SCRIPT = "mt5_grid_trading_ea.py"
    # EA_SCRIPT = "mt5_trailing_stop_ea.py"
    
    logging.info(f"VPS EA Service started for {EA_SCRIPT}")
    
    while True:
        try:
            # Check if it's market hours (optional)
            current_hour = datetime.now().hour
            
            if 0 <= current_hour <= 23:  # Run 24/7 for forex
                logging.info("Starting EA execution")
                run_ea(EA_SCRIPT)
                
                # Wait interval before next execution (configurable per EA)
                time.sleep(60)  # Default 1 minute
                
        except KeyboardInterrupt:
            logging.info("Service stopped by user")
            break
        except Exception as e:
            logging.error(f"Service error: {e}")
            time.sleep(60)  # Wait before retry

if __name__ == "__main__":
    main()
```

## Step 5: Setup Automatic Startup

### 5.1 Create Batch File
Save as `start_ea_service.bat` in your EA folder:
```batch
@echo off
cd C:\TradingEA\[your_ea_folder]
echo Starting [EA_NAME] VPS Service...
python vps_service.py
pause
```

**Examples for different EAs:**
- Trend Following: `cd C:\TradingEA\trend_following_ea`
- Grid Trading: `cd C:\TradingEA\grid_trading_ea`
- Trailing Stop: `cd C:\TradingEA\trailing_stop_ea`

### 5.2 Add to Windows Startup
1. Press `Win + R` → type `shell:startup` → Enter
2. Copy `start_ea_service.bat` to the startup folder
3. EA will now start automatically when VPS boots

### 5.3 Alternative: Windows Task Scheduler
1. Open Task Scheduler
2. Create Basic Task → "[EA_NAME] Service"
3. Trigger: "When computer starts"
4. Action: Start program → `C:\TradingEA\[your_ea_folder]\start_ea_service.bat`

## Step 6: Multiple EA Deployment

### 6.1 Running Multiple EAs Simultaneously
To run multiple EAs on the same VPS:

1. Create separate folders for each EA:
   ```
   C:\TradingEA\
   ├── trend_following_ea\
   ├── grid_trading_ea\
   └── trailing_stop_ea\
   ```

2. Configure different symbols or magic numbers for each EA
3. Create separate service scripts and batch files
4. Use Windows Task Scheduler for multiple startup tasks

### 6.2 Resource Considerations
- **t3.small**: Can handle 2-3 EAs simultaneously
- **t3.medium**: Can handle 4-6 EAs simultaneously
- Monitor CPU and memory usage via Task Manager

## Step 7: Monitoring and Maintenance

### 7.1 Remote Monitoring
- Use RDP to check EA status
- Monitor log files: `C:\TradingEA\ea_service.log`
- Check MT5 terminal for trades and errors

### 7.2 Log Rotation Script
Save as `cleanup_logs.py` in the TradingEA root folder:
```python
import os
import time
from datetime import datetime, timedelta

def cleanup_old_logs():
    """Remove logs older than 30 days"""
    log_dir = "C:\\TradingEA"
    cutoff_date = datetime.now() - timedelta(days=30)
    
    for filename in os.listdir(log_dir):
        if filename.endswith('.log'):
            filepath = os.path.join(log_dir, filename)
            file_time = datetime.fromtimestamp(os.path.getctime(filepath))
            
            if file_time < cutoff_date:
                os.remove(filepath)
                print(f"Removed old log: {filename}")

if __name__ == "__main__":
    cleanup_old_logs()
```

## Step 8: Security Best Practices

### 8.1 VPS Security
- Change default RDP port from 3389 to custom port
- Use strong passwords
- Enable Windows Firewall
- Regular Windows Updates
- Restrict RDP access to your IP only

### 8.2 Trading Security
- Use demo account for initial testing
- Start with small position sizes
- Monitor frequently during first week
- Set up email alerts for critical errors
- Use different magic numbers for each EA

## Step 9: Cost Optimization

### 9.1 Instance Types
- **t3.micro**: $8-10/month (1 EA, basic performance)
- **t3.small**: $15-20/month (2-3 EAs, recommended)
- **t3.medium**: $30-40/month (4-6 EAs, high performance)

### 9.2 Cost Saving Tips
- Use Reserved Instances for 1-year commitment (30-40% savings)
- Stop instance during weekends if not trading
- Use Spot Instances (risky but cheaper)
- Monitor CloudWatch for resource usage

## Step 10: EA-Specific Deployment Notes

### 10.1 Trend Following EA
- Best for: Long-term trend capture
- Timeframes: M1 primary, M5 confirmation
- Resource usage: Low-Medium
- Recommended instance: t3.small

### 10.2 Grid Trading EA
- Best for: Ranging/volatile markets
- Timeframes: 1-minute execution intervals
- Resource usage: Medium (multiple orders)
- Recommended instance: t3.small to t3.medium

### 10.3 Trailing Stop EA
- Best for: Risk management of existing positions
- Timeframes: Real-time (3-second updates)
- Resource usage: Low
- Can run alongside other EAs

## Step 11: Troubleshooting

### 11.1 Common Issues
- **EA not starting**: Check Python path, MT5 login, script name in vps_service.py
- **Connection lost**: Check internet, broker server status
- **High CPU usage**: Reduce update frequency, optimize code
- **Disk space**: Setup log rotation, clean temp files

### 11.2 Emergency Procedures
- Keep backup of config files
- Document broker login details securely
- Have mobile app access to close trades manually
- Set up multiple monitoring methods

## Quick Start Checklist

- [ ] Launch Windows EC2 instance
- [ ] Connect via RDP
- [ ] Install Python 3.13
- [ ] Install MetaTrader 5
- [ ] Upload chosen EA folder(s)
- [ ] Install Python dependencies
- [ ] Configure MT5 login
- [ ] Update EA config.py for VPS
- [ ] Modify vps_service.py with correct EA script name
- [ ] Test EA manually
- [ ] Setup automatic startup
- [ ] Monitor for 24 hours
- [ ] Setup log monitoring

## EA Selection Guide

**Choose the right EA for your VPS deployment:**

| EA Type | Best For | Resource Usage | Complexity |
|---------|----------|----------------|------------|
| Trailing Stop | Risk management | Low | Simple |
| Grid Trading | Volatile markets | Medium | Medium |
| Trend Following | Trend capture | Low-Medium | Medium |

## Support

For AWS-specific issues:
- AWS Documentation: docs.aws.amazon.com
- AWS Support (if subscribed)

For trading issues:
- Check MT5 terminal logs
- Verify broker connection
- Review EA-specific log files
- Check individual EA README files

---

**Important**: Always test thoroughly on demo accounts before deploying to live trading. Monitor closely during the first few days of VPS operation. Start with one EA and gradually add more as you gain experience with VPS management.
