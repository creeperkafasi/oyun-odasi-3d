"""Node based procedural materials."""
import bpy
import lib


def _new(name):
    m = bpy.data.materials.new(name)
    if m.node_tree is None:
        m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    lib._MATS[name] = m
    return m, nt, out


def _principled(nt):
    return nt.nodes.new("ShaderNodeBsdfPrincipled")


def _texcoord(nt, kind="Object", scale=(1, 1, 1), rot=(0, 0, 0)):
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = scale
    mp.inputs["Rotation"].default_value = rot
    nt.links.new(tc.outputs[kind], mp.inputs["Vector"])
    return mp.outputs["Vector"]


def _ramp(nt, inp, stops):
    r = nt.nodes.new("ShaderNodeValToRGB")
    el = r.color_ramp.elements
    el[0].position, el[0].color = stops[0][0], (*stops[0][1], 1)
    el[1].position, el[1].color = stops[-1][0], (*stops[-1][1], 1)
    for p, c in stops[1:-1]:
        e = el.new(p)
        e.color = (*c, 1)
    nt.links.new(inp, r.inputs["Fac"])
    return r.outputs["Color"]


def _noise(nt, vec, scale=5, detail=6, rough=0.5, distortion=0.0):
    n = nt.nodes.new("ShaderNodeTexNoise")
    n.inputs["Scale"].default_value = scale
    n.inputs["Detail"].default_value = detail
    n.inputs["Roughness"].default_value = rough
    n.inputs["Distortion"].default_value = distortion
    nt.links.new(vec, n.inputs["Vector"])
    return n


def _maprange(nt, inp, a, b, c, d):
    m = nt.nodes.new("ShaderNodeMapRange")
    m.inputs["From Min"].default_value = a
    m.inputs["From Max"].default_value = b
    m.inputs["To Min"].default_value = c
    m.inputs["To Max"].default_value = d
    nt.links.new(inp, m.inputs["Value"])
    return m.outputs["Result"]


def _bump(nt, height, strength=0.1, dist=0.01, normal=None):
    b = nt.nodes.new("ShaderNodeBump")
    b.inputs["Strength"].default_value = strength
    b.inputs["Distance"].default_value = dist
    nt.links.new(height, b.inputs["Height"])
    if normal is not None:
        nt.links.new(normal, b.inputs["Normal"])
    return b.outputs["Normal"]


def _mix(nt, a, b, fac, blend="MIX"):
    m = nt.nodes.new("ShaderNodeMix")
    m.data_type = "RGBA"
    m.blend_type = blend
    if isinstance(fac, float):
        m.inputs[0].default_value = fac
    else:
        nt.links.new(fac, m.inputs[0])
    for idx, v in ((6, a), (7, b)):
        if isinstance(v, tuple):
            m.inputs[idx].default_value = (*v, 1) if len(v) == 3 else v
        else:
            nt.links.new(v, m.inputs[idx])
    return m.outputs[2]


# --------------------------------------------------------------------------
def concrete(name="concrete"):
    m, nt, out = _new(name)
    p = _principled(nt)
    v = _texcoord(nt, "Object")
    n1 = _noise(nt, v, 1.6, 10, 0.6)
    n2 = _noise(nt, v, 18, 8, 0.65)
    col = _ramp(nt, n1.outputs["Fac"], [(0.35, (0.055, 0.049, 0.046)), (0.5, (0.085, 0.076, 0.071)), (0.68, (0.12, 0.107, 0.10))])
    col2 = _mix(nt, col, (0.12, 0.115, 0.11), _maprange(nt, n2.outputs["Fac"], 0.55, 0.85, 0, 0.35), "MULTIPLY")
    # big slab seams
    br = nt.nodes.new("ShaderNodeTexBrick")
    br.offset = 0.0
    br.inputs["Scale"].default_value = 1.0
    br.inputs["Mortar Size"].default_value = 0.004
    br.inputs["Brick Width"].default_value = 1.2
    br.inputs["Row Height"].default_value = 1.2
    br.inputs["Color1"].default_value = (1, 1, 1, 1)
    br.inputs["Color2"].default_value = (1, 1, 1, 1)
    br.inputs["Mortar"].default_value = (0, 0, 0, 1)
    nt.links.new(v, br.inputs["Vector"])
    col3 = _mix(nt, col2, (0.05, 0.05, 0.05), _maprange(nt, br.outputs["Fac"], 0, 1, 0, 1), "MIX")
    nt.links.new(col3, p.inputs["Base Color"])
    nt.links.new(_maprange(nt, n2.outputs["Fac"], 0.3, 0.75, 0.08, 0.24), p.inputs["Roughness"])
    nt.links.new(_bump(nt, n2.outputs["Fac"], 0.04), p.inputs["Normal"])
    nt.links.new(p.outputs[0], out.inputs[0])
    return m


