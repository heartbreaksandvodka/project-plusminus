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
