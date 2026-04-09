"""
╔══════════════════════════════════════════════════════════════╗
║           APEX ALGO TRADING — DATA FETCHERS                  ║
║   Fetch real OHLCV data from multiple sources                ║
║                                                              ║
║   Sources  : Yahoo Finance | Upstox | Zerodha | Binance      ║
║              Alpha Vantage                                    ║
║   Extras   : Upstox token exchange helper                    ║
║              OHLCV preprocessor / cleaner                    ║
╚══════════════════════════════════════════════════════════════╝

QUICK START — UPSTOX
─────────────────────
  Step 1: Run upstox_get_login_url()  →  opens browser login
  Step 2: After login you get redirected to:
            http://localhost:5000/callback?code=XXXXXX
          Copy the code= value.
  Step 3: Run upstox_exchange_token("XXXXXX")  →  prints access token
  Step 4: Paste the token into UPSTOX_ACCESS_TOKEN below, OR
          pass it directly: fetch_upstox(..., access_token="...")

NOTE  : Upstox access tokens expire daily. Repeat Steps 1-3 each day.
WARNING: Never share your API Secret or Access Token publicly.
"""

from __future__ import annotations

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

__all__ = [
    "upstox_get_login_url",
    "upstox_exchange_token",
    "fetch_yahoo",
    "fetch_upstox",
    "fetch_zerodha",
    "fetch_binance",
    "fetch_alpha_vantage",
    "preprocess",
]

# ══════════════════════════════════════════════════════════════
#  UPSTOX CREDENTIALS
#  Regenerate your API Secret if it was ever shared publicly:
#  https://developer.upstox.com/ → My Apps → Algo Bot → ↺
# ══════════════════════════════════════════════════════════════

UPSTOX_API_KEY    = "462da3be-44e0-438c-b57b-f31873f0f753"
UPSTOX_API_SECRET = "7wlq7ipauj"          # ← regenerate this after exposing it!
UPSTOX_REDIRECT   = "http://localhost:5000/callback"

# Paste your daily access token here after running upstox_exchange_token()
UPSTOX_ACCESS_TOKEN: str = "eyJ0eXAiOiJKV1QiLCJrZXlfaWQiOiJza192MS4wIiwiYWxnIjoiSFMyNTYifQ.eyJzdWIiOiI2TEE2WFEiLCJqdGkiOiI2OWQ2OWQ0ZGExMTJkOTA0ZWI5ZDkzZjEiLCJpc011bHRpQ2xpZW50IjpmYWxzZSwiaXNQbHVzUGxhbiI6dHJ1ZSwiaWF0IjoxNzc1NjcyNjUzLCJpc3MiOiJ1ZGFwaS1nYXRld2F5LXNlcnZpY2UiLCJleHAiOjE3NzU2ODU2MDB9.cYdgsyslL70RJ0xscCAGNunkchyddKaWR5GteVumafU"


# ══════════════════════════════════════════════════════════════
#  UPSTOX TOKEN HELPERS
# ══════════════════════════════════════════════════════════════

def upstox_get_login_url(
    api_key: str = UPSTOX_API_KEY,
    redirect_uri: str = UPSTOX_REDIRECT,
) -> str:
    """
    Build and print the Upstox OAuth login URL.
    Open this URL in a browser, log in, and copy the
    `code=` value from the redirected URL.

    Usage:
        url = upstox_get_login_url()
        # After login → http://localhost:5000/callback?code=XXXXXX
        # Copy XXXXXX and pass to upstox_exchange_token()
    """
    from urllib.parse import urlencode
    params = {
        "response_type": "code",
        "client_id":     api_key,
        "redirect_uri":  redirect_uri,
    }
    url = "https://api.upstox.com/v2/login/authorization/dialog?" + urlencode(params)

    print("\n── Upstox Login URL ─────────────────────────────────────")
    print(url)
    print("─────────────────────────────────────────────────────────")
    print("1. Open the URL above in your browser.")
    print("2. Log in with your Upstox account.")
    print("3. After login, copy the `code=` value from the redirect URL.")
    print("4. Call: upstox_exchange_token('<paste code here>')\n")

    try:
        import webbrowser
        webbrowser.open(url)
        print("   (Browser opened automatically)")
    except Exception:
        pass

    return url


