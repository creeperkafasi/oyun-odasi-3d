"""Render a close-up of an object from the main build (adds a camera aimed at target)."""
import bpy, sys, math
from mathutils import Vector
argv = sys.argv[sys.argv.index("--") + 1:]
tgt = Vector([float(x) for x in argv[0].split(",")]); cam = Vector([float(x) for x in argv[1].split(",")])
out = argv[2]; lens = float(argv[3]) if len(argv) > 3 else 35
sc = bpy.context.scene
cd = bpy.data.cameras.new("Close"); cd.lens = lens
ob = bpy.data.objects.new("Close", cd); sc.collection.objects.link(ob)
ob.location = cam
ob.rotation_mode = "QUATERNION"; ob.rotation_quaternion = (tgt - cam).to_track_quat("-Z", "Y")
sc.camera = ob
sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 800, 600, 100
sc.cycles.samples = 64
sc.render.filepath = out
bpy.ops.render.render(write_still=True)
