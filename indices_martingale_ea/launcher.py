"""
Launcher for Indices Martingale EA
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from mt5_indices_martingale_ea import IndicesMartingaleEA

def main():
    ea = IndicesMartingaleEA()
    ea.run()

if __name__ == "__main__":
    main()
