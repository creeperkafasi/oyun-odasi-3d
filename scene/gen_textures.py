"""Generate screen / poster textures with numpy + PIL."""
import numpy as np, os, random
from PIL import Image, ImageDraw, ImageFilter
OUT = os.path.join(os.path.dirname(__file__), "..", "tex")
rng = np.random.default_rng(7)


def ridge(w, base, amp, rough, seed):
    r = np.random.default_rng(seed)
    y = np.zeros(w)
    for k, a in ((2, 1.0), (5, 0.5), (11, 0.25), (23, 0.12), (51, 0.06)):
        ph = r.uniform(0, 6.28)
        y += a * np.sin(np.linspace(0, k * np.pi, w) + ph) * (rough if k > 10 else 1)
    return base - amp * y


def mountain_wallpaper(w=1280, h=720, glow=1.0):
    yy, xx = np.mgrid[0:h, 0:w] / np.array([h, w])[:, None, None]
    sky_top = np.array([0.02, 0.05, 0.20]); sky_hor = np.array([0.35, 0.55, 0.95])
    t = np.clip(yy / 0.55, 0, 1)[..., None]
    img = sky_top * (1 - t) + sky_hor * t
    # glow behind central peak
    d = np.sqrt(((xx - 0.5) * 1.6) ** 2 + (yy - 0.42) ** 2)
    img += (np.exp(-d * 6) * 0.9 * glow)[..., None] * np.array([0.6, 0.8, 1.0])
    # light beam
    beam = np.exp(-np.abs(xx - 0.5) * 220) * (yy < 0.42)
    img += beam[..., None] * np.array([0.8, 0.9, 1.0]) * 1.2
    im = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8))
    dr = ImageDraw.Draw(im)
    layers = [(0.50, 0.10, (40, 70, 140), 1), (0.58, 0.08, (25, 45, 105), 2), (0.66, 0.06, (14, 26, 70), 3)]
    for base, amp, col, sd in layers:
        ys = ridge(w, base * h, amp * h, 0.6, sd)
        poly = [(0, h)] + [(x, ys[x]) for x in range(w)] + [(w, h)]
        dr.polygon(poly, fill=col)
    # central peak (pyramid)
    dr.polygon([(w * 0.5, h * 0.30), (w * 0.38, h * 0.62), (w * 0.62, h * 0.62)], fill=(30, 55, 120))
    dr.polygon([(w * 0.5, h * 0.30), (w * 0.5, h * 0.62), (w * 0.62, h * 0.62)], fill=(18, 34, 85))
    dr.ellipse([w * 0.5 - 6, h * 0.30 - 6, w * 0.5 + 6, h * 0.30 + 6], fill=(230, 240, 255))
    # snowy road / reflection to the bottom
    dr.polygon([(w * 0.47, h * 0.66), (w * 0.53, h * 0.66), (w * 0.75, h), (w * 0.25, h)], fill=(90, 120, 190))
    dr.polygon([(w * 0.495, h * 0.66), (w * 0.505, h * 0.66), (w * 0.53, h), (w * 0.47, h)], fill=(200, 220, 255))
    im = im.filter(ImageFilter.GaussianBlur(1.2))
    return im


def editor_ui(w=1600, h=680):
    im = Image.new("RGB", (w, h), (22, 24, 30))
    dr = ImageDraw.Draw(im)
    wall = mountain_wallpaper(640, 360)
    # left: preview of wallpaper; right: program monitor
    im.paste(wall.resize((560, 315)), (20, 40))
    prog = mountain_wallpaper(640, 360, glow=0.6).resize((520, 292))
    im.paste(prog, (620, 40))
    dr.rectangle([620, 40, 1140, 332], outline=(80, 90, 110))
    # small thumbnails
    for i in range(4):
        th = mountain_wallpaper(320, 180, glow=0.3 + 0.2 * i).resize((120, 68))
        im.paste(th, (620 + i * 130, 350))
    # right panel: lines of text
    for i in range(22):
        y = 40 + i * 14
        dr.rectangle([1170, y, 1170 + random.randint(80, 380), y + 6], fill=(70, 75, 90) if i % 4 else (110, 150, 230))
    # timeline
    dr.rectangle([0, 440, w, h], fill=(16, 17, 22))
    cols = [(60, 110, 220), (50, 160, 210), (120, 90, 200), (40, 140, 120), (200, 120, 60)]
    for tr in range(7):
        y = 460 + tr * 30
        x = 40
        while x < w - 60:
            L = random.randint(60, 300)
            dr.rectangle([x, y, min(w - 40, x + L), y + 22], fill=cols[(tr + x) % len(cols)])
            x += L + random.randint(4, 30)
    dr.line([(700, 440), (700, h)], fill=(240, 80, 80), width=3)
    return im


