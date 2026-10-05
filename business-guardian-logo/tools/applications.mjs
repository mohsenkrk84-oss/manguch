/**
 * 90-applications.svg — the identity in use.
 * Browser tab + header, dashboard sidebar, incident notification and social
 * avatar. This is the "does it actually work?" page: every mark here is the
 * real vector file, not a redraw.
 */
import { BASE, ICON } from './emblem.mjs';
import { PALETTE, symbolBody, lockupHorizontal, lockupStacked } from './brand.mjs';
import { wordmark } from './wordmark.mjs';

const W = 2000;
const r2 = (v) => Number(v.toFixed(2));
const F = (size, weight = 400, fill = PALETTE.navy, ls = 0) =>
  `font-family:Inter;font-size:${size}px;font-weight:${weight};fill:${fill};letter-spacing:${ls}em`;

const CSS = `<style>
 .h{font-family:Inter;font-size:24px;letter-spacing:.2em;fill:${PALETTE.navy};font-weight:600}
 .sub{font-family:Inter;font-size:19px;fill:${PALETTE.slate}}
 .lab{font-family:Inter;font-size:17px;fill:#93A2B0;letter-spacing:.12em}
 .ui{font-family:Inter;font-size:15px;fill:#6C7C8C}
 .ui2{font-family:Inter;font-size:15px;fill:#26384A;font-weight:500}
</style>`;

function head(y, title, sub) {
  return `<text x="110" y="${y}" class="h">${title}</text>
  <text x="110" y="${y + 28}" class="sub">${sub}</text>
  <line x1="110" y1="${y + 44}" x2="${W - 110}" y2="${y + 44}" stroke="#E4EAEF" stroke-width="1.5"/>`;
}

function place(fig, x, y, w, h, maxK = Infinity) {
  const k = Math.min(w / fig.w, h / fig.h, maxK);
  return `<g transform="translate(${r2(x + (w - fig.w * k) / 2)} ${r2(y + (h - fig.h * k) / 2)}) scale(${r2(k)})">${
    fig.body
  }</g>`;
}

