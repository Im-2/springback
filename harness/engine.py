"""Springback strategy + backtest engine (daily bars, long only, alternating, closed-bar signals).

Fill model matches the platform (probe step 2): a signal on bar i fills at the OPEN of bar i+1.
`fill="close"` is the sensitivity variant (fills at the signal bar's close; not achievable on the platform).
"""
from dataclasses import dataclass, replace

import numpy as np
import pandas as pd

from .data import EARNINGS_FIRST_DATE


@dataclass(frozen=True)
class Params:
    slow: int = 100          # slow EMA length (trend filter)
    slope_bars: int = 20     # slow EMA must be higher than this many bars ago
    fast: int = 10           # fast EMA length (dip reference and snapback exit)
    k: float = 1.5           # dip: close at least k ATRs below fast EMA
    stop_atr: float = 3.0    # ATR stop distance from entry fill
    max_bars: int = 10       # time stop, bars held
    atr_len: int = 14        # fixed
    dip_mode: str = "atr"    # "atr": close < fast EMA - k*ATR ; "rsi": RSI(rsi_len) < rsi_thr
    rsi_len: int = 3
    rsi_thr: float = 20.0
    blackout_before: int = 0  # B: calendar days before a report with no new entries (0 = blackout off)
    blackout_after: int = 0   # A: calendar days after a report with no new entries
    pre_exit: bool = False   # exit before an approaching report
    slip_bps: float = 2.0    # slippage per side, basis points
    fee_bps: float = 0.0     # fee per side, basis points
    fill: str = "open"       # "open" (platform) or "close" (sensitivity)
    min_bars: int = 0        # warmup bars skipped; set by caller from slow EMA


def ema(values, length):
    return pd.Series(values).ewm(span=length, adjust=False).mean().to_numpy()


def atr(high, low, close, length):
    prev_close = np.concatenate([[close[0]], close[:-1]])
    true_range = np.maximum(high - low, np.maximum(abs(high - prev_close), abs(low - prev_close)))
    # Wilder smoothing
    return pd.Series(true_range).ewm(alpha=1 / length, adjust=False).mean().to_numpy()


def rsi(values, length):
    delta = pd.Series(values).diff()
    gain = delta.clip(lower=0).ewm(alpha=1 / length, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1 / length, adjust=False).mean()
    return (100 - 100 / (1 + gain / loss.replace(0, np.nan))).fillna(50).to_numpy()


def earnings_flags(index, earnings, params):
    """Per-bar flags from platform-visible earnings only (dates >= 2012-01-24).

    blocked[i]: bar i is inside the entry blackout window (B days before .. A days after a report).
    exit_now[i]: a pre-earnings exit signal fires on bar i (so the fill, at bar i+1's open, is before the gap).
      postmarket report on day D: gap is at D+1 open -> signal on D-1 close, fill D open.
      premarket / unknown report on D: gap is at D open -> signal on D-2 close, fill D-1 open (covers both).
    """
    n = len(index)
    blocked = np.zeros(n, dtype=bool)
    exit_now = np.zeros(n, dtype=bool)
    if earnings is None or not len(earnings):
        return blocked, exit_now
    for _, row in earnings.iterrows():
        report = row["date"]
        if params.blackout_before or params.blackout_after:
            lo = report - pd.Timedelta(days=params.blackout_before)
            hi = report + pd.Timedelta(days=params.blackout_after)
            blocked |= (index >= lo) & (index <= hi)
        if params.pre_exit:
            position = index.searchsorted(report)  # first bar on/after report date
            if position >= n:
                continue
            lead = 1 if row["when"] == "post" else 2
            signal_bar = position - lead
            if 0 <= signal_bar < n:
                exit_now[signal_bar] = True
    return blocked, exit_now


