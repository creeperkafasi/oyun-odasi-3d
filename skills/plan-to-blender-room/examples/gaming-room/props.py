"""Small props: monitors, PC, peripherals, gamepads, headphones, VR headsets,
figurines, game cases, frames, potted plants – and their placement."""
import math
import os
import random
import bpy
from mathutils import Vector, Euler
import lib
import materials as MT
import plants as PL
from lib import box, cyl, empty, ellipsoid, uv_plane, capsule_between
from cfg import W, D, H, DESK, VR

M = lib.get_mat
TEX = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "tex"))


def tex_materials():
    MT.image_emit("scr_wall", os.path.join(TEX, "wallpaper.png"), 4.0, rough=0.15)
    MT.image_emit("scr_editor", os.path.join(TEX, "editor.png"), 3.5, rough=0.15)
    MT.image_emit("scr_side", os.path.join(TEX, "side.png"), 3.5, rough=0.15)
    MT.image_emit("scr_deck", os.path.join(TEX, "streamdeck.png"), 2.5, rough=0.2)
    MT.image_mat("poster1", os.path.join(TEX, "poster1.png"), 0.4)
    MT.image_mat("poster2", os.path.join(TEX, "poster2.png"), 0.4)
    MT.image_mat("spines", os.path.join(TEX, "spines.png"), 0.35)
    lib.mat("fig_purple", (0.045, 0.035, 0.07), rough=0.3, metal=0.5)
    lib.mat("fig_gold", (0.35, 0.25, 0.12), rough=0.3, metal=1.0)
    lib.mat("fig_blue", (0.03, 0.06, 0.20), rough=0.25, metal=0.8)
    lib.mat("fig_navy", (0.025, 0.035, 0.09), rough=0.25, metal=0.85)
    lib.mat("fig_silver", (0.45, 0.47, 0.52), rough=0.25, metal=1.0)
    lib.mat("fig_red", (0.12, 0.02, 0.02), rough=0.25, metal=0.8)
    lib.mat("plastic_white", (0.75, 0.75, 0.76), rough=0.35)
    lib.mat("plastic_grey", (0.08, 0.08, 0.085), rough=0.4)
    lib.mat("gloss_black", (0.005, 0.005, 0.006), rough=0.05, coat=1.0)
    lib.mat("rubber", (0.01, 0.01, 0.01), rough=0.8)
    lib.mat("frame_black", (0.01, 0.01, 0.01), rough=0.5)
    lib.mat("book_white", (0.7, 0.68, 0.64), rough=0.6)
    lib.mat("book_black", (0.02, 0.02, 0.025), rough=0.6)
    MT.vcol_mat("vcol", rough=0.5)
    lib.emission_mat("led_white", (0.85, 0.9, 1.0), 6)
    lib.emission_mat("led_fan", (0.02, 0.15, 1.0), 6)
    lib.emission_mat("led_fan_core", (0.15, 0.35, 1.0), 3)
    lib.emission_mat("key_glow", (0.3, 0.45, 1.0), 1.5)
    lib.emission_mat("panel_light", (1.0, 0.93, 0.85), 10)


def _root(name, loc, rot=(0, 0, 0)):
    """Empty with rotation given in radians."""
    e = empty(name, loc)
    e.rotation_euler = rot
    return e


# ---------------------------------------------------------------- monitors / PC
def monitor(name, loc, w, h, yaw=0.0, scr="scr_wall", zc=None, bezel=0.008, arm=False):
    r = _root(name, loc, (0, 0, yaw))
    zc = zc if zc is not None else 0.20 + h / 2
    box(f"{name}_panel", (-w / 2 - bezel, -0.006, zc - h / 2 - bezel), (w / 2 + bezel, 0.012, zc + h / 2 + bezel + 0.004), M("plastic_black"), bevel=0.003, parent=r)
    box(f"{name}_back", (-w / 2 + 0.04, 0.012, zc - h / 2 + 0.03), (w / 2 - 0.04, 0.045, zc + h / 2 - 0.05), M("plastic_black"), bevel=0.01, parent=r)
    s = uv_plane(f"{name}_screen", w, h, M(scr), parent=r)
    s.location = (0, -0.0065, zc)
    if not arm:
        box(f"{name}_neck", (-0.025, 0.03, 0.02), (0.025, 0.05, zc - 0.02), M("alu_black"), bevel=0.004, parent=r)
        box(f"{name}_foot", (-0.13, -0.08, 0.0), (0.13, 0.10, 0.012), M("alu_black"), bevel=0.004, parent=r)
    else:
        box(f"{name}_vesa", (-0.04, 0.045, zc - 0.04), (0.04, 0.06, zc + 0.04), M("alu_black"), parent=r)
    return r


