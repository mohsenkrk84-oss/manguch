#!/usr/bin/env python3
"""Render forensic-log 2D vector animation to a looping GIF."""
from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw

OUT = Path("/home/user/manguch/forensic-log-animation.gif")
TMP = Path("/tmp/forensic-frames")
TMP.mkdir(parents=True, exist_ok=True)

# Output is 9:16. Draw at 2x then downscale for clean edges.
OW, OH = 432, 774
SCALE = 2
W, H = OW * SCALE, OH * SCALE
SX = W / 768.0
SY = H / 1376.0

CHAR = (30, 30, 28)
YELLOW = (235, 184, 39)
WHITE = (255, 255, 255)
DURATION = 8.0
FPS = 12
NFRAMES = int(DURATION * FPS)


def lerp(a, b, t):
    return a + (b - a) * t


def clamp(t, a=0.0, b=1.0):
    return max(a, min(b, t))


def ease_in_out(t):
    t = clamp(t)
    return t * t * (3 - 2 * t)


def cubic_bezier_approx(t):
    # smooth ease similar to cubic-bezier(0.45, 0.05, 0.25, 1)
    t = clamp(t)
    return 1 - (1 - t) ** 3


def bounce_scale(t):
    """t 0..1 over the pop window. returns scale."""
    t = clamp(t)
    if t <= 0:
        return 0.0
    if t < 0.55:
        u = t / 0.55
        return 1.12 * (1 - (1 - u) ** 3)
    if t < 0.78:
        u = (t - 0.55) / 0.23
        return lerp(1.12, 0.96, ease_in_out(u))
    u = (t - 0.78) / 0.22
    return lerp(0.96, 1.0, ease_in_out(u))


def local_t(now, start, end):
    if end <= start:
        return 0.0
    return clamp((now - start) / (end - start))


def xform(x, y):
    return x * SX, y * SY


def sw(w):
    return max(1, int(round(w * SX)))


