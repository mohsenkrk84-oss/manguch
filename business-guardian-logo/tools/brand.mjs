/**
 * BUSINESS GUARDIAN — brand asset generator
 * ------------------------------------------
 * Emits the full vector identity as self-contained SVG files:
 *   · primary emblem (colour, navy, mono black, mono white, reverse)
 *   · symbol-only marks
 *   · horizontal lockup
 *   · stacked lockup
 *   · small-size icon variant
 *   · app tile / favicon tile
 *   · wordmark outlines
 *
 * Every file carries its own mask id and no external references, so the SVGs
 * can be dropped anywhere (web, print, Figma, decks) unchanged.
 */
import {
  BASE,
  ICON,
  mkG,
  emblemParts,
  shellBBox,
} from './emblem.mjs';
import { wordmark } from './wordmark.mjs';

/* ------------------------------------------------------------------ */
/* Palette — restrained: one dark, one accent                          */
/* ------------------------------------------------------------------ */
export const PALETTE = {
  navy: '#0B1B2B', // Guardian Navy — primary mark + type
  navyDeep: '#081420', // deepest surfaces
  teal: '#14BFD4', // Signal Teal — the single accent (status point)
  tealBright: '#38D6E6', // accent on dark ground
  ink: '#000000', // mono black
  white: '#FFFFFF', // mono white / paper
  mist: '#F3F6F8', // light neutral surface
  slate: '#5B6B7C', // secondary type, rules
};

export const TYPE = {
  family: 'outfit',
  weight: 600,
  trackingRatio: 0.155, // tracking as a ratio of cap height
  wordGap: 0.5, // word gap as a ratio of cap height
  captionWeight: 500,
};

/* ------------------------------------------------------------------ */
/* Core symbol                                                         */
/* ------------------------------------------------------------------ */

/**
 * Symbol as SVG body (no <svg> wrapper).
 * Returns { body, w, h } in the symbol's own units.
 */
export function symbolBody(g = BASE, { opts = {}, size, fill, statusColor, pad = 0, tile } = {}) {
  const bb = shellBBox(g);
  const k = size / bb.h;
  const w = bb.w * k + pad * 2;
  const h = bb.h * k + pad * 2;
  const p = emblemParts(g, opts);
  const id = `bgm${Math.round(k * 1000)}${opts.simple ? 'i' : ''}${fill.replace('#', '')}${pad}`;
  let body = `<mask id="${id}" maskUnits="userSpaceOnUse" x="0" y="0" width="${g.W}" height="${g.W}">
<path d="${p.shell}" fill="#fff"/><path d="${p.holes}" fill="#000" fill-rule="evenodd"/>
</mask>
<g transform="translate(${pad}) scale(${k}) translate(${-bb.x0} ${-bb.y0})">
<g mask="url(#${id})"><rect x="${bb.x0}" y="${bb.y0}" width="${bb.w}" height="${bb.h}" fill="${fill}"/><path d="${p.pupils}" fill="${fill}"/></g>
${p.voids ? `<path d="${p.voids}" fill="${tile || 'none'}" class="void"/>` : ''}
${statusColor ? statusDots(g, opts, statusColor, bb, pad, k) : ''}
</g>`;
  if (tile) body = `<rect width="${w}" height="${h}" rx="${tile.rx}" fill="${tile.fill}"/>${body}`;
  return { body, w, h };
}

function statusDots(g, opts, color, bb, pad, k) {
  if (!opts.status) return '';
  const r = 8.5;
  const a = opts.status === 2 ? -90 : -45;
  const rad = (a * Math.PI) / 180;
  const off = 17;
  const dots = [-1, 1]
    .map((s) => {
      const cx = g.cx + s * g.ex + off * Math.cos(rad);
      const cy = g.ey + off * Math.sin(rad);
      return `<circle cx="${cx.toFixed(2)}" cy="${cy.toFixed(2)}" r="${r}" fill="${color}"/>`;
    })
    .join('');
  void bb;
  void pad;
  void k;
  return dots;
}

/** Standalone SVG document for the symbol. */
export function symbolSVG(g = BASE, opts = {}) {
  const { size = 512, fill = PALETTE.navy, statusColor = PALETTE.teal, pad = 0.085, ...rest } = opts;
  const padPx = size * (typeof pad === 'number' ? pad : 0);
  const { body, w, h } = symbolBody(g, { ...rest, size, fill, statusColor, pad: padPx });
  return wrap(body, w, h);
}