def side_screen(w=500, h=900):
    yy, xx = np.mgrid[0:h, 0:w] / np.array([h, w])[:, None, None]
    img = np.zeros((h, w, 3)) + np.array([0.02, 0.04, 0.15])
    for k in range(9):
        cx = 0.5 + 0.3 * np.sin(k * 1.7)
        d = np.abs((xx - cx) * 3 + (yy - 0.5) * (k - 4) * 0.4)
        img += np.exp(-d * 8)[..., None] * np.array([0.25, 0.4, 1.0]) * 0.35
    img += np.exp(-np.abs(xx - 0.5) * 30)[..., None] * np.array([0.6, 0.75, 1.0]) * 0.6
    return Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8))


def streamdeck(w=480, h=320):
    im = Image.new("RGB", (w, h), (10, 10, 14))
    dr = ImageDraw.Draw(im)
    cols = [(60, 120, 255), (90, 200, 255), (255, 255, 255), (130, 90, 255), (60, 220, 160), (255, 160, 60)]
    for r in range(3):
        for c in range(5):
            x0, y0 = 20 + c * 92, 20 + r * 98
            dr.rounded_rectangle([x0, y0, x0 + 78, y0 + 80], 10, fill=(25, 30, 45))
            dr.ellipse([x0 + 22, y0 + 20, x0 + 56, y0 + 54], fill=random.choice(cols))
    return im


def poster(w=400, h=300, seed=1):
    r = random.Random(seed)
    im = mountain_wallpaper(w * 2, h * 2, glow=0.5).resize((w, h))
    dr = ImageDraw.Draw(im)
    dr.rectangle([0, int(h * 0.55), w, h], fill=(30, 30, 34))
    # silhouette of a car / character
    dr.polygon([(w * 0.2, h * 0.75), (w * 0.35, h * 0.55), (w * 0.7, h * 0.55), (w * 0.85, h * 0.75)], fill=(20, 20, 24))
    dr.ellipse([w * 0.25, h * 0.7, w * 0.38, h * 0.85], fill=(5, 5, 5)); dr.ellipse([w * 0.65, h * 0.7, w * 0.78, h * 0.85], fill=(5, 5, 5))
    return im


def game_spines(w=1024, h=256, seed=3):
    r = random.Random(seed)
    im = Image.new("RGB", (w, h), (10, 20, 60))
    dr = ImageDraw.Draw(im)
    x = 0
    while x < w:
        bw = r.randint(14, 22)
        base = (r.randint(10, 40), r.randint(30, 70), r.randint(110, 200))
        dr.rectangle([x, 0, x + bw - 2, h], fill=base)
        dr.rectangle([x + 3, 20, x + bw - 5, 40], fill=(230, 230, 240))
        for k in range(r.randint(2, 5)):
            yy = r.randint(60, h - 30)
            dr.rectangle([x + 4, yy, x + bw - 6, yy + r.randint(8, 40)], fill=(200, 210, 230) if r.random() < 0.5 else (20, 20, 30))
        dr.rectangle([x + bw - 2, 0, x + bw, h], fill=(5, 5, 10))
        x += bw
    return im


random.seed(5)
mountain_wallpaper().save(os.path.join(OUT, "wallpaper.png"))
editor_ui().save(os.path.join(OUT, "editor.png"))
side_screen().save(os.path.join(OUT, "side.png"))
streamdeck().save(os.path.join(OUT, "streamdeck.png"))
poster(seed=1).save(os.path.join(OUT, "poster1.png"))
poster(seed=2).save(os.path.join(OUT, "poster2.png"))
game_spines().save(os.path.join(OUT, "spines.png"))
print("ok")