def dashed_line(draw, x1, y1, x2, y2, dash=16, gap=11, width=4.4, offset=0, fill=CHAR):
    x1, y1 = xform(x1, y1)
    x2, y2 = xform(x2, y2)
    dx, dy = x2 - x1, y2 - y1
    length = math.hypot(dx, dy) or 1
    ux, uy = dx / length, dy / length
    dash_p = dash * SX
    gap_p = gap * SX
    period = dash_p + gap_p
    pos = -((offset * SX) % period)
    w = sw(width)
    while pos < length:
        a = max(pos, 0)
        b = min(pos + dash_p, length)
        if b > a:
            draw.line(
                [(x1 + ux * a, y1 + uy * a), (x1 + ux * b, y1 + uy * b)],
                fill=fill,
                width=w,
            )
        pos += period
    # round caps on visible ends
    r = max(1, w // 2)
    draw.ellipse([x1 - r, y1 - r, x1 + r, y1 + r], fill=fill)
    draw.ellipse([x2 - r, y2 - r, x2 + r, y2 + r], fill=fill)


def solid_line(draw, x1, y1, x2, y2, width=4, fill=CHAR):
    p1 = xform(x1, y1)
    p2 = xform(x2, y2)
    w = sw(width)
    draw.line([p1, p2], fill=fill, width=w)
    r = max(1, w // 2)
    for x, y in (p1, p2):
        draw.ellipse([x - r, y - r, x + r, y + r], fill=fill)


def circle(draw, cx, cy, r, fill=None, outline=None, width=4):
    x, y = xform(cx, cy)
    rr = r * SX
    bbox = [x - rr, y - rr, x + rr, y + rr]
    w = sw(width)
    if fill and outline:
        draw.ellipse(bbox, fill=fill, outline=outline, width=w)
    elif fill:
        draw.ellipse(bbox, fill=fill)
    else:
        draw.ellipse(bbox, outline=outline, width=w)


def rounded_rect(draw, x, y, w, h, rx, fill=None, outline=None, width=3.4):
    x1, y1 = xform(x, y)
    x2, y2 = xform(x + w, y + h)
    rad = int(rx * SX)
    kw = {}
    if fill:
        kw["fill"] = fill
    if outline:
        kw["outline"] = outline
        kw["width"] = sw(width)
    draw.rounded_rectangle([x1, y1, x2, y2], radius=rad, **kw)


def polygon(draw, pts, fill=None, outline=None, width=3.2):
    mapped = [xform(x, y) for x, y in pts]
    w = sw(width)
    if fill:
        draw.polygon(mapped, fill=fill)
    if outline:
        draw.line(mapped + [mapped[0]], fill=outline, width=w)
        r = max(1, w // 2)
        for x, y in mapped:
            draw.ellipse([x - r, y - r, x + r, y + r], fill=outline)


def draw_scene(now: float) -> Image.Image:
    img = Image.new("RGB", (W, H), WHITE)
    draw = ImageDraw.Draw(img)

    # --- log dash offset (ticks during first 28%) ---
    if now < 2.24:
        dash_off = (now / 2.24) * 54
    elif now < 7.2:
        dash_off = 54
    else:
        dash_off = 54 * (1 - local_t(now, 7.2, 8.0))

    highlight_op = 0.55
    if 1.76 <= now <= 7.2:
        highlight_op = lerp(0.55, 1.0, ease_in_out(local_t(now, 1.76, 2.4)))
    elif now > 7.2:
        highlight_op = lerp(1.0, 0.55, local_t(now, 7.68, 8.0))

    # yellow highlight
    hy = Image.new("RGB", (W, H), WHITE)
    hd = ImageDraw.Draw(hy)
    rounded_rect(hd, 46, 708, 348, 58, 14, fill=YELLOW)
    img = Image.blend(img, hy, highlight_op)
    draw = ImageDraw.Draw(img)

    logs = [
        (58, 548, 372, 548),
        (58, 612, 428, 612),
        (58, 676, 396, 676),
        (58, 737, 430, 737),
        (58, 800, 414, 800),
        (58, 864, 384, 864),
        (58, 928, 336, 928),
    ]
    for x1, y1, x2, y2 in logs:
        dashed_line(draw, x1, y1, x2, y2, offset=dash_off)

    # X mark
    solid_line(draw, 78, 725, 108, 749, width=5.2)
    solid_line(draw, 108, 725, 78, 749, width=5.2)

    # connector
    conn_op = 0.0
    if 2.56 <= now <= 7.2:
        conn_op = ease_in_out(local_t(now, 2.56, 3.04))
    elif now > 7.2:
        conn_op = 1 - local_t(now, 7.68, 8.0)
    if conn_op > 0.02:
        layer = img.copy()
        ld = ImageDraw.Draw(layer)
        dashed_line(ld, 396, 720, 458, 690, dash=7, gap=6, width=3.2, offset=0)
        dashed_line(ld, 396, 754, 458, 790, dash=7, gap=6, width=3.2, offset=0)
        img = Image.blend(img, layer, conn_op)
        draw = ImageDraw.Draw(img)

    # magnifier Y offset
    if now < 0.24:
        mag_y = -228
    elif now < 1.92:
        mag_y = lerp(-228, 10, cubic_bezier_approx(local_t(now, 0.24, 1.92)))
    elif now < 2.24:
        mag_y = lerp(10, -3, ease_in_out(local_t(now, 1.92, 2.24)))
    elif now < 2.56:
        mag_y = lerp(-3, 0, ease_in_out(local_t(now, 2.24, 2.56)))
    elif now < 7.2:
        mag_y = 0
    else:
        mag_y = lerp(0, -228, ease_in_out(local_t(now, 7.76, 8.0)))

    ring_scale = 0.86
    ring_op = 0.55
    if 1.92 <= now <= 7.2:
        u = ease_in_out(local_t(now, 1.92, 2.4))
        ring_scale = lerp(0.86, 1.0, u)
        ring_op = lerp(0.55, 1.0, u)
    elif now > 7.2:
        u = local_t(now, 7.68, 8.0)
        ring_scale = lerp(1.0, 0.86, u)
        ring_op = lerp(1.0, 0.55, u)

    def my(y):
        return y + mag_y

    # handle then lens
    solid_line(draw, 400, my(802), 478, my(912), width=18)
    circle(draw, 338, my(737), 84, fill=WHITE, outline=CHAR, width=5.5)

    # yellow ring (draw as thick ring via two circles blended)
    rr = 30 * ring_scale
    ring_layer = img.copy()
    rd = ImageDraw.Draw(ring_layer)
    # outer yellow disk then punch inner white
    circle(rd, 338, my(737), rr + 6.5, fill=YELLOW)
    circle(rd, 338, my(737), max(4, rr - 6.5), fill=WHITE)
    img = Image.blend(img, ring_layer, ring_op)
    draw = ImageDraw.Draw(img)
    # redraw lens stroke on top so ring doesn't eat outline
    circle(draw, 338, my(737), 84, outline=CHAR, width=5.5)

    # card pop
    if now < 2.56:
        card_s, card_op = 0.0, 0.0
    elif now < 4.0:
        card_s = bounce_scale(local_t(now, 2.56, 4.0))
        card_op = clamp(local_t(now, 2.56, 3.04))
    elif now < 7.2:
        card_s, card_op = 1.0, 1.0
    else:
        card_s = lerp(1.0, 0.0, ease_in_out(local_t(now, 7.68, 8.0)))
        card_op = 1 - local_t(now, 7.68, 8.0)

    shot_op = 0.0
    if 3.84 <= now <= 7.2:
        shot_op = ease_in_out(local_t(now, 3.84, 4.48))
    elif now > 7.2:
        shot_op = 1 - local_t(now, 7.68, 8.0)

    vid_op = 0.0
    if 4.48 <= now <= 7.2:
        vid_op = ease_in_out(local_t(now, 4.48, 5.12))
    elif now > 7.2:
        vid_op = 1 - local_t(now, 7.68, 8.0)

    spark_op = 0.0
    spark_s = 0.7
    if 5.28 <= now < 5.68:
        u = (now - 5.28) / 0.4
        if u < 0.4:
            spark_op = u / 0.4
            spark_s = lerp(0.7, 1.12, u / 0.4)
        elif u < 0.7:
            spark_op = 1.0
            spark_s = 1.12
        else:
            spark_op = 1 - (u - 0.7) / 0.3
            spark_s = lerp(1.12, 0.85, (u - 0.7) / 0.3)
    elif 5.92 <= now < 6.24:
        u = (now - 5.92) / 0.32
        if u < 0.45:
            spark_op = u / 0.45
            spark_s = lerp(0.7, 1.08, u / 0.45)
        else:
            spark_op = 1 - (u - 0.45) / 0.55
            spark_s = lerp(1.08, 0.7, (u - 0.45) / 0.55)

    if card_op > 0.02 and card_s > 0.01:
        # scale card around origin (458, 736) ~ left-center
        ox, oy = 458.0, 736.0

        def cs(x, y):
            return ox + (x - ox) * card_s, oy + (y - oy) * card_s

        layer = img.copy()
        ld = ImageDraw.Draw(layer)

        # card border as dashed rounded rect approximation
        x, y, w, h, rx = cs(458, 612)[0], cs(458, 612)[1], 236 * card_s, 248 * card_s, 20 * card_s
        # We need draw in viewBox coords still — easier: draw unscaled on a card image then paste.
        # Simpler path: draw card elements in viewBox using cs() points.

        def vr(x0, y0, ww, hh, rad, **kw):
            a = cs(x0, y0)
            b = cs(x0 + ww, y0 + hh)
            # after scale, convert via xform
            p1 = xform(*a)
            p2 = xform(*b)
            ld.rounded_rectangle(
                [p1[0], p1[1], p2[0], p2[1]],
                radius=max(1, int(rad * card_s * SX)),
                **kw,
            )

        vr(458, 612, 236, 248, 20, fill=WHITE, outline=CHAR, width=sw(3.4))

        # dashed overlay on card edge — skip, solid is cleaner at small scale;
        # add dash ticks along the rect by drawing short segments
        def dash_round_rect(x0, y0, ww, hh, rad):
            # sample perimeter
            pts = []
            # approximate as rectangle perimeter
            corners = [
                (x0 + rad, y0, x0 + ww - rad, y0),
                (x0 + ww, y0 + rad, x0 + ww, y0 + hh - rad),
                (x0 + ww - rad, y0 + hh, x0 + rad, y0 + hh),
                (x0, y0 + hh - rad, x0, y0 + rad),
            ]
            for a, b, c, d in corners:
                p1 = cs(a, b)
                p2 = cs(c, d)
                dashed_line(ld, p1[0], p1[1], p2[0], p2[1], dash=11, gap=8, width=3.4 * card_s, offset=0)

        # dashed_line already applies xform, but p1 is already in viewBox after cs.
        dash_round_rect(458, 612, 236, 248, 20)

        img = Image.blend(img, layer, card_op)
        draw = ImageDraw.Draw(img)

        # screenshot
        if shot_op > 0.02:
            sl = img.copy()
            sd = ImageDraw.Draw(sl)

            def sline(x1, y1, x2, y2, width=3.2):
                p1 = cs(x1, y1)
                p2 = cs(x2, y2)
                solid_line(sd, p1[0], p1[1], p2[0], p2[1], width=width * card_s)

            def scirc(cx, cy, r, fill=None, outline=None, width=3):
                p = cs(cx, cy)
                circle(sd, p[0], p[1], r * card_s, fill=fill, outline=outline, width=width * card_s)

            def spolygon(pts, fill=None, outline=None, width=3.2):
                mapped = [cs(x, y) for x, y in pts]
                polygon(sd, mapped, fill=fill, outline=outline, width=width * card_s)

            # dashed screenshot frame
            x0, y0, ww, hh = 478, 636, 156, 112
            for a, b, c, d in [
                (x0, y0, x0 + ww, y0),
                (x0 + ww, y0, x0 + ww, y0 + hh),
                (x0 + ww, y0 + hh, x0, y0 + hh),
                (x0, y0 + hh, x0, y0),
            ]:
                p1 = cs(a, b)
                p2 = cs(c, d)
                dashed_line(sd, p1[0], p1[1], p2[0], p2[1], dash=7, gap=6, width=2.8 * card_s)

            spolygon([(492, 730), (528, 678), (562, 730)], fill=WHITE, outline=CHAR, width=3.2)
            spolygon([(540, 730), (592, 658), (640, 730)], fill=WHITE, outline=CHAR, width=3.2)
            scirc(618, 672, 9, fill=YELLOW)
            sline(492, 730, 626, 730, width=3.2)

            img = Image.blend(img, sl, shot_op * card_op)
            draw = ImageDraw.Draw(img)

        # video
        if vid_op > 0.02:
            vl = img.copy()
            vd = ImageDraw.Draw(vl)

            def vrect(x0, y0, ww, hh, rad):
                a = cs(x0, y0)
                b = cs(x0 + ww, y0 + hh)
                p1 = xform(*a)
                p2 = xform(*b)
                vd.rounded_rectangle(
                    [p1[0], p1[1], p2[0], p2[1]],
                    radius=max(1, int(rad * card_s * SX)),
                    fill=WHITE,
                    outline=CHAR,
                    width=sw(4 * card_s),
                )

            vrect(508, 762, 138, 78, 12)
            pts = [cs(556, 782), cs(556, 820), cs(594, 801)]
            polygon(vd, pts, fill=WHITE, outline=CHAR, width=3.6 * card_s)
            img = Image.blend(img, vl, vid_op * card_op)
            draw = ImageDraw.Draw(img)

    # spark
    if spark_op > 0.02:
        sl = img.copy()
        sd = ImageDraw.Draw(sl)
        ox, oy = 688.0, 656.0
        bolt = [(708, 598), (682, 650), (698, 650), (668, 714), (712, 648), (694, 648)]
        scaled = [(ox + (x - ox) * spark_s, oy + (y - oy) * spark_s) for x, y in bolt]
        polygon(sd, scaled, fill=WHITE, outline=CHAR, width=4)
        img = Image.blend(img, sl, spark_op)

    # downscale
    return img.resize((OW, OH), Image.Resampling.LANCZOS)


def main():
    frames = []
    for i in range(NFRAMES):
        t = i / FPS
        fr = draw_scene(t)
        frames.append(fr.convert("P", palette=Image.Palette.ADAPTIVE, colors=24, dither=Image.Dither.NONE))
        if i % 12 == 0:
            print(f"frame {i}/{NFRAMES} t={t:.2f}", flush=True)

    # duration per frame in ms
    ms = int(1000 / FPS)
    frames[0].save(
        OUT,
        save_all=True,
        append_images=frames[1:],
        duration=ms,
        loop=0,
        optimize=True,
        disposal=2,
    )
    print("wrote", OUT, "size", OUT.stat().st_size)


if __name__ == "__main__":
    main()