function wrap(body, w, h, extra = '') {
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${round(w)}" height="${round(
    h
  )}" viewBox="0 0 ${round(w)} ${round(h)}" fill="none" role="img" aria-label="Business Guardian">${extra}${body}</svg>`;
}

const round = (v) => Number(v.toFixed(2));

/* ------------------------------------------------------------------ */
/* Lockups                                                             */
/* ------------------------------------------------------------------ */

/**
 * Horizontal lockup: symbol left, wordmark right, cap-height aligned.
 * Sizing: the symbol's tight height is 1.70× the wordmark cap height.
 */
export function lockupHorizontal(opts = {}) {
  const {
    g = BASE,
    markOpts = { opts: { status: 1 } },
    fill = PALETTE.navy,
    statusColor = PALETTE.teal,
    cap = 100,
    symbolRatio = 1.7,
    gapRatio = 0.62, // horizontal air between mark and type, × cap
    padRatio = 0.42, // clear space baked in, × cap
  } = opts;

  const Hm = cap * symbolRatio;
  const pad = Math.round(cap * padRatio);
  const wm = wordmark(['BUSINESS', 'GUARDIAN'], {
    family: TYPE.family,
    weight: TYPE.weight,
    size: cap,
    tracking: cap * TYPE.trackingRatio,
    wordGap: TYPE.wordGap,
  });
  const gap = cap * gapRatio;
  const W = pad + Hm * (shellBBox(g).w / shellBBox(g).h) + gap + wm.width + pad;
  const H = Hm + pad * 2;

  const sym = symbolBody(g, { ...markOpts, size: Hm, fill, statusColor });

  /* cap centre sits at 52% of the mark's height: the tufts pull visual mass up */
  const baseline = pad + Hm * 0.52 + cap / 2;
  const body =
    `<g transform="translate(${round(pad)} ${round(pad)})">${sym.body}</g>` +
    `<g transform="translate(${round(pad + Hm * (shellBBox(g).w / shellBBox(g).h) + gap)} ${round(
      baseline
    )})"><path d="${wm.d}" fill="${fill}"/></g>`;

  return { body, w: W, h: H };
}

/** Stacked lockup: symbol above centred wordmark. */
export function lockupStacked(opts = {}) {
  const {
    g = BASE,
    markOpts = { opts: { status: 1 } },
    fill = PALETTE.navy,
    statusColor = PALETTE.teal,
    cap = 100,
    symbolRatio = 2.6,
    gapRatio = 0.72,
    padRatio = 0.4,
  } = opts;

  const Hm = cap * symbolRatio;
  const pad = Math.round(cap * padRatio);
  const wm = wordmark(['BUSINESS', 'GUARDIAN'], {
    family: TYPE.family,
    weight: TYPE.weight,
    size: cap,
    tracking: cap * TYPE.trackingRatio,
    wordGap: TYPE.wordGap,
  });
  const bb = shellBBox(g);
  const symW = Hm * (bb.w / bb.h);
  const gap = cap * gapRatio;
  const W = Math.max(symW, wm.width) + pad * 2;
  const H = Hm + gap + cap + pad * 2;
  const sym = symbolBody(g, { ...markOpts, size: Hm, fill, statusColor });

  const body =
    `<g transform="translate(${round((W - symW) / 2)} ${pad})">${sym.body}</g>` +
    `<g transform="translate(${round((W - wm.width) / 2)} ${round(pad + Hm + gap + cap)})"><path d="${wm.d}" fill="${fill}"/></g>`;

  return { body, w: W, h: H };
}

/* ------------------------------------------------------------------ */
/* Export bundle                                                       */
/* ------------------------------------------------------------------ */