def pc_tower(name, loc, yaw=0.0):
    """Mid tower, front (3 RGB fans) faces local -Y, glass side faces local -X."""
    r = _root(name, loc, (0, 0, yaw))
    w, d, h = 0.23, 0.46, 0.48
    box(f"{name}_case", (-w / 2, -d / 2, 0.02), (w / 2, d / 2, h), M("plastic_black"), bevel=0.004, parent=r)
    for i, (sx, sy) in enumerate(((-1, -1), (1, -1), (-1, 1), (1, 1))):
        cyl(f"{name}_foot{i}", (sx * (w / 2 - 0.03), sy * (d / 2 - 0.04), 0), 0.015, 0.02, M("rubber"), verts=12, parent=r)
    # front glass + fans
    box(f"{name}_frontglass", (-w / 2 + 0.008, -d / 2 - 0.006, 0.03), (w / 2 - 0.008, -d / 2, h - 0.01), M("glass_dark"), parent=r)
    for k in range(3):
        zc = 0.10 + 0.135 * k + 0.02
        fan = _root(f"{name}_fan{k}", (0, -d / 2 + 0.004, zc), (math.radians(90), 0, 0))
        fan.parent = r
        lib.torus(f"{name}_fanring{k}", (0, 0, 0), 0.056, 0.006, M("led_fan"), parent=fan, maj=48, mnr=8)
        lib.torus(f"{name}_fanring_in{k}", (0, 0, 0), 0.040, 0.0035, M("led_fan_core"), parent=fan, maj=48, mnr=6)
        cyl(f"{name}_fanhub{k}", (0, 0, -0.004), 0.018, 0.008, M("plastic_grey"), parent=fan, verts=24)
        for b in range(7):
            bl = box(f"{name}_blade{k}_{b}", (0.018, -0.006, -0.002), (0.052, 0.012, 0.002), M("plastic_grey"), parent=fan)
            bl.rotation_euler = (0.35, 0, b * 2 * math.pi / 7)
    # side glass with glowing interior
    box(f"{name}_sideglass", (-w / 2 - 0.004, -d / 2 + 0.02, 0.04), (-w / 2, d / 2 - 0.02, h - 0.02), M("glass_dark"), parent=r)
    box(f"{name}_gpu", (-w / 2 + 0.02, -d / 2 + 0.05, 0.18), (w / 2 - 0.03, d / 2 - 0.08, 0.22), M("plastic_grey"), parent=r)
    box(f"{name}_gpuled", (-w / 2 + 0.019, -d / 2 + 0.07, 0.205), (-w / 2 + 0.021, d / 2 - 0.12, 0.212), M("led_fan"), parent=r)
    box(f"{name}_innerglow", (-w / 2 + 0.015, d / 2 - 0.05, 0.05), (-w / 2 + 0.02, d / 2 - 0.03, h - 0.04), M("led_fan_core"), parent=r)
    return r


def keyboard(name, loc, yaw=0.0):
    r = _root(name, loc, (0, 0, yaw))
    box(f"{name}_base", (-0.22, -0.07, 0), (0.22, 0.07, 0.018), M("alu_black"), bevel=0.004, parent=r)
    box(f"{name}_glow", (-0.215, -0.065, 0.017), (0.215, 0.065, 0.019), M("key_glow"), parent=r)
    import bmesh
    bm = bmesh.new()
    for row in range(5):
        for col in range(16):
            x0 = -0.205 + col * 0.0255
            y0 = -0.058 + row * 0.024
            wkey = 0.021 if not (row == 0 and 4 <= col <= 10) else 0.0
            if row == 0 and col == 4:
                wkey = 0.0255 * 6 - 0.004
            if wkey == 0:
                continue
            bmesh.ops.create_cube(bm, size=1.0, matrix=__import__("mathutils").Matrix.LocRotScale(
                Vector((x0 + wkey / 2, y0 + 0.0105, 0.026)), None, Vector((wkey, 0.021, 0.012))))
    ob = lib.mesh_from_bm(f"{name}_keys", bm, M("plastic_black"))
    ob.parent = r
    return r


