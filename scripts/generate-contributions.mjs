import { execFileSync } from 'node:child_process';
import { mkdir, writeFile, rename } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

export const LOGIN = 'pedro-art2611';
export const COLORS = Object.freeze({
  NONE: '#071b29', FIRST_QUARTILE: '#063c65', SECOND_QUARTILE: '#087cba',
  THIRD_QUARTILE: '#00c7e6', FOURTH_QUARTILE: '#9cf7ff',
});
export const QUERY = `query CalendarioDoPerfil($login: String!) {
  viewer { login }
  user(login: $login) {
    contributionsCollection {
      startedAt endedAt hasAnyRestrictedContributions restrictedContributionsCount
      contributionCalendar {
        totalContributions
        months { firstDay name totalWeeks year }
        weeks { firstDay contributionDays { date weekday contributionCount contributionLevel } }
      }
    }
  }
}`;

const DAY = 86400000;
const xml = value => String(value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&apos;'}[c]));
const dateValue = value => {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(value) || new Date(value).toISOString().slice(0, 10) !== value)
    throw new Error('Data inválida no calendário.');
  return Date.parse(`${value}T00:00:00Z`);
};

export function validateCalendar(calendar) {
  if (!Number.isInteger(calendar?.totalContributions) || calendar.totalContributions < 0 ||
      !Array.isArray(calendar.weeks) || !calendar.weeks.length || calendar.weeks.length > 54 ||
      !Array.isArray(calendar.months) || !calendar.months.length)
    throw new Error('Calendário ausente ou inválido; o SVG anterior será preservado.');
  const dates = new Set();
  let previousDate, previousSunday, sum = 0;
  for (const week of calendar.weeks) {
    if (!week.contributionDays?.length || week.contributionDays.length > 7) throw new Error('Semana inválida.');
    const first = week.contributionDays[0];
    const sunday = dateValue(first.date) - first.weekday * DAY;
    if (previousSunday !== undefined && sunday !== previousSunday + 7 * DAY) throw new Error('Semanas fora de sequência.');
    if (dateValue(week.firstDay) !== sunday && week.firstDay !== first.date) throw new Error('Início de semana inconsistente.');
    for (const day of week.contributionDays) {
      const timestamp = dateValue(day.date);
      if (dates.has(day.date) || (previousDate !== undefined && timestamp !== previousDate + DAY) ||
          !Number.isInteger(day.weekday) || day.weekday < 0 || day.weekday > 6 ||
          new Date(timestamp).getUTCDay() !== day.weekday || timestamp !== sunday + day.weekday * DAY ||
          !Number.isInteger(day.contributionCount) || day.contributionCount < 0 || !Object.hasOwn(COLORS, day.contributionLevel))
        throw new Error('Dia, posição ou nível inconsistente no calendário.');
      dates.add(day.date); previousDate = timestamp; sum += day.contributionCount;
    }
    previousSunday = sunday;
  }
  if (sum !== calendar.totalContributions) throw new Error('Total da API difere da soma dos dias; publicação interrompida.');
  let previousMonth;
  for (const month of calendar.months) {
    const key = month.firstDay.slice(0, 7);
    dateValue(month.firstDay);
    if (!month.name || Number(key.slice(0, 4)) !== month.year || !Number.isInteger(month.totalWeeks) ||
        month.totalWeeks < 0 || (previousMonth && key <= previousMonth)) throw new Error('Mês inválido.');
    if (![...dates].some(date => date.startsWith(key))) throw new Error('Mês sem dias no calendário.');
    previousMonth = key;
  }
  if ([...dates].some(date => !calendar.months.some(month => month.firstDay.slice(0,7) === date.slice(0,7))))
    throw new Error('Mês ausente na resposta.');
  return { days: dates.size, sum };
}

// Moldura e divisórias vetoriais: nenhum raster, recurso remoto ou script no SVG.
function divider(y) {
  return `<g transform="translate(0 ${y})" fill="none">
    <path d="M86 0H964 M1198 0H2080" stroke="#031221" stroke-width="9"/>
    <path d="M86 0H964 M1198 0H2080" stroke="#074778" stroke-width="3"/>
    <path d="M200 -2H850 M1275 -2H1948" stroke="#08649c" stroke-width="1"/>
    <g id="arrow-${y}" stroke-linejoin="miter">
      <path d="M96 -20H114L136 0 114 20H96L116 0Z" fill="#031629" stroke="#07558b" stroke-width="3"/>
      <path d="M106 -15H115L131 0 115 15H106L120 0Z" fill="#22ddfa"/>
      <path d="M137 -5H150L155 0 150 5H137" fill="#ff444a"/>
      <path d="M144 -2H154" stroke="#ffad6f" stroke-width="3"/>
      <path d="M166 -3V3 M180 -5V5 M198 -3V3" stroke="#0589c7" stroke-width="4"/>
    </g>
    <use href="#arrow-${y}" transform="translate(2164 0) scale(-1 1)"/>
    <path d="M900 -26V15 M1262 -26V15" stroke="#ff394a" stroke-width="3"/>
    <path d="M855 -5V5 M877 -3V3 M1960 -4V4 M1990 -2V2" stroke="#1477a6" stroke-width="3"/>
    <path d="M1032 -34H1012L976 0 1012 34H1032L996 0Z" fill="#043669" stroke="#061527" stroke-width="7"/>
    <path d="M1025 -28H1015L985 0 1015 28H1025L995 0Z" fill="#28dbff"/>
    <path d="M1132 -34H1152L1188 0 1152 34H1132L1168 0Z" fill="#612a36" stroke="#061527" stroke-width="7"/>
    <path d="M1139 -28H1149L1179 0 1149 28H1139L1169 0Z" fill="#ff9569"/>
    <path d="M1081 -29V29" stroke="#943142" stroke-width="6"/>
    <path d="M1080 -29V29" stroke="#ff646c" stroke-width="2"/>
  </g>`;
}

