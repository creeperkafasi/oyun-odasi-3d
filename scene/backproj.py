import numpy as np
Wpx, Hpx = 1447, 1087
CAM = (4.731, 1.744, 1.220, 8.73, 700.0, 0.191, -0.115)
def ray(u, v, cam=CAM):
    cx, cy, cz, yaw, f, sx, sy = cam
    a = np.radians(yaw)
    fwd = np.array([-np.cos(a), -np.sin(a), 0]); right = np.array([-np.sin(a), np.cos(a), 0]); up = np.array([0, 0, 1.0])
    x = (u - Wpx / 2 + sx * Wpx) / f; y = -(v - Hpx / 2 - sy * Wpx) / f
    return np.array([cx, cy, cz]), fwd + x * right + y * up
def at_z(u, v, z=0.0):
    o, d = ray(u, v); t = (z - o[2]) / d[2]; return o + t * d
pts = {
 "VR left": (433, 568), "VR right": (730, 568), "VR back": (583, 540), "VR front": (583, 598),
 "rugR left": (95, 790), "rugR right": (675, 760), "rugR front": (430, 910), "rugR back": (400, 665),
 "rugT backleft": (715, 628), "rugT frontleft": (860, 975), "rugT frontright": (1330, 940),
 "chair base": (1000, 770), "drawer frontleft": (1255, 935), "desk side bottom": (1360, 965),
 "sofa seat FL": (205, 750), "sofa seat FR": (360, 745), "otto FL": (350, 735), "otto FR": (485, 725),
 "plant pot": (445, 540), "lamp base": (330, 530), "tripod": (485, 545), "VR headset floor": (545, 530),
}
for k, (u, v) in pts.items():
    p = at_z(u, v); print(f"{k:18s} ({u},{v}) -> x={p[0]:.2f} y={p[1]:.2f}")
for k, (u, v, z) in {"desk W top": (985, 493, 0.76), "desk front top right": (1340, 640, 0.76), "seat top front": (290, 640, 0.40), "sofa back top": (330, 550, 0.62), "fcab top": (400, 925, 0.58), "fcab top2": (540, 930, 0.58), "ring center": (610, 105, 2.3)}.items():
    p = at_z(u, v, z); print(f"{k:18s} ({u},{v}) z={z} -> x={p[0]:.2f} y={p[1]:.2f}")
