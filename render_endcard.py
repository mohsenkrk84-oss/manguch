#!/usr/bin/env python3
"""Guardian end-card: frames + cinematic sting → ready for ffmpeg mux."""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

# --- canvas ---
OW, OH = 720, 1290
SCALE = 2
W, H = OW * SCALE, OH * SCALE
SX = W / 768.0
SY = H / 1376.0

CHAR = (30, 30, 28)
YELLOW = (235, 184, 39)
WHITE = (255, 255, 255)

DUR = 6.5
FPS = 12
NFRAMES = int(round(DUR * FPS))
SR = 44100
RNG = np.random.default_rng(11)

FRAME_DIR = Path("/tmp/endcard-frames")
WAV = Path("/home/user/manguch/guardian-endcard-sfx.wav")
MP3 = Path("/home/user/manguch/guardian-endcard-sfx.mp3")

CX, CY = 384.0, 478.0  # shield/eye center in viewBox


def clamp(t, a=0.0, b=1.0):
    return max(a, min(b, t))


def ease_out(t):
    t = clamp(t)
    return 1 - (1 - t) ** 3


def ease_in_out(t):
    t = clamp(t)
    return t * t * (3 - 2 * t)


def local_t(now, a, b):
    if b <= a:
        return 0.0
    return clamp((now - a) / (b - a))


def xform(x, y):
    return x * SX, y * SY


def sw(w):
    return max(1, int(round(w * SX)))


