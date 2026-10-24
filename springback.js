// Springback: Trend-Filtered Dip Signals  (#TSBuild26, Track 1)
// Built for the DAILY timeframe, regular trading hours. Long only. Alternating BUY / SELL.
//
// BUY  : the stock is in a long-term uptrend (close above the slow EMA) and has just dipped
//        (RSI(3) below the dip level). Decided on the bar's close.
// SELL : price has snapped back to the fast EMA, or the uptrend has failed (close below the slow EMA).
// A signal only ever looks at that bar and older bars, so it never moves after it appears.
// Fill assumption used in testing: the open of the bar after the signal.

describe_indicator('Springback: Trend-Filtered Dip Signals');

const slowLength = input.number('Trend EMA', 200, { min: 20, max: 400 });
const fastLength = input.number('Snapback EMA', 10, { min: 3, max: 100 });
const dipLevel = input.number('Dip RSI(3) below', 25, { min: 5, max: 50 });
const waitForClose = input.boolean('Ignore unfinished last bar', true);

const RSI_LENGTH = 3;
const barCount = close.length;
const lastIndex = barCount - 1;

// Exponential average, seeded with the first value. Same maths as the research harness.
function emaOf(values, length) {
	const result = series_of(null);
	const alpha = 2 / (length + 1);
	let previous = values[0];
	result[0] = previous;
	for (let index = 1; index < barCount; index += 1) {
		previous = previous + alpha * (values[index] - previous);
		result[index] = previous;
	}
	return result;
}

// Wilder RSI, seeded with the first change.
function rsiOf(values, length) {
	const result = series_of(null);
	const alpha = 1 / length;
	let averageGain = 0;
	let averageLoss = 0;
	for (let index = 1; index < barCount; index += 1) {
		const change = values[index] - values[index - 1];
		const gain = change > 0 ? change : 0;
		const loss = change < 0 ? -change : 0;
		if (index === 1) {
			averageGain = gain;
			averageLoss = loss;
		} else {
			averageGain = averageGain + alpha * (gain - averageGain);
			averageLoss = averageLoss + alpha * (loss - averageLoss);
		}
		result[index] = averageLoss === 0 ? (averageGain === 0 ? 50 : 100) : 100 - 100 / (1 + averageGain / averageLoss);
	}
	return result;
}

const slowEma = emaOf(close, slowLength);
const fastEma = emaOf(close, fastLength);
const shortRsi = rsiOf(close, RSI_LENGTH);

const buySignal = series_of(null);
const sellSignal = series_of(null);
const buyLabels = series_of(null);
const sellLabels = series_of(null);

// The newest bar may still be forming; its close can change, so it is not allowed to signal.
const lastDecisionIndex = waitForClose ? lastIndex - 1 : lastIndex;

let isLong = false;
for (let index = slowLength; index <= lastDecisionIndex; index += 1) {
	if (isLong) {
		const snappedBack = close[index] >= fastEma[index];
		const trendFailed = close[index] < slowEma[index];
		if (snappedBack || trendFailed) {
			isLong = false;
			sellSignal[index] = true;
			sellLabels[index] = 'SELL';
		}
	} else {
		const inUptrend = close[index] > slowEma[index];
		const dipped = shortRsi[index] < dipLevel;
		if (inUptrend && dipped) {
			isLong = true;
			buySignal[index] = true;
			buyLabels[index] = 'BUY';
		}
	}
}

register_signal(buySignal, 'Springback BUY');
register_signal(sellSignal, 'Springback SELL');

paint(slowEma, { name: 'Trend EMA', color: '#8c8c8c', thickness: 2 });
paint(fastEma, { name: 'Snapback EMA', color: '#2e86de', thickness: 1 });
paint(buyLabels, { name: 'BUY', color: '#1e9e4a', backgroundColor: '#1e9e4a', style: 'labels_below' });
paint(sellLabels, { name: 'SELL', color: '#d63031', backgroundColor: '#d63031', style: 'labels_above' });

const trendNow = close[lastIndex] > slowEma[lastIndex];
// Tiny two-line legend: short lines, parked left of the top-right chart icons so nothing is cut off.
paint_overlay('Springback legend', { position: 'top_right', offset_y: 40, offset_x: -60 }, {
	rows: [
		{ cells: [{ text: 'Dip BUY / snap SELL', color: 'var(--text-color)', fontSize: '11px', padding: 2, whiteSpace: 'nowrap' }] },
		{ cells: [{ text: trendNow ? 'Trend UP' : 'Trend DOWN', color: trendNow ? '#1e9e4a' : '#d63031', fontSize: '11px', padding: 2, whiteSpace: 'nowrap' }] }
	]
});
