#!/usr/bin/env python3
"""30s Instagram 9:16 motion-graphics reel for Business Guardian."""
from __future__ import annotations

import math
import subprocess
from pathlib import Path

import arabic_reshaper
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from bidi.algorithm import get_display

ROOT = Path("/home/user/manguch")
FF = "/tmp/venv/lib/python3.11/site-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2"
FRAME_DIR = Path("/tmp/reel-frames")
FORE_DIR = Path("/tmp/f-forensic")
END_DIR = Path("/tmp/f-end")
OUT = ROOT / "businessguardian-reel.mp4"
WAV = ROOT / "businessguardian-reel.wav"
FONT_B = str(ROOT / "fonts/Vazirmatn-Bold.ttf")
FONT_M = str(ROOT / "fonts/Vazirmatn-Medium.ttf")

W, H = 1080, 1920
FPS = 24
DUR = 30.0
N = int(DUR * FPS)  # 720
SR = 44100
CHAR = (30, 30, 28)
YELLOW = (235, 184, 39)
WHITE = (255, 255, 255)
RNG = np.random.default_rng(21)

SHOTS = [
    (0.00, 4.00, "s1"),
    (4.00, 9.00, "s2"),
    (9.00, 14.00, "s3"),
    (14.00, 21.00, "s4"),
    (21.00, 25.00, "s5"),
    (25.00, 30.00, "s6"),
]
SUBS = {
    "s1": "سایت بالاس… ولی کسی نمی‌تونه خرید کنه.",
    "s2": "آپتایم سبز می‌گه همه‌چی خوبه.\nسبد، درگاه و فرم از کار افتادن.",
    "s3": "مثل یک مشتری واقعی، کل مسیر خرید\nوردپرس و ووکامرس رو تست می‌کنه.",
    "s4": "وقتی خطا می‌ده، اسکرین‌شات، ویدیو\nو علت ریشه‌ای رو با AI می‌فرسته.",
    "s5": "فرم‌ها، درگاه‌های ایرانی، سبد خرید\n— قبل از مشتری، تو خبردار می‌شی.",
    "s6": None,  # custom end-card type
}

XFADE = 0.35  # seconds


def clamp(v, a=0.0, b=1.0):
    return max(a, min(b, v))


def ease(t):
    t = clamp(t)
    return t * t * (3 - 2 * t)


def fa(text: str) -> str:
    return get_display(arabic_reshaper.reshape(text))


def load_still(name: str) -> Image.Image:
    im = Image.open(ROOT / name).convert("RGB")
    return im.resize((W, H), Image.Resampling.LANCZOS)


