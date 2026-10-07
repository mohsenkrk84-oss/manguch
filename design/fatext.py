# -*- coding: utf-8 -*-
"""Persian text shaping engine: uharfbuzz (shaping) + freetype-py (raster) + PIL (composite).
Works with fonts that lack Arabic Presentation Forms (e.g. Hasti).

Shaping model (mini-bidi, no python-bidi — it drops U+200C):
1. Itemize text into directional runs: R (RTL incl. ZWNJ), L (Latin), D (digits),
   N (neutrals resolved by neighbours, else paragraph direction).
2. Mirror brackets inside R runs (bidi mirroring is not done by HarfBuzz).
3. Shape each run with its own direction (R->rtl, L/D->ltr).
4. Concatenate runs: reversed for RTL paragraph, in-order for LTR.
This keeps digit order (۱٬۷۹۹٬۰۰۰), ZWNJ joining, parens and mixed text correct.
"""
import uharfbuzz as hb
import freetype
from PIL import Image

_MIRROR = {0x28: 0x29, 0x29: 0x28, 0x5B: 0x5D, 0x5D: 0x5B, 0x7B: 0x7D, 0x7D: 0x7B,
           0xAB: 0xBB, 0xBB: 0xAB, 0x2039: 0x203A, 0x203A: 0x2039,
           0x3C: 0x3E, 0x3E: 0x3C}


def _char_class(c):
    o = ord(c)
    if "A" <= c <= "Z" or "a" <= c <= "z" or 0x00C0 <= o <= 0x02AF:
        return "L"
    if c.isdecimal() or o in (0x066C, 0x066B):
        return "D"
    if 0x0590 <= o <= 0x08FF or o in (0x200C, 0x200D):
        return "R"
    return "N"


def _itemize(text):
    n = len(text)
    if n == 0:
        return "L", []
    cls = [_char_class(c) for c in text]
    base = "L"
    for c in cls:
        if c in ("L", "R"):
            base = c
            break
    else:
        base = "R" if "R" in cls else "L"
    # resolve neutrals: between same class -> that class, else base direction
    res = list(cls)
    i = 0
    while i < n:
        if res[i] != "N":
            i += 1
            continue
        j = i
        while j < n and res[j] == "N":
            j += 1
        prev_c = res[i - 1] if i > 0 else None
        next_c = res[j] if j < n else None
        fill = prev_c if (prev_c == next_c and prev_c in ("L", "R", "D")) else base
        for k in range(i, j):
            res[k] = fill
        i = j
    # group maximal runs
    runs = []
    i = 0
    while i < n:
        j = i
        while j < n and res[j] == res[i]:
            j += 1
        runs.append((res[i], text[i:j]))
        i = j
    return base, runs


class FaFont:
    def __init__(self, path, size):
        self.path = path
        self.size = size
        with open(path, "rb") as f:
            data = f.read()
        self._blob = hb.Blob(data)
        self._face = hb.Face(self._blob)
        self._hbfont = hb.Font(self._face)
        self._hbfont.scale = (size * 64, size * 64)
        self.ft = freetype.Face(path)
        self.ft.set_pixel_sizes(0, size)
        self.asc = self.ft.size.ascender / 64.0
        self.desc = self.ft.size.descender / 64.0  # negative
        self.height = self.asc - self.desc

    def _shape_run(self, substr, direction, script, language):
        buf = hb.Buffer()
        buf.add_str(substr)
        buf.direction = direction
        buf.script = script
        buf.language = language
        hb.shape(self._hbfont, buf, {"kern": True, "liga": True})
        return [(info.codepoint, pos.x_offset / 64.0, pos.y_offset / 64.0,
                 pos.x_advance / 64.0)
                for info, pos in zip(buf.glyph_infos, buf.glyph_positions)]

    def shape(self, text):
        """Return (glyphs, width_px). glyphs = list of (gid, x_offset, y_offset, x_advance)."""
        if not text:
            return [], 0.0
        base, runs = _itemize(text)
        shaped_runs = []
        for dirc, substr in runs:
            if dirc == "R":
                glyphs = self._shape_run(substr.translate(_MIRROR), "rtl", "arab", "fa")
            elif dirc == "L":
                glyphs = self._shape_run(substr, "ltr", "latn", "en")
            else:  # digits: always LTR order
                if base == "R":
                    glyphs = self._shape_run(substr, "ltr", "arab", "fa")
                else:
                    glyphs = self._shape_run(substr, "ltr", "latn", "en")
            shaped_runs.append(glyphs)
        if base == "R":
            shaped_runs = shaped_runs[::-1]
        glyphs = [g for run in shaped_runs for g in run]
        width = sum(g[3] for g in glyphs)
        return glyphs, width

    def measure(self, text):
        _, w = self.shape(text)
        return w


def draw_fa(base_img, xy, text, font, fill, anchor="ra", shadow=None, line_spacing=1.45):
    """Draw (possibly multi-line) Persian text.

    anchor: horizontal l/m/r + vertical t/m/b, e.g. 'ra' right-top, 'mm' center.
    shadow: (color, dx, dy) or None.
    Returns total height drawn.
    """
    if not text:
        return 0
    ha, va = anchor[0], anchor[1]
    lines = text.split("\n")
    line_h = font.height * line_spacing
    total_h = line_h * (len(lines) - 1) + font.height
    x, y = xy
    if va == "m":
        y = y - total_h / 2
    elif va == "b":
        y = y - total_h

    for i, line in enumerate(lines):
        glyphs, w = font.shape(line)
        if ha == "m":
            lx = x - w / 2
        elif ha == "r":
            lx = x - w
        else:
            lx = x
        baseline = y + i * line_h + font.asc
        if shadow is not None:
            _draw_line(base_img, glyphs, lx + shadow[1], baseline + shadow[2], font, shadow[0])
        _draw_line(base_img, glyphs, lx, baseline, font, fill)
    return total_h


def _draw_line(base_img, glyphs, lx, baseline, font, fill):
    if len(fill) == 3:
        fill = fill + (255,)
    pen = lx
    ft = font.ft
    for gid, xoff, yoff, xadv in glyphs:
        if gid == 0:
            pen += xadv
            continue
        try:
            ft.load_glyph(gid, freetype.FT_LOAD_RENDER)
        except Exception:
            pen += xadv
            continue
        slot = ft.glyph
        bmp = slot.bitmap
        w, rows = bmp.width, bmp.rows
        if w and rows:
            buf = bytes(bmp.buffer)
            if len(buf) < w * rows:
                buf = buf + b"\x00" * (w * rows - len(buf))
            mask = Image.frombytes("L", (w, rows), buf[:w * rows])
            color = Image.new("RGBA", (w, rows), fill)
            gx = int(round(pen + xoff)) + slot.bitmap_left
            gy = int(round(baseline - yoff)) - slot.bitmap_top
            base_img.paste(color, (gx, gy), mask)
        pen += xadv


def text_width(text, font):
    return font.measure(text)
