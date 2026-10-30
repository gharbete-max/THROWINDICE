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
    for n, sg in (('L', 1), ('R', -1)):                               # tuck the legs up
        rot(rig, f'leg.{n}', -0.2 - 0.9 * hit, 0, sg * 0.06); rot(rig, f'shin.{n}', 0.35 + 1.0 * hit, 0, 0); rot(rig, f'foot.{n}', 0.45 + 0.4 * hit, 0, 0)
    rot(rig, 'tail', 0.6 * hit, 0, -0.4 * hit)                        # tail whips up

# ---------------- choreography: a sequence of different moves, ~140 bpm ----------------
# Every move returns offsets from the neutral stance that are zero at its start and end, so moves chain and the
# whole sequence loops seamlessly. Feet stay planted unless a move lifts them.
NEUTRAL = dict(yaw=0, lift=0, dx=0, dip=0, lean=0, twist=0, hx=0, hy=0, hz=0, aL=0, aR=0, fL=0, fR=0, bL=0.15, bR=0.15, stepL=0, stepR=0, glow=1.6)
S = math.sin; PI = math.pi
def frac(x): return x - math.floor(x)
def env(u, k=0.18): return ease(u / k) * ease((1 - u) / k)          # fade a move in and out at its edges

def mv_shuffle(u):      # quick side shuffle, two steps each way, paw on the weight side waves, head bobs on every beat
    sw = S(4 * PI * u); e = env(u, 0.08)
    return dict(dx=0.07 * sw * e, dip=0.04 * (1 - math.cos(8 * PI * u)) / 2, lean=0.06 * sw * e, twist=0.15 * sw * e,
                stepL=max(0, -sw) ** 2 * e, stepR=max(0, sw) ** 2 * e, aL=(0.55 * max(0, sw) ** 1.3 - 0.1 * max(0, -sw)) * e,
                aR=(0.55 * max(0, -sw) ** 1.3 - 0.1 * max(0, sw)) * e, hx=0.08 * S(8 * PI * u), hz=-0.15 * sw * e, fL=0.2 * sw * e, fR=-0.2 * sw * e)

def mv_roof(u):         # "raise the roof": both arms shoot up and pump four times, knees bounce, head nods
    e = env(u, 0.15); pump = S(8 * PI * u)
    return dict(aL=e * (0.4 + 0.1 * pump), aR=e * (0.4 + 0.1 * pump), bL=e * (0.42 + 0.12 * pump), bR=e * (0.42 + 0.12 * pump),  # V arms, forearms up and out
                dip=e * 0.06 * (1 - math.cos(8 * PI * u)) / 2, dx=0.05 * S(4 * PI * u) * e, hx=e * 0.16 * pump, hz=0.12 * S(4 * PI * u) * e)

def mv_spin_point(u):   # fast 360 spin with arms out, then a disco point: one arm up high, the other down, hip pop
    out = {}
    if u < 0.5:
        v = u / 0.5; out['yaw'] = 2 * PI * ease(v); a = S(PI * v); out.update(aL=0.1 * a, aR=0.1 * a, dip=0.05 * a, lift=0.05 * a)
    else:
        v = S(PI * (u - 0.5) / 0.5)
        out.update(aL=0.75 * v, aR=-0.45 * v, bL=-0.15 * v, fL=-0.1 * v, dx=0.06 * v, lean=0.12 * v, hz=0.15 * v, hy=-0.12 * v, twist=-0.2 * v, stepR=0.5 * v)
    return out

def mv_hops(u):         # two quick hops: crouch, spring up with legs tucked and arms flapping, land
    h = frac(2 * u); air = S(PI * ease((h - 0.2) / 0.6)) if 0.2 < h < 0.8 else 0.0
    crouch = (1 - ease(h / 0.2)) * 0.6 if h < 0.2 else ((ease((h - 0.8) / 0.2)) * 0.6 if h > 0.8 else 0.0)
    e = env(u, 0.1)
    return dict(lift=0.24 * air, dip=0.08 * crouch * e, stepL=0.7 * air, stepR=0.7 * air, aL=0.6 * air - 0.15 * crouch * e,
                aR=0.6 * air - 0.15 * crouch * e, hx=-0.12 * air + 0.1 * crouch * e, twist=0.2 * S(2 * PI * u) * e)

