# Verified TrendSpider API (Phase 0)

Source: https://platform-docs.trendspider.com/scripting/docs/ (read in a normal browser pane; the host has no robots.txt
and the main site's robots.txt does not restrict docs). Pages read: signals, strategies, additional_series, limitations,
common_mistakes, best_practices, scripting_language, writing_ang_debugging, api.

## Functions confirmed to exist (signatures from the API reference)
- `describe_indicator(name, [type], metainfo)`; `input.number(title, default, {min,max})`; `input.select`, `input.boolean` (used in docs examples)
- `ema(series, length)`, `sma`, `atr(length)` and `atr(high, low, close, length)`, `rsi(input, length)`, `highest`, `lowest`
- `add/sub/mult/div`, `for_every`, `series_of(value)`, `shift(series, offset)`, `max_of/min_of`
- `register_signal(signal, name)`: series of truthy/falsy per candle; name must be a STATIC string; call must run on every execution
- `paint(series, {name, color, style, ...})`; styles include `labels_above`, `labels_below`; `fill`, `color_cloud`, `color_candles`
- `await request.earnings(ticker, {filters})` returns up to 300 records:
  `{timestamp, isFuture, when ('postmarket' etc.), change, eps, eps_est, eps_surprise_percent, period, period_year, ...}`
- `land_points_onto_series(srcTimes, srcValues, targetTimes, method)`, `interpolate_sparse_series(series, 'constant')` (only 'constant' is backtest-safe)
- Globals: `open high low close volume time`, `current.ticker`, `current.resolution`, `current.session`

## Facts that shape the design
1. The script runs ONCE over all candles and is recomputed on each real-time update. A plain loop over candles is the documented strategy pattern (see `strategies` page, which uses `register_signal` for Entry and Exit and says the Strategy Tester skips conflicting repeated signals itself).
2. Signals/paints must be registered unconditionally with fixed names, or the platform ignores them after save.
3. `request.earnings` without a timestamp filter trims future events beyond "3 days after now". Upcoming dates are therefore only partly visible live; pass a timestamp filter to see further ahead.
4. Earnings records carry `when` (e.g. postmarket) so before-open/after-close can be handled.
5. Docs examples use both `constants.ticker` and `current.ticker`; `current.ticker` is the documented constant. Verify in the editor.
6. Limits: 6 non-history `request.*` calls per script, 70 output series.

## Still unverified (cannot be settled from the docs)
- How the still-forming last bar is exposed to the script (is `close[last]` the live price?). Needs a test in the editor.
- Whether `request.earnings` returns deep enough history when the script runs inside the Strategy Tester.
- Whether the Strategy Tester fills on the signal bar close or next bar open.

## Confirmed platform restrictions (found by running scripts in the editor)
- `new` is NOT allowed in scripts ("Using \"new\" in scripts is not currently allowed"). So no `new Date(...)`, `new Map`, `new Set`, `new Array`. Use arithmetic on Unix-second timestamps, plain objects/arrays and `series_of()`. Strategy code must stay free of `new`.
- Other restrictions: none found yet (this list is extended whenever the editor rejects something).

## Probe step 1 results (user's account, AAPL daily, run 2026-10-23, US market closed)
- `request.earnings(current.ticker)` WORKS inside a script even though the chart's own Earnings line says the plan does not support it. Status ok, 59 records, oldest 2012-01-24, newest 2026-07-30, 0 future-flagged records.
- Earnings history starts 2012, so a 7,000-bar daily window (back to ~1998) is only covered from 2012 on. The harness must apply the blackout only from 2012-01-24 and treat earlier years as "no earnings data".
- No upcoming report date came back with the default request. Whether a `timestamp` filter exposes future dates is still to be tested.
- The script saw bars 2025-07-18 .. 2026-10-23 on the chart as loaded (the visible chart range; candle count not captured), last/prev close matched the chart.
- `current.now` produced NaN in `(current.now - time[last]) / 3600`: do not depend on `current.now`.
- Live (forming-bar) behavior: untested until a market day. Design rule: never depend on it; decide signals from closed bars only.
