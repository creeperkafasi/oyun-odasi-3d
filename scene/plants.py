"""Procedural plants and trees. Every plant = one leaf mesh (with per-leaf colour
attribute 'Col') + optional stem curves."""
import math
import random
import bmesh
from mathutils import Vector, Matrix, Quaternion
import lib
from lib import cyl

M = lib.get_mat


class LeafBuilder:
    def __init__(self):
        self.bm = bmesh.new()
        self.col = self.bm.loops.layers.color.new("Col")

    def leaf(self, base, direction, length, width, color, up=Vector((0, 0, 1)), bend=0.25,
             curl=0.15, shape="ellipse", nseg=6):
        """Add one leaf starting at base growing along direction."""
        d = Vector(direction).normalized()
        side = d.cross(up)
        if side.length < 1e-4:
            side = d.cross(Vector((1, 0, 0)))
        side.normalize()
        nrm = side.cross(d).normalized()
        verts_l, verts_m, verts_r = [], [], []
        for i in range(nseg + 1):
            t = i / nseg
            if shape == "heart":
                w = width * (math.sin(math.pi * min(1, t * 1.2)) ** 0.7) * (1 - t * 0.35)
            elif shape == "needle":
                w = width * (1 - t)
            else:
                w = width * math.sin(math.pi * t) ** 0.8
            sag = bend * length * t * t
            p = Vector(base) + d * (length * t) - nrm * sag
            # cup the leaf: edges a bit up
            verts_m.append(self.bm.verts.new(p))
            verts_l.append(self.bm.verts.new(p - side * w * 0.5 + nrm * curl * w))
            verts_r.append(self.bm.verts.new(p + side * w * 0.5 + nrm * curl * w))
        faces = []
        for i in range(nseg):
            faces.append(self.bm.faces.new((verts_l[i], verts_m[i], verts_m[i + 1], verts_l[i + 1])))
            faces.append(self.bm.faces.new((verts_m[i], verts_r[i], verts_r[i + 1], verts_m[i + 1])))
        c = (*color, 1.0)
        for f in faces:
            for lp in f.loops:
                lp[self.col] = c
        return faces

    def card(self, center, size, color, rnd):
        """Small random quad (distant foliage)."""
        q = Quaternion(Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-1, 1))).normalized(), rnd.uniform(0, 6.28))
        m = q.to_matrix()
        s = size
        pts = [Vector(center) + m @ Vector(v) for v in ((-s, 0, -s * 0.6), (s, 0, -s * 0.6), (s * 0.7, 0, s * 0.6), (-s * 0.7, 0, s * 0.6))]
        f = self.bm.faces.new([self.bm.verts.new(p) for p in pts])
        for lp in f.loops:
            lp[self.col] = (*color, 1.0)

    def build(self, name, m=None, c=None):
        ob = lib.mesh_from_bm(name, self.bm, m or M("leaf_vc"), c=c, smooth=True)
        return ob


def _jit(col, rnd, amt=0.25):
    k = 1 + rnd.uniform(-amt, amt)
    h = rnd.uniform(-amt, amt) * 0.3
    return (max(0, col[0] * k + h * 0.2), max(0, col[1] * k), max(0, col[2] * k - h * 0.1))


def stem(name, pts, r, m=None):
    return lib.bezier_path(name, pts, r, m or M("stem"), res=2)


# ---------------------------------------------------------------- indoor plants
def ficus(name, base, height=1.4, stems=5, seed=1, leaf_len=0.16, color=(0.05, 0.16, 0.03)):
    """Tall leafy plant (rubber plant / ficus style)."""
    rnd = random.Random(seed)
    lb = LeafBuilder()
    bx, by, bz = base
    for s in range(stems):
        a = rnd.uniform(0, 2 * math.pi)
        lean = rnd.uniform(0.05, 0.22)
        h = height * rnd.uniform(0.7, 1.0)
        top = Vector((bx + math.cos(a) * lean * h, by + math.sin(a) * lean * h, bz + h))
        mid = Vector((bx + math.cos(a) * lean * h * 0.35, by + math.sin(a) * lean * h * 0.35, bz + h * 0.5))
        stem(f"{name}_stem{s}", [Vector(base), mid, top], 0.007)
        nleaf = rnd.randint(14, 20)
        for k in range(nleaf):
            t = 0.25 + 0.75 * k / nleaf
            p = Vector(base).lerp(mid, min(1, t * 2)) if t < 0.5 else mid.lerp(top, (t - 0.5) * 2)
            ang = rnd.uniform(0, 2 * math.pi)
            dirv = Vector((math.cos(ang), math.sin(ang), rnd.uniform(0.2, 0.9)))
            L = leaf_len * rnd.uniform(0.7, 1.25) * (1.15 - 0.3 * t)
            lb.leaf(p, dirv, L, L * 0.45, _jit(color, rnd), bend=0.35, curl=0.12)
        # top tuft
        for k in range(4):
            ang = rnd.uniform(0, 2 * math.pi)
            lb.leaf(top, Vector((math.cos(ang) * 0.4, math.sin(ang) * 0.4, 1)), leaf_len * 0.8, leaf_len * 0.35, _jit(color, rnd), bend=0.2)
    return lb.build(name + "_leaves")