def mouse(name, loc, yaw=0.0):
    r = _root(name, loc, (0, 0, yaw))
    box(f"{name}_pad", (-0.17, -0.13, 0), (0.17, 0.13, 0.003), M("rubber"), bevel=0.002, parent=r)
    ellipsoid(f"{name}_body", (0.03, 0.0, 0.003), (0.032, 0.058, 0.022), M("plastic_black"), parent=r)
    box(f"{name}_cut", (0.0285, 0.0, 0.02), (0.0315, 0.05, 0.026), M("plastic_grey"), parent=r)
    return r


def gamepad(name, loc, rot=(0, 0, 0), m="plastic_black", scale=1.0):
    r = _root(name, loc, rot)
    r.scale = (scale,) * 3
    pm = M(m)
    ellipsoid(f"{name}_body", (0, 0, 0), (0.058, 0.036, 0.017), pm, parent=r)
    for s in (-1, 1):
        g = ellipsoid(f"{name}_grip{s}", (s * 0.045, -0.032, -0.004), (0.022, 0.036, 0.017), pm, parent=r)
        g.rotation_euler = (0, 0, s * 0.35)
        cyl(f"{name}_stick{s}", (s * 0.022, -0.012, 0.010), 0.008, 0.012, M("rubber"), parent=r, verts=16)
        cyl(f"{name}_stickcap{s}", (s * 0.022, -0.012, 0.022), 0.011, 0.004, M("rubber"), parent=r, verts=16)
        box(f"{name}_trig{s}", (s * 0.045 - 0.015, 0.028, 0.0), (s * 0.045 + 0.015, 0.042, 0.012), pm, bevel=0.004, parent=r)
    for k, (dx, dy) in enumerate(((0.008, 0), (-0.008, 0), (0, 0.008), (0, -0.008))):
        cyl(f"{name}_btn{k}", (0.045 + dx, 0.008 + dy, 0.013), 0.004, 0.004, M("plastic_grey"), parent=r, verts=10)
        box(f"{name}_dpad{k}", (-0.045 + dx - 0.003, 0.008 + dy - 0.003, 0.012), (-0.045 + dx + 0.003, 0.008 + dy + 0.003, 0.017), M("plastic_grey"), parent=r)
    box(f"{name}_touch", (-0.02, 0.0, 0.014), (0.02, 0.025, 0.018), M("plastic_grey"), bevel=0.002, parent=r)
    return r


def headphones(name, loc, rot=(0, 0, 0), m="plastic_black"):
    """Over-ear headphones hanging (band on top, cups at sides along local X)."""
    r = _root(name, loc, rot)
    pts = [(0.085 * math.cos(a), 0, 0.085 * math.sin(a) + 0.02) for a in [math.radians(t) for t in range(-10, 191, 10)]]
    lib.curve_path(f"{name}_band", pts, 0.009, M(m), parent=r)
    for s in (-1, 1):
        c = cyl(f"{name}_cup{s}", (s * 0.075, 0, -0.04), 0.045, 0.03, M(m), axis="X", parent=r, verts=32, bevel=0.006)
        c.location.x = s * 0.075 - (0.03 if s > 0 else 0)
        cyl(f"{name}_pad{s}", (s * 0.075 - (0.03 if s > 0 else 0) + (0.0 if s > 0 else 0.03), 0, -0.04), 0.04, 0.012, M("leather_black"), axis="X", parent=r, verts=24)
    return r


def headphone_stand(name, loc, rot=(0, 0, 0)):
    r = _root(name, loc, rot)
    cyl(f"{name}_base", (0, 0, 0), 0.06, 0.012, M("alu_black"), parent=r, verts=32)
    cyl(f"{name}_pole", (0, 0, 0.012), 0.008, 0.24, M("alu_black"), parent=r, verts=12)
    box(f"{name}_top", (-0.05, -0.015, 0.25), (0.05, 0.015, 0.265), M("alu_black"), bevel=0.006, parent=r)
    headphones(f"{name}_hp", (0, 0, 0.17), (0, 0, 0)).parent = r
    return r


