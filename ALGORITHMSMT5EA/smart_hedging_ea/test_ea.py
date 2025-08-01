# Smart Hedging EA Testing Script
# This script can be used to run backtests or dry runs for the EA

from mt5_smart_hedging_ea import SmartHedgingEA

def test_hedging():
    ea = SmartHedgingEA(symbol="US500", base_lot=0.1, hedge_ratio=0.5, magic_number=54321)
    print("Testing Smart Hedging EA logic...")
    print(f"Symbol: {ea.symbol}")
    print(f"Base Lot: {ea.base_lot}")
    print(f"Hedge Ratio: {ea.hedge_ratio}")
    print(f"Max Drawdown: {ea.max_drawdown_percent}")
    print("Test complete.")

if __name__ == "__main__":
    test_hedging()
