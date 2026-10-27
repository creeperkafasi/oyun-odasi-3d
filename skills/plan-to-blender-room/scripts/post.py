"""Post: bloom (multi-scale), mild vignette. Usage: post.py in.png out.png [strength]"""
import sys
import numpy as np
from PIL import Image, ImageFilter
src, dst = sys.argv[1], sys.argv[2]
k = float(sys.argv[3]) if len(sys.argv) > 3 else 0.35
im = Image.open(src).convert("RGB")
a = np.asarray(im).astype(np.float32) / 255.0
lum = a @ np.array([0.2126, 0.7152, 0.0722], np.float32)
mask = np.clip((lum - 0.62) / 0.38, 0, 1)[..., None]
hi = (a * mask * 255).astype(np.uint8)
hi_im = Image.fromarray(hi)
bloom = np.zeros_like(a)
w = im.width
for r, wt in ((w * 0.004, 0.5), (w * 0.012, 0.35), (w * 0.035, 0.25)):
    bloom += np.asarray(hi_im.filter(ImageFilter.GaussianBlur(r))).astype(np.float32) / 255.0 * wt
out = 1 - (1 - a) * (1 - np.clip(bloom * k * 2.2, 0, 1))      # screen blend
yy, xx = np.mgrid[0:im.height, 0:im.width]
d = np.sqrt(((xx - im.width / 2) / (im.width / 2)) ** 2 + ((yy - im.height / 2) / (im.height / 2)) ** 2)
out *= (1 - 0.18 * np.clip(d - 0.45, 0, 1) ** 1.5)[..., None]
Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8)).save(dst)