def controller_stand(name, loc, rot=(0, 0, 0)):
    r = _root(name, loc, rot)
    cyl(f"{name}_base", (0, 0, 0), 0.045, 0.012, M("alu_black"), parent=r, verts=32)
    cyl(f"{name}_pole", (0, 0, 0.012), 0.007, 0.13, M("alu_black"), parent=r, verts=12)
    gp = gamepad(f"{name}_pad", (0, 0, 0.17), (math.radians(70), 0, 0))
    gp.parent = r
    return r


def vr_headset(name, loc, rot=(0, 0, 0), style="black", scale=1.0):
    r = _root(name, loc, rot)
    r.scale = (scale,) * 3
    body = {"black": "plastic_black", "white": "plastic_white", "quest": "plastic_white"}[style]
    front = {"black": "gloss_black", "white": "gloss_black", "quest": "plastic_white"}[style]
    box(f"{name}_visor", (-0.095, -0.06, -0.05), (0.095, 0.04, 0.05), M(body), bevel=0.03, segs=4, parent=r)
    box(f"{name}_front", (-0.088, -0.066, -0.042), (0.088, -0.03, 0.042), M(front), bevel=0.025, segs=4, parent=r)
    box(f"{name}_face", (-0.08, 0.035, -0.04), (0.08, 0.06, 0.04), M("fabric_sofa"), bevel=0.015, parent=r)
    halo = lib.torus(f"{name}_halo", (0, 0.12, 0.02), 0.095, 0.012, M(body), parent=r, maj=48, mnr=10)
    halo.scale = (1.0, 1.15, 1.0)
    halo.rotation_euler = (math.radians(-15), 0, 0)
    box(f"{name}_strapL", (-0.10, 0.02, -0.01), (-0.09, 0.12, 0.03), M(body), bevel=0.004, parent=r)
    box(f"{name}_strapR", (0.09, 0.02, -0.01), (0.10, 0.12, 0.03), M(body), bevel=0.004, parent=r)
    if style == "black":
        lib.torus(f"{name}_ledring", (0, -0.067, 0), 0.05, 0.004, M("led_fan"), parent=r, maj=48, mnr=6).scale = (1.4, 1, 0.75)
        lib.get_mat  # noqa
    if style == "white":
        box(f"{name}_ledbar", (-0.07, -0.0665, -0.045), (0.07, -0.06, -0.04), M("led_fan"), parent=r)
    return r


def pedestal(name, loc, r=0.06, h=0.05):
    cyl(name, loc, r, h, M("black_matte_sh"), verts=32, bevel=0.003)


# ---------------------------------------------------------------- figurines
FIG_STYLES = {
    "titan": ("fig_purple", "fig_navy"),
    "iron": ("fig_red", "fig_gold"),
    "blue": ("fig_blue", "fig_silver"),
    "dark": ("plastic_black", "fig_blue"),
    "white": ("plastic_white", "fig_blue"),
}


