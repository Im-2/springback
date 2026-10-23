# Springback results log

Honest record of what was measured. Nothing here predicts future performance.

## Phase 1: harness (daily bars)
- Universe: current Dow 30 per Wikipedia "List of DJIA companies" (Alphabet added 2026-06-29, Verizon no longer listed; cross-checked with a second site). Data: yfinance daily, split-adjusted, not dividend-adjusted (like the platform). Last 7,000 daily bars per ticker (GOOGL, CRM, V have fewer: 5,581 / 5,621 / 4,680).
- Fill model: signal on bar i fills at open of bar i+1 (confirmed on the platform, probe step 2). Close-fill is a sensitivity only. Cost: 2 bps slippage per side, no commission (the Strategy Tester's default cost was 0%).
- Earnings: yfinance report dates used as a PROXY for TrendSpider's records, only from 2012-01-24 and only up to the last bar (the platform returned no future dates). Earlier years: no blackout, as on the platform.
- Checks: trade-compounded return equals daily equity return (open and close fills); results on a truncated history reproduce the same trades (a first no-repaint sanity check; a full bar-by-bar replay comes with the JS port).
- First default run (slow EMA 100, slope 20, fast EMA 10, k 1.5 ATR, ATR stop 3, time stop 10, no blackout): 20/30 tickers positive, 837 trades total (18..48 per ticker), exposure ~2%. Too few trades and too little exposure to call robust. This is a starting point, not a design.
