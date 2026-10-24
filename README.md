# Springback: Trend-Filtered Dip Signals

**#TSBuild26 | Track 1: Best Buy/Sell Signal Indicator | TrendSpider custom indicator (JavaScript)**

Springback buys short, sharp dips in stocks that are already in a long-term uptrend, and sells when price snaps back. It is long only, holds one position at a time, and its signals alternate BUY, SELL, BUY, SELL.

**Timeframe: DAILY (1D), regular trading hours.** It was designed and tested on daily bars only.

## The rules

| Signal | Condition (decided on a closed bar) |
|---|---|
| **BUY** | Close is above the 200-day EMA (uptrend) **and** RSI(3) is below 25 (a sharp short-term dip). |
| **SELL** | Close is at or above the 10-day EMA (the snapback), **or** close is below the 200-day EMA (the uptrend is lost). |

On the chart: green BUY label under the bar, red SELL label above it, grey line = 200-day EMA, blue line = 10-day EMA. Act at the next bar's open (that is the fill the Strategy Tester uses, and what was assumed in testing).

**Inputs:** Trend EMA (200), Snapback EMA (10), Dip RSI(3) below (25), Ignore unfinished last bar (on).
**Signals for the Strategy Tester, alerts and scanners:** `Springback BUY` and `Springback SELL` (use "Signal emerged").

**No repainting.** A signal uses only its own bar and older bars, so once it appears it never moves. With the default setting the newest, still-forming bar cannot signal, so a live signal appears once the next bar has begun.

## How to use it in TrendSpider

1. Open the **Custom Indicator Editor** and create a new indicator.
2. Delete the starter code, copy all of [`springback.js`](springback.js), paste it in, and click **Apply**, then **Save**.
3. Add it to a **Daily** chart of a US stock.
4. In the **Strategy Tester**, set the entry to *Springback BUY, Signal emerged* and the exit to *Springback SELL, Signal emerged*.

(It is also published in the TrendSpider Store as "Springback: Trend-Filtered Dip Signals".)

## What was measured, and its limits

Local Python model on the last 7,000 daily bars of the current 30 Dow stocks, next-open fills, 2 basis points of slippage per side, price-only data (yfinance), one unit per trade:

- Positive total return on **28 of 30** stocks (IBM and CVX lost money). 167 to 268 trades per stock, invested about 17% of the time.
- Average Sharpe **0.28**, average max drawdown about **-31%**.
- **It does not beat buy and hold on Sharpe**: buy and hold over the same bars averaged 0.47, with a much deeper average drawdown (about -69%). Springback's profile is shallower drawdowns while mostly in cash.
- **It is cost-sensitive**: the average trade is about 0.3%, so at 10 basis points per side the average Sharpe falls to about 0.14.
- The oldest third of the history was weaker (19 of 30 stocks positive vs 29 and 22 in the other thirds).
- 36 nearby parameter settings all landed between 0.22 and 0.285 Sharpe, so there is no sharp parameter peak.
- On TrendSpider's Strategy Tester (AAPL, Daily, 7,000 candles, 0% cost): 249 long trades, 72% winners, about +410% compounded, against about +97,964% for simply holding AAPL; the strategy's max drawdown was -40%. 243 of the harness's 246 AAPL trades matched the tester's trades exactly by date.

An earnings blackout (the original idea, hence the repo's early name) was tested and **did not help**, so it is not in the script. See [`RESULTS.md`](RESULTS.md) for every experiment, including the rejected designs.

These are past, backtested figures from specific data and settings, not a forecast.

## Repository guide

- `springback.js`: the indicator (this is what is published in the Store).
- `RESULTS.md`: methodology, results, rejected experiments, platform verification.
- `STORE_LISTING.md`, `SUBMISSION_CHECKLIST.md`: Store text and the hard-rule checklist with evidence.
- `harness/`: Python backtest (downloads price data itself; data is not stored in the repo). Needs `pandas numpy yfinance pyarrow`. Example: `python -m harness.simple`.
- `verify/`: Node check that `springback.js` reproduces the Python signals, a no-repaint replay test, and the Strategy Tester trade list for AAPL.
- `probe/`: throwaway scripts used to learn how the platform behaves (live bar, earnings data depth, fill timing).
- `docs-notes/VERIFIED_API.md`: the TrendSpider functions and restrictions that were verified before use.

## Disclaimer

Not investment advice. For education and research only. Trading involves risk of loss, and past performance does not guarantee future results.

## License

MIT, see [`LICENSE`](LICENSE).
