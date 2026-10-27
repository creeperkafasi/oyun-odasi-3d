"""Geometry Nodes fur for shag rugs / fluffy surfaces.

fur(rug_obj, fiber_material, density=32000, length=0.04)
Pair with materials.shag (base) + materials.shag_fiber (strands).
"""
import math
import bpy
import lib

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