def figure(name, loc, h=0.25, yaw=0.0, style="titan", seed=0):
    """Chunky superhero-style collectible on a round base."""
    rnd = random.Random(seed)
    skin, armor = (M(n) for n in FIG_STYLES[style])
    r = _root(name, loc, (0, 0, yaw))
    cyl(f"{name}_base", (0, 0, 0), 0.30 * h, 0.035 * h, M("black_matte_sh"), parent=r, verts=40, bevel=0.003)
    b = 0.035 * h
    hip = 0.46 * h + b
    stance = rnd.uniform(0.07, 0.11) * h
    # legs + boots
    for s in (-1, 1):
        knee = Vector((s * stance * 0.85, -0.01 * h, 0.26 * h + b))
        foot = Vector((s * stance, 0.0, 0.05 * h + b))
        capsule_between(f"{name}_thigh{s}", (s * 0.055 * h, 0, hip), knee, 0.058 * h, skin, parent=r)
        capsule_between(f"{name}_shin{s}", knee, foot, 0.050 * h, armor, parent=r)
        ellipsoid(f"{name}_knee{s}", tuple(knee), (0.055 * h, 0.055 * h, 0.05 * h), armor, parent=r, segs=12, rings=8)
        ellipsoid(f"{name}_boot{s}", tuple(foot + Vector((0, -0.03 * h, -0.01 * h))), (0.045 * h, 0.075 * h, 0.035 * h), armor, parent=r, segs=12, rings=8)
    ellipsoid(f"{name}_pelvis", (0, 0, hip + 0.02 * h), (0.11 * h, 0.07 * h, 0.07 * h), armor, parent=r)
    ellipsoid(f"{name}_belt", (0, 0, hip + 0.06 * h), (0.105 * h, 0.072 * h, 0.03 * h), M("fig_gold"), parent=r, segs=24, rings=8)
    ellipsoid(f"{name}_abs", (0, 0, 0.62 * h + b), (0.10 * h, 0.07 * h, 0.11 * h), skin, parent=r)
    ellipsoid(f"{name}_chest", (0, -0.01 * h, 0.74 * h + b), (0.16 * h, 0.095 * h, 0.10 * h), armor, parent=r)
    # arms
    for s in (-1, 1):
        sh = Vector((s * 0.165 * h, 0, 0.79 * h + b))
        ang = rnd.uniform(0.15, 0.55)
        fwd = rnd.uniform(0.0, 0.10)
        elbow = sh + Vector((s * math.sin(ang) * 0.15 * h, -fwd * h, -0.16 * h))
        hand = elbow + Vector((s * math.sin(ang) * 0.06 * h, -fwd * 1.5 * h, -0.15 * h))
        ellipsoid(f"{name}_pad{s}", tuple(sh + Vector((s * 0.01 * h, 0, 0.02 * h))), (0.075 * h, 0.07 * h, 0.06 * h), armor, parent=r, segs=16, rings=8)
        capsule_between(f"{name}_uarm{s}", sh, elbow, 0.052 * h, skin, parent=r)
        capsule_between(f"{name}_farm{s}", elbow, hand, 0.050 * h, armor, parent=r)
        ellipsoid(f"{name}_fist{s}", tuple(hand), (0.048 * h, 0.048 * h, 0.05 * h), M("fig_gold") if style == "titan" and s > 0 else armor, parent=r, segs=12, rings=8)
    # neck + head + helmet
    capsule_between(f"{name}_neck", (0, 0, 0.82 * h + b), (0, 0, 0.88 * h + b), 0.04 * h, skin, parent=r)
    ellipsoid(f"{name}_head", (0, -0.005 * h, 0.92 * h + b), (0.055 * h, 0.06 * h, 0.07 * h), skin, parent=r)
    ellipsoid(f"{name}_helm", (0, 0.012 * h, 0.95 * h + b), (0.06 * h, 0.06 * h, 0.06 * h), armor, parent=r)
    return r


# ---------------------------------------------------------------- shelves stuff
def game_cases(name, loc, length, axis="Y", h=0.17, depth=0.135, face="+X"):
    """Row of game cases; spine texture on the visible face."""
    x, y, z = loc
    if axis == "Y":
        box(f"{name}_blk", (x - depth, y, z), (x, y + length, z + h), M("book_black"))
        p = uv_plane(f"{name}_sp", length, h, M("spines"), uv=(length / 0.9, 1.0))
        p.location = (x + 0.0005, y + length / 2, z + h / 2)
        p.rotation_euler = (0, 0, math.radians(90))
    else:
        box(f"{name}_blk", (x, y, z), (x + length, y + depth, z + h), M("book_black"))
        p = uv_plane(f"{name}_sp", length, h, M("spines"), uv=(length / 0.9, 1.0))
        p.location = (x + length / 2, y - 0.0005, z + h / 2)


def book_stack(name, loc, n=3, yaw=0.0, seed=0):
    rnd = random.Random(seed)
    r = _root(name, loc, (0, 0, yaw))
    z = 0
    for i in range(n):
        w, d, t = rnd.uniform(0.22, 0.28), rnd.uniform(0.16, 0.2), rnd.uniform(0.025, 0.045)
        m = M("book_white") if i % 2 else M("book_black")
        b = box(f"{name}_b{i}", (-w / 2, -d / 2, z), (w / 2, d / 2, z + t), m, bevel=0.002, parent=r)
        b.rotation_euler = (0, 0, rnd.uniform(-0.08, 0.08))
        z += t
    return r, z


def frame(name, loc, w, h, img, yaw=0.0, lean=8):
    r = _root(name, loc, (math.radians(-lean), 0, yaw))
    r.rotation_euler = (math.radians(-lean), 0, yaw)
    box(f"{name}_fr", (-w / 2, 0, 0), (w / 2, 0.02, h), M("frame_black"), bevel=0.003, parent=r)
    p = uv_plane(f"{name}_img", w - 0.03, h - 0.03, M(img), parent=r)
    p.location = (0, -0.001, h / 2)
    return r


