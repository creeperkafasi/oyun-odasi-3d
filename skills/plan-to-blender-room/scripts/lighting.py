"""Light objects (spots, areas, points) and world."""
import math
import bpy
from mathutils import Vector
import lib

WARM = (1.0, 0.68, 0.42)
WARM2 = (1.0, 0.76, 0.52)
BLUE = (0.25, 0.42, 1.0)


def _light(name, kind, loc, energy, color, coll="Lights"):
    ld = bpy.data.lights.new(name, kind)
    ld.energy = energy
    ld.color = color
    ob = bpy.data.objects.new(name, ld)
    ob.location = loc
    lib.coll(coll).objects.link(ob)
    return ob


def spot(name, loc, direction, energy=30, size=45, blend=0.6, color=WARM, radius=0.015):
    ob = _light(name, "SPOT", loc, energy, color)
    ob.data.spot_size = math.radians(size)
    ob.data.spot_blend = blend
    ob.data.shadow_soft_size = radius
    lib.aim(ob, direction)
    return ob


def area(name, loc, direction, sx, sy, energy, color=WARM, spread=180):
    ob = _light(name, "AREA", loc, energy, color)
    ob.data.shape = "RECTANGLE"
    ob.data.size = sx
    ob.data.size_y = sy
    ob.data.spread = math.radians(spread)
    lib.aim(ob, direction)
    return ob


def point(name, loc, energy, color=WARM, radius=0.05):
    ob = _light(name, "POINT", loc, energy, color)
    ob.data.shadow_soft_size = radius
    return ob


def visible_to_camera(ob, flag):
    ob.visible_camera = flag
