"""Loose furniture: gaming chair, modular sofa, side tables, rugs, VR zone,
ceiling ring, track lights, foreground cabinet, lamps."""
import math
import random
import bpy
import bmesh
from mathutils import Vector, Matrix
import lib
from lib import box, cyl, empty, prism, rounded_rect_pts
from cfg import W, D, H, DESK, VR, RING, RUG_ROUND, RUG_RECT

M = lib.get_mat
FUR = True
FUR_DENSITY = 32000


# ---------------------------------------------------------------- gaming chair
def gaming_chair(loc=(2.42, 2.80, 0), rot=22):
    lib.set_coll("Chair")
    root = empty("Chair", loc, (0, 0, rot))
    lea, ins, plast = M("leather_black"), M("leather_grey"), M("plastic_black")
    # 5-star base
    for k in range(5):
        a = math.radians(90 + k * 72)
        bm = bmesh.new()
        prof = [(0.03, -0.028, 0.10), (0.30, -0.018, 0.085), (0.30, 0.018, 0.085), (0.03, 0.028, 0.10)]
        vs_top = [bm.verts.new((r * math.cos(a) - w * math.sin(a), r * math.sin(a) + w * math.cos(a), z)) for r, w, z in prof]
        vs_bot = [bm.verts.new((v.co.x, v.co.y, v.co.z - 0.035)) for v in vs_top]
        bm.faces.new(vs_top)
        bm.faces.new(list(reversed(vs_bot)))
        for i in range(4):
            j = (i + 1) % 4
            bm.faces.new((vs_top[i], vs_bot[i], vs_bot[j], vs_top[j]))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        leg = lib.mesh_from_bm(f"Chair_leg{k}", bm, plast)
        lib.add_bevel(leg, 0.006, 2)
        leg.parent = root
        cx, cy = 0.31 * math.cos(a), 0.31 * math.sin(a)
        cyl(f"Chair_castpin{k}", (cx, cy, 0.05), 0.008, 0.03, M("black_metal"), parent=root, verts=12)
        w = cyl(f"Chair_caster{k}", (cx - 0.02 * math.sin(a), cy + 0.02 * math.cos(a), 0.03), 0.03, 0.04, plast, parent=root, axis="X", verts=24)
        w.rotation_euler = (0, 0, a)
    cyl("Chair_hub", (0, 0, 0.06), 0.05, 0.05, plast, parent=root)
    cyl("Chair_gas", (0, 0, 0.10), 0.026, 0.30, M("chrome_dark"), parent=root)
    cyl("Chair_gascover", (0, 0, 0.10), 0.04, 0.17, plast, r2=0.03, parent=root)
    box("Chair_mech", (-0.12, -0.12, 0.40), (0.12, 0.12, 0.45), plast, parent=root)
    # seat: bolstered surface
    seat = _chair_surface("Chair_seat", kind="seat", mats=(lea, ins))
    seat.parent = root
    # backrest: winged surface with harness slots (tilted back)
    bk = empty("Chair_backpivot", (0, -0.23, 0.50), (-12, 0, 0), parent=root)
    back = _chair_surface("Chair_back", kind="back", mats=(lea, ins))
    back.parent = bk
    # headrest emblem (front + back)
    prism("Chair_emblem", [(-0.045, 0.83), (0.045, 0.83), (0.03, 0.77), (0.0, 0.745), (-0.03, 0.77)], 0.004, M("emblem_white"), plane="XZ", offset=0.006, parent=bk)
    prism("Chair_emblem_b", [(-0.05, 0.83), (0.05, 0.83), (0.035, 0.76), (0.0, 0.73), (-0.035, 0.76)], 0.004, M("emblem_white"), plane="XZ", offset=-0.098, parent=bk)
    # lumbar + head pillows
    lum = box("Chair_lumbar", (-0.13, 0.03, 0.14), (0.13, 0.10, 0.28), ins, bevel=0.03, segs=4, parent=bk)
    hp = box("Chair_headpillow", (-0.10, 0.015, 0.70), (0.10, 0.07, 0.79), ins, bevel=0.025, segs=4, parent=bk)
    # armrests
    for s in (-1, 1):
        box(f"Chair_armbr{s}", (s * 0.12 - 0.02, -0.06, 0.41), (s * 0.30 + 0.02 * s, 0.0, 0.44), plast, parent=root)
        box(f"Chair_armpost{s}", (s * 0.30 - 0.022, -0.07, 0.41), (s * 0.30 + 0.022, -0.02, 0.66), plast, bevel=0.008, parent=root)
        box(f"Chair_armpad{s}", (s * 0.30 - 0.045, -0.18, 0.66), (s * 0.30 + 0.045, 0.10, 0.695), plast, bevel=0.012, segs=3, parent=root)
    return root


