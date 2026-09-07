import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { COLORS, renderCalendar, validateCalendar } from './generate-contributions.mjs';

// A entrada é uma resposta REAL da API obtida nesta execução; não há fixtures fictícias.
const collection = JSON.parse(await readFile(process.argv[2], 'utf8'));
const calendar = collection.contributionCalendar;
const svg = await readFile(new URL('../assets/v3/contributions/contributions.svg', import.meta.url), 'utf8');
assert.equal(svg, renderCalendar(calendar), 'SVG precisa corresponder exatamente à resposta consultada');
const expected = calendar.weeks.flatMap(week => week.contributionDays);
const rects = [...svg.matchAll(/<rect data-date="([^"]+)" data-count="(\d+)" data-level="([^"]+)" data-weekday="(\d+)" x="([^"]+)" y="([^"]+)" width="([^"]+)" height="([^"]+)" rx="3" fill="([^"]+)"/g)];
assert.equal(rects.length, expected.length);
let index = 0;
for (const [column, week] of calendar.weeks.entries()) {
  for (const day of week.contributionDays) {
    const [, date, count, level, weekday, x, y, width, height, fill] = rects[index++];
    assert.equal(date, day.date);
    assert.equal(Number(count), day.contributionCount);
    assert.equal(level, day.contributionLevel);
    assert.equal(Number(weekday), day.weekday);
    assert.equal(Number(y), 302 + day.weekday * 25);
    assert.equal(Number(x), Number((177 + column * 1703 / calendar.weeks.length).toFixed(2)));
    assert.equal(fill, COLORS[day.contributionLevel]);
    assert.equal(width, height);
  }
}
assert.equal(Number(svg.match(/id="total" data-total="(\d+)"/)[1]), calendar.totalContributions);
assert.equal(expected.reduce((sum, day) => sum + day.contributionCount, 0), calendar.totalContributions);
for (const month of calendar.months) {
  assert.ok(svg.includes(`data-month="${month.firstDay}" data-year="${month.year}" data-total-weeks="${month.totalWeeks}"`));
}
for (let i = 1; i < expected.length; i++) {
  assert.equal(Date.parse(expected[i].date) - Date.parse(expected[i - 1].date), 86400000);
}
const yearTransitions = expected.filter((day, i) => i && day.date.slice(0,4) !== expected[i-1].date.slice(0,4));
for (const day of yearTransitions) assert.ok(day.date.endsWith('-01-01'));
// Nenhuma célula extra para preencher semanas incompletas; nenhuma referência sensível.
assert.ok(!/<(?:image|script|foreignObject)\b|https?:\/\/(?!www\.w3\.org\/2000\/svg)|gh[pousr]_/i.test(svg));
const badLevel = structuredClone(calendar);
badLevel.weeks[0].contributionDays[0].contributionLevel = 'NIVEL_DESCONHECIDO';
assert.throws(() => validateCalendar(badLevel));
const missingDay = structuredClone(calendar);
missingDay.weeks[1].contributionDays.splice(2, 1);
assert.throws(() => validateCalendar(missingDay));
const badTotal = structuredClone(calendar);
badTotal.totalContributions++;
assert.throws(() => validateCalendar(badTotal));
console.log(JSON.stringify({ status: 'validado', total: calendar.totalContributions,
  days: expected.length, weeks: calendar.weeks.length, months: calendar.months.length,
  yearTransitions: yearTransitions.map(day => day.date),
  incompleteWeeks: calendar.weeks.filter(week => week.contributionDays.length < 7).map(week => week.firstDay),
  samples: expected.filter(day => ['2025-12-31','2026-01-01','2026-08-04','2026-09-03','2026-09-06'].includes(day.date)) }));
