"""Built-in joinery: back (west) wall shelving + console, north wall panelling,
slat wall, pegboard, floating shelf and the desk carcass."""
import math
import random
import lib
from lib import box, cyl
from cfg import W, D, H, WIN_Y, WIN_Z, DOOR_X, DOOR_Z, DESK

M = lib.get_mat
TH = 0.025  # board thickness
COMPARTMENTS = []   # (x0, x1, y0, y1, z_bottom, z_top) of lit open compartments


def led_strip(name, a, b, kind="led_warm"):
    return box(name, a, b, M(kind))


# ---------------------------------------------------------------- helpers
def panel_grooves(prefix, y0, y1, z0, z1, x, pitch=0.30, mat="wood_back"):
    """Vertical veneer panels on the west wall (x = wall face)."""
    y = y0
    i = 0
    while y < y1 - 0.01:
        ye = min(y + pitch, y1)
        box(f"{prefix}_{i}", (x, y + 0.002, z0), (x + 0.018, ye - 0.002, z1), M(mat))
        y = ye
        i += 1


def tower(name, y0, y1, shelves, x0=0.02, x1=0.40, top=None, divider_from=None, plinth=0.08):
    """Open shelving tower against west wall. shelves = list of z (board bottoms)."""
    top = top or (H - 0.12)
    mw = M("wood_dark")
    box(f"{name}_sideS", (x0, y0, 0), (x1, y0 + TH, top + TH), mw)
    box(f"{name}_sideN", (x0, y1 - TH, 0), (x1, y1, top + TH), mw)
    box(f"{name}_top", (x0, y0, top), (x1, y1, top + TH), mw)
    if plinth > 0:
        box(f"{name}_plinth", (x0 + 0.04, y0 + TH, 0), (x1 - 0.03, y1 - TH, plinth), M("cabinet"))
    box(f"{name}_back", (x0, y0 + TH, 0), (x0 + 0.012, y1 - TH, top), M("wood_shelfback"))
    zs = sorted(shelves)
    for i, z in enumerate(zs):
        box(f"{name}_sh{i}", (x0 + 0.012, y0 + TH, z), (x1, y1 - TH, z + TH), mw)
    # LED: under each shelf (and under top) near the front, plus vertical back glow
    for i, z in enumerate(zs[1:] + [top]):
        led_strip(f"{name}_led{i}", (x1 - 0.05, y0 + TH + 0.01, z - 0.004), (x1 - 0.035, y1 - TH - 0.01, z - 0.001))
    bounds = zs + [top]
    for i in range(len(zs)):
        COMPARTMENTS.append((x0, x1, y0 + TH, y1 - TH, bounds[i] + TH, bounds[i + 1]))
    if divider_from is not None:
        ym = (y0 + y1) / 2
        box(f"{name}_div", (x0 + 0.012, ym - TH / 2, divider_from), (x1, ym + TH / 2, top), mw)
    return zs, top


