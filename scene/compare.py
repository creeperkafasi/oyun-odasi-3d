"""Side-by-side + 50% overlay of a render vs the reference image."""
import sys
from PIL import Image, ImageChops, ImageOps
ref = Image.open(sys.argv[1]).convert("RGB")
ren = Image.open(sys.argv[2]).convert("RGB").resize(ref.size)
out = sys.argv[3]
mode = sys.argv[4] if len(sys.argv) > 4 else "both"
w, h = ref.size
if mode in ("both", "side"):
    sb = Image.new("RGB", (w * 2, h)); sb.paste(ref, (0, 0)); sb.paste(ren, (w, 0))
    sb = sb.resize((w, h // 2)); sb.save(out.replace(".png", "_side.png"))
if mode in ("both", "overlay"):
    Image.blend(ImageOps.autocontrast(ref), ren, 0.5).save(out.replace(".png", "_ovl.png"))