def plaster(name, color, rough=0.85, scale=6, bump=0.03):
    m, nt, out = _new(name)
    p = _principled(nt)
    v = _texcoord(nt, "Object")
    n = _noise(nt, v, scale, 8, 0.6)
    c0 = tuple(x * 0.85 for x in color)
    c1 = tuple(min(1, x * 1.12) for x in color)
    nt.links.new(_ramp(nt, n.outputs["Fac"], [(0.3, c0), (0.7, c1)]), p.inputs["Base Color"])
    p.inputs["Roughness"].default_value = rough
    nt.links.new(_bump(nt, n.outputs["Fac"], bump), p.inputs["Normal"])
    nt.links.new(p.outputs[0], out.inputs[0])
    return m


def wood(name, dark=(0.06, 0.035, 0.02), light=(0.16, 0.10, 0.06), rough=0.45,
         axis="Z", scale=1.0, coat=0.0):
    """Veneer. Grain runs along `axis` of object coordinates."""
    m, nt, out = _new(name)
    p = _principled(nt)
    st = {"X": (1, 25, 25), "Y": (25, 1, 25), "Z": (25, 25, 1)}[axis]
    v = _texcoord(nt, "Object", scale=tuple(s * scale for s in st))
    wv = nt.nodes.new("ShaderNodeTexWave")
    wv.wave_type = "BANDS"
    wv.bands_direction = {"X": "Y", "Y": "X", "Z": "X"}[axis] if axis != "Z" else "X"
    wv.inputs["Scale"].default_value = 0.6
    wv.inputs["Distortion"].default_value = 6
    wv.inputs["Detail"].default_value = 3
    wv.inputs["Detail Scale"].default_value = 1.5
    nt.links.new(v, wv.inputs["Vector"])
    n = _noise(nt, v, 0.4, 4, 0.5)
    fac = _mix(nt, wv.outputs["Fac"], n.outputs["Fac"], 0.35)
    col = _ramp(nt, fac, [(0.15, dark), (0.55, tuple((a + b) / 2 for a, b in zip(dark, light))), (0.9, light)])
    nt.links.new(col, p.inputs["Base Color"])
    p.inputs["Roughness"].default_value = rough
    if coat:
        p.inputs["Coat Weight"].default_value = coat
        p.inputs["Coat Roughness"].default_value = 0.15
    nt.links.new(_bump(nt, wv.outputs["Fac"], 0.02), p.inputs["Normal"])
    nt.links.new(p.outputs[0], out.inputs[0])
    m.diffuse_color = (*light, 1)
    return m


def fabric(name, color, rough=0.95, scale=220, bump=0.15, sheen=0.6, var=0.25):
    m, nt, out = _new(name)
    p = _principled(nt)
    v = _texcoord(nt, "Object")
    n = _noise(nt, v, scale, 4, 0.7)
    big = _noise(nt, v, 4, 4, 0.5)
    c0 = tuple(x * (1 - var) for x in color)
    c1 = tuple(min(1, x * (1 + var)) for x in color)
    nt.links.new(_ramp(nt, big.outputs["Fac"], [(0.3, c0), (0.7, c1)]), p.inputs["Base Color"])
    p.inputs["Roughness"].default_value = rough
    p.inputs["Sheen Weight"].default_value = sheen
    p.inputs["Sheen Roughness"].default_value = 0.4
    nt.links.new(_bump(nt, n.outputs["Fac"], bump, 0.002), p.inputs["Normal"])
    nt.links.new(p.outputs[0], out.inputs[0])
    m.diffuse_color = (*color, 1)
    return m


