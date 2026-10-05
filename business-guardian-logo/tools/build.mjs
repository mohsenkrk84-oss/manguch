/**
 * Build all brand assets:
 *   svg/   self-contained vector files (the masters)
 *   png/   rendered raster exports at fixed sizes
 *   favicon.ico
 *
 * Run: node business-guardian-logo/tools/build.mjs
 */
import { writeFileSync, mkdirSync, existsSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { FILES, PALETTE } from './brand.mjs';

const ROOT = new URL('..', import.meta.url).pathname; // business-guardian-logo/
const SVG = join(ROOT, 'svg');
const PNG = join(ROOT, 'png');
mkdirSync(SVG, { recursive: true });
mkdirSync(PNG, { recursive: true });

const files = FILES();
for (const f of files) {
  writeFileSync(join(SVG, f.name), f.svg);
}
console.log(`svg: ${files.length} files`);

/* ---------------- raster exports ---------------- */
let render = null;
let renderBuf = null;
try {
  ({ render, renderBuf } = await import('./renderer.mjs'));
} catch (err) {
  console.warn('PNG export skipped:', err.message);
}
void existsSync;

function svgOf(name) {
  return files.find((f) => f.name === name)?.svg;
}

function pngFrom(name, out, width, { background } = {}) {
  let svg = svgOf(name);
  if (!svg) throw new Error(`missing ${name}`);
  if (background) svg = injectBg(svg, background);
  render(svg, join(PNG, out), { width });
}

function injectBg(svg, color) {
  return svg.replace(/(<svg[^>]*>)/, `$1<rect width="100%" height="100%" fill="${color}"/>`);
}

if (render) {
  /* emblems */
  for (const w of [128, 256, 512, 1024]) pngFrom('01-emblem-primary.svg', `emblem-primary-${w}.png`, w);
  for (const w of [256, 1024]) {
    pngFrom('02-emblem-navy.svg', `emblem-navy-${w}.png`, w);
    pngFrom('03-emblem-black.svg', `emblem-black-${w}.png`, w);
    pngFrom('04-emblem-white.svg', `emblem-white-${w}.png`, w, { background: PALETTE.navy });
    pngFrom('05-emblem-reverse.svg', `emblem-reverse-${w}.png`, w, { background: PALETTE.navy });
  }

  /* lockups */
  pngFrom('10-lockup-horizontal-primary.svg', 'lockup-horizontal-primary-1600.png', 1600);
  pngFrom('13-lockup-horizontal-reverse.svg', 'lockup-horizontal-reverse-1600.png', 1600, {
    background: PALETTE.navy,
  });
  pngFrom('11-lockup-horizontal-black.svg', 'lockup-horizontal-black-1600.png', 1600);
  pngFrom('20-lockup-stacked-primary.svg', 'lockup-stacked-primary-1200.png', 1200);
  pngFrom('23-lockup-stacked-reverse.svg', 'lockup-stacked-reverse-1200.png', 1200, {
    background: PALETTE.navy,
  });

  /* icons + favicons */
  for (const w of [16, 24, 32, 48, 64, 128, 256]) {
    pngFrom('30-icon-primary.svg', `icon-navy-${w}.png`, w);
  }
  for (const w of [16, 24, 32, 48]) {
    pngFrom('31-icon-black.svg', `icon-black-${w}.png`, w);
    pngFrom('32-icon-white.svg', `icon-white-${w}.png`, w, { background: PALETTE.navy });
  }
  pngFrom('40-app-tile.svg', 'app-tile-512.png', 512);
  pngFrom('40-app-tile.svg', 'apple-touch-icon-180.png', 180);
  pngFrom('40-app-tile.svg', 'social-avatar-1024.png', 1024);
  pngFrom('41-app-tile-light.svg', 'app-tile-light-512.png', 512);

  /* wordmark */
  pngFrom('50-wordmark-black.svg', 'wordmark-black-1600.png', 1600);
  pngFrom('51-wordmark-white.svg', 'wordmark-white-1600.png', 1600, { background: PALETTE.navy });

  console.log(`png: exported`);
}

writeFileSync(join(ROOT, 'i-made-this.txt'), 'placeholder\n');
console.log('done');
void dirname;

/* ---------------- diagrams, sheets, guidelines ---------------- */
if (render) {
  const { construction, concept, clearspace } = await import('./diagrams.mjs');
  const { brandSheet } = await import('./sheet.mjs');
  const { applications } = await import('./applications.mjs');
  mkdirSync(join(ROOT, 'docs'), { recursive: true });

  const safe = (svg) => svg.replace(/&(?!(amp|lt|gt|quot|apos|#\d+|#x[0-9a-fA-F]+);)/g, '&amp;');
  const extra = {
    '60-construction.svg': construction({ showLabels: true }),
    '61-concept-owl.svg': concept('owl', { label: 'OWL — VIGILANCE' }),
    '62-concept-eye.svg': concept('eye', { label: 'EYE — MONITORING' }),
    '63-concept-shield.svg': concept('shield', { label: 'SHIELD — PROTECTION' }),
    '70-clearspace.svg': clearspace(),
    '80-brand-sheet.svg': safe(brandSheet()),
    '90-applications.svg': safe(applications()),
  };
  for (const [name, svg] of Object.entries(extra)) writeFileSync(join(SVG, name), svg);

  render(extra['80-brand-sheet.svg'], join(ROOT, 'docs', 'brand-sheet.png'), { width: 2000 });
  render(extra['90-applications.svg'], join(ROOT, 'docs', 'applications.png'), { width: 1800 });
  render(extra['60-construction.svg'], join(ROOT, 'docs', 'construction.png'), { width: 1400 });
  for (const k of ['61-concept-owl', '62-concept-eye', '63-concept-shield', '70-clearspace']) {
    render(extra[`${k}.svg`], join(ROOT, 'docs', `${k}.png`), { width: 1000 });
  }
  console.log('svg: diagrams + docs rendered');
}

/* ---------------- app icon + scale test sheets ---------------- */
if (render) {
  const { ICON, BASE } = await import('./emblem.mjs');
  const { symbolBody, PALETTE } = await import('./brand.mjs');
  const { writeFileSync: wf } = await import('node:fs');

  /* icon scale test */
  let row1 = '';
  let row2 = '';
  [16, 24, 32, 48, 64, 96, 128].forEach((size, i) => {
    const b = symbolBody(ICON, { size, fill: PALETTE.navy, pad: 0 });
    row1 += `<g transform="translate(${40 + i * 130} ${120 - size / 2})">${b.body}</g>
      <text x="${40 + i * 130}" y="152" class="m">${size}px</text>`;
  });
  [48, 64, 96, 128, 192].forEach((size, i) => {
    const b = symbolBody(BASE, { size, fill: PALETTE.navy, statusColor: PALETTE.teal, pad: 0 });
    row2 += `<g transform="translate(${40 + i * 180} ${360 - size / 2})">${b.body}</g>
      <text x="${40 + i * 180}" y="392" class="m">${size}px</text>`;
  });
  const scaleSvg = `<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="440"><style>
    .t{font-family:Inter;font-size:17px;fill:${PALETTE.navy};letter-spacing:.08em}
    .m{font-family:Inter;font-size:14px;fill:#93A2B0}</style>
    <rect width="1000" height="440" fill="#FFFFFF"/>
    <text x="40" y="70" class="t">ICON VARIANT — FAVICON / APP ICON</text>${row1}
    <text x="40" y="240" class="t">FULL-DETAIL VARIANT — WITH STATUS POINT</text>${row2}</svg>`;
  render(scaleSvg, join(ROOT, 'docs', 'scale-test.png'), { width: 1000 });

  /* app tile sheet */
  const tile = (bg, fill, status) => {
    const inner = 512 * (1 - 0.185 * 2);
    const b = symbolBody(ICON, { size: inner, fill, statusColor: status, pad: 0 });
    return `<rect width="512" height="512" rx="112" fill="${bg}"/>
      <g transform="translate(${(512 - b.w) / 2} ${(512 - b.h) / 2})">${b.body}</g>`;
  };
  const navy = tile(PALETTE.navy, '#FFFFFF', PALETTE.tealBright);
  const light = tile('#FFFFFF', PALETTE.navy, PALETTE.teal);
  const put = (innerBody, size, x, y) =>
    `<g transform="translate(${x} ${y})"><svg width="${size}" height="${size}" viewBox="0 0 512 512">${innerBody}</svg>
     <text x="0" y="${size + 28}" class="m">${size}px</text></g>`;
  let x = 40;
  let cellTop = '';
  [512, 256, 180, 128, 96, 64].forEach((size) => {
    cellTop += put(navy, size, x, 60);
    x += size + 34;
  });
  let x2 = 40;
  let cellBottom = '';
  [180, 128, 64, 48].forEach((size) => {
    cellBottom += put(light, size, x2, 60 + 512 + 90);
    x2 += size + 40;
  });
  const tileW = 40 + 512 + 40 + 256 + 180 + 128 + 96 + 34 * 5 + 60;
  const tileH = 60 + 512 + 90 + 260;
  const tileSvg = `<svg xmlns="http://www.w3.org/2000/svg" width="${tileW}" height="${tileH}"><style>
    .h{font-family:Inter;font-size:17px;fill:${PALETTE.navy};letter-spacing:.08em}
    .m{font-family:Inter;font-size:14px;fill:#93A2B0}</style>
    <rect width="${tileW}" height="${tileH}" fill="#FFFFFF"/>
    <text x="40" y="40" class="h">APP TILE — NAVY (iOS / ANDROID / PWA)</text>${cellTop}
    <text x="40" y="${60 + 512 + 70}" class="h">APP TILE — LIGHT</text>${cellBottom}</svg>`;
  render(tileSvg, join(ROOT, 'docs', 'app-icons.png'), { width: tileW });
  wf(join(SVG, '91-app-icons.svg'), tileSvg);
  console.log('docs: scale + app icon sheets rendered');
}

/* ---------------- favicon.ico ---------------- */
if (render) {
  const { writeIco } = await import('./ico.mjs');
  if (!renderBuf) throw new Error('renderBuf unavailable');
  const iconSvg = svgOf('30-icon-primary.svg');
  const frames = [16, 24, 32, 48, 64].map((s) => ({ size: s, png: renderBuf(iconSvg, s) }));
  writeIco(frames, join(ROOT, 'favicon.ico'));
  console.log('favicon.ico written');
}
