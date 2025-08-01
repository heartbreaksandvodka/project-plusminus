# Liquidity EA Testing Script
from mt5_liquidity_ea import LiquidityEA

def test_liquidity_ea():
    ea = LiquidityEA(symbol="EURUSD", base_lot=0.1, magic_number=88888)
    print("Testing Liquidity EA logic...")
    print(f"Symbol: {ea.symbol}")
    print(f"Base Lot: {ea.base_lot}")
    print(f"Magic Number: {ea.magic_number}")
    print("Test complete.")

if __name__ == "__main__":
    test_liquidity_ea()