# ---------------------------------------------------------------- west wall
def west_wall():
    lib.set_coll("Joinery")
    wy0, wy1 = WIN_Y
    z0, z1 = WIN_Z
    # wall cladding (around window)
    panel_grooves("CladW_lo", 0.6, wy0 + 0.1, 0.98, H, 0.0)
    panel_grooves("CladW_top", wy0 - 0.05, wy1 + 0.05, z1 + 0.05, H, 0.0, pitch=0.3)
    box("CladW_gapL", (0, 0.60, 0), (0.018, 1.15, H), M("wood_back"))
    # window reveal (dark lining)
    box("WinReveal_S", (-0.06, wy0 - 0.06, z0 - 0.04), (0.02, wy0, z1 + 0.06), M("cabinet"))
    box("WinReveal_N", (-0.06, wy1, z0 - 0.04), (0.02, wy1 + 0.06, z1 + 0.06), M("cabinet"))
    box("WinReveal_T", (-0.06, wy0 - 0.06, z1), (0.02, wy1 + 0.06, z1 + 0.06), M("cabinet"))
    box("WinSill", (-0.06, wy0 - 0.06, z0 - 0.04), (0.10, wy1 + 0.06, z0), M("wood_dark"))

    # left tower (south side)
    tower("TowerL", 0.04, 0.60, [0.08, 0.55, 1.05, 1.55, 2.0])
    # console
    cy0, cy1 = 1.15, 2.80
    mw = M("wood_dark")
    box("Con_plinth", (0.06, cy0, 0), (0.39, cy1, 0.05), M("cabinet"))
    ndoors = 5
    dw = (cy1 - cy0) / ndoors
    for i in range(ndoors):
        box(f"Con_door{i}", (0.02, cy0 + i * dw + 0.002, 0.05), (0.42, cy0 + (i + 1) * dw - 0.002, 0.55), M("cabinet"), bevel=0.003)
        # finger-pull groove line
        box(f"Con_pull{i}", (0.418, cy0 + i * dw + 0.03, 0.525), (0.423, cy0 + (i + 1) * dw - 0.03, 0.535), M("black_metal"))
    box("Con_shelf", (0.02, cy0, 0.55), (0.42, cy1, 0.55 + TH), mw)
    box("Con_top", (0.02, cy0, 0.97), (0.42, cy1, 0.97 + TH + 0.005), mw)
    box("Con_back", (0.0, cy0, 0.55), (0.014, cy1, 0.97), M("wood_shelfback"))
    box("Con_sideS", (0.02, cy0, 0.55), (0.42, cy0 + TH, 0.97), mw)
    nb = 4
    bw = (cy1 - cy0) / nb
    for i in range(1, nb):
        y = cy0 + i * bw
        box(f"Con_div{i}", (0.02, y - TH / 2, 0.575), (0.42, y + TH / 2, 0.97), mw)
    led_strip("Con_led", (0.37, cy0 + 0.03, 0.966), (0.385, cy1 - 0.03, 0.969))
    COMPARTMENTS.append((0.02, 0.42, cy0 + TH, cy1, 0.575, 0.97))
    # right tower above console (two columns at the upper part)
    ry0, ry1 = 2.80, D - 0.03
    box("TowerR_doors_base", (0.06, ry0, 0), (0.39, ry1, 0.05), M("cabinet"))
    for i in range(2):
        a = ry0 + i * (ry1 - ry0) / 2
        b = ry0 + (i + 1) * (ry1 - ry0) / 2
        box(f"TowerR_door{i}", (0.02, a + 0.002, 0.05), (0.42, b - 0.002, 0.55), M("cabinet"), bevel=0.003)
        box(f"TowerR_pull{i}", (0.418, a + 0.03, 0.525), (0.423, b - 0.03, 0.535), M("black_metal"))
    zs, top = tower("TowerR", ry0, ry1, [0.55, 0.97, 1.55, 1.97], x0=0.02, x1=0.42, divider_from=1.55, plinth=0.0)


