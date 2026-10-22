"""Gaming room – procedural Blender scene.

Coordinates (metres): X → east, Y → north, Z ↑.
Origin = interior south-west corner of the room (bottom-left room of the plan).
Room interior 5.24 x 3.63 (from the PDF plan), camera looks west.

Run:  blender -b -P scene/build.py -- --mode cycles --out out/x.png --pct 50 --samples 64
"""
import sys, os, math, argparse, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bpy
from mathutils import Vector
import lib
import materials as MT
from lib import box, cyl, mat, emission_mat
from cfg import W, D, H, CAM, DESK, VR, RING

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
ap = argparse.ArgumentParser()
ap.add_argument("--mode", default="cycles")          # quick | cycles
ap.add_argument("--out", default="out/render.png")
ap.add_argument("--samples", type=int, default=64)
ap.add_argument("--pct", type=int, default=50)
ap.add_argument("--save", default="")
ap.add_argument("--nofur", action="store_true")
ap.add_argument("--norender", action="store_true")
ap.add_argument("--cam", default="main")
ap.add_argument("--exposure", type=float, default=1.1)
ap.add_argument("--view", default="AgX")
ap.add_argument("--look", default="AgX - Medium High Contrast")
A = ap.parse_args(argv)

T0 = time.time()
lib.reset()
scene = bpy.context.scene
TEX = os.path.join(HERE, "..", "tex")