def _lerp_table(tab, v):
    for (v0, a), (v1, b) in zip(tab, tab[1:]):
        if v0 <= v <= v1:
            t = (v - v0) / (v1 - v0) if v1 > v0 else 0
            return a + (b - a) * t
    return tab[-1][1]


def _chair_surface(name, kind="back", mats=None):
    """Racing-seat style shell built as a grid surface + solidify + subsurf."""
    nu, nv = 26, 40
    bm = bmesh.new()
    grid = []
    for j in range(nv + 1):
        v = j / nv
        row = []
        for i in range(nu + 1):
            u = -1 + 2 * i / nu
            if kind == "back":
                hw = _lerp_table([(0, 0.23), (0.24, 0.21), (0.52, 0.27), (0.66, 0.27), (0.75, 0.17), (0.93, 0.155), (1.0, 0.12)], v)
                wing = _lerp_table([(0, 0.09), (0.3, 0.06), (0.55, 0.11), (0.7, 0.07), (0.8, 0.03), (1.0, 0.02)], v)
                x = u * hw
                y = wing * abs(u) ** 3 + 0.025 * math.sin(math.pi * min(1, v / 0.6)) * (1 - abs(u) ** 2)
                z = 0.92 * v
            else:  # seat: u across, v front(1)->back(0)
                x = u * 0.265
                y = -0.24 + 0.50 * v
                z = 0.53 + 0.075 * abs(u) ** 4 + 0.02 * math.sin(math.pi * v) * (1 - u * u) - 0.015 * (1 - v)
            row.append(bm.verts.new((x, y, z)))
        grid.append(row)
    for j in range(nv):
        for i in range(nu):
            v, u = (j + 0.5) / nv, -1 + 2 * (i + 0.5) / nu
            if kind == "back" and 0.66 <= v <= 0.75 and 0.45 <= abs(u) <= 0.78:
                continue   # harness slots
            f = bm.faces.new((grid[j][i], grid[j][i + 1], grid[j + 1][i + 1], grid[j + 1][i]))
            inner = abs(u) < 0.55 and ((kind == "back" and 0.04 < v < 0.64) or (kind == "seat" and 0.08 < v < 0.92))
            f.material_index = 1 if inner else 0
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ob = lib.mesh_from_bm(name, bm, list(mats), smooth=True)
    # make normals point toward the sitter (+Y for back, +Z for seat)
    ob.data.update()
    nsum = sum((p.normal for p in ob.data.polygons), Vector())
    want = Vector((0, 1, 0)) if kind == "back" else Vector((0, 0, 1))
    if nsum.dot(want) < 0:
        for p in ob.data.polygons:
            p.flip()
    sol = ob.modifiers.new("Solid", "SOLIDIFY")
    sol.thickness = 0.085 if kind == "back" else 0.08
    sol.offset = -1
    sol.use_even_offset = True
    sol.material_offset_rim = 0
    lib.subsurf(ob, 1, 2)
    return ob


# ---------------------------------------------------------------- soft furniture
def cushion(name, mn, mx, m, r=0.06, parent=None):
    ob = box(name, mn, mx, m, bevel=r, segs=5, parent=parent)
    return ob


def sofa_group():
    lib.set_coll("Sofa")
    fab = M("fabric_sofa")
    # back module (long axis along y)
    cushion("Sofa_back_base", (1.42, 0.22, 0.0), (1.92, 1.30, 0.36), fab, 0.05)
    cushion("Sofa_back_pad", (1.42, 0.24, 0.30), (1.68, 1.28, 0.64), fab, 0.08)
    cushion("Sofa_back_seat", (1.64, 0.24, 0.30), (1.94, 1.28, 0.44), fab, 0.06)
    # front seat cube
    cushion("Sofa_seat_base", (2.0, 0.40, 0.0), (2.62, 1.02, 0.26), fab, 0.06)
    cushion("Sofa_seat_cush", (2.01, 0.41, 0.22), (2.61, 1.01, 0.40), fab, 0.07)
    # ottoman
    cushion("Sofa_otto_base", (1.84, 1.07, 0.0), (2.46, 1.70, 0.24), fab, 0.06)
    cushion("Sofa_otto_cush", (1.85, 1.08, 0.20), (2.45, 1.69, 0.38), fab, 0.07)
    throw_blanket()
    # tiny feet shadows gap: sit modules on slim plinths (hidden) -> skip


