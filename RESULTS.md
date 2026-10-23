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

## Phase 2c: ablations, simplification, final design
Ablating the design on the 30 tickers (next-open fills, 2 bps/side) showed the extras do not pay for themselves:
- ATR stop (3 ATR): mean Sharpe 0.248 with it, 0.272 without it (on the earlier version). REJECTED: it cuts winners that recover.
- Slow-EMA slope filter (EMA rising vs 20 bars ago): 0.248 vs 0.252 without it. REJECTED (the brief suggested it; the data says it adds nothing).
- Time stop (10 bars): 0.276 with and without it. REJECTED as dead weight.
- Earnings blackout / pre-earnings exit: see Phase 2b. REJECTED.
- ATR-distance dip trigger: REJECTED in favour of RSI(3) (see Phase 2a).

**Final design (3 inputs): BUY when close > 200-EMA and RSI(3) < 25; SELL when close >= 10-EMA or close < 200-EMA.** Daily bars, signal on the close, fill at the next open.

Measured on the last 7,000 daily bars of each current Dow 30 stock, 2 bps/side slippage, no commission, one unit per trade, not compounded across tickers:
| case | tickers return>0 | mean Sharpe | mean return | mean max DD | trades (min / median per ticker) | exposure |
|---|---|---|---|---|---|---|
| FINAL | 28/30 | 0.276 | 150% | -31% | 167 / 213 | 17% |
| oldest third of window | 19/30 | 0.185 | 21% | -25% | 43 / 63 | 15% |
| middle third | 29/30 | 0.415 | 42% | -18% | 61 / 81 | 19% |
| newest third | 22/30 | 0.229 | 38% | -24% | 42 / 76 | 18% |
| close-fill (not achievable live) | 27/30 | 0.260 | 125% | -32% | 167 / 213 | 17% |
| cost 0 | 28/30 | 0.309 | 173% | -30% | | |
| cost 5 bps/side | 26/30 | 0.227 | 119% | -33% | | |
| cost 10 bps/side | 21/30 | 0.144 | 75% | -37% | | |
| buy and hold (same window) | 30/30 | 0.472 | n/m | -69% | | 100% |

Neighbor test (36 settings: RSI level 15/20/25/30 x slow EMA 150/200/250 x fast EMA 8/10/12): mean Sharpe ranges 0.220-0.285 (std 0.014), the chosen setting sits at 0.276; no sharp peak. By RSI level: 15 -> 0.258, 20 -> 0.255, 25 -> 0.267, 30 -> 0.241.

Honest reading:
- Positive on 28 of 30 stocks and in all three sub-periods on average, but the OLDEST third is weaker (20/30 positive) and the edge is NOT uniform: IBM and DIS lose.
- It does not beat buy and hold on Sharpe (0.28 vs 0.47). What it offers is a much shallower drawdown (-31% vs -69% mean) with 17% of the time invested. The platform's ranking metric is unknown, so I cannot say how it ranks against other entries.
- It is cost-sensitive: average trade is ~0.3%, so at 10 bps per side the mean Sharpe falls to 0.14. The platform's Strategy Tester showed 0% cost by default.
- Sharpe here uses daily returns including flat days, one unit per trade, no position sizing.
- Data: yfinance, price-only; the platform's data (adjustments, session) will differ slightly. Not a forecast of future results.

Per-ticker results (final design):
| ticker | return | Sharpe | Sortino | max DD | profit factor | win % | trades | exposure |
|---|---|---|---|---|---|---|---|---|
| MMM | 57% | 0.25 | 0.13 | -25% | 1.35 | 67% | 204 | 17% |
| GOOGL | 169% | 0.43 | 0.27 | -31% | 1.49 | 68% | 213 | 22% |
| AXP | 52% | 0.20 | 0.11 | -34% | 1.23 | 67% | 230 | 18% |
| AMGN | 35% | 0.15 | 0.09 | -48% | 1.18 | 60% | 215 | 17% |
| AMZN | 364% | 0.41 | 0.28 | -28% | 1.59 | 68% | 232 | 19% |
| AAPL | 335% | 0.42 | 0.28 | -41% | 1.63 | 72% | 246 | 21% |
| BA | 58% | 0.21 | 0.11 | -38% | 1.25 | 65% | 212 | 16% |
| CAT | 125% | 0.32 | 0.19 | -27% | 1.39 | 66% | 209 | 16% |
| CVX | -10% | -0.00 | -0.00 | -47% | 1.00 | 63% | 194 | 15% |
| CSCO | 106% | 0.30 | 0.18 | -25% | 1.49 | 64% | 191 | 15% |
| KO | 7% | 0.07 | 0.04 | -23% | 1.07 | 61% | 222 | 16% |
| DIS | 12% | 0.09 | 0.05 | -32% | 1.10 | 70% | 197 | 16% |
| GS | 53% | 0.20 | 0.10 | -40% | 1.24 | 68% | 209 | 17% |
| HD | 27% | 0.14 | 0.09 | -37% | 1.16 | 63% | 215 | 18% |
| HON | 43% | 0.20 | 0.11 | -29% | 1.21 | 65% | 235 | 17% |
| IBM | -45% | -0.25 | -0.12 | -45% | 0.74 | 58% | 177 | 14% |
| JNJ | 89% | 0.39 | 0.23 | -18% | 1.53 | 66% | 226 | 18% |
| JPM | 57% | 0.22 | 0.12 | -23% | 1.28 | 67% | 202 | 16% |
| MCD | 117% | 0.41 | 0.26 | -20% | 1.51 | 68% | 235 | 17% |
| MRK | 67% | 0.26 | 0.15 | -30% | 1.35 | 63% | 187 | 16% |
| MSFT | 158% | 0.40 | 0.22 | -26% | 1.59 | 67% | 213 | 16% |
| NKE | 46% | 0.18 | 0.09 | -35% | 1.23 | 70% | 202 | 16% |
| NVDA | 1301% | 0.52 | 0.37 | -65% | 1.82 | 71% | 233 | 20% |
| PG | 43% | 0.23 | 0.11 | -18% | 1.28 | 67% | 233 | 16% |
| CRM | 45% | 0.19 | 0.10 | -37% | 1.23 | 63% | 167 | 19% |
| SHW | 214% | 0.50 | 0.34 | -29% | 1.69 | 72% | 226 | 19% |
| TRV | 134% | 0.39 | 0.23 | -17% | 1.51 | 64% | 236 | 19% |
| UNH | 597% | 0.67 | 0.44 | -19% | 1.96 | 70% | 268 | 20% |
| V | 218% | 0.63 | 0.35 | -24% | 2.02 | 77% | 178 | 20% |
| WMT | 27% | 0.15 | 0.08 | -24% | 1.19 | 66% | 198 | 16% |

## Phase 3: port to TrendSpider JavaScript (in progress)
- springback.js written with its own EMA and RSI loops (so the maths equals the harness and does not depend on how built-ins seed their averages). No `new`, classes or imports.
- Verified in Node with stubbed TrendSpider globals: the script's BUY/SELL bars are identical to the Python engine on AAPL, JPM, KO, NVDA, IBM, V (verify/dump_and_compare.py).
- Replay no-repaint test (verify/replay_norepaint.py): for 90 cut points over 3 tickers the signals produced when bar k was the last bar equal the full-history signals on all earlier bars, and the last bar never carries a signal. This is a stub-based test; it does not replace the check on the real platform.
- NOT yet verified on the platform: that the editor accepts the script, and that the Strategy Tester trades match the harness.