def upstox_exchange_token(
    auth_code: str,
    api_key: str      = UPSTOX_API_KEY,
    api_secret: str   = UPSTOX_API_SECRET,
    redirect_uri: str = UPSTOX_REDIRECT,
) -> str:
    """
    Exchange a one-time authorization code for an Upstox access token.

    Usage:
        # After login redirect gives: ?code=XXXXXX
        token = upstox_exchange_token("XXXXXX")

        # Then either set the global:
        #   UPSTOX_ACCESS_TOKEN = token
        # Or pass directly:
        #   fetch_upstox(..., access_token=token)

    Returns:
        access_token string, or "" on failure.
    """
    try:
        import requests
    except ImportError:
        print("  [ERROR] requests not installed. Run: pip install requests")
        return ""

    try:
        response = requests.post(
            "https://api.upstox.com/v2/login/authorization/token",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={
                "code":          auth_code,
                "client_id":     api_key,
                "client_secret": api_secret,
                "redirect_uri":  redirect_uri,
                "grant_type":    "authorization_code",
            },
            timeout=15,
        )
        response.raise_for_status()
        data = response.json()

        token = data.get("access_token", "")
        if not token:
            print(f"  [ERROR] Token exchange failed. Response: {data}")
            return ""

        print("\n── Upstox Access Token ──────────────────────────────────")
        print(f"  {token}")
        print("─────────────────────────────────────────────────────────")
        print("Copy the token above and either:")
        print("  • Set  UPSTOX_ACCESS_TOKEN = '<token>'  in this file")
        print("  • Or pass  access_token='<token>'  to fetch_upstox()")
        print("  ⚠  Token expires daily. Regenerate each trading day.\n")
        return token

    except Exception as e:
        print(f"  [ERROR] Token exchange failed: {e}")
        return ""


# ══════════════════════════════════════════════════════════════
#  YAHOO FINANCE  (Free, Global — no API key needed)
# ══════════════════════════════════════════════════════════════

def fetch_yahoo(
    symbol: str,
    period: str   = "2y",
    interval: str = "1d",
) -> pd.DataFrame:
    """
    Fetch OHLCV from Yahoo Finance (FREE, no API key needed).

    symbol   : Yahoo ticker  e.g. "RELIANCE.NS", "^NSEI", "BTC-USD"
    period   : "1d","5d","1mo","3mo","6mo","1y","2y","5y","10y","ytd","max"
    interval : "1m","2m","5m","15m","30m","60m","90m","1h",
               "1d","5d","1wk","1mo","3mo"

    Note: Intraday data (< 1d) is only available for the last 60 days.

    Examples:
        fetch_yahoo("RELIANCE.NS", "1y",  "1d")   # NSE daily
        fetch_yahoo("^NSEI",       "6mo", "1h")   # Nifty50 hourly
        fetch_yahoo("BTC-USD",     "3mo", "1h")   # Bitcoin hourly
        fetch_yahoo("TCS.NS",      "2y",  "1d")   # TCS daily
    """
    try:
        import yfinance as yf
    except ImportError:
        print("  [ERROR] yfinance not installed. Run: pip install yfinance")
        return pd.DataFrame()

    try:
        df: pd.DataFrame = yf.download(
            symbol,
            period=period,
            interval=interval,
            progress=False,
            auto_adjust=True,   # adjusts for splits/dividends automatically
        )

        if df.empty:
            print(f"  [Yahoo] No data returned for {symbol!r}. Check symbol/period.")
            return pd.DataFrame()

        # Flatten MultiIndex columns returned by yfinance >= 0.2.x
        # e.g. ("Close", "RELIANCE.NS") → "close"
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [col[0].lower() for col in df.columns]
        else:
            df.columns = [c.lower() for c in df.columns]

        available = [c for c in ["open", "high", "low", "close", "volume"]
                     if c in df.columns]
        if len(available) < 5:
            print(f"  [Yahoo] Unexpected columns: {df.columns.tolist()}")
            return pd.DataFrame()

        df = df[available].dropna()
        print(f"  [Yahoo] Loaded {len(df)} bars for {symbol}  "
              f"({df.index[0].date()} → {df.index[-1].date()})")
        return df

    except Exception as e:
        print(f"  [ERROR] Yahoo fetch failed: {e}")
        return pd.DataFrame()


