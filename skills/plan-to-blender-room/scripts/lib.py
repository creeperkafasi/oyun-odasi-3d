"""Small helper library for procedural scene building in Blender."""
import bpy
import bmesh
import math
from mathutils import Vector, Matrix, Euler

_COLLS = {}
_MATS = {}


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    _COLLS.clear()
    _MATS.clear()


def coll(name):
    if name in _COLLS:
        return _COLLS[name]
    c = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(c)
    _COLLS[name] = c
    return c


_CUR = ["Misc"]


def set_coll(name):
    _CUR[0] = name


def _link(obj, c=None):
    (coll(c) if c else coll(_CUR[0])).objects.link(obj)
    return obj


# ---------------------------------------------------------------- materials
def _bsdf(m):
    if m.node_tree is None:
        m.use_nodes = True
    nt = m.node_tree
    return nt, nt.nodes.get("Principled BSDF")


def mat(name, color=(0.8, 0.8, 0.8), rough=0.5, metal=0.0, spec=0.5,
        emit=None, strength=0.0, transmission=0.0, ior=1.45, alpha=1.0,
        coat=0.0, sheen=0.0):
    if name in _MATS:
        return _MATS[name]
    m = bpy.data.materials.new(name)
    nt, b = _bsdf(m)
    if len(color) == 3:
        color = (*color, 1.0)
    b.inputs["Base Color"].default_value = color
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if "Specular IOR Level" in b.inputs:
        b.inputs["Specular IOR Level"].default_value = spec
    b.inputs["IOR"].default_value = ior
    if transmission:
        b.inputs["Transmission Weight"].default_value = transmission
    if coat:
        b.inputs["Coat Weight"].default_value = coat
    if sheen:
        b.inputs["Sheen Weight"].default_value = sheen
    if emit is not None:
        if len(emit) == 3:
            emit = (*emit, 1.0)
        b.inputs["Emission Color"].default_value = emit
        b.inputs["Emission Strength"].default_value = strength
    if alpha < 1.0:
        b.inputs["Alpha"].default_value = alpha
    m.diffuse_color = color
    _MATS[name] = m
    return m


def emission_mat(name, color, strength):
    """Pure emitter (no diffuse) - for LED strips etc."""
    if name in _MATS:
        return _MATS[name]
    m = bpy.data.materials.new(name)
    nt, b = _bsdf(m)
    nodes, links = nt.nodes, nt.links
    nodes.remove(b)
    out = nodes.get("Material Output")
    e = nodes.new("ShaderNodeEmission")
    e.inputs["Color"].default_value = (*color, 1.0)
    e.inputs["Strength"].default_value = strength
    links.new(e.outputs[0], out.inputs["Surface"])
    m.diffuse_color = (*color, 1.0)
    _MATS[name] = m
    return m


def get_mat(name):
    return _MATS[name]


# ---------------------------------------------------------------- geometry
def mesh_from_bm(name, bm, m=None, c=None, smooth=False):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    if smooth:
        for p in me.polygons:
            p.use_smooth = True
    ob = bpy.data.objects.new(name, me)
    if m is not None:
        if isinstance(m, (list, tuple)):
            for mm in m:
                me.materials.append(mm)
        else:
            me.materials.append(m)
    return _link(ob, c)


def box(name, mn, mx, m=None, bevel=0.0, segs=2, c=None, parent=None):
    """Axis aligned box from min corner to max corner (local coords if parent)."""
    mn, mx = Vector(mn), Vector(mx)
    size = mx - mn
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = Vector((v.co.x * size.x, v.co.y * size.y, v.co.z * size.z))
    ob = mesh_from_bm(name, bm, m, c)
    ob.location = (mn + mx) / 2
    if bevel > 0:
        add_bevel(ob, bevel, segs)
    if parent:
        ob.parent = parent
    return ob


def cyl(name, base, r, h, m=None, verts=48, c=None, parent=None, axis="Z",
        smooth=True, r2=None, bevel=0.0):
    """Cylinder (or cone if r2 given) standing on `base` along axis."""
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=verts,
                          radius1=r, radius2=r if r2 is None else r2, depth=h)
    bmesh.ops.translate(bm, verts=bm.verts, vec=(0, 0, h / 2))
    if axis == "X":
        bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0),
                         matrix=Matrix.Rotation(math.radians(90), 3, "Y"))
    elif axis == "Y":
        bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0),
                         matrix=Matrix.Rotation(math.radians(-90), 3, "X"))
    ob = mesh_from_bm(name, bm, m, c, smooth=smooth)
    ob.location = base
    if smooth:
        _autosmooth(ob)
    if bevel > 0:
        add_bevel(ob, bevel, 2)
    if parent:
        ob.parent = parent
    return ob


