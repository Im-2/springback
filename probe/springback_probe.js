// Springback PROBE (throwaway). Answers 3 platform questions. Not the final indicator.
// 1) What does the script see on the live last bar?
// 2) How deep is request.earnings history?
// 3) Does a Strategy Tester fill happen at the signal bar's close or the next bar's open?

describe_indicator('Springback Probe');

const lastIndex = close.length - 1;
// Unix seconds -> 'YYYY-MM-DD' (UTC) using arithmetic only: "new" and Date objects are not allowed.
const pad2 = value => (value < 10 ? '0' : '') + value;
const toDate = ts => {
	const days = Math.floor(ts / 86400) + 719468;
	const era = Math.floor(days / 146097);
	const dayOfEra = days - era * 146097;
	const yearOfEra = Math.floor((dayOfEra - Math.floor(dayOfEra / 1460) + Math.floor(dayOfEra / 36524) - Math.floor(dayOfEra / 146096)) / 365);
	const dayOfYear = dayOfEra - (365 * yearOfEra + Math.floor(yearOfEra / 4) - Math.floor(yearOfEra / 100));
	const monthIndex = Math.floor((5 * dayOfYear + 2) / 153);
	const day = dayOfYear - Math.floor((153 * monthIndex + 2) / 5) + 1;
	const month = monthIndex < 10 ? monthIndex + 3 : monthIndex - 9;
	const year = yearOfEra + era * 400 + (month <= 2 ? 1 : 0);
	return year + '-' + pad2(month) + '-' + pad2(day);
};

// ---- Earnings depth ----
let earningsData = null;
let earningsStatus = 'ok';
try {
	earningsData = await request.earnings(current.ticker);
} catch (caught) {
	earningsStatus = 'THREW: ' + String(caught && caught.message ? caught.message : caught);
}
if (earningsData && earningsData.error) {
	earningsStatus = 'RETURNED ERROR: ' + String(earningsData.error);
} else if (earningsStatus === 'ok' && !Array.isArray(earningsData)) {
	earningsStatus = 'NOT AN ARRAY: ' + typeof earningsData;
} else if (earningsStatus === 'ok' && earningsData.length === 0) {
	earningsStatus = 'EMPTY ARRAY';
}
const earningsList = (Array.isArray(earningsData) ? earningsData : []).slice().sort((a, b) => a.timestamp - b.timestamp);
const earningsTimes = earningsList.map(record => record.timestamp);
const earningsWhen = earningsList.map(record => record.when || '?');
const oldestEarnings = earningsTimes.length ? earningsTimes.reduce((a, b) => (a < b ? a : b)) : null;
const newestEarnings = earningsTimes.length ? earningsTimes.reduce((a, b) => (a > b ? a : b)) : null;
const futureCount = earningsList.filter(record => record.isFuture).length;

// Mark earnings on candles (signal for the Strategy Tester + labels on the chart)
const earningsLanded = earningsTimes.length
	? land_points_onto_series(earningsTimes, earningsWhen, time, 'le')
	: series_of(null);
const earningsMarker = for_every(earningsLanded, value => value ? 1 : null);
const earningsLabels = for_every(earningsLanded, value => value ? 'E:' + value : null);

// ---- Fill timing test: buy every 10th bar, sell 5 bars later ----
const buySignal = series_of(null);
const sellSignal = series_of(null);
const buyLabels = series_of(null);
const sellLabels = series_of(null);
for (let index = 0; index < lastIndex; index += 1) {
	const nextOpen = open[index + 1];
	const text = `C ${close[index].toFixed(2)} | nextO ${nextOpen.toFixed(2)}`;
	if (index % 10 === 0) {
		buySignal[index] = true;
		buyLabels[index] = 'BUY ' + text;
	}
	if (index % 10 === 5) {
		sellSignal[index] = true;
		sellLabels[index] = 'SELL ' + text;
	}
}

register_signal(buySignal, 'Probe Buy');
register_signal(sellSignal, 'Probe Sell');
register_signal(earningsMarker, 'Probe Earnings Bar');

paint(buyLabels, { name: 'Probe Buy Labels', color: 'blue', backgroundColor: 'blue', style: 'labels_below' });
paint(sellLabels, { name: 'Probe Sell Labels', color: '#8c29a8', backgroundColor: '#8c29a8', style: 'labels_above' });
paint(earningsLabels, { name: 'Probe Earnings Labels', color: 'orange', backgroundColor: 'orange', style: 'labels_above' });

// ---- Live-bar readout ----
const ageHours = ((current.now - time[lastIndex]) / 3600).toFixed(1);
const rows = [
	['Ticker / resolution', `${current.ticker} / ${current.resolution}`],
	['Candles', String(close.length)],
	['First bar', toDate(time[0])],
	['Last bar', toDate(time[lastIndex])],
	['Last bar age (hours since its open)', ageHours],
	['Last close seen by script', close[lastIndex].toFixed(2)],
	['Prev close seen by script', close[lastIndex - 1].toFixed(2)],
	['Last bar high / low', `${high[lastIndex].toFixed(2)} / ${low[lastIndex].toFixed(2)}`],
	['Earnings records', String(earningsList.length)],
	['Oldest earnings', oldestEarnings ? toDate(oldestEarnings) : 'none'],
	['Newest earnings', newestEarnings ? toDate(newestEarnings) : 'none'],
	['Future-flagged records', String(futureCount)],
	['EARNINGS STATUS', earningsStatus]
].map(([label, value]) => ({ cells: [{ text: label, color: 'var(--text-color)', padding: 3 }, { text: value, color: 'var(--text-color)', padding: 3 }] }));

paint_overlay('Springback Probe', { position: 'top_right' }, { rows });
