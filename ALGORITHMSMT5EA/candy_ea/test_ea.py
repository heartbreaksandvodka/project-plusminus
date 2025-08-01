# Candy EA Testing Script
from mt5_candy_ea import CandyEA

def test_candy_ea():
    ea = CandyEA(symbol="EURUSD", base_lot=0.1, magic_number=20250731)
    print("Testing Candy EA logic...")
    print(f"Symbol: {ea.symbol}")
    print(f"Base Lot: {ea.base_lot}")
    print(f"Magic Number: {ea.magic_number}")
    print("Test complete.")

if __name__ == "__main__":
    test_candy_ea()
