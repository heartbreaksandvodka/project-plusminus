"""
Launcher for News EA
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from mt5_news_ea import NewsEA

def main():
    ea = NewsEA()
    ea.run()

if __name__ == "__main__":
    main()