def potted(name, loc, kind="bush", pot_r=0.06, pot_h=0.09, pot_m="pot_white", seed=0, size=1.0):
    x, y, z = loc
    cyl(f"{name}_pot", (x, y, z), pot_r, pot_h, M(pot_m), verts=32, bevel=0.004)
    cyl(f"{name}_soil", (x, y, z + pot_h - 0.012), pot_r - 0.006, 0.006, M("soil"), verts=24)
    top = (x, y, z + pot_h - 0.01)
    if kind == "bush":
        return PL.bush(name, top, radius=0.12 * size, height=0.20 * size, n=int(110 * size), seed=seed, leaf_len=0.04 * size)
    if kind == "pothos":
        return PL.pothos(name, top, n_vines=7, length=0.55 * size, seed=seed)
    if kind == "small":
        return PL.bush(name, top, radius=0.08 * size, height=0.12 * size, n=int(60 * size), seed=seed, leaf_len=0.03 * size, color=(0.10, 0.2, 0.04))
    if kind == "ficus":
        return PL.ficus(name, top, height=0.5 * size, stems=3, seed=seed, leaf_len=0.07 * size)


# ---------------------------------------------------------------- placement
def desk_setup():
    lib.set_coll("Desk")
    top = DESK["top"]
    yb = D - 0.05            # desk back edge
    yf = yb - DESK["depth"]
    monitor("MonA", (2.12, yb - 0.21, top), 0.60, 0.34, yaw=math.radians(8), scr="scr_wall")
    monitor("MonB", (2.76, yb - 0.22, top), 0.64, 0.32, yaw=0.0, scr="scr_editor")
    monitor("MonC", (3.22, yb - 0.27, top), 0.32, 0.46, yaw=math.radians(-30), scr="scr_side", zc=0.37)
    pc_tower("PC", (3.49, yf + 0.22, top), yaw=math.radians(-12))
    keyboard("Kbd", (2.42, yf + 0.20, top), yaw=math.radians(3))
    mouse("Mouse", (2.80, yf + 0.20, top), yaw=math.radians(2))
    # stream deck / tablet on a stand
    tr = _root("Tablet", (1.98, yf + 0.25, top), (0, 0, math.radians(15)))
    box("Tablet_stand", (-0.05, 0.0, 0), (0.05, 0.06, 0.01), M("alu_black"), parent=tr)
    tb = _root("Tablet_tilt", (0, 0.02, 0.01), (math.radians(-60), 0, 0))
    tb.parent = tr
    box("Tablet_body", (-0.12, -0.002, 0), (0.12, 0.008, 0.17), M("plastic_black"), bevel=0.006, parent=tb)
    s = uv_plane("Tablet_screen", 0.22, 0.15, M("scr_deck"), parent=tb)
    s.location = (0, -0.0025, 0.085)
    controller_stand("CtrlStand1", (3.02, yb - 0.38, top), (0, 0, math.radians(-10)))
    controller_stand("CtrlStand2", (3.18, yf + 0.14, top), (0, 0, math.radians(-25)))
    headphone_stand("HPStand", (2.98, yf + 0.16, top), (0, 0, math.radians(-30)))
    # mic arm + mic at the west end
    mx, my = 1.86, yb - 0.04
    cyl("Mic_clamp", (mx, my, top), 0.02, 0.05, M("alu_black"), verts=16)
    capsule_between("Mic_arm1", (mx, my, top + 0.05), (mx + 0.02, my - 0.05, top + 0.38), 0.008, M("alu_black"))
    capsule_between("Mic_arm2", (mx + 0.02, my - 0.05, top + 0.38), (mx + 0.03, my - 0.22, top + 0.48), 0.007, M("alu_black"))
    cyl("Mic_body", (mx + 0.03, my - 0.25, top + 0.40), 0.025, 0.13, M("plastic_black"), verts=24, bevel=0.005)
    potted("DeskPlant", (1.92, yf + 0.40, top), "small", pot_r=0.05, pot_h=0.08, pot_m="pot_black", seed=21, size=1.6)
    # under-desk subwoofer
    cyl("Sub", (2.0, yb - 0.25, 0.0), 0.12, 0.28, M("plastic_black"), verts=32, bevel=0.01)