export function applications() {
  const parts = [];
  let y = 110;

  parts.push(head(y, 'IN USE', 'Every mark below is the delivered vector file, placed at real interface sizes.'));
  y += 90;

  /* ---------------- 1. browser window ---------------- */
  const bw = 1120;
  const bh = 640;
  const l = lockupHorizontal({ cap: 34, fill: PALETTE.navy, statusColor: PALETTE.teal });
  const fav = symbolBody(ICON, { size: 18, fill: PALETTE.navy, pad: 0 });

  parts.push(`<text x="110" y="${y - 12}" class="lab">WEBSITE HEADER &amp; BROWSER TAB</text>`);
  parts.push(`<rect x="110" y="${y}" width="${bw}" height="${bh}" rx="18" fill="#FFFFFF" stroke="#DDE4EA"/>`);
  /* tab strip */
  parts.push(`<path d="M110 ${y + 18} a18 18 0 0 1 18 -18 h${bw - 36} a18 18 0 0 1 18 18 v34 h-${bw} Z" fill="#EEF2F6"/>`);
  parts.push(`<rect x="110" y="${y + 30}" width="290" height="44" rx="12" fill="#FFFFFF"/>`);
  parts.push(place({ body: fav.body, w: fav.w, h: fav.h }, 128, y + 30, 44, 44));
  parts.push(`<text x="182" y="${y + 58}" class="ui2">Business Guardian</text>`);
  parts.push(`<text x="420" y="${y + 58}" class="ui">+ 4 tabs</text>`);
  /* url bar */
  parts.push(`<rect x="${110 + bw - 420}" y="${y + 36}" width="400" height="34" rx="17" fill="#FFFFFF"/>`);
  parts.push(
    `<text x="${110 + bw - 200}" y="${y + 58}" class="ui" text-anchor="middle">app.businessguardian.io/monitoring</text>`
  );
  /* page header */
  parts.push(`<rect x="110" y="${y + 74}" width="${bw}" height="96" fill="#FFFFFF"/>`);
  parts.push(place(l, 160, y + 92, 520, 60));
  parts.push(
    `<text x="${110 + bw - 60}" y="${y + 128}" class="ui2" text-anchor="end">Dashboard</text>
     <text x="${110 + bw - 170}" y="${y + 128}" class="ui" text-anchor="end">Incidents</text>
     <text x="${110 + bw - 270}" y="${y + 128}" class="ui" text-anchor="end">Journeys</text>
     <text x="${110 + bw - 360}" y="${y + 128}" class="ui" text-anchor="end">APIs</text>`
  );
  parts.push(`<line x1="110" y1="${y + 170}" x2="${110 + bw}" y2="${y + 170}" stroke="#E4EAEF"/>`);
  /* page body: status cards */
  const cardY = y + 214;
  const cards = [
    ['Uptime', '99.98%', '#0E7C66', 'last 30 days'],
    ['Checks today', '18,420', PALETTE.navy, 'across 96 journeys'],
    ['Active incidents', '1', '#B4432B', 'checkout — degraded'],
    ['Mean detection', '41s', PALETTE.navy, 'before customers notice'],
  ];
  cards.forEach(([label, value, color, note], i) => {
    const cw = (bw - 100 - 3 * 22) / 4;
    const x = 160 + i * (cw + 22);
    parts.push(`<rect x="${x}" y="${cardY}" width="${cw}" height="150" rx="14" fill="#F7F9FB" stroke="#E7EDF2"/>`);
    parts.push(`<text x="${x + 24}" y="${cardY + 42}" class="lab" style="letter-spacing:.08em">${label.toUpperCase()}</text>`);
    parts.push(`<text x="${x + 24}" y="${cardY + 92}" style="${F(38, 600, color)}">${value}</text>`);
    parts.push(`<text x="${x + 24}" y="${cardY + 122}" class="ui">${note}</text>`);
  });
  /* chart */
  parts.push(`<rect x="160" y="${cardY + 186}" width="${bw - 100}" height="208" rx="14" fill="#F7F9FB" stroke="#E7EDF2"/>`);
  parts.push(`<text x="184" y="${cardY + 224}" class="ui2">Response time — production</text>`);
  const pts = [210, 205, 195, 190, 150, 140, 146, 138, 132, 128, 120, 118, 112, 108, 106, 104];
  const path = pts
    .map((v, i) => `${i ? 'L' : 'M'} ${184 + i * ((bw - 150) / (pts.length - 1))} ${cardY + 348 - (v - 90) * 1.02}`)
    .join(' ');
  parts.push(`<path d="${path}" fill="none" stroke="${PALETTE.teal}" stroke-width="3" stroke-linejoin="round"/>`);
  parts.push(`<line x1="184" y1="${cardY + 372}" x2="${bw - 20}" y2="${cardY + 372}" stroke="#DDE4EA"/>`);

  /* ---------------- 2. dashboard sidebar + app icon ---------------- */
  const sx = 110 + bw + 60;
  const sw = W - 110 - sx;
  parts.push(`<text x="${sx}" y="${y - 12}" class="lab">SAAS DASHBOARD · APP ICON · NOTIFICATIONS</text>`);
  /* sidebar */
  parts.push(`<rect x="${sx}" y="${y}" width="${sw}" height="360" rx="18" fill="${PALETTE.navy}"/>`);
  const side = lockupStacked({ cap: 22, fill: PALETTE.white, statusColor: PALETTE.tealBright, symbolRatio: 2.2, padRatio: 0 });
  parts.push(place(side, sx + 30, y + 34, 210, 130, 1));
  ['Overview', 'Journeys', 'API checks', 'Incidents', 'Reports'].forEach((it, i) => {
    const oy = y + 190 + i * 32;
    if (i === 3) parts.push(`<rect x="${sx + 20}" y="${oy - 20}" width="${sw - 40}" height="28" rx="8" fill="#17324A"/>`);
    parts.push(`<circle cx="${sx + 44}" cy="${oy - 6}" r="4" fill="${i === 3 ? PALETTE.tealBright : '#3E556B'}"/>`);
    parts.push(
      `<text x="${sx + 62}" y="${oy}" style="${F(16, 400, i === 3 ? '#FFFFFF' : '#8CA0B2')}">${it}</text>`
    );
  });
  /* app icon row */
  const tile = 104;
  const icons = [
    ['App icon', ICON, PALETTE.navy, PALETTE.white, PALETTE.tealBright, '#0B1B2B', true],
    ['Light tile', ICON, PALETTE.white, PALETTE.navy, PALETTE.teal, '#FFFFFF', true],
    ['Favicon 32', ICON, null, PALETTE.navy, null, null, false],
    ['Favicon 16', ICON, null, PALETTE.navy, null, null, false],
  ];
  icons.forEach(([label, g, bg, fill, status, bgLight, isTile], i) => {
    const size = isTile ? taleSize(tile) : i === 2 ? 32 : 16;
    const s = symbolBody(g, { size, fill, statusColor: status, pad: 0 });
    const x = sx + i * (sw / icons.length + 6);
    const boxY = y + 400;
    if (bgLight) {
      parts.push(`<rect x="${x}" y="${boxY}" width="${tile}" height="${tile}" rx="22" fill="${bgLight}"/>`);
    } else {
      parts.push(`<rect x="${x}" y="${boxY}" width="${tile}" height="${tile}" rx="18" fill="#F7F9FB" stroke="#E7EDF2"/>`);
    }
    parts.push(place({ body: s.body, w: s.w, h: s.h }, x, boxY, tile, tile));
    parts.push(`<text x="${x + tile / 2}" y="${boxY + tile + 26}" text-anchor="middle" class="ui">${label}</text>`);
  });

  /* ---------------- 3. incident notification ---------------- */
  const ny = y + 400 + tile + 90;
  const nw = W - 220;
  parts.push(
    `<rect x="110" y="${ny}" width="${nw}" height="250" rx="18" fill="#FFFFFF" stroke="#DDE4EA"/>`
  );
  const ns = symbolBody(ICON, { size: 40, fill: PALETTE.navy, pad: 0 });
  parts.push(place({ body: ns.body, w: ns.w, h: ns.h }, 152, ny + 34, 40, 40));
  parts.push(`<text x="208" y="${ny + 62}" style="${F(19, 600)}">Business Guardian</text>`);
  parts.push(`<text x="${nw - 40}" y="${ny + 60}" class="ui" text-anchor="end">09:41 · just now</text>`);
  parts.push(`<line x1="110" y1="${ny + 96}" x2="${110 + nw}" y2="${ny + 96}" stroke="#EDF1F5"/>`);
  parts.push(
    `<text x="152" y="${ny + 146}" style="${F(26, 600)}">Checkout journey failing in 2 regions</text>
     <text x="152" y="${ny + 182}" class="ui">Simulated user journey “Checkout — EU” failed 3 consecutive checks. Card payment step returns HTTP 502.</text>
     <text x="152" y="${ny + 210}" class="ui">Detected 09:40:58 · customers would have noticed at ~09:47 · notified in 41s.</text>`
  );
  parts.push(`<rect x="152" y="${ny + 224}" width="150" height="4" rx="2" fill="${PALETTE.teal}"/>`);

  /* ---------------- 4. social avatar + dark header ---------------- */
  const ay = ny + 250 + 90;
  const avatar = 210;
  const tileSvg = symbolBody(ICON, { size: 128, fill: PALETTE.white, statusColor: PALETTE.tealBright, pad: 0 });
  parts.push(`<text x="110" y="${ay - 12}" class="lab">SOCIAL AVATAR · DARK HEADER</text>`);
  parts.push(`<circle cx="${110 + avatar / 2}" cy="${ay + avatar / 2}" r="${avatar / 2}" fill="${PALETTE.navy}"/>`);
  parts.push(place({ body: tileSvg.body, w: tileSvg.w, h: tileSvg.h }, 110 + 30, ay + 30, avatar - 60, avatar - 60));
  parts.push(`<text x="${110 + avatar / 2}" y="${ay + avatar + 30}" text-anchor="middle" class="ui">Profile grid</text>`);

  const hx = 110 + avatar + 60;
  const hw = W - 110 - hx;
  parts.push(`<rect x="${hx}" y="${ay}" width="${hw}" height="${avatar}" rx="18" fill="${PALETTE.navy}"/>`);
  const dl = lockupHorizontal({ cap: 36, fill: PALETTE.white, statusColor: PALETTE.tealBright });
  parts.push(place(dl, hx + 46, ay + (avatar - dl.h) / 2, 560, dl.h, 1));
  parts.push(
    `<text x="${hx + hw - 46}" y="${ay + 96}" class="ui" text-anchor="end" fill="#8CA0B2">Product</text>
     <text x="${hx + hw - 170}" y="${ay + 96}" class="ui" text-anchor="end" fill="#8CA0B2">Pricing</text>
     <text x="${hx + hw - 260}" y="${ay + 96}" class="ui" text-anchor="end" fill="#8CA0B2">Docs</text>
     <rect x="${hx + hw - 210}" y="${ay + 118}" width="164" height="44" rx="22" fill="${PALETTE.teal}"/>
     <text x="${hx + hw - 128}" y="${ay + 146}" text-anchor="middle" style="${F(16, 600, '#062733')}">Start free</text>`
  );

  y = ay + avatar + 110;

  return `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${Math.round(y)}" viewBox="0 0 ${W} ${Math.round(
    y
  )}">${CSS}<rect width="${W}" height="${Math.round(y)}" fill="#FFFFFF"/>${parts.join('\n')}</svg>`;
}

function taleSize(tile) {
  return tile * 0.62;
}

void BASE;
void wordmark;
