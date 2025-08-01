# Liquidity EA Utilities
# - Fair Value Gap (FVG) detection
# - Liquidity pool (swing high/low) detection
# - Order block detection (future extension)

import pandas as pd

def detect_fvg(df, lookback=20):
    """
    Detect bullish and bearish fair value gaps (FVG) in OHLCV DataFrame.
    Returns a list of dicts: {'index': idx, 'type': 'bullish'|'bearish', 'low': low, 'high': high}
    """
    fvg_list = []
    for i in range(2, min(len(df), lookback)):
        # Bullish FVG: candle 1 high < candle 3 low
        if df['high'].iloc[-i] < df['low'].iloc[-i+2]:
            fvg_list.append({'index': len(df)-i, 'type': 'bullish', 'low': df['high'].iloc[-i], 'high': df['low'].iloc[-i+2]})
        # Bearish FVG: candle 1 low > candle 3 high
        if df['low'].iloc[-i] > df['high'].iloc[-i+2]:
            fvg_list.append({'index': len(df)-i, 'type': 'bearish', 'low': df['high'].iloc[-i+2], 'high': df['low'].iloc[-i]})
    return fvg_list

def detect_liquidity_pools(df, window=20):
    """
    Detect swing highs/lows as liquidity pools.
    Returns two lists: swing_highs, swing_lows (each is a list of (index, price))
    """
    swing_highs = []
    swing_lows = []
    for i in range(window, len(df)-window):
        high = df['high'].iloc[i]
        low = df['low'].iloc[i]
        if high == max(df['high'].iloc[i-window:i+window+1]):
            swing_highs.append((i, high))
        if low == min(df['low'].iloc[i-window:i+window+1]):
            swing_lows.append((i, low))
    return swing_highs, swing_lows

# --- Session Detection ---
import datetime
def get_session(dt: datetime.datetime):
    """
    Returns the trading session for a given datetime (UTC):
    - Asia: 23:00-07:59 UTC
    - Europe: 08:00-15:59 UTC
    - New York: 16:00-22:59 UTC
    """
    hour = dt.hour
    if 23 <= hour or hour < 8:
        return "Asia"
    elif 8 <= hour < 16:
        return "Europe"
    else:
        return "New York"