# ------------------------------------------------------------------ materials
def materials():
    MT.concrete("concrete")
    MT.plaster("wall", (0.105, 0.092, 0.080), rough=0.85)
    MT.plaster("ceiling", (0.035, 0.036, 0.042), rough=0.9, bump=0.01)
    MT.plaster("render_ext", (0.32, 0.30, 0.28), rough=0.9)
    MT.wood("wood_back", dark=(0.035, 0.022, 0.014), light=(0.085, 0.055, 0.035), rough=0.6, axis="Z")
    MT.wood("wood_shelfback", dark=(0.035, 0.022, 0.014), light=(0.09, 0.06, 0.037), rough=0.55, axis="Z")
    MT.wood("wood_dark", dark=(0.045, 0.028, 0.017), light=(0.12, 0.075, 0.045), rough=0.45, axis="Y")
    MT.wood("wood_mid", dark=(0.09, 0.055, 0.03), light=(0.24, 0.15, 0.085), rough=0.5, axis="Z")
    MT.wood("wood_panel", dark=(0.05, 0.032, 0.02), light=(0.12, 0.08, 0.05), rough=0.5, axis="Z", scale=0.7)
    MT.wood("door_wood", dark=(0.035, 0.022, 0.014), light=(0.08, 0.052, 0.033), rough=0.45, axis="Z", scale=0.8)
    MT.wood("desk_wood", dark=(0.22, 0.14, 0.085), light=(0.45, 0.29, 0.18), rough=0.35, axis="X", coat=0.3)
    MT.wood("desk_wood_v", dark=(0.22, 0.14, 0.085), light=(0.45, 0.29, 0.18), rough=0.4, axis="Z")
    MT.wood("wood_soffit", dark=(0.08, 0.05, 0.03), light=(0.18, 0.12, 0.07), rough=0.6, axis="X")
    mat("cabinet", (0.030, 0.030, 0.032), rough=0.45)
    mat("cabinet_in", (0.02, 0.02, 0.022), rough=0.6)
    mat("black_metal", (0.02, 0.02, 0.02), rough=0.3, metal=0.9)
    mat("black_metal_matte", (0.012, 0.012, 0.013), rough=0.55, metal=0.6)
    mat("black_matte", (0.01, 0.01, 0.01), rough=0.7)
    mat("alu_black", (0.015, 0.015, 0.016), rough=0.35, metal=0.8)
    mat("chrome_dark", (0.3, 0.3, 0.32), rough=0.15, metal=1.0)
    mat("plastic_black", (0.012, 0.012, 0.013), rough=0.4)
    MT.leather("leather_black", (0.010, 0.010, 0.011), rough=0.45)
    MT.leather("leather_grey", (0.03, 0.03, 0.032), rough=0.40)
    mat("emblem_white", (0.7, 0.7, 0.72), rough=0.4)
    MT.fabric("fabric_sofa", (0.030, 0.031, 0.036), scale=260, bump=0.3, sheen=0.12)
    MT.fabric("knit", (0.02, 0.02, 0.022), scale=90, bump=0.6, sheen=0.15)
    MT.shag("rug_round", (0.12, 0.11, 0.105), scale=70)
    MT.shag("rug_rect", (0.09, 0.085, 0.08), scale=70)
    MT.shag_fiber("fiber_round", (0.12, 0.118, 0.12), contrast=1.3)
    MT.shag_fiber("fiber_rect", (0.085, 0.083, 0.085), contrast=1.3)
    mat("vr_mat", (0.018, 0.019, 0.022), rough=0.6)
    MT.thin_glass("glass", refl=(0.01, 0.06))
    MT.thin_glass("glass_dark", tint=(0.35, 0.37, 0.42), refl=(0.05, 0.3))
    mat("glass_rail", (0.85, 0.9, 0.9), rough=0.02, transmission=1.0, ior=1.5)
    mat("blind", (0.035, 0.035, 0.037), rough=0.45, metal=0.3)
    MT.curtain("curtain_sheer", (0.92, 0.86, 0.80), trans=0.6)
    MT.fabric("curtain_dark", (0.02, 0.02, 0.025), scale=150, bump=0.1)
    mat("lampshade", (1.0, 0.92, 0.8), rough=0.8, emit=(1.0, 0.75, 0.48), strength=6.0)
    mat("slat_black", (0.014, 0.014, 0.015), rough=0.55)
    pegboard()
    MT.leaf_vc("leaf_vc", 0.3)
    MT.leaf_vc("leaf_glossy", 0.25)
    lib.get_mat("leaf_glossy").node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.28
    MT.leaf_vc("leaf_vc_tree", 0.45)
    mat("stem", (0.05, 0.04, 0.02), rough=0.7)
    mat("stem_green", (0.05, 0.10, 0.02), rough=0.6)
    mat("soil", (0.02, 0.015, 0.01), rough=1.0)
    mat("bark", (0.05, 0.04, 0.03), rough=0.9)
    terrace_tile()
    mat("stone_light", (0.45, 0.43, 0.40), rough=0.7)
    MT.fabric("grass", (0.03, 0.06, 0.02), scale=40, bump=0.4)
    mat("outdoor_frame", (0.035, 0.035, 0.038), rough=0.5, metal=0.3)
    MT.fabric("outdoor_fabric", (0.42, 0.40, 0.38), scale=200, bump=0.2)
    MT.fabric("outdoor_fabric2", (0.42, 0.40, 0.37), scale=200, bump=0.2)
    mat("planter_grey", (0.12, 0.12, 0.12), rough=0.5)
    mat("hill_haze", (0.15, 0.17, 0.28), rough=1.0, emit=(0.30, 0.34, 0.52), strength=1.5)
    mat("pot_black", (0.015, 0.015, 0.016), rough=0.35)
    mat("pot_white", (0.55, 0.53, 0.5), rough=0.35)
    mat("pot_grey", (0.06, 0.06, 0.065), rough=0.4)
    mat("black_matte_sh", (0.02, 0.02, 0.02), rough=0.25)
    # emitters
    emission_mat("led_warm", (1.0, 0.60, 0.30), 25)
    emission_mat("led_warm_soft", (1.0, 0.62, 0.34), 6)
    emission_mat("led_blue", (0.04, 0.16, 1.0), 6)
    emission_mat("led_blue_floor", (0.05, 0.2, 1.0), 6)
    emission_mat("led_blue_ring", (0.0, 0.09, 1.0), 1.6)
    emission_mat("led_blue_ring_soft", (0.06, 0.22, 1.0), 2)
    emission_mat("led_spot", (1.0, 0.78, 0.55), 40)
    mat("screen", (0.01, 0.01, 0.01), rough=0.2, emit=(0.25, 0.4, 1.0), strength=3.0)