def throw_blanket():
    """Knit throw draped from the seat cube down into the gap toward the ottoman."""
    nu, nv = 14, 40
    width = 0.42
    x0 = 2.12
    path = []
    # (y, z) centreline: on seat top, over the edge, down to the floor
    for i in range(nv + 1):
        t = i / nv
        if t < 0.35:
            s = t / 0.35
            y, z = 0.66 + 0.35 * s, 0.405
        elif t < 0.55:
            s = (t - 0.35) / 0.2
            a = s * math.pi / 2
            y, z = 1.01 + 0.05 * math.sin(a), 0.405 - 0.06 * (1 - math.cos(a)) - 0.02 * s
        else:
            s = (t - 0.55) / 0.45
            y, z = 1.06 + 0.02 * s, 0.33 - 0.31 * s
        path.append((y, z))
    bm = bmesh.new()
    grid = []
    rnd = random.Random(3)
    for i, (y, z) in enumerate(path):
        row = []
        for j in range(nu + 1):
            u = j / nu
            x = x0 + width * u
            wob = 0.018 * math.sin(u * 9 + i * 0.25) * min(1, i / 10)
            hang = max(0, i / nv - 0.5)
            x += hang * 0.10 * math.sin(u * math.pi)
            row.append(bm.verts.new((x, y + wob * 0.6, z + wob * 0.3)))
        grid.append(row)
    for i in range(nv):
        for j in range(nu):
            bm.faces.new((grid[i][j], grid[i][j + 1], grid[i + 1][j + 1], grid[i + 1][j]))
    ob = lib.mesh_from_bm("Throw", bm, M("knit"), smooth=True)
    sol = ob.modifiers.new("Solid", "SOLIDIFY")
    sol.thickness = 0.012
    lib.subsurf(ob, 1)
    return ob


# ---------------------------------------------------------------- tables & lamps
def side_table(name, center, r=0.24, h=0.48, top_m="black_matte"):
    x, y = center
    cyl(f"{name}_top", (x, y, h - 0.02), r, 0.02, M(top_m), verts=64, bevel=0.004)
    cyl(f"{name}_rim", (x, y, h - 0.035), r - 0.01, 0.015, M(top_m), verts=64)
    cyl(f"{name}_pole", (x, y, 0.02), 0.012, h - 0.04, M("black_metal"), verts=16)
    cyl(f"{name}_base", (x, y, 0), 0.15, 0.02, M("black_metal"), verts=48, bevel=0.003)


def floor_lamp(loc=(0.50, 0.72)):
    x, y = loc
    cyl("Lamp_base", (x, y, 0), 0.09, 0.015, M("black_metal"), verts=32)
    cyl("Lamp_stem", (x, y, 0.015), 0.006, 0.58, M("black_metal"), verts=12)
    cyl("Lamp_shade", (x, y, 0.58), 0.075, 0.21, M("lampshade"), verts=48)
    cyl("Lamp_cap", (x, y, 0.79), 0.076, 0.005, M("black_metal"), verts=48)


def rugs():
    lib.set_coll("Rugs")
    r = cyl("Rug_round", (RUG_ROUND["x"], RUG_ROUND["y"], 0), RUG_ROUND["r"], 0.012, M("rug_round"), verts=128, bevel=0.004)
    b = box("Rug_rect", (RUG_RECT[0], RUG_RECT[1], 0), (RUG_RECT[2], RUG_RECT[3], 0.012), M("rug_rect"), bevel=0.004)
    if FUR:
        fur(r, M("fiber_round"), density=FUR_DENSITY, length=0.04, seed=1)
        fur(b, M("fiber_rect"), density=FUR_DENSITY, length=0.035, seed=7)


