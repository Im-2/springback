"""Final design report: per-ticker table, thirds, sensitivities, ablations."""
import pandas as pd

from .engine import Params
from .run import buy_and_hold, evaluate, summary

FINAL = Params(dip_mode="rsi", rsi_len=3, rsi_thr=25, slow=200, slope_bars=20, fast=10, stop_atr=3.0, max_bars=10)

if __name__ == "__main__":
    pd.set_option("display.width", 250)
    pd.set_option("display.max_columns", 30)
    table = evaluate(FINAL)
    table.to_csv("results_final_per_ticker.csv")
    print(table.round(3).to_string())
    cases = {
        "FINAL (next-open, 2bps)": (FINAL, None),
        "thirds: oldest": (FINAL, 0), "thirds: middle": (FINAL, 1), "thirds: newest": (FINAL, 2),
        "close-fill (not achievable)": (Params(**{**FINAL.__dict__, "fill": "close"}), None),
        "cost 10 bps/side": (Params(**{**FINAL.__dict__, "slip_bps": 10}), None),
        "cost 0": (Params(**{**FINAL.__dict__, "slip_bps": 0}), None),
        "no slope filter (slope_bars=1)": (Params(**{**FINAL.__dict__, "slope_bars": 1}), None),
        "no stop (stop 99 ATR)": (Params(**{**FINAL.__dict__, "stop_atr": 99}), None),
        "no time stop (999)": (Params(**{**FINAL.__dict__, "max_bars": 999}), None),
    }
    rows = {}
    for name, (params, part) in cases.items():
        rows[name] = summary(evaluate(params, part=part))
    out = pd.DataFrame(rows).T
    cols = ["pos_return", "pos_sharpe", "mean_return", "med_return", "mean_sharpe", "mean_sortino", "mean_maxdd", "med_pf", "mean_win", "trades_total", "trades_min", "trades_med", "mean_exposure"]
    print(out[cols].round(3).to_string())
    out.to_csv("results_final_cases.csv")
    print("BUY&HOLD", pd.Series(summary(buy_and_hold())).round(3).to_string())