def solid_line(draw, x1, y1, x2, y2, width=4.4, fill=CHAR):
    p1, p2 = xform(x1, y1), xform(x2, y2)
    w = sw(width)
    draw.line([p1, p2], fill=fill, width=w)
    r = max(1, w // 2)
    for x, y in (p1, p2):
        draw.ellipse([x - r, y - r, x + r, y + r], fill=fill)


def polyline(draw, pts, width=4.4, fill=CHAR, closed=False):
    if len(pts) < 2:
        return
    mapped = [xform(x, y) for x, y in pts]
    w = sw(width)
    seq = mapped + ([mapped[0]] if closed else [])
    draw.line(seq, fill=fill, width=w, joint="curve")
    r = max(1, w // 2)
    for x, y in seq:
        draw.ellipse([x - r, y - r, x + r, y + r], fill=fill)


def circle_fill(draw, cx, cy, r, fill):
    x, y = xform(cx, cy)
    rr = r * SX
    draw.ellipse([x - rr, y - rr, x + rr, y + rr], fill=fill)


def circle_stroke(draw, cx, cy, r, width=5, fill=CHAR):
    x, y = xform(cx, cy)
    rr = r * SX
    w = sw(width)
    draw.ellipse([x - rr, y - rr, x + rr, y + rr], outline=fill, width=w)


def x_mark(draw, cx, cy, s=14, width=4.4, fill=CHAR):
    solid_line(draw, cx - s, cy - s, cx + s, cy + s, width=width, fill=fill)
    solid_line(draw, cx + s, cy - s, cx - s, cy + s, width=width, fill=fill)


def shield_pts():
    top = (CX, 338)
    r_sh = (534, 408)
    r_mid = (548, 500)
    bot = (CX, 648)
    l_mid = (220, 500)
    l_sh = (234, 408)
    # denser polyline approximating the classic heater shield
    pts = []

    def quad(p0, p1, p2, n=10):
        for i in range(n):
            t = i / n
            a = (1 - t) ** 2
            b = 2 * (1 - t) * t
            c = t * t
            pts.append(
                (
                    a * p0[0] + b * p1[0] + c * p2[0],
                    a * p0[1] + b * p1[1] + c * p2[1],
                )
            )

    quad(top, (CX + 70, 348), r_sh, 8)
    quad(r_sh, r_mid, bot, 14)
    quad(bot, l_mid, l_sh, 14)
    quad(l_sh, (CX - 70, 348), top, 8)
    return pts


def dashed_circle(draw, cx, cy, r, rot_deg=0, dash=11, gap=9, width=4.6):
    # dash/gap in degrees
    a = rot_deg
    end = rot_deg + 360
    while a < end:
        a1 = a
        a2 = min(a + dash, end)
        n = max(4, int((a2 - a1) * 0.6))
        pts = []
        for i in range(n + 1):
            ang = math.radians(a1 + (a2 - a1) * i / n - 90)
            pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
        polyline(draw, pts, width=width)
        a += dash + gap


def almond_eye(draw, open_amt=1.0):
    """open_amt 1 = open, 0 = closed slit."""
    open_amt = clamp(open_amt, 0.06, 1.0)
    # outer almond
    w, h = 168.0, 78.0 * open_amt
    n = 48
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        # almond-ish: squircle-ellipse pinched
        x = CX + (w / 2) * math.cos(t)
        y = CY + (h / 2) * math.sin(t) * (0.85 + 0.15 * abs(math.cos(t)))
        pts.append((x, y))
    mapped = [xform(x, y) for x, y in pts]
    draw.polygon(mapped, fill=WHITE)
    polyline(draw, pts, width=4.6, closed=True)

    if open_amt < 0.18:
        # closed: just the slit already drawn
        return

    # yellow iris
    iris_r = 36 * (0.55 + 0.45 * open_amt)
    circle_fill(draw, CX, CY, iris_r, YELLOW)
    circle_stroke(draw, CX, CY, iris_r, width=3.2)
    # pupil — offset C / spiral look
    circle_fill(draw, CX + 6, CY - 2, 16 * open_amt, CHAR)
    # tiny highlight
    circle_fill(draw, CX - 10, CY - 10, 4.5 * open_amt, WHITE)


def mix_white(color, op):
    op = clamp(op)
    return tuple(int(color[i] * op + 255 * (1 - op)) for i in range(3))


def checkmark(draw, scale=1.0, alpha=1.0):
    if alpha <= 0.02 or scale <= 0.02:
        return
    ox, oy = CX, 692.0
    base = [(CX - 28, 686), (CX - 6, 714), (CX + 42, 658)]
    pts = [(ox + (x - ox) * scale, oy + (y - oy) * scale) for x, y in base]
    polyline(draw, pts, width=11.5, fill=mix_white(YELLOW, alpha))


def draw_scene(now: float) -> Image.Image:
    img = Image.new("RGB", (W, H), WHITE)
    draw = ImageDraw.Draw(img)

    # halo rotation: slow, eases to a stop
    if now < 4.6:
        rot = 28.0 * ease_out(now / 4.6)
    else:
        rot = 28.0
    dashed_circle(draw, CX, CY + 8, 228, rot_deg=rot, dash=12, gap=9, width=4.8)

    # × marks fade 0.55 → 1.85
    x_op = 1.0 - ease_in_out(local_t(now, 0.55, 1.85))
    x_positions = [
        (198, 368, 13),
        (590, 312, 13),
        (586, 618, 12),
    ]
    if x_op > 0.02:
        xc = mix_white(CHAR, x_op)
        for x, y, s in x_positions:
            x_mark(draw, x, y, s=s, width=4.5, fill=xc)

    # shield
    sp = shield_pts()
    mapped = [xform(x, y) for x, y in sp]
    draw.polygon(mapped, fill=WHITE)
    polyline(draw, sp, width=5.2, closed=True)

    # blink once around 2.05–2.38
    if now < 2.05:
        open_amt = 1.0
    elif now < 2.18:
        open_amt = 1.0 - ease_in_out(local_t(now, 2.05, 2.18)) * 0.94
    elif now < 2.40:
        open_amt = 0.06 + 0.94 * ease_out(local_t(now, 2.18, 2.40))
    else:
        open_amt = 1.0
    almond_eye(draw, open_amt=open_amt)

    # checkmark: fade in + scale settle 1.35 → 2.55
    if now < 1.35:
        c_s, c_a = 0.35, 0.0
    elif now < 2.55:
        u = ease_out(local_t(now, 1.35, 2.55))
        # overshoot settle
        if u < 0.72:
            c_s = 0.35 + 0.80 * (u / 0.72)  # → 1.15
        else:
            c_s = 1.15 - 0.15 * ease_in_out((u - 0.72) / 0.28)
        c_a = ease_out(local_t(now, 1.35, 1.85))
    else:
        c_s, c_a = 1.0, 1.0

    checkmark(draw, scale=c_s, alpha=c_a)

    return img.resize((OW, OH), Image.Resampling.LANCZOS)


# -------------------- audio --------------------
def fir_lp(x, cutoff, taps=97):
    n = np.arange(taps)
    m = (taps - 1) / 2.0
    h = np.sinc(2.0 * cutoff / SR * (n - m))
    h *= np.hamming(taps)
    s = h.sum()
    if s:
        h /= s
    return np.convolve(x, h, mode="same")


def fir_hp(x, cutoff, taps=97):
    n = np.arange(taps)
    m = (taps - 1) / 2.0
    h = np.sinc(2.0 * cutoff / SR * (n - m))
    h *= np.hamming(taps)
    h /= h.sum()
    h = -h
    h[int(m)] += 1.0
    return np.convolve(x, h, mode="same")


def rising_cutoff_noise(n, f0, f1):
    """Approximate a rising lowpass by blending 4 pre-filtered noise bands."""
    raw = RNG.normal(0, 1, n).astype(np.float64)
    # pink-ish
    raw = np.cumsum(raw)
    raw -= np.linspace(raw[0], raw[-1], n)
    raw /= np.std(raw) + 1e-9
    bands = [400, 900, 2200, 6000]
    filts = [fir_lp(raw, f) for f in bands]
    t = np.arange(n) / SR
    # riser 0→2.18s mapped onto this buffer
    pos = np.clip(t / (n / SR), 0, 1)
    pos = pos ** 1.35
    out = np.zeros(n)
    for i, f in enumerate(filts):
        center = i / (len(filts) - 1)
        w = np.clip(1.0 - 2.2 * np.abs(pos - center), 0, 1)
        out += w * f
    env = pos ** 0.85
    # slight AM shimmer
    out *= env * (0.85 + 0.15 * np.sin(2 * math.pi * 3.2 * t))
    return 0.22 * out / (np.max(np.abs(out)) + 1e-9)


def riser_tones(n):
    t = np.arange(n) / SR
    dur = n / SR
    # rising cluster
    f0, f1 = 92.0, 390.0
    freq = f0 * (f1 / f0) ** np.clip(t / dur, 0, 1)
    phase = 2 * math.pi * np.cumsum(freq) / SR
    sig = 0.55 * np.sin(phase)
    sig += 0.22 * np.sin(2 * phase)
    sig += 0.10 * np.sin(3 * phase + 0.4)
    env = (t / dur) ** 1.1
    env *= np.clip((dur - t) / 0.08, 0, 1)  # tiny fade into impact
    return 0.18 * sig * env


def impact(n):
    t = np.arange(n) / SR
    # pitch drop sine
    f = 68 * np.exp(-t * 9.5) + 28
    phase = 2 * math.pi * np.cumsum(f) / SR
    body = np.sin(phase) * np.exp(-t * 3.4)
    sub = np.sin(2 * math.pi * 42 * t) * np.exp(-t * 2.2)
    click = fir_hp(RNG.normal(0, 1, n), 1800) * np.exp(-t * 70)
    # short punch envelope
    punch = np.exp(-t * 18)
    sig = 0.85 * body * punch + 0.40 * sub * np.exp(-t * 2.6) + 0.16 * click
    return 0.95 * sig


def warm_pad(n):
    t = np.arange(n) / SR
    # G major-ish warmth but mostly fifths: G2 D3 G3 D4
    partials = [
        (98.00, 0.22, 2.8),
        (146.83, 0.18, 3.1),
        (196.00, 0.16, 3.3),
        (293.66, 0.10, 2.6),
        (392.00, 0.06, 2.2),
    ]
    sig = np.zeros(n)
    for i, (f, amp, dec) in enumerate(partials):
        det = 1.0 + (0.0014 if i % 2 == 0 else -0.0010)
        tone = np.sin(2 * math.pi * f * det * t)
        tone += 0.08 * np.sin(2 * math.pi * f * 2 * t)
        sig += amp * tone * np.exp(-t / dec)
    # slow attack so it blooms out of the impact
    att = int(0.18 * SR)
    ramp = np.ones(n)
    ramp[:att] = 0.5 - 0.5 * np.cos(np.pi * np.linspace(0, 1, att))
    air = fir_lp(fir_hp(RNG.normal(0, 1, n), 600), 2400) * np.exp(-t / 1.6) * 0.03
    return 0.55 * (sig * ramp + air)


def render_audio():
    n = int(DUR * SR)
    buf = np.zeros((n, 2), dtype=np.float64)

    # riser 0 → 2.18
    rn = int(2.18 * SR)
    riser = rising_cutoff_noise(rn, 400, 6000) + riser_tones(rn)
    # stereo widen
    rL = riser
    rR = np.roll(riser, int(0.012 * SR))
    rR[: int(0.012 * SR)] = 0
    buf[:rn, 0] += rL
    buf[:rn, 1] += rR

    # impact at 2.18 (checkmark settle / × gone)
    imp_n = int(1.8 * SR)
    imp = impact(imp_n)
    i0 = int(2.18 * SR)
    i1 = min(n, i0 + imp_n)
    sl = imp[: i1 - i0]
    buf[i0:i1, 0] += sl
    buf[i0:i1, 1] += sl * 0.98

    # warm pad from 2.16
    pn = n - int(2.16 * SR)
    pad = warm_pad(pn)
    # slight Haas
    p0 = int(2.16 * SR)
    buf[p0:, 0] += pad
    delay = int(0.011 * SR)
    buf[p0 + delay :, 1] += pad[:-delay] if delay < pad.size else pad

    # master fade out last 1.1s
    fade_n = int(1.1 * SR)
    ramp = np.linspace(1, 0, fade_n) ** 1.2
    buf[-fade_n:] *= ramp[:, None]

    buf[:, 0] -= buf[:, 0].mean()
    buf[:, 1] -= buf[:, 1].mean()
    peak = np.max(np.abs(buf))
    buf *= (10 ** (-1.2 / 20)) / (peak + 1e-12)
    buf = np.tanh(buf * 1.12) / math.tanh(1.12)
    peak = np.max(np.abs(buf))
    buf *= (10 ** (-1.0 / 20)) / (peak + 1e-12)

    import wave

    pcm = np.clip(buf * 32767.0, -32768, 32767).astype(np.int16)
    with wave.open(str(WAV), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(pcm.tobytes())
    print("wav", WAV, WAV.stat().st_size)


def render_frames():
    FRAME_DIR.mkdir(parents=True, exist_ok=True)
    for i in range(NFRAMES):
        t = i / FPS
        fr = draw_scene(t)
        fr.save(FRAME_DIR / f"f{i:04d}.png")
        if i % 12 == 0:
            print(f"frame {i}/{NFRAMES} t={t:.2f}", flush=True)
    print("frames", NFRAMES, "dir", FRAME_DIR)


if __name__ == "__main__":
    render_frames()
    render_audio()