function frame() {
  const outline = 'M94 173H793L807 155H1357L1371 173H2069L2095 197V525L2069 551H95L68 525V198Z';
  const corner = `<g id="corner"><path d="M67 224V198L91 173H127" fill="none" stroke="#032b4b" stroke-width="13"/>
    <path d="M68 219V198L93 173H126" fill="none" stroke="#078ac6" stroke-width="5"/>
    <path d="M76 197L88 184 M100 173H120" stroke="#6bf4ff" stroke-width="5"/>
    <path d="M79 195L86 188" stroke="#ff4e56" stroke-width="3"/>
    <path d="M90 211L106 197" stroke="#00e0e7" stroke-width="3"/>
    <path d="M71 267V343" stroke="#0388cf" stroke-width="6"/>
    <path d="M73 270V340" stroke="#a2f7ff" stroke-width="2"/>
    <path d="M65 371V438L71 442 77 436V366L71 362Z" fill="#061625" stroke="#125582" stroke-width="2"/>
    <path d="M67 376V430" stroke="#00b2df" stroke-width="2"/></g>`;
  return `<path d="${outline}" fill="url(#panel)" stroke="#020b14" stroke-width="14"/>
    <path d="${outline}" fill="none" stroke="#063958" stroke-width="7"/>
    <path d="${outline}" fill="none" stroke="#0a82b5" stroke-width="2"/>
    <path d="M116 179H796 M1368 179H2053 M119 545H2047" stroke="#073457" stroke-width="3"/>
    ${corner}<use href="#corner" transform="translate(2164 0) scale(-1 1)"/>
    <g transform="translate(0 724) scale(1 -1)"><path d="M68 198L94 173H127 M2037 173H2070L2095 198" fill="none" stroke="#078ac6" stroke-width="5"/>
    <path d="M91 175H118 M2046 175H2071" stroke="#affbff" stroke-width="3"/>
    <path d="M82 194L93 184 M2070 184L2082 194" stroke="#ff555a" stroke-width="4"/>
    <path d="M89 218L105 201 M2059 201L2075 218" stroke="#02cce7" stroke-width="3"/></g>
    <path d="M793 175L819 147H1345L1371 175 1345 205H819Z" fill="#020e19" stroke="#05314b" stroke-width="8"/>
    <path d="M802 175L823 151H1341L1362 175 1341 201H823Z" fill="none" stroke="#0c6991" stroke-width="2"/>
    <path d="M841 153H1323 M841 198H1323" stroke="#18cee0" stroke-width="2"/>
    <path d="M825 164V187 M1339 164V187" stroke="#fa3d51" stroke-width="6"/>
    <path d="M827 165V185 M1337 165V185" stroke="#ff9c85" stroke-width="2"/>`;
}

