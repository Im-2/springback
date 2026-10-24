# Store listing: Springback: Trend-Filtered Dip Signals

**Title:** Springback: Trend-Filtered Dip Signals

**Timeframe: DAILY (1D) chart, regular trading hours.** Use it on the Daily timeframe. It is designed and tested there only.

**#TSBuild26**

## Short description (paste into the Store description box)

```
Springback: Trend-Filtered Dip Signals  #TSBuild26
TIMEFRAME: Daily (1D), regular trading hours.

Springback buys short dips in stocks that are already in a long-term uptrend, and sells when price snaps back. Long only, one position at a time, signals alternate BUY, SELL, BUY, SELL. No scaling in or out.

HOW TO READ IT
- BUY (green label under the bar): the close is above the 200-day EMA (uptrend) AND the 3-day RSI is below 25 (a sharp short-term dip). Act at the next open.
- SELL (red label above the bar): the close is back at or above the 10-day EMA (the snapback), OR the close has dropped below the 200-day EMA (the uptrend is lost). Act at the next open.
- Grey line = 200-day trend EMA. Blue line = 10-day snapback EMA. The small legend shows whether the trend is UP or DOWN. No buys are generated while the trend is down.

INPUTS (defaults)
- Trend EMA: 200
- Snapback EMA: 10
- Dip RSI(3) below: 25
- Ignore unfinished last bar: on

SIGNALS FOR THE STRATEGY TESTER / ALERTS / SCANNER
- "Springback BUY" and "Springback SELL" (use "Signal emerged").

NO REPAINTING
Every signal is decided on a closed bar using only that bar and older bars, so a signal never moves or disappears once it appears. With the default setting the newest, still-forming bar is never allowed to signal, so a live signal shows up once the next bar has begun. Turn the last input off only if you accept that the newest bar's signal can change until it closes.

WHAT WAS MEASURED (and what it is not)
Tested in a local Python model on the last 7,000 daily bars of the current 30 Dow stocks, assuming the next bar's open for fills and 2 basis points of slippage per side:
- Positive total return on 28 of 30 stocks. IBM and DIS lost money.
- 167 to 279 trades per stock (median about 213), invested about 17% of the time.
- Average Sharpe 0.28 and average maximum drawdown about -31%. Plain buy and hold over the same bars had a higher average Sharpe (0.47) and a much deeper average drawdown (about -69%). Springback does NOT beat buy and hold on Sharpe; its profile is shallower drawdowns while mostly in cash.
- The older third of the history was weaker than the other two (20 of 30 stocks positive vs 29 and 22).
- It is cost-sensitive: average trade is only about 0.3%, and at 10 basis points per side average Sharpe falls to about 0.14.
- On TrendSpider's Strategy Tester, AAPL daily, 7,000 candles, 0% cost: 249 long trades, 72% winners, compounded about +410% for the strategy against about +97,964% for holding AAPL, with a -40% maximum drawdown for the strategy.
These are past, backtested figures from specific data and settings. They are not a forecast.

LIMITATIONS
- Daily timeframe only. Not tuned or tested on other timeframes.
- Does not use earnings data. An earnings blackout was tested during development and did not improve results, so it was left out. A signal can fire before an earnings report.
- Signals can cluster in sharp market sell-offs; the trend filter turns buys off only after the close falls under the 200-day EMA.
- The next-open fill is an assumption; real fills can differ.

Not investment advice. Past performance does not guarantee future results. For education and research only.
```

## Notes for the submitter (not part of the Store text)
- The numbers above come from RESULTS.md; update both together if anything changes.
- The official submission form is separate from publishing; see SUBMISSION_CHECKLIST.md.
