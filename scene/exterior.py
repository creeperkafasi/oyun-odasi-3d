"""Terrace outside the sliding door, garden trees, outdoor lights."""
import math
import random
import bpy
from mathutils import Vector
import lib
from lib import box, cyl
import plants
from cfg import W, D, H, T, SLIDE_X

M = lib.get_mat


def terrace():
    lib.set_coll("Exterior")
    ty0, ty1 = -1.40, -T          # terrace depth (plan ≈ 0.9 m, a bit deeper)
    tx0, tx1 = -0.25, 3.60
    box("Ter_floor", (tx0, ty0, -0.12), (tx1, ty1, -0.03), M("terrace_tile"))
    box("Ter_parapet", (tx0 - 0.15, ty0 - 0.15, -0.12), (tx1, ty0, 0.62), M("render_ext"))
    box("Ter_coping", (tx0 - 0.17, ty0 - 0.18, 0.62), (tx1 + 0.02, ty0 + 0.03, 0.66), M("stone_light"))
    box("Ter_wallW", (tx0 - 0.15, ty0 - 0.15, -0.12), (tx0, ty1, 0.62), M("render_ext"))
    box("Ter_wallW_cop", (tx0 - 0.17, ty0 - 0.18, 0.62), (tx0 + 0.02, ty1, 0.66), M("stone_light"))
    # glass balustrade on top of the parapet
    box("Ter_glassrail", (tx0, ty0 - 0.06, 0.66), (tx1, ty0 - 0.05, 1.05), M("glass_rail"))
    # overhang (upper floor) – dark timber soffit
    box("Ter_soffit", (-0.6, -1.9, H + 0.25), (W + 0.6, -T, H + 0.45), M("render_ext"))
    box("Ter_soffit_wood", (-0.4, -1.75, H + 0.22), (W + 0.4, -T, H + 0.25), M("wood_soffit"))
    for i, x in enumerate((0.6, 1.8, 3.0)):
        cyl(f"Ter_downlight{i}", (x, -0.85, H + 0.215), 0.04, 0.006, M("led_spot"), verts=24)
    # ground below/around
    box("Ground", (-40, -40, -0.6), (40, 40, -0.13), M("grass"))
    # outdoor sofa
    sx0, sx1, sy0, sy1 = 0.05, 1.60, ty0 + 0.04, ty0 + 0.78
    box("OSofa_frame", (sx0, sy0, 0.06), (sx1, sy1, 0.32), M("outdoor_frame"), bevel=0.02)
    for k in range(4):
        cyl(f"OSofa_leg{k}", (sx0 + 0.06 + (sx1 - sx0 - 0.12) * (k % 2), sy0 + 0.06 + (sy1 - sy0 - 0.12) * (k // 2), -0.03), 0.018, 0.09, M("alu_black"), verts=12)
    box("OSofa_back", (sx0, sy0, 0.30), (sx1, sy0 + 0.16, 0.72), M("outdoor_frame"), bevel=0.03)
    box("OSofa_armL", (sx0, sy0, 0.30), (sx0 + 0.12, sy1, 0.55), M("outdoor_frame"), bevel=0.03)
    box("OSofa_armR", (sx1 - 0.12, sy0, 0.30), (sx1, sy1, 0.55), M("outdoor_frame"), bevel=0.03)
    nseat = 2
    sw = (sx1 - sx0 - 0.24) / nseat
    for k in range(nseat):
        a = sx0 + 0.12 + k * sw
        box(f"OSofa_seat{k}", (a + 0.005, sy0 + 0.16, 0.32), (a + sw - 0.005, sy1 - 0.01, 0.45), M("outdoor_fabric"), bevel=0.05, segs=4)
        box(f"OSofa_backc{k}", (a + 0.01, sy0 + 0.15, 0.43), (a + sw - 0.01, sy0 + 0.32, 0.80), M("outdoor_fabric"), bevel=0.06, segs=4)
    box("OSofa_pillow", (sx0 + 0.18, sy0 + 0.25, 0.45), (sx0 + 0.50, sy0 + 0.40, 0.72), M("outdoor_fabric2"), bevel=0.06, segs=4)
    # planters with small trees on the terrace
    for i, (x, y, h) in enumerate(((2.55, ty0 + 0.28, 1.9), (-0.05, ty0 + 0.25, 2.4))):
        cyl(f"Ter_planter{i}", (x, y, -0.03), 0.22, 0.55, M("planter_grey"), verts=48, bevel=0.01)
        cyl(f"Ter_planter{i}_soil", (x, y, 0.50), 0.20, 0.01, M("soil"), verts=32)
        plants.tree(f"Ter_tree{i}", (x, y, 0.5), height=h, crown=(0.55, 0.55, h * 0.8), n=15000, seed=10 + i,
                    palette=((0.62, 0.42, 0.07), (0.45, 0.38, 0.06), (0.25, 0.30, 0.05), (0.55, 0.28, 0.05)),
                    leaf=0.036, trunk_r=0.025, shaped=True, clusters=70)
    # warm uplight in each planter
    return [(Vector((2.55, ty0 + 0.28, 0.6)), 25), (Vector((-0.05, ty0 + 0.25, 0.6)), 25)]


def garden():
    lib.set_coll("Garden")
    rnd = random.Random(42)
    autumn = ((0.14, 0.26, 0.05), (0.50, 0.38, 0.06), (0.62, 0.28, 0.05), (0.26, 0.32, 0.06))
    green = ((0.06, 0.16, 0.04), (0.09, 0.20, 0.05), (0.18, 0.24, 0.05))
    trees = []
    # south (seen through the sliding door)
    for i in range(9):
        x = rnd.uniform(-3.0, 6.5)
        y = rnd.uniform(-4.5, -9.0)
        h = rnd.uniform(3.5, 6.5)
        pal = autumn if rnd.random() < 0.6 else green
        plants.tree(f"TreeS{i}", (x, y, -0.13), h, (h * 0.28, h * 0.28, h * 0.65), n=9000, seed=100 + i, palette=pal, leaf=0.075)
    for i in range(3):
        x = rnd.uniform(-1.5, 4.0)
        plants.conifer(f"ConS{i}", (x, rnd.uniform(-3.0, -4.5), -0.13), rnd.uniform(3.0, 4.5), 0.7, n=1500, seed=200 + i)
    # west (seen through the window): a loose row of smaller, varied trees
    for i in range(14):
        x = rnd.uniform(-8.0, -15.0)
        y = rnd.uniform(-3.0, 7.0)
        h = rnd.uniform(2.6, 4.6)
        if rnd.random() < 0.3:
            plants.conifer(f"ConW{i}", (x, y, -0.13), h, h * 0.18, n=2500, seed=400 + i, color=(0.07, 0.15, 0.05))
            continue
        pal = autumn if rnd.random() < 0.55 else green
        cw = h * rnd.uniform(0.16, 0.24)
        plants.tree(f"TreeW{i}", (x, y, -0.13), h, (cw, cw, h * 0.62), n=6000, seed=300 + i, palette=pal, leaf=0.07, clusters=30)
    # distant hills (hazy band)
    for i, (x, y, r, h) in enumerate(((-90, 0, 40, 4), (-10, -100, 50, 4.5), (30, -90, 35, 3))):
        hill = cyl(f"Hill{i}", (x, y, -2), r, h, M("hill_haze"), verts=24, r2=r * 0.3)
