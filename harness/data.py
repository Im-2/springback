"""Download and cache daily OHLCV and earnings dates for the Dow 30 (cache lives in data/, which is git-ignored)."""
import os
import warnings

import pandas as pd
import yfinance as yf

warnings.filterwarnings("ignore")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, "data")

# Current Dow 30: Wikipedia list of DJIA companies, Alphabet added 2026-06-29 (Verizon no longer listed).
DOW30 = [
    "MMM", "GOOGL", "AXP", "AMGN", "AMZN", "AAPL", "BA", "CAT", "CVX", "CSCO",
    "KO", "DIS", "GS", "HD", "HON", "IBM", "JNJ", "JPM", "MCD", "MRK",
    "MSFT", "NKE", "NVDA", "PG", "CRM", "SHW", "TRV", "UNH", "V", "WMT",
]
# Platform window: 7,000 candles. Platform earnings data starts here (probe step 3).
TEST_CANDLES = 7000
EARNINGS_FIRST_DATE = pd.Timestamp("2012-01-24")


def load_prices(ticker):
    """Daily bars, split-adjusted but not dividend-adjusted (like the platform), regular session only."""
    path = os.path.join(CACHE, f"{ticker}_1d.parquet")
    if os.path.exists(path):
        return pd.read_parquet(path)
    os.makedirs(CACHE, exist_ok=True)
    frame = yf.download(ticker, period="max", interval="1d", progress=False, auto_adjust=False)
    frame.columns = [column[0] for column in frame.columns]
    frame = frame[["Open", "High", "Low", "Close", "Volume"]].dropna()
    frame.index = pd.DatetimeIndex(frame.index).tz_localize(None)
    frame.to_parquet(path)
    return frame


def load_earnings(ticker):
    """Report timestamps as (date, when) with when in {'pre', 'post', 'unknown'}, from 2012-01-24 only."""
    path = os.path.join(CACHE, f"{ticker}_earnings.parquet")
    if os.path.exists(path):
        return pd.read_parquet(path)
    os.makedirs(CACHE, exist_ok=True)
    try:
        dates = yf.Ticker(ticker).get_earnings_dates(limit=100)
    except Exception:
        dates = None
    rows = []
    if dates is not None and len(dates):
        for stamp in dates.index:
            local = stamp.tz_convert("America/New_York") if stamp.tzinfo else stamp
            hour = local.hour + local.minute / 60
            when = "pre" if hour < 12 else ("post" if hour >= 15 else "unknown")
            rows.append({"date": pd.Timestamp(local.date()), "when": when})
    frame = pd.DataFrame(rows, columns=["date", "when"]).drop_duplicates("date").sort_values("date")
    frame = frame[frame["date"] >= EARNINGS_FIRST_DATE].reset_index(drop=True)
    frame.to_parquet(path)
    return frame


def test_window(prices):
    """The platform tests the most recent 7,000 candles."""
    return prices.iloc[-TEST_CANDLES:]
