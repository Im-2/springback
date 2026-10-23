"""Simplified design: RSI(3) dip inside a 200-EMA uptrend, exit on snapback to fast EMA or trend failure. No slope filter, stop or time stop."""
import pandas as pd

from .engine import Params
from .run import evaluate, summary
from .sweep import sweep

SIMPLE = Params(dip_mode="rsi", rsi_len=3, rsi_thr=25, slow=200, slope_bars=0, fast=10, stop_atr=0, max_bars=0)

def case(**changes):
    return Params(**{**SIMPLE.__dict__, **changes})

if __name__ == "__main__":
    pd.set_option("display.width", 250)
    cases = {
        "SIMPLE": (SIMPLE, None),
        "thirds: oldest": (SIMPLE, 0), "thirds: middle": (SIMPLE, 1), "thirds: newest": (SIMPLE, 2),
        "+ time stop 10": (case(max_bars=10), None),
        "+ ATR stop 3": (case(stop_atr=3.0), None),
        "close-fill": (case(fill="close"), None),
        "cost 0": (case(slip_bps=0), None),
        "cost 5 bps/side": (case(slip_bps=5), None),
        "cost 10 bps/side": (case(slip_bps=10), None),
    }
    out = pd.DataFrame({name: summary(evaluate(p, part=part)) for name, (p, part) in cases.items()}).T
    cols = ["pos_return", "pos_sharpe", "mean_return", "med_return", "mean_sharpe", "mean_sortino", "mean_maxdd", "med_pf", "mean_win", "trades_total", "trades_min", "trades_med", "mean_exposure"]
    print(out[cols].round(3).to_string()); out.to_csv("results_simple_cases.csv")
    evaluate(SIMPLE).to_csv("results_simple_per_ticker.csv")
    nb = sweep({"rsi_thr": [15, 20, 25, 30], "slow": [150, 200, 250], "fast": [8, 10, 12]}, base=SIMPLE)
    nb["min_third"] = nb[["sharpe_t1", "sharpe_t2", "sharpe_t3"]].min(axis=1)
    nb.to_csv("results_simple_neighbors.csv", index=False)
    print(nb["mean_sharpe"].describe().round(3).to_string())
    for key in ["rsi_thr", "slow", "fast"]:
        print(nb.groupby(key)[["mean_sharpe", "pos_sharpe", "min_third", "trades_med", "mean_maxdd"]].mean().round(3).T.to_string())
    print(nb[(nb.rsi_thr == 25) & (nb.slow == 200) & (nb.fast == 10)].round(3).T.to_string())
