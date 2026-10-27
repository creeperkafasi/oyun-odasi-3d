"""Room shell, openings, door, blinds, curtains."""
import math
import bmesh
import lib
from lib import box, cyl
from cfg import W, D, H, T, WIN_Y, WIN_Z, SLIDE_X, SLIDE_Z, DOOR_X, DOOR_Z

M = lib.get_mat


def shell():
    lib.set_coll("Architecture")
    box("Floor", (-T, -T, -0.1), (W + T, D + T, 0), M("concrete"))
    box("FloorSill_slide", (SLIDE_X[0], -T, -0.1), (SLIDE_X[1], 0, 0.0), M("concrete"))
    box("Ceiling", (-T, -T, H), (W + T, D + T, H + 0.25), M("ceiling"))
    wy0, wy1 = WIN_Y
    box("WallW_a", (-T, -T, 0), (0, wy0, H), M("wall"))
    box("WallW_b", (-T, wy1, 0), (0, D + T, H), M("wall"))
    box("WallW_sill", (-T, wy0, 0), (0, wy1, WIN_Z[0]), M("wall"))
    box("WallW_head", (-T, wy0, WIN_Z[1]), (0, wy1, H), M("wall"))
    sx0, sx1 = SLIDE_X
    box("WallS_a", (-T, -T, 0), (sx0, 0, H), M("wall"))
    box("WallS_b", (sx1, -T, 0), (W + T, 0, H), M("wall"))
    box("WallS_head", (sx0, -T, SLIDE_Z[1]), (sx1, 0, H), M("wall"))
    dx0, dx1 = DOOR_X
    box("WallN_a", (-T, D, 0), (dx0, D + T, H), M("wall"))
    box("WallN_b", (dx1, D, 0), (W + T, D + T, H), M("wall"))
    box("WallN_head", (dx0, D, DOOR_Z[1]), (dx1, D + T, H), M("wall"))
    box("WallE", (W, -T, 0), (W + T, D + T, H), M("wall"))
    # skirting (shadow-gap style, dark)
    box("Skirt_S_east", (SLIDE_X[1], 0, 0), (W, 0.012, 0.06), M("black_matte"))
    box("Skirt_E", (W - 0.012, 0, 0), (W, D, 0.06), M("black_matte"))


def sliding_door():
    lib.set_coll("Openings")
    sx0, sx1 = SLIDE_X
    top = SLIDE_Z[1]
    fm = M("alu_black")
    # outer frame
    box("SlideFr_top", (sx0, -0.17, top - 0.07), (sx1, -0.02, top), fm)
    box("SlideFr_bot", (sx0, -0.17, -0.01), (sx1, -0.02, 0.02), fm)
    box("SlideFr_W", (sx0, -0.17, 0), (sx0 + 0.06, -0.02, top), fm)
    box("SlideFr_E", (sx1 - 0.06, -0.17, 0), (sx1, -0.02, top), fm)
    n = 3
    inner0, inner1 = sx0 + 0.04, sx1 - 0.04
    pw = (inner1 - inner0) / n + 0.03
    for i in range(n):
        x0 = inner0 + i * (inner1 - inner0) / n - (0.015 if i else 0)
        x1 = x0 + pw
        if i == n - 1:
            x1 = inner1
        yc = -0.13 if i % 2 == 0 else -0.07
        f = 0.055
        box(f"Slide{i}_glass", (x0 + f, yc - 0.006, 0.02 + f), (x1 - f, yc + 0.006, top - 0.07 - f + 0.02), M("glass"))
        box(f"Slide{i}_L", (x0, yc - 0.025, 0.02), (x0 + f, yc + 0.025, top - 0.05), fm)
        box(f"Slide{i}_R", (x1 - f, yc - 0.025, 0.02), (x1, yc + 0.025, top - 0.05), fm)
        box(f"Slide{i}_B", (x0, yc - 0.025, 0.02), (x1, yc + 0.025, 0.02 + f + 0.02), fm)
        box(f"Slide{i}_T", (x0, yc - 0.025, top - 0.05 - f), (x1, yc + 0.025, top - 0.05), fm)
        # pull handle on the room side
        hx = x1 - f - 0.035 if i == 0 else x0 + f + 0.035
        box(f"Slide{i}_handle", (hx - 0.01, yc + 0.025, 0.85), (hx + 0.01, yc + 0.05, 1.25), fm, bevel=0.004)
    # LED strip on the floor along the glass (as in the render)
    box("Slide_led", (sx0 + 0.06, -0.015, 0.0), (W - 0.25, -0.003, 0.012), M("led_warm"))


