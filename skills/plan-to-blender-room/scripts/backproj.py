"""Back-project reference-image pixels onto a horizontal plane (default the floor).

Usage: python3 backproj.py camera.json u,v[,z] [u,v[,z] ...]
Prints the plan (x, y) where each pixel's ray hits height z. Use it to place
furniture where the reference shows it: pick the pixel where a leg/edge meets
the floor (z=0) or a desk top edge (z=0.75) etc.
"""
import json, sys
import numpy as np
cam = json.load(open(sys.argv[1]))
W, H = cam["image"]
a = np.radians(cam["rot_z_deg"] + 90.0)
fwd = np.array([np.cos(a), np.sin(a), 0.0]); right = np.array([np.sin(a), -np.cos(a), 0.0]); up = np.array([0, 0, 1.0])
o = np.array(cam["loc"], float); f = cam["f_px"]
for arg in sys.argv[2:]:
    vals = [float(t) for t in arg.split(",")]
    u, v = vals[:2]; z = vals[2] if len(vals) > 2 else 0.0
    x = (u - W / 2 + cam["shift_x"] * W) / f; y = -(v - H / 2 - cam["shift_y"] * W) / f
    d = fwd + x * right + y * up
    if abs(d[2]) < 1e-9 or (z - o[2]) / d[2] < 0:
        print(f"({u:.0f},{v:.0f}) z={z}: ray never reaches that height"); continue
    p = o + (z - o[2]) / d[2] * d
    print(f"({u:.0f},{v:.0f}) z={z} -> x={p[0]:.3f} y={p[1]:.3f}")