def pegboard_items():
    lib.set_coll("Pegboard")
    y = D - 0.09
    headphones("PegHP1", (2.25, y, 1.55), (0, 0, 0))
    headphones("PegHP2", (2.47, y, 1.55), (0, 0, 0))
    gamepad("PegPad1", (2.95, y + 0.01, 1.50), (math.radians(90), 0, 0))
    gamepad("PegPad2", (3.25, y + 0.01, 1.48), (math.radians(90), 0, math.radians(8)))
    # camera on a mini tripod hanging
    box("PegCam", (2.72, y - 0.03, 1.52), (2.84, y + 0.03, 1.60), M("plastic_black"), bevel=0.01)
    cyl("PegCamLens", (2.78, y - 0.03, 1.56), 0.025, 0.04, M("plastic_black"), axis="Y", verts=24)
    lib.get_mat("plastic_black")
    for i, x in enumerate((2.18, 2.40, 2.62, 2.90, 3.10, 3.35)):
        cyl(f"PegHook{i}", (x, y + 0.02, 1.70), 0.003, 0.04, M("black_metal"), axis="Y", verts=6)


def wall_shelf_items():
    lib.set_coll("WallShelf")
    z = 1.94
    y = D - 0.16
    potted("ShelfPlant1", (2.20, y, z), "bush", pot_r=0.065, pot_h=0.10, pot_m="pot_white", seed=31, size=1.0)
    potted("ShelfPlant2", (2.45, y + 0.02, z), "bush", pot_r=0.07, pot_h=0.12, pot_m="pot_black", seed=32, size=1.3)
    figure("ShelfFig1", (2.68, y, z), 0.25, yaw=math.radians(-10), style="blue", seed=5)
    box("ShelfBox1", (2.82, y - 0.08, z), (3.0, y + 0.06, z + 0.06), M("book_white"), bevel=0.003)
    box("ShelfBox2", (2.84, y - 0.07, z + 0.06), (2.98, y + 0.05, z + 0.10), M("book_black"), bevel=0.003)
    frame("ShelfFrame1", (3.15, y + 0.06, z), 0.24, 0.18, "poster1", yaw=0)
    frame("ShelfFrame2", (3.42, y + 0.06, z), 0.30, 0.22, "poster2", yaw=0)
    potted("ShelfPothos", (3.75, y, z), "pothos", pot_r=0.08, pot_h=0.12, pot_m="pot_white", seed=33, size=1.0)