def pegboard():
    m, nt, out = MT._new("pegboard")
    p = nt.nodes.new("ShaderNodeBsdfPrincipled")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Object"], sep.inputs[0])
    comb = nt.nodes.new("ShaderNodeCombineXYZ")
    nt.links.new(sep.outputs["X"], comb.inputs["X"])
    nt.links.new(sep.outputs["Z"], comb.inputs["Y"])
    vor = nt.nodes.new("ShaderNodeTexVoronoi")
    vor.voronoi_dimensions = "2D"
    vor.inputs["Scale"].default_value = 38
    vor.inputs["Randomness"].default_value = 0.0
    nt.links.new(comb.outputs[0], vor.inputs["Vector"])
    hole = MT._maprange(nt, vor.outputs["Distance"], 0.16, 0.20, 0, 1)
    col = MT._mix(nt, (0.0, 0.0, 0.0), (0.018, 0.018, 0.02), hole)
    nt.links.new(col, p.inputs["Base Color"])
    p.inputs["Roughness"].default_value = 0.5
    nt.links.new(MT._bump(nt, hole, 0.5, 0.004), p.inputs["Normal"])
    nt.links.new(p.outputs[0], out.inputs[0])


def terrace_tile():
    m, nt, out = MT._new("terrace_tile")
    p = nt.nodes.new("ShaderNodeBsdfPrincipled")
    v = MT._texcoord(nt, "Object")
    br = nt.nodes.new("ShaderNodeTexBrick")
    br.inputs["Scale"].default_value = 1.0
    br.inputs["Brick Width"].default_value = 0.6
    br.inputs["Row Height"].default_value = 0.3
    br.inputs["Mortar Size"].default_value = 0.004
    br.inputs["Color1"].default_value = (0.30, 0.25, 0.22, 1)
    br.inputs["Color2"].default_value = (0.36, 0.30, 0.26, 1)
    br.inputs["Mortar"].default_value = (0.06, 0.05, 0.045, 1)
    nt.links.new(v, br.inputs["Vector"])
    nt.links.new(br.outputs["Color"], p.inputs["Base Color"])
    p.inputs["Roughness"].default_value = 0.22
    nt.links.new(p.outputs[0], out.inputs[0])


# ------------------------------------------------------------------ build
import arch, joinery as BI, furniture as FU, exterior as EX, lighting as LI, plants as PL, props as PR

materials()
PR.tex_materials()
FU.FUR = not A.nofur
MT.sky_world(top=(0.20, 0.24, 0.40), mid=(0.40, 0.42, 0.55), horizon=(0.6, 0.5, 0.5), strength=0.5, light_frac=1.0)
MT.sky_dome(top=(0.06, 0.10, 0.36), mid=(0.22, 0.30, 0.66), horizon=(0.46, 0.46, 0.66), strength=1.5)
arch.shell()
arch.sliding_door()
arch.west_window()
arch.door()
arch.curtains()
BI.west_wall()
BI.north_wall()
BI.desk()
FU.rugs()
FU.vr_zone()
FU.ceiling_ring()
spots = FU.track_lights()

# hide the cove LED emitters from direct view (they still light the scene)
for nm in ("LED_slat_top", "Cove_S_led"):
    o = bpy.data.objects.get(nm)
    if o:
        o.visible_camera = False
        o.visible_glossy = False
FU.gaming_chair()
FU.sofa_group()
FU.side_table("STable1", (1.88, 0.42), r=0.24, h=0.46)
FU.side_table("STable2", (1.10, 0.36), r=0.20, h=0.58)
FU.floor_lamp((0.58, 0.22))
fc = FU.front_cabinet()
ter_lights = EX.terrace()
EX.garden()

PR.desk_setup()
PR.pegboard_items()
PR.wall_shelf_items()
PR.back_shelves(BI.COMPARTMENTS)
PR.room_decor(fc)
# north-east corner (outside the reference frame): tall plant
PL.pot("NEPot", (4.95, 3.30, 0), 0.19, 0.50, lib.get_mat("pot_black"))
PL.leafy_plant("NEPlant", (4.95, 3.30, 0.48), height=1.3, stems=12, seed=9, leaf_len=0.24)