# ---------------------------------------------------------------- north wall
def north_wall():
    lib.set_coll("Joinery")
    dx0, dx1 = DOOR_X
    y = D
    # wood slats between back corner and door
    x = 0.02
    i = 0
    while x < dx0 - 0.10:
        box(f"SlatW_{i}", (x, y - 0.035, 0), (x + 0.035, y - 0.002, H), M("wood_mid"))
        x += 0.055
        i += 1
    box("SlatW_back", (0.0, y - 0.006, 0), (dx0 - 0.08, y, H), M("cabinet"))
    led_strip("LED_vert_A", (dx0 - 0.075, y - 0.012, 0.0), (dx0 - 0.062, y - 0.002, H), "led_warm_soft")
    # door casing (wood) + wood panel cladding east of door up to slat wall
    cas = 0.06
    box("DoorCas_W", (dx0 - cas, y - 0.02, 0), (dx0, y + 0.02, DOOR_Z[1] + cas), M("wood_mid"))
    box("DoorCas_E", (dx1, y - 0.02, 0), (dx1 + cas, y + 0.02, DOOR_Z[1] + cas), M("wood_mid"))
    box("DoorCas_T", (dx0 - cas, y - 0.02, DOOR_Z[1]), (dx1 + cas, y + 0.02, DOOR_Z[1] + cas), M("wood_mid"))
    box("DoorLining", (dx0, y, 0), (dx1, y + 0.2, 0.0005), M("wood_mid"))
    box("CladN_aboveDoor", (dx0 - cas, y - 0.012, DOOR_Z[1] + cas), (dx1 + cas, y, H), M("wood_panel"))
    box("CladN_east", (dx1 + cas, y - 0.012, 0), (DESK["x0"] - 0.06, y, H), M("wood_panel"))
    box("CladN_west", (dx0 - 0.08, y - 0.012, 0), (dx0 - cas, y, H), M("wood_panel"))
    led_strip("LED_vert_B", (DESK["x0"] - 0.06, y - 0.014, 0.0), (DESK["x0"] - 0.045, y - 0.004, H), "led_warm_soft")

    # black slat wall from desk start to east wall
    sx0 = DESK["x0"] - 0.04
    box("SlatBk_back", (sx0, y - 0.008, 0), (W, y, H), M("slat_black"))
    x = sx0
    i = 0
    while x < W - 0.02:
        box(f"SlatBk_{i}", (x, y - 0.045, 0.0), (x + 0.028, y - 0.008, H), M("slat_black"))
        x += 0.05
        i += 1
    # warm grazing LED at ceiling over slats
    led_strip("LED_slat_top", (sx0, y - 0.11, H - 0.012), (W, y - 0.095, H - 0.004), "led_warm")
    # pegboard over the desk
    px0, px1 = DESK["x0"] + 0.45, DESK["x1"] + 0.6
    pz0, pz1 = 0.92, 1.86
    box("Pegboard", (px0, y - 0.065, pz0), (px1, y - 0.048, pz1), M("pegboard"))
    # floating shelf + blue LED underneath
    box("WallShelf", (DESK["x0"] + 0.35, y - 0.28, 1.90), (W, y - 0.045, 1.94), M("wood_dark"))
    led_strip("WallShelf_led", (DESK["x0"] + 0.37, y - 0.27, 1.894), (W, y - 0.255, 1.899), "led_blue")
    led_strip("WallShelf_led2", (DESK["x0"] + 0.37, y - 0.075, 1.894), (W, y - 0.065, 1.899), "led_blue")


# ---------------------------------------------------------------- desk
def desk():
    lib.set_coll("Desk")
    x0, x1, dep, top = DESK["x0"], DESK["x1"], DESK["depth"], DESK["top"]
    y1 = D - 0.05
    y0 = y1 - dep
    box("Desk_top", (x0, y0, top - 0.04), (x1, y1, top), M("desk_wood"), bevel=0.004)
    box("Desk_sideE", (x1 - 0.04, y0 + 0.01, 0), (x1, y1, top - 0.04), M("desk_wood_v"))
    box("Desk_legW", (x0 + 0.02, y0 + 0.04, 0), (x0 + 0.06, y1 - 0.02, top - 0.04), M("cabinet"))
    box("Desk_modesty", (x0 + 0.06, y1 - 0.03, 0.12), (x1 - 0.04, y1 - 0.01, top - 0.04), M("cabinet"))
    # drawer unit at the east end
    dx0 = x1 - 0.04 - 0.46
    box("Drw_body", (dx0, y0 + 0.02, 0.0), (x1 - 0.04, y1 - 0.03, top - 0.045), M("cabinet"))
    # niche on top
    box("Drw_niche", (dx0 + 0.02, y0 + 0.015, 0.56), (x1 - 0.06, y0 + 0.4, top - 0.06), M("cabinet_in"))
    hs = [(0.02, 0.19), (0.20, 0.37), (0.38, 0.55)]
    for i, (a, b) in enumerate(hs):
        box(f"Drw_front{i}", (dx0 + 0.005, y0 + 0.005, a), (x1 - 0.045, y0 + 0.025, b), M("cabinet"), bevel=0.003)
        box(f"Drw_handle{i}", (dx0 + 0.10, y0 + 0.0, b - 0.045), (dx0 + 0.20, y0 + 0.006, b - 0.03), M("black_metal"))
    # blue LED under desk top (front lip) and along the floor at the back
    led_strip("Desk_led_under", (x0 + 0.07, y1 - 0.06, top - 0.048), (dx0 - 0.01, y1 - 0.045, top - 0.042), "led_blue")
    led_strip("Desk_led_floor", (x0 + 0.07, y1 - 0.05, 0.06), (dx0 - 0.01, y1 - 0.035, 0.07), "led_blue")
    led_strip("Desk_led_back", (x0 + 0.07, y1 + 0.0, top + 0.002), (x1 - 0.05, y1 + 0.012, top + 0.008), "led_blue")
