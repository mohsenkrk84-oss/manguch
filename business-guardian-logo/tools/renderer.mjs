/**
 * PNG renderer for the build (resvg-js). Only needed to regenerate raster
 * exports — the delivered SVGs never depend on it.
 */
import { mkdirSync, writeFileSync } from 'node:fs';
import { dirname } from 'node:path';
import { MODULES, fontPath } from './deps.mjs';

const { Resvg } = await import(`${MODULES}@resvg/resvg-js/index.js`);

const FONT_FILES = [
  fontPath('inter', 400),
  fontPath('inter', 500),
  fontPath('inter', 600),
  fontPath('outfit', 500),
  fontPath('outfit', 600),
  fontPath('outfit', 700),
].filter(Boolean);

export function render(svg, out, { width } = {}) {
  const r = new Resvg(svg, {
    fitTo: width ? { mode: 'width', value: width } : { mode: 'original' },
    font: { loadSystemFonts: false, defaultFontFamily: 'Inter', fontFiles: FONT_FILES },
  });
  mkdirSync(dirname(out), { recursive: true });
  writeFileSync(out, r.render().asPng());
  return out;
}

export function renderBuf(svg, width) {
  return Buffer.from(
    new Resvg(svg, {
      fitTo: { mode: 'width', value: width },
      font: { loadSystemFonts: false, defaultFontFamily: 'Inter', fontFiles: FONT_FILES },
    })
      .render()
      .asPng()
  );
}