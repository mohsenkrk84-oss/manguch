# -*- coding: utf-8 -*-
"""Instagram story pre-designs (1080x1920) for Manguch mochi course.
Titles: Hasti | Body: Aviny | Price digits: Aviny (Hasti digits look Latin)
Explicit escapes: ZWNJ | ئ | Persian digits | ٬
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fatext import FaFont, draw_fa
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1080, 1920
HASTI_RRD = os.path.join(ROOT, "Hasti-HeavyRRD.otf")
HASTI_R = os.path.join(ROOT, "Hasti-HeavyR.otf")
HASTI_S = os.path.join(ROOT, "Hasti-HeavyS.otf")
AVINY = os.path.join(ROOT, "aviny.otf")

_fonts = {}
def F(path, size):
    key = (path, size)
    if key not in _fonts:
        _fonts[key] = FaFont(path, size)
    return _fonts[key]

def fit(path, text, max_w, start, minimum=20):
    s = start
    while s > minimum and F(path, s).measure(text) > max_w:
        s -= 2
    return s

# ---------- basic helpers ----------
def vgradient(w, h, top, bottom):
    g = Image.new("RGB", (1, h))
    px = g.load()
    for y in range(h):
        t = y / max(h - 1, 1)
        px[0, y] = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
    return g.resize((w, h))

def dots(img, color, step=72, r=7, alpha=40, y0=0, y1=None):
    y1 = y1 or img.size[1]
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    c = color + (alpha,)
    row = 0
    for y in range(y0, y1, step):
        off = (step // 2) if row % 2 else 0
        for x in range(off, img.size[0], step):
            d.ellipse([x - r, y - r, x + r, y + r], fill=c)
        row += 1
    img.alpha_composite(layer)

def cover(path, w, h):
    im = Image.open(os.path.join(ROOT, path)).convert("RGB")
    sw, sh = im.size
    s = max(w / sw, h / sh)
    im = im.resize((int(sw * s) + 1, int(sh * s) + 1), Image.LANCZOS)
    x = (im.size[0] - w) // 2
    y = (im.size[1] - h) // 2
    im = im.crop((x, y, x + w, y + h))
    im = ImageEnhance.Color(im).enhance(1.06)
    im = ImageEnhance.Contrast(im).enhance(1.03)
    return im

def arch_mask(w, h):
    m = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(m)
    d.ellipse([0, 0, w, w], fill=255)
    d.rectangle([0, w // 2, w, h], fill=255)
    return m

def circle_mask(d):
    m = Image.new("L", (d, d), 0)
    ImageDraw.Draw(m).ellipse([0, 0, d, d], fill=255)
    return m

def paste_arch(img, photo_path, cx, top, w, h, border, border_color, shadow=True):
    ph = cover(photo_path, w, h)
    if shadow:
        sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ds = ImageDraw.Draw(sh)
        x0, y0 = cx - w // 2, top
        ds.ellipse([x0, y0 + 14, x0 + w, y0 + w + 14], fill=(0, 0, 0, 70))
        ds.rectangle([x0, y0 + w // 2 + 14, x0 + w, y0 + h + 14], fill=(0, 0, 0, 70))
        sh = sh.filter(ImageFilter.GaussianBlur(18))
        img.alpha_composite(sh)
    x0, y0 = cx - w // 2, top
    b = Image.new("RGBA", (w + border * 2, h + border * 2), (0, 0, 0, 0))
    db = ImageDraw.Draw(b)
    bw, bh = w + border * 2, h + border * 2
    db.ellipse([0, 0, bw, bw], fill=border_color + (255,))
    db.rectangle([0, bw // 2, bw, bh], fill=border_color + (255,))
    img.paste(b, (x0 - border, y0 - border), b)
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    layer.paste(ph, (0, 0))
    layer.putalpha(arch_mask(w, h))
    img.paste(layer, (x0, y0), layer)
    return (x0, y0, x0 + w, y0 + h)

def paste_circle(img, photo_path, cx, cy, d, ring_w, ring_color):
    ph = cover(photo_path, d, d)
    ImageDraw.Draw(img).ellipse([cx - d // 2 - ring_w, cy - d // 2 - ring_w,
                                 cx + d // 2 + ring_w, cy + d // 2 + ring_w],
                                fill=ring_color + (255,))
    layer = Image.new("RGBA", (d, d), (0, 0, 0, 0))
    layer.paste(ph, (0, 0))
    layer.putalpha(circle_mask(d))
    img.paste(layer, (cx - d // 2, cy - d // 2), layer)

def pill(img, box, fill, outline=None, width=3):
    d = ImageDraw.Draw(img)
    d.rounded_rectangle(box, radius=(box[3] - box[1]) // 2, fill=fill + (255,) if len(fill) == 3 else fill,
                        outline=(outline + (255,)) if outline else None, width=width)

def rbox(img, box, r, fill, outline=None, width=3):
    d = ImageDraw.Draw(img)
    d.rounded_rectangle(box, radius=r, fill=fill + (255,) if len(fill) == 3 else fill,
                        outline=(outline + (255,)) if outline else None, width=width)

def check_bullet(img, cx, cy, r, color):
    d = ImageDraw.Draw(img)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color + (255,))
    d.line([(cx - r * 0.5, cy + r * 0.05), (cx - r * 0.1, cy + r * 0.45),
            (cx + r * 0.55, cy - r * 0.4)], fill=(255, 255, 255, 255), width=max(3, r // 4), joint="curve")

def diamond(img, cx, cy, r, color):
    ImageDraw.Draw(img).polygon([(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)],
                                fill=color + (255,))

def heart(img, cx, cy, s, color):
    d = ImageDraw.Draw(img)
    r = s / 2
    d.ellipse([cx - s, cy - s * 0.9, cx, cy + r * 0.4], fill=color + (255,))
    d.ellipse([cx, cy - s * 0.9, cx + s, cy + r * 0.4], fill=color + (255,))
    d.polygon([(cx - s * 0.92, cy + r * 0.1), (cx + s * 0.92, cy + r * 0.1), (cx, cy + s)], fill=color + (255,))

def gift(img, cx, cy, s, box_color, ribbon_color):
    d = ImageDraw.Draw(img)
    w, h = s * 1.5, s
    d.rectangle([cx - w / 2, cy - h / 2 + s * 0.25, cx + w / 2, cy + h / 2 + s * 0.25], fill=box_color + (255,))
    d.rectangle([cx - w / 2 - s * 0.08, cy - h / 2, cx + w / 2 + s * 0.08, cy - h / 2 + s * 0.35], fill=box_color + (255,))
    d.rectangle([cx - s * 0.12, cy - h / 2, cx + s * 0.12, cy + h / 2 + s * 0.25], fill=ribbon_color + (255,))
    lw = max(3, int(s * 0.09))
    d.ellipse([cx - s * 0.42, cy - h / 2 - s * 0.32, cx, cy - h / 2 + s * 0.08], outline=ribbon_color + (255,), width=lw)
    d.ellipse([cx, cy - h / 2 - s * 0.32, cx + s * 0.42, cy - h / 2 + s * 0.08], outline=ribbon_color + (255,), width=lw)

def sparkle(img, cx, cy, r, color, alpha=255):
    d = ImageDraw.Draw(img)
    k = 0.22
    d.polygon([(cx, cy - r), (cx + r * k, cy - r * k), (cx + r, cy), (cx + r * k, cy + r * k),
               (cx, cy + r), (cx - r * k, cy + r * k), (cx - r, cy), (cx - r * k, cy - r * k)],
              fill=color + (alpha,))

def divider(img, y, color, cx=540, half=300):
    d = ImageDraw.Draw(img)
    d.line([(cx - half, y), (cx + half, y)], fill=color + (255,), width=3)
    diamond(img, cx, y, 12, color)

def stroke_text(img, xy, text, font, fill, stroke_fill, sw=3, anchor="mm", spacing=1.45):
    for dx in range(-sw, sw + 1):
        for dy in range(-sw, sw + 1):
            if dx == 0 and dy == 0:
                continue
            draw_fa(img, (xy[0] + dx, xy[1] + dy), text, font, stroke_fill, anchor=anchor, line_spacing=spacing)
    draw_fa(img, xy, text, font, fill, anchor=anchor, line_spacing=spacing)

def tag(img, label):
    f = F(AVINY, 26)
    w = f.measure(label) + 44
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([36, 52, 36 + w, 104], radius=26, fill=(0, 0, 0, 110))
    draw_fa(img, (36 + w / 2, 78), label, f, (255, 255, 255), anchor="mm")

def brand_top(img, y, color, sub=None, font_path=None):
    fp = font_path or HASTI_RRD
    draw_fa(img, (540, y), "منگوچ", F(fp, 54), color, anchor="mt")
    if sub:
        draw_fa(img, (540, y + 82), sub, F(AVINY, 28), color, anchor="mt")

# ---------- content ----------
ZW = "‌"
HM = "‌ئی‌"[1]
D1, D3, D7, D9, D0, SEP = "۱", "۳", "۷", "۹", "۰", "٬"
assert ZW == "‌" and HM == "‌ئی‌"[1]
SUB1 = "از صفر تا صد، مثل حرفه" + HM + "ی" + ZW + "ها"
SUB2 = "مناسب مبتدی" + ZW + "ها و حرفه" + HM + "ی" + ZW + "ها"
TOPICS_2COL = [
    ["مواد و ابزار مورد نیاز کار", D3 + " روش برتر پخت خمیر موچی",
     "طعم" + ZW + "دار کردن خمیر موچی",
     "اصول فرم دادن خامه", "مقاوم" + ZW + "سازی خامه در گرما"],
    [D3 + " فیلینگ پایه + فیلینگ پیشرفته", "اصول بقچه" + ZW + "بندی موچی",
     "خمیر توت" + ZW + "فرنگی منگوچ", "نگهداری و ماندگاری"],
]
TOPICS_1COL = ["معرفی مواد و ابزار مورد نیاز کار", "سه روش برتر پخت خمیر موچی",
               "طعم" + ZW + "دار کردن خمیر موچی", "اصول فرم دادن خامه",
               "مقاوم" + ZW + "سازی خامه در گرما",
               "سه مدل فیلینگ پایه + فیلینگ پیشرفته", "اصول بقچه" + ZW + "بندی موچی",
               "خمیر ویژه توت" + ZW + "فرنگی منگوچ", "اصول نگهداری و ماندگاری"]
ADV_DETAIL = "(براونی، دبی چاکلت، تیرامیسو، موچیز، مارمالاد و…)"
GIFT = "هدیه ویژه: رسپی براونی + چیزکیک سن" + ZW + "سباستین"
PRICE = D1 + SEP + D7 + D9 + D9 + SEP + D0 + D0 + D0 + " تومان"
CTA = "برای ثبت" + ZW + "نام دایرکت بده"
SEC_A = "تو این دوره یاد می" + ZW + "گیری:"
SEC_B = "سرفصل" + ZW + "های دوره:"
CTA_A = "ثبت" + ZW + "نام در دایرکت"
SUP = "پشتیبانی دائمی"

# ================= DESIGN A : cream bakery =================
def design_a(final=False):
    CREAM, BROWN, TERRA, GOLD = (250, 241, 230), (84, 39, 26), (193, 80, 46), (176, 124, 62)
    img = Image.new("RGBA", (W, H), CREAM + (255,))
    dots(img, (176, 124, 62), step=76, r=6, alpha=28)
    brand_top(img, 60, BROWN)
    if not final:
        tag(img, "پیش‌طرح A")
    paste_arch(img, "muchi.jpg", 540, 168, 640, 560, 12, TERRA)
    pill(img, [380, 688, 700, 776], TERRA)
    draw_fa(img, (540, 732), "دوره دوم", F(HASTI_RRD, 46), (255, 255, 255), anchor="mm")
    s = fit(HASTI_RRD, "آموزش موچی", 900, 116)
    draw_fa(img, (540, 800), "آموزش موچی", F(HASTI_RRD, s), BROWN, anchor="mt")
    ty = 800 + F(HASTI_RRD, s).height + 4
    draw_fa(img, (540, ty), SUB1, F(AVINY, 37), (138, 90, 59), anchor="mt")
    draw_fa(img, (540, ty + 58), SUB2, F(AVINY, 30), GOLD, anchor="mt")
    divider(img, int(ty + 128), GOLD)
    draw_fa(img, (990, int(ty + 152)), SEC_A, F(HASTI_RRD, 44), TERRA, anchor="rt")
    pill(img, [70, int(ty + 156), 420, int(ty + 222)], TERRA)
    heart(img, 340, int(ty + 189), 22, (255, 255, 255))
    draw_fa(img, (295, int(ty + 189)), SUP, F(HASTI_RRD, 30), (255, 255, 255), anchor="rm")
    y0, step = int(ty + 242), 60
    cols_x = [990, 500]
    for ci, col in enumerate(TOPICS_2COL):
        for i, t in enumerate(col):
            y = y0 + i * step
            fs = fit(AVINY, t, 400, 33, 24)
            check_bullet(img, cols_x[ci] - 2, y + F(AVINY, fs).height / 2 - 6, 15, TERRA)
            draw_fa(img, (cols_x[ci] - 30, y), t, F(AVINY, fs), BROWN, anchor="rt")
    dy = y0 + 5 * step + 2
    draw_fa(img, (540, dy), ADV_DETAIL, F(AVINY, 27), (138, 90, 59), anchor="mt")
    gy = dy + 52
    rbox(img, [70, gy, 1010, gy + 88], 44, (255, 255, 255), TERRA, 3)
    gift(img, 905, gy + 44, 32, TERRA, GOLD)
    gs = fit(HASTI_RRD, GIFT, 640, 35, 24)
    draw_fa(img, (830, gy + 44), GIFT, F(HASTI_RRD, gs), BROWN, anchor="rm")
    py = gy + 104
    draw_fa(img, (785, py), "هزینه دوره", F(AVINY, 28), BROWN, anchor="mm")
    pill(img, [560, py + 44, 1010, py + 140], BROWN)
    ps = fit(AVINY, PRICE, 400, 52, 30)
    draw_fa(img, (785, py + 92), PRICE, F(AVINY, ps), (245, 214, 150), anchor="mm")
    pill(img, [70, py + 44, 520, py + 140], TERRA)
    draw_fa(img, (295, py + 92), CTA_A, F(HASTI_RRD, 36), (255, 255, 255), anchor="mm")
    return img

# ================= DESIGN B : dark luxe =================
def design_b():
    TOP, BOT = (30, 15, 8), (88, 40, 18)
    GOLD, CREAM, PINK = (232, 185, 106), (247, 235, 220), (214, 120, 110)
    DARK = (43, 21, 12)
    img = vgradient(W, H, TOP, BOT).convert("RGBA")
    dots(img, GOLD, step=84, r=6, alpha=30)
    for (x, y, r) in [(140, 300, 26), (950, 620, 20), (120, 1050, 18), (140, 1500, 24), (880, 200, 14)]:
        sparkle(img, x, y, r, GOLD, 90)
    brand_top(img, 60, GOLD, font_path=HASTI_S)
    tag(img, "پیش‌طرح B")
    paste_circle(img, "mochi-slice.jpg", 790, 420, 350, 8, GOLD)
    pill(img, [300, 240, 560, 308], GOLD)
    draw_fa(img, (430, 274), "دوره دوم", F(HASTI_S, 42), DARK, anchor="mm")
    tf = F(HASTI_S, 102)
    draw_fa(img, (560, 322), "آموزش\nموچی", tf, CREAM, anchor="rt", line_spacing=1.08,
            shadow=((0, 0, 0), 3, 4))
    tt = 322 + tf.height * 1.08 + tf.height + 10
    draw_fa(img, (560, tt), SUB1, F(AVINY, 35), GOLD, anchor="rt")
    draw_fa(img, (560, tt + 58), SUB2, F(AVINY, 29), CREAM, anchor="rt")
    divider(img, int(tt + 128), GOLD, half=380)
    draw_fa(img, (990, int(tt + 152)), SEC_B, F(HASTI_S, 46), GOLD, anchor="rt")
    y0, step = int(tt + 232), 62
    for i, t in enumerate(TOPICS_1COL):
        y = y0 + i * step
        fs = fit(AVINY, t, 830, 36, 26)
        diamond(img, 962, y + F(AVINY, fs).height / 2 - 8, 11, GOLD)
        draw_fa(img, (925, y), t, F(AVINY, fs), CREAM, anchor="rt")
    draw_fa(img, (925, y0 + 9 * step - 6), ADV_DETAIL, F(AVINY, 28), GOLD, anchor="rt")
    gy = y0 + 9 * step + 48
    rbox(img, [70, gy, 1010, gy + 88], 30, GOLD)
    gift(img, 900, gy + 44, 30, DARK, DARK)
    gs = fit(HASTI_S, GIFT, 640, 34, 24)
    draw_fa(img, (825, gy + 44), GIFT, F(HASTI_S, gs), DARK, anchor="rm")
    py = gy + 104
    draw_fa(img, (990, py), "هزینه دوره", F(AVINY, 28), CREAM, anchor="rt")
    ps = fit(AVINY, PRICE, 380, 62, 34)
    draw_fa(img, (990, py + 38), PRICE, F(AVINY, ps), GOLD, anchor="rt", shadow=((0, 0, 0), 2, 3))
    sup = "پشتیبانی دائمی دوره"
    sf = F(AVINY, 30)
    draw_fa(img, (990, py + 150), sup, sf, CREAM, anchor="rt")
    heart(img, 990 - sf.measure(sup) - 32, py + 150 + sf.height / 2 - 4, 17, PINK)
    pill(img, [70, py + 42, 520, py + 146], (193, 80, 46))
    cs = fit(HASTI_S, CTA, 400, 36, 24)
    draw_fa(img, (295, py + 94), CTA, F(HASTI_S, cs), (255, 255, 255), anchor="mm")
    return img

# ================= DESIGN C : pink playful =================
def design_c():
    TOP, BOT = (253, 214, 224), (248, 183, 198)
    RASP, MAROON, YELLOW = (164, 19, 60), (110, 26, 44), (255, 224, 138)
    img = vgradient(W, H, TOP, BOT).convert("RGBA")
    dots(img, (255, 255, 255), step=70, r=8, alpha=70)
    for (x, y, r) in [(90, 420, 30), (990, 350, 22), (80, 1250, 20), (1000, 1100, 28), (930, 1620, 18), (150, 1700, 22)]:
        sparkle(img, x, y, r, (255, 255, 255), 140)
    brand_top(img, 56, MAROON)
    tag(img, "پیش‌طرح C")
    paste_arch(img, "Cake-muchi.jpg", 540, 190, 630, 520, 14, (255, 255, 255))
    st = Image.new("RGBA", (420, 150), (0, 0, 0, 0))
    ImageDraw.Draw(st).rounded_rectangle([8, 8, 412, 142], radius=60, fill=RASP + (255,))
    draw_fa(st, (210, 75), "دوره دوم", F(HASTI_R, 52), (255, 255, 255), anchor="mm")
    st = st.rotate(10, expand=True, resample=Image.BICUBIC)
    img.alpha_composite(st, (660, 575))
    s = fit(HASTI_R, "آموزش موچی", 880, 116)
    stroke_text(img, (540, 830), "آموزش موچی", F(HASTI_R, s), RASP, (255, 255, 255), sw=2, anchor="mt")
    th = F(HASTI_R, s).height
    draw_fa(img, (540, 830 + th + 2), SUB1, F(AVINY, 36), MAROON, anchor="mt")
    draw_fa(img, (540, 830 + th + 58), SUB2 + " + پشتیبانی دائمی",
            F(AVINY, 28), MAROON, anchor="mt")
    cols = [TOPICS_2COL[0], TOPICS_2COL[1]]
    cw, chh, gap = 462, 70, 18
    yc = 830 + th + 128
    for ci, col in enumerate(cols):
        xx = 548 if ci == 0 else 70
        for r, t in enumerate(col):
            yy = yc + r * (chh + gap)
            rbox(img, [xx, yy, xx + cw, yy + chh], 35, (255, 255, 255))
            if ci == 0:
                check_bullet(img, xx + cw - 44, yy + chh / 2, 15, RASP)
                fs = fit(AVINY, t, cw - 110, 30, 22)
                draw_fa(img, (xx + cw - 76, yy + chh / 2), t, F(AVINY, fs), MAROON, anchor="rm")
            else:
                check_bullet(img, xx + 44, yy + chh / 2, 15, RASP)
                fs = fit(AVINY, t, cw - 110, 30, 22)
                draw_fa(img, (xx + cw - 28, yy + chh / 2), t, F(AVINY, fs), MAROON, anchor="rm")
    draw_fa(img, (540, yc + 5 * (chh + gap) - 8), ADV_DETAIL, F(AVINY, 27), MAROON, anchor="mt")
    gy = yc + 5 * (chh + gap) + 34
    rbox(img, [70, gy, 1010, gy + 84], 42, YELLOW)
    gift(img, 900, gy + 42, 30, RASP, MAROON)
    gs = fit(HASTI_R, GIFT, 640, 33, 22)
    draw_fa(img, (830, gy + 42), GIFT, F(HASTI_R, gs), MAROON, anchor="rm")
    py = gy + 102
    ps = fit(AVINY, PRICE, 400, 48, 26)
    rbox(img, [560, py, 1010, py + 100], 50, (255, 255, 255))
    draw_fa(img, (785, py + 50), PRICE, F(AVINY, ps), RASP, anchor="mm")
    pill(img, [70, py, 520, py + 100], RASP)
    cs = fit(HASTI_R, CTA, 400, 33, 22)
    draw_fa(img, (295, py + 50), CTA, F(HASTI_R, cs), (255, 255, 255), anchor="mm")
    return img


if __name__ == "__main__":
    out = os.path.join(ROOT, "design")
    for name, fn in [("story-A-cream", lambda: design_a()), ("story-B-dark", design_b),
                     ("story-C-pink", design_c), ("story-final-A", lambda: design_a(final=True))]:
        img = fn()
        p = os.path.join(out, name + ".png")
        img.convert("RGB").save(p, quality=92)
        print("saved", p, img.size)
