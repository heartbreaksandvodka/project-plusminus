# News EA Testing Script
# This script can be used to run backtests or dry runs for the EA

from mt5_news_ea import NewsEA
from news_api import get_upcoming_events, filter_critical_events
import pandas as pd
import datetime

def test_news_ea():
    ea = NewsEA(symbol="EURUSD", base_lot=0.1, magic_number=67890)
    print("Testing News EA logic...")
    print(f"Symbol: {ea.symbol}")
    print(f"Base Lot: {ea.base_lot}")
    print(f"Magic Number: {ea.magic_number}")
    print("Test complete.")

def test_news_api_integration():
    print("\nTesting news_api integration...")
    # Get upcoming events for today (mocked country)
    today = datetime.datetime.now().strftime('%d/%m/%Y')
    try:
        events = get_upcoming_events('united states', 1)
        print(f"Fetched {len(events)} events for today.")
        print("All fetched events:")
        print(events)
        critical_events = filter_critical_events(events)
        print(f"Filtered {len(critical_events)} critical events.")
        if not critical_events.empty:
            print("Sample critical event:")
            print(critical_events.iloc[0])
        else:
            print("No critical events found.")
    except Exception as e:
        print(f"Error fetching or filtering events: {e}")

def test_dry_run_order_placement():
    print("\nTesting dry-run order placement...")
    ea = NewsEA(symbol="EURUSD", base_lot=0.1, magic_number=67890)
    # Mock event for order placement
    mock_event = {
        'event': 'Non-Farm Payrolls',
        'date': '28/07/2025',
        'time': '14:30',
        'country': 'united states',
        'impact': 'High',
    }
    try:
        ea.place_news_orders(mock_event)
        print("Dry-run order placement executed.")
    except Exception as e:
        print(f"Error in dry-run order placement: {e}")

if __name__ == "__main__":
    test_news_ea()
    test_news_api_integration()
    test_dry_run_order_placement()
