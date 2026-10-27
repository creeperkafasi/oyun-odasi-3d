"""Starter scene: room shell with openings, camera from camsolve, dusk sky dome,
light-linked exterior sun, Cycles/OptiX render setup. Copy this next to the
other scripts in your project and grow it (add furniture() / props() etc.).

blender -b -P template_build.py -- --room room.json [--cam camera.json] \
        --out out/x.png --pct 50 --samples 64 [--quick] [--save out/x.blend]

room.json (metres, origin = interior south-west corner, X east, Y north, Z up):
{
  "size": [5.24, 3.63, 2.65], "wall": 0.20,
  "openings": [
    {"wall": "W", "from": 1.20, "to": 2.71, "z": [1.10, 2.35], "kind": "window"},
    {"wall": "S", "from": 0.53, "to": 3.01, "z": [0.0, 2.45], "kind": "slide"},
    {"wall": "N", "from": 0.726, "to": 1.50, "z": [0.0, 2.12], "kind": "door"}
  ]
}
"from"/"to" run along the wall: X for S/N walls, Y for W/E walls.
"""
import sys, os, math, json, argparse
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bpy
from mathutils import Vector
import lib
import materials as MT
import lighting as LI
from lib import box, mat, emission_mat

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
ap = argparse.ArgumentParser()
ap.add_argument("--room", required=True)
ap.add_argument("--cam", default="")
ap.add_argument("--out", default="out/render.png")
ap.add_argument("--samples", type=int, default=64)
ap.add_argument("--pct", type=int, default=50)
ap.add_argument("--exposure", type=float, default=0.8)
ap.add_argument("--quick", action="store_true", help="workbench flat render for framing checks")
ap.add_argument("--save", default="")
ap.add_argument("--norender", action="store_true")
A = ap.parse_args(argv)

R = json.load(open(A.room))
W, D, H = R["size"]
T = R.get("wall", 0.2)
lib.reset()
scene = bpy.context.scene


# ------------------------------------------------------------------ materials
def materials():
    MT.concrete("floor")
    MT.plaster("wall", (0.30, 0.28, 0.26))
    MT.plaster("ceiling", (0.20, 0.20, 0.21), bump=0.01)
    MT.thin_glass("glass", refl=(0.01, 0.08))
    mat("frame", (0.015, 0.015, 0.016), rough=0.35, metal=0.8)
    MT.wood("door", dark=(0.07, 0.045, 0.028), light=(0.17, 0.11, 0.07), axis="Z")
    MT.fabric("grass", (0.03, 0.06, 0.02), scale=40, bump=0.4)
    emission_mat("led_warm", (1.0, 0.60, 0.30), 20)


# ------------------------------------------------------------------ shell
def wall_with_openings(side):
    """Build one wall as solid boxes around its openings."""
    ops = sorted([o for o in R["openings"] if o["wall"] == side], key=lambda o: o["from"])
    length = W if side in "SN" else D

    def seg(a, b, z0, z1, name):
        if b - a < 1e-4 or z1 - z0 < 1e-4:
            return
        if side == "S":
            box(name, (a, -T, z0), (b, 0, z1), lib.get_mat("wall"))
        elif side == "N":
            box(name, (a, D, z0), (b, D + T, z1), lib.get_mat("wall"))
        elif side == "W":
            box(name, (-T, a, z0), (0, b, z1), lib.get_mat("wall"))
        else:
            box(name, (W, a, z0), (W + T, b, z1), lib.get_mat("wall"))

    cur = -T
    for i, o in enumerate(ops):
        seg(cur, o["from"], 0, H, f"Wall{side}_{i}")
        seg(o["from"], o["to"], 0, o["z"][0], f"Wall{side}_{i}_below")
        seg(o["from"], o["to"], o["z"][1], H, f"Wall{side}_{i}_above")
        cur = o["to"]
    seg(cur, length + T, 0, H, f"Wall{side}_end")


def opening_fill(o, i):
    """Glass + black frame for windows/slides, a closed leaf for doors."""
    a, b = o["from"], o["to"]
    z0, z1 = o["z"]
    t = -T / 2
    def bx(name, u0, u1, zz0, zz1, d0, d1, m):
        side = o["wall"]
        if side == "S":
            box(name, (u0, d0, zz0), (u1, d1, zz1), m)
        elif side == "N":
            box(name, (u0, D - d1, zz0), (u1, D - d0, zz1), m)
        elif side == "W":
            box(name, (d0, u0, zz0), (d1, u1, zz1), m)
        else:
            box(name, (W - d1, u0, zz0), (W - d0, u1, zz1), m)
    if o["kind"] == "door":
        bx(f"Door{i}", a + 0.005, b - 0.005, z0 + 0.008, z1 - 0.004, t - 0.02, t + 0.02, lib.get_mat("door"))
        return
    fr = 0.05
    bx(f"Open{i}_glass", a, b, z0, z1, t - 0.004, t + 0.004, lib.get_mat("glass"))
    for k, (u0, u1, zz0, zz1) in enumerate(((a, a + fr, z0, z1), (b - fr, b, z0, z1), (a, b, z0, z0 + fr), (a, b, z1 - fr, z1))):
        bx(f"Open{i}_fr{k}", u0, u1, zz0, zz1, t - 0.03, t + 0.03, lib.get_mat("frame"))
    n = 3 if o["kind"] == "slide" else 2
    for k in range(1, n):
        u = a + (b - a) * k / n
        bx(f"Open{i}_mull{k}", u - fr / 2, u + fr / 2, z0, z1, t - 0.03, t + 0.03, lib.get_mat("frame"))


