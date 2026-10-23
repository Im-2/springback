# Springback: Earnings-Safe Dip Signals

Build ONE TrendSpider custom indicator (JavaScript) for the #TSBuild26 Developer Hackathon, Track 1: **Best Buy/Sell Signal Indicator**. This is the only product. Do not build anything for other tracks.

Deadline: submissions are due **Oct 26, 2026** (page says Oct 26; a PDF says Oct 5 and is probably stale; the user is confirming). Plan to publish by Sunday Oct 25.

---

## 1. How it is judged (this decides every design choice)

- **Performance, 70%. Measured, not judged.** Every qualifying entry runs the same backtest and the field is ranked on **risk-adjusted return**.
- **Signal quality and usability, 30%.** Could a trader open the chart and act on it without asking what it means?

### Hard rules from the official judging sheet. Violating any one can disqualify the entry.

1. **Long only.** No short entries.
2. Signals must **alternate**: buy, sell, buy, sell. **No scaling in or out.**
3. Register exactly **one buy and one sell signal with `register_signal()`**, clearly named. They become Strategy Tester conditions.
4. **State the timeframe in the Store description.** We choose it; they test on it. No timeframe in the description means no test.
5. Tested over a **7,000-candle lookback, regular trading hours only**.
6. Tested on assets from the **Dow 30**. Tickers are not published in advance, so build for robustness, not for one chart.
7. **No repainting.** A signal must stay on the bar where it fired. Repainting entries are disqualified.
8. Must be published **free and public** to the TrendSpider Store with **#TSBuild26** in the description, then submitted through the official form. The script can enter only one category.

Because ranking is on risk-adjusted return across unknown Dow stocks, **robust and simple beats clever and fragile**. Few parameters, no curve-fitting.

---

## 2. Strategy concept

**Springback buys short-term dips only in stocks whose trend is intact, stays out around earnings, and exits when price snaps back.**

The edge thesis (to be tested, not assumed):
- Large-cap stocks in uptrends tend to mean-revert after short-term stretches.
- Earnings gaps are a large source of single-stock drawdowns, so avoiding them should improve the risk-adjusted score.

### Logic (all evaluated on CLOSED bars only)

State machine, one pass, enforcing strict alternation (flat -> long -> flat):

- **Trend filter (entry gate):** close above a slow EMA and that EMA rising versus N bars ago.
- **Dip trigger:** price stretched below a fast EMA by at least `k` ATRs, and/or a short-period RSI below a threshold. Pick one clean formulation after testing; do not stack many conditions.
- **Earnings blackout:** no new entries from `B` days before a report through `A` days after it. Use earnings timestamps from `request.earnings(constants.ticker)`.
- **Exits (first to trigger):**
  1. Snapback: close back at or above the fast EMA.
  2. Trend failure: close below the slow EMA.
  3. ATR stop from the entry price.
  4. Time stop after `T` bars.
  5. **Pre-earnings exit:** if an earnings date is approaching, exit on the last regular-session bar before it.
- Keep total tunable parameters to about 6 or fewer, all exposed as script inputs with sane defaults.

### Known facts about the platform (from public examples)
- `request.earnings(constants.ticker)` returns records with at least `timestamp` and `eps_surprise_percent`.
- Helpers seen in examples: `describe_indicator()`, `paint()`, `land_points_onto_series()`, `for_every()`, `time_of()`, `library()`, `function()`, `constants.ticker`, built-in arrays such as `close`, `time`.
- Do NOT assume anything else. Read the docs and verify every function name and signature before relying on it, including `register_signal()`.

---

## 3. No-repainting requirements

- Never place a signal on a pivot or fractal bar. Pivots need later bars to confirm, so the signal would move.
- The still-forming live bar must not create or remove signals. Find out from the docs how the live (last) bar is handled, and make the signal depend only on closed-bar values.
- Test it: replay or step through bars and confirm every historical signal is identical to the one produced when that bar was the last bar.
- Earnings blackout must use only information known at that bar's time (see the live-data risk in section 6).

---

## 4. Build and test plan

Work in this order. Do not polish visuals before the logic proves robust.

**Phase 0: Environment.** Read the TrendSpider scripting docs (see section 7 if blocked). List the exact functions you will use and confirm they exist.

**Phase 1: Local test harness.**
- Build a Python harness that mimics the official test: long only, alternating signals, 7,000 candles, regular hours only, on the current Dow 30. **Look up the current Dow 30 membership; do not rely on memory.**
- Include small slippage and fees. Do not assume fills at the signal price.
- Report per ticker and in aggregate: total return, Sharpe, Sortino, max drawdown, profit factor, win rate, number of trades, exposure time. The aggregate ranking metric is unknown, so optimize for good risk-adjusted behavior across all of them.
- If the user's machine cannot fetch market data, stop and use the blocker protocol.

