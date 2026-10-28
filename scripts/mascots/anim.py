"""Pose helpers + per-character dance curves. t in [0,1) loops; special=True plays the click move."""
import math, bpy
from mathutils import Euler, Vector, Matrix

def ease(x): x = min(1, max(0, x)); return x * x * (3 - 2 * x)
def bump(t, a, b): return math.sin(math.pi * ease((t - a) / (b - a)))

def rot(rig, name, rx=0, ry=0, rz=0):
    """Rotate a pose bone by world-axis angles (in its rest frame)."""
    pb = rig.pose.bones[name]; pb.rotation_mode = 'QUATERNION'
    R = pb.bone.matrix_local.to_3x3(); W = Euler((rx, ry, rz), 'XYZ').to_matrix()
    pb.rotation_quaternion = (R.inverted() @ W @ R).to_quaternion()

def move(rig, name, x=0, y=0, z=0):
    pb = rig.pose.bones[name]; pb.location = pb.bone.matrix_local.to_3x3().inverted() @ Vector((x, y, z))

def arms(rig, L, R, fwdL=0, fwdR=0, bendL=0, bendR=0):
    """L/R = raise angle (radians) of each arm; positive lifts the arm up and out."""
    rot(rig, 'arm.L', fwdL, -L, 0); rot(rig, 'arm.R', fwdR, R, 0)
    rot(rig, 'fore.L', 0, -bendL, 0); rot(rig, 'fore.R', 0, bendR, 0)

def pug_pose(rig, parts, t, special=False):
    p = 2 * math.pi * t; s1 = math.sin(p); b = abs(s1)
    yaw, lift, lean, crouch = -0.25 + 0.3 * s1, 0.0, 0.06 * s1, 0.05 * b
    aL, aR = 0.75 + 0.45 * s1, 0.75 - 0.45 * s1
    headx, heady, headz = -0.14 * b + 0.04, 0.12 * s1, 0.12 * math.sin(p + 0.5)
    if special:
        air = bump(t, 0.12, 0.62); cr = bump(t, 0, 0.18) + 0.8 * bump(t, 0.56, 0.72); tada = bump(t, 0.6, 1)
        lift = 0.32 * air; yaw += 2 * math.pi * ease((t - 0.12) / 0.5); crouch += 0.09 * cr
        sp = max(air, tada); tgt = 0.25 if air > tada else 2.0
        aL = aL * (1 - sp) + tgt * sp; aR = aR * (1 - sp) + tgt * sp; headx += 0.22 * tada
    move(rig, 'root', 0, 0, lift); rot(rig, 'root', 0, 0, yaw)
    move(rig, 'hips', 0, 0, -crouch); rot(rig, 'hips', 0, lean, 0)
    rot(rig, 'spine', 0.05 * b, -lean * 0.5, 0.08 * s1)
    rot(rig, 'head', headx, heady, headz)
    arms(rig, aL, aR, 0.3 * s1, -0.3 * s1, 0.35, 0.35)
    for n, sg in (('L', 1), ('R', -1)):  # keep feet planted against the crouch
        rot(rig, f'leg.{n}', -0.25 * crouch * 4, sg * 0.04 * b, 0); rot(rig, f'shin.{n}', 0.5 * crouch * 4, 0, 0); rot(rig, f'foot.{n}', -0.25 * crouch * 4, 0, 0)
    if parts.get('tail'): pass

def alien_pose(rig, parts, t, special=False):
    p = 2 * math.pi * t; s1 = math.sin(p)
    x, lift, yaw, lean, glow = 0.08 * s1, 0.0, -0.3 + 0.15 * s1, -0.08 * s1, 1.6
    aL = aR = 1.15 + 0.25 * math.sin(2 * p); stepL, stepR = max(0, s1), max(0, -s1); crouch = 0.03 * (1 - math.cos(2 * p)) / 2
    hx, hy, hz = 0.06 * math.sin(2 * p), 0.15 * s1, 0.15 * math.sin(p - 0.6)
    if special:  # warp jump: crouch, leap with a full spin and arms up, antennae flare, land
        air = bump(t, 0.18, 0.8); cr = 0.6 * bump(t, 0, 0.25) + bump(t, 0.72, 0.95)
        lift = 0.35 * air; yaw += 2 * math.pi * ease((t - 0.18) / 0.6); crouch += 0.1 * cr
        aL = aR = aL + (2.3 - aL) * air; glow = 1.6 + 10 * air; stepL = stepR = 0.5 * air
    move(rig, 'root', x, 0, lift); rot(rig, 'root', 0, 0, yaw)
    move(rig, 'hips', 0, 0, -crouch); rot(rig, 'hips', 0, lean, 0); rot(rig, 'spine', 0.04, -lean * 0.6, 0.06 * s1)
    rot(rig, 'head', hx, hy, hz)
    arms(rig, aL, aR, 0.25 * s1, -0.25 * s1, 0.25, 0.25)
    for n, st in (('L', stepL), ('R', stepR)):
        rot(rig, f'leg.{n}', -0.45 * st - 3 * crouch, 0, 0); rot(rig, f'shin.{n}', 0.7 * st + 6 * crouch, 0, 0); rot(rig, f'foot.{n}', -0.25 * st - 3 * crouch, 0, 0)
    m = parts.get('orb_m')
    if m: m.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value = glow

def kitten_hang(rig, parts, t, special=False):
    p = 2 * math.pi * t; s1 = math.sin(p)
    arms(rig, 0.03 * s1, -0.03 * s1, 0, 0, 0, 0)
    rot(rig, 'spine', 0.05, 0.04 * s1, 0); rot(rig, 'hips', 0.08, 0.06 * s1, 0.05 * s1)
    rot(rig, 'head', -0.12 + 0.05 * math.sin(2 * p), 0.1 * s1, 0.1 * math.sin(p + 0.8))
    rot(rig, 'leg.L', -0.35 * s1 - 0.15, 0, 0.05); rot(rig, 'leg.R', 0.35 * s1 - 0.15, 0, -0.05)
    rot(rig, 'shin.L', 0.35 + 0.25 * max(0, s1), 0, 0); rot(rig, 'shin.R', 0.35 + 0.25 * max(0, -s1), 0, 0)
    rot(rig, 'foot.L', 0.5, 0, 0); rot(rig, 'foot.R', 0.5, 0, 0)
