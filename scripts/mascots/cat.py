import sys, math; sys.path.insert(0, '/home/claude/bl')
import bpy, numpy as np
from mathutils import Vector
from lib import *

def EL(co, ax, ay, az, stiff=2.0, neg=False):
    m = max(ax, ay, az); return E(co, 2 * m, (ax / m, ay / m, az / m), stiff, neg)

def oval(nt, sx, cx, cz, rx, rz, y_front=-0.1):
    """Soft oval mask on the front of the body (object space x/z), only where y < y_front."""
    dx = nt.nodes.new('ShaderNodeMath'); dx.operation = 'MULTIPLY_ADD'; nt.links.new(sx.outputs['X'], dx.inputs[0]); dx.inputs[1].default_value = 1 / rx; dx.inputs[2].default_value = -cx / rx
    dz = nt.nodes.new('ShaderNodeMath'); dz.operation = 'MULTIPLY_ADD'; nt.links.new(sx.outputs['Z'], dz.inputs[0]); dz.inputs[1].default_value = 1 / rz; dz.inputs[2].default_value = -cz / rz
    cm = nt.nodes.new('ShaderNodeCombineXYZ'); nt.links.new(dx.outputs[0], cm.inputs[0]); nt.links.new(dz.outputs[0], cm.inputs[1])
    v = nt.nodes.new('ShaderNodeVectorMath'); v.operation = 'LENGTH'; nt.links.new(cm.outputs[0], v.inputs[0])
    return mult(nt, smooth_mask(nt, v.outputs['Value'], 1.0, 0.55), smooth_mask(nt, sx.outputs['Y'], y_front, y_front - 0.2))

def maxs(nt, a, b):
    m = nt.nodes.new('ShaderNodeMath'); m.operation = 'MAXIMUM'; nt.links.new(a, m.inputs[0]); nt.links.new(b, m.inputs[1]); return m.outputs[0]