def vr_zone():
    lib.set_coll("VR")
    x, y, r = VR["x"], VR["y"], VR["r"]
    cyl("VR_mat", (x, y, 0), r - 0.01, 0.004, M("vr_mat"), verts=128)
    lib.torus("VR_led", (x, y, 0.006), r, 0.009, M("led_blue_floor"), maj=192, mnr=10)
    # tripod stand with base station / camera on top
    sx, sy = 0.62, 1.38
    for k in range(3):
        a = math.radians(30 + 120 * k)
        p0 = (sx, sy, 0.38)
        p1 = (sx + 0.22 * math.cos(a), sy + 0.22 * math.sin(a), 0.0)
        lib.curve_path(f"VR_tripod_leg{k}", [p0, p1], 0.008, M("black_metal"))
    cyl("VR_tripod_round", (sx, sy, 0), 0.16, 0.012, M("black_metal"), verts=48)
    cyl("VR_tripod_pole", (sx, sy, 0.3), 0.012, 1.02, M("black_metal"), verts=16)
    box("VR_tripod_head", (sx - 0.04, sy - 0.05, 1.32), (sx + 0.05, sy + 0.05, 1.40), M("plastic_black"), bevel=0.01)
    cyl("VR_tripod_lens", (sx + 0.05, sy, 1.36), 0.022, 0.02, M("glass_dark"), axis="X")


def ceiling_ring():
    lib.set_coll("Ceiling")
    x, y, R = RING["x"], RING["y"], RING["R"]
    z0, z1 = H - 0.17, H - 0.10
    lib.ring_band("Ring_body", (x, y, 0), R - 0.07, R, z0, z1, M("black_metal_matte"), seg=192)
    lib.ring_band("Ring_led_out", (x, y, 0), R, R + 0.004, z0 + 0.012, z1 - 0.012, M("led_blue_ring"), seg=192)
    lib.ring_band("Ring_led_bot", (x, y, 0), R - 0.055, R - 0.015, z0 - 0.003, z0, M("led_blue_ring"), seg=192)
    lib.ring_band("Ring_led_in", (x, y, 0), R - 0.074, R - 0.07, z0 + 0.01, z1 - 0.01, M("led_blue_ring_soft"), seg=192)
    for k in range(3):
        a = math.radians(90 + 120 * k)
        px, py = x + (R - 0.035) * math.cos(a), y + (R - 0.035) * math.sin(a)
        cyl(f"Ring_cable{k}", (px, py, z1), 0.0015, H - z1, M("black_metal"), verts=6)
        cyl(f"Ring_canopy{k}", (px, py, H - 0.012), 0.03, 0.012, M("black_metal_matte"), verts=24)


def track_lights():
    """Two ceiling tracks with spot heads; returns list of (pos, dir) for spot lights."""
    lib.set_coll("Ceiling")
    spots = []
    tracks = [
        (0.48, [(0.70, (0.25, -0.55, -1)), (1.45, (-0.1, -0.35, -1)), (2.25, (0.0, -0.45, -1)), (3.3, (0.1, -0.3, -1)), (4.3, (0, -0.2, -1))]),
        (3.18, [(0.75, (-0.45, 0.25, -1)), (1.55, (0.0, 0.45, -1)), (2.35, (0.05, 0.55, -1)), (3.2, (0.05, 0.6, -1)), (4.05, (0, 0.45, -1))]),
    ]
    for ti, (ty, heads) in enumerate(tracks):
        box(f"Track{ti}", (0.45, ty - 0.017, H - 0.035), (W - 0.15, ty + 0.017, H), M("black_metal_matte"))
        for hi, (hx, d) in enumerate(heads):
            pos = Vector((hx, ty, H - 0.035))
            box(f"Track{ti}_adapt{hi}", (hx - 0.03, ty - 0.02, H - 0.06), (hx + 0.03, ty + 0.02, H - 0.035), M("black_metal_matte"))
            cyl(f"Track{ti}_stem{hi}", (hx, ty, H - 0.10), 0.006, 0.05, M("black_metal_matte"), verts=8)
            head = empty(f"Track{ti}_headpivot{hi}", (hx, ty, H - 0.11))
            lib.aim(head, d)
            cyl(f"Track{ti}_head{hi}", (0, 0, -0.16), 0.042, 0.18, M("black_metal_matte"), verts=32, parent=head)
            cyl(f"Track{ti}_lens{hi}", (0, 0, -0.162), 0.032, 0.004, M("led_spot"), verts=32, parent=head)
            dv = Vector(d).normalized()
            spots.append((Vector((hx, ty, H - 0.11)) + dv * 0.17, dv))
    # cross connector from the south track toward the ring (as in the render)
    box("Track_conn", (RING["x"] + 0.98, 0.48, H - 0.03), (RING["x"] + 1.02, RING["y"] - 0.80, H), M("black_metal_matte"))
    return spots


