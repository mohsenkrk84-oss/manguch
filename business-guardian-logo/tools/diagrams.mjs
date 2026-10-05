/**
 * Explanatory diagrams:
 *   60-construction.svg     the grid the emblem is built on
 *   61..63-concept-*.svg    the three readings: owl / eye / shield
 *   70-clearspace.svg       clear space + minimum size rules
 */
import { BASE, ICON, emblemParts, shellPath, shellSegments, shellBBox, eyeOf, circle } from './emblem.mjs';
import { PALETTE, TYPE, symbolBody, lockupHorizontal } from './brand.mjs';
import { wordmark } from './wordmark.mjs';


const r2 = (v) => Number(v.toFixed(2));
const attr = (o) => Object.entries(o).map(([k, v]) => `${k}="${v}"`).join(' ');

/** A canonical modern shield: flat shoulders, near-vertical walls, single point. */
function shieldPolygon(g) {
  const [Sx, Sy] = g.sideMax;
  const [Lx, Ly] = g.sideLow;
  const [Ax, Ay] = g.apex;
  const top = Sy - 66;
  const m = (v) => g.W - v;
  return `M ${Sx + 18} ${r2(top)} Q ${Sx} ${r2(top)} ${Sx} ${r2(top + 36)}
    L ${Lx} ${Ly} Q ${Lx + 6} ${Ly + 44} ${g.cx} ${Ay}
    Q ${m(Lx + 6)} ${Ly + 44} ${m(Lx)} ${Ly}
    L ${m(Sx)} ${r2(top + 36)} Q ${m(Sx)} ${r2(top)} ${m(Sx + 18)} ${r2(top)}
    L ${m(Sx + 46)} ${r2(top)} L ${Sx + 46} ${r2(top)} Z`;
}

