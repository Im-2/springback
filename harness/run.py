"""Experiment runner: per-ticker and aggregate metrics for a parameter set."""
import numpy as np
import pandas as pd

from .data import DOW30, load_earnings, load_prices, test_window
from .engine import Params, metrics, run

_cache = {}


def _inputs(ticker):
    if ticker not in _cache:
        frame = test_window(load_prices(ticker))
        earnings = load_earnings(ticker)
        # platform has no upcoming dates (probe step 1): keep only reports on or before the last bar
        earnings = earnings[earnings["date"] <= frame.index[-1]].reset_index(drop=True)
        _cache[ticker] = (frame, earnings)
    return _cache[ticker]


def evaluate(params, tickers=DOW30, use_earnings=False, part=None, since=None):
    """Return a per-ticker metrics DataFrame. part in {None, 0, 1, 2} selects a third of the window."""
    rows = {}
    for ticker in tickers:
        frame, earnings = _inputs(ticker)
        trades, daily, held = run(frame, earnings if use_earnings else None, params)
        if part is not None:
            size = len(frame) // 3
            lo, hi = part * size, (part + 1) * size if part < 2 else len(frame)
            start, end = frame.index[lo], frame.index[hi - 1]
            daily, held = daily.iloc[lo:hi], held.iloc[lo:hi]
            trades = trades[(trades["exit"] >= start) & (trades["exit"] <= end)]
        if since is not None:
            keep = daily.index >= since
            daily, held = daily[keep], held[keep]
            trades = trades[trades["exit"] >= since]
        rows[ticker] = metrics(trades, daily, held)
    return pd.DataFrame(rows).T


def buy_and_hold(tickers=DOW30):
    rows = {}
    for ticker in tickers:
        frame, _ = _inputs(ticker)
        daily = frame["Close"].pct_change().fillna(0)
        rows[ticker] = metrics(pd.DataFrame({"ret": []}), daily, pd.Series(True, index=frame.index))
    return pd.DataFrame(rows).T


def summary(table):
    """Aggregate across tickers: equal-weight mean/median of the key metrics + breadth."""
    finite = table.replace([np.inf, -np.inf], np.nan)
    return {
        "tickers": len(table),
        "pos_return": int((table["total_return"] > 0).sum()),
        "pos_sharpe": int((table["sharpe"] > 0).sum()),
        "mean_return": finite["total_return"].mean(),
        "med_return": finite["total_return"].median(),
        "mean_sharpe": finite["sharpe"].mean(),
        "med_sharpe": finite["sharpe"].median(),
        "mean_sortino": finite["sortino"].mean(),
        "mean_maxdd": finite["max_dd"].mean(),
        "med_pf": finite["profit_factor"].median(),
        "mean_win": finite["win_rate"].mean(),
        "trades_total": int(table["trades"].sum()),
        "trades_min": int(table["trades"].min()),
        "trades_med": float(table["trades"].median()),
        "mean_exposure": finite["exposure"].mean(),
    }


if __name__ == "__main__":
    pd.set_option("display.width", 250)
    pd.set_option("display.max_columns", 30)
    base = Params()
    table = evaluate(base)
    print(table.round(3).to_string())
    print(pd.Series(summary(table)).round(3).to_string())
    print("BUY&HOLD", pd.Series(summary(buy_and_hold())).round(3).to_string())
