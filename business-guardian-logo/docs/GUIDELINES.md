# BUSINESS GUARDIAN — Brand Guidelines (v1.0)

**Always watching. Always protecting.**

---

## 1. The mark

An owl that is also a shield. A monitoring eye that is also an owl's eye.
The identity is one drawn object, not an assembly of symbols.

**The four readings, in the order a viewer meets them**

1. **Owl** — two ear tufts, a saddle crown and a broad facial disc. Vigilance.
2. **Eye** — socket → monitoring ring → pupil gap → sensor core → status point.
   A focused sensor, continuously on.
3. **Beak / facial disc** — the guardline leaves each eye socket tangentially and
   converges to one point, drawing the owl's face in a single gesture.
4. **Shield** — the guardline's point is the shield tip; the emblem's walls and
   that single point make the hidden shield. Protective geometry, discovered.

The status point (the small accent dot) is the "I am watching right now" signal.
It is optional in monochrome work.

---

## 2. Files and when to use them

| Need | File |
| --- | --- |
| Website header, deck, document | `10-lockup-horizontal-primary.svg` |
| Dark header, hero, footer | `13-lockup-horizontal-reverse.svg` |
| Covers, badges, profile grids | `20-lockup-stacked-primary.svg` |
| Single-colour print, stamps, etching | `03-emblem-black.svg` / `04-emblem-white.svg` |
| Favicon, app icon, browser extension | `30-icon-primary.svg`, `40-app-tile.svg`, `favicon.ico` |
| Incident notifications, reports, email | `30-icon-primary.svg` (flat colour, no shadow) |
| Social avatar | `40-app-tile.svg` (square) or a circular crop of it |
| Wordmark on its own | `50-wordmark-black.svg` / `51-wordmark-white.svg` |

All files are vector, self-contained and font-free. SVG for anything on screen
or in print; PNG only where a raster is required.

---

## 3. Colour

| Swatch | Name | Hex | Role |
| --- | --- | --- | --- |
| ▉ | Guardian Navy | `#0B1B2B` | Primary mark, wordmark, primary text |
| ▉ | Deep Navy | `#081420` | Hero and footer surfaces |
| ▉ | Signal Teal | `#14BFD4` | The single accent — status point, focus states |
| ▉ | Teal Bright | `#38D6E6` | The accent on dark grounds |
| ▉ | Mist | `#F3F6F8` | Light neutral surface |
| ▉ | Slate | `#5B6B7C` | Secondary type, rules, interface detail |

**Do**

* Keep the mark to one colour plus, at most, the single accent dot.
* Use `#14BFD4` on light grounds and `#38D6E6` on dark grounds.
* Test every new placement first in pure black.

**Don't**

* Don't gradient, glow or tint the mark.
* Don't fill large areas with Signal Teal behind the mark.
* Don't re-colour the mark to match a third-party palette — use monochrome instead.

---

## 4. Typography

| Use | Face | Setting |
| --- | --- | --- |
| Wordmark | Outfit SemiBold, uppercase | tracking `0.155 em`, word gap `0.5 × cap height` |
| Interface, reports, alerts | Inter Regular / Medium | — |

The wordmark ships as **outlines** in every logo file. Use those files; do not
retype "BUSINESS GUARDIAN". If a live-text version is unavoidable, match the
tracking and word gap above and never stretch or condense it.

---

## 5. Clear space and minimum sizes

* **Clear space** — half the wordmark cap height on all four sides of any
  lockup or the symbol. No type, rule, image or edge enters it.
* **Minimum sizes**

| Asset | Minimum |
| --- | --- |
| Icon variant | 16 px (favicon, 1× displays) |
| Full-detail emblem | 48 px |
| Horizontal lockup | 90 px wide |
| Stacked lockup | 64 px wide |

Below 48 px use the **icon variant** (`30-*`): the fine monitoring ring, the
status point and the thin guardline are replaced by a bolder eye so the mark
survives at 16 px. Never scale down the full-detail emblem and expect the same
result.

---

## 6. Misuse

Never:

* stretch, squish, rotate or skew the mark or wordmark;
* change the tuft angle, eye proportions or shield taper;
* place the mark on a busy photo without a solid panel or clear space;
* outline, emboss, bevel, glow or drop-shadow the mark;
* add a second accent colour, gradient or metallic effect;
* put the symbol inside an additional frame, circle or shield;
* set the wordmark in another typeface, or in lowercase / title case;
* re-space the lockup — the symbol-to-wordmark gap is fixed at `0.62 × cap`.

---

## 7. Quick implementation

```html
<!-- favicons -->
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" type="image/svg+xml" href="/icon.svg">
<link rel="apple-touch-icon" href="/apple-touch-icon-180.png">
```

```html
<!-- dark site header, inline for currentColor control -->
<svg viewBox="0 0 1180 105" role="img" aria-label="Business Guardian">
  <!-- paste the contents of 13-lockup-horizontal-reverse.svg -->
</svg>
```

For single-colour contexts (email, stamps, laser engraving) use
`03-emblem-black.svg`; the mark degrades to a clean silhouette with no loss of
recognition.
