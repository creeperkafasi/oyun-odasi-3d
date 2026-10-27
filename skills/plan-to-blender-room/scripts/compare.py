"""Reference vs render: side-by-side (and 50 % overlay).
Usage: python3 compare.py ref.jpg render.png out_prefix [side|overlay|both]"""
import sys
from PIL import Image, ImageOps
ref = Image.open(sys.argv[1]).convert("RGB"); ren = Image.open(sys.argv[2]).convert("RGB").resize(ref.size)
pre = sys.argv[3]; mode = sys.argv[4] if len(sys.argv) > 4 else "side"
w, h = ref.size
if mode in ("side", "both"):
    sb = Image.new("RGB", (w * 2, h)); sb.paste(ref, (0, 0)); sb.paste(ren, (w, 0))
    sb.resize((min(w * 2, 1600), int(h * min(w * 2, 1600) / (w * 2)))).save(pre + "_side.png")
if mode in ("overlay", "both"):
    Image.blend(ImageOps.autocontrast(ref), ren, 0.5).save(pre + "_ovl.png")
