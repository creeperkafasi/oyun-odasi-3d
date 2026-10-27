"""Export the interior to .glb (run on out/scene.blend).

glTF cannot carry the procedural node graphs, so every material is flattened to
a Principled BSDF with its viewport colour; emitters keep colour + strength,
image textures (screens, posters, game spines) are kept.
Fur instances, distant garden, sky dome and hills are left out.

blender -b scene.blend -P export_glb.py -- out.glb [--nodraco] [--lite] [--skip PREFIX ...]

--nodraco : plain GLB (needed for browser viewers that cannot fetch the Draco decoder)
--lite    : also drop exterior trees / garden (prefixes in LITE_PREFIXES) to shrink the file
--skip    : extra object-name prefixes to leave out
Work on a COPY of the .blend - materials are flattened in place.
"""
import bpy, sys, os

args = sys.argv[sys.argv.index("--") + 1:]
out = os.path.abspath(args[0])
DRACO = "--nodraco" not in args
LITE = "--lite" in args
EXTRA = tuple(args[args.index("--skip") + 1:]) if "--skip" in args else ()
LITE_PREFIXES = ("Ter_tree", "ConS", "TreeS", "TreeW", "ConW", "Tree", "Conifer")
SKIP_COLL = {"Garden", "Protos"}
SKIP_NAMES = ("SkyDome", "Hill", "Ground")

# fur off (geometry nodes instances)
for o in bpy.data.objects:
    for m in o.modifiers:
        if m.type == "NODES":
            m.show_render = m.show_viewport = False


def flatten(m):
    nt = m.node_tree
    if nt is None:
        return
    nodes = nt.nodes
    outn = next((n for n in nodes if n.type == "OUTPUT_MATERIAL"), None)
    tex = next((n for n in nodes if n.type == "TEX_IMAGE"), None)
    emis = next((n for n in nodes if n.type == "EMISSION"), None)
    pb = next((n for n in nodes if n.type == "BSDF_PRINCIPLED"), None)
    col = tuple(m.diffuse_color)
    if tex is not None and pb is not None:
        return                      # image based: exporter handles it
    rough = pb.inputs["Roughness"].default_value if pb else 0.5
    metal = pb.inputs["Metallic"].default_value if pb else 0.0
    e_col, e_str = None, 0.0
    if emis is not None:
        e_col = tuple(emis.inputs["Color"].default_value)
        e_str = emis.inputs["Strength"].default_value
    elif pb is not None and pb.inputs["Emission Strength"].default_value > 0 and not pb.inputs["Emission Color"].is_linked:
        e_col = tuple(pb.inputs["Emission Color"].default_value)
        e_str = pb.inputs["Emission Strength"].default_value
    trans = pb.inputs["Transmission Weight"].default_value if pb else 0.0
    for n in list(nodes):
        if n != outn:
            nodes.remove(n)
    p = nodes.new("ShaderNodeBsdfPrincipled")
    p.inputs["Base Color"].default_value = col if emis is None else (0, 0, 0, 1)
    p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metal
    if e_col is not None:
        p.inputs["Emission Color"].default_value = e_col
        p.inputs["Emission Strength"].default_value = min(e_str, 10.0)
    if m.name.startswith(("glass", "glass_rail")) or trans > 0.5:
        p.inputs["Base Color"].default_value = (0.8, 0.85, 0.9, 1)
        p.inputs["Alpha"].default_value = 0.18
        p.inputs["Roughness"].default_value = 0.05
        m.surface_render_method = "BLENDED"
    if m.name.startswith("curtain_sheer"):
        p.inputs["Alpha"].default_value = 0.55
        m.surface_render_method = "BLENDED"
    nt.links.new(p.outputs[0], outn.inputs["Surface"])


for m in bpy.data.materials:
    flatten(m)

# leaf vertex colours -> a sensible green base
for nm in ("leaf_vc", "leaf_glossy", "leaf_vc_tree"):
    m = bpy.data.materials.get(nm)
    if m:
        m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.09, 0.22, 0.05, 1)

keep = []
for o in bpy.data.objects:
    colls = {c.name for c in o.users_collection}
    lite_skip = (LITE and o.name.startswith(LITE_PREFIXES)) or (EXTRA and o.name.startswith(EXTRA))
    if lite_skip or colls & SKIP_COLL or o.name.startswith(SKIP_NAMES) or o.type in ("LIGHT", "CAMERA"):
        o.select_set(False)
        continue
    if o.type in ("MESH", "CURVE", "EMPTY"):
        o.select_set(True)
        keep.append(o)

bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", use_selection=True,
                          export_apply=True, export_yup=True, export_lights=False,
                          export_cameras=False, export_draco_mesh_compression_enable=DRACO,
                          export_draco_mesh_compression_level=6)
print("GLB", out, os.path.getsize(out) / 1e6, "MB", len(keep), "objects")
