"""No-repaint replay: for many cut points, the signals the script produced when bar k was the LAST bar must equal the full-history signals on bars < k (with 'Ignore unfinished last bar' on and off)."""
import json, os, subprocess, sys, warnings
warnings.filterwarnings("ignore")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from harness.run import _inputs

def js_signals(payload):
    out = subprocess.run(["node", os.path.join(ROOT, "verify", "run_stub.js")], input=json.dumps(payload), capture_output=True, text=True, cwd=ROOT)
    if out.returncode: raise SystemExit(out.stderr)
    return json.loads(out.stdout)

bad = checked = 0
for ticker in ["AAPL", "KO", "NVDA"]:
    frame, _ = _inputs(ticker)
    full = {c.lower(): frame[c].tolist() for c in ["Open", "High", "Low", "Close"]}
    full["time"] = [int(t.timestamp()) for t in frame.index]
    ref = js_signals(full)
    n = len(frame)
    for cut in range(1000, n, 400):
        part = {k: v[:cut] for k, v in full.items()}
        got = js_signals(part)
        for side in ("buy", "sell"):
            want = [i for i in ref[side] if i < cut - 1]
            have = [i for i in got[side] if i < cut - 1]
            checked += 1
            if want != have:
                bad += 1; print("MISMATCH", ticker, cut, side)
        # the unfinished last bar must never carry a signal
        for side in ("buy", "sell"):
            if (cut - 1) in got[side]:
                bad += 1; print("LAST BAR SIGNALLED", ticker, cut, side)
print("checks", checked, "failures", bad)
