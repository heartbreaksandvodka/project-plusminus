"""
Launcher for Candy EA
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from mt5_candy_ea import CandyEA

def main():
    ea = CandyEA()
    ea.run()

if __name__ == "__main__":
    main()