**Phase 2: Choose timeframe and parameters honestly.**
- Test several timeframes (for example 1h, 4h-equivalent if available, daily) and pick the one that is robust, not the single best backtest.
- Robustness checks required before accepting a design:
  - Positive on a clear majority of the 30 tickers, not carried by a few.
  - Stable across sub-periods (split the 7,000 candles into thirds).
  - **Neighbor test:** nearby parameter values perform similarly. A sharp peak means overfit, so reject it.
  - Enough trades per ticker to mean something. Report counts.
  - Compare with and without the earnings blackout to prove it earns its place. If it does not help, say so and drop it.
- Do not claim future performance. Report what was measured and the limitations.

**Phase 3: Port to TrendSpider JavaScript.**
- Implement the final logic as the platform script with `register_signal()` for buy and sell.
- Confirm it runs as a Strategy Tester strategy and that results are close to the Python harness. Investigate any gaps.

**Phase 4: Usability (30% of score).**
- Clear BUY and SELL markers with unambiguous labels.
- Light visuals only: the trend filter state, the earnings blackout shading, optionally the fast EMA. Nothing decorative.
- A compact legend or description so a trader understands it in seconds.
- Script inputs with sensible defaults and short names.

**Phase 5: Package.**
- Final script file `springback.js`.
- Store listing text (see section 8).
- `RESULTS.md`: methodology, results table, robustness findings, honest limitations.
- A final checklist against the hard rules in section 1.

---

## 5. Deliverables

1. `springback.js`: the final indicator script, ready to paste into the TrendSpider editor.
2. Local harness code plus `RESULTS.md`.
3. `STORE_LISTING.md`: title, description, timeframe statement, #TSBuild26.
4. `SUBMISSION_CHECKLIST.md`: every hard rule, ticked with evidence.

Store title: **Springback: Earnings-Safe Dip Signals**

---

## 6. Risks to handle explicitly

- **Earnings data depth:** if `request.earnings` history is too shallow, or does not give usable report dates, say so. Fallback: drop the earnings logic and ship a purely technical regime-aware pullback (efficiency ratio decides trend or range), and tell the user before doing it.
- **Live vs historical blackout:** the backtest can use past report dates, but live use needs the next report date. If the data does not provide upcoming dates, state this limitation in the Store description rather than hide it.
- **Report time of day (before open vs after close):** if the timestamp does not tell you, use a conservative window that covers both.
- **Overfitting:** the most likely way to lose. Prefer the simpler variant when results are close.

---

## 7. BLOCKER PROTOCOL (important)

Several things may be outside your reach: the scripting docs site may block automated access (robots rules), the TrendSpider editor requires the user's login, market data may not be downloadable from your environment, and you cannot run the platform's own Strategy Tester.

**Do not work around a site that disallows automated access** (no scraping, mirrors, or caches). Do not guess function names from memory and press on.

When you hit any blocker:
1. **Stop that specific task** and keep working on everything that is not blocked.
2. Write a clearly marked block in your reply:

```
NEEDS FROM USER
- What I'm blocked on: <one line>
- What I need: <exact thing, e.g. "the API reference section on request.* and register_signal()">
- Exactly how to get it: <step-by-step, e.g. "open charts.trendspider.com/scripting/docs, click X, copy the text, paste it into a file named docs-api.md in the project folder">
- Or send me: <the screenshot I need, and of which screen>
- Why I can't continue without it: <one line>
```

3. Assume the user is not a quant and is working from a phone or laptop; use plain steps, one thing per request, and make each request as small as possible.
4. The user may bring screenshots to a separate helper to get guidance, so make each request specific enough to be explained in a screenshot.
5. Ask for the most likely helpful item first. Typical requests to expect:
   - Pasted docs text, or screenshots of the docs pages for `register_signal()`, the `request.*` functions and the plotting API.
   - A screenshot of the Strategy Tester results panel after the user pastes the script and runs it on a Dow stock.
   - A screenshot of any error message in the TrendSpider script editor console.
   - Confirmation of the timeframe options and chart settings (regular hours only).
   - Exported market data files (CSV) if you cannot download data yourself.

---

## 8. Store listing requirements

Write the description so that it:
- States the **timeframe** clearly (required for testing).
- Includes **#TSBuild26**.
- Explains in plain language what the signals mean and how to act on them.
- Lists the inputs and defaults.
- States long-only, alternating, closed-bar, non-repainting behavior.
- Notes the earnings-data limitation honestly if one exists.
- Includes a standard "not investment advice" line.
- Makes no performance promises. Quote only measured figures, labeled with what was tested.

Documentation quality is part of how entries are scored, so keep it tidy.

---

## 9. Working style

- Start by confirming you understand the hard rules, then go to Phase 0.
- Report at the end of each phase in two or three sentences plus any NEEDS FROM USER block.
- If a design choice is close, choose the simpler one and say so.
- Tell the user early if something makes the plan unworkable. Do not quietly change the scope.