def leafy_plant(name, base, height=1.2, stems=10, seed=1, leaf_len=0.22, color=(0.10, 0.26, 0.045)):
    """Lush floor plant: arching stems, big glossy leaves concentrated in the upper 2/3."""
    rnd = random.Random(seed)
    lb = LeafBuilder()
    b = Vector(base)
    for s_ in range(stems):
        a = 2 * math.pi * s_ / stems + rnd.uniform(-0.25, 0.25)
        lean = rnd.uniform(0.12, 0.35)
        h = height * rnd.uniform(0.55, 1.0)
        out = Vector((math.cos(a), math.sin(a), 0))
        top = b + out * lean * h + Vector((0, 0, h))
        mid = b + out * lean * h * 0.3 + Vector((0, 0, h * 0.55))
        stem(f"{name}_stem{s_}", [b, mid, top], 0.0065)
        n = rnd.randint(7, 11)
        for k in range(n):
            t = 0.3 + 0.7 * k / (n - 1)
            p = (b.lerp(mid, t / 0.55) if t < 0.55 else mid.lerp(top, (t - 0.55) / 0.45))
            ang = a + rnd.uniform(-1.4, 1.4)
            d = Vector((math.cos(ang), math.sin(ang), rnd.uniform(0.15, 0.7)))
            L = leaf_len * rnd.uniform(0.75, 1.2) * (1.1 - 0.25 * t)
            lb.leaf(p, d, L, L * 0.42, _jit(color, rnd, 0.22), bend=0.45, curl=0.15, nseg=7)
        for k in range(3):
            ang = rnd.uniform(0, 2 * math.pi)
            lb.leaf(top, Vector((math.cos(ang) * 0.3, math.sin(ang) * 0.3, 1)), leaf_len * 0.7, leaf_len * 0.3, _jit(color, rnd, 0.2), bend=0.25)
    return lb.build(name + "_leaves", M("leaf_glossy"))


def bush(name, center, radius=0.18, height=0.3, n=140, seed=2, leaf_len=0.045, color=(0.10, 0.24, 0.045)):
    """Small-leaved shrub (foreground pots / shelves)."""
    rnd = random.Random(seed)
    lb = LeafBuilder()
    cx, cy, cz = center
    nst = 7
    tips = []
    for s in range(nst):
        a = 2 * math.pi * s / nst + rnd.uniform(-0.3, 0.3)
        r = radius * rnd.uniform(0.3, 0.9)
        tip = Vector((cx + r * math.cos(a), cy + r * math.sin(a), cz + height * rnd.uniform(0.6, 1.0)))
        stem(f"{name}_st{s}", [Vector((cx, cy, cz)), Vector((cx, cy, cz)).lerp(tip, 0.5) + Vector((0, 0, 0.03)), tip], 0.0025)
        tips.append(tip)
    for i in range(n):
        tip = tips[i % nst]
        t = rnd.uniform(0.25, 1.0)
        p = Vector((cx, cy, cz)).lerp(tip, t)
        ang = rnd.uniform(0, 2 * math.pi)
        dirv = Vector((math.cos(ang), math.sin(ang), rnd.uniform(0.0, 1.2)))
        lb.leaf(p, dirv, leaf_len * rnd.uniform(0.7, 1.3), leaf_len * 0.4, _jit(color, rnd), bend=0.2, nseg=3)
    return lb.build(name + "_leaves")


def pothos(name, base, n_vines=6, length=0.7, seed=3, color=(0.12, 0.25, 0.04), spread=0.25):
    """Trailing plant: vines spill over the pot rim and hang down."""
    rnd = random.Random(seed)
    lb = LeafBuilder()
    bx, by, bz = base
    for v in range(n_vines):
        a = rnd.uniform(-1.2, 1.2) + (math.pi if v % 3 == 0 else 0)
        dx, dy = math.cos(a), math.sin(a)
        L = length * rnd.uniform(0.4, 1.0)
        pts = [Vector((bx, by, bz + 0.05)),
               Vector((bx + dx * spread * 0.6, by + dy * spread * 0.6, bz + 0.09)),
               Vector((bx + dx * spread, by + dy * spread, bz - L * 0.4)),
               Vector((bx + dx * spread * 1.1, by + dy * spread * 1.1, bz - L))]
        stem(f"{name}_vine{v}", pts, 0.002, M("stem_green"))
        nl = int(10 * L / length) + 3
        for k in range(nl):
            t = k / nl
            seg = min(2, int(t * 3))
            p = pts[seg].lerp(pts[seg + 1], t * 3 - seg)
            ang = rnd.uniform(0, 2 * math.pi)
            dirv = Vector((math.cos(ang), math.sin(ang), rnd.uniform(-0.6, 0.4)))
            s = 0.05 * rnd.uniform(0.7, 1.2)
            lb.leaf(p, dirv, s, s * 0.85, _jit(color, rnd, 0.35), shape="heart", bend=0.15, nseg=4)
    # crown
    for k in range(18):
        ang = rnd.uniform(0, 2 * math.pi)
        dirv = Vector((math.cos(ang), math.sin(ang), rnd.uniform(0.3, 1.0)))
        s = 0.06 * rnd.uniform(0.7, 1.2)
        lb.leaf(Vector((bx, by, bz + 0.04)), dirv, s, s * 0.85, _jit(color, rnd, 0.35), shape="heart", bend=0.2, nseg=4)
    return lb.build(name + "_leaves")


