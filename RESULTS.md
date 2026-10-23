# Springback results log

Honest record of what was measured. Nothing here predicts future performance.

## Phase 1: harness (daily bars)
- Universe: current Dow 30 per Wikipedia "List of DJIA companies" (Alphabet added 2026-06-29, Verizon no longer listed; cross-checked with a second site). Data: yfinance daily, split-adjusted, not dividend-adjusted (like the platform). Last 7,000 daily bars per ticker (GOOGL, CRM, V have fewer: 5,581 / 5,621 / 4,680).
- Fill model: signal on bar i fills at open of bar i+1 (confirmed on the platform, probe step 2). Close-fill is a sensitivity only. Cost: 2 bps slippage per side, no commission (the Strategy Tester's default cost was 0%).
- Earnings: yfinance report dates used as a PROXY for TrendSpider's records, only from 2012-01-24 and only up to the last bar (the platform returned no future dates). Earlier years: no blackout, as on the platform.
- Checks: trade-compounded return equals daily equity return (open and close fills); results on a truncated history reproduce the same trades (a first no-repaint sanity check; a full bar-by-bar replay comes with the JS port).
- First default run (slow EMA 100, slope 20, fast EMA 10, k 1.5 ATR, ATR stop 3, time stop 10, no blackout): 20/30 tickers positive, 837 trades total (18..48 per ticker), exposure ~2%. Too few trades and too little exposure to call robust. This is a starting point, not a design.

## Phase 2a: dip trigger and first sweeps (no earnings, daily, 30 tickers, next-open fills)
Two 243-config grids (slow EMA 50/100/200, fast EMA 5/10/20, stop 2/3/4 ATR, time stop 5/10/20 bars, plus k = 0.5/1.0/1.5 ATR for the ATR trigger or RSI(3) < 10/20/30 for the RSI trigger). Metric: mean Sharpe across tickers (daily returns, flat days count as zero).
- Stops and time stop barely matter: mean Sharpe moves by ~0.01 across their values. They are kept as safety rails, not tuning knobs.
- Slow EMA: monotone 50 < 100 < 200 in both grids (RSI: 0.143 / 0.164 / 0.208). 200 is the edge of what was tested; 200 is also the conventional trend filter, so it is kept and not pushed longer.
- ATR trigger needs k <= 1.0 to trade enough (k = 1.5: ~23 trades per ticker over ~28 years, 2% exposure). RSI(3) < 20 or 30 trades 130-290 times per ticker.
- Grid medians: RSI trigger mean Sharpe 0.181, ATR trigger 0.140. Best configs of the two are equal (~0.25), so no clever-vs-simple gap. Chose the RSI trigger (grid-wide better, one well-known idea).
- Best-config buy-and-hold comparison (full window): buy and hold mean Sharpe 0.47 with mean max drawdown -69%; the strategy sits at ~0.25 with about -28% max drawdown and 13% exposure. Springback does NOT beat buy-and-hold on Sharpe on this universe; its case is shallow drawdowns and low exposure.

## Phase 2b: does the earnings blackout earn its place? (RSI(3)<20, slow 200, fast 10, stop 3, time 10)
Measured only on bars from 2012-01-24 (where the platform has earnings data) with proxy report dates; entry-blackout and pre-exit use exact report dates, i.e. the OPTIMISTIC case (live, the platform gives no future dates).
| variant | tickers w/ Sharpe>0 | mean Sharpe | mean return | trades |
|---|---|---|---|---|
| no blackout | 24 | 0.259 | 47.5% | 2984 |
| after report only, A=1 day | 24 | 0.269 | 50.8% | 2900 |
| after report only, A=3 | 24 | 0.265 | 49.0% | 2860 |
| 3 days before | 24 | 0.239 | 37.9% | 2857 |
| 7 days before | 26 | 0.222 | 32.6% | 2729 |
| 7 before + 3 after | 25 | 0.230 | 35.1% | 2637 |
| pre-report exit only | 25 | 0.249 | 44.2% | 3025 |
| pre-exit + 7 before + 3 after | 24 | 0.234 | 34.5% | 2640 |

Finding: the blackout does not earn its place. Blocking entries or exiting before reports lowers mean Sharpe and return in every variant that needs future dates; the only variant that does not hurt is a 1-day post-report pause (+0.01 Sharpe, within noise) and that one needs no future dates but adds nothing measurable. Decision: drop the earnings logic and ship the pure technical version (fewer parameters, no dependence on a data feed the user's plan flags as unsupported). Plausible reason (not tested): in large-cap uptrends the days before a report are often drift-up days, so sitting them out costs as much as it saves.