def extract_video_frames(src: Path, dest: Path):
    dest.mkdir(parents=True, exist_ok=True)
    subprocess.check_call(
        [
            FF, "-y", "-i", str(src),
            "-vf", f"scale={W}:{H}:flags=lanczos,fps={FPS}",
            str(dest / "%04d.png"),
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def list_frames(d: Path):
    return sorted(d.glob("*.png"))


def fit_cover_float(base: Image.Image, scale=1.0, dx=0, dy=0) -> Image.Image:
    """Scale about center, crop back to canvas."""
    if abs(scale - 1.0) < 0.001 and dx == 0 and dy == 0:
        return base
    nw, nh = int(W * scale), int(H * scale)
    img = base.resize((nw, nh), Image.Resampling.BILINEAR)
    canvas = Image.new("RGB", (W, H), WHITE)
    x = (W - nw) // 2 + int(dx)
    y = (H - nh) // 2 + int(dy)
    canvas.paste(img, (x, y))
    return canvas


def split_float(base: Image.Image, y_cut: int, top_dy=0, bot_dy=0) -> Image.Image:
    top = base.crop((0, 0, W, y_cut))
    bot = base.crop((0, y_cut, W, H))
    canvas = Image.new("RGB", (W, H), WHITE)
    canvas.paste(top, (0, int(top_dy)))
    canvas.paste(bot, (0, y_cut + int(bot_dy)))
    return canvas


def rgba(rgb, a=255):
    return (rgb[0], rgb[1], rgb[2], int(a))


def dashed_circle(draw, cx, cy, r, rot, dash=14, gap=10, width=5, fill=None):
    fill = fill or rgba(CHAR)
    a = rot
    while a < rot + 360:
        a1, a2 = a, a + dash
        pts = []
        n = max(3, int((a2 - a1) * 0.5))
        for i in range(n + 1):
            ang = math.radians(a1 + (a2 - a1) * i / n - 90)
            pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
        draw.line(pts, fill=fill, width=width, joint="curve")
        a += dash + gap


def x_mark(draw, x, y, s, width=5, fill=None):
    fill = fill if fill is not None else rgba(CHAR)
    if len(fill) == 3:
        fill = rgba(fill)
    draw.line([(x - s, y - s), (x + s, y + s)], fill=fill, width=width)
    draw.line([(x + s, y - s), (x - s, y + s)], fill=fill, width=width)


def pulse_alpha(t, speed=2.2):
    return 0.35 + 0.65 * (0.5 + 0.5 * math.sin(2 * math.pi * speed * t))


def overlay_rgba(base: Image.Image, drawer_fn, alpha=1.0) -> Image.Image:
    if alpha <= 0.01:
        return base
    ov = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    drawer_fn(d)
    if alpha < 0.995:
        a = ov.split()[-1].point(lambda p: int(p * alpha))
        ov.putalpha(a)
    return Image.alpha_composite(base.convert("RGBA"), ov).convert("RGB")


def subtitle_block(img: Image.Image, text: str, local_t: float, font) -> Image.Image:
    if not text:
        return img
    appear = ease(clamp(local_t / 0.28))
    if appear <= 0.02:
        return img
    lines = [fa(x) for x in text.split("\n")]
    pad_x, pad_y, gap = 36, 22, 8
    sizes = [font.getbbox(ln) for ln in lines]
    tw = max(s[2] - s[0] for s in sizes)
    th = sum(s[3] - s[1] for s in sizes) + gap * (len(lines) - 1)
    box_w = min(W - 80, tw + pad_x * 2)
    box_h = th + pad_y * 2
    x0 = (W - box_w) // 2
    y0 = H - 220 - box_h
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    fill_a = int(230 * appear)
    d.rounded_rectangle(
        [x0, y0, x0 + box_w, y0 + box_h],
        radius=22,
        fill=(30, 30, 28, fill_a),
    )
    # yellow tick on the right of the pill
    d.rounded_rectangle(
        [x0 + 10, y0 + 12, x0 + 18, y0 + box_h - 12],
        radius=4,
        fill=(235, 184, 39, fill_a),
    )
    y = y0 + pad_y
    for ln, bb in zip(lines, sizes):
        lh = bb[3] - bb[1]
        d.text(((W) // 2, y), ln, font=font, fill=(255, 255, 255, fill_a), anchor="mt")
        y += lh + gap
    return Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")


def endcard_type(img, local_t, font_b, font_m):
    appear = ease(clamp((local_t - 1.6) / 0.45))
    if appear <= 0.02:
        return img
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    a = int(255 * appear)
    # middle empty band ~ y 980–1180, lower ~ 1400
    line1 = fa("۳ روز تست — تمام امکانات")
    line2 = "businessguardian.ir"
    d.text((W // 2, 1040), line1, font=font_b, fill=(30, 30, 28, a), anchor="mm")
    # yellow underline
    bb = font_b.getbbox(line1)
    tw = bb[2] - bb[0]
    d.rounded_rectangle(
        [W // 2 - tw // 2, 1088, W // 2 + tw // 2, 1096],
        radius=3,
        fill=(235, 184, 39, a),
    )
    d.text((W // 2, 1160), line2, font=font_m, fill=(30, 30, 28, int(a * 0.9)), anchor="mm")
    return Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")


def draw_s1(base, t, font):
    # icons float, character grounded, dashed halo crawls, × pulse
    y_cut = 900
    top_dy = 10 * math.sin(2 * math.pi * t * 0.45)
    bot_dy = 3 * math.sin(2 * math.pi * t * 0.25 + 0.4)
    img = split_float(base, y_cut, top_dy=top_dy, bot_dy=bot_dy)
    scale = 1.0 + 0.012 * math.sin(2 * math.pi * t * 0.2)
    img = fit_cover_float(img, scale=scale)

    rot = t * 28
    pulse = pulse_alpha(t, 1.6)

    def ov(d):
        # motion arc between server (left) and cart (right)
        dashed_circle(d, 540, 430, 230, rot, dash=16, gap=12, width=6)
        for pos in [(820, 310), (900, 520), (700, 560)]:
            col = tuple(int(c * pulse + 255 * (1 - pulse)) for c in CHAR)
            x_mark(d, pos[0], pos[1], 12, width=5, fill=rgba(col, int(255 * pulse)))

    img = overlay_rgba(img, ov, alpha=0.85)
    return subtitle_block(img, SUBS["s1"], t, font)


def draw_s2(base, t, font):
    img = fit_cover_float(base, scale=1.0 + 0.01 * math.sin(t * 0.7), dy=4 * math.sin(t * 1.1))
    rot = t * 40

    def ov(d):
        # crawling dashes on the right path
        dashed_circle(d, 760, 820, 160, rot, dash=12, gap=10, width=5)
        # × on the break, pulsing
        p = pulse_alpha(t, 2.0)
        x_mark(d, 780, 780, 16, width=7, fill=rgba(CHAR, int(255 * p)))
        r = 92 + 8 * math.sin(t * 6)
        d.ellipse([250 - r, 820 - r, 250 + r, 820 + r], outline=rgba(YELLOW, 200), width=6)

    img = overlay_rgba(img, ov, 0.9)
    return subtitle_block(img, SUBS["s2"], t, font)


def draw_s3(base, t, font):
    img = fit_cover_float(base, scale=1.0 + 0.008 * t / 5.0)
    rot = t * 18

    def ov(d):
        dashed_circle(d, 540, 520, 250, rot, dash=13, gap=11, width=5)
        # walking cursor along an ellipse around the lower path
        ang = math.radians(-20 + t * 70)
        cx, cy, rx, ry = 540, 1420, 340, 160
        x = cx + rx * math.cos(ang)
        y = cy + ry * math.sin(ang)
        # simple pointer
        d.polygon([(x, y), (x + 28, y + 12), (x + 12, y + 14), (x + 18, y + 36)], outline=rgba(CHAR))
        d.line([(x, y), (x + 28, y + 12), (x + 12, y + 14), (x + 18, y + 36)], fill=rgba(CHAR), width=4)

    img = overlay_rgba(img, ov, 0.75)
    return subtitle_block(img, SUBS["s3"], t, font)


def draw_s5(base, t, font):
    img = fit_cover_float(base, scale=1.01)
    # sequential highlights: cart, form, gate, check — lower band
    spots = [
        (170, 1380, 110),
        (400, 1380, 100),
        (640, 1380, 120),
        (900, 1380, 110),
    ]
    slot = (t % 4.0)
    idx = min(3, int(slot))
    frac = slot - idx
    alpha = 0.22 * math.sin(math.pi * clamp(frac / 0.85))

    def ov(d):
        x, y, r = spots[idx]
        d.ellipse([x - r, y - r, x + r, y + r], fill=(235, 184, 39, int(200 * max(alpha, 0))))
        dashed_circle(d, 540, 520, 250, t * 14, dash=13, gap=11, width=5)

    img = overlay_rgba(img, ov, 1.0)
    return subtitle_block(img, SUBS["s5"], t, font)


def shot_at(now: float):
    for a, b, k in SHOTS:
        if a <= now < b or (k == "s6" and now >= a):
            return k, now - a, b - a
    return "s6", DUR - 25.0, 5.0


def render_frames(stills, forensic, endcard, font_b, font_m):
    FRAME_DIR.mkdir(parents=True, exist_ok=True)
    prev = None
    prev_key = None
    for i in range(N):
        now = i / FPS
        key, loc, dur = shot_at(now)
        if key == "s1":
            frame = draw_s1(stills["s1"], loc, font_b)
        elif key == "s2":
            frame = draw_s2(stills["s2"], loc, font_b)
        elif key == "s3":
            frame = draw_s3(stills["s3"], loc, font_b)
        elif key == "s4":
            fi = min(len(forensic) - 1, int(loc * FPS))
            frame = Image.open(forensic[fi]).convert("RGB")
            if frame.size != (W, H):
                frame = frame.resize((W, H), Image.Resampling.LANCZOS)
            frame = subtitle_block(frame, SUBS["s4"], loc, font_b)
        elif key == "s5":
            frame = draw_s5(stills["s5"], loc, font_b)
        else:
            fi = min(len(endcard) - 1, int(loc * FPS))
            frame = Image.open(endcard[fi]).convert("RGB")
            if frame.size != (W, H):
                frame = frame.resize((W, H), Image.Resampling.LANCZOS)
            frame = endcard_type(frame, loc, font_b, font_m)

        # crossfade at shot boundaries
        if prev is not None and prev_key != key and loc < XFADE:
            u = ease(loc / XFADE)
            frame = Image.blend(prev, frame, u)
        prev = frame
        prev_key = key
        frame.save(FRAME_DIR / f"{i:04d}.png", optimize=False)
        if i % 48 == 0:
            print(f"frame {i}/{N} t={now:.2f} {key}", flush=True)


# -------------------- audio --------------------
def fir_lp(x, cutoff, taps=81):
    n = np.arange(taps)
    m = (taps - 1) / 2.0
    h = np.sinc(2.0 * cutoff / SR * (n - m))
    h *= np.hamming(taps)
    h /= h.sum()
    return np.convolve(x, h, mode="same")


def fir_hp(x, cutoff, taps=81):
    n = np.arange(taps)
    m = (taps - 1) / 2.0
    h = np.sinc(2.0 * cutoff / SR * (n - m))
    h *= np.hamming(taps)
    h /= h.sum()
    h = -h
    h[int(m)] += 1.0
    return np.convolve(x, h, mode="same")


def load_wav(path: Path):
    import wave
    with wave.open(str(path), "rb") as w:
        assert w.getsampwidth() == 2
        nch = w.getnchannels()
        sr = w.getframerate()
        data = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float64) / 32768.0
        if nch == 2:
            data = data.reshape(-1, 2)
        else:
            data = np.stack([data, data], axis=1)
        if sr != SR:
            # naive resample
            t = np.linspace(0, 1, data.shape[0])
            nt = np.linspace(0, 1, int(data.shape[0] * SR / sr))
            data = np.stack([np.interp(nt, t, data[:, 0]), np.interp(nt, t, data[:, 1])], axis=1)
        return data


def place(buf, sig, at, gain=1.0):
    i0 = int(at * SR)
    n = sig.shape[0]
    i1 = min(buf.shape[0], i0 + n)
    if i1 <= i0:
        return
    sl = sig[: i1 - i0] * gain
    if sl.ndim == 1:
        buf[i0:i1, 0] += sl
        buf[i0:i1, 1] += sl
    else:
        buf[i0:i1] += sl


def whoosh(n):
    t = np.arange(n) / SR
    noise = RNG.normal(0, 1, n)
    sig = fir_lp(fir_hp(noise, 400), 5000)
    env = (t / (n / SR)) ** 0.5 * np.exp(-t * 8)
    return 0.25 * sig * env


def pad_tone(n, freqs, amp=0.08):
    t = np.arange(n) / SR
    sig = np.zeros(n)
    for i, f in enumerate(freqs):
        sig += (amp / len(freqs)) * np.sin(2 * math.pi * f * t + 0.2 * i)
        sig += (amp / len(freqs) * 0.15) * np.sin(2 * math.pi * f * 2 * t)
    att = int(0.4 * SR)
    env = np.ones(n)
    env[:att] = np.linspace(0, 1, att)
    env[-int(0.8 * SR) :] *= np.linspace(1, 0, int(0.8 * SR))
    return fir_lp(sig * env, 2400)


def ticks(total_n, until=9.0):
    buf = np.zeros((total_n, 2))
    t = 0.0
    k = 0
    while t < until:
        n = int(0.012 * SR)
        tt = np.arange(n) / SR
        f = float(RNG.uniform(1800, 4800))
        sig = np.sin(2 * math.pi * f * tt) * np.exp(-tt * 480)
        pan = math.sin(k * 0.9) * 0.4
        gL, gR = math.cos((pan + 1) * 0.25 * math.pi), math.sin((pan + 1) * 0.25 * math.pi)
        i0 = int(t * SR)
        i1 = min(total_n, i0 + n)
        buf[i0:i1, 0] += sig[: i1 - i0] * 0.09 * gL
        buf[i0:i1, 1] += sig[: i1 - i0] * 0.09 * gR
        t += 0.07 * float(RNG.uniform(0.7, 1.2)) * max(0.55, 1 - t / 14)
        k += 1
    return buf


def render_audio():
    n = int(DUR * SR)
    buf = np.zeros((n, 2))
    # bed
    buf[:, 0] += pad_tone(n, [98, 147, 196], 0.05)
    buf[:, 1] += pad_tone(n, [98.4, 146.5, 196.6], 0.05)
    buf += ticks(n, until=13.5)
    # whooshes at cuts
    w = whoosh(int(0.28 * SR))
    for at in (4.0, 9.0, 14.0, 21.0, 25.0):
        place(buf, w, at - 0.05, gain=0.8)
    # forensic sting at shot 4
    fpath = ROOT / "forensic-log-sfx.wav"
    if fpath.exists():
        place(buf, load_wav(fpath), 14.05, gain=0.7)
    # endcard sting at 25.0
    epath = ROOT / "guardian-endcard-sfx.wav"
    if epath.exists():
        place(buf, load_wav(epath), 25.05, gain=0.85)

    fade = int(0.25 * SR)
    buf[:fade] *= np.linspace(0, 1, fade)[:, None]
    buf[-int(0.6 * SR) :] *= np.linspace(1, 0, int(0.6 * SR))[:, None]
    peak = np.max(np.abs(buf))
    buf *= (10 ** (-1.3 / 20)) / (peak + 1e-12)
    import wave
    pcm = np.clip(buf * 32767, -32768, 32767).astype(np.int16)
    with wave.open(str(WAV), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(pcm.tobytes())
    print("wav", WAV.stat().st_size)


def mux():
    subprocess.check_call(
        [
            FF, "-y",
            "-framerate", str(FPS),
            "-i", str(FRAME_DIR / "%04d.png"),
            "-i", str(WAV),
            "-t", str(DUR),
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-profile:v", "high",
            "-crf", "16", "-preset", "veryfast",
            "-c:a", "aac", "-b:a", "192k", "-ac", "2", "-ar", "44100",
            "-movflags", "+faststart",
            str(OUT),
        ]
    )
    print("out", OUT, OUT.stat().st_size)


def main():
    print("extract video frames…")
    extract_video_frames(ROOT / "forensic-log-animation.mp4", FORE_DIR)
    extract_video_frames(ROOT / "guardian-endcard.mp4", END_DIR)
    forensic = list_frames(FORE_DIR)
    endcard = list_frames(END_DIR)
    print("forensic", len(forensic), "end", len(endcard))
    stills = {
        "s1": load_still("site-up-checkout-down.png"),
        "s2": load_still("uptime-vs-checkout-break.png"),
        "s3": load_still("guardian-checkout-watch.png"),
        "s5": load_still("guardian-checkout-watch.png"),
    }
    font_b = ImageFont.truetype(FONT_B, 44)
    font_m = ImageFont.truetype(FONT_M, 36)
    print("render frames…")
    render_frames(stills, forensic, endcard, font_b, font_m)
    print("audio…")
    render_audio()
    print("mux…")
    mux()


if __name__ == "__main__":
    main()