def shag(name, color, scale=60):
    """Shaggy rug - strong noisy bump + colour mottling."""
    m, nt, out = _new(name)
    p = _principled(nt)
    v = _texcoord(nt, "Object")
    n1 = _noise(nt, v, scale, 10, 0.75, 1.5)
    n2 = _noise(nt, v, 3.0, 6, 0.6, 0.5)
    c_dark = tuple(x * 0.45 for x in color)
    c_light = tuple(min(1, x * 1.9) for x in color)
    mott = _ramp(nt, n2.outputs["Fac"], [(0.35, c_dark), (0.5, color), (0.65, c_light)])
    fine = _ramp(nt, n1.outputs["Fac"], [(0.35, (0.35, 0.35, 0.35)), (0.65, (1.3, 1.3, 1.3))])
    col = _mix(nt, mott, fine, 1.0, "MULTIPLY")
    nt.links.new(col, p.inputs["Base Color"])
    p.inputs["Roughness"].default_value = 1.0
    p.inputs["Sheen Weight"].default_value = 0.15
    p.inputs["Sheen Roughness"].default_value = 0.6
    p.inputs["Specular IOR Level"].default_value = 0.2
    nt.links.new(_bump(nt, n1.outputs["Fac"], 0.9, 0.01), p.inputs["Normal"])
    nt.links.new(p.outputs[0], out.inputs[0])
    m.diffuse_color = (*color, 1)
    return m


def leather(name, color, rough=0.38):
    m, nt, out = _new(name)
    p = _principled(nt)
    v = _texcoord(nt, "Object")
    vor = nt.nodes.new("ShaderNodeTexVoronoi")
    vor.inputs["Scale"].default_value = 400
    nt.links.new(v, vor.inputs["Vector"])
    p.inputs["Base Color"].default_value = (*color, 1)
    nt.links.new(_maprange(nt, vor.outputs["Distance"], 0, 1, rough - 0.08, rough + 0.1), p.inputs["Roughness"])
    p.inputs["Coat Weight"].default_value = 0.15
    nt.links.new(_bump(nt, vor.outputs["Distance"], 0.15, 0.001), p.inputs["Normal"])
    nt.links.new(p.outputs[0], out.inputs[0])
    m.diffuse_color = (*color, 1)
    return m


def leaf(name, color, color2=None, translucency=0.35):
    m, nt, out = _new(name)
    p = _principled(nt)
    color2 = color2 or tuple(x * 1.5 for x in color)
    v = _texcoord(nt, "Object")
    n = _noise(nt, v, 25, 3, 0.5)
    obj = nt.nodes.new("ShaderNodeObjectInfo")
    rnd = _mix(nt, color, color2, obj.outputs["Random"] if True else 0.5)
    nt.links.new(_mix(nt, rnd, n.outputs["Color"], 0.12, "OVERLAY"), p.inputs["Base Color"])
    p.inputs["Roughness"].default_value = 0.45
    p.inputs["Specular IOR Level"].default_value = 0.5
    tr = nt.nodes.new("ShaderNodeBsdfTranslucent")
    tr.inputs["Color"].default_value = (*tuple(min(1, c * 1.6) for c in color2), 1)
    mx = nt.nodes.new("ShaderNodeMixShader")
    mx.inputs[0].default_value = translucency
    nt.links.new(p.outputs[0], mx.inputs[1])
    nt.links.new(tr.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], out.inputs[0])
    m.diffuse_color = (*color, 1)
    return m


def leaf_vc(name, translucency=0.35):
    """Leaf material whose colour comes from the 'Col' colour attribute."""
    m, nt, out = _new(name)
    p = _principled(nt)
    at = nt.nodes.new("ShaderNodeAttribute")
    at.attribute_name = "Col"
    nt.links.new(at.outputs["Color"], p.inputs["Base Color"])
    p.inputs["Roughness"].default_value = 0.5
    tr = nt.nodes.new("ShaderNodeBsdfTranslucent")
    nt.links.new(at.outputs["Color"], tr.inputs["Color"])
    mx = nt.nodes.new("ShaderNodeMixShader")
    mx.inputs[0].default_value = translucency
    nt.links.new(p.outputs[0], mx.inputs[1])
    nt.links.new(tr.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], out.inputs[0])
    m.diffuse_color = (0.1, 0.25, 0.05, 1)
    return m


def curtain(name, color=(0.85, 0.82, 0.78), trans=0.55):
    m, nt, out = _new(name)
    p = _principled(nt)
    p.inputs["Base Color"].default_value = (*color, 1)
    p.inputs["Roughness"].default_value = 0.9
    p.inputs["Sheen Weight"].default_value = 0.5
    tr = nt.nodes.new("ShaderNodeBsdfTranslucent")
    tr.inputs["Color"].default_value = (*color, 1)
    tp = nt.nodes.new("ShaderNodeBsdfTransparent")
    mx = nt.nodes.new("ShaderNodeMixShader")
    mx.inputs[0].default_value = trans
    nt.links.new(p.outputs[0], mx.inputs[1])
    nt.links.new(tr.outputs[0], mx.inputs[2])
    mx2 = nt.nodes.new("ShaderNodeMixShader")
    mx2.inputs[0].default_value = 0.25
    nt.links.new(mx.outputs[0], mx2.inputs[1])
    nt.links.new(tp.outputs[0], mx2.inputs[2])
    nt.links.new(mx2.outputs[0], out.inputs[0])
    m.diffuse_color = (*color, 1)
    return m


