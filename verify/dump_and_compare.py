"""Export bars, run springback.js in Node with stubbed TrendSpider globals, compare its signals with the Python engine."""
import json, subprocess, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import warnings; warnings.filterwarnings("ignore")
from harness.run import _inputs
from harness.simple import SIMPLE
from harness.engine import run

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
mismatches = 0
for ticker in ["AAPL", "JPM", "KO", "NVDA", "IBM", "V"]:
    frame, _ = _inputs(ticker)
    payload = {c.lower(): frame[c].tolist() for c in ["Open", "High", "Low", "Close"]}
    payload["time"] = [int(t.timestamp()) for t in frame.index]
    out = subprocess.run(["node", os.path.join(ROOT, "verify", "run_stub.js")], input=json.dumps(payload), capture_output=True, text=True, cwd=ROOT)
    if out.returncode:
        print(out.stderr); raise SystemExit(1)
    js = json.loads(out.stdout)
    trades, _, _ = run(frame, None, SIMPLE)
    idx = list(frame.index)
    # python signal bars: buy signal = bar before entry fill, sell signal = bar before exit fill
    py_buy = [idx.index(t) - 1 for t in trades["entry"]]
    py_sell = [idx.index(t) - 1 for t in trades["exit"]]
    js_buy, js_sell = js["buy"], js["sell"]
    # JS ignores the last bar by design; python trades only include filled ones
    same_buy = js_buy[: len(py_buy)] == py_buy
    same_sell = [s for s in js_sell if s <= len(idx) - 2][: len(py_sell)] == py_sell
    print(ticker, "bars", len(idx), "py buys", len(py_buy), "js buys", len(js_buy), "buys equal:", same_buy, "sells equal:", same_sell)
    mismatches += (not same_buy) + (not same_sell)
print("MISMATCHES", mismatches)
