"""
news_api.py - Global Economic Calendar & News API Wrapper
Reusable for all EAs in the workspace.
"""

import investpy
from datetime import datetime, timedelta
import MetaTrader5 as mt5

def get_upcoming_events(country='united states', days_ahead=1):
    today = datetime.today().date()
    end_date = today + timedelta(days=days_ahead)
    events = investpy.economic_calendar(
        countries=[country],
        from_date=today.strftime('%d/%m/%Y'),
        to_date=end_date.strftime('%d/%m/%Y')
    )
    return events


def filter_critical_events(events, impact_levels=['High']):
    # Filter for high-impact news
    return events[events['importance'].isin(impact_levels)]

def send_news_events_to_mt5(account_login, account_password, account_server, country='united states', days_ahead=1):
    """
    Fetch upcoming news events and send them as a message to the MT5 account.
    """
    if not mt5.initialize():
        print("MT5 initialization failed.")
        return False
    authorized = mt5.login(login=account_login, password=account_password, server=account_server)
    if not authorized:
        print("MT5 login failed.")
        mt5.shutdown()
        return False
    events = get_upcoming_events(country, days_ahead)
    if events.empty:
        message = f"No news events found for {country} in next {days_ahead} day(s)."
    else:
        message = f"Upcoming news events for {country} (next {days_ahead} day(s)):\n"
        for idx, event in events.iterrows():
            message += f"{event['date']} {event['time']} {event['event']} [{event['importance']}]\n"
    # Log message to file for daily review
    try:
        with open('news_events.log', 'a', encoding='utf-8') as log_file:
            log_file.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]\n{message}\n\n")
        print("News events logged to news_events.log.")
    except Exception as e:
        print(f"Error logging news events: {e}")
    mt5.shutdown()
    return True

def filter_critical_events(events, impact_levels=['High']):
    # Filter for high-impact news
    return events[events['importance'].isin(impact_levels)]

# Example usage:
# events = get_upcoming_events('united states', 2)
# critical = filter_critical_events(events)
# for idx, event in critical.iterrows():
#     print(event['date'], event['time'], event['event'], event['importance'])
