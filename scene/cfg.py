"""Shared dimensions (metres). Room = bottom-left room of the ground-floor plan."""
W, D, H = 5.24, 3.63, 2.65      # interior length (x, west→east), width (y, south→north), height
T = 0.20                          # wall thickness
WIN_Y = (1.20, 2.71)              # west wall window (plan: 1.45–2.71, widened toward the render)
WIN_Z = (1.10, 2.35)
SLIDE_X = (0.53, 3.01)            # south wall sliding door (plan)
SLIDE_Z = (0.0, 2.45)
DOOR_X = (0.726, 1.50)            # north wall door (plan)
DOOR_Z = (0.0, 2.12)
DESK = dict(x0=1.75, x1=3.62, depth=0.60, top=0.76)
VR = dict(x=1.05, y=1.95, r=0.70)
RING = dict(x=1.25, y=1.90, R=0.92)
RUG_ROUND = dict(x=2.55, y=1.10, r=0.90)
RUG_RECT = (1.25, 2.30, 3.25, 3.57)
CAM = dict(loc=(4.731, 1.744, 1.220), lens=15.4, shift_x=0.191, shift_y=-0.115, yaw=8.73)