def front_cabinet():
    lib.set_coll("FrontCab")
    x0, x1, y0, y1, h = 3.98, 4.36, 0.95, 1.85, 0.46
    box("FCab_body", (x0, y0, 0.02), (x1, y1, h), M("cabinet"), bevel=0.004)
    box("FCab_plinth", (x0 + 0.03, y0 + 0.03, 0), (x1 - 0.03, y1 - 0.03, 0.02), M("black_matte"))
    box("FCab_top", (x0 - 0.005, y0 - 0.005, h), (x1 + 0.005, y1 + 0.005, h + 0.02), M("cabinet"), bevel=0.003)
    return (x0, x1, y0, y1, h + 0.02)


# ---------------------------------------------------------------- geometry-nodes fur
_STRAND = {}


def _strand_proto(length=0.035, r=0.0035):
    key = (length, r)
    if key in _STRAND:
        return _STRAND[key]
    import bmesh
    bm = bmesh.new()
    rings = []
    for k, (zf, rf, xf) in enumerate(((0.0, 1.0, 0.0), (0.5, 0.75, 0.15), (1.0, 0.15, 0.45))):
        ring = []
        for i in range(4):
            a = i * math.pi / 2
            ring.append(bm.verts.new((r * rf * math.cos(a) + r * xf * 2, r * rf * math.sin(a), length * zf)))
        rings.append(ring)
    for k in range(2):
        for i in range(4):
            bm.faces.new((rings[k][i], rings[k][(i + 1) % 4], rings[k + 1][(i + 1) % 4], rings[k + 1][i]))
    bm.faces.new(list(reversed(rings[0])))
    bm.faces.new(rings[2])
    ob = lib.mesh_from_bm(f"StrandProto_{len(_STRAND)}", bm, None, c="Protos", smooth=True)
    ob.location = (0, 0, -50)
    ob.hide_render = True
    _STRAND[key] = ob
    return ob


def fur(target, m, density=30000, length=0.035, r=0.0035, tilt=0.55, seed=0):
    """Scatter strand instances over the up-facing faces of `target`."""
    proto = _strand_proto(length, r)
    proto.data.materials.clear()
    ng = bpy.data.node_groups.new(f"Fur_{target.name}", "GeometryNodeTree")
    ng.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    ng.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    N, L = ng.nodes, ng.links
    gi, go = N.new("NodeGroupInput"), N.new("NodeGroupOutput")
    nrm = N.new("GeometryNodeInputNormal")
    sep = N.new("ShaderNodeSeparateXYZ")
    cmp_ = N.new("FunctionNodeCompare")
    cmp_.data_type = "FLOAT"
    cmp_.operation = "GREATER_THAN"
    cmp_.inputs["B"].default_value = 0.5
    L.new(nrm.outputs[0], sep.inputs[0])
    L.new(sep.outputs["Z"], cmp_.inputs["A"])
    dist = N.new("GeometryNodeDistributePointsOnFaces")
    dist.inputs["Density"].default_value = density
    dist.inputs["Seed"].default_value = seed
    L.new(gi.outputs[0], dist.inputs["Mesh"])
    L.new(cmp_.outputs[0], dist.inputs["Selection"])
    oi = N.new("GeometryNodeObjectInfo")
    oi.inputs["Object"].default_value = proto
    oi.transform_space = "ORIGINAL"
    rv = N.new("FunctionNodeRandomValue")
    rv.data_type = "FLOAT_VECTOR"
    rv.inputs["Min"].default_value = (-tilt, -tilt, 0)
    rv.inputs["Max"].default_value = (tilt, tilt, 6.283)
    rv.inputs["Seed"].default_value = seed + 1
    rs = N.new("FunctionNodeRandomValue")
    rs.data_type = "FLOAT"
    rs.inputs["Min"].default_value = 0.6
    rs.inputs["Max"].default_value = 1.4
    rs.inputs["Seed"].default_value = seed + 2
    inst = N.new("GeometryNodeInstanceOnPoints")
    L.new(dist.outputs["Points"], inst.inputs["Points"])
    L.new(oi.outputs["Geometry"], inst.inputs["Instance"])
    L.new(rv.outputs["Value"], inst.inputs["Rotation"])
    L.new(rs.outputs["Value"], inst.inputs["Scale"])
    setm = N.new("GeometryNodeSetMaterial")
    setm.inputs["Material"].default_value = m
    L.new(inst.outputs[0], setm.inputs["Geometry"])
    join = N.new("GeometryNodeJoinGeometry")
    L.new(setm.outputs[0], join.inputs[0])
    L.new(gi.outputs[0], join.inputs[0])
    L.new(join.outputs[0], go.inputs[0])
    mod = target.modifiers.new("Fur", "NODES")
    mod.node_group = ng
    return mod