def pot(name, base, r, h, m, r_bottom=None, soil=True):
    cyl(name, base, r, h, m, verts=48, r2=None if r_bottom is None else r, bevel=0.004)
    if r_bottom is not None:
        lib.get_mat  # noqa
    if soil:
        cyl(name + "_soil", (base[0], base[1], base[2] + h - 0.02), r - 0.01, 0.01, M("soil"), verts=32)


# ---------------------------------------------------------------- trees (exterior)
def tree(name, base, height=5.0, crown=(1.6, 1.6, 2.4), n=2500, seed=0,
         palette=((0.12, 0.22, 0.04), (0.35, 0.28, 0.05), (0.55, 0.22, 0.04)),
         leaf=0.09, trunk_r=0.08, coll=None, shaped=False, clusters=36, branches=True):
    """Trunk + branches + clustered foliage (cluster-consistent colour)."""
    rnd = random.Random(seed)
    if coll:
        lib.set_coll(coll)
    bx, by, bz = base
    cz0 = bz + height - crown[2]          # crown bottom
    ccx, ccy = bx + rnd.uniform(-0.1, 0.1), by + rnd.uniform(-0.1, 0.1)
    trunk_top = Vector((ccx, ccy, cz0 + crown[2] * 0.55))
    lib.bezier_path(f"{name}_trunk", [Vector(base), Vector((bx + rnd.uniform(-0.08, 0.08), by, bz + height * 0.35)),
                                      trunk_top], trunk_r, M("bark"), res=2)
    centers = []
    for c in range(clusters):
        while True:
            u = Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-1, 1)))
            if u.length <= 1:
                break
        u = u.normalized() * (u.length ** 0.5)
        p = Vector((ccx + u.x * crown[0], ccy + u.y * crown[1], cz0 + (u.z + 1) * crown[2] / 2))
        col = palette[rnd.randrange(len(palette))]
        centers.append((p, col))
        if branches and c % 2 == 0:
            a = Vector((ccx, ccy, cz0 + crown[2] * rnd.uniform(0.0, 0.45)))
            mid = a.lerp(p, 0.5) + Vector((0, 0, crown[2] * 0.08))
            lib.bezier_path(f"{name}_br{c}", [a, mid, p], trunk_r * 0.35, M("bark"), res=1)
    lb = LeafBuilder()
    sig = max(crown[0], crown[1]) * 0.22
    for i in range(n):
        p0, col = centers[rnd.randrange(clusters)]
        p = p0 + Vector((rnd.gauss(0, sig), rnd.gauss(0, sig), rnd.gauss(0, sig * 0.8)))
        c = _jit(col, rnd, 0.15 if shaped else 0.12)
        if shaped:
            out = (p - Vector((ccx, ccy, p.z))).normalized() if (p - Vector((ccx, ccy, p.z))).length > 1e-3 else Vector((1, 0, 0))
            d = out + Vector((rnd.uniform(-0.8, 0.8), rnd.uniform(-0.8, 0.8), rnd.uniform(-0.6, 0.6)))
            L = leaf * rnd.uniform(0.7, 1.3)
            lb.leaf(p, d, L, L * 0.55, c, bend=0.2, nseg=2)
        else:
            lb.card(p, leaf * rnd.uniform(0.7, 1.3), c, rnd)
    return lb.build(name + "_crown", M("leaf_vc_tree"))


def conifer(name, base, height=3.0, radius=0.6, n=2500, seed=0, color=(0.05, 0.12, 0.04), coll=None):
    rnd = random.Random(seed)
    lb = LeafBuilder()
    bx, by, bz = base
    cyl(f"{name}_trunk", base, 0.05, height * 0.3, M("bark"), verts=8)
    for i in range(n):
        t = rnd.random() ** 0.8
        z = bz + height * (0.15 + 0.85 * t)
        r = radius * (1 - t) ** 0.9 * rnd.uniform(0.5, 1.0)
        a = rnd.uniform(0, 2 * math.pi)
        p = (bx + r * math.cos(a), by + r * math.sin(a), z)
        lb.card(p, 0.06 * rnd.uniform(0.7, 1.3), _jit(color, rnd, 0.3), rnd)
    return lb.build(name + "_crown", M("leaf_vc_tree"))