# ------------------------------------------------------------------ lights
def lights():
    for i, (p, d) in enumerate(spots):
        LI.spot(f"Spot{i}", p, d, energy=60, size=40, blend=0.75)
    for i, (x0, x1, y0, y1, zb, zt) in enumerate(BI.COMPARTMENTS):
        LI.area(f"Shelf{i}", ((x0 + x1) / 2 + 0.05, (y0 + y1) / 2, zt - 0.01), (0, 0, -1), (x1 - x0) * 0.7, (y1 - y0) * 0.9, 8.0, LI.WARM2)
    # desk / monitors glow
    LI.area("MonGlow", (2.75, D - 0.34, 1.15), (0, -1, 0), 1.3, 0.35, 5, LI.BLUE)
    LI.area("DeskUnder", (2.5, D - 0.12, 0.70), (0, -0.3, -1), 1.4, 0.1, 8, LI.BLUE)
    LI.area("PegWash", (2.9, D - 0.20, 1.86), (0, 0.35, -1), 1.6, 0.12, 10, LI.BLUE)
    LI.area("SlatGraze", (3.0, D - 0.14, H - 0.03), (0, 0.25, -1), 2.6, 0.06, 30, LI.WARM)
    # soft warm fill (bounce from the warm LEDs), invisible to camera
    for i, (fx, fy) in enumerate(((1.2, 1.2), (3.2, 1.6), (2.2, 2.8))):
        f = LI.area(f"Fill{i}", (fx, fy, H - 0.05), (0, 0, -1), 1.6, 1.2, 12, LI.WARM)
        f.visible_camera = False
        f.visible_glossy = False
    LI.area("VRGlow", (VR["x"], VR["y"], 0.03), (0, 0, 1), 1.2, 1.2, 0.8, LI.BLUE)
    for i, (fx, fy) in enumerate(((3.2, 1.9), (2.0, 2.1))):
        LI.spot(f"FloorPool{i}", (fx, fy, H - 0.05), (0, 0, -1), energy=35, size=45, blend=0.9)
    LI.spot("FrontPlants", (4.3, 0.48, H - 0.25), (-0.15, 0.55, -1.0), energy=60, size=35, blend=0.8)
    LI.spot("PlantKey", (0.95, 0.48, H - 0.25), (-0.55, 0.38, -1.0), energy=40, size=28, blend=0.6)
    LI.spot("CurtainWash", (0.62, 0.30, H - 0.08), (0.0, -0.6, -1.0), energy=40, size=35, blend=0.9)
    LI.point("LampBulb", (0.58, 0.22, 0.68), 6, LI.WARM, 0.05)
    # exterior
    for i, (p, e) in enumerate(ter_lights):
        LI.spot(f"TerUp{i}", p, (0, 0, 1), energy=e * 4, size=80, blend=1.0, color=(1, 0.65, 0.35))
    for i, x in enumerate((0.6, 1.8, 3.0)):
        LI.spot(f"TerDown{i}", (x, -0.85, H + 0.20), (0, 0, -1), energy=220, size=100, blend=0.8)
    # low dusk sun – light-linked so it only lights the garden / terrace
    sun = LI._light("DuskSun", "SUN", (0, 0, 10), 5.0, (1.0, 0.60, 0.32))
    sun.data.angle = math.radians(3)
    lib.aim(sun, (-0.75, -0.62, -0.18))
    rc = bpy.data.collections.new("SunReceivers")
    for cn in ("Exterior", "Garden"):
        rc.children.link(lib.coll(cn))
    sun.light_linking.receiver_collection = rc
    sun.light_linking.blocker_collection = rc
    for i, (gx, gy) in enumerate(((-1.5, -3.2), (1.5, -3.5), (4.0, -3.2), (-7.5, 0.0), (-7.5, 2.5), (-7.5, 5.0))):
        LI.spot(f"GardenUp{i}", (gx, gy, 0.0), (0, 0, 1), energy=900, size=70, blend=1.0, color=(1, 0.62, 0.32))


lights()

# hide the cove LED emitters from direct view (they still light the scene)
for nm in ("LED_slat_top", "Cove_S_led"):
    o = bpy.data.objects.get(nm)
    if o:
        o.visible_camera = False
        o.visible_glossy = False