def shell():
    lib.set_coll("Architecture")
    box("Floor", (-T, -T, -0.1), (W + T, D + T, 0), lib.get_mat("floor"))
    box("Ceiling", (-T, -T, H), (W + T, D + T, H + 0.2), lib.get_mat("ceiling"))
    for s in "SNWE":
        wall_with_openings(s)
    lib.set_coll("Openings")
    for i, o in enumerate(R["openings"]):
        opening_fill(o, i)
    lib.set_coll("Exterior")
    box("Ground", (-40, -40, -0.5), (40, 40, -0.12), lib.get_mat("grass"))


# ------------------------------------------------------------------ lights
def lights():
    # placeholder interior lighting: a soft warm ceiling panel per ~4 m2
    nx, ny = max(1, round(W / 2)), max(1, round(D / 2))
    for i in range(nx):
        for j in range(ny):
            LI.area(f"Ceil_{i}_{j}", ((i + 0.5) * W / nx, (j + 0.5) * D / ny, H - 0.02), (0, 0, -1),
                    0.6, 0.6, 40, LI.WARM)
    # dusk sun lighting only the outside (light linking + shadow linking)
    sun = LI._light("DuskSun", "SUN", (0, 0, 10), 4.0, (1.0, 0.6, 0.32))
    sun.data.angle = math.radians(3)
    lib.aim(sun, (-0.7, -0.6, -0.2))
    rc = bpy.data.collections.new("SunReceivers")
    rc.children.link(lib.coll("Exterior"))
    sun.light_linking.receiver_collection = rc
    sun.light_linking.blocker_collection = rc


# ------------------------------------------------------------------ camera
def camera():
    cd = bpy.data.cameras.new("Cam")
    cd.sensor_fit = "HORIZONTAL"
    cd.sensor_width = 36
    cd.clip_start = 0.05
    ob = bpy.data.objects.new("Cam", cd)
    scene.collection.objects.link(ob)
    if A.cam:
        C = json.load(open(A.cam))
        cd.lens, cd.shift_x, cd.shift_y = C["lens_mm"], C["shift_x"], C["shift_y"]
        ob.location = C["loc"]
        ob.rotation_euler = (math.radians(90), 0, math.radians(C["rot_z_deg"]))
        scene.render.resolution_x, scene.render.resolution_y = C["image"]
    else:   # default: from the east wall looking west
        cd.lens = 18
        ob.location = (W - 0.3, D / 2, 1.35)
        ob.rotation_euler = (math.radians(90), 0, math.radians(90))
        scene.render.resolution_x, scene.render.resolution_y = 1600, 1200
    cd.dof.use_dof = not A.quick
    cd.dof.focus_distance = 3.0
    cd.dof.aperture_fstop = 2.8
    scene.camera = ob


def render_setup():
    r = scene.render
    r.resolution_percentage = A.pct
    r.filepath = os.path.abspath(A.out)
    vs = scene.view_settings
    if A.quick:
        r.engine = "BLENDER_WORKBENCH"
        scene.display.shading.light = "FLAT"
        scene.display.shading.color_type = "MATERIAL"
        vs.view_transform = "Standard"
        return
    vs.view_transform = "AgX"
    vs.look = "AgX - Medium High Contrast"
    vs.exposure = A.exposure
    r.engine = "CYCLES"
    prefs = bpy.context.preferences.addons["cycles"].preferences
    for kind in ("OPTIX", "CUDA", "HIP", "METAL", "ONEAPI"):
        try:
            prefs.compute_device_type = kind
            prefs.get_devices()
            gpus = [d for d in prefs.devices if d.type == kind]
            if gpus:
                for d in prefs.devices:
                    d.use = d.type == kind
                scene.cycles.device = "GPU"
                print("RENDER DEVICE", kind, [d.name for d in gpus])
                break
        except TypeError:
            continue
    else:
        print("RENDER DEVICE CPU (no GPU backend found)")
    c = scene.cycles
    c.samples = A.samples
    c.use_adaptive_sampling = True
    c.adaptive_threshold = 0.02
    c.use_denoising = True
    c.max_bounces = 8
    c.diffuse_bounces = 4
    c.glossy_bounces = 4
    c.transparent_max_bounces = 12
    c.caustics_reflective = c.caustics_refractive = False
    c.sample_clamp_indirect = 8


# ------------------------------------------------------------------ build
materials()
MT.sky_world(strength=0.5, light_frac=1.0)       # dim world = interior fill only
MT.sky_dome(strength=1.5)                         # bright sky seen through glass
shell()
# furniture() / props() / exterior() go here
lights()
camera()
render_setup()
if A.save:
    try:
        bpy.ops.file.pack_all()
    except Exception as e:
        print("pack failed", e)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(A.save))
if not A.norender:
    bpy.ops.render.render(write_still=True)
    print("RENDERED", A.out)
