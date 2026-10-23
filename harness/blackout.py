"""With/without earnings blackout, restricted to bars where the platform has earnings data (2012-01-24 onward)."""
import pandas as pd

from .data import EARNINGS_FIRST_DATE
from .engine import Params
from .run import evaluate, summary

BASE = Params(dip_mode="rsi", rsi_len=3, rsi_thr=20, slow=200, slope_bars=20, fast=10, stop_atr=3.0, max_bars=10)
VARIANTS = {
    "none": dict(),
    "post A=1": dict(blackout_after=1),
    "post A=3": dict(blackout_after=3),
    "post A=5": dict(blackout_after=5),
    "pre B=3": dict(blackout_before=3),
    "pre B=7": dict(blackout_before=7),
    "pre B=7 + post A=3": dict(blackout_before=7, blackout_after=3),
    "pre-exit only": dict(pre_exit=True),
    "pre-exit + B=7 + A=3": dict(pre_exit=True, blackout_before=7, blackout_after=3),
}

if __name__ == "__main__":
    pd.set_option("display.width", 250)
    rows = []
    for name, changes in VARIANTS.items():
        params = Params(**{**BASE.__dict__, **changes})
        table = evaluate(params, use_earnings=True, since=EARNINGS_FIRST_DATE)
        row = {"variant": name}
        row.update(summary(table))
        rows.append(row)
    out = pd.DataFrame(rows).set_index("variant")
    cols = ["pos_sharpe", "mean_sharpe", "med_sharpe", "mean_return", "mean_maxdd", "med_pf", "mean_win", "trades_total", "mean_exposure"]
    print(out[cols].round(3).to_string())
    out.to_csv("results_blackout.csv")