def image_emit(name, path, strength=2.0, rough=0.2):
    """Screen: image texture as emission + glossy black glass."""
    m, nt, out = _new(name)
    p = _principled(nt)
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(path, check_existing=True)
    tc = nt.nodes.new("ShaderNodeTexCoord")
    nt.links.new(tc.outputs["UV"], tex.inputs["Vector"])
    p.inputs["Base Color"].default_value = (0.0, 0.0, 0.0, 1)
    p.inputs["Roughness"].default_value = rough
    nt.links.new(tex.outputs["Color"], p.inputs["Emission Color"])
    p.inputs["Emission Strength"].default_value = strength
    nt.links.new(p.outputs[0], out.inputs[0])
    m.diffuse_color = (0.2, 0.3, 0.8, 1)
    return m


def image_mat(name, path, rough=0.5, uv=True):
    m, nt, out = _new(name)
    p = _principled(nt)
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(path, check_existing=True)
    tc = nt.nodes.new("ShaderNodeTexCoord")
    nt.links.new(tc.outputs["UV"], tex.inputs["Vector"])
    nt.links.new(tex.outputs["Color"], p.inputs["Base Color"])
    p.inputs["Roughness"].default_value = rough
    nt.links.new(p.outputs[0], out.inputs[0])
    return m


def vcol_mat(name, rough=0.5, metal=0.0, emit_strength=0.0):
    """Base colour from 'Col' colour attribute (books, misc props)."""
    m, nt, out = _new(name)
    p = _principled(nt)
    at = nt.nodes.new("ShaderNodeAttribute")
    at.attribute_name = "Col"
    nt.links.new(at.outputs["Color"], p.inputs["Base Color"])
    p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metal
    if emit_strength:
        nt.links.new(at.outputs["Color"], p.inputs["Emission Color"])
        p.inputs["Emission Strength"].default_value = emit_strength
    nt.links.new(p.outputs[0], out.inputs[0])
    return m


def sky_world(top=(0.12, 0.17, 0.42), mid=(0.42, 0.42, 0.62), horizon=(0.95, 0.65, 0.45), strength=1.0, light_frac=0.25):
    w = bpy.data.worlds.new("Dusk")
    bpy.context.scene.world = w
    if w.node_tree is None:
        w.use_nodes = True
    nt = w.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputWorld")
    bg = nt.nodes.new("ShaderNodeBackground")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Generated"], sep.inputs[0])
    col = _ramp(nt, _maprange(nt, sep.outputs["Z"], -0.05, 0.6, 0, 1),
                [(0.0, (0.05, 0.05, 0.06)), (0.08, horizon), (0.25, mid), (1.0, top)])
    nt.links.new(col, bg.inputs["Color"])
    # camera rays see the full-strength sky; lighting rays get a dimmer one
    lp = nt.nodes.new("ShaderNodeLightPath")
    # Ray Depth ignores transparent bounces -> sky seen through glass counts as "direct"
    st = _maprange(nt, lp.outputs["Ray Depth"], 0, 1, strength, strength * light_frac)
    nt.links.new(st, bg.inputs["Strength"])
    nt.links.new(bg.outputs[0], out.inputs[0])
    return w


def thin_glass(name, tint=(0.96, 0.98, 0.98), refl=(0.03, 0.35)):
    """Window glass without refraction: transparent + fresnel glossy."""
    m, nt, out = _new(name)
    tp = nt.nodes.new("ShaderNodeBsdfTransparent")
    tp.inputs["Color"].default_value = (*tint, 1)
    gl = nt.nodes.new("ShaderNodeBsdfGlossy")
    gl.inputs["Roughness"].default_value = 0.02
    gl.inputs["Color"].default_value = (1, 1, 1, 1)
    lw = nt.nodes.new("ShaderNodeLayerWeight")
    lw.inputs["Blend"].default_value = 0.25
    fac = _maprange(nt, lw.outputs["Fresnel"], 0, 1, refl[0], refl[1])
    mx = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(fac, mx.inputs[0])
    nt.links.new(tp.outputs[0], mx.inputs[1])
    nt.links.new(gl.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], out.inputs[0])
    m.diffuse_color = (0.6, 0.7, 0.75, 0.3)
    return m