def back_shelves(comps):
    """Fill the lit compartments of the west-wall joinery."""
    lib.set_coll("ShelfProps")
    # left tower: VR headsets top-down + figures
    xL = 0.22
    pedestal("PedL4", (xL, 0.32, 2.05), 0.06, 0.06)
    vr_headset("VR_L4", (xL, 0.32, 2.19), (0, 0, math.radians(-90)), "black", 1.3)
    pedestal("PedL3", (xL, 0.32, 1.60), 0.06, 0.06)
    vr_headset("VR_L3", (xL, 0.32, 1.74), (0, 0, math.radians(-90)), "black", 1.3)
    pedestal("PedL2", (xL, 0.32, 1.10), 0.06, 0.06)
    vr_headset("VR_L2", (xL, 0.32, 1.24), (0, 0, math.radians(-90)), "white", 1.3)
    for i, (yy, st) in enumerate(((0.18, "blue"), (0.30, "white"), (0.42, "iron"))):
        figure(f"FigL1_{i}", (xL, yy, 0.60), 0.17, yaw=math.radians(-90), style=st, seed=40 + i)
    cyl("SpeakerL", (0.25, 0.32, 0.105), 0.14, 0.30, M("plastic_black"), verts=32, bevel=0.01)
    # console bays (y 1.15..2.80, 4 bays)
    zc = 0.60
    headphone_stand("ConHP", (0.22, 1.32, zc), (0, 0, math.radians(-90)))
    game_cases("ConGames1", (0.36, 1.60, zc), 0.36, "Y", h=0.17)
    game_cases("ConGames2", (0.36, 2.02, zc), 0.34, "Y", h=0.17)
    figure("ConFig1", (0.22, 2.50, zc), 0.25, yaw=math.radians(-90), style="white", seed=50)
    figure("ConFig2", (0.22, 2.66, zc), 0.22, yaw=math.radians(-90), style="dark", seed=51)
    # right tower
    ry0, ry1 = 2.80, D - 0.03
    figure("RFig0a", (0.22, 2.95, 0.60), 0.21, yaw=math.radians(-90), style="dark", seed=60)
    box("RBox0", (0.10, 3.05, 0.60), (0.32, 3.17, 0.75), M("plastic_black"), bevel=0.004)
    pedestal("RPed0", (0.22, 3.38, 0.60), 0.06, 0.04)
    vr_headset("RVR0", (0.22, 3.38, 0.70), (0, 0, math.radians(-90)), "black", 0.9)
    for i, yy in enumerate((2.96, 3.18, 3.42)):
        figure(f"RFig1_{i}", (0.22, yy, 1.00), 0.30, yaw=math.radians(-90 + (i - 1) * 12), style="titan", seed=70 + i)
    figure("RFig2_0", (0.22, 2.92, 1.58), 0.20, yaw=math.radians(-90), style="titan", seed=80)
    figure("RFig2_1", (0.22, 3.08, 1.58), 0.20, yaw=math.radians(-90), style="iron", seed=81)
    vr_headset("RVR2a", (0.22, 3.30, 1.64), (0, 0, math.radians(-100)), "white", 0.75)
    vr_headset("RVR2b", (0.22, 3.48, 1.64), (0, 0, math.radians(-80)), "white", 0.75)
    figure("RFig3_0", (0.22, 2.98, 2.00), 0.35, yaw=math.radians(-90), style="blue", seed=90)
    figure("RFig3_1", (0.22, 3.14, 2.00), 0.25, yaw=math.radians(-90), style="titan", seed=91)
    potted("RPlant3", (0.22, 3.42, 2.00), "bush", pot_r=0.07, pot_h=0.11, pot_m="pot_grey", seed=92, size=1.2)
    # window sill plant
    potted("SillPlant", (0.06, 2.60, 1.10), "small", pot_r=0.05, pot_h=0.08, pot_m="pot_grey", seed=93, size=1.3)


def room_decor(fc):
    lib.set_coll("Decor")
    x0, x1, y0, y1, top = fc
    # foreground cabinet: plants on the south part, book stack + gamepad on the north part
    potted("FCPlant1", (x0 + 0.20, y0 + 0.14, top), "bush", pot_r=0.08, pot_h=0.13, pot_m="pot_white", seed=101, size=1.5)
    potted("FCPlant2", (x0 + 0.10, y0 + 0.36, top), "bush", pot_r=0.065, pot_h=0.12, pot_m="pot_grey", seed=102, size=1.3)
    potted("FCPlant3", (x0 + 0.28, y0 + 0.40, top), "small", pot_r=0.06, pot_h=0.11, pot_m="pot_black", seed=103, size=1.6)
    rr, zt = book_stack("FCBooks", ((x0 + x1) / 2, y1 - 0.20, top), 3, yaw=math.radians(10), seed=4)
    gamepad("FCPad", ((x0 + x1) / 2, y1 - 0.20, top + zt + 0.02), (0, 0, math.radians(200)))
    # sofa props
    gamepad("OttoPad", (2.15, 1.40, 0.395), (0, 0, math.radians(160)))
    # side tables
    potted("ST1Plant", (1.86, 0.40, 0.46), "small", pot_r=0.035, pot_h=0.12, pot_m="pot_black", seed=104, size=1.5)
    cyl("ST1Dish", (1.97, 0.50, 0.46), 0.05, 0.012, M("fig_gold"), verts=24)
    potted("ST2Plant", (1.10, 0.36, 0.58), "small", pot_r=0.05, pot_h=0.08, pot_m="pot_black", seed=105, size=1.4)
    gamepad("ST2Pad", (1.16, 0.42, 0.60), (0, 0, math.radians(30)), scale=0.9)
    # VR area props
    vr_headset("VRFloor", (0.80, 1.62, 0.055), (math.radians(0), 0, math.radians(-70)), "black", 1.0)
    # big plant (back wall gap)
    PL.pot("BigPot", (0.34, 0.92, 0), 0.17, 0.46, M("pot_black"))
    PL.leafy_plant("BigPlant", (0.34, 0.92, 0.44), height=1.15, stems=11, seed=4, leaf_len=0.22, color=(0.10, 0.27, 0.045))
