/**
 * BUSINESS GUARDIAN — wordmark engine
 * ------------------------------------
 * The wordmark is set in a geometric sans and delivered as true outlines, so
 * no font file is needed to display the logo. Three deliberate refinements
 * make it read as a custom logotype rather than raw type:
 *
 *   1. cap-height setting — every mark is positioned by cap height, not em
 *      size, so optical sizes stay consistent across lockups;
 *   2. optical tracking   — uppercase is letterspaced and the trailing space
 *      is trimmed, so the wordmark's right edge is exactly flush;
 *   3. optical word gap   — the space between the two words is a ratio of the
 *      cap height instead of the font's default space glyph;
 *
 * The delivered wordmark is pure outline data: pixel-identical everywhere, no
 * font installation, no webfont request.
 */
import { readFileSync } from 'node:fs';
import { MODULES, fontPath } from './deps.mjs';

const ot = await import(`${MODULES}opentype.js/dist/opentype.mjs`);

const opentype = ot.default ?? ot;

const NAMES = {
  100: 'Thin',
  200: 'ExtraLight',
  300: 'Light',
  400: 'Regular',
  500: 'Medium',
  600: 'SemiBold',
  700: 'Bold',
  800: 'ExtraBold',
  900: 'Black',
};

export const fontFile = fontPath;

const cache = new Map();
export function loadFont(family, weight) {
  const key = `${family}-${weight}`;
  if (!cache.has(key)) {
    const buf = readFileSync(fontFile(family, weight));
    cache.set(key, opentype.parse(buf.buffer.slice(buf.byteOffset, buf.byteOffset + buf.byteLength)));
  }
  return cache.get(key);
}

/** Cap height in font units. */
export function capHeight(font) {
  const os2 = font.tables.os2 || {};
  if (os2.sCapHeight) return os2.sCapHeight;
  return font.getPath('H', 0, 0, 1000).getBoundingBox().y2;
}

/** Metrics for setting type by cap height instead of em size. */
export function metrics(family, weight, capSize) {
  const font = loadFont(family, weight);
  const upm = font.unitsPerEm;
  const cap = capHeight(font);
  const fontSize = (capSize * upm) / cap; // em size that yields the wanted cap
  const px = (units) => (units * fontSize) / upm;
  return { font, upm, cap, capSize, fontSize, px };
}

/**
 * The BUSINESS GUARDIAN wordmark: uppercase, tracked, with an optical word gap.
 * `size` is the CAP HEIGHT in px. Returns outline path data plus the exact
 * inked width so lockups can be aligned flush.
 *
 */
export function wordmark(
  words = ['BUSINESS', 'GUARDIAN'],
  {
    family = 'outfit',
    weight = 600,
    size = 100,
    tracking = 9,
    wordGap = 0.42,
    x = 0,
    y = 0,
  } = {}
) {
  const { font, px } = metrics(family, weight, size);
  let cursor = x;
  const parts = [];
  words.forEach((word, wi) => {
    for (const ch of word) {
      const glyph = font.charToGlyph(ch);
      parts.push(glyph.getPath(cursor, y, px(font.unitsPerEm)).toPathData(2));
      cursor += px(glyph.advanceWidth) + tracking;
    }
    cursor -= tracking;
    if (wi < words.length - 1) cursor += size * wordGap + tracking;
  });
  return { d: parts.join(' '), width: cursor - x, capHeight: size };
}