# ══════════════════════════════════════════════════════════════
#  UPSTOX  (India, Free Tier Available)
# ══════════════════════════════════════════════════════════════

def fetch_upstox(
    instrument_key: str,
    interval: str        = "day",
    from_date: str       = "2020-01-01",
    to_date: str         = "2025-12-31",
    access_token: str | None = None,
) -> pd.DataFrame:
    """
    Fetch OHLCV from Upstox API v2.

    instrument_key : Upstox instrument key
                     e.g. "NSE_INDEX|Nifty 50"
                          "NSE_EQ|INE002A01018"   (Reliance)
    interval       : "1minute","30minute","1hour","1day","1week","1month"
    from_date      : "YYYY-MM-DD"
    to_date        : "YYYY-MM-DD"
    access_token   : Daily token from upstox_exchange_token().
                     If None, uses UPSTOX_ACCESS_TOKEN global.

    How to get your daily token:
        url   = upstox_get_login_url()         # step 1
        token = upstox_exchange_token(code)    # step 2
        df    = fetch_upstox("NSE_INDEX|Nifty 50", access_token=token)

    Common instrument keys:
        Nifty 50    → "NSE_INDEX|Nifty 50"
        Bank Nifty  → "NSE_INDEX|Nifty Bank"
        Reliance    → "NSE_EQ|INE002A01018"
        TCS         → "NSE_EQ|INE467B01029"
        HDFC Bank   → "NSE_EQ|INE040A01034"
        Infosys     → "NSE_EQ|INE009A01021"
    """
    # Resolve token at call time (not definition time) so updating the global works
    resolved_token = access_token if access_token is not None else UPSTOX_ACCESS_TOKEN
    if not resolved_token:
        print("  [ERROR] Upstox access_token is empty.")
        print("          Run: token = upstox_exchange_token('<your auth code>')")
        print("          Then pass access_token=token  OR  set UPSTOX_ACCESS_TOKEN = token")
        return pd.DataFrame()

    try:
        import upstox_client
    except ImportError:
        print("  [ERROR] upstox-python-sdk not installed.")
        print("          Run: pip install upstox-python-sdk")
        return pd.DataFrame()

    try:
        config = upstox_client.Configuration()
        config.access_token = resolved_token

        api = upstox_client.HistoryApi(upstox_client.ApiClient(config))
        response = api.get_historical_candle_data1(
            instrument_key, interval, to_date, from_date, api_version="2.0"
        )
        candles = response.data.candles
        if not candles:
            print(f"  [Upstox] No candles returned for {instrument_key!r}")
            return pd.DataFrame()

        df = pd.DataFrame(
            candles,
            columns=["datetime", "open", "high", "low", "close", "volume", "oi"]
        )
        df["datetime"] = pd.to_datetime(df["datetime"])
        df = df.set_index("datetime").sort_index()
        df = df[["open", "high", "low", "close", "volume"]]
        print(f"  [Upstox] Loaded {len(df)} bars for {instrument_key}  "
              f"({df.index[0].date()} → {df.index[-1].date()})")
        return df

    except Exception as e:
        print(f"  [ERROR] Upstox fetch failed: {e}")
        return pd.DataFrame()


# ══════════════════════════════════════════════════════════════
#  ZERODHA KITE  (India, Requires API Key)
# ══════════════════════════════════════════════════════════════