def mv_wiggle(u):       # butt wiggle: hips swing fast left-right while the head stays steady, arms bent like a boxer
    e = env(u, 0.15); w = S(8 * PI * u)
    return dict(dx=0.05 * w * e, twist=0.35 * w * e, lean=0.1 * w * e, dip=0.05 * e, hy=-0.2 * w * e,
                aL=-0.25 * e, aR=-0.25 * e, fL=-0.6 * e, fR=-0.6 * e, bL=1.1 * e, bR=1.1 * e)

def choreo(t, moves):
    """moves: [(fn, beats)]; returns the pose dict at loop time t in [0,1)."""
    total = sum(b for _, b in moves); x = t * total; P = dict(NEUTRAL)
    for fn, b in moves:
        if x < b or fn is moves[-1][0]:
            for k, v in fn(min(1, x / b)).items(): P[k] = P.get(k, 0) + v
            return P
        x -= b
    return P

def apply_pose(rig, parts, P, base_yaw=-0.3, glow_mat=None):
    move(rig, 'root', 0, 0, P['lift']); rot(rig, 'root', 0, 0, base_yaw + P['yaw'])
    move(rig, 'hips', P['dx'], 0, -P['dip']); rot(rig, 'hips', 0, 0.6 * P['lean'], 0)
    rot(rig, 'spine', 0.04, -P['lean'], P['twist'])
    rot(rig, 'head', P['hx'], P['hy'], 0.1 + P['hz'])                           # 0.1 = a curious tilt
    arms(rig, P['aL'], P['aR'], P['fL'], P['fR'], P['bL'], P['bR'])
    L = 0.56; sway = math.asin(max(-0.9, min(0.9, P['dx'] / L))); knee = math.acos(max(0.6, (L - P['dip']) / L))
    leg_bend(rig, 'L', knee + 0.55 * P['stepL'], sway); leg_bend(rig, 'R', knee + 0.55 * P['stepR'], sway)
    m = parts.get('orb_m')
    if m: m.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value = P['glow'] + 6 * max(P['lift'] * 4, P['aL'] * 0.6 if P['aL'] > 1 else 0)

ALIEN_DANCE = [(mv_shuffle, 2), (mv_roof, 1.5), (mv_spin_point, 1.5), (mv_hops, 1.5)]
PUG_DANCE = [(mv_roof, 1.5), (mv_wiggle, 2), (mv_hops, 1.5), (mv_spin_point, 1.5)]

_alien_special, _pug_special = alien_pose, pug_pose
def alien_pose(rig, parts, t, special=False):
    if special: return _alien_special(rig, parts, t, True)
    apply_pose(rig, parts, choreo(t, ALIEN_DANCE))

def pug_pose(rig, parts, t, special=False):
    if special: return _pug_special(rig, parts, t, True)
    apply_pose(rig, parts, choreo(t, PUG_DANCE), base_yaw=-0.25)

# ---------------- tap specials: spin jump, backflip, superstar pose (each starts and ends neutral) ----------------
def sp_spin(t):
    air = bump(t, 0.18, 0.8); cr = 0.6 * bump(t, 0, 0.22) + bump(t, 0.75, 0.97)
    return dict(lift=0.38 * air, yaw=2 * PI * ease((t - 0.18) / 0.6), dip=0.1 * cr, aL=0.25 * air - 0.2 * cr, aR=0.25 * air - 0.2 * cr,
                stepL=0.6 * air, stepR=0.6 * air, hx=0.12 * cr - 0.1 * air, glow=9 * air)

def sp_flip(t):
    air = bump(t, 0.16, 0.82); cr = 0.7 * bump(t, 0, 0.2) + bump(t, 0.78, 0.98); tuck = bump(t, 0.25, 0.72)
    return dict(lift=0.6 * air, flip=-2 * PI * ease((t - 0.2) / 0.56), dip=0.12 * cr, aL=0.5 * bump(t, 0.1, 0.3) - 0.35 * tuck, aR=0.5 * bump(t, 0.1, 0.3) - 0.35 * tuck,
                fL=-0.6 * tuck, fR=-0.6 * tuck, bL=0.9 * tuck, bR=0.9 * tuck, stepL=1.0 * tuck, stepR=1.0 * tuck, hx=0.25 * tuck, glow=9 * air)