function wrapDoc(body, w, h, extra = '', bg = '#FFFFFF', docW = null) {
  const W = docW || w;
  const shift = (W - w) / 2;
  const H = Math.max(h, W * 0.62);
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" fill="none">
${extra}<rect width="${W}" height="${H}" fill="${bg}"/><g transform="translate(${r2(shift)} 0)">${body}</g></svg>`;
}

function constructionCss() {
  return `<style>.lbl{font-family:Inter;font-size:16px;fill:${PALETTE.slate};letter-spacing:.02em}</style>`;
}
const guides = { stroke: PALETTE.teal, 'stroke-width': 1.6, fill: 'none' };
const soft = { stroke: '#B9C6D2', 'stroke-width': 1.2, fill: 'none', 'stroke-dasharray': '7 8' };

/* ------------------------------------------------------------------ */
/* Construction grid                                                   */
/* ------------------------------------------------------------------ */

export function construction({ size = 900, showLabels = true } = {}) {
  const f = constructionFigure({ labels: showLabels });
  const pad = Math.round(size * 0.08);
  const k = (size - pad * 2) / f.w;
  const body = `<g transform="translate(${pad} ${pad}) scale(${k})">${f.body}</g>`;
  return wrapDoc(body, size, size, constructionCss(), '#FFFFFF');
}

/* ------------------------------------------------------------------ */
/* Figures (reusable in other layouts)                                 */
/* ------------------------------------------------------------------ */

/** Construction grid figure, in emblem units. */
export function constructionFigure({ labels = false } = {}) {
  const g = BASE;
  const p = emblemParts(g, {});
  const softLine = { stroke: '#B9C6D2', 'stroke-width': 1.2, fill: 'none', 'stroke-dasharray': '7 8' };
  const teal = { stroke: PALETTE.teal, 'stroke-width': 1.6, fill: 'none' };
  const body = `
    <g opacity="0.28"><mask id="cfg" maskUnits="userSpaceOnUse" x="0" y="0" width="${g.W}" height="${g.W}">
      <path d="${p.shell}" fill="#fff"/><path d="${p.holes}" fill="#000" fill-rule="evenodd"/></mask>
      <g mask="url(#cfg)"><rect width="${g.W}" height="${g.W}" fill="${PALETTE.navy}"/>
      <path d="${p.pupils}" fill="${PALETTE.navy}"/></g></g>
    <line x1="${g.cx}" y1="24" x2="${g.cx}" y2="${g.W - 24}" ${attr(softLine)}/>
    <line x1="24" y1="${g.ey}" x2="${g.W - 24}" y2="${g.ey}" ${attr(softLine)}/>
    <line x1="24" y1="${g.sideMax[1]}" x2="${g.W - 24}" y2="${g.sideMax[1]}" ${attr(softLine)}/>
    <path d="${shellPath(g)}" ${attr(teal)}/>
    ${[-1, 1]
      .map((s) => {
        const [cx, cy] = eyeOf(g, s);
        return [g.rSocket, g.rRing, g.rGap, g.rPupil]
          .map((r) => `<circle cx="${cx}" cy="${cy}" r="${r}" ${attr(teal)}/>`)
          .join('');
      })
      .join('')}
    ${[g.apex, eyeOf(g, -1), eyeOf(g, 1), g.ear, [g.W - g.ear[0], g.ear[1]]]
      .map((pt) => `<circle cx="${pt[0]}" cy="${pt[1]}" r="4.5" fill="${PALETTE.teal}"/>`)
      .join('')}
    ${labels ? constructionLabels(g) : ''}`;
  return { body, w: g.W, h: g.W };
}

function constructionLabels(g) {
  const X = (v) => r2(v);
  const Y = (v) => r2(v);
  return `<text x="${X(g.cx + 10)}" y="${Y(g.ey + 138)}" class="lbl">eye centre line — radii ${g.rSocket} / ${g.rRing} / ${g.rGap} / ${g.rPupil}</text>
  <text x="${X(g.W - 6)}" y="${Y(g.apex[1] - 26)}" text-anchor="end" class="lbl">single point — shield tip</text>
  <text x="${X(g.W - 6)}" y="${Y(g.ear[1] + 18)}" text-anchor="end" class="lbl">ear tuft ${Math.round(
    (Math.atan2(g.notch[0] - g.ear[0], g.notch[1] - g.ear[1]) * 180) / Math.PI
  )}° out from vertical</text>`;
}

/** Concept figure (owl / eye / shield), in emblem units. */
export function conceptFigure(mode) {
  const g = BASE;
  const p = emblemParts(g, { status: 1 });
  const dim = `<g opacity="0.14"><mask id="dm" maskUnits="userSpaceOnUse" x="0" y="0" width="${g.W}" height="${g.W}">
      <path d="${p.shell}" fill="#fff"/><path d="${p.holes}" fill="#000" fill-rule="evenodd"/></mask>
      <g mask="url(#dm)"><rect width="${g.W}" height="${g.W}" fill="${PALETTE.navy}"/><path d="${p.pupils}" fill="${PALETTE.navy}"/></g>
      <path d="${p.shell}" fill="none" stroke="${PALETTE.navy}" stroke-width="2.6"/></g>`;
  const eyeMask = [-1, 1].map((s) => circle(...eyeOf(g, s), g.rSocket + 6)).join(' ');
  let focus = '';
  if (mode === 'owl') {
    focus = `<mask id="fm" maskUnits="userSpaceOnUse" x="0" y="0" width="${g.W}" height="${g.W}">
      <path d="${p.shell}" fill="#fff"/><path d="${p.holes}" fill="#000" fill-rule="evenodd"/></mask>
      <g mask="url(#fm)"><rect width="${g.W}" height="${g.W}" fill="${PALETTE.navy}"/><path d="${p.pupils}" fill="${PALETTE.navy}"/></g>
      <path d="${p.voids}" fill="#fff"/>`;
  } else if (mode === 'eye') {
    focus = `<g opacity="0.1"><g mask="url(#fm2)"><rect width="${g.W}" height="${g.W}" fill="${PALETTE.navy}"/></g></g>
      <clipPath id="eyeclip"><path d="${eyeMask}" fill-rule="evenodd"/></clipPath>
      <g clip-path="url(#eyeclip)"><g mask="url(#fm2)"><rect width="${g.W}" height="${g.W}" fill="${PALETTE.navy}"/><path d="${p.pupils}" fill="${PALETTE.navy}"/></g>
      <path d="${p.voids}" fill="#fff"/></g>
      <mask id="fm2" maskUnits="userSpaceOnUse" x="0" y="0" width="${g.W}" height="${g.W}">
        <path d="${p.shell}" fill="#fff"/><path d="${p.holes}" fill="#000" fill-rule="evenodd"/></mask>`;
  } else {
    const sg = shieldPolygon(g);
    focus = `<g opacity="0.1"><g mask="url(#fm3)"><rect width="${g.W}" height="${g.W}" fill="${PALETTE.navy}"/></g></g>
      <clipPath id="shieldclip"><path d="${sg}"/></clipPath>
      <g clip-path="url(#shieldclip)"><g mask="url(#fm3)"><rect width="${g.W}" height="${g.W}" fill="${PALETTE.navy}"/><path d="${p.pupils}" fill="${PALETTE.navy}"/></g>
      <path d="${p.voids}" fill="#fff" opacity="0.9"/></g>
      <path d="${sg}" fill="none" stroke="${PALETTE.teal}" stroke-width="3.4" stroke-dasharray="13 10"/>
      <mask id="fm3" maskUnits="userSpaceOnUse" x="0" y="0" width="${g.W}" height="${g.W}">
        <path d="${p.shell}" fill="#fff"/><path d="${p.holes}" fill="#000" fill-rule="evenodd"/></mask>`;
  }
  return { body: `${dim}${focus}`, w: g.W, h: g.W };
}

/* ------------------------------------------------------------------ */
/* Concepts: owl / eye / shield                                        */
/* ------------------------------------------------------------------ */

/** One emblem with a specific element isolated. mode: 'owl' | 'eye' | 'shield'. */
export function concept(mode, { size = 900, label = '' } = {}) {
  const f = conceptFigure(mode);
  const pad = Math.round(size * 0.09);
  const k = (size - pad * 2) / f.w;
  const caption = label
    ? `<text x="${size / 2}" y="${size - 30}" text-anchor="middle" style="font-family:Inter;font-size:22px;letter-spacing:.14em;fill:${PALETTE.slate}">${label}</text>`
    : '';
  const body = `<g transform="translate(${pad} ${pad}) scale(${k})">${f.body}</g>${caption}`;
  return wrapDoc(body, size, size, constructionCss(), '#FFFFFF');
}

/* ------------------------------------------------------------------ */
/* Clear space + minimum size                                          */
/* ------------------------------------------------------------------ */

export function clearspace() {
  const cap = 74;
  const l = lockupHorizontal({ cap, fill: PALETTE.navy, statusColor: PALETTE.teal, padRatio: 0 });
  const x = cap / 2; // clear space = half the cap height
  const s = Math.min(1.6, 1180 / l.w);
  const y0 = 170;
  const wm = wordmark(['BUSINESS', 'GUARDIAN'], {
    family: TYPE.family,
    weight: TYPE.weight,
    size: 40,
    tracking: 40 * TYPE.trackingRatio,
    wordGap: TYPE.wordGap,
  });
  const small = ['30-icon-primary.svg'].length ? 0 : 0;
  void small;

  const body = `
  <text x="110" y="110" class="note">Clear space — half the wordmark cap height on all four sides. Nothing enters this zone.</text>
  <g transform="translate(150 ${y0})">
    <g transform="scale(${s})">
      <rect x="${-x}" y="${-x}" width="${l.w + x * 2}" height="${l.h + x * 2}" fill="#FBFCFD" stroke="${PALETTE.teal}" stroke-width="${1.4 / s}" stroke-dasharray="10 8"/>
      <rect x="0" y="0" width="${l.w}" height="${l.h}" fill="none" stroke="#C9D4DE" stroke-width="${1 / s}" stroke-dasharray="4 5"/>
      <g>${l.body}</g>
    </g>
    <text x="${l.w * s}" y="${l.h * s + 74}" text-anchor="end" class="note">LOCKUP BOX: ${Math.round(l.w * s)} × ${Math.round(l.h * s)} PX · DASHED LINE = CLEAR SPACE BOUNDARY</text>
  </g>

  <line x1="110" y1="${y0 + l.h * s + 110}" x2="1390" y2="${y0 + l.h * s + 110}" stroke="#E4EAEF"/>
  <text x="110" y="${y0 + l.h * s + 156}" class="note">Minimum sizes</text>
  <text x="110" y="${y0 + l.h * s + 182}" class="micro">ICON VARIANT FROM 16PX · FULL EMBLEM FROM 48PX · LOCKUP FROM 90PX WIDE</text>
  ${[16, 24, 32, 48, 64].map((size, i) => {
    const b = symbolBody(i < 3 ? ICON : BASE, { size, fill: PALETTE.navy, pad: 0, opts: { status: 1 } });
    const px = 110 + i * 96;
    const py = y0 + l.h * s + 224;
    return `<g><g transform="translate(${px} ${py})">${b.body}</g>
      <text x="${px}" y="${py + size + 34}" class="micro">${size}px</text></g>`;
  }).join('')}
  <g transform="translate(700 ${y0 + l.h * s + 224})">
    <g transform="scale(0.62)"><path d="${wm.d}" fill="${PALETTE.navy}"/></g>
    <text x="0" y="42" class="micro">WORDMARK — NEVER SET IN ANOTHER TYPEFACE</text>
  </g>`;

  const H = Math.round(y0 + l.h * s + 400);
  return `<svg xmlns="http://www.w3.org/2000/svg" width="1500" height="${H}" viewBox="0 0 1500 ${H}" fill="none"><style>
    .note{font-family:Inter;font-size:19px;fill:${PALETTE.slate}}
    .micro{font-family:Inter;font-size:15px;fill:#93A2B0;letter-spacing:.08em}
  </style><rect width="1500" height="${H}" fill="#FFFFFF"/>${body}</svg>`;
}

function iconMini(size) {
  const { body } = symbolBody(ICON, { size, fill: PALETTE.navy, statusColor: null, pad: 0 });
  return body;
}
