# Indices Martingale EA Testing Script
# This script can be used to run backtests or dry runs for the EA

from mt5_indices_martingale_ea import IndicesMartingaleEA

def test_martingale():
    ea = IndicesMartingaleEA(symbol="US500", base_lot=0.1, magic_number=12345, grid_step_points=100, max_trades=6)
    # Simulate a run (add more test logic as needed)
    print("Testing Martingale EA logic...")
    # You can add mock data or dry-run methods here
    # For now, just initialize and print config
    print(f"Symbol: {ea.symbol}")
    print(f"Base Lot: {ea.base_lot}")
    print(f"Grid Step: {ea.grid_step_points}")
    print(f"Max Trades: {ea.max_trades}")
    print("Test complete.")

if __name__ == "__main__":
    test_martingale()
