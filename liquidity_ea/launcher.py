"""
Launcher for Liquidity EA
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from mt5_liquidity_ea import LiquidityEA

def main():
    ea = LiquidityEA()
    ea.run()

if __name__ == "__main__":
    main()
