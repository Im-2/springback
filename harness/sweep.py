"""Parameter sweeps. Usage: python -m harness.sweep <name>"""
import itertools
import sys
import time

import pandas as pd

from .engine import Params
from .run import evaluate, summary


def sweep(grid, base=Params(), use_earnings=False, thirds=True):
    names = list(grid)
    rows = []
    for values in itertools.product(*grid.values()):
        params = Params(**{**base.__dict__, **dict(zip(names, values))})
        table = evaluate(params, use_earnings=use_earnings)
        row = dict(zip(names, values))
        row.update({key: value for key, value in summary(table).items()})
        if thirds:
            for part in range(3):
                sub = evaluate(params, use_earnings=use_earnings, part=part)
                row[f"sharpe_t{part + 1}"] = sub["sharpe"].replace([float("inf")], float("nan")).mean()
        rows.append(row)
    return pd.DataFrame(rows)


if __name__ == "__main__":
    pd.set_option("display.width", 250)
    pd.set_option("display.max_columns", 40)
    start = time.time()
    name = sys.argv[1]
    if name == "atr":
        out = sweep({"slow": [50, 100, 200], "fast": [5, 10, 20], "k": [0.5, 1.0, 1.5], "stop_atr": [2.0, 3.0, 4.0], "max_bars": [5, 10, 20]})
    elif name == "rsi":
        out = sweep({"slow": [50, 100, 200], "fast": [5, 10, 20], "rsi_thr": [10, 20, 30], "stop_atr": [2.0, 3.0, 4.0], "max_bars": [5, 10, 20]}, base=Params(dip_mode="rsi"))
    out.to_csv(f"results_sweep_{name}.csv", index=False)
    print(out.sort_values("mean_sharpe", ascending=False).head(15).round(3).to_string())
    print("secs", time.time() - start)