def west_window():
    lib.set_coll("Openings")
    wy0, wy1 = WIN_Y
    z0, z1 = WIN_Z
    fm = M("alu_black")
    box("Win_glassL", (-0.105, wy0 + 0.05, z0 + 0.05), (-0.095, (wy0 + wy1) / 2 - 0.03, z1 - 0.05), M("glass"))
    box("Win_glassR", (-0.105, (wy0 + wy1) / 2 + 0.03, z0 + 0.05), (-0.095, wy1 - 0.05, z1 - 0.05), M("glass"))
    for nm, a, b in (("L", (-0.13, wy0, z0), (-0.06, wy0 + 0.06, z1)),
                     ("R", (-0.13, wy1 - 0.06, z0), (-0.06, wy1, z1)),
                     ("B", (-0.13, wy0, z0), (-0.06, wy1, z0 + 0.06)),
                     ("T", (-0.13, wy0, z1 - 0.06), (-0.06, wy1, z1)),
                     ("M", (-0.13, (wy0 + wy1) / 2 - 0.035, z0), (-0.06, (wy0 + wy1) / 2 + 0.035, z1))):
        box("Win_f" + nm, a, b, fm)
    # venetian blinds (upper ~55 %)
    bottom = z1 - 0.62 * (z1 - z0)
    box("Blind_head", (-0.06, wy0 + 0.01, z1 - 0.05), (-0.01, wy1 - 0.01, z1), M("black_matte"))
    z = z1 - 0.07
    i = 0
    tilt = math.radians(50)
    while z > bottom:
        s = box(f"Blind_slat{i}", (-0.052, wy0 + 0.015, z - 0.0012), (-0.027, wy1 - 0.015, z + 0.0012), M("blind"))
        s.rotation_euler = (0, tilt, 0)
        z -= 0.03
        i += 1
    box("Blind_bottom", (-0.058, wy0 + 0.015, z - 0.006), (-0.018, wy1 - 0.015, z + 0.004), M("black_matte"))
    for yy in (wy0 + 0.25, (wy0 + wy1) / 2, wy1 - 0.25):
        box(f"Blind_cord{yy:.2f}", (-0.039, yy - 0.0015, z), (-0.036, yy + 0.0015, z1 - 0.05), M("black_matte"))


def door():
    lib.set_coll("Openings")
    dx0, dx1 = DOOR_X
    y = D + 0.02
    leaf = box("Door_leaf", (dx0 + 0.005, y, 0.008), (dx1 - 0.005, y + 0.045, DOOR_Z[1] - 0.004), M("door_wood"), bevel=0.002)
    # lever handle + rose (room side) — hinge on the west per plan
    hx = dx1 - 0.075
    cyl("Door_rose", (hx, y, 1.02), 0.026, 0.008, M("alu_black"), axis="Y", verts=32)
    cyl("Door_rose", (hx, y - 0.008, 1.02), 0.026, 0.008, M("alu_black"), axis="Y", verts=32)
    cyl("Door_lever_neck", (hx, y - 0.055, 1.02), 0.009, 0.05, M("alu_black"), axis="Y", verts=16)
    box("Door_lever", (hx - 0.13, y - 0.065, 1.01), (hx + 0.005, y - 0.045, 1.03), M("alu_black"), bevel=0.006)
    cyl("Door_keyrose", (hx, y - 0.008, 0.88), 0.018, 0.008, M("alu_black"), axis="Y", verts=24)


def curtain_sheet(name, x0, x1, y, z0, z1, m, folds=7, amp=0.035, nu=90, nv=24):
    bm = bmesh.new()
    rows = []
    for j in range(nv + 1):
        z = z0 + (z1 - z0) * j / nv
        row = []
        for i in range(nu + 1):
            u = i / nu
            x = x0 + (x1 - x0) * u
            a = amp * (0.8 + 0.2 * (j / nv))
            yy = y + a * math.sin(u * folds * 2 * math.pi) + 0.3 * a * math.sin(u * folds * 5.3 + 1)
            row.append(bm.verts.new((x, yy, z)))
        rows.append(row)
    for j in range(nv):
        for i in range(nu):
            bm.faces.new((rows[j][i], rows[j][i + 1], rows[j + 1][i + 1], rows[j + 1][i]))
    return lib.mesh_from_bm(name, bm, m, smooth=True)


def curtains():
    lib.set_coll("Openings")
    # dark blackout panel in the corner + sheer white curtain in front of the glass' west end
    curtain_sheet("Curtain_dark", 0.02, 0.30, 0.10, 0.01, H - 0.03, M("curtain_dark"), folds=4, amp=0.03)
    curtain_sheet("Curtain_sheer", 0.26, 0.88, 0.16, 0.01, H - 0.03, M("curtain_sheer"), folds=9, amp=0.04)
    box("Curtain_track", (0.0, 0.06, H - 0.03), (3.1, 0.21, H), M("black_matte"))
    # warm LED cove behind the curtains / above the glass
    box("Cove_S_led", (0.0, 0.215, H - 0.012), (3.1, 0.225, H - 0.004), M("led_warm"))
