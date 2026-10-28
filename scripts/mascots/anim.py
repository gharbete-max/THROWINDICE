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
        sp = max(air, tada); tgt = 0.2 if air > tada else 1.3
        aL = aL * (1 - sp) + tgt * sp; aR = aR * (1 - sp) + tgt * sp; headx += 0.22 * tada
    move(rig, 'root', 0, 0, lift); rot(rig, 'root', 0, 0, yaw)
    move(rig, 'hips', 0, 0, -crouch); rot(rig, 'hips', 0, lean, 0)
    rot(rig, 'spine', 0.05 * b, -lean * 0.5, 0.08 * s1)
    rot(rig, 'head', headx, heady, headz)
    arms(rig, aL, aR, 0.15 * s1, -0.15 * s1, 0.2, 0.2)
    for n, sg in (('L', 1), ('R', -1)):  # keep feet planted against the crouch
        rot(rig, f'leg.{n}', -0.25 * crouch * 4, sg * 0.04 * b, 0); rot(rig, f'shin.{n}', 0.5 * crouch * 4, 0, 0); rot(rig, f'foot.{n}', -0.25 * crouch * 4, 0, 0)
    if parts.get('tail'): pass

def alien_pose(rig, parts, t, special=False):
    p = 2 * math.pi * t; s1 = math.sin(p)
    x, lift, yaw, lean, glow = 0.08 * s1, 0.0, -0.3 + 0.15 * s1, -0.08 * s1, 1.6
    aL = aR = 0.85 + 0.22 * math.sin(2 * p); stepL, stepR = max(0, s1), max(0, -s1); crouch = 0.03 * (1 - math.cos(2 * p)) / 2
    hx, hy, hz = 0.06 * math.sin(2 * p), 0.15 * s1, 0.15 * math.sin(p - 0.6)
    if special:  # warp jump: crouch, leap with a full spin and arms up, antennae flare, land
        air = bump(t, 0.18, 0.8); cr = 0.6 * bump(t, 0, 0.25) + bump(t, 0.72, 0.95)
        lift = 0.35 * air; yaw += 2 * math.pi * ease((t - 0.18) / 0.6); crouch += 0.1 * cr
        aL = aR = aL + (1.35 - aL) * air; glow = 1.6 + 10 * air; stepL = stepR = 0.5 * air
    move(rig, 'root', x, 0, lift); rot(rig, 'root', 0, 0, yaw)
    move(rig, 'hips', 0, 0, -crouch); rot(rig, 'hips', 0, lean, 0); rot(rig, 'spine', 0.04, -lean * 0.6, 0.06 * s1)
    rot(rig, 'head', hx, hy, hz)
    arms(rig, aL, aR, 0.12 * s1, -0.12 * s1, 0.15, 0.15)
    for n, st in (('L', stepL), ('R', stepR)):
        rot(rig, f'leg.{n}', -0.45 * st - 3 * crouch, 0, 0); rot(rig, f'shin.{n}', 0.7 * st + 6 * crouch, 0, 0); rot(rig, f'foot.{n}', -0.25 * st - 3 * crouch, 0, 0)
    m = parts.get('orb_m')
    if m: m.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value = glow

PIVOT_Z = 2.34  # kitten paws: everything swings around this grip point

def kitten_hang(rig, parts, t, special=False):
    """Wobbly hang: pendulum sway from the paws, with the body, legs, tail and head trailing behind (follow-through)."""
    p = 2 * math.pi * t; w = lambda lag, k=1: math.sin(k * p - lag)
    th = 0.13 * w(0)                                   # main swing
    rot(rig, 'root', 0, th, 0); move(rig, 'root', -PIVOT_Z * math.sin(th), 0, PIVOT_Z * (1 - math.cos(th)))
    arms(rig, 0, 0, 0, 0, 0, 0)
    rot(rig, 'spine', 0.05 + 0.03 * w(0.2, 2), 0, 0.04 * w(0.8))  # no sideways bend here: it would drag the paws off the ball
    rot(rig, 'hips', 0.08 + 0.05 * w(0.5, 2), 0, 0.06 * w(1.2))  # belly jiggle
    rig.pose.bones['spine'].scale = (1, 1 + 0.035 * w(0.3, 2), 1)
    rot(rig, 'head', -0.1 + 0.07 * w(0.9, 2), 0.1 * w(-0.4), 0.14 * w(-0.6))
    for n, ph, sg in (('L', 0.0, 1), ('R', math.pi, -1)):  # bicycle kicks + dangling lag
        k = math.sin(p * 2 + ph)
        rot(rig, f'leg.{n}', -0.2 - 0.4 * k, -0.3 * w(1.4), sg * 0.06)  # legs trail the swing
        rot(rig, f'shin.{n}', 0.35 + 0.35 * max(0, k), 0, 0); rot(rig, f'foot.{n}', 0.45 + 0.3 * math.sin(p * 2 + ph - 0.8), 0, 0)
    rot(rig, 'tail', 0.15 * w(1.6, 2), 0.25 * w(2.0), 0.55 * w(2.2))
