"""Copy final renders into the artifact folder as JPEGs."""
import sys, os
from PIL import Image
root = "/home/denizt/dev/claude-mimar/out"
dst = sys.argv[1]
os.makedirs(dst, exist_ok=True)
def jpg(src, out, size=None, q=88, bg=(11, 13, 19)):
    im = Image.open(src)
    if im.mode == "RGBA":
        base = Image.new("RGB", im.size, bg); base.paste(im, mask=im.split()[3]); im = base
    im = im.convert("RGB")
    if size: im = im.resize(size, Image.LANCZOS)
    im.save(os.path.join(dst, out), quality=q)
jpg(f"{root}/final/01_ana_gorunum.png", "render.jpg")
for c, n in (("back", "02"), ("desk", "03"), ("sofa", "04"), ("top", "05")):
    p = f"{root}/final/{n}_{c}.png"
    if os.path.exists(p):
        jpg(p, f"v_{c}.jpg", q=85)
for it in ("17", "18"):
    jpg(f"{root}/it{it}_post.png", f"it{it}.jpg", size=(560, 421), q=80)
print("ok")