def run(frame, earnings, params):
    """Run one ticker. Returns (trades, daily strategy returns, in-position flags)."""
    index = frame.index
    o, h, l, c = (frame[col].to_numpy(dtype=float) for col in ("Open", "High", "Low", "Close"))
    n = len(frame)
    slow_ema, fast_ema = ema(c, params.slow), ema(c, params.fast)
    atr_values = atr(h, l, c, params.atr_len)
    rsi_values = rsi(c, params.rsi_len) if params.dip_mode == "rsi" else None
    blocked, exit_now = earnings_flags(index, earnings, params)
    warmup = max(params.slow + params.slope_bars, params.min_bars)

    cost = (params.slip_bps + params.fee_bps) / 1e4
    daily = np.zeros(n)
    held_flag = np.zeros(n, dtype=bool)
    trades = []
    in_position = False
    pending = None  # "buy" or "sell", executed at the next bar's open
    entry_fill = entry_bar = entry_atr = None
    open_fill = params.fill == "open"

    for i in range(n):
        # 1) execute the order signalled on the previous bar, at this bar's open
        if pending == "buy":
            entry_fill, entry_bar, entry_atr, in_position = o[i] * (1 + cost), i, atr_values[i - 1], True
            daily[i] += c[i] / entry_fill - 1
            held_flag[i] = True
        elif pending == "sell":
            exit_fill = o[i] * (1 - cost)
            daily[i] += exit_fill / c[i - 1] - 1
            held_flag[i] = True
            trades.append((index[entry_bar], index[i], entry_fill, exit_fill, i - entry_bar))
            in_position = False
        elif in_position:
            daily[i] += c[i] / c[i - 1] - 1
            held_flag[i] = True
        pending = None

        if i < warmup:
            continue

        # 2) decide on bar i's close (closed bars only)
        if in_position:
            held = i - entry_bar
            reason = None
            if c[i] >= fast_ema[i]:
                reason = "snapback"
            elif c[i] < slow_ema[i]:
                reason = "trend"
            elif c[i] <= entry_fill - params.stop_atr * entry_atr:
                reason = "stop"
            elif held >= params.max_bars:
                reason = "time"
            elif params.pre_exit and exit_now[i]:
                reason = "earnings"
            if reason:
                if open_fill:
                    pending = "sell"
                else:  # close-fill sensitivity: exit at this bar's close
                    exit_fill = c[i] * (1 - cost)
                    daily[i] += exit_fill / c[i] - 1
                    trades.append((index[entry_bar], index[i], entry_fill, exit_fill, i - entry_bar))
                    in_position = False
        else:
            trend_ok = c[i] > slow_ema[i] and slow_ema[i] > slow_ema[i - params.slope_bars]
            dip = (c[i] < fast_ema[i] - params.k * atr_values[i]) if rsi_values is None else rsi_values[i] < params.rsi_thr
            if trend_ok and dip and not blocked[i]:
                if open_fill:
                    if i + 1 < n:
                        pending = "buy"
                else:  # close-fill sensitivity: enter at this bar's close
                    entry_fill, entry_bar, entry_atr, in_position = c[i] * (1 + cost), i, atr_values[i], True
                    daily[i] += c[i] / entry_fill - 1
                    held_flag[i] = True
    # open position at the end: mark to last close, do not count as closed trade
    trade_frame = pd.DataFrame(trades, columns=["entry", "exit", "entry_px", "exit_px", "bars"])
    trade_frame["ret"] = trade_frame["exit_px"] / trade_frame["entry_px"] - 1
    return trade_frame, pd.Series(daily, index=index), pd.Series(held_flag, index=index)


def metrics(trades, daily, held=None):
    """Per-ticker metrics over the given daily return series (flat days count as 0 return)."""
    equity = (1 + daily).cumprod()
    total = equity.iloc[-1] - 1
    std = daily.std()
    downside = daily[daily < 0].std()
    drawdown = (equity / equity.cummax() - 1).min()
    wins = trades["ret"][trades["ret"] > 0].sum() if len(trades) else 0.0
    losses = -trades["ret"][trades["ret"] < 0].sum() if len(trades) else 0.0
    return {
        "total_return": total,
        "sharpe": daily.mean() / std * np.sqrt(252) if std > 0 else np.nan,
        "sortino": daily.mean() / downside * np.sqrt(252) if downside and downside > 0 else np.nan,
        "max_dd": drawdown,
        "profit_factor": wins / losses if losses > 0 else (np.inf if wins > 0 else np.nan),
        "win_rate": (trades["ret"] > 0).mean() if len(trades) else np.nan,
        "trades": len(trades),
        "exposure": held.mean() if held is not None else (daily != 0).mean(),
        "avg_trade": trades["ret"].mean() if len(trades) else np.nan,
    }


def with_params(params, **changes):
    return replace(params, **changes)