def fetch_zerodha(
    instrument_token: int,
    interval: str     = "60minute",
    days: int         = 60,
    api_key: str      = "",
    access_token: str = "",
) -> pd.DataFrame:
    """
    Fetch OHLCV from Zerodha Kite Connect API.

    instrument_token : Zerodha numeric token (from instruments CSV)
    interval         : "minute","3minute","5minute","10minute",
                       "15minute","30minute","60minute","day"
    days             : How many days back to fetch
    api_key          : Your Kite Connect API key
    access_token     : Your Kite access token (regenerated daily)

    Get API credentials: https://developers.zerodha.com

    Example:
        df = fetch_zerodha(
            instrument_token = 738561,    # RELIANCE
            interval         = "60minute",
            days             = 30,
            api_key          = "your_api_key",
            access_token     = "your_token",
        )
    """
    try:
        from kiteconnect import KiteConnect
    except ImportError:
        print("  [ERROR] kiteconnect not installed. Run: pip install kiteconnect")
        return pd.DataFrame()

    if not api_key or not access_token:
        print("  [ERROR] Zerodha requires both api_key and access_token.")
        return pd.DataFrame()

    try:
        kite = KiteConnect(api_key=api_key)
        kite.set_access_token(access_token)

        end_date   = datetime.now()
        start_date = end_date - timedelta(days=days)

        data = kite.historical_data(instrument_token, start_date, end_date, interval)
        if not data:
            print("  [Zerodha] No data returned.")
            return pd.DataFrame()

        df = pd.DataFrame(data)
        df = df.rename(columns={"date": "datetime"}).set_index("datetime")
        df.index = pd.to_datetime(df.index)
        df.columns = [c.lower() for c in df.columns]
        df = df[["open", "high", "low", "close", "volume"]]
        print(f"  [Zerodha] Loaded {len(df)} bars  "
              f"({df.index[0].date()} → {df.index[-1].date()})")
        return df

    except Exception as e:
        print(f"  [ERROR] Zerodha fetch failed: {e}")
        return pd.DataFrame()


# ══════════════════════════════════════════════════════════════
#  BINANCE  (Crypto, Free — no API key needed)
# ══════════════════════════════════════════════════════════════

def fetch_binance(
    symbol: str   = "BTCUSDT",
    interval: str = "1h",
    limit: int    = 1000,
) -> pd.DataFrame:
    """
    Fetch crypto OHLCV from Binance public API (no key needed).

    symbol   : Binance pair  e.g. "BTCUSDT", "ETHUSDT", "BNBUSDT"
    interval : "1m","3m","5m","15m","30m","1h","2h","4h",
               "6h","8h","12h","1d","3d","1w","1M"
    limit    : Number of bars to fetch. Binance hard cap = 1000.

    Examples:
        fetch_binance("BTCUSDT", "1h",  1000)
        fetch_binance("ETHUSDT", "4h",  500)
        fetch_binance("SOLUSDT", "1d",  365)
    """
    if limit > 1000:
        print(f"  [Binance] limit={limit} exceeds Binance max of 1000; clamping to 1000.")
        limit = 1000

    try:
        import requests
    except ImportError:
        print("  [ERROR] requests not installed. Run: pip install requests")
        return pd.DataFrame()

    try:
        url      = "https://api.binance.com/api/v3/klines"
        params   = {"symbol": symbol, "interval": interval, "limit": limit}
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if not data:
            print(f"  [Binance] No data returned for {symbol!r}")
            return pd.DataFrame()

        df = pd.DataFrame(data, columns=[
            "timestamp", "open", "high", "low", "close", "volume",
            "close_time", "quote_volume", "trades",
            "taker_buy_base", "taker_buy_quote", "ignore",
        ])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df = df.set_index("timestamp")
        df = df[["open", "high", "low", "close", "volume"]].astype(float)
        print(f"  [Binance] Loaded {len(df)} bars for {symbol}  "
              f"({df.index[0].date()} → {df.index[-1].date()})")
        return df

    except Exception as e:
        print(f"  [ERROR] Binance fetch failed: {e}")
        return pd.DataFrame()


# ══════════════════════════════════════════════════════════════
#  ALPHA VANTAGE  (Free tier: 25 req/day)
# ══════════════════════════════════════════════════════════════

