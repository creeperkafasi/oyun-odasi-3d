import sys
from PIL import Image, ImageDraw
im = Image.open(sys.argv[1]).convert("RGB")
x0, y0, x1, y1 = map(int, sys.argv[2:6]); sc = int(sys.argv[6]); out = sys.argv[7]
step = int(sys.argv[8]) if len(sys.argv) > 8 else 10
c = im.crop((x0, y0, x1, y1)).resize(((x1 - x0) * sc, (y1 - y0) * sc), Image.NEAREST)
d = ImageDraw.Draw(c)
for x in range((x0 // step + 1) * step, x1, step):
    X = (x - x0) * sc
    d.line([(X, 0), (X, c.height)], fill=(255, 0, 0) if x % (step*5) == 0 else (120, 0, 0), width=1)
    if x % (step*5) == 0: d.text((X + 2, 2), str(x), fill=(255, 255, 0))
for y in range((y0 // step + 1) * step, y1, step):
    Y = (y - y0) * sc
    d.line([(0, Y), (c.width, Y)], fill=(0, 255, 0) if y % (step*5) == 0 else (0, 110, 0), width=1)
    if y % (step*5) == 0: d.text((2, Y + 2), str(y), fill=(0, 255, 255))
c.save(out)