export const FILES = () => {
  const out = [];
  const add = (name, body, w, h) => out.push({ name, svg: wrap(body, w, h) });

  /* --- A/B. symbol, colour + mono ---------------------------------- */
  const markOpts = { opts: { status: 1 } };
  add('01-emblem-primary.svg', ...Object.values(symDoc(BASE, markOpts, PALETTE.navy, PALETTE.teal)));
  add('02-emblem-navy.svg', ...Object.values(symDoc(BASE, {}, PALETTE.navy)));
  add('03-emblem-black.svg', ...Object.values(symDoc(BASE, {}, PALETTE.ink)));
  add('04-emblem-white.svg', ...Object.values(symDoc(BASE, {}, PALETTE.white)));
  add('05-emblem-reverse.svg', ...Object.values(symDoc(BASE, markOpts, PALETTE.white, PALETTE.tealBright)));

  /* --- C. horizontal lockup --------------------------------------- */
  for (const [name, o] of Object.entries({
    '10-lockup-horizontal-primary.svg': { fill: PALETTE.navy, statusColor: PALETTE.teal },
    '11-lockup-horizontal-black.svg': { fill: PALETTE.ink, statusColor: null, markOpts: { opts: {} } },
    '12-lockup-horizontal-white.svg': { fill: PALETTE.white, statusColor: null, markOpts: { opts: {} } },
    '13-lockup-horizontal-reverse.svg': { fill: PALETTE.white, statusColor: PALETTE.tealBright, markOpts: { opts: { status: 1 } } },
  })) {
    const l = lockupHorizontal(o);
    add(name, l.body, l.w, l.h);
  }

  /* --- D. stacked lockup ------------------------------------------ */
  for (const [name, o] of Object.entries({
    '20-lockup-stacked-primary.svg': { fill: PALETTE.navy, statusColor: PALETTE.teal },
    '21-lockup-stacked-black.svg': { fill: PALETTE.ink, statusColor: null, markOpts: { opts: {} } },
    '22-lockup-stacked-white.svg': { fill: PALETTE.white, statusColor: null, markOpts: { opts: {} } },
    '23-lockup-stacked-reverse.svg': { fill: PALETTE.white, statusColor: PALETTE.tealBright, markOpts: { opts: { status: 1 } } },
  })) {
    const l = lockupStacked(o);
    add(name, l.body, l.w, l.h);
  }

  /* --- G. small icon ---------------------------------------------- */
  add('30-icon-primary.svg', ...Object.values(iconDoc(ICON, PALETTE.navy, PALETTE.teal)));
  add('31-icon-black.svg', ...Object.values(iconDoc(ICON, PALETTE.ink)));
  add('32-icon-white.svg', ...Object.values(iconDoc(ICON, PALETTE.white)));

  /* --- app tile + social avatar ----------------------------------- */
  add('40-app-tile.svg', ...Object.values(tileDoc(ICON, PALETTE.navy, PALETTE.white, PALETTE.tealBright)));
  add('41-app-tile-light.svg', ...Object.values(tileDoc(ICON, PALETTE.white, PALETTE.navy, PALETTE.teal)));

  /* --- wordmark ---------------------------------------------------- */
  const wm = wordmark(['BUSINESS', 'GUARDIAN'], {
    family: TYPE.family,
    weight: TYPE.weight,
    size: 200,
    tracking: 200 * TYPE.trackingRatio,
    wordGap: TYPE.wordGap,
  });
  const padW = 30;
  add(
    '50-wordmark-black.svg',
    `<g transform="translate(${padW} ${padW + 200})"><path d="${wm.d}" fill="${PALETTE.ink}"/></g>`,
    wm.width + padW * 2,
    200 + padW * 2
  );
  add(
    '51-wordmark-white.svg',
    `<g transform="translate(${padW} ${padW + 200})"><path d="${wm.d}" fill="${PALETTE.white}"/></g>`,
    wm.width + padW * 2,
    200 + padW * 2
  );

  return out;
};

function symDoc(g, markOpts, fill, statusColor) {
  const pad = 0.085 * 400;
  const { body, w, h } = symbolBody(g, { ...markOpts, size: 400, fill, statusColor, pad });
  return { body, w, h };
}

function iconDoc(g, fill, statusColor) {
  const pad = 0.08 * 400;
  const { body, w, h } = symbolBody(g, { size: 400, fill, statusColor, pad });
  return { body, w, h };
}

function tileDoc(g, bg, fill, statusColor) {
  const S = 512;
  const inset = 0.185; // optical size of the mark inside the tile
  const { body, w, h } = symbolBody(g, {
    size: S * (1 - inset * 2),
    fill,
    statusColor,
    pad: 0,
  });
  void w;
  void h;
  const x = (S - S * (1 - inset * 2) * (shellBBox(g).w / shellBBox(g).h)) / 2;
  const y = S * inset;
  return {
    body:
      `<rect width="${S}" height="${S}" rx="${S * 0.22}" fill="${bg}"/>` +
      `<g transform="translate(${round(x)} ${round(y)})">${body}</g>`,
    w: S,
    h: S,
  };
}

void mkG;
