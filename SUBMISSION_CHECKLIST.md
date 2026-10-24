# Submission checklist (hard rules from the judging sheet)

Legend: [x] done with evidence, [~] done but only partly evidenced, [ ] still to do by the user.

| # | Rule | Status | Evidence |
|---|---|---|---|
| 1 | Long only | [x] | The script has no short logic (springback.js, one state machine flat <-> long). Strategy Tester AAPL run: 249 trades, all "long" (verify/tester-AAPL.csv). |
| 2 | Signals alternate; no scaling in/out | [x] | One state machine emits BUY only when flat and SELL only when long. Replay test (verify/replay_norepaint.py) and Node-vs-Python comparison (verify/dump_and_compare.py) show identical BUY/SELL bars. Tester: no overlapping trades, every entry at least 1 bar after the previous exit; one fixed-size position, no adds. |
| 3 | Exactly one buy and one sell via `register_signal()`, clearly named | [x] | springback.js registers `register_signal(buySignal, 'Springback BUY')` and `register_signal(sellSignal, 'Springback SELL')`, static names, called unconditionally. Both appear in the Strategy Tester as "Springback BUY/SELL" (screenshot of the tester). |
| 4 | Timeframe stated in the Store description | [~] | STORE_LISTING.md states "TIMEFRAME: Daily (1D), regular trading hours" at the top of the description. The user must paste it in the Store form (see "To do"). |
| 5 | Tested over 7,000 candles, regular trading hours only | [~] | Strategy Tester ran 7,000 candles (27.8 years of AAPL daily). Daily bars are regular-session by construction; the harness uses 7,000 daily bars per stock. Not independently confirmed whether the tester's regular-hours-only setting was on. |
| 6 | Assets from the Dow 30; tickers not published | [~] | Harness: all 30 current Dow stocks (28/30 positive, RESULTS.md). Platform: only AAPL run so far. No ticker-specific logic or tuning to a ticker; neighbor test shows a flat parameter landscape. |
| 7 | No repainting | [~] | Signals use only the current and older closed bars (springback.js loop). The still-forming last bar is excluded by default ("Ignore unfinished last bar", on). Replay test: 90 cut points over 3 tickers, signals on earlier bars identical and the last bar never signals (stubbed, in Node). NOT yet confirmed on a live chart during market hours (planned Monday check). |
| 8 | Published free and public with #TSBuild26, then submitted via the official form; one category only | [ ] | To do by the user: publish to the TrendSpider Store (free, public), paste STORE_LISTING.md (contains #TSBuild26), submit the official form for Track 1 only. |

## Other things the brief asked for
- [x] No `new`, classes, imports or requires in springback.js (the editor rejects `new`; script loads without errors on the user's account).
- [x] Earnings logic removed (tested and rejected, RESULTS.md Phase 2b), so no dependency on earnings data or plan.
- [x] No performance promises; measured figures are labeled with what was tested, with limitations (STORE_LISTING.md).
- [x] Inputs have short names and defaults (Trend EMA 200, Snapback EMA 10, Dip RSI(3) below 25, Ignore unfinished last bar on).
- [ ] Deadline: the page says Oct 26, an older PDF said Oct 5. Confirm which applies.

## To do (user)
1. Monday (market open): live-bar check, to confirm no signal flickers on the forming bar.
2. Optionally run the Strategy Tester on 2 or 3 more Dow stocks and send the summary screenshots.
3. Publish to the Store (free, public), paste the description from STORE_LISTING.md, submit the form.