def sp_pose(t):
    v = ease(t / 0.12) * ease((1 - t) / 0.22); beat = 0.5 + 0.5 * S(2 * PI * 3 * t)  # snap in, hold with a little hip bounce, release
    return dict(aL=0.8 * v, bL=-0.15 * v, aR=-0.55 * v, fR=-0.55 * v, bR=1.25 * v, dx=0.07 * v, lean=0.15 * v, twist=-0.3 * v,
                hz=0.18 * v, hy=-0.12 * v, stepR=0.35 * v, yaw=0.35 * v, dip=0.03 * v * beat, glow=6 * v)

SPECIALS = {'special': sp_spin, 'flip': sp_flip, 'pose': sp_pose}

def apply_pose2(rig, parts, P, base_yaw):
    """apply_pose plus an optional flip (rotation about the character's own side axis, pivoting at mid-body)."""
    apply_pose(rig, parts, P, base_yaw)
    a = P.get('flip', 0.0)
    if a:
        c = 1.0; yaw = base_yaw + P['yaw']; ty, tz = c * math.sin(a), c * (1 - math.cos(a))
        rot(rig, 'root', a, 0, yaw); move(rig, 'root', -math.sin(yaw) * ty, math.cos(yaw) * ty, P['lift'] + tz)

def alien_pose(rig, parts, t, special=False):
    if special: P = dict(NEUTRAL); [P.__setitem__(k, P.get(k, 0) + v) for k, v in SPECIALS[special if isinstance(special, str) else 'special'](t).items()]
    else: P = choreo(t, ALIEN_DANCE)
    apply_pose2(rig, parts, P, -0.3)

def pug_pose(rig, parts, t, special=False):
    if special: P = dict(NEUTRAL); [P.__setitem__(k, P.get(k, 0) + v) for k, v in SPECIALS[special if isinstance(special, str) else 'special'](t).items()]
    else: P = choreo(t, PUG_DANCE)
    apply_pose2(rig, parts, P, -0.25)

_DANCE = None
def dancer_pose(rig, parts, t, special=False):
    """Frame-for-frame dance retargeted from the reference video (see retarget.py)."""
    global _DANCE
    import numpy as np, bpy
    if _DANCE is None:
        d = np.load('/home/claude/bl/dance.npz'); _DANCE = {k: d[k] for k in d.files}
        _DANCE['msL'] = np.median(_DANCE['sL']); _DANCE['msR'] = np.median(_DANCE['sR']); _DANCE['mhip'] = np.median(_DANCE['hipt'])
    D = _DANCE; n = int(D['n']); i = int(round(t * n)) % n; g = lambda k: float(D[k][i])
    for pb in rig.pose.bones: pb.location = (0, 0, 0)
    rot(rig, 'root', 0, 0, -0.22 + 0.85 * g('yaw'))
    rot(rig, 'hips', 0, -0.6 * (g('hipt') - D['mhip']), 0)
    rot(rig, 'spine', 0, 0.8 * g('lean'), 0)
    rot(rig, 'head', 0, 0.8 * g('tilt'), g('look'))
    arms(rig, g('aL'), g('aR'), 0, 0, g('bL'), g('bR'))
    for n_, s_, k_ in (('L', 'sL', 'kL'), ('R', 'sR', 'kR')):
        a = g(k_); side = -(g(s_) - D['m' + s_])
        rot(rig, f'leg.{n_}', -a, side, 0); rot(rig, f'shin.{n_}', 2 * a, 0, 0); rot(rig, f'foot.{n_}', -a, 0, 0)
    bpy.context.view_layer.update()                      # keep the lowest foot on the floor
    low = min(min((rig.matrix_world @ rig.pose.bones[f'foot.{x}'].head).z, (rig.matrix_world @ rig.pose.bones[f'foot.{x}'].tail).z) for x in 'LR')
    move(rig, 'root', 0, 0, 0.05 - low)
