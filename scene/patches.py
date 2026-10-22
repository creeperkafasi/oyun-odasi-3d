import sys
from PIL import Image
import numpy as np
ref = np.asarray(Image.open("ref/render.jpg").convert("RGB")).astype(float)
ren = np.asarray(Image.open(sys.argv[1]).convert("RGB").resize((1447, 1087))).astype(float)
P = {"floor_near": (700, 1000, 60), "floor_mid": (640, 700, 30), "ceiling": (700, 30, 30), "ceiling_L": (420, 60, 25),
     "backwall_top": (600, 185, 15), "window_sky": (520, 330, 12), "glass_sky": (40, 250, 25), "terrace_floor": (60, 600, 25),
     "curtain": (265, 330, 12), "rug_round": (330, 820, 30), "rug_rect": (1000, 900, 30), "sofa": (280, 700, 20),
     "door_wood": (975, 300, 15), "slats": (1250, 120, 20), "desk_top": (1300, 610, 10), "shelfL": (360, 300, 10), "shelfR": (790, 420, 10)}
print(f"{'region':14s} {'ref':>16s} {'mine':>16s}  ratio(L)")
for k, (x, y, r) in P.items():
    a = ref[y - r:y + r, x - r:x + r].reshape(-1, 3).mean(0); b = ren[y - r:y + r, x - r:x + r].reshape(-1, 3).mean(0)
    print(f"{k:14s} {str(a.astype(int)):>16s} {str(b.astype(int)):>16s}  {b.mean() / max(1, a.mean()):.2f}")
