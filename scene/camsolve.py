"""Least-squares camera fit: 3D points (plan coords) -> pixels in the AI render."""
import numpy as np, sys
from scipy.optimize import least_squares
Wpx, Hpx = 1447, 1087
D = 3.63
PTS = [  # (X, Y, Z) -> (u, v)
    ((-0.06, 1.20, 2.35), (453, 210)),
    ((-0.06, 2.71, 2.35), (712, 210)),
    ((-0.06, 1.20, 1.10), (453, 378)),
    ((-0.06, 2.71, 1.10), (712, 378)),
    ((0.726, D, 2.12), (940, 208)),
    ((1.50, D, 2.12), (1017, 183)),
    ((1.425, D, 1.02), (1005, 407)),
    ((0.40, 0.04, 2.55), (322, 182)),
    ((0.40, 0.60, 2.55), (400, 182)),
    ((0.40, 0.04, 0.0), (322, 545)),
    ((0.42, 2.80, 2.55), (737, 182)),
    ((0.42, 2.80, 0.98), (737, 395)),
    # sliding door (south wall): west end + panel mullions at floor
    ((0.53, -0.07, 2.45), (235, 175)),
    ((0.53, -0.07, 0.02), (235, 592)),
    ((1.36, -0.07, 0.02), (172, 612)),
    ((2.19, -0.07, 0.02), (91, 665)),
]
X = np.array([p[0] for p in PTS]); U = np.array([p[1] for p in PTS], float)

def project(params, X):
    cx, cy, cz, yaw, f, sx, sy = params
    a = np.radians(yaw)
    fwd = np.array([-np.cos(a), -np.sin(a), 0]); right = np.array([-np.sin(a), np.cos(a), 0]); up = np.array([0, 0, 1.0])
    d = X - np.array([cx, cy, cz])
    z = d @ fwd; x = d @ right; y = d @ up
    u = Wpx / 2 + f * x / z - sx * Wpx
    v = Hpx / 2 - f * y / z + sy * Wpx
    return np.stack([u, v], 1)

def res(p, fixed=None):
    return (project(p, X) - U).ravel()

p0 = [5.1, 1.8, 1.4, 0, 744, 0.11, -0.14]
lo = [3.0, 0.5, 0.8, -20, 300, -0.5, -0.5]; hi = [5.23, 3.2, 2.2, 20, 2000, 0.5, 0.5]
r = least_squares(res, p0, bounds=(lo, hi))
p = r.x
print("cam x y z = %.3f %.3f %.3f  yaw=%.2f  f=%.1fpx (lens %.2fmm)  shift=%.3f %.3f" % (p[0], p[1], p[2], p[3], p[4], p[4] / Wpx * 36, p[5], p[6]))
err = project(p, X) - U
for (pt, uv), e in zip(PTS, err):
    print(pt, uv, np.round(e, 1))
print("rms", np.sqrt((err ** 2).mean()))

print("---- yaw fixed sweeps")
for yaw in (0, 4, 8, 12):
    def res3(q): return res([q[0], q[1], q[2], yaw, q[3], q[4], q[5]])
    r3 = least_squares(res3, [5.0, 1.5, 1.4, 744, 0.11, -0.14], bounds=([2.5, 0.3, 0.8, 300, -0.6, -0.6], [5.23, 3.3, 2.2, 2000, 0.6, 0.6]))
    q = r3.x; e3 = res3(q).reshape(-1, 2)
    print("yaw %d -> x %.2f y %.3f z %.3f f %.1f (%.2fmm) shift %.3f %.3f rms %.1f" % (yaw, q[0], q[1], q[2], q[3], q[3] / Wpx * 36, q[4], q[5], np.sqrt((e3 ** 2).mean())))
