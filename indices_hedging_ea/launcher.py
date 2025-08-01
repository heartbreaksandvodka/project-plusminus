"""
Launcher for Indices Hedging EA
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from mt5_indices_hedging_ea import IndicesHedgingEA

def main():
    ea = IndicesHedgingEA()
    ea.run()

if __name__ == "__main__":
    main()
