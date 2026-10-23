// Runs springback.js with minimal stand-ins for the TrendSpider globals (series_of, input, paint...).
const fs = require('fs');
const bars = JSON.parse(fs.readFileSync(0, 'utf8'));
const n = bars.close.length;
const seriesOf = value => new Array(n).fill(value);
const registered = {};
const globals = {
	open: bars.open, high: bars.high, low: bars.low, close: bars.close, time: bars.time,
	series_of: seriesOf,
	describe_indicator: () => {},
	input: { number: (title, def) => def, boolean: (title, def) => def },
	register_signal: (series, name) => { registered[name] = series; },
	paint: () => {}, paint_overlay: () => {},
};
const source = fs.readFileSync(__dirname + '/../springback.js', 'utf8');
const names = Object.keys(globals);
new Function(...names, source)(...names.map(k => globals[k]));
const pick = series => series.map((v, i) => (v ? i : -1)).filter(i => i >= 0);
console.log(JSON.stringify({ buy: pick(registered['Springback BUY']), sell: pick(registered['Springback SELL']) }));
