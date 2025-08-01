"""
Launcher for Smart Hedging EA
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from mt5_smart_hedging_ea import SmartHedgingEA

def main():
    ea = SmartHedgingEA()
    ea.run()

if __name__ == "__main__":
    main()
