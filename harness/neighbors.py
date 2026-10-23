"""Neighbor test around the RSI design (no earnings), with thirds."""
import pandas as pd

from .blackout import BASE
from .sweep import sweep

if __name__ == "__main__":
    pd.set_option("display.width", 250)
    out = sweep({"rsi_thr": [15, 20, 25, 30], "slow": [150, 200, 250], "fast": [8, 10, 12], "slope_bars": [10, 20, 40]}, base=BASE)
    out["min_third"] = out[["sharpe_t1", "sharpe_t2", "sharpe_t3"]].min(axis=1)
    out.to_csv("results_neighbors.csv", index=False)
    cols = ["rsi_thr", "slow", "fast", "slope_bars", "pos_sharpe", "mean_sharpe", "mean_return", "mean_maxdd", "trades_min", "trades_med", "min_third"]
    print(out.sort_values("mean_sharpe", ascending=False)[cols].round(3).head(10).to_string())
    print(out["mean_sharpe"].describe().round(3).to_string())
    for key in ["rsi_thr", "slow", "fast", "slope_bars"]:
        print(out.groupby(key)[["mean_sharpe", "pos_sharpe", "min_third", "trades_med"]].mean().round(3).T.to_string())
    ref = out[(out.rsi_thr == 20) & (out.slow == 200) & (out.fast == 10) & (out.slope_bars == 20)]
    print("REFERENCE", ref[cols].round(3).to_string())
