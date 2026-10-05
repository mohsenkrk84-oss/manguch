/**
 * 80-brand-sheet.svg — the identity on one page.
 * Symbol, lockups, the three conceptual readings, scale behaviour, colour and
 * typography. Meant as the hand-off summary alongside README.md.
 */
import { BASE, ICON, shellBBox } from './emblem.mjs';
import { PALETTE, TYPE, symbolBody, lockupHorizontal, lockupStacked } from './brand.mjs';
import { wordmark } from './wordmark.mjs';
import { conceptFigure, constructionFigure } from './diagrams.mjs';

const W = 2400;
const M = 120;
const r2 = (v) => Number(v.toFixed(2));

const CSS = `<style>
  .h{font-family:Inter;font-size:25px;letter-spacing:.2em;fill:${PALETTE.navy};font-weight:600}
  .sub{font-family:Inter;font-size:20px;fill:${PALETTE.slate}}
  .cap{font-family:Inter;font-size:19px;fill:${PALETTE.slate}}
  .k{font-family:Inter;font-size:16px;fill:#93A2B0;letter-spacing:.14em}
  .n{font-family:Inter;font-size:18px;fill:${PALETTE.navy}}
  .big{font-family:Inter;font-size:62px;fill:${PALETTE.white};font-weight:600}
</style>`;

/** place a {body,w,h} figure into a box, centred, preserving aspect */
function place(fig, x, y, w, h, maxScale = Infinity) {
  const k = Math.min(w / fig.w, h / fig.h, maxScale);
  const ox = x + (w - fig.w * k) / 2;
  const oy = y + (h - fig.h * k) / 2;
  return `<g transform="translate(${r2(ox)} ${r2(oy)}) scale(${r2(k)})">${fig.body}</g>`;
}

function head(y, title, sub) {
  return `<text x="${M}" y="${y}" class="h">${title}</text>
  <text x="${M}" y="${y + 30}" class="sub">${sub}</text>
  <line x1="${M}" y1="${y + 48}" x2="${W - M}" y2="${y + 48}" stroke="#E4EAEF" stroke-width="1.5"/>`;
}