# ------------------------------------------------------------------ camera
def camera():
    cd = bpy.data.cameras.new("Cam")
    cd.lens = CAM["lens"]
    cd.sensor_fit = "HORIZONTAL"
    cd.sensor_width = 36
    cd.shift_x = CAM["shift_x"]
    cd.shift_y = CAM["shift_y"]
    cd.clip_start = 0.05
    cd.dof.use_dof = A.mode != "quick"
    cd.dof.focus_distance = 3.2
    cd.dof.aperture_fstop = 1.6
    ob = bpy.data.objects.new("Cam", cd)
    scene.collection.objects.link(ob)
    ob.location = CAM["loc"]
    ob.rotation_euler = (math.radians(90), 0, math.radians(90 + CAM.get("yaw", 0)))
    scene.camera = ob
    # extra views of the same model
    views = {
        "desk": dict(loc=(0.95, 1.15, 1.45), tgt=(3.0, 3.3, 0.95), lens=20),
        "sofa": dict(loc=(3.4, 3.25, 1.55), tgt=(1.2, 0.3, 0.6), lens=18),
        "back": dict(loc=(3.9, 2.4, 1.35), tgt=(0.0, 1.9, 1.2), lens=22),
    }
    for nm, v in views.items():
        c2 = bpy.data.cameras.new("Cam_" + nm)
        c2.lens = v["lens"]
        c2.clip_start = 0.05
        o2 = bpy.data.objects.new("Cam_" + nm, c2)
        scene.collection.objects.link(o2)
        o2.location = v["loc"]
        o2.rotation_euler = (Vector(v["tgt"]) - Vector(v["loc"])).to_track_quat("-Z", "Y").to_euler()
    ct = bpy.data.cameras.new("Cam_top")
    ct.type = "ORTHO"
    ct.ortho_scale = 7.2
    ot = bpy.data.objects.new("Cam_top", ct)
    scene.collection.objects.link(ot)
    ct.ortho_scale = 8.4
    ct.clip_start = 1.0
    ct.clip_end = 60
    ot.rotation_euler = (math.radians(55), 0, math.radians(35))
    dirv = ot.rotation_euler.to_matrix() @ Vector((0, 0, -1))
    ot.location = Vector((2.55, 1.75, 0.6)) - dirv * 22
    if A.cam != "main":
        scene.camera = bpy.data.objects["Cam_" + A.cam]
        if A.cam == "top":
            for o in scene.objects:
                colls = {c.name for c in o.users_collection}
                if (o.name.startswith(("Ceiling", "Track", "Ring_", "Ter_", "OSofa", "SkyDome", "Hill", "Curtain", "Cove"))
                        or o.name in ("WallS_a", "WallS_b", "WallS_head", "WallE", "Skirt_E", "Skirt_S_east", "Ground")
                        or colls & {"Garden"}):
                    o.visible_camera = False
            scene.render.film_transparent = True


camera()


def render_setup():
    r = scene.render
    r.resolution_x, r.resolution_y = 1447, 1087
    r.resolution_percentage = A.pct
    r.filepath = os.path.abspath(A.out)
    scene.view_settings.view_transform = A.view
    scene.view_settings.look = A.look if A.view == "AgX" else "None"
    scene.view_settings.exposure = A.exposure
    if A.mode == "quick":
        r.engine = "BLENDER_WORKBENCH"
        sh = scene.display.shading
        sh.light = "FLAT"
        sh.color_type = "MATERIAL"
        scene.view_settings.view_transform = "Standard"
        return
    r.engine = "CYCLES"
    c = scene.cycles
    prefs = bpy.context.preferences.addons["cycles"].preferences
    prefs.compute_device_type = "OPTIX"
    prefs.get_devices()
    for d in prefs.devices:
        d.use = d.type == "OPTIX"
    c.device = "GPU"
    c.samples = A.samples
    c.use_adaptive_sampling = True
    c.adaptive_threshold = 0.02
    c.use_denoising = True
    c.denoiser = "OPTIX"
    c.max_bounces = 8
    c.diffuse_bounces = 4
    c.glossy_bounces = 4
    c.transmission_bounces = 8
    c.transparent_max_bounces = 8
    c.caustics_reflective = False
    c.caustics_refractive = False
    c.sample_clamp_indirect = 8
    c.light_sampling_threshold = 0.01


render_setup()
print(f"BUILD {time.time() - T0:.1f}s  objects={len(bpy.data.objects)}")
if A.save:
    try:
        bpy.ops.file.pack_all()
    except Exception as e:
        print("pack failed", e)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(A.save))
if not A.norender:
    bpy.ops.render.render(write_still=True)
    print(f"RENDERED {A.out} total {time.time() - T0:.1f}s")
