# -*- coding: utf-8 -*-
"""Persian text shaping engine: uharfbuzz (shaping) + freetype-py (raster) + PIL (composite).
Works with fonts that lack Arabic Presentation Forms (e.g. Hasti).
"""
import uharfbuzz as hb
import freetype
from bidi.algorithm import get_display
from PIL import Image


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

    def shape(self, text):
        """Return (glyphs, width_px). glyphs = list of (gid, x_offset, y_offset, x_advance)."""
        visual = get_display(text)
        buf = hb.Buffer()
        buf.add_str(visual)
        buf.direction = "ltr"
        buf.script = "arab"
        buf.language = "fa"
        hb.shape(self._hbfont, buf, {"kern": True, "liga": True})
        glyphs = []
        for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
            glyphs.append((info.codepoint, pos.x_offset / 64.0, pos.y_offset / 64.0,
                            pos.x_advance / 64.0))
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
