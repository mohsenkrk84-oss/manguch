#!/usr/bin/env python3
"""Forensic-log sting: scan ticks, keystrokes, digital glitch, resolving tone."""
from __future__ import annotations

import math
import struct
import wave
from pathlib import Path

import numpy as np

SR = 44100
DUR = 6.2
RNG = np.random.default_rng(7)
OUT = Path("/home/user/manguch/forensic-log-sfx.wav")


def t_axis(n):
    return np.arange(n, dtype=np.float64) / SR


def onespole_lp(x, cutoff):
    a = math.exp(-2.0 * math.pi * cutoff / SR)
    y = np.empty_like(x)
    acc = 0.0
    b = 1.0 - a
    for i, v in enumerate(x):
        acc = b * v + a * acc
        y[i] = acc
    return y


def onespole_hp(x, cutoff):
    return x - onespole_lp(x, cutoff)


def fir_lp(x, cutoff, taps=91):
    n = np.arange(taps)
    m = (taps - 1) / 2.0
    h = np.sinc(2.0 * cutoff / SR * (n - m))
    h *= np.hamming(taps)
    s = h.sum()
    if s:
        h /= s
    return np.convolve(x, h, mode="same")


def fir_hp(x, cutoff, taps=91):
    n = np.arange(taps)
    m = (taps - 1) / 2.0
    h = np.sinc(2.0 * cutoff / SR * (n - m))
    h *= np.hamming(taps)
    h /= h.sum()
    # spectral inversion
    h = -h
    h[int(m)] += 1.0
    return np.convolve(x, h, mode="same")


def bandpass(x, lo, hi):
    return fir_lp(fir_hp(x, lo), hi)


def env_ads(n, attack, decay, sustain=0.0):
    t = t_axis(n)
    att = np.clip(t / max(attack, 1e-5), 0, 1)
    # cosine attack
    att = 0.5 - 0.5 * np.cos(np.pi * att)
    dec = np.exp(-t / max(decay, 1e-4))
    # after attack, decay toward sustain
    e = np.empty(n)
    a_n = max(1, int(attack * SR))
    e[:a_n] = att[:a_n]
    tail = np.exp(-np.arange(n - a_n) / SR / max(decay, 1e-4))
    e[a_n:] = sustain + (1.0 - sustain) * tail
    return e


def place(buf, sig, at, gain=1.0, pan=0.0):
    """pan -1 L .. +1 R. buf is (N, 2)."""
    i0 = int(at * SR)
    n = sig.shape[0]
    i1 = min(buf.shape[0], i0 + n)
    if i1 <= i0:
        return
    sl = sig[: i1 - i0] * gain
    gL = math.cos((pan + 1) * 0.25 * math.pi)
    gR = math.sin((pan + 1) * 0.25 * math.pi)
    if sl.ndim == 1:
        buf[i0:i1, 0] += sl * gL
        buf[i0:i1, 1] += sl * gR
    else:
        buf[i0:i1] += sl


def scan_tick(freq, noise_amt=0.35):
    n = int(0.014 * SR)
    t = t_axis(n)
    e = np.exp(-t * 520.0)
    tone = np.sin(2 * math.pi * freq * t + 0.4 * np.sin(2 * math.pi * freq * 0.5 * t))
    noise = fir_hp(RNG.normal(0, 1, n), 2500) * noise_amt
    sig = (0.85 * tone + noise) * e
    # tiny DC-block
    sig -= sig.mean()
    return sig * 0.55


def keystroke(kind="char"):
    if kind == "enter":
        n = int(0.055 * SR)
        noise = RNG.normal(0, 1, n)
        body = bandpass(noise, 600, 2800)
        click = fir_hp(noise, 4000)
        t = t_axis(n)
        e_body = np.exp(-t * 55)
        e_click = np.exp(-t * 220)
        thump = np.sin(2 * math.pi * 190 * t) * np.exp(-t * 70)
        sig = 0.70 * body * e_body + 0.45 * click * e_click + 0.22 * thump
        return sig * 0.72
    if kind == "space":
        n = int(0.04 * SR)
        noise = RNG.normal(0, 1, n)
        body = bandpass(noise, 400, 1600)
        t = t_axis(n)
        sig = body * np.exp(-t * 70) + 0.15 * np.sin(2 * math.pi * 140 * t) * np.exp(-t * 50)
        return sig * 0.5
    # character key
    n = int(0.028 * SR)
    noise = RNG.normal(0, 1, n)
    lo = 1400 + float(RNG.uniform(-200, 400))
    hi = 4200 + float(RNG.uniform(-400, 600))
    body = bandpass(noise, lo, hi)
    t = t_axis(n)
    ping_f = float(RNG.uniform(1800, 3200))
    ping = np.sin(2 * math.pi * ping_f * t) * np.exp(-t * 280)
    e = np.exp(-t * float(RNG.uniform(90, 160)))
    sig = 0.9 * body * e + 0.22 * ping
    return sig * float(RNG.uniform(0.42, 0.7))