def torus(name, center, R, r, m=None, c=None, parent=None, maj=96, mnr=16):
    bm = bmesh.new()
    verts = []
    for i in range(maj):
        a = 2 * math.pi * i / maj
        ring = []
        for j in range(mnr):
            b = 2 * math.pi * j / mnr
            x = (R + r * math.cos(b)) * math.cos(a)
            y = (R + r * math.cos(b)) * math.sin(a)
            z = r * math.sin(b)
            ring.append(bm.verts.new((x, y, z)))
        verts.append(ring)
    for i in range(maj):
        for j in range(mnr):
            a = verts[i][j]
            b2 = verts[(i + 1) % maj][j]
            cc = verts[(i + 1) % maj][(j + 1) % mnr]
            d = verts[i][(j + 1) % mnr]
            bm.faces.new((a, b2, cc, d))
    ob = mesh_from_bm(name, bm, m, c, smooth=True)
    ob.location = center
    if parent:
        ob.parent = parent
    return ob


def ring_band(name, center, r_in, r_out, z0, z1, m=None, c=None, parent=None, seg=128):
    """Annular band (tube with rectangular cross-section)."""
    bm = bmesh.new()
    rings = []
    for (rr, zz) in ((r_out, z0), (r_out, z1), (r_in, z1), (r_in, z0)):
        rings.append([bm.verts.new((rr * math.cos(2 * math.pi * i / seg),
                                    rr * math.sin(2 * math.pi * i / seg), zz))
                      for i in range(seg)])
    for k in range(4):
        A, B = rings[k], rings[(k + 1) % 4]
        for i in range(seg):
            bm.faces.new((A[i], A[(i + 1) % seg], B[(i + 1) % seg], B[i]))
    ob = mesh_from_bm(name, bm, m, c)
    ob.location = center
    if parent:
        ob.parent = parent
    return ob


def disc(name, center, r, thick, m=None, c=None, verts=96, parent=None):
    return cyl(name, center, r, thick, m, verts=verts, c=c, parent=parent)


def add_bevel(ob, w, segs=2):
    mod = ob.modifiers.new("Bevel", "BEVEL")
    mod.width = w
    mod.segments = segs
    mod.limit_method = "ANGLE"
    mod.harden_normals = True
    for p in ob.data.polygons:
        p.use_smooth = True
    _autosmooth(ob)
    return mod


def _autosmooth(ob, angle=35):
    try:
        with bpy.context.temp_override(object=ob, active_object=ob, selected_objects=[ob],
                                       selected_editable_objects=[ob]):
            bpy.ops.object.shade_smooth_by_angle(angle=math.radians(angle))
    except Exception:
        pass


def empty(name, loc=(0, 0, 0), rot=(0, 0, 0), c=None, parent=None):
    e = bpy.data.objects.new(name, None)
    e.empty_display_size = 0.2
    e.location = loc
    e.rotation_euler = [math.radians(a) for a in rot]
    _link(e, c)
    if parent:
        e.parent = parent
    return e


def parent_all(objs, p):
    for o in objs:
        o.parent = p


def subsurf(ob, levels=2, render=None):
    mod = ob.modifiers.new("Subsurf", "SUBSURF")
    mod.levels = levels
    mod.render_levels = render if render is not None else levels
    for p in ob.data.polygons:
        p.use_smooth = True
    return mod


def rounded_box(name, mn, mx, m=None, radius=0.03, segs=3, c=None, parent=None):
    return box(name, mn, mx, m, bevel=radius, segs=segs, c=c, parent=parent)


def ellipse_floor(name, center, rx, ry, thick, m=None, c=None, seg=128):
    ob = cyl(name, center, 1.0, thick, m, verts=seg, c=c)
    ob.scale = (rx, ry, 1)
    return ob


def curve_path(name, pts, bevel_r, m=None, c=None, closed=False, parent=None, res=4):
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = bevel_r
    cu.bevel_resolution = res
    cu.use_fill_caps = True
    sp = cu.splines.new("POLY")
    sp.points.add(len(pts) - 1)
    for i, p in enumerate(pts):
        sp.points[i].co = (*p, 1)
    sp.use_cyclic_u = closed
    ob = bpy.data.objects.new(name, cu)
    if m is not None:
        cu.materials.append(m)
    _link(ob, c)
    if parent:
        ob.parent = parent
    return ob


