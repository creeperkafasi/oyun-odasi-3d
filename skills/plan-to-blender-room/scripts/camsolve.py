"""Fit a Blender camera to a reference image from 3D<->pixel correspondences.

Usage:  python3 camsolve.py points.json [--fix-yaw DEG] [--fix-x X] > camera.json

points.json:
{
  "image": [1447, 1087],                 # reference width, height in px
  "forward": "-X",                        # rough view direction: -X, +X, -Y, +Y
  "points": [ {"xyz": [x, y, z], "uv": [u, v], "note": "window top-left"}, ... ],
  "bounds": {"x": [0, 5.2], "y": [0, 3.6], "z": [0.8, 2.0]}   # optional camera position box
}
Model: pinhole, no pitch/roll (verticals stay vertical, like archviz renders),
horizon offset handled by lens shift. Coordinates: metres, Z up.
Output JSON is ready for template_build.py (loc, yaw_deg, lens_mm, shift_x, shift_y).
"""
import json, sys, argparse
import numpy as np
from scipy.optimize import least_squares

ap = argparse.ArgumentParser()
ap.add_argument("points")
ap.add_argument("--fix-yaw", type=float)
ap.add_argument("--fix-x", type=float)
ap.add_argument("--sensor", type=float, default=36.0)
A = ap.parse_args()
cfg = json.load(open(A.points))
Wpx, Hpx = cfg["image"]
BASE = {"-X": 180.0, "+X": 0.0, "-Y": 270.0, "+Y": 90.0}[cfg.get("forward", "-X")]
X = np.array([p["xyz"] for p in cfg["points"]], float)
U = np.array([p["uv"] for p in cfg["points"]], float)


def project(cx, cy, cz, yaw, f, sx, sy):
    a = np.radians(BASE + yaw)
    fwd = np.array([np.cos(a), np.sin(a), 0.0])
    right = np.array([np.sin(a), -np.cos(a), 0.0])
    d = X - np.array([cx, cy, cz])
    z = d @ fwd
    u = Wpx / 2 + f * (d @ right) / z - sx * Wpx
    v = Hpx / 2 - f * d[:, 2] / z + sy * Wpx
    return np.stack([u, v], 1)


names = ["cx", "cy", "cz", "yaw", "f", "sx", "sy"]
b = cfg.get("bounds", {})
lo = [b.get("x", [-50, 50])[0], b.get("y", [-50, 50])[0], b.get("z", [0.5, 3])[0], -45, 150, -0.6, -0.6]
hi = [b.get("x", [-50, 50])[1], b.get("y", [-50, 50])[1], b.get("z", [0.5, 3])[1], 45, 4000, 0.6, 0.6]
c = X.mean(0)
p0 = [np.clip(c[0], lo[0], hi[0]), np.clip(c[1], lo[1], hi[1]), 1.4, 0, Wpx * 0.6, 0, -0.1]
fixed = {}
if A.fix_yaw is not None: fixed["yaw"] = A.fix_yaw
if A.fix_x is not None: fixed["cx"] = A.fix_x
free = [i for i, n in enumerate(names) if n not in fixed]


def full(q):
    p = [0] * 7
    for i, n in enumerate(names):
        p[i] = fixed[n] if n in fixed else None
    for k, i in enumerate(free):
        p[i] = q[k]
    return p


def res(q):
    return (project(*full(q)) - U).ravel()


p0 = [min(max(v, lo[i] + 1e-6), hi[i] - 1e-6) for i, v in enumerate(p0)]
best = None
for yaw0 in (-15, 0, 15):       # a few starts; the problem is mildly non-convex
    s = list(p0); s[3] = yaw0
    r = least_squares(res, [s[i] for i in free], bounds=([lo[i] for i in free], [hi[i] for i in free]))
    if best is None or r.cost < best.cost:
        best = r
p = full(best.x)
err = project(*p) - U
out = {
    "loc": [round(p[0], 4), round(p[1], 4), round(p[2], 4)],
    "rot_z_deg": round(BASE + p[3] - 90.0, 3),                  # Blender rotation_euler.z (x rot = 90)
    "f_px": round(p[4], 2), "lens_mm": round(p[4] / Wpx * A.sensor, 3),
    "shift_x": round(p[5], 4), "shift_y": round(p[6], 4),
    "rms_px": round(float(np.sqrt((err ** 2).mean())), 2),
    "image": [Wpx, Hpx],
    "residuals": [{"note": q.get("note", ""), "du": round(float(e[0]), 1), "dv": round(float(e[1]), 1)}
                  for q, e in zip(cfg["points"], err)],
}
json.dump(out, sys.stdout, indent=1)
print()