def fetch_alpha_vantage(
    symbol: str,
    api_key: str,
    interval: str = "60min",
) -> pd.DataFrame:
    """
    Fetch OHLCV from Alpha Vantage.
    Free key: https://www.alphavantage.co/support/#api-key

    symbol   : e.g. "IBM", "AAPL", "MSFT"
    api_key  : Your Alpha Vantage API key
    interval : Intraday  → "1min","5min","15min","30min","60min"
               Daily     → "daily"
               Weekly    → "weekly"
               Monthly   → "monthly"

    Examples:
        fetch_alpha_vantage("IBM",  "YOUR_KEY", "60min")  # intraday
        fetch_alpha_vantage("AAPL", "YOUR_KEY", "daily")  # daily
    """
    try:
        import requests
    except ImportError:
        print("  [ERROR] requests not installed. Run: pip install requests")
        return pd.DataFrame()

    _FUNCTION_MAP = {
        "daily":   "TIME_SERIES_DAILY",
        "weekly":  "TIME_SERIES_WEEKLY",
        "monthly": "TIME_SERIES_MONTHLY",
    }
    is_intraday = interval.endswith("min")
    function    = ("TIME_SERIES_INTRADAY" if is_intraday
                   else _FUNCTION_MAP.get(interval.lower(), "TIME_SERIES_DAILY"))

    try:
        params: dict = {
            "function":   function,
            "symbol":     symbol,
            "apikey":     api_key,
            "outputsize": "full",
            "datatype":   "json",
        }
        if is_intraday:
            params["interval"] = interval   # only valid for intraday endpoint

        response = requests.get(
            "https://www.alphavantage.co/query",
            params=params, timeout=15
        )
        response.raise_for_status()
        data = response.json()

        if "Error Message" in data:
            print(f"  [ERROR] AlphaVantage: {data['Error Message']}")
            return pd.DataFrame()
        if "Note" in data:
            print(f"  [WARN]  AlphaVantage rate-limit hit: {data['Note']}")
            return pd.DataFrame()
        if "Information" in data:
            print(f"  [WARN]  AlphaVantage: {data['Information']}")
            return pd.DataFrame()

        ts_key = next((k for k in data if "Time Series" in k), None)
        if ts_key is None:
            print(f"  [ERROR] AlphaVantage unexpected response keys: {list(data.keys())}")
            return pd.DataFrame()

        df = pd.DataFrame(data[ts_key]).T
        df.index = pd.to_datetime(df.index)

        # AV column names look like "1. open", "2. high", etc. — strip the prefix
        df.columns = [c.split(". ", 1)[-1].lower() for c in df.columns]
        df = df.rename(columns={"adjusted close": "close"})   # weekly/monthly

        for col in ["open", "high", "low", "close", "volume"]:
            if col not in df.columns:
                print(f"  [ERROR] AlphaVantage missing column: {col!r}")
                return pd.DataFrame()

        df = df[["open", "high", "low", "close", "volume"]].astype(float).sort_index()
        print(f"  [AlphaVantage] Loaded {len(df)} bars for {symbol}  "
              f"({df.index[0].date()} → {df.index[-1].date()})")
        return df

    except Exception as e:
        print(f"  [ERROR] AlphaVantage fetch failed: {e}")
        return pd.DataFrame()


# ══════════════════════════════════════════════════════════════
#  OHLCV PREPROCESSOR
# ══════════════════════════════════════════════════════════════

def preprocess(df: pd.DataFrame, remove_outliers: bool = True) -> pd.DataFrame:
    """
    Clean, validate, and normalise an OHLCV DataFrame.

    Steps:
      1. Normalise column names to lowercase
      2. Drop rows with any NaN
      3. Fix OHLC relationships  (high = row-max, low = row-min)
      4. Remove zero or negative volume bars
      5. (Optional) Remove extreme return outliers (99.9th percentile)
      6. Sort chronologically

    Returns cleaned DataFrame.
    Raises ValueError on empty input or missing required columns.
    """
    if df.empty:
        raise ValueError("preprocess(): Input DataFrame is empty.")

    df = df.copy()
    df.columns = [c.lower().strip() for c in df.columns]

    required = ["open", "high", "low", "close", "volume"]
    missing  = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"preprocess(): Missing columns: {missing}")

    df = df[required].dropna()

    # Fix any OHLC relationship violations
    ohlc       = df[["open", "high", "low", "close"]]
    df["high"] = ohlc.max(axis=1)
    df["low"]  = ohlc.min(axis=1)

    # Drop zero / negative volume bars
    df = df[df["volume"] > 0]

    # Remove extreme outliers via 99.9th-percentile absolute return filter
    # fillna(0) ensures the very first row (NaN from pct_change) is never dropped
    if remove_outliers and len(df) > 1:
        returns = df["close"].pct_change().abs().fillna(0)
        q999    = returns.quantile(0.999)
        df      = df[returns <= q999]

    df = df.sort_index()

    if df.empty:
        print("  [PREPROCESS] Warning: All rows removed after cleaning.")
        return df

    print(f"  [PREPROCESS] {len(df)} bars  "
          f"({df.index[0].date()} → {df.index[-1].date()})  "
          f"| close: {df['close'].min():.2f} – {df['close'].max():.2f}")
    return df