def bezier_path(name, pts, bevel_r, m=None, c=None, parent=None, res=4):
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = bevel_r
    cu.bevel_resolution = res
    cu.use_fill_caps = True
    sp = cu.splines.new("BEZIER")
    sp.bezier_points.add(len(pts) - 1)
    for i, p in enumerate(pts):
        bp = sp.bezier_points[i]
        bp.co = p
        bp.handle_left_type = bp.handle_right_type = "AUTO"
    ob = bpy.data.objects.new(name, cu)
    if m is not None:
        cu.materials.append(m)
    _link(ob, c)
    if parent:
        ob.parent = parent
    return ob


def prism(name, pts, thick, m=None, c=None, plane="XZ", parent=None, offset=0.0):
    """Extrude a 2D outline. plane XZ -> extruded along +Y from `offset`.
    plane XY -> extruded along +Z."""
    bm = bmesh.new()
    if plane == "XZ":
        vs = [bm.verts.new((u, offset, v)) for u, v in pts]
        vec = (0, thick, 0)
    elif plane == "YZ":
        vs = [bm.verts.new((offset, u, v)) for u, v in pts]
        vec = (thick, 0, 0)
    else:
        vs = [bm.verts.new((u, v, offset)) for u, v in pts]
        vec = (0, 0, thick)
    f = bm.faces.new(vs)
    r = bmesh.ops.extrude_face_region(bm, geom=[f])
    nv = [g for g in r["geom"] if isinstance(g, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, verts=nv, vec=vec)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ob = mesh_from_bm(name, bm, m, c)
    if parent:
        ob.parent = parent
    return ob


def rounded_rect_pts(w, h, r, n=6, cx=0.0, cy=0.0):
    pts = []
    for (sx, sy, a0) in ((1, 1, 0), (-1, 1, 90), (-1, -1, 180), (1, -1, 270)):
        ox, oy = cx + sx * (w / 2 - r), cy + sy * (h / 2 - r)
        for i in range(n + 1):
            a = math.radians(a0 + 90 * i / n)
            pts.append((ox + r * math.cos(a), oy + r * math.sin(a)))
    return pts


def boolean(target, cutter, op="DIFFERENCE"):
    mod = target.modifiers.new("Bool", "BOOLEAN")
    mod.operation = op
    mod.object = cutter
    mod.solver = "EXACT"
    cutter.hide_render = True
    cutter.hide_viewport = True
    return mod


def aim(ob, direction, up="Y"):
    """Rotate object so its local -Z points along direction."""
    d = Vector(direction).normalized()
    ob.rotation_mode = "QUATERNION"
    ob.rotation_quaternion = (-d).to_track_quat("Z", up)


def join(objs, name=None):
    """Join objects (applying nothing else). Returns the joined object."""
    if len(objs) == 1:
        return objs[0]
    ctx = {"active_object": objs[0], "selected_objects": objs,
           "selected_editable_objects": objs, "object": objs[0]}
    with bpy.context.temp_override(**ctx):
        bpy.ops.object.join()
    if name:
        objs[0].name = name
    return objs[0]


def uv_plane(name, w, h, m=None, c=None, parent=None, uv=(1.0, 1.0)):
    """Plane in local XZ (facing -Y), UV 0..uv, origin at centre."""
    bm = bmesh.new()
    uvl = bm.loops.layers.uv.new("UVMap")
    vs = [bm.verts.new(p) for p in ((-w / 2, 0, -h / 2), (w / 2, 0, -h / 2), (w / 2, 0, h / 2), (-w / 2, 0, h / 2))]
    f = bm.faces.new(vs)
    for lp, (a, b) in zip(f.loops, ((0, 0), (1, 0), (1, 1), (0, 1))):
        lp[uvl].uv = (a * uv[0], b * uv[1])
    bm.normal_update()
    if f.normal.y > 0:
        f.normal_flip()
    ob = mesh_from_bm(name, bm, m, c)
    if parent:
        ob.parent = parent
    return ob


def ellipsoid(name, center, radii, m=None, c=None, parent=None, segs=24, rings=12):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=segs, v_segments=rings, radius=1.0)
    for v in bm.verts:
        v.co = Vector((v.co.x * radii[0], v.co.y * radii[1], v.co.z * radii[2]))
    ob = mesh_from_bm(name, bm, m, c, smooth=True)
    ob.location = center
    if parent:
        ob.parent = parent
    return ob


def capsule_between(name, p0, p1, r, m=None, c=None, parent=None, verts=12):
    """Cylinder between two points (local coords)."""
    p0, p1 = Vector(p0), Vector(p1)
    d = p1 - p0
    ob = cyl(name, (0, 0, 0), r, d.length, m, verts=verts, c=c, parent=parent)
    ob.location = p0
    ob.rotation_mode = "QUATERNION"
    ob.rotation_quaternion = d.to_track_quat("Z", "Y")
    return ob
