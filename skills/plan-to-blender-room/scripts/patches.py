"""Measure brightness/colour differences between reference and render, region by region.

Usage: python3 patches.py ref.jpg render.png [regions.json]
regions.json: {"floor_near": [x, y, half_size], ...} in reference pixels.
Without it a 4x3 grid is used. ratio = render luminance / reference luminance;
>1.3 means the render is too bright there, <0.7 too dark. Only trust regions
where both images show the same thing (geometry can differ slightly)."""
import sys, json
import numpy as np
from PIL import Image
ref = np.asarray(Image.open(sys.argv[1]).convert("RGB")).astype(float)
H, W = ref.shape[:2]
ren = np.asarray(Image.open(sys.argv[2]).convert("RGB").resize((W, H))).astype(float)
if len(sys.argv) > 3:
    P = json.load(open(sys.argv[3]))
else:
    P = {f"r{r}c{c}": (int(W * (c + 0.5) / 4), int(H * (r + 0.5) / 3), int(min(W, H) / 10)) for r in range(3) for c in range(4)}
print(f"{'region':14s} {'ref RGB':>16s} {'render RGB':>16s}  ratio")
for k, (x, y, r) in P.items():
    a = ref[y - r:y + r, x - r:x + r].reshape(-1, 3).mean(0); b = ren[y - r:y + r, x - r:x + r].reshape(-1, 3).mean(0)
    print(f"{k:14s} {str(a.astype(int)):>16s} {str(b.astype(int)):>16s}  {b.mean() / max(1, a.mean()):.2f}")