def sky_dome(top=(0.16, 0.24, 0.62), mid=(0.42, 0.50, 0.85), horizon=(0.80, 0.66, 0.70), strength=6.0, radius=150):
    """Camera-only emissive sky dome (gradient by elevation)."""
    import bmesh
    m, nt, out = _new("sky_dome")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nrm = nt.nodes.new("ShaderNodeVectorMath")
    nrm.operation = "NORMALIZE"
    nt.links.new(tc.outputs["Object"], nrm.inputs[0])
    nt.links.new(nrm.outputs[0], sep.inputs[0])
    col = _ramp(nt, _maprange(nt, sep.outputs["Z"], -0.02, 0.6, 0, 1),
                [(0.0, horizon), (0.12, horizon), (0.35, mid), (1.0, top)])
    # soft dusk clouds (stretched noise), strongest a little above the horizon
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (1.5, 1.5, 6.0)
    nt.links.new(nrm.outputs[0], mp.inputs["Vector"])
    cn = _noise(nt, mp.outputs["Vector"], 2.5, 6, 0.55, 0.3)
    band = _ramp(nt, sep.outputs["Z"], [(0.02, (0, 0, 0)), (0.10, (1, 1, 1)), (0.45, (0.6, 0.6, 0.6)), (0.8, (0, 0, 0))])
    cl = nt.nodes.new("ShaderNodeMath")
    cl.operation = "MULTIPLY"
    nt.links.new(_maprange(nt, cn.outputs["Fac"], 0.48, 0.68, 0, 0.75), cl.inputs[0])
    sepb = nt.nodes.new("ShaderNodeSeparateColor")
    nt.links.new(band, sepb.inputs[0])
    nt.links.new(sepb.outputs[0], cl.inputs[1])
    col = _mix(nt, col, (0.62, 0.52, 0.62), cl.outputs[0])
    em = nt.nodes.new("ShaderNodeEmission")
    nt.links.new(col, em.inputs["Color"])
    em.inputs["Strength"].default_value = strength
    nt.links.new(em.outputs[0], out.inputs[0])
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=64, v_segments=32, radius=radius)
    bmesh.ops.reverse_faces(bm, faces=bm.faces)
    ob = lib.mesh_from_bm("SkyDome", bm, m, c="Exterior")
    ob.location = (0, 0, -2)
    ob.visible_diffuse = False
    ob.visible_shadow = False
    ob.visible_volume_scatter = False
    ob.visible_glossy = False
    ob.visible_transmission = True
    return ob


def shag_fiber(name, color, contrast=1.0):
    """Fibre material for instanced rug strands: world-space mottling + per-strand random."""
    m, nt, out = _new(name)
    p = _principled(nt)
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    n = nt.nodes.new("ShaderNodeTexNoise")
    n.inputs["Scale"].default_value = 2.2
    n.inputs["Detail"].default_value = 6
    n.inputs["Roughness"].default_value = 0.6
    n.inputs["Distortion"].default_value = 0.8
    nt.links.new(geo.outputs["Position"], n.inputs["Vector"])
    c_dark = tuple(x * (1 - 0.6 * contrast) for x in color)
    c_light = tuple(min(1, x * (1 + 1.3 * contrast)) for x in color)
    mott = _ramp(nt, n.outputs["Fac"], [(0.35, c_dark), (0.5, color), (0.65, c_light)])
    oi = nt.nodes.new("ShaderNodeObjectInfo")
    rnd = _maprange(nt, oi.outputs["Random"], 0, 1, 0.55, 1.35)
    col = _mix(nt, mott, (1, 1, 1), 0.0)
    mul = nt.nodes.new("ShaderNodeVectorMath")
    mul.operation = "SCALE"
    nt.links.new(mott, mul.inputs[0])
    nt.links.new(rnd, mul.inputs["Scale"])
    nt.links.new(mul.outputs[0], p.inputs["Base Color"])
    p.inputs["Roughness"].default_value = 0.85
    p.inputs["Sheen Weight"].default_value = 0.3
    p.inputs["Specular IOR Level"].default_value = 0.3
    nt.links.new(p.outputs[0], out.inputs[0])
    m.diffuse_color = (*color, 1)
    return m
