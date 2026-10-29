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
    aL, aR = 0.42 * s1, -0.42 * s1  # relative to the arms-out rest pose
    headx, heady, headz = -0.14 * b + 0.04, 0.12 * s1, 0.1 + 0.1 * math.sin(p + 0.5)  # curious head tilt
    if special:
        air = bump(t, 0.12, 0.62); cr = bump(t, 0, 0.18) + 0.8 * bump(t, 0.56, 0.72); tada = bump(t, 0.6, 1)
        lift = 0.32 * air; yaw += 2 * math.pi * ease((t - 0.12) / 0.5); crouch += 0.09 * cr
        sp = max(air, tada); tgt = -0.1 if air > tada else 0.6
        aL = aL * (1 - sp) + tgt * sp; aR = aR * (1 - sp) + tgt * sp; headx += 0.22 * tada
    move(rig, 'root', 0, 0, lift); rot(rig, 'root', 0, 0, yaw)
    move(rig, 'hips', 0, 0, -crouch); rot(rig, 'hips', 0, lean, 0)
    rot(rig, 'spine', 0.05 * b, -lean * 0.5, 0.08 * s1)
    rot(rig, 'head', headx, heady, headz)
    arms(rig, aL, aR, 0.15 * s1, -0.15 * s1, 0.2, 0.2)
    for n, sg in (('L', 1), ('R', -1)):  # keep feet planted against the crouch
        rot(rig, f'leg.{n}', -0.25 * crouch * 4, sg * 0.04 * b, 0); rot(rig, f'shin.{n}', 0.5 * crouch * 4, 0, 0); rot(rig, f'foot.{n}', -0.25 * crouch * 4, 0, 0)
    if parts.get('tail'): pass

def leg_bend(rig, n, a, sway=0.0):
    """Bend a leg at hip/knee/ankle by a (knee forward) while compensating hip sway so the foot stays put."""
    rot(rig, f'leg.{n}', -a, sway, 0); rot(rig, f'shin.{n}', 2 * a, 0, 0); rot(rig, f'foot.{n}', -a, 0, 0)

def alien_pose(rig, parts, t, special=False):
    """Groove with planted feet: hips sway over the standing foot, knees dip through the weight change,
    the free foot lifts, the paw on the weight side waves up and the head follows a beat late."""
    p = 2 * math.pi * t; s1 = math.sin(p)
    sw = math.copysign(abs(s1) ** 0.8, s1)                # weight shift (+ = over the left foot)
    dx = 0.065 * sw; dip = 0.035 * (1 + math.cos(2 * p)) / 2 # body dips as it passes the middle
    stepL, stepR = max(0, -s1) ** 2, max(0, s1) ** 2       # the unweighted foot lifts
    lift, yaw, glow = 0.0, 0.0, 1.6
    aL = 0.06 + 0.5 * max(0, s1) ** 1.4 - 0.1 * max(0, -s1); aR = 0.06 + 0.5 * max(0, -s1) ** 1.4 - 0.1 * max(0, s1)
    hx, hy, hz = 0.05 * math.sin(2 * p + 0.6), 0.16 * math.sin(p - 0.4), 0.1 - 0.12 * math.sin(p - 0.5)  # curious head tilt
    if special:  # warp jump: crouch, leap with a full spin and arms up, antennae flare, land
        air = bump(t, 0.18, 0.8); cr = 0.6 * bump(t, 0, 0.25) + bump(t, 0.72, 0.95)
        lift = 0.35 * air; yaw = 2 * math.pi * ease((t - 0.18) / 0.6); dip += 0.1 * cr
        aL = aL + (0.6 - aL) * air; aR = aR + (0.6 - aR) * air; glow = 1.6 + 10 * air; stepL = stepR = 0.6 * air
    move(rig, 'root', 0, 0, lift); rot(rig, 'root', 0, 0, -0.3 + yaw)
    move(rig, 'hips', dx, 0, -dip); rot(rig, 'hips', 0, 0.05 * sw, 0)
    rot(rig, 'spine', 0.04, -0.08 * sw, 0.1 * math.sin(p - 0.3))   # torso counter-tilt and a little twist
    rot(rig, 'head', hx, hy, hz)
    arms(rig, aL, aR, 0.12 * s1, -0.12 * s1, 0.15, 0.15)
    L = 0.56; sway = math.asin(max(-0.9, min(0.9, dx / L)))
    knee = lambda d: math.acos(max(0.6, (L - d) / L))
    leg_bend(rig, 'L', knee(dip) + 0.55 * stepL, sway - 0.05 * sw); leg_bend(rig, 'R', knee(dip) + 0.55 * stepR, sway - 0.05 * sw)
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

def kitten_scared(rig, parts, t, special=False):
    """Slider smacked into the end: eyes squeeze shut, head ducks, legs tuck, a quick tremble, then wide-eyed relief.
    t=0 matches kitten_hang(t=0) so the clip can be swapped in seamlessly."""
    kitten_hang(rig, parts, 0)
    hit = bump(t, 0.0, 0.75) ** 0.6                                  # fast in, slower out
    shut = 0.04 < t < 0.68
    for o in parts.get('lids', []): o.hide_render = not shut
    shake = 0.05 * math.sin(2 * math.pi * 7 * t) * bump(t, 0.05, 0.6)
    PZ = PIVOT_Z; th = shake
    rot(rig, 'root', 0, th, 0); move(rig, 'root', -PZ * math.sin(th), 0, PZ * (1 - math.cos(th)))
    rot(rig, 'head', -0.1 + 0.35 * hit, 0, 0.08 * hit)              # duck the head
    rig.pose.bones['spine'].scale = (1, 1 - 0.06 * hit, 1)            # cringe
    for n, sg in (('L', 1), ('R', -1)):                               # tuck the legs up
        rot(rig, f'leg.{n}', -0.2 - 0.9 * hit, 0, sg * 0.06); rot(rig, f'shin.{n}', 0.35 + 1.0 * hit, 0, 0); rot(rig, f'foot.{n}', 0.45 + 0.4 * hit, 0, 0)
    rot(rig, 'tail', 0.6 * hit, 0, -0.4 * hit)                        # tail whips up