export function renderCalendar(calendar) {
  const { days } = validateCalendar(calendar);
  const startX = 177, startY = 302, pitchX = 1703 / calendar.weeks.length, pitchY = 25;
  const size = Math.min(21, pitchX - 6);
  const cells = calendar.weeks.map((week, column) => `<g data-week="${xml(week.firstDay)}">\n` +
    week.contributionDays.map(day => `<rect data-date="${day.date}" data-count="${day.contributionCount}" data-level="${day.contributionLevel}" data-weekday="${day.weekday}" x="${(startX + column * pitchX).toFixed(2)}" y="${startY + day.weekday * pitchY}" width="${size}" height="${size}" rx="3" fill="${COLORS[day.contributionLevel]}" stroke="#0a3043" stroke-width="1"><title>${day.date}: ${day.contributionCount} contribuições</title></rect>`).join('\n') + '\n</g>').join('\n');
  const months = calendar.months.map(month => {
    // Posiciona no primeiro início de semana do mês, como o GitHub; meses parciais ficam dentro do painel.
    let column = calendar.weeks.findIndex(week => week.firstDay >= month.firstDay && week.firstDay.slice(0,7) === month.firstDay.slice(0,7));
    if (column < 0) column = calendar.weeks.findIndex(week => week.contributionDays.some(day => day.date.slice(0,7) === month.firstDay.slice(0,7)));
    const x = startX + column * pitchX;
    return `<text data-month="${month.firstDay}" data-year="${month.year}" data-total-weeks="${month.totalWeeks}" x="${x.toFixed(2)}" y="278" font-size="18" fill="#79a1bc"><title>${xml(month.name)} ${month.year}</title>${xml(month.name.slice(0,3))}</text>`;
  }).join('\n');
  const legend = Object.entries(COLORS).map(([level, color], i) => `<g transform="translate(1940 ${302 + i * 34})"><rect width="21" height="21" rx="2" fill="${color}" stroke="#0a3043"/><text x="35" y="16" font-size="16" fill="#a0bfd0">${['Nenhuma','Pouca','Média','Alta','Máxima'][i]}</text></g>`).join('\n');
  const total = new Intl.NumberFormat('pt-BR').format(calendar.totalContributions);
  return `<svg xmlns="http://www.w3.org/2000/svg" width="2164" height="727" viewBox="0 0 2164 727" fill="none" role="img" aria-labelledby="title description">
<title id="title">Contribuições de ${LOGIN}</title>
<desc id="description">${total} contribuições nos últimos 12 meses no GitHub. ${calendar.weeks.length} semanas e ${days} dias, de ${calendar.weeks[0].contributionDays[0].date} a ${calendar.weeks.at(-1).contributionDays.at(-1).date}. Contagens e níveis oficiais, incluindo atividade privada anonimizada disponibilizada pelo GitHub.</desc>
<defs>
  <radialGradient id="background"><stop stop-color="#05131e"/><stop offset="1" stop-color="#080f15"/></radialGradient>
  <linearGradient id="panel" x2="0" y2="1"><stop stop-color="#03101c"/><stop offset="1" stop-color="#04111b"/></linearGradient>
</defs>
<rect width="2164" height="727" fill="url(#background)"/>
${divider(79)}
${frame()}
<g font-family="'Courier New',monospace">
<text x="1082" y="187" text-anchor="middle" font-size="29" font-weight="bold" letter-spacing="5" fill="#b9edff">CONTRIBUIÇÕES</text>
<text x="1082" y="232" text-anchor="middle" font-size="21" letter-spacing="2" fill="#82a9c5">Últimos 12 meses no GitHub</text>
${months}
${cells}
${legend}
<path d="M826 507H914 M1250 507H1338" stroke="#04cde6" stroke-width="2"/>
<text id="total" data-total="${calendar.totalContributions}" x="1082" y="515" text-anchor="middle" font-size="26" font-weight="bold" fill="#98eaff">${total} contribuições</text>
</g>
${divider(644)}
</svg>\n`;
}

export async function fetchCalendar(token) {
  if (!token) throw new Error('Configure PROFILE_CONTRIBUTIONS_TOKEN com read:user. Sem fallback para GITHUB_TOKEN.');
  const response = await fetch('https://api.github.com/graphql', {
    method: 'POST', headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json', 'User-Agent': 'profile-contributions-v3' },
    body: JSON.stringify({ query: QUERY, variables: { login: LOGIN } }), signal: AbortSignal.timeout(30000),
  });
  if (!response.ok) throw new Error(`GitHub HTTP ${response.status}; confira token, validade e SSO.`);
  const scopes = (response.headers.get('x-oauth-scopes') || '').split(',').map(s => s.trim());
  if (!scopes.includes('read:user') && !scopes.includes('user')) throw new Error('Token sem escopo read:user verificável. Use um token clássico com read:user.');
  const result = await response.json();
  if (result.errors?.length) throw new Error('A GraphQL retornou erros; confira token, read:user e SSO. SVG anterior preservado.');
  if (result.data?.viewer?.login.toLowerCase() !== LOGIN) throw new Error('O token precisa pertencer à própria conta do perfil.');
  const collection = result.data?.user?.contributionsCollection;
  validateCalendar(collection?.contributionCalendar);
  return collection;
}

async function main() {
  // --gh é exclusivamente local e explícito; o workflow exige o secret dedicado.
  const token = process.argv.includes('--gh') ? execFileSync('gh', ['auth', 'token'], { encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'] }).trim() : process.env.PROFILE_CONTRIBUTIONS_TOKEN;
  const collection = await fetchCalendar(token);
  const destination = fileURLToPath(new URL('../assets/v3/contributions/contributions.svg', import.meta.url));
  const svg = renderCalendar(collection.contributionCalendar);
  await mkdir(dirname(destination), { recursive: true });
  await writeFile(`${destination}.tmp`, svg, 'utf8');
  await rename(`${destination}.tmp`, destination);
  const auditIndex = process.argv.indexOf('--audit');
  if (auditIndex >= 0) {
    if (!process.argv[auditIndex + 1]) throw new Error('Informe o caminho local para auditoria.');
    await writeFile(resolve(process.argv[auditIndex + 1]), JSON.stringify(collection, null, 2));
  }
  console.log(JSON.stringify({ total: collection.contributionCalendar.totalContributions,
    weeks: collection.contributionCalendar.weeks.length, days: validateCalendar(collection.contributionCalendar).days,
    restrictedContributionsCount: collection.restrictedContributionsCount,
    hasAnyRestrictedContributions: collection.hasAnyRestrictedContributions, readUser: true }));
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  main().catch(error => { console.error(error.message); process.exitCode = 1; });
}
