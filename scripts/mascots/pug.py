import sys, math; sys.path.insert(0, '/home/claude/bl')
import bpy, numpy as np
from mathutils import Vector
from lib import *

def EL(co, ax, ay, az, stiff=2.0, neg=False):
    m = max(ax, ay, az); return E(co, 2 * m, (ax / m, ay / m, az / m), stiff, neg)

def build():
    reset()
    from cat import oval, maxs
    def mask(nt, sx):  # classic fawn pug: black mask over the muzzle and round the eyes
        return oval(nt, sx, 0, 1.66, 0.36, 0.23, -0.32)
    furm = principled('pugFur', (0.5, 0.33, 0.18), 0.85, spec=0.2, sheen=0.0, sss=0.04, sss_radius=(0.4, 0.2, 0.15), sss_scale=0.03)
    fur_bump(furm, 700, 0.18)
    def belly(nt, sx):  # oval puppy-belly patch on the front
        dx = nt.nodes.new('ShaderNodeMath'); dx.operation = 'DIVIDE'; nt.links.new(sx.outputs['X'], dx.inputs[0]); dx.inputs[1].default_value = 0.2
        dz = nt.nodes.new('ShaderNodeMath'); dz.operation = 'MULTIPLY_ADD'; nt.links.new(sx.outputs['Z'], dz.inputs[0]); dz.inputs[1].default_value = 1 / 0.2; dz.inputs[2].default_value = -0.9 / 0.2
        v = nt.nodes.new('ShaderNodeVectorMath'); v.operation = 'LENGTH'; cm = nt.nodes.new('ShaderNodeCombineXYZ')
        nt.links.new(dx.outputs[0], cm.inputs[0]); nt.links.new(dz.outputs[0], cm.inputs[1]); nt.links.new(cm.outputs[0], v.inputs[0])
        return mult(nt, smooth_mask(nt, v.outputs['Value'], 1.0, 0.6), smooth_mask(nt, sx.outputs['Y'], -0.1, -0.3))
    region_mix(furm, (0.012, 0.01, 0.01), mask)
    ear_m = fur_bump(principled('pugEar', (0.012, 0.011, 0.013), 0.7, sheen=0.3, sheen_rough=0.5, sheen_tint=(0.4, 0.4, 0.5), spec=0.3), 900, 0.2)
    nose_m = fur_bump(principled('nose', (0.0, 0.0, 0.0), 0.5, spec=0.22), 1800, 0.9, 1.0)
    tongue_m = principled('tongue', (0.82, 0.12, 0.24), 0.28, sss=0.2, sss_radius=(1, 0.3, 0.3), sss_scale=0.05, coat=0.5, coat_rough=0.1)
    line_m = principled('mouth', (0.0, 0.0, 0.0), 1.0, spec=0.0)

    els = [EL((0, 0.02, 0.98), 0.40, 0.36, 0.46), EL((0, -0.10, 1.12), 0.33, 0.26, 0.30), EL((0, -0.06, 0.78), 0.36, 0.30, 0.28), EL((0, 0.06, 0.72), 0.38, 0.32, 0.26),
           EL((0, -0.02, 1.38), 0.30, 0.28, 0.18)]
    for s in (-1, 1):
        els += [EL((s * 0.21, 0.0, 0.55), 0.16, 0.17, 0.20)] + chain((s * 0.22, -0.02, 0.42), (s * 0.23, -0.05, 0.15), 0.22, 0.2, 5)
        els += [EL((s * 0.23, -0.12, 0.075), 0.12, 0.17, 0.075)] + [EL((s * 0.23 + d, -0.25, 0.06), 0.042, 0.05, 0.045) for d in (-0.06, 0, 0.06)]
        # arms modelled out to the sides (the dance's neutral pose) so raising them never stretches the armpits
        els += chain((s * 0.30, -0.04, 1.26), (s * 0.52, -0.07, 1.28), 0.2, 0.17, 5) + chain((s * 0.52, -0.07, 1.28), (s * 0.7, -0.09, 1.3), 0.17, 0.15, 4)
        els += [EL((s * 0.75, -0.11, 1.3), 0.085, 0.1, 0.09)] + [EL((s * 0.79, -0.18, 1.3 + d), 0.032, 0.035, 0.032) for d in (-0.055, 0, 0.055)]
    # head: big round skull, flat face, jowls, muzzle pad, brows, wrinkles
    els += [EL((0, 0.0, 1.76), 0.52, 0.42, 0.42), EL((0, -0.18, 1.70), 0.44, 0.30, 0.36), EL((0, -0.44, 1.6), 0.24, 0.11, 0.13), EL((0, -0.31, 1.45), 0.14, 0.1, 0.07)]
    for s in (-1, 1):
        els += [EL((s * 0.21, -0.33, 1.53), 0.19, 0.16, 0.17), EL((s * 0.15, -0.43, 1.5), 0.14, 0.11, 0.11), EL((s * 0.19, -0.37, 1.88), 0.1, 0.06, 0.055)]
        for k in range(14):  # eyelid ring around each eye
            a = 2 * math.pi * k / 14; els.append(EL((s * 0.2 + 0.14 * math.cos(a), -0.39, 1.76 + 0.13 * math.sin(a)), 0.03, 0.03, 0.03, 2.4))
    for z, w, y0 in ((1.96, 0.16, -0.355), (2.03, 0.12, -0.31), (1.71, 0.21, -0.47)):  # forehead folds + nose roll
        for k in range(9):
            x = -w + 2 * w * k / 8; els.append(EL((x, y0 + 1.2 * x * x, z - 0.6 * x * x), 0.045, 0.04, 0.032, 2.6))
    body = blob('pug', els, smooth=3); body.data.materials.append(furm)

    bpy.context.view_layer.update()
    S = lambda x, z: surf(body, x, z)
    er = 0.138; eye_m = eye_mat('pugEye', (0.06, 0.03, 0.015), er, pupil=0.3)
    eyes = [uv_sphere(f'eye{s}', er, (s * 0.2, S(s * 0.2, 1.76) + er * 0.42, 1.76), (1, 0.9, 1)) for s in (-1, 1)]
    for e in eyes: e.data.materials.append(eye_m)
    hls = [o for e in eyes for o in catchlights(tuple(e.location), er, 0.9)]
    nz = 1.64; ny = S(0, nz); nose = uv_sphere('nose', 0.09, (0, ny + 0.035, nz), (1.6, 0.75, 0.88)); nose.data.materials.append(nose_m)
    nost = [uv_sphere(f'nost{s}', 0.03, (s * 0.062, ny - 0.04, nz - 0.022), (1.25, 0.4, 0.5), ) for s in (-1, 1)]
    for n, s in zip(nost, (-1, 1)): n.rotation_euler = (0, 0.5 * s, -0.45 * s)
    for n in nost: n.data.materials.append(line_m)
    my = lambda x, z: S(x, z) - 0.004
    mouth = [tube('philtrum', [(0, my(0, 1.6), 1.6), (0, my(0, 1.575), 1.575), (0, my(0, 1.55), 1.55)], [0.009] * 3, line_m)]
    for s in (-1, 1): mouth.append(tube(f'lip{s}', [(s * x, my(s * x, z), z) for x, z in ((0, 1.55), (0.05, 1.533), (0.1, 1.542), (0.15, 1.572))], [0.009, 0.009, 0.008, 0.005], line_m))  # smile
    ty = S(0.04, 1.5)
    tongue = blob('tongue', [EL((0.03, ty - 0.006, 1.5), 0.05, 0.02, 0.045), EL((0.033, ty - 0.014, 1.468), 0.046, 0.018, 0.034)], 0.008, 0.005, 3); tongue.data.materials.append(tongue_m)
    ears = []
    for s in (-1, 1):  # folded button ears lying on the head, tips toward the eyes
        bp, bn = normal_at(body, s * 0.38, 2.06); tp, tn = normal_at(body, s * 0.53, 1.9)
        ears.append(flap(f'ear{s}', bp + bn * 0.01, tp + tn * 0.07 + Vector((s * 0.05, -0.04, 0)), (bn + tn) / 2, 0.13, 0.15, 0.024, ear_m))
    tail = tube('tail', [(0, 0.3, 0.86), (0.07, 0.44, 0.94), (0.02, 0.52, 1.06), (-0.09, 0.45, 1.08), (-0.08, 0.37, 0.98), (-0.02, 0.38, 0.93)], [0.08, 0.075, 0.065, 0.055, 0.045, 0.03], furm)

    bones = [('root', (0, 0, 0), (0, 0, 0.3), None), ('hips', (0, 0.02, 0.62), (0, 0.02, 0.95), 'root'), ('spine', (0, 0.02, 0.95), (0, -0.02, 1.36), 'hips'),
             ('head', (0, -0.02, 1.36), (0, -0.05, 2.1), 'spine')]
    for s, n in ((1, 'L'), (-1, 'R')):
        bones += [(f'arm.{n}', (s * 0.3, -0.04, 1.26), (s * 0.52, -0.07, 1.28), 'spine'), (f'fore.{n}', (s * 0.52, -0.07, 1.28), (s * 0.8, -0.11, 1.3), f'arm.{n}'),
                  (f'leg.{n}', (s * 0.21, 0, 0.66), (s * 0.22, -0.02, 0.4), 'hips'), (f'shin.{n}', (s * 0.22, -0.02, 0.4), (s * 0.23, -0.06, 0.1), f'leg.{n}'),
                  (f'foot.{n}', (s * 0.23, -0.06, 0.1), (s * 0.23, -0.28, 0.06), f'shin.{n}')]
    hm = hair_mat('pugHair', melanin=0.32, redness=0.62, rough=0.6)  # light fawn coat, matte
    nt = hm.node_tree; h = [n for n in nt.nodes if n.type == 'BSDF_HAIR_PRINCIPLED'][0]
    h.inputs['Coat'].default_value = 0.0; h.inputs['Radial Roughness'].default_value = 0.7
    from cat import oval as _ov, maxs as _mx  # pink blush on the fawn cheeks (Tint works in melanin mode)
    tc2 = nt.nodes.new('ShaderNodeTexCoord'); sx2 = nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(tc2.outputs['Object'], sx2.inputs[0])
    tm = nt.nodes.new('ShaderNodeMix'); tm.data_type = 'RGBA'; tm.inputs['A'].default_value = (1, 1, 1, 1); tm.inputs['B'].default_value = (1, 0.5, 0.62, 1)
    bl = _mx(nt, _ov(nt, sx2, 0.36, 1.58, 0.09, 0.07, -0.15), _ov(nt, sx2, -0.36, 1.58, 0.09, 0.07, -0.15))
    nt.links.new(bl, tm.inputs['Factor']); nt.links.new(tm.outputs['Result'], h.inputs['Tint'])
    tc = nt.nodes.new('ShaderNodeTexCoord'); sx = nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(tc.outputs['Object'], sx.inputs[0])
    mr = nt.nodes.new('ShaderNodeMapRange'); mr.inputs['To Min'].default_value = 0.32; mr.inputs['To Max'].default_value = 0.98
    nt.links.new(mask(nt, sx), mr.inputs['Value']); nt.links.new(mr.outputs['Result'], h.inputs['Melanin'])  # black mask
    hm_dark = hair_mat('pugEarHair', melanin=0.95, redness=0.2, rough=0.4)
    fur(body, hm, count=45000, length=0.015, children=16, droop=(0, 0, -0.35), radius=0.0026, clump=0.05, comb=False,
        avoid=[((s * 0.2, S(s * 0.2, 1.76), 1.76), 0.112) for s in (-1, 1)] + [((0, ny, nz), 0.1), ((0.04, ty, 1.5), 0.06)],
        short=[((0, -0.45, 1.62), 0.3, 0.3), ((0, -0.36, 1.98), 0.28, 0.35)] + [((s * 0.2, -0.4, 1.76), 0.2, 0.5) for s in (-1, 1)])
    for e in ears: fur(e, hm_dark, count=1600, length=0.01, children=10, droop=(0, 0, -1.0), radius=0.0022, clump=0.05, comb=False)
    rest_coords(body, [furm, hm])  # black mask stays on the face when the head turns
    rig = make_rig(bones)
    skin(body, rig, [b for b in bones if b[0] != 'root'])
    for o in eyes + [nose, tongue] + nost + mouth + ears + hls: attach(o, rig, 'head')
    attach(tail, rig, 'hips')
    return rig, {'ears': ears, 'tail': tail}

if __name__ == '__main__':
    rig, parts = build()
    stage(res=int(sys.argv[2]) if len(sys.argv) > 2 else 480, samples=int(sys.argv[3]) if len(sys.argv) > 3 else 48,
          cam_loc=(-1.7, -7.4, 1.9) if 'face' not in sys.argv else (-0.6, -6.5, 1.85), target=(0, 0, 1.3) if 'face' not in sys.argv else (0, -0.3, 1.72), lens=78 if 'face' not in sys.argv else 190)
    shadow_catcher()
    render(sys.argv[1] if len(sys.argv) > 1 else '/home/claude/bl/pug_test.png')
