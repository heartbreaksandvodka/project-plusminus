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

def run_ea():
    """Run the trend following EA"""
    try:
        os.chdir('C:\\TradingEA\\trend_following_ea')
        result = subprocess.run([
            'python', 'mt5_trend_following_ea.py'
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
    logging.info("VPS EA Service started")
    
    while True:
        try:
            # Check if it's market hours (optional)
            current_hour = datetime.now().hour
            
            if 0 <= current_hour <= 23:  # Run 24/7 for forex
                logging.info("Starting EA execution")
                run_ea()
                
                # Wait 1 minute before next execution
                time.sleep(60)
            else:
                # Market closed - wait longer
                logging.info("Market hours - sleeping")
                time.sleep(300)  # 5 minutes
                
        except KeyboardInterrupt:
            logging.info("Service stopped by user")
            break
        except Exception as e:
            logging.error(f"Service error: {e}")
            time.sleep(60)  # Wait before retry

if __name__ == "__main__":
    main()