def glitch_burst(src_mono, t0, length=0.32):
    """Build a digital glitch using a grain from src plus synthesized zap."""
    n = int(length * SR)
    i0 = max(0, int((t0 - 0.045) * SR))
    grain_n = int(0.022 * SR)
    grain = src_mono[i0 : i0 + grain_n]
    if grain.size < grain_n:
        grain = np.pad(grain, (0, grain_n - grain.size))
    # stutter with shrinking grains
    out = np.zeros(n)
    pos = 0
    g = grain.copy()
    while pos < n:
        gn = max(40, int(g.size * (0.72 + 0.15 * math.sin(pos))))
        piece = g[: min(gn, g.size)]
        # random dropouts / polarity flips
        if RNG.random() < 0.25:
            piece = -piece
        if RNG.random() < 0.2:
            piece = np.round(piece * 6) / 6.0
        take = min(piece.size, n - pos)
        out[pos : pos + take] += piece[:take]
        pos += take if RNG.random() > 0.18 else max(20, take // 3)

    t = t_axis(n)
    # FM zap
    sweep = 2400 * np.exp(-t * 14) + 180
    fm = np.sin(2 * math.pi * 70 * t + 3 * np.sin(2 * math.pi * 33 * t))
    zap = np.sin(2 * math.pi * sweep * t + 6 * fm) * np.exp(-t * 9)
    # bitcrush noise splat
    crush_src = RNG.normal(0, 1, n)
    step = 8
    crush_src = np.repeat(crush_src[::step], step)[:n]
    crush_src = np.round(crush_src * 5) / 5.0
    splat = fir_hp(crush_src, 1200) * np.exp(-t * 16) * (0.35 + 0.65 * (np.sin(2 * math.pi * 48 * t) > 0))

    sig = 0.55 * out / (np.max(np.abs(out)) + 1e-9) + 0.38 * zap + 0.22 * splat
    # hard digital gate flutter
    gate = (np.sin(2 * math.pi * 90 * t) * 0.5 + 0.5) ** 0.3
    gate = np.where(t < 0.05, 1.0, gate)
    sig *= gate
    # very short fade out
    fade = np.ones(n)
    ft = int(0.04 * SR)
    fade[-ft:] = np.linspace(1, 0, ft)
    fade[: int(0.004 * SR)] = np.linspace(0, 1, int(0.004 * SR))
    return 0.9 * sig * fade


def resolving_tone():
    """Clean fifths — solved, not fanfare."""
    n = int(3.6 * SR)
    t = t_axis(n)
    # attack ~ 70ms cosine, long exp decay
    att = 0.07
    a_n = int(att * SR)
    e_master = np.ones(n)
    e_master[:a_n] = 0.5 - 0.5 * np.cos(np.pi * np.linspace(0, 1, a_n))
    # frequencies: G3, D4, G4, D5, a quiet D6 sparkle
    partials = [
        (196.00, 0.16, 1.55),
        (293.66, 0.22, 1.85),
        (392.00, 0.28, 2.10),
        (587.33, 0.14, 2.35),
        (1174.66, 0.055, 1.20),
    ]
    sig = np.zeros(n)
    for i, (f, amp, dec) in enumerate(partials):
        # tiny slow beat, not chorus-y
        det = 1.0 + (0.0012 if i % 2 else -0.0008)
        tone = np.sin(2 * math.pi * f * det * t)
        # slight 2nd harmonic, very quiet, for body not buzz
        tone += 0.07 * np.sin(2 * math.pi * f * 2 * t)
        env = np.exp(-t / dec) * e_master
        sig += amp * tone * env
    # soft air: filtered noise bloom
    air = fir_lp(fir_hp(RNG.normal(0, 1, n), 1800), 6500)
    air *= (0.5 - 0.5 * np.cos(np.pi * np.clip(t / 0.12, 0, 1))) * np.exp(-t / 0.55)
    sig += 0.04 * air
    # gentle high sine ding at start of resolve
    ding_n = n
    ding = np.sin(2 * math.pi * 784.0 * t) * np.exp(-t / 0.55) * e_master
    sig += 0.11 * ding
    return sig * 0.92


def render():
    n = int(DUR * SR)
    buf = np.zeros((n, 2), dtype=np.float64)
    mono_preview = np.zeros(n, dtype=np.float64)

    # --- 1. fast data-scan ticks (0.00 → 2.08), accelerating ---
    t = 0.0
    interval = 0.052
    k = 0
    while t < 2.08:
        freq = float(RNG.uniform(2100, 5400))
        # every 4th tick a slightly lower "scan line" blip
        if k % 4 == 0:
            freq = float(RNG.uniform(1400, 2200))
        tick = scan_tick(freq, noise_amt=0.28 if k % 4 else 0.4)
        pan = math.sin(k * 0.85) * 0.35
        gain = 0.62 + 0.16 * math.sin(k * 0.5)
        # denser / a hair louder as we approach the lock
        dens = 1.05 + 0.55 * (t / 2.08)
        place(buf, tick, t, gain=gain * dens, pan=pan)
        i0 = int(t * SR)
        i1 = min(n, i0 + tick.size)
        if i1 > i0:
            mono_preview[i0:i1] += tick[: i1 - i0] * gain * dens
        interval = max(0.022, 0.055 - t * 0.016)
        t += interval * float(RNG.uniform(0.86, 1.12))
        k += 1

    # --- 2. terminal keystrokes, clustered ---
    clusters = [
        # (start, count, gap_mean, kind_pattern)
        (0.18, 7, 0.068, "char"),
        (0.78, 9, 0.055, "char"),
        (1.36, 5, 0.06, "char"),
    ]
    for start, count, gap, _ in clusters:
        tt = start
        for j in range(count):
            kind = "char"
            if j == count - 1 and start > 1.0:
                kind = "enter"
            elif RNG.random() < 0.08:
                kind = "space"
            ks = keystroke(kind)
            pan = float(RNG.uniform(-0.22, 0.22))
            place(buf, ks, tt, gain=1.05, pan=pan)
            i0 = int(tt * SR)
            i1 = min(n, i0 + ks.size)
            if i1 > i0:
                mono_preview[i0:i1] += ks[: i1 - i0] * 0.85
            tt += gap * float(RNG.uniform(0.7, 1.35))
            if RNG.random() < 0.12:
                tt += 0.05  # brief hesitation

    # a decisive enter right before the glitch
    ent = keystroke("enter")
    place(buf, ent, 1.98, gain=1.05, pan=0.05)
    i0 = int(1.98 * SR)
    i1 = min(n, i0 + ent.size)
    mono_preview[i0:i1] += ent[: i1 - i0]

    # --- 3. short digital glitch at the lock (~2.10) ---
    g = glitch_burst(mono_preview, 2.08, length=0.30)
    # make it slightly wider than center: micro delay + invert crumbs
    gL = g.copy()
    gR = np.roll(g, int(0.0016 * SR))
    gR[: int(0.0016 * SR)] = 0
    gR *= 0.92
    # brief L/R flicker
    t = t_axis(g.size)
    flick = 0.5 + 0.5 * np.sign(np.sin(2 * math.pi * 38 * t))
    stereo = np.stack([gL * (0.7 + 0.3 * flick), gR * (0.7 + 0.3 * (1 - flick))], axis=1)
    place(buf, stereo, 2.10, gain=1.0, pan=0.0)

    # --- 4. clean resolving tone (problem solved) ---
    tone = resolving_tone()
    # tiny Haas width
    tone_st = np.stack([tone, np.roll(tone, int(0.008 * SR))], axis=1)
    tone_st[: int(0.008 * SR), 1] = 0
    place(buf, tone_st, 2.36, gain=0.95, pan=0.0)

    # fade out last 0.35s
    fade_n = int(0.35 * SR)
    ramp = np.linspace(1, 0, fade_n)
    buf[-fade_n:, 0] *= ramp
    buf[-fade_n:, 1] *= ramp

    # safety DC block
    buf[:, 0] -= buf[:, 0].mean()
    buf[:, 1] -= buf[:, 1].mean()

    # peak normalize to -1.2 dBFS
    peak = np.max(np.abs(buf))
    if peak > 0:
        buf *= (10 ** (-1.2 / 20)) / peak

    # gentle tanh limiter for the glitch peaks
    buf = np.tanh(buf * 1.15) / math.tanh(1.15)
    peak = np.max(np.abs(buf))
    buf *= (10 ** (-1.0 / 20)) / peak

    pcm = np.clip(buf * 32767.0, -32768, 32767).astype(np.int16)
    with wave.open(str(OUT), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(pcm.tobytes())

    print("wrote", OUT, "seconds", DUR, "peak", float(np.max(np.abs(buf))), "bytes", OUT.stat().st_size)
    # envelope snapshot for QA
    hop = SR // 50
    env = np.sqrt(np.mean(buf[::1] ** 2, axis=1))
    # downsample env
    env_ds = env[: len(env) // hop * hop].reshape(-1, hop).mean(axis=1)
    print("env_max", float(env_ds.max()), "env_points", len(env_ds))
    print("env", ",".join(f"{v:.3f}" for v in env_ds[::2]))


if __name__ == "__main__":
    render()