# ══════════════════════════════════════════════════════════════
#  ENTRY POINT — DEMO & TEST
# ══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    SEP = "═" * 60

    # ── 1. Binance (no credentials, always works) ─────────────
    print(SEP)
    print("  TEST 1 — Binance BTCUSDT hourly (500 bars)")
    print(SEP)
    btc = fetch_binance("BTCUSDT", "1h", 500)
    if not btc.empty:
        btc = preprocess(btc)
        print(btc.tail(3).to_string())

    # ── 2. Yahoo Finance ──────────────────────────────────────
    print()
    print(SEP)
    print("  TEST 2 — Nifty 50 daily via Yahoo Finance")
    print(SEP)
    nifty = fetch_yahoo("^NSEI", "3mo", "1d")
    if not nifty.empty:
        nifty = preprocess(nifty)
        print(nifty.tail(3).to_string())

    # ── 3. Upstox guide ───────────────────────────────────────
    print()
    print(SEP)
    print("  UPSTOX — How to get your access token each day")
    print(SEP)
    print("""
  from data_fetchers import upstox_get_login_url, upstox_exchange_token, fetch_upstox

  # Step 1 — open browser login
  upstox_get_login_url()

  # Step 2 — after login, browser redirects to:
  #   http://localhost:5000/callback?code=XXXXXX
  #   Copy XXXXXX

  # Step 3 — exchange code for token
  token = upstox_exchange_token("XXXXXX")

  # Step 4 — fetch data
  df = fetch_upstox(
      instrument_key = "NSE_INDEX|Nifty 50",
      interval       = "1day",
      from_date      = "2024-01-01",
      to_date        = "2024-12-31",
      access_token   = token,
  )

  Common instrument keys:
    Nifty 50    →  "NSE_INDEX|Nifty 50"
    Bank Nifty  →  "NSE_INDEX|Nifty Bank"
    Reliance    →  "NSE_EQ|INE002A01018"
    TCS         →  "NSE_EQ|INE467B01029"
    HDFC Bank   →  "NSE_EQ|INE040A01034"
    Infosys     →  "NSE_EQ|INE009A01021"
    """)

    # ── 4. All other examples ─────────────────────────────────
    print(SEP)
    print("  Copy-paste ready examples")
    print(SEP)
    print("""
  # Yahoo — Indian stocks & indices
  reliance = fetch_yahoo("RELIANCE.NS", "1y",  "1d")
  tcs      = fetch_yahoo("TCS.NS",      "6mo", "1d")
  nifty_h  = fetch_yahoo("^NSEI",       "1mo", "1h")
  bnkn     = fetch_yahoo("^NSEBANK",    "3mo", "1d")

  # Binance — Crypto pairs
  eth  = fetch_binance("ETHUSDT", "4h", 1000)
  sol  = fetch_binance("SOLUSDT", "1d",  365)
  bnb  = fetch_binance("BNBUSDT", "1h", 1000)

  # Alpha Vantage — US stocks (free key, 25 req/day)
  ibm  = fetch_alpha_vantage("IBM",  "YOUR_AV_KEY", "60min")
  aapl = fetch_alpha_vantage("AAPL", "YOUR_AV_KEY", "daily")

  # Zerodha Kite
  rel_z = fetch_zerodha(
      instrument_token = 738561,       # Reliance token
      interval         = "60minute",
      days             = 30,
      api_key          = "YOUR_KITE_KEY",
      access_token     = "YOUR_KITE_TOKEN",
  )
    """)