export function brandSheet() {
  const parts = [];
  let y = 110;

  /* ---------------- hero ---------------- */
  const heroH = 560;
  const markH = 360;
  const mark = symbolBody(BASE, { opts: { status: 1 }, size: markH, fill: PALETTE.white, statusColor: PALETTE.tealBright, pad: 0 });
  const tx = M + 110 + mark.w + 120;
  parts.push(`
  <rect x="${M}" y="${y}" width="${W - M * 2}" height="${heroH}" rx="26" fill="${PALETTE.navy}"/>
  <g transform="translate(${M + 110} ${y + (heroH - markH) / 2 - 20})">${mark.body}</g>
  <text x="${tx}" y="${y + 168}" class="big">BUSINESS GUARDIAN</text>
  <text x="${tx}" y="${y + 226}" style="font-family:Inter;font-size:27px;fill:#8FA6B8;letter-spacing:.05em">Always watching. Always protecting.</text>
  <text x="${tx}" y="${y + 292}" style="font-family:Inter;font-size:20px;fill:#63798D">Cloud monitoring for websites, APIs and critical business processes.</text>
  <text x="${tx}" y="${y + 326}" style="font-family:Inter;font-size:20px;fill:#63798D">Simulated user journeys · failure detection · incident alerting.</text>
  <line x1="${M + 110}" y1="${y + heroH - 118}" x2="${W - M - 110}" y2="${y + heroH - 118}" stroke="#22384C"/>
  <text x="${M + 110}" y="${y + heroH - 74}" style="font-family:Inter;font-size:18px;fill:#5E7488;letter-spacing:.1em">LOGO &amp; IDENTITY SYSTEM · v1.0</text>
  <text x="${W - M - 110}" y="${y + heroH - 74}" text-anchor="end" style="font-family:Inter;font-size:18px;fill:#5E7488;letter-spacing:.1em">SYMBOL · LOCKUPS · MONOCHROME · COLOUR · ICON</text>`);
  y += heroH + 130;

  /* ---------------- symbol on four grounds ---------------- */
  const grounds = [
    ['Primary', PALETTE.navy, PALETTE.teal, null],
    ['Monochrome', '#000000', null, null],
    ['Reversed', PALETTE.white, PALETTE.tealBright, PALETTE.navy],
    ['Mono reversed', PALETTE.white, null, PALETTE.navy],
    ['Accent', PALETTE.teal, null, PALETTE.navy],
  ];
  const cw = (W - M * 2) / grounds.length;
  const box = 330;
  parts.push(head(y, 'SYMBOL', 'One mark, four grounds. The status point is the only colour in the system and is optional.'));
  grounds.forEach(([label, fill, status, bg], i) => {
    const x = M + i * cw;
    const s = symbolBody(BASE, { opts: { status: 1 }, size: box - 90, fill, statusColor: status, pad: 0 });
    if (bg) {
      parts.push(
        `<rect x="${x + 10}" y="${y + 96}" width="${box - 20}" height="${box - 20}" rx="18" fill="${bg}"/>`
      );
    }
    parts.push(place({ body: s.body, w: s.w, h: s.h }, x + 10, y + 96, box - 20, box - 20));
    parts.push(`<text x="${x + box / 2}" y="${y + 96 + box + 26}" text-anchor="middle" class="cap">${label}</text>`);
  });
  y += 96 + box + 130;

  /* ---------------- lockups ---------------- */
  const hl = lockupHorizontal({ cap: 74, fill: PALETTE.navy, statusColor: PALETTE.teal, padRatio: 0 });
  const hlw = lockupHorizontal({ cap: 74, fill: PALETTE.white, statusColor: PALETTE.tealBright, padRatio: 0 });
  const st = lockupStacked({ cap: 60, fill: PALETTE.navy, statusColor: PALETTE.teal, padRatio: 0, symbolRatio: 2.3 });
  const colA = 1330;
  const colB = W - M * 2 - colA - 40;
  const stackH = 500;
  parts.push(head(y, 'LOCKUPS', 'Horizontal for navigation, decks and documents. Stacked for badges, covers and profile grids.'));
  const ly = y + 96;
  const tileH = (hl.h + hlw.h + 96 + 70) / 2;
  parts.push(`<rect x="${M}" y="${ly}" width="${colA}" height="${tileH}" rx="16" fill="#F7F9FB"/>`);
  parts.push(place(hl, M + 36, ly + (tileH - hl.h) / 2, colA - 72, hl.h, 1));
  parts.push(`<rect x="${M}" y="${ly + tileH + 40}" width="${colA}" height="${tileH}" rx="16" fill="${PALETTE.navy}"/>`);
  parts.push(place(hlw, M + 36, ly + tileH + 40 + (tileH - hlw.h) / 2, colA - 72, hlw.h, 1));
  parts.push(`<rect x="${M + colA + 40}" y="${ly}" width="${colB}" height="${tileH * 2 + 40}" rx="16" fill="#F7F9FB"/>`);
  parts.push(place(st, M + colA + 80, ly + 40, colB - 120, tileH * 2 + 40 - 80, 1));
  void stackH;
  y = ly + tileH * 2 + 40 + 130;

  /* ---------------- construction + three readings ---------------- */
  const figs = [
    [constructionFigure({ labels: false }), 'Construction grid'],
    [conceptFigure('owl'), 'Reads as: owl — vigilance'],
    [conceptFigure('eye'), 'Reads as: eye — monitoring'],
    [conceptFigure('shield'), 'Reads as: shield — protection'],
  ];
  const fw = (W - M * 2 - 3 * 24) / 4;
  parts.push(head(y, 'CONSTRUCTION & THREE READINGS', 'One silhouette does all three jobs. Nothing is stacked behind the owl — the shield is the owl.'));
  figs.forEach(([fig, label], i) => {
    const x = M + i * (fw + 24);
    parts.push(`<rect x="${x}" y="${y + 96}" width="${fw}" height="${fw}" rx="16" fill="#FBFCFD" stroke="#E9EEF2"/>`);
    parts.push(place(fig, x + 14, y + 110, fw - 28, fw - 28));
    parts.push(`<text x="${x + fw / 2}" y="${y + 96 + fw + 30}" text-anchor="middle" class="cap">${label}</text>`);
  });
  y += 96 + fw + 130;

  /* ---------------- scale ---------------- */
  const ladder = [128, 64, 48, 32, 24, 16];
  parts.push(head(y, 'SMALL SIZES', 'The icon variant holds at 16px: bolder monitoring ring, larger sensor core, no status point.'));
  const rowY = y + 108;
  const cell = 168;
  parts.push(`<text x="${M}" y="${rowY}" class="cap" style="letter-spacing:.1em">ICON VARIANT — favicon · app icon · extension · incident notifications</text>`);
  ladder.forEach((sz, i) => {
    const x = M + i * cell;
    const a = symbolBody(ICON, { size: sz, fill: PALETTE.navy, pad: 0 });
    parts.push(place({ body: a.body, w: a.w, h: a.h }, x, rowY + 22, cell - 34, 132));
    parts.push(`<text x="${x + (cell - 34) / 2}" y="${rowY + 182}" text-anchor="middle" class="k">${sz}px</text>`);
  });
  const rowY2 = rowY + 236;
  parts.push(`<text x="${M}" y="${rowY2 - 4}" class="cap" style="letter-spacing:.1em">FULL-DETAIL VARIANT — use from 48px up, or where the mark is large</text>`);
  [128, 64, 48].forEach((sz, i) => {
    const x = M + i * cell;
    const b = symbolBody(BASE, { size: sz, fill: PALETTE.navy, statusColor: PALETTE.teal, pad: 0 });
    parts.push(place({ body: b.body, w: b.w, h: b.h }, x, rowY2 + 24, cell - 34, 132));
    parts.push(`<text x="${x + (cell - 34) / 2}" y="${rowY2 + 184}" text-anchor="middle" class="k">${sz}px</text>`);
  });
  parts.push(`<text x="${M + 3 * cell + 30}" y="${rowY2 + 96}" class="cap">Below 48px the fine monitoring ring,</text>`);
  parts.push(`<text x="${M + 3 * cell + 30}" y="${rowY2 + 124}" class="cap">the status point and the thin guardline are</text>`);
  parts.push(`<text x="${M + 3 * cell + 30}" y="${rowY2 + 152}" class="cap">replaced by the icon variant above.</text>`);
  y = rowY2 + 240;

  /* ---------------- colour + typography ---------------- */
  parts.push(head(y, 'COLOUR & TYPOGRAPHY', 'Outfit SemiBold for the wordmark, Inter for interface and body copy. One accent only.'));
  const swatches = [
    ['Guardian Navy', PALETTE.navy],
    ['Deep Navy', PALETTE.navyDeep],
    ['Signal Teal', PALETTE.teal],
    ['Teal Bright', PALETTE.tealBright],
    ['Mist', PALETTE.mist],
    ['Slate', PALETTE.slate],
  ];
  const swW = (W - M * 2) / swatches.length;
  swatches.forEach(([name, hex], i) => {
    const x = M + i * swW;
    parts.push(`<rect x="${x}" y="${y + 96}" width="${swW - 20}" height="116" rx="12" fill="${hex}" stroke="#E7ECF0"/>`);
    parts.push(`<text x="${x}" y="${y + 96 + 146}" class="n">${name}</text>`);
    parts.push(`<text x="${x}" y="${y + 96 + 172}" class="k">${hex.toUpperCase()}</text>`);
  });
  const wm = wordmark(['BUSINESS', 'GUARDIAN'], {
    family: TYPE.family,
    weight: TYPE.weight,
    size: 54,
    tracking: 54 * TYPE.trackingRatio,
    wordGap: TYPE.wordGap,
  });
  const alpha = wordmark(['ABCDEFGHIJKLM', 'NOPQRSTUVWXYZ', '0123456789'], {
    family: TYPE.family,
    weight: TYPE.weight,
    size: 30,
    tracking: 30 * 0.09,
    wordGap: 0.55,
  });
  const ty = y + 96 + 116 + 160;
  parts.push(`<line x1="${M}" y1="${ty - 34}" x2="${W - M}" y2="${ty - 34}" stroke="#E4EAEF"/>`);
  parts.push(`<path transform="translate(${M} ${ty + 56})" d="${wm.d}" fill="${PALETTE.navy}"/>`);
  parts.push(`<path transform="translate(${M} ${ty + 180})" d="${alpha.d}" fill="${PALETTE.navy}" opacity="0.85"/>`);
  parts.push(`<text x="${W - M}" y="${ty + 60}" text-anchor="end" class="cap">Outfit SemiBold · tracking 0.155 em</text>`);
  parts.push(`<text x="${W - M}" y="${ty + 90}" text-anchor="end" class="cap">Delivered as outlines — no font required</text>`);
  parts.push(`<text x="${W - M}" y="${ty + 184}" text-anchor="end" class="cap">Inter Regular / Medium — interface, reports, alerts</text>`);
  y = ty + 240;

  /* ---------------- tagline ---------------- */
  parts.push(`
  <rect x="${M}" y="${y}" width="${W - M * 2}" height="190" rx="24" fill="${PALETTE.navy}"/>
  <text x="${W / 2}" y="${y + 96}" text-anchor="middle" class="big">Always watching. Always protecting.</text>
  <text x="${W / 2}" y="${y + 142}" text-anchor="middle" style="font-family:Inter;font-size:18px;fill:#7E93A6;letter-spacing:.14em">MONITORING · DETECTION · INCIDENT ALERTING FOR DIGITAL BUSINESS</text>`);
  y += 190 + 110;

  return `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${Math.round(y)}" viewBox="0 0 ${W} ${Math.round(
    y
  )}">${CSS}<rect width="${W}" height="${Math.round(y)}" fill="#FFFFFF"/>${parts.join('\n')}</svg>`;
}

void shellBBox;
