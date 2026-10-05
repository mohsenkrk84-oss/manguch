/**
 * Dependency resolution for the build tools.
 *
 * The delivered SVG files are completely self-contained (the wordmark is
 * outlines, not live text), so nothing here is needed to *use* the logo —
 * only to regenerate it. Dependencies are looked up in this order:
 *
 *   1. ../node_modules            (npm install inside business-guardian-logo)
 *   2. a shared tool checkout     (development convenience)
 */
import { existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';

const here = (p) => fileURLToPath(new URL(p, import.meta.url));

const CANDIDATES = [here('../node_modules/'), '/home/user/.tools/svgtool/node_modules/'];

export const MODULES = CANDIDATES.find((p) => existsSync(p)) || CANDIDATES[0];
export const FONTS = `${MODULES}@expo-google-fonts/`;

/** Absolute path to a bundled font, e.g. fontPath('outfit', 600) */
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

export function fontPath(family, weight) {
  const cap = family[0].toUpperCase() + family.slice(1);
  const dir = `${weight}${NAMES[weight]}`;
  return `${FONTS}${family}/${dir}/${cap}_${weight}${NAMES[weight]}.ttf`;
}

/** Import a build-time dependency from whichever checkout has it. */
export async function dep(name) {
  const local = `${MODULES}${name}`;
  const target = existsSync(local) ? local : name;
  return import(/* @vite-ignore */ `${target}/`);
}