def build(kind='alien'):
    reset()
    alien = kind == 'alien'
    if alien:
        c1, c2 = (0.07, 0.62, 0.22), (0.55, 0.92, 0.66)  # mint body, pale belly / muzzle
        mask = lambda nt, sx: maxs(nt, oval(nt, sx, 0, 0.9, 0.2, 0.24), oval(nt, sx, 0, 1.56, 0.2, 0.1, -0.3))
        flen, iris = 0.03, (0.06, 0.02, 0.09)
    else:
        c1, c2 = (0.97, 0.96, 0.95), (0.17, 0.16, 0.19)  # white kitten, grey hood
        def mask(nt, sx):
            top = smooth_mask(nt, sx.outputs['Z'], 1.84, 1.97)
            ax = nt.nodes.new('ShaderNodeMath'); ax.operation = 'ABSOLUTE'; nt.links.new(sx.outputs['X'], ax.inputs[0])
            blaze = mult(nt, mult(nt, smooth_mask(nt, ax.outputs[0], 0.13, 0.05), smooth_mask(nt, sx.outputs['Y'], -0.2, -0.38)), smooth_mask(nt, sx.outputs['Z'], 2.12, 1.98))
            inv = nt.nodes.new('ShaderNodeMath'); inv.operation = 'SUBTRACT'; inv.inputs[0].default_value = 1; nt.links.new(blaze, inv.inputs[1])
            return mult(nt, top, inv.outputs[0])
        flen, iris = 0.042, (0.1, 0.17, 0.3)
    skin_m = region_mix(principled('catSkin', c1, 0.6, sss=0.15, sss_radius=(1, 0.4, 0.3), sss_scale=0.04), c2, mask)
    pink = principled('pink', (0.95, 0.42, 0.52), 0.42, sss=0.4, sss_radius=(1, 0.3, 0.3), sss_scale=0.03)
    line_m = principled('mouth', (0.05, 0.02, 0.03), 0.7, spec=0.1)
    whisk_m = principled('whisker', (0.95, 0.95, 0.95), 0.35)

    els = [EL((0, 0.02, 0.95), 0.33, 0.3, 0.42), EL((0, -0.07, 1.1), 0.28, 0.24, 0.28), EL((0, -0.05, 0.8), 0.3, 0.26, 0.26), EL((0, 0.05, 0.72), 0.32, 0.28, 0.24),
           EL((0, -0.01, 1.33), 0.24, 0.22, 0.15)]
    for s in (-1, 1):
        els += [EL((s * 0.17, 0, 0.55), 0.14, 0.15, 0.19)] + chain((s * 0.18, -0.02, 0.42), (s * 0.19, -0.04, 0.15), 0.18, 0.16, 5)
        els += [EL((s * 0.19, -0.11, 0.07), 0.1, 0.15, 0.065)]
        el, wr, pw = ((0.45, 1.06), (0.6, 0.94), (0.64, 0.9)) if alien else ((0.64, 1.72), (0.82, 2.22), (0.86, 2.34))  # kitten: arms already up around the head, hanging
        els += chain((s * 0.25, -0.03, 1.22), (s * el[0], -0.05, el[1]), 0.17, 0.14, 6) + chain((s * el[0], -0.05, el[1]), (s * wr[0], -0.07, wr[1]), 0.14, 0.12, 6)
        els += [EL((s * pw[0], -0.09, pw[1]), 0.08, 0.09, 0.075)]
        els += [EL((s * 0.22, -0.25, 1.6), 0.22, 0.2, 0.18)]  # fluffy cheeks
        els += chain((s * 0.29, 0.0, 2.02), (s * 0.43, 0.02, 2.4), 0.3, 0.05, 8, 2.0, (1, 0.55, 1))  # cone ears
    els += [EL((0, 0, 1.75), 0.5, 0.44, 0.43), EL((0, -0.36, 1.6), 0.13, 0.09, 0.09), EL((0, -0.3, 1.5), 0.09, 0.07, 0.06)]
    body = blob('cat', els, smooth=3); body.data.materials.append(skin_m)
    bpy.context.view_layer.update(); S = lambda x, z: surf(body, x, z)

    er = 0.155; eye_m = eye_mat('catEye', iris, er)
    eyes = [uv_sphere(f'eye{s}', er, (s * 0.215, S(s * 0.215, 1.72) + er * 0.5, 1.72), (1, 0.85, 1.05)) for s in (-1, 1)]
    for e in eyes: e.data.materials.append(eye_m)
    nz = 1.615; ny = S(0, nz); nose = uv_sphere('nose', 0.042, (0, ny + 0.012, nz), (1.45, 0.6, 0.85)); nose.data.materials.append(pink)
    mouth = []
    for s in (-1, 1):
        mouth.append(tube(f'lip{s}', [(s * x, S(s * x, z) - 0.003, z) for x, z in ((0, 1.585), (0.025, 1.555), (0.06, 1.55), (0.085, 1.565))], [0.007, 0.007, 0.006, 0.004], line_m))
    mouth.append(tube('philtrum', [(0, S(0, 1.6) - 0.003, 1.6), (0, S(0, 1.585) - 0.003, 1.585)], [0.007, 0.007], line_m))
    whiskers = []
    for s in (-1, 1):
        for k, (dz, ang) in enumerate(((0.02, 0.15), (0.0, 0.0), (-0.02, -0.15))):
            x0, z0 = s * 0.13, 1.58 + dz; y0 = S(x0, z0) + 0.01
            whiskers.append(tube(f'wh{s}{k}', [(x0, y0, z0), (x0 + s * 0.2, y0 - 0.05, z0 + 0.03 + ang * 0.15), (x0 + s * 0.42, y0 + 0.02, z0 + ang * 0.6 - 0.02)], [0.006, 0.004, 0.001], whisk_m))
    inner = []
    for s in (-1, 1):
        off = 0.02 if alien else -0.006  # kitten fur is longer, so bring the pink inner ear forward
        a = Vector((s * 0.31, S(s * 0.31, 2.08) + off, 2.08)); b = Vector((s * 0.41, S(s * 0.41, 2.32) + off * 0.75, 2.32))
        inner.append(flap(f'inner{s}', a + Vector((0, -0.005, 0)), b, (0, -1, 0), 0.11, 0.15, 0.015, pink))
    tail = tube('tail', [(0, 0.28, 0.7), (0.15, 0.48, 0.66), (0.32, 0.55, 0.85), (0.35, 0.5, 1.15), (0.26, 0.45, 1.35)], [0.075, 0.07, 0.065, 0.06, 0.05], skin_m)
    liner_m = principled('liner', (0.03, 0.025, 0.03), 0.6, spec=0.2)
    liners = []
    for s in (-1, 1):  # dark rim where the eye meets the fur, like real cat eyes
        cx, cz = s * 0.215, 1.72; pts = []
        for k in range(25):
            a = 2 * math.pi * k / 24; x, z = cx + er * 1.0 * math.cos(a), cz + er * 1.05 * 1.0 * math.sin(a); pts.append((x, S(x, z) - 0.002, z))
        liners.append(tube(f'liner{s}', pts, [0.011] * 25, liner_m))
    beans = []
    if not alien:  # pink toe beans on the raised paws, facing the viewer
        bean_m = principled('bean', (0.95, 0.45, 0.55), 0.38, sss=0.5, sss_radius=(1, 0.35, 0.35), sss_scale=0.03, coat=0.3, coat_rough=0.2)
        for s in (-1, 1):
            px, pz = s * 0.85, 2.31; py = S(px, pz) - 0.004
            grp_ = [uv_sphere(f'pad{s}', 0.036, (px, py, pz), (1.25, 0.42, 1.0))]
            for k, dx in enumerate((-0.042, 0, 0.042)): grp_.append(uv_sphere(f'toe{s}{k}', 0.018, (px + dx * s, S(px + dx * s, pz + 0.06 - abs(dx) * 0.4) - 0.003, pz + 0.06 - abs(dx) * 0.4), (1, 0.45, 1.15)))
            for b in grp_: b.data.materials.append(bean_m)
            beans.append(grp_)
    extra = []
    if alien:
        orb_m = principled('orb', (1.0, 0.25, 0.75), 0.15, emit=(1.0, 0.12, 0.6), emit_str=1.6, coat=1.0, coat_rough=0.0)
        for s in (-1, 1):
            x0 = s * 0.13; z0 = 2.12; y0 = S(x0, z0) + 0.03
            extra.append(tube(f'ant{s}', [(x0, y0, z0 - 0.04), (x0 + s * 0.06, y0 - 0.02, z0 + 0.2), (x0 + s * 0.17, y0 - 0.06, z0 + 0.42)], [0.026, 0.021, 0.017], skin_m))
            o = uv_sphere(f'orb{s}', 0.075, (x0 + s * 0.175, y0 - 0.065, z0 + 0.48)); o.data.materials.append(orb_m); extra.append(o)

    if alien: hm = hair_mat('catHair', color=c1, rough=0.32, region=(c2, mask))
    else: hm = hair_mat('catHair', color=c1, rough=0.38, region=(c2, mask))
    eyec = [(s * 0.215, S(s * 0.215, 1.72), 1.72) for s in (-1, 1)]
    fur(body, hm, count=26000 if alien else 34000, length=flen, children=14 if alien else 20, droop=(0, 0, -0.55), radius=0.0028 if alien else 0.0022, clump=0.25 if alien else 0.26, rough=0.006,
        avoid=[(c, er * 0.95) for c in eyec] + [((0, ny, nz), 0.06), ((0, ny, 1.565), 0.05)] + ([] if alien else [((s * 0.85, S(s * 0.85, 2.33), 2.33), 0.085) for s in (-1, 1)]),
        short=[((0, -0.38, 1.6), 0.18, 0.35)] + [(c, 0.24, 0.45) for c in eyec] + [((s * 0.4, 0, 2.3), 0.25, 0.5 if alien else 0.3) for s in (-1, 1)]
              + ([] if alien else [((s * 0.3, -0.26, 1.55), 0.22, 1.25) for s in (-1, 1)] + [((0, -0.26, 1.15), 0.3, 1.3)]))  # kitten: fluffy cheek and chest ruff
    if not alien:  # white ear tufts
        tuft = hair_mat('tuft', color=(0.9, 0.88, 0.86), rough=0.4)
        for i in inner: fur(i, tuft, count=160, length=0.028, children=6, droop=(0, -0.2, 0.9), radius=0.0015, clump=0.5, rough=0.004)
    fur(tail, hm, count=3000, length=flen * 1.2, children=14, droop=(0, 0, 0), radius=0.0028, clump=0.3, rough=0.008)

    bones = [('root', (0, 0, 0), (0, 0, 0.3), None), ('hips', (0, 0.02, 0.62), (0, 0.02, 0.95), 'root'), ('spine', (0, 0.02, 0.95), (0, -0.01, 1.33), 'hips'),
             ('head', (0, -0.01, 1.33), (0, -0.03, 2.1), 'spine')]
    for s, n in ((1, 'L'), (-1, 'R')):
        bones += [(f'arm.{n}', (s * 0.25, -0.03, 1.22), (s * el[0], -0.05, el[1]), 'spine'), (f'fore.{n}', (s * el[0], -0.05, el[1]), (s * (pw[0] + 0.02), -0.09, pw[1] - 0.02), f'arm.{n}'),
                  (f'leg.{n}', (s * 0.17, 0, 0.66), (s * 0.18, -0.02, 0.4), 'hips'), (f'shin.{n}', (s * 0.18, -0.02, 0.4), (s * 0.19, -0.05, 0.1), f'leg.{n}'),
                  (f'foot.{n}', (s * 0.19, -0.05, 0.1), (s * 0.19, -0.24, 0.05), f'shin.{n}')]
    bones_tail = ('tail', (0, 0.28, 0.72), (0.3, 0.5, 1.2), 'hips')
    rig = make_rig(bones + [bones_tail])
    skin(body, rig, [b for b in bones if b[0] != 'root'])
    for o in eyes + [nose] + mouth + whiskers + inner + extra + liners: attach(o, rig, 'head')
    for (s, n), g in zip(((-1, 'R'), (1, 'L')), beans):
        for b in g: attach(b, rig, f'fore.{n}')
    attach(tail, rig, 'tail')
    return rig, {'tail': tail, 'orbs': [o for o in extra if o.name.startswith('orb')], 'orb_m': extra and bpy.data.materials.get('orb')}

if __name__ == '__main__':
    kind = sys.argv[1]
    rig, parts = build(kind)
    stage(res=int(sys.argv[3]), samples=int(sys.argv[4]), cam_loc=(-1.7, -7.4, 1.9), target=(0, 0, 1.3), lens=74, exposure=0.0 if kind == 'alien' else -0.25)
    shadow_catcher(); render(sys.argv[2])
